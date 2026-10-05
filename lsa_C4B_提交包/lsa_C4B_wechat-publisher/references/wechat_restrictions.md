# WeChat Official Account HTML Restrictions

微信公众号编辑器允许与禁止的完整规则参考。转换器必须强制这些规则以产出可用 HTML。

## 允许的 HTML 标签

```
p, h2, h3, ul, ol, li, span, img, a, table, tr, th, td, br
```

## 禁止的 HTML 标签

| 标签 | 原因 | 处理 |
|------|------|------|
| `<h1>` | 微信保留 h1 给文章标题 | 转为 `<h2>` |
| `<div>` | 渲染不可靠 | 转为 `<p>` 或 `<span>` |
| `<script>` | 安全——总是被剥离 | 完全删除 |
| `<style>` | CSS 必须 inline | 移到 `style=""` |
| `<iframe>` | 禁止外部嵌入 | 删除或转链接 |
| `<video>` | 必须用微信视频嵌入 | 删除或转链接 |
| `<audio>` | 必须用微信音频嵌入 | 删除或转链接 |

## 禁止的 HTML 属性

| 属性 | 原因 | 处理 |
|------|------|------|
| `class` | 微信不支持 CSS class | 删除 |
| `id` | 微信不支持元素 id | 删除 |
| `onclick` 等 | 禁止 JS 事件 | 删除 |

## CSS 规则

### 必须 inline

每个元素都要带 `style="..."`。

```html
<!-- ✅ 正确 -->
<p style="font-size: 16px; color: #333;">Hello</p>

<!-- ❌ 错误——微信会剥离 -->
<style>p { font-size: 16px; }</style>
<p>Hello</p>

<!-- ❌ 错误——微信会剥离 class -->
<p class="body-text">Hello</p>
```

### 允许的 CSS 属性

```
color, background-color, font-size, font-weight, font-style,
line-height, text-align, margin, padding, border, border-left,
border-collapse, text-decoration, display, vertical-align,
max-width, width
```

### 禁止的 CSS

- `position`, `float`, `flex`, `grid` — 布局属性
- `animation`, `transition` — 动效属性
- `@media` 查询 — 不支持响应式断点
- `@font-face` 自定义字体

## 图片规则

| 方式 | 是否可用 | 说明 |
|------|----------|------|
| `<img src="https://...">` | ⚠️ | URL 可访问时可；微信可能重新托管 |
| `<img src="data:image/png;base64,...">` | ✅ | 粘贴时微信转为 CDN 托管 |
| `<img src="data:image/svg+xml;base64,...">` | ❌ | 保存时消失——微信无法重新上传 SVG |
| 内联 `<svg>...</svg>` | ❌ | 完全被剥离 |

**最佳实践**：自包含图片用 PNG base64；照片上传微信图库后用 CDN URL。

## 文章限制

| 限制 | 值 |
|------|-----|
| 最大文章长度 | 约 20,000 汉字 |
| 最大图片数 | 每篇 100 张 |
| 单图最大 | 10 MB |
| 支持图片格式 | PNG, JPG, GIF |
| GIF 最大 | 2 MB |

## 常见坑

1. **保存后格式丢失**：通常用了禁止标签或 CSS
2. **图片消失**：SVG data URI 或失效外链
3. **间距问题**：微信对 margin 的折叠与浏览器不同
4. **代码块损坏**：必须用带 inline 样式的 `<p>`，不能用 `<pre><code>`
5. **表格过宽**：无横向滚动，考虑拆分过宽表格
