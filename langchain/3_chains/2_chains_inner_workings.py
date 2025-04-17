"""
Dieses Skript demonstriert die interne Funktionsweise von Chains in LangChain.

Im Gegensatz zum vereinfachten Pipe-Operator (|) in 1_chains_basics.py
wird hier die Chain explizit mit RunnableSequence und RunnableLambda-Funktionen 
aufgebaut. Dies zeigt, was unter der Haube passiert, wenn der Pipe-Operator verwendet wird.

Die Chain besteht aus drei Hauptkomponenten:
1. Format-Prompt: Wandelt Eingabeparameter in ein formatiertes Prompt um
2. Invoke-Model: Sendet das Prompt an das LLM und erhält eine Antwort
3. Parse-Output: Extrahiert den Textinhalt aus der Modellantwort

Diese explizite Implementierung bietet mehr Kontrolle und Transparenz über die 
einzelnen Verarbeitungsschritte, ist aber weniger kompakt als die Pipe-Syntax.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSequence

# Initialisierung des LLM-Modells
model = ChatOpenAI(model="gpt-4o-mini")

# Erstellung des Prompt-Templates mit Platzhaltern
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Du bist ein KI Experte für {topic}."),
    ("human", "Gib mir die {number} wichtigstenInformationen über {topic}."),
])

# Komponente 1: Formatierung des Prompts mit den Eingabeparametern
format_prompt = RunnableLambda(lambda x: prompt_template.format_prompt(**x))

# Komponente 2: Aufruf des LLM mit dem formatierten Prompt
invoke_model = RunnableLambda(lambda x: model.invoke(x.to_messages()))

# Komponente 3: Extraktion des Inhalts aus der Modellantwort (entspricht StrOutputParser)
parse_output = RunnableLambda(lambda x: x.content)

# Explizite Verkettung der Komponenten mit RunnableSequence
chain = RunnableSequence(first=format_prompt, middle=[invoke_model], last=parse_output)

# Ausführung der Chain mit konkreten Werten
result = chain.invoke({"topic": "LLMOps", "number": 3})

# Ausgabe des Ergebnisses (ein einfacher String)
print(result)

# docker-compose run --rm app langchain/3_chains/2_chains_inner_workings.py