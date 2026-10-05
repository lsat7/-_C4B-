---
name: lsa-wechat-publisher
description: Convert Markdown or Word documents into copy-paste-ready HTML for WeChat Official Account (微信公众号) publishing. Adds a multi-theme system (default/accent/warm/minimal), callout boxes (📘知识点/💡提示/⚠️注意/🔧实践), an auto-generated table of contents, article metadata (title/author/date/summary), a footer copyright notice, and Chinese typography optimization. Trigger whenever the user asks to convert to WeChat, 公众号文章, 微信公众号格式, 转换成公众号, make WeChat article, generate WeChat HTML, or provides a .md/.docx file and wants it formatted for WeChat publishing.
agent_created: true
---

# lsa-wechat-publisher — Markdown/Word → 公众号 HTML

## Purpose

把一个 Markdown (.md) 或 Word (.docx) 文档转换成可直接粘贴到微信公众号编辑器的
HTML。可以把它理解成公众号的"打印驱动"——给内容，产出能扛住微信严格编辑器规则的排版。

在官方 starter kit（`wechat-publisher`）基础能力之上，本技能新增了 6 项定制能力，
让输出文章"好看、有个性、可定制"：

| 能力 | 说明 | 使用方式 |
|------|------|----------|
| 多主题系统 | 4 套配色（默认/蓝/暖/极简） | `--theme` 或 frontmatter `theme` |
| callout 框 | 📘知识点 / 💡提示 / ⚠️注意 / 🔧实践 | blockquote + `[!TYPE]` 前缀 |
| 自动目录 | 从 h2/h3 生成内嵌目录 | `--toc` 或 frontmatter `toc: true` |
| 文章元数据 | 标题/作者/日期/摘要 | YAML frontmatter |
| 页脚版权 | 自动追加版权声明 | frontmatter `copyright` |
| 中文排版优化 | 中英文间距、代码块保护 | 自动执行 |

## Quick Start

```bash
python scripts/convert_to_wechat.py input.md output.html
python scripts/convert_to_wechat.py input.md output.html --theme accent --toc
```

然后：浏览器打开 `output.html` → Ctrl+A → Ctrl+C → 粘贴到公众号编辑器。

## 主题系统

`--theme` 可选值：`default`（默认）、`accent`（蓝色强调）、`warm`（暖橙）、`minimal`（极简黑白）。
详细的 inline CSS 值见 `references/wechat_styles.md`。

## callout 语法

在 Markdown 中用引用块（`>`）加前缀标记：

```markdown
> [!NOTE] 知识点
> 这里是知识点内容。

> [!WARNING] 注意
> 这里是需要警惕的内容。

> [!TIP] 提示
> 实用小技巧。

> [!PRACTICE] 实践
> 动手试一试。
```

中文别名同样支持：`[!知识点]`、`[!注意]`、`[!提示]`、`[!实践]`。

## frontmatter 元数据

在 Markdown 顶部用 `---` 包裹 frontmatter：

```yaml
---
title: 文章标题
author: lsa
date: 2026-10-05
summary: 一句话摘要，会显示为文章开头的摘要框。
theme: accent
toc: true
copyright: 本文由 AI 辅助创作。
---
```

字段说明：`title`（标题）、`author`（作者）、`date`（日期）、`summary`（摘要）、
`theme`（主题）、`toc`（是否生成目录，true/false）、`copyright`（自定义版权，留空用默认）。

## Supported Input Formats

| 格式 | 处理方式 |
|------|----------|
| Markdown (.md) | `markdown` 库转换，支持表格、围栏代码、frontmatter |
| Word (.docx) | `python-docx` 提取，保留标题/粗体/斜体 |
| HTML (.html) | 直接清洗 |

## WeChat HTML Restrictions

转换器自动强制以下规则（详见 `references/wechat_restrictions.md`）：

- 允许标签：`p, h2, h3, ul, ol, li, span, img, a, table, tr, th, td, br`
- `<h1>` → `<h2>`；`<div>` → `<p>`；`<script>/<style>/<iframe>` → 删除
- `class`/`id` → 删除；CSS 只能 inline（`style="..."`）
- 图片用 PNG base64（SVG 会消失）

## Workflow

1. **读源文件** — 检测 .md/.docx，转成 HTML，解析 frontmatter。
2. **清洗** — 删禁用标签，h1→h2，div→p，代码块/行内代码→带样式元素，blockquote→callout/引用。
3. **中文排版优化** — 中文与英文/数字之间自动加空格（代码块除外）。
4. **生成目录**（可选）— 从 h2/h3 提取。
5. **应用主题样式** — 按选定主题加 inline CSS。
6. **元数据头部 + 页脚** — 标题/作者/日期/摘要 + 版权声明。
7. **清理属性 + 输出** — 删除 class/id/data-*，输出可粘贴 HTML。

## Dependencies

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

脚本首次运行会自动安装缺失依赖。

## Edge Cases

| 情况 | 处理 |
|------|------|
| 空文件 | 报错，不生成空 HTML |
| 超长文章（>10000 字） | 正常处理，提示微信字数上限 |
| 非 UTF-8 编码 | 先试 UTF-8，再回退 GBK |
| 未知主题 | 回退到 default 并提示 |
| 本地图片 | 保留 `<img>` 标签，提示上传微信图库或转 base64 |
| 宽表格 | 主题默认加 `width:100%`，建议拆分过宽表格 |
