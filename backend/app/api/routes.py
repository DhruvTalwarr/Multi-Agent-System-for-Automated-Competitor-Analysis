from fastapi import APIRouter, HTTPException
from app.core.schemas import (
    AnalyzeRequest, AnalyzeResponse,
    ReportRequest, ReportResponse,
    ErrorResponse,
)
from app.agents.orchestrator import run_analysis, run_report

router = APIRouter(prefix="/api/v1", tags=["intelligence"])


# ── POST /analyze ─────────────────────────────────────────────────────────────
@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Run competitor & market analysis",
)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return await run_analysis(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /report ──────────────────────────────────────────────────────────────
@router.post(
    "/report",
    response_model=ReportResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Generate formatted intelligence report",
)
async def report(request: ReportRequest) -> ReportResponse:
    try:
        return await run_report(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /health ───────────────────────────────────────────────────────────────
@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "SBDA Backend"}
