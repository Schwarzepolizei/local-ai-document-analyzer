import io

import fitz
from PIL import Image

from app.services.image_preprocessor import preprocess_pil_image_for_ocr
from app.services.ocr_extractor import (
    extract_ocr_data,
    filter_ocr_data,
    build_text_from_ocr_data,
    compute_average_confidence,
)


def parse_scanned_pdf(file_bytes: bytes) -> tuple[list[str], int, list[list[dict]], list[float | None]]:
    page_texts = []
    page_ocr_data = []
    page_confidences = []

    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        pix = page.get_pixmap(dpi=250)
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        if image.mode != "RGB":
            image = image.convert("RGB")

        processed_image = preprocess_pil_image_for_ocr(image)

        ocr_data = extract_ocr_data(
            processed_image,
            lang="rus+eng",
            config="--oem 3 --psm 6"
        )

        ocr_data = filter_ocr_data(ocr_data)

        text = build_text_from_ocr_data(ocr_data).strip()
        avg_conf = compute_average_confidence(ocr_data)

        page_texts.append(text)
        page_ocr_data.append(ocr_data)
        page_confidences.append(avg_conf)

    page_count = len(page_texts)
    pdf.close()

    return page_texts, page_count, page_ocr_data, page_confidences