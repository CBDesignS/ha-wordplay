# H.A WordPlay

<img width="804" height="620" alt="Landing" src="https://github.com/user-attachments/assets/d3afa712-5b70-4b1d-849f-f844bab97eb1" />

<img width="798" height="654" alt="Wordplay game play" src="https://github.com/user-attachments/assets/4814bcd6-6ca9-44a9-86b3-1d917d97a230" />

🎮 **The Ultimate Word Guessing Game Integration for Home Assistant** 🎮

A professional HTML panel word guessing game that brings the complete word puzzle experience directly to your Home Assistant sidebar!

## 🌟 Key Features

**🎯 Modern HTML Panel Interface**
- **Sidebar Integration** - Native Home Assistant panel experience  
- **Dynamic Responsive Design** - HTML panel that automatically resizes to different screen sizes
- **Multi-Device Perfect** - Optimized for desktop, tablet, and mobile experiences
- **Theme Integration** - Automatically matches your HA theme (light/dark)
- **Professional UI** - Clean, intuitive game interface

**🛡️ Advanced Anti-Cheat System**
- **Smart Validation** - Prevents vowel dumping and unrealistic guessing patterns
- **Fair Play Enforcement** - Blocks common cheating strategies like "AEIOU"
- **Balanced Word Requirements** - Ensures realistic letter combinations
- **Real-time Feedback** - Instant notifications for rule violations

**🌐 Bulletproof Reliability & Localization** 
- **Multi-API System** - 3-tier word generation with automatic failover
- **Language Support** - Currently English (GB) with automatic locale detection
- **Expandable Languages** - Framework ready for additional language APIs
- **Offline Capability** - Built-in word lists when APIs unavailable
- **Connection Recovery** - Automatic reconnection handling
- **Smart Polling** - Intelligent refresh system

**⚡ Enhanced Gameplay**
- **Variable Difficulty** - Easy, Normal, or Hard modes
- **Multiple Word Lengths** - 5, 6, 7, or 8-letter words
- **Smart Guess Limits** - Number of guesses equals word length
- **Color-Coded Feedback** - 🔵 Correct • 🔴 Wrong position • ⚪ Not in word
- **Dictionary Hints** - AI-powered clues from real definitions

## 🚀 Installation & Setup

**⚠️ Configuration Required:** This integration requires a long-lived access token for secure operation.

### [📖 Complete Installation Guide →](INSTALL.md)

**Quick Overview:**
1. Install via HACS or manually
2. Generate a long-lived access token in HA
3. Add integration via Settings → Devices & Services
4. Enter your Long Lived token to enable authentication service and validate the connection
5. Choose the users you want to give access to from the drop down box and submit to save.
6. Access game from sidebar

## 🎮 How to Play

### Game Rules
- **Word Length**: Choose between 5, 6, 7, or 8-letter words
- **Guess Limit**: Number of attempts equals word length
- **Valid Words**: Real English words with balanced letter patterns
- **Win Condition**: Guess the exact word within your attempts

### Color Feedback System
- **🔵 Blue Tile**: Correct letter in correct position
- **🔴 Red Tile**: Correct letter in wrong position  
- **⚪ White Tile**: Letter not in the word

### Difficulty Modes
- **Easy**: Hints shown before guessing
- **Normal**: Hints available on request
- **Hard**: No hints available

### Anti-Cheat Rules
The game enforces fair play by blocking unrealistic strategies:

❌ **Blocked Examples:** `AEIOU`, `AAEIO`, `AAAAB`
✅ **Fair Examples:** `HOUSE`, `BOARD`, `STEAM`, `QUICK`

## 🔧 Advanced Features

### Built-in Services
Optional services for automation enthusiasts:

```yaml
# Start new game
service: ha_wordplay.new_game
data:
  word_length: 6

# Submit current guess
service: ha_wordplay.submit_guess

# Get hint
service: ha_wordplay.get_hint
```

### Created Entities
- **`button.ha_wordplay_game`** - Game state and rich attributes
- **`text.ha_wordplay_guess_input`** - Text input for guesses  
- **`select.ha_wordplay_word_length`** - Word length selector

💡 **The HTML panel provides the complete experience** - entities are optional for advanced automation only.

## 🎯 Game Strategy Tips

### Effective Starting Words
- **BOARD** - Excellent consonant/vowel balance
- **STEAM** - Tests common letter patterns
- **FLING** - Multiple consonant combinations
- **CHORE** - Balanced letter distribution

### Winning Strategies
- ✅ Use balanced vowel/consonant ratios
- ✅ Include multiple different consonants  
- ✅ Test common letter patterns (TH, ST, ING)
- ✅ Focus on real English words
- ✅ Use hints strategically when stuck

## 🌐 Reliability Features

### Multi-Tier Word Generation
1. **Primary API**: `random-word-api.herokuapp.com`
2. **Backup API**: `random-word-api.vercel.app` 
3. **Fallback API**: `random-words-api.vercel.app`
4. **Local Words**: Built-in word lists (400+ words) for offline play

### Smart Connection Management
- **Authentication Protection** - Secure token-based access
- **Intelligent Polling** - Adaptive refresh rates
- **Error Recovery** - Automatic backoff and reconnection
- **Activity Tracking** - Optimized performance

## 🔒 Privacy & Security

- **No Data Collection** - Everything stays local to your HA instance
- **No External Accounts** - Zero registration required  
- **Secure Token Authentication** - Protected API access
- **Local Fallbacks** - Works completely offline
- **Safe API Usage** - Smart request limiting

## 🚧 System Requirements

- **Home Assistant**: 2023.1.0 or newer
- **Browser**: Modern browser with JavaScript enabled
- **Network**: Internet connection for word APIs (optional)
- **Configuration**: Long-lived access token required

## 🔮 Planned Updates

### Language Expansion
- **Spanish (ES)** - Add Spanish word APIs and localization
- **French (FR)** - French dictionary and word generation support
- **German (DE)** - German language integration
- **Dutch (NL)** - Netherlands localization
- **Italian (IT)** - Italian word support
- **Portuguese (PT)** - Portuguese language addition

*We welcome community contributions for additional language APIs! Character-based languages (Chinese, Japanese, etc.) are not planned due to gameplay mechanics.*

### Feature Roadmap
- **Custom Word Lists** - User-defined word collections
- **Multiplayer Modes** - Family tournaments and challenges
- **Advanced Themes** - More visual customization options
- **Sound Effects** - Optional audio feedback (respects HA quiet hours)

**Want to help?** [Contribute language APIs or suggest features!](https://github.com/CBDesignS/ha-wordplay/discussions)

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **Language Support** - Add word APIs for other languages
- **UI Enhancements** - Improve visual experience and animations
- **Game Modes** - Additional play styles and difficulty options
- **Performance** - Optimization and efficiency improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/CBDesignS/ha-wordplay/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CBDesignS/ha-wordplay/discussions)  
- **Community**: [Home Assistant Forum](https://community.home-assistant.io/)

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Josh Wardle's original Wordle
- Built for the Home Assistant community
- Uses Free Dictionary API and multiple Random Word APIs
- Special thanks to HACS for distribution support

---

**🎮 Ready to play?** [Follow the installation guide](INSTALL.md) to get started!

*Note: This integration is not affiliated with the original Wordle game or The New York Times.*
** It is My take upon a word guessing game, My code, My icon, My Hard Work.. ** 
   ps. I never wrote a single line of code. I challenged myself to use online Ai to do everything.
   all of the code was generated by Anthropic Claude Sonnet 4. We fell out quite a few times but here it is.

