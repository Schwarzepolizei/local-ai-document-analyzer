from app.agent.local_llm import LocalLLM
from app.schemas.document import ETLResponse


class Summarizer:
    def __init__(self, llm: LocalLLM | None = None) -> None:
        self.llm = llm or LocalLLM()

    def summarize(self, document: ETLResponse) -> str:
        text = document.content.full_text.strip()

        if not text:
            return "Текст документа не найден."

        prompt = f"""
Ты — локальный AI-агент для анализа документов.

Сделай полное саммари документа на русском языке.

Структура ответа:
1. Ключевая мысль
2. Краткое саммари
3. Основные пункты
4. Важные детали
5. Возможные ограничения качества извлечения

Документ:
{text[:12000]}
"""

        return self.llm.generate(prompt)