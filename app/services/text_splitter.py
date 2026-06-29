from app.schemas.document import Block, Chunk


def guess_block_type(paragraph: str, is_first: bool = False) -> str:
    text = paragraph.strip()

    if not text:
        return "unknown"

    if is_first and len(text) < 80 and "\n" not in text and text.count(".") <= 1:
        return "title"

    if len(text) < 120 and text.isupper():
        return "section_header"

    return "paragraph"


def build_blocks_from_text(text: str) -> list[Block]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    blocks = []

    for idx, paragraph in enumerate(paragraphs, start=1):
        block_type = guess_block_type(paragraph, is_first=(idx == 1))

        blocks.append(
            Block(
                block_id=f"b{idx}",
                page_num=1,
                block_order=idx,
                block_type=block_type,
                text=paragraph,
                confidence=1.0,
            )
        )

    return blocks


def build_blocks_from_pages(page_texts: list[str]) -> list[Block]:
    blocks = []
    block_counter = 1

    for page_num, page_text in enumerate(page_texts, start=1):
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]

        for idx, paragraph in enumerate(paragraphs, start=1):
            block_type = guess_block_type(
                paragraph,
                is_first=(idx == 1),
            )

            blocks.append(
                Block(
                    block_id=f"b{block_counter}",
                    page_num=page_num,
                    block_order=block_counter,
                    block_type=block_type,
                    text=paragraph,
                    confidence=1.0,
                )
            )
            block_counter += 1

    return blocks


def build_blocks_from_sheet_rows(sheets_data: list[dict]) -> list[Block]:
    blocks = []
    block_index = 1

    for page_num, sheet in enumerate(sheets_data, start=1):
        sheet_name = sheet["sheet_name"]
        rows = sheet["rows"]

        if sheet_name:
            blocks.append(
                Block(
                    block_id=f"b{block_index}",
                    page_num=page_num,
                    block_order=block_index,
                    block_type="section_header",
                    text=sheet_name,
                    confidence=1.0,
                )
            )
            block_index += 1

        for row_text in rows:
            blocks.append(
                Block(
                    block_id=f"b{block_index}",
                    page_num=page_num,
                    block_order=block_index,
                    block_type="table_row",
                    text=row_text,
                    confidence=1.0,
                )
            )
            block_index += 1

    return blocks


def build_blocks_from_word_elements(elements: list[dict]) -> list[Block]:
    blocks = []
    block_index = 1

    for element in elements:
        text = element.get("text", "").strip()
        if not text:
            continue

        element_type = element.get("type", "paragraph")

        if element_type == "table_row":
            block_type = "table_row"
        elif element_type == "table_start":
            block_type = "table_start"
        elif element_type == "table_end":
            block_type = "table_end"
        elif text.startswith("[FORMULA]"):
            block_type = "formula"
        else:
            block_type = guess_block_type(text, is_first=(block_index == 1))

        blocks.append(
            Block(
                block_id=f"b{block_index}",
                page_num=1,
                block_order=block_index,
                block_type=block_type,
                text=text,
                confidence=1.0,
            )
        )
        block_index += 1

    return blocks


def build_chunks_from_blocks(
    blocks: list[Block],
    mode: str = "native",
) -> list[Chunk]:
    if not blocks:
        return []

    if mode == "ocr":
        max_chars = 800
        soft_min_chars = 250
        hard_limit_chars = 2500
    else:
        max_chars = 1400
        soft_min_chars = 500
        hard_limit_chars = 4000

    chunks: list[Chunk] = []
    current_blocks: list[Block] = []
    chunk_order = 1
    inside_table = False

    def estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    def detect_chunk_content_type(block_types: list[str]) -> str:
        unique_types = set(block_types)

        if "table_row" in unique_types:
            return "table"
        if "formula" in unique_types:
            return "formula"
        if unique_types & {"title", "section_header"}:
            return "section"
        return "text"

    def find_section_title(block_group: list[Block]) -> str | None:
        for block in reversed(block_group):
            if block.block_type in {"title", "section_header"}:
                return block.text.strip()
        return None

    def flush_chunk(block_group: list[Block], order: int) -> Chunk | None:
        if not block_group:
            return None

        texts = []
        for b in block_group:
            t = b.text.strip()
            if t:
                texts.append(t)

        if not texts:
            return None

        chunk_text = "\n\n".join(texts)
        page_nums = sorted({b.page_num for b in block_group})
        block_types = [b.block_type for b in block_group]

        content_type = detect_chunk_content_type(block_types)
        section_title = find_section_title(block_group)

        if section_title:
            source_context = f"Раздел: {section_title}"
        elif page_nums:
            source_context = f"Страницы: {', '.join(map(str, page_nums))}"
        else:
            source_context = None

        return Chunk(
            chunk_id=f"c{order}",
            chunk_order=order,
            block_ids=[b.block_id for b in block_group],
            text=chunk_text,
            page_span=page_nums,
            block_types=block_types,
            char_count=len(chunk_text),
            section_title=section_title,
            content_type=content_type,
            source_context=source_context,
            token_estimate=estimate_tokens(chunk_text),
        )

    for block in blocks:
        if not block.text.strip():
            continue

        if block.block_type == "table_start":
            if current_blocks:
                chunk = flush_chunk(current_blocks, chunk_order)
                if chunk:
                    chunks.append(chunk)
                    chunk_order += 1
                current_blocks = []

            inside_table = True
            current_blocks.append(block)
            continue

        candidate_blocks = current_blocks + [block]
        candidate_text = "\n\n".join(b.text.strip() for b in candidate_blocks)

        if not current_blocks:
            current_blocks.append(block)

            if block.block_type == "table_row":
                inside_table = True
            elif block.block_type == "table_end":
                inside_table = False

            continue

        prev_block = current_blocks[-1]

        page_changed = prev_block.page_num != block.page_num
        is_boundary = block.block_type in {
            "title",
            "section_header",
            "table_start",
            "formula",
        }

        exceeds_limit = len(candidate_text) > max_chars
        hard_limit_exceeded = len(candidate_text) > hard_limit_chars

        should_flush = False

        if hard_limit_exceeded:
            should_flush = True
        elif exceeds_limit and not inside_table:
            should_flush = True
        elif mode == "ocr" and len(candidate_text) > soft_min_chars:
            if page_changed:
                should_flush = True
        elif mode == "native" and len(candidate_text) > soft_min_chars:
            if not inside_table and (page_changed or is_boundary):
                should_flush = True

        if should_flush:
            chunk = flush_chunk(current_blocks, chunk_order)
            if chunk:
                chunks.append(chunk)
                chunk_order += 1
            current_blocks = [block]
        else:
            current_blocks.append(block)

        if block.block_type == "table_row":
            inside_table = True

        if block.block_type == "table_end":
            inside_table = False

            chunk = flush_chunk(current_blocks, chunk_order)
            if chunk:
                chunks.append(chunk)
                chunk_order += 1
            current_blocks = []

    chunk = flush_chunk(current_blocks, chunk_order)
    if chunk:
        chunks.append(chunk)

    return chunks