下面这份 **README.md** 已按典型 GitHub 项目的格式写好，直接复制保存为 `README.md`（或在仓库新建该文件）即可。
如果后续想加截图，只需把图片放进 `docs/` 或 `assets/` 目录后，在相应位置插入 Markdown 引用即可。

---

```markdown
# FileIntegritySystem · 基于 SM3 的文件完整性保护工具

> 版本 v0.1.2  · 仅供学习与实验使用，禁止商业用途  

本项目通过 **SM3** 哈希算法为任意文件创建和校验“指纹”，配合简单友好的 Tkinter 图形界面，帮助用户快速检测文件是否被篡改。  
初衷是完成课程实验，但代码已整理成通用的小工具，欢迎同学们 Fork / 二次开发。

---

## 📦 项目结构

```

FileIntegritySystem/
├─ main.py                # 程序入口，启动 GUI
├─ ui.py                  # 界面与交互逻辑
├─ sm3.py                 # 纯 Python 实现的 SM3 哈希
├─ record\_manager.py      # 记录读写 & 增删改
├─ dist/                  # 可执行文件与资源示例
│  ├─ sm3.exe             # PyInstaller 打包的 SM3 加速版 (可选)
│  ├─ spinner.gif         # 动态加载动画
│  └─ click.wav           # 按钮音效
├─ spinner.gif            # 运行时使用的 GIF
├─ click.wav              # 运行时使用的音效
├─ readme.txt             # 原始简易说明 (中文)
└─ hash\_record.json       # 运行后自动生成的完整性记录

````

---

## 💡 主要功能

| 功能 | 说明 |
|------|------|
| **初装记录** | 计算选中文件的 SM3 值并写入 `hash_record.json` |
| **完整性校验** | 重新计算哈希并与初装记录对比，提示是否被篡改 |
| **查看记录** | 列表化展示所有已记录文件，可编辑备注或删除记录 |
| **多媒体反馈** | 点击音效 + 加载动画，交互更直观 |

> ⚠️ 声音播放依赖 Windows 的 `winsound`；在 macOS / Linux 上运行时若无声，可忽略不影响核心功能。

---

## 🖥️ 运行环境

| 依赖 | 版本建议 |
|------|----------|
| Python | ≥ 3.8（3.12 已验证） |
| Pillow | ≥ 10.0（仅用于 GIF 播放） |

> Tkinter 属于标准库；若在 Linux 发行版上报缺失，可先安装 `sudo apt install python3-tk`.

---

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/<your-id>/FileIntegritySystem.git
cd FileIntegritySystem

# 2. 创建并激活虚拟环境（可选）
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. 安装依赖
pip install pillow

# 4. 启动程序
python main.py
````

### 使用步骤

1. 点击 **「选择文件」** 挑选需要保护 / 校验的目标文件
2. 首次使用对该文件点击 **「初装记录」** 写入基准 SM3 哈希
3. 任何时候怀疑文件被改动，点击 **「完整性校验」**
4. 如需查看或管理所有记录，点 **「查看记录」**

程序会在工作目录下生成 / 更新 **`hash_record.json`**，格式示例如下：

```json
{
  "D:/docs/report.docx": {
    "hash": "9F1E5EA3...F04ABC",
    "remark": "论文最终版"
  }
}
```

---

## 🛠️ 打包为 .exe

已经提供示例 `dist/sm3.exe` 供加速计算；如需把整个 GUI 打包成单文件可执行：

```bash
pip install pyinstaller
pyinstaller -F -n FileIntegritySystem ^
  --add-data "spinner.gif;." --add-data "click.wav;." main.py
```

生成文件位于 `dist/FileIntegritySystem.exe`，方便在无 Python 环境的机器上直接运行。

---

## 🗒️ 版本日志

| 版本         | 变更               |
| ---------- | ---------------- |
| **v0.1.2** | 所有注释改为英文，避免乱码    |
| **v0.1.1** | 新增动画与音效，界面优化     |
| **v0.1.0** | GUI & SM3 核心功能实现 |

---

## 🤝 贡献

1. Fork 仓库、创建特性分支
2. 提交 PR 前请确保 `flake8` / `black` 通过
3. PR 合并后将计入贡献者名单

---

## 📜 许可

除非另行书面说明，代码采用 **MIT License** 发布；多媒体素材仅限学习研究，禁止商业使用。

---

## ✨ 鸣谢

* [https://github.com/guanzhi/GmSSL](https://github.com/guanzhi/GmSSL) —— SM3 规范参考
* Pillow 社区提供的 GIF 播放支持
* PyPI、StackOverflow 等开源社区的帮助

---

> 如果本项目对你有帮助，记得 Star ⭐ 一下！

```

---  

建议把 `Pillow` 写进 `requirements.txt` 方便 `pip install -r requirements.txt`；如日后添加依赖（例如 `PyInstaller`、`flake8`），也一并列在该文件即可。祝你上传顺利，实验报告拿满分！
```
