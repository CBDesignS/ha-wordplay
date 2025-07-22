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
            return;
        }
        
        const ha = window.wordplayHA();
        if (!ha.currentUser || ha.currentUser === 'default') {
            // Hide stats for default/guest users
            this.hideStats();
            return;
        }
        
        try {
            // Get the button entity to read stats
            const buttonEntityId = `button.ha_wordplay_game_${ha.currentUser}`;
            
            const response = await fetch('/api/states/' + buttonEntityId, {
                headers: {
                    'Authorization': `Bearer ${ha.accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const entity = await response.json();
            
            if (entity && entity.attributes && entity.attributes.stats_summary) {
                this.currentStats = entity.attributes.stats_summary;
                this.displayStats(this.currentStats);
                this.debugLog('✅ Stats updated:', this.currentStats);
            } else {
                this.debugLog('📊 No stats found for user');
                this.hideStats();
            }
            
        } catch (error) {
            this.debugLog('❌ Error fetching stats:', error);
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
        
        // Show the container
        this.statsContainer.style.display = 'block';
        
        // Add animation class if first time showing
        if (!this.statsContainer.classList.contains('stats-loaded')) {
            this.statsContainer.classList.add('stats-loaded');
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
                    this.updateStats();
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
        }, 1000);
    }, 500);
});