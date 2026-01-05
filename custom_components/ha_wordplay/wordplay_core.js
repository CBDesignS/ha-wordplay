// Rev 2.0 - Fixed grid refresh bug where switching word lengths would not update the grid
// The issue was setWordLength() updating currentWordLength before createGrid() checked if recreation was needed

/**
 * WordPlay Core - Game Logic and State Management
 * Handles core game mechanics, grid management, and game state
 */

class WordPlayCore {
    constructor() {
        // Game configuration
        this.currentWordLength = 5;
        this.gameGrid = [];
        
        // Game state
        this.currentGameData = {
            word_length: 5,
            game_state: 'idle',
            guesses: [],
            guess_results: [],
            hint: '',
            last_message: '',
            message_type: '',
            revealed_word: ''
        };
        
        // Debug mode
        this.debugVisible = true;
        
        this.init();
    }
    
    init() {
        this.debugLog('🎮 WordPlay Core initialized');
    }
    
    /**
     * Debug logging
     * @param {string} message - Log message
     * @param {*} data - Optional data to log
     */
    debugLog(message, data = null) {
        if (this.debugVisible) {
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = `[${timestamp}] ${message}`;
            console.log(logEntry, data);
        }
    }
    
    /**
     * Create the game grid
     * @param {number} wordLength - Size of the grid
     * @param {boolean} forceRecreate - Force recreation even if same size
     */
    createGrid(wordLength, forceRecreate = false) {
        // FIX: Check against current word length BEFORE updating it
        if (!forceRecreate && wordLength === this.currentWordLength && this.gameGrid.length > 0) {
            this.debugLog(`🎯 Grid already correct size: ${wordLength}x${wordLength}`);
            return;
        }
        
        this.debugLog(`🎯 Creating grid: ${wordLength}x${wordLength} (forced: ${forceRecreate})`);
        
        // Update word length AFTER the check
        this.currentWordLength = wordLength;
        const grid = document.getElementById('gameGrid');
        
        if (!grid) {
            this.debugLog('⚠ Game grid element not found');
            return;
        }
        
        grid.innerHTML = '';
        grid.style.gridTemplateColumns = `repeat(${wordLength}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${wordLength}, 1fr)`;
        
        this.gameGrid = [];
        for (let row = 0; row < wordLength; row++) {
            this.gameGrid[row] = [];
            for (let col = 0; col < wordLength; col++) {
                const tile = document.createElement('div');
                tile.className = 'game-tile';
                grid.appendChild(tile);
                this.gameGrid[row][col] = tile;
            }
        }
        
        this.debugLog(`✅ Grid created: ${this.gameGrid.length} rows`);
    }
    
    /**
     * Clear the game grid
     */
    clearGrid() {
        this.gameGrid.forEach(row => {
            row.forEach(tile => {
                tile.textContent = '';
                tile.className = 'game-tile';
            });
        });
        this.debugLog('🧹 Grid cleared');
    }
    
    /**
     * Get current game data
     * @returns {Object} Current game state
     */
    getGameData() {
        return { ...this.currentGameData };
    }
    
    /**
     * Update game data from backend
     * @param {Object} gameData - New game data from backend
     */
    updateGameData(gameData) {
        // FIX: If word length changed, force grid recreation
        const wordLengthChanged = gameData.word_length !== this.currentWordLength;
        
        this.currentGameData = { ...gameData };
        
        // Handle grid recreation if word length changed
        if (wordLengthChanged) {
            this.debugLog(`📏 Word length changed from ${this.currentWordLength} to ${gameData.word_length}`);
            // Force recreation since word length is different
            this.createGrid(gameData.word_length, true);
        }
        
        this.debugLog('📊 Game data updated', this.currentGameData);
    }
    
    /**
     * Extract word from guess string
     * Handles format like "1. WORD"
     * @param {string} guessString - Raw guess string
     * @returns {string} The extracted word
     */
    extractWordFromGuess(guessString) {
        let actualWord = guessString;
        if (typeof guessString === 'string' && guessString.includes('.')) {
            const parts = guessString.split('.');
            if (parts.length > 1) {
                actualWord = parts[1].trim();
            }
        }
        return actualWord;
    }
    
    /**
     * Parse letter result from result string
     * @param {string} resultString - Format like "R⬜ O🟥 P⬜ E⬜ S⬜"
     * @param {number} index - Letter index
     * @returns {string} 'correct', 'partial', or 'absent'
     */
    parseLetterResult(resultString, index) {
        if (typeof resultString !== 'string') return 'absent';
        
        const letterPairs = resultString.split(' ');
        const letterResult = letterPairs[index];
        
        if (!letterResult) return 'absent';
        
        if (letterResult.includes('🟦')) return 'correct';
        if (letterResult.includes('🟥')) return 'partial';
        if (letterResult.includes('⬜')) return 'absent';
        
        return 'absent';
    }
    
    /**
     * Get tile at position
     * @param {number} row - Row index
     * @param {number} col - Column index
     * @returns {HTMLElement|null} Tile element
     */
    getTile(row, col) {
        if (this.gameGrid[row] && this.gameGrid[row][col]) {
            return this.gameGrid[row][col];
        }
        return null;
    }
    
    /**
     * Set word length
     * @param {number} length - New word length
     */
    setWordLength(length) {
        // FIX: Don't update currentWordLength here anymore
        // Let createGrid handle it after checking if recreation is needed
        this.debugLog(`📢 Word length will be set to: ${length}`);
        // Just trigger grid creation with the new length
        this.createGrid(length, false);
    }
    
    /**
     * Get current word length
     * @returns {number} Current word length
     */
    getWordLength() {
        return this.currentWordLength;
    }
    
    /**
     * Check if game is in progress
     * @returns {boolean} True if game is active
     */
    isGameActive() {
        return this.currentGameData.game_state === 'playing';
    }
    
    /**
     * Get remaining guesses
     * @returns {number} Number of guesses left
     */
    getRemainingGuesses() {
        return this.currentWordLength - this.currentGameData.guesses.length;
    }
}

// Global core instance
let wordplayCore = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    wordplayCore = new WordPlayCore();
    window.wordplayCore = () => wordplayCore;
    console.log('🎮 WordPlay Core ready');
});