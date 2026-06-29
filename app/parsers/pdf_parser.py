import io
import pdfplumber


def parse_pdf(file_bytes: bytes) -> tuple[list[str], int, bool]:
    """
    Возвращает:
    page_texts, page_count, has_text_layer
    """
    page_texts = []
    has_text_layer = False

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            page_text = page_text.strip()

            if page_text:
                has_text_layer = True

            page_texts.append(page_text)

        page_count = len(pdf.pages)

    return page_texts, page_count, has_text_layer