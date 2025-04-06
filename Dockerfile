# Verwende das offizielle Python 3.11 Image
FROM python:3.11-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die requirements.txt Datei
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest der Anwendung
COPY . .

# Definiere den Einstiegspunkt und den Standardbefehl
ENTRYPOINT ["python"]
CMD ["main.py"] 