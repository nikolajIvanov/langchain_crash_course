from typing import List
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langgraph.graph import MessageGraph, END

from chains import first_responder_chain, revisor_chain
from execute_tools import execute_tools

graph = MessageGraph()
MAX_ITERATIONS = 2

graph.add_node("responder", first_responder_chain)
graph.add_node("revisor", revisor_chain)
graph.add_node("execute_tools", execute_tools)

graph.add_edge("responder", "execute_tools")
graph.add_edge("execute_tools", "revisor")

def event_loop(state: List[BaseMessage]) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state)
    num_iterations = count_tool_visits

    if num_iterations > MAX_ITERATIONS:
        return END
    return "execute_tools"

graph.add_conditional_edges("revisor",event_loop)

graph.set_entry_point("responder")

app = graph.compile()

print(app.get_graph().draw_mermaid())

response = app.invoke([HumanMessage(content="Informiere dich über das Agenten System manus.im. Was macht es so besonders und welche Alternativen gibt es?")])

print(response[-1].tool_calls[0]["args"]["answer"])

# docker-compose run --rm app langgraph/3_reflextion_agent_system/reflextion_graph.py