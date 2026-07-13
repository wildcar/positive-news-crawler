# State

## Goal

Operate a single-host multilingual news crawler whose source list improves from asynchronous positive-news feedback.

## Now

- MVP code and repository harness are present in `D:\repo\positive-news-crawler`.
- Git is initialized on `main`; the GitHub remote is `https://github.com/wildcar/positive-news-crawler`.
- SQLite migrations, WAL pragmas, exchange views/triggers, daily backup, retention, source policy, UI, deployment files, and tests are implemented.
- Verified on Windows with Python 3.14.5: Django checks clean, migrations current, 16 tests pass, SQLite integrity is `ok`.

## Next

- Copy `.env.example` values into host environment and set a strong `NEWSAGG_SECRET_KEY`.
- Create the operator, add initial sources, and run web plus the single worker.
- Perform opt-in live smoke tests against selected sources and tune per-site rules.

## Open questions

- Which initial source list and contact address should be used in `NEWSAGG_USER_AGENT`?
- Which reverse proxy/HTTPS setup will be used if the UI is exposed beyond localhost?

## Deferred

- Remote/multi-host operation, multiple workers, server database, paid/search APIs, email/webhook notifications, and the positivity classifier itself.
