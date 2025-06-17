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
)

_LOGGER = logging.getLogger(__name__)

class WordPlayGame:
    """Main game logic class."""
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the game."""
        self.hass = hass
        self.current_word = ""
        self.word_length = 5
        self.guesses = []
        self.game_state = STATE_IDLE
        self.hint = ""
        self.guess_results = []  # Store results for each guess
        
    async def start_new_game(self, word_length: int = 5) -> bool:
        """Start a new game with specified word length."""
        try:
            _LOGGER.info(f"Starting new game with word length: {word_length}")
            
            # Reset game state
            self.word_length = word_length
            self.guesses = []
            self.guess_results = []
            self.hint = ""
            self.game_state = STATE_PLAYING
            
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
    
    async def make_guess(self, guess: str) -> Dict[str, Any]:
        """Process a guess and return results."""
        try:
            if self.game_state != STATE_PLAYING:
                return {"error": "No game in progress"}
            
            guess = guess.upper()
            
            if len(guess) != self.word_length:
                return {"error": f"Guess must be {self.word_length} letters"}
            
            # Check if already guessed
            if guess in self.guesses:
                return {"error": "Already guessed that word"}
            
            # Process the guess
            self.guesses.append(guess)
            result = self._check_guess(guess)
            self.guess_results.append(result)
            
            # Check win condition
            if guess == self.current_word:
                self.game_state = STATE_WON
                _LOGGER.info(f"Game won in {len(self.guesses)} guesses!")
            elif len(self.guesses) >= MAX_GUESSES:
                self.game_state = STATE_LOST
                _LOGGER.info(f"Game lost. Word was: {self.current_word}")
            
            # Update states
            await self._update_game_states()
            
            return {
                "guess": guess,
                "result": result,
                "game_state": self.game_state,
                "guesses_remaining": MAX_GUESSES - len(self.guesses)
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
    
    def _check_guess(self, guess: str) -> List[str]:
        """Check guess against current word and return color results."""
        result = []
        target_word = self.current_word
        
        # First pass: mark exact matches
        for i, letter in enumerate(guess):
            if letter == target_word[i]:
                result.append("correct")  # Green
            else:
                result.append("pending")  # Placeholder
        
        # Second pass: mark partial matches
        target_letters = list(target_word)
        
        # Remove exact matches from target letters
        for i, status in enumerate(result):
            if status == "correct":
                target_letters[i] = None
        
        # Check for partial matches
        for i, letter in enumerate(guess):
            if result[i] == "pending":
                if letter in target_letters:
                    result[i] = "partial"  # Yellow
                    target_letters[target_letters.index(letter)] = None
                else:
                    result[i] = "absent"  # Gray
        
        return result
    
    async def _get_random_word(self, length: int) -> Optional[str]:
        """Get a random word of specified length."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
                url = f"{RANDOM_WORD_API}?length={length}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            word = data[0]
                            _LOGGER.debug(f"Got random word: {word}")
                            return word
                    else:
                        _LOGGER.error(f"API returned status {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error getting random word: {e}")
        
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
        except Exception as e:
            _LOGGER.error(f"Error getting word definition: {e}")
            self.hint = "No hint available"
    
    def _simplify_definition(self, definition: str) -> str:
        """Simplify definition to create a good hint."""
        # Basic simplification - take first sentence and limit length
        if not definition:
            return "No hint available"
        
        # Split by periods and take first sentence
        sentences = definition.split('.')
        hint = sentences[0].strip()
        
        # Limit length
        if len(hint) > 100:
            hint = hint[:97] + "..."
        
        return hint.capitalize()
    
    async def _update_game_states(self) -> None:
        """Update Home Assistant entity states."""
        try:
            # Update game state
            self.hass.states.async_set(
                "sensor.ha_wordplay_game_state",
                self.game_state,
                {
                    "word_length": self.word_length,
                    "guesses_made": len(self.guesses),
                    "guesses_remaining": MAX_GUESSES - len(self.guesses),
                    "hint": self.hint,
                    "friendly_name": "WordPlay Game State"
                }
            )
            
            # Update guesses
            self.hass.states.async_set(
                "sensor.ha_wordplay_guesses",
                len(self.guesses),
                {
                    "guesses": self.guesses,
                    "results": self.guess_results,
                    "max_guesses": MAX_GUESSES,
                    "friendly_name": "WordPlay Guesses"
                }
            )
            
            # For debugging - only in development
            if _LOGGER.isEnabledFor(logging.DEBUG):
                self.hass.states.async_set(
                    "sensor.ha_wordplay_debug",
                    self.current_word,
                    {
                        "current_word": self.current_word,
                        "friendly_name": "WordPlay Debug (Remove in Production)"
                    }
                )
                
        except Exception as e:
            _LOGGER.error(f"Error updating game states: {e}")
