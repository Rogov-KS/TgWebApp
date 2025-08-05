import urllib.parse
import secrets

from backend.core.config import settings
# from backend.core.state_storage import state_storage


def generate_google_oauth_redirect_uri() -> str:
    '''
    Generate Google OAuth redirect URI

    Returns:
        str: Google OAuth redirect URI
    '''
    random_state = secrets.token_urlsafe(16)
    # state_storage.add(random_state)

    query_params = {
        "client_id": settings.OATH_GOOGLE_WEB_CLIENT_ID,
        "redirect_uri": "http://localhost:5173/auth/google",
        "response_type": "code",
        "scope": " ".join([
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/calendar",
            "openid",
            "profile",
            "email",
        ]),
        "access_type": "offline",
        "state": random_state,
    }

    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{query_string}"
