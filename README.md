# 📄 ETL Document Service + RAG

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![FAISS](https://img.shields.io/badge/FAISS-vector_search-orange)
![RAG](https://img.shields.io/badge/RAG-enabled-purple)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

# Local AI Document Analyzer

Локальный AI-агент для анализа документов.

Приложение позволяет загружать документы, извлекать из них текст, формировать саммари и извлекать нужную пользователю информацию с помощью локальной LLM через Ollama.

## Возможности

- обработка документов PDF, DOCX, DOC, TXT, RTF, XLSX и изображений;
- OCR для сканов и изображений;
- очистка текста;
- разбиение документа на блоки и фрагменты;
- оценка качества извлечения текста;
- локальное саммари документа;
- извлечение информации по пользовательскому запросу;
- экспорт результатов в Markdown;
- работа без облачных API.

## Стек

- Python 3.12
- Poetry
- FastAPI
- PySide6 planned
- Ollama
- Qwen2.5 / Qwen3
- FAISS
- sentence-transformers
- Tesseract OCR
- PyMuPDF
- pdfplumber
- python-docx

## Установка

```bash
git clone <repository-url>
cd AI_agent_document_service
poetry install
```

## Настройка Ollama

### Установить Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Скачать модель:

```bash
ollama pull qwen2.5:7b-instruct
```

### Проверить запуск:

```bash
ollama run qwen2.5:7b-instruct
```

## Запуск

### Проверка CLI:

```bash
poetry run python main.py --help
```

### Саммари документа

```bash
poetry run python main.py summary data/raw/test.txt
```

### С экспортом:

```bash
poetry run python main.py summary data/raw/test.txt -o data/processed/test_summary.md
```

### Извлечение информации

```bash
poetry run python main.py extract data/raw/test.txt "Извлеки цель документа и основные возможности агента"
```

### С экспортом:

```bash
poetry run python main.py extract data/raw/test.txt "Извлеки цель документа и основные возможности агента" -o data/processed/test_extraction.md
```

### Форматирование и проверка кода

```bash
poetry run black app main.py
poetry run ruff check app main.py --fix
```

## Структура проекта

```bash
app/
├── agent/
│   ├── local_llm.py
│   ├── summarizer.py
│   ├── extractor.py
│   └── parsers/
├── api/
├── config/
├── desktop/
├── export/
├── parsers/
├── pipeline/
├── prompts/
├── rag/
├── schemas/
├── services/
└── utils/
```

## Основные команды Poetry

### Установить зависимость:

```bash
poetry add package-name
```

### Установить dev-зависимость:

```bash
poetry add --group dev package-name
```

### Запустить команду внутри окружения:

```bash
poetry run python main.py
```

### Обновить lock-файл:

```bash
poetry lock
```

## Статус проекта

### Текущий этап:

- настроено Poetry-окружение;
- подключен существующий ETL pipeline;
- добавлен локальный LLM-клиент;
- добавлен модуль саммари;
- добавлен модуль извлечения информации;
- добавлен экспорт в Markdown;
- добавлен CLI.

### Следующие этапы:

- Добавить JSON-режим ответов LLM.
- Улучшить саммари больших документов.
- Добавить Document Structure Builder.
- Добавить PySide6 desktop GUI.
- Добавить экспорт в DOCX.
- Подготовить сборку приложения.

# 👤 Автор

#### Александр — Data Scientist 