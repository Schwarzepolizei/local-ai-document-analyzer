from app.agent.local_llm import LocalLLM
from app.schemas.document import ETLResponse
from app.schemas.summary import SectionSummary, SummaryResult


class Summarizer:
    def __init__(self, llm: LocalLLM | None = None) -> None:
        self.llm = llm or LocalLLM()

    def summarize(self, document: ETLResponse) -> SummaryResult:
        text = document.content.full_text.strip()

        if not text:
            return SummaryResult(
                document_id=document.document_id,
                file_name=document.source.file_name,
                key_idea="Текст документа не найден.",
                short_summary="Саммари невозможно сформировать.",
                detailed_summary="Документ не содержит извлечённого текста.",
                quality_warnings=document.processing.warnings,
            )

        llm_text = self._summarize_text(text)

        return SummaryResult(
            document_id=document.document_id,
            file_name=document.source.file_name,
            key_idea=self._extract_section(llm_text, "Ключевая мысль"),
            short_summary=self._extract_section(llm_text, "Краткое саммари"),
            detailed_summary=self._extract_section(llm_text, "Подробное саммари"),
            sections=self._build_section_summaries(document),
            important_facts=self._extract_list(llm_text, "Важные факты"),
            quality_warnings=document.processing.warnings,
        )

    def _summarize_text(self, text: str) -> str:
        prompt = f"""
Ты — локальный AI-агент для анализа документов.

Сделай саммари документа на русском языке.

Ответь строго в таком формате:

Ключевая мысль:
...

Краткое саммари:
...

Подробное саммари:
...

Важные факты:
- ...
- ...
- ...

Документ:
{text[:12000]}
"""

        return self.llm.generate(prompt)

    def _build_section_summaries(self, document: ETLResponse) -> list[SectionSummary]:
        sections: list[SectionSummary] = []

        for chunk in document.content.chunks[:10]:
            title = chunk.section_title or f"Фрагмент {chunk.chunk_order}"

            sections.append(
                SectionSummary(
                    title=title,
                    pages=chunk.page_span,
                    main_idea=chunk.text[:250],
                    summary=chunk.text[:500],
                )
            )

        return sections

    def _extract_section(self, text: str, title: str) -> str:
        marker = f"{title}:"

        if marker not in text:
            return ""

        after = text.split(marker, 1)[1]

        possible_next_markers = [
            "Ключевая мысль:",
            "Краткое саммари:",
            "Подробное саммари:",
            "Важные факты:",
        ]

        for next_marker in possible_next_markers:
            if next_marker != marker and next_marker in after:
                after = after.split(next_marker, 1)[0]

        return after.strip()

    def _extract_list(self, text: str, title: str) -> list[str]:
        section = self._extract_section(text, title)

        items = []

        for line in section.splitlines():
            line = line.strip()

            if line.startswith("-"):
                items.append(line.removeprefix("-").strip())

        return items