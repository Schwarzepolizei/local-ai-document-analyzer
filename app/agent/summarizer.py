from pydantic import ValidationError

from app.agent.local_llm import LocalLLM
from app.agent.parsers.summary_response_parser import SummaryResponseParser
from app.agent.summary_strategy import SummaryStrategy, SummaryStrategySelector
from app.prompts.global_summary_prompt import GlobalSummaryPrompt
from app.prompts.section_summary_prompt import SectionSummaryPrompt
from app.prompts.summary_prompt import SummaryPrompt
from app.schemas.document import ETLResponse
from app.schemas.summary import (
    SectionSummary,
    SectionSummaryLLMResponse,
    SummaryLLMResponse,
    SummaryResult,
)
from app.services.document_structure import DocumentStructureBuilder
from app.utils.logger import logger


class Summarizer:
    def __init__(
        self,
        llm: LocalLLM | None = None,
        response_parser: SummaryResponseParser | None = None,
        structure_builder: DocumentStructureBuilder | None = None,
        strategy_selector: SummaryStrategySelector | None = None,
    ) -> None:
        self.llm = llm or LocalLLM()
        self.response_parser = response_parser or SummaryResponseParser()
        self.structure_builder = structure_builder or DocumentStructureBuilder()
        self.strategy_selector = strategy_selector or SummaryStrategySelector()

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

        strategy = self.strategy_selector.select(text)
        estimated_tokens = self.strategy_selector.estimate_tokens(text)

        logger.info(
            "Summary strategy selected: %s | estimated_tokens=%s",
            strategy.value,
            estimated_tokens,
        )

        if strategy == SummaryStrategy.SMALL:
            return self._summarize_small_document(document=document, text=text)

        return self._summarize_map_reduce(document=document, text=text)

    def _summarize_small_document(
        self,
        document: ETLResponse,
        text: str,
    ) -> SummaryResult:
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

        sections = self._build_section_summaries_without_llm(document)

        return SummaryResult(
            document_id=document.document_id,
            file_name=document.source.file_name,
            key_idea=key_idea,
            short_summary=short_summary,
            detailed_summary=detailed_summary,
            sections=sections,
            important_facts=important_facts,
            quality_warnings=document.processing.warnings,
        )

    def _summarize_map_reduce(
        self,
        document: ETLResponse,
        text: str,
    ) -> SummaryResult:
        section_summaries = self._build_section_summaries_from_structure(document)

        if len(section_summaries) == 1:
            logger.info("Using single section summary as global summary")

            section_summary = section_summaries[0]

            return SummaryResult(
                document_id=document.document_id,
                file_name=document.source.file_name,
                key_idea=section_summary.main_idea,
                short_summary=section_summary.summary,
                detailed_summary=section_summary.summary,
                sections=section_summaries,
                important_facts=[],
                quality_warnings=document.processing.warnings,
            )

        logger.info(
            "Building global summary from %s section summaries",
            len(section_summaries),
        )

        global_prompt = GlobalSummaryPrompt.build(
            section_summaries=self._format_section_summaries_for_global_prompt(
                section_summaries,
            )
        )

        try:
            llm_json = self.llm.generate_json(global_prompt, temperature=0.2)
            parsed = SummaryLLMResponse.model_validate(llm_json)

            key_idea = parsed.key_idea
            short_summary = parsed.short_summary
            detailed_summary = parsed.detailed_summary
            important_facts = parsed.important_facts

        except (ValueError, ValidationError, AttributeError):
            prompt = SummaryPrompt.build(text)
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
            sections=section_summaries,
            important_facts=important_facts,
            quality_warnings=document.processing.warnings,
        )

    def _build_section_summaries_from_structure(
        self,
        document: ETLResponse,
    ) -> list[SectionSummary]:
        section_summaries: list[SectionSummary] = []
        document_sections = self.structure_builder.build(document)

        logger.info("Document sections detected: %s", len(document_sections))

        for index, section in enumerate(document_sections, start=1):
            logger.info(
                "Summarizing section %s/%s: %s",
                index,
                len(document_sections),
                section.title,
            )

            section_text = section.text.strip()

            if not section_text:
                continue

            prompt = SectionSummaryPrompt.build(
                title=section.title,
                text=section_text,
            )

            try:
                llm_json = self.llm.generate_json(prompt, temperature=0.2)
                parsed = SectionSummaryLLMResponse.model_validate(llm_json)

                main_idea = parsed.main_idea
                summary = parsed.summary

            except (ValueError, ValidationError, AttributeError):
                main_idea = section_text[:250]
                summary = section_text[:500]

            section_summaries.append(
                SectionSummary(
                    title=section.title,
                    pages=section.pages,
                    main_idea=main_idea,
                    summary=summary,
                )
            )

        return section_summaries

    def _build_section_summaries_without_llm(
        self,
        document: ETLResponse,
    ) -> list[SectionSummary]:
        section_summaries: list[SectionSummary] = []

        for section in self.structure_builder.build(document):
            section_text = section.text.strip()

            if not section_text:
                continue

            section_summaries.append(
                SectionSummary(
                    title=section.title,
                    pages=section.pages,
                    main_idea=section_text[:250],
                    summary=section_text[:500],
                )
            )

        return section_summaries

    def _format_section_summaries_for_global_prompt(
        self,
        section_summaries: list[SectionSummary],
    ) -> str:
        parts: list[str] = []

        for index, section in enumerate(section_summaries, start=1):
            pages = ", ".join(str(page) for page in section.pages) or "не указаны"

            parts.append(
                "\n".join(
                    [
                        f"Раздел {index}: {section.title}",
                        f"Страницы: {pages}",
                        f"Главная мысль: {section.main_idea}",
                        f"Саммари: {section.summary}",
                    ]
                )
            )

        return "\n\n".join(parts)