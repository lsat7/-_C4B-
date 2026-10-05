# lsa · C4B 拿来说明（从 starter kit 拿了什么、改了什么、为什么）

> 命名规范：`姓名拼音_C4B_内容描述.扩展名`，本文姓名统一为 `lsa`。

## 一、我拿了什么

我从随挑战附带的 `c4b-wechat-publisher-starter.zip` 出发，完整保留了它的"骨架"：

| 模块 | 拿了什么 | 状态 |
|------|----------|------|
| `SKILL.md` | 主指令结构（frontmatter + Purpose + Quick Start + Workflow） | ✏️ 改造 |
| `scripts/convert_to_wechat.py` | 转换脚本骨架（读文件 → sanitize → apply_styles → clean → 输出） | ✏️ 大幅增强 |
| `references/wechat_styles.md` | 样式参考文档 | ✏️ 更新为 4 套主题 |
| `references/wechat_restrictions.md` | 公众号限制规则（标签白名单/黑名单、图片规则） | ✅ 基本沿用 |
| `examples/` | 示例输入/输出 | ✏️ 重写为展示新能力 |

**具体保留的"确定性"逻辑（没重造轮子）：**

- `ALLOWED_TAGS` / `FORBIDDEN_TAGS` 标签白名单黑名单
- `sanitize()` 里的 h1→h2、div→p、script/style/iframe 删除
- 代码块 → 带样式 `<p>`、行内代码 → 带样式 `<span>` 的思路
- `apply_styles()` 的"已有 style 不覆盖"规则
- `.md` / `.docx` 双格式读取

## 二、我改了什么

### 改动 1：样式配置从"单套字典"升级为"多主题系统"

**原来**：一个写死的 `STYLES` 字典，只有一套配色。

**改成**：`THEMES` 字典包含 `default / accent / warm / minimal` 四套主题，每套定义标题、正文、链接、强调色、callout 配色等全部 inline CSS 值，通过 `--theme` 或 frontmatter `theme` 字段切换。

**为什么**：挑战文档说 starter "主题/配色系统 ❌ 缺失"，而"让文章有不同风格"是"好看、有个性、可定制"的直接体现。

### 改动 2：新增 callout 框（4 种）

**原来**：blockquote 只能转成一个灰色引用块。

**改成**：blockquote + `> [!NOTE]` 前缀触发 callout，支持 📘知识点 / 💡提示 / ⚠️注意 / 🔧实践 四种（含中文别名 `[!知识点]` 等），每种独立配色图标。

**为什么**：callout 是公众号文章的核心排版元素，挑战文档明确列为"缺少的能力"第一名。

### 改动 3：新增自动目录

**原来**：无目录。

**改成**：从 h2/h3 提取标题，生成带"📑 目录"的目录框，`--toc` 或 frontmatter `toc: true` 开启。

**为什么**：长文必备，挑战文档列为"缺少的能力"。

### 改动 4：新增文章元数据

**原来**：无标题/作者/日期/摘要概念。

**改成**：解析 YAML frontmatter（title/author/date/summary），生成居中标题 + 作者日期行 + 摘要框。

**为什么**：完善文章结构，实际发布必需。

### 改动 5：新增页脚版权

**原来**：无页脚。

**改成**：自动追加版权声明，frontmatter `copyright` 可自定义。

**为什么**：实际发布必需，挑战文档列为"缺少的能力"。

### 改动 6：新增中文排版优化

**原来**：中英文之间无间距处理。

**改成**：中文与英文/数字之间自动加空格，用 `data-nospace` 标记保护代码块，最后统一清理。

**为什么**：专业感提升，挑战文档列为"缺少的能力"（难度 ★★★）。

## 三、为什么这么改（设计原则）

1. **每个改动都对应一个真实痛点**，不炫技。判断标准：能不能让"输入 → 输出"更顺滑。
2. **保留 starter 的确定性部分**，只在它"缺"的地方做加法——这是拿来主义，不是重写。
3. **配置优先于硬编码**：主题、callout、元数据都走"配置/声明"，让技能可复用、可被别人定制。
4. **满足 C4 四条件**：
   - 可复用：别人装了这个技能，直接 `python convert_to_wechat.py x.md y.html` 就能生成自己的文章；
   - 可执行：一条命令跑通；
   - 可验证：给定 md 输入，输出公众号 HTML 可预期；
   - IO 明确：输入 md/docx，输出公众号 HTML。

## 四、还参考了什么

- `skill-creator`：必须使用的"做技能的技能"，用于结构化开发和打包校验（见 AI 日志）。
- `wechat_restrictions.md`：公众号限制规则，沿用其标签白名单/图片规则。
- `wechat-math-html`（了解）：其 PNG base64 方案暂未纳入本文（本文不含公式），已作为后续迭代方向记录在 AAR。
