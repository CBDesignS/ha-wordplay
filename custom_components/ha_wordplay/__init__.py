"""H.A WordPlay integration for Home Assistant - Config Entry Version."""
import logging
import asyncio
import os
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers import discovery
from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_ACCESS_TOKEN

from .const import (
    DOMAIN,
    SERVICE_NEW_GAME,
    SERVICE_MAKE_GUESS,
    SERVICE_GET_HINT,
    SERVICE_SUBMIT_GUESS,
    DEFAULT_WORD_LENGTH,
)
from .game_logic import WordPlayGame
from .api_config import get_supported_languages

# Config flow constants
CONF_DIFFICULTY = "difficulty"
CONF_WORD_LENGTHS = "word_lengths"
DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal" 
DIFFICULTY_HARD = "hard"

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up H.A WordPlay integration from YAML (legacy support)."""
    # This is kept for backward compatibility but the main setup is now via config entry
    _LOGGER.info("WordPlay YAML setup detected - please migrate to config entry via UI")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up H.A WordPlay from a config entry."""
    _LOGGER.info("Setting up H.A WordPlay integration from config entry")
    
    # Get configuration from entry
    config_data = entry.data
    access_token = config_data.get(CONF_ACCESS_TOKEN)
    difficulty = config_data.get(CONF_DIFFICULTY, DIFFICULTY_NORMAL)
    word_lengths = config_data.get(CONF_WORD_LENGTHS, [5, 6, 7, 8])
    
    if not access_token:
        _LOGGER.error("No access token found in config entry")
        return False
    
    _LOGGER.info(f"WordPlay config: difficulty={difficulty}, word_lengths={word_lengths}")
    
    # Initialize TTS configuration
    tts_config = await _setup_tts_config(hass)
    
    # Initialize the game instance with config
    game = WordPlayGame(hass)
    game.set_difficulty(difficulty)
    game.set_word_lengths(word_lengths)
    
    # Store game and configuration data
    hass.data[DOMAIN] = {
        "game": game,
        "entities": {},
        "config_entry": entry,
        "access_token": access_token,
        "difficulty": difficulty,
        "word_lengths": word_lengths,
        "tts_config": tts_config,
        "supported_languages": get_supported_languages(),
    }
    
    # Load entity platforms using discovery
    await discovery.async_load_platform(hass, "button", DOMAIN, {}, {})
    await discovery.async_load_platform(hass, "text", DOMAIN, {}, {})
    await discovery.async_load_platform(hass, "select", DOMAIN, {}, {})
    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, {})
    
    # Wait a moment for entities to be created
    await asyncio.sleep(2)
    
    # Register the WordPlay HTML panel with secure token passing
    await _register_wordplay_html_panel(hass, access_token)
    
    # Set up state tracking for live input updates
    async def handle_input_change(event):
        """Handle changes to the text input."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        if new_state and entity_id == "text.ha_wordplay_guess_input":
            await game.update_current_input(new_state.state or "")
            # Update button attributes to reflect input changes
            await _update_button_attributes(hass)
    
    # Track the text input entity
    try:
        async_track_state_change_event(
            hass, ["text.ha_wordplay_guess_input"], handle_input_change
        )
        _LOGGER.debug("State tracking setup for text input")
    except Exception as e:
        _LOGGER.warning(f"Could not setup state tracking: {e}")
    
    # Register services
    await _register_services(hass, game)
    
    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    _LOGGER.info("H.A WordPlay integration setup complete - Config Entry Ready!")
    _LOGGER.info(f"Difficulty: {difficulty}, Word lengths: {word_lengths}")
    return True

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener for config entry changes."""
    _LOGGER.info("WordPlay configuration updated, reloading...")
    await hass.config_entries.async_reload(entry.entry_id)

async def _register_wordplay_html_panel(hass: HomeAssistant, access_token: str) -> None:
    """Register the WordPlay HTML panel with secure token passing."""
    try:
        # Get the integration directory path
        integration_dir = os.path.dirname(__file__)
        
        # Register static path for the integration files
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                url_path="/hacsfiles/ha_wordplay",
                path=integration_dir,
                cache_headers=False,
            )
        ])
        
        # Create the panel URL with the access token as a parameter
        # This is secure because it's only accessible to authenticated users
        panel_url = f"/hacsfiles/ha_wordplay/wordplay_game.html?access_token={access_token}"
        
        # Register iframe panel with secure token URL
        async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title="🎮 WordPlay",
            sidebar_icon="mdi:gamepad-variant",
            frontend_url_path="wordplay",
            config={
                "url": panel_url,
                "title": "🎮 H.A WordPlay",
            },
            require_admin=False,
        )
        
        _LOGGER.info("WordPlay iframe panel registered successfully with secure token!")
        _LOGGER.info("Panel will use dedicated long-lived access token")
        
    except Exception as e:
        _LOGGER.error(f"Failed to register WordPlay HTML panel: {e}")

async def _update_button_attributes(hass: HomeAssistant) -> None:
    """Update button entity attributes when game state changes."""
    try:
        domain_data = hass.data.get(DOMAIN, {})
        button_entity = domain_data.get("entities", {}).get("game_button")
        if button_entity:
            button_entity.update_attributes()
    except Exception as e:
        _LOGGER.debug(f"Could not update button attributes: {e}")

async def _register_services(hass: HomeAssistant, game: WordPlayGame) -> None:
    """Register all game services - enhanced for config entry support."""
    _LOGGER.info("Registering H.A WordPlay services...")
    
    async def handle_new_game(call: ServiceCall) -> None:
        """Handle new game service call."""
        try:
            word_length = call.data.get("word_length", DEFAULT_WORD_LENGTH)
            language = call.data.get("language", "en")
            
            # Try to get from select entity if not provided
            if not word_length or word_length == DEFAULT_WORD_LENGTH:
                select_state = hass.states.get("select.ha_wordplay_word_length")
                if select_state and select_state.state:
                    try:
                        word_length = int(select_state.state)
                    except (ValueError, TypeError):
                        word_length = DEFAULT_WORD_LENGTH
            
            # Check if word length is allowed by config
            domain_data = hass.data.get(DOMAIN, {})
            allowed_lengths = domain_data.get("word_lengths", [5, 6, 7, 8])
            if word_length not in allowed_lengths:
                _LOGGER.warning(f"Word length {word_length} not allowed by config, using default")
                word_length = allowed_lengths[0] if allowed_lengths else 5
            
            success = await game.start_new_game(int(word_length), language)
            
            if success:
                _LOGGER.info(f"New game started: {word_length} letters, language: {language}")
                await _update_button_attributes(hass)
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
                await _update_button_attributes(hass)
            else:
                _LOGGER.warning("No guess provided to make_guess service")
        except Exception as e:
            _LOGGER.error(f"Error in make_guess service: {e}")
    
    async def handle_get_hint(call: ServiceCall) -> None:
        """Handle get hint service call."""
        try:
            hint = await game.get_hint()
            _LOGGER.info(f"Hint requested: {hint}")
            await _update_button_attributes(hass)
        except Exception as e:
            _LOGGER.error(f"Error in get_hint service: {e}")
    
    async def handle_submit_guess(call: ServiceCall) -> None:
        """Handle submit current guess service call."""
        try:
            # Get current input from text entity state
            text_state = hass.states.get("text.ha_wordplay_guess_input")
            guess = None
            
            if text_state and text_state.state:
                guess = text_state.state.upper().strip()
            
            if guess and guess != "HELLO":
                result = await game.make_guess(guess)
                if "error" in result:
                    _LOGGER.warning(f"Submit guess error: {result['error']}")
                else:
                    _LOGGER.info(f"Guess submitted: {guess}")
                await _update_button_attributes(hass)
            else:
                _LOGGER.warning("No valid guess to submit")
        except Exception as e:
            _LOGGER.error(f"Error in submit_guess service: {e}")
    
    # Register the services
    try:
        hass.services.async_register(DOMAIN, SERVICE_NEW_GAME, handle_new_game)
        hass.services.async_register(DOMAIN, SERVICE_MAKE_GUESS, handle_make_guess)
        hass.services.async_register(DOMAIN, SERVICE_GET_HINT, handle_get_hint)
        hass.services.async_register(DOMAIN, SERVICE_SUBMIT_GUESS, handle_submit_guess)
        
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
            "enabled": False,  # Disable TTS for now to avoid test server noise
            "media_player": media_players[0] if media_players else "media_player.dummy",
            "language": "en-US",
            "voice": None,
        }
        
        if tts_available:
            _LOGGER.info(f"TTS auto-configured but disabled for testing: target: {config['media_player']}")
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