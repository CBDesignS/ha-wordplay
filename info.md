# H.A WordPlay

A Wordle-style word guessing game integration for Home Assistant.

## Features

- Play word guessing games directly from your HA dashboard
- Dynamic word generation with 4-8 letter words
- Smart hints from dictionary definitions  
- Wordle-style color-coded feedback
- Zero configuration required
- Completely standalone - no external accounts or data collection

## Installation

1. Install via HACS
2. Restart Home Assistant
3. Add dashboard cards to start playing

## Usage

Use the provided services to:
- Start new games: `ha_wordplay.new_game`
- Make guesses: `ha_wordplay.make_guess` 
- Get hints: `ha_wordplay.get_hint`

Perfect for family game time integrated into your smart home!
