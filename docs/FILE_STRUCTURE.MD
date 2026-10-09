# File Structure

This document describes how the Future Code repository is organized.

The project is a monorepo with three main areas:

- `frontend/` — React + TypeScript + Tailwind client (Vite)
- `backend/` — Flask REST API (SQLAlchemy, PostgreSQL, OpenAI, AWS)
- `docs/` and `design/` — documentation and architecture diagrams

Items marked **(planned)** do not exist yet. They show where new code should go as features from the [Roadmap](./ROADMAP.md) are built.

---

## Top Level

```
future-code/
├── backend/                 # Flask REST API
├── frontend/                # React client
├── docs/                    # Project documentation
├── design/                  # draw.io diagrams and exported images
├── .github/                 # (planned) GitHub Actions CI/CD workflows
├── docker-compose.yml       # (planned) Local dev: frontend, backend, PostgreSQL
├── .gitignore
├── LICENSE
└── README.md
```

---

## Backend

```
backend/
├── run.py                   # Entry point — starts the Flask dev server
├── app.py                   # Application factory (create_app), registers blueprints & extensions
├── config.py                # Config classes (Development / Testing / Production) loaded from env vars
├── extensions.py            # (planned) Shared instances: db (SQLAlchemy), migrate, cors, jwt
├── requirements.txt         # Python dependencies
├── .env.example             # Template for required environment variables (copy to .env)
├── Dockerfile               # (planned) Backend container image
│
├── routes/                  # API endpoints (Flask Blueprints), one file per resource
│   ├── auth.py              # Login, signup, token refresh, OAuth callbacks (Cognito)
│   ├── users.py             # (planned) User profile endpoints
│   ├── resumes.py           # (planned) Resume upload / retrieval / analysis
│   ├── interviews.py        # (planned) Interview plans & mock interview sessions
│   ├── coding.py            # (planned) Coding challenges, hints, solution feedback
│   └── progress.py          # (planned) Dashboard stats, streaks, strengths/weaknesses
│
├── models/                  # (planned) SQLAlchemy database models
│   ├── user.py
│   ├── resume.py
│   ├── interview.py         # Interview plans, sessions, questions, answers
│   ├── coding_challenge.py
│   └── progress.py
│
├── schemas/                 # (planned) Request validation & response serialization
│
├── services/                # (planned) Business logic — routes stay thin and call these
│   ├── auth_service.py      # Cognito token verification, user sync
│   ├── s3_service.py        # Resume upload/download with Amazon S3
│   ├── resume_service.py    # Resume parsing & profile generation
│   ├── interview_service.py
│   └── progress_service.py
│
├── ai/                      # (planned) LLM integration layer
│   ├── client.py            # OpenAI client setup
│   ├── prompts/             # Prompt templates (resume analysis, questions, feedback)
│   ├── resume_analyzer.py   # Extract skills, education, projects, technologies
│   ├── question_generator.py# Personalized interview / coding questions
│   └── feedback.py          # AI feedback on answers and mock interviews
│
├── utils/                   # (planned) Helpers: decorators (e.g. @login_required), errors, validators
├── migrations/              # (planned) Flask-Migrate / Alembic database migrations
└── tests/                   # (planned) pytest tests, mirroring the folders above
```

### Request flow

```
HTTP request → routes/ → services/ → models/ (PostgreSQL)
                              ├────→ ai/      (OpenAI)
                              └────→ AWS      (S3, Cognito)
```

- **routes** handle HTTP only: parse input, call a service, return JSON.
- **services** hold the business logic and are the only layer that talks to models, AI, and AWS.
- **models** define database tables and relationships.

---

## Frontend

```
frontend/
├── index.html               # Vite HTML entry
├── package.json
├── vite.config.ts
├── eslint.config.js
├── tsconfig.json            # Base TS config (references app + node configs)
├── tsconfig.app.json        # TS config for src/
├── tsconfig.node.json       # TS config for vite.config.ts
├── Dockerfile               # (planned) Build + serve with Nginx
│
├── public/                  # Static files served as-is
│   ├── favicon.png
│   └── icons.svg
│
└── src/
    ├── main.tsx             # React entry — mounts <App /> inside the router
    ├── App.tsx              # Route definitions
    ├── index.css            # Tailwind imports & global styles
    │
    ├── assets/              # Images imported by components
    │   └── InterviewPrepAi_Logo.png
    │
    ├── components/          # Reusable UI components
    │   ├── Header.tsx
    │   └── ui/              # (planned) Buttons, inputs, cards, modals
    │
    ├── pages/               # One component per route
    │   ├── LandingPage.tsx
    │   ├── LoginPage.tsx            # (planned)
    │   ├── SignupPage.tsx           # (planned)
    │   ├── DashboardPage.tsx        # (planned) Progress dashboard
    │   ├── ProfilePage.tsx          # (planned)
    │   ├── ResumePage.tsx           # (planned) Resume upload & analysis
    │   ├── InterviewPlanPage.tsx    # (planned)
    │   ├── MockInterviewPage.tsx    # (planned)
    │   └── CodingCoachPage.tsx      # (planned)
    │
    ├── layouts/             # (planned) Shared page layouts (e.g. app shell with sidebar)
    ├── routes/              # (planned) ProtectedRoute and route guards
    ├── api/                 # (planned) Fetch/axios client and per-resource API calls
    ├── context/             # (planned) React context (e.g. AuthContext)
    ├── hooks/               # (planned) Custom hooks (useAuth, useResume, ...)
    ├── types/               # (planned) Shared TypeScript types matching API responses
    └── utils/               # (planned) Formatting and helper functions
```

---

## Docs

```
docs/
├── ARCHITECTURE.MD          # System architecture and data flows
├── API.MD                   # REST API endpoint reference
├── AWS.MD                   # AWS services and setup (Cognito, S3, EC2, RDS, CloudFront)
├── DATABASE.MD              # Database schema and ER diagram
├── DEPLOYMENT.MD            # Docker, Nginx, CI/CD and production deployment
├── DEVELOPMENT.MD           # Local setup and development workflow
├── FILE_STRUCTURE.MD        # This file
├── ROADMAP.md               # Development phases and progress
└── SECURITY.MD              # Auth, secrets handling, and security practices
```

## Design

```
design/
├── UseCaseDiagram.drawio    # Use case diagram
└── Architecture/
    ├── Overview.drawio      # High-level architecture (editable source)
    ├── Overview.png         # Exported image used in ARCHITECTURE.MD
    └── Unfinished.drawio    # Work-in-progress diagram
```

---

## Conventions

- **Backend:** `snake_case` file names; one Blueprint per resource in `routes/`; business logic lives in `services/`, not in routes.
- **Frontend:** `PascalCase` for component and page files (`LandingPage.tsx`); `camelCase` for hooks and utilities (`useAuth.ts`).
- **Secrets:** never commit `.env`; add every new variable to `backend/.env.example`.
- **Tests:** mirror the source folder structure (e.g. `services/resume_service.py` → `tests/services/test_resume_service.py`).
