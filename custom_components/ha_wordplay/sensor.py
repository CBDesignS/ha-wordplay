"""Sensor platform for H.A WordPlay integration - Multi-User Version."""
import logging
from typing import Optional, Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

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
    """Set up the sensor platform for WordPlay - Multi-User."""
    
    # Get all users from Home Assistant
    users = await hass.auth.async_get_users()
    
    entities = []
    
    # Function to create sensors for a user
    def create_user_sensors(user_id: str, user_name: str = None):
        """Create sensor entities for a specific user."""
        user_entities = [
            WordPlayGameStateSensor(hass, user_id, user_name),
            WordPlayGuessesSensor(hass, user_id, user_name),
        ]
        
        # Add debug sensor in development mode
        if _LOGGER.isEnabledFor(logging.DEBUG):
            user_entities.append(WordPlayDebugSensor(hass, user_id, user_name))
        
        # Store entity references in hass.data for service access
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {"entities": {}}
        if user_id not in hass.data[DOMAIN]["entities"]:
            hass.data[DOMAIN]["entities"][user_id] = {}
        
        for entity in user_entities:
            if isinstance(entity, WordPlayGameStateSensor):
                hass.data[DOMAIN]["entities"][user_id]["game_state"] = entity
            elif isinstance(entity, WordPlayGuessesSensor):
                hass.data[DOMAIN]["entities"][user_id]["guesses"] = entity
            elif isinstance(entity, WordPlayDebugSensor):
                hass.data[DOMAIN]["entities"][user_id]["debug"] = entity
        
        return user_entities
    
    # Always create default sensors for system/admin use
    default_sensors = create_user_sensors("default", "Default")
    entities.extend(default_sensors)
    
    # Create sensors for each user
    for user in users:
        if user.system_generated:
            continue  # Skip system users
            
        user_sensors = create_user_sensors(user.id, user.name)
        entities.extend(user_sensors)
        _LOGGER.info(f"Created WordPlay sensors for user: {user.name} ({user.id})")
    
    # Add entities to Home Assistant
    async_add_entities(entities, True)
    
    _LOGGER.info(f"WordPlay sensor entities created: {len(entities)} sensors total")


class WordPlayGameStateSensor(SensorEntity):
    """Sensor for current game state and display data - one per user."""

    def __init__(self, hass: HomeAssistant, user_id: str, user_name: str = None) -> None:
        """Initialize the game state sensor."""
        super().__init__()
        self.hass = hass
        self.user_id = user_id
        self.user_name = user_name or user_id
        self._attr_name = f"ha wordplay game state ({user_id})" if user_id != "default" else "ha wordplay game state"
        self._attr_unique_id = f"{DOMAIN}_game_state_{user_id}"
        self._attr_entity_category = None
        self._attr_icon = "mdi:gamepad-variant"
        self._attr_native_value = STATE_IDLE
        self._attr_extra_state_attributes = {"user_id": user_id}
        
        # Set entity_id explicitly to ensure proper registration
        self.entity_id = f"sensor.ha_wordplay_game_state_{user_id}"

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
        # Always include user_id in attributes
        attributes["user_id"] = self.user_id
        attributes["user_name"] = self.user_name
        self._attr_extra_state_attributes = attributes
        if self.hass is not None:
            self.async_write_ha_state()


class WordPlayGuessesSensor(SensorEntity):
    """Sensor for guess history and results - one per user."""

    def __init__(self, hass: HomeAssistant, user_id: str, user_name: str = None) -> None:
        """Initialize the guesses sensor."""
        super().__init__()
        self.hass = hass
        self.user_id = user_id
        self.user_name = user_name or user_id
        self._attr_name = f"ha wordplay guesses ({user_id})" if user_id != "default" else "ha wordplay guesses"
        self._attr_unique_id = f"{DOMAIN}_guesses_{user_id}"
        self._attr_entity_category = None
        self._attr_icon = "mdi:format-list-numbered"
        self._attr_native_value = 0
        self._attr_extra_state_attributes = {"user_id": user_id}
        
        # Set entity_id explicitly to ensure proper registration
        self.entity_id = f"sensor.ha_wordplay_guesses_{user_id}"

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
        # Always include user_id in attributes
        attributes["user_id"] = self.user_id
        attributes["user_name"] = self.user_name
        self._attr_extra_state_attributes = attributes
        if self.hass is not None:
            self.async_write_ha_state()


class WordPlayDebugSensor(SensorEntity):
    """Debug sensor for development (only in debug mode) - one per user."""

    def __init__(self, hass: HomeAssistant, user_id: str, user_name: str = None) -> None:
        """Initialize the debug sensor."""
        super().__init__()
        self.hass = hass
        self.user_id = user_id
        self.user_name = user_name or user_id
        self._attr_name = f"ha wordplay debug ({user_id})" if user_id != "default" else "ha wordplay debug"
        self._attr_unique_id = f"{DOMAIN}_debug_{user_id}"
        self._attr_entity_category = None
        self._attr_icon = "mdi:bug"
        self._attr_native_value = "DEBUG_MODE"
        self._attr_extra_state_attributes = {"user_id": user_id}
        
        # Set entity_id explicitly to ensure proper registration
        self.entity_id = f"sensor.ha_wordplay_debug_{user_id}"

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
        # Always include user_id in attributes
        attributes["user_id"] = self.user_id
        attributes["user_name"] = self.user_name
        self._attr_extra_state_attributes = attributes
        if self.hass is not None:
            self.async_write_ha_state()