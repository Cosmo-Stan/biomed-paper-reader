# Biomed Paper Reader

**面向科研人员的遵循用户输出语言的导师式论文精读 Skill，附 Windows Portable 安装包。**

A portable Codex skill for language-aware, mentor-style biomedical paper reading, traceable evidence, and an offline HTML reader.

版本：**1.0-portable.2**。内容和界面采用 v1.0 稳定基线。

## 它做什么

将已有、可追溯的论文资源组织为以科学问题推进的导师式精读。三个视图共享同一份 `evidence.json`：

- **B 研究全景**：科学问题、证据组及关系。
- **A1 连续阅读**：导师式长文、内嵌证据与可展开背景。
- **A2 左右对照**：实验解读与原始图像并排，可放大。

提供速览、导师讲解和深度审查三种阅读深度，以及快速理解、研究级原理、数学或技术细节三级背景。HTML 和 Markdown 从同一受控内容生成；离线阅读不依赖 CDN、云服务或 Python。

## 输出语言（1.0-portable.2）

用户明确指定语言时优先遵循；否则跟随当前任务提示词的主要语言。例如，英文任务默认英文，中文任务默认中文，中文提示中要求“用英文输出”仍输出英文。HTML、Markdown、证据说明和审查说明保持一致；原图、原文引文和机器字段不被翻译覆盖。

内置简体中文/英文界面；其他语言由代理提供完整标签译表。生成器负责呈现，代理负责科学内容的目标语言写作。见 [语言配置](portable/skill/biomed-paper-reader/references/output-language.md)。没有增加在线翻译服务。

## 科学边界

每项关键论述保留来源页码、图号或 panel、方法与证据关联，区分原文转述、数据结果、作者解释、AI 推论和外部知识。保留样本单位、实验重复、统计方法、阴性结果与解释局限。FRAP、荧光富集、形态及功能实验分别解释，不压缩成一个物理指标。

此 Skill 需要代理对来源进行实际阅读和组织，不是把任意 PDF 一键变成已核验结论的程序。自动结构、路径与哈希校验不能代替科学审查。生成器也不直接接受任意 Paper2Skill 输出格式，需要依据内容契约建立 `evidence.json`。

## Windows 安装

准备 Codex 与 Python 3.9+。生成器仅依赖 Python 标准库；本轮实际测试版本为 Python 3.13.7。

下载本仓库 ZIP 并解压，或克隆仓库。在仓库根目录运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\portable\install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\portable\verify-install.ps1
```

自动安装到 `$HOME\.agents\skills\biomed-paper-reader`。不需要管理员权限，不修改系统环境变量或全局执行策略。已有不同内容时拒绝覆盖；相同内容重装无改动。

也可以下载 [Portable ZIP](portable/biomed-paper-reader-v1.0-portable.zip) 与 [SHA-256](portable/biomed-paper-reader-v1.0-portable.zip.sha256)，解压后直接运行其中的 `install.ps1`。公开软件的许可证为根目录 [LICENSE](LICENSE)，分发该独立包时请同时附带许可证。

完整安装参数与上游依赖说明见 [Portable README](portable/README.md)。Git 克隆时，`.gitattributes` 保留 `portable/` 的原始字节，避免换行转换导致哈希失效。

## 调用

新建 Codex 项目，在 Skill 选择器确认用户级 Portable 版本。未出现时重启 Codex。项目已有同名 Skill 时，明确选择用户级路径。

```text
$biomed-paper-reader
使用用户级 1.0-portable.2，读取 $HOME/.agents/skills/biomed-paper-reader/SKILL.md。
资料目录：<本篇论文资料目录>
输出目录：<新的输出目录>
沿用 v1.0 科研导师式规范，优先复用可核验资源；原始资料只读。
明确补充材料缺失、审查范围及证据不足，不执行 Paper2MCP。
```

输出包括 `read.html`、`reading.md`、`evidence.json`、`assets/` 与 `audit/`。复制完整输出目录后即可离线阅读；重新构建还需要可核查的源文件。

## 与 Paper2Agent 衔接

已有足够的已审读资源时，可直接使用本 Skill。若只有新 PDF、缺少可靠提取与审读资源，需要另行安装 [Paper2Agent](https://github.com/jmiao24/Paper2Agent)，按其 paper-only / Paper2Skill 工作流准备材料。本项目不包含上游仓库、不静默安装上游，也不执行 Paper2MCP。

## 验证与贡献

```powershell
python .\scripts\verify_release.py
python .\portable\skill\biomed-paper-reader\scripts\smoke_test.py
```

自检仅使用虚构材料，覆盖 1/3/12 章和 1/7/53 个图像及证据组。没有固定真实论文数量假设。

已完成本机 Windows 安装、Codex 发现、虚构回归和 Edge 离线交互测试；**未在第二台实体 Windows 电脑验证**。旧版部署测试范围见 [兼容性报告](portable/reports/compatibility.md)、[差异清单](portable/reports/differences.md) 与 [独立部署审查](portable/reports/independent-review.md)。这些报告记录部署检查，不代表新论文通过科学审查。

请通过 Issue 报告问题，并提供无敏感信息的最小虚构样例。不要提交论文 PDF、受限图像、患者资料、Zotero 数据、个人路径或密钥。`portable/` 是已验证的发布快照；后续变更请在新版本中开发并更新相应校验清单，不覆盖稳定基线。旧版 v1.0-portable.1 的 Git 标签及 Release 保留。

## 许可证与来源

[MIT License](LICENSE)。本项目的通用指令、生成器、界面和安装工具在作者的科研阅读项目中借助 Codex 开发。Paper2Agent 为独立上游项目；本仓库不复制其实现，也不重新许可论文或其他第三方资料。论文内容、原图及数据的权利仍属于各自权利人。

本次语言更新的测试范围见 [语言更新记录](portable/reports/language-update.md)。升级时先把旧安装移到 Skill 发现目录之外备份，再运行安装程序；不静默覆盖已安装版本。
