"""Rider accounts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .fares import Plan


class AccountStatus(StrEnum):
    """Lifecycle of a rider account."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class Account:
    """A rider, as the rental service sees them."""

    id: str
    status: AccountStatus = AccountStatus.ACTIVE
    balance_due: Decimal = Decimal("0.00")
    plan: Plan = Plan.CASUAL

    @property
    def is_active(self) -> bool:
        return self.status is AccountStatus.ACTIVE

    @property
    def owes_money(self) -> bool:
        return self.balance_due > Decimal("0.00")
