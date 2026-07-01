from pathlib import Path

from app.utils.logger import logger


class DocumentService:
    def process_document(self, file_path: str | Path) -> dict:
        path = Path(file_path)

        logger.info("Processing document: %s", path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return {
            "file_name": path.name,
            "file_path": str(path),
            "status": "processed",
        }