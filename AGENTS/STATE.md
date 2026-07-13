# State

## Goal

Operate a single-host multilingual news crawler whose source list improves from asynchronous positive-news feedback.

## Now

- MVP code and repository harness are present in `D:\repo\positive-news-crawler`.
- Git is initialized on `main`; the GitHub remote is `https://github.com/wildcar/positive-news-crawler`.
- Naming is unified: Positive News Crawler is the product, while `newscrawler` is the Django package, deployment directory, service account, and runtime prefix.
- SQLite migrations, WAL pragmas, exchange views/triggers, daily backup, retention, source policy, UI, deployment files, and tests are implemented.
- Ubuntu production deployment is documented with root-owned code/config, group-shared local SQLite state, hardened systemd units, and a guarded update script with backup and rollback.
- Ubuntu 24.04 LTS and its stock Python 3.12 are supported; CI covers Python 3.12, 3.13, and 3.14 on Ubuntu and Windows.
- Verified on Windows with Python 3.14.5: Django checks clean, migrations current, 16 tests pass, SQLite integrity is `ok`.

## Next

- Deploy on the destination Ubuntu host using `docs/ubuntu-deployment.md` and configure a strong `NEWSCRAWLER_SECRET_KEY`.
- Register every local SQLite client service in `/etc/newscrawler/update-services`, create the UI operator, and add initial sources.
- Perform opt-in live smoke tests against selected sources and tune per-site rules.

## Open questions

- Which initial source list and contact address should be used in `NEWSCRAWLER_USER_AGENT`?
- Which reverse proxy/HTTPS setup will be used if the UI is exposed beyond localhost?

## Deferred

- Remote/multi-host operation, multiple workers, server database, paid/search APIs, email/webhook notifications, and the positivity classifier itself.
