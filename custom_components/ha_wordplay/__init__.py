"""H.A WordPlay integration for Home Assistant."""
import logging
import asyncio
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry as er
from homeassistant.components.input_text import DOMAIN as INPUT_TEXT_DOMAIN

from .const import (
    DOMAIN,
    SERVICE_NEW_GAME,
    SERVICE_MAKE_GUESS,
    SERVICE_GET_HINT,
)
from .game_logic import WordPlayGame
from .lovelace import async_create_wordplay_dashboard

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up H.A WordPlay integration."""
    _LOGGER.info("Setting up H.A WordPlay integration")
    
    # Initialize the game instance
    game = WordPlayGame(hass)
    hass.data[DOMAIN] = {"game": game}
    
    # Create input_text helper entity
    await _create_input_text_helper(hass)
    
    # Create automation for auto-submit
    await _create_auto_submit_automation(hass)
    
    # Register services
    async def handle_new_game(call: ServiceCall) -> None:
        """Handle new game service call."""
        word_length = call.data.get("word_length", 5)
        await game.start_new_game(word_length)
    
    async def handle_make_guess(call: ServiceCall) -> None:
        """Handle make guess service call."""
        guess = call.data.get("guess", "").upper()
        if guess:
            result = await game.make_guess(guess)
            # Clear input field after successful guess
            if "error" not in result:
                await _clear_input_field(hass)
    
    async def handle_get_hint(call: ServiceCall) -> None:
        """Handle get hint service call."""
        await game.get_hint()
    
    async def handle_submit_guess(call: ServiceCall) -> None:
        """Handle submit current guess service call."""
        current_guess = hass.states.get("input_text.ha_wordplay_guess")
        if current_guess and current_guess.state:
            guess = current_guess.state.upper()
            result = await game.make_guess(guess)
            # Clear input field after submission
            await _clear_input_field(hass)
    
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
        DOMAIN, "submit_guess", handle_submit_guess
    )
    
    # Create WordPlay dashboard configuration
    await async_create_wordplay_dashboard(hass)
    
    _LOGGER.info("H.A WordPlay integration setup complete")
    return True

async def _create_input_text_helper(hass: HomeAssistant) -> None:
    """Create input_text helper for word guessing."""
    try:
        # Create the input_text entity using HA's helper creation
        entity_id = "input_text.ha_wordplay_guess"
        
        # Use the input_text component's create method
        input_text_data = {
            "name": "WordPlay Guess Input",
            "min": 4,
            "max": 8,
            "pattern": "[A-Za-z]*",
            "initial": ""
        }
        
        # Create via service call
        await hass.services.async_call(
            "input_text", "reload",
            {},
            blocking=True
        )
        
        # Set initial state manually
        hass.states.async_set(
            entity_id,
            "",
            {
                "friendly_name": "WordPlay Guess Input",
                "min": 4,
                "max": 8,
                "pattern": "[A-Za-z]*",
                "editable": True
            }
        )
        
        _LOGGER.info("Created input_text helper: %s", entity_id)
    except Exception as e:
        _LOGGER.error("Could not create input_text helper: %s", e)

async def _create_auto_submit_automation(hass: HomeAssistant) -> None:
    """Create automation for auto-submitting guesses."""
    try:
        # This will be handled by our service instead of a separate automation
        # to keep everything within the integration
        _LOGGER.info("Auto-submit will be handled by submit_guess service")
    except Exception as e:
        _LOGGER.warning("Could not create automation: %s", e)

async def _clear_input_field(hass: HomeAssistant) -> None:
    """Clear the input field after a guess."""
    try:
        await hass.services.async_call(
            "input_text", "set_value",
            {"entity_id": "input_text.ha_wordplay_guess", "value": ""},
            blocking=False
        )
    except Exception as e:
        _LOGGER.debug("Could not clear input field: %s", e)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload H.A WordPlay integration."""
    _LOGGER.info("Unloading H.A WordPlay integration")
    
    # Remove services
    hass.services.async_remove(DOMAIN, SERVICE_NEW_GAME)
    hass.services.async_remove(DOMAIN, SERVICE_MAKE_GUESS)
    hass.services.async_remove(DOMAIN, SERVICE_GET_HINT)
    hass.services.async_remove(DOMAIN, "submit_guess")
    
    # Clean up data
    hass.data.pop(DOMAIN, None)
    
    return True
