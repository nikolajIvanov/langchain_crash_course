from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")


messages = [
    SystemMessage(content="Du bist ein hilfreicher Reiseführer."),
    HumanMessage(content="Was ist die Hauptstadt von der Türkei?"),
    AIMessage(content="Die Hauptstadt von der Türkei ist Ankara."),
]

restult = llm.invoke(messages)

print(restult.content)