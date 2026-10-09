# API Reference

Base URL (local): `http://127.0.0.1:5000/api`

All endpoints marked **(planned)** are designed but not implemented yet. See [SECURITY.MD](./SECURITY.MD) for how authentication works.

## Conventions

- Request and response bodies are JSON (`Content-Type: application/json`).
- Protected endpoints require `Authorization: Bearer <access_token>`.
- Endpoints marked 🍪 authenticate with the `session_token` cookie. Call them with `credentials: "include"`.

### Errors

Every error uses the same shape:

```json
{ "error": { "code": "invalid_credentials", "message": "Email or password is incorrect." } }
```

| Status | Typical `code` | Meaning |
|---|---|---|
| 400 | `validation_error` | Malformed or missing fields (`error.fields` lists them) |
| 401 | `authentication_required` | No access token sent |
| 401 | `token_expired` | Access token expired. Call `/auth/refresh`, then retry once |
| 401 | `invalid_token` | Tampered, malformed or wrong-type token |
| 401 | `session_revoked` | Session logged out or expired. Send the user to the login page |
| 401 | `invalid_credentials` | Wrong email or password (deliberately not more specific) |
| 403 | `forbidden` | Logged in but missing the required role |
| 409 | `email_taken` | Registration with an existing email |
| 429 | `rate_limited` | Too many attempts |

---

## Auth — `/api/auth`

### `POST /auth/register` (planned)

```json
// request
{ "email": "ada@example.com", "password": "correct horse battery", "name": "Ada" }
```

`201 Created` + `Set-Cookie: session_token=...; HttpOnly; SameSite=Lax; Path=/api/auth`

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": { "id": 42, "email": "ada@example.com", "name": "Ada", "role": "user" }
}
```

Errors: `400 validation_error`, `409 email_taken`, `429 rate_limited`

### `POST /auth/login` (planned)

```json
{ "email": "ada@example.com", "password": "correct horse battery" }
```

`200 OK` + `Set-Cookie: session_token=...`. The body is the same as for register.

Errors: `400 validation_error`, `401 invalid_credentials`, `429 rate_limited`

### `POST /auth/refresh` 🍪 (planned)

No body. Rotates the session token and returns a new access token.

`200 OK` + `Set-Cookie: session_token=<new value>`

```json
{ "access_token": "eyJhbGciOi...", "token_type": "Bearer", "expires_in": 900 }
```

Errors: `401 session_revoked` (cookie cleared), `403 forbidden` (bad `Origin`)

### `POST /auth/logout` 🍪 (planned)

Revokes the current session and clears the cookie. Always returns `204 No Content`, even if the session was already gone.

### `POST /auth/logout-all` 🔒 (planned)

Requires a Bearer token. Uses `@login_required(check_session=True)`. Revokes **every** session for the user. Returns `204 No Content`.

### `GET /auth/me` 🔒 (planned)

```json
{ "id": 42, "email": "ada@example.com", "name": "Ada", "role": "user", "email_verified": false }
```

---

## Frontend integration

```ts
// api/client.ts (sketch)
let accessToken: string | null = null;

export async function api(path: string, init: RequestInit = {}, retry = true): Promise<Response> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init.headers,
    },
  });

  if (res.status === 401 && retry) {
    const body = await res.clone().json().catch(() => null);
    if (body?.error?.code === "token_expired" && (await refresh())) {
      return api(path, init, false);           // retry once with the new token
    }
  }
  return res;
}

export async function refresh(): Promise<boolean> {
  const res = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",                     // send the HttpOnly session cookie
    headers: { "Content-Type": "application/json" },
  });
  accessToken = res.ok ? (await res.json()).access_token : null;
  return res.ok;
}
```

- On app start, call `refresh()` once. If it succeeds, the user is still logged in.
- Several requests can fail with `token_expired` at the same moment. Share one in-flight `refresh()` promise between them instead of starting several refreshes. Each refresh rotates the cookie, so parallel refreshes would race.
