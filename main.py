from app.config.settings import settings
from app.services.document_service import DocumentService
from app.utils.logger import logger


def main() -> None:
    logger.info("Starting %s %s", settings.app_name, settings.app_version)

    service = DocumentService()
    print(settings.app_name)
    print("DocumentService initialized:", service.__class__.__name__)


if __name__ == "__main__":
    main()