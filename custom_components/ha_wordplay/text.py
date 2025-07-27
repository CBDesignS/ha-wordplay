"""Text platform for H.A WordPlay integration - Multi-User Version with User Selection."""
import logging
from typing import Optional

from homeassistant.components.text import TextEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .wordplay_const import (
    DOMAIN,
    MIN_WORD_LENGTH,
    MAX_WORD_LENGTH,
    CONF_SELECTED_USERS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the text platform for WordPlay - Multi-User with User Selection."""
    
    # Get selected users from config
    domain_data = hass.data.get(DOMAIN, {})
    selected_user_ids = domain_data.get("selected_users", [])
    
    if not selected_user_ids:
        _LOGGER.warning("No users selected for WordPlay - no text entities will be created")
        return
    
    # Get all users from Home Assistant
    users = await hass.auth.async_get_users()
    
    entities = []
    
    # Store entity references
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"entities": {}}
    
    # Create entity only for selected users
    for user in users:
        if user.system_generated:
            continue  # Skip system users
        
        # Only create entities for selected users
        if user.id not in selected_user_ids:
            continue
            
        user_id = user.id
        entity = WordPlayGuessInput(hass, user_id)
        entities.append(entity)
        
        # Store entity reference
        if user_id not in hass.data[DOMAIN]["entities"]:
            hass.data[DOMAIN]["entities"][user_id] = {}
        hass.data[DOMAIN]["entities"][user_id]["text_input"] = entity
        
        _LOGGER.info(f"Created WordPlay text input for selected user: {user.name} ({user_id})")
    
    async_add_entities(entities, True)
    _LOGGER.info(f"WordPlay created {len(entities)} text input entities for {len(selected_user_ids)} selected users")


class WordPlayGuessInput(TextEntity):
    """Custom text input entity for word guesses - one per user."""

    def __init__(self, hass: HomeAssistant, user_id: str) -> None:
        """Initialize the text input entity."""
        super().__init__()
        self.hass = hass
        self.user_id = user_id
        self._attr_name = f"ha wordplay guess input ({user_id})"
        self._attr_unique_id = f"{DOMAIN}_guess_input_{user_id}"
        self._attr_entity_category = None
        self._attr_icon = "mdi:keyboard"
        self._attr_native_value = "HELLO"  # Start with valid value to avoid validation errors
        self._attr_native_max = MAX_WORD_LENGTH
        self._attr_native_min = 0  # Allow empty values
        self._attr_pattern = r"^[A-Za-z]*$"
        self._attr_mode = "text"
        
        # Set entity_id explicitly
        self.entity_id = f"text.ha_wordplay_guess_input_{user_id}"

    @property
    def native_value(self) -> str:
        """Return the current value."""
        return self._attr_native_value

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        # Convert to uppercase and validate
        value = value.upper().strip()
        
        # Only allow letters
        if value and not value.isalpha():
            _LOGGER.warning(f"Invalid guess input for user {self.user_id}: {value} (only letters allowed)")
            return
        
        # Limit length based on current game
        game_data = self.hass.data.get(DOMAIN, {})
        games = game_data.get("games", {})
        game = games.get(self.user_id)
        
        if game and hasattr(game, 'word_length'):
            max_length = game.word_length
        else:
            max_length = MAX_WORD_LENGTH
            
        if len(value) > max_length:
            value = value[:max_length]
        
        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_clear_value(self) -> None:
        """Clear the input value."""
        self._attr_native_value = ""
        self.async_write_ha_state()