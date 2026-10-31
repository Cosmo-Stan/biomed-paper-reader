# Portable v1.0 默认规范与衔接

内容默认：按用户指定或当前提示词语言进行科研导师式连续精读，信息密度适中；B 全景、A1 连续阅读、A2 左右证据对照；三种阅读深度；三级背景；原文转述、结果、作者解释、AI 推论、外部知识分开。HTML 与 Markdown 只从同一 evidence.json 生成。科学审查规则仍见 scientific-review.md。

以本 Skill 的实际目录定位脚本和模板，所有项目输出写到用户指定的独立目录。在该目录保存 evidence.json、assets/、由 presentation.audit_path 指定的审查报告（中文默认 audit/验收报告.md，其他语言默认 audit/report.md）。重新构建必须提供可核查的来源文件；源路径相对 evidence.json 父目录解析，也接受绝对路径。复制 read.html、reading.md、assets/、audit/ 即可离线阅读；重新构建还需要 evidence.json 及其来源，不要求把论文放入 Skill 安装目录。

运行：`python "<skill>/scripts/build_reader.py" "<output>/evidence.json"`。仅 Python 3.9+ 标准库，无 pip 必需项。源 PDF 提取、浏览器审查、外部文献检索属于制作阶段工具，不是 HTML 离线依赖；依任务检测，不能假装已具备。

## Paper2Agent 交接

接收 Paper2Skill 的已审读产物、来源清单/哈希、逐页逐图索引和验证记录。逐项核对后人工组织为本 Skill 的 evidence.json；两种结构不假定一一兼容，不存在自动无损转换承诺。原始资料只读，证据未读或冲突必须保留。

有足够已审读资源时，即使 Paper2Agent 未安装也可继续阅读器制作，但报告上游缺失以及实际核查范围。只有新 PDF、缺少可靠资源时，先定位 `$paper2agent` / Paper2Skill，按其官方 paper-only 流程 prepare → extract → review-aid → build → verify；此 Skill 不替代该流程、不执行 Paper2MCP。

若缺失，明确提示“Paper2Agent 未找到：从新 PDF 建立审读资源的上游步骤不可执行”。上游来源为 [jmiao24/Paper2Agent](https://github.com/jmiao24/Paper2Agent)，所需完整目录为 `skills/paper2agent/`。可对 Codex 输入：“请阅读该上游 README，使用 $skill-installer 将 skills/paper2agent 完整安装到当前用户的 .agents/skills/paper2agent；若已有版本先比较，不覆盖；只安装，不处理论文。”遵循上游宿主和依赖要求，paper-only 仍需上游自身的 Python 依赖及独立审查能力。安装后的上游根目录内应存在 `SKILL.md`、`paper2skill/SKILL.md`、`paper2skill/scripts/paper_bundle.py`，重新运行安装验证。这个包不提供也不静默下载上游仓库；安装上游本身需要另行联网或已有完整离线副本。

## 同名 Skill

用户级目录是 `$HOME/.agents/skills/biomed-paper-reader`。项目级同名 Skill 可与它同时被发现，不会合并。新空白项目直接使用 `$biomed-paper-reader`；有同名项时在选择器确认用户级路径，或在提示词明确指定该路径的 SKILL.md 和版本 1.0-portable.2。不要自动删除或覆盖项目基线。若安装未被发现，重启 Codex 后再检查。

## 已知继承行为

布局与 CSS 保留 v1.0，展示文字按语言配置输出；中文末尾仍使用“试点范围末尾”，第十章编号仍为 QUESTION 010。这些措辞不限制实际数量。本次仅增加输出语言设置。自动验证检查结构、已声明页界和哈希，不等同逐页 PDF 目视审读或科学正确性证明。
