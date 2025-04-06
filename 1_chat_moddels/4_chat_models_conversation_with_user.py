"""
Dieses Skript implementiert einen einfachen Chatbot in der Kommandozeile.
Es nutzt LangChain und das OpenAI-Modell 'gpt-4o-mini', um auf Benutzereingaben zu antworten.

Der Chatverlauf wird in der Liste 'chat_history' gespeichert und bei jeder Anfrage
an das Modell übergeben, um kontextbezogene Antworten zu ermöglichen.
Eine Systemnachricht legt zu Beginn das Verhalten des Assistenten fest.
Der Chat läuft in einer Schleife, bis der Benutzer 'exit' eingibt.
"""
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

chat_history = [] # Liste für die Chat-History

system_message = SystemMessage(content="Du bist ein hilfreicher KI-Assistant.")
chat_history.append(system_message)

while True:
    user_input = input("Du: ")
    if user_input.lower() == "exit":
        break
    chat_history.append(HumanMessage(content=user_input))
    result = llm.invoke(chat_history)
    chat_history.append(result)
    print(result.content)