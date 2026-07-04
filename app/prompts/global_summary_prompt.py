class GlobalSummaryPrompt:
    @staticmethod
    def build(section_summaries: str) -> str:
        return f"""
Ты — локальный AI-агент для анализа документов.

Ниже даны саммари разделов одного документа.
Собери из них итоговое саммари всего документа.

Ответь только валидным JSON без Markdown.

Схема:
{{
  "key_idea": "...",
  "short_summary": "...",
  "detailed_summary": "...",
  "important_facts": ["...", "..."]
}}

Саммари разделов:
{section_summaries}
""".strip()