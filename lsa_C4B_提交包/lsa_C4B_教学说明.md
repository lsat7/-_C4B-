# lsa · C4B 教学说明（怎么安装、怎么用）

> 本说明面向"拿到这个技能包的其他人"，目标是：**照着做，5 分钟就能生成自己的公众号文章。**

## 一、这是什么

`lsa_C4B_wechat-publisher` 是一个公众号文章生成技能：把 Markdown / Word 文档一键转换成
可直接粘贴到微信公众号编辑器的 HTML，并自带排版美化。

## 二、目录结构

```
lsa_C4B_wechat-publisher/
├── SKILL.md                          # 主指令（技能入口）
├── README.md                         # 简介
├── scripts/
│   └── convert_to_wechat.py          # 核心转换脚本
├── references/
│   ├── wechat_styles.md              # 4 套主题的样式值参考
│   └── wechat_restrictions.md        # 公众号限制规则
└── examples/
    ├── sample_article.md             # 示例输入
    └── sample_output.html            # 示例输出
```

## 三、安装

### 1. 准备 Python 环境

需要 Python 3.8+。依赖包：

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

> 脚本首次运行会自动检测并安装缺失依赖，一般无需手动装。

### 2. 拿到技能目录

把 `lsa_C4B_wechat-publisher/` 目录放到任意位置即可（无需全局安装）。

## 四、使用

### 最简用法

```bash
python scripts/convert_to_wechat.py 你的文章.md 输出.html
```

### 完整用法（带主题和目录）

```bash
python scripts/convert_to_wechat.py 你的文章.md 输出.html --theme accent --toc --author 你的名字
```

### 支持的主题

`default`（默认）、`accent`（蓝色强调）、`warm`（暖橙）、`minimal`（极简黑白）。

## 五、进阶：用 frontmatter 控制元数据

在 Markdown 顶部加一段 frontmatter：

```yaml
---
title: 文章标题
author: 你的名字
date: 2026-10-05
summary: 一句话摘要
theme: accent
toc: true
copyright: 本文由 AI 辅助创作。
---
```

## 六、callout 语法

在 Markdown 中用引用块加前缀：

```markdown
> [!NOTE] 知识点
> 内容

> [!WARNING] 注意
> 内容

> [!TIP] 提示
> 内容

> [!PRACTICE] 实践
> 内容
```

中文别名同样可用：`[!知识点]`、`[!注意]`、`[!提示]`、`[!实践]`。

## 七、发布到公众号（5 步）

1. 浏览器打开生成的 `输出.html`；
2. `Ctrl+A` 全选 → `Ctrl+C` 复制；
3. 打开公众号后台 `mp.weixin.qq.com`，新建图文；
4. `Ctrl+V` 粘贴到编辑器；
5. 手机端预览 → 满意后发布。

> 图片注意：本地图片请先上传公众号图库或用 PNG base64，SVG 会在保存时消失。

## 八、常见问题

| 问题 | 解决 |
|------|------|
| 报缺依赖 | 手动 `pip install markdown beautifulsoup4 python-docx lxml` |
| 输出样式不对 | 确认 `--theme` 拼写正确，未知主题会自动回退 default |
| 目录没出现 | 加 `--toc` 或 frontmatter `toc: true` |
| 中英文挤在一起 | 脚本已自动处理，代码块会被正确跳过 |
