# dlib-face-compare

> English · [中文文档](README.zh.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [Français](README.fr.md) · [Deutsch](README.de.md)

> Face comparison and 1:N retrieval powered by **dlib**: give it two images to tell whether they show the same person, or give it one image plus a folder to rank every image in that folder by similarity.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-20.x-0B72B9?logo=dlib&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Table of contents

- [1. Prerequisites](#1-prerequisites)
- [2. Get the project and install dependencies](#2-get-the-project-and-install-dependencies)
- [3. Download the weight files](#3-download-the-weight-files)
- [4. Usage](#4-usage)
- [5. Options](#5-options)
- [6. Distance threshold reference](#6-distance-threshold-reference)
- [7. Project structure](#7-project-structure)
- [8. FAQ](#8-faq)

---

## 1. Prerequisites

dlib is a **C++ library**, so `pip install dlib` compiles its sources from scratch. A working C++ toolchain therefore has to be in place first. Once all four items below are installed, installation becomes a single command.

| Software | Version | Purpose | Download page |
| --- | --- | --- | --- |
| **Python** | 3.8 or newer | Runs the script | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio** | 2019 / 2022 | Provides the MSVC compiler | [Visual Studio Community (free)](https://visualstudio.microsoft.com/vs/community/) |
| **Visual Studio Installer** | — | Lets you pick the C++ workload | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) |
| **CMake** | 3.18 or newer | Drives the dlib build | [cmake.org/download](https://cmake.org/download/) |

### What to tick in Visual Studio

After installing Visual Studio Community, the **Visual Studio Installer** `Workloads` page must include this one:

- [x] **Desktop development with C++**

Selecting it automatically pulls in, so you do not need to hunt them down separately:

- MSVC v143 build tools
- Windows 10/11 SDK
- CMake tools (the bundled copy inside Visual Studio)

> Installing only Python without this workload guarantees
> `error: Microsoft Visual C++ 14.0 or greater is required`
> when you run `pip install dlib`.

Official Microsoft documentation (workload and component details):

- Install Visual Studio: <https://learn.microsoft.com/visualstudio/install/>
- MSVC compiler / toolset: <https://learn.microsoft.com/cpp/build/vscmd>
- Windows SDK overview: <https://learn.microsoft.com/windows/win32/winprog/windows-sdk>

### dlib resources

- Official site: <http://dlib.net/>
- Source repository: <https://github.com/davisking/dlib>
- Official model download page: <http://dlib.net/files/>
- dlib face recognition tutorial (Python example): <https://www.dlib.net/face_recognition.py.html>

---

## 2. Get the project and install dependencies

```bash
git clone https://github.com/wangyifan349/dlib-face-compare.git
cd dlib-face-compare
```

> The repository on GitHub is named `dlib-face-compare`.

Install dlib (the first build takes **5–15 minutes**, longer on slower machines):

```bash
pip install dlib
```

If the build fails, install the missing build tools and retry:

```bash
pip install cmake          # install the latest CMake, bypassing older copies in PATH
pip install dlib --no-cache-dir
```

dlib is the only dependency; nothing else is required.

---

## 3. Download the weight files

Put the three `.dat` files into the `models/` folder (each download is a `.bz2` archive that unpacks straight into a `.dat`):

| File | Purpose | Size | Download |
| --- | --- | --- | --- |
| `dlib_face_recognition_resnet_model_v1.dat` | **Required**, extracts the 128-d feature vector | 21.4 MB | [dlib.net](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2) |
| `shape_predictor_5_face_landmarks.dat` | **Required**, 5 landmarks used to straighten the face | 9.1 MB | [dlib.net](http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2) |
| `mmod_human_face_detector.dat` | Only needed when you use `-d cnn` | 0.7 MB | [dlib.net](http://dlib.net/files/mmod_human_face_detector.dat.bz2) |

The downloads come as `.bz2` archives. **Windows Explorer does not support `.bz2`**, so unpack them with Python:

```python
import bz2
for name in ("dlib_face_recognition_resnet_model_v1", "shape_predictor_5_face_landmarks", "mmod_human_face_detector"):
    data = bz2.open(f"{name}.dat.bz2", "rb").read()
    open(f"models/{name}.dat", "wb").write(data)
```

---

## 4. Usage

```bash
# compare two images
python face_compare.py compare a.jpg b.jpg

# 1:N search inside a folder, printed from most to least similar
python face_compare.py search a.jpg ./photos

# use the CNN face detector (more accurate, slower)
python face_compare.py -d cnn search a.jpg ./photos

# use a custom recognition model
python face_compare.py -m my_model.dat search a.jpg ./photos
```

A usage banner is printed on every run. Sample output of `search` mode:

```text
 1. 0.0000  query.jpg                          MATCH
 2. 0.0590  person_b.jpg                       MATCH
 3. 0.1790  person_c.jpg                       MATCH
 4. 0.4127  person_d.jpg
 5. 0.7934  person_e.jpg
```

The number is the euclidean distance — **the smaller, the more similar**. The first row is the query image itself (always `0.0000` when the same file is part of the folder).

---

## 5. Options

| Option | Meaning | Default |
| --- | --- | --- |
| `compare` | Mode: compare two images, print distance and verdict | — |
| `search` | Mode: one image plus a folder, score everything and sort descending | — |
| `-d hog` | HOG detector, fast, **no weight file needed** | ✅ default |
| `-d cnn` | CNN (MTCNN-style) detector, steadier on odd angles and small faces, much slower | requires `mmod_human_face_detector.dat` |
| `-m <path>` | Custom recognition network weight file | `models/dlib_face_recognition_resnet_model_v1.dat` |

Pipeline: `HOG/CNN face detection` → `5-point landmarks` → `straighten and crop to 150×150` → `ResNet 128-d vector` → `euclidean distance`.

---

## 6. Distance threshold reference

The default threshold of this project is `0.6` (HOG detector + 5-point alignment, ResNet-128):

| Distance | Verdict |
| --- | --- |
| < 0.3 | Almost certainly the same person |
| 0.3 – 0.6 | Same person, reported as **MATCH** by this project |
| > 0.6 | Most likely not the same person |

In a real deployment, tune this value against your own positive and negative pairs: lower it to cut false matches, raise it if genuine matches are being rejected.

---

## 7. Project structure

```text
dlib-face-compare/
├── face_compare.py              # main program, single file
├── README.md                    # English documentation
├── README.zh.md                 # Chinese documentation
├── README.ko.md                 # Korean documentation
├── README.ja.md                 # Japanese documentation
├── README.fr.md                 # French documentation
├── README.de.md                 # German documentation
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   └── mmod_human_face_detector.dat
└── test_images/                 # test photos (replace them with your own)
    ├── 2007_007763.jpg
    ├── 2008_001009.jpg
    └── ...
```

---

## 8. FAQ

### 1. `RuntimeError: Unable to open ... xxx.dat`

**The path contains non-ASCII characters or spaces.** dlib's C++ layer opens files with narrow character strings, which fails outright on Chinese Windows paths. Move the project to a pure ASCII location such as `C:\Users\yourname\dlib_face_demo`.

### 2. `error: Microsoft Visual C++ 14.0 or greater is required`

The **Desktop development with C++** workload is not selected in the Visual Studio Installer.
Open the installer → Modify → tick that workload → Install → open a fresh terminal and retry.

### 3. `Could not build wheels for dlib` / CMake not found

```bash
pip install cmake
pip install dlib --no-cache-dir
```

### 4. The build takes forever or runs out of memory

A single dlib C++ source file saturates the whole CPU during compilation. This is normal — wait the 5–15 minutes.

### 5. HOG or CNN?

HOG needs no weight file and is fast, which is enough for portraits and ID photos. CNN is roughly 10× slower but far steadier on profiles, occlusions and small faces. Start with HOG, add `-d cnn` only if you need it.

---

## Acknowledgements

- [dlib](https://github.com/davisking/dlib) by Davis King — for the HOG/CNN face detector, the 5-point landmark predictor and the ResNet recognition model.
- The open-source community, whose free tools and resources made this project possible.

## License

This project is licensed under the **MIT License**. In short, you may freely use, copy, modify, merge, publish, distribute and even sell this software, as long as you keep the original copyright notice and this permission notice. The software is provided "as is", without any warranty.
