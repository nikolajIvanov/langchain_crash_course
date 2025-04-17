from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

"""
RAG (Retrieval Augmented Generation) mit LLM-Integration - Vollständige Implementierung

Dieses Skript implementiert ein vollständiges RAG-System mit folgenden Komponenten:
- Laden einer existierenden Chroma-Vektordatenbank mit Metadaten
- Konfiguration eines Retrievers für semantische Ähnlichkeitssuche
- Abrufen relevanter Dokumentabschnitte basierend auf einer Benutzeranfrage
- Kombination von Anfrage und relevanten Dokumenten in einem Prompt
- Generierung einer natürlichsprachlichen Antwort mit ChatOpenAI (GPT-4o-mini)

Dieser Workflow demonstriert den vollständigen RAG-Prozess:
1. Retrieval: Relevante Dokumente werden aus der Vektordatenbank abgerufen
2. Augmentation: Die abgerufenen Dokumente werden mit der Benutzeranfrage kombiniert
3. Generation: Ein LLM generiert eine Antwort basierend auf den bereitgestellten Informationen

Im Unterschied zu früheren Beispielen:
- Die Antwort wird direkt vom LLM generiert statt nur Dokumente anzuzeigen
- Der LLM wird angewiesen, nur auf Basis der bereitgestellten Dokumente zu antworten
- Bei fehlenden Informationen soll explizit "Not provided in the documents" zurückgegeben werden

Verwendete Komponenten:
- Embedding-Modell: text-embedding-3-small (OpenAI)
- LLM-Modell: gpt-4o-mini (OpenAI)
- Retriever-Konfiguration: Ähnlichkeitssuche mit k=1 (ein relevantes Dokument)
"""

# Initialisierung des LLM-Modells
# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # Ermittle das aktuelle Verzeichnis
db_dir = os.path.join(current_dir, "db")  # Übergeordnetes Verzeichnis für die Vektordatenbank
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")  # Speicherort der Vektordatenbank mit Metadaten

# Define the embedding model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # Verwende das gleiche Embedding-Modell wie bei der Erstellung
)

# Load the existing vector store with the embedding function
db = Chroma(
    embedding_function=embeddings,  # Verwende die gleiche Embedding-Funktion wie bei der Erstellung
    persist_directory=persistent_directory,  # Lade die Datenbank aus dem Speicherort
)

# Define the user's query
query = "Where is Dracula's castle located?"  # Beispielabfrage zum Testen der Metadaten-Funktion

# Retrive relevant documents based on the query
retrieved = db.as_retriever(
    search_type="similarity",  # Verwende Schwellenwert-basierte Ähnlichkeitssuche
    search_kwargs={"k": 1},  # Maximal 3 Dokumente mit mindestens 20% Ähnlichkeit (niedriger Schwellenwert für breitere Ergebnisse)
)
relevant_docs = retrieved.invoke(query)  # Führe die Abfrage durch und erhalte relevante Dokumente
"""
print("\n--- Relevant documents ---")
for i, doc in enumerate(relevant_docs, 1):  # Durchlaufe alle gefundenen relevanten Dokumente
    print(f"\nDocument {i}: {doc.page_content}")  # Zeige den Inhalt des Dokuments an
    print(f"Source: {doc.metadata['source']}")  # Zeige die Quelle aus den Metadaten an (direkte Indizierung statt get)
"""

combined_input = (
    "Here are some documents that might help answer the question: "
    + query
    + "\n\n Relevant documents: "
    + "\n".join([doc.page_content for doc in relevant_docs])
    + "\n\n Please provide a rough answer based only on the provided documents. If the answer ist not in the documents, respond with 'Not provided in the documents'."
)

model = ChatOpenAI(model="gpt-4o-mini")

message = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content=combined_input),
]

result = model.invoke(message)
print(result.content)

# Befehl zum Ausführen des Skripts in einer Docker-Umgebung
# docker-compose run --rm app langchain/4_RAGs/3_rag_one_off_question.py