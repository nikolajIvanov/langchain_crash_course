# Docker Konzepte erklärt: Dockerfile vs. docker run vs. Docker Compose

Dieses Dokument soll helfen, die Rollen der verschiedenen Docker-Komponenten zu verstehen, insbesondere im Kontext der Entwicklung.

## 1. Dockerfile: Die Bauanleitung für das Image

*   **Zweck:** Eine `Dockerfile` ist eine Textdatei, die Anweisungen enthält, wie ein **Docker-Image** Schritt für Schritt gebaut werden soll.
*   **Was sie tut:** Sie definiert das Basis-Image (z.B. `python:3.11-slim`), kopiert notwendige Dateien (Anwendungscode, Konfigurationsdateien wie `requirements.txt`), installiert Abhängigkeiten (`pip install`) und legt Standardeinstellungen wie das Arbeitsverzeichnis (`WORKDIR`), freigegebene Ports (`EXPOSE`, hier nicht verwendet) und den Standard-Startbefehl (`ENTRYPOINT`, `CMD`) fest.
*   **Ergebnis:** Ein **Image**. Ein Image ist eine unveränderliche Vorlage (Snapshot), die alles Nötige enthält, um deine Anwendung auszuführen. Es ist portabel und kann auf jedem System mit Docker ausgeführt werden.
*   **Befehl:** `docker build`

## 2. docker run: Starten eines Containers aus einem Image

*   **Zweck:** Der `docker run`-Befehl nimmt ein vorhandenes **Image** und startet daraus einen laufenden **Container**.
*   **Was er tut:** Er erstellt eine isolierte Umgebung (den Container) basierend auf dem Image. Beim Starten können zahlreiche **Laufzeitkonfigurationen** über Flags angepasst werden, die *nicht* Teil des Images selbst sind:
    *   **Port-Mapping (`-p`):** Verbindet Ports des Containers mit Ports des Host-Rechners.
    *   **Volume Mounts (`-v`):** Verbindet Verzeichnisse des Host-Rechners mit Verzeichnissen im Container.
    *   **Umgebungsvariablen (`-e`, `--env-file`):** Übergibt Konfigurationswerte oder Geheimnisse.
    *   **Überschreiben von `CMD`/`ENTRYPOINT`:** Startet einen anderen Befehl als den im Image definierten Standard.
    *   **Automatische Bereinigung (`--rm`):** Löscht den Container nach Beendigung.
*   **Ergebnis:** Ein laufender **Container**, eine Instanz des Images, mit potenziell angepasster Laufzeitkonfiguration.

### Beispielhafte `docker run`-Befehle (Vor Docker Compose)

Die folgenden Beispiele zeigen, wie Skripte *vor* der Einführung von Docker Compose ausgeführt wurden. **Die aktuelle, empfohlene Methode mit `docker-compose run` findest du in der `README.md`.** Diese Beispiele dienen dem Verständnis der Entwicklung und der Komplexität, die Docker Compose reduziert:

*   **Ganz einfach (funktioniert nur, wenn keine Volumes/Env-Vars nötig & Code im Image aktuell):**
    ```bash
    # Baue das Image zuerst: docker build -t langchain_course .
    docker run langchain_course 1_chat_moddels/1_chat_models_starter.py
    ```

*   **Mit Umgebungsvariablen (aber ohne Live-Code-Updates durch Volumes):**
    ```bash
    # Baue das Image zuerst: docker build -t langchain_course .
    docker run --rm --env-file .env langchain_course 1_chat_moddels/1_chat_models_starter.py
    ```
    *Hier müssten Code-Änderungen immer noch einen `docker build` erfordern.* 

*   **Mit Umgebungsvariablen UND Volume für Live-Code-Updates (komplexer Befehl):**
    ```bash
    # Baue das Image nur bei Dockerfile/requirements-Änderung: docker build -t langchain_course .
    docker run --rm --env-file .env -v $(pwd):/app langchain_course 1_chat_moddels/1_chat_models_starter.py
    ```
    *Dies ermöglichte Live-Updates, erforderte aber die manuelle Angabe aller Flags.*

*   **Ausführen anderer Befehle (z.B. `pip`):**
    ```bash
    docker run --rm --entrypoint="" langchain_course pip freeze
    ```

**Man sieht, dass die `docker run`-Befehle schnell lang und unhandlich werden können, besonders mit Volumes und Umgebungsvariablen. Genau hier setzt Docker Compose an.**

## 3. Docker Compose: Orchestrierung von Multi-Container-Anwendungen (und Vereinfachung für einzelne)

*   **Zweck:** Docker Compose ist ein Werkzeug, um Anwendungen zu definieren und auszuführen, die aus **mehreren Containern** bestehen (z.B. ein Webserver, eine Datenbank, ein Caching-Dienst). Es vereinfacht aber auch erheblich die Konfiguration und Ausführung von **einzelnen Containern**, besonders während der Entwicklung.
*   **Was es tut:** Man definiert die Services (Container), Netzwerke und Volumes in einer **`docker-compose.yml`**-Datei. Diese Datei beschreibt zentral viele der Laufzeitkonfigurationen, die man sonst `docker run` über Flags mitgeben müsste:
    *   Welches Image verwendet/gebaut werden soll (`build`, `image`).
    *   Port-Mappings (`ports`).
    *   **Volume Mounts (`volumes`)**: Definiert die Verbindung zwischen Host und Container.
    *   Umgebungsvariablen (`environment`, `env_file`).
    *   Abhängigkeiten zwischen Services (`depends_on`).
*   **Ergebnis:** Eine einfachere Möglichkeit, komplexe (oder auch einfache) Anwendungen zu starten, zu stoppen und zu verwalten.
*   **Befehle:** `docker-compose build`, `docker-compose up`, `docker-compose down`, `docker-compose run`.

### Wichtiger Hinweis zu `docker-compose run`

Es ist wichtig zu verstehen, dass **`docker-compose run` immer einen *neuen* Container startet**, wenn du den Befehl ausführst. Er verwendet keinen alten, gestoppten Container wieder.

*   Das `--rm`-Flag beeinflusst nur, ob dieser *neu erstellte* Container nach der Ausführung automatisch **gelöscht** wird.
*   Ohne `--rm` wird der neu erstellte Container nach der Ausführung **gestoppt**, aber **nicht gelöscht** und sammelt sich auf deinem System an.
*   Dieses Verhalten ist ideal für Einmal-Aufgaben wie das Ausführen von Skripten oder Tests, bei denen man eine frische Umgebung wünscht.

## Warum kann man kein Host-Volume in der Dockerfile binden?

Die `Dockerfile` dient dazu, ein **portables, eigenständiges Image** zu erstellen. Ein Image soll auf *jedem* Docker-Host laufen können.

Ein **Host-Pfad** (wie `/Users/nikolajivanov/...` oder `$(pwd)`) ist aber spezifisch für den Rechner, auf dem das Image *später* ausgeführt wird. Diesen fest in die `Dockerfile` zu schreiben würde:

1.  **Die Portabilität zerstören:** Das Image würde nur auf deinem Rechner funktionieren (oder einem mit exakt gleicher Verzeichnisstruktur).
2.  **Gegen das Prinzip verstoßen:** Die `Dockerfile` beschreibt den *Inhalt* des Images, nicht die *Interaktion mit einem spezifischen Host-System zur Laufzeit*.

Die `VOLUME`-Anweisung in der Dockerfile deklariert nur, dass ein bestimmter Pfad *im Container* für Volumes vorgesehen ist, sie legt aber keine Verbindung zu einem Host-Pfad fest.

**Docker Compose löst das Problem:** Die `docker-compose.yml` ist explizit dafür da, die **Laufzeitkonfiguration** zu beschreiben, wie die Container auf einem Host gestartet werden sollen. Daher ist es der richtige Ort, um die Verknüpfung zwischen einem Host-Verzeichnis (`.` oder `$(pwd)`) und einem Container-Verzeichnis (`/app`) über das `volumes`-Schlüsselwort herzustellen. 