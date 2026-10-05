# lsa-wechat-publisher

把 Markdown / Word 一键转成微信公众号可粘贴 HTML 的技能包。

## 这是什么

这是对官方 starter kit `wechat-publisher` 的定制增强版，新增了 6 项能力：

- 多主题（default / accent / warm / minimal）
- callout 框（📘知识点 / 💡提示 / ⚠️注意 / 🔧实践）
- 自动目录
- 文章元数据（标题 / 作者 / 日期 / 摘要）
- 页脚版权声明
- 中文排版优化

## 目录结构

```
lsa_C4B_wechat-publisher/
├── SKILL.md                          # 主指令
├── README.md                         # 本文件
├── scripts/
│   └── convert_to_wechat.py          # 转换脚本
├── references/
│   ├── wechat_styles.md              # 主题样式参考
│   └── wechat_restrictions.md        # 公众号限制规则
└── examples/
    ├── sample_article.md             # 示例输入
    └── sample_output.html            # 示例输出
```

## 安装

```bash
pip install markdown beautifulsoup4 python-docx lxml
```

（脚本首次运行会自动安装缺失依赖）

## 使用

```bash
python scripts/convert_to_wechat.py input.md output.html
python scripts/convert_to_wechat.py input.md output.html --theme accent --toc --author lsa
```

详细说明见 `SKILL.md`。
