# dlib-face-compare

> [English](README.md) · [中文文档](README.zh.md) · [한국어](README.ko.md) · 日本語 · [Français](README.fr.md) · [Deutsch](README.de.md)

> **dlib** による顔比較と1:N検索：2枚の画像を渡せば同一人物かどうかを判定し、1枚の画像とフォルダを渡せば、フォルダ内のすべての画像を類似度の高い順に並べます。

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-20.x-0B72B9?logo=dlib&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 目次

- [1. 前提条件](#1-前提条件)
- [2. プロジェクトの取得と依存関係のインストール](#2-プロジェクトの取得と依存関係のインストール)
- [3. 重みファイルのダウンロード](#3-重みファイルのダウンロード)
- [4. 使い方](#4-使い方)
- [5. オプション](#5-オプション)
- [6. 距離しきい値の目安](#6-距離しきい値の目安)
- [7. プロジェクト構成](#7-プロジェクト構成)
- [8. よくある質問](#8-よくある質問)

---

## 1. 前提条件

dlibは **C++ライブラリ** であるため、`pip install dlib` はソースから新規にコンパイルします。そのため、先に動作するC++ビルド環境を用意する必要があります。以下の4点をすべてセットアップすれば、あとは1行のコマンドでインストールが完了します。

| ソフトウェア | バージョン | 用途 | ダウンロードページ |
| --- | --- | --- | --- |
| **Python** | 3.8 以降 | スクリプトを実行 | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio** | 2019 / 2022 | MSVCコンパイラを提供 | [Visual Studio Community（無料）](https://visualstudio.microsoft.com/vs/community/) |
| **Visual Studio Installer** | — | C++ワークロードを選択 | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) |
| **CMake** | 3.18 以降 | dlibのビルドを駆動 | [cmake.org/download](https://cmake.org/download/) |

### Visual Studioで選択する項目

Visual Studio Communityのインストール後、**Visual Studio Installer** の「ワークロード」ページで必ず以下にチェックを入れてください。

- [x] **C++ を使用したデスクトップ開発** (*Desktop development with C++*)

この1項目を選ぶと、以下のものが自動的に含まれるため、個別に探す必要はありません。

- MSVC v143 ビルドツール
- Windows 10/11 SDK
- CMake ツール (Visual Studioに同梱)

> Pythonだけをインストールしてこのワークロードを選ばなかった場合、`pip install dlib` 実行時に必ず
> `error: Microsoft Visual C++ 14.0 or greater is required`
> というエラーが出ます。

Microsoft公式ドキュメント（ワークロードとコンポーネントの詳細）:

- Visual Studioのインストール: <https://learn.microsoft.com/visualstudio/install/>
- MSVCコンパイラ / ツールセット: <https://learn.microsoft.com/cpp/build/vscmd>
- Windows SDK 概要: <https://learn.microsoft.com/windows/win32/winprog/windows-sdk>

### dlib 関連リンク

- 公式サイト: <http://dlib.net/>
- ソースリポジトリ: <https://github.com/davisking/dlib>
- 公式モデルダウンロードページ: <http://dlib.net/files/>
- dlib 顔認識チュートリアル (Python例): <https://www.dlib.net/face_recognition.py.html>

---

## 2. プロジェクトの取得と依存関係のインストール

```bash
git clone https://github.com/wangyifan349/dlib-face-compare.git
cd dlib-face-compare
```

dlibをインストールします（初回ビルドは **5〜15分** かかり、低スペックなマシンではさらに時間がかかります）。

```bash
pip install dlib
```

ビルドに失敗した場合は、不足しているビルドツールを補ってから再試行してください。

```bash
pip install cmake          # PATHに残っている古いCMakeを回避して最新版をインストール
pip install dlib --no-cache-dir
```

依存パッケージはdlibのみで、他のパッケージは不要です。

---

## 3. 重みファイルのダウンロード

3つの `.dat` ファイルを `models/` フォルダに置きます（ダウンロードされるのはすべて `.bz2` 圧縮アーカイブで、展開するとそのまま `.dat` になります）。

| ファイル | 用途 | サイズ | ダウンロード |
| --- | --- | --- | --- |
| `dlib_face_recognition_resnet_model_v1.dat` | **必須**、128次元特徴ベクトルを抽出 | 21.4 MB | [dlib.net](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2) |
| `shape_predictor_5_face_landmarks.dat` | **必須**、顔の向きを直すための5点ランドマーク | 9.1 MB | [dlib.net](http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2) |
| `mmod_human_face_detector.dat` | `-d cnn` 使用時のみ必要 | 0.7 MB | [dlib.net](http://dlib.net/files/mmod_human_face_detector.dat.bz2) |

取得したのは `.bz2` 圧縮アーカイブです。**Windowsエクスプローラーは `.bz2` をサポートしていない**ため、Pythonで展開して `.dat` に変換してください。

```python
import bz2
for name in ("dlib_face_recognition_resnet_model_v1", "shape_predictor_5_face_landmarks", "mmod_human_face_detector"):
    data = bz2.open(f"{name}.dat.bz2", "rb").read()
    open(f"models/{name}.dat", "wb").write(data)
```

---

## 4. 使い方

```bash
# 2枚の画像を比較
python face_compare.py compare a.jpg b.jpg

# 1:Nフォルダ検索、類似度の高い順に出力
python face_compare.py search a.jpg ./photos

# CNN顔検出器を使用 (より正確だが低速)
python face_compare.py -d cnn search a.jpg ./photos

# 独自の認識モデルを指定
python face_compare.py -m my_model.dat search a.jpg ./photos
```

実行のたびに使用法が表示されます。`search` モードの出力例：

```text
 1. 0.0000  query.jpg                          MATCH
 2. 0.0590  person_b.jpg                       MATCH
 3. 0.1790  person_c.jpg                       MATCH
 4. 0.4127  person_d.jpg
 5. 0.7934  person_e.jpg
```

この数値はユークリッド距離で、**小さいほど似ている**ことを意味します。1行目はクエリ画像自身です（同じファイルがフォルダ内にある場合は常に `0.0000`）。

---

## 5. オプション

| オプション | 意味 | 既定値 |
| --- | --- | --- |
| `compare` | モード：2枚の画像を比較し、距離と判定を出力 | — |
| `search` | モード：1枚の画像とフォルダを受け取り、全件を採点して降順に並べる | — |
| `-d hog` | HOG検出器、高速、**重みファイル不要** | ✅ 既定 |
| `-d cnn` | CNN (MTCNN系) 検出器、斜め顔や小さな顔に強いが大幅に遅い | `mmod_human_face_detector.dat` が必要 |
| `-m <パス>` | 認識ネットワークの重みファイルを指定 | `models/dlib_face_recognition_resnet_model_v1.dat` |

パイプライン：`HOG/CNNによる顔検出` → `5点ランドマーク` → `顔を正立化して150×150に切り出し` → `ResNetによる128次元ベクトル化` → `ユークリッド距離`。

---

## 6. 距離しきい値の目安

本プロジェクトの既定しきい値は `0.6` です（HOG検出器 + 5点アライメント、ResNet-128）:

| 距離 | 判定 |
| --- | --- |
| < 0.3 | ほぼ確実に同一人物 |
| 0.3 – 0.6 | 同一人物。本プロジェクトでは **MATCH** と表示 |
| > 0.6 | 同一人物ではない可能性が高い |

実運用の際は、実際の正例・負例ペアでこの値を調整してください。誤判定が多い場合は下げ、正常な一致を取りこぼす場合は上げてください。

---

## 7. プロジェクト構成

```text
dlib-face-compare/
├── face_compare.py              # メインプログラム (単一ファイル)
├── README.md                    # 英語版
├── README.zh.md                 # 中国語版
├── README.ko.md                 # 韓国語版
├── README.ja.md                 # 日本語版
├── README.fr.md                 # フランス語版
├── README.de.md                 # ドイツ語版
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   └── mmod_human_face_detector.dat
└── test_images/                 # テスト画像 (お使いの画像に置き換えてください)
    ├── 2007_007763.jpg
    ├── 2008_001009.jpg
    └── ...
```

---

## 8. よくある質問

### 1. `RuntimeError: Unable to open ... xxx.dat`

**パスに非ASCII文字や空白が含まれています。** dlibのC++層は狭義文字列でファイルを開くため、日本語・中国語・韓国語を含むWindowsパスでは失敗します。`C:\Users\yourname\dlib_face_demo` のような純粋なASCIIパスへ移動してください。

### 2. `error: Microsoft Visual C++ 14.0 or greater is required`

Visual Studio Installerで **C++ を使用したデスクトップ開発** ワークロードにチェックが入っていません。
インストーラーを開く → 変更 → 該当ワークロードにチェック → インストール → 新しいターミナルを開いて再試行してください。

### 3. `Could not build wheels for dlib` / CMake が見つからない

```bash
pip install cmake
pip install dlib --no-cache-dir
```

### 4. ビルドが非常に遅い / メモリ不足

dlibのコンパイルでは単一のC++ソースファイルがCPUを使い切ります。これは正常なので、5〜15分ほどお待ちください。

### 5. HOG と CNN、どちらを使うべきですか？

HOGは重みファイル不要で高速、正面の人物写真や証明写真には十分です。CNNは約10倍遅いものの、横顔・遮蔽・小さな顔での精度が大幅に向上します。まずHOGで動作確認し、必要な場合にのみ `-d cnn` を追加してください。

---

## 謝辞

- Davis King 氏の [dlib](https://github.com/davisking/dlib) —— HOG/CNN顔検出器、5点ランドマーク予測器、ResNet認識モデルを提供してくださいました。
- このプロジェクトを実現できたのは、数多くの無償ツールやリソースを提供してくださったオープンソースコミュニティのおかげです。

## ライセンス

本プロジェクトは **MITライセンス** のもとで公開されています。簡単に言えば、原著作権表示と本許諾表示を保持する限り、本ソフトウェアを営利・非営利を問わず自由に使用・複製・改変・統合・公開・頒布・販売できます。ソフトウェアは「現状のまま」提供され、いかなる保証も行われません。
