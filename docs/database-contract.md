# SQLite exchange contract

Этот контракт предназначен для локального асинхронного отборщика. Миграции Django создают его автоматически.

## Чтение очереди

```sql
SELECT n.news_id,
       n.primary_url,
       n.sources_json,
       n.title,
       n.body_text,
       n.language,
       n.published_at,
       n.first_seen_at
FROM exchange_news_for_selection AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM exchange_latest_reviews AS r
    WHERE r.news_id = n.news_id
      AND r.selector_name = :selector_name
)
ORDER BY n.first_seen_at
LIMIT :batch_size;
```

`sources_json` — JSON-массив объектов с `url`, `canonical_url`, `source_id`, `source_name`, `domain` и `fetched_at`.

## Запись решения

```sql
INSERT INTO exchange_review_events (
    news_id, decision, score, reason,
    selector_name, selector_version,
    idempotency_key, created_at
) VALUES (
    :news_id, :decision, :score, :reason,
    :selector_name, :selector_version,
    :idempotency_key, :created_at
);
```

- `decision`: `positive`, `not_positive` или `skipped`;
- `score`: `NULL` или `[0, 1]`;
- `idempotency_key`: стабильный уникальный идентификатор попытки;
- `created_at`: UTC ISO 8601, например `2026-07-13T12:30:00+00:00`.

Транзакция должна содержать небольшой batch и сразу завершаться `COMMIT`. При `database is locked` следует повторить транзакцию с экспоненциальной задержкой. Не удерживайте read-транзакцию во время работы модели.

## Исправление решения

События неизменяемы. Для исправления вставьте новое событие с другим `idempotency_key`. `exchange_latest_reviews` выберет его по `created_at`, затем по `id`.

