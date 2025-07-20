/**
 * WordPlay Home Assistant API - Backend Integration - Multi-User Version
 * Handles all communication with Home Assistant backend for specific users
 */

class WordPlayHA {
    constructor() {
        // API configuration
        this.accessToken = null;
        this.updateInterval = null;
        this.lastUpdate = 'Never';
        
        // User identification
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
        
        // Get current user
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
     * Identify the current user from HA
     * @returns {Promise<string>} User ID
     */
    async identifyCurrentUser() {
        try {
            this.debugLog('🔍 Starting user identification process...');
            
            // Method 0: Check if user ID was passed in URL (most reliable!)
            const urlParams = new URLSearchParams(window.location.search);
            const urlUserId = urlParams.get('user_id');
            const urlUserName = urlParams.get('user_name');
            
            if (urlUserId) {
                this.currentUser = urlUserId;
                this.debugLog(`👤 User ID from URL: ${this.currentUser} (${urlUserName})`);
                return this.currentUser;
            }
            
            // Method 1: Try to get current user info from HA API
            const headers = {'Content-Type': 'application/json'};
            if (this.accessToken) {
                headers['Authorization'] = `Bearer ${this.accessToken}`;
            }
            
            // First, try to get the current user's information
            try {
                const userResponse = await fetch('/api/config', {
                    method: 'GET',
                    headers: headers
                });
                
                if (userResponse.ok) {
                    const configData = await userResponse.json();
                    this.debugLog('📊 Config data received:', configData);
                    
                    // The config endpoint doesn't directly give us the user ID
                    // So we need to use a different approach
                }
            } catch (error) {
                this.debugLog('⚠️ Could not get config data:', error);
            }
            
            // Method 2: Get the frontend user info if available
            try {
                // Check if we're in an iframe and can access parent HA
                if (window.parent && window.parent !== window) {
                    const parentDoc = window.parent.document;
                    if (parentDoc) {
                        // Try to get the hass object from parent
                        const haMain = parentDoc.querySelector('home-assistant');
                        if (haMain && haMain.hass && haMain.hass.user) {
                            const userId = haMain.hass.user.id;
                            if (userId) {
                                this.currentUser = userId;
                                this.debugLog(`👤 Found user ID from parent HA: ${this.currentUser}`);
                                return this.currentUser;
                            }
                        }
                    }
                }
            } catch (error) {
                this.debugLog('⚠️ Could not access parent frame for user info:', error);
            }
            
            // Method 3: Find the correct user by checking which entities we can actually access
            // List all entities to find WordPlay entities
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
                
                // Now we need to determine which user we are
                // Try to call a service and see which user context we get
                for (const button of wordplayButtons) {
                    const entityId = button.entity_id;
                    const userId = entityId.replace('button.ha_wordplay_game_', '');
                    
                    // Skip default for now
                    if (userId === 'default') continue;
                    
                    // Check if this button has an active game or recent activity
                    if (button.attributes && button.attributes.user_id === userId) {
                        // Try to verify we can access this user's entities
                        const textEntityId = `text.ha_wordplay_guess_input_${userId}`;
                        const textEntity = states.find(s => s.entity_id === textEntityId);
                        
                        if (textEntity) {
                            // Found a matching set of entities, let's test if we can write to it
                            try {
                                // Make a test call to see if we get an error
                                const testResponse = await fetch(`/api/states/${textEntityId}`, {
                                    method: 'GET',
                                    headers: headers
                                });
                                
                                if (testResponse.ok) {
                                    // We can access this entity, this might be our user
                                    this.currentUser = userId;
                                    this.debugLog(`👤 Found accessible user entity: ${this.currentUser}`);
                                    
                                    // Double-check by looking at any active game state
                                    if (button.attributes.game_status && 
                                        button.attributes.game_status !== 'Ready to Play') {
                                        // This user has an active game, likely ours
                                        this.debugLog(`✅ Confirmed user ${this.currentUser} has active game`);
                                        return this.currentUser;
                                    }
                                }
                            } catch (error) {
                                this.debugLog(`Cannot access entities for user ${userId}`);
                            }
                        }
                    }
                }
                
                // If no active games found, we need another approach
                // Let's check which user's services we can actually call
                if (!this.currentUser && wordplayButtons.length > 0) {
                    this.debugLog('🔍 No active games found, testing service access...');
                    
                    // We'll determine user by making a test service call
                    // The backend will use call.context.user_id to identify us
                    try {
                        // Call get_hint service which should fail gracefully if no game
                        const hintResponse = await this.callHAService('ha_wordplay', 'get_hint');
                        this.debugLog('🎯 Hint service response received');
                        
                        // After this call, check entities again to see which one was updated
                        await new Promise(resolve => setTimeout(resolve, 500)); // Wait for state update
                        
                        // Re-fetch states
                        const statesAfter = await this.getEntityState('button.ha_wordplay_game_default');
                        if (statesAfter && statesAfter.attributes && statesAfter.attributes.last_message) {
                            // Default entity was updated, we might be default user
                            const defaultButton = wordplayButtons.find(b => 
                                b.entity_id === 'button.ha_wordplay_game_default'
                            );
                            
                            if (defaultButton) {
                                this.currentUser = 'default';
                                this.debugLog('👤 Identified as default user based on service response');
                                return this.currentUser;
                            }
                        }
                        
                        // Check each user's button for recent updates
                        for (const button of wordplayButtons) {
                            const userId = button.entity_id.replace('button.ha_wordplay_game_', '');
                            if (userId === 'default') continue;
                            
                            const userButton = await this.getEntityState(button.entity_id);
                            if (userButton && userButton.attributes && 
                                userButton.attributes.last_message === "No game in progress") {
                                // This entity was just updated by our service call
                                this.currentUser = userId;
                                this.debugLog(`👤 Identified as user ${this.currentUser} based on service response`);
                                return this.currentUser;
                            }
                        }
                        
                    } catch (error) {
                        this.debugLog('⚠️ Service test failed:', error);
                    }
                }
                
                // Final fallback - if we still don't have a user, default to 'default'
                if (!this.currentUser) {
                    this.currentUser = 'default';
                    this.debugLog('👤 Using default user as final fallback');
                }
                
            } else {
                this.currentUser = 'default';
                this.debugLog('⚠️ Could not list entities, using default user');
            }
            
        } catch (error) {
            this.debugLog('❌ Error identifying user:', error);
            this.currentUser = 'default';
        }
        
        this.debugLog(`🏁 User identification complete: ${this.currentUser}`);
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
     * Call Home Assistant service
     * @param {string} domain - Service domain
     * @param {string} service - Service name
     * @param {Object} data - Service data
     * @returns {Promise} Service response
     */
    async callHAService(domain, service, data = {}) {
        this.debugLog(`🔧 Calling HA service: ${domain}.${service} (user: ${this.currentUser})`, data);
        
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
                
                // Update our user ID from the backend if it's different
                if (attrs.user_id && attrs.user_id !== this.currentUser) {
                    this.debugLog(`⚠️ User mismatch detected! Frontend: ${this.currentUser}, Backend: ${attrs.user_id}`);
                    // Don't update - this might be the issue!
                }
                
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
        // Step 1: Set the user's text input
        const textEntityId = this.getUserEntityId('text.ha_wordplay_guess_input');
        await this.callHAService('text', 'set_value', {
            entity_id: textEntityId,
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
    console.log('🔌 WordPlay HA API (Multi-User) ready');
});