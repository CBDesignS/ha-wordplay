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
     */
    createGrid(wordLength) {
        if (wordLength === this.currentWordLength && this.gameGrid.length > 0) {
            return;
        }
        
        this.debugLog(`🎯 Creating grid: ${wordLength}x${wordLength}`);
        
        this.currentWordLength = wordLength;
        const grid = document.getElementById('gameGrid');
        
        if (!grid) {
            this.debugLog('❌ Game grid element not found');
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
     * @param {Object} data - New game data
     */
    updateGameData(data) {
        this.currentGameData = {
            word_length: data.word_length || this.currentGameData.word_length,
            game_state: data.game_state || this.currentGameData.game_state,
            guesses: data.guesses || this.currentGameData.guesses,
            guess_results: data.guess_results || this.currentGameData.guess_results,
            hint: data.hint || this.currentGameData.hint,
            last_message: data.last_message || this.currentGameData.last_message,
            message_type: data.message_type || this.currentGameData.message_type,
            revealed_word: data.revealed_word || this.currentGameData.revealed_word
        };
        
        this.debugLog('📊 Game data updated', this.currentGameData);
    }
    
    /**
     * Parse game state from backend status
     * @param {string} gameStatus - Status string from backend
     * @returns {string} Normalized game state
     */
    parseGameState(gameStatus) {
        if (!gameStatus) return 'idle';
        
        const status = gameStatus.toLowerCase();
        if (status.includes('playing')) return 'playing';
        if (status.includes('won')) return 'won';
        if (status.includes('game over') || status.includes('lost')) return 'lost';
        if (status.includes('ready')) return 'idle';
        
        return 'idle';
    }
    
    /**
     * Extract word from guess string format
     * @param {string} guessString - Format like "1. WORD"
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
        this.currentWordLength = length;
        this.debugLog(`🔢 Word length set to: ${length}`);
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