import re
from typing import Optional


def compute_text_noise_ratio(text: str) -> float:
    if not text.strip():
        return 1.0

    non_space_chars = [ch for ch in text if not ch.isspace()]
    if not non_space_chars:
        return 1.0

    bad_chars = sum(
        1 for ch in non_space_chars
        if not (ch.isalnum() or ch in ".,:;!?()[]%+-=/№\"'«»")
    )

    return round(bad_chars / len(non_space_chars), 4)

def compute_page_quality_score(
    text: str,
    extraction_method: str,
    confidence: Optional[float] = None,
) -> float:
    text = text or ""
    text_len = len(text.strip())
    noise_ratio = compute_text_noise_ratio(text)

    if text_len == 0:
        return 0.0

    if extraction_method == "ocr":
        conf_score = (confidence or 0.0) / 100.0
        length_score = min(text_len / 1000, 1.0)
        noise_score = max(0.0, 1.0 - noise_ratio)

        score = (
            0.5 * conf_score +
            0.3 * length_score +
            0.2 * noise_score
        )
    else:
        length_score = min(text_len / 1500, 1.0)
        noise_score = max(0.0, 1.0 - noise_ratio)

        score = (
            0.7 * length_score +
            0.3 * noise_score
        )

    return round(score * 100, 2)

def compute_document_quality_score(page_scores: list[float]) -> float:
    if not page_scores:
        return 0.0

    return round(sum(page_scores) / len(page_scores), 2)


def get_quality_label(score: float) -> str:
    if score >= 80:
        return "high"
    if score >= 55:
        return "medium"
    return "low"