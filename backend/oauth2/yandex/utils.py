import urllib.parse
import secrets

from backend.core.config import settings
# from backend.core.state_storage import state_storage


def generate_yandex_oauth_redirect_uri(state: str = None) -> str:
    '''
    Generate Yandex OAuth redirect URI

    Args:
        state: OAuth state parameter (если не передан, генерируется случайный)

    Returns:
        str: Yandex OAuth redirect URI
    '''
    if state is None:
        state = secrets.token_urlsafe(16)
    # state_storage.add(random_state)

    query_params = {
        "client_id": settings.OATH_YANDEX_WEB_CLIENT_ID,
        "redirect_uri": "http://localhost:5173/auth/yandex",
        "response_type": "code",
        "access_type": "offline",
        "scope": " ".join([
            "login:avatar",
            "login:birthday",
            "login:email",
            "cloud_api:disk.read",
            "login:info",
            "calendar:all"
        ]),
        "state": state,
    }
    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    base_url = "https://oauth.yandex.ru/authorize?"
    return f"{base_url}{query_string}"
