"""Whether a rider may take a bike out right now."""

from __future__ import annotations

from dataclasses import dataclass

from .accounts import Account
from .stations import Station

ACCOUNT_INACTIVE = "account_inactive"
BALANCE_DUE = "balance_due"
NO_BIKES_AVAILABLE = "no_bikes_available"


@dataclass(frozen=True, slots=True)
class Decision:
    """The answer the app shows when someone taps *unlock*."""

    allowed: bool
    reason: str | None = None

    def __bool__(self) -> bool:
        return self.allowed


def authorize(account: Account, station: Station) -> Decision:
    """Decide whether ``account`` can start a rental at ``station``."""
    if not account.is_active:
        return Decision(False, ACCOUNT_INACTIVE)
    if account.owes_money:
        return Decision(False, BALANCE_DUE)
    if station.available_bikes == 0:
        return Decision(False, NO_BIKES_AVAILABLE)
    return Decision(True)
