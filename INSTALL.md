# H.A WordPlay Installation Guide

[← Back to README](README.md)

This guide will walk you through installing and configuring H.A WordPlay in Home Assistant.

## 📋 Prerequisites

- Home Assistant 2023.1.0 or newer
- HACS installed (recommended) or manual installation capability
- Admin access to Home Assistant

## 🚀 Step 1: Install the Integration

### Via HACS (Recommended)

1. **Open HACS** in Home Assistant
2. **Go to Integrations**
3. **Click the ⋮ menu** → Custom repositories  
4. **Add Repository**: `https://github.com/CBDesignS/ha-wordplay`
5. **Category**: Integration
6. **Click Add**
7. **Find "H.A WordPlay"** in the integration list
8. **Click Install**
9. **Restart Home Assistant**

### Manual Installation

1. **Download** the latest release from GitHub
2. **Extract** the files
3. **Copy** `custom_components/ha_wordplay/` to your Home Assistant `custom_components` directory
4. **Restart** Home Assistant

## 🔑 Step 2: Generate Long-Lived Access Token

**⚠️ This step is required for the integration to work securely.**

1. **Go to your Home Assistant Profile**
   - Click your profile picture in the bottom left
   - Select "Profile"

2. **Navigate to Security Tab**
   - Scroll down to "Long-lived access tokens"

3. **Create New Token**
   - Click "Create Token"
   - Enter a name like "WordPlay Game"
   - Click "OK"

4. **Copy the Token**
   - **⚠️ IMPORTANT**: Copy the token immediately - you won't see it again!
   - Save it temporarily in a secure location

## ⚙️ Step 3: Add the Integration

1. **Go to Settings** → **Devices & Services**

2. **Add Integration**
   - Click "+ Add Integration"
   - Search for "H.A WordPlay"
   - Click on it

3. **Configure Integration**
   - **Paste your access token** in the "Long-lived Access Token" field
   - **Choose difficulty level**:
     - **Easy**: Hint shown before guessing
     - **Normal**: Hints available on request  
     - **Hard**: No hints available
   - **Click Submit**

4. **Confirm Setup**
   - The integration should be added successfully
   - You'll see "WordPlay (Normal Mode)" or similar in your integrations list

## 🎮 Step 4: Access the Game

1. **Check the Sidebar**
   - Look for "🎮 WordPlay" in your Home Assistant sidebar
   - It should appear automatically after setup

2. **Start Playing**
   - Click the WordPlay panel
   - Select your preferred word length (5-8 letters)
   - Click "New Game" to start
   - Type your guesses and click "Submit Guess"

## 🔧 Step 5: Optional Configuration

### Change Settings Later

1. **Go to Settings** → **Devices & Services**
2. **Find H.A WordPlay** in your integrations
3. **Click Configure** to modify:
   - Difficulty level
   - Access token (if needed)

### Advanced Users: Entity Control

The integration creates these entities for automation:
- `button.ha_wordplay_game` - Main game control
- `text.ha_wordplay_guess_input` - Text input field
- `select.ha_wordplay_word_length` - Word length selector
- `sensor.ha_wordplay_game_state` - Game state information
- `sensor.ha_wordplay_guesses` - Guess history

## 🚨 Troubleshooting

### Token Issues
- **"Invalid token"**: Generate a new long-lived token and try again
- **"Insufficient permissions"**: Ensure the token has full access (default for long-lived tokens)

### Connection Issues
- **Game won't load**: Check that Home Assistant is accessible on your network
- **"Connection failed"**: Verify your access token is correct

### Game Issues
- **Panel not appearing**: Restart Home Assistant after installation
- **Game not responding**: Check the integration is properly configured in Devices & Services

### Getting Help
- **Check logs**: Go to Settings → System → Logs for error messages
- **GitHub Issues**: [Report problems here](https://github.com/CBDesignS/ha-wordplay/issues)
- **Community Forum**: [Get help from other users](https://community.home-assistant.io/)

## 🔒 Security Notes

- **Token Storage**: Your access token is stored securely in Home Assistant's configuration
- **Local Operation**: All game data stays within your Home Assistant instance
- **No External Accounts**: No registration or external services required
- **API Calls**: Only makes calls to public word APIs for new words (optional - works offline)

## 🎯 Next Steps

Once installed and configured:

1. **Explore Difficulty Modes** - Try Easy mode for hints, Hard mode for challenge
2. **Test Different Word Lengths** - 5-8 letter words for variety
3. **Check Out Services** - Use `ha_wordplay.*` services for automation
4. **Customize Experience** - Game adapts to your Home Assistant theme

---

**🎮 Ready to play?** [Back to README](README.md) for gameplay tips and features!

**Having issues?** Check the troubleshooting section above or [open an issue](https://github.com/CBDesignS/ha-wordplay/issues) on GitHub.