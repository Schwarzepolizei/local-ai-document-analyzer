from app.agent.local_llm import LocalLLM
from app.agent.parsers.summary_response_parser import SummaryResponseParser
from app.prompts.summary_prompt import SummaryPrompt
from app.schemas.document import ETLResponse
from app.schemas.summary import SectionSummary, SummaryResult


class Summarizer:
    def __init__(
        self,
        llm: LocalLLM | None = None,
        response_parser: SummaryResponseParser | None = None,
    ) -> None:
        self.llm = llm or LocalLLM()
        self.response_parser = response_parser or SummaryResponseParser()

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

        prompt = SummaryPrompt.build(text)
        llm_text = self.llm.generate(prompt)

        return SummaryResult(
            document_id=document.document_id,
            file_name=document.source.file_name,
            key_idea=self.response_parser.extract_section(llm_text, "Ключевая мысль"),
            short_summary=self.response_parser.extract_section(
                llm_text,
                "Краткое саммари",
            ),
            detailed_summary=self.response_parser.extract_section(
                llm_text,
                "Подробное саммари",
            ),
            sections=self._build_section_summaries(document),
            important_facts=self.response_parser.extract_list(llm_text, "Важные факты"),
            quality_warnings=document.processing.warnings,
        )

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
