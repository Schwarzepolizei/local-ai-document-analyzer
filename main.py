from pathlib import Path

from app.config.settings import settings
from app.services.document_service import DocumentService
from app.utils.logger import logger


def main() -> None:
    logger.info("Starting %s %s", settings.app_name, settings.app_version)

    service = DocumentService()

    test_file = Path("data/raw/test.txt")

    if not test_file.exists():
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            "Это тестовый документ. Он нужен для проверки ETL pipeline.",
            encoding="utf-8",
        )

    result = service.process_document(test_file)

    print("Document:", result.source.file_name)
    print("Status:", result.processing.status)
    print("Full text:", result.content.full_text[:200])
    print("Chunks:", len(result.content.chunks))
    print("Quality:", result.document.quality_label)


if __name__ == "__main__":
    main()