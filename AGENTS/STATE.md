# State

## Goal

Operate a single-host multilingual news crawler whose source list improves from asynchronous positive-news feedback.

## Now

- MVP code and repository harness are present in the development checkout and deployed to `/opt/newscrawler` on the Ubuntu production host.
- Git is initialized on `main`; the GitHub remote is `https://github.com/wildcar/positive-news-crawler`.
- Naming is unified: Positive News Crawler is the product, while `newscrawler` is the Django package, deployment directory, service account, and runtime prefix.
- SQLite migrations, WAL pragmas, exchange views/triggers, daily backup, retention, source policy, UI, deployment files, and tests are implemented.
- Ubuntu production deployment is documented with root-owned code/config, group-shared local SQLite state, hardened systemd units, and a guarded update script with backup and rollback.
- Ubuntu 24.04 LTS and its stock Python 3.12 are supported; CI covers Python 3.12, 3.13, and 3.14 on Ubuntu and Windows.
- Ubuntu deployment explicitly sets the shared SQLite database to `0660`; both crawler systemd units normalize that mode before startup.
- `https://newscrawler.wildcar.org` is live behind Nginx with a Let's Encrypt certificate and automatic HTTP-to-HTTPS redirect; Waitress remains restricted to `127.0.0.1:8000`.
- Verified on Ubuntu/Python 3.12: Django checks clean, migrations current, 18 tests pass, HTTPS login and static endpoints respond, and SQLite integrity is `ok`.

## Next

- Register every local SQLite client service in `/etc/newscrawler/update-services`, create the UI operator, and add initial sources.
- Perform opt-in live smoke tests against selected sources and tune per-site rules.

## Open questions

- Which initial source list and contact address should be used in `NEWSCRAWLER_USER_AGENT`?

## Deferred

- Remote/multi-host operation, multiple workers, server database, paid/search APIs, email/webhook notifications, and the positivity classifier itself.
