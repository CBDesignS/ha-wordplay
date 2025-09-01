# Rev 1.0 - Backend i18n translation helper for WordPlay
"""Translation helper module for H.A WordPlay backend."""
import json
import logging
import os
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)

class WordPlayTranslator:
    """Handle translations for WordPlay backend messages."""
    
    def __init__(self, integration_dir: str):
        """Initialize the translator with the integration directory path."""
        self.integration_dir = integration_dir
        self.languages_dir = os.path.join(integration_dir, "languages")
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = "en"
        self._load_all_translations()
    
    def _load_all_translations(self) -> None:
        """Load all available language files."""
        try:
            # Load all JSON files from languages directory
            if os.path.exists(self.languages_dir):
                for filename in os.listdir(self.languages_dir):
                    if filename.endswith('.json'):
                        lang_code = filename[:-5]  # Remove .json extension
                        filepath = os.path.join(self.languages_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                self.translations[lang_code] = json.load(f)
                                _LOGGER.debug(f"Loaded translations for {lang_code}")
                        except Exception as e:
                            _LOGGER.error(f"Error loading {lang_code} translations: {e}")
                            self.translations[lang_code] = {}
            else:
                _LOGGER.warning(f"Languages directory not found: {self.languages_dir}")
        except Exception as e:
            _LOGGER.error(f"Error loading translations: {e}")
    
    def set_language(self, language: str) -> None:
        """Set the current language for translations."""
        if language in self.translations:
            self.current_language = language
            _LOGGER.debug(f"Language set to {language}")
        else:
            _LOGGER.warning(f"Language {language} not available, keeping {self.current_language}")
    
    def get(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Get a translated string by key.
        
        Args:
            key: Translation key (e.g., "backend.noGameInProgress")
            language: Optional language code, uses current_language if not provided
            **kwargs: Variables to replace in the translation string
        
        Returns:
            Translated string with variables replaced
        """
        lang = language or self.current_language
        
        # Get translations for the language
        lang_translations = self.translations.get(lang, {})
        
        # Get the translation or fallback to English or the key itself
        translation = lang_translations.get(key)
        if translation is None:
            # Try English fallback
            translation = self.translations.get("en", {}).get(key)
            if translation is None:
                # Return the key itself as last resort
                _LOGGER.warning(f"Translation key '{key}' not found for language '{lang}'")
                return key
        
        # Replace placeholders with provided values
        if kwargs:
            try:
                # Replace {variable} style placeholders
                for var_name, var_value in kwargs.items():
                    placeholder = f"{{{var_name}}}"
                    translation = translation.replace(placeholder, str(var_value))
            except Exception as e:
                _LOGGER.error(f"Error replacing variables in translation: {e}")
        
        return translation
    
    def reload_translations(self) -> None:
        """Reload all translation files (useful for development/testing)."""
        self.translations.clear()
        self._load_all_translations()
        _LOGGER.info("Translations reloaded")

# Singleton instance that will be initialized in __init__.py
_translator_instance: Optional[WordPlayTranslator] = None

def get_translator() -> Optional[WordPlayTranslator]:
    """Get the singleton translator instance."""
    return _translator_instance

def init_translator(integration_dir: str) -> WordPlayTranslator:
    """Initialize the singleton translator instance."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = WordPlayTranslator(integration_dir)
    return _translator_instance
