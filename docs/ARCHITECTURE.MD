# Architecture

Future Code is a cloud-native full-stack web application that helps
software engineering candidates prepare for technical interviews using
AI-powered tools such as resume analysis, mock interviews, coding
challenges, and personalized feedback.

The application follows a client-server architecture where the React
frontend communicates with a Flask REST API backend. The backend manages
authentication, business logic, database operations, AI integrations, and
file storage through PostgreSQL, AWS services, and the OpenAI API.

## Table of Contents

- High-Level Architecture
- Backend Structure
- Authentication Flow
- Resume Upload Flow
- AI Processing
- Database Architecture
- Deployment Architecture

---

## High-Level Architecture

![Architecture](../design/Architecture/Overview.png)

> Editable source: [architecture.drawio](../design/Architecture/Overview.drawio)

---

## Backend Structure

The Flask app is built by an application factory, `create_app()` in `backend/app.py`:

1. Load `Config` from environment variables (`backend/config.py` + `.env`).
2. Initialize the shared extensions from `backend/extensions.py`: `cors`, `db` (SQLAlchemy) and `migrate` (Flask-Migrate).
3. Register one Blueprint per resource through `routes.register_routes(app)`.

Requests go through three layers:

```
routes/ (Blueprints, HTTP only) → services/ (business logic) → models/ (SQLAlchemy)
        ↑
  utils/auth.py decorators (@login_required, @role_required) run before the view
```

See [FILE_STRUCTURE.MD](./FILE_STRUCTURE.MD) for where each piece lives.

---

## Authentication Flow

The client authenticates with a short-lived **JWT access token** (15 min, sent as a Bearer header) and a long-lived, revocable **session token** (an `HttpOnly` cookie backed by the `sessions` table). See [SECURITY.MD](./SECURITY.MD) for the full design.

```mermaid
sequenceDiagram
    participant B as Browser (React)
    participant A as Flask API
    participant D as Database

    B->>A: POST /api/auth/login {email, password}
    A->>D: find user, check password hash
    A->>D: INSERT sessions (token_hash = sha256(session_token))
    A-->>B: 200 {access_token} + Set-Cookie session_token (HttpOnly)

    B->>A: GET /api/... Authorization: Bearer access_token
    Note over A: @login_required: verify signature + exp (no DB query)
    A-->>B: 200 data

    B->>A: GET /api/... (access token expired)
    A-->>B: 401 token_expired
    B->>A: POST /api/auth/refresh (cookie)
    A->>D: look up sha256(cookie), check active, rotate token
    A-->>B: 200 {access_token} + Set-Cookie new session_token
    B->>A: retry original request

    B->>A: POST /api/auth/logout (cookie)
    A->>D: UPDATE sessions SET revoked_at = now()
    A-->>B: 204 + clear cookie
```
