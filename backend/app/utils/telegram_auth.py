"""
Telegram WebApp authentication utilities.

Validates Telegram WebApp init_data using HMAC-SHA256 as documented at:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import urllib.parse
from typing import Optional


def validate_telegram_web_app_data(
    init_data: str, bot_token: str
) -> Optional[dict]:
    """
    Validate Telegram WebApp init_data and return parsed dict if valid.

    Returns None if validation fails.
    """
    try:
        parsed = urllib.parse.parse_qs(init_data)
        hash_value = parsed.get("hash", [None])[0]
        if not hash_value:
            return None

        # Build data-check-string: sorted key=value pairs except 'hash'
        data_check_items = []
        for key in sorted(parsed.keys()):
            if key == "hash":
                continue
            value = parsed[key][0]
            data_check_items.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_items)

        # Compute secret key: HMAC-SHA256(bot_token, "WebAppData")
        secret_key = hmac.new(
            "WebAppData".encode(), bot_token.encode(), hashlib.sha256
        ).digest()

        # Compute hash: HMAC-SHA256(secret_key, data_check_string)
        computed_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        # Compare hashes
        if not hmac.compare_digest(computed_hash, hash_value):
            return None

        # Return parsed data as flat dict
        result = {}
        for key, values in parsed.items():
            result[key] = values[0]
        return result

    except Exception:
        return None


def get_telegram_user_id(init_data: str, bot_token: str) -> Optional[str]:
    """
    Validate init_data and extract the Telegram user ID.

    Returns the user ID string if valid, None otherwise.
    """
    data = validate_telegram_web_app_data(init_data, bot_token)
    if data is None:
        return None

    user_json = data.get("user")
    if not user_json:
        return None

    try:
        user = json.loads(user_json)
        return str(user.get("id"))
    except (json.JSONDecodeError, AttributeError):
        return None