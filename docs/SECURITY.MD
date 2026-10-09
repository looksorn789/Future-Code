# Security

This document describes how the backend authenticates users, protects routes, and handles secrets.

Items marked **(planned)** are designed but not implemented yet.

## Table of Contents

- Authentication Model
- Token Lifecycle
- Protecting Routes (`@login_required`, `@role_required`)
- Cookies, CORS and CSRF
- Passwords and Login Hardening
- OAuth / Cognito
- Secrets and Configuration
- Checklist

---

## Authentication Model

A logged-in user holds **two tokens**:

| | Access token | Session token |
|---|---|---|
| **Format** | JWT, signed HS256 with `JWT_SECRET` | Opaque random string (`secrets.token_urlsafe(32)`) |
| **Lifetime** | 15 minutes | 14 days, renewed on every refresh |
| **Where the client keeps it** | In memory only (React `AuthContext`), **never** `localStorage` | `HttpOnly` cookie (JavaScript cannot read it) |
| **How it is sent** | `Authorization: Bearer <token>` header | Automatically by the browser, only to `/api/auth/*` |
| **Where the server keeps it** | Nowhere, it is stateless | SHA-256 hash in the `sessions` table |
| **Used for** | Every protected API call | Getting a new access token, logging out |
| **Revocable?** | No, it expires on its own | Yes, delete or revoke the row |

Why both:

- **The JWT is fast.** `@login_required` checks the signature and expiry without a database query.
- **The session token can be revoked.** If you delete or revoke the database row, the user is logged out on that device. "Log out of all devices" revokes every row for that user. A JWT on its own cannot be revoked, so we keep it short-lived and let the session token re-issue it.
- **XSS exposure is limited.** The long-lived credential sits in an `HttpOnly` cookie, so an injected script cannot steal it. The access token lives in memory and is useless after 15 minutes.

> **"Session token" here is not Flask's built-in `flask.session`.** `flask.session` is a signed cookie that stores data on the client and cannot be revoked server-side. We do not use it, so the app does not need `SECRET_KEY` for authentication.

### JWT claims

```json
{
  "sub": "42",                       // user id (string, per the JWT spec)
  "role": "user",                    // "user" | "admin"
  "sid": "3f6c...",                  // session id: links this JWT to a row in `sessions`
  "type": "access",
  "iss": "interviewprepai",
  "aud": "interviewprepai-api",
  "iat": 1760000000,
  "exp": 1760000900
}
```

Do not put anything secret or personal in a JWT (email, name, resume data). A JWT is only base64-encoded, so anyone holding it can read it.

---

## Token Lifecycle

```
Login     POST /api/auth/login     email + password
          → verify password
          → create sessions row (store sha256(session_token))
          → 200 { access_token, user }  +  Set-Cookie: session_token=...

API call  GET /api/resumes         Authorization: Bearer <access_token>
          → @login_required verifies signature + exp → g.user_id, g.role

Expired   API returns 401 { code: "token_expired" }
          → frontend calls POST /api/auth/refresh (cookie sent automatically)
          → server looks up sha256(cookie) in sessions, checks not revoked / not expired
          → ROTATE: new session_token, update hash, push expires_at forward
          → 200 { access_token }  +  Set-Cookie: new session_token
          → frontend retries the original request once

Page load Access token is gone from memory → frontend calls /api/auth/refresh once

Logout    POST /api/auth/logout    → set sessions.revoked_at, clear cookie → 204
```

Rules:

- **Rotate the session token on every refresh.** A stolen session token stays valid only until the real user's next refresh.
- **Only store a hash of the session token.** If the database leaks, the attacker cannot use the stored values as cookies. The token already has 256 bits of randomness, so plain SHA-256 is enough. It does not need a slow hash like a password does.
- **Refresh fails closed.** A token that is missing, unknown, expired or revoked returns 401, clears the cookie, and the frontend sends the user to `/login`.
- **(planned) Detect reuse.** Keep the previous token hash for each session. If someone presents a token that has already been rotated, the token was stolen, so revoke the whole session.

---

## Protecting Routes

The decorators live in `backend/utils/auth.py` **(planned)**.

| Decorator / helper | Purpose | Failure |
|---|---|---|
| `@login_required` | Requires a valid access token. Sets `g.user_id`, `g.role` and `g.session_id`. | `401` |
| `@login_required(check_session=True)` | Also checks that the session row is still active. Use it for sensitive actions: change password, delete account, log out of all devices. | `401` |
| `@role_required("admin")` | Logged in **and** has one of the listed roles (it implies `@login_required`). | `401` / `403` |
| `get_current_user()` | Loads the `User` row once per request and caches it on `g`. | — |

### Where the decorator goes, and where it doesn't

```python
@auth_bp.post("/login")                 # NO decorator: the caller is not logged in yet.
def login():                            # This endpoint *creates* the session.
    ...

@resumes_bp.get("/")
@login_required                         # any logged-in user
def list_resumes():
    return resume_service.list_for_user(g.user_id)

@admin_bp.get("/users")
@role_required("admin")                 # only admins
def list_users():
    ...
```

Do not put a verification decorator such as `@verify` on `login` itself. A decorator runs **before** the view, and before login the caller has no token to verify. Checking the email and password is the job of `login`, done in `auth_service.authenticate(email, password)`. The decorators protect every route **after** login.

A call like `verified.user("user")` becomes `@role_required("user")` (or just `@login_required`, since every account has at least the `user` role).

### Reference implementation

```python
# backend/utils/auth.py
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from extensions import db
from models.session import Session
from models.user import User


def _error(code, status):
    return jsonify(error={"code": code}), status


def _decode_access_token(token):
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET"],
        algorithms=["HS256"],                     # pin it: never trust the token's own "alg" header
        audience=current_app.config["JWT_AUDIENCE"],
        issuer=current_app.config["JWT_ISSUER"],
        options={"require": ["exp", "iat", "sub", "sid"]},
    )


def login_required(fn=None, *, check_session=False):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            scheme, _, token = request.headers.get("Authorization", "").partition(" ")
            if scheme.lower() != "bearer" or not token:
                return _error("authentication_required", 401)
            try:
                claims = _decode_access_token(token)
            except jwt.ExpiredSignatureError:
                return _error("token_expired", 401)   # frontend: refresh and retry
            except jwt.InvalidTokenError:
                return _error("invalid_token", 401)
            if claims.get("type") != "access":
                return _error("invalid_token", 401)

            if check_session:
                session = db.session.get(Session, claims["sid"])
                if session is None or not session.is_active:
                    return _error("session_revoked", 401)

            g.user_id = int(claims["sub"])
            g.role = claims["role"]
            g.session_id = claims["sid"]
            return view(*args, **kwargs)
        return wrapper

    return decorator(fn) if fn else decorator     # supports @login_required and @login_required(...)


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if g.role not in roles:
                return _error("forbidden", 403)
            return view(*args, **kwargs)
        return login_required(wrapper)
    return decorator


def get_current_user():
    if "current_user" not in g:
        g.current_user = db.session.get(User, g.user_id)
    return g.current_user
```

Notes:

- The role in the JWT may be up to 15 minutes stale. If someone is demoted from admin, their admin access ends when the token expires. Use `check_session=True`, or re-read the role from the database, where that delay is not acceptable.
- `401` means "you are not authenticated" (missing, expired or invalid token). `403` means "you are authenticated but not allowed". The frontend refreshes only on `401` with `token_expired`.

---

## Cookies, CORS and CSRF

### Session cookie attributes

```python
response.set_cookie(
    "session_token",
    token,
    max_age=SESSION_TTL_DAYS * 86400,
    httponly=True,                       # not readable from JavaScript
    secure=app.config["COOKIE_SECURE"],  # True in production (HTTPS only)
    samesite="Lax",                      # not sent on cross-site POSTs
    path="/api/auth",                    # only sent to refresh/logout, not every API call
)
```

### CORS

The frontend and the API run on different origins (the Vite dev server and Flask on `:5000`), so CORS must allow the frontend origin **with credentials** (cookies):

```python
cors.init_app(
    app,
    resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"]]}},
    supports_credentials=True,
)
```

- The resource pattern must start with `/`. Flask-CORS matches it against `request.path`, and `request.path` always starts with `/`.
- The keyword is `supports_credentials`, with an "s". Flask-CORS silently ignores the misspelling `support_credentials`.
- Never combine `origins="*"` with credentials. Always list origins explicitly.
- On the frontend, every call to `/api/auth/refresh` and `/api/auth/logout` must use `fetch(url, { method: "POST", credentials: "include" })`.

> Alternative for local development: configure a Vite `server.proxy` for `/api` → `http://127.0.0.1:5000`. The browser then sees a single origin, and CORS is not involved in development.

### CSRF

- Endpoints authenticated by the **`Authorization` header** cannot be hit by CSRF. A malicious site cannot make the browser attach that header.
- Endpoints authenticated by the **cookie** (`/refresh`, `/logout`) need protection:
  1. They accept `POST` only, never `GET`.
  2. The cookie uses `SameSite=Lax`, so the browser does not send it on cross-site POSTs.
  3. The server checks that the `Origin` header equals `FRONTEND_ORIGIN` and rejects the request otherwise.
  4. Requests must use `Content-Type: application/json` (or a custom header such as `X-Requested-With`). This forces a CORS preflight, which a foreign origin fails.

---

## Passwords and Login Hardening

- Hash passwords with `werkzeug.security.generate_password_hash`, which is already installed with Flask and uses scrypt by default. Check them with `check_password_hash`. Never store or log plain-text passwords.
- Use **one generic error** for a wrong email and a wrong password: `401 { code: "invalid_credentials" }`. This avoids revealing which emails have accounts (account enumeration).
- If the email does not exist, still run `check_password_hash` against a dummy hash. Otherwise the faster response time reveals that the email is unknown.
- Normalize emails (`strip().lower()`) before saving and looking them up.
- Require at least 8 characters for passwords. Do not impose composition rules.
- **(planned)** Rate-limit `/login`, `/register` and `/refresh` with Flask-Limiter, for example 5 login attempts per minute per IP and per email.
- **(planned)** Changing the password revokes every other session for that user.
- **(planned)** Email verification: the `users.email_verified_at` column, plus a single-use, expiring verification token stored hashed (same pattern as session tokens).

---

## OAuth / Cognito

The README lists Amazon Cognito and Google/GitHub OAuth. They fit the model above as **alternative ways to prove identity at login**. They do not replace the session layer:

```
Google / GitHub / Cognito callback  →  backend verifies the provider's ID token
                                    →  find-or-create the User (by provider + provider_user_id)
                                    →  issue OUR access token + session token, exactly like password login
```

The rest of the app (`@login_required`, refresh, logout) stays the same whichever way the user logged in.

If you later decide to let Cognito issue the tokens itself, `_decode_access_token` changes to verify Cognito's RS256 JWTs against its JWKS endpoint. The decorators and routes stay the same.

---

## Secrets and Configuration

| Variable | Required | Purpose |
|---|---|---|
| `JWT_SECRET` | yes | HMAC key that signs access tokens. Generate it with `python -c "import secrets; print(secrets.token_urlsafe(64))"`. |
| `JWT_ISSUER` / `JWT_AUDIENCE` | (planned) | `iss` / `aud` claims. Defaults: `interviewprepai` / `interviewprepai-api`. |
| `ACCESS_TOKEN_TTL_MINUTES` | (planned) | Default `15`. |
| `SESSION_TTL_DAYS` | (planned) | Default `14`. |
| `COOKIE_SECURE` | (planned) | `false` for local http, `true` in production. |
| `FRONTEND_ORIGIN` | no | The only origin CORS allows. It must match the Vite dev server (default `http://localhost:5173`). |

- `.env` is git-ignored. Add every new variable to `backend/.env.example` with a placeholder value.
- Each environment (dev, staging, prod) uses a different `JWT_SECRET`. Rotating it logs everyone out (all JWTs become invalid). Session tokens survive the rotation, so users simply refresh.
- In production, load secrets from AWS Secrets Manager or SSM Parameter Store, not from a file on the server.
- Never log `Authorization` headers, cookies, tokens or passwords.

---

## Checklist

- [ ] Fix blueprint prefix: `url_prefix="/api/auth"` (Werkzeug rejects rules without a leading `/`)
- [x] Fix CORS: `r"/api/*"` and `supports_credentials=True`
- [ ] Align `FRONTEND_ORIGIN` default with the Vite port (`5173`)
- [ ] `User` and `Session` models + migration
- [ ] `utils/auth.py` with `login_required`, `role_required`, `get_current_user`
- [ ] `services/auth_service.py`: register, authenticate, create/rotate/revoke session, issue JWT
- [ ] Auth endpoints: register, login, refresh, logout, logout-all, me
- [ ] Origin check on cookie-authenticated endpoints
- [ ] Rate limiting on auth endpoints
- [ ] Frontend `AuthContext`: in-memory access token, refresh on load and on `token_expired`
- [ ] Tests: expired token, tampered token, wrong `alg`, revoked session, rotated-token reuse, role denial
