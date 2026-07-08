class SummaryPrompt:
    @staticmethod
    def build(text: str) -> str:
        return f"""
Ты — локальный AI-агент для анализа документов.

Сделай краткое саммари документа.

Ответь только валидным JSON без Markdown.
Пиши кратко.
Не больше 1 предложения на поле.
important_facts: максимум 5 пунктов.

Схема:
{{
  "key_idea": "...",
  "short_summary": "...",
  "detailed_summary": "...",
  "important_facts": ["...", "..."]
}}

Текст документа:
{text}
""".strip()