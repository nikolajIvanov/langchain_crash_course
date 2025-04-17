"""
RAG (Retrieval Augmented Generation) mit Metadaten - Erstellungsphase

Dieses Skript implementiert ein RAG-System mit Metadatenanreicherung:
- Laden aller Textdokumente (.txt) aus einem Verzeichnis
- Anreicherung jedes Dokuments mit Metadaten (Quelldateiname)
- Aufteilen der Texte in überlappende Chunks
- Erstellen von Embeddings mit OpenAI
- Speichern der Embeddings und Metadaten in einer Chroma-Vektordatenbank

Die Metadaten ermöglichen später eine gezieltere Suche und bessere Quellenangaben.
Die Vektordatenbank wird nur erstellt, wenn sie nicht bereits existiert.
"""
from langchain_community.document_loaders import TextLoader  # Zum Laden von Textdokumenten
from langchain_text_splitters import CharacterTextSplitter  # Zum Aufteilen von Dokumenten in Chunks
from langchain_chroma import Chroma  # Vektordatenbank für die Speicherung von Embeddings
from langchain_openai import OpenAIEmbeddings  # OpenAI-API für Embeddings
import os  # Für Dateisystem-Operationen

# Definiere die Verzeichnisse für Quelldateien und Vektordatenbank
current_dir = os.path.dirname(os.path.abspath(__file__))  # Aktuelles Verzeichnis ermitteln
books_dir = os.path.join(current_dir, "documents")  # Verzeichnis mit den Textdateien
db_dir = os.path.join(current_dir, "db")  # Übergeordnetes Verzeichnis für die Vektordatenbank
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")  # Speicherort für die Vektordatenbank mit Metadaten

print(f"Books directory: {db_dir}")
print(f"Persistent directory: {persistent_directory}")

# Überprüfe, ob die Chroma-Vektordatenbank bereits existiert
if not os.path.exists(persistent_directory):
    print("Persistent directory does not extist. Initializing vector store...")  # Statusmeldung
    
    # Stelle sicher, dass das Dokumentverzeichnis existiert
    if not os.path.exists(books_dir):
        raise FileNotFoundError(f"Books directory not found at {books_dir}")  # Fehler, wenn Verzeichnis fehlt
    
    # Sammle alle Textdateien aus dem Verzeichnis
    book_files = [f for f in os.listdir(books_dir) if f.endswith(".txt")]  # Filtere nach .txt-Dateien
    
    # Lade alle Textdateien und füge Metadaten hinzu
    documents = []
    for book_file in book_files:  # Iteriere über alle Textdateien
        file_path = os.path.join(books_dir, book_file)  # Vollständiger Pfad zur Datei
        loader = TextLoader(file_path)  # Initialisiere den Loader
        book_docs = loader.load()  # Lade das Dokument
        for doc in book_docs:  # Für jedes geladene Dokument
            doc.metadata = {"source": book_file}  # Füge Metadaten hinzu (Quelldateiname)
            documents.append(doc)  # Füge das Dokument zur Liste hinzu
    
    # Teile die Dokumente in Chunks auf
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)  # 1000 Zeichen pro Chunk mit 50 Zeichen Überlappung
    docs = text_splitter.split_documents(documents)  # Führe die Aufteilung durch (Metadaten werden übernommen)
    
    # Zeige Informationen über die erzeugten Chunks an
    print("\n--- Document Chunks Information ---")
    print(f"Number of document chunks: {len(docs)}")  # Anzahl der erzeugten Chunks
    print(f"Sample chunk:\n{docs[0].page_content}")  # Beispielinhalt des ersten Chunks
    print(f"Sample metadata: {docs[0].metadata}")  # Beispiel für Metadaten
    
    # Erstelle Embeddings mit OpenAI
    print("\n--- Creating embeddings ---")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",  # Verwende das kleine OpenAI-Embedding-Modell
    )
    print("\n--- Finished creating embeddings ---")
    
    # Erstelle die Vektordatenbank und speichere sie automatisch
    print("\n--- Creating vector store ---")
    db = Chroma.from_documents(
        documents=docs,  # Die aufgeteilten Dokumente mit Metadaten
        embedding=embeddings,  # Die Embedding-Funktion
        persist_directory=persistent_directory,  # Wo die Datenbank gespeichert werden soll
    )
    print("\n--- Vector store created and persisted ---")

else:
    print("Vector store already exists. No need to initialize.")  # Meldung, wenn Datenbank bereits existiert

# Befehl zum Ausführen des Skripts in einer Docker-Umgebung
# docker-compose run --rm app langchain/4_RAGs/2a_rag_basics_metadata.py 