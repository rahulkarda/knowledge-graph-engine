import io
import tempfile
import os

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ingest import NoteIngest, UrlIngest, IngestResponse
from app.services.ingestion.text_processor import TextProcessor
from app.services.ingestion.file_processor import FileProcessor
from app.services.ingestion.url_scraper import UrlScraper
from app.services.ingestion.audio_processor import AudioProcessor

router = APIRouter()

text_processor = TextProcessor()
file_processor = FileProcessor()
url_scraper = UrlScraper()
audio_processor = AudioProcessor()


@router.post("/note", response_model=IngestResponse)
async def ingest_note(payload: NoteIngest, db: AsyncSession = Depends(get_db)):
    return await text_processor.process(
        title=payload.title,
        content=payload.content,
        content_type="note",
        db=db,
    )


@router.post("/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    filename = file.filename or "upload"
    content_bytes = await file.read()

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    if ext not in ("pdf", "docx", "txt"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT.")

    title, text = file_processor.extract(filename, content_bytes)
    return await text_processor.process(
        title=title,
        content=text,
        content_type=ext,
        db=db,
        file_path=filename,
    )


@router.post("/url", response_model=IngestResponse)
async def ingest_url(payload: UrlIngest, db: AsyncSession = Depends(get_db)):
    title, text = await url_scraper.scrape(payload.url)
    if payload.title:
        title = payload.title
    return await text_processor.process(
        title=title,
        content=text,
        content_type="url",
        db=db,
        source_url=payload.url,
    )


@router.post("/audio", response_model=IngestResponse)
async def ingest_audio(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    audio_bytes = await file.read()
    filename = file.filename or "audio.wav"

    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1] or ".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        title, transcript = audio_processor.transcribe(tmp_path, filename)
    finally:
        os.unlink(tmp_path)

    return await text_processor.process(
        title=title,
        content=transcript,
        content_type="audio",
        db=db,
    )
