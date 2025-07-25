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
        
        // Also check if landing screen is already active
        const landingScreen = document.getElementById('landingScreen');
        if (landingScreen && landingScreen.classList.contains('active')) {
            // Delay initial load to ensure HA API is ready
            setTimeout(() => this.updateStats(), 1500);
        }
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
     * Fetch and update stats display
     */
    async updateStats() {
        // Wait for HA API to be ready
        if (!window.wordplayHA) {
            this.debugLog('⏳ Waiting for HA API...');
            setTimeout(() => this.updateStats(), 500);
            return;
        }
        
        const ha = window.wordplayHA();
        if (!ha || !ha.currentUser) {
            this.debugLog('⏳ Waiting for user identification...');
            setTimeout(() => this.updateStats(), 500);
            return;
        }
        
        if (ha.currentUser === 'default') {
            // Hide stats for default/guest users
            this.hideStats();
            return;
        }
        
        try {
            // Get the stats sensor entity directly (more reliable than button attributes)
            const statsSensorId = `sensor.ha_wordplay_stats_${ha.currentUser}`;
            
            const response = await fetch('/api/states/' + statsSensorId, {
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
                // Extract stats from sensor attributes
                const stats = {
                    games_played: entity.attributes.games_played || 0,
                    games_won: entity.attributes.games_won || 0,
                    win_rate: entity.attributes.win_rate_display || '0%',
                    current_streak: entity.attributes.current_streak || 0
                };
                
                this.currentStats = stats;
                this.displayStats(stats);
                this.debugLog('✅ Stats updated from sensor:', stats);
            } else {
                this.debugLog('📊 No stats found in sensor for user');
                this.hideStats();
            }
            
        } catch (error) {
            this.debugLog('❌ Error fetching stats:', error);
            
            // Try fallback to button entity
            try {
                const buttonEntityId = `button.ha_wordplay_game_${ha.currentUser}`;
                const response = await fetch('/api/states/' + buttonEntityId, {
                    headers: {
                        'Authorization': `Bearer ${ha.accessToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const entity = await response.json();
                    if (entity && entity.attributes && entity.attributes.stats_summary) {
                        this.currentStats = entity.attributes.stats_summary;
                        this.displayStats(this.currentStats);
                        this.debugLog('✅ Stats updated from button fallback:', this.currentStats);
                        return;
                    }
                }
            } catch (fallbackError) {
                this.debugLog('❌ Fallback also failed:', fallbackError);
            }
            
            this.hideStats();
        }
    }
    
    /**
     * Display stats on the UI
     * @param {Object} stats - Stats object from backend
     */
    displayStats(stats) {
        if (!this.statsContainer) return;
        
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
        document.addEventListener('wordplayGameStateChanged', () => {
            this.debugLog('🔄 Game state changed, updating stats...');
            setTimeout(() => this.updateStats(), 500);
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
        
        // Initial stats update after a delay
        setTimeout(() => {
            wordplayStats.updateStats();
        }, 2000);
    }, 500);
});