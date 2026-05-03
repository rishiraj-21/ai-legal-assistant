import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    if not request.issue or len(request.issue.strip()) < 10:
        raise HTTPException(status_code=400, detail="Issue description must be at least 10 characters.")

    logger.info("Analyze request: case_type=%s, issue_length=%d", request.case_type, len(request.issue))
    result = await rag_service.analyze(request.issue, request.case_type)
    return result
