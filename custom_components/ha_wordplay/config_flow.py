"""Config flow for H.A WordPlay integration - Long-Lived Token Setup."""
import logging
import aiohttp
import asyncio
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_DIFFICULTY = "difficulty"

# Difficulty options
DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"

DIFFICULTY_OPTIONS = {
    DIFFICULTY_EASY: "Easy (Hint shown before guessing)",
    DIFFICULTY_NORMAL: "Normal (Hints available on request)",
    DIFFICULTY_HARD: "Hard (No hints available)"
}

# FIXED: Config schema - ONLY token and difficulty
CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_ACCESS_TOKEN): cv.string,
    vol.Required(CONF_DIFFICULTY, default=DIFFICULTY_NORMAL): vol.In(DIFFICULTY_OPTIONS)
})


class WordPlayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for H.A WordPlay."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._token = None
        self._difficulty = DIFFICULTY_NORMAL

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the token
            token = user_input[CONF_ACCESS_TOKEN].strip()
            difficulty = user_input[CONF_DIFFICULTY]

            # Test the token
            is_valid, error_message = await self._test_token(token)
            
            if is_valid:
                # Token works, create the entry
                title = f"WordPlay ({difficulty.title()} Mode)"
                
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ACCESS_TOKEN: token,
                        CONF_DIFFICULTY: difficulty
                        # REMOVED: word_lengths - controlled in game interface
                    }
                )
            else:
                # Token failed validation
                errors["base"] = error_message
                _LOGGER.error(f"Token validation failed: {error_message}")

        # Show the form (initial or with errors)
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
            description_placeholders={
                "token_url": f"{self.hass.config.external_url or self.hass.config.internal_url}/profile/security"
            }
        )

    async def _test_token(self, token: str) -> tuple[bool, Optional[str]]:
        """Test if the provided token works with Home Assistant API."""
        try:
            # Get the base URL
            base_url = self.hass.config.internal_url or "http://localhost:8123"
            
            # Test the token by making a simple API call
            session = async_get_clientsession(self.hass)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Test 1: Basic API access
            async with session.get(f"{base_url}/api/", headers=headers) as response:
                if response.status == 401:
                    return False, "invalid_token"
                elif response.status == 403:
                    return False, "insufficient_permissions"
                elif not response.ok:
                    return False, "api_error"
            
            # Test 2: States access (needed for game)
            async with session.get(f"{base_url}/api/states", headers=headers) as response:
                if response.status == 401:
                    return False, "invalid_token"
                elif response.status == 403:
                    return False, "states_access_denied"
                elif not response.ok:
                    return False, "states_error"
            
            # Test 3: Services access (needed for game actions)
            async with session.get(f"{base_url}/api/services", headers=headers) as response:
                if response.status == 401:
                    return False, "invalid_token"
                elif response.status == 403:
                    return False, "services_access_denied"
                elif not response.ok:
                    return False, "services_error"
            
            _LOGGER.info("Token validation successful")
            return True, None
            
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Network error during token validation: {e}")
            return False, "network_error"
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout during token validation")
            return False, "timeout"
        except Exception as e:
            _LOGGER.error(f"Unexpected error during token validation: {e}")
            return False, "unknown_error"

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return WordPlayOptionsFlowHandler(config_entry)


class WordPlayOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for H.A WordPlay."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # If token was changed, validate it
            new_token = user_input.get(CONF_ACCESS_TOKEN)
            current_token = self.config_entry.data.get(CONF_ACCESS_TOKEN)
            
            if new_token and new_token != current_token:
                # Token changed, validate it
                is_valid, error_message = await self._test_token(new_token)
                if not is_valid:
                    errors["base"] = error_message
                else:
                    # Update the config entry with new data
                    updated_data = {**self.config_entry.data}
                    updated_data.update(user_input)
                    
                    self.hass.config_entries.async_update_entry(
                        self.config_entry, data=updated_data
                    )
                    
                    return self.async_create_entry(title="", data={})
            else:
                # No token change, just update other settings
                updated_data = {**self.config_entry.data}
                updated_data.update(user_input)
                
                # Keep the original token if not provided
                if CONF_ACCESS_TOKEN not in user_input:
                    updated_data[CONF_ACCESS_TOKEN] = current_token
                
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=updated_data
                )
                
                return self.async_create_entry(title="", data={})

        # Build the options schema with current values - FIXED: only difficulty
        current_data = self.config_entry.data
        
        options_schema = vol.Schema({
            vol.Optional(
                CONF_ACCESS_TOKEN, 
                description="Leave blank to keep current token"
            ): cv.string,
            vol.Required(
                CONF_DIFFICULTY, 
                default=current_data.get(CONF_DIFFICULTY, DIFFICULTY_NORMAL)
            ): vol.In(DIFFICULTY_OPTIONS)
            # REMOVED: word_lengths option - controlled in game interface
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
            description_placeholders={
                "current_difficulty": current_data.get(CONF_DIFFICULTY, "normal").title(),
                "token_url": f"{self.hass.config.external_url or self.hass.config.internal_url}/profile/security"
            }
        )

    async def _test_token(self, token: str) -> tuple[bool, Optional[str]]:
        """Test token (same as main config flow)."""
        try:
            base_url = self.hass.config.internal_url or "http://localhost:8123"
            session = async_get_clientsession(self.hass)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with session.get(f"{base_url}/api/", headers=headers) as response:
                if response.status == 401:
                    return False, "invalid_token"
                elif response.status == 403:
                    return False, "insufficient_permissions"
                elif not response.ok:
                    return False, "api_error"
            
            return True, None
            
        except Exception as e:
            _LOGGER.error(f"Token validation error: {e}")
            return False, "unknown_error"