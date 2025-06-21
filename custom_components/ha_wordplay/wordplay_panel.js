/**
 * H.A WordPlay Panel - Full Page Game Interface
 * Standalone panel for beautiful WordPlay experience
 */

import { LitElement, html, css } from "lit";

class WordPlayPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
      _gameState: { type: Object },
      _currentInput: { type: String },
      _wordLength: { type: Number },
      _isSubmitting: { type: Boolean },
    };
  }

  constructor() {
    super();
    this._currentInput = "";
    this._wordLength = 5;
    this._isSubmitting = false;
    this._gameState = {
      state: "idle",
      guesses: [],
      guessResults: [],
      hint: "",
      message: "",
      messageType: "info",
    };
  }

  connectedCallback() {
    super.connectedCallback();
    this._updateGameState();
    // Set up polling for game state updates
    this._pollInterval = setInterval(() => this._updateGameState(), 1000);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this._pollInterval) {
      clearInterval(this._pollInterval);
    }
  }

  updated(changedProps) {
    if (changedProps.has("hass")) {
      this._updateGameState();
    }
  }

  _updateGameState() {
    if (!this.hass) return;

    // Get game data from button entity attributes
    const buttonEntity = this.hass.states["button.ha_wordplay_game"];
    if (buttonEntity) {
      const attrs = buttonEntity.attributes;
      this._gameState = {
        state: attrs.game_status || "Ready to Play",
        guesses: attrs.guess_history || [],
        guessResults: attrs.guess_results || [],
        hint: attrs.hint || "",
        message: attrs.last_message || "",
        messageType: attrs.message_type || "info",
        wordLength: attrs.word_length || 5,
        guessesRemaining: attrs.guesses_remaining || 5,
        currentInput: attrs.current_input || "",
      };
    }

    // Get current input from text entity
    const textEntity = this.hass.states["text.ha_wordplay_guess_input"];
    if (textEntity) {
      this._currentInput = textEntity.state || "";
    }

    // Get word length from select entity
    const selectEntity = this.hass.states["select.ha_wordplay_word_length"];
    if (selectEntity) {
      this._wordLength = parseInt(selectEntity.state) || 5;
    }
  }

  _callService(service, data = {}) {
    return this.hass.callService("ha_wordplay", service, data);
  }

  async _startNewGame() {
    this._isSubmitting = true;
    try {
      await this._callService("new_game", { word_length: this._wordLength });
    } catch (error) {
      console.error("Error starting new game:", error);
    } finally {
      this._isSubmitting = false;
    }
  }

  async _submitGuess() {
    if (!this._currentInput || this._currentInput.length !== this._wordLength) {
      this._showInputError();
      return;
    }

    this._isSubmitting = true;
    try {
      await this._callService("submit_guess");
      // Clear input after successful submission
      await this.hass.callService("text", "set_value", {
        entity_id: "text.ha_wordplay_guess_input",
        value: "",
      });
    } catch (error) {
      console.error("Error submitting guess:", error);
    } finally {
      this._isSubmitting = false;
    }
  }

  async _getHint() {
    try {
      await this._callService("get_hint");
    } catch (error) {
      console.error("Error getting hint:", error);
    }
  }

  async _changeWordLength(length) {
    this._wordLength = length;
    try {
      await this.hass.callService("select", "select_option", {
        entity_id: "select.ha_wordplay_word_length",
        option: length.toString(),
      });
    } catch (error) {
      console.error("Error changing word length:", error);
    }
  }

  _onInputChange(event) {
    const value = event.target.value.toUpperCase().slice(0, this._wordLength);
    this.hass.callService("text", "set_value", {
      entity_id: "text.ha_wordplay_guess_input",
      value: value,
    });
  }

  _onKeyPress(event) {
    if (event.key === "Enter" && this._currentInput.length === this._wordLength) {
      this._submitGuess();
    }
  }

  _showInputError() {
    const inputField = this.shadowRoot.querySelector(".input-field");
    if (inputField) {
      inputField.classList.add("error");
      setTimeout(() => inputField.classList.remove("error"), 500);
    }
  }

  _renderGameGrid() {
    const gridSize = this._wordLength;
    const guesses = this._gameState.guesses || [];
    const results = this._gameState.guessResults || [];

    return html`
      <div
        class="game-grid"
        style="grid-template-columns: repeat(${gridSize}, 1fr); grid-template-rows: repeat(${gridSize}, 1fr);"
      >
        ${Array(gridSize)
          .fill()
          .map((_, rowIndex) =>
            Array(gridSize)
              .fill()
              .map((_, colIndex) => {
                const guess = guesses[rowIndex];
                const result = results[rowIndex];
                const letter = guess ? guess[colIndex] : "";
                const status = result ? result[colIndex] : "";

                // Show current input in active row
                let displayLetter = letter;
                let tileClass = "game-tile";

                if (!letter && rowIndex === guesses.length && this._currentInput) {
                  displayLetter = this._currentInput[colIndex] || "";
                  if (displayLetter) tileClass += " filled";
                } else if (letter) {
                  tileClass += ` filled ${status}`;
                }

                return html`<div class="${tileClass}">${displayLetter}</div>`;
              })
          )}
      </div>
    `;
  }

  _renderWordLengthSelector() {
    return html`
      <div class="word-length-selector">
        <span>Word Length:</span>
        ${[5, 6, 7, 8].map(
          (length) => html`
            <button
              class="length-button ${this._wordLength === length ? "active" : ""}"
              @click=${() => this._changeWordLength(length)}
              ?disabled=${this._gameState.state.includes("Playing")}
            >
              ${length}
            </button>
          `
        )}
      </div>
    `;
  }

  render() {
    const isPlaying = this._gameState.state.includes("Playing");
    const isGameOver = this._gameState.state.includes("Won") || this._gameState.state.includes("Game Over");

    return html`
      <div class="wordplay-panel">
        <div class="game-container">
          <div class="game-header">
            <h1 class="game-title">🎮 WordPlay</h1>
            <p class="game-status">${this._gameState.state}</p>
            ${!isPlaying ? this._renderWordLengthSelector() : ""}
          </div>

          <div class="game-content">
            ${this._renderGameGrid()}

            <div class="game-input">
              <input
                type="text"
                class="input-field"
                placeholder="Type your guess here..."
                .value=${this._currentInput}
                maxlength=${this._wordLength}
                @input=${this._onInputChange}
                @keypress=${this._onKeyPress}
                ?disabled=${!isPlaying || this._isSubmitting}
                autofocus
              />

              <div class="action-buttons">
                ${isPlaying
                  ? html`
                      <button
                        class="action-button primary"
                        @click=${this._submitGuess}
                        ?disabled=${this._isSubmitting || this._currentInput.length !== this._wordLength}
                      >
                        ${this._isSubmitting ? "Submitting..." : "Submit Guess"}
                      </button>
                      <button class="action-button secondary" @click=${this._getHint} ?disabled=${this._isSubmitting}>
                        💡 Get Hint
                      </button>
                    `
                  : ""}

                <button
                  class="action-button ${isPlaying ? "secondary" : "primary"}"
                  @click=${this._startNewGame}
                  ?disabled=${this._isSubmitting}
                >
                  ${isGameOver ? "🎮 Play Again" : "🎲 New Game"}
                </button>
              </div>
            </div>

            ${this._gameState.hint
              ? html`
                  <div class="game-info">
                    <div class="hint-text">💡 ${this._gameState.hint}</div>
                  </div>
                `
              : ""}

            ${this._gameState.message
              ? html`
                  <div class="message ${this._gameState.messageType}">
                    ${this._gameState.message}
                  </div>
                `
              : ""}

            <div class="instructions">
              <strong>How to play:</strong> 🟦 Correct position • 🟥 Wrong position • ⬜ Not in word
            </div>
          </div>
        </div>
      </div>
    `;
  }

  static get styles() {
    return css`
      :host {
        --tile-correct: #2196f3;
        --tile-partial: #f44336;
        --tile-absent: #ffffff;
        --tile-empty: var(--card-background-color, #ffffff);
        --tile-border: var(--divider-color, #e0e0e0);
        --tile-size: 60px;
        --tile-gap: 6px;
        display: block;
        width: 100%;
        height: 100vh;
        overflow-y: auto;
      }

      .wordplay-panel {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        min-height: 100vh;
        background: var(--primary-background-color);
        padding: 20px;
        box-sizing: border-box;
      }

      .game-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        max-width: 600px;
        width: 100%;
        gap: 24px;
        background: var(--card-background-color);
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--divider-color);
      }

      .game-header {
        text-align: center;
        width: 100%;
      }

      .game-title {
        font-size: 48px;
        font-weight: bold;
        color: var(--primary-text-color);
        margin: 0 0 12px 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
      }

      .game-status {
        font-size: 20px;
        color: var(--secondary-text-color);
        margin: 0 0 20px 0;
        font-weight: 500;
      }

      .word-length-selector {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin: 12px 0;
        flex-wrap: wrap;
      }

      .word-length-selector span {
        font-size: 16px;
        font-weight: 600;
        color: var(--primary-text-color);
      }

      .length-button {
        padding: 12px 20px;
        border: 2px solid var(--primary-color);
        background: var(--card-background-color);
        color: var(--primary-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
        font-size: 16px;
        min-width: 50px;
      }

      .length-button.active {
        background: var(--primary-color);
        color: white;
        transform: scale(1.05);
      }

      .length-button:hover:not(:disabled) {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
      }

      .length-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }

      .game-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 24px;
        width: 100%;
      }

      .game-grid {
        display: grid;
        gap: var(--tile-gap);
        justify-content: center;
        margin: 20px 0;
        transition: all 0.3s ease;
      }

      .game-tile {
        width: var(--tile-size);
        height: var(--tile-size);
        border: 3px solid var(--tile-border);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        background: var(--tile-empty);
        color: var(--primary-text-color);
        transition: all 0.4s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      .game-tile.filled {
        background: var(--secondary-background-color);
        border-color: var(--secondary-text-color);
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
      }

      .game-tile.correct {
        background: var(--tile-correct);
        color: white;
        border-color: var(--tile-correct);
        animation: flip 0.6s ease;
        box-shadow: 0 8px 16px rgba(33, 150, 243, 0.3);
      }

      .game-tile.partial {
        background: var(--tile-partial);
        color: white;
        border-color: var(--tile-partial);
        animation: flip 0.6s ease;
        box-shadow: 0 8px 16px rgba(244, 67, 54, 0.3);
      }

      .game-tile.absent {
        background: var(--tile-absent);
        color: var(--primary-text-color);
        border-color: var(--tile-border);
        animation: flip 0.6s ease;
        opacity: 0.7;
      }

      @keyframes flip {
        0% {
          transform: rotateY(0deg) scale(1);
        }
        50% {
          transform: rotateY(90deg) scale(1.1);
        }
        100% {
          transform: rotateY(0deg) scale(1);
        }
      }

      @keyframes shake {
        0%, 100% {
          transform: translateX(0);
        }
        25% {
          transform: translateX(-8px);
        }
        75% {
          transform: translateX(8px);
        }
      }

      .game-input {
        width: 100%;
        max-width: 500px;
        text-align: center;
      }

      .input-field {
        width: 100%;
        padding: 20px;
        font-size: 24px;
        text-align: center;
        text-transform: uppercase;
        border: 3px solid var(--tile-border);
        border-radius: 16px;
        margin-bottom: 20px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        transition: all 0.3s ease;
        letter-spacing: 3px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      .input-field:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2), 0 8px 16px rgba(0, 0, 0, 0.15);
        transform: scale(1.02);
      }

      .input-field.error {
        border-color: var(--tile-partial);
        animation: shake 0.6s ease;
        box-shadow: 0 0 0 4px rgba(244, 67, 54, 0.2);
      }

      .action-buttons {
        display: flex;
        gap: 16px;
        justify-content: center;
        flex-wrap: wrap;
      }

      .action-button {
        padding: 16px 32px;
        border: none;
        border-radius: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        min-width: 160px;
        font-size: 18px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
      }

      .action-button.primary {
        background: var(--primary-color);
        color: white;
      }

      .action-button.secondary {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
        border: 3px solid var(--divider-color);
      }

      .action-button:hover:not(:disabled) {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
      }

      .action-button.primary:hover:not(:disabled) {
        box-shadow: 0 12px 24px rgba(33, 150, 243, 0.4);
      }

      .action-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }

      .game-info {
        text-align: center;
        padding: 20px;
        background: var(--secondary-background-color);
        border-radius: 16px;
        max-width: 500px;
        margin: 12px 0;
        border-left: 6px solid var(--primary-color);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      .hint-text {
        font-style: italic;
        color: var(--secondary-text-color);
        font-size: 18px;
        line-height: 1.4;
      }

      .message {
        text-align: center;
        padding: 16px 24px;
        border-radius: 16px;
        margin: 12px 0;
        font-weight: 600;
        font-size: 18px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      .message.success {
        background: rgba(76, 175, 80, 0.15);
        color: #4caf50;
        border: 3px solid rgba(76, 175, 80, 0.3);
      }

      .message.error {
        background: rgba(244, 67, 54, 0.15);
        color: var(--tile-partial);
        border: 3px solid rgba(244, 67, 54, 0.3);
      }

      .message.info {
        background: rgba(33, 150, 243, 0.15);
        color: var(--primary-color);
        border: 3px solid rgba(33, 150, 243, 0.3);
      }

      .instructions {
        text-align: center;
        font-size: 16px;
        color: var(--secondary-text-color);
        margin-top: 20px;
        padding: 16px;
        background: rgba(0, 0, 0, 0.05);
        border-radius: 12px;
        line-height: 1.4;
      }

      /* Mobile responsiveness */
      @media (max-width: 768px) {
        :host {
          --tile-size: 50px;
          --tile-gap: 4px;
        }

        .wordplay-panel {
          padding: 12px;
        }

        .game-container {
          padding: 20px;
          margin: 0;
        }

        .game-title {
          font-size: 36px;
        }

        .game-status {
          font-size: 18px;
        }

        .input-field {
          font-size: 20px;
          padding: 16px;
        }

        .action-buttons {
          flex-direction: column;
          align-items: center;
        }

        .action-button {
          width: 100%;
          max-width: 320px;
        }
      }

      @media (max-width: 480px) {
        :host {
          --tile-size: 45px;
          --tile-gap: 3px;
        }

        .game-title {
          font-size: 28px;
        }

        .game-status {
          font-size: 16px;
        }

        .input-field {
          font-size: 18px;
          padding: 14px;
        }

        .action-button {
          font-size: 16px;
          padding: 14px 24px;
        }
      }

      /* Dark mode adjustments */
      @media (prefers-color-scheme: dark) {
        :host {
          --tile-absent: #424242;
        }

        .game-container {
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
      }

      /* Landscape mode adjustments */
      @media (max-height: 600px) and (orientation: landscape) {
        .wordplay-panel {
          padding: 12px;
        }

        .game-container {
          padding: 20px;
          max-width: 800px;
        }

        .game-content {
          flex-direction: row;
          flex-wrap: wrap;
          justify-content: center;
          align-items: flex-start;
        }

        .game-grid {
          margin: 0;
        }

        .game-input {
          max-width: 300px;
        }
      }
    `;
  }
}

// Define the custom element
customElements.define("wordplay-panel", WordPlayPanel);

// Wait for Home Assistant to be ready
const waitForHass = () => {
  if (window.customElements && window.customElements.get("ha-panel-wordplay")) {
    setupPanel();
  } else {
    setTimeout(waitForHass, 100);
  }
};

function setupPanel() {
  // Register the panel element
  customElements.define("ha-panel-wordplay", WordPlayPanel);
  
  console.info(
    `%c  WORDPLAY-PANEL %c  Successfully loaded and registered  `,
    'color: orange; font-weight: bold; background: black',
    'color: white; font-weight: bold; background: dimgray',
  );
}

// Start the process
waitForHass();

console.info(
  `%c  WORDPLAY-PANEL %c  Version 1.0.0  `,
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray',
);