"""Input text entity for H.A WordPlay."""
import logging
from typing import Optional

from homeassistant.components.input_text import InputText, CONF_INITIAL, CONF_MIN, CONF_MAX, CONF_PATTERN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the input_text platform for WordPlay."""
    
    # Create the input text entity
    entity = WordPlayInputText(
        object_id="ha_wordplay_guess",
        name="WordPlay Guess Input",
        initial="",
        minimum=4,
        maximum=8,
        pattern=r"[A-Za-z]*"
    )
    
    async_add_entities([entity])
    _LOGGER.info("WordPlay input text entity created")

class WordPlayInputText(InputText):
    """Input text entity for WordPlay guesses."""
    
    def __init__(
        self,
        object_id: str,
        name: str,
        initial: str,
        minimum: int,
        maximum: int,
        pattern: Optional[str] = None,
    ) -> None:
        """Initialize the input text entity."""
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{object_id}"
        self.entity_id = f"input_text.{object_id}"
        self._state = initial
        self._minimum = minimum
        self._maximum = maximum
        self._pattern = pattern
        
    @property
    def state(self) -> str:
        """Return the current state."""
        return self._state
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            "min": self._minimum,
            "max": self._maximum,
            "pattern": self._pattern,
            "friendly_name": self._attr_name,
        }
    
    async def async_set_value(self, value: str) -> None:
        """Set the value."""
        if len(value) <= self._maximum:
            self._state = value
            self.async_write_ha_state()
