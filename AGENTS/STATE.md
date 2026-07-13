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
- Production database holds 20 active sources: RIA "Хорошие новости" (repaired: 404 sitemap endpoint removed, `ria\.ru/\d{8}/` include pattern) plus 19 RSS sources added 2026-07-13 — RU: positivnews.ru, moydom.moscow, life.ru, tumentoday.ru, yuga.ru, vladnews.ru, nsknews.info, scientificrussia.ru; EN: goodnewsnetwork.org, positive.news, reasonstobecheerful.world, optimistdaily.com, goodgoodgood.co, sunnyskyz.com, notallnewsisbad.com, upi.com/Odd_News, upworthy.com, sciencedaily.com, thebetterindia.com.
- Rejected source candidates (checked 2026-07-13): regions.ru (403 for this host), citysakh.ru and sdelanounas.ru (feed URLs return HTML), sib.fm/asi.org.ru/goodnewsfinland.com (no working feed), mos.ru (connection failure), apnews.com (no public RSS).

## Next

- Register every local SQLite client service in `/etc/newscrawler/update-services` and create the UI operator.
- Watch crawl runs and positive-yield statistics for the initial sources; tune per-site rules (selectors, intervals, Playwright) where extraction fails.

## Open questions

- None.

## Deferred

- Remote/multi-host operation, multiple workers, server database, paid/search APIs, email/webhook notifications, and the positivity classifier itself.
