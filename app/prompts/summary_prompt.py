class SummaryPrompt:
    @staticmethod
    def build(text: str, max_chars: int = 12000) -> str:
        document_text = text[:max_chars]

        return f"""
Ты — локальный AI-агент для анализа документов.

Сделай саммари документа на русском языке.

Ответь строго в таком формате:

Ключевая мысль:
...

Краткое саммари:
...

Подробное саммари:
...

Важные факты:
- ...
- ...
- ...

Документ:
{document_text}
"""
