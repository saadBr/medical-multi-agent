from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from backend.app.nodes.diagnostic_agent import diagnostic_agent
from backend.app.nodes.physician_review import physician_review
from backend.app.nodes.report_agent import report_agent
from backend.app.nodes.supervisor import supervisor
from backend.app.nodes.interim_care_agent import interim_care_agent
from backend.app.state import MedicalState

def route_supervisor(state: MedicalState)-> str:
    """
    Return the node selected by the supervisor.
    """

    return state ["next"]

workflow = StateGraph(MedicalState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("diagnostic_agent", diagnostic_agent)
workflow.add_node("physician_review", physician_review)
workflow.add_node("report_agent", report_agent)
workflow.add_node("interim_care_agent", interim_care_agent)
workflow.add_edge(START, "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        "interim_care_agent": "interim_care_agent",
        "FINISH": END,   
    }
)

workflow.add_edge("diagnostic_agent", "supervisor")
workflow.add_edge("physician_review", "supervisor")
workflow.add_edge("report_agent", "supervisor")
workflow.add_edge("interim_care_agent", "supervisor")

memory = InMemorySaver()
graph = workflow.compile(checkpointer=memory)
studio_graph = workflow.compile()