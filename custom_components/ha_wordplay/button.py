"""Button platform for H.A WordPlay integration - Single Game Button."""
import logging
from typing import Optional, Any, Dict

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    STATE_IDLE,
    STATE_PLAYING,
    STATE_WON,
    STATE_LOST,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the button platform for WordPlay."""
    
    # Create the main game button entity
    entity = WordPlayGameButton(hass)
    
    async_add_entities([entity], True)
    
    # Store entity reference
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    
    hass.data[DOMAIN]["entities"]["game_button"] = entity
    
    _LOGGER.info("WordPlay game button entity created")


class WordPlayGameButton(ButtonEntity):
    """Main game button entity - single button for dashboard."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the game button."""
        super().__init__()
        self.hass = hass
        self._attr_name = "WordPlay Game"
        self._attr_unique_id = f"{DOMAIN}_game_button"
        self._attr_entity_category = None
        self._attr_icon = "mdi:gamepad-variant"
        self._attr_extra_state_attributes = {}
        
        # Set entity_id explicitly
        self.entity_id = "button.ha_wordplay_game"

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
        game = game_data.get("game")
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
            game = game_data.get("game")
            
            if not game:
                return {
                    "game_status": "Ready",
                    "instructions": "Click to start a new WordPlay game!",
                    "friendly_name": "WordPlay Game",
                    "icon": "mdi:gamepad-variant"
                }
            
            # Format game state for rich display
            attributes = {
                "game_status": self._format_game_status(game),
                "word_length": game.word_length,
                "guesses_made": len(game.guesses),
                "guesses_remaining": game.word_length - len(game.guesses),
                "max_guesses": game.word_length,
                "friendly_name": "WordPlay Game",
                "icon": self.icon
            }
            
            # Add current game info if playing
            if game.game_state == STATE_PLAYING:
                attributes.update({
                    "current_word_length": f"{game.word_length} letters",
                    "hint": game.hint if game.hint else "Click 'Get Hint' for a clue!",
                    "current_input": self._format_current_input(game),
                    "latest_guess": self._format_latest_guess(game),
                })
            
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
                    "📝 Submit Guess - Submit your current guess",
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
            _LOGGER.error(f"Error generating button attributes: {e}")
            return {
                "game_status": "Error",
                "error": str(e),
                "friendly_name": "WordPlay Game"
            }

    def _format_game_status(self, game) -> str:
        """Format game status for display."""
        if game.game_state == STATE_IDLE:
            return "Ready to Play"
        elif game.game_state == STATE_PLAYING:
            return f"Playing ({game.word_length} letters, {game.word_length - len(game.guesses)} guesses left)"
        elif game.game_state == STATE_WON:
            return f"Won in {len(game.guesses)} guesses! 🎉"
        elif game.game_state == STATE_LOST:
            return f"Game Over - Word was {game.current_word}"
        return "Unknown"

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
            return "No guesses yet"
        
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
            # Get game instance
            game_data = self.hass.data.get(DOMAIN, {})
            game = game_data.get("game")
            
            if not game:
                _LOGGER.error("Game instance not found")
                return
            
            # If no game in progress, start a new one
            if game.game_state in [STATE_IDLE, STATE_WON, STATE_LOST]:
                # Get word length from select entity or use default
                word_length = 5
                try:
                    select_state = self.hass.states.get("select.ha_wordplay_word_length")
                    if select_state and select_state.state:
                        word_length = int(select_state.state)
                except (ValueError, TypeError):
                    word_length = 5
                
                success = await game.start_new_game(word_length)
                if success:
                    _LOGGER.info(f"New game started from button press: {word_length} letters")
                else:
                    _LOGGER.error("Failed to start new game from button press")
            
            # Update button attributes to reflect new state
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"Error handling button press: {e}")

    def update_attributes(self) -> None:
        """Update button attributes when game state changes."""
        self.async_write_ha_state()