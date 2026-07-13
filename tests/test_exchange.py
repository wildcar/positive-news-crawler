import pytest
from django.db import connection, transaction

from collector.models import ReviewEvent, Source
from collector.services.ingest import ingest_article


@pytest.mark.django_db
def test_exchange_views_and_append_only_trigger():
    source = Source.objects.create(name="One", base_url="https://one.example/", domain="one.example")
    item, _, _ = ingest_article(source=source, url="https://one.example/a", title="A useful headline", body="Substantial article body. " * 30, language="en")
    with connection.cursor() as cursor:
        cursor.execute("SELECT news_id, primary_url, sources_json FROM exchange_news_for_selection WHERE news_id=%s", [item.pk])
        row = cursor.fetchone()
    assert row[0] == item.pk
    assert row[1] == "https://one.example/a"
    event = ReviewEvent.objects.create(news_item=item, decision="positive", score=0.9, selector_name="test", selector_version="1", idempotency_key="one")
    with connection.cursor() as cursor:
        cursor.execute("SELECT decision FROM exchange_latest_reviews WHERE news_id=%s", [item.pk])
        assert cursor.fetchone()[0] == "positive"
        with pytest.raises(Exception, match="append-only"):
            with transaction.atomic():
                cursor.execute("UPDATE exchange_review_events SET reason='changed' WHERE id=%s", [event.pk])


@pytest.mark.django_db
def test_review_idempotency():
    source = Source.objects.create(name="One", base_url="https://one.example/", domain="one.example")
    item, _, _ = ingest_article(source=source, url="https://one.example/a", title="A useful headline", body="Substantial article body. " * 30)
    ReviewEvent.objects.create(news_item=item, decision="positive", selector_name="test", idempotency_key="same")
    with pytest.raises(Exception):
        ReviewEvent.objects.create(news_item=item, decision="positive", selector_name="test", idempotency_key="same")
