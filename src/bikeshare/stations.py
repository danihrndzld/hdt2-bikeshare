"""Stations and their docks."""

from __future__ import annotations

from dataclasses import dataclass, field

from .errors import BikeAlreadyDocked, StationEmpty, StationFull, UnknownBike

LOW_OCCUPANCY = 0.20
HIGH_OCCUPANCY = 0.80


@dataclass(slots=True)
class Station:
    """A dock station holding bikes by id."""

    id: str
    name: str
    capacity: int
    docked: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.capacity < 0:
            raise ValueError("capacity cannot be negative")
        if len(self.docked) > self.capacity:
            raise ValueError("more bikes docked than the station can hold")

    @property
    def available_bikes(self) -> int:
        return len(self.docked)

    @property
    def free_docks(self) -> int:
        return self.capacity - len(self.docked)

    def dock(self, bike_id: str) -> None:
        """Leave ``bike_id`` at this station."""
        if bike_id in self.docked:
            raise BikeAlreadyDocked(f"bike {bike_id} is already docked at {self.id}")
        if self.free_docks <= 0:
            raise StationFull(f"station {self.id} has no free dock")
        self.docked.append(bike_id)

    def undock(self, bike_id: str | None = None) -> str:
        """Take a bike out, either a specific one or the one docked longest."""
        if not self.docked:
            raise StationEmpty(f"station {self.id} has no bike available")
        if bike_id is None:
            return self.docked.pop(0)
        if bike_id not in self.docked:
            raise UnknownBike(f"bike {bike_id} is not docked at {self.id}")
        self.docked.remove(bike_id)
        return bike_id


def needs_rebalance(station: Station) -> bool:
    """Tell whether a truck should visit this station."""
    if station.capacity == 0:
        return False
    occupancy = station.available_bikes / station.capacity
    return occupancy <= LOW_OCCUPANCY or occupancy >= HIGH_OCCUPANCY
