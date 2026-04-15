# main.py

import json
import traceback

from competitor_analysis.planner_agent import PlannerAgent
from competitor_analysis.research_agent import ResearchAgent
from competitor_analysis.report_generator import ReportGeneratorAgent
from competitor_analysis.critic_agent import CriticAgent


def run_analysis(query: str) -> dict:
    try:
        print("\n🚀 Starting Multi-Agent Competitor Analysis...\n")

        # Initialize agents
        planner = PlannerAgent()
        research = ResearchAgent()
        report_generator = ReportGeneratorAgent()
        critic = CriticAgent()

        # Step 1: Planning
        print("🧠 Planner Agent working...")
        plan = planner.create_plan(query)

        if not plan or plan.get("status") == "error":
            raise ValueError("Planner failed")

        # Step 2: Research
        print("🔍 Research Agent gathering data...")
        research_data = research.gather_data(plan)

        if not research_data or research_data.get("status") != "success":
            raise ValueError("Research failed")

        # Step 3: Report Generation
        print("📊 Generating report...")
        report = report_generator.generate_report(research_data)

        if not report or report.get("status") != "success":
            raise ValueError("Report generation failed")

        # Step 4: Critic Review
        print("🛡️ Critic Agent reviewing report...")
        final_result = critic.review_report(report)

        print("\n✅ Analysis Completed!\n")

        return final_result

    except Exception as e:
        return {
            "status": "Error",
            "message": str(e),
            "trace": traceback.format_exc()
        }


if __name__ == "__main__":
    print("======================================")
    print("🤖 AI Competitor Analysis System")
    print("======================================\n")

    # ✅ Take two company inputs
    company1 = input("👉 Enter Company 1: ").strip()
    company2 = input("👉 Enter Company 2: ").strip()

    # ✅ Validation
    if not company1 or not company2:
        print("❌ Please enter both company names.")
    elif company1.lower() == company2.lower():
        print("❌ Please enter two different companies.")
    else:
        # Convert into query
        user_query = f"Compare {company1} {company2}"

        result = run_analysis(user_query)

        print("\n📌 FINAL OUTPUT:\n")
        print("=" * 50)
        print(json.dumps(result, indent=4))
        print("=" * 50)