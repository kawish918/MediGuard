# backend/app/graph/graph.py

from langgraph.graph import StateGraph
from app.graph.state import MediGuardState
from app.graph.nodes.scribe import scribe_agent
from app.graph.nodes.threat import threat_agent
from app.graph.nodes.guard import guard_agent

graph = StateGraph(MediGuardState)

graph.add_node("scribe", scribe_agent)
graph.add_node("threat", threat_agent)
graph.add_node("guard", guard_agent)

graph.set_entry_point("scribe")
graph.add_edge("scribe", "threat")
graph.add_edge("threat", "guard")
graph.set_finish_point("guard")

app = graph.compile()