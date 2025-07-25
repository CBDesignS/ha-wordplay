/**
 * WordPlay Home Assistant API - Backend Integration - Multi-User Version
 * FIXED: iPhone app compatibility and user context handling
 */

class WordPlayHA {
    constructor() {
        // API configuration
        this.accessToken = null;
        this.updateInterval = null;
        this.lastUpdate = 'Never';
        
        // User identification - for entity naming only
        this.currentUser = null;
        
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
    
    async init() {
        this.accessToken = this.getAccessToken();
        this.debugLog(`🔑 Access token: ${this.accessToken ? 'Present' : 'Missing'}`);
        
        // Get current user for entity naming
        await this.identifyCurrentUser();
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
     * Identify the current user from HA - for entity naming only
     * @returns {Promise<string>} User ID
     */
    async identifyCurrentUser() {
        try {
            // Check if user was already detected by wordplay-user-detect.js
            if (window.WORDPLAY_USER_ID) {
                this.currentUser = window.WORDPLAY_USER_ID;
                this.debugLog(`👤 User from pre-detection: ${window.WORDPLAY_USER_NAME} (${this.currentUser})`);
                return this.currentUser;
            }
            
            // Wait for user detection to complete
            if (window.waitForWordPlayUser) {
                const userInfo = await window.waitForWordPlayUser();
                this.currentUser = userInfo.userId;
                this.debugLog(`👤 User from detection promise: ${userInfo.userName} (${this.currentUser})`);
                return this.currentUser;
            }
            
            const headers = {'Content-Type': 'application/json'};
            if (this.accessToken) {
                headers['Authorization'] = `Bearer ${this.accessToken}`;
            }
            
            // Try to get user context from the token
            // First, try to call a service to identify the user context
            try {
                // iPhone app fix: Use config/core/check_config as a simple test
                const testResponse = await fetch('/api/config/core/check_config', {
                    method: 'GET',
                    headers: headers
                });
                
                if (testResponse.ok) {
                    this.debugLog('✅ API connection verified for iPhone app');
                }
            } catch (testError) {
                this.debugLog('⚠️ Initial API test failed (iPhone app may need reconnection)');
            }
            
            // List all entities to find WordPlay entities for this session
            const response = await fetch('/api/states', {
                method: 'GET',
                headers: headers
            });
            
            if (response.ok) {
                const states = await response.json();
                
                // Find all WordPlay button entities
                const wordplayButtons = states.filter(state => 
                    state.entity_id.startsWith('button.ha_wordplay_game_')
                );
                
                this.debugLog(`Found ${wordplayButtons.length} WordPlay button entities`);
                
                // If we have entities, try to determine which user this session belongs to
                if (wordplayButtons.length > 0) {
                    // Look for user entities in order of preference
                    for (const button of wordplayButtons) {
                        const entityId = button.entity_id;
                        const userId = entityId.replace('button.ha_wordplay_game_', '');
                        
                        // Skip 'default' for now and use actual user entities
                        if (userId !== 'default' && userId.length > 20) {
                            // This looks like a real user ID (they're typically long hex strings)
                            this.currentUser = userId;
                            this.debugLog(`👤 Found user entity for naming: ${this.currentUser}`);
                            break;
                        }
                    }
                    
                    // If no user entity found, fall back to default
                    if (!this.currentUser) {
                        const defaultButton = wordplayButtons.find(btn => 
                            btn.entity_id === 'button.ha_wordplay_game_default'
                        );
                        
                        if (defaultButton) {
                            this.currentUser = 'default';
                            this.debugLog('👤 Using default user for naming');
                        }
                    }
                } else {
                    this.currentUser = 'default';
                    this.debugLog('👤 No entities found, using default user for naming');
                }
            } else {
                this.currentUser = 'default';
                this.debugLog('⚠️ Could not list entities, using default user for naming');
            }
            
        } catch (error) {
            this.debugLog('❌ Error identifying user:', error);
            this.currentUser = 'default';
        }
        
        return this.currentUser;
    }
    
    /**
     * Get entity ID for current user
     * @param {string} entityType - Base entity type (e.g., 'button.ha_wordplay_game')
     * @returns {string} User-specific entity ID
     */
    getUserEntityId(entityType) {
        const baseName = entityType.replace('_default', '').replace(/_[a-f0-9-]+$/, '');
        return `${baseName}_${this.currentUser}`;
    }
    
    /**
     * Call Home Assistant service - iPhone app compatible
     * @param {string} domain - Service domain
     * @param {string} service - Service name
     * @param {Object} data - Service data
     * @returns {Promise} Service response
     */
    async callHAService(domain, service, data = {}) {
        const serviceData = { ...data };
        
        this.debugLog(`🔧 Calling HA service: ${domain}.${service} (user context automatic)`, serviceData);
        
        const headers = {'Content-Type': 'application/json'};
        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        try {
            const response = await fetch(`/api/services/${domain}/${service}`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(serviceData)
            });

            if (!response.ok) {
                this.debugLog(`❌ Service call failed: ${response.status}`);
                
                // iPhone app specific: Try to get more error details
                try {
                    const errorText = await response.text();
                    this.debugLog(`❌ Error details: ${errorText}`);
                } catch (e) {
                    // Ignore if we can't get error text
                }
                
                throw new Error(`Service call failed: ${response.status}`);
            }

            const result = await response.json();
            this.debugLog(`✅ Service call successful`, result);
            return result;
            
        } catch (error) {
            this.debugLog(`❌ Service call error:`, error);
            
            // iPhone app fix: Retry once with a delay
            if (error.message.includes('Failed to fetch') || error.message.includes('Network')) {
                this.debugLog('🔄 Retrying service call for iPhone app...');
                await new Promise(resolve => setTimeout(resolve, 500));
                
                try {
                    const retryResponse = await fetch(`/api/services/${domain}/${service}`, {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify(serviceData)
                    });
                    
                    if (retryResponse.ok) {
                        const retryResult = await retryResponse.json();
                        this.debugLog(`✅ Retry successful`, retryResult);
                        return retryResult;
                    }
                } catch (retryError) {
                    this.debugLog(`❌ Retry also failed:`, retryError);
                }
            }
            
            throw error;
        }
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

        try {
            const response = await fetch(`/api/states/${entityId}`, {
                method: 'GET',
                headers: headers
            });

            if (!response.ok) {
                throw new Error(`Entity fetch failed: ${response.status}`);
            }

            return response.json();
        } catch (error) {
            // iPhone app fix: Retry once
            this.debugLog('🔄 Retrying entity fetch for iPhone app...');
            await new Promise(resolve => setTimeout(resolve, 500));
            
            const retryResponse = await fetch(`/api/states/${entityId}`, {
                method: 'GET',
                headers: headers
            });
            
            if (!retryResponse.ok) {
                throw new Error(`Entity fetch failed after retry: ${retryResponse.status}`);
            }
            
            return retryResponse.json();
        }
    }
    
    /**
     * Refresh game state from backend
     * @returns {Promise<boolean>} Success status
     */
    async refreshGameState() {
        try {
            this.debugLog('🔄 Refreshing game state from user-specific button entity...');
            
            // Get game data from user's button entity
            const buttonEntityId = this.getUserEntityId('button.ha_wordplay_game');
            const buttonEntity = await this.getEntityState(buttonEntityId);
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
                    revealed_word: attrs.revealed_word || '',
                    user_id: attrs.user_id || this.currentUser
                };
                
                this.debugLog('📈 Parsed game data', gameData);
                
                this.lastUpdate = new Date().toLocaleTimeString();
                
                // Trigger update callback
                if (this.onStateUpdate) {
                    this.onStateUpdate(gameData);
                }
                
                // Update connection status
                if (this.onConnectionChange) {
                    this.onConnectionChange('connected', `Connected (User: ${this.currentUser})`);
                }
                
                // Update our user ID from the backend if available
                if (attrs.user_id && attrs.user_id !== this.currentUser) {
                    this.currentUser = attrs.user_id;
                    this.debugLog(`👤 User updated from backend: ${this.currentUser}`);
                }
                
                // Dispatch custom event for stats update
                document.dispatchEvent(new CustomEvent('wordplayGameStateChanged', {
                    detail: { gameData, user: this.currentUser }
                }));
                
                return true;
            }
            
            // Also get word length from user's select entity
            const lengthEntityId = this.getUserEntityId('select.ha_wordplay_word_length');
            const lengthEntity = await this.getEntityState(lengthEntityId);
            if (lengthEntity && lengthEntity.state) {
                const entityWordLength = parseInt(lengthEntity.state);
                this.debugLog(`🔢 Word length from user's select: ${entityWordLength}`);
                
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
        
        this.debugLog(`⏰ Polling started for user ${this.currentUser} (1 second intervals)`);
        
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
        // iPhone app fix: Add small delay before text input update
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Step 1: Set the user's text input
        const textEntityId = this.getUserEntityId('text.ha_wordplay_guess_input');
        await this.callHAService('text', 'set_value', {
            entity_id: textEntityId,
            value: guess
        });
        
        // iPhone app fix: Add delay between calls
        await new Promise(resolve => setTimeout(resolve, 200));
        
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
        const selectEntityId = this.getUserEntityId('select.ha_wordplay_word_length');
        return this.callHAService('select', 'select_option', {
            entity_id: selectEntityId,
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
    console.log('🔌 WordPlay HA API (Multi-User + iPhone Fix) ready');
});