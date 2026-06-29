import time
import uuid

from app.parsers.txt_parser import parse_txt
from app.schemas.document import (
    ETLResponse,
    SourceMeta,
    DocumentMeta,
    Content,
    Page,
    ProcessingInfo,
)

from app.parsers.doc_parser import parse_doc
from app.parsers.pdf_parser import parse_pdf
from app.parsers.rtf_parser import parse_rtf
from app.parsers.image_parser import parse_image
from app.parsers.pdf_ocr_parser import parse_scanned_pdf
from app.parsers.docx_parser import parse_docx
from app.parsers.xlsx_parser import parse_xlsx
from app.services.ocr_extractor import build_ocr_line_blocks, merge_ocr_lines_to_paragraphs
from app.services.ocr_filter import filter_ocr_noise
from app.services.processing_stats import build_processing_stats
from app.services.text_splitter import (
    build_blocks_from_text,
    build_chunks_from_blocks,
    build_blocks_from_pages,
    build_blocks_from_sheet_rows,
    build_blocks_from_word_elements,
)
from app.services.text_cleaner import clean_text
from app.services.quality_scorer import (
    compute_page_quality_score,
    compute_document_quality_score,
    get_quality_label,
)
from app.utils.file_types import detect_file_type


def run_etl(file_name: str, file_bytes: bytes) -> ETLResponse:
    started = time.time()
    doc_id = str(uuid.uuid4())
    file_type = detect_file_type(file_name)

    warnings = []
    errors = []
    extra_stats = {}

    full_text = ""
    page_count = 0
    is_scanned = False
    extraction_method = "native"
    pages = []
    blocks = []
    page_scores = []

    if file_type == "txt":
        full_text = clean_text(parse_txt(file_bytes))
        page_count = 1
        is_scanned = False
        extraction_method = "native"

        page_score = compute_page_quality_score(
            text=full_text,
            extraction_method="native",
            confidence=None,
        )
        page_scores = [page_score]

        pages = [
            Page(
                page_num=1,
                text=full_text,
                quality_score=page_score,
            )
        ]
        blocks = build_blocks_from_text(full_text)

    elif file_type == "docx":
        try:
            parsed = parse_docx(file_bytes)

            full_text = clean_text(parsed["full_text"])
            elements = parsed["elements"]
            word_stats = parsed.get("stats", {})
            extra_stats.update(word_stats)

            page_count = None
            is_scanned = False
            extraction_method = "native"

            if word_stats.get("tables_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['tables_count']} таблицы; извлеченные в виде блоков table_row."
                )

            if word_stats.get("equations_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['equations_count']} уравнений; извлечение формул ограничено."
                )

            if word_stats.get("images_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['images_count']} изображений; извлечение изображений не реализовано."
                )

            if word_stats.get("embedded_objects_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['embedded_objects_count']} встроенных объектов; извлечение ограничено."
                )

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="native",
                confidence=None,
            )

            tables_count = word_stats.get("tables_count", 0)
            equations_count = word_stats.get("equations_count", 0)
            images_count = word_stats.get("images_count", 0)
            embedded_objects_count = word_stats.get("embedded_objects_count", 0)

            if tables_count > 0:
                page_score = max(0, page_score - min(10, tables_count * 2))

            if equations_count > 0:
                page_score = max(0, page_score - min(15, equations_count * 3))

            if images_count > 0:
                page_score = max(0, page_score - min(15, images_count * 3))

            if embedded_objects_count > 0:
                page_score = max(0, page_score - min(20, embedded_objects_count * 5))

            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    quality_score=page_score,
                )
            ]

            blocks = build_blocks_from_word_elements(elements)

        except Exception as e:
            errors.append(f"DOCX processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "doc":
        try:
            parsed = parse_doc(file_bytes)

            full_text = clean_text(parsed["full_text"])
            elements = parsed["elements"]
            word_stats = parsed.get("stats", {})
            extra_stats.update(word_stats)

            page_count = None
            is_scanned = False
            extraction_method = "native"

            warnings.append(
                "DOC file was converted to DOCX via LibreOffice; layout may differ from original."
            )

            if word_stats.get("tables_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['tables_count']} таблицы; извлеченные в виде блоков table_row."
                )

            if word_stats.get("equations_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['equations_count']} уравнений; извлечение формул ограничено."
                )

            if word_stats.get("images_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['images_count']} изображений; извлечение изображений не реализовано."
                )

            if word_stats.get("embedded_objects_count", 0) > 0:
                warnings.append(
                    f"Документ Word содержит {word_stats['embedded_objects_count']} встроенных объектов; извлечение ограничено."
                )

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="native",
                confidence=None,
            )

            tables_count = word_stats.get("tables_count", 0)
            equations_count = word_stats.get("equations_count", 0)
            images_count = word_stats.get("images_count", 0)
            embedded_objects_count = word_stats.get("embedded_objects_count", 0)

            if tables_count > 0:
                page_score = max(0, page_score - min(10, tables_count * 2))

            if equations_count > 0:
                page_score = max(0, page_score - min(15, equations_count * 3))

            if images_count > 0:
                page_score = max(0, page_score - min(15, images_count * 3))

            if embedded_objects_count > 0:
                page_score = max(0, page_score - min(20, embedded_objects_count * 5))

            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    quality_score=page_score,
                )
            ]

            blocks = build_blocks_from_word_elements(elements)

        except Exception as e:
            errors.append(f"DOC processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "rtf":
        try:
            full_text = clean_text(parse_rtf(file_bytes))

            page_count = None
            is_scanned = False
            extraction_method = "native"
            text_extracted = bool(full_text.strip())

            warnings.append(
                "Количество страниц в формате RTF недоступно без рендеринга документа."
            )

            formula_markers = [
                "формула",
                "формулы",
                "по формуле",
                "(1)",
                "(2)",
                "(3)",
                "(4)",
                "(5)",
                "(6)",
                "(7)",
                "(8)",
                "(9)",
            ]

            has_formula_like_content = any(
                marker in full_text.lower()
                for marker in formula_markers
            )

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="native",
                confidence=None,
            )

            if has_formula_like_content:
                page_score = max(0, page_score - 10)
                warnings.append(
                    "RTF содержит формулы; извлечение формул может быть неполным."
                )

            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    quality_score=page_score,
                )
            ]

            blocks = build_blocks_from_text(full_text)

        except Exception as e:
            errors.append(f"RTF processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "xlsx":
        try:
            sheets_data, page_count = parse_xlsx(file_bytes)
            is_scanned = False
            extraction_method = "native"

            cleaned_sheet_texts = [clean_text(sheet["text"]) for sheet in sheets_data]
            full_text = "\n\n".join([text for text in cleaned_sheet_texts if text.strip()])

            pages = []
            page_scores = []

            for i, sheet in enumerate(sheets_data):
                page_text = clean_text(sheet["text"])

                page_score = compute_page_quality_score(
                    text=page_text,
                    extraction_method="native",
                    confidence=None,
                )
                page_scores.append(page_score)

                pages.append(
                    Page(
                        page_num=i + 1,
                        text=page_text,
                        quality_score=page_score,
                    )
                )

                sheet["text"] = page_text

            blocks = build_blocks_from_sheet_rows(sheets_data)

        except Exception as e:
            errors.append(f"XLSX processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "pdf":
        try:
            page_texts, page_count, has_text_layer = parse_pdf(file_bytes)

            page_ocr_data = []
            page_confidences = []

            def count_suspicious_words(text: str) -> int:
                return sum(
                    1
                    for word in text.split()
                    if len(word) > 20 and not any(ch.isdigit() for ch in word)
                )

            def has_valid_text(text: str) -> bool:
                valid_words = sum(1 for w in text.split() if len(w) > 2)
                return valid_words > 20

            def get_confidence(idx: int) -> float | None:
                if idx < len(page_confidences):
                    return page_confidences[idx]
                return None

            pdf_artifacts = ["■■", "���", "□", "�"]

            formula_markers = [
                "формула",
                "формулы",
                "по формуле",
                "(1)",
                "(2)",
                "(3)",
                "(4)",
                "(5)",
                "(6)",
                "(7)",
                "(8)",
                "(9)",
            ]

            if has_text_layer:
                cleaned_pages = [clean_text(p) for p in page_texts]

                native_text = "\n\n".join(p for p in cleaned_pages if p.strip())
                empty_native_pages = sum(1 for p in cleaned_pages if not p.strip())

                native_text_too_small = len(native_text) < 500
                too_many_empty_pages = (
                    page_count > 0 and empty_native_pages / page_count > 0.5
                )

                should_fallback_to_ocr = native_text_too_small or too_many_empty_pages

                if should_fallback_to_ocr:
                    warnings.append(
                        "Текстовый слой PDF-файла недостаточен; использован OCR fallback."
                    )

                    page_texts, page_count, page_ocr_data, page_confidences = parse_scanned_pdf(
                        file_bytes
                    )

                    is_scanned = True
                    extraction_method = "ocr"
                    cleaned_pages = [clean_text(p) for p in page_texts]
                else:
                    is_scanned = False
                    extraction_method = "native"
                    page_confidences = [None] * len(cleaned_pages)

            else:
                page_texts, page_count, page_ocr_data, page_confidences = parse_scanned_pdf(
                    file_bytes
                )

                is_scanned = True
                extraction_method = "ocr"
                cleaned_pages = [clean_text(p) for p in page_texts]

            full_text = "\n\n".join(p for p in cleaned_pages if p.strip())
            text_extracted = has_valid_text(full_text)

            artifact_count = sum(full_text.count(a) for a in pdf_artifacts)
            artifact_ratio = artifact_count / max(len(full_text), 1)

            if extraction_method == "native":
                if artifact_ratio > 0.03:
                    warnings.append(
                        "Текстовый слой PDF-файла содержит артефакты; качество извлечения может быть ограничено."
                    )

                if count_suspicious_words(full_text) > 30:
                    warnings.append(
                        "Текстовый слой PDF-файла содержит подозрительно длинные токены; качество извлечения может быть ограничено."
                    )

                if any(marker in full_text.lower() for marker in formula_markers):
                    warnings.append(
                        "PDF содержит формулы или похожий на формулы контент; извлечение формул может быть неполным."
                    )

            pages = []
            page_scores = []

            if extraction_method == "ocr":
                blocks = []
                paragraph_index = 1

                for page_num, ocr_data in enumerate(page_ocr_data, start=1):
                    line_blocks = build_ocr_line_blocks(
                        ocr_data,
                        page_num=page_num,
                        start_block_index=paragraph_index,
                    )

                    paragraph_blocks = merge_ocr_lines_to_paragraphs(line_blocks)

                    for block in paragraph_blocks:
                        block.block_id = f"b{paragraph_index}"
                        block.block_order = paragraph_index
                        blocks.append(block)
                        paragraph_index += 1

                blocks, removed_ocr_noise = filter_ocr_noise(blocks)

                if removed_ocr_noise > 0:
                    warnings.append(
                        f"Removed {removed_ocr_noise} low-quality OCR blocks from indexing."
                    )

                full_text = "\n\n".join(
                    block.text.strip()
                    for block in blocks
                    if block.text.strip()
                )
                text_extracted = has_valid_text(full_text)

                page_text_map = {}

                for block in blocks:
                    page_text_map.setdefault(block.page_num, []).append(block.text.strip())

                for page_num in range(1, page_count + 1):
                    page_blocks = page_text_map.get(page_num)

                    if page_blocks:
                        page_text = "\n\n".join(page_blocks)
                    else:
                        page_text = (
                            cleaned_pages[page_num - 1]
                            if page_num - 1 < len(cleaned_pages)
                            else ""
                        )

                    page_conf = get_confidence(page_num - 1)

                    page_score = compute_page_quality_score(
                        text=page_text,
                        extraction_method="ocr",
                        confidence=page_conf,
                    )

                    page_has_formula_like_content = any(
                        marker in page_text.lower()
                        for marker in formula_markers
                    )

                    if not has_valid_text(page_text):
                        page_score = max(0, page_score - 10)

                    if page_has_formula_like_content:
                        page_score = max(0, page_score - 3)

                    page_scores.append(page_score)

                    pages.append(
                        Page(
                            page_num=page_num,
                            text=page_text,
                            confidence=page_conf,
                            quality_score=page_score,
                        )
                    )

            else:
                blocks = build_blocks_from_pages(cleaned_pages)

                for i, page_text in enumerate(cleaned_pages):
                    page_conf = get_confidence(i)

                    page_score = compute_page_quality_score(
                        text=page_text,
                        extraction_method="native",
                        confidence=page_conf,
                    )

                    page_artifact_count = sum(page_text.count(a) for a in pdf_artifacts)
                    page_artifact_ratio = page_artifact_count / max(len(page_text), 1)

                    page_suspicious_words = count_suspicious_words(page_text)

                    page_has_formula_like_content = any(
                        marker in page_text.lower()
                        for marker in formula_markers
                    )

                    if page_artifact_ratio > 0.03:
                        page_score = max(0, page_score - 10)

                    if page_suspicious_words > 10:
                        page_score = max(0, page_score - 10)

                    if page_has_formula_like_content:
                        page_score = max(0, page_score - 5)

                    page_scores.append(page_score)

                    pages.append(
                        Page(
                            page_num=i + 1,
                            text=page_text,
                            confidence=page_conf,
                            quality_score=page_score,
                        )
                    )

        except Exception as e:
            errors.append(f"PDF processing error: {type(e).__name__}: {str(e)}")
            
    elif file_type == "image":
        try:
            raw_text, _, avg_conf, ocr_data = parse_image(file_bytes)
            full_text = clean_text(raw_text)
            page_count = 1
            is_scanned = True
            extraction_method = "ocr"

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="ocr",
                confidence=avg_conf,
            )
            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    confidence=avg_conf,
                    quality_score=page_score,
                )
            ]

            line_blocks = build_ocr_line_blocks(ocr_data, page_num=1) if ocr_data else []
            blocks = merge_ocr_lines_to_paragraphs(line_blocks) if line_blocks else []

        except Exception as e:
            errors.append(f"Image processing error: {type(e).__name__}: {str(e)}")

    else:
        warnings.append(f"Parser for file type '{file_type}' is not implemented yet.")

    if extraction_method == "ocr":
        chunks = build_chunks_from_blocks(blocks, mode="ocr")
    else:
        chunks = build_chunks_from_blocks(blocks, mode="native")
    duration_ms = int((time.time() - started) * 1000)
    text_extracted = bool(full_text.strip())

    document_quality_score = compute_document_quality_score(page_scores) if pages else 0.0
    document_quality_label = get_quality_label(document_quality_score)

    processing_stats = build_processing_stats(
    full_text=full_text,
    pages=pages,
    blocks=blocks,
    chunks=chunks,
    extra_stats=extra_stats,
)

    return ETLResponse(
        document_id=doc_id,
        source=SourceMeta(
            file_name=file_name,
            file_type=file_type,
        ),
        document=DocumentMeta(
            language=["ru"],
            page_count=page_count,
            is_scanned=is_scanned,
            extraction_method=extraction_method,
            text_extracted=text_extracted,
            quality_score=document_quality_score,
            quality_label=document_quality_label,
        ),
        content=Content(
            full_text=full_text,
            pages=pages,
            blocks=blocks,
            chunks=chunks,
        ),
        processing=ProcessingInfo(
            status="success" if not errors else "failed",
            pipeline_version="0.1.0",
            duration_ms=duration_ms,
            warnings=warnings,
            errors=errors,
            stats=processing_stats,
        ),
    )