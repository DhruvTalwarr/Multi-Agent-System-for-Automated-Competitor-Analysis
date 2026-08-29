# from typing import TypedDict, List, Annotated
# import operator

# class AgentState(TypedDict):
#     # 'messages' keeps track of the conversation history
#     messages: Annotated[List[str], operator.add]
#     # Specialized fields for your project tasks
#     plan: str
#     research_data: str
#     report: str
#     is_approved: bool

from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    # messages accumulates history; other fields overwrite
    messages: Annotated[List[str], operator.add]
    plan: str
    research_data: str
    report: str
    is_approved: bool
    revision_count: int  # CRITICAL: Tracks loops to prevent 429/timeouts