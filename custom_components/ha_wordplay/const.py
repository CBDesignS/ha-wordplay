"""Constants for H.A WordPlay integration."""

DOMAIN = "ha_wordplay"

# API Endpoints
RANDOM_WORD_API = "https://random-word-api.herokuapp.com/word"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"

# Game Configuration
MIN_WORD_LENGTH = 5  # Updated: removed 4-letter words
MAX_WORD_LENGTH = 8  # Updated: added 7&8 letter words
MAX_GUESSES = 6

# Service Names
SERVICE_NEW_GAME = "new_game"
SERVICE_MAKE_GUESS = "make_guess"
SERVICE_GET_HINT = "get_hint"
SERVICE_SUBMIT_GUESS = "submit_guess"

# Entity IDs
GAME_STATE_ENTITY = "sensor.ha_wordplay_game_state"
CURRENT_WORD_ENTITY = "sensor.ha_wordplay_current_word"
GUESSES_ENTITY = "sensor.ha_wordplay_guesses"
WORD_LENGTH_ENTITY = "select.ha_wordplay_word_length"  # Updated: now a select entity
GUESS_INPUT_ENTITY = "text.ha_wordplay_guess_input"    # Updated: custom text entity

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