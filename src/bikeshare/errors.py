"""Exception hierarchy for the bikeshare core.

Every error raised by the domain inherits from :class:`BikeshareError`, so a
caller that does not care about the specific failure can catch a single type.
"""

from __future__ import annotations


class BikeshareError(Exception):
    """Base class for every error raised by this package."""


class InvalidRental(BikeshareError):
    """The rental duration is outside what the service accepts."""


class InvalidTransition(BikeshareError):
    """The rental received an event that its current state cannot handle."""


class ReservationExpired(BikeshareError):
    """The hold on the reserved bike ran out before the rental started."""


class RentalRefused(BikeshareError):
    """The rider is not allowed to take a bike out right now."""


class StationFull(BikeshareError):
    """There is no free dock left at the station."""


class StationEmpty(BikeshareError):
    """There is no bike left to take at the station."""


class UnknownBike(BikeshareError):
    """The requested bike is not docked at this station."""


class BikeAlreadyDocked(BikeshareError):
    """The bike is already docked at this station."""
