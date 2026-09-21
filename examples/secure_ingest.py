"""Sanitized example: validate and normalize a document before ingestion.

This module contains no production identifiers, credentials, or private data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import re
from typing import Mapping


FORBIDDEN_KEYS = frozenset({"password", "api_key", "token", "secret", "private_key"})
SECRET_PATTERNS = (
    re.compile(r"(?i)bearer\s+[a-z0-9._-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|secret)\s*[:=]\s*\S+"),
)


@dataclass(frozen=True)
class SafeDocument:
    title: str
    content: str
    source_type: str
    fingerprint: str


def _clean_text(value: object, *, max_length: int) -> str:
    text = " ".join(str(value).split()).strip()
    if not text:
        raise ValueError("Required text is empty")
    if len(text) > max_length:
        raise ValueError(f"Text exceeds {max_length} characters")
    return text


def validate_payload(payload: Mapping[str, object]) -> SafeDocument:
    """Return a normalized, deduplicatable document or reject unsafe input."""
    normalized_keys = {str(key).lower() for key in payload}
    blocked = sorted(FORBIDDEN_KEYS.intersection(normalized_keys))
    if blocked:
        raise ValueError(f"Sensitive fields are not accepted: {blocked}")

    title = _clean_text(payload.get("title", ""), max_length=200)
    content = _clean_text(payload.get("content", ""), max_length=20_000)
    source_type = _clean_text(payload.get("source_type", "demo"), max_length=40)

    if any(pattern.search(content) for pattern in SECRET_PATTERNS):
        raise ValueError("Content appears to contain a secret")

    fingerprint = sha256(f"{source_type}\0{title}\0{content}".encode()).hexdigest()
    return SafeDocument(title, content, source_type, fingerprint)


def public_record(payload: Mapping[str, object]) -> dict[str, str]:
    """Example boundary: expose only explicitly approved fields."""
    return asdict(validate_payload(payload))


if __name__ == "__main__":
    demo = {
        "title": "Architecture notes",
        "content": "Hybrid retrieval combines keyword and semantic search.",
        "source_type": "sanitized-demo",
    }
    print(public_record(demo))
