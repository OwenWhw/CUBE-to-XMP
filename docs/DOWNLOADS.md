# 下载与历史版本 / Downloads and previous versions

最新版本：[CUBE TO XMP v2.2.0](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v2.2.0)。从这一版起，压缩包统一采用 `CUBE-TO-XMP-v主版本.次版本.修订版本-系统-架构.zip`，例如 `CUBE-TO-XMP-v2.2.0-windows-x64.zip`。每个新版本还提供 `SHA256SUMS.txt`。

Latest release: [CUBE TO XMP v2.2.0](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v2.2.0). New archives follow `CUBE-TO-XMP-vMAJOR.MINOR.PATCH-platform-architecture.zip`, with a `SHA256SUMS.txt` checksum list.

| 版本 / Release | 可下载平台 / Available packages | 说明 / Note |
| --- | --- | --- |
| [v2.2.0](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v2.2.0) | Windows x64, macOS x64 / ARM64, Linux x64 | 当前摄影工作台 / Current photography studio. |
| [v2.1.0](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v2.1.0) | Windows x64 | 首个 WebView2 版，仅 Windows / First WebView2 release, Windows only. |
| [v2.0.0](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v2.0.0) | Windows x64, macOS ARM64, Linux x64, source | 旧 Tk 界面，历史归档 / Historical Tk interface. |
| [v1.0.0 初始版](https://github.com/OwenWhw/CUBE-to-XMP/releases/tag/v1.0.0-Initial-Release) | Legacy archive | 平台未标注；仅供回溯 / Platform not labelled; for archival use. |

## v2.0.0 旧版附件 / v2.0.0 archive details

旧版附件已统一文件名前缀与版本号，文件内容保持原样。历史版本和当前工作台的界面、功能、依赖不相同；请优先下载最新版。

The old assets were renamed without changing their contents. They use a different interface and dependency stack; choose the latest release for the current studio.

| 文件 / Asset | 说明 / Note |
| --- | --- |
| [`CUBE-TO-XMP-v2.0.0-windows-x64.zip`](https://github.com/OwenWhw/CUBE-to-XMP/releases/download/v2.0.0/CUBE-TO-XMP-v2.0.0-windows-x64.zip) | 旧版 Windows 主包 / Main legacy Windows build. |
| [`CUBE-TO-XMP-v2.0.0-windows-x64-alternate.zip`](https://github.com/OwenWhw/CUBE-to-XMP/releases/download/v2.0.0/CUBE-TO-XMP-v2.0.0-windows-x64-alternate.zip) | 保留原来第二份不同大小的 Windows 包；未重新验证 / Second distinct historical build, retained as-is and not reverified. |
| [`CUBE-TO-XMP-v2.0.0-macos-arm64.zip`](https://github.com/OwenWhw/CUBE-to-XMP/releases/download/v2.0.0/CUBE-TO-XMP-v2.0.0-macos-arm64.zip) | 旧版 Apple 芯片包 / Legacy Apple-silicon build. |
| [`CUBE-TO-XMP-v2.0.0-linux-x64.zip`](https://github.com/OwenWhw/CUBE-to-XMP/releases/download/v2.0.0/CUBE-TO-XMP-v2.0.0-linux-x64.zip) | 旧版 Linux 包 / Legacy Linux build. |
| [`CUBE-TO-XMP-v2.0.0-source.zip`](https://github.com/OwenWhw/CUBE-to-XMP/releases/download/v2.0.0/CUBE-TO-XMP-v2.0.0-source.zip) | 当时上传的源码快照 / Historical source snapshot. |

## 校验下载 / Verify a download

在发布页下载 ZIP 和 `SHA256SUMS.txt`，比较 ZIP 的 SHA-256。Windows PowerShell：

```powershell
Get-FileHash .\CUBE-TO-XMP-v2.2.0-windows-x64.zip -Algorithm SHA256
```

On macOS or Linux, place the ZIP and `SHA256SUMS.txt` in the same folder, then run `shasum -a 256 -c SHA256SUMS.txt` (macOS) or `sha256sum -c SHA256SUMS.txt` (Linux).

[中文使用说明](../README.md) · [English guide](../README.en.md)
