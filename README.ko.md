# dlib-face-compare

> [English](README.md) · [中文文档](README.zh.md) · 한국어 · [日本語](README.ja.md) · [Français](README.fr.md) · [Deutsch](README.de.md)

> **dlib** 기반 얼굴 비교 및 1:N 검색: 두 이미지를 주면 같은 사람인지 판단하고, 한 이미지와 폴더를 주면 폴더 안의 모든 이미지를 유사도 순으로 정렬합니다.

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-20.x-0B72B9?logo=dlib&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 목차

- [1. 사전 준비](#1-사전-준비)
- [2. 프로젝트 가져오기 및 의존성 설치](#2-프로젝트-가져오기-및-의존성-설치)
- [3. 가중치 파일 다운로드](#3-가중치-파일-다운로드)
- [4. 실행](#4-실행)
- [5. 옵션](#5-옵션)
- [6. 거리 임계값 참고](#6-거리-임계값-참고)
- [7. 프로젝트 구조](#7-프로젝트-구조)
- [8. 자주 묻는 질문](#8-자주-묻는-질문)

---

## 1. 사전 준비

dlib은 **C++ 라이브러리**이므로 `pip install dlib`은 소스에서부터 컴파일합니다. 따라서 먼저 C++ 빌드 도구가 설치되어 있어야 하며, 아래 네 가지를 모두 설치하면 이후 설치는 한 줄의 명령으로 끝납니다.

| 소프트웨어 | 버전 | 용도 | 다운로드 페이지 |
| --- | --- | --- | --- |
| **Python** | 3.8 이상 | 스크립트 실행 | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio** | 2019 / 2022 | MSVC 컴파일러 제공 | [Visual Studio Community (무료)](https://visualstudio.microsoft.com/vs/community/) |
| **Visual Studio Installer** | — | C++ 워크로드 선택 | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) |
| **CMake** | 3.18 이상 | dlib 빌드 구동 | [cmake.org/download](https://cmake.org/download/) |

### Visual Studio에서 선택해야 하는 것

Visual Studio Community 설치 후, **Visual Studio Installer**의 「작업 부하」 페이지에서 반드시 다음 항목을 체크하세요.

- [x] **C++를 사용한 데스크톱 개발** (*Desktop development with C++*)

이 한 항목을 선택하면 아래가 자동으로 포함되어 별도로 찾을 필요가 없습니다.

- MSVC v143 빌드 도구
- Windows 10/11 SDK
- CMake 도구 (Visual Studio 내장)

> Python만 설치하고 이 작업 부하를 선택하지 않으면, `pip install dlib` 실행 시 반드시
> `error: Microsoft Visual C++ 14.0 or greater is required`
> 오류가 발생합니다.

공식 Microsoft 문서 (작업 부하 및 구성 요소 세부 정보):

- Visual Studio 설치: <https://learn.microsoft.com/visualstudio/install/>
- MSVC 컴파일러 / 도구 집합: <https://learn.microsoft.com/cpp/build/vscmd>
- Windows SDK 개요: <https://learn.microsoft.com/windows/win32/winprog/windows-sdk>

### dlib 자료

- 공식 사이트: <http://dlib.net/>
- 소스 저장소: <https://github.com/davisking/dlib>
- 공식 모델 다운로드 페이지: <http://dlib.net/files/>
- dlib 얼굴 인식 튜토리얼 (Python 예제): <https://www.dlib.net/face_recognition.py.html>

---

## 2. 프로젝트 가져오기 및 의존성 설치

```bash
git clone https://github.com/wangyifan349/dlib-face-compare.git
cd dlib-face-compare
```

dlib 설치 (처음 빌드하는 데 **5~15분**이 소요되며, 사양이 낮을수록 더 걸립니다):

```bash
pip install dlib
```

빌드가 실패하면 필요한 빌드 도구를 설치한 뒤 다시 시도하세요.

```bash
pip install cmake          # PATH에 있는 이전 CMake를 무시하고 최신 버전을 설치
pip install dlib --no-cache-dir
```

의존성은 dlib뿐이며, 다른 패키지는 필요하지 않습니다.

---

## 3. 가중치 파일 다운로드

세 개의 `.dat` 파일을 `models/` 폴더에 넣으세요 (모두 `.bz2` 압축 파일이며, 압축을 풀면 바로 `.dat`가 됩니다).

| 파일 | 용도 | 크기 | 다운로드 |
| --- | --- | --- | --- |
| `dlib_face_recognition_resnet_model_v1.dat` | **필수**, 128차원 특징 벡터 추출 | 21.4 MB | [dlib.net](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2) |
| `shape_predictor_5_face_landmarks.dat` | **필수**, 얼굴을 바로잡기 위한 5점 랜드마크 | 9.1 MB | [dlib.net](http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2) |
| `mmod_human_face_detector.dat` | `-d cnn` 사용 시에만 필요 | 0.7 MB | [dlib.net](http://dlib.net/files/mmod_human_face_detector.dat.bz2) |

다운로드된 파일은 `.bz2` 압축 파일입니다. **Windows 탐색기는 `.bz2`를 지원하지 않으므로** Python으로 풀어 `.dat`로 저장하세요.

```python
import bz2
for name in ("dlib_face_recognition_resnet_model_v1", "shape_predictor_5_face_landmarks", "mmod_human_face_detector"):
    data = bz2.open(f"{name}.dat.bz2", "rb").read()
    open(f"models/{name}.dat", "wb").write(data)
```

---

## 4. 실행

```bash
# 두 이미지 비교
python face_compare.py compare a.jpg b.jpg

# 1:N 폴더 검색, 유사도가 높은 순으로 출력
python face_compare.py search a.jpg ./photos

# CNN 얼굴 검출기 사용 (정확하지만 느림)
python face_compare.py -d cnn search a.jpg ./photos

# 사용자 지정 인식 모델 사용
python face_compare.py -m my_model.dat search a.jpg ./photos
```

실행할 때마다 사용법이 출력됩니다. `search` 모드의 출력 예:

```text
 1. 0.0000  query.jpg                          MATCH
 2. 0.0590  person_b.jpg                       MATCH
 3. 0.1790  person_c.jpg                       MATCH
 4. 0.4127  person_d.jpg
 5. 0.7934  person_e.jpg
```

숫자는 유클리드 거리이며, **작을수록 더 유사**합니다. 첫 번째 줄은 쿼리 이미지 자신입니다 (같은 파일이 폴더에 있으면 항상 `0.0000`).

---

## 5. 옵션

| 옵션 | 의미 | 기본값 |
| --- | --- | --- |
| `compare` | 모드: 두 이미지를 비교하고 거리와 판정을 출력 | — |
| `search` | 모드: 한 이미지와 폴더를 받아 모두 채점해 내림차순 정렬 | — |
| `-d hog` | HOG 검출기, 빠르고 **가중치 파일 불필요** | ✅ 기본값 |
| `-d cnn` | CNN (MTCNN 계열) 검출기, 각도가 틀어지거나 작은 얼굴에 더 안정적, 훨씬 느림 | `mmod_human_face_detector.dat` 필요 |
| `-m <경로>` | 사용자 지정 인식 네트워크 가중치 파일 | `models/dlib_face_recognition_resnet_model_v1.dat` |

파이프라인: `HOG/CNN 얼굴 검출` → `5점 랜드마크` → `곧게 펴서 150×150으로 잘라냄` → `ResNet 128차원 벡터` → `유클리드 거리`.

---

## 6. 거리 임계값 참고

이 프로젝트의 기본 임계값은 `0.6`입니다 (HOG 검출기 + 5점 정렬, ResNet-128):

| 거리 | 판정 |
| --- | --- |
| < 0.3 | 거의 확실하게 같은 사람 |
| 0.3 – 0.6 | 같은 사람, 본 프로젝트에서는 **MATCH**로 표시 |
| > 0.6 | 같은 사람이 아닐 가능성이 높음 |

실제 환경에서는 직접 수집한 양성/음성 샘플로 이 값을 조정하세요. 오탐이 많으면 낮추고, 정상 매칭을 놓치면 높이세요.

---

## 7. 프로젝트 구조

```text
dlib-face-compare/
├── face_compare.py              # 메인 프로그램, 단일 파일
├── README.md                    # 영문 문서
├── README.zh.md                 # 중문 문서
├── README.ko.md                 # 한국어 문서
├── README.ja.md                 # 일문 문서
├── README.fr.md                 # 프랑스어 문서
├── README.de.md                 # 독일어 문서
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   └── mmod_human_face_detector.dat
└── test_images/                 # 테스트 이미지 (본인 이미지로 교체 가능)
    ├── 2007_007763.jpg
    ├── 2008_001009.jpg
    └── ...
```

---

## 8. 자주 묻는 질문

### 1. `RuntimeError: Unable to open ... xxx.dat`

**경로에 비ASCII 문자나 공백이 포함되어 있습니다.** dlib의 C++ 계층은 좁은 문자 문자열로 파일을 열기 때문에, 한글/한자/일본어가 포함된 Windows 경로에서는 바로 실패합니다. `C:\Users\yourname\dlib_face_demo`처럼 순수 ASCII 경로로 옮기세요.

### 2. `error: Microsoft Visual C++ 14.0 or greater is required`

Visual Studio Installer에서 **C++를 사용한 데스크톱 개발** 작업 부하가 선택되지 않았습니다.
인스톨러 열기 → 수정 → 해당 작업 부하에 체크 → 설치 → 새 터미널을 열고 다시 시도하세요.

### 3. `Could not build wheels for dlib` / CMake를 찾을 수 없음

```bash
pip install cmake
pip install dlib --no-cache-dir
```

### 4. 빌드가 매우 느리거나 메모리 부족

dlib 컴파일 시 단일 C++ 소스 파일이 CPU 전체를 사용합니다. 정상적인 현상이므로 5~15분 정도 기다려 주세요.

### 5. HOG와 CNN 중 무엇을 쓸까요?

HOG는 가중치 파일 없이 빠르며, 증명사진이나 정면 인물 사진에는 충분합니다. CNN은 약 10배 느리지만 측면, 가림, 작은 얼굴에서 훨씬 안정적입니다. HOG로 먼저 시작하고, 필요할 때만 `-d cnn`을 추가하세요.

---

## 감사의 말

- Davis King의 [dlib](https://github.com/davisking/dlib) —— HOG/CNN 얼굴 검출기, 5점 랜드마크 예측기, ResNet 인식 모델을 제공합니다.
- 오픈소스 커뮤니티 —— 무료 도구와 리소스를 제공해 주신 덕분에 이 프로젝트가 가능했습니다.

## 라이선스

이 프로젝트는 **MIT 라이선스**를 따릅니다. 간단히 말해, 원본 저작권 표시와 본 고지문을 유지하는 한, 본 소프트웨어를 상업적 용도를 포함해 자유롭게 사용, 복제, 수정, 병합, 배포, 판매할 수 있습니다. 소프트웨어는 "있는 그대로" 제공되며 어떠한 보증도 하지 않습니다.
