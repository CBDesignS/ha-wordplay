/**
 * WordPlay Home Assistant API - Backend Integration
 * Handles all communication with Home Assistant backend
 */

class WordPlayHA {
    constructor() {
        // API configuration
        this.accessToken = null;
        this.updateInterval = null;
        this.lastUpdate = 'Never';
        
        // Raw button entity data for debugging
        this.rawButtonData = null;
        
        // Action cooldowns to prevent spam
        this.cooldowns = {
            newGame: false,
            submitGuess: false,
            getHint: false
        };
        
        // Polling configuration
        this.pollingInterval = 1000; // 1 second
        
        // Event callbacks
        this.onStateUpdate = null;
        this.onConnectionChange = null;
        
        this.init();
    }
    
    init() {
        this.accessToken = this.getAccessToken();
        this.debugLog(`🔑 Access token: ${this.accessToken ? 'Present' : 'Missing'}`);
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
     * Get access token from URL parameters
     * @returns {string|null} Access token
     */
    getAccessToken() {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('access_token');
        
        if (token) {
            this.debugLog('🔑 Access token extracted from URL parameter');
            return token;
        }
        
        this.debugLog('❌ No access token found in URL parameters');
        return null;
    }
    
    /**
     * Call Home Assistant service
     * @param {string} domain - Service domain
     * @param {string} service - Service name
     * @param {Object} data - Service data
     * @returns {Promise} Service response
     */
    async callHAService(domain, service, data = {}) {
        this.debugLog(`🔧 Calling HA service: ${domain}.${service}`, data);
        
        const headers = {'Content-Type': 'application/json'};
        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        const response = await fetch(`/api/services/${domain}/${service}`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            this.debugLog(`❌ Service call failed: ${response.status}`);
            throw new Error(`Service call failed: ${response.status}`);
        }

        const result = await response.json();
        this.debugLog(`✅ Service call successful`, result);
        return result;
    }
    
    /**
     * Get entity state from Home Assistant
     * @param {string} entityId - Entity ID
     * @returns {Promise} Entity state
     */
    async getEntityState(entityId) {
        const headers = {'Content-Type': 'application/json'};
        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        const response = await fetch(`/api/states/${entityId}`, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            throw new Error(`Entity fetch failed: ${response.status}`);
        }

        return response.json();
    }
    
    /**
     * Refresh game state from backend
     * @returns {Promise<boolean>} Success status
     */
    async refreshGameState() {
        try {
            this.debugLog('🔄 Refreshing game state from button entity...');
            
            // For now, use default user entity until we implement proper user detection
            const buttonEntity = await this.getEntityState('button.ha_wordplay_game_default');
            this.rawButtonData = buttonEntity; // Store for debugging
            
            if (buttonEntity && buttonEntity.attributes) {
                const attrs = buttonEntity.attributes;
                this.debugLog('📊 Raw button attributes received', attrs);
                
                // Parse data from button entity
                const gameData = {
                    word_length: attrs.word_length || 5,
                    game_state: this.parseGameState(attrs.game_status),
                    guesses: attrs.guess_history || [],
                    guess_results: attrs.guess_results || [],
                    hint: attrs.hint || '',
                    last_message: attrs.last_message || '',
                    message_type: attrs.message_type || 'info',
                    revealed_word: attrs.revealed_word || ''
                };
                
                this.debugLog('📈 Parsed game data', gameData);
                
                this.lastUpdate = new Date().toLocaleTimeString();
                
                // Trigger update callback
                if (this.onStateUpdate) {
                    this.onStateUpdate(gameData);
                }
                
                // Update connection status
                if (this.onConnectionChange) {
                    this.onConnectionChange('connected', 'Connected to Home Assistant');
                }
                
                return true;
            }
            
            // Also get word length from select entity
            const lengthEntity = await this.getEntityState('select.ha_wordplay_word_length_default');
            if (lengthEntity && lengthEntity.state) {
                const entityWordLength = parseInt(lengthEntity.state);
                this.debugLog(`🔢 Word length from select: ${entityWordLength}`);
                
                // Trigger word length update if needed
                if (this.onWordLengthUpdate) {
                    this.onWordLengthUpdate(entityWordLength);
                }
            }
            
        } catch (error) {
            this.debugLog('❌ Failed to refresh game state', error);
            
            if (this.onConnectionChange) {
                this.onConnectionChange('disconnected', '❌ Connection failed');
            }
            
            return false;
        }
    }
    
    /**
     * Parse game state from backend format
     * @param {string} gameStatus - Status from backend
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
     * Start polling for updates
     */
    startPolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(() => {
            this.refreshGameState();
        }, this.pollingInterval);
        
        this.debugLog('⏰ Polling started (1 second intervals)');
        
        // Initial refresh
        this.refreshGameState();
    }
    
    /**
     * Stop polling for updates
     */
    stopPolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            this.debugLog('⏹️ Polling stopped');
        }
    }
    
    /**
     * Check if action is allowed (cooldown)
     * @param {string} action - Action name
     * @returns {boolean} True if allowed
     */
    isActionAllowed(action) {
        return !this.cooldowns[action];
    }
    
    /**
     * Set action cooldown
     * @param {string} action - Action name
     * @param {number} duration - Cooldown duration in ms
     */
    setActionCooldown(action, duration = 500) {
        this.cooldowns[action] = true;
        this.debugLog(`Action cooldown set: ${action} for ${duration}ms`);
        
        setTimeout(() => {
            this.cooldowns[action] = false;
            this.debugLog(`Action cooldown cleared: ${action}`);
        }, duration);
    }
    
    /**
     * Start new game
     * @param {number} wordLength - Word length
     * @returns {Promise} Service response
     */
    async startNewGame(wordLength) {
        return this.callHAService('ha_wordplay', 'new_game', {
            word_length: wordLength
        });
    }
    
    /**
     * Submit a guess
     * @param {string} guess - The guess word
     * @returns {Promise} Service response
     */
    async submitGuess(guess) {
        // Step 1: Set the text input (using default user entity)
        await this.callHAService('text', 'set_value', {
            entity_id: 'text.ha_wordplay_guess_input_default',
            value: guess
        });
        
        // Step 2: Submit the guess
        return this.callHAService('ha_wordplay', 'submit_guess');
    }
    
    /**
     * Get a hint
     * @returns {Promise} Service response
     */
    async getHint() {
        return this.callHAService('ha_wordplay', 'get_hint');
    }
    
    /**
     * Update word length selection
     * @param {number} length - New word length
     * @returns {Promise} Service response
     */
    async updateWordLength(length) {
        return this.callHAService('select', 'select_option', {
            entity_id: 'select.ha_wordplay_word_length_default',
            option: length.toString()
        });
    }
    
    /**
     * Set callback for state updates
     * @param {Function} callback - Callback function
     */
    setStateUpdateCallback(callback) {
        this.onStateUpdate = callback;
    }
    
    /**
     * Set callback for connection changes
     * @param {Function} callback - Callback function
     */
    setConnectionChangeCallback(callback) {
        this.onConnectionChange = callback;
    }
    
    /**
     * Set callback for word length updates
     * @param {Function} callback - Callback function
     */
    setWordLengthUpdateCallback(callback) {
        this.onWordLengthUpdate = callback;
    }
}

// Global HA API instance
let wordplayHA = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    wordplayHA = new WordPlayHA();
    window.wordplayHA = () => wordplayHA;
    console.log('🔌 WordPlay HA API ready');
});