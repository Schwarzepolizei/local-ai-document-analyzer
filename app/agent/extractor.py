from app.agent.local_llm import LocalLLM
from app.agent.parsers.extraction_response_parser import ExtractionResponseParser
from app.prompts.extraction_prompt import ExtractionPrompt
from app.schemas.document import ETLResponse
from app.schemas.extraction import ExtractionResult


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
                missing=["Текст документа не найден."],
            )

        prompt = ExtractionPrompt.build(
            text=text,
            user_request=user_request,
        )

        llm_text = self.llm.generate(prompt)

        return ExtractionResult(
            document_id=document.document_id,
            file_name=document.source.file_name,
            request=user_request,
            items=self.response_parser.parse_items(llm_text),
            missing=self.response_parser.parse_missing(llm_text),
            notes=self.response_parser.parse_notes(llm_text),
        )