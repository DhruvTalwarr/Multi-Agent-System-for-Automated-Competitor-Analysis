# competitor_analysis/critic_agent.py

class CriticAgent:

    def review_report(self, report: dict) -> dict:
        try:
            issues = []

            # ✅ Required sections
            required_sections = [
                "Executive Summary",
                "Competitor Comparison",
                "SWOT Analysis",
                "Risk Analysis",
                "Recommendations"
            ]

            for sec in required_sections:
                if sec not in report:
                    issues.append(f"Missing section: {sec}")

            # 📊 Validate comparison table
            comparison = report.get("Competitor Comparison", [])
            if not isinstance(comparison, list) or len(comparison) < 2:
                issues.append("Not enough companies for meaningful comparison")

            # 🧠 Validate SWOT
            swot = report.get("SWOT Analysis", {})
            if not all(k in swot for k in ["Strengths", "Weaknesses", "Opportunities", "Threats"]):
                issues.append("Incomplete SWOT Analysis")

            # ⚠️ Validate Risks
            risks = report.get("Risk Analysis", [])
            if not risks:
                issues.append("Risk Analysis is empty")

            # 💡 Improve Recommendations safely
            recommendations = report.get("Recommendations", [])
            if not isinstance(recommendations, list):
                recommendations = []

            if len(recommendations) < 3:
                recommendations.append("Enhance strategic recommendations with deeper insights")

            # Ensure updated recommendations go back
            report["Recommendations"] = recommendations

            # 📈 Add quality score
            score = max(0, 100 - (len(issues) * 20))

            return {
                "status": "Approved" if not issues else "Needs Improvement",
                "score": score,
                "issues": issues,
                "final_report": report
            }

        except Exception as e:
            return {
                "status": "Error",
                "message": str(e)
            }