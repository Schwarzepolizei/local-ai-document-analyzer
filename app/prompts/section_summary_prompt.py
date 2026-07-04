class SectionSummaryPrompt:
    @staticmethod
    def build(title: str, text: str) -> str:
        return f"""
Ты — локальный AI-агент для анализа документов.

Проанализируй один раздел документа.

Название раздела:
{title}

Ответь только валидным JSON без Markdown.

Схема:
{{
  "main_idea": "...",
  "summary": "..."
}}

Текст раздела:
{text}
""".strip()