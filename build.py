"""產生棉棉兔記帳的隱私權政策與使用條款網頁。

來源是主程式儲存庫的 `上架準備/隱私權政策.md`、`上架準備/使用條款.md`，
只取「## 繁體中文」「## 日本語」「## English」「## 简体中文」各段的內容。

用法：python3 build.py [主程式儲存庫路徑]（預設 ~/Projects/Money_Manager）
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Projects/Money_Manager") / "上架準備"

LANGS = [  # (資料夾, md 段落標題, html lang, 切換列顯示)
    ("zh-Hant", "繁體中文", "zh-Hant", "繁中"),
    ("ja", "日本語", "ja", "日本語"),
    ("en", "English", "en", "English"),
    ("zh-Hans", "简体中文", "zh-Hans", "简中"),
]
PAGES = {"privacy": "隱私權政策.md", "terms": "使用條款.md"}
NAV = {  # 頁首兩個分頁的名稱
    "zh-Hant": ("隱私權政策", "使用條款"),
    "ja": ("プライバシーポリシー", "利用規約"),
    "en": ("Privacy Policy", "Terms of Use"),
    "zh-Hans": ("隐私政策", "使用条款"),
}

CSS = """
:root{--bg:#F6F0E6;--card:#FFFDF8;--ink:#3B3128;--sub:#8A7B6C;--line:#E6DACB;--accent:#C0794B;--chip:#EFE4D4}
@media (prefers-color-scheme:dark){:root{--bg:#14110E;--card:#1E1A16;--ink:#EDE3D6;--sub:#A3968A;--line:#3A322B;--accent:#E2A174;--chip:#2A241F}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 -apple-system,BlinkMacSystemFont,"Hiragino Sans","PingFang TC","PingFang SC","Noto Sans CJK TC",sans-serif;-webkit-text-size-adjust:100%}
.wrap{max-width:760px;margin:0 auto;padding:20px 16px 56px}
header{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;margin-bottom:18px}
.tabs,.langs{display:flex;flex-wrap:wrap;gap:6px}
.tabs a,.langs a{padding:6px 12px;border-radius:999px;text-decoration:none;color:var(--sub);background:var(--chip);font-size:14px}
.tabs a.on,.langs a.on{background:var(--accent);color:#fff}
article{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:24px 22px}
h1{font-size:24px;line-height:1.35;margin:0 0 4px}
h2{font-size:18px;margin:28px 0 8px}
.date{color:var(--sub);font-size:14px;margin:0 0 18px}
p{margin:0 0 12px}
ul{margin:0 0 12px;padding-left:22px}
li{margin:4px 0}
a{color:var(--accent);word-break:break-all}
.table{overflow-x:auto;margin:0 0 12px}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:9px 8px}
th{color:var(--sub);font-weight:600;white-space:nowrap}
td:first-child{white-space:nowrap;font-weight:600}
footer{color:var(--sub);font-size:13px;text-align:center;margin-top:20px}
"""


def inline(text: str) -> str:
    out, pos = [], 0
    pattern = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|(https?://[^\s）)]+)")
    for m in pattern.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1):
            out.append(f"<strong>{html.escape(m.group(1))}</strong>")
        elif m.group(2):
            out.append(f'<a href="{html.escape(m.group(3))}">{html.escape(m.group(2))}</a>')
        else:
            url = html.escape(m.group(4))
            out.append(f'<a href="{url}">{url}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def md_to_html(md: str) -> tuple[str, str]:
    lines = md.strip().splitlines()
    parts, title, i = [], "", 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
        elif line.startswith("# "):
            title = line[2:].strip()
            parts.append(f"<h1>{inline(title)}</h1>")
            # 標題下一個非空行是日期
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            parts.append(f'<p class="date">{inline(lines[i].strip())}</p>')
            i += 1
        elif line.startswith("## "):
            parts.append(f"<h2>{inline(line[3:])}</h2>")
            i += 1
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            parts.append(f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|- |\|)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            parts.append(f"<p>{inline(' '.join(para))}</p>")
    return title, "\n".join(parts)


def sections(md: str) -> dict[str, str]:
    found, current = {}, None
    labels = {label for _, label, _, _ in LANGS}
    for line in md.splitlines():
        if line.startswith("## ") and line[3:].strip() in labels:
            current = line[3:].strip()
            found[current] = []
        elif line.strip() == "---":
            current = None
        elif current:
            found[current].append(line)
    return {k: "\n".join(v) for k, v in found.items()}


def page(lang, html_lang, title, body, page_key):
    tabs = "".join(
        f'<a class="{"on" if key == page_key else ""}" href="{key}.html">{NAV[lang][n]}</a>'
        for n, key in enumerate(PAGES)
    )
    langs = "".join(
        f'<a class="{"on" if code == lang else ""}" href="../{code}/{page_key}.html" hreflang="{hl}">{short}</a>'
        for code, _, hl, short in LANGS
    )
    return f"""<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header><nav class="tabs">{tabs}</nav><nav class="langs">{langs}</nav></header>
<article>
{body}
</article>
<footer>© 2026 Howausa</footer>
</div>
</body>
</html>
"""


def main():
    for key, filename in PAGES.items():
        parts = sections((SRC / filename).read_text(encoding="utf-8"))
        for code, label, hl, _ in LANGS:
            title, body = md_to_html(parts[label])
            out = ROOT / code / f"{key}.html"
            out.parent.mkdir(exist_ok=True)
            out.write_text(page(code, hl, title, body, key), encoding="utf-8")
            print("寫入", out.relative_to(ROOT))
    # 首頁：依瀏覽器語言跳到對應的隱私權政策
    links = "".join(f'<li><a href="{c}/privacy.html">{l}</a></li>' for c, l, _, _ in LANGS)
    (ROOT / "index.html").write_text(f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Howausa</title><style>{CSS}</style>
<script>
var l=(navigator.language||"en").toLowerCase(),d="en";
if(l.indexOf("ja")===0)d="ja";else if(/^zh-(hans|cn|sg)/.test(l))d="zh-Hans";else if(l.indexOf("zh")===0)d="zh-Hant";
location.replace(d+"/privacy.html");
</script></head>
<body><div class="wrap"><article><h1>Howausa</h1><ul>{links}</ul></article></div></body></html>
""", encoding="utf-8")
    print("寫入 index.html")


if __name__ == "__main__":
    main()
