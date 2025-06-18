"""Select platform for H.A WordPlay integration."""
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
    """Set up the select platform for WordPlay."""
    
    # Create the select entity
    entity = WordPlayWordLengthSelect(hass)
    
    async_add_entities([entity])
    
    # Store entity reference
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    hass.data[DOMAIN]["entities"]["word_length"] = entity
    
    _LOGGER.info("WordPlay word length selector entity created")


class WordPlayWordLengthSelect(SelectEntity):
    """Select entity for choosing word length."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._attr_name = "ha wordplay word length"  # This will create select.ha_wordplay_word_length
        self._attr_unique_id = f"{DOMAIN}_word_length"
        self._attr_entity_category = None
        self._attr_icon = "mdi:numeric"
        self._attr_options = [str(length) for length in WORD_LENGTH_OPTIONS]
        self._attr_current_option = str(DEFAULT_WORD_LENGTH)



    @property
    def current_option(self) -> str:
        """Return the current option."""
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        if option in self._attr_options:
            self._attr_current_option = option
            self.async_write_ha_state()
            _LOGGER.info("Word length selected: %s", option)
        else:
            _LOGGER.error("Invalid word length option: %s", option)

    def get_selected_length(self) -> int:
        """Get the currently selected word length as integer."""
        try:
            return int(self._attr_current_option)
        except (ValueError, TypeError):
            return DEFAULT_WORD_LENGTH