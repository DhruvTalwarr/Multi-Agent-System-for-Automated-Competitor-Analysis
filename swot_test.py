import os
import pandas as pd
import json
from openai import OpenAI

# 1. SETUP: Use the OpenAI bridge for Groq
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"]
)

# 2. STRATEGIC DATASET: SWOT Queries & AI Responses
# These are your "Test Cases" for the SWOT experiment
swot_test_cases = [
    {
        "company": "BYD",
        "user_input": "Perform a SWOT analysis for BYD's luxury EV segment in Europe for 2026.",
        "ai_response": """
        Strengths: Vertical integration of 'Blade' battery tech. 
        Weaknesses: Lack of premium brand heritage compared to BMW/Mercedes.
        Opportunities: New EU-China trade corridors and green subsidies.
        Threats: Rising EU tariffs and rapid software advances by local OEMs.
        """,
        "facts_retrieved": "BYD produces its own batteries; EU tariffs on Chinese EVs are increasing; Mercedes has 100+ years of brand equity."
    },
    {
        "company": "NVIDIA",
        "user_input": "Analyze NVIDIA's market positioning in the 2026 AI Inference sector.",
        "ai_response": """
        Strengths: Dominant CUDA ecosystem. 
        Weaknesses: High power consumption of Blackwell chips.
        Opportunities: Massive shift from AI training to real-time inference.
        Threats: Specialized LPU rivals like Groq offering 10x lower latency.
        """,
        "facts_retrieved": "NVIDIA Blackwell TDP is 1200W; Groq LPU leads in tokens/sec; CUDA is used by 4M+ developers."
    }
]

# 3. THE JUDGE LOGIC: Grading the SWOT quality
def judge_swot_quality(case):
    prompt = f"""
    Act as a Senior Business Strategy Consultant. Grade the following AI-generated SWOT analysis.
    
    CRITERIA (Score 1-5):
    1. Strategic Depth: Does it identify non-obvious market dynamics?
    2. Actionability: Could a CEO make a decision based on this?
    3. Grounding: Is it supported by the retrieved facts?

    USER QUERY: {case['user_input']}
    AI RESPONSE: {case['ai_response']}
    FACTS RETRIEVED: {case['facts_retrieved']}

    Return ONLY a JSON object:
    {{"depth": score, "actionability": score, "grounding": score, "reasoning": "short explanation"}}
    """
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# 4. EXECUTION
print("🚀 Starting Experiment 4: Strategic SWOT Evaluation...")
results = []
for case in swot_test_cases:
    score = judge_swot_quality(case)
    score['Company'] = case['company']
    results.append(score)

# 5. FINAL REPORTING
df_swot = pd.DataFrame(results)
print("\n📊 EXPERIMENT 4: QUALITATIVE INSIGHT SCORES (1-5)")
print("-" * 60)
print(df_swot[['Company', 'depth', 'actionability', 'grounding']])

df_swot.to_csv("Experiment4_SWOT_Analysis.csv", index=False)
print("\n✅ Strategic Analysis saved to 'Experiment4_SWOT_Analysis.csv'")