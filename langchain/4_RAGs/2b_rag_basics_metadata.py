from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os

"""
RAG (Retrieval Augmented Generation) mit Metadaten - Abfragephase

Dieses Skript demonstriert die Abfragefunktionalität eines RAG-Systems mit Metadaten:
- Laden einer existierenden Chroma-Vektordatenbank mit Metadaten
- Konfiguration eines Retrievers mit Schwellenwert-basierter Ähnlichkeitssuche
- Durchführung einer semantischen Suche mit einer Benutzerabfrage
- Anzeige der relevanten Dokumentenabschnitte mit Quellenangaben aus den Metadaten

Dieses Skript setzt voraus, dass 2a_rag_basics_metadata.py bereits ausgeführt wurde
und die Vektordatenbank mit den entsprechenden Embeddings und Metadaten erstellt wurde.

Verwendete Parameter:
- Embedding-Modell: text-embedding-3-small (OpenAI)
- Maximale Anzahl zurückgegebener Dokumente: 3
- Minimaler Ähnlichkeitsschwellenwert: 0.2 (20%)
- Beispielabfrage: "Where is Dracula's castle located?"
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
    search_type="similarity_score_threshold",  # Verwende Schwellenwert-basierte Ähnlichkeitssuche
    search_kwargs={"k": 3, "score_threshold": 0.2},  # Maximal 3 Dokumente mit mindestens 20% Ähnlichkeit (niedriger Schwellenwert für breitere Ergebnisse)
)
relevant_docs = retrieved.invoke(query)  # Führe die Abfrage durch und erhalte relevante Dokumente

print("\n--- Relevant documents ---")
for i, doc in enumerate(relevant_docs, 1):  # Durchlaufe alle gefundenen relevanten Dokumente
    print(f"\nDocument {i}: {doc.page_content}")  # Zeige den Inhalt des Dokuments an
    print(f"Source: {doc.metadata['source']}")  # Zeige die Quelle aus den Metadaten an (direkte Indizierung statt get)

# Befehl zum Ausführen des Skripts in einer Docker-Umgebung
# docker-compose run --rm app langchain/4_RAGs/2b_rag_basics_metadata.py 