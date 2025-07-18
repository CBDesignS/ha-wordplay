/**
 * WordPlay UI - User Interface Management
 * Handles screen transitions, UI updates, and DOM manipulation
 */

class WordPlayUI {
    constructor(core, ha) {
        // Module references
        this.core = core;
        this.ha = ha;
        
        // UI state
        this.currentScreen = 'landing';
        this.selectedWordLength = 5;
        
        // DOM element cache
        this.elements = {};
        
        this.init();
    }
    
    init() {
        this.cacheElements();
        this.debugLog('🎨 WordPlay UI initialized');
    }
    
    /**
     * Debug logging
     * @param {string} message - Log message
     * @param {*} data - Optional data to log
     */
    debugLog(message, data = null) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${message}`;
        console.log(logEntry, data);
    }
    
    /**
     * Cache commonly used DOM elements
     */
    cacheElements() {
        this.elements = {
            // Screens
            landingScreen: document.getElementById('landingScreen'),
            gameScreen: document.getElementById('gameScreen'),
            
            // Status elements
            connectionStatus: document.getElementById('connectionStatus'),
            gameStatus: document.getElementById('gameStatus'),
            
            // Game elements
            gameGrid: document.getElementById('gameGrid'),
            guessInput: document.getElementById('guessInput'),
            hintText: document.getElementById('hintText'),
            
            // Buttons
            startGameBtn: document.getElementById('startGameBtn'),
            submitBtn: document.getElementById('submitBtn'),
            hintBtn: document.getElementById('hintBtn'),
            backBtn: document.getElementById('backBtn'),
            audioSettingsBtn: document.getElementById('audioSettingsBtn'),
            
            // Modal
            audioSettingsModal: document.getElementById('audioSettingsModal'),
            audioSettingsIframe: document.getElementById('audioSettingsIframe')
        };
    }
    
    /**
     * Switch between screens with smooth transition
     * @param {string} screenName - 'landing' or 'game'
     */
    switchScreen(screenName) {
        const currentScreenEl = document.querySelector('.screen.active');
        const newScreenEl = this.elements[screenName + 'Screen'];
        
        if (currentScreenEl && newScreenEl && currentScreenEl !== newScreenEl) {
            // Fade out current screen
            currentScreenEl.style.opacity = '0';
            
            setTimeout(() => {
                // Hide current and show new
                currentScreenEl.classList.remove('active');
                newScreenEl.classList.add('active');
                
                // Fade in new screen
                setTimeout(() => {
                    newScreenEl.style.opacity = '1';
                }, 50);
            }, 200);
            
            this.currentScreen = screenName;
            this.debugLog(`📱 Switched to ${screenName} screen`);
        }
    }
    
    /**
     * Update connection status display
     * @param {string} status - 'connected', 'disconnected', or 'connecting'
     * @param {string} message - Status message
     */
    updateConnectionStatus(status, message) {
        const statusEl = this.elements.connectionStatus;
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `connection-status ${status}`;
        }
        this.debugLog(`Connection status: ${status} - ${message}`);
    }
    
    /**
     * Update game status display
     * @param {string} message - Status message
     * @param {string} type - 'info', 'success', 'error', or 'loading'
     */
    updateGameStatus(message, type = 'info') {
        const statusEl = this.elements.gameStatus;
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `game-status ${type}`;
        }
        this.debugLog(`Game status: ${type} - ${message}`);
    }
    
    /**
     * Update game UI based on current game data
     */
    updateGameUI() {
        this.debugLog('🎨 Updating UI with current game data');
        
        // Only update UI if we're on the game screen
        if (this.currentScreen !== 'game') {
            return;
        }
        
        const gameData = this.core.getGameData();
        
        // Update game status
        if (gameData.game_state === 'playing') {
            const remaining = this.core.getRemainingGuesses();
            this.updateGameStatus(`Playing • ${gameData.word_length} letters • ${remaining} guesses remaining`, 'success');
        } else if (gameData.game_state === 'won') {
            this.updateGameStatus(`🎉 You won! • ${gameData.guesses.length} guesses`, 'success');
        } else if (gameData.game_state === 'lost') {
            this.updateGameStatus(`😞 Game over • Better luck next time!`, 'error');
        } else {
            this.updateGameStatus(`Ready to play • ${gameData.word_length} letters`, 'info');
        }
        
        // Update grid
        this.populateGrid();
        
        // Update hint
        this.updateHint(gameData);
        
        // Update input
        if (this.elements.guessInput) {
            this.elements.guessInput.maxLength = gameData.word_length;
        }
        
        // Update button states
        this.updateButtonStates();
        
        this.debugLog('✅ UI update complete');
    }
    
    /**
     * Populate grid with guesses
     */
    populateGrid() {
        this.debugLog('🔤 Populating grid with guesses');
        
        const gameData = this.core.getGameData();
        
        // Clear all tiles
        this.core.clearGrid();
        
        // Show completed guesses
        this.debugLog(`📝 Processing ${gameData.guesses.length} guesses`, {
            guesses: gameData.guesses,
            results: gameData.guess_results
        });
        
        gameData.guesses.forEach((guessString, guessIndex) => {
            // Extract actual word
            const actualWord = this.core.extractWordFromGuess(guessString);
            const resultString = gameData.guess_results[guessIndex] || '';
            
            this.debugLog(`📍 Processing guess ${guessIndex}: "${guessString}" -> extracted: "${actualWord}"`);
            this.debugLog(`📍 Result string: "${resultString}"`);
            
            for (let i = 0; i < actualWord.length && i < this.core.getWordLength(); i++) {
                const tile = this.core.getTile(guessIndex, i);
                if (tile) {
                    tile.textContent = actualWord[i];
                    tile.classList.add('filled');
                    
                    // Apply result styling
                    const letterStatus = this.core.parseLetterResult(resultString, i);
                    if (letterStatus !== 'absent') {
                        tile.classList.add(letterStatus);
                    } else {
                        tile.classList.add('absent');
                    }
                    
                    this.debugLog(`🎨 TILE [${guessIndex},${i}]: "${actualWord[i]}" - ${letterStatus}`);
                }
            }
        });
        
        this.debugLog('✅ Grid population complete');
    }
    
    /**
     * Update hint display
     * @param {Object} gameData - Current game data
     */
    updateHint(gameData) {
        const hintEl = this.elements.hintText;
        if (!hintEl) return;
        
        if (gameData.game_state === 'lost' && gameData.revealed_word) {
            // Show the revealed word when game is lost
            hintEl.textContent = `💀 The word was: ${gameData.revealed_word}`;
            hintEl.style.fontWeight = 'bold';
            hintEl.style.color = '#f44336'; // Red color for game over
        } else if (gameData.hint) {
            // Show regular hint
            hintEl.textContent = gameData.hint;
            hintEl.style.fontWeight = 'normal';
            hintEl.style.color = 'var(--text-secondary-color)';
        } else {
            // Default message
            hintEl.textContent = '💡 Click "Get Hint" for a clue!';
            hintEl.style.fontWeight = 'normal';
            hintEl.style.color = 'var(--text-secondary-color)';
        }
    }
    
    /**
     * Update button states based on game state
     */
    updateButtonStates() {
        const gameData = this.core.getGameData();
        const isPlaying = gameData.game_state === 'playing';
        
        // Submit button
        if (this.elements.submitBtn && this.elements.guessInput) {
            const hasValidInput = this.elements.guessInput.value.length === this.core.getWordLength();
            this.elements.submitBtn.disabled = !isPlaying || !hasValidInput || !this.ha.isActionAllowed('submitGuess');
        }
        
        // Hint button
        if (this.elements.hintBtn) {
            this.elements.hintBtn.disabled = !isPlaying || !this.ha.isActionAllowed('getHint');
        }
        
        // Back button
        if (this.elements.backBtn) {
            this.elements.backBtn.disabled = !this.ha.isActionAllowed('newGame');
        }
    }
    
    /**
     * Handle word length selection
     * @param {number} length - Selected word length
     */
    selectWordLength(length) {
        this.selectedWordLength = length;
        
        // Update button states
        document.querySelectorAll('.word-length-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-length="${length}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        this.debugLog(`🔢 Word length selected: ${length}`);
    }
    
    /**
     * Get current input value
     * @returns {string} Current guess input
     */
    getInputValue() {
        return this.elements.guessInput ? this.elements.guessInput.value.trim().toUpperCase() : '';
    }
    
    /**
     * Clear input field
     */
    clearInput() {
        if (this.elements.guessInput) {
            this.elements.guessInput.value = '';
        }
    }
    
    /**
     * Disable/enable start button
     * @param {boolean} disabled - Disabled state
     * @param {string} text - Button text
     */
    setStartButtonState(disabled, text) {
        if (this.elements.startGameBtn) {
            this.elements.startGameBtn.disabled = disabled;
            this.elements.startGameBtn.textContent = text;
        }
    }
    
    /**
     * Open audio settings modal
     */
    openAudioSettings() {
        this.debugLog('🔊 Opening audio settings modal');
        
        if (this.elements.audioSettingsModal && this.elements.audioSettingsIframe) {
            this.elements.audioSettingsIframe.src = 'wordplay_sound_cfg.html';
            this.elements.audioSettingsModal.classList.add('active');
        }
    }
    
    /**
     * Close audio settings modal
     */
    closeAudioSettings() {
        this.debugLog('🔊 Closing audio settings modal');
        
        if (this.elements.audioSettingsModal && this.elements.audioSettingsIframe) {
            this.elements.audioSettingsModal.classList.remove('active');
            this.elements.audioSettingsIframe.src = '';
        }
    }
    
    /**
     * Get selected word length
     * @returns {number} Selected word length
     */
    getSelectedWordLength() {
        return this.selectedWordLength;
    }
}

// Global UI instance
let wordplayUI = null;

// Initialize when DOM is ready (after core and HA)
document.addEventListener('DOMContentLoaded', () => {
    // Wait for core and HA to be ready
    setTimeout(() => {
        if (window.wordplayCore && window.wordplayHA) {
            const core = window.wordplayCore();
            const ha = window.wordplayHA();
            wordplayUI = new WordPlayUI(core, ha);
            window.wordplayUI = () => wordplayUI;
            console.log('🎨 WordPlay UI ready');
        } else {
            console.error('❌ WordPlay Core or HA not ready for UI initialization');
        }
    }, 100);
});