import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"



st.set_page_config(page_title="ETL + RAG", page_icon="📄", layout="wide")
st.title("📄 ETL + RAG интерфейс")


def show_error(response):
    try:
        st.error(response.json())
    except Exception:
        st.error(response.text)


tab_process, tab_index, tab_search, tab_ask, tab_docs = st.tabs(
    [
        "Обработка",
        "Индексация",
        "Поиск",
        "Вопрос-ответ",
        "Документы",
    ]
)


with tab_process:
    st.header("Обработка документа через /process")

    file = st.file_uploader(
        "Загрузи файл",
        type=["pdf", "docx", "doc", "xlsx", "txt", "rtf", "jpg", "jpeg", "png"],
        key="process_file",
    )

    if st.button("Обработать", disabled=file is None):
        with st.spinner("Обрабатываю документ..."):
            response = requests.post(
                f"{API_URL}/process",
                files={"file": (file.name, file.getvalue(), file.type)},
                timeout=300,
            )

        if response.status_code != 200:
            show_error(response)
        else:
            data = response.json()
            st.session_state["last_etl"] = data

            st.success("Документ обработан")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Тип", data["source"]["file_type"])
            col2.metric("Метод", data["document"]["extraction_method"])
            col3.metric("Страниц", data["document"]["page_count"])
            col4.metric("Quality", data["document"]["quality_score"])

            if data["processing"]["warnings"]:
                for warning in data["processing"]["warnings"]:
                    st.warning(warning)

            st.subheader("Статистика")
            st.json(data["processing"].get("stats", {}))

            st.subheader("Текст")
            st.text_area(
                "full_text",
                data["content"]["full_text"][:15000],
                height=300,
            )

            st.subheader("Первые chunks")
            for chunk in data["content"]["chunks"][:10]:
                title = (
                    f'{chunk["chunk_id"]} | '
                    f'{chunk.get("source_context")} | '
                    f'{chunk.get("content_type")}'
                )
                with st.expander(title):
                    st.write(chunk["text"])
                    st.json(
                        {
                            "page_span": chunk.get("page_span"),
                            "block_types": chunk.get("block_types"),
                            "token_estimate": chunk.get("token_estimate"),
                        }
                    )


with tab_index:
    st.header("Индексация документа через /rag/index")

    file = st.file_uploader(
        "Загрузи файл для индексации",
        type=["pdf", "docx", "doc", "xlsx", "txt", "rtf", "jpg", "jpeg", "png"],
        key="index_file",
    )

    if st.button("Добавить в RAG index", disabled=file is None):
        with st.spinner("Обрабатываю и индексирую..."):
            response = requests.post(
                f"{API_URL}/rag/index",
                files={"file": (file.name, file.getvalue(), file.type)},
                timeout=500,
            )

        if response.status_code != 200:
            show_error(response)
        else:
            st.success("Документ добавлен в индекс")
            st.json(response.json())

    st.divider()

    if st.button("Очистить весь индекс"):
        response = requests.delete(f"{API_URL}/rag/index", timeout=120)

        if response.status_code != 200:
            show_error(response)
        else:
            st.success("Индекс очищен")
            st.json(response.json())


with tab_search:
    st.header("Поиск по RAG через /rag/search")

    query = st.text_input("Запрос", key="search_query")
    top_k = st.slider("top_k", 1, 20, 5, key="search_top_k")

    col1, col2 = st.columns(2)
    document_id = col1.text_input("document_id фильтр", key="search_doc_id")
    file_name = col2.text_input("file_name фильтр", key="search_file_name")

    if st.button("Искать"):
        payload = {
            "query": query,
            "top_k": top_k,
            "document_id": document_id or None,
            "file_name": file_name or None,
        }

        with st.spinner("Ищу..."):
            response = requests.post(
                f"{API_URL}/rag/search",
                json=payload,
                timeout=120,
            )

        if response.status_code != 200:
            show_error(response)
        else:
            data = response.json()
            results = data.get("results", [])

            st.success(f"Найдено: {len(results)}")

            for i, item in enumerate(results, start=1):
                title = (
                    f'{i}. score={item.get("score")} | '
                    f'{item.get("file_name")} | '
                    f'{item.get("source_context")}'
                )
                with st.expander(title):
                    st.write(item.get("text"))
                    st.json(item)


with tab_ask:
    st.header("Вопрос-ответ через /rag/ask")

    query = st.text_input("Вопрос", key="ask_query")
    top_k = st.slider("top_k", 1, 20, 5, key="ask_top_k")

    col1, col2 = st.columns(2)
    document_id = col1.text_input("document_id фильтр", key="ask_doc_id")
    file_name = col2.text_input("file_name фильтр", key="ask_file_name")

    if st.button("Получить ответ"):
        payload = {
            "query": query,
            "top_k": top_k,
            "document_id": document_id or None,
            "file_name": file_name or None,
        }

        with st.spinner("Формирую ответ..."):
            response = requests.post(
                f"{API_URL}/rag/ask",
                json=payload,
                timeout=180,
            )

        if response.status_code != 200:
            show_error(response)
        else:
            data = response.json()

            st.subheader("Ответ")
            st.write(data.get("answer"))

            with st.expander("Контекст"):
                st.write(data.get("context"))

            with st.expander("Найденные chunks"):
                for item in data.get("results", []):
                    st.write(item.get("text"))
                    st.json(item)
                    st.divider()


with tab_docs:
    st.header("Документы в индексе")

    if st.button("Обновить список документов"):
        response = requests.get(f"{API_URL}/rag/documents", timeout=120)

        if response.status_code != 200:
            show_error(response)
        else:
            data = response.json()
            st.session_state["documents"] = data.get("documents", [])

    documents = st.session_state.get("documents", [])

    if documents:
        for i, doc in enumerate(documents):
            doc_id = doc.get("document_id", "no_id")
            file_name = doc.get("file_name", "unknown")
            unique_key = f"{doc_id}_{file_name}_{i}"

            with st.expander(file_name):
                st.json(doc)

                col1, col2 = st.columns(2)

                if col1.button(
                    "Удалить по document_id",
                    key=f"delete_doc_id_{unique_key}",
                ):
                    response = requests.delete(
                        f"{API_URL}/rag/document",
                        json={
                            "document_id": doc.get("document_id"),
                            "file_name": None,
                        },
                        timeout=120,
                    )

                    if response.status_code != 200:
                        show_error(response)
                    else:
                        st.success("Документ удалён")
                        st.json(response.json())

                if col2.button(
                    "Удалить по file_name",
                    key=f"delete_file_{unique_key}",
                ):
                    response = requests.delete(
                        f"{API_URL}/rag/document",
                        json={
                            "document_id": None,
                            "file_name": doc.get("file_name"),
                        },
                        timeout=120,
                    )

                    if response.status_code != 200:
                        show_error(response)
                    else:
                        st.success("Документ удалён")
                        st.json(response.json())
    else:
        st.info("Нажми «Обновить список документов»")