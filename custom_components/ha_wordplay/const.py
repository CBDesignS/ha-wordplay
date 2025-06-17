"""Constants for H.A WordPlay integration."""

DOMAIN = "ha_wordplay"

# API Endpoints
RANDOM_WORD_API = "https://random-word-api.herokuapp.com/word"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"

# Game Configuration
MIN_WORD_LENGTH = 4
MAX_WORD_LENGTH = 8
MAX_GUESSES = 6

# Service Names
SERVICE_NEW_GAME = "new_game"
SERVICE_MAKE_GUESS = "make_guess"
SERVICE_GET_HINT = "get_hint"

# Entity IDs
GAME_STATE_ENTITY = "sensor.ha_wordplay_game_state"
CURRENT_WORD_ENTITY = "sensor.ha_wordplay_current_word"
GUESSES_ENTITY = "sensor.ha_wordplay_guesses"
WORD_LENGTH_ENTITY = "input_number.ha_wordplay_word_length"

# Game States
STATE_IDLE = "idle"
STATE_PLAYING = "playing"
STATE_WON = "won"
STATE_LOST = "lost"

# API Timeouts
API_TIMEOUT = 10
