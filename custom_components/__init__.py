"""H.A WordPlay integration for Home Assistant."""
import logging
import asyncio
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    SERVICE_NEW_GAME,
    SERVICE_MAKE_GUESS,
    SERVICE_GET_HINT,
)
from .game_logic import WordPlayGame

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up H.A WordPlay integration."""
    _LOGGER.info("Setting up H.A WordPlay integration")
    
    # Initialize the game instance
    game = WordPlayGame(hass)
    hass.data[DOMAIN] = {"game": game}
    
    # Register services
    async def handle_new_game(call: ServiceCall) -> None:
        """Handle new game service call."""
        word_length = call.data.get("word_length", 5)
        await game.start_new_game(word_length)
    
    async def handle_make_guess(call: ServiceCall) -> None:
        """Handle make guess service call."""
        guess = call.data.get("guess", "").upper()
        if guess:
            await game.make_guess(guess)
    
    async def handle_get_hint(call: ServiceCall) -> None:
        """Handle get hint service call."""
        await game.get_hint()
    
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
    
    _LOGGER.info("H.A WordPlay integration setup complete")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload H.A WordPlay integration."""
    _LOGGER.info("Unloading H.A WordPlay integration")
    
    # Remove services
    hass.services.async_remove(DOMAIN, SERVICE_NEW_GAME)
    hass.services.async_remove(DOMAIN, SERVICE_MAKE_GUESS)
    hass.services.async_remove(DOMAIN, SERVICE_GET_HINT)
    
    # Clean up data
    hass.data.pop(DOMAIN, None)
    
    return True
