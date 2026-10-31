# 内容契约 v1

`evidence.json` 是唯一科学内容源，UTF-8。模板只负责呈现，不编写新结论。生成器拒绝断裂引用、路径逃逸、资产哈希变化、没有证据的关键段落。

- `schema_version`: 1。
- `presentation`（新任务必填，旧输入可省略）：`language` 为目标语言标签（zh-CN、en 等），可选 `labels` 完整译表、`audit_path` 审查报告相对路径。选择规则、其他语言和原文保留要求见 [输出语言配置](output-language.md)。
- `paper`: `title`, `citation`, `doi`, `scope`, `status`, `intro`。
- `sources[]`: `id`, `label`, `path`（相对于 evidence.json 父目录，或绝对路径）, `sha256`, `pages`, `page_sizes`（逐页宽高，PDF points）, `status`。规范化PDF应另记`original_path`/`original_sha256`以保留原始输入链；original_path 遵循同一相对路径规则。外部文献可用 `url` 和 `status`，不假装本地已读。
- `assets[]`: `id`, `label`, `path`（输出内相对路径）, `sha256`, `source_id`, `source_sha256`, `page`, `bbox`, `dpi`, `width`, `height`。焦点裁图仍关联整图和原始页；不能只写一个不校验的source_id。
- `methods[]`: `id`, `title`, `text`, `sources[]`（`source_id`, `page`, `locator`）。
- `evidence[]`: `id`, `title`, `figure`, `panels`, `asset`（整图ID）, 可选 `focus_asset`，`metric`（独立读出）, `sample_unit`, `summary`, `details[]`, `limits[]`, `methods[]`（ID），`sources[]`（定位），`captions[]`（原图注文本，注明转录来源）。
- `chapters[]`: `id`, `title`, `question`, `evidence[]`（ID）, `blocks[]`, `background[]`。
- `blocks[]`: `id`（全局唯一科学主张ID）, `kind`（原文转述/结果/作者解释/AI推论/外部知识）, `depth`（1速览、2导师、3审查）, `text`, `evidence[]`。一条关键结论不得仅指另一个AI摘要。
- `background[]`: `level`（1/2/3）, `title`, `kind`, `text`, `evidence[]`，可附外部 `sources[]`。数学模型注明变量、假设和非本文测量边界。
- `relations[]`: `from`, `to`（章节ID）, `label`, `type`（推进/支持/限定/待验证）；关系图不能把顺序等同已证因果。
- `limitations[]`: 每项是读者可理解的范围或差异说明。

不需 JSON 内嵌全部原PDF。保留可独立搬移的读物和图像；绝对源路径只用于同机溯源。引用指向具体PDF页和panel/段落，不能仅给DOI。全文原图注可置于折叠区，与中文解释分开。HTML正文仅显示depth≤所选深度；Markdown始终包含所有深度和所有背景。来源、方法、限制和图注在两种输出中均可访问。

生成器严格要求本地源文件存在且哈希一致；搬移后阅读HTML不需要源PDF，重新构建则需恢复可核查源路径。页界校验依据已记录page_sizes，不能代替对原PDF的实际页数和裁图目视/像素复核。无可读图注时必须填写`caption_missing_reason`，不得静默丢弃。可用`raw_data[]`保存仓库URL与下载/复算状态。
