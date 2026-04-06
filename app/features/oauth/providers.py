"""OAuth2 provider configurations and token exchange logic."""

from dataclasses import dataclass

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.core.config import settings


@dataclass
class OAuthUserInfo:
    """Normalized user info from any OAuth2 provider."""

    provider: str
    provider_user_id: str
    email: str
    name: str


PROVIDER_CONFIGS: dict[str, dict] = {
    "google": {
        "client_id": lambda: settings.GOOGLE_CLIENT_ID,
        "client_secret": lambda: settings.GOOGLE_CLIENT_SECRET,
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
    },
    "github": {
        "client_id": lambda: settings.GITHUB_CLIENT_ID,
        "client_secret": lambda: settings.GITHUB_CLIENT_SECRET,
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scope": "user:email",
    },
}

SUPPORTED_PROVIDERS = list(PROVIDER_CONFIGS.keys())


def get_redirect_uri(provider: str) -> str:
    return f"{settings.OAUTH2_REDIRECT_BASE_URL}/api/v1/auth/oauth/{provider}/callback"


def create_oauth_client(provider: str) -> AsyncOAuth2Client:
    config = PROVIDER_CONFIGS[provider]
    return AsyncOAuth2Client(
        client_id=config["client_id"](),
        client_secret=config["client_secret"](),
        redirect_uri=get_redirect_uri(provider),
        scope=config["scope"],
    )


def get_authorization_url(provider: str, state: str) -> str:
    config = PROVIDER_CONFIGS[provider]
    client = create_oauth_client(provider)
    url, _ = client.create_authorization_url(config["authorize_url"], state=state)
    return url


async def exchange_code_for_user_info(provider: str, code: str) -> OAuthUserInfo:
    """Exchange authorization code for tokens, then fetch user info."""
    config = PROVIDER_CONFIGS[provider]
    client = create_oauth_client(provider)

    token = await client.fetch_token(
        config["token_url"],
        code=code,
        grant_type="authorization_code",
    )

    access_token = token["access_token"]

    if provider == "google":
        return await _fetch_google_user(config["userinfo_url"], access_token)
    elif provider == "github":
        return await _fetch_github_user(config["userinfo_url"], access_token)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def _fetch_google_user(userinfo_url: str, access_token: str) -> OAuthUserInfo:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        data = resp.json()
    return OAuthUserInfo(
        provider="google",
        provider_user_id=data["id"],
        email=data["email"],
        name=data.get("name", data["email"]),
    )


async def _fetch_github_user(userinfo_url: str, access_token: str) -> OAuthUserInfo:
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        resp = await client.get(userinfo_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        # GitHub may not return email in profile; fetch from emails endpoint
        email = data.get("email")
        if not email:
            email_resp = await client.get(
                "https://api.github.com/user/emails", headers=headers
            )
            email_resp.raise_for_status()
            emails = email_resp.json()
            primary = next(
                (e for e in emails if e.get("primary") and e.get("verified")),
                None,
            )
            if primary:
                email = primary["email"]

    if not email:
        raise ValueError("GitHub account has no verified email")

    return OAuthUserInfo(
        provider="github",
        provider_user_id=str(data["id"]),
        email=email,
        name=data.get("name") or data.get("login", email),
    )
