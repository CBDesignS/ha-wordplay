"""Select platform for H.A WordPlay integration - Multi-User Version."""
import logging
from typing import Optional

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    WORD_LENGTH_OPTIONS,
    DEFAULT_WORD_LENGTH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the select platform for WordPlay - Multi-User."""
    
    # Get all users from Home Assistant
    users = await hass.auth.async_get_users()
    
    entities = []
    
    # Always create a default entity for system/admin use
    default_entity = WordPlayWordLengthSelect(hass, "default")
    entities.append(default_entity)
    
    # Store default entity reference
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    if "default" not in hass.data[DOMAIN]["entities"]:
        hass.data[DOMAIN]["entities"]["default"] = {}
    hass.data[DOMAIN]["entities"]["default"]["word_length"] = default_entity
    
    # Create entity for each user
    for user in users:
        if user.system_generated:
            continue  # Skip system users
            
        user_id = user.id
        entity = WordPlayWordLengthSelect(hass, user_id)
        entities.append(entity)
        
        # Store entity reference
        if user_id not in hass.data[DOMAIN]["entities"]:
            hass.data[DOMAIN]["entities"][user_id] = {}
        hass.data[DOMAIN]["entities"][user_id]["word_length"] = entity
        
        _LOGGER.info(f"Created WordPlay word length selector for user: {user.name} ({user_id})")
    
    async_add_entities(entities, True)
    _LOGGER.info(f"WordPlay created {len(entities)} word length selector entities")


class WordPlayWordLengthSelect(SelectEntity):
    """Select entity for choosing word length - one per user."""

    def __init__(self, hass: HomeAssistant, user_id: str) -> None:
        """Initialize the select entity."""
        super().__init__()
        self.hass = hass
        self.user_id = user_id
        self._attr_name = f"ha wordplay word length ({user_id})" if user_id != "default" else "ha wordplay word length"
        self._attr_unique_id = f"{DOMAIN}_word_length_{user_id}"
        self._attr_entity_category = None
        self._attr_icon = "mdi:numeric"
        self._attr_options = [str(length) for length in WORD_LENGTH_OPTIONS]
        self._attr_current_option = str(DEFAULT_WORD_LENGTH)
        
        # Set entity_id explicitly
        self.entity_id = f"select.ha_wordplay_word_length_{user_id}"

    @property
    def current_option(self) -> str:
        """Return the current option."""
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        if option in self._attr_options:
            self._attr_current_option = option
            self.async_write_ha_state()
            _LOGGER.info(f"Word length selected for user {self.user_id}: {option}")
        else:
            _LOGGER.error(f"Invalid word length option for user {self.user_id}: {option}")

    def get_selected_length(self) -> int:
        """Get the currently selected word length as integer."""
        try:
            return int(self._attr_current_option)
        except (ValueError, TypeError):
            return DEFAULT_WORD_LENGTH