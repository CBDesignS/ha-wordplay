# Only showing the modified _get_user_id function and service handlers
# Add this modified function to your existing __init__.py

def _get_user_id(call: ServiceCall) -> str:
    """Extract user ID from service call context or data."""
    # First check if user_id was explicitly passed in the service data
    if "user_id" in call.data:
        user_id = call.data.get("user_id")
        if user_id:
            _LOGGER.debug(f"Using explicit user_id from service data: {user_id}")
            return user_id
    
    # Fall back to context user_id
    user_id = call.context.user_id
    if not user_id:
        # Fallback for admin or system calls
        user_id = "default"
    return user_id

# Update the service handlers to remove user_id from data before processing
async def handle_new_game(call: ServiceCall) -> None:
    """Handle new game service call."""
    try:
        user_id = _get_user_id(call)
        game = _get_or_create_game(hass, user_id)
        
        # Remove user_id from data if present
        service_data = dict(call.data)
        service_data.pop("user_id", None)
        
        word_length = service_data.get("word_length", DEFAULT_WORD_LENGTH)
        language = service_data.get("language", "en")
        
        # Rest of the function remains the same...
        # Try to get from user's select entity if not provided
        if not word_length or word_length == DEFAULT_WORD_LENGTH:
            select_state = hass.states.get(f"select.ha_wordplay_word_length_{user_id}")
            if select_state and select_state.state:
                try:
                    word_length = int(select_state.state)
                except (ValueError, TypeError):
                    word_length = DEFAULT_WORD_LENGTH
        
        success = await game.start_new_game(int(word_length), language)
        
        if success:
            _LOGGER.info(f"New game started for user {user_id}: {word_length} letters, language: {language}")
            await _update_button_attributes(hass, user_id)
        else:
            _LOGGER.error(f"Failed to start new game for user {user_id}")
    except Exception as e:
        _LOGGER.error(f"Error in new_game service: {e}")

async def handle_make_guess(call: ServiceCall) -> None:
    """Handle make guess service call."""
    try:
        user_id = _get_user_id(call)
        game = _get_or_create_game(hass, user_id)
        
        # Remove user_id from data if present
        service_data = dict(call.data)
        service_data.pop("user_id", None)
        
        guess = service_data.get("guess", "").upper()
        if guess:
            result = await game.make_guess(guess)
            if "error" in result:
                _LOGGER.warning(f"Guess error for user {user_id}: {result['error']}")
            else:
                _LOGGER.info(f"Guess processed for user {user_id}: {guess}")
            await _update_button_attributes(hass, user_id)
        else:
            _LOGGER.warning(f"No guess provided to make_guess service for user {user_id}")
    except Exception as e:
        _LOGGER.error(f"Error in make_guess service: {e}")

async def handle_get_hint(call: ServiceCall) -> None:
    """Handle get hint service call."""
    try:
        user_id = _get_user_id(call)
        game = _get_or_create_game(hass, user_id)
        
        hint = await game.get_hint()
        _LOGGER.info(f"Hint requested by user {user_id}: {hint}")
        await _update_button_attributes(hass, user_id)
    except Exception as e:
        _LOGGER.error(f"Error in get_hint service: {e}")

async def handle_submit_guess(call: ServiceCall) -> None:
    """Handle submit current guess service call."""
    try:
        user_id = _get_user_id(call)
        game = _get_or_create_game(hass, user_id)
        
        # Get current input from user's text entity state
        text_state = hass.states.get(f"text.ha_wordplay_guess_input_{user_id}")
        guess = None
        
        if text_state and text_state.state:
            guess = text_state.state.upper().strip()
        
        if guess and guess != "HELLO":
            result = await game.make_guess(guess)
            if "error" in result:
                _LOGGER.warning(f"Submit guess error for user {user_id}: {result['error']}")
            else:
                _LOGGER.info(f"Guess submitted by user {user_id}: {guess}")
            await _update_button_attributes(hass, user_id)
        else:
            _LOGGER.warning(f"No valid guess to submit for user {user_id}")
    except Exception as e:
        _LOGGER.error(f"Error in submit_guess service: {e}")