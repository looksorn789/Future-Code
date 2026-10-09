# Database

The backend uses SQLAlchemy (Flask-SQLAlchemy) with Flask-Migrate (Alembic) for schema changes.

- **Development:** SQLite. The file location comes from `DATABASE_PATH` (see `backend/config.py`).
- **Production (planned):** PostgreSQL on Amazon RDS. Only `SQLALCHEMY_DATABASE_URI` changes.

Do not call `db.create_all()`. Every schema change goes through a migration:

```powershell
cd backend
python -m flask --app app:create_app db migrate -m "add users and sessions"
python -m flask --app app:create_app db upgrade
```

Items marked **(planned)** are not implemented yet.

---

## Authentication tables (planned)

```
users 1 ──── * sessions
```

### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | integer, PK | |
| `email` | string(255), unique, not null | Stored lowercase and trimmed |
| `password_hash` | string(255), nullable | `NULL` for OAuth-only accounts |
| `name` | string(100) | |
| `role` | string(20), not null, default `'user'` | `'user'` or `'admin'` |
| `is_active` | boolean, not null, default `true` | Disabled accounts cannot log in or refresh |
| `email_verified_at` | datetime, nullable | |
| `created_at` / `updated_at` | datetime (UTC), not null | |

### `sessions`

One row per logged-in device or browser.

| Column | Type | Notes |
|---|---|---|
| `id` | string(36), PK | UUID4. Goes into the JWT `sid` claim |
| `user_id` | integer, FK → `users.id`, `ON DELETE CASCADE`, indexed | |
| `token_hash` | string(64), unique, not null | `sha256(session_token)` hex. **The raw token is never stored** |
| `created_at` | datetime (UTC), not null | |
| `last_used_at` | datetime (UTC), not null | Updated on refresh |
| `expires_at` | datetime (UTC), not null | Pushed forward on each refresh (sliding expiry) |
| `revoked_at` | datetime (UTC), nullable | Set on logout / logout-all / password change |
| `user_agent` | string(255), nullable | Shown in a future "active devices" list |
| `ip_address` | string(45), nullable | IPv6-safe length |

```python
# backend/models/session.py (sketch)
import uuid
from datetime import datetime, timezone

from extensions import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_used_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    revoked_at = db.Column(db.DateTime(timezone=True))
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))

    user = db.relationship("User", back_populates="sessions")

    @property
    def is_active(self):
        return self.revoked_at is None and self.expires_at > datetime.now(timezone.utc)
```

> SQLite does not store time zones, so datetimes read back from it are naive. Until the move to PostgreSQL, either store naive UTC everywhere or use a `TypeDecorator` that adds `timezone.utc` when reading. Do not mix naive and aware datetimes in comparisons: Python raises a `TypeError`.

Housekeeping (planned): a periodic job deletes rows where `expires_at < now() - 30 days` or `revoked_at < now() - 30 days`.

---

## Application tables (planned)

Resumes, interview plans, mock interviews (name that table `interview_sessions` so it does not clash with the auth `sessions` table), questions and answers, coding challenges and progress will be documented here, along with an ER diagram, once they are designed. See the [Roadmap](./ROADMAP.md), Phase 1.
