
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents import planner_agent, researcher_agent, report_generator_agent, critic_agent

def should_continue(state: AgentState):
    # Stop if approved or if we reached the loop limit (3)
    if state["is_approved"] or state.get("revision_count", 0) >= 2:
        return "end"
    # If not approved, try to research again (RAG will try dynamic scrape on 2nd attempt)
    return "researcher"

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_agent)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("generator", report_generator_agent)
workflow.add_node("critic", critic_agent)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "generator")
workflow.add_edge("generator", "critic")

workflow.add_conditional_edges(
    "critic",
    should_continue,
    {"end": END, "researcher": "researcher"}
)

app = workflow.compile()