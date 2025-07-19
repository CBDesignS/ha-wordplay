"""H.A WordPlay integration for Home Assistant - Multi-User Version.
Enhanced to support multiple simultaneous players with isolated game states.
"""
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
    CONF_DIFFICULTY,
    CONF_AUDIO_ENABLED,
    CONF_AUDIO_VOLUME,
    CONF_AUDIO_GAME_EVENTS,
    CONF_AUDIO_GUESS_EVENTS,
    CONF_AUDIO_UI_EVENTS,
    CONF_AUDIO_ERROR_EVENTS,
    DEFAULT_AUDIO_ENABLED,
    DEFAULT_AUDIO_VOLUME,
    DEFAULT_AUDIO_GAME_EVENTS,
    DEFAULT_AUDIO_GUESS_EVENTS,
    DEFAULT_AUDIO_UI_EVENTS,
    DEFAULT_AUDIO_ERROR_EVENTS,
)
from .game_logic import WordPlayGame
from .api_config import get_supported_languages

# Config flow constants
DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal" 
DIFFICULTY_HARD = "hard"

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up H.A WordPlay integration from YAML (legacy support)."""
    _LOGGER.info("WordPlay YAML setup detected - please migrate to config entry via UI")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up H.A WordPlay from a config entry - Multi-User Version."""
    _LOGGER.info("Setting up H.A WordPlay Multi-User integration from config entry")
    
    # Get configuration from entry
    config_data = entry.data
    access_token = config_data.get(CONF_ACCESS_TOKEN)
    difficulty = config_data.get(CONF_DIFFICULTY, DIFFICULTY_NORMAL)
    
    # Get audio configuration with defaults
    audio_config = {
        CONF_AUDIO_ENABLED: config_data.get(CONF_AUDIO_ENABLED, DEFAULT_AUDIO_ENABLED),
        CONF_AUDIO_VOLUME: config_data.get(CONF_AUDIO_VOLUME, DEFAULT_AUDIO_VOLUME),
        CONF_AUDIO_GAME_EVENTS: config_data.get(CONF_AUDIO_GAME_EVENTS, DEFAULT_AUDIO_GAME_EVENTS),
        CONF_AUDIO_GUESS_EVENTS: config_data.get(CONF_AUDIO_GUESS_EVENTS, DEFAULT_AUDIO_GUESS_EVENTS),
        CONF_AUDIO_UI_EVENTS: config_data.get(CONF_AUDIO_UI_EVENTS, DEFAULT_AUDIO_UI_EVENTS),
        CONF_AUDIO_ERROR_EVENTS: config_data.get(CONF_AUDIO_ERROR_EVENTS, DEFAULT_AUDIO_ERROR_EVENTS),
    }
    
    if not access_token:
        _LOGGER.error("No access token found in config entry")
        return False
    
    _LOGGER.info(f"WordPlay config: difficulty={difficulty}, audio_enabled={audio_config[CONF_AUDIO_ENABLED]}")
    
    # Initialize TTS configuration
    tts_config = await _setup_tts_config(hass)
    
    # Initialize multi-user game storage
    hass.data[DOMAIN] = {
        "games": {},  # Will store {user_id: game_instance}
        "entities": {},  # Will store {user_id: {entity_type: entity}}
        "config_entry": entry,
        "access_token": access_token,
        "difficulty": difficulty,
        "audio_config": audio_config,
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
    
    # Register services with multi-user support
    await _register_services(hass)
    
    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    
    _LOGGER.info("H.A WordPlay Multi-User integration setup complete!")
    return True

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener for config entry changes."""
    _LOGGER.info("WordPlay configuration updated, reloading...")
    await hass.config_entries.async_reload(entry.entry_id)

async def _register_wordplay_html_panel(hass: HomeAssistant, access_token: str) -> None:
    """Register the WordPlay HTML panel with secure token passing and audio configuration."""
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
        
        # Get audio config from stored data
        domain_data = hass.data.get(DOMAIN, {})
        audio_config = domain_data.get("audio_config", {})
        
        # Create the panel URL with access token
        panel_url = f"/hacsfiles/ha_wordplay/wordplay_game.html?access_token={access_token}"
        
        # Add audio parameters manually
        if audio_config:
            audio_enabled = str(audio_config.get(CONF_AUDIO_ENABLED, DEFAULT_AUDIO_ENABLED)).lower()
            audio_volume = str(audio_config.get(CONF_AUDIO_VOLUME, DEFAULT_AUDIO_VOLUME))
            audio_game_events = str(audio_config.get(CONF_AUDIO_GAME_EVENTS, DEFAULT_AUDIO_GAME_EVENTS)).lower()
            audio_guess_events = str(audio_config.get(CONF_AUDIO_GUESS_EVENTS, DEFAULT_AUDIO_GUESS_EVENTS)).lower()
            audio_ui_events = str(audio_config.get(CONF_AUDIO_UI_EVENTS, DEFAULT_AUDIO_UI_EVENTS)).lower()
            audio_error_events = str(audio_config.get(CONF_AUDIO_ERROR_EVENTS, DEFAULT_AUDIO_ERROR_EVENTS)).lower()
            
            panel_url += f"&audio_enabled={audio_enabled}"
            panel_url += f"&audio_volume={audio_volume}"
            panel_url += f"&audio_gameEvents={audio_game_events}"
            panel_url += f"&audio_guessEvents={audio_guess_events}"
            panel_url += f"&audio_uiEvents={audio_ui_events}"
            panel_url += f"&audio_errorEvents={audio_error_events}"
        
        # Register iframe panel with secure token URL and audio config
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
        
        _LOGGER.info("WordPlay iframe panel registered successfully with secure token and audio config!")
        
    except Exception as e:
        _LOGGER.error(f"Failed to register WordPlay HTML panel: {e}")

def _get_user_id(call: ServiceCall) -> str:
    """Extract user ID from service call context."""
    # For now, always use 'default' until we implement proper user detection
    # The frontend is using 'default' entities, so backend must match
    return "default"
    
    # TODO: Future implementation when we have proper user detection
    # user_id = call.context.user_id
    # if not user_id:
    #     user_id = "default"
    # return user_id

def _get_or_create_game(hass: HomeAssistant, user_id: str) -> WordPlayGame:
    """Get existing game instance for user or create new one."""
    games = hass.data[DOMAIN]["games"]
    
    if user_id not in games:
        _LOGGER.info(f"Creating new game instance for user: {user_id}")
        game = WordPlayGame(hass)
        
        # Set difficulty from config
        difficulty = hass.data[DOMAIN].get("difficulty", DIFFICULTY_NORMAL)
        game.set_difficulty(difficulty)
        
        games[user_id] = game
    
    return games[user_id]

async def _update_button_attributes(hass: HomeAssistant, user_id: str) -> None:
    """Update button entity attributes for specific user when game state changes."""
    try:
        domain_data = hass.data.get(DOMAIN, {})
        user_entities = domain_data.get("entities", {}).get(user_id, {})
        button_entity = user_entities.get("game_button")
        
        if button_entity:
            button_entity.update_attributes()
    except Exception as e:
        _LOGGER.debug(f"Could not update button attributes for user {user_id}: {e}")

async def _register_services(hass: HomeAssistant) -> None:
    """Register all game services with multi-user support."""
    _LOGGER.info("Registering H.A WordPlay multi-user services...")
    
    async def handle_new_game(call: ServiceCall) -> None:
        """Handle new game service call."""
        try:
            user_id = _get_user_id(call)
            game = _get_or_create_game(hass, user_id)
            
            word_length = call.data.get("word_length", DEFAULT_WORD_LENGTH)
            language = call.data.get("language", "en")
            
            # Try to get from user's select entity if not provided
            if not word_length or word_length == DEFAULT_WORD_LENGTH:
                select_state = hass.states.get(f"select.ha_wordplay_word_length_{user_id}")
                if select_state and select_state.state:
                    try:
                        word_length = int(select_state.state)
                    except (ValueError, TypeError):
                        word_length = DEFAULT_WORD_LENGTH
            
            success = await game.start_new_game(int(word_length), language)
            
            if success:
                _LOGGER.info(f"New game started for user {user_id}: {word_length} letters, language: {language}")
                await _update_button_attributes(hass, user_id)
            else:
                _LOGGER.error(f"Failed to start new game for user {user_id}")
        except Exception as e:
            _LOGGER.error(f"Error in new_game service: {e}")
    
    async def handle_make_guess(call: ServiceCall) -> None:
        """Handle make guess service call."""
        try:
            user_id = _get_user_id(call)
            game = _get_or_create_game(hass, user_id)
            
            guess = call.data.get("guess", "").upper()
            if guess:
                result = await game.make_guess(guess)
                if "error" in result:
                    _LOGGER.warning(f"Guess error for user {user_id}: {result['error']}")
                else:
                    _LOGGER.info(f"Guess processed for user {user_id}: {guess}")
                await _update_button_attributes(hass, user_id)
            else:
                _LOGGER.warning(f"No guess provided to make_guess service for user {user_id}")
        except Exception as e:
            _LOGGER.error(f"Error in make_guess service: {e}")
    
    async def handle_get_hint(call: ServiceCall) -> None:
        """Handle get hint service call."""
        try:
            user_id = _get_user_id(call)
            game = _get_or_create_game(hass, user_id)
            
            hint = await game.get_hint()
            _LOGGER.info(f"Hint requested by user {user_id}: {hint}")
            await _update_button_attributes(hass, user_id)
        except Exception as e:
            _LOGGER.error(f"Error in get_hint service: {e}")
    
    async def handle_submit_guess(call: ServiceCall) -> None:
        """Handle submit current guess service call."""
        try:
            user_id = _get_user_id(call)
            game = _get_or_create_game(hass, user_id)
            
            # Get current input from user's text entity state
            text_state = hass.states.get(f"text.ha_wordplay_guess_input_{user_id}")
            guess = None
            
            if text_state and text_state.state:
                guess = text_state.state.upper().strip()
            
            if guess and guess != "HELLO":
                result = await game.make_guess(guess)
                if "error" in result:
                    _LOGGER.warning(f"Submit guess error for user {user_id}: {result['error']}")
                else:
                    _LOGGER.info(f"Guess submitted by user {user_id}: {guess}")
                await _update_button_attributes(hass, user_id)
            else:
                _LOGGER.warning(f"No valid guess to submit for user {user_id}")
        except Exception as e:
            _LOGGER.error(f"Error in submit_guess service: {e}")
    
    # Register the services
    try:
        hass.services.async_register(DOMAIN, SERVICE_NEW_GAME, handle_new_game)
        hass.services.async_register(DOMAIN, SERVICE_MAKE_GUESS, handle_make_guess)
        hass.services.async_register(DOMAIN, SERVICE_GET_HINT, handle_get_hint)
        hass.services.async_register(DOMAIN, SERVICE_SUBMIT_GUESS, handle_submit_guess)
        
        _LOGGER.info("All H.A WordPlay multi-user services registered successfully")
        
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