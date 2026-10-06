# dlib-face-compare

> [English](README.md) · [中文文档](README.zh.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [Français](README.fr.md) · Deutsch

> Gesichtsvergleich und 1:N-Suche mit **dlib**: Geben Sie zwei Bilder an, um zu prüfen, ob dieselbe Person zu sehen ist, oder ein Bild und einen Ordner, um alle Bilder im Ordner nach Ähnlichkeit zu sortieren.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-20.x-0B72B9?logo=dlib&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Inhaltsverzeichnis

- [1. Voraussetzungen](#1-voraussetzungen)
- [2. Projekt holen und Abhängigkeiten installieren](#2-projekt-holen-und-abhängigkeiten-installieren)
- [3. Gewichtsdateien herunterladen](#3-gewichtsdateien-herunterladen)
- [4. Verwendung](#4-verwendung)
- [5. Optionen](#5-optionen)
- [6. Referenz zum Abstandsschwellwert](#6-referenz-zum-abstandsschwellwert)
- [7. Projektstruktur](#7-projektstruktur)
- [8. Häufige Fragen](#8-häufige-fragen)

---

## 1. Voraussetzungen

dlib ist eine **C++-Bibliothek**, daher kompiliert `pip install dlib` seine Quellen von Grund auf. Es muss also zuerst eine lauffähige C++-Build-Umgebung vorhanden sein. Sobald die folgenden vier Punkte installiert sind, reduziert sich die Einrichtung auf einen einzigen Befehl.

| Software | Version | Zweck | Downloadseite |
| --- | --- | --- | --- |
| **Python** | 3.8 oder neuer | Führt das Skript aus | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio** | 2019 / 2022 | Liefert den MSVC-Compiler | [Visual Studio Community (kostenlos)](https://visualstudio.microsoft.com/vs/community/) |
| **Visual Studio Installer** | — | Zum Auswählen des C++-Workloads | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) |
| **CMake** | 3.18 oder neuer | Steuert den dlib-Build | [cmake.org/download](https://cmake.org/download/) |

### In Visual Studio auswählen

Nach der Installation von Visual Studio Community muss im **Visual Studio Installer** auf der Seite „Workloads“ Folgendes angehakt sein:

- [x] **Desktopentwicklung mit C++** (*Desktop development with C++*)

Diese eine Auswahl bringt automatisch Folgendes mit, ohne dass Sie danach suchen müssen:

- MSVC v143 Buildtools
- Windows-10/11-SDK
- CMake-Tools (die in Visual Studio enthaltene Version)

> Wer nur Python installiert und dieses Workload nicht auswählt, bekommt bei `pip install dlib` zwangsläufig
> `error: Microsoft Visual C++ 14.0 or greater is required`
> ausgegeben.

Offizielle Microsoft-Dokumentation (Workload- und Komponentendetails):

- Visual Studio installieren: <https://learn.microsoft.com/visualstudio/install/>
- MSVC-Compiler / Toolset: <https://learn.microsoft.com/cpp/build/vscmd>
- Windows-SDK-Übersicht: <https://learn.microsoft.com/windows/win32/winprog/windows-sdk>

### dlib-Ressourcen

- Offizielle Website: <http://dlib.net/>
- Quell-Repository: <https://github.com/davisking/dlib>
- Offizielle Modell-Downloadseite: <http://dlib.net/files/>
- dlib-Gesichtserkennungstutorial (Python-Beispiel): <https://www.dlib.net/face_recognition.py.html>

---

## 2. Projekt holen und Abhängigkeiten installieren

```bash
git clone https://github.com/wangyifan349/dlib-face-compare.git
cd dlib-face-compare
```

dlib installieren (der erste Build dauert **5–15 Minuten**, auf langsameren Rechnern länger):

```bash
pip install dlib
```

Schlägt der Build fehl, installieren Sie die fehlenden Build-Werkzeuge und versuchen es erneut:

```bash
pip install cmake          # installiert das neueste CMake und umgeht ältere Kopien im PATH
pip install dlib --no-cache-dir
```

dlib ist die einzige Abhängigkeit; darüber hinaus wird nichts benötigt.

---

## 3. Gewichtsdateien herunterladen

Legen Sie die drei `.dat`-Dateien in den Ordner `models/` (alle Downloads sind komprimierte `.bz2`-Archive und werden direkt zu `.dat` entpackt):

| Datei | Zweck | Größe | Download |
| --- | --- | --- | --- |
| `dlib_face_recognition_resnet_model_v1.dat` | **Erforderlich**, extrahiert den 128-dimensionalen Merkmalsvektor | 21,4 MB | [dlib.net](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2) |
| `shape_predictor_5_face_landmarks.dat` | **Erforderlich**, 5 Landmarken zum Geraderichten des Gesichts | 9,1 MB | [dlib.net](http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2) |
| `mmod_human_face_detector.dat` | Nur bei `-d cnn` nötig | 0,7 MB | [dlib.net](http://dlib.net/files/mmod_human_face_detector.dat.bz2) |

Die Downloads liegen als `.bz2`-Archive vor. **Der Windows-Explorer unterstützt `.bz2` nicht**, daher per Python entpacken:

```python
import bz2
for name in ("dlib_face_recognition_resnet_model_v1", "shape_predictor_5_face_landmarks", "mmod_human_face_detector"):
    data = bz2.open(f"{name}.dat.bz2", "rb").read()
    open(f"models/{name}.dat", "wb").write(data)
```

---

## 4. Verwendung

```bash
# zwei Bilder vergleichen
python face_compare.py compare a.jpg b.jpg

# 1:N-Suche in einem Ordner, nach Ähnlichkeit absteigend ausgegeben
python face_compare.py search a.jpg ./photos

# CNN-Gesichtsdetektor verwenden (genauer, langsamer)
python face_compare.py -d cnn search a.jpg ./photos

# eigenes Erkennungsmodell verwenden
python face_compare.py -m my_model.dat search a.jpg ./photos
```

Bei jedem Aufruf wird eine Nutzungsübersicht gedruckt. Beispielausgabe des Modus `search`:

```text
 1. 0.0000  query.jpg                          MATCH
 2. 0.0590  person_b.jpg                       MATCH
 3. 0.1790  person_c.jpg                       MATCH
 4. 0.4127  person_d.jpg
 5. 0.7934  person_e.jpg
```

Die Zahl ist die euklidische Distanz — **je kleiner, desto ähnlicher**. Die erste Zeile ist das Abfragebild selbst (immer `0.0000`, wenn dieselbe Datei im Ordner liegt).

---

## 5. Optionen

| Option | Bedeutung | Standard |
| --- | --- | --- |
| `compare` | Modus: zwei Bilder vergleichen, Distanz und Ergebnis ausgeben | — |
| `search` | Modus: ein Bild + ein Ordner, alle bewerten und absteigend sortieren | — |
| `-d hog` | HOG-Detektor, schnell, **keine Gewichtsdatei nötig** | ✅ Standard |
| `-d cnn` | CNN-Detektor (MTCNN-artig), stabiler bei schrägen Winkeln und kleinen Gesichtern, deutlich langsamer | `mmod_human_face_detector.dat` erforderlich |
| `-m <Pfad>` | Eigene Gewichtsdatei für das Erkennungsnetzwerk | `models/dlib_face_recognition_resnet_model_v1.dat` |

Pipeline: `HOG/CNN-Gesichtserkennung` → `5-Punkt-Landmarken` → `Geraderichten und auf 150×150 zuschneiden` → `ResNet-128D-Vektor` → `euklidische Distanz`.

---

## 6. Referenz zum Abstandsschwellwert

Der Standard-Schwellwert dieses Projekts beträgt `0.6` (HOG-Detektor + 5-Punkt-Ausrichtung, ResNet-128):

| Distanz | Beurteilung |
| --- | --- |
| < 0.3 | Sehr wahrscheinlich dieselbe Person |
| 0.3 – 0.6 | Dieselbe Person, von diesem Projekt als **MATCH** gemeldet |
| > 0.6 | Sehr wahrscheinlich nicht dieselbe Person |

In der Praxis sollten Sie diesen Wert mit eigenen Positiv-/Negativpaaren anpassen: Bei zu vielen Fehltreffern verringern, bei zurückgewiesenen echten Treffern erhöhen.

---

## 7. Projektstruktur

```text
dlib-face-compare/
├── face_compare.py              # Hauptprogramm, einzelne Datei
├── README.md                    # englische Dokumentation
├── README.zh.md                 # chinesische Dokumentation
├── README.ko.md                 # koreanische Dokumentation
├── README.ja.md                 # japanische Dokumentation
├── README.fr.md                 # französische Dokumentation
├── README.de.md                 # deutsche Dokumentation
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   └── mmod_human_face_detector.dat
└── test_images/                 # Testbilder (durch eigene Bilder ersetzen)
    ├── 2007_007763.jpg
    ├── 2008_001009.jpg
    └── ...
```

---

## 8. Häufige Fragen

### 1. `RuntimeError: Unable to open ... xxx.dat`

**Der Pfad enthält Nicht-ASCII-Zeichen oder Leerzeichen.** Die C++-Schicht von dlib öffnet Dateien mit schmalen Zeichenketten, daher scheitern Windows-Pfade mit chinesischen, koreanischen oder japanischen Zeichen. Verschieben Sie das Projekt in einen reinen ASCII-Pfad, z. B. `C:\Users\yourname\dlib_face_demo`.

### 2. `error: Microsoft Visual C++ 14.0 or greater is required`

Das Workload **Desktopentwicklung mit C++** ist im Visual Studio Installer nicht ausgewählt.
Installer öffnen → Ändern → dieses Workload ankreuzen → Installieren → neues Terminal öffnen und erneut versuchen.

### 3. `Could not build wheels for dlib` / CMake nicht gefunden

```bash
pip install cmake
pip install dlib --no-cache-dir
```

### 4. Der Build dauert ewig oder der Speicher läuft voll

Eine einzelne dlib-C++-Quelldatei nutzt während der Kompilierung die ganze CPU. Das ist völlig normal – warten Sie einfach die 5 bis 15 Minuten ab.

### 5. HOG oder CNN?

HOG braucht keine Gewichtsdatei und ist schnell, für Porträts und Passfotos ist das ausreichend. CNN ist etwa 10-fach langsamer, dafür aber bei Profilen, Verdeckungen und kleinen Gesichtern wesentlich stabiler. Starten Sie mit HOG, fügen Sie `-d cnn` nur bei Bedarf hinzu.

---

## Danksagung

- [dlib](https://github.com/davisking/dlib) von Davis King — für den HOG/CNN-Gesichtsdetektor, den 5-Punkt-Landmarken-Prädiktor und das ResNet-Erkennungsmodell.
- Die Open-Source-Community — für die vielen kostenlosen Werkzeuge und Ressourcen, die dieses Projekt ermöglicht haben.

## Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Kurz gesagt: Sie dürfen diese Software frei verwenden, kopieren, ändern, zusammenführen, veröffentlichen, verbreiten und sogar verkaufen, solange Sie den ursprünglichen Copyright-Hinweis und diesen Erlaubnisteil beibehalten. Die Software wird "wie sie ist" bereitgestellt, ohne jegliche Gewährleistung.
