/**
 * H.A WordPlay More-Info Dialog Override
 * Auto-loaded by the integration's frontend platform
 * Replaces the default more-info popup with the game interface
 */

import { LitElement, html, css } from "lit";

class WordPlayMoreInfo extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      stateObj: { type: Object },
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

  updated(changedProps) {
    if (changedProps.has("hass") || changedProps.has("stateObj")) {
      this._updateGameState();
    }
  }

  _updateGameState() {
    if (!this.hass || !this.stateObj) return;

    // Get game data from button entity attributes
    const attrs = this.stateObj.attributes;
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
      <div class="wordplay-container">
        <div class="game-header">
          <h1 class="game-title">🎮 WordPlay</h1>
          <p class="game-status">${this._gameState.state}</p>
          ${!isPlaying ? this._renderWordLengthSelector() : ""}
        </div>

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
        --tile-size: 50px;
        --tile-gap: 4px;
        display: block;
        width: 100%;
        height: 100%;
      }

      .wordplay-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 16px;
        gap: 16px;
        min-height: 500px;
        width: 100%;
        box-sizing: border-box;
      }

      .game-header {
        text-align: center;
        width: 100%;
      }

      .game-title {
        font-size: 28px;
        font-weight: bold;
        color: var(--primary-text-color);
        margin: 0 0 8px 0;
      }

      .game-status {
        font-size: 16px;
        color: var(--secondary-text-color);
        margin: 0 0 16px 0;
      }

      .word-length-selector {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin: 8px 0;
        flex-wrap: wrap;
      }

      .length-button {
        padding: 8px 16px;
        border: 2px solid var(--primary-color);
        background: var(--card-background-color);
        color: var(--primary-color);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: bold;
        font-size: 14px;
      }

      .length-button.active {
        background: var(--primary-color);
        color: white;
      }

      .length-button:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }

      .length-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .game-grid {
        display: grid;
        gap: var(--tile-gap);
        justify-content: center;
        margin: 16px 0;
        transition: all 0.3s ease;
      }

      .game-tile {
        width: var(--tile-size);
        height: var(--tile-size);
        border: 2px solid var(--tile-border);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
        text-transform: uppercase;
        background: var(--tile-empty);
        color: var(--primary-text-color);
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .game-tile.filled {
        background: var(--secondary-background-color);
        border-color: var(--secondary-text-color);
        transform: scale(1.02);
      }

      .game-tile.correct {
        background: var(--tile-correct);
        color: white;
        border-color: var(--tile-correct);
        animation: flip 0.6s ease;
      }

      .game-tile.partial {
        background: var(--tile-partial);
        color: white;
        border-color: var(--tile-partial);
        animation: flip 0.6s ease;
      }

      .game-tile.absent {
        background: var(--tile-absent);
        color: var(--primary-text-color);
        border-color: var(--tile-border);
        animation: flip 0.6s ease;
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
        0%,
        100% {
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
        max-width: 400px;
        text-align: center;
      }

      .input-field {
        width: 100%;
        padding: 16px;
        font-size: 20px;
        text-align: center;
        text-transform: uppercase;
        border: 2px solid var(--tile-border);
        border-radius: 12px;
        margin-bottom: 16px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        transition: all 0.3s ease;
        letter-spacing: 2px;
      }

      .input-field:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
        transform: scale(1.02);
      }

      .input-field.error {
        border-color: var(--tile-partial);
        animation: shake 0.6s ease;
      }

      .action-buttons {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
      }

      .action-button {
        padding: 14px 24px;
        border: none;
        border-radius: 12px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        min-width: 140px;
        font-size: 16px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      .action-button.primary {
        background: var(--primary-color);
        color: white;
      }

      .action-button.secondary {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
        border: 2px solid var(--divider-color);
      }

      .action-button:hover:not(:disabled) {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
      }

      .action-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }

      .game-info {
        text-align: center;
        padding: 16px;
        background: var(--secondary-background-color);
        border-radius: 12px;
        max-width: 400px;
        margin: 8px 0;
        border-left: 4px solid var(--primary-color);
      }

      .hint-text {
        font-style: italic;
        color: var(--secondary-text-color);
        font-size: 16px;
      }

      .message {
        text-align: center;
        padding: 12px 20px;
        border-radius: 12px;
        margin: 8px 0;
        font-weight: 500;
        font-size: 16px;
      }

      .message.success {
        background: rgba(76, 175, 80, 0.15);
        color: #4caf50;
        border: 2px solid rgba(76, 175, 80, 0.3);
      }

      .message.error {
        background: rgba(244, 67, 54, 0.15);
        color: var(--tile-partial);
        border: 2px solid rgba(244, 67, 54, 0.3);
      }

      .message.info {
        background: rgba(33, 150, 243, 0.15);
        color: var(--primary-color);
        border: 2px solid rgba(33, 150, 243, 0.3);
      }

      .instructions {
        text-align: center;
        font-size: 14px;
        color: var(--secondary-text-color);
        margin-top: 16px;
        padding: 12px;
        background: rgba(0, 0, 0, 0.05);
        border-radius: 8px;
      }

      /* Mobile responsiveness */
      @media (max-width: 768px) {
        :host {
          --tile-size: 40px;
          --tile-gap: 3px;
        }

        .wordplay-container {
          padding: 12px;
        }

        .game-title {
          font-size: 24px;
        }

        .input-field {
          font-size: 18px;
          padding: 12px;
        }

        .action-buttons {
          flex-direction: column;
          align-items: center;
        }

        .action-button {
          width: 100%;
          max-width: 280px;
        }
      }

      @media (max-width: 480px) {
        :host {
          --tile-size: 35px;
          --tile-gap: 2px;
        }

        .game-title {
          font-size: 20px;
        }
      }

      /* Dark mode adjustments */
      @media (prefers-color-scheme: dark) {
        :host {
          --tile-absent: #424242;
        }
      }
    `;
  }
}

// Define the custom element
customElements.define("wordplay-more-info", WordPlayMoreInfo);

// Wait for Home Assistant to be ready, then override the more-info dialog
const waitForHass = () => {
  if (window.customElements && window.customElements.get("hui-more-info-dialog")) {
    setupMoreInfoOverride();
  } else {
    setTimeout(waitForHass, 100);
  }
};

function setupMoreInfoOverride() {
  const moreInfoDialog = customElements.get("hui-more-info-dialog");
  
  if (moreInfoDialog && !moreInfoDialog._wordplayPatched) {
    // Mark as patched to avoid double-patching
    moreInfoDialog._wordplayPatched = true;
    
    // Store the original _renderContent method
    const originalRenderContent = moreInfoDialog.prototype._renderContent || 
                                  moreInfoDialog.prototype.render;
    
    // Override the _renderContent method
    const newRenderContent = function() {
      // Check if this is our WordPlay button
      if (this.stateObj && this.stateObj.entity_id === "button.ha_wordplay_game") {
        return html`
          <wordplay-more-info
            .hass=${this.hass}
            .stateObj=${this.stateObj}
          ></wordplay-more-info>
        `;
      }
      
      // For all other entities, use the original method
      return originalRenderContent.call(this);
    };
    
    // Apply the override
    if (moreInfoDialog.prototype._renderContent) {
      moreInfoDialog.prototype._renderContent = newRenderContent;
    } else if (moreInfoDialog.prototype.render) {
      moreInfoDialog.prototype.render = newRenderContent;
    }
    
    console.info(
      `%c  WORDPLAY-MORE-INFO %c  Successfully loaded and patched more-info dialog  `,
      'color: orange; font-weight: bold; background: black',
      'color: white; font-weight: bold; background: dimgray',
    );
  }
}

// Start the process
waitForHass();

console.info(
  `%c  WORDPLAY-MORE-INFO %c  Version 1.0.0  `,
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray',
);