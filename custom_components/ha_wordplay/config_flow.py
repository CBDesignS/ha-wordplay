"""Config flow for H.A WordPlay integration - Enhanced with User Selection and Stats Reset."""
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
from homeassistant.helpers import storage
import homeassistant.helpers.config_validation as cv

from .wordplay_const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_SELECTED_USERS = "selected_users"

# Storage constants for stats
STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = f"{DOMAIN}_stats"


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
        self._users_with_stats = []

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the main options menu."""
        if user_input is not None:
            if user_input.get("action") == "manage_users":
                return await self.async_step_manage_users()
            elif user_input.get("action") == "reset_stats":
                return await self.async_step_stats_overview()

        # Main options menu
        options_schema = vol.Schema({
            vol.Required("action"): vol.In({
                "manage_users": "Manage Selected Users",
                "reset_stats": "Reset Game Statistics"
            }),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "current_user_count": str(len(self.config_entry.data.get(CONF_SELECTED_USERS, []))),
                "token_url": f"{self.hass.config.external_url or self.hass.config.internal_url}/profile/security"
            }
        )

    async def async_step_manage_users(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage selected users and token."""
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
            step_id="manage_users",
            data_schema=options_schema,
            errors=errors,
            description_placeholders={
                "current_user_count": str(len(current_selection)),
                "token_url": f"{self.hass.config.external_url or self.hass.config.internal_url}/profile/security"
            }
        )

    async def async_step_stats_overview(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Show overview of users with statistics."""
        if user_input is not None:
            return await self.async_step_stats_selection()

        # Get users with stats
        self._users_with_stats = await self._get_users_with_stats()
        
        if not self._users_with_stats:
            return self.async_show_form(
                step_id="stats_overview",
                data_schema=vol.Schema({}),
                errors={"base": "no_stats_found"},
                description_placeholders={}
            )

        # Build stats summary for display
        stats_summary = []
        for user_data in self._users_with_stats:
            stats = user_data.get('stats', {})
            summary = (
                f"**{user_data['name']}**: "
                f"{stats.get('games_played', 0)} games, "
                f"{stats.get('games_won', 0)} wins, "
                f"{stats.get('win_rate', 0):.1f}% win rate"
            )
            stats_summary.append(summary)

        stats_text = "\n".join(stats_summary)

        # Simple continue schema
        continue_schema = vol.Schema({
            vol.Required("continue", default=True): cv.boolean,
        })

        return self.async_show_form(
            step_id="stats_overview",
            data_schema=continue_schema,
            description_placeholders={
                "stats_summary": stats_text,
                "user_count": str(len(self._users_with_stats))
            }
        )

    async def async_step_stats_selection(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Select users whose stats to reset."""
        if user_input is not None:
            selected_users = user_input.get("users_to_reset", [])
            if not selected_users:
                return self.async_show_form(
                    step_id="stats_selection",
                    data_schema=self._build_stats_selection_schema(),
                    errors={"base": "no_users_selected_for_reset"}
                )
            
            # Store selected users for confirmation step
            self._selected_users_for_reset = selected_users
            return await self.async_step_stats_confirmation()

        return self.async_show_form(
            step_id="stats_selection",
            data_schema=self._build_stats_selection_schema(),
        )

    def _build_stats_selection_schema(self):
        """Build schema for user selection."""
        user_options = {}
        
        for user_data in self._users_with_stats:
            stats = user_data.get('stats', {})
            display_name = (
                f"{user_data['name']} - "
                f"{stats.get('games_played', 0)} games, "
                f"{stats.get('games_won', 0)} wins, "
                f"{stats.get('win_rate', 0):.1f}% win rate"
            )
            user_options[user_data['user_id']] = display_name

        return vol.Schema({
            vol.Required("users_to_reset"): cv.multi_select(user_options),
        })

    async def async_step_stats_confirmation(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Final confirmation before resetting stats."""
        if user_input is not None:
            if user_input.get("confirm_reset"):
                # Perform the reset
                reset_results = await self._reset_user_stats(self._selected_users_for_reset)
                
                if reset_results["success"]:
                    return self.async_show_form(
                        step_id="stats_confirmation",
                        data_schema=vol.Schema({}),
                        errors={"base": "stats_reset_success"},
                        description_placeholders={
                            "reset_count": str(reset_results["reset_count"]),
                            "details": reset_results["details"]
                        }
                    )
                else:
                    return self.async_show_form(
                        step_id="stats_confirmation",
                        data_schema=self._build_confirmation_schema(),
                        errors={"base": "stats_reset_failed"},
                        description_placeholders={
                            "error_details": reset_results.get("error", "Unknown error")
                        }
                    )
            else:
                # User cancelled, return to main menu
                return await self.async_step_init()

        return self.async_show_form(
            step_id="stats_confirmation",
            data_schema=self._build_confirmation_schema(),
            description_placeholders={
                "users_to_reset": self._format_users_for_confirmation(),
                "warning": "This action cannot be undone!"
            }
        )

    def _build_confirmation_schema(self):
        """Build confirmation schema."""
        return vol.Schema({
            vol.Required("confirm_reset", default=False): cv.boolean,
        })

    def _format_users_for_confirmation(self):
        """Format selected users for confirmation display."""
        user_lines = []
        for user_data in self._users_with_stats:
            if user_data['user_id'] in self._selected_users_for_reset:
                stats = user_data.get('stats', {})
                line = (
                    f"• **{user_data['name']}**: "
                    f"{stats.get('games_played', 0)} games played, "
                    f"{stats.get('games_won', 0)} wins, "
                    f"{stats.get('win_rate', 0):.1f}% win rate, "
                    f"{stats.get('max_streak', 0)} max streak"
                )
                user_lines.append(line)
        
        return "\n".join(user_lines)

    async def _get_users_with_stats(self) -> List[Dict[str, Any]]:
        """Get list of users who have game statistics."""
        try:
            users = await self.hass.auth.async_get_users()
            selected_user_ids = self.config_entry.data.get(CONF_SELECTED_USERS, [])
            users_with_stats = []
            
            for user in users:
                if user.id not in selected_user_ids or user.system_generated:
                    continue
                
                # Check if user has stats
                store = storage.Store(self.hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}_{user.id}")
                stats_data = await store.async_load()
                
                if stats_data and stats_data.get('games_played', 0) > 0:
                    users_with_stats.append({
                        'user_id': user.id,
                        'name': user.name or "Unnamed User",
                        'stats': stats_data
                    })
            
            return users_with_stats
            
        except Exception as e:
            _LOGGER.error(f"Error getting users with stats: {e}")
            return []

    async def _reset_user_stats(self, user_ids: List[str]) -> Dict[str, Any]:
        """Reset statistics for specified users."""
        try:
            reset_count = 0
            reset_details = []
            
            for user_id in user_ids:
                try:
                    # Get user name for logging
                    user = await self.hass.auth.async_get_user(user_id)
                    user_name = user.name if user else user_id
                    
                    # Step 1: Delete storage file
                    store = storage.Store(self.hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}_{user_id}")
                    await store.async_remove()
                    
                    # Step 2: Reset sensor entity if it exists
                    sensor_entity_id = f"sensor.ha_wordplay_stats_{user_id}"
                    
                    # Get the sensor entity from the domain data
                    domain_data = self.hass.data.get(DOMAIN, {})
                    user_entities = domain_data.get("entities", {}).get(user_id, {})
                    stats_sensor = user_entities.get("stats")
                    
                    if stats_sensor:
                        # Reset sensor to default stats
                        default_stats = {
                            'games_played': 0,
                            'games_won': 0,
                            'total_guesses': 0,
                            'guess_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
                            'win_streak': 0,
                            'max_streak': 0,
                            'last_played': None,
                            'average_guesses': 0.0,
                            'win_rate': 0.0,
                            'total_play_time': 0,
                            'fastest_win': None,
                            'difficulty_stats': {
                                'easy': {'played': 0, 'won': 0},
                                'normal': {'played': 0, 'won': 0},
                                'hard': {'played': 0, 'won': 0}
                            }
                        }
                        
                        stats_sensor.update_stats(0, default_stats)
                    
                    # Step 3: Reset in-memory game stats if game exists
                    games = domain_data.get("games", {})
                    if user_id in games:
                        game = games[user_id]
                        # Reset the game's stats to defaults
                        game.stats = {
                            'games_played': 0,
                            'games_won': 0,
                            'total_guesses': 0,
                            'guess_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0},
                            'win_streak': 0,
                            'max_streak': 0,
                            'last_played': None,
                            'average_guesses': 0.0,
                            'win_rate': 0.0,
                            'total_play_time': 0,
                            'fastest_win': None,
                            'difficulty_stats': {
                                'easy': {'played': 0, 'won': 0},
                                'normal': {'played': 0, 'won': 0},
                                'hard': {'played': 0, 'won': 0}
                            }
                        }
                    
                    reset_count += 1
                    reset_details.append(f"✅ {user_name}: All stats reset successfully")
                    _LOGGER.info(f"Reset stats for user {user_name} ({user_id})")
                    
                except Exception as user_error:
                    reset_details.append(f"❌ {user_name}: Error - {str(user_error)}")
                    _LOGGER.error(f"Error resetting stats for user {user_id}: {user_error}")
            
            return {
                "success": True,
                "reset_count": reset_count,
                "details": "\n".join(reset_details)
            }
            
        except Exception as e:
            _LOGGER.error(f"Error in stats reset process: {e}")
            return {
                "success": False,
                "error": str(e),
                "reset_count": 0,
                "details": ""
            }

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