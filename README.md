# CUBE TO XMP

在照片上看见色彩，再把 LUT 带到下一段工作流程。

CUBE TO XMP 是一款在 Windows 本地运行的摄影 LUT 工作台。你可以导入 `.cube` 或带有 RGBTable 的 `.xmp`，在照片上比较调色前后，将 LUT 转换为另一种格式，并把常用风格留在自己的资料库里。照片和 LUT 都在本机处理。

[下载 Windows 免安装版](https://github.com/13489079165/CUBE-to-XMP/releases/latest) · [English](README.en.md) · [转换格式说明](docs/CONVERSION.md)

## 你可以做什么

| 场景 | 操作 |
| --- | --- |
| 先看效果 | 选择六款内置胶片灵感风格，或导入自己的 LUT；在演示照片或自己的照片上拖动分隔线比较。 |
| 整理 LUT | 一次导入多份 `.cube` / `.xmp`，在资料库搜索、筛选、应用和移除；导入的文件会复制到本地资料库。 |
| 转换格式 | CUBE → XMP、XMP → CUBE；选择输出网格，保存到指定位置。 |
| 找到结果 | 在「转换记录」中查看本次运行实际导出的文件，并打开所在文件夹。 |

界面提供简体中文和 English、浅色和深色主题，以及可关闭的动效。应用图标、窗口和资料库预览已统一为黑白灰的摄影工作台风格。

## 下载与运行

1. 打开 [最新版本](https://github.com/13489079165/CUBE-to-XMP/releases/latest)，下载 `CUBE-TO-XMP-v2.1.0-windows-x64.zip`。
2. 解压**整个文件夹**，运行其中的 `CUBE-TO-XMP.exe`。不要单独移动 EXE；同目录的 `_internal` 文件夹是程序运行所需的资源。
3. 首次启动需要 Windows 上的 Microsoft Edge WebView2 Runtime。如果缺少，请先安装。

这是 Windows 64 位版本，无需单独安装 Python。程序不会把照片或 LUT 上传到服务器。

## 三步完成一次转换

1. 在「工作台」点击「导入 LUT」，或从下方选择一款内置风格。右侧会显示源格式和输出格式。
2. 拖动照片上的分隔线比较效果。需要时点击「更换预览照片」，载入 JPG、PNG、TIFF 或 BMP。照片仅用于预览，不会被导出操作改写。
3. 选择输出网格，点击「导出 XMP」或「导出 CUBE」，在系统保存窗口选定位置。保存成功后可在「转换记录」找到文件。

快捷键：`Ctrl+O` 导入 LUT、`Ctrl+P` 更换照片、`Ctrl+S` 导出。聚焦对比照片后，可用方向键、`Home`、`End` 调整分隔线。

导入的 LUT 保存在 `%LOCALAPPDATA%\CUBE TO XMP\Library`；设置保存在同一应用数据目录。删除原始文件后，已导入的副本仍可使用。

## 格式与兼容性

- CUBE 输入支持 2–65³ 的标准 **3D LUT**，输入域必须是 0–1；不支持 1D LUT。
- XMP 输入必须包含 Adobe RGBTable。普通 Lightroom / Camera Raw 滑块预设不属于可转换的 LUT。
- 输出网格可选 16、17、25、32、33、64、65。XMP 实际输出最高 32³；选择更大网格时会重采样为 32³。
- 照片预览基于 RGB 像素处理，是判断风格的参考。不同目标软件的色彩管理可能使最终效果略有差异；Adobe Camera Raw / Lightroom 中的实际兼容性仍待验证。

内置六款风格是胶片色彩灵感预设，不代表富士官方胶片模拟。

## 从源码运行

需要 Windows、Python 3.12 和 Edge WebView2 Runtime：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe cube_to_xmp.py
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -q
.\.venv\Scripts\python.exe tests\smoke_web_ui.py
```

打包：先安装 `pyinstaller`，再运行 `.\.venv\Scripts\python.exe build.py`。当前桌面版由 `frontend/` 的 HTML/CSS/JavaScript 和 `web_studio.py` 的本地桥接组成；转换逻辑在 `conversion_service.py`、`lut_core.py`，导入库在 `lut_library.py`。详见 [转换说明](docs/CONVERSION.md) 和 [测试清单](docs/TESTING.md)。

[MIT License](LICENSE) · [v2.1.0 更新内容](docs/RELEASE_v2.1.0.md)
