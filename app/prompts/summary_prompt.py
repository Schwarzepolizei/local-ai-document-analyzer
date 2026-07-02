class SummaryPrompt:
    @staticmethod
    def build(text: str, max_chars: int = 12000) -> str:
        document_text = text[:max_chars]

        return f"""
Ты — локальный AI-агент для анализа документов.

Сделай саммари документа на русском языке.

Ответь только валидным JSON без Markdown.

Схема:
{{
  "key_idea": "...",
  "short_summary": "...",
  "detailed_summary": "...",
  "important_facts": ["...", "..."]
}}

Документ:
{document_text}
"""
