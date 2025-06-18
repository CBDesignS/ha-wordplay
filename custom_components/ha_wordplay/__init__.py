"""H.A WordPlay integration for Home Assistant."""
import logging
import asyncio
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    SERVICE_NEW_GAME,
    SERVICE_MAKE_GUESS,
    SERVICE_GET_HINT,
    SERVICE_SUBMIT_GUESS,
    DEFAULT_WORD_LENGTH,
)
from .game_logic import WordPlayGame
from .entities import async_setup_entities
from .lovelace import async_create_wordplay_dashboard

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up H.A WordPlay integration."""
    _LOGGER.info("Setting up H.A WordPlay integration")
    
    # Initialize the game instance
    game = WordPlayGame(hass)
    
    # Store game and entities data
    hass.data[DOMAIN] = {
        "game": game,
        "entities": {}
    }
    
    # Create custom entities
    def add_entities_callback(entities):
        """Callback to add entities."""
        # Store entity references for game interaction
        for entity in entities:
            if hasattr(entity, 'entity_id'):
                if 'guess_input' in entity.entity_id:
                    hass.data[DOMAIN]["entities"]["text_input"] = entity
                elif 'word_length' in entity.entity_id:
                    hass.data[DOMAIN]["entities"]["word_length"] = entity
    
    await async_setup_entities(hass, add_entities_callback)
    
    # Set up state tracking for live input updates
    async def handle_input_change(event):
        """Handle changes to the text input."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        if new_state and entity_id == "text.ha_wordplay_guess_input":
            await game.update_current_input(new_state.state or "")
    
    # Track the text input entity
    async_track_state_change_event(
        hass, ["text.ha_wordplay_guess_input"], handle_input_change
    )
    
    # Register services
    async def handle_new_game(call: ServiceCall) -> None:
        """Handle new game service call."""
        # Get word length from select entity or service data
        word_length = call.data.get("word_length")
        
        if not word_length:
            # Try to get from select entity
            select_entity = hass.data[DOMAIN]["entities"].get("word_length")
            if select_entity:
                word_length = select_entity.get_selected_length()
            else:
                word_length = DEFAULT_WORD_LENGTH
        
        success = await game.start_new_game(int(word_length))
        
        if success:
            _LOGGER.info(f"New game started with {word_length} letters")
        else:
            _LOGGER.error("Failed to start new game")
    
    async def handle_make_guess(call: ServiceCall) -> None:
        """Handle make guess service call."""
        guess = call.data.get("guess", "").upper()
        if guess:
            result = await game.make_guess(guess)
            if "error" in result:
                _LOGGER.warning(f"Guess error: {result['error']}")
            else:
                _LOGGER.info(f"Guess processed: {guess}")
    
    async def handle_get_hint(call: ServiceCall) -> None:
        """Handle get hint service call."""
        hint = await game.get_hint()
        _LOGGER.info(f"Hint requested: {hint}")
    
    async def handle_submit_guess(call: ServiceCall) -> None:
        """Handle submit current guess service call."""
        text_entity = hass.data[DOMAIN]["entities"].get("text_input")
        if text_entity and text_entity.native_value:
            guess = text_entity.native_value.upper()
            result = await game.make_guess(guess)
            if "error" in result:
                _LOGGER.warning(f"Submit guess error: {result['error']}")
            else:
                _LOGGER.info(f"Guess submitted: {guess}")
        else:
            _LOGGER.warning("No guess to submit")
    
    # Register the services
    hass.services.async_register(
        DOMAIN, SERVICE_NEW_GAME, handle_new_game
    )
    hass.services.async_register(
        DOMAIN, SERVICE_MAKE_GUESS, handle_make_guess
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET_HINT, handle_get_hint
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SUBMIT_GUESS, handle_submit_guess
    )
    
    # Create WordPlay dashboard configuration
    await async_create_wordplay_dashboard(hass)
    
    _LOGGER.info("H.A WordPlay integration setup complete")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload H.A WordPlay integration."""
    _LOGGER.info("Unloading H.A WordPlay integration")
    
    # Remove services
    hass.services.async_remove(DOMAIN, SERVICE_NEW_GAME)
    hass.services.async_remove(DOMAIN, SERVICE_MAKE_GUESS)
    hass.services.async_remove(DOMAIN, SERVICE_GET_HINT)
    hass.services.async_remove(DOMAIN, SERVICE_SUBMIT_GUESS)
    
    # Clean up data
    hass.data.pop(DOMAIN, None)
    
    return True