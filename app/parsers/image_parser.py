from app.services.image_preprocessor import preprocess_image_for_ocr
from app.services.ocr_extractor import (
    extract_ocr_data,
    filter_ocr_data,
    build_text_from_ocr_data,
    compute_average_confidence,
)


def parse_image(file_bytes: bytes) -> tuple[str, bool, float | None, list[dict]]:
    image = preprocess_image_for_ocr(file_bytes)

    ocr_data = extract_ocr_data(
        image,
        lang="rus+eng",
        config="--oem 3 --psm 6"
    )

    ocr_data = filter_ocr_data(ocr_data)

    text = build_text_from_ocr_data(ocr_data).strip()
    avg_conf = compute_average_confidence(ocr_data)
    has_text = bool(text)

    return text, has_text, avg_conf, ocr_data