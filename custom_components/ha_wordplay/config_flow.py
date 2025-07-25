"""Config flow for H.A WordPlay integration - Enhanced with User Selection."""
import logging
import aiohttp
import asyncio
from typing import Any, Dict, Optional, List

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .wordplay_const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_SELECTED_USERS = "selected_users"


class WordPlayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for H.A WordPlay."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._token = None
        self._available_users = []

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step - Access Token."""
        errors = {}

        if user_input is not None:
            # Validate the token
            token = user_input[CONF_ACCESS_TOKEN].strip()

            # Test the token
            is_valid, error_message = await self._test_token(token)
            
            if is_valid:
                # Store token for next step
                self._token = token
                
                # Move to user selection step
                return await self.async_step_user_selection()
            else:
                # Token failed validation
                errors["base"] = error_message
                _LOGGER.error(f"Token validation failed: {error_message}")

        # Build initial config schema - REMOVED DIFFICULTY
        config_schema = vol.Schema({
            vol.Required(CONF_ACCESS_TOKEN): cv.string,
        })

        # Show the form (initial or with errors)
        return self.async_show_form(
            step_id="user",
            data_schema=config_schema,
            errors=errors,
            description_placeholders={
                "token_url": f"{self.hass.config.external_url or self.hass.config.internal_url}/profile/security"
            }
        )

    async def async_step_user_selection(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle user selection step."""
        errors = {}

        # Get available users if not already loaded
        if not self._available_users:
            self._available_users = await self._get_available_users()

        if user_input is not None:
            # Get selected users
            selected_users = user_input.get(CONF_SELECTED_USERS, [])
            
            if not selected_users:
                errors["base"] = "no_users_selected"
            else:
                # Create the entry with selected configuration
                title = f"WordPlay - {len(selected_users)} Users"
                
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ACCESS_TOKEN: self._token,
                        CONF_SELECTED_USERS: selected_users,
                    }
                )

        # Build user selection schema
        if self._available_users:
            # Create options for user selection
            user_options = {}
            default_selection = []
            
            for user in self._available_users:
                # Create a friendly display name
                display_name = f"{user['name']} ({user['role']})"
                user_options[user['id']] = display_name
                
                # Auto-select active, non-system users by default
                if user['is_active'] and not user['system_generated'] and user['role'] in ['owner', 'administrator', 'user']:
                    default_selection.append(user['id'])

            user_selection_schema = vol.Schema({
                vol.Required(
                    CONF_SELECTED_USERS, 
                    default=default_selection
                ): cv.multi_select(user_options),
            })
        else:
            # Fallback if no users found
            user_selection_schema = vol.Schema({})
            errors["base"] = "no_users_found"

        return self.async_show_form(
            step_id="user_selection",
            data_schema=user_selection_schema,
            errors=errors,
            description_placeholders={
                "user_count": str(len(self._available_users))
            }
        )

    async def _get_available_users(self) -> List[Dict[str, Any]]:
        """Get list of available users from Home Assistant."""
        try:
            users = await self.hass.auth.async_get_users()
            available_users = []
            
            for user in users:
                # Determine user role
                if user.is_owner:
                    role = "Owner"
                elif user.is_admin:
                    role = "Administrator" 
                elif user.system_generated:
                    role = "System User"
                else:
                    role = "User"
                
                available_users.append({
                    'id': user.id,
                    'name': user.name or "Unnamed User",
                    'role': role,
                    'is_active': user.is_active,
                    'system_generated': user.system_generated,
                })
            
            # Sort users: Owners first, then Admins, then Users, then System users
            role_priority = {"Owner": 0, "Administrator": 1, "User": 2, "System User": 3}
            available_users.sort(key=lambda x: (role_priority.get(x['role'], 4), x['name']))
            
            _LOGGER.info(f"Found {len(available_users)} available users for WordPlay selection")
            return available_users
            
        except Exception as e:
            _LOGGER.error(f"Error getting available users: {e}")
            return []

    async def _test_token(self, token: str) -> tuple[bool, Optional[str]]:
        """Test if the provided token works with Home Assistant API."""
        try:
            # Try multiple base URLs - internal first, then external
            base_urls_to_try = []
            
            # Try internal URL first (if it exists)
            if self.hass.config.internal_url:
                base_urls_to_try.append(self.hass.config.internal_url)
            
            # Try external URL as fallback
            if self.hass.config.external_url:
                base_urls_to_try.append(self.hass.config.external_url)
            
            # Last resort fallback
            if not base_urls_to_try:
                base_urls_to_try.append("http://localhost:8123")
            
            _LOGGER.info(f"Token validation will try URLs: {base_urls_to_try}")
            
            # Try each URL until one works
            last_error = None
            for base_url in base_urls_to_try:
                _LOGGER.info(f"Testing token validation against: {base_url}")
                
                try:
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
                            _LOGGER.warning(f"API test failed on {base_url}: status {response.status}")
                            continue  # Try next URL
                    
                    # Test 2: States access (needed for game)
                    async with session.get(f"{base_url}/api/states", headers=headers) as response:
                        if response.status == 401:
                            return False, "invalid_token"
                        elif response.status == 403:
                            return False, "states_access_denied"
                        elif not response.ok:
                            _LOGGER.warning(f"States test failed on {base_url}: status {response.status}")
                            continue  # Try next URL
                    
                    # Test 3: Services access (needed for game actions)
                    async with session.get(f"{base_url}/api/services", headers=headers) as response:
                        if response.status == 401:
                            return False, "invalid_token"
                        elif response.status == 403:
                            return False, "services_access_denied"
                        elif not response.ok:
                            _LOGGER.warning(f"Services test failed on {base_url}: status {response.status}")
                            continue  # Try next URL
                    
                    # If we get here, all tests passed on this URL
                    _LOGGER.info(f"Token validation successful using: {base_url}")
                    return True, None
                    
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    _LOGGER.warning(f"Network error testing {base_url}: {e}")
                    last_error = e
                    continue  # Try next URL
                
            # If we get here, all URLs failed
            _LOGGER.error(f"Token validation failed on all URLs. Last error: {last_error}")
            return False, "network_error"
            
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
        self._available_users = []

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        # Get available users
        if not self._available_users:
            self._available_users = await self._get_available_users()

        if user_input is not None:
            # Handle token change if provided
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
                # No token change or validation passed, update other settings
                updated_data = {**self.config_entry.data}
                updated_data.update(user_input)
                
                # Keep the original token if not provided
                if CONF_ACCESS_TOKEN not in user_input:
                    updated_data[CONF_ACCESS_TOKEN] = current_token
                
                # Validate user selection
                selected_users = user_input.get(CONF_SELECTED_USERS, [])
                if not selected_users:
                    errors["base"] = "no_users_selected"
                else:
                    self.hass.config_entries.async_update_entry(
                        self.config_entry, data=updated_data
                    )
                    
                    return self.async_create_entry(title="", data={})

        # Build the options schema with current values
        current_data = self.config_entry.data
        
        # Create user options
        user_options = {}
        current_selection = current_data.get(CONF_SELECTED_USERS, [])
        
        for user in self._available_users:
            display_name = f"{user['name']} ({user['role']})"
            user_options[user['id']] = display_name

        # REMOVED DIFFICULTY FROM OPTIONS
        options_schema = vol.Schema({
            vol.Optional(
                CONF_ACCESS_TOKEN, 
                description="Leave blank to keep current token"
            ): cv.string,
            vol.Required(
                CONF_SELECTED_USERS,
                default=current_selection
            ): cv.multi_select(user_options),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
            description_placeholders={
                "current_user_count": str(len(current_selection)),
                "token_url": f"{self.hass.config.external_url or self.hass.config.internal_url}/profile/security"
            }
        )

    async def _get_available_users(self) -> List[Dict[str, Any]]:
        """Get list of available users from Home Assistant."""
        try:
            users = await self.hass.auth.async_get_users()
            available_users = []
            
            for user in users:
                # Determine user role
                if user.is_owner:
                    role = "Owner"
                elif user.is_admin:
                    role = "Administrator" 
                elif user.system_generated:
                    role = "System User"
                else:
                    role = "User"
                
                available_users.append({
                    'id': user.id,
                    'name': user.name or "Unnamed User",
                    'role': role,
                    'is_active': user.is_active,
                    'system_generated': user.system_generated,
                })
            
            # Sort users: Owners first, then Admins, then Users, then System users
            role_priority = {"Owner": 0, "Administrator": 1, "User": 2, "System User": 3}
            available_users.sort(key=lambda x: (role_priority.get(x['role'], 4), x['name']))
            
            return available_users
            
        except Exception as e:
            _LOGGER.error(f"Error getting available users: {e}")
            return []

    async def _test_token(self, token: str) -> tuple[bool, Optional[str]]:
        """Test token (same as main config flow)."""
        try:
            # Use the same logic as main config flow
            base_urls_to_try = []
            
            if self.hass.config.internal_url:
                base_urls_to_try.append(self.hass.config.internal_url)
            
            if self.hass.config.external_url:
                base_urls_to_try.append(self.hass.config.external_url)
            
            if not base_urls_to_try:
                base_urls_to_try.append("http://localhost:8123")
            
            session = async_get_clientsession(self.hass)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            for base_url in base_urls_to_try:
                try:
                    async with session.get(f"{base_url}/api/", headers=headers) as response:
                        if response.status == 401:
                            return False, "invalid_token"
                        elif response.status == 403:
                            return False, "insufficient_permissions"
                        elif response.ok:
                            return True, None
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    continue
            
            return False, "network_error"
            
        except Exception as e:
            _LOGGER.error(f"Token validation error: {e}")
            return False, "unknown_error"
