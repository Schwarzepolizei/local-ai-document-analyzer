import re
from app.schemas.document import Block


def _meaningful_ratio(text: str) -> float:
    if not text:
        return 0.0

    meaningful = re.findall(r"[A-Za-zА-Яа-яЁё0-9]", text)
    return len(meaningful) / max(1, len(text))


def _has_cyrillic(text: str) -> bool:
    return bool(re.search(r"[А-Яа-яЁё]", text))


def is_ocr_noise(block: Block) -> bool:
    text = block.text.strip()

    if not text:
        return True

    confidence = block.confidence or 0

    if confidence < 50 and len(text) < 40:
        return True

    if len(text) <= 3 and confidence < 80:
        return True

    if _meaningful_ratio(text) < 0.45 and confidence < 70:
        return True

    if not _has_cyrillic(text) and len(text) < 25 and confidence < 75:
        return True

    return False


def filter_ocr_noise(blocks: list[Block]) -> tuple[list[Block], int]:
    filtered = []

    for block in blocks:
        if not is_ocr_noise(block):
            filtered.append(block)

    removed_count = len(blocks) - len(filtered)

    for idx, block in enumerate(filtered, start=1):
        block.block_id = f"b{idx}"
        block.block_order = idx

    return filtered, removed_count