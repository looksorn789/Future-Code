# Backend Setup

This guide starts the Flask backend locally on Windows using PowerShell.

## Requirements

- Python 3.12 (the existing `backend\venv` was created with Python 3.12)
- PowerShell

Run the commands below from the repository root, unless a step says otherwise.

## 1. Create or activate the virtual environment

If `backend\venv` does not exist yet, create it:

```powershell
py -3.12 -m venv backend\venv
```

Activate it:

```powershell
.\backend\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can skip activation and use the venv's Python executable directly in the commands below.

## 2. Install backend dependencies

With the virtual environment activated:

```powershell
python -m pip install -r backend\requirements.txt
```

Without activation:

```powershell
.\backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## 3. Configure environment variables

Create `backend\.env` with a `JWT_SECRET`. Generate a secret locally; do not use the placeholder value from `.env.example`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

If you did not activate the virtual environment, run the same command with:

```powershell
.\backend\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

Put the generated value in `backend\.env`:

```env
JWT_SECRET=replace-with-your-generated-secret
```

The following settings are optional. The backend uses these defaults if they are omitted:

```env
FRONTEND_ORIGIN=http://localhost:3000
ENV=development
DATABASE_PATH=futurecode.db
```

`DATABASE_PATH` is a SQLite file path. A relative path is resolved from the current working directory when the app is started; to keep the database in `backend`, start Flask from that directory as shown below, or set an absolute path.

Keep `backend\.env` private. It is ignored by Git; do not commit real secrets.

## 4. Run the backend

Change to the backend directory:

```powershell
Set-Location backend
```

With the virtual environment activated:

```powershell
python -m flask --app app:create_app run --debug
```

Without activating the environment:

```powershell
.\venv\Scripts\python.exe -m flask --app app:create_app run --debug
```

Flask should report that it is serving at `http://127.0.0.1:5000`. Press `Ctrl+C` to stop it.

The app currently has no API endpoint implementations, so visiting `/` may return 404 even when the server started successfully.

## Troubleshooting

- **`JWT_SECRET` is missing:** Confirm `backend\.env` exists and contains a non-empty `JWT_SECRET=...` line.
- **`SQLALCHEMY_DATABASE_URI` is missing:** Confirm you are running the current app code, which derives the SQLite URI from `DATABASE_PATH`.
- **A package cannot be imported:** Activate `backend\venv` and rerun `python -m pip install -r requirements.txt` from `backend`, or run the install command from the repository root shown above.
- **The command path is not found:** From the repository root use `.\backend\venv\Scripts\...`; from `backend` use `.\venv\Scripts\...`.
