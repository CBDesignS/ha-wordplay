"""Game logic for H.A WordPlay - Enhanced with Difficulty Support."""
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any

from homeassistant.core import HomeAssistant

from .const import (
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
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
)
from .api_config import (
    get_language_config,
    get_dictionary_config,
    get_fallback_word,
    build_api_url,
    extract_word_from_response,
    DEFAULT_LANGUAGE,
    MAX_API_ATTEMPTS,
)

_LOGGER = logging.getLogger(__name__)

class WordPlayGame:
    """Main game logic class - Enhanced with Difficulty Support."""
    
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
        self.latest_result = []  # Store latest guess result
        self.last_message = ""  # Store messages for UI display
        self.message_type = ""  # Type of message: success, error, info
        self.language = DEFAULT_LANGUAGE  # Current language
        
        # NEW: Difficulty settings
        self.difficulty = DIFFICULTY_NORMAL
        self.allowed_word_lengths = [5, 6, 7, 8]
        self.hint_mode = "on_request"  # "immediate", "on_request", "disabled"
        
    def set_difficulty(self, difficulty: str) -> None:
        """Set game difficulty and update hint behavior."""
        self.difficulty = difficulty
        
        if difficulty == DIFFICULTY_EASY:
            self.hint_mode = "immediate"  # Show hint immediately when game starts
            _LOGGER.info("Difficulty set to EASY - hints shown immediately")
        elif difficulty == DIFFICULTY_NORMAL:
            self.hint_mode = "on_request"  # Show hints when requested
            _LOGGER.info("Difficulty set to NORMAL - hints available on request")
        elif difficulty == DIFFICULTY_HARD:
            self.hint_mode = "disabled"  # No hints available
            _LOGGER.info("Difficulty set to HARD - no hints available")
        else:
            _LOGGER.warning(f"Unknown difficulty: {difficulty}, defaulting to NORMAL")
            self.difficulty = DIFFICULTY_NORMAL
            self.hint_mode = "on_request"
    
    def set_word_lengths(self, word_lengths: List[int]) -> None:
        """Set allowed word lengths."""
        # Validate word lengths
        valid_lengths = [length for length in word_lengths 
                        if MIN_WORD_LENGTH <= length <= MAX_WORD_LENGTH]
        
        if not valid_lengths:
            _LOGGER.warning("No valid word lengths provided, using defaults")
            valid_lengths = [5, 6, 7, 8]
        
        self.allowed_word_lengths = valid_lengths
        _LOGGER.info(f"Allowed word lengths set to: {valid_lengths}")
        
        # If current word length is not allowed, change to first allowed
        if self.word_length not in valid_lengths:
            self.word_length = valid_lengths[0]
            _LOGGER.info(f"Current word length changed to: {self.word_length}")
        
    async def start_new_game(self, word_length: int = None, language: str = DEFAULT_LANGUAGE) -> bool:
        """Start a new game with specified word length and language."""
        try:
            # Use provided word length or current setting
            if word_length is None:
                word_length = self.word_length
            
            # Validate word length against allowed lengths
            if word_length not in self.allowed_word_lengths:
                _LOGGER.warning(f"Word length {word_length} not allowed, using {self.allowed_word_lengths[0]}")
                word_length = self.allowed_word_lengths[0]
            
            # Validate word length bounds
            if word_length < MIN_WORD_LENGTH or word_length > MAX_WORD_LENGTH:
                _LOGGER.error("Invalid word length: %d", word_length)
                return False
                
            _LOGGER.info(f"Starting new game: {word_length} letters, language: {language}, difficulty: {self.difficulty}")
            
            # Reset game state
            self.word_length = word_length
            self.language = language
            self.guesses = []
            self.guess_results = []
            self.latest_result = []
            self.hint = ""
            self.current_guess_input = ""
            self.game_state = STATE_PLAYING
            
            # Set initial message based on difficulty
            if self.difficulty == DIFFICULTY_EASY:
                self.last_message = f"New {word_length} letter game started! Hint coming right up..."
            elif self.difficulty == DIFFICULTY_HARD:
                self.last_message = f"New {word_length} letter game started! No hints in hard mode - good luck!"
            else:
                self.last_message = f"New {word_length} letter game started!"
            
            self.message_type = "success"
            
            # Clear the input field
            await self._clear_input_field()
            
            # Get a random word using multi-API system
            word = await self._get_random_word_multi_api(word_length, language)
            if not word:
                self._set_message("Using local word - APIs unavailable", "info")
                word = get_fallback_word(language, word_length)
                
            self.current_word = word.upper()
            _LOGGER.info(f"New game started with word: [HIDDEN] (length: {len(word)})")
            
            # Get definition for hint based on difficulty
            if self.hint_mode != "disabled":
                await self._get_word_definition()
                
                # For easy mode, show hint immediately
                if self.hint_mode == "immediate" and self.hint:
                    self.last_message = f"New {word_length} letter game! Hint: {self.hint}"
                    self.message_type = "info"
            
            # Update button attributes
            await self._update_button_attributes()
            
            return True
            
        except Exception as e:
            _LOGGER.error(f"Error starting new game: {e}")
            self.game_state = STATE_IDLE
            self._set_message("Error starting game", "error")
            await self._update_button_attributes()
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
                # Anti-cheat violation - set error message
                self._set_message(error_msg, "error")
                await self._update_button_attributes()
                return {"error": error_msg}
            
            # Process the guess
            self.guesses.append(guess)
            result = self._check_guess(guess)
            self.guess_results.append(result)
            self.latest_result = result
            
            # Check win condition
            if guess == self.current_word:
                self.game_state = STATE_WON
                win_message = f"Congratulations! You guessed {self.current_word} in {len(self.guesses)} tries!"
                if self.difficulty == DIFFICULTY_HARD:
                    win_message += " Impressive work in hard mode!"
                self._set_message(win_message, "success")
                _LOGGER.info(f"Game won in {len(self.guesses)} guesses!")
            elif len(self.guesses) >= self.word_length:
                self.game_state = STATE_LOST
                loss_message = f"Game over! The word was {self.current_word}"
                if self.difficulty == DIFFICULTY_HARD:
                    loss_message += " Hard mode is tough - try again!"
                self._set_message(loss_message, "info")
                _LOGGER.info(f"Game lost. Word was {self.current_word}")
            else:
                # Continue playing
                remaining = self.word_length - len(self.guesses)
                self._set_message(f"Good guess! {remaining} tries remaining", "info")
            
            # Clear input and update button
            await self._clear_input_field()
            await self._update_button_attributes()
            
            return {
                "guess": guess,
                "result": result,
                "game_state": self.game_state,
                "guesses_remaining": self.word_length - len(self.guesses),
                "success": True
            }
            
        except Exception as e:
            _LOGGER.error(f"Error processing guess: {e}")
            self._set_message("Error processing guess", "error")
            await self._update_button_attributes()
            return {"error": str(e)}
    
    async def get_hint(self) -> str:
        """Get hint for current word - respects difficulty settings."""
        if self.game_state != STATE_PLAYING:
            return "No game in progress"
        
        # Check if hints are disabled in hard mode
        if self.hint_mode == "disabled":
            hint_message = "No hints available in hard mode! You're on your own."
            self._set_message(hint_message, "info")
            await self._update_button_attributes()
            return hint_message
        
        # Get hint if we don't have one
        if not self.hint:
            await self._get_word_definition()
        
        # Set message about hint
        if self.hint:
            self._set_message(f"Hint: {self.hint}", "info")
        else:
            self._set_message("Sorry, no hint available for this word", "info")
        
        await self._update_button_attributes()
        return self.hint or "No hint available"
    
    async def update_current_input(self, input_text: str) -> None:
        """Update the current input for live display."""
        self.current_guess_input = input_text.upper().strip()
        await self._update_button_attributes()
    
    def _check_guess(self, guess: str) -> List[str]:
        """Check guess against current word and return color results."""
        result = []
        target_word = self.current_word
        
        # First pass: mark exact matches
        for i, letter in enumerate(guess):
            if letter == target_word[i]:
                result.append(LETTER_CORRECT)  # Correct position
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
                    result[i] = LETTER_PARTIAL  # Wrong position
                    target_letters[target_letters.index(letter)] = None
                else:
                    result[i] = LETTER_ABSENT  # Not in word
        
        return result
    
    async def _get_random_word_multi_api(self, length: int, language: str = DEFAULT_LANGUAGE) -> Optional[str]:
        """Get random word using multi-API cascade system."""
        lang_config = get_language_config(language)
        
        # Try primary API
        word = await self._try_api(lang_config["primary"], length)
        if word:
            _LOGGER.info(f"Got word from primary API (length: {length})")
            return word
        
        # Try backup APIs
        for backup_key in ["backup1", "backup2"]:
            if backup_key in lang_config:
                word = await self._try_api(lang_config[backup_key], length)
                if word:
                    _LOGGER.info(f"Got word from {backup_key} API (length: {length})")
                    return word
        
        # All APIs failed
        _LOGGER.warning(f"All APIs failed for language: {language}, length: {length}")
        return None
    
    async def _try_api(self, api_config: dict, length: int) -> Optional[str]:
        """Try a specific API configuration."""
        for attempt in range(MAX_API_ATTEMPTS):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
                    url = build_api_url(api_config, length)
                    _LOGGER.debug(f"Trying API: {url} (attempt {attempt + 1})")
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            word = extract_word_from_response(data, api_config)
                            
                            if word and len(word) == length and word.isalpha():
                                return word.upper()
                            else:
                                _LOGGER.debug(f"Invalid word from API: {word}")
                                
            except Exception as e:
                _LOGGER.debug(f"API attempt {attempt + 1} failed: {e}")
            
            # Wait before retry
            if attempt < MAX_API_ATTEMPTS - 1:
                await asyncio.sleep(1)
        
        return None
    
    async def _get_word_definition(self) -> None:
        """Get definition for current word using multi-language dictionary APIs."""
        try:
            dict_config = get_dictionary_config(self.language)
            url = dict_config["primary"].format(word=self.current_word.lower())
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
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
                                    _LOGGER.debug(f"Got definition for current word")
                                    return
        except Exception as e:
            _LOGGER.debug(f"Error getting word definition: {e}")
        
        # Fallback hints based on word length and difficulty
        if self.difficulty == DIFFICULTY_EASY:
            fallback_hints = {
                5: "A common 5-letter English word you use often",
                6: "A 6-letter word you might encounter daily",
                7: "A 7-letter word with interesting letter patterns", 
                8: "An 8-letter word - think of longer, descriptive words"
            }
        else:
            fallback_hints = {
                5: "A common 5-letter English word",
                6: "A 6-letter word you might use daily",
                7: "A 7-letter word with good letter variety", 
                8: "An 8-letter word - think carefully!"
            }
        
        self.hint = fallback_hints.get(self.word_length, "A word you need to guess!")
    
    def _simplify_definition(self, definition: str) -> str:
        """Simplify definition to create a good hint."""
        if not definition:
            return "A word you need to guess!"
        
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
        
        # Limit length based on difficulty
        max_length = 80 if self.difficulty == DIFFICULTY_EASY else 60
        if len(hint) > max_length:
            hint = hint[:max_length-3] + "..."
        
        return hint.capitalize() if hint else "A word you need to guess!"
    
    async def _clear_input_field(self) -> None:
        """Clear the input field."""
        try:
            # Get the text entity and clear it
            domain_data = self.hass.data.get("ha_wordplay", {})
            text_entity = domain_data.get("entities", {}).get("text_input")
            if text_entity:
                await text_entity.async_clear_value()
            
            # Also clear our internal tracking
            self.current_guess_input = ""
        except Exception as e:
            _LOGGER.debug(f"Could not clear input field: {e}")
    
    async def _update_button_attributes(self) -> None:
        """Update button entity attributes when game state changes."""
        try:
            domain_data = self.hass.data.get("ha_wordplay", {})
            button_entity = domain_data.get("entities", {}).get("game_button")
            if button_entity:
                button_entity.update_attributes()
        except Exception as e:
            _LOGGER.debug(f"Could not update button attributes: {e}")