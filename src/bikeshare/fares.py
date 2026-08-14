"""Fare calculation.

Money is handled with :class:`~decimal.Decimal` and rounded half up, which is
what the billing provider expects. Durations are whole minutes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from .errors import InvalidRental

GRACE_MINUTES = 15
HOUR_MINUTES = 60
DAY_MINUTES = 1440
MAX_RENTAL_MINUTES = DAY_MINUTES

FIRST_HOUR_RATE = Decimal("15.00")
EXTRA_HOUR_RATE = Decimal("10.00")
DAY_RATE = Decimal("90.00")
UNLOCK_FEE = Decimal("5.00")
PEAK_FEE = Decimal("5.00")
ELECTRIC_RATE = Decimal("0.20")
DAILY_CAP = Decimal("100.00")

ZERO = Decimal("0.00")


class BikeType(StrEnum):
    """The two kinds of bike in the fleet."""

    STANDARD = "standard"
    ELECTRIC = "electric"


class Plan(StrEnum):
    """How the rider pays: per ride, or through a monthly membership."""

    CASUAL = "casual"
    MEMBER = "member"


@dataclass(frozen=True, slots=True)
class Fare:
    """The billed amounts for one finished rental."""

    minutes: int
    base: Decimal
    surcharge: Decimal
    total: Decimal

    def __str__(self) -> str:
        return (
            f"{self.minutes} min | base Q{self.base} "
            f"+ extras Q{self.surcharge} = Q{self.total}"
        )


def _money(value: Decimal) -> Decimal:
    """Round a raw amount to cents, half up."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def base_fare(minutes: int) -> Decimal:
    """Return the time based part of the fare for a rental of ``minutes``."""
    if isinstance(minutes, bool) or not isinstance(minutes, int):
        raise TypeError("minutes must be a whole number of minutes")
    if minutes < 0:
        raise InvalidRental("a rental cannot last a negative number of minutes")
    if minutes > MAX_RENTAL_MINUTES:
        raise InvalidRental("a rental cannot be longer than one day")

    if minutes <= GRACE_MINUTES:
        return ZERO
    if minutes <= HOUR_MINUTES:
        return FIRST_HOUR_RATE
    if minutes < 3 * HOUR_MINUTES:
        extra_hours = math.ceil((minutes - HOUR_MINUTES) / HOUR_MINUTES)
        return FIRST_HOUR_RATE + EXTRA_HOUR_RATE * extra_hours
    return DAY_RATE


def surcharges(
    base: Decimal,
    *,
    bike_type: BikeType = BikeType.STANDARD,
    plan: Plan = Plan.CASUAL,
    peak: bool = False,
) -> Decimal:
    """Return the extras that ride on top of ``base``."""
    extra = ZERO
    if bike_type is BikeType.ELECTRIC:
        extra += base * ELECTRIC_RATE
    if plan is Plan.CASUAL:
        extra += UNLOCK_FEE
    if peak:
        extra += PEAK_FEE
    return _money(extra)


def quote(
    minutes: int,
    *,
    bike_type: BikeType = BikeType.STANDARD,
    plan: Plan = Plan.CASUAL,
    peak: bool = False,
) -> Fare:
    """Price a rental end to end, cap included."""
    base = base_fare(minutes)
    extra = surcharges(base, bike_type=bike_type, plan=plan, peak=peak)
    total = base + extra
    if total > DAILY_CAP:
        total = DAILY_CAP
    return Fare(
        minutes=minutes,
        base=_money(base),
        surcharge=extra,
        total=_money(total),
    )
