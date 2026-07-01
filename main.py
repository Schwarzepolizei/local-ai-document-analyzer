import argparse
from pathlib import Path

from app.services.document_service import DocumentService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local AI Document Analyzer",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser("summary", help="Сделать саммари документа")
    summary_parser.add_argument("file", help="Путь к документу")
    summary_parser.add_argument(
        "--output",
        "-o",
        help="Путь для сохранения Markdown",
        default=None,
    )

    extract_parser = subparsers.add_parser(
        "extract",
        help="Извлечь информацию из документа",
    )
    extract_parser.add_argument("file", help="Путь к документу")
    extract_parser.add_argument("request", help="Что нужно извлечь")
    extract_parser.add_argument(
        "--output",
        "-o",
        help="Путь для сохранения Markdown",
        default=None,
    )

    return parser


def run_summary(file_path: str, output_path: str | None) -> None:
    service = DocumentService()
    summary = service.summarize_document(file_path)

    print("\nКлючевая мысль:")
    print(summary.key_idea)

    print("\nКраткое саммари:")
    print(summary.short_summary)

    if output_path:
        exported_path = service.export_summary_to_markdown(summary, output_path)
        print(f"\nФайл сохранён: {exported_path}")


def run_extraction(file_path: str, user_request: str, output_path: str | None) -> None:
    service = DocumentService()
    extraction = service.extract_information(file_path, user_request)

    print("\nНайдено:")

    if extraction.items:
        for item in extraction.items:
            print(f"- {item.field}: {item.value}")
    else:
        print("- Ничего не найдено")

    if extraction.missing:
        print("\nНе найдено:")
        for item in extraction.missing:
            print(f"- {item}")

    if output_path:
        exported_path = service.export_extraction_to_markdown(
            extraction,
            output_path,
        )
        print(f"\nФайл сохранён: {exported_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    if args.command == "summary":
        run_summary(args.file, args.output)

    elif args.command == "extract":
        run_extraction(args.file, args.request, args.output)


if __name__ == "__main__":
    main()