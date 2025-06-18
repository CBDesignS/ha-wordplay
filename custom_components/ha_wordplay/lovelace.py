"""Lovelace dashboard configuration for H.A WordPlay."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.lovelace import _async_gen_from_config

_LOGGER = logging.getLogger(__name__)

WORDPLAY_CARD_CONFIG = {
    "type": "vertical-stack",
    "title": "H.A WordPlay",
    "cards": [
        {
            "type": "horizontal-stack",
            "cards": [
                {
                    "type": "button",
                    "tap_action": {
                        "action": "call-service",
                        "service": "ha_wordplay.new_game",
                        "data": {"word_length": 4}
                    },
                    "name": "New 4-Letter Game",
                    "icon": "mdi:alpha-a-circle"
                },
                {
                    "type": "button", 
                    "tap_action": {
                        "action": "call-service",
                        "service": "ha_wordplay.new_game",
                        "data": {"word_length": 5}
                    },
                    "name": "New 5-Letter Game",
                    "icon": "mdi:alpha-a-circle-outline"
                },
                {
                    "type": "button",
                    "tap_action": {
                        "action": "call-service", 
                        "service": "ha_wordplay.new_game",
                        "data": {"word_length": 6}
                    },
                    "name": "New 6-Letter Game",
                    "icon": "mdi:alpha-a-circle"
                }
            ]
        },
        {
            "type": "entities",
            "title": "Game Status",
            "show_header_toggle": False,
            "entities": [
                {
                    "entity": "sensor.ha_wordplay_game_state",
                    "name": "Game Status"
                },
                {
                    "entity": "sensor.ha_wordplay_guesses", 
                    "name": "Guesses Made"
                }
            ]
        },
        {
            "type": "markdown",
            "content": """{% set game_state = states('sensor.ha_wordplay_game_state') %}
{% set guesses_entity = states.sensor.ha_wordplay_guesses %}
{% if guesses_entity and guesses_entity.attributes %}
  {% set guesses = guesses_entity.attributes.get('guesses', []) %}
  {% set results = guesses_entity.attributes.get('results', []) %}
  {% set word_length = states.sensor.ha_wordplay_game_state.attributes.get('word_length', 5) %}
  {% set max_guesses = guesses_entity.attributes.get('max_guesses', 6) %}
  
  ## Word Grid ({{ word_length }} letters)
  
  {% for guess_num in range(max_guesses) %}
  {% if guess_num < guesses|length %}
    {% set guess = guesses[guess_num] %}
    {% set result = results[guess_num] %}
  **Row {{ guess_num + 1 }}:**  
  {% for i in range(word_length) %}{% set letter = guess[i] if i < guess|length else ' ' %}{% set color = result[i] if i < result|length else 'absent' %}{% if color == 'correct' %}🟦**{{ letter }}**{% elif color == 'partial' %}🟥**{{ letter }}**{% else %}⬛**{{ letter }}**{% endif %}   {% endfor %}  
  {% else %}
  **Row {{ guess_num + 1 }}:**  
  {% for i in range(word_length) %}⬜**_**   {% endfor %}  
  {% endif %}
  {% endfor %}
  
  {% if game_state == 'won' %}
  ## 🎉 You Won! 🎉
  {% elif game_state == 'lost' %}
  ## 😞 Game Over
  **The word was:** {{ states.sensor.ha_wordplay_debug.state if states.sensor.ha_wordplay_debug else 'Unknown' }}
  {% elif game_state == 'playing' %}
  **{{ max_guesses - guesses|length }}** guesses remaining
  {% else %}
  Start a new game to play!
  {% endif %}
{% else %}
  ## H.A WordPlay
  Start a new game to begin playing!
{% endif %}"""
        },
        {
            "type": "conditional",
            "conditions": [
                {
                    "entity": "sensor.ha_wordplay_game_state",
                    "state": "playing"
                }
            ],
            "card": {
                "type": "entities",
                "title": "Enter Your Guess",
                "entities": [
                    {
                        "entity": "input_text.ha_wordplay_guess",
                        "name": "Type your word here"
                    }
                ]
            }
        },
        {
            "type": "conditional", 
            "conditions": [
                {
                    "entity": "sensor.ha_wordplay_game_state",
                    "state": "playing"
                }
            ],
            "card": {
                "type": "horizontal-stack",
                "cards": [
                    {
                        "type": "button",
                        "tap_action": {
                            "action": "call-service",
                            "service": "ha_wordplay.submit_guess"
                        },
                        "name": "Submit Guess",
                        "icon": "mdi:send"
                    },
                    {
                        "type": "button",
                        "tap_action": {
                            "action": "call-service", 
                            "service": "ha_wordplay.get_hint"
                        },
                        "name": "Get Hint",
                        "icon": "mdi:lightbulb"
                    }
                ]
            }
        }
    ]
}

async def async_create_wordplay_dashboard(hass: HomeAssistant) -> None:
    """Create a WordPlay dashboard automatically."""
    try:
        # This would require more complex integration with HA's dashboard system
        # For now, we'll provide the config for manual creation
        _LOGGER.info("WordPlay dashboard configuration available")
    except Exception as e:
        _LOGGER.error("Could not create dashboard: %s", e)
