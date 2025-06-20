# H.A WordPlay

A Wordle-style word guessing game integration for Home Assistant with built-in anti-cheat protection and voice announcements. Play directly from your HA dashboard with dynamically generated word puzzles! 

*Requires card-mod to be installed from HACS to enable the compact game card layout.*

## 🎮 Features

- **Zero Configuration**: Install and play immediately - no setup required
- **Custom Input System**: Built-in text input and word length selector - no manual helpers needed
- **Dynamic Word Generation**: Uses online APIs to fetch random words (5-8 letters)
- **Smart Hints**: Get contextual clues from word definitions
- **🛡️ Anti-Cheat Protection**: Prevents vowel dumping and unfair letter hunting strategies
- **🔊 Voice Announcements**: TTS feedback for wins, losses, and rule violations (auto-configured)
- **Wordle-Style Feedback**: Color-coded letter feedback (🟦 correct, 🟥 partial, ⬜ absent)
- **Dynamic Game Length**: Choose words from 5 to 8 letters (guesses = word length)
- **Clean Single-Card Interface**: Unified dashboard design with live input preview
- **Unlimited Play**: Start new games whenever you want
- **Standalone**: No external servers, user accounts, or data collection

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations" 
3. Click the three dots (⋮) in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/CBDesignS/ha-wordplay`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "H.A WordPlay" and install
9. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/ha_wordplay` folder to your HA `custom_components` directory
3. Restart Home Assistant

## 🎯 How to Play

### Quick Start

1. **Select Word Length**: Use the dropdown to choose 5, 6, 7, or 8 letters
2. **Start Game**: Click "New Game" button
3. **Type Your Guess**: Use the text input field 
4. **Submit**: Click "Submit" or use the submit_guess service
5. **See Results**: Latest guess shows with color feedback
6. **Repeat**: Continue guessing until you win or run out of attempts

### Game Rules

- **Dynamic Guesses**: Number of guesses equals word length (5 letters = 5 guesses, 8 letters = 8 guesses)
- **Valid Words**: Must be real English words with balanced letter composition
- **Win Condition**: Guess the exact word within your allowed attempts

### Color Coding

- **🟦 Blue**: Correct letter in correct position
- **🟥 Red**: Correct letter in wrong position  
- **⬜ White**: Letter not in the word

## 🛡️ Anti-Cheat Protection

WordPlay includes smart anti-cheat rules to ensure fair gameplay and prevent common cheating strategies:

### Blocked Strategies

❌ **Vowel Dumping**: `AEIOU` - Cannot guess all vowels
```
🚨 "Guess must contain at least one consonant (no vowel dumping!)"
```

❌ **Vowel Overload**: `AEIOP` - Maximum 60% vowels allowed
```
🚨 "Too many vowels! Try a more balanced word"
```

❌ **Single Consonant**: `AAAAB` - Need at least 2 different consonants for 5+ letter words
```
🚨 "Need at least 2 different consonants for fair play"
```

### Allowed Examples

✅ **BOARD** - Good balance of vowels and consonants  
✅ **HOUSE** - Multiple consonants, reasonable vowel ratio  
✅ **QUICK** - Complex consonant patterns allowed  
✅ **STORM** - Single vowel with multiple consonants

### Anti-Cheat Feedback

- **Visual**: Red error messages appear in the game interface
- **Audio**: Voice announcements explain the violation (if TTS configured)
- **Immediate**: Blocked guesses don't count against your guess limit

## 🔊 Audio Features

WordPlay automatically integrates with Home Assistant's TTS system for immersive audio feedback:

### Voice Announcements

🎉 **Win Celebration**: *"Congratulations! You guessed the word HOUSE correctly in 3 tries!"*  
🚨 **Anti-Cheat Warning**: *"Invalid guess. Too many vowels! Try a more balanced word."*  
😢 **Game Over**: *"Game over! The word was STORM. Better luck next time!"*  
🎮 **New Game**: *"New 6 letter WordPlay game started! Good luck!"*

### Auto-Configuration

- **Detects TTS Services**: Works with Google Translate, Cloud TTS, or any HA TTS service
- **Finds Speakers**: Automatically uses available media players (Google Home, Alexa, Cast devices)
- **Smart Fallback**: Gracefully disables if no TTS/speakers available
- **Zero Setup**: No configuration required - works out of the box

### Manual TTS Setup (Optional)

If auto-detection fails, you can specify devices in the integration configuration:

```yaml
# Not normally needed - auto-detects by default
ha_wordplay:
  tts:
    enabled: true
    media_player: "media_player.kitchen_speaker"
    language: "en"
```

## 📊 Game Entities

The integration creates several entities for dashboard integration:

- `select.ha_wordplay_word_length` - Word length selector (5-8)
- `text.ha_wordplay_guess_input` - Text input for guesses
- `sensor.ha_wordplay_game_state` - Current game status and display data
- `sensor.ha_wordplay_guesses` - Guess history and results

## 🎨 Dashboard Integration

### Complete Dashboard Configuration

Use this YAML for the optimal gaming experience:

```yaml
type: custom:mod-card
card_mod:
  style: |
    ha-card {
      background: var(--card-background-color);
      border-radius: 12px;
      padding: 16px;
      overflow: hidden;
      box-shadow: var(--ha-card-box-shadow);
    }
card:
  type: vertical-stack
  title: ""
  cards:
    - type: markdown
      content: |
        <center>
          <h2 style="margin: 8px 0; color: var(--primary-text-color);">
            🎮 H.A WordPlay
          </h2>
        </center>
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Message Display for Anti-Cheat Feedback
    - type: markdown
      content: >
        {% set message = state_attr('sensor.ha_wordplay_game_state',
        'last_message') %}

        {% set message_type = state_attr('sensor.ha_wordplay_game_state',
        'message_type') %}

        {% if message %}
          {% if message_type == 'success' %}
            <div style="background: green; color: white; padding: 8px; border-radius: 6px; text-align: center; margin: 4px 0;">
              🎉 {{ message }}
            </div>
          {% elif message_type == 'error' %}
            <div style="background: red; color: white; padding: 8px; border-radius: 6px; text-align: center; margin: 4px 0;">
              🚨 {{ message }}
            </div>
          {% else %}
            <div style="background: blue; color: white; padding: 8px; border-radius: 6px; text-align: center; margin: 4px 0;">
              ℹ️ {{ message }}
            </div>
          {% endif %}
        {% endif %}
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Game Status Bar
    - type: markdown
      content: >
        <div style="display: flex; justify-content: space-around; background:
        var(--secondary-background-color); padding: 8px; border-radius: 6px;
        margin: 8px 0;">
          <span>📊 {{ states('sensor.ha_wordplay_game_state') | title }}</span>
          <span>🎯 {{ state_attr('sensor.ha_wordplay_game_state', 'guesses_remaining') or 5 }} left</span>
          <span>📝 {{ state_attr('sensor.ha_wordplay_game_state', 'word_length') or 5 }} letters</span>
        </div>
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Previous Guesses
    - type: markdown
      content: >
        <h3 style="margin: 12px 0 6px 0;">Previous Guesses</h3>

        <div style="background: var(--secondary-background-color); padding:
        12px; border-radius: 6px; min-height: 80px; font-family: monospace;">

        {%- set guesses = state_attr('sensor.ha_wordplay_guesses',
        'all_guesses_formatted') -%}

        {%- if guesses and guesses|length > 0 -%}
          {%- for guess in guesses -%}
            <div style="text-align: center; font-size: 16px; margin: 4px 0;">{{ guess }}</div>
          {%- endfor -%}
        {%- else -%}
          <div style="text-align: center; color: var(--secondary-text-color); font-style: italic; padding: 20px 0;">Start a new game to begin guessing!</div>
        {%- endif -%}

        </div>
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Latest Guess
    - type: markdown
      content: >
        <h3 style="margin: 12px 0 6px 0;">Latest Guess</h3>

        <div style="background: var(--primary-color); color:
        var(--text-primary-color); padding: 12px; border-radius: 6px;
        text-align: center; font-family: monospace; font-size: 20px;
        letter-spacing: 2px;">

        {%- set latest = state_attr('sensor.ha_wordplay_game_state',
        'latest_result') -%}

        {{ latest if latest else "_ _ _ _ _" }}

        </div>
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Current Input
    - type: markdown
      content: >
        <h3 style="margin: 12px 0 6px 0;">Current Guess</h3>

        <div style="background: var(--secondary-background-color); border: 2px
        dashed var(--divider-color); padding: 12px; border-radius: 6px;
        text-align: center; font-family: monospace; font-size: 20px;
        letter-spacing: 2px;">

        {%- set current = state_attr('sensor.ha_wordplay_game_state',
        'current_input') -%}

        {{ current if current else "_ _ _ _ _" }}

        </div>
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Hint Section
    - type: markdown
      content: >
        <div style="background: var(--info-color); color: white; padding: 8px
        12px; border-radius: 6px; margin: 8px 0;">
          <strong>💡 Hint:</strong>
          {%- set hint = state_attr('sensor.ha_wordplay_game_state', 'hint') -%}
          {{ hint if hint else "Start a game and click 'Get Hint' for clues!" }}
        </div>
      card_mod:
        style: >
          ha-card { background: transparent; box-shadow: none; border: none;
          margin: 0; }
    
    # Input Field
    - type: entities
      entities:
        - entity: text.ha_wordplay_guess_input
          name: Type Your Guess
          icon: mdi:keyboard
        - entity: select.ha_wordplay_word_length
          name: Word Length
          icon: mdi:numeric
      show_header_toggle: false
      card_mod:
        style: |
          ha-card { 
            background: var(--secondary-background-color); 
            border-radius: 6px; 
            margin: 8px 0;
          }
    
    # Controls - All 3 buttons in one row
    - type: horizontal-stack
      cards:
        - type: button
          name: Submit
          icon: mdi:send
          tap_action:
            action: call-service
            service: ha_wordplay.submit_guess
          card_mod:
            style: |
              ha-card {
                background: var(--success-color);
                color: white;
                border-radius: 6px;
                margin: 2px;
                height: 50px !important;
                font-size: 14px;
              }
        - type: button
          name: New Game
          icon: mdi:play
          tap_action:
            action: call-service
            service: ha_wordplay.new_game
          card_mod:
            style: |
              ha-card {
                background: var(--primary-color);
                color: var(--text-primary-color);
                border-radius: 6px;
                margin: 2px;
                height: 50px !important;
                font-size: 14px;
              }
        - type: button
          name: Get Hint
          icon: mdi:lightbulb
          tap_action:
            action: call-service
            service: ha_wordplay.get_hint
          card_mod:
            style: |
              ha-card {
                background: var(--warning-color);
                color: white;
                border-radius: 6px;
                margin: 2px;
                height: 50px !important;
                font-size: 14px;
              }
```

## 🔧 Services

### `ha_wordplay.new_game`

Start a new word guessing game.

**Parameters:**
- `word_length` (optional): Number of letters (5-8, default: uses selected length)

**Example:**
```yaml
service: ha_wordplay.new_game
data:
  word_length: 6
```

### `ha_wordplay.make_guess`

Submit a guess for the current game.

**Parameters:**
- `guess` (required): Your word guess (must match current word length)

**Example:**
```yaml
service: ha_wordplay.make_guess
data:
  guess: "BOARD"
```

### `ha_wordplay.submit_guess`

Submit the current text input as a guess.

**No parameters required.**

**Example:**
```yaml
service: ha_wordplay.submit_guess
```

### `ha_wordplay.get_hint`

Get a hint for the current word (based on dictionary definition).

**No parameters required.**

**Example:**
```yaml
service: ha_wordplay.get_hint
```

## 🌐 API Dependencies

This integration uses the following free APIs:

- **Random Word API**: `https://random-word-api.herokuapp.com/` - For generating random words
- **Free Dictionary API**: `https://dictionaryapi.dev/` - For word definitions and hints

Both APIs are free and require no authentication. The integration handles all API communication automatically with smart fallbacks and retry logic.

## 🔒 Privacy & Security

- **No Data Collection**: Your games, scores, and guesses stay local to your Home Assistant instance
- **No User Accounts**: No registration or personal information required  
- **No External Storage**: All game data is stored locally in HA entities
- **Secure Logging**: Debug logs never expose the current word to prevent cheating
- **UK English Focus**: Currently optimized for UK English dictionary

## 🚧 Development Status

**Current Version**: 0.3.0 (Beta)

**What's Working:**
- ✅ Core game logic with anti-cheat protection
- ✅ Custom text input and word length selector entities
- ✅ Service integration with Home Assistant
- ✅ Clean unified dashboard interface
- ✅ Live input preview and dynamic guess limits
- ✅ TTS integration with auto-configuration
- ✅ API integration for words and definitions
- ✅ 5-8 letter word support with balanced gameplay

**Recent Updates:**
- 🛡️ Anti-cheat system prevents vowel dumping strategies
- 🔊 Voice announcements for all game events
- 🎯 Dynamic guess limits (word length = guess count)
- 🔒 Secure debug logging (no word leaks)
- 🎨 Unified single-card dashboard design

**Coming Soon:**
- 🔲 Enhanced UI animations and visual effects
- 🔲 Statistics tracking and performance metrics
- 🔲 Achievement system and badges

**Future Plans:**
- 🔲 Easy/Hard modes with different rule sets
- 🔲 Multi-language support and international dictionaries
- 🔲 Custom word lists and themed categories
- 🔲 Multiplayer and tournament modes
- 🔲 Advanced difficulty levels

## 🐛 Known Issues

- Dashboard requires manual YAML configuration (auto-creation planned)
- API failures may require game restart in rare cases
- Some TTS services may need specific language codes

## 🎮 Game Strategy Tips

### Effective Starting Words
- **BOARD** - Good mix of common letters
- **STEAM** - Covers multiple vowels efficiently  
- **FLING** - Tests common consonant patterns
- **CHORE** - Balanced letter distribution

### Anti-Cheat Approved Strategies
- ✅ Use words with balanced vowel/consonant ratios
- ✅ Include multiple different consonants
- ✅ Test common letter patterns like TH, ST, ING
- ✅ Use actual English words for best results

### What NOT to Do
- ❌ Don't try to guess all vowels at once
- ❌ Avoid words with excessive vowel concentration
- ❌ Don't use single-consonant patterns
- ❌ Random letter combinations won't work

## 🤝 Contributing

This is an open-source project! Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Areas for Contribution:**
- Additional language support
- UI/UX improvements
- Performance optimizations
- New game modes
- Enhanced anti-cheat detection

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by the original Wordle game by Josh Wardle
- Uses the Random Word API for word generation
- Uses the Free Dictionary API for definitions
- Built for the Home Assistant community with ❤️

## 📞 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/CBDesignS/ha-wordplay/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/CBDesignS/ha-wordplay/discussions)
- **Home Assistant Community**: Find help in the [HA Community Forum](https://community.home-assistant.io/)

---

**Note**: This integration is not affiliated with or endorsed by the original Wordle game or The New York Times. It is a custom implementation of a word guessing game designed specifically for Home Assistant automation enthusiasts.
