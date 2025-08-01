"""API Configuration for H.A WordPlay - International Support with German, French, Spanish."""
import logging

_LOGGER = logging.getLogger(__name__)

# Language-specific API configurations
LANGUAGE_APIS = {
    "en": {
        "name": "English (UK)",
        "primary": {
            "url": "https://random-word-api.herokuapp.com/word",
            "params": {"length": "{length}"},
            "response_format": "list",
            "word_key": 0  # word is at index 0 in list
        },
        "backup1": {
            "url": "https://random-word-api.vercel.app/api",
            "params": {"words": 1, "length": "{length}"},
            "response_format": "list",
            "word_key": 0
        },
        "backup2": {
            "url": "https://random-words-api.vercel.app/word",
            "params": {},
            "response_format": "list",
            "word_key": "word"  # word is in object at key "word"
        },
        "fallback_words": {
            5: ["HOUSE", "BOARD", "STEAM", "LIGHT", "MUSIC", "DANCE", "PLANT", "CHAIR", "WATER", "SMILE"],
            6: ["GARDEN", "BRIDGE", "CASTLE", "PLANET", "FRIEND", "COFFEE", "NATURE", "MARKET", "LISTEN", "BRIGHT"],
            7: ["KITCHEN", "FREEDOM", "JOURNEY", "MORNING", "RAINBOW", "SCIENCE", "BALANCE", "LIBRARY", "HARMONY", "MYSTERY"],
            8: ["COMPLETE", "SURPRISE", "STRENGTH", "ADVENTURE", "LAUGHTER", "DISCOVER", "PEACEFUL", "CREATIVE", "TOMORROW", "BUTTERFLY"]
        }
    },
    "es": {
        "name": "Español (Spanish)",
        "primary": {
            "url": "https://random-word-api.herokuapp.com/word",
            "params": {"lang": "es", "length": "{length}"},
            "response_format": "list",
            "word_key": 0
        },
        "backup1": {
            "url": "https://random-words-api.vercel.app/word/spanish",
            "params": {},
            "response_format": "list",
            "word_key": "word"
        },
        "fallback_words": {
            5: ["CASA", "MESA", "AGUA", "LIBRO", "MUNDO", "TIEMPO", "AMIGO", "LUGAR", "GENTE", "TANTO"],
            6: ["CIUDAD", "FAMILIA", "ESCUELA", "TRABAJO", "ANIMAL", "CABEZA", "DINERO", "NÚMERO", "GRANDE", "PEQUEÑO"],
            7: ["EJEMPLO", "MOMENTO", "PROCESO", "SISTEMA", "CONTROL", "HISTORIA", "SERVICIO", "PRODUCTO", "EMPRESA", "PERSONA"],
            8: ["PROBLEMA", "DESARROLLO", "SITUACIÓN", "INFORMACIÓN", "EDUCACIÓN", "TECNOLOGÍA", "ACTIVIDAD", "MEDICINA", "SOCIEDAD", "MEDICINA"]
        }
    },
    "fr": {
        "name": "Français (French)",
        "primary": {
            "url": "https://random-word-api.herokuapp.com/word",
            "params": {"lang": "fr", "length": "{length}"},
            "response_format": "list",
            "word_key": 0
        },
        "backup1": {
            "url": "https://random-words-api.vercel.app/word/french",
            "params": {},
            "response_format": "list",
            "word_key": "word"
        },
        "fallback_words": {
            5: ["MAISON", "TABLE", "LIVRE", "TEMPS", "MONDE", "HOMME", "FEMME", "ENFANT", "PLACE", "ÉCOLE"],
            6: ["FAMILLE", "TRAVAIL", "NOMBRE", "ARGENT", "ANIMAL", "NATURE", "CENTRE", "MARCHÉ", "MUSIQUE", "VOYAGE"],
            7: ["EXEMPLE", "SYSTÈME", "HISTOIRE", "SERVICE", "PRODUIT", "SOCIÉTÉ", "SCIENCE", "CULTURE", "JOURNAL", "MACHINE"],
            8: ["PROBLÈME", "ÉDUCATION", "POLITIQUE", "ÉCONOMIE", "MÉDECINE", "RELATION", "ACTIVITÉ", "MATÉRIEL", "FONCTION", "CRÉATION"]
        }
    },
    "de": {
        "name": "Deutsch (German)",
        "primary": {
            "url": "https://random-word-api.herokuapp.com/word",
            "params": {"lang": "de", "length": "{length}"},
            "response_format": "list",
            "word_key": 0
        },
        "backup1": {
            "url": "https://random-words-api.vercel.app/word/german",
            "params": {},
            "response_format": "list",
            "word_key": "word"
        },
        "fallback_words": {
            5: ["HAUS", "TISCH", "BUCH", "ZEIT", "WELT", "MANN", "FRAU", "KIND", "PLATZ", "SCHULE"],
            6: ["FAMILIE", "ARBEIT", "NUMMER", "GELD", "TIER", "NATUR", "ZENTRUM", "MARKT", "MUSIK", "REISE"],
            7: ["BEISPIEL", "SYSTEM", "GESCHICHTE", "SERVICE", "PRODUKT", "GESELLSCHAFT", "WISSENSCHAFT", "KULTUR", "ZEITUNG", "MASCHINE"],
            8: ["PROBLEM", "BILDUNG", "POLITIK", "WIRTSCHAFT", "MEDIZIN", "BEZIEHUNG", "AKTIVITÄT", "MATERIAL", "FUNKTION", "SCHÖPFUNG"]
        }
    }
}

# Dictionary API configurations (for hints)
DICTIONARY_APIS = {
    "en": {
        "primary": "https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
        "backup": None  # Could add backup dictionary API
    },
    "es": {
        "primary": "https://api.dictionaryapi.dev/api/v2/entries/es/{word}",
        "backup": None
    },
    "fr": {
        "primary": "https://api.dictionaryapi.dev/api/v2/entries/fr/{word}",
        "backup": None
    },
    "de": {
        "primary": "https://api.dictionaryapi.dev/api/v2/entries/de/{word}",
        "backup": None
    }
}

# Default language if not specified
DEFAULT_LANGUAGE = "en"

# API timeout settings
API_TIMEOUT = 10
MAX_API_ATTEMPTS = 2  # Per API endpoint


def get_language_config(language_code: str = None) -> dict:
    """Get API configuration for a specific language."""
    if not language_code:
        language_code = DEFAULT_LANGUAGE
    
    config = LANGUAGE_APIS.get(language_code)
    if not config:
        _LOGGER.warning(f"Language '{language_code}' not supported, falling back to {DEFAULT_LANGUAGE}")
        config = LANGUAGE_APIS[DEFAULT_LANGUAGE]
    
    return config


def get_dictionary_config(language_code: str = None) -> dict:
    """Get dictionary API configuration for a specific language."""
    if not language_code:
        language_code = DEFAULT_LANGUAGE
    
    config = DICTIONARY_APIS.get(language_code)
    if not config:
        _LOGGER.warning(f"Dictionary for '{language_code}' not available, falling back to {DEFAULT_LANGUAGE}")
        config = DICTIONARY_APIS[DEFAULT_LANGUAGE]
    
    return config


def get_supported_languages() -> list:
    """Get list of supported language codes."""
    return list(LANGUAGE_APIS.keys())


def get_fallback_word(language_code: str, word_length: int) -> str:
    """Get a fallback word for when all APIs fail."""
    config = get_language_config(language_code)
    fallback_words = config.get("fallback_words", {})
    
    words_for_length = fallback_words.get(word_length, [])
    if words_for_length:
        import random
        return random.choice(words_for_length)
    
    # Ultimate fallback
    ultimate_fallbacks = {
        4: "WORD",
        5: "HOUSE", 
        6: "CASTLE",
        7: "RAINBOW",
        8: "COMPLETE"
    }
    
    return ultimate_fallbacks.get(word_length, "FALLBACK")


def build_api_url(api_config: dict, word_length: int = None) -> str:
    """Build API URL with parameters."""
    url = api_config["url"]
    params = api_config.get("params", {})
    
    if params:
        param_strings = []
        for key, value in params.items():
            if isinstance(value, str) and "{length}" in value and word_length:
                value = value.format(length=word_length)
            param_strings.append(f"{key}={value}")
        
        if param_strings:
            url += "?" + "&".join(param_strings)
    
    return url


def extract_word_from_response(response_data: any, api_config: dict) -> str:
    """Extract word from API response based on configuration."""
    try:
        response_format = api_config.get("response_format", "list")
        word_key = api_config.get("word_key", 0)
        
        if response_format == "list":
            if isinstance(word_key, int):
                # Word is at specific index in list
                return response_data[word_key]
            elif isinstance(word_key, str):
                # Word is in object at specific key
                return response_data[0][word_key]
        
        return str(response_data)
        
    except (IndexError, KeyError, TypeError) as e:
        _LOGGER.error(f"Error extracting word from API response: {e}")
        return None