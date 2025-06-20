"""H.A WordPlay integration for Home Assistant - Fixed Platform Setup."""
import logging
import asyncio
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import Platform

from .const import (
    DOMAIN,
    SERVICE_NEW_GAME,
    SERVICE_MAKE_GUESS,
    SERVICE_GET_HINT,
    SERVICE_SUBMIT_GUESS,
    DEFAULT_WORD_LENGTH,
)
from .game_logic import WordPlayGame
from .lovelace import async_create_wordplay_dashboard

_LOGGER = logging.getLogger(__name__)

# Define the platforms this integration provides
PLATFORMS = [Platform.TEXT, Platform.SELECT, Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up H.A WordPlay integration."""
    _LOGGER.info("Setting up H.A WordPlay integration with modern platform setup")
    
    # Initialize TTS configuration
    tts_config = await _setup_tts_config(hass)
    
    # Initialize the game instance
    game = WordPlayGame(hass)
    
    # Store game and configuration data
    hass.data[DOMAIN] = {
        "game": game,
        "entities": {},
        "tts_config": tts_config,
        "platforms_loaded": []
    }
    
    # Set up platforms using modern approach
    try:
        await _setup_platforms(hass)
        _LOGGER.info("All platforms setup initiated")
    except Exception as e:
        _LOGGER.error(f"Platform setup failed: {e}")
        return False
    
    # Wait for entities to be created before setting up services
    await _wait_for_entities(hass)
    
    # Set up state tracking for live input updates
    async def handle_input_change(event):
        """Handle changes to the text input."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        if new_state and entity_id == "text.ha_wordplay_guess_input":
            await game.update_current_input(new_state.state or "")
    
    # Track the text input entity with error handling
    try:
        async_track_state_change_event(
            hass, ["text.ha_wordplay_guess_input"], handle_input_change
        )
        _LOGGER.debug("State tracking setup for text input")
    except Exception as e:
        _LOGGER.warning(f"Could not setup state tracking: {e}")
    
    # Register services after entities are ready
    await _register_services(hass, game)
    
    # Create WordPlay dashboard configuration
    await async_create_wordplay_dashboard(hass)
    
    _LOGGER.info("H.A WordPlay integration setup complete with modern platform setup")
    return True

async def _setup_platforms(hass: HomeAssistant) -> None:
    """Set up platforms using modern HA approach."""
    from .text import async_setup_platform as setup_text
    from .select import async_setup_platform as setup_select
    from .sensor import async_setup_platform as setup_sensor
    
    # Setup text platform
    try:
        await setup_text(hass, {}, lambda entities: _store_entities(hass, "text", entities), None)
        hass.data[DOMAIN]["platforms_loaded"].append("text")
        _LOGGER.info("Text platform setup completed")
    except Exception as e:
        _LOGGER.error(f"Text platform setup failed: {e}")
        raise
    
    # Setup select platform
    try:
        await setup_select(hass, {}, lambda entities: _store_entities(hass, "select", entities), None)
        hass.data[DOMAIN]["platforms_loaded"].append("select")
        _LOGGER.info("Select platform setup completed")
    except Exception as e:
        _LOGGER.error(f"Select platform setup failed: {e}")
        raise
    
    # Setup sensor platform - ACTUALLY CALL IT NOW!
    try:
        await setup_sensor(hass, {}, lambda entities: _store_entities(hass, "sensor", entities), None)
        hass.data[DOMAIN]["platforms_loaded"].append("sensor")
        _LOGGER.info("Sensor platform setup completed")
    except Exception as e:
        _LOGGER.error(f"Sensor platform setup failed: {e}")
        raise

def _store_entities(hass: HomeAssistant, platform: str, entities: list) -> None:
    """Store entity references for service access."""
    for entity in entities:
        if platform == "text" and hasattr(entity, '_attr_unique_id'):
            if "guess_input" in entity._attr_unique_id:
                hass.data[DOMAIN]["entities"]["text_input"] = entity
                _LOGGER.debug("Text input entity stored")
        elif platform == "select" and hasattr(entity, '_attr_unique_id'):
            if "word_length" in entity._attr_unique_id:
                hass.data[DOMAIN]["entities"]["word_length"] = entity
                _LOGGER.debug("Word length selector entity stored")
        elif platform == "sensor" and hasattr(entity, '_attr_unique_id'):
            if "game_state" in entity._attr_unique_id:
                hass.data[DOMAIN]["entities"]["game_state"] = entity
                _LOGGER.debug("Game state sensor entity stored")
            elif "guesses" in entity._attr_unique_id:
                hass.data[DOMAIN]["entities"]["guesses"] = entity
                _LOGGER.debug("Guesses sensor entity stored")
            elif "debug" in entity._attr_unique_id:
                hass.data[DOMAIN]["entities"]["debug"] = entity
                _LOGGER.debug("Debug sensor entity stored")

async def _wait_for_entities(hass: HomeAssistant, max_wait: int = 10) -> None:
    """Wait for entities to be created with timeout."""
    _LOGGER.info("Waiting for entities to be created...")
    
    wait_count = 0
    while wait_count < max_wait:
        # Check if key entities exist in state registry
        text_entity = hass.states.get("text.ha_wordplay_guess_input")
        select_entity = hass.states.get("select.ha_wordplay_word_length")
        game_state_entity = hass.states.get("sensor.ha_wordplay_game_state")
        guesses_entity = hass.states.get("sensor.ha_wordplay_guesses")
        
        if (text_entity is not None and 
            select_entity is not None and 
            game_state_entity is not None and 
            guesses_entity is not None):
            _LOGGER.info("All required entities detected in state registry")
            break
        
        _LOGGER.debug(f"Waiting for entities... attempt {wait_count + 1}/{max_wait}")
        _LOGGER.debug(f"Text entity: {'✓' if text_entity else '✗'}")
        _LOGGER.debug(f"Select entity: {'✓' if select_entity else '✗'}")
        _LOGGER.debug(f"Game state sensor: {'✓' if game_state_entity else '✗'}")
        _LOGGER.debug(f"Guesses sensor: {'✓' if guesses_entity else '✗'}")
        
        await asyncio.sleep(1)
        wait_count += 1
    
    if wait_count >= max_wait:
        _LOGGER.warning("Timeout waiting for entities - proceeding with service registration")
    else:
        _LOGGER.info("Entity creation verified - proceeding with service registration")

async def _register_services(hass: HomeAssistant, game: WordPlayGame) -> None:
    """Register all game services."""
    _LOGGER.info("Registering H.A WordPlay services...")
    
    async def handle_new_game(call: ServiceCall) -> None:
        """Handle new game service call."""
        try:
            # Get word length from select entity or service data
            word_length = call.data.get("word_length")
            
            if not word_length:
                # Try to get from select entity
                select_entity = hass.data[DOMAIN]["entities"].get("word_length")
                if select_entity:
                    word_length = select_entity.get_selected_length()
                else:
                    # Fallback: check state directly
                    select_state = hass.states.get("select.ha_wordplay_word_length")
                    if select_state:
                        word_length = int(select_state.state)
                    else:
                        word_length = DEFAULT_WORD_LENGTH
            
            success = await game.start_new_game(int(word_length))
            
            if success:
                _LOGGER.info(f"New game started with {word_length} letters")
            else:
                _LOGGER.error("Failed to start new game")
        except Exception as e:
            _LOGGER.error(f"Error in new_game service: {e}")
    
    async def handle_make_guess(call: ServiceCall) -> None:
        """Handle make guess service call."""
        try:
            guess = call.data.get("guess", "").upper()
            if guess:
                result = await game.make_guess(guess)
                if "error" in result:
                    _LOGGER.warning(f"Guess error: {result['error']}")
                else:
                    _LOGGER.info(f"Guess processed: {guess}")
            else:
                _LOGGER.warning("No guess provided to make_guess service")
        except Exception as e:
            _LOGGER.error(f"Error in make_guess service: {e}")
    
    async def handle_get_hint(call: ServiceCall) -> None:
        """Handle get hint service call."""
        try:
            hint = await game.get_hint()
            _LOGGER.info(f"Hint requested: {hint}")
        except Exception as e:
            _LOGGER.error(f"Error in get_hint service: {e}")
    
    async def handle_submit_guess(call: ServiceCall) -> None:
        """Handle submit current guess service call."""
        try:
            # Try multiple methods to get current input
            guess = None
            
            # Method 1: From stored entity reference
            text_entity = hass.data[DOMAIN]["entities"].get("text_input")
            if text_entity and hasattr(text_entity, 'native_value'):
                guess = text_entity.native_value
            
            # Method 2: From state directly
            if not guess:
                text_state = hass.states.get("text.ha_wordplay_guess_input")
                if text_state:
                    guess = text_state.state
            
            if guess and guess.strip() and guess.upper() != "HELLO":
                guess = guess.upper().strip()
                result = await game.make_guess(guess)
                if "error" in result:
                    _LOGGER.warning(f"Submit guess error: {result['error']}")
                else:
                    _LOGGER.info(f"Guess submitted: {guess}")
            else:
                _LOGGER.warning("No valid guess to submit")
        except Exception as e:
            _LOGGER.error(f"Error in submit_guess service: {e}")
    
    # Register the services with error handling
    try:
        hass.services.async_register(DOMAIN, SERVICE_NEW_GAME, handle_new_game)
        _LOGGER.debug("Registered new_game service")
        
        hass.services.async_register(DOMAIN, SERVICE_MAKE_GUESS, handle_make_guess)
        _LOGGER.debug("Registered make_guess service")
        
        hass.services.async_register(DOMAIN, SERVICE_GET_HINT, handle_get_hint)
        _LOGGER.debug("Registered get_hint service")
        
        hass.services.async_register(DOMAIN, SERVICE_SUBMIT_GUESS, handle_submit_guess)
        _LOGGER.debug("Registered submit_guess service")
        
        _LOGGER.info("All H.A WordPlay services registered successfully")
        
    except Exception as e:
        _LOGGER.error(f"Service registration failed: {e}")
        raise

async def _setup_tts_config(hass: HomeAssistant) -> Dict[str, Any]:
    """Set up TTS configuration with smart defaults."""
    try:
        # Check available TTS services
        tts_services = hass.services.async_services().get("tts", {})
        tts_available = len(tts_services) > 0
        
        # Find suitable media players
        media_players = []
        for entity_id in hass.states.async_entity_ids("media_player"):
            state = hass.states.get(entity_id)
            if state and state.state != "unavailable":
                media_players.append(entity_id)
        
        # Auto-configure based on available services/devices
        config = {
            "enabled": tts_available,  # Enable if TTS service exists, regardless of speakers
            "media_player": media_players[0] if media_players else "media_player.dummy",
            "language": "en",
            "voice": None,  # Use default
        }
        
        if config["enabled"]:
            _LOGGER.info(f"TTS auto-configured: service available, target: {config['media_player']}")
        else:
            _LOGGER.info("TTS disabled: no TTS service found")
        
        return config
        
    except Exception as e:
        _LOGGER.error(f"TTS configuration error: {e}")
        return {"enabled": False}

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload H.A WordPlay integration."""
    _LOGGER.info("Unloading H.A WordPlay integration")
    
    # Remove services
    try:
        hass.services.async_remove(DOMAIN, SERVICE_NEW_GAME)
        hass.services.async_remove(DOMAIN, SERVICE_MAKE_GUESS)
        hass.services.async_remove(DOMAIN, SERVICE_GET_HINT)
        hass.services.async_remove(DOMAIN, SERVICE_SUBMIT_GUESS)
        _LOGGER.info("Services removed successfully")
    except Exception as e:
        _LOGGER.warning(f"Error removing services: {e}")
    
    # Clean up data
    hass.data.pop(DOMAIN, None)
    
    return True