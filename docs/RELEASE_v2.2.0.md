# CUBE TO XMP v2.2.0

摄影 LUT 工作台现提供按系统区分的免安装包：Windows x64、macOS Intel、macOS Apple 芯片及 Linux x64。下载一个 ZIP，完整解压后即可使用相应系统的应用。文件名统一为 `CUBE-TO-XMP-v2.2.0-系统-架构.zip`。

## 本版更新

- 桌面窗口按系统选择 WebView 后端：Windows 使用 Edge WebView2、macOS 使用系统 WebKit、Linux 使用 Qt WebEngine。
- 各平台分别构建，并检查转换服务、前端脚本、打包后的内置 LUT 与照片资源；Windows 界面操作另在本机完成实测。
- 中英文项目说明加入工作台及 LUT 资料库截图、分平台下载指南与历史版本索引。
- v2.0.0 历史附件统一命名，原压缩包内容不变；两份不同的 Windows 旧包均保留并明确区分。

## 下载与运行

| 系统 | 文件 |
| --- | --- |
| Windows x64 | `CUBE-TO-XMP-v2.2.0-windows-x64.zip` |
| macOS Intel | `CUBE-TO-XMP-v2.2.0-macos-x64.zip` |
| macOS Apple 芯片 | `CUBE-TO-XMP-v2.2.0-macos-arm64.zip` |
| Linux x64 | `CUBE-TO-XMP-v2.2.0-linux-x64.zip` |

Windows 需 Edge WebView2 Runtime。macOS 应用尚未签名或公证，可能需要手动确认来源。Linux 包在 Ubuntu 24.04 x64 构建，其他发行版未逐一验证。各平台都请完整解压；发布页提供 SHA-256 校验文件。

转换仍限于标准 3D CUBE 和包含 Adobe RGBTable 的 XMP。普通 XMP 滑块预设、1D LUT、非 0–1 输入域不支持；Adobe Camera Raw / Lightroom 中的实际效果和兼容性仍待验证。

---

The photography LUT studio now has separate portable downloads for Windows x64, macOS Intel, macOS Apple silicon, and Linux x64. Archive names use the consistent pattern `CUBE-TO-XMP-v2.2.0-platform-architecture.zip`.

The desktop shell selects Edge WebView2 on Windows, system WebKit on macOS, and Qt WebEngine on Linux. The project guides now include studio and library screenshots plus a [download history](DOWNLOADS.md). Historical v2.0.0 assets have been renamed for clarity without changing their contents.

Extract the full archive before running the app. Windows needs Edge WebView2 Runtime. macOS builds are neither signed nor notarized and may require a manual security confirmation. The Linux x64 build targets Ubuntu 24.04; other distributions have not been verified. `SHA256SUMS.txt` is provided for download verification.

The format limits are unchanged: normalized 3D CUBE files and XMP files containing Adobe RGBTable data are supported; ordinary XMP slider presets and 1D LUTs are not. Results inside Adobe Camera Raw / Lightroom have not yet been verified.

[中文说明](../README.md) · [English guide](../README.en.md) · [All downloads](DOWNLOADS.md)
