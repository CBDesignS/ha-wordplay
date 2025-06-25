"""Constants for H.A WordPlay integration - Config Flow Version with Audio Config."""

DOMAIN = "ha_wordplay"

# Game Configuration
MIN_WORD_LENGTH = 5  # Updated: removed 4-letter words
MAX_WORD_LENGTH = 8  # Updated: added 7&8 letter words
MAX_GUESSES = 6

# Service Names
SERVICE_NEW_GAME = "new_game"
SERVICE_MAKE_GUESS = "make_guess"
SERVICE_GET_HINT = "get_hint"
SERVICE_SUBMIT_GUESS = "submit_guess"

# Active Entity IDs (used by current platforms)
WORD_LENGTH_ENTITY = "select.ha_wordplay_word_length"  # Used by select.py
GUESS_INPUT_ENTITY = "text.ha_wordplay_guess_input"    # Used by text.py

# Game States
STATE_IDLE = "idle"
STATE_PLAYING = "playing"
STATE_WON = "won"
STATE_LOST = "lost"

# Letter States
LETTER_CORRECT = "correct"    # Blue - right letter, right position
LETTER_PARTIAL = "partial"    # Red - right letter, wrong position  
LETTER_ABSENT = "absent"      # Gray - letter not in word

# Word Length Options
WORD_LENGTH_OPTIONS = [5, 6, 7, 8]

# API Timeouts
API_TIMEOUT = 10

# UI Configuration
DEFAULT_WORD_LENGTH = 5

# Config Flow Constants
CONF_DIFFICULTY = "difficulty"

# Audio Configuration Constants
CONF_AUDIO_ENABLED = "audio_enabled"
CONF_AUDIO_VOLUME = "audio_volume"
CONF_AUDIO_GAME_EVENTS = "audio_game_events"
CONF_AUDIO_GUESS_EVENTS = "audio_guess_events"
CONF_AUDIO_UI_EVENTS = "audio_ui_events"
CONF_AUDIO_ERROR_EVENTS = "audio_error_events"

# Difficulty Levels
DIFFICULTY_EASY = "easy"      # Hint shown before guessing
DIFFICULTY_NORMAL = "normal"  # Hints available on request
DIFFICULTY_HARD = "hard"      # No hints available

# Default Config Values
DEFAULT_DIFFICULTY = DIFFICULTY_NORMAL

# Audio Default Values
DEFAULT_AUDIO_ENABLED = True
DEFAULT_AUDIO_VOLUME = 30  # Percentage (0-100)
DEFAULT_AUDIO_GAME_EVENTS = True
DEFAULT_AUDIO_GUESS_EVENTS = True
DEFAULT_AUDIO_UI_EVENTS = False
DEFAULT_AUDIO_ERROR_EVENTS = True