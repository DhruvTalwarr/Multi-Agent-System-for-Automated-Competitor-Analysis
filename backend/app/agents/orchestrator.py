"""
Placeholder orchestrator.
The agent team replaces these functions with real LangGraph agents.
The FastAPI layer (routes.py) never needs to change.
"""
from app.core.schemas import (
    AnalyzeRequest, AnalyzeResponse,
    ReportRequest, ReportResponse,
    Competitor, SwotAnalysis, RiskItem,
)


async def run_analysis(request: AnalyzeRequest) -> AnalyzeResponse:
    # TODO: Agent team wires LangGraph pipeline here
    return AnalyzeResponse(
        query=request.query,
        region=request.region.value,
        competitors=[
            Competitor(
                name="Tata Motors EV",
                market_share="12%",
                hq="Mumbai, India",
                key_products=["Nexon EV", "Tiago EV"],
                strengths=["Strong brand", "Wide network"],
                weaknesses=["Battery dependency"],
            ),
            Competitor(
                name="Ola Electric",
                market_share="21%",
                hq="Bengaluru, India",
                key_products=["S1 Pro", "S1 Air"],
                strengths=["Aggressive pricing", "App-first"],
                weaknesses=["Service issues"],
            ),
        ],
        swot=SwotAnalysis(
            strengths=["Growing EV demand", "Govt subsidies"],
            weaknesses=["Charging infra gaps", "High upfront cost"],
            opportunities=["Fleet electrification", "Export potential"],
            threats=["Chinese OEMs", "Subsidy uncertainty"],
        ) if request.include_swot else None,
        risks=[
            RiskItem(risk="Battery supply chain", severity="high", mitigation="Multi-supplier strategy"),
            RiskItem(risk="Price competition", severity="medium", mitigation="Differentiate on service"),
        ] if request.include_risk else None,
    )


async def run_report(request: ReportRequest) -> ReportResponse:
    # TODO: Agent team wires LangGraph pipeline here
    analyze_req = AnalyzeRequest(
        query=request.query,
        region=request.region,
    )
    analysis = await run_analysis(analyze_req)

    header = "| Company | Market Share | HQ | Products |\n|---|---|---|---|\n"
    rows = "\n".join(
        f"| {c.name} | {c.market_share} | {c.hq} | {', '.join(c.key_products)} |"
        for c in analysis.competitors
    )

    return ReportResponse(
        title=f"Market Intelligence: {request.query}",
        summary=f"Analysis of {len(analysis.competitors)} competitors in {request.region.value} market.",
        competitor_table=header + rows,
        swot_summary=str(analysis.swot.model_dump()) if analysis.swot else "N/A",
        risk_analysis="\n".join(f"[{r.severity.upper()}] {r.risk}" for r in (analysis.risks or [])),
        strategic_recommendation="Focus on tier-2 cities, charging infra, and software differentiation.",
    )
