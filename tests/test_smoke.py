"""The suite that shipped with the project.

It walks the happy path of each module and nothing else. It is here so the
service has a heartbeat in CI, not because the rules are covered.
"""

from __future__ import annotations

from decimal import Decimal

from bikeshare import Account, Station, authorize, base_fare, quote


def test_a_short_ride_costs_nothing() -> None:
    assert base_fare(10) == Decimal("0.00")


def test_a_ride_inside_the_first_hour_pays_the_first_hour_rate() -> None:
    assert base_fare(45) == Decimal("15.00")


def test_a_casual_rider_pays_the_unlock_fee() -> None:
    fare = quote(45)
    assert fare.base == Decimal("15.00")
    assert fare.total == Decimal("20.00")


def test_an_active_rider_may_take_a_bike() -> None:
    station = Station(id="ST-01", name="Plaza", capacity=4, docked=["B1"])
    rider = Account(id="AC-1")
    assert authorize(rider, station).allowed is True
