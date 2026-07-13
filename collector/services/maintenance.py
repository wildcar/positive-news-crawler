import logging
import sqlite3
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from collector.models import DiscoveryDomain, NewsItem, OperatorEvent, ReviewEvent, Source, SourceEndpoint
from .fetch import allowed_by_robots, discover_endpoints, fetch_url

logger = logging.getLogger(__name__)


def latest_reviews():
    latest_ids = []
    seen = set()
    for event in ReviewEvent.objects.order_by("news_item_id", "selector_name", "-created_at", "-id"):
        key = (event.news_item_id, event.selector_name)
        if key not in seen:
            seen.add(key)
            latest_ids.append(event.id)
    return ReviewEvent.objects.filter(id__in=latest_ids)


def evaluate_sources():
    now = timezone.now()
    since = now - timedelta(days=30)
    latest = list(latest_reviews().filter(created_at__gte=since, decision__in=[ReviewEvent.Decision.POSITIVE, ReviewEvent.Decision.NOT_POSITIVE]))
    decisions = {event.news_item_id: event.decision for event in latest}
    for source in Source.objects.filter(status__in=[Source.Status.ACTIVE, Source.Status.PROBATION, Source.Status.PROBATION_WAITING]):
        item_ids = set(source.occurrences.filter(news_item_id__in=decisions).values_list("news_item_id", flat=True))
        total = len(item_ids)
        positives = sum(decisions[item_id] == ReviewEvent.Decision.POSITIVE for item_id in item_ids)
        ratio = positives / total if total else 0
        if source.status in {Source.Status.PROBATION, Source.Status.PROBATION_WAITING} and total >= 10:
            totals = source.crawl_runs.filter(started_at__gte=source.probation_started_at or source.created_at).aggregate(fetched=Sum("fetched_count"), saved=Sum("saved_count"))
            fetched = totals["fetched"] or 0
            saved = totals["saved"] or 0
            extraction_ok = fetched > 0 and saved / fetched >= 0.8
            if extraction_ok and ratio >= 0.02:
                _change_status(source, Source.Status.ACTIVE, "Источник успешно прошел пробный режим", {"reviews": total, "positive_ratio": ratio})
            elif total >= 50 and ratio < 0.02:
                _change_status(source, Source.Status.PAUSED_LOW_YIELD, "Источник не прошел пробный режим", {"reviews": total, "positive_ratio": ratio})
        elif source.status == Source.Status.ACTIVE and total >= 50 and ratio < 0.02:
            _change_status(source, Source.Status.PAUSED_LOW_YIELD, "Автопауза: доля позитивных новостей ниже 2%", {"reviews": total, "positive_ratio": ratio})


def _change_status(source, status, message, details):
    source.status = status
    source.save(update_fields=["status", "updated_at"])
    OperatorEvent.objects.create(event_type="source_status", source=source, message=message, details=details)


def process_positive_discovery(limit=20):
    events = latest_reviews().filter(decision=ReviewEvent.Decision.POSITIVE).exclude(discovered_domains__isnull=False)[:limit]
    for event in events:
        links = event.news_item.occurrences.values_list("outbound_links__url", "outbound_links__domain").filter(outbound_links__is_external=True)
        for url, domain in links:
            if not domain or Source.objects.filter(domain=domain).exists():
                continue
            probe, created = DiscoveryDomain.objects.get_or_create(review_event=event, domain=domain, defaults={"url": url})
            if created:
                _probe_domain(probe)


def _probe_domain(probe):
    parts = urlsplit(probe.url)
    base_url = f"{parts.scheme}://{parts.netloc}/"
    source = None
    try:
        if not allowed_by_robots(base_url):
            raise PermissionError("robots.txt forbids crawling")
        result = fetch_url(base_url)
        source = Source.objects.create(name=probe.domain, base_url=base_url, domain=probe.domain, status=Source.Status.PROBATION, is_auto_discovered=True, probation_started_at=timezone.now())
        found = discover_endpoints(source, result.body, result.url)
        if not found:
            SourceEndpoint.objects.create(source=source, kind=SourceEndpoint.Kind.HTML, url=base_url)
        from .fetch import candidate_urls
        has_candidates = False
        for endpoint in source.endpoints.filter(enabled=True).order_by("priority"):
            try:
                probe_result = fetch_url(endpoint.url)
                if candidate_urls(endpoint, probe_result):
                    has_candidates = True
                    break
            except Exception:
                continue
        if not has_candidates:
            raise ValueError("No publication URLs found")
        probe.status = "accepted"
        probe.source = source
        OperatorEvent.objects.create(event_type="source_discovered", source=source, message="Источник автоматически добавлен из позитивной новости", details={"review_event_id": probe.review_event_id})
    except Exception as exc:
        if source is not None:
            source.delete()
        probe.status = "rejected"
        probe.error = str(exc)[:1000]
    probe.save()


def purge_old_content(days=90):
    cutoff = timezone.now() - timedelta(days=days)
    items = NewsItem.objects.filter(first_seen_at__lt=cutoff, purged_at__isnull=True)
    count = items.update(title="[purged]", body_text="", author="", metadata={}, purged_at=timezone.now())
    if count:
        OperatorEvent.objects.create(event_type="retention", message=f"Удалено содержимое {count} старых новостей", details={"days": days})
    return count


def create_backup(keep=7):
    backup_dir = settings.NEWSAGG_BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    filename = backup_dir / f"newsagg-{timezone.now():%Y%m%d-%H%M%S}.sqlite3"
    source = None
    destination = None
    backup_error = None
    try:
        source = sqlite3.connect(str(settings.DB_PATH), timeout=30)
        destination = sqlite3.connect(str(filename))
        source.backup(destination)
        result = destination.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"Backup integrity check failed: {result}")
    except Exception as exc:
        backup_error = exc
    finally:
        if destination is not None:
            destination.close()
        if source is not None:
            source.close()
    if backup_error is not None:
        OperatorEvent.objects.create(event_type="backup_failed", message=f"Ошибка резервного копирования: {backup_error}", details={"path": str(filename)})
        if filename.exists():
            filename.unlink()
        raise backup_error
    backups = sorted(backup_dir.glob("newsagg-*.sqlite3"), reverse=True)
    for old in backups[keep:]:
        old.unlink()
    OperatorEvent.objects.create(event_type="backup_success", message=f"Создана резервная копия {filename.name}", details={"path": str(filename)})
    return filename
