"""Text platform for H.A WordPlay integration."""
import logging
from typing import Optional

from homeassistant.components.text import TextEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    MIN_WORD_LENGTH,
    MAX_WORD_LENGTH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the text platform for WordPlay."""
    
    # Create the text input entity
    entity = WordPlayGuessInput(hass)
    
    async_add_entities([entity])
    
    # Store entity reference
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    hass.data[DOMAIN]["entities"]["text_input"] = entity
    
    _LOGGER.info("WordPlay text input entity created")


class WordPlayGuessInput(TextEntity):
    """Custom text input entity for word guesses."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the text input entity."""
        self.hass = hass
        self._attr_name = "ha wordplay guess input"  # This will create text.ha_wordplay_guess_input
        self._attr_unique_id = f"{DOMAIN}_guess_input"
        self._attr_entity_category = None
        self._attr_icon = "mdi:keyboard"
        self._attr_native_value = ""
        self._attr_native_max = MAX_WORD_LENGTH
        self._attr_native_min = MIN_WORD_LENGTH
        self._attr_pattern = r"^[A-Za-z]*$"
        self._attr_mode = "text"



    @property
    def native_value(self) -> str:
        """Return the current value."""
        return self._attr_native_value

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        # Convert to uppercase and validate
        value = value.upper().strip()
        
        # Only allow letters
        if value and not value.isalpha():
            _LOGGER.warning("Invalid guess input: %s (only letters allowed)", value)
            return
            
        # Limit length based on current game
        game_data = self.hass.data.get(DOMAIN, {})
        game = game_data.get("game")
        if game and hasattr(game, 'word_length'):
            max_length = game.word_length
        else:
            max_length = MAX_WORD_LENGTH
            
        if len(value) > max_length:
            value = value[:max_length]
        
        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_clear_value(self) -> None:
        """Clear the input value."""
        self._attr_native_value = ""
        self.async_write_ha_state()