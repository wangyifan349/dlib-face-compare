# dlib-face-compare

> [English](README.md) · [中文文档](README.zh.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · Français · [Deutsch](README.de.md)

> Comparaison de visages et recherche 1:N avec **dlib** : donnez deux images pour savoir s'il s'agit de la même personne, ou une image plus un dossier pour classer toutes les images du dossier par similarité.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-20.x-0B72B9?logo=dlib&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Sommaire

- [1. Prérequis](#1-prérequis)
- [2. Récupérer le projet et installer les dépendances](#2-récupérer-le-projet-et-installer-les-dépendances)
- [3. Télécharger les fichiers de poids](#3-télécharger-les-fichiers-de-poids)
- [4. Utilisation](#4-utilisation)
- [5. Options](#5-options)
- [6. Référence du seuil de distance](#6-référence-du-seuil-de-distance)
- [7. Structure du projet](#7-structure-du-projet)
- [8. FAQ](#8-faq)

---

## 1. Prérequis

dlib est une **bibliothèque C++** : `pip install dlib` compile ses sources depuis zéro. Il faut donc au préalable disposer d'un environnement de compilation C++. Une fois les quatre éléments ci-dessous installés, l'installation tient sur une seule commande.

| Logiciel | Version | Rôle | Page de téléchargement |
| --- | --- | --- | --- |
| **Python** | 3.8 ou plus récent | Exécute le script | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio** | 2019 / 2022 | Fournit le compilateur MSVC | [Visual Studio Community (gratuit)](https://visualstudio.microsoft.com/vs/community/) |
| **Visual Studio Installer** | — | Sélectionne la charge de travail C++ | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) |
| **CMake** | 3.18 ou plus récent | Pilote la compilation de dlib | [cmake.org/download](https://cmake.org/download/) |

### Que sélectionner dans Visual Studio

Après l'installation de Visual Studio Community, dans **Visual Studio Installer** de la page « Charges de travail », cochez impérativement :

- [x] **Développement Desktop en C++** (*Desktop development with C++*)

Ce seul choix inclut automatiquement, sans recherche supplémentaire :

- Outils de build MSVC v143
- SDK Windows 10/11
- Outils CMake (version intégrée à Visual Studio)

> N'installer que Python sans cette charge entraîne à coup sûr l'erreur
> `error: Microsoft Visual C++ 14.0 or greater is required`
> lors de l'exécution de `pip install dlib`.

Documentation Microsoft officielle (détails des charges et composants) :

- Installer Visual Studio : <https://learn.microsoft.com/visualstudio/install/>
- Compilateur / outillage MSVC : <https://learn.microsoft.com/cpp/build/vscmd>
- Présentation du SDK Windows : <https://learn.microsoft.com/windows/win32/winprog/windows-sdk>

### Ressources dlib

- Site officiel : <http://dlib.net/>
- Dépôt source : <https://github.com/davisking/dlib>
- Page officielle de téléchargement des modèles : <http://dlib.net/files/>
- Tutoriel de reconnaissance faciale dlib (exemple Python) : <https://www.dlib.net/face_recognition.py.html>

---

## 2. Récupérer le projet et installer les dépendances

```bash
git clone https://github.com/wangyifan349/dlib-face-compare.git
cd dlib-face-compare
```

Installez dlib (la première compilation prend **5 à 15 minutes**, davantage sur une machine lente) :

```bash
pip install dlib
```

Si la compilation échoue, installez les outils de build manquants puis réessayez :

```bash
pip install cmake          # installe la dernière version, en ignorant les anciennes copies dans PATH
pip install dlib --no-cache-dir
```

dlib est la seule dépendance ; rien d'autre n'est requis.

---

## 3. Télécharger les fichiers de poids

Placez les trois fichiers `.dat` dans le dossier `models/` (chaque téléchargement est une archive `.bz2` qui s'extrait directement en `.dat`) :

| Fichier | Rôle | Taille | Téléchargement |
| --- | --- | --- | --- |
| `dlib_face_recognition_resnet_model_v1.dat` | **Requis**, extrait le vecteur 128-D | 21,4 Mo | [dlib.net](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2) |
| `shape_predictor_5_face_landmarks.dat` | **Requis**, 5 points de repère pour redresser le visage | 9,1 Mo | [dlib.net](http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2) |
| `mmod_human_face_detector.dat` | Nécessaire uniquement avec `-d cnn` | 0,7 Mo | [dlib.net](http://dlib.net/files/mmod_human_face_detector.dat.bz2) |

Les téléchargements sont des archives `.bz2`. **L'explorateur Windows ne prend pas en charge `.bz2`** : décompressez-les donc avec Python pour obtenir les `.dat` :

```python
import bz2
for name in ("dlib_face_recognition_resnet_model_v1", "shape_predictor_5_face_landmarks", "mmod_human_face_detector"):
    data = bz2.open(f"{name}.dat.bz2", "rb").read()
    open(f"models/{name}.dat", "wb").write(data)
```

---

## 4. Utilisation

```bash
# comparer deux images
python face_compare.py compare a.jpg b.jpg

# recherche 1:N dans un dossier, affiché de la plus proche à la plus éloignée
python face_compare.py search a.jpg ./photos

# utiliser le détecteur CNN (plus précis, plus lent)
python face_compare.py -d cnn search a.jpg ./photos

# utiliser un modèle de reconnaissance personnalisé
python face_compare.py -m my_model.dat search a.jpg ./photos
```

Une bannière d'utilisation s'affiche à chaque exécution. Exemple de sortie du mode `search` :

```text
 1. 0.0000  query.jpg                          MATCH
 2. 0.0590  person_b.jpg                       MATCH
 3. 0.1790  person_c.jpg                       MATCH
 4. 0.4127  person_d.jpg
 5. 0.7934  person_e.jpg
```

Le nombre est la distance euclidienne : **plus il est petit, plus les visages se ressemblent**. La première ligne est l'image recherchée elle-même (toujours `0.0000` si le même fichier figure dans le dossier).

---

## 5. Options

| Option | Signification | Défaut |
| --- | --- | --- |
| `compare` | Mode : compare deux images, affiche la distance et le verdict | — |
| `search` | Mode : une image + un dossier, toutes les images sont notées et triées par ordre décroissant | — |
| `-d hog` | Détecteur HOG, rapide, **aucun fichier de poids requis** | ✅ par défaut |
| `-d cnn` | Détecteur CNN (type MTCNN), plus stable sur angles décalés et petits visages, beaucoup plus lent | nécessite `mmod_human_face_detector.dat` |
| `-m <chemin>` | Fichier de poids personnalisé pour le réseau de reconnaissance | `models/dlib_face_recognition_resnet_model_v1.dat` |

Pipeline : `détection faciale HOG/CNN` → `5 points de repère` → `redressement et rognage à 150×150` → `vecteur 128-D (ResNet)` → `distance euclidienne`.

---

## 6. Référence du seuil de distance

Le seuil par défaut de ce projet est `0.6` (détecteur HOG + alignement 5 points, ResNet-128) :

| Distance | Verdict |
| --- | --- |
| < 0.3 | Très probablement la même personne |
| 0.3 – 0.6 | Même personne, signalé comme **MATCH** par ce projet |
| > 0.6 | Très probablement une personne différente |

En production, ajustez cette valeur avec vos propres paires positives/négatives : diminuez-la pour réduire les faux positifs, augmentez-la si de vrais matchs sont rejetés.

---

## 7. Structure du projet

```text
dlib-face-compare/
├── face_compare.py              # programme principal, un seul fichier
├── README.md                    # documentation en anglais
├── README.zh.md                 # documentation en chinois
├── README.ko.md                 # documentation en coréen
├── README.ja.md                 # documentation en japonais
├── README.fr.md                 # documentation en français
├── README.de.md                 # documentation en allemand
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   └── mmod_human_face_detector.dat
└── test_images/                 # photos de test (remplacez-les par les vôtres)
    ├── 2007_007763.jpg
    ├── 2008_001009.jpg
    └── ...
```

---

## 8. FAQ

### 1. `RuntimeError: Unable to open ... xxx.dat`

**Le chemin contient des caractères non-ASCII ou des espaces.** La couche C++ de dlib ouvre les fichiers avec des chaînes de caractères étroites, ce qui échoue immédiatement pour les chemins Windows contenant des caractères chinois, coréens ou japonais. Déplacez le projet vers un chemin purement ASCII, par ex. `C:\Users\yourname\dlib_face_demo`.

### 2. `error: Microsoft Visual C++ 14.0 or greater is required`

La charge **Développement Desktop en C++** n'est pas cochée dans Visual Studio Installer.
Ouvrez l'installateur → Modifier → cochez cette charge → Installer → ouvrez un nouveau terminal puis réessayez.

### 3. `Could not build wheels for dlib` / CMake introuvable

```bash
pip install cmake
pip install dlib --no-cache-dir
```

### 4. La compilation est très lente ou manque de mémoire

Un seul fichier source C++ de dlib accapare tout le CPU pendant la compilation. C'est normal — comptez 5 à 15 minutes.

### 5. HOG ou CNN ?

HOG ne requiert aucun fichier de poids et est rapide, suffisant pour les portraits et photos d'identité. CNN est environ 10 fois plus lent mais beaucoup plus stable en profil, occlusion ou petits visages. Commencez avec HOG, ajoutez `-d cnn` en cas de besoin.

---

## License

MIT
