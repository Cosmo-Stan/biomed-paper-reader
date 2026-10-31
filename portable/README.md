# Biomed Paper Reader v1.0 Portable

部署版本 **1.0-portable.2**，内容与界面基线 **biomed-paper-reader-v1.0**。通用 Skill 包，不包含论文、个人审读历史、PDF、病例或上游仓库。科学内容规则及布局不变；显示文字按目标语言输出，CSS 与冻结版相同。

## 另一台 Windows 电脑：最简安装

1. 复制 `biomed-paper-reader-v1.0-portable.zip` 及 `.zip.sha256`，解压 ZIP 到自己的可写目录（不要在 ZIP 浏览窗口内运行）。可先运行 `Get-FileHash .\biomed-paper-reader-v1.0-portable.zip -Algorithm SHA256` 与旁边的校验文件比较。哈希用于发现传输损坏，不是数字签名。
2. 准备 Codex 和 Python 3.9 或更新版本。生成器仅依赖 Python 标准库；离线阅读成品 HTML 不需要 Python。Python 可从 https://www.python.org/downloads/windows/ 获取；不要求管理员安装或修改系统环境变量，可用 `-PythonPath` 指定已有解释器。
3. 在解压目录打开 PowerShell，运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\verify-install.ps1
```

`-ExecutionPolicy Bypass` 只作用于这次子进程，不修改全局执行策略；组织策略禁止脚本时遵循组织规则。安装器不需要管理员、不调用 Set-ExecutionPolicy、不写系统环境变量、不联网。自动目标是当前用户的 `$HOME\.agents\skills\biomed-paper-reader`。

已有相同内容则报告无改动；已有不同版本、缺文件或额外文件则拒绝覆盖。需要替换时先自行保存并移走原目录，明确决定后再安装。不要覆盖稳定项目 Skill。失败时可能保留带随机名的暂存目录，安装器不会自动递归删除用户文件。

可选参数：`-PythonPath <python.exe>` 指定解释器；`-InstallRoot <skills目录>` 用于自定义或模拟安装（**不会自动让 Codex 发现自定义目录**）。`verify-install.ps1 -ProjectPath <项目目录> -Paper2AgentPath <上游Skill目录> -ReportPath <包外报告路径>` 可检查指定项目、非标准上游位置并保存报告。

## 新 Codex 项目的标准调用

打开新的项目/会话，在 Skill 选择器确认用户级版本；未出现时重启 Codex。输入：

```text
$biomed-paper-reader
使用用户级 Biomed Paper Reader 1.0-portable.2。
请先读取 $HOME/.agents/skills/biomed-paper-reader/SKILL.md 和 version.json。
论文资料位于：<本项目资料目录>；输出到：<本项目新的输出目录>。
优先复用可核验的 Paper2Skill 资源；清点缺失的补充材料。
沿用 v1.0 科研导师式规范，生成同源 read.html、reading.md、evidence.json、assets/ 和 audit/。
原始资料只读，区分软件核验、源文审读、独立复核和数据复算状态，不执行 Paper2MCP。
```

尖括号内容请替换为当前项目真实路径；不要把输出写入安装目录。如果项目也有同名 Skill，应在选择器指定用户级路径，或直接要求读取上面明确路径的文件。同名版本不会合并，不能仅凭名称保证选中了哪一个。见 [官方 Skill 发现说明](https://learn.chatgpt.com/docs/build-skills)。

## 输入与离线输出

`skill/biomed-paper-reader/` 是可安装的完整通用 Skill。生成命令和内容契约在其 SKILL.md 与 references/ 中。输出位于 `evidence.json` 的父目录；输入源文件相对路径也以该目录解析，绝对路径继续可用。图像必须处于输出目录内；图像、章节、证据数量动态读取。

复制整套输出目录，双击 read.html 即可离线查看。不要只移动 HTML 而丢失 assets/；来源链接若指向互联网，仅点击访问时需要联网。重新构建需要 evidence.json 指向的源文件及其正确哈希。审查报告须按实际范围编写，生成器不伪造科学审查。

## 依赖与上游

新 PDF → 已审读知识资源：需要另行安装 Paper2Agent / Paper2Skill 及其自身依赖；已获得可靠审读资源 → 本阅读器：不强制安装上游。验证脚本会显式报告上游缺失，指导见 `skill/biomed-paper-reader/references/portable.md`。上游入口存在不等于上游环境已完成验证。

## 验证、完整性与边界

安装及验证先核对 SHA-256，再在临时目录运行纯虚构样例（1/3/12 章，1/7/53 个图像及证据组）。没有真实科研数据。保留样例以浏览检查：

```powershell
python "$HOME\.agents\skills\biomed-paper-reader\scripts\smoke_test.py" --output ".\new-synthetic-demo"
```

`--output` 必须是不存在的新目录。程序不会把虚构样例当作论文结果。测试页面沿用原模板中的“原始 PDF”说明，但输入文件和所有图像均明确标为 SYNTHETIC，不能用于科研解读。

`SHA256SUMS.json` 覆盖解压包中的全部文件，唯独排除它本身、ZIP 和 ZIP 校验侧文件；Skill 内的 `skill-manifest.json` 覆盖其余所有 Skill 文件。ZIP 内不包含 ZIP 自身或校验侧文件。安装验证拒绝未列入清单的其他文件。添加笔记请放在包外。测试不会写入 Skill 目录。

测试覆盖、实际完成与模拟边界见 [兼容性报告](reports/compatibility.md)，修改清单见 [版本差异](reports/differences.md)。没有在另一台实体 Windows 电脑验证；其他电脑须重跑验证。模板遗留的试点措辞和两位编号显示保留，不影响动态数量。不得据软件测试通过宣称科学内容已审读。

## 输出语言更新

1.0-portable.2 优先遵循用户明确指定的输出语言，否则跟随当前任务提示词的主要语言。正文与审查说明由代理按目标语言写作；生成器按 presentation.language 呈现内置中英文标签，其他语言需完整译表。原文引文、原图文字与机器字段保留。见 skill/biomed-paper-reader/references/output-language.md 和 reports/language-update.md。旧的兼容性与独立审查报告记录 .1 版本，不能冒充本次语言测试。
