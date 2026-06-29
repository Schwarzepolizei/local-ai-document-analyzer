import json

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.pipeline.etl_pipeline import run_etl
from app.rag.answer_builder import AnswerBuilder
from app.rag.document_manager import DocumentManager
from app.rag.index_builder import IndexBuilder
from app.rag.index_store import FaissIndexStore
from app.rag.retriever import Retriever
from app.schemas.rag import (
    SearchRequest,
    SearchResponse,
    IndexResponse,
    AskRequest,
    AskResponse,
    DocumentsResponse,
    DeleteDocumentRequest,
    DeleteDocumentResponse,
)


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index", response_model=IndexResponse)
async def index_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        etl_response = run_etl(file.filename, file_bytes)
        etl_dict = etl_response.model_dump()

        if etl_dict["processing"]["status"] != "success":
            raise HTTPException(status_code=400, detail=etl_dict["processing"]["errors"])

        builder = IndexBuilder()
        result = builder.build_from_etl_response(etl_dict)
        return IndexResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        retriever = Retriever()
        results = retriever.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            file_name=request.file_name,
        )

        return SearchResponse(
            query=request.query,
            top_k=request.top_k,
            results=results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/index")
async def clear_index():
    try:
        store = FaissIndexStore()
        store.clear()
        return {"status": "success", "message": "Index cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    try:
        retriever = Retriever()
        results = retriever.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            file_name=request.file_name,
        )

        answer_builder = AnswerBuilder()
        context = answer_builder.build_context(results)
        answer = answer_builder.build_answer(request.query, results)

        return AskResponse(
            query=request.query,
            answer=answer,
            context=context,
            results=results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/documents", response_model=DocumentsResponse)
async def list_documents():
    try:
        store = FaissIndexStore()
        documents = store.list_documents()
        return DocumentsResponse(documents=documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/document", response_model=DeleteDocumentResponse)
async def delete_document(request: DeleteDocumentRequest):
    try:
        manager = DocumentManager()
        result = manager.delete_document(
            document_id=request.document_id,
            file_name=request.file_name,
        )
        return DeleteDocumentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))