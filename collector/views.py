from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import SourceForm
from .models import CrawlRun, NewsItem, OperatorEvent, ReviewEvent, Source


@login_required
def dashboard(request):
    latest_backup = OperatorEvent.objects.filter(event_type__in=["backup_success", "backup_failed"]).first()
    context = {
        "source_counts": Source.objects.values("status").annotate(count=Count("id")).order_by("status"),
        "news_count": NewsItem.objects.filter(purged_at__isnull=True).count(),
        "unreviewed_count": NewsItem.objects.filter(purged_at__isnull=True, review_events__isnull=True).count(),
        "recent_runs": CrawlRun.objects.select_related("source")[:10],
        "recent_events": OperatorEvent.objects.select_related("source")[:10],
        "latest_backup": latest_backup,
    }
    return render(request, "collector/dashboard.html", context)


@login_required
def source_list(request):
    status = request.GET.get("status")
    sources = Source.objects.select_related("runtime").annotate(news_count=Count("occurrences", distinct=True))
    if status:
        sources = sources.filter(status=status)
    return render(request, "collector/source_list.html", {"sources": sources, "statuses": Source.Status.choices, "selected_status": status})


@login_required
def source_create(request):
    form = SourceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        source = form.save()
        messages.success(request, "Источник добавлен. Worker обнаружит доступные ленты при следующем запуске.")
        return redirect("source_detail", pk=source.pk)
    return render(request, "collector/source_form.html", {"form": form, "heading": "Новый источник"})


@login_required
def source_edit(request, pk):
    source = get_object_or_404(Source, pk=pk)
    form = SourceForm(request.POST or None, instance=source)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Источник обновлен")
        return redirect("source_detail", pk=source.pk)
    return render(request, "collector/source_form.html", {"form": form, "heading": f"Источник: {source.name}"})


@login_required
def source_detail(request, pk):
    source = get_object_or_404(Source.objects.select_related("runtime"), pk=pk)
    cutoff = timezone.now() - timezone.timedelta(days=30)
    decisions = ReviewEvent.objects.filter(news_item__occurrences__source=source, created_at__gte=cutoff).values("decision").annotate(count=Count("id"))
    return render(request, "collector/source_detail.html", {"source": source, "runs": source.crawl_runs.all()[:30], "decisions": decisions})


@login_required
def source_resume(request, pk):
    if request.method == "POST":
        source = get_object_or_404(Source, pk=pk)
        source.status = Source.Status.PROBATION
        source.probation_started_at = timezone.now()
        source.save(update_fields=["status", "probation_started_at", "updated_at"])
        OperatorEvent.objects.create(event_type="source_resumed", source=source, message="Источник возвращен в probation оператором")
        messages.success(request, "Источник возвращен в пробный режим")
    return redirect("source_detail", pk=pk)


@login_required
def news_list(request):
    items = NewsItem.objects.prefetch_related("occurrences__source").annotate(source_count=Count("occurrences__source", distinct=True))
    decision = request.GET.get("decision")
    if decision == "unreviewed":
        items = items.filter(review_events__isnull=True)
    elif decision:
        items = items.filter(review_events__decision=decision)
    return render(request, "collector/news_list.html", {"items": items[:200], "decision": decision})


@login_required
def news_detail(request, pk):
    item = get_object_or_404(NewsItem.objects.prefetch_related("occurrences__source", "review_events"), pk=pk)
    return render(request, "collector/news_detail.html", {"item": item})


@login_required
def run_list(request):
    return render(request, "collector/run_list.html", {"runs": CrawlRun.objects.select_related("source")[:300]})


@login_required
def event_list(request):
    return render(request, "collector/event_list.html", {"events": OperatorEvent.objects.select_related("source")[:300]})

