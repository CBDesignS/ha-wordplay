"""Lovelace dashboard configuration for H.A WordPlay."""
import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

async def async_create_wordplay_dashboard(hass: HomeAssistant) -> None:
    """Create a WordPlay dashboard automatically."""
    try:
        # Dashboard auto-creation will be implemented later
        # For now, just log that the config is available
        _LOGGER.info("WordPlay dashboard configuration ready for manual setup")
    except Exception as e:
        _LOGGER.error("Could not prepare dashboard: %s", e)
