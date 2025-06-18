"""Custom entities for H.A WordPlay integration."""
import logging
from typing import Optional, List

from homeassistant.components.text import TextEntity
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    WORD_LENGTH_OPTIONS,
    DEFAULT_WORD_LENGTH,
    MIN_WORD_LENGTH,
    MAX_WORD_LENGTH,
)

_LOGGER = logging.getLogger(__name__)


class WordPlayGuessInput(TextEntity):
    """Custom text input entity for word guesses."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the text input entity."""
        self.hass = hass
        self._attr_name = "WordPlay Guess Input"
        self._attr_unique_id = f"{DOMAIN}_guess_input"
        self._attr_entity_category = None
        self._attr_icon = "mdi:keyboard"
        self._attr_native_value = ""
        self._attr_native_max = MAX_WORD_LENGTH
        self._attr_native_min = MIN_WORD_LENGTH
        self._attr_pattern = r"^[A-Za-z]*$"
        self._attr_mode = "text"

    @property
    def entity_id(self) -> str:
        """Return entity ID."""
        return "text.ha_wordplay_guess_input"

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


class WordPlayWordLengthSelect(SelectEntity):
    """Select entity for choosing word length."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the select entity."""
        self.hass = hass
        self._attr_name = "WordPlay Word Length"
        self._attr_unique_id = f"{DOMAIN}_word_length"
        self._attr_entity_category = None
        self._attr_icon = "mdi:numeric"
        self._attr_options = [str(length) for length in WORD_LENGTH_OPTIONS]
        self._attr_current_option = str(DEFAULT_WORD_LENGTH)

    @property
    def entity_id(self) -> str:
        """Return entity ID."""
        return "select.ha_wordplay_word_length"

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


async def async_setup_entities(
    hass: HomeAssistant,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WordPlay custom entities."""
    entities = [
        WordPlayGuessInput(hass),
        WordPlayWordLengthSelect(hass),
    ]
    
    async_add_entities(entities)
    _LOGGER.info("WordPlay custom entities created: %d entities", len(entities))