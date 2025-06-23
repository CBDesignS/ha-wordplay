# H.A WordPlay

![game panel](https://github.com/user-attachments/assets/34b4a7aa-6109-4ae9-831e-d87af7f541c5)


🎮 **The Ultimate Wordle-style Integration for Home Assistant** 🎮

A revolutionary HTML panel word guessing game that brings the complete Wordle experience directly to your Home Assistant sidebar with zero configuration required!

## 🌟 Key Features

**🎯 Modern HTML Panel Interface**
- **Zero Configuration** - Works immediately after installation
- **Sidebar Integration** - Native Home Assistant panel experience  
- **Responsive Design** - Perfect on desktop, tablet, and mobile
- **Theme Integration** - Automatically matches your HA theme (light/dark)

**🛡️ Advanced Anti-Cheat System**
- **Smart Validation** - Prevents vowel dumping and unrealistic guessing patterns
- **Fair Play Enforcement** - Blocks common cheating strategies like "AEIOU"
- **Balanced Word Requirements** - Ensures realistic letter combinations
- **Real-time Feedback** - Instant notifications for rule violations

**🌐 Bulletproof Reliability** 
- **Multi-API System** - 3-tier word generation with automatic failover
- **Smart Polling** - Intelligent refresh system with ban prevention
- **Offline Capability** - Built-in word lists when APIs unavailable
- **Connection Recovery** - Automatic reconnection handling

**⚡ Enhanced Gameplay**
- **Variable Difficulty** - 5, 6, 7, or 8-letter words
- **Smart Guess Limits** - Number of guesses equals word length
- **Wordle-Style Feedback** - 🔵 Correct • 🔴 Wrong position • ⚪ Not in word
- **Dictionary Hints** - AI-powered clues from real definitions
- **Live Input Preview** - See your guess as you type

## 🚀 Installation

### Via HACS (Recommended)

1. **Open HACS** → Integrations
2. **Click ⋮** → Custom repositories  
3. **Add Repository**: `https://github.com/CBDesignS/ha-wordplay`
4. **Category**: Integration
5. **Install** "H.A WordPlay"
6. **Restart** Home Assistant

### Manual Installation

1. Download the latest release
2. Copy `custom_components/ha_wordplay/` to your HA directory
3. Restart Home Assistant

## 🎯 Quick Start

**🎮 Instant Access - No Configuration Required!**

1. **After Installation** - The game automatically appears in your sidebar
2. **Click "🎮 WordPlay"** in the Home Assistant sidebar
3. **Start Playing** - Complete game interface loads immediately
4. **Choose Difficulty** - Select 5, 6, 7, or 8-letter words
5. **Make Guesses** - Type and submit your guesses
6. **Get Hints** - Click for dictionary-powered clues

**That's it!** No YAML configuration, no dashboard setup, no entity configuration required.

## 🎮 How to Play

### Game Rules
- **Word Length**: Choose between 5, 6, 7, or 8-letter words
- **Guess Limit**: Number of attempts equals word length (5 letters = 5 guesses)
- **Valid Words**: Real English words with balanced letter patterns
- **Win Condition**: Guess the exact word within your attempts

### Color Feedback System
- **🔵 Blue Tile**: Correct letter in correct position
- **🔴 Red Tile**: Correct letter in wrong position  
- **⚪ White Tile**: Letter not in the word

### Anti-Cheat Rules
The game enforces fair play by blocking unrealistic guessing strategies:

❌ **Blocked Examples:**
- `AEIOU` - Pure vowel dumping
- `AAEIO` - Too many vowels (>60%)
- `AAAAB` - Need 2+ different consonants

✅ **Fair Examples:**
- `HOUSE`, `BOARD`, `STEAM`, `QUICK` - Balanced letter patterns

## 🔧 Advanced Features

### Built-in Services

The integration provides optional services for automation:

**`ha_wordplay.new_game`**
```yaml
service: ha_wordplay.new_game
data:
  word_length: 6  # Optional: 5-8 letters
```

**`ha_wordplay.submit_guess`**
```yaml
service: ha_wordplay.submit_guess
# Submits current input automatically
```

**`ha_wordplay.get_hint`**
```yaml
service: ha_wordplay.get_hint
# Gets dictionary-based hint
```

### Created Entities

The integration creates these entities for advanced users:

- **`button.ha_wordplay_game`** - Game state and rich attributes
- **`text.ha_wordplay_guess_input`** - Text input for guesses  
- **`select.ha_wordplay_word_length`** - Word length selector

**💡 Pro Tip:** The HTML panel provides the complete experience - entities are optional for advanced automation only.

## 🌐 Reliability & Performance

### Multi-Tier Word Generation
1. **Primary API**: `random-word-api.herokuapp.com`
2. **Backup API**: `random-word-api.vercel.app` 
3. **Fallback API**: `random-words-api.vercel.app`
4. **Local Words**: Built-in word lists (400+ words) for offline play

### Smart Connection Management
- **Authentication Protection** - Prevents API bans from invalid requests
- **Intelligent Polling** - Adaptive refresh rates based on activity
- **Error Recovery** - Automatic backoff and reconnection handling
- **Activity Tracking** - Reduces polling during inactivity to prevent bans

### Dictionary Integration
- **Hint System**: Free Dictionary API for word definitions
- **Smart Filtering**: Removes target word from hints to prevent spoilers
- **Fallback Hints**: Generic clues when dictionary unavailable

## 🎨 Interface Features

### Responsive Design
- **Desktop**: Full-featured interface with optimal tile sizing
- **Tablet**: Adapted layout with touch-friendly controls
- **Mobile**: Compact view with stacked buttons and smaller tiles

### Theme Integration
- **Auto-Detection**: Automatically matches Home Assistant theme
- **Light Mode**: Clean, bright interface
- **Dark Mode**: Easy-on-eyes dark interface
- **Custom Themes**: Adapts to custom HA theme colors

### Real-time Updates
- **Live Input**: See your guess forming as you type
- **Instant Feedback**: Immediate color coding after each guess
- **Connection Status**: Always know your connection state
- **Game Messages**: Clear status updates and error messages

## 🔒 Privacy & Security

- **No Data Collection** - Everything stays local to your HA instance
- **No External Accounts** - Zero registration or authentication required  
- **Secure Logging** - Debug logs never expose target words
- **Local Fallbacks** - Works completely offline with built-in word lists
- **Safe API Usage** - Smart request limiting prevents IP bans

## 🚧 System Requirements

- **Home Assistant**: 2023.1.0 or newer
- **Browser**: Modern browser with JavaScript enabled
- **Network**: Internet connection for word APIs (optional - works offline)
- **Resources**: Minimal - lightweight HTML interface

## 🎯 Game Strategy Tips

### Effective Starting Words
- **BOARD** - Excellent consonant/vowel balance
- **STEAM** - Tests common letter patterns
- **FLING** - Multiple consonant combinations
- **CHORE** - Balanced letter distribution

### Winning Strategies
- ✅ Use words with balanced vowel/consonant ratios
- ✅ Include multiple different consonants  
- ✅ Test common letter patterns (TH, ST, ING)
- ✅ Focus on real English words
- ✅ Use hints strategically when stuck

## 🔮 Version History

**v1.0.0 - HTML Panel Revolution** *(Current)*
- 🎯 Complete HTML panel interface with sidebar integration
- 🌐 Multi-API cascade system with bulletproof failover
- 🛡️ Advanced anti-cheat system with real-time validation
- ⚡ Zero configuration required - works immediately
- 🎮 Professional game interface with responsive design
- 🔒 Smart authentication and connection management

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **Language Support** - Add word APIs for other languages
- **UI Enhancements** - Improve visual experience and animations
- **Game Modes** - Additional play styles and difficulty options
- **Performance** - Optimization and efficiency improvements
- **Testing** - Edge cases and cross-browser compatibility

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

**🎮 Ready to play? Install now and check your Home Assistant sidebar for the WordPlay panel!** 


*Note: This integration is not affiliated with the original Wordle game or The New York Times.* 
** It is My take upon a word guessing game, My code, My icon, My Hard Work.. ** 
   ps. I never wrote a single line of code. I challenged myself to use online Ai to do everything.
   all of the code was generated by Anthropic Claude Sonnet 4. We fell out quite a few times but here it is.

