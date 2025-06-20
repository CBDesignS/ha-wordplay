# H.A WordPlay

A Wordle-style word guessing game integration for Home Assistant. Play directly from your HA dashboard with dynamically generated word puzzles! !! this requires card-mod to be installed from hacs to enable the compact game card layout !!

## 🎮 Features

- **Zero Configuration**: Install and play immediately - no setup required
- **Custom Input System**: Built-in text input and word length selector - no manual helpers needed
- **Dynamic Word Generation**: Uses online APIs to fetch random words (5-8 letters)
- **Smart Hints**: Get contextual clues from word definitions
- **Wordle-Style Feedback**: Color-coded letter feedback (🟦 correct, 🟥 partial, ⬜ absent)
- **Multiple Game Lengths**: Choose words from 5 to 8 letters long
- **Clean 2-Row Interface**: Top row shows latest guess results, bottom row shows live typing
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
5. **See Results**: Top row shows your guess with color feedback
6. **Repeat**: Continue guessing until you win or run out of attempts

### Color Coding

- **🟦 Blue**: Correct letter in correct position
- **🟥 Red**: Correct letter in wrong position  
- **⬜ White**: Letter not in the word

### Service Calls

You can also control the game via service calls:

```yaml
# Start a new 6-letter game
service: ha_wordplay.new_game
data:
  word_length: 6

# Submit a guess
service: ha_wordplay.make_guess
data:
  guess: "WORDLE"

# Submit current text input
service: ha_wordplay.submit_guess

# Get a hint
service: ha_wordplay.get_hint
```

## 📊 Game Entities

The integration creates several entities:

- `select.ha_wordplay_word_length` - Word length selector (5-8)
- `text.ha_wordplay_guess_input` - Text input for guesses
- `sensor.ha_wordplay_game_state` - Current game status and display data
- `sensor.ha_wordplay_guesses` - Guess history and results
- `sensor.ha_wordplay_debug` - Debug info (development only)

## 🎨 Dashboard Integration

### Complete Dashboard Example

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
    # Header Section
    - type: markdown
      content: |
        <center>
          <h2 style="margin: 8px 0; color: var(--primary-text-color);">
            🎮 H.A WordPlay
          </h2>
        </center>
      card_mod:
        style: |
          ha-card { background: transparent; box-shadow: none; border: none; margin: 0; }

    # Game Status Bar
    - type: markdown
      content: |
        <div style="display: flex; justify-content: space-around; background: var(--secondary-background-color); padding: 8px; border-radius: 6px; margin: 8px 0;">
          <span>📊 {{ states('sensor.ha_wordplay_game_state') | title }}</span>
          <span>🎯 {{ state_attr('sensor.ha_wordplay_game_state', 'guesses_remaining') or 6 }} left</span>
          <span>📝 {{ state_attr('sensor.ha_wordplay_game_state', 'word_length') or 5 }} letters</span>
        </div>
      card_mod:
        style: |
          ha-card { background: transparent; box-shadow: none; border: none; margin: 0; }

    # Previous Guesses
    - type: markdown
      content: |
        <h3 style="margin: 12px 0 6px 0;">Previous Guesses</h3>
        <div style="background: var(--secondary-background-color); padding: 12px; border-radius: 6px; min-height: 80px; font-family: monospace;">
        {%- set guesses = state_attr('sensor.ha_wordplay_guesses', 'all_guesses_formatted') -%}
        {%- if guesses and guesses|length > 0 -%}
          {%- for guess in guesses -%}
            <div style="text-align: center; font-size: 16px; margin: 4px 0;">{{ guess }}</div>
          {%- endfor -%}
        {%- else -%}
          <div style="text-align: center; color: var(--secondary-text-color); font-style: italic; padding: 20px 0;">Start a new game to begin guessing!</div>
        {%- endif -%}
        </div>
      card_mod:
        style: |
          ha-card { background: transparent; box-shadow: none; border: none; margin: 0; }

    # Latest Guess
    - type: markdown
      content: |
        <h3 style="margin: 12px 0 6px 0;">Latest Guess</h3>
        <div style="background: var(--primary-color); color: var(--text-primary-color); padding: 12px; border-radius: 6px; text-align: center; font-family: monospace; font-size: 20px; letter-spacing: 2px;">
        {%- set latest = state_attr('sensor.ha_wordplay_game_state', 'latest_result') -%}
        {{ latest if latest else "_ _ _ _ _" }}
        </div>
      card_mod:
        style: |
          ha-card { background: transparent; box-shadow: none; border: none; margin: 0; }

    # Current Input
    - type: markdown
      content: |
        <h3 style="margin: 12px 0 6px 0;">Current Guess</h3>
        <div style="background: var(--secondary-background-color); border: 2px dashed var(--divider-color); padding: 12px; border-radius: 6px; text-align: center; font-family: monospace; font-size: 20px; letter-spacing: 2px;">
        {%- set current = state_attr('sensor.ha_wordplay_game_state', 'current_input') -%}
        {{ current if current else "_ _ _ _ _" }}
        </div>
      card_mod:
        style: |
          ha-card { background: transparent; box-shadow: none; border: none; margin: 0; }

    # Hint Section (below current guess as requested)
    - type: markdown
      content: |
        <div style="background: var(--info-color); color: white; padding: 8px 12px; border-radius: 6px; margin: 8px 0;">
          <strong>💡 Hint:</strong>
          {%- set hint = state_attr('sensor.ha_wordplay_game_state', 'hint') -%}
          {{ hint if hint else "Start a game and click 'Get Hint' for clues!" }}
        </div>
      card_mod:
        style: |
          ha-card { background: transparent; box-shadow: none; border: none; margin: 0; }

    # Input Field
    - type: entities
      entities:
        - entity: text.ha_wordplay_guess_input
          name: "Type Your Guess"
          icon: mdi:keyboard
        - entity: select.ha_wordplay_word_length
          name: "Word Length"
          icon: mdi:numeric
      show_header_toggle: false
      card_mod:
        style: |
          ha-card { 
            background: var(--secondary-background-color); 
            border-radius: 6px; 
            margin: 8px 0;
          }

    # Controls - All 3 buttons in one row, much smaller
    - type: horizontal-stack
      cards:
        - type: button
          name: "Submit"
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
                border-radius: 6px;
                margin: 2px;
                height: 50px !important;
                font-size: 14px;
              }
        
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

### `ha_wordplay.make_guess`

Submit a guess for the current game.

**Parameters:**
- `guess` (required): Your word guess (must match current word length)

### `ha_wordplay.submit_guess`

Submit the current text input as a guess.

**No parameters required.**

### `ha_wordplay.get_hint`

Get a hint for the current word (based on dictionary definition).

**No parameters required.**

## 🌐 API Dependencies

This integration uses the following free APIs:

- **Random Word API**: `https://random-word-api.herokuapp.com/` - For generating random words
- **Free Dictionary API**: `https://dictionaryapi.dev/` - For word definitions and hints

Both APIs are free and require no authentication. The integration handles all API communication automatically.

## 🔒 Privacy & Data

- **No Data Collection**: Your games, scores, and guesses stay local to your Home Assistant instance
- **No User Accounts**: No registration or personal information required  
- **No External Storage**: All game data is stored locally in HA entities
- **UK English Focus**: Currently optimized for UK English dictionary

## 🚧 Development Status

**Current Version**: 0.2.0 (Beta)

**What's Working:**
- ✅ Core game logic (word generation, guess checking, hints)
- ✅ Custom text input and word length selector entities
- ✅ Service integration with Home Assistant
- ✅ Clean 2-row dashboard interface
- ✅ Live input preview
- ✅ API integration for words and definitions
- ✅ 5-8 letter word support

**Coming Soon:**
- 🔲 Enhanced UI styling and animations
- 🔲 Statistics tracking
- 🔲 Automatic dashboard creation

**Future Plans:**
- 🔲 Easy/Hard modes (with/without alphabet helper)
- 🔲 Multi-language support
- 🔲 Custom word lists
- 🔲 Achievement system
- 🔲 Difficulty levels

## 🐛 Known Issues

- Dashboard requires manual YAML configuration
- API failures may require game restart
- Debug sensor shows current word (development builds only)

## 🎮 Game Features

### Current Interface
- **Top Row**: Shows your latest guess with color-coded feedback
- **Bottom Row**: Shows what you're currently typing (live preview)
- **Dropdown**: Select word length (5, 6, 7, or 8 letters)
- **Text Input**: Type your guesses naturally
- **Clean Layout**: Everything in one organized dashboard

### Planned Enhancements
- **Easy Mode**: Alphabet helper showing used letters
- **Hard Mode**: No letter hints - memory challenge
- **Statistics**: Track wins, streaks, and performance
- **Themes**: Different color schemes and styles

## 🤝 Contributing

This is an open-source project! Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by the original Wordle game by Josh Wardle
- Uses the Random Word API for word generation
- Uses the Free Dictionary API for definitions
- Built for the Home Assistant community

## 📞 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/CBDesignS/ha-wordplay/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/CBDesignS/ha-wordplay/discussions)
- **Home Assistant Community**: Find help in the [HA Community Forum](https://community.home-assistant.io/)

---

**Note**: This integration is not affiliated with or endorsed by the original Wordle game or The New York Times. It is a custom implementation of a word guessing game for Home Assistant...
