"""Command line shell around the domain, so the package can be run by hand.

This module is a thin demo wrapper and is left out of the coverage scope on
purpose: the rules worth testing live in the other modules.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from decimal import Decimal

from .accounts import Account, AccountStatus
from .errors import BikeshareError
from .fares import BikeType, Plan, quote
from .rentals import reserve
from .stations import Station, needs_rebalance


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bikeshare",
        description="Fare and rental core of a city bike service.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    quote_cmd = sub.add_parser("quote", help="price a rental of N minutes")
    quote_cmd.add_argument("--minutes", type=int, required=True)
    quote_cmd.add_argument("--electric", action="store_true")
    quote_cmd.add_argument("--member", action="store_true")
    quote_cmd.add_argument("--peak", action="store_true")

    sub.add_parser("demo", help="run one rental from reservation to invoice")
    return parser


def _run_quote(args: argparse.Namespace) -> int:
    fare = quote(
        args.minutes,
        bike_type=BikeType.ELECTRIC if args.electric else BikeType.STANDARD,
        plan=Plan.MEMBER if args.member else Plan.CASUAL,
        peak=args.peak,
    )
    print(fare)
    return 0


def _run_demo() -> int:
    station = Station(id="ST-01", name="Plaza", capacity=6, docked=["B1", "B2"])
    rider = Account(
        id="AC-42",
        status=AccountStatus.ACTIVE,
        balance_due=Decimal("0.00"),
        plan=Plan.MEMBER,
    )
    print(f"station {station.name}: {station.available_bikes} bikes, "
          f"{station.free_docks} free docks")

    rental = reserve(rider, station, rental_id="RN-7", now=480)
    print(f"reserved {rental.bike_id} at minute {rental.reserved_at}")

    rental.start(485)
    print(f"rental {rental.id} is {rental.state}")

    fare = rental.finish(485 + 95, station)
    print(f"rental {rental.id} is {rental.state}")
    print(f"invoice: {fare}")
    print(f"rebalance truck needed: {needs_rebalance(station)}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``bikeshare`` and ``python -m bikeshare``."""
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "quote":
            return _run_quote(args)
        return _run_demo()
    except BikeshareError as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
