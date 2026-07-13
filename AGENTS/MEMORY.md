# Memory

Durable facts and working agreements that are not merely a restatement of code or current state.

## Working agreements

- User-facing conversation and operator UI are Russian; code and new technical documentation are English to keep maintenance consistent.
- Prefer simple single-host operation over speculative scaling; additional infrastructure needs an observed requirement.
- The source list is feedback-driven: missing or skipped selector feedback must never penalize a source.

## Project facts

- Permanent repository path is `D:\repo\positive-news-crawler`.
- The positivity classifier is owned by another process and integrates only through the local `exchange_*` SQLite contract.
- Initial sources are added by an operator; automatic discovery follows external links only from positively reviewed news.

