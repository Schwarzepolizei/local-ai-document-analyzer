from pathlib import Path

from app.services.document_service import DocumentService


def main() -> None:
    service = DocumentService()

    test_file = Path("data/raw/test.txt")

    summary = service.summarize_document(test_file)

    print("Файл:", summary.file_name)
    print("Ключевая мысль:", summary.key_idea)
    print("Краткое саммари:", summary.short_summary)
    print("Важные факты:")
    for fact in summary.important_facts:
        print("-", fact)


if __name__ == "__main__":
    main()