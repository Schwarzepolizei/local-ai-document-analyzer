from pydantic import ValidationError

from app.agent.local_llm import LocalLLM
from app.agent.parsers.extraction_response_parser import ExtractionResponseParser
from app.prompts.extraction_prompt import ExtractionPrompt
from app.schemas.document import ETLResponse
from app.schemas.extraction import ExtractionLLMResponse, ExtractionResult


class Extractor:
    def __init__(
        self,
        llm: LocalLLM | None = None,
        response_parser: ExtractionResponseParser | None = None,
    ) -> None:
        self.llm = llm or LocalLLM()
        self.response_parser = response_parser or ExtractionResponseParser()

    def extract(self, document: ETLResponse, user_request: str) -> ExtractionResult:
        text = document.content.full_text.strip()

        if not text:
            return ExtractionResult(
                document_id=document.document_id,
                file_name=document.source.file_name,
                request=user_request,
                items=[],
                missing=["Текст документа не найден."],
                notes=[],
            )

        prompt = ExtractionPrompt.build(
            text=text,
            user_request=user_request,
        )

        try:
            llm_json = self.llm.generate_json(prompt, temperature=0.0)
            parsed = ExtractionLLMResponse.model_validate(llm_json)

            items = parsed.items
            missing = parsed.missing
            notes = parsed.notes

        except (ValueError, ValidationError, AttributeError):
            llm_text = self.llm.generate(prompt)

            items = self.response_parser.parse_items(llm_text)
            missing = self.response_parser.parse_missing(llm_text)
            notes = self.response_parser.parse_notes(llm_text)

        return ExtractionResult(
            document_id=document.document_id,
            file_name=document.source.file_name,
            request=user_request,
            items=items,
            missing=missing,
            notes=notes,
        )