# 1.0-portable.2：输出语言更新

日期：2026-10-31。此版本仅调整输出语言规则、展示标签、相关说明及打包版本。科学审查规则、源文核查要求、页面结构与 CSS 不变。

## 行为

- 用户明确要求的输出语言优先；未指定时采用当前任务提示词的主要语言。代理在 evidence.json 中记录 presentation.language 并以该语言编写解读与审查说明。
- HTML、Markdown 的标题、按钮、背景、证据分类显示及来源标签使用同一译表。内置简体中文、英文；其他语言允许完整自定义译表，缺少配置会报错，不默默显示中文。
- 原文引文、原图、机器字段和兼容枚举保持原样。生成器不翻译科学内容、不调用外部翻译服务。
- 不含语言配置的旧 JSON 保留中文默认。中文审查链接默认 audit/验收报告.md，其他语言默认 audit/report.md，可显式配置。

## 本轮验证

- 纯虚构材料的 Python 检查通过：旧中文 Markdown 与 .1 逐字节一致；英文 Markdown 的展示文字为英文，特意设置的中文原文引文保持原样；源文件、资产及输入 JSON 哈希不变。
- 验证英文审查链接、完整自定义译表、缺失译表、格式参数缺失和越界审查路径。无效配置在写出前拒绝，已有输出保留。
- Node 内存中的 JavaScript 渲染测试覆盖 3 个视图、3 个深度、证据切换、放大目标、缺失图注与来源/原始数据入口；可见英文标签检查通过。此测试不使用真实浏览器，不是视觉排版验收。
- 既有 1/3/12 章及 1/7/53 图像虚构自检通过；CSS 和科学审查规则未改。
- 旧的 compatibility.md、differences.md、independent-review.md 是 .1 版本的历史部署记录，不能据此声称新版已重复完成全部浏览器或独立审查。

本轮内置浏览器禁止打开本地 file:// URL；未绕过该限制，未将新版视图切换、长文本换行和其他语言字体排版标为真实浏览器实测。其他自然语言的完整译文质量、从提示词选择语言的代理行为以及新论文科学内容仍需按实际任务审读；上述脚本不证明这些事项。

## 验证命令

```text
python portable/skill/biomed-paper-reader/scripts/test_language.py
python portable/skill/biomed-paper-reader/scripts/smoke_test.py
python scripts/verify_release.py
```

可用 test_language.py --output <新目录> 保留纯虚构语言样例；如果有 Node.js，可运行 `node scripts/test_language_render.cjs <新目录>/en` 进行内存渲染检查。Node.js 仅用于这个开发测试，不是阅读器或安装器的新依赖。
