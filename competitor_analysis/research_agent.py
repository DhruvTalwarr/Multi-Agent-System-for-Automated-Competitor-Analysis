# competitor_analysis/research_agent.py

import random
import re

class ResearchAgent:

    def extract_companies(self, query: str):
        """
        Extract company names using regex + cleanup
        """

        # Extract capitalized words (basic NLP)
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)

        # Remove filler words
        ignore = {"Compare", "And", "Vs", "With"}
        companies = [word for word in words if word not in ignore]

        # ✅ Ensure at least 2 companies
        if len(companies) == 1:
            companies.append("CompetitorX")   # auto competitor
        elif len(companies) == 0:
            companies = ["CompanyA", "CompanyB"]

        # ✅ Limit to only 2 (clean comparison)
        return companies[:2]


    def generate_company_data(self, company: str):
        """
        Generate mock company data
        """

        strengths_pool = [
            "Strong brand value",
            "Global presence",
            "Innovation leader",
            "Efficient supply chain",
            "Customer loyalty"
        ]

        weaknesses_pool = [
            "High operational cost",
            "Limited market share",
            "Dependence on few products",
            "Regulatory challenges"
        ]

        return {
            "name": company,
            "revenue": random.randint(50, 500),  # billions
            "market_share": random.randint(5, 40),  # %
            "growth_rate": round(random.uniform(1, 20), 2),  # %
            "strength": random.choice(strengths_pool),
            "weakness": random.choice(weaknesses_pool)
        }


    def gather_data(self, plan: dict) -> dict:
        """
        Main research pipeline
        """

        try:
            query = plan.get("objective", "")

            if not query:
                raise ValueError("Invalid plan: missing objective")

            # Extract companies
            companies = self.extract_companies(query)

            # Generate data
            data = []
            for company in companies:
                data.append(self.generate_company_data(company))

            return {
                "status": "success",
                "companies": data,
                "market_trends": [
                    "Market growing steadily",
                    "Digital transformation increasing",
                    "Competition intensifying"
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }