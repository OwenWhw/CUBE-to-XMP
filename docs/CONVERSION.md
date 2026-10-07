# 转换模块

界面通过 `StudioBridge` 调用 `ConversionService`，不在浏览器中实现第二套转换算法。`LutLibrary` 负责文件副本和索引。后续重写转换算法时可保持 `ConversionService.load_lut / preview / export` 的接口，避免重做界面。

数据流：选择内置或导入 LUT → 校验并解析为 `LutDocument(size, samples, source)` → Pillow RGB 预览 → 选择反向格式与尺寸 → 插值 / 编码 → 目标目录临时文件 → 原子替换 → 记录真实输出。

- CUBE：读取标准 3D LUT；拒绝 1D、非 0–1 输入域、不完整网格及无效数值。
- XMP：按 XML 命名空间定位 Adobe RGBTable；检查 Base85、压缩数据大小、3D 网格和采样数量。不能把普通 XMP 滑块预设当作 LUT。
- XMP 输出上限 32³；CUBE 输出尺寸有 16、17、25、32、33、64、65。大网格转换用四面体插值。
- 文件写入在同目录临时文件完成后替换目标，以免编码失败时留下截断文件。
- 导入库位于 `%LOCALAPPDATA%\CUBE TO XMP\Library`。相同内容按 SHA-256 去重，索引为 JSON。

运行 `python -m unittest discover -s tests -p 'test_*.py'` 检查六个预设往返、通道顺序、元数据、边界文件、持久化导入和桥接反向转换。Adobe 软件端仍需用真实安装环境验证。
