from pathlib import Path

from app.agent.summarizer import Summarizer
from app.pipeline.etl_pipeline import run_etl
from app.schemas.summary import SummaryResult
from app.utils.logger import logger


class DocumentService:
    def process_document(self, file_path: str | Path) -> SummaryResult:
        path = Path(file_path)

        logger.info("Processing document: %s", path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        file_bytes = path.read_bytes()

        result = run_etl(
            file_name=path.name,
            file_bytes=file_bytes,
        )

        logger.info(
            "Document processed: %s | status=%s | chunks=%s | quality=%s",
            path.name,
            result.processing.status,
            len(result.content.chunks),
            result.document.quality_label,
        )

        return result

    def summarize_document(self, file_path: str | Path) -> SummaryResult:
        document = self.process_document(file_path)
        summarizer = Summarizer()

        logger.info("Summarizing document: %s", document.source.file_name)

        return summarizer.summarize(document)
