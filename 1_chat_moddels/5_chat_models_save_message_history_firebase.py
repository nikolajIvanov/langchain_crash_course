"""
Dieses Skript implementiert einen einfachen Chatbot in der Kommandozeile.
Es nutzt LangChain und das OpenAI-Modell 'gpt-4o-mini', um auf Benutzereingaben zu antworten.

Der Chatverlauf wird in der Liste 'chat_history' gespeichert und bei jeder Anfrage
an das Modell übergeben, um kontextbezogene Antworten zu ermöglichen.
Eine Systemnachricht legt zu Beginn das Verhalten des Assistenten fest.
Der Chat läuft in einer Schleife, bis der Benutzer 'exit' eingibt.

Die Chat-History wird außerdem in Firebase gespeichert, um sie zwischen Sitzungen zu erhalten.
"""
# --- IMPORT-ANWEISUNGEN ---
# LangChain-Importe für das Nachrichtenformat und das Chat-Modell
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Firebase-Importe für die Datenbankanbindung
import firebase_admin  # Hauptbibliothek für Firebase-Dienste
from firebase_admin import credentials, firestore  # Für Authentifizierung und Firestore-Datenbank

# Standardbibliotheken für verschiedene Hilfsfunktionen
import datetime  # Für Zeitstempel in der Datenbank
import json      # Für JSON-Verarbeitung
import os        # Für Dateipfadoperationen und Umgebungsvariablen
import pathlib   # Für fortgeschrittene Dateipfadoperationen

# --- FIREBASE-INITIALISIERUNG ---
# Prüfen, ob bereits eine Firebase-App initialisiert wurde
if not firebase_admin._apps:
    # Pfade, an denen die Firebase-Credentials gesucht werden
    # Die Datei kann an verschiedenen Orten sein, abhängig davon, ob der Code lokal oder in Docker läuft
    creds_paths = [
        './secrets/firebase-credentials.json',       # Lokaler Entwicklungspfad
        './secrets/firebase-adminsdk.json',          # Alternative Benennung
        '/app/secrets/firebase-credentials.json',    # Docker-Container-Pfad
        '/app/secrets/firebase-adminsdk.json'        # Alternative Benennung im Docker-Container
    ]
    
    cred = None
    
    # Suche nach der Credentials-Datei an den definierten Pfaden
    for path in creds_paths:
        if os.path.exists(path):
            print(f"Firebase-Credentials gefunden unter: {path}")
            # Wenn gefunden, erstelle ein Credentials-Objekt aus der Datei
            cred = credentials.Certificate(path)
            break
            
    # Wenn keine Credentials-Datei gefunden wurde, versuche es mit ApplicationDefault
    # ApplicationDefault sucht nach Umgebungsvariablen oder lokalen Anmeldedaten
    if cred is None:
        print("Keine Credentials-Datei gefunden, verwende ApplicationDefault")
        try:
            # Versuche, die Standard-Anmeldeinformationen zu verwenden
            # Dies funktioniert, wenn die Umgebungsvariable GOOGLE_APPLICATION_CREDENTIALS gesetzt ist
            # oder der Benutzer mit der Google Cloud CLI angemeldet ist
            cred = credentials.ApplicationDefault()
        except Exception as e:
            # Bei Fehlern gib hilfreiche Informationen aus
            print(f"Fehler bei der Authentifizierung: {e}")
            print("Hinweis: Du musst eine firebase-credentials.json im secrets/-Verzeichnis ablegen")
            print("Diese kannst du in der Firebase Console unter Projekteinstellungen > Dienstkonten > Firebase Admin SDK erzeugen.")
            exit(1)  # Programm beenden, da ohne Authentifizierung nicht fortgefahren werden kann
    
    # Firebase-App initialisieren mit den gefundenen Credentials
    # Die projectId wird aus der Umgebungsvariable oder dem Standardwert genommen
    firebase_admin.initialize_app(cred, {
        'projectId': os.environ.get('FIREBASE_PROJECT_ID', 'langchaintutorial-92b5b'),
    })

# --- DATENBANKVERBINDUNG HERSTELLEN ---
# Firestore-Client erstellen für Datenbankzugriffe
db = firestore.client()

# --- CHAT-MODELL INITIALISIEREN ---
# OpenAI-Chat-Modell initialisieren
# Der API-Schlüssel wird automatisch aus der Umgebungsvariable OPENAI_API_KEY gelesen
llm = ChatOpenAI(model="gpt-4o-mini")

# --- KONSTANTEN FÜR FIREBASE ---
# Firebase-Projekt-ID zur Identifikation des Projekts
PROJECT_ID = "langchaintutorial-92b5b"
# Eine eindeutige Sitzungs-ID - in einer richtigen App würde diese pro Benutzer/Sitzung generiert
SESSION_ID = "1234567890"
# Der Name der Firestore-Collection, in der die Chat-History gespeichert wird
COLLECTION_NAME = "chat_history"

# --- CHAT-HISTORY INITIALISIEREN ---
# Eine leere Liste, die den aktuellen Chat-Verlauf enthält
chat_history = []

# --- VORHANDENE CHAT-HISTORY AUS FIREBASE LADEN ---
try:
    # Referenz zum Dokument in Firestore erstellen
    chat_ref = db.collection(COLLECTION_NAME).document(SESSION_ID)
    # Dokument abrufen
    chat_doc = chat_ref.get()
    
    # Prüfen, ob das Dokument existiert (ob es bereits eine gespeicherte Chat-History gibt)
    if chat_doc.exists:
        # Dokument in ein Python-Dictionary umwandeln
        chat_data = chat_doc.to_dict()
        # Die gespeicherten Nachrichten extrahieren
        saved_messages = chat_data.get('messages', [])
        
        # Jede gespeicherte Nachricht in ein LangChain-Nachrichtenobjekt umwandeln
        # und zur Chat-History hinzufügen
        for msg in saved_messages:
            if msg['type'] == 'system':
                # System-Nachrichten definieren das Verhalten des Assistenten
                chat_history.append(SystemMessage(content=msg['content']))
            elif msg['type'] == 'human':
                # Benutzer-Nachrichten sind die Eingaben des Benutzers
                chat_history.append(HumanMessage(content=msg['content']))
            elif msg['type'] == 'ai':
                # KI-Nachrichten sind die Antworten des Modells
                # Korrekte Klasse: AIMessage anstelle von SystemMessage verwenden
                from langchain_core.messages import AIMessage
                chat_history.append(AIMessage(content=msg['content']))
        
        print(f"Chat-History mit {len(saved_messages)} Nachrichten geladen.")
    else:
        # Wenn keine gespeicherte Chat-History existiert, eine neue mit einer System-Nachricht starten
        system_message = SystemMessage(content="Du bist ein hilfreicher KI-Assistant.")
        chat_history.append(system_message)
        
        # Die neue Chat-History in Firebase speichern
        chat_ref.set({
            'messages': [{
                'type': 'system',
                'content': "Du bist ein hilfreicher KI-Assistant.",
                'timestamp': datetime.datetime.now().isoformat()  # Zeitstempel für die Nachricht
            }],
            'created_at': datetime.datetime.now().isoformat(),  # Erstellungszeitpunkt der Chat-History
            'updated_at': datetime.datetime.now().isoformat()   # Letzter Aktualisierungszeitpunkt
        })
except Exception as e:
    # Bei Fehlern beim Laden aus Firebase Fehlermeldung ausgeben
    print(f"Fehler beim Laden der Chat-History: {e}")
    # Fallback: Lokale Chat-History mit System-Nachricht starten
    system_message = SystemMessage(content="Du bist ein hilfreicher KI-Assistant.")
    chat_history.append(system_message)

# --- FUNKTION ZUM SPEICHERN VON NACHRICHTEN IN FIREBASE ---
def save_message_to_firebase(message, msg_type):
    """
    Speichert eine Nachricht in Firebase Firestore.
    
    Args:
        message: LangChain-Nachrichtenobjekt (HumanMessage oder AIMessage)
        msg_type: Typ der Nachricht ('system', 'human' oder 'ai')
    """
    try:
        # Referenz zum Dokument in Firestore
        chat_ref = db.collection(COLLECTION_NAME).document(SESSION_ID)
        # Prüfen, ob das Dokument existiert
        chat_doc = chat_ref.get()
        
        if chat_doc.exists:
            # Wenn das Dokument existiert, die neue Nachricht zum Array hinzufügen
            # und den Aktualisierungszeitpunkt aktualisieren
            chat_ref.update({
                'messages': firestore.ArrayUnion([{  # ArrayUnion fügt Elemente zu einem Array hinzu
                    'type': msg_type,
                    'content': message.content,
                    'timestamp': datetime.datetime.now().isoformat()
                }]),
                'updated_at': datetime.datetime.now().isoformat()
            })
        else:
            # Wenn das Dokument nicht existiert, ein neues erstellen
            chat_ref.set({
                'messages': [{
                    'type': msg_type,
                    'content': message.content,
                    'timestamp': datetime.datetime.now().isoformat()
                }],
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            })
    except Exception as e:
        # Bei Fehlern beim Speichern Fehlermeldung ausgeben
        print(f"Fehler beim Speichern in Firebase: {e}")

# --- HAUPT-CHAT-SCHLEIFE ---
while True:
    # Benutzereingabe abfragen
    user_input = input("Du: ")
    # Überprüfen, ob der Benutzer den Chat beenden möchte
    if user_input.lower() == "exit":
        break
    
    # Benutzer-Nachricht zur lokalen Chat-History hinzufügen
    human_message = HumanMessage(content=user_input)
    chat_history.append(human_message)
    
    # Benutzer-Nachricht in Firebase speichern
    save_message_to_firebase(human_message, 'human')
    
    """
    Hier wird das aktuelle Chat-Verlauf an das Modell übergeben und die Antwort generiert.
    Die Antwort wird der Chat-History hinzugefügt und auf der Konsole ausgegeben.
    """
    # Das LLM mit der aktuellen Chat-History aufrufen
    result = llm.invoke(chat_history)
    # Die Antwort des LLM zur Chat-History hinzufügen
    chat_history.append(result)
    
    # KI-Antwort in Firebase speichern
    save_message_to_firebase(result, 'ai')
    
    # Die Antwort des Modells ausgeben
    print(result.content)

# --- AUSGABE DER CHAT-HISTORY NACH BEENDIGUNG ---
print("---- Message History ----")
print(chat_history)
