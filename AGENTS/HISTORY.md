# History

Newest first. Each entry is at most five lines using the format defined in `AGENTS.md`.

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
