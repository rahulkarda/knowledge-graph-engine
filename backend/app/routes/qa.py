from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.qa import QARequest, QAResponse

router = APIRouter()


@router.post("/ask", response_model=QAResponse)
async def ask_question(payload: QARequest, db: AsyncSession = Depends(get_db)):
    from app.services.qa_service import QAService
    qa = QAService()
    return await qa.answer(payload.question, payload.top_k, db)
