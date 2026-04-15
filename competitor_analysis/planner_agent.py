# competitor_analysis/planner_agent.py

import re

class PlannerAgent:
    def create_plan(self, user_query: str) -> dict:
        """
        Creates a structured plan based on user query
        """

        # Step 1: Extract company names (basic NLP)
        companies = self.extract_companies(user_query)

        # Step 2: Build structured plan
        plan = {
            "status": "success",
            "objective": user_query,
            "companies": companies,
            "tasks": [
                "Extract company names",
                "Collect company data (products, pricing, market share)",
                "Perform comparative analysis",
                "Generate SWOT analysis",
                "Perform risk analysis",
                "Generate strategic recommendations",
                "Compile final report"
            ]
        }

        return plan

    def extract_companies(self, query: str):
        """
        Simple company name extractor (can upgrade later with NLP)
        """
        # Split words and pick capitalized ones
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)

        # Remove common words
        ignore = {"Compare", "And", "Vs", "With"}
        companies = [word for word in words if word not in ignore]

        return companies if companies else ["Unknown"]