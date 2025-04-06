# langchain_crash_course

## Docker Anweisungen

### Image bauen (nur einmalig oder bei Änderungen)

Um das Docker-Image zu bauen, führe folgenden Befehl im Hauptverzeichnis (wo sich die `Dockerfile` befindet) aus:

```bash
docker build -t langchain_course .
```

**Erklärung der Flags:**

*   `docker build`: Der Befehl zum Erstellen eines Docker-Images.
*   `-t langchain_course`: Das `-t` Flag steht für "Tag". Hiermit gibst du dem Image einen Namen (hier `langchain_course`), damit du es später leichter verwenden kannst.
*   `.`: Der Punkt am Ende gibt den sogenannten "Build Context" an. Das ist das Verzeichnis (hier das aktuelle Verzeichnis `.`), in dem sich deine `Dockerfile` und die zu kopierenden Dateien (z.B. deine Python-Skripte) befinden.

### Skripte im Container ausführen

Nachdem das Image gebaut wurde, kannst du Container daraus starten, um deine Python-Skripte auszuführen.

**Grundlegender Ausführungsbefehl (ohne Umgebungsvariablen):**

Der einfachste Weg, das Standard-Skript (`main.py` gemäß `CMD` in der Dockerfile) auszuführen, ist:

```bash
docker run langchain_course
```

Um ein anderes Skript auszuführen:

```bash
docker run langchain_course anderes_skript.py
```

*   Diese Befehle starten jeweils einen Container und führen das angegebene Python-Skript aus. Der Container bleibt danach bestehen, bis er manuell entfernt wird (z.B. mit `docker rm`).
*   Dieser einfache Befehl funktioniert gut, wenn deine Skripte keine externen Konfigurationen wie API-Schlüssel benötigen.

**Ausführung mit Umgebungsvariablen und automatischer Bereinigung (empfohlen für dieses Projekt):**

Wenn dein Skript Umgebungsvariablen benötigt (z.B. API-Schlüssel aus einer `.env`-Datei), solltest du diese sicher übergeben und den Container nach Gebrauch aufräumen.

*Standard-Skript ausführen (`main.py`):*

```bash
docker run --rm --env-file .env langchain_course
```

*Anderes Skript ausführen (z.B. `1_chat_moddels/1_chat_models_starter.py`):*

```bash
docker run --rm --env-file .env langchain_course 1_chat_moddels/1_chat_models_starter.py
```

**Erklärung der zusätzlichen Flags:**

*   `--rm`: Entfernt den Container automatisch, nachdem das Skript beendet wurde. Das verhindert, dass sich viele gestoppte Container ansammeln.
*   `--env-file .env`: Liest Umgebungsvariablen aus der lokalen `.env`-Datei (stelle sicher, dass `.env` in `.dockerignore` steht!) und macht sie im Container verfügbar. Dies ist der sicherste Weg, um sensible Daten wie API-Schlüssel zu übergeben, ohne sie ins Image zu brennen.
*   `langchain_course`: Der Name des verwendeten Images.
*   (Optional) `1_chat_moddels/1_chat_models_starter.py`: Der Pfad zum Skript, das ausgeführt werden soll. Wenn weggelassen, wird das Standard-`CMD` aus der Dockerfile verwendet.

### Andere Befehle im Container ausführen (z.B. `pip`)

Da die `Dockerfile` den `ENTRYPOINT` auf `python` setzt, werden Argumente an `docker run` standardmäßig als auszuführende Python-Skripte interpretiert (`python <argument>`). Wenn du einen anderen Befehl wie `pip show` oder `pip freeze` ausführen möchtest, musst du den Standard-Entrypoint für diesen Lauf überschreiben:

```bash
docker run --rm --entrypoint="" langchain_course pip show <paketname>
```

Oder für alle installierten Pakete:

```bash
docker run --rm --entrypoint="" langchain_course pip freeze
```

**Erklärung:**

*   `--entrypoint=""`: Dieses Flag überschreibt den `ENTRYPOINT ["python"]` aus der `Dockerfile` für diesen speziellen `docker run`-Befehl. Dadurch wird der Befehlsteil nach dem Image-Namen (z.B. `pip show <paketname>`) direkt in der Standard-Shell des Containers ausgeführt, anstatt als Argument an `python` übergeben zu werden.
*   `--rm`: Dieses Flag sorgt dafür, dass der Container nach der Ausführung automatisch entfernt wird. Das ist nützlich für kurze Befehle, bei denen man den Container nicht behalten möchte.
*   `pip show <paketname>` / `pip freeze`: Der eigentliche Befehl, der im Container ausgeführt werden soll.
