# 0005. OAuth2 Provider Authentication

Date: 2026-04-06

## Status
Proposed

## Context

The application currently supports only email/password authentication with JWT tokens. Users increasingly expect social login options (Google, GitHub) for convenience and reduced password fatigue. Adding OAuth2 support will:

- Lower friction for new user registration
- Reduce password-related support burden
- Enable future integrations that require provider API access (e.g., GitHub repo import)

## Decision

We will add OAuth2 authentication with Google and GitHub as initial providers, using the authorization code flow (server-side).

Key design choices:

1. **Separate `oauth_accounts` table** — rather than adding columns to `users`, we create a linking table so users can connect multiple providers and retain email/password login.

2. **Email-based account linking** — when a user logs in via OAuth2 and their provider email matches an existing account, we link automatically rather than creating a duplicate user.

3. **Same JWT output** — OAuth2 login returns the same JWT access/refresh token format as email/password login. Downstream code doesn't need to know how the user authenticated.

4. **Server-side flow only** — we implement the authorization code flow on the backend. No implicit/client-side token flow. The frontend redirects to our `/authorize` endpoint, which redirects to the provider, and the callback comes back to our server.

5. **Authlib library** — we use [Authlib](https://authlib.org/) for OAuth2 client implementation rather than rolling our own. It handles token exchange, PKCE, and provider quirks.

## Consequences

### Easier
- Users can sign up/in with one click via Google or GitHub
- Adding more providers in the future follows the same pattern
- Account linking by email reduces duplicate accounts

### Harder
- New table and migration to manage
- Must securely store provider tokens (encryption at rest)
- Must handle edge cases: email conflicts, provider downtime, revoked tokens
- Environment configuration grows (client IDs/secrets per provider)
- Testing requires mocking provider OAuth2 flows
