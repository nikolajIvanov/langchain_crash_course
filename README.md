# langchain_crash_course

Dieses Projekt nutzt Docker und Docker Compose, um eine isolierte Python-Umgebung für LangChain-Experimente bereitzustellen.

## Docker Konzepte verstehen

Für ein tieferes Verständnis der verwendeten Docker-Konzepte (Dockerfile vs. docker run vs. Docker Compose, Volumes etc.) und die Entwicklungsschritte, die zur aktuellen Konfiguration geführt haben, siehe die Datei [DOCKER_EXPLAINER.md](DOCKER_EXPLAINER.md).

## Docker Anweisungen (mit Docker Compose)

Docker Compose vereinfacht das Bauen und Ausführen des Containers, insbesondere während der Entwicklung.

### Image bauen (nur bei Änderungen an Dockerfile/requirements.txt)

Um das Docker-Image mit Docker Compose zu bauen oder zu aktualisieren, führe folgenden Befehl im Hauptverzeichnis aus:

```bash
docker-compose build
```

*   Dieser Befehl liest die `docker-compose.yml` und die `Dockerfile`, um das Image `langchain_course` zu erstellen/aktualisieren.
*   Dies ist nur nötig, wenn du die `Dockerfile` oder die `requirements.txt` änderst.

### Skripte im Container ausführen

Verwende `docker-compose run`, um Skripte im `app`-Service (definiert in `docker-compose.yml`) auszuführen. Docker Compose kümmert sich automatisch um das Mounten des Volumes (`.:/app`) für Live-Code-Updates und das Laden der `.env`-Datei für Umgebungsvariablen.

**Standard-Skript ausführen (`main.py`):**

```bash
docker-compose run --rm app
```

*   `--rm`: Entfernt den Container automatisch nach der Ausführung.
*   `app`: Der Name des Services aus der `docker-compose.yml`.

**Ein anderes Skript ausführen (z.B. `1_chat_moddels/1_chat_models_starter.py`):**

```bash
docker-compose run --rm app 1_chat_moddels/1_chat_models_starter.py
```

*   Hier wird der Pfad zum Skript als Befehl an den `app`-Service übergeben.
*   Änderungen an Python-Skripten auf dem Host sind dank des Volumes sofort wirksam. Führe einfach den `docker-compose run`-Befehl erneut aus.

### Andere Befehle im Container ausführen (z.B. `pip`)

Um Befehle auszuführen, die nicht Python-Skripte sind, überschreibe den Standard-Entrypoint:

```bash
docker-compose run --rm --entrypoint="" app pip show <paketname>
```

Oder für alle installierten Pakete:

```bash
docker-compose run --rm --entrypoint="" app pip freeze
```

*   `--entrypoint=""`: Überschreibt den `ENTRYPOINT` für diesen Lauf.
*   `pip show <paketname>` / `pip freeze`: Der eigentliche Befehl.
