# H.A WordPlay

A Wordle-style word guessing game integration for Home Assistant. Play directly from your HA dashboard with dynamically generated word puzzles!

## 🎮 Features

- **Zero Configuration**: Install and play immediately - no setup required
- **Dynamic Word Generation**: Uses online APIs to fetch random words of your chosen length (4-8 letters)
- **Smart Hints**: Get contextual clues from word definitions
- **Wordle-Style Feedback**: Color-coded letter feedback (correct, partial, absent)
- **Multiple Game Lengths**: Choose words from 4 to 8 letters long
- **Unlimited Play**: Start new games whenever you want
- **Standalone**: No external servers, user accounts, or data collection

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations" 
3. Click the three dots (⋮) in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/yourusername/ha-wordplay`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "H.A WordPlay" and install
9. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/ha_wordplay` folder to your HA `custom_components` directory
3. Restart Home Assistant

## 🎯 How to Play

### Starting a Game

Use the service call to start a new game:

```yaml
service: ha_wordplay.new_game
data:
  word_length: 5  # Choose 4-8 letters
```

### Making Guesses

Submit your word guesses:

```yaml
service: ha_wordplay.make_guess
data:
  guess: "CRANE"
```

### Getting Hints

Need help? Get a hint:

```yaml
service: ha_wordplay.get_hint
```

## 📊 Game Entities

The integration creates several entities you can use in your dashboard:

- `sensor.ha_wordplay_game_state` - Current game status (idle/playing/won/lost)
- `sensor.ha_wordplay_guesses` - Your guesses and their results
- `sensor.ha_wordplay_debug` - Debug info (development only)

## 🎨 Dashboard Integration

### Basic Dashboard Card Example

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: call-service
          service: ha_wordplay.new_game
          data:
            word_length: 5
        name: "New 5-Letter Game"
      - type: button
        tap_action:
          action: call-service
          service: ha_wordplay.get_hint
        name: "Get Hint"
  
  - type: entities
    entities:
      - sensor.ha_wordplay_game_state
      - sensor.ha_wordplay_guesses
```

### Advanced Template Card (Coming Soon)

A dynamic template card that generates the proper grid layout based on word length and provides visual feedback is in development.

## 🔧 Services

### `ha_wordplay.new_game`

Start a new word guessing game.

**Parameters:**
- `word_length` (required): Number of letters (4-8)

### `ha_wordplay.make_guess`

Submit a guess for the current game.

**Parameters:**
- `guess` (required): Your word guess (must match current word length)

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

**Current Version**: 0.1.0 (Alpha)

**What's Working:**
- ✅ Core game logic (word generation, guess checking, hints)
- ✅ Service integration with Home Assistant
- ✅ Basic entity state management
- ✅ API integration for words and definitions

**Coming Soon:**
- 🔲 Dynamic dashboard card with visual grid
- 🔲 Color-coded guess feedback display
- 🔲 Enhanced UI components
- 🔲 Statistics tracking

**Future Plans:**
- 🔲 Multi-language support
- 🔲 Difficulty levels
- 🔲 Custom word lists
- 🔲 Achievement system

## 🐛 Known Issues

- Dashboard integration requires manual YAML configuration
- Limited error handling for API failures
- Debug sensor exposes current word (will be removed in production)

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

- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/ha-wordplay/issues)
- **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/yourusername/ha-wordplay/discussions)
- **Home Assistant Community**: Find help in the [HA Community Forum](https://community.home-assistant.io/)

---

**Note**: This integration is not affiliated with or endorsed by the original Wordle game or The New York Times.
