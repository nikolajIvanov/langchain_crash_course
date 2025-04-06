"""
Dieses Skript implementiert einen einfachen Chatbot in der Kommandozeile.
Es nutzt LangChain und das OpenAI-Modell 'gpt-4o-mini', um auf Benutzereingaben zu antworten.

Der Chatverlauf wird in der Liste 'chat_history' gespeichert und bei jeder Anfrage
an das Modell übergeben, um kontextbezogene Antworten zu ermöglichen.
Eine Systemnachricht legt zu Beginn das Verhalten des Assistenten fest.
Der Chat läuft in einer Schleife, bis der Benutzer 'exit' eingibt.

Die Chat-History wird außerdem in Firebase gespeichert, um sie zwischen Sitzungen zu erhalten.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import json
import os
import pathlib

# Firebase-Initialisierung
if not firebase_admin._apps:
    # Pfad zur Firebase-Credentials-Datei
    creds_paths = [
        './secrets/firebase-credentials.json',
        './secrets/firebase-adminsdk.json',
        '/app/secrets/firebase-credentials.json',
        '/app/secrets/firebase-adminsdk.json'
    ]
    
    cred = None
    
    # Versuche verschiedene mögliche Pfade für die Credentials-Datei
    for path in creds_paths:
        if os.path.exists(path):
            print(f"Firebase-Credentials gefunden unter: {path}")
            cred = credentials.Certificate(path)
            break
            
    # Fallback auf ApplicationDefault, falls keine Datei gefunden wurde
    if cred is None:
        print("Keine Credentials-Datei gefunden, verwende ApplicationDefault")
        try:
            cred = credentials.ApplicationDefault()
        except Exception as e:
            print(f"Fehler bei der Authentifizierung: {e}")
            print("Hinweis: Du musst eine firebase-credentials.json im secrets/-Verzeichnis ablegen")
            print("Diese kannst du in der Firebase Console unter Projekteinstellungen > Dienstkonten > Firebase Admin SDK erzeugen.")
            exit(1)
    
    # Firebase-App initialisieren
    firebase_admin.initialize_app(cred, {
        'projectId': os.environ.get('FIREBASE_PROJECT_ID', 'langchaintutorial-92b5b'),
    })

db = firestore.client()

llm = ChatOpenAI(model="gpt-4o-mini")

PROJECT_ID = "langchaintutorial-92b5b"
SESSION_ID = "1234567890"
COLLECTION_NAME = "chat_history"

chat_history = [] # Liste für die Chat-History

# Vorhandene Chat-History aus Firebase laden, falls vorhanden
try:
    chat_ref = db.collection(COLLECTION_NAME).document(SESSION_ID)
    chat_doc = chat_ref.get()
    
    if chat_doc.exists:
        chat_data = chat_doc.to_dict()
        saved_messages = chat_data.get('messages', [])
        
        for msg in saved_messages:
            if msg['type'] == 'system':
                chat_history.append(SystemMessage(content=msg['content']))
            elif msg['type'] == 'human':
                chat_history.append(HumanMessage(content=msg['content']))
            elif msg['type'] == 'ai':
                chat_history.append(SystemMessage(content=msg['content']))
        
        print(f"Chat-History mit {len(saved_messages)} Nachrichten geladen.")
    else:
        # Neue Chat-History mit System-Nachricht starten
        system_message = SystemMessage(content="Du bist ein hilfreicher KI-Assistant.")
        chat_history.append(system_message)
        
        # Neue Chat-History in Firebase speichern
        chat_ref.set({
            'messages': [{
                'type': 'system',
                'content': "Du bist ein hilfreicher KI-Assistant.",
                'timestamp': datetime.datetime.now().isoformat()
            }],
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        })
except Exception as e:
    print(f"Fehler beim Laden der Chat-History: {e}")
    # Fallback: Lokale Chat-History mit System-Nachricht starten
    system_message = SystemMessage(content="Du bist ein hilfreicher KI-Assistant.")
    chat_history.append(system_message)

def save_message_to_firebase(message, msg_type):
    """Speichert eine Nachricht in Firebase."""
    try:
        chat_ref = db.collection(COLLECTION_NAME).document(SESSION_ID)
        chat_doc = chat_ref.get()
        
        if chat_doc.exists:
            # Dokument existiert bereits, Nachricht hinzufügen
            chat_ref.update({
                'messages': firestore.ArrayUnion([{
                    'type': msg_type,
                    'content': message.content,
                    'timestamp': datetime.datetime.now().isoformat()
                }]),
                'updated_at': datetime.datetime.now().isoformat()
            })
        else:
            # Neues Dokument erstellen
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
        print(f"Fehler beim Speichern in Firebase: {e}")

while True:
    user_input = input("Du: ")
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
    result = llm.invoke(chat_history)
    chat_history.append(result)
    
    # KI-Antwort in Firebase speichern
    save_message_to_firebase(result, 'ai')
    
    print(result.content)

print("---- Message History ----")
print(chat_history)
