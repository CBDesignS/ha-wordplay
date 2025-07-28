/**
 * WordPlay Home Assistant API - Backend Integration - Multi-User Version
 * FIXED: No default fallback - requires valid user authentication
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
        
        if (!this.accessToken) {
            this.debugLog('❌ No access token found - cannot initialize');
            this.handleAuthenticationError();
            return;
        }
        
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
     * Handle authentication errors
     */
    handleAuthenticationError() {
        if (this.onConnectionChange) {
            this.onConnectionChange('disconnected', '❌ Authentication failed - no access token');
        }
        
        // Show error in UI
        const connectionStatus = document.getElementById('connectionStatus');
        if (connectionStatus) {
            connectionStatus.textContent = '❌ Authentication failed - no access token';
            connectionStatus.className = 'connection-status disconnected';
        }
    }
    
    /**
     * Identify the current user from HA - for entity naming only
     * @returns {Promise<string>} User ID
     */
    async identifyCurrentUser() {
        try {
            // FIXED: First try the new get_current_user service to get the actual logged-in user
            this.debugLog('🔍 Attempting to identify current user via service...');
            
            try {
                const userResponse = await this.callHAService('ha_wordplay', 'get_current_user');
                
                if (userResponse && userResponse.user_id && userResponse.is_authorized) {
                    this.currentUser = userResponse.user_id;
                    this.debugLog(`👤 Current user identified via service: ${userResponse.user_name} (${this.currentUser})`);
                    return this.currentUser;
                } else if (userResponse && userResponse.error) {
                    this.debugLog(`❌ User service error: ${userResponse.error}`);
                }
            } catch (serviceError) {
                this.debugLog('⚠️ get_current_user service failed, trying fallback methods...');
            }
            
            // FIXED: Check if user was already detected by wordplay_user_detect.js and USE IT
            if (window.WORDPLAY_USER_ID) {
                this.currentUser = window.WORDPLAY_USER_ID;
                this.debugLog(`👤 User from pre-detection: ${window.WORDPLAY_USER_NAME} (${this.currentUser})`);
                return this.currentUser;
            }
            
            // Wait for user detection to complete
            if (window.waitForWordPlayUser) {
                try {
                    const userInfo = await window.waitForWordPlayUser();
                    this.currentUser = userInfo.userId;
                    this.debugLog(`👤 User from detection promise: ${userInfo.userName} (${this.currentUser})`);
                    return this.currentUser;
                } catch (userError) {
                    this.debugLog('❌ User detection failed:', userError);
                    throw new Error('User authentication required');
                }
            }
            
            // FIXED: DO NOT do API-based detection that overwrites the correct user
            // The code below was finding Chris's entities and overwriting Joanne
            
            // If we get here, no user was detected
            throw new Error('No valid user context found');
            
        } catch (error) {
            this.debugLog('❌ Error identifying user:', error);
            this.handleUserIdentificationError();
            throw error;
        }
    }
    
    /**
     * Handle user identification errors
     */
    handleUserIdentificationError() {
        if (this.onConnectionChange) {
            this.onConnectionChange('disconnected', '❌ User authentication failed');
        }
        
        // Disable polling
        this.stopPolling();
    }
    
    /**
     * Get entity ID for current user
     * @param {string} entityType - Base entity type (e.g., 'button.ha_wordplay_game')
     * @returns {string} User-specific entity ID
     */
    getUserEntityId(entityType) {
        if (!this.currentUser) {
            throw new Error('No user identified - cannot get entity ID');
        }
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
        if (!this.currentUser && service !== 'get_current_user') {
            throw new Error('No user identified - cannot call services');
        }
        
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
            if (!this.currentUser) {
                this.debugLog('❌ Cannot refresh game state - no user identified');
                return false;
            }
            
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
        if (!this.currentUser) {
            this.debugLog('❌ Cannot start polling - no user identified');
            return;
        }
        
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
    console.log('🔌 WordPlay HA API (Multi-User - No Default) ready');
});