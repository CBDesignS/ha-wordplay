/**
 * WordPlay Alphabet Grid - Letter Display System
 * Shows A-Z letters around the game grid with color feedback
 */

class WordPlayAlphabet {
    constructor(core) {
        // Module reference
        this.core = core;
        
        // Alphabet state tracking
        this.alphabetGrid = {};
        this.alphabetElements = {};
        
        // Define alphabet positions around the grid (clockwise from bottom-left)
        this.ALPHABET_POSITIONS = {
            // Left side (A-I) - bottom to top
            'A': { side: 'left', position: 0 },
            'B': { side: 'left', position: 1 },
            'C': { side: 'left', position: 2 },
            'D': { side: 'left', position: 3 },
            'E': { side: 'left', position: 4 },
            'F': { side: 'left', position: 5 },
            'G': { side: 'left', position: 6 },
            'H': { side: 'left', position: 7 },
            'I': { side: 'left', position: 8 },
            
            // Top side (J-Q) - left to right
            'J': { side: 'top', position: 0 },
            'K': { side: 'top', position: 1 },
            'L': { side: 'top', position: 2 },
            'M': { side: 'top', position: 3 },
            'N': { side: 'top', position: 4 },
            'O': { side: 'top', position: 5 },
            'P': { side: 'top', position: 6 },
            'Q': { side: 'top', position: 7 },
            
            // Right side (R-Z) - top to bottom
            'R': { side: 'right', position: 0 },
            'S': { side: 'right', position: 1 },
            'T': { side: 'right', position: 2 },
            'U': { side: 'right', position: 3 },
            'V': { side: 'right', position: 4 },
            'W': { side: 'right', position: 5 },
            'X': { side: 'right', position: 6 },
            'Y': { side: 'right', position: 7 },
            'Z': { side: 'right', position: 8 }
        };
        
        this.init();
    }
    
    init() {
        this.debugLog('🔤 WordPlay Alphabet initialized');
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
     * Create the alphabet grid around the game grid
     * @param {number} wordLength - Current word length (5-8)
     */
    createAlphabetGrid(wordLength) {
        this.debugLog(`🔤 Creating alphabet grid for word length: ${wordLength}`);
        
        // Clear existing alphabet if any
        this.clearAlphabetGrid();
        
        // Reset alphabet state
        this.alphabetGrid = {};
        this.alphabetElements = {};
        
        // Initialize all letters as unused
        for (let letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
            this.alphabetGrid[letter] = 'unused';
        }
        
        // Get the main game container
        const gameContainer = document.querySelector('.game-screen');
        if (!gameContainer) {
            this.debugLog('❌ Game container not found for alphabet grid');
            return;
        }
        
        // Find the game grid element
        const gameGrid = document.getElementById('gameGrid');
        if (!gameGrid) {
            this.debugLog('❌ Game grid not found for alphabet grid');
            return;
        }
        
        // Create alphabet container if it doesn't exist
        let alphabetContainer = document.getElementById('alphabetContainer');
        if (!alphabetContainer) {
            alphabetContainer = document.createElement('div');
            alphabetContainer.id = 'alphabetContainer';
            alphabetContainer.className = 'alphabet-container';
            
            // Insert alphabet container before the game grid
            gameGrid.parentNode.insertBefore(alphabetContainer, gameGrid);
        }
        
        // Create alphabet wrapper that will contain both grid and letters
        let alphabetWrapper = document.getElementById('alphabetWrapper');
        if (!alphabetWrapper) {
            alphabetWrapper = document.createElement('div');
            alphabetWrapper.id = 'alphabetWrapper';
            alphabetWrapper.className = 'alphabet-wrapper';
            
            // Move game grid into wrapper
            alphabetContainer.appendChild(alphabetWrapper);
            alphabetWrapper.appendChild(gameGrid);
        }
        
        // Create left side letters (A-I, bottom to top)
        this.createAlphabetSide('left', ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'], wordLength);
        
        // Create top side letters (J-Q, left to right)  
        this.createAlphabetSide('top', ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'], wordLength);
        
        // Create right side letters (R-Z, top to bottom)
        this.createAlphabetSide('right', ['R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], wordLength);
        
        this.debugLog('✅ Alphabet grid created successfully');
    }
    
    /**
     * Create alphabet letters for one side of the grid
     * @param {string} side - 'left', 'top', or 'right'
     * @param {Array} letters - Array of letters for this side
     * @param {number} wordLength - Current word length
     */
    createAlphabetSide(side, letters, wordLength) {
        const alphabetWrapper = document.getElementById('alphabetWrapper');
        if (!alphabetWrapper) return;
        
        // Create or get container for this side
        let sideContainer = document.getElementById(`alphabet-${side}`);
        if (sideContainer) {
            sideContainer.remove(); // Remove existing
        }
        
        sideContainer = document.createElement('div');
        sideContainer.id = `alphabet-${side}`;
        sideContainer.className = `alphabet-side alphabet-${side}`;
        
        // Create individual letter elements
        letters.forEach((letter, index) => {
            const letterEl = document.createElement('div');
            letterEl.id = `alphabet-letter-${letter}`;
            letterEl.className = 'alphabet-letter unused';
            letterEl.textContent = letter;
            letterEl.setAttribute('data-letter', letter);
            letterEl.setAttribute('data-side', side);
            letterEl.setAttribute('data-position', index);
            
            // Store reference for quick access
            this.alphabetElements[letter] = letterEl;
            
            sideContainer.appendChild(letterEl);
        });
        
        alphabetWrapper.appendChild(sideContainer);
    }
    
    /**
     * Clear the existing alphabet grid
     */
    clearAlphabetGrid() {
        this.debugLog('🧹 Clearing alphabet grid states (keeping DOM structure)');
        
        // Reset all letters to unused state
        for (let letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
            this.alphabetGrid[letter] = 'unused';
            if (this.alphabetElements[letter]) {
                this.alphabetElements[letter].className = 'alphabet-letter unused';
            }
        }
        
        this.debugLog('✅ Alphabet grid states cleared (DOM structure preserved)');
    }
    
    /**
     * Update alphabet letter colors based on guess results
     * @param {Array} guesses - Array of guesses made
     * @param {Array} guessResults - Array of guess results
     */
    updateAlphabetColors(guesses, guessResults) {
        this.debugLog('🎨 Updating alphabet colors based on guess results');
        
        // Reset all letters to unused first
        for (let letter of 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
            this.alphabetGrid[letter] = 'unused';
            if (this.alphabetElements[letter]) {
                this.alphabetElements[letter].className = 'alphabet-letter unused';
            }
        }
        
        // Process each guess and its results
        guesses.forEach((guessString, guessIndex) => {
            // Extract actual word from guess
            const actualWord = this.core.extractWordFromGuess(guessString);
            const resultString = guessResults[guessIndex] || '';
            
            // Process each letter in the guess
            for (let i = 0; i < actualWord.length; i++) {
                const letter = actualWord[i].toUpperCase();
                const letterStatus = this.core.parseLetterResult(resultString, i);
                
                // Update alphabet letter status (prioritize better status)
                const currentStatus = this.alphabetGrid[letter];
                if (currentStatus === 'unused' || 
                    (currentStatus === 'absent' && letterStatus !== 'absent') ||
                    (currentStatus === 'partial' && letterStatus === 'correct')) {
                    
                    this.alphabetGrid[letter] = letterStatus;
                    
                    // Update visual element
                    if (this.alphabetElements[letter]) {
                        this.alphabetElements[letter].className = `alphabet-letter ${letterStatus}`;
                    }
                }
            }
        });
        
        this.debugLog('✅ Alphabet colors updated');
    }
    
    /**
     * Hook into grid creation to add alphabet
     */
    enhanceGridCreation() {
        // Store reference to original createGrid function
        const originalCreateGrid = this.core.createGrid.bind(this.core);
        
        // Replace with enhanced version
        this.core.createGrid = (wordLength) => {
            // Call original grid creation
            originalCreateGrid(wordLength);
            
            // Add alphabet grid
            this.createAlphabetGrid(wordLength);
        };
        
        this.debugLog('✅ Grid creation enhanced with alphabet');
    }
    
    /**
     * Update alphabet after grid population
     */
    updateAfterPopulate() {
        const gameData = this.core.getGameData();
        this.updateAlphabetColors(gameData.guesses, gameData.guess_results);
    }
}

// Global alphabet instance
let wordplayAlphabet = null;

// Initialize when DOM is ready (after core)
document.addEventListener('DOMContentLoaded', () => {
    // Wait for core to be ready
    setTimeout(() => {
        if (window.wordplayCore) {
            const core = window.wordplayCore();
            wordplayAlphabet = new WordPlayAlphabet(core);
            window.wordplayAlphabet = () => wordplayAlphabet;
            console.log('🔤 WordPlay Alphabet ready');
        } else {
            console.error('❌ WordPlay Core not ready for Alphabet initialization');
        }
    }, 100);
});