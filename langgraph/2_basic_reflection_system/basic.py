from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import MessageGraph, END
from langchain_core.messages import HumanMessage, BaseMessage
from chains import generation_chain, reflection_chain


graph = MessageGraph()

REFLECT = "reflect"
GENERATE = "generate"


def generate_node(state):
    return generation_chain.invoke({
        "messages": state
    })


def reflect_node(state):
    response = reflection_chain.invoke({
        "messages": state
    })
    return [HumanMessage(content=response.content)]

graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)

graph.set_entry_point(GENERATE)

def should_continue(state):
    if(len(state) > 6):
        return END
    return REFLECT

graph.add_conditional_edges(GENERATE, should_continue)

graph.add_edge(REFLECT, GENERATE)

app = graph.compile()

# print(app.get_graph().draw_mermaid())
# app.get_graph().print_ascii()

response = app.invoke([HumanMessage(content="KI Multi Agent System für Content Erstellung")])

print(response)

# docker-compose run --rm app langgraph/2_basic_reflection_system/basic.py