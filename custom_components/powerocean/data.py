"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import PowerOceanApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type PowerOceanConfigEntry = ConfigEntry[PowerOceanData]


@dataclass
class PowerOceanData:
    """Data for the Blueprint integration."""

    client: PowerOceanApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
