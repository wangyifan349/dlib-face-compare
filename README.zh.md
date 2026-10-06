# dlib-face-compare

> [English](README.md) · 中文文档 · [한국어](README.ko.md) · [日本語](README.ja.md) · [Français](README.fr.md) · [Deutsch](README.de.md)

> 用 **dlib** 做人脸对比与 1:N 检索：给两张图判断是不是同一个人，或给一张图加一个目录，把目录里的图片按相似度从高到低排好序。

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![dlib](https://img.shields.io/badge/dlib-20.x-0B72B9?logo=dlib&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 目录

- [一、环境准备](#一环境准备)
- [二、获取项目并安装依赖](#二获取项目并安装依赖)
- [三、下载权重文件](#三下载权重文件)
- [四、运行](#四运行)
- [五、参数说明](#五参数说明)
- [六、相似度阈值参考](#六相似度阈值参考)
- [七、项目结构](#七项目结构)
- [八、常见问题](#八常见问题)

---

## 一、环境准备

dlib 是 **C++ 库**，`pip install dlib` 会现场编译源码，所以必须先装好 C++ 编译环境。
下面四个全部装好之后，安装就是一条命令的事。

| 软件 | 版本要求 | 作用 | 下载界面 |
| --- | --- | --- | --- |
| **Python** | 3.8 及以上 | 运行脚本 | [python.org 下载](https://www.python.org/downloads/) |
| **Visual Studio** | 2019 / 2022 | 提供 MSVC 编译器 | [Visual Studio Community（免费）](https://visualstudio.microsoft.com/vs/community/) |
| **Visual Studio Installer** | — | 用于勾选 C++ 工作负荷 | [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) |
| **CMake** | 3.18 及以上 | 驱动 dlib 编译 | [cmake.org 下载](https://cmake.org/download/) |

### Visual Studio 怎么装

安装 Visual Studio Community 后，在 **Visual Studio Installer** 的「工作负荷」页必须勾选：

- [x] **使用 C++ 的桌面开发**（*Desktop development with C++*）

这一个勾选会自动带上，你不需要再单独找：

- MSVC v143 编译工具集
- Windows 10/11 SDK
- CMake 工具（VS 内置版）

> 如果只装 Python 不勾这个工作负荷，`pip install dlib` 必然报
> `error: Microsoft Visual C++ 14.0 or greater is required`。

微软官方文档（可查工作负荷与组件明细）：

- Visual Studio 安装文档：<https://learn.microsoft.com/visualstudio/install/>
- MSVC 编译器 / 工具集：<https://learn.microsoft.com/cpp/build/vscmd>
- Windows SDK 说明：<https://learn.microsoft.com/windows/win32/winprog/windows-sdk>

### dlib 官方

- 官网首页：<http://dlib.net/>
- 源码仓库：<https://github.com/davisking/dlib>
- 官方模型下载页：<http://dlib.net/files/>
- dlib 人脸对比教程（Python 示例）：<https://www.dlib.net/face_recognition.py.html>

---

## 二、获取项目并安装依赖

```bash
git clone https://github.com/wangyifan349/dlib-face-compare.git
cd dlib-face-compare
```

安装 dlib（首次编译需要 **5～15 分钟**，机器越差越久）：

```bash
pip install dlib
```

如果编译报错，先补上构建工具再重试：

```bash
pip install cmake          # 装最新的 CMake，绕开 PATH 里的旧版本
pip install dlib --no-cache-dir
```

只用到 dlib，无其他依赖。

---

## 三、下载权重文件

把三个 `.dat` 放进 `models/` 目录（下载到的都是 `.bz2` 压缩包，解压后直接是 `.dat`）：

| 文件 | 用途 | 大小 | 下载地址 |
| --- | --- | --- | --- |
| `dlib_face_recognition_resnet_model_v1.dat` | **必需**，提取 128 维特征 | 21.4 MB | [dlib.net](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2) |
| `shape_predictor_5_face_landmarks.dat` | **必需**，5 点关键点，用于摆正脸 | 9.1 MB | [dlib.net](http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2) |
| `mmod_human_face_detector.dat` | 仅用 `-d cnn` 时需要 | 0.7 MB | [dlib.net](http://dlib.net/files/mmod_human_face_detector.dat.bz2) |

下载得到的是 `.bz2` 压缩包。**Windows 资源管理器不支持 `.bz2`**，直接用 Python 解压成 `.dat`：

```python
import bz2
for name in ("dlib_face_recognition_resnet_model_v1", "shape_predictor_5_face_landmarks", "mmod_human_face_detector"):
    data = bz2.open(f"{name}.dat.bz2", "rb").read()
    open(f"models/{name}.dat", "wb").write(data)
```

---

## 四、运行

```bash
# 两张图片对比
python face_compare.py compare a.jpg b.jpg

# 1:N 目录搜索，按相似度降序输出
python face_compare.py search a.jpg ./photos

# 换用 CNN 检测器（更准但更慢）
python face_compare.py -d cnn search a.jpg ./photos

# 自定义识别权重文件
python face_compare.py -m my_model.dat search a.jpg ./photos
```

每次运行都会先打印用法说明。示例输出（`search` 模式）：

```text
 1. 0.0000  query.jpg                          MATCH
 2. 0.0590  person_b.jpg                       MATCH
 3. 0.1790  person_c.jpg                       MATCH
 4. 0.4127  person_d.jpg
 5. 0.7934  person_e.jpg
```

数字是欧氏距离，**越小越像**，排第一的是查询图自己（同一张图放在目录里时恒为 `0.0000`）。

---

## 五、参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `compare` | 模式：两张图片对比，输出距离和判定结果 | — |
| `search` | 模式：输入一张图 + 一个目录，全量打分并降序排列 | — |
| `-d hog` | HOG 检测器，速度快，**无需权重文件** | ✅ 默认 |
| `-d cnn` | CNN（MTCNN 类）检测器，复杂角度、小脸更稳，慢很多 | 需 `mmod_human_face_detector.dat` |
| `-m <路径>` | 自定义识别网络权重文件 | `models/dlib_face_recognition_resnet_model_v1.dat` |

识别流程：`HOG/CNN 检测人脸` → `5 点关键点` → `摆正裁剪 150×150` → `ResNet 提取 128 维向量` → `欧氏距离`。

---

## 六、相似度阈值参考

本项目默认阈值为 `0.6`（HOG + 5 点摆正，ResNet-128）：

| 距离 | 判定 |
| --- | --- |
| < 0.3 | 非常确定是同一个人 |
| 0.3 ~ 0.6 | 同一个人，本项目默认判为**匹配** |
| > 0.6 | 大概率不是同一人 |

真实场景建议用自己的正/负样本对调一下这个值：误认太多就调小，认不出就调大。

---

## 七、项目结构

```text
dlib-face-compare/
├── face_compare.py              # 主程序，单文件
├── README.md                    # 英文文档
├── README.zh.md                 # 中文文档
├── README.ko.md                 # 韩文文档
├── README.ja.md                 # 日文文档
├── README.fr.md                 # 法语文档
├── README.de.md                 # 德语文档
├── models/
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   └── mmod_human_face_detector.dat
└── test_images/                 # 测试图片（可自行替换成你的图片）
    ├── 2007_007763.jpg
    ├── 2008_001009.jpg
    └── ...
```

---

## 八、常见问题

### 1. `RuntimeError: Unable to open ... xxx.dat`

**路径里有中文或空格。** dlib 的 C++ 层用窄字符打开文件，Windows 中文路径会直接失败。
把项目放到纯英文路径下，例如 `C:\Users\yourname\dlib_face_demo`。

### 2. `error: Microsoft Visual C++ 14.0 or greater is required`

Visual Studio Installer 里没有勾选 **「使用 C++ 的桌面开发」**。
打开安装器 → 修改 → 勾选该工作负荷 → 安装 → 重开终端重试。

### 3. `Could not build wheels for dlib` / 找不到 CMake

```bash
pip install cmake
pip install dlib --no-cache-dir
```

### 4. 编译卡很久 / 内存不足

dlib 编译时单个 C++ 文件会吃满整颗 CPU，属于正常现象，耐心等 5～15 分钟即可。

### 5. HOG 和 CNN 怎么选

HOG 免权重、快，正脸照、证件照够用；CNN 慢约 10 倍，侧脸、遮挡、小目标更稳。
先用 HOG 跑通，需要时再加 `-d cnn`。

---

## License

MIT
