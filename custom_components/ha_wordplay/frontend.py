"""Frontend platform for H.A WordPlay - Auto-registers frontend resources."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.frontend import add_extra_js_url

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

WORDPLAY_JS_URL = f"/hacsfiles/{DOMAIN}/ha-wordplay-more-info.js"

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities,
    discovery_info=None,
) -> bool:
    """Set up the frontend platform for WordPlay."""
    _LOGGER.info("Setting up H.A WordPlay frontend platform")
    
    try:
        # Register the JavaScript file with Home Assistant frontend
        await hass.async_add_executor_job(
            add_extra_js_url, hass, WORDPLAY_JS_URL
        )
        
        _LOGGER.info(f"WordPlay frontend resource registered: {WORDPLAY_JS_URL}")
        return True
        
    except Exception as e:
        _LOGGER.error(f"Failed to register WordPlay frontend resource: {e}")
        return False


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up frontend from a config entry."""
    return await async_setup_platform(hass, {}, None, None)