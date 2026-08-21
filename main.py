# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from graph import app as agent_graph  # Importing your compiled LangGraph

# # 1. Initialize FastAPI
# app = FastAPI(title="Smart Business Decision Assistant (SBDA)")

# # 2. Define the Request Structure
# class AnalyzeRequest(BaseModel):
#     query: str  # The business question or company to analyze

# # 3. Create the /analyze endpoint (Divyanshi's task 33)
# @app.post("/analyze")
# async def run_analysis(request: AnalyzeRequest):
#     try:
#         # Initial state for your graph
#         initial_state = {
#             "messages": [request.query],
#             "is_approved": False
#         }
        
#         # Invoke the graph (your orchestration logic)
#         final_state = await agent_graph.ainvoke(initial_state)
        
#         # Return the structured report (Dolly's task 47)
#         return {
#             "status": "success",
#             "analysis": final_state.get("report", "No report generated."),
#             "plan_followed": final_state.get("plan")
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # To run this: uvicorn main:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
from graph import app as agent_app

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/analyze")
async def analyze(query: Query):
    # Set the initial state
    initial_input = {
        "messages": [query.text],
        "revision_count": 0,
        "is_approved": False
    }
    
    # Run the graph
    result = agent_app.invoke(initial_input)
    
    return {
        "report": result["report"],
        "iterations": result["revision_count"]
    }