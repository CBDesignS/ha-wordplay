"""Game logic for H.A WordPlay - Multi-User Version with Stats Foundation."""
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage

from .wordplay_const import (
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
    DOMAIN,
)
from .wordplay_api_config import (
    get_language_config,
    get_dictionary_config,
    get_fallback_word,
    build_api_url,
    extract_word_from_response,
    DEFAULT_LANGUAGE,
    MAX_API_ATTEMPTS,
)

_LOGGER = logging.getLogger(__name__)

# Storage constants for future stats
STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = f"{DOMAIN}_stats"

class WordPlayGame:
    """Main game logic class - Multi-User Version with Stats Foundation."""
    
    def __init__(self, hass: HomeAssistant, user_id: str = "default"):
        """Initialize the game for a specific user."""
        self.hass = hass
        self.user_id = user_id
        
        # Game state
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
        
        # Word reveal for loss situations
        self.revealed_word = ""  # Only populated when game is lost
        
        # Difficulty settings
        self.difficulty = DIFFICULTY_NORMAL
        self.hint_mode = "on_request"  # "immediate", "on_request", "disabled"
        
        # Game timing
        self.game_start_time = None
        self.game_end_time = None
        
        # Stats foundation - ready for future expansion
        # FIXED: Ensure all numeric values are initialized as integers
        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'total_guesses': 0,
            'guess_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
            'win_streak': 0,
            'max_streak': 0,
            'last_played': None,
            'average_guesses': 0.0,
            'win_rate': 0.0,
            'total_play_time': 0,  # FIXED: Ensure this is always an integer
            'fastest_win': None,  # in seconds
            'difficulty_stats': {
                DIFFICULTY_EASY: {'played': 0, 'won': 0},
                DIFFICULTY_NORMAL: {'played': 0, 'won': 0},
                DIFFICULTY_HARD: {'played': 0, 'won': 0}
            }
        }
        
        # Load stats on initialization
        asyncio.create_task(self._load_stats())
        
    async def _load_stats(self) -> None:
        """Load user statistics from storage."""
        try:
            store = storage.Store(self.hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}_{self.user_id}")
            data = await store.async_load()
            if data:
                # FIXED: Ensure loaded stats have correct types
                if 'total_play_time' in data:
                    # Convert to int if it's a string or float
                    try:
                        data['total_play_time'] = int(data['total_play_time'])
                    except (ValueError, TypeError):
                        data['total_play_time'] = 0
                
                # Ensure all numeric fields are proper types
                for key in ['games_played', 'games_won', 'total_guesses', 'win_streak', 'max_streak']:
                    if key in data:
                        try:
                            data[key] = int(data[key])
                        except (ValueError, TypeError):
                            data[key] = 0
                
                # Ensure guess_distribution values are integers
                if 'guess_distribution' in data:
                    # Convert all keys to integers and values to integers
                    fixed_distribution = {}
                    for k, v in data['guess_distribution'].items():
                        try:
                            key_int = int(k)
                            value_int = int(v)
                            fixed_distribution[key_int] = value_int
                        except (ValueError, TypeError):
                            pass
                    # Ensure all keys 1-8 exist
                    for i in range(1, 9):
                        if i not in fixed_distribution:
                            fixed_distribution[i] = 0
                    data['guess_distribution'] = fixed_distribution
                
                self.stats.update(data)
                _LOGGER.info(f"Loaded stats for user {self.user_id}: {self.stats['games_played']} games played")
        except Exception as e:
            _LOGGER.error(f"Error loading stats for user {self.user_id}: {e}")
    
    async def _save_stats(self) -> None:
        """Save user statistics to storage."""
        try:
            store = storage.Store(self.hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}_{self.user_id}")
            await store.async_save(self.stats)
            _LOGGER.debug(f"Saved stats for user {self.user_id}")
            
            # Update the stats sensor entity
            await self._update_stats_sensor()
            
        except Exception as e:
            _LOGGER.error(f"Error saving stats for user {self.user_id}: {e}")
    
    async def _update_stats_sensor(self) -> None:
        """Update the stats sensor entity with current stats."""
        try:
            domain_data = self.hass.data.get(DOMAIN, {})
            user_entities = domain_data.get("entities", {}).get(self.user_id, {})
            stats_entity = user_entities.get("stats")
            
            if stats_entity:
                stats_entity.update_stats(self.stats['games_played'], self.stats)
                _LOGGER.debug(f"Updated stats sensor for user {self.user_id}")
        except Exception as e:
            _LOGGER.debug(f"Could not update stats sensor: {e}")
        
    def set_difficulty(self, difficulty: str) -> None:
        """Set game difficulty and update hint behavior."""
        self.difficulty = difficulty
        
        if difficulty == DIFFICULTY_EASY:
            self.hint_mode = "immediate"  # Show hint immediately when game starts
            _LOGGER.info(f"User {self.user_id}: Difficulty set to EASY - hints shown immediately")
        elif difficulty == DIFFICULTY_NORMAL:
            self.hint_mode = "on_request"  # Show hints when requested
            _LOGGER.info(f"User {self.user_id}: Difficulty set to NORMAL - hints available on request")
        elif difficulty == DIFFICULTY_HARD:
            self.hint_mode = "disabled"  # No hints available
            _LOGGER.info(f"User {self.user_id}: Difficulty set to HARD - no hints available")
        else:
            _LOGGER.warning(f"Unknown difficulty: {difficulty}, defaulting to NORMAL")
            self.difficulty = DIFFICULTY_NORMAL
            self.hint_mode = "on_request"
        
    async def start_new_game(self, word_length: int = None, language: str = DEFAULT_LANGUAGE) -> bool:
        """Start a new game with specified word length and language."""
        try:
            # Use provided word length or current setting
            if word_length is None:
                word_length = self.word_length
            
            # Validate word length bounds
            if word_length < MIN_WORD_LENGTH or word_length > MAX_WORD_LENGTH:
                _LOGGER.error(f"User {self.user_id}: Invalid word length: {word_length}")
                return False
                
            _LOGGER.info(f"User {self.user_id}: Starting new game: {word_length} letters, language: {language}, difficulty: {self.difficulty}")
            
            # Reset game state
            self.word_length = word_length
            self.language = language
            self.guesses = []
            self.guess_results = []
            self.latest_result = []
            self.hint = ""
            self.current_guess_input = ""
            self.game_state = STATE_PLAYING
            self.revealed_word = ""  # Clear any previous revealed word
            self.game_start_time = datetime.now()
            self.game_end_time = None
            
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
            _LOGGER.info(f"User {self.user_id}: New game started with word: [HIDDEN] (length: {len(word)})")
            
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
            _LOGGER.error(f"User {self.user_id}: Error starting new game: {e}")
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
        _LOGGER.info(f"User {self.user_id} UI message ({message_type}): {message}")
    
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
            
            # Update total guesses stat
            self.stats['total_guesses'] += 1
            
            # Check win condition
            if guess == self.current_word:
                self.game_state = STATE_WON
                self.game_end_time = datetime.now()
                win_message = f"Congratulations! You guessed {self.current_word} in {len(self.guesses)} tries!"
                if self.difficulty == DIFFICULTY_HARD:
                    win_message += " Impressive work in hard mode!"
                self._set_message(win_message, "success")
                _LOGGER.info(f"User {self.user_id}: Game won in {len(self.guesses)} guesses!")
                
                # Update stats for win
                await self._update_stats_for_game_end(won=True)
                
            elif len(self.guesses) >= self.word_length:
                self.game_state = STATE_LOST
                self.game_end_time = datetime.now()
                # Set revealed word for loss situations
                self.revealed_word = self.current_word
                loss_message = f"Game over! The word was {self.current_word}"
                if self.difficulty == DIFFICULTY_HARD:
                    loss_message += " Hard mode is tough - try again!"
                self._set_message(loss_message, "info")
                _LOGGER.info(f"User {self.user_id}: Game lost. Word was {self.current_word}")
                
                # Update stats for loss
                await self._update_stats_for_game_end(won=False)
                
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
            _LOGGER.error(f"User {self.user_id}: Error processing guess: {e}")
            self._set_message("Error processing guess", "error")
            await self._update_button_attributes()
            return {"error": str(e)}
    
    async def _update_stats_for_game_end(self, won: bool) -> None:
        """Update statistics when game ends."""
        try:
            # Calculate game duration
            if self.game_start_time and self.game_end_time:
                game_duration = (self.game_end_time - self.game_start_time).total_seconds()
                # FIXED: Ensure total_play_time is an integer before adding
                current_play_time = int(self.stats.get('total_play_time', 0))
                self.stats['total_play_time'] = current_play_time + int(game_duration)
            
            # Update basic stats
            self.stats['games_played'] += 1
            self.stats['last_played'] = datetime.now().isoformat()
            
            # Update difficulty-specific stats
            self.stats['difficulty_stats'][self.difficulty]['played'] += 1
            
            if won:
                self.stats['games_won'] += 1
                self.stats['win_streak'] += 1
                self.stats['max_streak'] = max(self.stats['max_streak'], self.stats['win_streak'])
                
                # FIXED: Ensure guess count is within valid range and key exists
                guess_count = len(self.guesses)
                if 1 <= guess_count <= 8:
                    # Ensure key exists in dictionary
                    if guess_count not in self.stats['guess_distribution']:
                        self.stats['guess_distribution'][guess_count] = 0
                    self.stats['guess_distribution'][guess_count] += 1
                
                self.stats['difficulty_stats'][self.difficulty]['won'] += 1
                
                # Track fastest win
                if self.game_start_time and self.game_end_time:
                    if not self.stats['fastest_win'] or game_duration < self.stats['fastest_win']:
                        self.stats['fastest_win'] = int(game_duration)
            else:
                self.stats['win_streak'] = 0
            
            # Calculate derived stats
            if self.stats['games_played'] > 0:
                self.stats['win_rate'] = round(self.stats['games_won'] / self.stats['games_played'] * 100, 1)
                
            if self.stats['games_won'] > 0:
                total_winning_guesses = sum(
                    guesses * count 
                    for guesses, count in self.stats['guess_distribution'].items()
                )
                self.stats['average_guesses'] = round(total_winning_guesses / self.stats['games_won'], 2)
            
            # Save stats
            await self._save_stats()
            
            _LOGGER.info(f"User {self.user_id}: Updated stats - Games: {self.stats['games_played']}, Wins: {self.stats['games_won']}, Win Rate: {self.stats['win_rate']}%")
            
        except Exception as e:
            _LOGGER.error(f"User {self.user_id}: Error updating stats: {e}")
    
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
            _LOGGER.info(f"User {self.user_id}: Got word from primary API (length: {length})")
            return word
        
        # Try backup APIs
        for backup_key in ["backup1", "backup2"]:
            if backup_key in lang_config:
                word = await self._try_api(lang_config[backup_key], length)
                if word:
                    _LOGGER.info(f"User {self.user_id}: Got word from {backup_key} API (length: {length})")
                    return word
        
        # All APIs failed
        _LOGGER.warning(f"User {self.user_id}: All APIs failed for language: {language}, length: {length}")
        return None
    
    async def _try_api(self, api_config: dict, length: int) -> Optional[str]:
        """Try a specific API configuration."""
        for attempt in range(MAX_API_ATTEMPTS):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
                    url = build_api_url(api_config, length)
                    _LOGGER.debug(f"User {self.user_id}: Trying API: {url} (attempt {attempt + 1})")
                    
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            word = extract_word_from_response(data, api_config)
                            
                            if word and len(word) == length and word.isalpha():
                                return word.upper()
                            else:
                                _LOGGER.debug(f"User {self.user_id}: Invalid word from API: {word}")
                                
            except Exception as e:
                _LOGGER.debug(f"User {self.user_id}: API attempt {attempt + 1} failed: {e}")
            
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
                                    _LOGGER.debug(f"User {self.user_id}: Got definition for current word")
                                    return
        except Exception as e:
            _LOGGER.debug(f"User {self.user_id}: Error getting word definition: {e}")
        
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
        """Clear the input field for this user."""
        try:
            # Get the user's text entity and clear it
            domain_data = self.hass.data.get(DOMAIN, {})
            user_entities = domain_data.get("entities", {}).get(self.user_id, {})
            text_entity = user_entities.get("text_input")
            
            if text_entity:
                await text_entity.async_clear_value()
            
            # Also clear our internal tracking
            self.current_guess_input = ""
        except Exception as e:
            _LOGGER.debug(f"User {self.user_id}: Could not clear input field: {e}")
    
    async def _update_button_attributes(self) -> None:
        """Update button entity attributes when game state changes."""
        try:
            domain_data = self.hass.data.get(DOMAIN, {})
            user_entities = domain_data.get("entities", {}).get(self.user_id, {})
            button_entity = user_entities.get("game_button")
            
            if button_entity:
                button_entity.update_attributes()
        except Exception as e:
            _LOGGER.debug(f"User {self.user_id}: Could not update button attributes: {e}")
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get a summary of user statistics for display."""
        return {
            "games_played": self.stats['games_played'],
            "games_won": self.stats['games_won'],
            "win_rate": f"{self.stats['win_rate']}%",
            "current_streak": self.stats['win_streak'],
            "max_streak": self.stats['max_streak'],
            "average_guesses": self.stats['average_guesses'],
            "total_play_time": self._format_play_time(self.stats['total_play_time']),
            "fastest_win": self._format_play_time(self.stats['fastest_win']) if self.stats['fastest_win'] else "N/A",
            "difficulty_breakdown": {
                diff: f"{stats['won']}/{stats['played']} ({(stats['won']/stats['played']*100 if stats['played'] > 0 else 0):.1f}%)"
                for diff, stats in self.stats['difficulty_stats'].items()
            }
        }
    
    def _format_play_time(self, seconds: int) -> str:
        """Format play time in seconds to human readable format."""
        if seconds is None:
            return "N/A"
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def export_stats(self) -> Dict[str, Any]:
        """Export full statistics for backup or analysis."""
        return {
            "user_id": self.user_id,
            "export_date": datetime.now().isoformat(),
            "stats": self.stats
        }