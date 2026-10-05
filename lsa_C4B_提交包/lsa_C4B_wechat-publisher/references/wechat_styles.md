# lsa-wechat-publisher — Style Reference

本文件记录 4 套主题的标准 inline CSS 值，供自定义样式时参考。
主题通过 `--theme` 或 frontmatter `theme` 字段选择。

## 主题总览

| 主题 key | 名称 | 强调色 accent | 适用场景 |
|----------|------|---------------|----------|
| `default` | 默认 | `#0366d6` | 通用、技术文章 |
| `accent`  | 蓝色强调 | `#1a73e8` | 科技、产品介绍 |
| `warm`    | 暖橙 | `#e65100` | 生活、学习心得 |
| `minimal` | 极简黑白 | `#444444` | 深度长文、专栏 |

## Typography

### H2（公众号顶级标题）

```
font-size: 22px; font-weight: bold; line-height: 1.6;
color: <accent-or-#333>; margin: 22px 0 12px 0;
```

### H3（次级标题）

```
font-size: 18px; font-weight: bold; line-height: 1.6;
color: <accent-or-#333>; margin: 16px 0 8px 0;
```

### 正文段落

```
font-size: 16px; line-height: 1.75; color: #333; margin: 12px 0;
```

### 列表项

```
font-size: 16px; line-height: 1.75; color: #333; margin: 6px 0;
```

## 代码

### 行内代码

```
background-color: #f5f5f5; color: #d73a49; font-size: 14px; padding: 2px 5px;
```

### 代码块

```
background-color: #f6f8fa; color: #24292e; font-size: 14px;
line-height: 1.6; padding: 16px; margin: 12px 0;
```

## Callout 框配色

| 类型 | 图标 | 背景 | 左边框 | 文字 |
|------|------|------|--------|------|
| NOTE（知识点） | 📘 | `#eef4ff` | `#4a90d9` | `#2b4a77` |
| TIP（提示） | 💡 | `#eefaf0` | `#4caf50` | `#2e5d33` |
| WARNING（注意） | ⚠️ | `#fff6e6` | `#f0a020` | `#7a5200` |
| PRACTICE（实践） | 🔧 | `#f4efff` | `#8e6fd8` | `#46317a` |

callout 统一样式：

```
font-size: 15px; line-height: 1.75; padding: 14px 16px; margin: 14px 0;
border-left: 4px solid <border-color>;
background-color: <bg>; color: <text>;
```

## 元数据头部

### 文章标题（data-title）

```
font-size: 24px; font-weight: bold; line-height: 1.5; color: #111;
text-align: center; margin: 8px 0 14px 0;
```

### 作者/日期行（data-byline）

```
font-size: 14px; color: #999; text-align: center; margin: 0 0 16px 0;
```

### 摘要框（data-summary）

```
font-size: 15px; color: #666; line-height: 1.7; background-color: #fafafa;
padding: 12px 16px; margin: 8px 0 18px 0; border-left: 4px solid #ccc;
```

### 目录（data-toc）

```
background-color: #f6f8fa; color: #333; padding: 14px 18px; margin: 14px 0;
border-left: 4px solid <accent>; font-size: 15px; line-height: 1.8;
```

### 页脚（data-footer）

```
font-size: 13px; color: #999; text-align: center; margin: 28px 0 8px 0;
border-top: 1px solid #eee; padding-top: 14px;
```

## 移动端注意事项

- **正文最小字号**：16px（再小在手机上难读）
- **最大宽度**：手机约 375px
- **行高**：1.75 是中文可读性的甜点值
- **颜色**：避免纯黑 `#000`，用 `#333` 更柔和
- **图片**：始终设置 `max-width: 100%` 防溢出
- **中文排版**：中英文/数字之间加空格（脚本自动处理）
