# Rev 1.0 - Added i18n translation support ONLY - no other changes
"""Button platform for H.A WordPlay integration - Multi-User Version with User Selection."""
import logging
from typing import Optional, Any, Dict

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .wordplay_const import (
    DOMAIN,
    STATE_IDLE,
    STATE_PLAYING,
    STATE_WON,
    STATE_LOST,
    CONF_SELECTED_USERS,
)
from .wordplay_i18n import get_translator

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the button platform for WordPlay - Multi-User with User Selection."""
    
    # Get selected users from config
    domain_data = hass.data.get(DOMAIN, {})
    selected_user_ids = domain_data.get("selected_users", [])
    
    if not selected_user_ids:
        _LOGGER.warning("No users selected for WordPlay - no button entities will be created")
        return
    
    # Get all users from Home Assistant
    users = await hass.auth.async_get_users()
    
    entities = []
    
    # Store entity references
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    
    # Create entity only for selected users
    for user in users:
        if user.system_generated:
            continue  # Skip system users
        
        # Only create entities for selected users
        if user.id not in selected_user_ids:
            continue
            
        user_id = user.id
        entity = WordPlayGameButton(hass, user_id)
        entities.append(entity)
        
        # Store entity reference
        if user_id not in hass.data[DOMAIN]["entities"]:
            hass.data[DOMAIN]["entities"][user_id] = {}
        hass.data[DOMAIN]["entities"][user_id]["game_button"] = entity
        
        _LOGGER.info(f"Created WordPlay button for selected user: {user.name} ({user_id})")
    
    async_add_entities(entities, True)
    _LOGGER.info(f"WordPlay created {len(entities)} game button entities for {len(selected_user_ids)} selected users")


class WordPlayGameButton(ButtonEntity):
    """Main game button entity - one per user."""

    def __init__(self, hass: HomeAssistant, user_id: str) -> None:
        """Initialize the game button."""
        super().__init__()
        self.hass = hass
        self.user_id = user_id
        self._attr_name = f"WordPlay Game ({user_id})"
        self._attr_unique_id = f"{DOMAIN}_game_button_{user_id}"
        self._attr_entity_category = None
        self._attr_icon = "mdi:gamepad-variant"
        self._attr_extra_state_attributes = {}
        self._hint_requested = False  # Track if hint has been requested
        
        # Get translator instance for i18n support
        self.translator = get_translator()
        
        # Set entity_id explicitly
        self.entity_id = f"button.ha_wordplay_game_{user_id}"

    def _t(self, key: str, **kwargs) -> str:
        """Helper method to get translations."""
        # Get the game's current language if available
        game_data = self.hass.data.get(DOMAIN, {})
        games = game_data.get("games", {})
        game = games.get(self.user_id)
        
        language = "en"  # Default
        if game and hasattr(game, 'language'):
            language = game.language
        
        if self.translator:
            return self.translator.get(key, language, **kwargs)
        # Fallback if translator not available - return hardcoded English
        fallbacks = {
            "backend.readyToPlay": "Ready to Play",
            "backend.playingStatus": f"Playing ({kwargs.get('letters', '?')} letters, {kwargs.get('remaining', '?')} guesses left)",
            "backend.wonStatus": f"Won in {kwargs.get('guesses', '?')} guesses! 🎉",
            "backend.lostStatus": f"Game Over - Word was {kwargs.get('word', 'UNKNOWN')}",
            "backend.noGuessesYet": "No guesses yet",
            "backend.clickToStart": "Click to start a new WordPlay game!",
            "backend.unknown": "Unknown"
        }
        return fallbacks.get(key, key)

    @property
    def name(self) -> str:
        """Return the name of the button."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return self._attr_unique_id

    @property
    def icon(self) -> str:
        """Return the icon."""
        # Dynamic icon based on game state
        game_data = self.hass.data.get(DOMAIN, {})
        games = game_data.get("games", {})
        game = games.get(self.user_id)
        
        if game:
            if game.game_state == STATE_PLAYING:
                return "mdi:gamepad-variant"
            elif game.game_state == STATE_WON:
                return "mdi:trophy"
            elif game.game_state == STATE_LOST:
                return "mdi:emoticon-sad"
        return "mdi:gamepad-variant"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return rich attributes for more-info dialog."""
        try:
            game_data = self.hass.data.get(DOMAIN, {})
            games = game_data.get("games", {})
            game = games.get(self.user_id)
            
            if not game:
                return {
                    "user_id": self.user_id,
                    "game_status": self._t("backend.readyToPlay"),
                    "instructions": self._t("backend.clickToStart"),
                    "friendly_name": self._attr_name,
                    "icon": "mdi:gamepad-variant"
                }
            
            # Format game state for rich display
            attributes = {
                "user_id": self.user_id,
                "game_status": self._format_game_status(game),
                "word_length": game.word_length,
                "guesses_made": len(game.guesses),
                "guesses_remaining": game.word_length - len(game.guesses),
                "max_guesses": game.word_length,
                "friendly_name": self._attr_name,
                "icon": self.icon
            }
            
            # Add revealed word for lost games
            if game.game_state == STATE_LOST and hasattr(game, 'revealed_word') and game.revealed_word:
                attributes["revealed_word"] = game.revealed_word
                attributes["word_reveal_message"] = f"The word was: {game.revealed_word}"
            
            # Add current game info if playing
            if game.game_state == STATE_PLAYING:
                # FIXED: Only show hint if it's been requested or difficulty is easy
                hint_to_show = ""
                if game.difficulty == "easy" and game.hint:
                    hint_to_show = game.hint
                    self._hint_requested = True
                elif self._hint_requested and game.hint:
                    hint_to_show = game.hint
                
                attributes.update({
                    "current_word_length": f"{game.word_length} letters",
                    "hint": hint_to_show if hint_to_show else self._t("backend.clickForHint"),
                    "hint_shown": bool(hint_to_show),  # Track if hint is displayed
                    "current_input": self._format_current_input(game),
                    "latest_guess": self._format_latest_guess(game),
                })
            else:
                # Reset hint tracking when game ends
                self._hint_requested = False
            
            # Add guess history
            if game.guesses:
                attributes["guess_history"] = self._format_guess_history(game)
                attributes["guess_results"] = self._format_guess_results(game)
            
            # Add game messages
            if game.last_message:
                attributes["last_message"] = game.last_message
                attributes["message_type"] = game.message_type
            
            # Add service call hints for more-info dialog
            attributes.update({
                "available_actions": [
                    "🎮 New Game - Start a new word puzzle",
                    "🔍 Submit Guess - Submit your current guess",
                    "💡 Get Hint - Get a clue about the word",
                    "⚙️ Settings - Change word length"
                ],
                "how_to_play": [
                    "1. Type your guess in the text field",
                    "2. Use Submit Guess to check your answer", 
                    "3. 🟦 = Correct letter & position",
                    "4. 🟥 = Correct letter, wrong position",
                    "5. ⬜ = Letter not in word"
                ]
            })
            
            return attributes
            
        except Exception as e:
            _LOGGER.error(f"Error generating button attributes for user {self.user_id}: {e}")
            return {
                "user_id": self.user_id,
                "game_status": "Error",
                "error": str(e),
                "friendly_name": self._attr_name
            }

    def _format_game_status(self, game) -> str:
        """Format game status for display."""
        if game.game_state == STATE_IDLE:
            return self._t("backend.readyToPlay")
        elif game.game_state == STATE_PLAYING:
            return self._t("backend.playingStatus", 
                          letters=game.word_length, 
                          remaining=game.word_length - len(game.guesses))
        elif game.game_state == STATE_WON:
            return self._t("backend.wonStatus", guesses=len(game.guesses))
        elif game.game_state == STATE_LOST:
            word = game.revealed_word or self._t("backend.unknown")
            return self._t("backend.lostStatus", word=word)
        return self._t("backend.unknown")

    def _format_current_input(self, game) -> str:
        """Format current input for display."""
        if game.current_guess_input:
            # Pad to word length with underscores
            padded = game.current_guess_input.ljust(game.word_length, '_')
            return ' '.join(padded)
        return ' '.join(['_'] * game.word_length)

    def _format_latest_guess(self, game) -> str:
        """Format latest guess with results."""
        if not game.guesses or not game.latest_result:
            return self._t("backend.noGuessesYet")
        
        latest_guess = game.guesses[-1]
        result_display = []
        
        for letter, result in zip(latest_guess, game.latest_result):
            if result == "correct":
                result_display.append(f"{letter}🟦")
            elif result == "partial":
                result_display.append(f"{letter}🟥")
            else:
                result_display.append(f"{letter}⬜")
        
        return " ".join(result_display)

    def _format_guess_history(self, game) -> list:
        """Format all guesses for display."""
        history = []
        for i, guess in enumerate(game.guesses):
            history.append(f"{i+1}. {guess}")
        return history

    def _format_guess_results(self, game) -> list:
        """Format all guess results for display."""
        results = []
        for guess, result in zip(game.guesses, game.guess_results):
            result_display = []
            for letter, status in zip(guess, result):
                if status == "correct":
                    result_display.append(f"{letter}🟦")
                elif status == "partial":
                    result_display.append(f"{letter}🟥")
                else:
                    result_display.append(f"{letter}⬜")
            results.append(" ".join(result_display))
        return results

    async def async_press(self) -> None:
        """Handle button press - start new game or show game info."""
        try:
            # Get game instance for this user
            game_data = self.hass.data.get(DOMAIN, {})
            games = game_data.get("games", {})
            
            # Create game if doesn't exist
            if self.user_id not in games:
                from .wordplay_game_logic import WordPlayGame
                game = WordPlayGame(self.hass, self.user_id)  # Pass user_id to constructor
                
                # Set difficulty
                difficulty = game_data.get("difficulty", "normal")
                game.set_difficulty(difficulty)
                
                games[self.user_id] = game
            
            game = games[self.user_id]
            
            # If no game in progress, start a new one
            if game.game_state in [STATE_IDLE, STATE_WON, STATE_LOST]:
                # Reset hint tracking for new game
                self._hint_requested = False
                
                # Get word length from user's select entity or use default
                word_length = 5
                try:
                    select_state = self.hass.states.get(f"select.ha_wordplay_word_length_{self.user_id}")
                    if select_state and select_state.state:
                        word_length = int(select_state.state)
                except (ValueError, TypeError):
                    word_length = 5
                
                # Get language from user's language select entity if available
                language = "en"  # Default to English
                try:
                    # Check if there's a language select entity for this user
                    lang_select_state = self.hass.states.get(f"select.ha_wordplay_language_{self.user_id}")
                    if lang_select_state and lang_select_state.state:
                        language = lang_select_state.state
                except Exception:
                    # If no language entity, keep default
                    pass
                
                # FIXED: Now passing both word_length AND language parameters
                success = await game.start_new_game(word_length, language)
                if success:
                    _LOGGER.info(f"New game started from button press for user {self.user_id}: {word_length} letters, language: {language}")
                else:
                    _LOGGER.error(f"Failed to start new game from button press for user {self.user_id}")
            
            # Update button attributes to reflect new state
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error handling button press for user {self.user_id}: {e}")

    def update_attributes(self) -> None:
        """Update button attributes when game state changes."""
        # Check if hint was requested
        game_data = self.hass.data.get(DOMAIN, {})
        games = game_data.get("games", {})
        game = games.get(self.user_id)
        
        if game and hasattr(game, 'hint') and game.hint and game.game_state == STATE_PLAYING:
            # If game has a hint and we're playing, mark it as requested
            # This handles the case where get_hint service was called
            if game.last_message and "Hint:" in game.last_message:
                self._hint_requested = True
        
        self.async_write_ha_state()
