# 冻结 v1.0 → 1.0-portable.1 差异

原冻结版本和原项目文件不变。以下仅存在于新 Portable 副本。

| 文件或范围 | 差异 | 行为影响 |
| --- | --- | --- |
| scripts/build_reader.py | 增加 source_path，path 与 original_path 的相对路径以 evidence.json 目录解析 | 有意修正跨目录重建；绝对路径输入在三个虚构规模下输出与基线完全一致 |
| scripts/build_reader.py | 明确要求 Python 3.9+ 和非优化模式；拒绝空章节/证据、无 depth=1 概览 | 无效输入提早失败；避免关闭断言或浏览器启动时报错。有效输入的科学文本及排版不变 |
| SKILL.md | 增加当前 Skill 目录定位、输出目录规则、版本/默认配置、动态数量、上游缺失处理与审查报告路径 | 适用于不同项目，仍要求明确证据与审读范围 |
| references/content-schema.md | 源路径可相对 evidence.json 父目录，也接受绝对路径 | 来源页码、哈希、裁切框、方法与科学主张关系仍保留 |
| agents/openai.yaml | 显示名称加 v1.0 Portable | 便于同名项区分；调用名仍是 biomed-paper-reader |
| version.json、references/v1.0-defaults.json | 新增通用版本标识和默认规范，不带原论文限制或原路径 | 固定内容风格；图像、章节、证据数量由实际输入决定 |
| references/portable.md | 新增移植、上游交接和同名选择说明 | Paper2Agent 是新论文准备的条件依赖，不自动打包或下载 |
| scripts/smoke_test.py | 新增无真实科研资料的动态虚构样例与自检 | 临时目录测试，无额外 Python 包；不产生科学核验结论 |
| install.ps1、verify-install.ps1、lib/common.ps1 | 新增用户级安装、清单检查、Python 检测、只报告条件依赖、同名提示 | 无管理员需求；拒绝静默覆盖；只对本次 PowerShell 子进程使用执行策略参数 |
| README、reports、完整性清单、ZIP | 新增部署文档、当次软件测试报告及分发结构 | 不包含历史科学审查、论文或个人机器日志 |
| assets/reader.html、reader.css、reader.js | **无改动** | 保留 v1.0 既有界面、交互与有效输入渲染行为 |
| references/scientific-review.md | **无改动** | 读出区分、证据解释边界等科学审查规则保持 |

没有加入固定论文 DOI、章节编号、图号或图像数量。测试脚本中的 1/3/12 与 1/7/53 是覆盖用例，不是生成器配额。

未实现自动将任意上游格式无损转换成 evidence.json；仍由 Skill 按可信来源组织内容。本次也未执行 Paper2MCP、论文再生成、现有成果重写或界面升级。将来改变内容或界面应另立版本与输出目录。
