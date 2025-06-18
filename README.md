# H.A WordPlay

A Wordle-style word guessing game integration for Home Assistant. Play directly from your HA dashboard with dynamically generated word puzzles!

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
