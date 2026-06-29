from fastapi import APIRouter, UploadFile, File

from app.pipeline.etl_pipeline import run_etl
from app.schemas.document import ETLResponse

router = APIRouter()


@router.post("/process", response_model=ETLResponse)
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    result = run_etl(file_name=file.filename, file_bytes=content)
    return result