# competitor_analysis/report_generator.py

class ReportGeneratorAgent:

    def generate_report(self, research_data: dict) -> dict:
        try:
            companies = research_data.get("companies", [])

            if not companies:
                raise ValueError("No company data available")

            # 📊 Comparison Table
            table = []
            for c in companies:
                table.append({
                    "Name": c.get("name", "N/A"),
                    "Revenue (B$)": c.get("revenue", "N/A"),
                    "Market Share (%)": c.get("market_share", "N/A"),
                    "Growth Rate (%)": c.get("growth_rate", "N/A")
                })

            # 🧠 SWOT Analysis
            swot = {
                "Strengths": [c.get("strength", "N/A") for c in companies],
                "Weaknesses": [c.get("weakness", "N/A") for c in companies],
                "Opportunities": [
                    "Market expansion",
                    "Technological innovation",
                    "Emerging markets"
                ],
                "Threats": [
                    "High competition",
                    "Economic slowdown",
                    "Regulatory risks"
                ]
            }

            # ⚠️ Risk Analysis
            risks = [
                "Market volatility",
                "Supply chain disruptions",
                "Regulatory changes",
                "Technological disruption"
            ]

            # 💡 Recommendations
            recommendations = [
                "Invest in innovation and R&D",
                "Expand into new markets",
                "Optimize operational costs",
                "Strengthen digital presence"
            ]

            return {
                "status": "success",
                "Executive Summary": f"Analysis of {len(companies)} companies completed successfully.",
                "Competitor Comparison": table,
                "SWOT Analysis": swot,
                "Risk Analysis": risks,
                "Recommendations": recommendations
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }