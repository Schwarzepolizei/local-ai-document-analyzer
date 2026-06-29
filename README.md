# 📄 ETL Document Service + RAG

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![FAISS](https://img.shields.io/badge/FAISS-vector_search-orange)
![RAG](https://img.shields.io/badge/RAG-enabled-purple)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

Сервис для обработки документов разных форматов и построения поиска и ответов (RAG) поверх них.

---

## 🚀 Возможности

### 📥 Поддержка форматов
- PDF (native + OCR fallback)
- DOC / DOCX
- RTF
- XLSX (таблицы)
- TXT
- Изображения (OCR)

---

### ⚙️ ETL Pipeline
- Определение типа документа
- Извлечение текста (native / OCR)
- Очистка текста
- Разбиение на блоки (Block)
- Умный chunking (Chunk)
- Оценка качества (quality scoring)

---

### 🧠 RAG (Retrieval-Augmented Generation)
- Индексация документов
- Векторный поиск (FAISS)
- Фильтрация по:
  - `document_id`
  - `file_name`
- Генерация ответа на основе найденных чанков

---

## 🌐 API (FastAPI)

### 📌 Индексация документа
```bash
POST /rag/index
```

### 🔍 Поиск
```bash
POST /rag/search
```

### 💬 Вопрос к документам
```bash
POST /rag/ask
```

### 📄 Список документов
```bash
GET /rag/documents
```

### ❌ Удаление документа
```bash
DELETE /rag/document
```

### 🧹 Очистка индекса
```bash
DELETE /rag/index
```

## 🖥️ UI (Streamlit)
- Загрузка файлов
- Индексация
- Поиск
- Вопрос-ответ (RAG)
- Управление документами

## 🏗️ Архитектура
```bash
ETL Pipeline
   ↓
Blocks → Chunks
   ↓
Embeddings
   ↓
FAISS Index
   ↓
Retriever
   ↓
Answer Builder
```

## 📂 Структура проекта
```bash
app/
 ├── api/          # FastAPI роуты
 ├── parsers/      # Парсеры документов
 ├── pipeline/     # ETL pipeline
 ├── rag/          # RAG логика
 ├── schemas/      # Pydantic модели
 ├── services/     # OCR, cleaning, chunking
 └── utils/

ui.py              # Streamlit интерфейс
main.py            # FastAPI entrypoint
```

## Инженерные задачи и исследовательские решения

### 1. Проблема: Нативное извлечение PDF было ненадежным.

**Задача**

Многие PDF-документы содержали:
- битый text layer
- артефакты (, □, ■■)
- пустые страницы
- некорректный Unicode
- частично сканированные страницы

В результате semantic retrieval работал нестабильно.


**Решение**

Был реализован fallback pipeline:

```bash
Native PDF extraction
        ↓
Quality validation
        ↓
OCR fallback (if needed)
```

Система автоматически:

- проверяет наличие text layer
- оценивает объем текста
- анализирует подозрительные токены
- ищет PDF artifacts
- переключается на OCR при низком качестве

**Почему это важно**

Такой подход значительно повысил:

- recall retrieval системы
- стабильность эмбеддингов
- качество semantic search

### 2. Проблема: текст, полученный методом OCR, содержит шум.

**Задача**

Tesseract OCR создавал:

- мусорные токены
- обрывки строк
- некорректные символы
- Фрагментированные абзацы

Особенно на:

- сканах PDF
- старых DOC
- изображениях плохого качества


**Решение**

Был реализован отдельный OCR cleaning pipeline:

- image preprocessing
- OCR confidence filtering
- line merging
- paragraph reconstruction
- OCR noise filtering

**Результат**

Удалось значительно уменьшить количество:

- Низкокачественных чанков
- шум выборки


### 3. Проблема: Отсутствие прозрачности в отношении качества извлечения данных

**Задача**

Без quality scoring невозможно понять:

- насколько хорошо извлечен текст
- пригоден ли документ для retrieval
- нужен ли OCR fallback


**Решение**

Была реализована quality scoring system.

Система анализирует:

- достоверность распознавания текста
- подозрительные токены
- PDF артифакты
- пустые страницы
- содержание, напоминающее формулу


**Результат**

Каждая страница получает:

quality_score
quality_label

Это позволяет:

- фильтровать плохие документы
- анализировать extraction quality
- улучшать retrieval reliability


### 4. Почему FAISS 

Рассмотренные альтернативы:

- ChromaDB
- Qdrant
- Elasticsearch
- Pinecone

**FAISS**

FAISS был выбран потому что:

- чрезвычайно быстрый локальный векторный поиск
- низкие расходы паямти
- простая интеграция
- идеально подходит для прототипов и исследовательских систем.
- работает эффективно без внешней инфраструктуры.


**Компромиссы**

FAISS:

✅ быстрый
✅ простой
✅ локальный

Но:

❌ не распределённый
❌ нет встроенного уровня персистентности

---


## 🧪 Запуск локально

Перед локальным запуском необходимо заменить API_URL = "http://api:8000" в файле ui.py на API_URL = "http://127.0.0.1:8000"

1. Установка зависимостей
```bash
pip install -r requirements.txt
```

2. Запуск API
```bash
uvicorn main:app --reload
```

3. Запуск UI
```bash
streamlit run ui.py
```

## 🐳 Запуск через Docker
```bash
docker compose up --build
```

или

## 🐳 Запуск через Docker
```bash
docker-compose up --build
```

### После запуска:

API: http://localhost:8000/docs
UI: http://localhost:8501

## 🧠 Особенности реализации
- OCR fallback для PDF
- Quality scoring страниц
- Очистка шумных OCR-блоков
- Учет структуры документа (таблицы, заголовки)
- LLM-ready чанки (metadata, context)

## ⚠️ Ограничения
- Таблицы обрабатываются как строки
- Формулы извлекаются частично
- OCR зависит от качества изображения

## 🔮 Возможные улучшения
- Layout-aware parsing
- Улучшенный table extraction
- Кэширование эмбеддингов
- История диалогов
- Авторизация
- Деплой

## 🛠️ Стек
- FastAPI
- Streamlit
- FAISS
- sentence-transformers
- Tesseract OCR
- LibreOffice

# 👤 Автор

#### Александр — Data Scientist 