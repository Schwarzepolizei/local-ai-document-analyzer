from pathlib import Path

from app.services.document_service import DocumentService


def main() -> None:
    service = DocumentService()

    test_file = Path("data/raw/test.txt")

    result = service.extract_information(
        file_path=test_file,
        user_request="Извлеки цель документа и основные возможности агента.",
    )

    print("Файл:", result.file_name)
    print("Запрос:", result.request)

    print("\nНайдено:")
    for item in result.items:
        print(f"- {item.field}: {item.value}")
        if item.source:
            print(f"  Источник: {item.source}")
        if item.confidence:
            print(f"  Уверенность: {item.confidence}")

    print("\nНе найдено:")
    for item in result.missing:
        print("-", item)

    print("\nПримечания:")
    for note in result.notes:
        print("-", note)


if __name__ == "__main__":
    main()
