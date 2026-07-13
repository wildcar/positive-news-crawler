# Positive News Aggregator

Небольшой мультиязычный агрегатор публичных новостей. Он собирает статьи в локальную SQLite-базу, объединяет перепечатки и предоставляет стабильный SQL-контракт внешнему процессу, который оценивает позитивность. Обратная связь автоматически влияет на список источников.

## Возможности

- RSS/Atom, sitemap, HTML-разделы и опциональный Playwright для JS-сайтов;
- соблюдение `robots.txt`, доменная задержка, backoff и запрет приватных сетевых адресов;
- извлечение текста и метаданных Trafilatura, CSS-переопределения через UI;
- точная и близкая дедупликация с сохранением всех URL;
- SQLite WAL, единственный worker, восстановление просроченной аренды;
- append-only обратная связь, retention 90 дней и семь дневных backup;
- probation автоматически найденных источников и отключение источников с низким yield;
- защищенный интерфейс одного оператора.

## Быстрый запуск

Требуется Python 3.13 или 3.14. База должна находиться на локальном диске, не в сетевой или синхронизируемой папке.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
./scripts/install.ps1
./.venv/Scripts/python.exe manage.py createoperator operator
$env:NEWSAGG_SECRET_KEY = "replace-with-a-long-random-secret"
./.venv/Scripts/python.exe -m waitress --listen=127.0.0.1:8000 newsagg.wsgi:application
```

В другом окне:

```powershell
./.venv/Scripts/python.exe manage.py runworker
```

Ubuntu:

```bash
cp .env.example .env
sh scripts/install.sh
.venv/bin/python manage.py createoperator operator
set -a; . ./.env; set +a
.venv/bin/python -m waitress --listen=127.0.0.1:8000 newsagg.wsgi:application
```

В другом терминале:

```bash
set -a; . ./.env; set +a
.venv/bin/python manage.py runworker
```

UI будет доступен на `http://127.0.0.1:8000/`. Для production разместите reverse proxy с HTTPS перед Waitress и задайте `NEWSAGG_SECURE=1`.

> Django не читает `.env` автоматически. При ручном запуске экспортируйте значения в окружение; systemd использует файл напрямую. В Windows постоянные значения можно задать через системные переменные среды.

## Работа worker

Worker проверяет очередь раз в минуту. Одновременно разрешен ровно один экземпляр — второй не получит файловую блокировку. Для одного диагностического прохода:

```bash
python manage.py runworker --once
```

Раз в сутки тот же процесс:

1. пересчитывает yield источников;
2. проверяет внешние домены из позитивно оцененных статей;
3. удаляет содержимое старше 90 дней;
4. создает и проверяет backup SQLite.

Для ручного запуска обслуживания используйте `python manage.py maintenance`.

## Добавление источника

Откройте «Источники → Добавить источник». Минимально нужны название и публичный HTTPS URL. RSS, sitemap и страница новостей необязательны: worker попробует обнаружить их сам. При проблемах извлечения задайте:

- include/exclude URL regex;
- CSS-селекторы заголовка и текста;
- Playwright для конкретного сайта;
- интервал и задержку запросов.

Ссылки на login, subscribe, paywall и CAPTCHA пропускаются. Если `robots.txt` явно запрещает URL или не удается безопасно проверить его из-за сетевой ошибки, страница не загружается. Отсутствующий `robots.txt` (`404`) разрешает обход.

## Контракт отборщика

Отборщик открывает тот же локальный файл, устанавливая обязательные pragma:

```python
connection = sqlite3.connect("data/newsagg.sqlite3", timeout=30)
connection.execute("PRAGMA journal_mode=WAL")
connection.execute("PRAGMA foreign_keys=ON")
connection.execute("PRAGMA busy_timeout=30000")
```

Доступны:

- `exchange_news_for_selection` — непустые новости, основной URL и JSON-массив всех публикаций;
- `exchange_review_events` — таблица для вставки решений;
- `exchange_latest_reviews` — последнее событие по новости и имени отборщика.

Допустимые решения: `positive`, `not_positive`, `skipped`. `score` либо `NULL`, либо число от 0 до 1. Пара `(selector_name, idempotency_key)` уникальна. `UPDATE` и `DELETE` событий запрещены триггерами; исправление — новое событие.

Полный рабочий пример находится в [examples/selector_client.py](examples/selector_client.py).

Отборщик и web/worker должны работать под учетными записями ОС, которым разрешен доступ к каталогу `data`. SQLite не предоставляет табличных ролей: пользователь с правом записи на файл технически может изменить любую таблицу.

## Автоматические статусы

- Автоматически найденный домен начинается в `probation` и может сохранить до 20 публикаций.
- После лимита он переходит в `probation_waiting` до появления оценок.
- При 10 оценках, не менее 80% успешных извлечений и positive yield не ниже 2% источник становится `active`.
- Активный источник при 50 окончательных оценках за 30 дней и yield ниже 2% получает `paused_low_yield`.
- `skipped` и отсутствие оценки не учитываются.
- Оператор может вручную вернуть источник в probation.

## Нативные службы

Шаблоны systemd находятся в `deploy/systemd`. Они предполагают установку в `/opt/newsagg` и пользователя `newsagg`:

```bash
sudo cp deploy/systemd/newsagg-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now newsagg-web newsagg-worker
```

На Windows после установки запустите PowerShell от имени администратора:

```powershell
./scripts/register-windows-tasks.ps1
```

## Проверка

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pytest
```

Live smoke-тесты реальных сайтов намеренно не входят в обычный набор: их результат зависит от сети и изменений издателя.

## Ограничения

- один компьютер и один crawler-worker;
- до 200 источников;
- только публичные HTTP(S) сайты;
- файл SQLite нельзя размещать на NFS/SMB/OneDrive и нельзя открывать с другого компьютера;
- процесс классификации позитивности не входит в проект.

