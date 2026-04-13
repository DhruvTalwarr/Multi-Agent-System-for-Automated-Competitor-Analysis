from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum


class MarketRegion(str, Enum):
    india = "india"
    usa = "usa"
    europe = "europe"
    global_ = "global"
    southeast_asia = "southeast_asia"


# ── Request Models ────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="e.g. 'Analyze competitors in EV market in India'",
    )
    region: MarketRegion = Field(default=MarketRegion.india)
    max_competitors: int = Field(default=5, ge=2, le=10)
    include_swot: bool = Field(default=True)
    include_risk: bool = Field(default=True)

    @field_validator("query")
    @classmethod
    def query_must_be_meaningful(cls, v: str) -> str:
        if v.strip().lower() in ["test", "hello", "hi"]:
            raise ValueError("Please enter a real business query.")
        return v.strip()


class ReportRequest(BaseModel):
    query: str = Field(..., min_length=10, max_length=500)
    region: MarketRegion = Field(default=MarketRegion.india)
    format: str = Field(default="markdown", pattern="^(markdown|json)$")


# ── Response Models ───────────────────────────────────────────────────────────

class Competitor(BaseModel):
    name: str
    market_share: Optional[str] = None
    hq: Optional[str] = None
    key_products: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []


class SwotAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]


class RiskItem(BaseModel):
    risk: str
    severity: str  # low | medium | high
    mitigation: str


class AnalyzeResponse(BaseModel):
    query: str
    region: str
    competitors: List[Competitor]
    swot: Optional[SwotAnalysis] = None
    risks: Optional[List[RiskItem]] = None
    status: str = "success"


class ReportResponse(BaseModel):
    title: str
    summary: str
    competitor_table: str
    swot_summary: str
    risk_analysis: str
    strategic_recommendation: str
    status: str = "success"


class ErrorResponse(BaseModel):
    detail: str
    code: str
    status: str = "error"
