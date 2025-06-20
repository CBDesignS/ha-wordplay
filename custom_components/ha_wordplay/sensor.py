"""Sensor platform for H.A WordPlay integration."""
import logging
from typing import Optional, Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import generate_entity_id

from .const import (
    DOMAIN,
    STATE_IDLE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform for WordPlay."""
    
    # Create sensor entities with proper platform context
    entities = [
        WordPlayGameStateSensor(hass),
        WordPlayGuessesSensor(hass),
    ]
    
    # Add debug sensor in development mode
    if _LOGGER.isEnabledFor(logging.DEBUG):
        entities.append(WordPlayDebugSensor(hass))
    
    # Add entities to Home Assistant
    async_add_entities(entities, True)
    
    # Store entity references in hass.data for service access
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    
    for entity in entities:
        if isinstance(entity, WordPlayGameStateSensor):
            hass.data[DOMAIN]["entities"]["game_state"] = entity
        elif isinstance(entity, WordPlayGuessesSensor):
            hass.data[DOMAIN]["entities"]["guesses"] = entity
        elif isinstance(entity, WordPlayDebugSensor):
            hass.data[DOMAIN]["entities"]["debug"] = entity
    
    _LOGGER.info(f"WordPlay sensor entities created: {len(entities)} sensors")


class WordPlayGameStateSensor(SensorEntity):
    """Sensor for current game state and display data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the game state sensor."""
        super().__init__()
        self.hass = hass
        self._attr_name = "ha wordplay game state"
        self._attr_unique_id = f"{DOMAIN}_game_state"
        self._attr_entity_category = None
        self._attr_icon = "mdi:gamepad-variant"
        self._attr_native_value = STATE_IDLE
        self._attr_extra_state_attributes = {}
        
        # Set entity_id explicitly to ensure proper registration
        self.entity_id = "sensor.ha_wordplay_game_state"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return self._attr_unique_id

    @property
    def native_value(self) -> str:
        """Return the current game state."""
        return self._attr_native_value

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return self._attr_extra_state_attributes

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._attr_icon

    def update_state(self, state: str, attributes: Dict[str, Any]) -> None:
        """Update the sensor state and attributes."""
        self._attr_native_value = state
        self._attr_extra_state_attributes = attributes
        if self.hass is not None:
            self.async_write_ha_state()


class WordPlayGuessesSensor(SensorEntity):
    """Sensor for guess history and results."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the guesses sensor."""
        super().__init__()
        self.hass = hass
        self._attr_name = "ha wordplay guesses"
        self._attr_unique_id = f"{DOMAIN}_guesses"
        self._attr_entity_category = None
        self._attr_icon = "mdi:format-list-numbered"
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {}
        
        # Set entity_id explicitly to ensure proper registration
        self.entity_id = "sensor.ha_wordplay_guesses"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return self._attr_unique_id

    @property
    def native_value(self) -> int:
        """Return the number of guesses made."""
        return self._attr_native_value

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return self._attr_extra_state_attributes

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._attr_icon

    def update_state(self, count: int, attributes: Dict[str, Any]) -> None:
        """Update the sensor state and attributes."""
        self._attr_native_value = count
        self._attr_extra_state_attributes = attributes
        if self.hass is not None:
            self.async_write_ha_state()


class WordPlayDebugSensor(SensorEntity):
    """Debug sensor for development (only in debug mode)."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the debug sensor."""
        super().__init__()
        self.hass = hass
        self._attr_name = "ha wordplay debug"
        self._attr_unique_id = f"{DOMAIN}_debug"
        self._attr_entity_category = None
        self._attr_icon = "mdi:bug"
        self._attr_native_value = "DEBUG_MODE"
        self._attr_extra_state_attributes = {}
        
        # Set entity_id explicitly to ensure proper registration
        self.entity_id = "sensor.ha_wordplay_debug"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return self._attr_unique_id

    @property
    def native_value(self) -> str:
        """Return debug status."""
        return self._attr_native_value

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return debug attributes."""
        return self._attr_extra_state_attributes

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._attr_icon

    def update_state(self, state: str, attributes: Dict[str, Any]) -> None:
        """Update the debug sensor state and attributes."""
        self._attr_native_value = state
        self._attr_extra_state_attributes = attributes
        if self.hass is not None:
            self.async_write_ha_state()