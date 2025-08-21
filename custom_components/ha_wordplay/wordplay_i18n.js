// Rev 1.0 - Clean modular i18n system with separate JSON language files
/**
 * WordPlay Internationalization Loader
 * Loads translations from separate JSON files
 */

class WordPlayI18n {
    constructor() {
        this.currentLanguage = 'en';
        this.translations = {};
        this.fallbackTranslations = {};
        this.ready = false;
    }
    
    async init() {
        // Detect language
        this.currentLanguage = this.detectLanguage();
        
        // Load translations
        await this.loadTranslations(this.currentLanguage);
        
        // Load English as fallback if not already loaded
        if (this.currentLanguage !== 'en') {
            await this.loadFallbackTranslations();
        }
        
        // Apply translations to page
        this.applyTranslations();
        
        // Mark as ready
        this.ready = true;
        
        // Dispatch ready event
        document.dispatchEvent(new CustomEvent('i18nReady', {
            detail: { language: this.currentLanguage }
        }));
        
        console.log(`🌍 I18n initialized with language: ${this.currentLanguage}`);
    }
    
    detectLanguage() {
        // Check URL parameter first
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        if (urlLang) {
            return urlLang;
        }
        
        // Check localStorage
        const savedLang = localStorage.getItem('wordplay_language');
        if (savedLang) {
            return savedLang;
        }
        
        // Check browser language
        const browserLang = navigator.language.substring(0, 2).toLowerCase();
        
        // Supported languages
        const supported = ['en', 'de', 'fr', 'es'];
        if (supported.includes(browserLang)) {
            return browserLang;
        }
        
        // Default to English
        return 'en';
    }
    
    async loadTranslations(lang) {
        try {
            const response = await fetch(`languages/${lang}.json`);
            if (response.ok) {
                this.translations = await response.json();
                console.log(`✅ Loaded ${lang} translations`);
            } else {
                console.warn(`❌ Could not load ${lang} translations, using English`);
                if (lang !== 'en') {
                    await this.loadTranslations('en');
                }
            }
        } catch (error) {
            console.error(`Error loading ${lang} translations:`, error);
            if (lang !== 'en') {
                await this.loadTranslations('en');
            }
        }
    }
    
    async loadFallbackTranslations() {
        try {
            const response = await fetch('languages/en.json');
            if (response.ok) {
                this.fallbackTranslations = await response.json();
            }
        } catch (error) {
            console.error('Error loading fallback translations:', error);
        }
    }
    
    t(key, params = {}) {
        // Get translation from current language or fallback
        let translation = this.translations[key] || this.fallbackTranslations[key] || key;
        
        // Replace parameters {param} with values
        Object.keys(params).forEach(param => {
            translation = translation.replace(`{${param}}`, params[param]);
        });
        
        return translation;
    }
    
    applyTranslations() {
        // Apply to all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            // Handle different element types
            if (element.tagName === 'INPUT') {
                if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                }
                if (element.type === 'button' || element.type === 'submit') {
                    element.value = translation;
                }
            } else if (element.tagName === 'TITLE') {
                element.textContent = translation;
            } else {
                // For most elements, just set textContent
                element.textContent = translation;
            }
        });
        
        console.log(`✅ Applied ${this.currentLanguage} translations to DOM`);
    }
    
    switchLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('wordplay_language', lang);
        
        // Reload translations and apply
        this.loadTranslations(lang).then(() => {
            this.applyTranslations();
            
            // Dispatch event for other modules
            document.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language: lang }
            }));
        });
    }
    
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    isReady() {
        return this.ready;
    }
    
    // Wait for i18n to be ready
    async waitForReady() {
        if (this.ready) return;
        
        return new Promise(resolve => {
            document.addEventListener('i18nReady', resolve, { once: true });
        });
    }
}

// Global i18n instance
let wordplayI18n = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    wordplayI18n = new WordPlayI18n();
    window.wordplayI18n = () => wordplayI18n;
    
    // Initialize after a short delay to ensure DOM is ready
    setTimeout(() => {
        wordplayI18n.init();
    }, 100);
    
    console.log('🌍 WordPlay I18n loader ready');
});