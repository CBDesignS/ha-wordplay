/**
 * WordPlay User Detection - Runs FIRST to get current user
 * Sets global variables for other scripts to use
 */

// Global variables that other scripts will use
window.WORDPLAY_USER_ID = null;
window.WORDPLAY_USER_NAME = null;

// Detect user immediately
(function() {
    console.log('[WordPlay User Detect] Starting user detection...');
    
    try {
        // Method 1: Get from parent HA frame
        if (window.parent && window.parent !== window) {
            // Try to access parent's HA object
            const parentDoc = window.parent.document;
            if (parentDoc) {
                const haMain = parentDoc.querySelector('home-assistant');
                if (haMain && haMain.hass && haMain.hass.user) {
                    window.WORDPLAY_USER_ID = haMain.hass.user.id;
                    window.WORDPLAY_USER_NAME = haMain.hass.user.name;
                    console.log(`[WordPlay User Detect] ✅ Found user from parent HA: ${window.WORDPLAY_USER_NAME} (${window.WORDPLAY_USER_ID})`);
                    return;
                }
            }
        }
    } catch (error) {
        console.log('[WordPlay User Detect] Could not access parent frame:', error);
    }
    
    // Method 2: Check URL parameters as fallback
    const urlParams = new URLSearchParams(window.location.search);
    const urlUserId = urlParams.get('user_id');
    const urlUserName = urlParams.get('user_name');
    
    if (urlUserId) {
        window.WORDPLAY_USER_ID = urlUserId;
        window.WORDPLAY_USER_NAME = urlUserName || 'Player';
        console.log(`[WordPlay User Detect] ✅ Found user from URL: ${window.WORDPLAY_USER_NAME} (${window.WORDPLAY_USER_ID})`);
        return;
    }
    
    // Method 3: Default fallback
    window.WORDPLAY_USER_ID = 'default';
    window.WORDPLAY_USER_NAME = 'Guest Player';
    console.log('[WordPlay User Detect] ⚠️ Using default user');
    
})();