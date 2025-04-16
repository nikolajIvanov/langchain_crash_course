"""
RAG (Retrieval Augmented Generation) Basisimplementierung - Teil 1

Dieses Skript implementiert den ersten Teil eines RAG-Systems mit LangChain:
- Laden eines Textdokuments (Lord of the Rings)
- Aufteilen des Textes in überlappende Chunks
- Erstellen von Embeddings mit OpenAI
- Speichern der Embeddings in einer Chroma-Vektordatenbank

Die Vektordatenbank wird nur erstellt, wenn sie nicht bereits existiert.
Dies ermöglicht eine effiziente Wiederverwendung für spätere Abfragen.
"""
from langchain_community.document_loaders import TextLoader  # Zum Laden von Textdokumenten
from langchain_text_splitters import CharacterTextSplitter  # Zum Aufteilen von Dokumenten in Chunks
from langchain_chroma import Chroma  # Vektordatenbank für die Speicherung von Embeddings
from langchain_openai import OpenAIEmbeddings  # OpenAI-API für Embeddings
import os  # Für Dateisystem-Operationen

# Definiere die Verzeichnisse für Quelldatei und Vektordatenbank
current_dir = os.path.dirname(os.path.abspath(__file__))  # Aktuelles Verzeichnis ermitteln
file_path = os.path.join(current_dir, "documents", "lord_of_the_rings.txt")  # Pfad zur Textdatei
persistent_directory = os.path.join(current_dir, "db", "chroma_db")  # Speicherort für die Vektordatenbank

# Überprüfe, ob die Chroma-Vektordatenbank bereits existiert
if not os.path.exists(persistent_directory):
    print("Persistent directory does not extist. Initializing vector store...")  # Statusmeldung
    
    # Stelle sicher, dass die Textdatei existiert
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found at {file_path}")  # Fehler, wenn Datei fehlt
    
    # Lade die Textdatei mit dem TextLoader
    loader = TextLoader(file_path)  # Initialisiere den Loader mit dem Dateipfad
    documents = loader.load()  # Lade das Dokument in den Speicher
    
    # Teile das Dokument in Chunks auf
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)  # 1000 Zeichen pro Chunk mit 50 Zeichen Überlappung
    docs = text_splitter.split_documents(documents)  # Führe die Aufteilung durch
    
    # Zeige Informationen über die erzeugten Chunks an
    print("\n--- Document Chunks Information ---")
    print(f"Number of document chunks: {len(docs)}")  # Anzahl der erzeugten Chunks
    print(f"Sample chunk:\n{docs[0].page_content}")  # Beispielinhalt des ersten Chunks
    
    # Erstelle Embeddings mit OpenAI
    print("\n--- Creating embeddings ---")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",  # Verwende das kleine OpenAI-Embedding-Modell
    )
    print("\n--- Finished creating embeddings ---")
    
    # Erstelle die Vektordatenbank und speichere sie automatisch
    print("\n--- Creating vector store ---")
    db = Chroma.from_documents(
        documents=docs,  # Die aufgeteilten Dokumente
        embedding=embeddings,  # Die Embedding-Funktion
        persist_directory=persistent_directory,  # Wo die Datenbank gespeichert werden soll
    )
    print("\n--- Vector store created and persisted ---")

else:
    print("Vector store already exists. No need to initialize.")  # Meldung, wenn Datenbank bereits existiert

# Befehl zum Ausführen des Skripts in einer Docker-Umgebung
# docker-compose run --rm app 4_RAGs/1a_basic_part_1.py 