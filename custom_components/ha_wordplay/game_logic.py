"""Game logic for H.A WordPlay."""
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change

from .const import (
    RANDOM_WORD_API,
    DICTIONARY_API,
    API_TIMEOUT,
    STATE_IDLE,
    STATE_PLAYING,
    STATE_WON,
    STATE_LOST,
    MAX_GUESSES,
    LETTER_CORRECT,
    LETTER_PARTIAL,
    LETTER_ABSENT,
    MIN_WORD_LENGTH,
    MAX_WORD_LENGTH,
    DEFAULT_WORD_LENGTH,
)

_LOGGER = logging.getLogger(__name__)

class WordPlayGame:
    """Main game logic class."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the game."""
        self.hass = hass
        self.current_word = ""
        self.word_length = DEFAULT_WORD_LENGTH
        self.guesses = []
        self.game_state = STATE_IDLE
        self.hint = ""
        self.guess_results = []  # Store results for each guess
        self.current_guess_input = ""  # Track live input
        self.latest_result = []  # Store latest guess result for top row display
        self.last_message = ""  # Store messages for UI display
        self.message_type = ""  # Type of message: success, error, info
        
    async def start_new_game(self, word_length: int = DEFAULT_WORD_LENGTH) -> bool:
        """Start a new game with specified word length."""
        try:
            # Validate word length
            if word_length < MIN_WORD_LENGTH or word_length > MAX_WORD_LENGTH:
                _LOGGER.error("Invalid word length: %d", word_length)
                return False
                
            _LOGGER.info(f"Starting new game with word length: {word_length}")
            
            # Reset game state
            self.word_length = word_length
            self.guesses = []
            self.guess_results = []
            self.latest_result = []
            self.hint = ""
            self.current_guess_input = ""
            self.game_state = STATE_PLAYING
            self.last_message = ""
            self.message_type = ""
            
            # Clear the input field
            await self._clear_input_field()
            
            # Get a random word
            word = await self._get_random_word(word_length)
            if not word:
                _LOGGER.error("Failed to get random word")
                self.game_state = STATE_IDLE
                return False
                
            self.current_word = word.upper()
            _LOGGER.info(f"New game started with word: {self.current_word}")
            
            # Get definition for hint
            await self._get_word_definition()
            
            # Update Home Assistant states
            await self._update_game_states()
            
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error starting new game: {e}")
            self.game_state = STATE_IDLE
            return False

    def _is_valid_guess(self, guess: str) -> tuple[bool, str]:
        """Validate guess for anti-cheating rules."""
        guess = guess.upper().strip()
        
        # Basic validation
        if len(guess) != self.word_length:
            return False, f"Guess must be {self.word_length} letters"
        
        if not guess.isalpha():
            return False, "Guess must contain only letters"
        
        # Check if already guessed
        if guess in self.guesses:
            return False, "Already guessed that word"
        
        # Anti-cheat: Prevent pure vowel dumping
        vowels = set('AEIOU')
        consonants = set('BCDFGHJKLMNPQRSTVWXYZ')
        
        guess_letters = set(guess)
        vowel_count = len(guess_letters & vowels)
        consonant_count = len(guess_letters & consonants)
        
        # Rule 1: Can't be all vowels
        if consonant_count == 0:
            return False, "Guess must contain at least one consonant (no vowel dumping!)"
        
        # Rule 2: Can't have more than 60% vowels (prevents AEIOU + 1 consonant)
        vowel_percentage = vowel_count / len(guess_letters)
        if vowel_percentage > 0.6:
            return False, "Too many vowels! Try a more balanced word"
        
        # Rule 3: Must have at least 2 different consonants for words 5+ letters
        if self.word_length >= 5 and consonant_count < 2:
            return False, "Need at least 2 different consonants for fair play"
        
        return True, ""
    
    async def _speak_message(self, message: str) -> None:
        """Use TTS to speak a message via Home Assistant frontend."""
        try:
            # Send TTS command to Home Assistant frontend
            self.hass.bus.async_fire("wordplay_tts", {"message": message})
            _LOGGER.info(f"TTS message sent: {message}")
        except Exception as e:
            _LOGGER.error(f"Error sending TTS message: {e}")
    
    def _set_message(self, message: str, message_type: str = "info") -> None:
        """Set a message for UI display with type."""
        self.last_message = message
        self.message_type = message_type
        _LOGGER.info(f"UI message set ({message_type}): {message}")
    
    async def make_guess(self, guess: str) -> Dict[str, Any]:
        """Process a guess and return results."""
        try:
            if self.game_state != STATE_PLAYING:
                return {"error": "No game in progress"}
            
            guess = guess.upper().strip()
            
            # Validate guess with anti-cheat rules
            is_valid, error_msg = self._is_valid_guess(guess)
            if not is_valid:
                # Anti-cheat violation - set error message and speak it
                self._set_message(error_msg, "error")
                await self._speak_message(f"Invalid guess. {error_msg}")
                await self._update_game_states()  # Update UI to show error
                return {"error": error_msg}
            
            # Process the guess
            self.guesses.append(guess)
            result = self._check_guess(guess)
            self.guess_results.append(result)
            self.latest_result = result  # Store for top row display
            
            # Check win condition
            if guess == self.current_word:
                self.game_state = STATE_WON
                win_message = f"Congratulations! You guessed the word {self.current_word} correctly in {len(self.guesses)} tries!"
                self._set_message(win_message, "success")
                await self._speak_message(win_message)
                _LOGGER.info(f"Game won in {len(self.guesses)} guesses!")
            elif len(self.guesses) >= MAX_GUESSES:
                self.game_state = STATE_LOST
                loss_message = f"Game over! The word was {self.current_word}. Better luck next time!"
                self._set_message(loss_message, "info")
                await self._speak_message(loss_message)
                _LOGGER.info(f"Game lost. Word was: {self.current_word}")
            
            # Clear input and update states
            await self._clear_input_field()
            await self._update_game_states()
            
            return {
                "guess": guess,
                "result": result,
                "game_state": self.game_state,
                "guesses_remaining": MAX_GUESSES - len(self.guesses),
                "success": True
            }
            
        except Exception as e:
            _LOGGER.error(f"Error processing guess: {e}")
            return {"error": str(e)}
    
    async def get_hint(self) -> str:
        """Get hint for current word."""
        if self.game_state != STATE_PLAYING:
            return "No game in progress"
        
        if not self.hint:
            await self._get_word_definition()
        
        return self.hint or "No hint available"
    
    async def update_current_input(self, input_text: str) -> None:
        """Update the current input for live display."""
        self.current_guess_input = input_text.upper().strip()
        await self._update_game_states()
    
    def _check_guess(self, guess: str) -> List[str]:
        """Check guess against current word and return color results."""
        result = []
        target_word = self.current_word
        
        # First pass: mark exact matches
        for i, letter in enumerate(guess):
            if letter == target_word[i]:
                result.append(LETTER_CORRECT)  # Blue - correct position
            else:
                result.append("pending")  # Placeholder
        
        # Second pass: mark partial matches
        target_letters = list(target_word)
        
        # Remove exact matches from target letters
        for i, status in enumerate(result):
            if status == LETTER_CORRECT:
                target_letters[i] = None
        
        # Check for partial matches
        for i, letter in enumerate(guess):
            if result[i] == "pending":
                if letter in target_letters:
                    result[i] = LETTER_PARTIAL  # Red - wrong position
                    target_letters[target_letters.index(letter)] = None
                else:
                    result[i] = LETTER_ABSENT  # Gray - not in word
        
        return result
    
    async def _get_random_word(self, length: int) -> Optional[str]:
        """Get a random word of specified length."""
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
                    # Try the length-specific API first
                    url = f"{RANDOM_WORD_API}?length={length}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if isinstance(data, list) and len(data) > 0:
                                word = data[0]
                                if len(word) == length and word.isalpha():
                                    _LOGGER.debug(f"Got random word: {word}")
                                    return word
                        
                        # Fallback: get any word and check length
                        async with session.get(RANDOM_WORD_API) as fallback_response:
                            if fallback_response.status == 200:
                                fallback_data = await fallback_response.json()
                                if isinstance(fallback_data, list) and len(fallback_data) > 0:
                                    word = fallback_data[0]
                                    if len(word) == length and word.isalpha():
                                        _LOGGER.debug(f"Got fallback word: {word}")
                                        return word
                                        
            except Exception as e:
                _LOGGER.warning(f"Error getting random word (attempt {attempt + 1}): {e}")
            
            attempt += 1
            if attempt < max_attempts:
                await asyncio.sleep(1)  # Wait before retry
        
        _LOGGER.error(f"Failed to get random word after {max_attempts} attempts")
        return None
    
    async def _get_word_definition(self) -> None:
        """Get definition for current word to use as hint."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
                url = f"{DICTIONARY_API}/{self.current_word.lower()}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            meanings = data[0].get("meanings", [])
                            if meanings:
                                definitions = meanings[0].get("definitions", [])
                                if definitions:
                                    definition = definitions[0].get("definition", "")
                                    # Simplify the definition for hint
                                    self.hint = self._simplify_definition(definition)
                                    _LOGGER.debug(f"Got definition: {self.hint}")
                                    return
        except Exception as e:
            _LOGGER.error(f"Error getting word definition: {e}")
        
        self.hint = "No hint available"
    
    def _simplify_definition(self, definition: str) -> str:
        """Simplify definition to create a good hint."""
        if not definition:
            return "No hint available"
        
        # Basic simplification - take first sentence and limit length
        sentences = definition.split('.')
        hint = sentences[0].strip()
        
        # Remove the word itself from the hint to avoid giving it away
        hint_words = hint.split()
        filtered_words = []
        for word in hint_words:
            clean_word = ''.join(c for c in word if c.isalpha()).upper()
            if clean_word != self.current_word:
                filtered_words.append(word)
        
        hint = ' '.join(filtered_words)
        
        # Limit length
        if len(hint) > 100:
            hint = hint[:97] + "..."
        
        return hint.capitalize() if hint else "No hint available"
    
    async def _clear_input_field(self) -> None:
        """Clear the input field."""
        try:
            # Get the text entity and clear it
            text_entity = self.hass.data.get("ha_wordplay", {}).get("entities", {}).get("text_input")
            if text_entity:
                await text_entity.async_clear_value()
            
            # Also clear our internal tracking
            self.current_guess_input = ""
        except Exception as e:
            _LOGGER.debug(f"Could not clear input field: {e}")
    
    async def _update_game_states(self) -> None:
        """Update Home Assistant entity states."""
        try:
            # Format latest result for display
            latest_display = []
            if self.latest_result and self.guesses:
                latest_guess = self.guesses[-1]
                for i, (letter, result) in enumerate(zip(latest_guess, self.latest_result)):
                    if result == LETTER_CORRECT:
                        latest_display.append(f"{letter}🟦")  # Blue for correct
                    elif result == LETTER_PARTIAL:
                        latest_display.append(f"{letter}🟥")  # Red for partial
                    else:
                        latest_display.append(f"{letter}⬜")  # White for absent
            
            # Format current input for live display
            current_input_display = []
            if self.current_guess_input:
                for letter in self.current_guess_input:
                    current_input_display.append(f"{letter}⬜")
                # Pad with empty slots
                while len(current_input_display) < self.word_length:
                    current_input_display.append("_")
            else:
                current_input_display = ["_"] * self.word_length
            
            # Update game state sensor
            self.hass.states.async_set(
                "sensor.ha_wordplay_game_state",
                self.game_state,
                {
                    "word_length": self.word_length,
                    "guesses_made": len(self.guesses),
                    "guesses_remaining": MAX_GUESSES - len(self.guesses),
                    "hint": self.hint,
                    "latest_result": " ".join(latest_display),
                    "current_input": " ".join(current_input_display),
                    "last_message": self.last_message,
                    "message_type": self.message_type,
                    "friendly_name": "WordPlay Game State",
                    "icon": "mdi:gamepad-variant"
                }
            )
            
            # Update guesses sensor
            self.hass.states.async_set(
                "sensor.ha_wordplay_guesses",
                len(self.guesses),
                {
                    "guesses": self.guesses,
                    "results": self.guess_results,
                    "max_guesses": MAX_GUESSES,
                    "all_guesses_formatted": self._format_all_guesses(),
                    "friendly_name": "WordPlay Guesses",
                    "icon": "mdi:format-list-numbered"
                }
            )
            
            # Debug sensor (development only) - Hide current word for security
            if _LOGGER.isEnabledFor(logging.DEBUG):
                self.hass.states.async_set(
                    "sensor.ha_wordplay_debug",
                    "DEBUG_MODE",
                    {
                        "game_state": self.game_state,
                        "word_length": self.word_length,
                        "guesses_count": len(self.guesses),
                        "friendly_name": "WordPlay Debug (Development Only)",
                        "icon": "mdi:bug"
                    }
                )
                
        except Exception as e:
            _LOGGER.error(f"Error updating game states: {e}")
    
    def _format_all_guesses(self) -> List[str]:
        """Format all guesses with their results for display."""
        formatted = []
        for i, (guess, result) in enumerate(zip(self.guesses, self.guess_results)):
            guess_display = []
            for letter, status in zip(guess, result):
                if status == LETTER_CORRECT:
                    guess_display.append(f"{letter}🟦")
                elif status == LETTER_PARTIAL:
                    guess_display.append(f"{letter}🟥")
                else:
                    guess_display.append(f"{letter}⬜")
            formatted.append(" ".join(guess_display))
        return formatted