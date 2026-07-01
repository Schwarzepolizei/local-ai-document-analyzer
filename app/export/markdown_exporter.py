from pathlib import Path

from app.schemas.extraction import ExtractionResult
from app.schemas.summary import SummaryResult


class MarkdownExporter:
    def export_summary(self, summary: SummaryResult, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = self._build_summary_markdown(summary)
        path.write_text(content, encoding="utf-8")

        return path

    def export_extraction(
        self,
        extraction: ExtractionResult,
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = self._build_extraction_markdown(extraction)
        path.write_text(content, encoding="utf-8")

        return path

    def _build_summary_markdown(self, summary: SummaryResult) -> str:
        lines = [
            f"# Саммари документа: {summary.file_name}",
            "",
            "## Ключевая мысль",
            summary.key_idea,
            "",
            "## Краткое саммари",
            summary.short_summary,
            "",
            "## Подробное саммари",
            summary.detailed_summary,
            "",
            "## Разделы / фрагменты",
            "",
        ]

        for section in summary.sections:
            pages = (
                ", ".join(map(str, section.pages)) if section.pages else "не указано"
            )

            lines.extend(
                [
                    f"### {section.title}",
                    f"**Страницы:** {pages}",
                    "",
                    f"**Главная мысль:** {section.main_idea}",
                    "",
                    section.summary,
                    "",
                ]
            )

        lines.extend(
            [
                "## Важные факты",
                "",
            ]
        )

        if summary.important_facts:
            for fact in summary.important_facts:
                lines.append(f"- {fact}")
        else:
            lines.append("- Не указано")

        lines.extend(
            [
                "",
                "## Предупреждения качества",
                "",
            ]
        )

        if summary.quality_warnings:
            for warning in summary.quality_warnings:
                lines.append(f"- {warning}")
        else:
            lines.append("- Нет предупреждений")

        return "\n".join(lines)

    def _build_extraction_markdown(self, extraction: ExtractionResult) -> str:
        lines = [
            f"# Извлечение информации: {extraction.file_name}",
            "",
            "## Запрос пользователя",
            extraction.request,
            "",
            "## Найдено",
            "",
        ]

        if extraction.items:
            for item in extraction.items:
                lines.extend(
                    [
                        f"### {item.field}",
                        f"**Значение:** {item.value}",
                    ]
                )

                if item.source:
                    lines.append(f"**Источник:** {item.source}")

                if item.confidence:
                    lines.append(f"**Уверенность:** {item.confidence}")

                lines.append("")
        else:
            lines.append("Данные не найдены.")
            lines.append("")

        lines.extend(
            [
                "## Не найдено",
                "",
            ]
        )

        if extraction.missing:
            for item in extraction.missing:
                lines.append(f"- {item}")
        else:
            lines.append("- Нет")

        lines.extend(
            [
                "",
                "## Примечания",
                "",
            ]
        )

        if extraction.notes:
            for note in extraction.notes:
                lines.append(f"- {note}")
        else:
            lines.append("- Нет")

        return "\n".join(lines)
