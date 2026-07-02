from pydantic import BaseModel


class SectionSummary(BaseModel):
    title: str
    pages: list[int] = []
    main_idea: str
    summary: str


class SummaryResult(BaseModel):
    document_id: str
    file_name: str
    key_idea: str
    short_summary: str
    detailed_summary: str
    sections: list[SectionSummary] = []
    important_facts: list[str] = []
    quality_warnings: list[str] = []


class SummaryLLMResponse(BaseModel):
    key_idea: str = ""
    short_summary: str = ""
    detailed_summary: str = ""
    important_facts: list[str] = []
