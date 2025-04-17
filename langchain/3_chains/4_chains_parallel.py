"""
Dieses Skript demonstriert die parallele Verarbeitung mit Chains in LangChain.

Diese Implementierung zeigt, wie mehrere Verarbeitungszweige gleichzeitig ausgeführt 
und anschließend kombiniert werden können, indem RunnableParallel verwendet wird.

Die Chain besteht aus folgenden Komponenten:
1. Erste Analyse: Sammelt grundlegende Filminformationen basierend auf dem Filmnamen
2. Parallele Verarbeitung: 
   - Plot-Analyse-Zweig: Analysiert die Stärken und Schwächen der Handlung
   - Charakter-Analyse-Zweig: Analysiert die Stärken und Schwächen der Charaktere
3. Kombination: Führt die Ergebnisse beider Analysen zu einem Gesamtbericht zusammen

Dieser Ansatz demonstriert, wie komplexe Verarbeitungslogik mit mehreren
Analyseschritten effizient implementiert werden kann.
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSequence, RunnableParallel

# Initialisierung des LLM-Modells
model = ChatOpenAI(model="gpt-4.1-nano")

# Erstellung des Prompt-Templates mit Platzhaltern
summary_template = ChatPromptTemplate.from_messages([
    ("system", "You are a movie critic."),
    ("human", "Gib mir die wichtigsten Informationen über das Film {movie_name}."),
])

# Define plot analysis step
def analyze_plot(plot):
    plot_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a movie critic."),
            ("human", "Analyze the plot: {plot}. What are its strengths and weaknesses?"),
        ]
    )
    return plot_template.format_prompt(plot=plot)

# Define character analysis step
def analyze_characters(characters):
    character_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a movie critic."),
            ("human", "Analyze the characters: {characters}. What are its strengths and weaknesses?"),
        ]
    )
    return character_template.format_prompt(characters=characters)

def combine_verdicts(plot_analysis, character_analysis):
    return f"Plot Analysis: {plot_analysis}\nCharacters Analysis: {character_analysis}"

# Simplify branches with LCEL
plot_branche_chain = (
    RunnableLambda(lambda x: analyze_plot(x)) | model | StrOutputParser()
)

# Character analysis branch
character_branch_chain = (
    RunnableLambda(lambda x: analyze_characters(x)) | model | StrOutputParser()
)


# Define the chain
chain = (
    summary_template 
    | model 
    | StrOutputParser() 
    | RunnableParallel(branches={"plot": plot_branche_chain, "characters": character_branch_chain}) 
    | RunnableLambda(lambda x: combine_verdicts(x["branches"]["plot"], x["branches"]["characters"]))
)

# Ausführung der Chain mit konkreten Werten
result = chain.invoke({"movie_name": "Inception"})

# Ausgabe des Ergebnisses (ein einfacher String)
print(result)

# docker-compose run --rm app langchain/3_chains/4_chains_parallel.py 