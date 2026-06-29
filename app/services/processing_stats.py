from typing import Optional

from app.schemas.document import Page, Block, Chunk, ProcessingStats


def _safe_avg(values: list[float]) -> Optional[float]:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def build_processing_stats(
    full_text: str,
    pages: list[Page],
    blocks: list[Block],
    chunks: list[Chunk],
    extra_stats: dict | None = None,
) -> ProcessingStats:
    extra_stats = extra_stats or {}

    page_confidences = [p.confidence for p in pages if p.confidence is not None]
    page_qualities = [p.quality_score for p in pages if p.quality_score is not None]

    empty_pages_count = sum(1 for p in pages if not p.text.strip())

    table_rows_count = sum(1 for b in blocks if b.block_type == "table_row")

    return ProcessingStats(
        pages_count=len(pages),
        blocks_count=len(blocks),
        chunks_count=len(chunks),
        empty_pages_count=empty_pages_count,
        text_length=len(full_text),
        avg_page_confidence=_safe_avg(page_confidences),
        avg_page_quality=_safe_avg(page_qualities),

        tables_count=extra_stats.get("tables_count", 0),
        table_rows_count=table_rows_count,
        images_count=extra_stats.get("images_count", 0),
        equations_count=extra_stats.get("equations_count", 0),
        embedded_objects_count=extra_stats.get("embedded_objects_count", 0),
    )