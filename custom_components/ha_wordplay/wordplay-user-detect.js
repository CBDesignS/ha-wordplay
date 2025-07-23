/**
 * WordPlay User Detection - FIXED: Robust retry logic for reliable user context
 * Sets global variables for other scripts to use with proper timing handling
 */

// Global variables that other scripts will use
window.WORDPLAY_USER_ID = null;
window.WORDPLAY_USER_NAME = null;
window.WORDPLAY_USER_READY = false;

// Detection state tracking
let detectionAttempts = 0;
const MAX_DETECTION_ATTEMPTS = 50; // 5 seconds with 100ms intervals
const DETECTION_INTERVAL = 100; // milliseconds

// Enhanced user detection with retry logic
(function() {
    console.log('[WordPlay User Detect] Starting robust user detection...');
    
    /**
     * Wait for Home Assistant hass object to be available
     * @returns {Promise<Object>} HA hass object
     */
    async function waitForHAObject() {
        return new Promise((resolve, reject) => {
            const checkHA = () => {
                detectionAttempts++;
                
                try {
                    // Method 1: Check parent frame HA object
                    if (window.parent && window.parent !== window) {
                        const parentDoc = window.parent.document;
                        if (parentDoc) {
                            const haMain = parentDoc.querySelector('home-assistant');
                            if (haMain && haMain.hass && haMain.hass.user && haMain.hass.user.id) {
                                console.log('[WordPlay User Detect] ✅ Found HA object in parent frame');
                                resolve({
                                    source: 'parent_frame',
                                    hass: haMain.hass,
                                    user: haMain.hass.user
                                });
                                return;
                            }
                        }
                    }
                    
                    // Method 2: Check if we're in an iframe and can access parent context
                    if (window.parent && window.parent.hass && window.parent.hass.user) {
                        console.log('[WordPlay User Detect] ✅ Found HA object in parent window');
                        resolve({
                            source: 'parent_window',
                            hass: window.parent.hass,
                            user: window.parent.hass.user
                        });
                        return;
                    }
                    
                    // Method 3: Check current window (unlikely but possible)
                    if (window.hass && window.hass.user && window.hass.user.id) {
                        console.log('[WordPlay User Detect] ✅ Found HA object in current window');
                        resolve({
                            source: 'current_window',
                            hass: window.hass,
                            user: window.hass.user
                        });
                        return;
                    }
                    
                } catch (error) {
                    console.log(`[WordPlay User Detect] Access denied attempt ${detectionAttempts}:`, error.message);
                }
                
                // Retry logic
                if (detectionAttempts < MAX_DETECTION_ATTEMPTS) {
                    setTimeout(checkHA, DETECTION_INTERVAL);
                } else {
                    console.log('[WordPlay User Detect] ⚠️ Max attempts reached, falling back to URL/default');
                    resolve(null); // Fall back to other methods
                }
            };
            
            checkHA();
        });
    }
    
    /**
     * Extract user info from URL parameters
     * @returns {Object|null} User info from URL
     */
    function getUserFromURL() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const urlUserId = urlParams.get('user_id');
            const urlUserName = urlParams.get('user_name');
            
            if (urlUserId) {
                console.log('[WordPlay User Detect] ✅ Found user in URL parameters');
                return {
                    source: 'url_params',
                    user_id: urlUserId,
                    user_name: urlUserName || 'Player'
                };
            }
        } catch (error) {
            console.log('[WordPlay User Detect] Error parsing URL:', error);
        }
        
        return null;
    }
    
    /**
     * Main detection logic with fallback chain
     */
    async function detectUser() {
        try {
            // Step 1: Try to get user from HA object with retry logic
            console.log('[WordPlay User Detect] Step 1: Attempting HA object detection...');
            const haResult = await waitForHAObject();
            
            if (haResult && haResult.user && haResult.user.id) {
                window.WORDPLAY_USER_ID = haResult.user.id;
                window.WORDPLAY_USER_NAME = haResult.user.name || 'HA User';
                console.log(`[WordPlay User Detect] ✅ User from ${haResult.source}: ${window.WORDPLAY_USER_NAME} (${window.WORDPLAY_USER_ID})`);
                markUserReady();
                return;
            }
            
            // Step 2: Try URL parameters
            console.log('[WordPlay User Detect] Step 2: Checking URL parameters...');
            const urlResult = getUserFromURL();
            
            if (urlResult) {
                window.WORDPLAY_USER_ID = urlResult.user_id;
                window.WORDPLAY_USER_NAME = urlResult.user_name;
                console.log(`[WordPlay User Detect] ✅ User from ${urlResult.source}: ${window.WORDPLAY_USER_NAME} (${window.WORDPLAY_USER_ID})`);
                markUserReady();
                return;
            }
            
            // Step 3: Try API-based detection with access token
            console.log('[WordPlay User Detect] Step 3: Attempting API-based detection...');
            const apiResult = await detectUserFromAPI();
            
            if (apiResult) {
                window.WORDPLAY_USER_ID = apiResult.user_id;
                window.WORDPLAY_USER_NAME = apiResult.user_name;
                console.log(`[WordPlay User Detect] ✅ User from API: ${window.WORDPLAY_USER_NAME} (${window.WORDPLAY_USER_ID})`);
                markUserReady();
                return;
            }
            
            // Step 4: Default fallback
            console.log('[WordPlay User Detect] Step 4: Using default fallback');
            window.WORDPLAY_USER_ID = 'default';
            window.WORDPLAY_USER_NAME = 'Guest Player';
            console.log('[WordPlay User Detect] ⚠️ Using default user');
            markUserReady();
            
        } catch (error) {
            console.error('[WordPlay User Detect] Error in detection:', error);
            // Even on error, provide defaults
            window.WORDPLAY_USER_ID = 'default';
            window.WORDPLAY_USER_NAME = 'Guest Player';
            markUserReady();
        }
    }
    
    /**
     * Try to detect user via API call
     * @returns {Promise<Object|null>} User info from API
     */
    async function detectUserFromAPI() {
        try {
            // Get access token from URL
            const urlParams = new URLSearchParams(window.location.search);
            const accessToken = urlParams.get('access_token');
            
            if (!accessToken) {
                console.log('[WordPlay User Detect] No access token for API detection');
                return null;
            }
            
            // Try to call HA API to identify user
            const response = await fetch('/api/states', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                console.log('[WordPlay User Detect] API call failed:', response.status);
                return null;
            }
            
            const states = await response.json();
            
            // Look for WordPlay entities to infer user
            const wordplayEntities = states.filter(state => 
                state.entity_id.startsWith('button.ha_wordplay_game_') ||
                state.entity_id.startsWith('sensor.ha_wordplay_stats_')
            );
            
            console.log(`[WordPlay User Detect] Found ${wordplayEntities.length} WordPlay entities`);
            
            if (wordplayEntities.length > 0) {
                // Try to find a real user entity (not default)
                for (const entity of wordplayEntities) {
                    const entityId = entity.entity_id;
                    let userId = null;
                    
                    if (entityId.startsWith('button.ha_wordplay_game_')) {
                        userId = entityId.replace('button.ha_wordplay_game_', '');
                    } else if (entityId.startsWith('sensor.ha_wordplay_stats_')) {
                        userId = entityId.replace('sensor.ha_wordplay_stats_', '');
                    }
                    
                    if (userId && userId !== 'default' && userId.length > 10) {
                        // Check if entity has user name in attributes
                        const userName = entity.attributes?.user_name || entity.attributes?.friendly_name || 'Player';
                        
                        return {
                            user_id: userId,
                            user_name: userName
                        };
                    }
                }
                
                // Fallback to default entity if found
                const defaultEntity = wordplayEntities.find(e => 
                    e.entity_id.includes('_default')
                );
                
                if (defaultEntity) {
                    return {
                        user_id: 'default',
                        user_name: 'Guest Player'
                    };
                }
            }
            
        } catch (error) {
            console.log('[WordPlay User Detect] API detection error:', error);
        }
        
        return null;
    }
    
    /**
     * Mark user detection as complete and notify other scripts
     */
    function markUserReady() {
        window.WORDPLAY_USER_READY = true;
        
        // Dispatch custom event for other scripts
        const event = new CustomEvent('wordplayUserReady', {
            detail: {
                userId: window.WORDPLAY_USER_ID,
                userName: window.WORDPLAY_USER_NAME
            }
        });
        document.dispatchEvent(event);
        
        console.log(`[WordPlay User Detect] 🎯 User detection complete: ${window.WORDPLAY_USER_NAME} (${window.WORDPLAY_USER_ID})`);
    }
    
    /**
     * Provide a promise-based API for other scripts
     */
    window.waitForWordPlayUser = function() {
        return new Promise((resolve) => {
            if (window.WORDPLAY_USER_READY) {
                resolve({
                    userId: window.WORDPLAY_USER_ID,
                    userName: window.WORDPLAY_USER_NAME
                });
            } else {
                document.addEventListener('wordplayUserReady', function(event) {
                    resolve(event.detail);
                }, { once: true });
            }
        });
    };
    
    // Start detection immediately
    detectUser();
    
})();

// Provide debugging information
window.getWordPlayUserDebug = function() {
    return {
        userId: window.WORDPLAY_USER_ID,
        userName: window.WORDPLAY_USER_NAME,
        ready: window.WORDPLAY_USER_READY,
        attempts: detectionAttempts,
        maxAttempts: MAX_DETECTION_ATTEMPTS
    };
};