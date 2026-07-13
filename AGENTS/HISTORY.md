# History

Newest first. Each entry is at most five lines using the format defined in `AGENTS.md`.

## 2026-07-13 · Nginx HTTPS reverse-proxy support
- What: Added the Nginx site, trusted proxy scheme handling, deployment procedure, and a regression assertion for `newscrawler.wildcar.org`.
- Why: Publish the operator UI through HTTPS while keeping Waitress bound only to loopback.
- Files: `deploy/nginx/`, `newscrawler/settings.py`, `docs/ubuntu-deployment.md`, `tests/test_ui.py`, `AGENTS/*`
- Next: Activate the site and certificate on the production host and verify external HTTPS access.

## 2026-07-13 · Shared SQLite mode normalization
- What: Added explicit `0660` initialization and systemd pre-start normalization for the production SQLite database.
- Why: SQLite creates a new database with default `0644` permissions, which became `0640` and blocked other group members from writing.
- Files: `deploy/systemd/`, `docs/ubuntu-deployment.md`, `docs/database-contract.md`, `AGENTS/*`
- Next: Apply `chmod 0660` on the target database and continue deployment verification.

## 2026-07-13 · Ubuntu 24.04 and Python 3.12 support
- What: Extended the supported Python range to 3.12, added it to the CI matrix, and retargeted the Ubuntu guide to the stock 24.04 runtime.
- Why: Deploy cleanly on the destination Ubuntu 24.04 LTS host without third-party Python packages.
- Files: `pyproject.toml`, `.github/workflows/ci.yml`, `docs/ubuntu-deployment.md`, `README.md`, `AGENTS/*`
- Next: Run the documented deployment on the destination host and verify the live systemd services.

## 2026-07-13 · Ubuntu production deployment and updater
- What: Added the production filesystem/user model, shared SQLite group permissions, hardened systemd units, full deployment guide, and guarded update script with backup/rollback.
- Why: Support sudo-driven installation and safe same-host database access by multiple local service accounts.
- Files: `docs/ubuntu-deployment.md`, `scripts/update-ubuntu.sh`, `deploy/`, `README.md`, `AGENTS/*`
- Next: Deploy on the target host, register selector units, configure HTTPS, and run live source smoke tests.

## 2026-07-13 · Unified crawler naming
- What: Renamed the Django package and every runtime, deployment, database, log, environment, UI, and package identifier to the crawler naming contract.
- Why: Remove conflicting product terminology and standardize the internal folder and service account as `newscrawler`.
- Files: `newscrawler/`, `deploy/systemd/`, `collector/services/`, `.env.example`, `README.md`, `AGENTS/*`
- Next: Configure the runtime environment and seed initial production sources.

## 2026-07-13 · GitHub repository initialized
- What: Initialized Git on `main`, configured the GitHub remote, and published the project repository.
- Why: Establish version control and the shared upstream repository.
- Files: repository metadata, `AGENTS/STATE.md`, `AGENTS/HISTORY.md`
- Next: Configure the runtime environment and seed initial production sources.

## 2026-07-13 · SQLite crawler MVP and repository relocation
- What: Implemented the crawler, UI, SQLite exchange contract, policy automation, deployment assets, tests, and populated the repository harness.
- Why: Deliver the approved single-host positive-news collection plan in its permanent repository location.
- Files: `collector/`, Django project package, `tests/`, `README.md`, `AGENTS/*`, `docs/`
- Next: Configure environment/operator, seed real sources, and run live smoke tests.

---
