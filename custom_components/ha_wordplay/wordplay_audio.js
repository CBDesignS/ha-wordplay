/**
 * WordPlay Audio System - Main Handler
 * Separate audio module for H.A WordPlay that doesn't modify the main game HTML
 * Uses Web Audio API for local device sound generation
 */

class WordPlayAudio {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
        this.volume = 0.3;
        this.soundEffects = new Map();
        this.lastGameState = null;
        this.lastGuessCount = 0;
        this.userInteracted = false;
        
        // Audio preferences
        this.preferences = {
            enabled: true,
            volume: 0.3,
            gameEvents: true,    // New game, win, lose
            guessEvents: true,   // Letter feedback sounds
            uiEvents: false,     // Button clicks (can be annoying)
            errorEvents: true    // Error notifications
        };
        
        this.init();
    }
    
    async init() {
        try {
            // Load preferences from localStorage
            this.loadPreferences();
            
            // Create audio context (requires user interaction first)
            this.setupAudioContext();
            
            // Pre-generate sound effects
            this.generateSoundEffects();
            
            // Setup event listeners for user interaction
            this.setupUserInteractionListeners();
            
            console.log('🔊 WordPlay Audio System initialized');
            
        } catch (error) {
            console.warn('🔇 Audio initialization failed:', error);
            this.enabled = false;
        }
    }
    
    setupAudioContext() {
        // Audio context needs user interaction to start
        document.addEventListener('click', this.enableAudioContext.bind(this), { once: true });
        document.addEventListener('keydown', this.enableAudioContext.bind(this), { once: true });
        document.addEventListener('touchstart', this.enableAudioContext.bind(this), { once: true });
    }
    
    async enableAudioContext() {
        if (this.audioContext) return;
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            await this.audioContext.resume();
            this.userInteracted = true;
            console.log('🔊 Audio context enabled after user interaction');
        } catch (error) {
            console.warn('🔇 Could not enable audio context:', error);
            this.enabled = false;
        }
    }
    
    generateSoundEffects() {
        // Define sound frequencies and patterns
        this.soundDefinitions = {
            // Game state sounds
            newGame: { type: 'chord', frequencies: [440, 554, 659], duration: 0.3, volume: 0.4 },
            gameWon: { type: 'ascending', frequencies: [440, 523, 659, 784], duration: 0.8, volume: 0.5 },
            gameLost: { type: 'descending', frequencies: [440, 370, 311, 277], duration: 0.6, volume: 0.4 },
            
            // Letter feedback sounds
            letterCorrect: { type: 'tone', frequency: 800, duration: 0.15, volume: 0.3 },
            letterPartial: { type: 'tone', frequency: 600, duration: 0.15, volume: 0.3 },
            letterAbsent: { type: 'tone', frequency: 300, duration: 0.1, volume: 0.2 },
            
            // UI interaction sounds
            buttonClick: { type: 'click', frequency: 1000, duration: 0.05, volume: 0.2 },
            inputType: { type: 'tick', frequency: 1200, duration: 0.03, volume: 0.1 },
            
            // Error and notification sounds
            error: { type: 'buzz', frequency: 200, duration: 0.2, volume: 0.3 },
            hint: { type: 'chime', frequencies: [523, 659, 784], duration: 0.4, volume: 0.3 },
            guessSubmitted: { type: 'swoosh', frequency: 500, duration: 0.2, volume: 0.2 }
        };
    }
    
    setupUserInteractionListeners() {
        // Monitor for audio events without modifying existing game code
        // These listeners will detect game state changes
        
        // Watch for game state changes
        this.startGameStateMonitoring();
        
        // Optional: Add subtle UI sound listeners (disabled by default)
        if (this.preferences.uiEvents) {
            this.setupUIListeners();
        }
    }
    
    startGameStateMonitoring() {
        // Monitor the global game state that the HTML already tracks
        setInterval(() => {
            this.checkForGameStateChanges();
        }, 500); // Check every 500ms
    }
    
    checkForGameStateChanges() {
        // Access the global game data that's already available in the HTML
        if (typeof currentGameData !== 'undefined') {
            const gameState = currentGameData.game_state;
            const guessCount = currentGameData.guesses.length;
            const lastMessage = currentGameData.last_message;
            const messageType = currentGameData.message_type;
            
            // Detect game state changes
            if (this.lastGameState !== gameState) {
                this.handleGameStateChange(this.lastGameState, gameState);
                this.lastGameState = gameState;
            }
            
            // Detect new guesses
            if (this.lastGuessCount !== guessCount && guessCount > 0) {
                this.handleNewGuess(currentGameData);
                this.lastGuessCount = guessCount;
            }
            
            // Detect error messages
            if (messageType === 'error' && this.preferences.errorEvents) {
                this.playSound('error');
            }
        }
    }
    
    handleGameStateChange(oldState, newState) {
        if (!this.preferences.gameEvents) return;
        
        switch (newState) {
            case 'playing':
                if (oldState === 'idle' || oldState === null) {
                    this.playSound('newGame');
                }
                break;
            case 'won':
                this.playSound('gameWon');
                break;
            case 'lost':
                this.playSound('gameLost');
                break;
        }
    }
    
    handleNewGuess(gameData) {
        if (!this.preferences.guessEvents) return;
        
        // Play guess submission sound first
        this.playSound('guessSubmitted');
        
        // Then play letter feedback sounds with delay
        setTimeout(() => {
            this.playLetterFeedback(gameData);
        }, 300);
    }
    
    playLetterFeedback(gameData) {
        const latestResult = gameData.guess_results[gameData.guess_results.length - 1];
        
        if (typeof latestResult === 'string' && latestResult.includes('🟦')) {
            // Parse the result string format like "R⬜ O🟥 P⬜ E⬜ S⬜"
            const letterPairs = latestResult.split(' ');
            
            letterPairs.forEach((pair, index) => {
                setTimeout(() => {
                    if (pair.includes('🟦')) {
                        this.playSound('letterCorrect');
                    } else if (pair.includes('🟥')) {
                        this.playSound('letterPartial');
                    } else if (pair.includes('⬜')) {
                        this.playSound('letterAbsent');
                    }
                }, index * 100); // Stagger sounds by 100ms
            });
        }
    }
    
    setupUIListeners() {
        // Optional UI sounds (disabled by default to avoid annoyance)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('action-button')) {
                this.playSound('buttonClick');
            }
        });
        
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('input-field')) {
                this.playSound('inputType');
            }
        });
    }
    
    async playSound(soundName) {
        if (!this.enabled || !this.preferences.enabled || !this.userInteracted) {
            return;
        }
        
        const soundDef = this.soundDefinitions[soundName];
        if (!soundDef) {
            console.warn(`🔇 Unknown sound: ${soundName}`);
            return;
        }
        
        try {
            await this.generateAndPlaySound(soundDef);
        } catch (error) {
            console.warn(`🔇 Error playing sound ${soundName}:`, error);
        }
    }
    
    async generateAndPlaySound(soundDef) {
        if (!this.audioContext) return;
        
        const now = this.audioContext.currentTime;
        const volume = (soundDef.volume || 0.3) * this.volume * this.preferences.volume;
        
        switch (soundDef.type) {
            case 'tone':
                this.playTone(soundDef.frequency, soundDef.duration, volume, now);
                break;
                
            case 'chord':
                soundDef.frequencies.forEach((freq, index) => {
                    setTimeout(() => {
                        this.playTone(freq, soundDef.duration, volume, this.audioContext.currentTime);
                    }, index * 50);
                });
                break;
                
            case 'ascending':
                soundDef.frequencies.forEach((freq, index) => {
                    const startTime = now + (index * soundDef.duration / soundDef.frequencies.length);
                    this.playTone(freq, soundDef.duration / soundDef.frequencies.length, volume, startTime);
                });
                break;
                
            case 'descending':
                soundDef.frequencies.slice().reverse().forEach((freq, index) => {
                    const startTime = now + (index * soundDef.duration / soundDef.frequencies.length);
                    this.playTone(freq, soundDef.duration / soundDef.frequencies.length, volume, startTime);
                });
                break;
                
            case 'click':
                this.playClick(soundDef.frequency, soundDef.duration, volume, now);
                break;
                
            case 'tick':
                this.playTick(soundDef.frequency, soundDef.duration, volume, now);
                break;
                
            case 'buzz':
                this.playBuzz(soundDef.frequency, soundDef.duration, volume, now);
                break;
                
            case 'chime':
                this.playChime(soundDef.frequencies, soundDef.duration, volume, now);
                break;
                
            case 'swoosh':
                this.playSwoosh(soundDef.frequency, soundDef.duration, volume, now);
                break;
        }
    }
    
    playTone(frequency, duration, volume, startTime) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(volume, startTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
    }
    
    playClick(frequency, duration, volume, startTime) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        oscillator.type = 'square';
        
        gainNode.gain.setValueAtTime(volume, startTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
    }
    
    playTick(frequency, duration, volume, startTime) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        oscillator.type = 'sawtooth';
        
        gainNode.gain.setValueAtTime(volume, startTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
    }
    
    playBuzz(frequency, duration, volume, startTime) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, startTime);
        oscillator.type = 'square';
        
        // Create buzz effect with rapid volume changes
        let time = startTime;
        const buzzInterval = 0.02;
        while (time < startTime + duration) {
            gainNode.gain.setValueAtTime(volume, time);
            gainNode.gain.setValueAtTime(0, time + buzzInterval / 2);
            time += buzzInterval;
        }
        
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
    }
    
    playChime(frequencies, duration, volume, startTime) {
        frequencies.forEach((freq, index) => {
            const delay = (duration / frequencies.length) * index;
            this.playTone(freq, duration / 2, volume, startTime + delay);
        });
    }
    
    playSwoosh(startFreq, duration, volume, startTime) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(startFreq, startTime);
        oscillator.frequency.exponentialRampToValueAtTime(startFreq * 0.3, startTime + duration);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, startTime);
        gainNode.gain.linearRampToValueAtTime(volume, startTime + duration * 0.1);
        gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        oscillator.start(startTime);
        oscillator.stop(startTime + duration);
    }
    
    // Audio control methods
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        this.preferences.volume = this.volume;
        this.savePreferences();
    }
    
    toggleEnabled() {
        this.preferences.enabled = !this.preferences.enabled;
        this.savePreferences();
        return this.preferences.enabled;
    }
    
    setPreference(key, value) {
        if (this.preferences.hasOwnProperty(key)) {
            this.preferences[key] = value;
            this.savePreferences();
        }
    }
    
    getPreferences() {
        return { ...this.preferences };
    }
    
    // Persistence
    loadPreferences() {
        try {
            const stored = localStorage.getItem('wordplay_audio_prefs');
            if (stored) {
                const prefs = JSON.parse(stored);
                this.preferences = { ...this.preferences, ...prefs };
                this.volume = this.preferences.volume;
            }
        } catch (error) {
            console.warn('Could not load audio preferences:', error);
        }
    }
    
    savePreferences() {
        try {
            localStorage.setItem('wordplay_audio_prefs', JSON.stringify(this.preferences));
        } catch (error) {
            console.warn('Could not save audio preferences:', error);
        }
    }
    
    // Manual trigger methods for external use
    triggerNewGame() { this.playSound('newGame'); }
    triggerWin() { this.playSound('gameWon'); }
    triggerLoss() { this.playSound('gameLost'); }
    triggerError() { this.playSound('error'); }
    triggerHint() { this.playSound('hint'); }
    triggerButtonClick() { this.playSound('buttonClick'); }
}

// Global audio instance
let wordplayAudio = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    wordplayAudio = new WordPlayAudio();
    console.log('🔊 WordPlay Audio System ready');
});

// Export for manual control
window.WordPlayAudio = WordPlayAudio;
window.wordplayAudio = () => wordplayAudio;