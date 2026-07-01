from pathlib import Path

from app.services.document_service import DocumentService


def main() -> None:
    service = DocumentService()

    test_file = Path("data/raw/test.txt")

    summary = service.summarize_document(test_file)

    output_path = service.export_summary_to_markdown(
        summary=summary,
        output_path="data/processed/test_summary.md",
    )

    print("Summary exported to:", output_path)


if __name__ == "__main__":
    main()
