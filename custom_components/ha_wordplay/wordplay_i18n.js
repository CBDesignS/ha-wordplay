// Rev 1.1 - Added Home Assistant language detection for automatic language selection
/**
 * WordPlay i18n (Internationalization) Module
 * Handles loading and applying translations for the WordPlay game
 */

(function() {
    'use strict';
    
    // Supported languages
    const supportedLanguages = ['en', 'de', 'fr', 'es'];
    const defaultLanguage = 'en';
    
    // Current language and translations
    let currentLanguage = defaultLanguage;
    let translations = {};
    
    /**
     * Get Home Assistant language setting
     * @returns {string|null} HA language code or null
     */
    function getHALanguage() {
        try {
            // Method 1: Check parent frame HA object
            if (window.parent && window.parent !== window) {
                const parentDoc = window.parent.document;
                if (parentDoc) {
                    const haMain = parentDoc.querySelector('home-assistant');
                    if (haMain && haMain.hass) {
                        // Check hass.language (system language)
                        if (haMain.hass.language) {
                            // HA language format is usually like 'de-DE', we need just 'de'
                            const haLang = haMain.hass.language.split('-')[0].toLowerCase();
                            console.log(`🌍 Detected HA system language: ${haLang}`);
                            return haLang;
                        }
                        // Check user language preference
                        if (haMain.hass.user && haMain.hass.user.language) {
                            const userLang = haMain.hass.user.language.split('-')[0].toLowerCase();
                            console.log(`🌍 Detected HA user language: ${userLang}`);
                            return userLang;
                        }
                    }
                }
            }
            
            // Method 2: Check if we can access hass object directly
            if (window.parent && window.parent.hass) {
                if (window.parent.hass.language) {
                    const lang = window.parent.hass.language.split('-')[0].toLowerCase();
                    console.log(`🌍 Detected HA language from parent.hass: ${lang}`);
                    return lang;
                }
            }
            
            // Method 3: Try to get from localStorage (HA stores selectedLanguage)
            const haSelectedLang = localStorage.getItem('selectedLanguage');
            if (haSelectedLang) {
                try {
                    const langData = JSON.parse(haSelectedLang);
                    if (langData && typeof langData === 'string') {
                        const lang = langData.split('-')[0].toLowerCase();
                        console.log(`🌍 Detected HA language from localStorage: ${lang}`);
                        return lang;
                    }
                } catch (e) {
                    // If it's not JSON, try as string
                    const lang = haSelectedLang.split('-')[0].toLowerCase();
                    console.log(`🌍 Detected HA language from localStorage (string): ${lang}`);
                    return lang;
                }
            }
            
        } catch (error) {
            console.log('Could not detect HA language:', error.message);
        }
        return null;
    }
    
    /**
     * Detect the language to use
     * Priority: URL param > HA language > localStorage > browser > default
     */
    function detectLanguage() {
        // 1. Check URL parameter (highest priority for testing)
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        if (urlLang && supportedLanguages.includes(urlLang)) {
            console.log(`🌍 Language from URL: ${urlLang}`);
            return urlLang;
        }
        
        // 2. Check Home Assistant language setting
        const haLang = getHALanguage();
        if (haLang && supportedLanguages.includes(haLang)) {
            console.log(`🌍 Using Home Assistant language: ${haLang}`);
            return haLang;
        }
        
        // 3. Check localStorage for saved preference
        const storedLang = localStorage.getItem('wordplay_language');
        if (storedLang && supportedLanguages.includes(storedLang)) {
            console.log(`🌍 Language from storage: ${storedLang}`);
            return storedLang;
        }
        
        // 4. Check browser language
        const browserLang = navigator.language.substring(0, 2).toLowerCase();
        if (supportedLanguages.includes(browserLang)) {
            console.log(`🌍 Language from browser: ${browserLang}`);
            return browserLang;
        }
        
        // 5. Default to English
        console.log('🌍 No language detected, defaulting to English');
        return defaultLanguage;
    }
    
    /**
     * Load translations for a specific language
     * @param {string} lang - Language code
     * @returns {Promise<Object>} Translation object
     */
    async function loadTranslations(lang) {
        try {
            const response = await fetch(`languages/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load ${lang} translations`);
            }
            const data = await response.json();
            console.log(`✅ Loaded ${lang} translations`);
            return data;
        } catch (error) {
            console.error(`Error loading ${lang} translations:`, error);
            
            // Try to fallback to English if not already English
            if (lang !== 'en') {
                console.log('Falling back to English translations');
                try {
                    const response = await fetch(`languages/en.json`);
                    if (response.ok) {
                        const data = await response.json();
                        console.log('✅ Loaded English translations as fallback');
                        return data;
                    }
                } catch (fallbackError) {
                    console.error('Failed to load English fallback:', fallbackError);
                }
            }
            
            // Return empty object if all fails
            return {};
        }
    }
    
    /**
     * Get a translation by key
     * @param {string} key - Translation key
     * @param {Object} params - Parameters to replace in translation
     * @returns {string} Translated text
     */
    function t(key, params = {}) {
        let text = translations[key] || key;
        
        // Replace parameters like {name} with actual values
        Object.keys(params).forEach(param => {
            text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), params[param]);
        });
        
        return text;
    }
    
    /**
     * Apply translations to DOM elements with data-i18n attribute
     */
    function applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = t(key);
            
            // Handle different element types
            if (element.tagName === 'INPUT') {
                if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                }
                if (element.type === 'button' || element.type === 'submit') {
                    element.value = translation;
                }
            } else {
                element.textContent = translation;
            }
        });
        
        console.log(`✅ Applied ${currentLanguage} translations to DOM`);
    }
    
    /**
     * Initialize the i18n system
     */
    async function init() {
        // Detect language
        currentLanguage = detectLanguage();
        
        // Load translations
        translations = await loadTranslations(currentLanguage);
        
        // Apply to existing DOM elements
        applyTranslations();
        
        // Store the selected language
        localStorage.setItem('wordplay_language', currentLanguage);
        
        console.log(`🌍 I18n initialized with language: ${currentLanguage}`);
        
        // Dispatch ready event
        document.dispatchEvent(new CustomEvent('i18nReady', {
            detail: { language: currentLanguage }
        }));
    }
    
    /**
     * Change language dynamically
     * @param {string} lang - New language code
     */
    async function changeLanguage(lang) {
        if (!supportedLanguages.includes(lang)) {
            console.error(`Language ${lang} not supported`);
            return;
        }
        
        currentLanguage = lang;
        translations = await loadTranslations(lang);
        applyTranslations();
        localStorage.setItem('wordplay_language', lang);
        
        // Dispatch language change event
        document.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: lang }
        }));
    }
    
    // Public API
    window.wordplayI18n = {
        init,
        t,
        changeLanguage,
        getCurrentLanguage: () => currentLanguage,
        getSupportedLanguages: () => supportedLanguages,
        applyTranslations
    };
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    console.log('🌍 WordPlay I18n loader ready');
})();