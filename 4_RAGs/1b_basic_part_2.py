from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os

"""
RAG (Retrieval Augmented Generation) Basisimplementierung - Teil 2: Abfrage der Vektordatenbank

Dieses Skript demonstriert den zweiten Teil eines RAG-Systems mit LangChain:
- Laden einer existierenden Chroma-Vektordatenbank
- Konfiguration eines Retrievers mit Schwellenwert-basierter Ähnlichkeitssuche
- Durchführung einer semantischen Suche mit einer Benutzerabfrage
- Anzeige der relevanten Dokumentenabschnitte

Dieses Skript setzt voraus, dass Teil 1 (1a_basic_part_1.py) bereits ausgeführt wurde
und die Vektordatenbank mit den entsprechenden Embeddings erstellt wurde.

Verwendete Parameter:
- Embedding-Modell: text-embedding-3-small (OpenAI)
- Maximale Anzahl zurückgegebener Dokumente: 3
- Minimaler Ähnlichkeitsschwellenwert: 0.5 (50%)
- Beispielabfrage: "Where does Gandalf meet Frodo?"
"""

# Initialisierung des LLM-Modells
# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))  # Ermittle das aktuelle Verzeichnis
persistent_directory = os.path.join(current_dir, "db", "chroma_db")  # Pfad zur gespeicherten Vektordatenbank

# Define the embedding model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # Verwende das kleine OpenAI-Embedding-Modell für Effizienz
)

# Load the existing vector store with the embedding function
db = Chroma(
    embedding_function=embeddings,  # Verwende die gleiche Embedding-Funktion wie bei der Erstellung
    persist_directory=persistent_directory,  # Lade die Datenbank aus dem Speicherort
)

# Define the user's query
query = "Where does Gandalf meet Frodo?"  # Beispielabfrage zum Testen des RAG-Systems

# Retrive relevant documents based on the query
retrieved = db.as_retriever(
    search_type="similarity_score_threshold",  # Verwende Schwellenwert-basierte Ähnlichkeitssuche
    search_kwargs={"k": 3, "score_threshold": 0.5},  # Maximal 3 Dokumente mit mindestens 50% Ähnlichkeit
)
relevant_docs = retrieved.invoke(query)  # Führe die Abfrage durch und erhalte relevante Dokumente

print("\n--- Relevant documents ---")
for i, doc in enumerate(relevant_docs, 1):  # Durchlaufe alle gefundenen relevanten Dokumente
    print(f"\nDocument {i}: {doc.page_content}")  # Zeige den Inhalt des Dokuments an
    if doc.metadata:  # Falls Metadaten vorhanden sind
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")  # Zeige die Quelle des Dokuments an

# Befehl zum Ausführen des Skripts in einer Docker-Umgebung
# docker-compose run --rm app 4_RAGs/1b_basic_part_2.py 