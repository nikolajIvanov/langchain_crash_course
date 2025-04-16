"""
Dieses Skript demonstriert das grundlegende Konzept von Chains in LangChain.

Eine Chain ist eine Verkettung von Komponenten, die nacheinander ausgeführt werden,
wobei die Ausgabe einer Komponente als Eingabe für die nächste dient.

In diesem Beispiel wird eine einfache Chain erstellt, die:
1. Ein Prompt-Template mit Platzhaltern für Thema und Anzahl der Informationen verwendet
2. Dieses Template an ein LLM (gpt-4o-mini) weiterleitet
3. Die LLM-Ausgabe mit einem StrOutputParser in einen einfachen String umwandelt

Diese Verkettung wird mit dem Pipe-Operator (|) realisiert, was den Code
übersichtlicher und modularer gestaltet als verschachtelte Funktionsaufrufe.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


model = ChatOpenAI(model="gpt-4o-mini")


messages = [
    ("system", "Du bist ein KI Experte für {topic}."),
    ("human", "Gib mir {number} Informationen über {topic}."),
]

prompt_template = ChatPromptTemplate.from_messages(messages)

chain = prompt_template | model | StrOutputParser()

result = chain.invoke({"topic": "LLMOps", "number": 3})

print(result)

# docker-compose run --rm app 3_chains/1_chains_basics.py