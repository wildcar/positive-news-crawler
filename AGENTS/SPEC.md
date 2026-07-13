# Positive News Crawler — functional & technical specification

## Purpose

Collect multilingual articles from public mainstream and niche news sites into a local database. A separate asynchronous selector evaluates whether a logical news item is positive. Its append-only feedback drives source discovery and automatically pauses consistently low-yield sources. A single operator manages the system through a small authenticated website.

## Stack

- Python 3.13 or 3.14; Django 5.2 LTS and server-rendered templates.
- SQLite in WAL mode on a local disk; one web process, one crawler worker, one local selector.
- Feedparser for RSS/Atom, XML sitemap parsing, Trafilatura for main-text extraction, Playwright Chromium only for configured JS sites.
- Waitress for the web process; systemd on Ubuntu and Task Scheduler on Windows.

## Architecture

```text
Public sites -> crawler worker -> normalization/deduplication -> SQLite WAL
                                          |                      ^
Operator -> authenticated Django UI ------+                      |
External selector <- exchange views -> append-only review events-+
```

## Functional requirements

### Collection

- ✅ Poll due sources every minute; default source interval is 60 minutes.
- ✅ Source acquisition cascade: RSS/Atom, sitemap (including gzip/index), HTML listing, opt-in Playwright.
- ✅ Preserve feed ETag and Last-Modified values.
- ✅ Obey robots, identify the user agent, apply delays/timeouts/backoff, reject private/reserved addresses and protected paths.
- ✅ Extract title, text, author, date, language, canonical URL, metadata, and outbound links.
- ✅ Allow per-source URL regexes, CSS selectors, delay, interval, and Playwright setting.

### Storage and duplicate handling

- ✅ Configure WAL, foreign keys, 30-second busy timeout, and normal synchronization on Django connections.
- ✅ Allow one worker via OS file lock; lease due sources and recover expired leases.
- ✅ Group exact normalized-body SHA-256 duplicates.
- ✅ Group near duplicates of the same language within 48 hours using SimHash and title similarity; translations remain separate.
- ✅ Retain every occurrence/source URL while exposing one logical item to the selector.
- ✅ Purge full content and detailed metadata after 90 days while retaining the technical tombstone.
- ✅ Create integrity-checked SQLite backups and retain seven files.

### Feedback contract

- ✅ `exchange_news_for_selection` exposes active logical news and all occurrences as JSON.
- ✅ `exchange_review_events` accepts positive/not_positive/skipped events with selector/version/idempotency metadata.
- ✅ `exchange_latest_reviews` returns the latest event for a news/selector pair.
- ✅ Unique idempotency constraint and triggers enforce append-only events.

### Source policy

- ✅ Discover candidate domains only from external links of positively reviewed items.
- ✅ Automatically accepted sources enter probation, limited to 20 saved articles.
- ✅ Promote after at least ten final reviews, at least 80% extraction success, and positive yield of at least 2%.
- ✅ Pause an active source below 2% yield after at least 50 final reviews in a rolling 30-day window.
- ✅ Ignore skipped/missing reviews and allow the operator to restart probation.

### Operator and operation

- ✅ Single local operator account; authenticated dashboard, source editor, news/duplicate view, crawl runs, events, source statistics, backup status.
- ✅ CLI commands for operator creation, worker, and maintenance.
- ✅ Windows/Ubuntu install and service files, structured rotating logs, CI matrix.
- ⏳ Real-source smoke validation and production reverse-proxy deployment are environment-specific follow-up work.

## Project structure

```text
collector/       Django domain, migrations, services, commands, views
newsagg/         Django project configuration
templates/       Russian operator interface
tests/           parser, policy, database contract, UI and worker tests
docs/            selector contract and ADRs
examples/        direct-SQLite selector example
scripts/         Windows/Ubuntu installation and Windows task setup
deploy/systemd/  Ubuntu service units
```

## Deployment

- Copy `.env.example` to a host-managed environment configuration and set secrets outside Git.
- Run migrations, create the operator, install Chromium, then start Waitress and exactly one worker.
- Keep the database, backup directory, logs, worker, UI, and selector on the same machine.
- Detailed procedures are in `README.md` and `AGENTS/ENV.md`.

## Current state

- ✅ MVP implemented, migrated, and verified on Windows/Python 3.14.5.
- ✅ Sixteen deterministic tests pass; SQLite integrity and exchange objects are verified.
- ⏳ Configure real operator credentials and add initial production sources on the destination host.

See `AGENTS/STATE.md` for the live snapshot.

## Data sources & dependencies

- Public HTTP(S) RSS/Atom feeds, sitemaps, and article/listing HTML.
- No search API, paid publisher account, CAPTCHA bypass, remote DB, Redis, or Celery.
- External selector is a separate process that shares the same local SQLite file.

