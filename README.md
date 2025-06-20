# H.A WordPlay

🎮 **The Ultimate Wordle-style Integration for Home Assistant** 🎮

A revolutionary single-button word guessing game that brings the Wordle experience directly to your Home Assistant dashboard with zero configuration required!

## 🌟 Key Features

**🎯 Single Button Experience**
- **Zero YAML Configuration** - Just add one button entity to your dashboard
- **Rich More-Info Dialog** - Complete game interface in the entity popup
- **Professional UX** - Matches native Home Assistant integration patterns
- **Vacuum-Style Interface** - Familiar single-entity approach

**🛡️ Anti-Cheat Protection**
- **Smart Validation** - Prevents vowel dumping and unfair strategies
- **Balanced Gameplay** - Enforces realistic word patterns
- **Fair Play Rules** - Blocks common cheating techniques
- **Real-time Feedback** - Instant rule violation alerts

**🌐 Multi-API Reliability** 
- **3-Tier API System** - Primary + 2 backup word sources
- **Automatic Failover** - Seamless switching when APIs are down
- **Local Fallbacks** - Built-in word lists for offline play
- **International Ready** - Framework for multiple languages

**⚡ Advanced Game Logic**
- **Dynamic Difficulty** - Guess count equals word length (5-8 letters)
- **Wordle-Style Feedback** - 🟦 Correct, 🟥 Partial, ⬜ Absent
- **Smart Hints** - Dictionary-powered clues
- **Live Input Preview** - See your guess as you type

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS → Integrations
2. Click ⋮ → Custom repositories  
3. Add: `https://github.com/CBDesignS/ha-wordplay`
4. Category: Integration
5. Install "H.A WordPlay"
6. Restart Home Assistant

### Manual Installation

1. Download latest release
2. Copy `custom_components/ha_wordplay/` to your HA directory
3. Restart Home Assistant

## 🎯 Quick Start

**🎮 Single Entity Approach - No YAML Required!**

1. **Add Button to Dashboard**
   - Add entity: `button.ha_wordplay_game`
   - That's it! No YAML configuration needed

2. **Click for Rich Interface**
   - Click the button entity for full more-info popup
   - Complete game interface with live updates
   - All controls accessible from entity dialog

3. **Alternative: Individual Entities**
   - `select.ha_wordplay_word_length` - Choose 5-8 letters
   - `text.ha_wordplay_guess_input` - Type your guesses
   - Use services: `ha_wordplay.new_game`, `ha_wordplay.submit_guess`

## 🎮 How to Play

### Game Rules
- **Word Length**: Choose 5, 6, 7, or 8 letters
- **Guess Limit**: Number of guesses equals word length
- **Valid Words**: Real English words with balanced letter patterns
- **Win Condition**: Guess the exact word within your attempts

### Color Feedback
- **🟦 Blue**: Correct letter in correct position
- **🟥 Red**: Correct letter in wrong position  
- **⬜ White**: Letter not in the word

### Anti-Cheat Rules
❌ **Blocked Strategies:**
- `AEIOU` - No pure vowel dumping
- `AAEIO` - Maximum 60% vowels allowed
- `AAAAB` - Need 2+ different consonants

✅ **Fair Examples:**
- `HOUSE`, `BOARD`, `STEAM`, `QUICK`

## 🔧 Services

### Core Services

**`ha_wordplay.new_game`**
```yaml
service: ha_wordplay.new_game
data:
  word_length: 6  # Optional: 5-8 letters
  language: en    # Optional: Future feature
```

**`ha_wordplay.submit_guess`**
```yaml
service: ha_wordplay.submit_guess
# Submits current text input automatically
```

**`ha_wordplay.make_guess`**
```yaml
service: ha_wordplay.make_guess
data:
  guess: "BOARD"
```

**`ha_wordplay.get_hint`**
```yaml
service: ha_wordplay.get_hint
# Gets dictionary-based hint for current word
```

## 🏗️ Created Entities

The integration automatically creates three entities:

- **`button.ha_wordplay_game`** - Main game interface
- **`text.ha_wordplay_guess_input`** - Text input for guesses  
- **`select.ha_wordplay_word_length`** - Word length selector (5-8)

**💡 Pro Tip:** Just add the button entity to your dashboard for the complete experience!

## 🌐 API & Reliability

### Multi-Tier API System
1. **Primary**: `random-word-api.herokuapp.com`
2. **Backup 1**: `random-word-api.vercel.app` 
3. **Backup 2**: `random-words-api.vercel.app`
4. **Local Fallback**: Built-in word lists for each length

### Dictionary Integration
- **Hints**: Free Dictionary API for word definitions
- **Smart Fallback**: Generic hints when dictionary unavailable
- **Definition Filtering**: Removes target word from hints

## 🎨 Dashboard Integration

### Method 1: Single Button (Recommended)
```yaml
type: entity
entity: button.ha_wordplay_game
```

### Method 2: Custom Card Layout
```yaml
type: entities
entities:
  - entity: button.ha_wordplay_game
    name: WordPlay Game
  - entity: select.ha_wordplay_word_length
    name: Word Length
  - entity: text.ha_wordplay_guess_input
    name: Your Guess
```

### Method 3: Grid Layout
```yaml
type: grid
cards:
  - type: entity
    entity: button.ha_wordplay_game
  - type: entity
    entity: text.ha_wordplay_guess_input
  - type: entity
    entity: select.ha_wordplay_word_length
```

## 🔒 Privacy & Security

- **No Data Collection** - Everything stays local to your HA instance
- **No Accounts Required** - Zero external authentication  
- **Secure Logging** - Debug logs never expose the target word
- **Local Fallbacks** - Works offline with built-in word lists

## 🚧 Version History

**v0.4.0 - Single Button Revolution** *(Current)*
- 🎯 Single button approach with rich more-info popup
- 🌐 Multi-API cascade system with automatic failover
- 🛡️ Advanced anti-cheat system with real-time validation
- ⚡ Zero YAML configuration required
- 🎮 Professional integration-style UX

**v0.3.0 - Multi-Entity Foundation**
- ✅ Text input and select entities
- ✅ Service-based architecture
- ✅ Basic game logic and validation

## 🎯 Game Strategy Tips

### Effective Starting Words
- **BOARD** - Good consonant/vowel balance
- **STEAM** - Tests common patterns
- **FLING** - Multiple consonant combinations
- **CHORE** - Balanced letter distribution

### Anti-Cheat Approved Tactics
- ✅ Use balanced vowel/consonant ratios
- ✅ Include multiple different consonants  
- ✅ Test common letter patterns (TH, ST, ING)
- ✅ Focus on real English words

## 🔮 Roadmap

**Coming Soon:**
- 📊 Statistics tracking and performance metrics
- 🏆 Achievement system and badges  
- 🎨 Enhanced UI animations and effects
- 🌍 Multi-language support (German, Spanish, French)

**Future Vision:**
- 🎮 Tournament and multiplayer modes
- 📚 Custom word lists and themed categories
- 🎓 Educational modes and difficulty levels
- 🔗 Integration with HA automations

## 🤝 Contributing

We welcome contributions! Areas of interest:

- **Language Packs** - Add support for other languages
- **UI Enhancements** - Improve visual experience
- **Game Modes** - Additional play styles
- **Performance** - Optimization and efficiency
- **Testing** - Edge cases and validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/CBDesignS/ha-wordplay/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CBDesignS/ha-wordplay/discussions)  
- **Community**: [Home Assistant Forum](https://community.home-assistant.io/)

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Josh Wardle's original Wordle
- Built for the Home Assistant community
- Uses Free Dictionary API and Random Word APIs
- Special thanks to HACS for distribution platform

---

**🎮 Ready to play? Install now and add `button.ha_wordplay_game` to your dashboard!** 

*Note: This integration is not affiliated with the original Wordle game or The New York Times.*
