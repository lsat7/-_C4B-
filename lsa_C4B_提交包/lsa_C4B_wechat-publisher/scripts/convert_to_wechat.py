#!/usr/bin/env python3
"""
WeChat Publisher — Markdown/Word → 微信公众号 HTML（lsa 定制增强版）

在 starter kit 基础上新增的能力：
  1. 多主题系统（default / accent / warm / minimal）
  2. callout 框（📘知识点 / 💡提示 / ⚠️注意 / 🔧实践）
  3. 自动目录（从 h2/h3 生成内嵌目录）
  4. 文章元数据（标题 / 作者 / 日期 / 摘要，YAML frontmatter）
  5. 页脚版权声明（自动追加）
  6. 中文排版优化（中英文间距、全角标点、段落处理）

用法：
    python convert_to_wechat.py input.md output.html [--theme accent] [--toc]
    python convert_to_wechat.py report.docx output.html --author lsa

然后：浏览器打开 output.html → Ctrl+A → Ctrl+C → 粘贴到公众号编辑器。
"""

import sys
import os
import re
import argparse
from pathlib import Path


# --- 自动安装依赖 ---
def install_dependencies():
    """安装缺失的第三方包（不污染全局环境）。"""
    missing = []
    try:
        import markdown
    except ImportError:
        missing.append("markdown")
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing.append("beautifulsoup4")
    try:
        from docx import Document
    except ImportError:
        missing.append("python-docx")
    try:
        import lxml
    except ImportError:
        missing.append("lxml")

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}...")
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", *missing, "-q"
        ])
        print("Done!\n")


install_dependencies()

import markdown
from bs4 import BeautifulSoup
from bs4 import NavigableString, Tag
from docx import Document


# ============================================================
# 一、主题系统（多主题支持）
# ============================================================
# 每套主题定义：标题/正文/链接/强调色/背景等 inline CSS 值。
# 可通过 --theme 或 frontmatter 的 theme 字段选择。

THEMES = {
    'default': {
        'name': '默认',
        'accent': '#0366d6',
        'h2': 'font-size: 22px; font-weight: bold; line-height: 1.6; color: #333; margin: 22px 0 12px 0;',
        'h3': 'font-size: 18px; font-weight: bold; line-height: 1.6; color: #333; margin: 16px 0 8px 0;',
        'p': 'font-size: 16px; line-height: 1.75; color: #333; margin: 12px 0;',
        'li': 'font-size: 16px; line-height: 1.75; color: #333; margin: 6px 0;',
        'a': 'color: #0366d6; text-decoration: underline;',
        'blockquote': 'background-color: #f9f9f9; color: #666; padding: 12px 16px; margin: 12px 0; border-left: 4px solid #ddd;',
        'code_inline': 'background-color: #f5f5f5; color: #d73a49; font-size: 14px; padding: 2px 5px;',
        'code_block': 'background-color: #f6f8fa; color: #24292e; font-size: 14px; line-height: 1.6; padding: 16px; margin: 12px 0;',
        'table': 'border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;',
        'th': 'background-color: #f6f8fa; color: #24292e; font-weight: bold; padding: 8px; text-align: left; border: 1px solid #ddd;',
        'td': 'padding: 8px; border: 1px solid #ddd; color: #333;',
        'toc_box': 'background-color: #f6f8fa; padding: 14px 18px; margin: 14px 0; border-left: 4px solid #0366d6;',
    },
    'accent': {
        'name': '蓝色强调',
        'accent': '#1a73e8',
        'h2': 'font-size: 22px; font-weight: bold; line-height: 1.6; color: #1a73e8; margin: 22px 0 12px 0;',
        'h3': 'font-size: 18px; font-weight: bold; line-height: 1.6; color: #1a73e8; margin: 16px 0 8px 0;',
        'p': 'font-size: 16px; line-height: 1.75; color: #2b2b2b; margin: 12px 0;',
        'li': 'font-size: 16px; line-height: 1.75; color: #2b2b2b; margin: 6px 0;',
        'a': 'color: #1a73e8; text-decoration: underline;',
        'blockquote': 'background-color: #f0f7ff; color: #41597a; padding: 12px 16px; margin: 12px 0; border-left: 4px solid #1a73e8;',
        'code_inline': 'background-color: #eef4fd; color: #c7254e; font-size: 14px; padding: 2px 5px;',
        'code_block': 'background-color: #f5f9ff; color: #1f2d3d; font-size: 14px; line-height: 1.6; padding: 16px; margin: 12px 0;',
        'table': 'border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;',
        'th': 'background-color: #eaf2ff; color: #1a73e8; font-weight: bold; padding: 8px; text-align: left; border: 1px solid #cfe0ff;',
        'td': 'padding: 8px; border: 1px solid #dde7f5; color: #2b2b2b;',
        'toc_box': 'background-color: #f5f9ff; padding: 14px 18px; margin: 14px 0; border-left: 4px solid #1a73e8;',
    },
    'warm': {
        'name': '暖橙',
        'accent': '#e65100',
        'h2': 'font-size: 22px; font-weight: bold; line-height: 1.6; color: #e65100; margin: 22px 0 12px 0;',
        'h3': 'font-size: 18px; font-weight: bold; line-height: 1.6; color: #e65100; margin: 16px 0 8px 0;',
        'p': 'font-size: 16px; line-height: 1.75; color: #3a2e25; margin: 12px 0;',
        'li': 'font-size: 16px; line-height: 1.75; color: #3a2e25; margin: 6px 0;',
        'a': 'color: #e65100; text-decoration: underline;',
        'blockquote': 'background-color: #fff8e1; color: #7a5c30; padding: 12px 16px; margin: 12px 0; border-left: 4px solid #ff9800;',
        'code_inline': 'background-color: #fdf3e3; color: #c0392b; font-size: 14px; padding: 2px 5px;',
        'code_block': 'background-color: #fff8ee; color: #4a3727; font-size: 14px; line-height: 1.6; padding: 16px; margin: 12px 0;',
        'table': 'border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;',
        'th': 'background-color: #fff3e0; color: #e65100; font-weight: bold; padding: 8px; text-align: left; border: 1px solid #f0d9b5;',
        'td': 'padding: 8px; border: 1px solid #f0e2cc; color: #3a2e25;',
        'toc_box': 'background-color: #fffdf5; padding: 14px 18px; margin: 14px 0; border-left: 4px solid #ff9800;',
    },
    'minimal': {
        'name': '极简黑白',
        'accent': '#444444',
        'h2': 'font-size: 21px; font-weight: bold; line-height: 1.6; color: #111; margin: 22px 0 12px 0;',
        'h3': 'font-size: 17px; font-weight: bold; line-height: 1.6; color: #111; margin: 16px 0 8px 0;',
        'p': 'font-size: 16px; line-height: 1.75; color: #333; margin: 12px 0;',
        'li': 'font-size: 16px; line-height: 1.75; color: #333; margin: 6px 0;',
        'a': 'color: #555; text-decoration: underline;',
        'blockquote': 'background-color: #fafafa; color: #666; padding: 12px 16px; margin: 12px 0; border-left: 4px solid #999;',
        'code_inline': 'background-color: #f3f3f3; color: #333; font-size: 14px; padding: 2px 5px;',
        'code_block': 'background-color: #f7f7f7; color: #333; font-size: 14px; line-height: 1.6; padding: 16px; margin: 12px 0;',
        'table': 'border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;',
        'th': 'background-color: #f3f3f3; color: #111; font-weight: bold; padding: 8px; text-align: left; border: 1px solid #ddd;',
        'td': 'padding: 8px; border: 1px solid #ddd; color: #333;',
        'toc_box': 'background-color: #fafafa; padding: 14px 18px; margin: 14px 0; border-left: 4px solid #999;',
    },
}


# ============================================================
# 二、callout 框（知识点 / 提示 / 注意 / 实践）
# ============================================================
# Markdown 中用 blockquote 加前缀标记触发：
#   > [!NOTE] 知识点标题
#   > 内容……
# 图标与配色如下：

CALLOUTS = {
    'NOTE':      {'icon': '📘', 'label': '知识点', 'bg': '#eef4ff', 'border': '#4a90d9', 'text': '#2b4a77'},
    'TIP':       {'icon': '💡', 'label': '提示',   'bg': '#eefaf0', 'border': '#4caf50', 'text': '#2e5d33'},
    'WARNING':   {'icon': '⚠️', 'label': '注意',   'bg': '#fff6e6', 'border': '#f0a020', 'text': '#7a5200'},
    'PRACTICE':  {'icon': '🔧', 'label': '实践',   'bg': '#f4efff', 'border': '#8e6fd8', 'text': '#46317a'},
}
# 中文别名，方便中文写作时使用
CALLOUT_ALIASES = {
    '知识点': 'NOTE', '知识': 'NOTE', 'NOTE': 'NOTE',
    '提示': 'TIP', 'TIP': 'TIP',
    '注意': 'WARNING', '警告': 'WARNING', 'WARNING': 'WARNING', 'WARN': 'WARNING',
    '实践': 'PRACTICE', '练习': 'PRACTICE', 'PRACTICE': 'PRACTICE', 'TODO': 'PRACTICE',
}

CALLOUT_RE = re.compile(r'^\[!\s*([^\]\s]+)\s*\]\s*(.*)$')


# ============================================================
# 三、标签白名单 / 黑名单 / 允许的 CSS 属性
# ============================================================

ALLOWED_TAGS = {
    'p', 'h2', 'h3', 'ul', 'ol', 'li', 'span', 'img', 'a',
    'table', 'tr', 'th', 'td', 'br',
}

FORBIDDEN_TAGS = {'script', 'style', 'iframe', 'h1', 'div', 'video', 'audio'}

ALLOWED_CSS = {
    'color', 'background-color', 'font-size', 'font-weight',
    'line-height', 'text-align', 'font-style', 'margin',
    'padding', 'border', 'border-left', 'border-collapse',
    'text-decoration', 'width', 'max-width', 'display',
    'vertical-align',
}


# ============================================================
# 四、frontmatter 解析（文章元数据）
# ============================================================
# 支持 YAML 风格 frontmatter（--- 包裹），字段：
#   title / author / date / summary / theme / toc / copyright

def parse_frontmatter(text):
    """从 Markdown 文本顶部解析 frontmatter，返回 (meta, 剩余正文)。"""
    meta = {
        'title': '', 'author': '', 'date': '', 'summary': '',
        'theme': 'default', 'toc': False, 'copyright': '',
    }
    body = text
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
            for line in fm.splitlines():
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, _, value = line.partition(':')
                key = key.strip().lower()
                value = value.strip().strip('"').strip("'")
                if key == 'title':
                    meta['title'] = value
                elif key == 'author':
                    meta['author'] = value
                elif key == 'date':
                    meta['date'] = value
                elif key == 'summary':
                    meta['summary'] = value
                elif key == 'theme':
                    meta['theme'] = value.lower()
                elif key == 'toc':
                    meta['toc'] = value.lower() in ('true', 'yes', '1', 'on')
                elif key in ('copyright', 'footer'):
                    meta['copyright'] = value
    return meta, body


# ============================================================
# 五、输入读取
# ============================================================

def read_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    meta, body = parse_frontmatter(content)
    html = markdown.markdown(body, extensions=[
        'extra', 'fenced_code', 'nl2br', 'sane_lists',
    ])
    return meta, html


def read_docx(filepath):
    doc = Document(filepath)
    parts = []
    meta = {'title': '', 'author': '', 'date': '', 'summary': '',
            'theme': 'default', 'toc': False, 'copyright': ''}

    title_added = False
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style_name = para.style.name if para.style else ''
        if style_name.startswith('Heading'):
            level = style_name.replace('Heading ', '')
            tag = 'h2' if level in ('1', '2') else 'h3'
            if tag == 'h2' and not title_added:
                # 第一个 h2 视为文章标题
                title_added = True
            parts.append(f'<{tag}>{text}</{tag}>')
        else:
            p_html = '<p>'
            for run in para.runs:
                t = run.text
                if not t:
                    continue
                if run.bold and run.italic:
                    p_html += f'<span style="font-weight:bold;font-style:italic;">{t}</span>'
                elif run.bold:
                    p_html += f'<span style="font-weight:bold;">{t}</span>'
                elif run.italic:
                    p_html += f'<span style="font-style:italic;">{t}</span>'
                else:
                    p_html += t
            p_html += '</p>'
            parts.append(p_html)

    return meta, '\n'.join(parts)


# ============================================================
# 六、HTML 清洗（sanitize）
# ============================================================

def _blockquote_text(bq):
    """取 blockquote 纯文本，把 <br> 转成换行。"""
    for br in bq.find_all('br'):
        br.replace_with('\n')
    return bq.get_text()


def _parse_blockquote_text(text):
    """
    按行解析 blockquote 文本，支持一个 blockquote 内多个连续 callout。
    返回 (callouts, plain_lines)：
      callouts: [(ctype, title, body_text), ...]
      plain_lines: 非 callout 的普通引用行列表
    """
    lines = [l.rstrip() for l in text.split('\n')]
    callouts = []
    plain_lines = []
    current = None  # {'ctype':..., 'title':..., 'body':[...]}

    for raw in lines:
        line = raw.strip()
        m = CALLOUT_RE.match(line)
        if m:
            if current:
                callouts.append(current)
            ctype_raw = m.group(1)
            ctype = CALLOUT_ALIASES.get(ctype_raw, CALLOUT_ALIASES.get(ctype_raw.upper()))
            if ctype in CALLOUTS:
                current = {'ctype': ctype, 'title': m.group(2).strip(), 'body': []}
            else:
                # 未知类型，当作普通引用行
                current = None
                plain_lines.append(raw)
        else:
            if current is not None:
                current['body'].append(raw)
            else:
                plain_lines.append(raw)

    if current:
        callouts.append(current)

    result = []
    for c in callouts:
        body = '\n'.join(x for x in c['body'] if x.strip())
        result.append((c['ctype'], c['title'], body))
    return result, [x for x in plain_lines if x.strip()]


def sanitize(soup):
    """清洗为公众号兼容 HTML：
    1. 删除禁用标签 script/style/iframe/video/audio
    2. h1 → h2，div → p
    3. 代码块 / 行内代码 → 带样式的 p / span（标记 data-nospace）
    4. blockquote → callout 框或普通引用 p
    5. strong/em/b/i → span
    """
    for tag_name in ('script', 'style', 'iframe', 'video', 'audio'):
        for el in soup.find_all(tag_name):
            el.decompose()

    for h1 in soup.find_all('h1'):
        h1.name = 'h2'
    for div in soup.find_all('div'):
        div.name = 'p'

    # 代码块 <pre><code> → 带样式的 <p>
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        code_text = code.get_text() if code else pre.get_text()
        p = soup.new_tag('p')
        p.string = code_text
        p['data-nospace'] = '1'
        pre.replace_with(p)

    # 行内 <code> → 带样式的 <span>
    for code in soup.find_all('code'):
        span = soup.new_tag('span')
        span.string = code.get_text()
        span['data-nospace'] = '1'
        code.replace_with(span)

    # blockquote → callout 框或普通引用
    for bq in soup.find_all('blockquote'):
        text = _blockquote_text(bq).strip()
        callouts, plain = _parse_blockquote_text(text)
        if callouts:
            # 一个 blockquote 内可能包含多个 callout，逐一生成并替换
            for ctype, title, body in callouts:
                cfg = CALLOUTS[ctype]
                label = f'{cfg["icon"]} {title}' if title else f'{cfg["icon"]} {cfg["label"]}'
                p = soup.new_tag('p')
                p['data-callout'] = ctype
                p.string = label + ('\n' + body if body else '')
                bq.insert_before(p)
            bq.decompose()
        else:
            p = soup.new_tag('p')
            p['data-blockquote'] = '1'
            p.string = text
            bq.replace_with(p)

    # strong/b → span
    for tag in soup.find_all(['strong', 'b']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['data-bold'] = '1'
        tag.replace_with(span)
    # em/i → span
    for tag in soup.find_all(['em', 'i']):
        span = soup.new_tag('span')
        span.string = tag.get_text()
        span['data-italic'] = '1'
        tag.replace_with(span)

    return soup


# ============================================================
# 七、中文排版优化
# ============================================================
# 在中文与英文/数字之间插入空格，提升专业感。
# 跳过代码块、行内代码（带 data-nospace 的元素）。

def _should_space(node):
    """判断文本节点是否应做中英文间距处理。"""
    for parent in node.parents:
        if not isinstance(parent, Tag):
            continue
        if parent.get('data-nospace') == '1':
            return False
    return True


def optimize_chinese_typography(soup):
    cjk = r'\u4e00-\u9fff'
    re_cjk_ascii = re.compile(f'([{cjk}])([A-Za-z0-9])')
    re_ascii_cjk = re.compile(f'([A-Za-z0-9])([{cjk}])')
    for node in list(soup.find_all(string=True)):
        if not isinstance(node, NavigableString):
            continue
        if not _should_space(node):
            continue
        text = str(node)
        new = re_cjk_ascii.sub(r'\1 \2', text)
        new = re_ascii_cjk.sub(r'\1 \2', new)
        if new != text:
            node.replace_with(NavigableString(new))
    return soup


# ============================================================
# 八、目录生成
# ============================================================

def build_toc(soup, theme):
    """从 h2/h3 生成目录，插入到 body 最前。"""
    headings = soup.find_all(['h2', 'h3'])
    if not headings:
        return soup

    # 跳过文章标题（第一个 h2 若与元数据标题一致，会被标记 data-title，这里不重复判断）
    toc_items = []
    for h in headings:
        if h.get('data-title') == '1':
            continue
        level = 0 if h.name == 'h2' else 1
        toc_items.append((level, h.get_text().strip()))

    if not toc_items:
        return soup

    # 构建目录容器 <p>
    toc_p = soup.new_tag('p')
    toc_p['data-toc'] = '1'
    lines = ['📑 目录']
    for level, title in toc_items:
        if level == 0:
            lines.append(title)
        else:
            lines.append('　· ' + title)
    toc_p.string = '\n'.join(lines)

    # 插入到 body 第一个元素之前
    body = soup.find('body')
    if body is None:
        return soup
    body.insert(0, toc_p)
    return soup


# ============================================================
# 九、元数据头部 / 页脚
# ============================================================

def build_header(soup, meta, theme):
    """根据元数据生成文章头部（标题 + 作者/日期 + 摘要）。"""
    body = soup.find('body')
    if body is None:
        return soup

    elements = []
    if meta.get('title'):
        title = soup.new_tag('h2')
        title['data-title'] = '1'
        title.string = meta['title']
        elements.append(title)

    byline_bits = []
    if meta.get('author'):
        byline_bits.append(f'✍️ {meta["author"]}')
    if meta.get('date'):
        byline_bits.append(f'🗓️ {meta["date"]}')
    if byline_bits:
        byline = soup.new_tag('p')
        byline['data-byline'] = '1'
        byline.string = '　'.join(byline_bits)
        elements.append(byline)

    if meta.get('summary'):
        summary = soup.new_tag('p')
        summary['data-summary'] = '1'
        summary.string = meta['summary']
        elements.append(summary)

    for el in reversed(elements):
        body.insert(0, el)
    return soup


def build_footer(soup, meta, theme):
    """追加页脚版权声明。"""
    body = soup.find('body')
    if body is None:
        return soup
    copyright_text = meta.get('copyright')
    if not copyright_text:
        copyright_text = '本文由 AI 辅助创作，使用 lsa 的 wechat-publisher 技能排版。'
    footer = soup.new_tag('p')
    footer['data-footer'] = '1'
    footer.string = copyright_text
    body.append(footer)
    return soup


# ============================================================
# 十、样式应用
# ============================================================

def apply_styles(soup, theme_key):
    theme = THEMES.get(theme_key, THEMES['default'])

    style_map = {
        'h2': theme['h2'],
        'h3': theme['h3'],
        'p': theme['p'],
        'li': theme['li'],
        'table': theme['table'],
        'th': theme['th'],
        'td': theme['td'],
        'a': theme['a'],
    }
    for tag_name, style in style_map.items():
        for el in soup.find_all(tag_name):
            if el.get('style'):
                continue
            el['style'] = style

    # 特殊元素
    for el in soup.find_all(attrs={'data-nospace': '1'}):
        if el.name == 'p':
            el['style'] = theme['code_block']
        elif el.name == 'span':
            el['style'] = theme['code_inline']

    for el in soup.find_all(attrs={'data-blockquote': '1'}):
        el['style'] = theme['blockquote']

    # callout 框
    for el in soup.find_all(attrs={'data-callout': True}):
        ctype = el.get('data-callout')
        cfg = CALLOUTS.get(ctype)
        if cfg:
            el['style'] = (
                f'background-color: {cfg["bg"]}; color: {cfg["text"]}; '
                f'padding: 14px 16px; margin: 14px 0; border-left: 4px solid {cfg["border"]}; '
                f'font-size: 15px; line-height: 1.75;'
            )

    # 目录
    for el in soup.find_all(attrs={'data-toc': '1'}):
        el['style'] = (
            f'background-color: #f6f8fa; color: #333; padding: 14px 18px; '
            f'margin: 14px 0; border-left: 4px solid {theme["accent"]}; '
            f'font-size: 15px; line-height: 1.8;'
        )
        # 目录第一行加粗
        text = el.string or ''
        el.string = ''  # 先清空，重建第一行加粗
        el.clear()
        lines = text.split('\n')
        first = soup.new_tag('span')
        first['data-bold'] = '1'
        first.string = lines[0]
        el.append(first)
        if len(lines) > 1:
            el.append(NavigableString('\n' + '\n'.join(lines[1:])))

    # 加粗 / 斜体 span
    for el in soup.find_all(attrs={'data-bold': '1'}):
        el['style'] = 'font-weight: bold;'
    for el in soup.find_all(attrs={'data-italic': '1'}):
        el['style'] = 'font-style: italic;'

    # 元数据头部
    for el in soup.find_all(attrs={'data-title': '1'}):
        el['style'] = 'font-size: 24px; font-weight: bold; line-height: 1.5; color: #111; text-align: center; margin: 8px 0 14px 0;'
    for el in soup.find_all(attrs={'data-byline': '1'}):
        el['style'] = 'font-size: 14px; color: #999; text-align: center; margin: 0 0 16px 0;'
    for el in soup.find_all(attrs={'data-summary': '1'}):
        el['style'] = 'font-size: 15px; color: #666; line-height: 1.7; background-color: #fafafa; padding: 12px 16px; margin: 8px 0 18px 0; border-left: 4px solid #ccc;'
    # 页脚
    for el in soup.find_all(attrs={'data-footer': '1'}):
        el['style'] = 'font-size: 13px; color: #999; text-align: center; margin: 28px 0 8px 0; border-top: 1px solid #eee; padding-top: 14px;'

    return soup


def clean_attributes(soup):
    """删除 class/id/data-*，unwrap 非白名单标签。"""
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            if attr in ('class', 'id') or attr.startswith('data-'):
                del tag.attrs[attr]
        if tag.name not in ALLOWED_TAGS and tag.name not in ('html', 'head', 'body', '[document]'):
            tag.unwrap()
    return soup


# ============================================================
# 十一、主转换流程
# ============================================================

def convert(input_path, output_path, options):
    path = Path(input_path)
    if not path.exists():
        print(f"❌ Error: File '{input_path}' not found.")
        return False

    ext = path.suffix.lower()

    print(f"📖 Reading {path.name} ({ext})...")
    if ext == '.md':
        meta, html = read_markdown(input_path)
    elif ext == '.docx':
        meta, html = read_docx(input_path)
    elif ext in ('.html', '.htm'):
        with open(input_path, 'r', encoding='utf-8') as f:
            html = f.read()
        meta = {'title': '', 'author': '', 'date': '', 'summary': '',
                'theme': 'default', 'toc': False, 'copyright': ''}
    else:
        print(f"❌ Unsupported format: {ext}")
        print("   Supported: .md, .docx, .html")
        return False

    # 命令行参数覆盖 frontmatter
    if options.theme:
        meta['theme'] = options.theme
    if options.toc:
        meta['toc'] = True
    if options.author:
        meta['author'] = options.author
    if options.no_footer:
        meta['copyright'] = ''  # 禁用页脚

    theme_key = meta.get('theme', 'default')
    if theme_key not in THEMES:
        print(f"⚠️  未知主题 '{theme_key}'，回退到 default。可用：{', '.join(THEMES)}")
        theme_key = 'default'

    print("🧹 Sanitizing HTML for WeChat...")
    soup = BeautifulSoup(html, 'lxml')
    soup = sanitize(soup)

    print("🀄 Optimizing Chinese typography...")
    soup = optimize_chinese_typography(soup)

    if meta.get('toc'):
        print("📑 Generating table of contents...")
        soup = build_toc(soup, theme_key)

    print("📇 Adding metadata header & footer...")
    soup = build_header(soup, meta, theme_key)
    soup = build_footer(soup, meta, theme_key)

    print(f"🎨 Applying theme styles ({THEMES[theme_key]['name']})...")
    soup = apply_styles(soup, theme_key)

    print("✂️  Cleaning non-allowed attributes...")
    soup = clean_attributes(soup)

    body = soup.find('body')
    if body:
        content = '\n'.join(str(child) for child in body.children if str(child).strip())
    else:
        content = str(soup)

    output_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta.get('title') or 'WeChat Article Preview'}</title>
</head>
<body style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;">
{content}
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ Done! {output_path} ({size_kb:.1f} KB)")
    print(f"\n📋 Next steps:")
    print(f"   1. Open {output_path} in a browser to preview")
    print(f"   2. Ctrl+A → Ctrl+C (select all, copy)")
    print(f"   3. Go to mp.weixin.qq.com → create new article")
    print(f"   4. Ctrl+V (paste into editor)")
    print(f"   5. Upload images via WeChat media library if needed")
    print(f"   6. Preview on phone → publish!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='WeChat Publisher — Markdown/Word → 微信公众号 HTML（lsa 定制增强版）'
    )
    parser.add_argument('input', help='输入文件 (.md / .docx / .html)')
    parser.add_argument('output', help='输出 HTML 文件')
    parser.add_argument('--theme', choices=list(THEMES.keys()),
                        help='主题（覆盖 frontmatter）')
    parser.add_argument('--toc', action='store_true', help='生成目录')
    parser.add_argument('--author', help='作者（覆盖 frontmatter）')
    parser.add_argument('--no-footer', action='store_true', help='不追加页脚版权')
    args = parser.parse_args()

    success = convert(args.input, args.output, args)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
