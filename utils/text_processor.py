"""Text segmentation for TingJu.

The project deliberately keeps sentence segmentation deterministic and local.
sentencex supplies the language-aware boundaries; the small post-processing
layer only repairs punctuation fragments and a few Japanese/Korean reporting
constructions that are not represented consistently by generic segmenters.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

import sentencex

from utils.logger import logger


LANGUAGE_CODE_MAP = {
    "english": "en",
    "french": "fr",
    "german": "de",
    "japanese": "ja",
    "korean": "ko",
    "russian": "ru",
    "spanish": "es",
    "portuguese": "pt",
    "italian": "it",
}
SUPPORTED_LANGUAGE_CODES = frozenset(LANGUAGE_CODE_MAP.values())

# These are only used to recognize a boundary that sentencex has already
# produced. They are not a second sentence segmenter.
ORPHAN_CLOSER_PATTERN = re.compile(r"^(\s*[\u201d\u2019\u00bb\u203a\u300d\u300f\uff09\u3011\u005d\u007d]+[.,!?;:\u2026]*)\s*")
PUNCTUATION_ONLY_PATTERN = re.compile(
    r"^[\s\"'\u201c\u201d\u2018\u2019\u00ab\u00bb\u2039\u203a\u300c\u300d\u300e\u300f"
    r"()\[\]{}<>.,!?;:\u2026\u3002\uff01\uff1f\uff0c\uff1b\uff1a\u3001\u2014\u2013\-]+$"
)

JAPANESE_REPORTING_PREFIXES = ("と", "って")
KOREAN_REPORTING_PREFIXES = ("라고", "고", "라며", "라면서")
QUOTE_CLOSERS = frozenset("\"'\u201d\u2019\u00bb\u203a\u300d\u300f\uff09\u3011\u005d\u007d")


@dataclass(frozen=True)
class _SentenceSpan:
    start: int
    end: int
    boundary_symbol: str | None = None


def get_sentences(paragraph: str, lang: str = "english") -> list[str]:
    """Split text into sentence-sized learning units.

    The returned strings are trimmed views of the original text. Punctuation,
    quotation marks, casing, and internal whitespace are never normalized.
    A complete quotation is intentionally treated as one unit, even when it
    contains multiple terminal punctuation marks.
    """
    if not isinstance(paragraph, str):
        raise TypeError("paragraph must be a string")

    if not paragraph.strip():
        return []

    language_code = _resolve_language_code(lang)
    spans = _get_sentence_spans(paragraph, language_code)
    spans = _apply_special_rules(paragraph, spans, language_code)

    sentences = []
    for span in spans:
        sentence = paragraph[span.start : span.end].strip()
        if sentence and _contains_word_or_number(sentence):
            sentences.append(sentence)

    logger.info("Sentence segmentation completed: %s sentences", len(sentences))
    return sentences


def _resolve_language_code(lang: str) -> str:
    """Resolve TingJu language names and ISO codes to sentencex codes."""
    key = (lang or "english").strip().lower()
    if key in LANGUAGE_CODE_MAP:
        return LANGUAGE_CODE_MAP[key]
    if key in SUPPORTED_LANGUAGE_CODES:
        return key

    logger.warning("Unsupported sentence language %r; falling back to English", lang)
    return "en"


def _get_sentence_spans(text: str, language_code: str) -> list[_SentenceSpan]:
    """Get and validate non-overlapping sentencex offsets.

    If the native segmenter fails or returns malformed offsets, returning one
    complete span is safer than dropping or rewriting source text.
    """
    try:
        raw_boundaries = sentencex.get_sentence_boundaries(language_code, text)
    except Exception as error:  # pragma: no cover - native extension failure
        logger.exception("sentencex segmentation failed: %s", error)
        return [_SentenceSpan(0, len(text))]

    spans: list[_SentenceSpan] = []
    for boundary in raw_boundaries:
        try:
            start = int(boundary["start_index"])
            end = int(boundary["end_index"])
            symbol = boundary.get("boundary_symbol")
        except (KeyError, TypeError, ValueError):
            logger.warning("sentencex returned an invalid boundary: %r", boundary)
            return [_SentenceSpan(0, len(text))]

        if not (0 <= start < end <= len(text)):
            logger.warning("sentencex returned an out-of-range boundary: %r", boundary)
            return [_SentenceSpan(0, len(text))]
        spans.append(_SentenceSpan(start, end, symbol))

    if not spans:
        return [_SentenceSpan(0, len(text))]

    if spans[0].start != 0 or spans[-1].end != len(text):
        logger.warning("sentencex boundaries did not cover the complete input")
        return [_SentenceSpan(0, len(text))]

    if any(previous.end != current.start for previous, current in zip(spans, spans[1:])):
        logger.warning("sentencex boundaries contained a gap or overlap")
        return [_SentenceSpan(0, len(text))]

    return spans


def _apply_special_rules(
    text: str,
    spans: list[_SentenceSpan],
    language_code: str,
) -> list[_SentenceSpan]:
    """Apply only narrow, deterministic corrections after sentencex."""
    merged: list[_SentenceSpan] = []

    for span in spans:
        if not merged:
            merged.append(span)
            continue

        previous = merged[-1]
        previous_text = text[previous.start : previous.end].rstrip()
        current_text = text[span.start : span.end].lstrip()

        # A generic segmenter can leave a closing quote/bracket at the start of
        # the next span. Move that prefix back without changing its characters.
        closer_match = ORPHAN_CLOSER_PATTERN.match(text[span.start : span.end])
        if closer_match and current_text and not _contains_word_or_number(closer_match.group(1)):
            prefix_length = closer_match.end()
            remaining_start = span.start + prefix_length
            if remaining_start >= span.end:
                merged[-1] = _SentenceSpan(previous.start, span.end, span.boundary_symbol)
                continue
            merged[-1] = _SentenceSpan(previous.start, remaining_start, previous.boundary_symbol)
            span = _SentenceSpan(remaining_start, span.end, span.boundary_symbol)
            current_text = text[span.start : span.end].lstrip()
            previous = merged[-1]
            previous_text = text[previous.start : previous.end].rstrip()

        # Keep punctuation-only fragments attached to the preceding unit.
        if PUNCTUATION_ONLY_PATTERN.fullmatch(current_text):
            merged[-1] = _SentenceSpan(previous.start, span.end, span.boundary_symbol)
            continue

        # Japanese/Korean reporting clauses commonly follow a closing quote
        # without whitespace. sentencex may expose that clause as a separate
        # span even though it belongs to the same spoken sentence.
        if _is_reporting_continuation(previous_text, current_text, language_code):
            merged[-1] = _SentenceSpan(previous.start, span.end, span.boundary_symbol)
            continue

        merged.append(span)

    return merged


def _is_reporting_continuation(previous: str, current: str, language_code: str) -> bool:
    if not previous or previous[-1] not in QUOTE_CLOSERS:
        return False

    if language_code == "ja":
        return current.startswith(JAPANESE_REPORTING_PREFIXES)
    if language_code == "ko":
        return current.startswith(KOREAN_REPORTING_PREFIXES)
    return False


def _contains_word_or_number(text: str) -> bool:
    """Return true for lexical content, including CJK and short sentences."""
    return any(character.isalnum() for character in text)
