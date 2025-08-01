# H.A WordPlay Installation Guide

[← Back to README](README.md)

This guide walks you through installing and configuring H.A WordPlay in Home Assistant using the UI and HACS.

## 📋 Prerequisites

- Home Assistant 2023.1.0 or newer  
- [HACS](https://hacs.xyz/) installed and working  
- Admin access to Home Assistant

## 🚀 Step 1: Install via HACS

1. Open **HACS** in Home Assistant  
2. Go to **Integrations**  
3. Click the **⋮ menu** → **Custom repositories**  
4. Add this repository URL:  
   **https://github.com/CBDesignS/ha-wordplay**  
5. Set category to **Integration** and click **Add**  
6. Find **H.A WordPlay** in the list and click **Install**  
7. Restart Home Assistant when prompted

## 🔑 Step 2: Generate a Long-Lived Access Token

> ⚠️ This token is required for the integration to connect securely.

1. Go to your **Home Assistant Profile**  
   (Click your user icon at the bottom left)  
2. Scroll to the **Security** section  
3. Click **Create Token** under Long-lived access tokens  
4. Name it something like `"WordPlay Game"`  
5. Click **OK**, then **copy the token immediately**  
   (you won't see it again!)  
6. Save it temporarily in a safe place

## ⚙️ Step 3: Add the Integration

1. Go to **Settings** → **Devices & Services**  
2. Click **+ Add Integration**  
3. Search for **H.A WordPlay** and click it

### Fill out the setup form:

<img width="431" height="326" alt="config1" src="https://github.com/user-attachments/assets/f1d0eb57-8661-47a2-a9e6-7c5a3091bc32" />

- **choose Manage Selected Users and press Submit**

- **Paste your access token in the Access Token Box**

<img width="424" height="329" alt="settings2" src="https://github.com/user-attachments/assets/b0dd3548-d5c9-490b-a0e0-6eb79e9981ac" />

- **Choose the players you want to let play the game**


<img width="377" height="522" alt="settings1" src="https://github.com/user-attachments/assets/862f5896-20f7-467e-a954-ef533a04871c" />

- Click **Submit** to finish  

Selecting Reset Game Statisatics then lets you reset any of the game player game stats. Lots of warning etc so you do NOT reset by accident.
ONLY users that can access the Devices & settings can peform stats reset so they should be safe from normal users etc.

## 🎮 Step 4: Access the Game

1. Look for **🎮 WordPlay** in the Home Assistant sidebar  
2. Click it to open the game panel
3. Choose the game difficulty level you want to play at
4. Choose a word length (5 to 8 letters)  
5. Click **Start Game** to begin
6. If you want to adjust in game audio just press the Audio Settings button to open a new window overlay,
7. If you need a hint in normal mode press the get hint button (hints auto enabled in easy mode, no hints in hard mode)
8. Type word guesses into the ENTER YOUR GUESSES box and click **Submit Guess or press enter/return on the keyboard or mobile device screen**


You can change your settings later at any time on the initial landing page:

### Advanced Users: Entity Control

The integration provides these entities for automations:

- `button.ha_wordplay_game` – Game control button  
- `text.ha_wordplay_guess_input` – Input field for guesses  
- `select.ha_wordplay_word_length` – Word length selector  
- `sensor.ha_wordplay_game_state` – Game status info  
- `sensor.ha_wordplay_guesses` – List of past guesses

## 🚨 Troubleshooting

### Token Problems

- **Invalid token** – Create a new long-lived token  
- **Insufficient permissions** – Tokens must have full access (default)

### Game Not Loading?

- Make sure Home Assistant is reachable on your network  
- Double-check your access token  
- Restart Home Assistant if the panel doesn't show up

### General Issues

- **Panel missing?** – Restart Home Assistant  
- **Game not responding?** – Recheck configuration under Devices & Services  
- **Still stuck?** – See the logs:  
  Go to **Settings** → **System** → **Logs**

### Still need help?

- Open a GitHub issue: [GitHub Issues](https://github.com/CBDesignS/ha-wordplay/issues)  
- Ask the community: [Home Assistant Forum](https://community.home-assistant.io/)

## 🔒 Security Notes

- Your access token is stored securely in Home Assistant  
- All gameplay happens inside your Home Assistant instance  
- No external accounts, no tracking  
- Word lookup uses a public word API (optional – works offline too)

## 🎯 Next Steps

- Try different difficulty modes for more challenge  
- Test 5–8 letter word lengths  
- Use `ha_wordplay.*` services for automations  
- Enjoy full integration with your Home Assistant theme

---

🎮 **Ready to play?** [Back to README](README.md) for gameplay tips and more features  
💬 **Need help?** Use the troubleshooting section above or [open an issue](https://github.com/CBDesignS/ha-wordplay/issues)
