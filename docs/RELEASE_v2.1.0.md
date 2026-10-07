# CUBE TO XMP v2.1.0

这一版把 CUBE TO XMP 从旧的 Tk 界面更新为 Windows 摄影 LUT 工作台。界面改为本地 WebView2，保留 Python 转换核心，并加入可持久保存的 LUT 资料库。

## 新增与改进

- 在照片上实时比较 LUT 前后效果，可导入自己的照片；资料库卡片使用更清晰的预览图。
- 支持导入多份 CUBE/XMP、搜索、筛选、移除；导入副本保存在本机，重复文件按内容去重。
- CUBE ↔ XMP 双向转换，保存前可选择输出网格；XMP 输出最高 32³。
- 新的窗口、黑白灰主题、浅色/深色模式、中英文界面、动效设置和应用图标。
- 导出记录只展示本次运行中实际保存的文件。
- 转换核心独立于界面，增加了格式校验、原子写入和自动化测试。

## 下载

下载 `CUBE-TO-XMP-v2.1.0-windows-x64.zip`，完整解压后运行 `CUBE-TO-XMP.exe`。请保留 `_internal` 文件夹。需要 Windows 64 位和 Microsoft Edge WebView2 Runtime，无需安装 Python。

## 已知边界

仅支持标准 3D CUBE 和包含 Adobe RGBTable 的 XMP；普通 XMP 滑块预设、1D LUT 和非 0–1 输入域不支持。照片预览是 RGB 参考，Adobe Camera Raw / Lightroom 中的实际效果和兼容性仍待验证。本次只发布经过本机验证的 Windows 包。

详细操作见 [中文说明](../README.md) / [English guide](../README.en.md)。
