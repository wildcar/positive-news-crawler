# History

Newest first. Each entry is at most five lines using the format defined in `AGENTS.md`.

## 2026-07-13 · Current-date-only collection
- What: `crawl_source` saves only articles published on the current date (`published_today` gate: stale feed entries skipped before download, undated or older articles rejected at ingest); stale pre-existing rows purged from the production database.
- Why: Operator decision — the pipeline should hold only same-day news; 619 of 969 initially collected articles were older backfill.
- Files: `collector/services/crawler.py`, `tests/test_worker.py`, `AGENTS/SPEC.md`, `AGENTS/*`
- Next: Verify the next crawl cycle saves only current-date articles and watch per-source yields under the date filter.

## 2026-07-13 · Case-insensitive gzip response handling
- What: `fetch_url` now detects gzip bodies by magic bytes (`decompress_gzip_body`) instead of a case-sensitive `Content-Encoding` dict lookup; added a unit test.
- Why: ria.ru sends lowercase `content-encoding: gzip`, so bodies stayed compressed and HTML listings silently produced zero candidate links (run "success" with 0 articles).
- Files: `collector/services/fetch.py`, `tests/test_fetch.py`, `AGENTS/*`
- Next: Deploy to `/opt/newscrawler`, re-run the RIA source, and confirm articles are saved.

## 2026-07-13 · Initial production source list
- What: Added 20 verified sources (8 RU + 12 EN positive-news sites: 19 RSS feeds plus the AP Oddities HTML listing, each checked for HTTP 200, feed validity, freshness, robots.txt) to the production database and repaired the RIA source (removed 404 sitemap endpoint, added `ria\.ru/\d{8}/` include pattern).
- Why: The deployed crawler had an empty working source list; candidates came from `~/repo/hermes/positive-news/registry.md` usage counts and a web search for dedicated positive-news outlets.
- Files: production SQLite only (no code changes); rejected candidates recorded in `AGENTS/STATE.md`.
- Next: Watch first crawl runs and positive-yield statistics; tune per-site rules and probation/pauses as feedback arrives.

## 2026-07-13 · Nginx HTTPS reverse-proxy support
- What: Added the Nginx site, loopback-only forwarded-scheme trust in Waitress/Django, deployment procedure, and regression assertions for `newscrawler.wildcar.org`.
- Why: Publish the operator UI through HTTPS while keeping Waitress bound only to loopback.
- Files: `deploy/nginx/`, `newscrawler/settings.py`, `docs/ubuntu-deployment.md`, `tests/test_ui.py`, `AGENTS/*`
- Next: Create the UI operator, add initial sources, and run selected live-source smoke tests.

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
