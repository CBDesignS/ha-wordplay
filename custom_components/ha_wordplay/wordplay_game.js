/**
 * WordPlay Game - Main Coordinator
 * Orchestrates all modules and handles game flow
 */

class WordPlayGame {
    constructor() {
        // Module instances
        this.core = null;
        this.ha = null;
        this.ui = null;
        this.alphabet = null;
        
        // Audio configuration from URL parameters
        this.audioConfig = {
            enabled: true,
            volume: 30,
            gameEvents: true,
            guessEvents: true,
            uiEvents: false,
            errorEvents: true
        };
        
        // Initialize when modules are ready
        this.waitForModules();
    }
    
    /**
     * Wait for all modules to be ready
     */
    waitForModules() {
        const checkModules = () => {
            if (window.wordplayCore && window.wordplayHA && window.wordplayUI && window.wordplayAlphabet) {
                this.initializeModules();
            } else {
                setTimeout(checkModules, 50);
            }
        };
        checkModules();
    }
    
    /**
     * Initialize all modules
     */
    initializeModules() {
        // Get module instances
        this.core = window.wordplayCore();
        this.ha = window.wordplayHA();
        this.ui = window.wordplayUI();
        this.alphabet = window.wordplayAlphabet();
        
        // Set up module connections
        this.connectModules();
        
        // Initialize game
        this.init();
    }
    
    /**
     * Connect modules together
     */
    connectModules() {
        // Set up HA callbacks
        this.ha.setStateUpdateCallback(this.onStateUpdate.bind(this));
        this.ha.setConnectionChangeCallback(this.onConnectionChange.bind(this));
        this.ha.setWordLengthUpdateCallback(this.onWordLengthUpdate.bind(this));
        
        // Enhance grid creation with alphabet
        this.alphabet.enhanceGridCreation();
        
        // Hook into UI populate grid
        const originalPopulateGrid = this.ui.populateGrid.bind(this.ui);
        this.ui.populateGrid = () => {
            originalPopulateGrid();
            this.alphabet.updateAfterPopulate();
        };
    }
    
    /**
     * Initialize the game
     */
    async init() {
        this.debugLog('🚀 WordPlay: Initializing two-screen system with backend integration');
        
        // Setup theme detection
        this.detectHATheme();
        
        // Get audio configuration from URL
        this.loadAudioConfig();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Test connection and start polling
        try {
            await this.ha.refreshGameState();
            this.ha.startPolling();
            
            // Load user's difficulty setting
            await this.loadUserDifficulty();
            
            // Apply audio configuration after delay
            setTimeout(() => this.applyAudioConfig(), 2000);
            
        } catch (error) {
            this.debugLog('❌ Initialization failed', error);
            this.ui.updateConnectionStatus('disconnected', '❌ Connection failed');
        }
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
     * Auto-detect Home Assistant theme
     */
    detectHATheme() {
        try {
            // Method 1: Check parent frame theme
            if (window.parent && window.parent !== window) {
                const parentDoc = window.parent.document;
                if (parentDoc) {
                    const haMain = parentDoc.querySelector('home-assistant');
                    if (haMain && haMain.hass && haMain.hass.themes) {
                        const currentTheme = haMain.hass.themes.darkMode ? 'dark' : 'light';
                        document.body.setAttribute('data-theme', currentTheme);
                        this.debugLog(`🎨 HA theme detected: ${currentTheme}`);
                        return;
                    }
                }
            }
            
            // Method 2: Check URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('theme')) {
                const theme = urlParams.get('theme');
                document.body.setAttribute('data-theme', theme);
                this.debugLog(`🎨 URL theme detected: ${theme}`);
                return;
            }
            
            // Method 3: Use browser preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const theme = prefersDark ? 'dark' : 'light';
            document.body.setAttribute('data-theme', theme);
            this.debugLog(`🎨 Browser theme detected: ${theme}`);
            
        } catch (error) {
            this.debugLog('⚠️ Theme detection failed, using browser default', error);
        }
    }
    
    /**
     * Load audio configuration from URL
     */
    loadAudioConfig() {
        const urlParams = new URLSearchParams(window.location.search);
        
        try {
            this.audioConfig = {
                enabled: urlParams.get('audio_enabled') === 'true',
                volume: parseInt(urlParams.get('audio_volume')) || 30,
                gameEvents: urlParams.get('audio_gameEvents') === 'true',
                guessEvents: urlParams.get('audio_guessEvents') === 'true',
                uiEvents: urlParams.get('audio_uiEvents') === 'true',
                errorEvents: urlParams.get('audio_errorEvents') === 'true'
            };
            
            this.debugLog('🔊 Audio configuration loaded:', this.audioConfig);
        } catch (error) {
            this.debugLog('⚠️ Audio config failed, using defaults:', error);
        }
    }
    
    /**
     * Load user's difficulty setting from their select entity
     */
    async loadUserDifficulty() {
        try {
            if (!this.ha.currentUser) {
                this.debugLog('⏳ Waiting for user identification before loading difficulty');
                return;
            }
            
            const difficultyEntityId = `select.ha_wordplay_difficulty_${this.ha.currentUser}`;
            const response = await fetch('/api/states/' + difficultyEntityId, {
                headers: {
                    'Authorization': `Bearer ${this.ha.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const entity = await response.json();
                if (entity && entity.state) {
                    // Only update UI if we're on the landing screen
                    if (this.ui.currentScreen === 'landing') {
                        this.ui.selectDifficulty(entity.state);
                        this.debugLog(`🎯 Loaded user difficulty: ${entity.state}`);
                    }
                }
            }
        } catch (error) {
            this.debugLog('⚠️ Could not load user difficulty, using default:', error);
        }
    }
    
    /**
     * Apply audio configuration
     */
    applyAudioConfig() {
        // Fixed: Check for global wordplayAudio instance directly
        if (window.wordplayAudio) {
            const audio = window.wordplayAudio;
            if (audio) {
                audio.setPreference('enabled', this.audioConfig.enabled);
                audio.setVolume(this.audioConfig.volume / 100);
                audio.setPreference('gameEvents', this.audioConfig.gameEvents);
                audio.setPreference('guessEvents', this.audioConfig.guessEvents);
                audio.setPreference('uiEvents', this.audioConfig.uiEvents);
                audio.setPreference('errorEvents', this.audioConfig.errorEvents);
                
                this.debugLog('✅ Audio configuration applied successfully');
            } else {
                setTimeout(() => this.applyAudioConfig(), 1000);
            }
        } else {
            setTimeout(() => this.applyAudioConfig(), 1000);
        }
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Word length selection buttons
        document.querySelectorAll('.word-length-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const length = parseInt(e.target.dataset.length);
                this.selectWordLength(length);
            });
        });
        
        // Difficulty selection buttons
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Find the actual button element (might have clicked on child)
                let targetBtn = e.target;
                while (targetBtn && !targetBtn.classList.contains('difficulty-btn')) {
                    targetBtn = targetBtn.parentElement;
                }
                
                if (targetBtn) {
                    const difficulty = targetBtn.dataset.difficulty;
                    this.selectDifficulty(difficulty);
                }
            });
        });
        
        // Start game button
        const startBtn = document.getElementById('startGameBtn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startNewGameFlow());
        }
        
        // Audio settings button
        const audioBtn = document.getElementById('audioSettingsBtn');
        if (audioBtn) {
            audioBtn.addEventListener('click', () => this.openAudioSettings());
        }
        
        // Game action buttons
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitGuess());
        }
        
        const hintBtn = document.getElementById('hintBtn');
        if (hintBtn) {
            hintBtn.addEventListener('click', () => this.getHint());
        }
        
        const backBtn = document.getElementById('backBtn');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.returnToLanding());
        }
        
        // Input field
        const guessInput = document.getElementById('guessInput');
        if (guessInput) {
            guessInput.addEventListener('input', () => this.updateInput());
            guessInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
        }
        
        // Message handler for audio settings iframe
        window.addEventListener('message', this.handleAudioSettingsMessage.bind(this));
    }
    
    /**
     * Handle state update from HA
     * @param {Object} gameData - New game data
     */
    onStateUpdate(gameData) {
        // Update core game data
        this.core.updateGameData(gameData);
        
        // Update UI
        this.ui.updateGameUI();
        
        // Check for auto-return to landing
        if (this.ui.currentScreen === 'game') {
            this.checkAutoReturn(gameData.game_state);
        }
    }
    
    /**
     * Handle connection change
     * @param {string} status - Connection status
     * @param {string} message - Status message
     */
    onConnectionChange(status, message) {
        this.ui.updateConnectionStatus(status, message);
    }
    
    /**
     * Handle word length update from backend
     * @param {number} length - New word length
     */
    onWordLengthUpdate(length) {
        if (this.ui.currentScreen === 'landing') {
            this.ui.selectWordLength(length);
        }
    }
    
    /**
     * Select word length
     * @param {number} length - Selected word length
     */
    async selectWordLength(length) {
        this.ui.selectWordLength(length);
        
        // Update backend select entity
        try {
            await this.ha.updateWordLength(length);
        } catch (error) {
            this.debugLog('⚠️ Could not update word length entity:', error);
        }
        
        this.debugLog(`🔢 Word length selected: ${length}`);
    }
    
    /**
     * Select difficulty - Don't update backend until game starts
     * @param {string} difficulty - Selected difficulty
     */
    async selectDifficulty(difficulty) {
        this.ui.selectDifficulty(difficulty);
        
        // Don't update backend immediately - wait until game starts
        this.debugLog(`🎯 Difficulty selected: ${difficulty} (will update backend on game start)`);
    }
    
    /**
     * Start new game flow
     */
    async startNewGameFlow() {
        try {
            const selectedLength = this.ui.getSelectedWordLength();
            const selectedDifficulty = this.ui.getSelectedDifficulty();
            
            this.debugLog(`🎮 Starting new game flow with ${selectedLength} letters, ${selectedDifficulty} difficulty`);
            
            // Disable start button
            this.ui.setStartButtonState(true, 'Starting...');
            
            // Update difficulty in backend only once here
            try {
                const difficultyEntityId = `select.ha_wordplay_difficulty_${this.ha.currentUser}`;
                await this.ha.callHAService('select', 'select_option', {
                    entity_id: difficultyEntityId,
                    option: selectedDifficulty
                });
                this.debugLog(`🎯 Difficulty updated in backend: ${selectedDifficulty}`);
            } catch (error) {
                this.debugLog('⚠️ Could not update difficulty entity:', error);
            }
            
            // Switch to game screen
            this.ui.switchScreen('game');
            
            // Set word length in core
            this.core.setWordLength(selectedLength);
            
            // Initialize alphabet system
            this.alphabet.createAlphabetGrid(selectedLength);
            
            // Create game grid
            this.core.createGrid(selectedLength);
            
            // Start the actual game
            await this.ha.startNewGame(selectedLength);
            
            // Update input field max length
            const guessInput = document.getElementById('guessInput');
            if (guessInput) {
                guessInput.maxLength = selectedLength;
            }
            
            // Reset start button
            this.ui.setStartButtonState(false, 'Start Game');
            
            this.debugLog('✅ Game flow started successfully');
            
        } catch (error) {
            this.debugLog('❌ Start game flow failed', error);
            
            // Reset start button
            this.ui.setStartButtonState(false, 'Start Game');
            
            // Return to landing screen
            this.ui.switchScreen('landing');
        }
    }
    
    /**
     * Submit a guess
     */
    async submitGuess() {
        if (!this.ha.isActionAllowed('submitGuess')) {
            this.debugLog('🚫 Submit guess blocked by cooldown');
            return;
        }
        
        const guess = this.ui.getInputValue();
        
        this.debugLog(`📝 Submit guess called with: "${guess}"`);
        
        if (guess.length !== this.core.getWordLength()) {
            this.debugLog(`❌ Invalid guess length: ${guess.length} (expected ${this.core.getWordLength()})`);
            return;
        }
        
        try {
            this.ha.setActionCooldown('submitGuess', 500);
            this.ui.updateGameStatus('🔍 Processing guess...', 'loading');
            
            await this.ha.submitGuess(guess);
            
            // Clear input
            this.ui.clearInput();
            
            this.debugLog('✅ Guess submitted successfully, refreshing state');
            
            // Refresh state after delay
            setTimeout(() => {
                this.ha.refreshGameState();
            }, 300);
            
        } catch (error) {
            this.debugLog('❌ Submit guess failed', error);
            this.ui.updateGameStatus('Failed to submit guess', 'error');
        }
    }
    
    /**
     * Get a hint
     */
    async getHint() {
        if (!this.ha.isActionAllowed('getHint')) {
            this.debugLog('🚫 Get hint blocked by cooldown');
            return;
        }
        
        try {
            this.ha.setActionCooldown('getHint', 500);
            this.ui.updateGameStatus('💡 Getting hint...', 'loading');
            
            await this.ha.getHint();
            
            this.debugLog('✅ Hint service called, refreshing state');
            
            // Refresh state after delay
            setTimeout(() => {
                this.ha.refreshGameState();
            }, 500);
            
        } catch (error) {
            this.debugLog('❌ Get hint failed', error);
            this.ui.updateGameStatus('Failed to get hint', 'error');
        }
    }
    
    /**
     * Return to landing screen
     */
    returnToLanding() {
        this.debugLog('🏠 Returning to landing screen');
        
        // Clear game state
        this.alphabet.clearAlphabetGrid();
        
        // Clear input
        this.ui.clearInput();
        
        // Switch to landing screen
        this.ui.switchScreen('landing');
        
        // Reload user's difficulty setting
        this.loadUserDifficulty();
    }
    
    /**
     * Handle input updates
     */
    updateInput() {
        this.ui.updateButtonStates();
    }
    
    /**
     * Handle key press
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyPress(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.debugLog('⌨️ Enter key pressed - calling submitGuess()');
            this.submitGuess();
        }
    }
    
    /**
     * Check for auto-return to landing
     * @param {string} gameState - Current game state
     */
    checkAutoReturn(gameState) {
        // AUTO-RETURN DISABLED - Use manual "New Game" button instead
    }
    
    /**
     * Open audio settings modal
     */
    openAudioSettings() {
        this.ui.openAudioSettings();
    }
    
    /**
     * Close audio settings modal
     */
    closeAudioSettings() {
        this.ui.closeAudioSettings();
    }
    
    /**
     * Handle messages from audio settings iframe
     * @param {MessageEvent} event - Message event
     */
    handleAudioSettingsMessage(event) {
        this.debugLog('📨 Received message from iframe:', event.data);
        
        if (event.data) {
            if (event.data.action === 'closeAudioSettings' || 
                event.data.action === 'close' ||
                event.data === 'close' ||
                event.data === 'closeAudioSettings') {
                this.closeAudioSettings();
            }
        }
    }
}

// Global game instance
let wordplayGame = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    wordplayGame = new WordPlayGame();
    window.wordplayGame = () => wordplayGame;
    console.log('🎮 WordPlay Game Coordinator ready');
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (window.wordplayHA) {
        const ha = window.wordplayHA();
        if (ha) {
            ha.stopPolling();
            console.log('🧹 Cleanup: Polling stopped');
        }
    }
});