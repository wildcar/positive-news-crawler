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
- Production database holds 20 active sources: RIA "Хорошие новости" (repaired: 404 sitemap endpoint removed, `ria\.ru/\d{8}/` include pattern; collects only after the gzip fix is deployed) plus 19 sources added 2026-07-13 — RU RSS: positivnews.ru, moydom.moscow, life.ru, tumentoday.ru, yuga.ru, vladnews.ru, nsknews.info; EN RSS: goodnewsnetwork.org, positive.news, reasonstobecheerful.world, optimistdaily.com, goodgoodgood.co, sunnyskyz.com, notallnewsisbad.com, upi.com/Odd_News, upworthy.com, sciencedaily.com, thebetterindia.com; EN HTML listing: apnews.com/oddities (no public RSS, include pattern `/article/`, 5 s delay after HTTP 429).
- First crawl pass on 2026-07-13 collected ~1000 articles; scientificrussia.ru was added and then removed the same day because Python's robotparser reads its `Disallow: /?` as a full-site ban.
- Rejected source candidates (checked 2026-07-13): regions.ru (403 for this host), citysakh.ru and sdelanounas.ru (feed URLs return HTML), sib.fm/asi.org.ru/goodnewsfinland.com (no working feed), mos.ru (connection failure), scientificrussia.ru (robots.txt disallows `/rss/` and article listings).
- `fetch_url` decompresses gzip bodies by magic bytes; the previous case-sensitive `Content-Encoding` lookup silently broke sources whose servers send lowercase headers (found via ria.ru).

- The crawler saves only articles published on the current date (UTC `TIME_ZONE`): stale feed entries are skipped before download, undated or older articles are rejected; rows not published on 2026-07-13 were purged from the production database the same day.
- Agent-authored Russian text must follow the vendored `humanizer-ru` skill (`.claude/skills/humanizer-ru/SKILL.md`, mandated in `AGENTS.md`); crawled article content stays verbatim.
- The exchange contract carries the News Evaluator axis set v1 (20 characteristics, integer 0–10): `exchange_evaluation_characteristics` (seeded by migration 0004), append-only `exchange_evaluation_scores` tied to review events, and the `exchange_latest_evaluation_scores` view; documented in `docs/database-contract.md`. Applied on production 2026-07-14 via `update-ubuntu.sh` (f8739e7 → c67532c, backup `pre-update-20260714T221728Z.sqlite3`); 20 seeded characteristics, the view, triggers, services, and integrity verified live.
- The operator news list sorts by date or source name (both directions) and filters by source, selector decision, and evaluation scores: all 20 axes render at once as dual-threshold 0-10 sliders; every narrowed range requires a matching latest score, so unevaluated news drops out. Backed by a read-only unmanaged model over `exchange_latest_evaluation_scores` (state-only migration 0005); verified by pytest and a headless-Chromium pass. Not yet deployed to production.
- The news detail page renders the latest evaluation of each selector as a category-grouped heat scale: one cell per characteristic on an 11-step single-hue teal ramp (monotone lightness, per-step text contrast ≥ 4.5:1 — dark ink through step 6, white from 7), value digits always visible, axis anchors in tooltips, 0-10 legend, placeholder for unevaluated news. Shared UI test fixtures live in `tests/conftest.py`. Not yet deployed to production.

## Next

- Register every local SQLite client service in `/etc/newscrawler/update-services` and create the UI operator.
- Watch crawl runs and positive-yield statistics for the initial sources; tune per-site rules (selectors, intervals, Playwright) where extraction fails.

## Open questions

- None.

## Deferred

- Remote/multi-host operation, multiple workers, server database, paid/search APIs, email/webhook notifications, and the positivity classifier itself.
