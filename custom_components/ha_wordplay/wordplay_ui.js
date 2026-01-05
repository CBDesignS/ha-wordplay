// Rev 2.0 - Fixed hint display to properly show hints when received from backend
// Ensures hint text updates immediately when hint button is clicked

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
        this.selectedDifficulty = 'normal';
        
        // DOM element cache
        this.elements = {};
        
        // Focus management
        this.lastFocusedElement = null;
        
        this.init();
    }
    
    init() {
        this.cacheElements();
        this.setupFocusManagement();
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
     * Get translated text using i18n system
     * @param {string} key - Translation key
     * @param {Object} params - Optional parameters
     * @returns {string} Translated text
     */
    t(key, params = {}) {
        if (window.wordplayI18n && window.wordplayI18n.getCurrentLanguage) {
            return window.wordplayI18n.t(key, params);
        }
        return key; // Fallback to key if i18n not ready
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
            
            // Audio Modal
            audioSettingsModal: document.getElementById('audioSettingsModal'),
            audioSettingsIframe: document.getElementById('audioSettingsIframe'),
            
            // Stats Modal
            statsModal: document.getElementById('statsModal'),
            statsIframe: document.getElementById('statsIframe')
        };
    }
    
    /**
     * Setup focus management for accessibility
     */
    setupFocusManagement() {
        // Add escape key handler for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.elements.audioSettingsModal && this.elements.audioSettingsModal.classList.contains('active')) {
                    this.closeAudioSettings();
                }
                if (this.elements.statsModal && this.elements.statsModal.classList.contains('active')) {
                    this.closeStatsPage();
                }
            }
        });
        
        // Set up focus trapping for audio modal
        if (this.elements.audioSettingsModal) {
            this.elements.audioSettingsModal.addEventListener('keydown', this.handleModalKeydown.bind(this));
        }
        
        // Set up focus trapping for stats modal
        if (this.elements.statsModal) {
            this.elements.statsModal.addEventListener('keydown', this.handleModalKeydown.bind(this));
        }
    }
    
    /**
     * Handle keydown events in modal for focus trapping
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleModalKeydown(e) {
        if (e.key !== 'Tab') return;
        
        const modal = e.currentTarget;
        if (!modal.classList.contains('active')) return;
        
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), iframe'
        );
        
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    }
    
    /**
     * Switch between screens
     * @param {string} screen - 'landing' or 'game'
     */
    switchScreen(screen) {
        // Hide all screens
        if (this.elements.landingScreen) {
            this.elements.landingScreen.classList.remove('active');
            this.elements.landingScreen.setAttribute('aria-hidden', 'true');
        }
        if (this.elements.gameScreen) {
            this.elements.gameScreen.classList.remove('active');
            this.elements.gameScreen.setAttribute('aria-hidden', 'true');
        }
        
        // Show requested screen
        if (screen === 'landing') {
            if (this.elements.landingScreen) {
                this.elements.landingScreen.classList.add('active');
                this.elements.landingScreen.setAttribute('aria-hidden', 'false');
                this.focusFirstElement(this.elements.landingScreen);
            }
        } else if (screen === 'game') {
            if (this.elements.gameScreen) {
                this.elements.gameScreen.classList.add('active');
                this.elements.gameScreen.setAttribute('aria-hidden', 'false');
                // Focus on guess input
                if (this.elements.guessInput) {
                    setTimeout(() => {
                        this.elements.guessInput.focus();
                    }, 100);
                }
            }
        }
        
        this.currentScreen = screen;
        this.debugLog(`📱 Switched to ${screen} screen`);
    }
    
    /**
     * Focus first focusable element in container
     * @param {HTMLElement} container - Container element
     */
    focusFirstElement(container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
    
    /**
     * Update connection status display
     * @param {string} status - 'connected', 'disconnected', or 'connecting'
     * @param {string} message - Status message (optional)
     */
    updateConnectionStatus(status, message) {
        const statusEl = this.elements.connectionStatus;
        if (statusEl) {
            // Use translated message if it's a known status
            let displayMessage = message;
            if (status === 'connected') {
                displayMessage = this.t('connection.connected');
            } else if (status === 'disconnected') {
                displayMessage = this.t('connection.disconnected');
            } else if (status === 'connecting') {
                displayMessage = this.t('connection.connecting');
            }
            statusEl.textContent = displayMessage;
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
            // Check if message contains known patterns and translate
            let translatedMessage = message;
            if (message.includes('Processing guess')) {
                translatedMessage = this.t('game.processing');
            } else if (message.includes('Getting hint')) {
                translatedMessage = this.t('game.gettingHint');
            } else if (message.includes('Starting game')) {
                translatedMessage = this.t('game.starting');
            }
            statusEl.textContent = translatedMessage;
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
        
        // Update game status with translated text
        if (gameData.game_state === 'playing') {
            const remaining = this.core.getRemainingGuesses();
            const message = `${this.t('game.playing')} • ${gameData.word_length} ${this.t('wordLength.letters').toLowerCase()} • ${remaining} ${this.t('game.guessesRemaining')}`;
            this.updateGameStatus(message, 'success');
        } else if (gameData.game_state === 'won') {
            const message = `${this.t('game.won')} • ${gameData.guesses.length} ${this.t('game.wonIn')}`;
            this.updateGameStatus(message, 'success');
        } else if (gameData.game_state === 'lost') {
            const message = `${this.t('game.lost')} • ${this.t('game.betterLuck')}`;
            this.updateGameStatus(message, 'error');
        } else {
            const message = `${this.t('game.ready')} • ${gameData.word_length} ${this.t('wordLength.letters').toLowerCase()}`;
            this.updateGameStatus(message, 'info');
        }
        
        // Update grid
        this.populateGrid();
        
        // Update hint - FIX: Force update even if hint hasn't changed
        this.updateHint(gameData, true);
        
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
        this.debugLog(`🔍 Processing ${gameData.guesses.length} guesses`, {
            guesses: gameData.guesses,
            results: gameData.guess_results
        });
        
        gameData.guesses.forEach((guessString, guessIndex) => {
            // Extract actual word
            const actualWord = this.core.extractWordFromGuess(guessString);
            const resultString = gameData.guess_results[guessIndex] || '';
            
            this.debugLog(`🔍 Processing guess ${guessIndex}: "${guessString}" -> extracted: "${actualWord}"`);
            this.debugLog(`🔍 Result string: "${resultString}"`);
            
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
     * @param {boolean} forceUpdate - Force update even if unchanged
     */
    updateHint(gameData, forceUpdate = false) {
        const hintEl = this.elements.hintText;
        if (!hintEl) return;
        
        // FIX: Always update hint when called to ensure it displays
        this.debugLog('💡 Updating hint display', { 
            hint: gameData.hint, 
            state: gameData.game_state,
            revealed: gameData.revealed_word 
        });
        
        if (gameData.game_state === 'lost' && gameData.revealed_word) {
            // Show the revealed word when game is lost with translation
            const revealText = `${this.t('game.lost')} - ${this.t('game.wordWas')}: ${gameData.revealed_word}`;
            hintEl.textContent = revealText;
            hintEl.style.fontWeight = 'bold';
            hintEl.style.color = '#f44336'; // Red color for game over
        } else if (gameData.hint && gameData.hint.trim() !== '') {
            // Show regular hint - Keep hints in original language from API
            hintEl.textContent = gameData.hint;
            hintEl.style.fontWeight = 'normal';
            hintEl.style.color = 'var(--text-secondary-color)';
            this.debugLog('💡 Hint displayed: ' + gameData.hint);
        } else if (gameData.last_message && gameData.last_message.includes('Hint:')) {
            // FIX: Extract hint from last_message if it contains hint
            const hintMatch = gameData.last_message.match(/Hint:\s*(.+)/);
            if (hintMatch) {
                hintEl.textContent = `💡 ${hintMatch[1]}`;
                hintEl.style.fontWeight = 'normal';
                hintEl.style.color = 'var(--text-secondary-color)';
                this.debugLog('💡 Hint extracted from message: ' + hintMatch[1]);
            }
        } else {
            // Default message - translated
            hintEl.textContent = this.t('game.enterGuess');
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
        
        this.debugLog(`📢 Word length selected: ${length}`);
    }
    
    /**
     * Handle difficulty selection
     * @param {string} difficulty - Selected difficulty
     */
    selectDifficulty(difficulty) {
        this.selectedDifficulty = difficulty;
        
        // Update button states with a small delay to prevent lag
        requestAnimationFrame(() => {
            document.querySelectorAll('.difficulty-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            const activeBtn = document.querySelector(`[data-difficulty="${difficulty}"]`);
            if (activeBtn) {
                activeBtn.classList.add('active');
            }
        });
        
        this.debugLog(`🎯 Difficulty selected: ${difficulty}`);
    }
    
    /**
     * Get current input value
     * @returns {string} Current guess input
     */
    getInputValue() {
        return this.elements.guessInput ? this.elements.guessInput.value.toUpperCase() : '';
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
     * Set start button state
     * @param {boolean} loading - Is loading
     * @param {string} text - Button text
     */
    setStartButtonState(loading, text) {
        if (this.elements.startGameBtn) {
            this.elements.startGameBtn.disabled = loading;
            this.elements.startGameBtn.textContent = text || this.t('button.startGame');
            if (loading) {
                this.elements.startGameBtn.classList.add('loading');
            } else {
                this.elements.startGameBtn.classList.remove('loading');
            }
        }
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
            console.error('⚠ WordPlay Core or HA not ready for UI initialization');
        }
    }, 50);
});