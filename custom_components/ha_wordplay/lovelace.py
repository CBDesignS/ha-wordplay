"""Lovelace dashboard configuration for H.A WordPlay."""
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Sample dashboard configuration for copy/paste
DASHBOARD_CONFIG = """
# H.A WordPlay Dashboard Configuration
# Copy this YAML to your dashboard

type: vertical-stack
title: H.A WordPlay
cards:
  # Game Controls
  - type: horizontal-stack
    cards:
      - type: entities
        title: Game Setup
        entities:
          - entity: select.ha_wordplay_word_length
            name: Word Length
      - type: button
        name: New Game
        icon: mdi:play
        tap_action:
          action: call-service
          service: ha_wordplay.new_game
        hold_action:
          action: none

  # Game Display - Two Row Layout
  - type: vertical-stack
    title: Game Board
    cards:
      # Top Row - Latest Guess Result
      - type: markdown
        title: "Latest Guess"
        content: |
          {% set latest = state_attr('sensor.ha_wordplay_game_state', 'latest_result') %}
          {% if latest %}
          ## {{ latest }}
          {% else %}
          ## _ _ _ _ _
          {% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              font-family: monospace;
              font-size: 1.5em;
              background: var(--primary-color);
              color: var(--text-primary-color);
            }

      # Bottom Row - Current Input
      - type: markdown
        title: "Current Guess"
        content: |
          {% set current = state_attr('sensor.ha_wordplay_game_state', 'current_input') %}
          {% if current %}
          ## {{ current }}
          {% else %}
          ## _ _ _ _ _
          {% endif %}
        card_mod:
          style: |
            ha-card {
              text-align: center;
              font-family: monospace;
              font-size: 1.5em;
              background: var(--secondary-background-color);
            }

  # Input Controls
  - type: horizontal-stack
    cards:
      - type: entities
        entities:
          - entity: text.ha_wordplay_guess_input
            name: Type Your Guess
      - type: button
        name: Submit
        icon: mdi:send
        tap_action:
          action: call-service
          service: ha_wordplay.submit_guess

  # Game Information
  - type: entities
    title: Game Status
    entities:
      - entity: sensor.ha_wordplay_game_state
        name: Game State
      - entity: sensor.ha_wordplay_guesses
        name: Guesses Made
    
  # Game Actions
  - type: horizontal-stack
    cards:
      - type: button
        name: Get Hint
        icon: mdi:lightbulb
        tap_action:
          action: call-service
          service: ha_wordplay.get_hint
      - type: markdown
        content: |
          {% set hint = state_attr('sensor.ha_wordplay_game_state', 'hint') %}
          **Hint:** {{ hint if hint else "Start a game to get hints!" }}
        card_mod:
          style: |
            ha-card {
              padding: 8px;
              font-size: 0.9em;
            }

  # All Guesses History
  - type: markdown
    title: "Guess History"
    content: |
      {% set guesses = state_attr('sensor.ha_wordplay_guesses', 'all_guesses_formatted') %}
      {% if guesses %}
      {% for guess in guesses %}
      {{ loop.index }}. {{ guess }}
      {% endfor %}
      {% else %}
      No guesses yet - start a new game!
      {% endif %}
    card_mod:
      style: |
        ha-card {
          font-family: monospace;
          text-align: center;
        }
"""

async def async_create_wordplay_dashboard(hass: HomeAssistant) -> None:
    """Create a WordPlay dashboard automatically."""
    try:
        # For now, just log the configuration for manual setup
        _LOGGER.info("WordPlay dashboard configuration ready for manual setup")
        _LOGGER.info("Copy the dashboard YAML from the integration documentation")
        
        # Future enhancement: automatically create dashboard
        # This would require accessing the lovelace configuration API
        
    except Exception as e:
        _LOGGER.error("Could not prepare dashboard: %s", e)

def get_dashboard_config() -> str:
    """Return the dashboard configuration YAML."""
    return DASHBOARD_CONFIG