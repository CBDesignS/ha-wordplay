H.A WordPlay Installation Guide

← Back to README

This guide walks you through installing and configuring H.A WordPlay in Home Assistant using HACS.
📋 Prerequisites

    Home Assistant 2023.1.0 or newer
    HACS installed and working
    Admin access to Home Assistant

🚀 Step 1: Install via HACS

    Open HACS in Home Assistant
    Go to Integrations
    Search for "H.A WordPlay"
    Click Install
    Restart Home Assistant when prompted

🔑 Step 2: Generate a Long-Lived Access Token

    ⚠️ This token is required for the integration to connect securely.

    Go to your Home Assistant Profile
    (Click your user icon at the bottom left)
    Scroll to the Security section
    Click Create Token under Long-lived access tokens
    Name it something like "WordPlay Game"
    Click OK, then copy the token immediately
    (you won't see it again!)
    Save it temporarily in a safe place

⚙️ Step 3: Add the Integration

    Go to Settings → Devices & Services
    Click + Add Integration
    Search for H.A WordPlay and click it

Fill out the setup form:
<img width="431" height="326" alt="config1" src="https://github.com/user-attachments/assets/f1d0eb57-8661-47a2-a9e6-7c5a3091bc32" />

    Enter your access token in the Access Token field

<img width="424" height="329" alt="settings2" src="https://github.com/user-attachments/assets/b0dd3548-d5c9-490b-a0e0-6eb79e9981ac" />

    Select the users you want to give game access to

<img width="377" height="522" alt="settings1" src="https://github.com/user-attachments/assets/862f5896-20f7-467e-a954-ef533a04871c" />

    Click Submit to finish

🎮 Step 4: Access the Game

    Look for 🎮 WordPlay in the Home Assistant sidebar
    Click it to open the game panel
    Choose your preferred difficulty level
    Choose a word length (5 to 8 letters)
    Click Start Game to begin
    Use the Audio Settings button to customize game sounds
    Get hints in Normal mode or challenge yourself in Hard mode
    Type your guesses and click Submit Guess or press Enter

🎯 Game Features
Multi-Language Support

The game automatically detects your language and supports:

    English - Full word lists and dictionary hints
    Spanish - Español word generation
    French - Français word support
    German - Deutsch word integration

Statistics Tracking

Your game statistics are automatically tracked including:

    Games played and won
    Win streaks and records
    Guess distribution patterns
    Total play time

Audio Experience

Customize your game sounds:

    Game event sounds (new game, win, lose)
    Letter feedback audio
    Volume control
    Individual sound toggles

🚨 Troubleshooting
Token Problems

    Invalid token – Create a new long-lived token
    Insufficient permissions – Tokens must have full access (default)

Game Not Loading?

    Make sure Home Assistant is reachable on your network
    Double-check your access token
    Restart Home Assistant if the panel doesn't show up

General Issues

    Panel missing? – Restart Home Assistant
    Game not responding? – Recheck configuration under Devices & Services
    Still stuck? – See the logs:
    Go to Settings → System → Logs

Still need help?

    Open a GitHub issue: GitHub Issues
    Ask the community: Home Assistant Forum

🔒 Security Notes

    Your access token is stored securely in Home Assistant
    All gameplay happens inside your Home Assistant instance
    No external accounts, no tracking
    Word lookup uses public APIs (optional – works offline too)

🎯 Next Steps

    Try different difficulty modes for more challenge
    Test all supported languages (English, Spanish, French, German)
    Experiment with 5–8 letter word lengths
    Check your statistics and aim for win streaks
    Customize audio settings to your preference

🎮 Ready to play? Back to README for gameplay tips and more features
💬 Need help? Use the troubleshooting section above or open an issue
