---
title: 5 分钟上手 lsa-wechat-publisher
author: lsa
date: 2026-10-05
summary: 这是一个展示全部新增能力的示例：主题、callout、目录、元数据、页脚、中文排版优化。
theme: accent
toc: true
copyright: 本文使用 lsa 的 wechat-publisher 技能排版。
---

## 为什么要做这个技能

在 AI 时代，**个人能力的价值不在于自己用了多少次，而在于能被复制多少次**。
一个能一键把 Markdown 变成精美公众号文章的技能，就是一个"内容生产力引擎"。

## 它解决了什么痛点

公众号编辑器有一堆技术坑：只认 inline CSS、禁止 h1 和 div、图片要走 CDN、SVG 会消失。
这个技能把这些坑一次性填平。

> [!NOTE] 知识点
> 微信只允许 `p, h2, h3, ul, ol, li, span, img, a, table, tr, th, td, br` 这十几个标签。

## 新增能力一览

| 能力 | 难度 | 价值 |
|------|------|------|
| 多主题 | ★★ | 让文章有不同风格 |
| callout 框 | ★★ | 公众号核心排版元素 |
| 自动目录 | ★★ | 长文必备 |
| 中文排版 | ★★★ | 专业感提升 |

## 三个主题预览

- `default`：通用技术文章，稳妥
- `accent`：蓝色强调，科技感
- `warm`：暖橙，适合学习心得

> [!TIP] 提示
> 用 `--theme accent` 或 frontmatter 里写 `theme: accent` 即可切换主题。

## 动手试试

```bash
python scripts/convert_to_wechat.py input.md output.html --theme accent --toc
```

> [!WARNING] 注意
> 图片一定要用 PNG base64 或上传微信图库，SVG 会在保存时消失。

> [!PRACTICE] 实践
> 拿你最近写的一篇 Markdown 笔记跑一遍，看看效果如何。

## 写在最后

先交比不交强，迭代比完美主义强。这个技能就是从一个 starter kit"拿来"改出来的。
