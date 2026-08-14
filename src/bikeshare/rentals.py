"""The rental itself: reservation, ride, and what the rider ends up paying.

Time is passed in as ``now``, a whole number of minutes on the service clock.
Nothing here reads the system clock, so a caller decides what time it is.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .accounts import Account
from .eligibility import authorize
from .errors import (
    InvalidRental,
    InvalidTransition,
    RentalRefused,
    ReservationExpired,
)
from .fares import MAX_RENTAL_MINUTES, BikeType, Fare, Plan, quote
from .stations import Station

RESERVATION_HOLD_MINUTES = 10


class RentalState(StrEnum):
    """Where a rental is in its life."""

    RESERVED = "reserved"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    LOST = "lost"


@dataclass(slots=True)
class Rental:
    """One rental, from the moment a bike is held to the moment it is billed."""

    id: str
    bike_id: str
    account_id: str
    reserved_at: int
    bike_type: BikeType = BikeType.STANDARD
    plan: Plan = Plan.CASUAL
    state: RentalState = RentalState.RESERVED
    started_at: int | None = None
    ended_at: int | None = None

    def _require(self, expected: RentalState, event: str) -> None:
        if self.state is not expected:
            raise InvalidTransition(
                f"cannot {event} a rental that is {self.state}"
            )

    def start(self, now: int) -> None:
        """Unlock the bike and begin charging time."""
        self._require(RentalState.RESERVED, "start")
        if now - self.reserved_at > RESERVATION_HOLD_MINUTES:
            self.state = RentalState.CANCELLED
            raise ReservationExpired(
                f"the hold on bike {self.bike_id} ran out"
            )
        self.state = RentalState.ACTIVE
        self.started_at = now

    def cancel(self) -> None:
        """Drop a reservation before the ride starts."""
        self._require(RentalState.RESERVED, "cancel")
        self.state = RentalState.CANCELLED

    def finish(self, now: int, station: Station, *, peak: bool = False) -> Fare:
        """Dock the bike, close the rental and price it."""
        self._require(RentalState.ACTIVE, "finish")
        assert self.started_at is not None
        minutes = now - self.started_at
        if minutes < 0:
            raise InvalidRental("the rental cannot end before it started")
        if minutes > MAX_RENTAL_MINUTES:
            self.state = RentalState.LOST
            raise InvalidRental(
                f"bike {self.bike_id} was out for more than a day"
            )
        station.dock(self.bike_id)
        self.state = RentalState.COMPLETED
        self.ended_at = now
        return quote(minutes, bike_type=self.bike_type, plan=self.plan, peak=peak)


def reserve(
    account: Account,
    station: Station,
    *,
    rental_id: str,
    now: int,
    bike_type: BikeType = BikeType.STANDARD,
) -> Rental:
    """Hold a bike for ``account`` at ``station`` and return the rental."""
    decision = authorize(account, station)
    if not decision:
        raise RentalRefused(f"rental refused: {decision.reason}")
    bike_id = station.undock()
    return Rental(
        id=rental_id,
        bike_id=bike_id,
        account_id=account.id,
        reserved_at=now,
        bike_type=bike_type,
        plan=account.plan,
    )
