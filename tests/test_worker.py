from datetime import timedelta

import pytest
from django.utils import timezone

from collector.models import Source, SourceRuntimeState
from collector.services.crawler import lease_next_source


@pytest.mark.django_db
def test_expired_lease_is_recovered():
    source = Source.objects.create(name="Due", base_url="https://due.example/", domain="due.example")
    SourceRuntimeState.objects.create(source=source, next_run_at=timezone.now() - timedelta(hours=1), lease_until=timezone.now() - timedelta(minutes=1), lease_owner="dead")
    state = lease_next_source("new-worker")
    assert state.source_id == source.pk
    assert state.lease_owner == "new-worker"
    assert state.lease_until > timezone.now()
