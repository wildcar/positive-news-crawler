import json
import re
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from collector.models import NewsItem, NewsTranslation

from .model_router import ModelRouterError, call_chat


class TranslationError(RuntimeError):
    pass


@dataclass(frozen=True)
class TranslationResult:
    title: str
    body_text: str
    summary: str
    model_id: str


def _extract_json(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    source = fenced.group(1) if fenced else text
    start = source.find("{")
    decoder = json.JSONDecoder()
    if start < 0:
        raise TranslationError("model response does not contain JSON")
    try:
        payload, _ = decoder.raw_decode(source[start:])
    except json.JSONDecodeError as exc:
        raise TranslationError("model response contains invalid JSON") from exc
    if not isinstance(payload, dict):
        raise TranslationError("model response is not a JSON object")
    return payload


def translate_news(item: NewsItem) -> NewsTranslation:
    messages = [
        {
            "role": "system",
            "content": (
                "Translate the supplied news article into natural Russian and summarize it in Russian. "
                "Preserve facts, names, numbers, links, and paragraph breaks. Do not add facts or opinions. "
                "Return one JSON object with string fields title, body_text, and summary. "
                "The summary must be two to four concise sentences. Return no other text."
            ),
        },
        {
            "role": "user",
            "content": f"Title:\n{item.title}\n\nArticle language: {item.language}\n\nBody:\n{item.body_text}",
        },
    ]
    try:
        reply = call_chat(
            url=settings.NEWSCRAWLER_ROUTER_MCP_URL,
            token=settings.NEWSCRAWLER_ROUTER_AUTH_TOKEN,
            messages=messages,
            external_user_id="positive-news-crawler-translation",
            provider=settings.NEWSCRAWLER_TRANSLATION_PROVIDER,
            model_id=settings.NEWSCRAWLER_TRANSLATION_MODEL,
            tier=settings.NEWSCRAWLER_TRANSLATION_TIER,
            params={
                "temperature": settings.NEWSCRAWLER_TRANSLATION_TEMPERATURE,
                "max_tokens": settings.NEWSCRAWLER_TRANSLATION_MAX_TOKENS,
            },
            timeout=settings.NEWSCRAWLER_ROUTER_TIMEOUT_SECONDS,
        )
    except ModelRouterError:
        raise
    payload = _extract_json(reply["text"])
    fields = {key: payload.get(key) for key in ("title", "body_text", "summary")}
    if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
        raise TranslationError("model response has missing or empty translation fields")
    model_id = str(reply.get("model_id") or settings.NEWSCRAWLER_TRANSLATION_MODEL)
    translation, _ = NewsTranslation.objects.update_or_create(
        news_item=item,
        defaults={
            "title": fields["title"].strip(),
            "body_text": fields["body_text"].strip(),
            "summary": fields["summary"].strip(),
            "model_id": model_id[:200],
            "generated_at": timezone.now(),
        },
    )
    return translation
