"""Enhanced Lovelace dashboard configuration for H.A WordPlay."""
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Unified single-card dashboard configuration
UNIFIED_DASHBOARD_CONFIG = """
# H.A WordPlay - Unified Game Interface
# Single card design - no more blocky separation!

type: custom:mod-card
card_mod:
  style: |
    ha-card {
      background: var(--card-background-color);
      border-radius: 12px;
      padding: 0;
      overflow: hidden;
      box-shadow: var(--ha-card-box-shadow);
    }
card:
  type: vertical-stack
  title: ""
  cards:
    # Header Section
    - type: markdown
      content: |
        <div style="text-align: center; padding: 16px 0 8px 0;">
          <h2 style="margin: 0; color: var(--primary-text-color); display: flex; align-items: center; justify-content: center; gap: 8px;">
            🎮 <span>H.A WordPlay</span>
          </h2>
        </div>
      card_mod:
        style: |
          ha-card {
            background: transparent;
            box-shadow: none;
            border: none;
          }

    # Game Board Section
    - type: markdown
      content: |
        <div style="padding: 0 20px;">
          <!-- Game Status Bar -->
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding: 8px 12px; background: var(--secondary-background-color); border-radius: 8px;">
            <span style="font-size: 14px; color: var(--secondary-text-color);">
              📊 {{ states('sensor.ha_wordplay_game_state') | title }}
            </span>
            <span style="font-size: 14px; color: var(--secondary-text-color);">
              🎯 {{ state_attr('sensor.ha_wordplay_game_state', 'guesses_remaining') or 6 }} left
            </span>
            <span style="font-size: 14px; color: var(--secondary-text-color);">
              📝 {{ state_attr('sensor.ha_wordplay_game_state', 'word_length') or 5 }} letters
            </span>
          </div>
          
          <!-- Previous Guesses History -->
          <div style="margin-bottom: 16px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: var(--primary-text-color);">Previous Guesses</h3>
            <div style="min-height: 120px; background: var(--secondary-background-color); border-radius: 8px; padding: 12px; font-family: 'Courier New', monospace;">
              {% set guesses = state_attr('sensor.ha_wordplay_guesses', 'all_guesses_formatted') %}
              {% if guesses and guesses|length > 0 %}
                {% for guess in guesses %}
                  <div style="margin-bottom: 8px; font-size: 18px; text-align: center; letter-spacing: 2px;">
                    {{ guess }}
                  </div>
                {% endfor %}
              {% else %}
                <div style="text-align: center; color: var(--secondary-text-color); font-style: italic; padding-top: 40px;">
                  Start a new game to begin guessing!
                </div>
              {% endif %}
            </div>
          </div>
          
          <!-- Latest Guess Result -->
          <div style="margin-bottom: 16px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: var(--primary-text-color);">Latest Guess</h3>
            <div style="background: var(--primary-color); color: var(--text-primary-color); border-radius: 8px; padding: 16px; text-align: center; font-family: 'Courier New', monospace; font-size: 24px; letter-spacing: 4px; min-height: 40px; display: flex; align-items: center; justify-content: center;">
              {% set latest = state_attr('sensor.ha_wordplay_game_state', 'latest_result') %}
              {{ latest if latest else "_ _ _ _ _" }}
            </div>
          </div>
          
          <!-- Current Input Preview -->
          <div style="margin-bottom: 20px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: var(--primary-text-color);">Current Guess</h3>
            <div style="background: var(--secondary-background-color); border: 2px dashed var(--divider-color); border-radius: 8px; padding: 16px; text-align: center; font-family: 'Courier New', monospace; font-size: 24px; letter-spacing: 4px; min-height: 40px; display: flex; align-items: center; justify-content: center;">
              {% set current = state_attr('sensor.ha_wordplay_game_state', 'current_input') %}
              {{ current if current else "_ _ _ _ _" }}
            </div>
          </div>
        </div>
      card_mod:
        style: |
          ha-card {
            background: transparent;
            box-shadow: none;
            border: none;
          }

    # Controls Section
    - type: horizontal-stack
      cards:
        # Input and Submit
        - type: vertical-stack
          cards:
            - type: entities
              entities:
                - entity: text.ha_wordplay_guess_input
                  name: "Type Your Guess"
                  icon: mdi:keyboard
              show_header_toggle: false
              card_mod:
                style: |
                  ha-card {
                    background: var(--secondary-background-color);
                    border-radius: 8px;
                    margin: 4px;
                  }
            
            - type: button
              name: "Submit Guess"
              icon: mdi:send
              tap_action:
                action: call-service
                service: ha_wordplay.submit_guess
              card_mod:
                style: |
                  ha-card {
                    background: var(--success-color);
                    color: white;
                    border-radius: 8px;
                    margin: 4px;
                  }
        
        # Game Controls
        - type: vertical-stack
          cards:
            - type: entities
              entities:
                - entity: select.ha_wordplay_word_length
                  name: "Word Length"
                  icon: mdi:numeric
              show_header_toggle: false
              card_mod:
                style: |
                  ha-card {
                    background: var(--secondary-background-color);
                    border-radius: 8px;
                    margin: 4px;
                  }
            
            - type: button
              name: "New Game"
              icon: mdi:play
              tap_action:
                action: call-service
                service: ha_wordplay.new_game
              card_mod:
                style: |
                  ha-card {
                    background: var(--primary-color);
                    color: var(--text-primary-color);
                    border-radius: 8px;
                    margin: 4px;
                  }

    # Hint Section
    - type: horizontal-stack
      cards:
        - type: button
          name: "Get Hint"
          icon: mdi:lightbulb
          tap_action:
            action: call-service
            service: ha_wordplay.get_hint
          card_mod:
            style: |
              ha-card {
                background: var(--warning-color);
                color: white;
                border-radius: 8px;
                margin: 4px;
                flex: 0 0 30%;
              }
        
        - type: markdown
          content: |
            <div style="padding: 8px 12px; background: var(--info-color); color: white; border-radius: 8px; margin: 4px;">
              <strong>💡 Hint:</strong><br>
              {% set hint = state_attr('sensor.ha_wordplay_game_state', 'hint') %}
              {{ hint if hint else "Start a game and click 'Get Hint' for clues!" }}
            </div>
          card_mod:
            style: |
              ha-card {
                background: transparent;
                box-shadow: none;
                border: none;
                flex: 1;
              }
"""

# Legacy dashboard for fallback
LEGACY_DASHBOARD_CONFIG = """
# H.A WordPlay Dashboard Configuration - Legacy Version
# Copy this YAML to your dashboard if the unified version doesn't work

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
        _LOGGER.info("WordPlay unified dashboard configuration ready for manual setup")
        _LOGGER.info("New unified single-card design eliminates blocky appearance")
        
        # Store the configuration in hass.data for potential auto-creation
        if "ha_wordplay" not in hass.data:
            hass.data["ha_wordplay"] = {}
        
        hass.data["ha_wordplay"]["dashboard_configs"] = {
            "unified": UNIFIED_DASHBOARD_CONFIG,
            "legacy": LEGACY_DASHBOARD_CONFIG
        }
        
        # Future enhancement: automatically create dashboard
        # This would require accessing the lovelace configuration API
        
    except Exception as e:
        _LOGGER.error("Could not prepare dashboard: %s", e)

def get_unified_dashboard_config() -> str:
    """Return the unified dashboard configuration YAML."""
    return UNIFIED_DASHBOARD_CONFIG

def get_legacy_dashboard_config() -> str:
    """Return the legacy dashboard configuration YAML."""
    return LEGACY_DASHBOARD_CONFIG

# Auto-install capability for future use
async def async_auto_install_dashboard(hass: HomeAssistant, config_type: str = "unified") -> bool:
    """Automatically install the dashboard configuration (future feature)."""
    try:
        # This would require Home Assistant's lovelace config API
        # Implementation pending HA dashboard auto-creation capabilities
        _LOGGER.info(f"Auto-install requested for {config_type} dashboard")
        _LOGGER.info("Manual dashboard setup still required")
        return False
    except Exception as e:
        _LOGGER.error(f"Auto-install failed: {e}")
        return False