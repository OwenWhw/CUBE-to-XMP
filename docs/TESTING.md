# 点击测试清单

1. 打开新版 EXE，确认左上角显示 CUBE TO XMP、照片和六个风格缩略图。
2. 点击每个风格；右侧应显示 CUBE → XMP，照片右半边变化。
3. 拖动照片分隔线，或聚焦后用方向键 / Home / End 比较。
4. 点击「导入 LUT」，选一份 `.xmp`；右侧应显示 XMP → CUBE，资料库数量增加。
5. 打开「LUT 资料库」，搜索、应用导入文件，重启程序后再检查文件仍在。
6. 更换预览照片；原文件不应被改写。
7. 选择输出网格、导出，使用系统保存框；「转换记录」应出现真实文件。
8. 把刚导出的 XMP 再导入，导出 CUBE；用应用重新读取或独立软件检查。
9. 在资料库移除导入文件；内置六个预设不应被移除。
10. 测试窗口最小化、最大化、拖动及关闭。

自动测试：`.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v`。

已通过源码版真实鼠标交互完成 CUBE → XMP → 资料库导入 → CUBE，并重新读取输出。Adobe Camera Raw / Lightroom 端尚未验证。

WebView2 页面冒烟测试：`.venv\Scripts\python.exe tests\smoke_web_ui.py`。验证窗口缩放、主题与语言设置、资料库预览清晰度、导入筛选、应用 LUT 后的 XMP→CUBE 方向以及空记录页面。
