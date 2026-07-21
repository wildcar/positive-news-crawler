# Environment

Host facts, tools, credentials pointers, and command cheat-sheet for this project.

## Host

- **Dev**: Windows, PowerShell, repository `D:\repo\positive-news-crawler`.
- **Supported runtime**: Windows or Ubuntu on one machine with a local filesystem.
- **Production layout**: code `/opt/newscrawler`, configuration `/etc/newscrawler`, shared local state `/var/lib/newscrawler`, logs `/var/log/newscrawler`, service user/group `newscrawler`.

## Tools

- Python `>=3.12,<3.15`; implementation was verified locally with Python 3.14.5 and Python 3.12 is covered by CI.
- Django 5.2 LTS, SQLite from the selected Python runtime.
- Playwright Chromium installed by `python -m playwright install chromium`.
- Git is optional until the target directory is initialized and a remote is configured.
- The production `model-router-mcp` endpoint is local at `http://127.0.0.1:8088/mcp`; news translation uses its `chat` tool.

## Credentials & secrets

- Runtime values come from `NEWSCRAWLER_*` environment variables; template: `.env.example`.
- Never store the Django secret key, operator password, or site credentials in the repository.
- The router token is `AUTH_TOKEN` in `/opt/model-router-mcp/.env`; copy its value to `NEWSCRAWLER_ROUTER_AUTH_TOKEN` in the protected crawler environment file, never to Git.
- `.env`, `data/*.sqlite3`, backups, logs, and lock files are gitignored.

## Environments

| Env | Host | Identifier | Role / account | Where used |
|-----|------|------------|----------------|------------|
| dev | Windows / localhost | local SQLite | current OS user | UI, worker, tests |
| prod | Windows or Ubuntu | one host/local disk | dedicated service account | UI, worker, selector |

## Commands cheat-sheet

### Dev — PowerShell

```powershell
./scripts/install.ps1
./.venv/Scripts/python.exe manage.py migrate
./.venv/Scripts/python.exe manage.py createoperator operator
./.venv/Scripts/python.exe -m waitress --listen=127.0.0.1:8000 newscrawler.wsgi:application
./.venv/Scripts/python.exe manage.py runworker
./.venv/Scripts/python.exe -m pytest
```

When using the already installed system Python during development, replace `./.venv/Scripts/python.exe` with `python`.

### Prod — Ubuntu

```bash
sudo /opt/newscrawler/scripts/update-ubuntu.sh
sudo systemctl status --no-pager newscrawler-web.service newscrawler-worker.service
sudo sqlite3 /var/lib/newscrawler/newscrawler.sqlite3 'PRAGMA integrity_check;'
```

Initial deployment, shared-group permissions, and update-service registration are documented in `docs/ubuntu-deployment.md`.

### Diagnostics

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py runworker --once
python manage.py maintenance
python -m pytest
```

## Host-specific quirks

### Dev

- The SQLite database must remain on a local non-synchronized disk.
- Package installs may default to the user site when the system Python directory is read-only.
- Windows scheduled tasks require an elevated PowerShell; use `scripts/register-windows-tasks.ps1`.

### Prod

- Set `NEWSCRAWLER_SECURE=1` only after HTTPS termination is configured.
- Playwright on Ubuntu needs browser system packages; `scripts/install.sh` uses `--with-deps`.
- All direct SQLite clients must run on the same host, belong to the `newscrawler` group, and be registered in `/etc/newscrawler/update-services` when managed by systemd.
