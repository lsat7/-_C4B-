# lsa · C4B AI 日志（skill-creator 使用过程完整记录）

> 本日志记录我使用 `skill-creator` 技能把公众号 starter kit 改造成 `lsa-wechat-publisher`
> 的完整过程，含每一轮 prompt、AI 输出要点、发现的问题与迭代。这是评审重点之一。

---

## 一、前置：加载 skill-creator，理解元技能流程

**Prompt（我对 AI 说的第一句话）：**

> 我要把一份 WeChat 公众号文章生成的 starter kit 改造成我自己的版本，
> 请用 skill-creator 技能引导我完成。

**AI（skill-creator）输出的关键指引：**

- 技能 = `SKILL.md`（必需）+ 可选 `scripts/`（确定性代码）、`references/`（按需加载的文档）、`assets/`（输出用资源）。
- 开发流程六步：**理解示例 → 规划内容 → 初始化 → 编辑 → 打包 → 迭代**。
- SKILL.md 的 YAML frontmatter 必须含 `name` + `description`，且要加 `agent_created: true`。
- 写作风格用祈使/不定式（verb-first），不用第二人称。
- 打包用 `package_skill.py`，会自动校验 frontmatter、命名、结构。

**我的理解**：skill-creator 的价值不是"替我写代码"，而是给了一套**结构化流程 + 校验标准**，避免我拍脑袋瞎写。

---

## 二、第 1 轮：读代码，理解 starter kit 每个模块

**Prompt：**

> 帮我读懂 c4b-wechat-publisher-starter 的 convert_to_wechat.py，
> 讲清楚 read_markdown / read_docx / sanitize_html / apply_inline_styles / WECHAT_STYLES 各自干什么。

**AI 输出要点（我的阅读笔记）：**

| 模块 | 职责 | 我注意到的可改进点 |
|------|------|--------------------|
| `read_markdown()` | `markdown` 库转 HTML（extra/fenced_code/nl2br） | 无 frontmatter、无主题 |
| `read_docx()` | `python-docx` 提取标题/粗斜体 | 无元数据提取 |
| `sanitize()` | 删 script/style/iframe，h1→h2，div→p，code/blockquote→带样式 p | blockquote 处理粗暴，`get_text()` 丢内联格式 |
| `apply_styles()` | 按 `STYLES` 字典加 inline CSS | 只有一套硬编码样式 |
| `STYLES` 字典 | 各元素默认样式 | 单一配色，无法切换 |

**结论**：starter 的"确定性转换"是好的，缺的是"可定制性"——正好对应挑战文档里列的 10 个"缺少的能力"。

---

## 三、第 2 轮：规划要新增的能力（intent → interview）

**Prompt：**

> 我决定至少新增 6 项能力：多主题、callout 框、自动目录、文章元数据、页脚版权、中文排版优化。
> 帮我评估每项的技术方案和边界情况。

**AI 输出要点（方案定稿）：**

1. **多主题** → 用 `THEMES` 字典 + `--theme` / frontmatter `theme` 字段。
2. **callout 框** → 复用 blockquote，加 `> [!NOTE]` 前缀标记，转成带图标的 `<p>`。
   - *边界情况*：markdown 会把连续的 `>` 行合并，多个相邻 callout 可能并成一个 blockquote。
3. **自动目录** → 从 h2/h3 提取，生成目录 `<p>`。
4. **文章元数据** → YAML frontmatter（title/author/date/summary），生成头部。
5. **页脚版权** → frontmatter `copyright` 字段 + 默认值。
6. **中文排版** → 中英文/数字之间加空格，**代码块要跳过**。

---

## 四、第 3 轮：写 SKILL.md 和增强版脚本（draft）

**Prompt：**

> 基于上面的方案，帮我写出改造后的 SKILL.md 和增强版 convert_to_wechat.py。

**AI 输出**：生成了完整的 SKILL.md（frontmatter + 六项能力说明 + 用法）和约 600 行增强脚本。

**我做的关键决策（不是照单全收）：**

- 主题从 starter 建议的 3 套扩到 4 套，并把 callout 配色也纳入主题体系。
- callout 用「按行解析」而非「正则匹配整个 p」，因为预判到 markdown 会合并 blockquote 行。
- 中文排版用 `data-nospace` 标记保护代码块，最后统一清理 `data-*`。

---

## 五、第 4 轮：跑 eval，发现 3 个真实 bug（test）

**Prompt：**

> 跑 examples/sample_article.md，检查输出是否正确。

**实际运行 + 发现的问题（这是最值钱的迭代）：**

| # | 现象 | 根因 | 修复 |
|---|------|------|------|
| 1 | callout 没转成框，`[!NOTE]` 原样输出 | markdown 把多行 `>` 合并成一个 `<p>`，我的正则用 `$` 无法跨行匹配 | 改为「取文本 → 按行 split → 逐行识别 `[!TYPE]`」，一个 blockquote 支持多个连续 callout |
| 2 | 日志打印 `theme styles (%s)` 字面量 | `print()` 用逗号分隔，未做 `%` 格式化 | 改成 f-string |
| 3 | 标题/摘要/页脚没有 inline 样式 | 元数据头部和页脚在 `apply_styles()` 之后才插入 | 把 `build_header`/`build_footer` 移到 `apply_styles` 之前 |

**结论**：eval 不是"跑一遍能出文件"就完事，而是**逐项核对输出 HTML 是否真的符合预期**。三个 bug 都是"肉眼扫一遍输出"才发现的。

---

## 六、第 5–6 轮：修复 + 回归（iterate）

- 第 5 轮：重写 blockquote 处理（新增 `_blockquote_text` / `_parse_blockquote_text` 两个辅助函数），验证 4 种 callout 全部正确渲染。
- 第 6 轮：调整转换顺序，验证元数据头部/页脚样式正确。

**回归测试结果**：

```
✅ 4 种 callout（📘💡⚠️🔧）正确渲染，配色/图标正确
✅ 连续两个 callout（WARNING + PRACTICE）正确拆分
✅ 目录从 h2/h3 自动生成
✅ 标题居中 / byline 居中 / 摘要框 / 页脚 均有 inline 样式
✅ 表格、代码块、行内代码、列表、粗体、斜体 正常
✅ 中英文间距自动处理，代码块不受影响
```

---

## 七、第 7 轮：写正式文章并端到端发布验证

**Prompt：**

> 用这个技能把《从「工具使用者」到「内容工厂主理人」》转成公众号 HTML。

**结果**：`lsa_C4B_output.html`（13.7 KB）生成成功，浏览器预览排版正常，可直接 Ctrl+A/Ctrl+C 粘贴到公众号编辑器。

---

## 八、总结：skill-creator 用在哪了

| skill-creator 步骤 | 我在 C4B 中的对应动作 |
|--------------------|------------------------|
| Step 1 理解示例 | 读 starter 的 5 个模块，明确输入输出 |
| Step 2 规划内容 | 定 6 项新能力的方案与边界 |
| Step 3 初始化 | 建立 `lsa_C4B_wechat-publisher/` 目录结构 |
| Step 4 编辑 | 写 SKILL.md + 增强脚本 + references |
| Step 5 打包 | 用 `package_skill.py` 校验并打包 |
| Step 6 迭代 | 3 个 bug 的发现与修复 |

**一句话结论**：skill-creator 帮我完成了「从想法到可复用技能」的正规化，而 eval 环节逼出了 3 个真实 bug——**不跑 eval，就不知道技能是坏的。**
