from pydantic import ValidationError

from app.agent.local_llm import LocalLLM
from app.agent.parsers.summary_response_parser import SummaryResponseParser
from app.prompts.summary_prompt import SummaryPrompt
from app.schemas.document import ETLResponse
from app.schemas.summary import SectionSummary, SummaryLLMResponse, SummaryResult


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
                sections=[],
                important_facts=[],
                quality_warnings=document.processing.warnings,
            )

        prompt = SummaryPrompt.build(text)

        try:
            llm_json = self.llm.generate_json(prompt, temperature=0.2)
            parsed = SummaryLLMResponse.model_validate(llm_json)

            key_idea = parsed.key_idea
            short_summary = parsed.short_summary
            detailed_summary = parsed.detailed_summary
            important_facts = parsed.important_facts

        except (ValueError, ValidationError, AttributeError):
            llm_text = self.llm.generate(prompt)

            key_idea = self.response_parser.extract_section(
                llm_text,
                "Ключевая мысль",
            )
            short_summary = self.response_parser.extract_section(
                llm_text,
                "Краткое саммари",
            )
            detailed_summary = self.response_parser.extract_section(
                llm_text,
                "Подробное саммари",
            )
            important_facts = self.response_parser.extract_list(
                llm_text,
                "Важные факты",
            )

        return SummaryResult(
            document_id=document.document_id,
            file_name=document.source.file_name,
            key_idea=key_idea,
            short_summary=short_summary,
            detailed_summary=detailed_summary,
            sections=self._build_section_summaries(document),
            important_facts=important_facts,
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
