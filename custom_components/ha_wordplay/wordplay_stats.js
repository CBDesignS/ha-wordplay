// Rev 2.0 - Added i18n support for consistency with other modules
/**
 * WordPlay Stats - Statistics Display and Management
 * Handles fetching and displaying user game statistics
 */

class WordPlayStats {
    constructor() {
        // Cache for stats data
        this.currentStats = null;
        this.statsContainer = null;
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.debugLog('📊 WordPlay Stats module initialized');
        
        // Get container element
        this.statsContainer = document.getElementById('userStatsSimple');
        
        // Set up observer for landing screen changes
        this.setupScreenObserver();
        
        // FIXED: Wait for user to be identified before loading stats
        this.waitForUserAndLoadStats();
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
     * Get translated text using i18n system
     * @param {string} key - Translation key
     * @param {Object} params - Optional parameters
     * @returns {string} Translated text
     */
    t(key, params = {}) {
        if (window.wordplayI18n && window.wordplayI18n().isReady()) {
            return window.wordplayI18n().t(key, params);
        }
        return key; // Fallback to key if i18n not ready
    }
    
    /**
     * Wait for user identification then load stats
     */
    async waitForUserAndLoadStats() {
        try {
            // Wait for user detection to complete
            if (window.waitForWordPlayUser) {
                const userInfo = await window.waitForWordPlayUser();
                this.debugLog('📊 User identified for stats:', userInfo);
                
                // Check if on landing screen
                const landingScreen = document.getElementById('landingScreen');
                if (landingScreen && landingScreen.classList.contains('active')) {
                    // Small delay to ensure HA API is ready
                    setTimeout(() => this.updateStats(), 500);
                }
            } else {
                // Fallback: wait a bit and try again
                setTimeout(() => this.waitForUserAndLoadStats(), 500);
            }
        } catch (error) {
            this.debugLog('❌ Error waiting for user:', error);
            // Try again after delay
            setTimeout(() => this.waitForUserAndLoadStats(), 1000);
        }
    }
    
    /**
     * Fetch and update stats display
     */
    async updateStats() {
        // Wait for HA API to be ready
        if (!window.wordplayHA || !window.wordplayHA().accessToken) {
            this.debugLog('⏳ HA API not ready yet, waiting...');
            setTimeout(() => this.updateStats(), 1000);
            return;
        }
        
        try {
            // Get user-specific sensor
            const ha = window.wordplayHA();
            const sensorEntityId = `sensor.ha_wordplay_stats_${ha.currentUser}`;
            
            this.debugLog(`📊 Fetching stats for sensor: ${sensorEntityId}`);
            
            const response = await fetch('/api/states/' + sensorEntityId, {
                headers: {
                    'Authorization': `Bearer ${ha.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const entity = await response.json();
            
            if (entity && entity.attributes) {
                this.debugLog('📊 Raw stats entity:', entity);
                
                // Extract stats from sensor attributes
                const stats = {
                    games_played: entity.attributes.games_played || 0,
                    games_won: entity.attributes.games_won || 0,
                    win_rate: entity.attributes.win_rate_display || entity.attributes.win_rate || '0%',
                    current_streak: entity.attributes.current_streak || 0
                };
                
                // If win_rate is a number, format it
                if (typeof stats.win_rate === 'number') {
                    stats.win_rate = `${stats.win_rate}%`;
                }
                
                this.currentStats = stats;
                this.displayStats(stats);
                this.debugLog('✅ Stats updated from sensor:', stats);
            } else {
                this.debugLog('📊 No stats found in sensor for user');
                this.displayDefaultStats();
            }
            
        } catch (error) {
            this.debugLog('❌ Error fetching stats:', error);
            
            // Try fallback to button entity
            try {
                const ha = window.wordplayHA();
                const buttonEntityId = `button.ha_wordplay_game_${ha.currentUser}`;
                const response = await fetch('/api/states/' + buttonEntityId, {
                    headers: {
                        'Authorization': `Bearer ${ha.accessToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const entity = await response.json();
                    this.debugLog('📊 Button entity fallback:', entity);
                    
                    // Try multiple possible locations for stats
                    let stats = null;
                    
                    // Check for stats_summary in attributes
                    if (entity && entity.attributes && entity.attributes.stats_summary) {
                        stats = entity.attributes.stats_summary;
                    }
                    // Check for direct stats in attributes
                    else if (entity && entity.attributes && entity.attributes.games_played !== undefined) {
                        stats = {
                            games_played: entity.attributes.games_played || 0,
                            games_won: entity.attributes.games_won || 0,
                            win_rate: entity.attributes.win_rate || '0%',
                            current_streak: entity.attributes.current_streak || 0
                        };
                    }
                    
                    if (stats) {
                        this.currentStats = stats;
                        this.displayStats(stats);
                        this.debugLog('✅ Stats updated from button fallback:', stats);
                        return;
                    }
                }
            } catch (fallbackError) {
                this.debugLog('❌ Fallback also failed:', fallbackError);
            }
            
            this.displayDefaultStats();
        }
    }
    
    /**
     * Display default stats when none found
     */
    displayDefaultStats() {
        const defaultStats = {
            games_played: 0,
            games_won: 0,
            win_rate: '0%',
            current_streak: 0
        };
        this.displayStats(defaultStats);
    }
    
    /**
     * Display stats on the UI
     * @param {Object} stats - Stats object from backend
     */
    displayStats(stats) {
        if (!this.statsContainer) {
            this.debugLog('❌ Stats container not found');
            return;
        }
        
        this.debugLog('🎯 Displaying stats:', stats);
        
        // Update basic stats
        this.updateStatElement('statGamesPlayed', stats.games_played || 0);
        this.updateStatElement('statGamesWon', stats.games_won || 0);
        this.updateStatElement('statWinRate', stats.win_rate || '0%');
        this.updateStatElement('statStreak', stats.current_streak || 0);
        
        // Show the container with fade-in effect
        this.statsContainer.style.display = 'block';
        
        // Add animation class if first time showing
        if (!this.statsContainer.classList.contains('stats-loaded')) {
            this.statsContainer.classList.add('stats-loaded');
            // Force a reflow to ensure animation plays
            this.statsContainer.offsetHeight;
            this.statsContainer.style.opacity = '0';
            setTimeout(() => {
                this.statsContainer.style.transition = 'opacity 0.5s ease-in';
                this.statsContainer.style.opacity = '1';
            }, 50);
        }
    }
    
    /**
     * Update individual stat element
     * @param {string} elementId - Element ID
     * @param {string|number} value - Stat value
     */
    updateStatElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            this.debugLog(`📊 Updated ${elementId} to ${value}`);
        } else {
            this.debugLog(`❌ Element ${elementId} not found`);
        }
    }
    
    /**
     * Hide stats display
     */
    hideStats() {
        if (this.statsContainer) {
            this.statsContainer.style.display = 'none';
        }
    }
    
    /**
     * Setup observer for landing screen visibility
     */
    setupScreenObserver() {
        // Update stats when landing screen becomes active
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.classList && 
                    mutation.target.classList.contains('landing-screen') && 
                    mutation.target.classList.contains('active')) {
                    this.debugLog('🔄 Landing screen active, updating stats...');
                    // Small delay to ensure everything is loaded
                    setTimeout(() => this.updateStats(), 500);
                }
            });
        });
        
        const landingScreen = document.getElementById('landingScreen');
        if (landingScreen) {
            observer.observe(landingScreen, { 
                attributes: true, 
                attributeFilter: ['class'] 
            });
        }
        
        // Also listen for custom events that might indicate stats need updating
        document.addEventListener('wordplayUserReady', () => {
            this.debugLog('🔄 User ready event, updating stats...');
            setTimeout(() => this.updateStats(), 1000);
        });
        
        // Listen for game state changes
        document.addEventListener('wordplayGameStateChanged', (event) => {
            this.debugLog('🔄 Game state changed, updating stats...', event.detail);
            // Update stats after a win or loss
            if (event.detail && event.detail.gameData) {
                const gameState = event.detail.gameData.game_state;
                if (gameState === 'won' || gameState === 'lost') {
                    // Wait a bit for backend to update
                    setTimeout(() => this.updateStats(), 2000);
                }
            }
        });
        
        // Force refresh when returning to landing screen
        document.addEventListener('click', (e) => {
            if (e.target && e.target.id === 'backBtn') {
                this.debugLog('🔄 Back button clicked, will refresh stats...');
                setTimeout(() => this.updateStats(), 1000);
            }
        });
    }
    
    /**
     * Start automatic stats refresh
     * @param {number} interval - Refresh interval in ms
     */
    startAutoRefresh(interval = 30000) {
        this.stopAutoRefresh();
        this.updateInterval = setInterval(() => {
            this.updateStats();
        }, interval);
        this.debugLog(`🔄 Auto-refresh started (${interval}ms)`);
    }
    
    /**
     * Stop automatic stats refresh
     */
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            this.debugLog('⏹️ Auto-refresh stopped');
        }
    }
    
    /**
     * Get current stats
     * @returns {Object|null} Current stats object
     */
    getCurrentStats() {
        return this.currentStats;
    }
    
    /**
     * Force refresh stats
     */
    async forceRefresh() {
        this.debugLog('🔄 Force refreshing stats...');
        await this.updateStats();
    }
    
    // Future expansion methods
    
    /**
     * Display detailed stats modal
     */
    showDetailedStats() {
        // TODO: Implement detailed stats view
        this.debugLog('📊 Detailed stats view not yet implemented');
    }
    
    /**
     * Export stats to CSV
     */
    exportStats() {
        // TODO: Implement stats export
        this.debugLog('📤 Stats export not yet implemented');
    }
    
    /**
     * Display guess distribution chart
     */
    showGuessDistribution() {
        // TODO: Implement guess distribution visualization
        this.debugLog('📈 Guess distribution chart not yet implemented');
    }
}

// Global stats instance
let wordplayStats = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for HA API to be ready first
    setTimeout(() => {
        wordplayStats = new WordPlayStats();
        window.wordplayStats = () => wordplayStats;
        console.log('📊 WordPlay Stats module ready');
    }, 500);
});
