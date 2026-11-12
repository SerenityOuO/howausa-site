"""產生棉棉兔記帳的網站：首頁、隱私權政策、使用條款，四種語言。

- 隱私權政策、使用條款：主程式儲存庫的 `上架準備/隱私權政策.md`、`上架準備/使用條款.md`，
  只取「## 繁體中文」「## 日本語」「## English」「## 简体中文」各段的內容。
- 首頁文字：這個儲存庫的 `landing.json`。
- 外觀照 `設計稿/產品介紹網站_2026-11-12/定案.md`：白天＝午後手帳、夜晚＝雨夜床邊窗，右上切換。

用法：python3 build.py [主程式儲存庫路徑]（預設 ~/Projects/Money_Manager）
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Projects/Money_Manager")
SRC = APP / "上架準備"
SITE = "https://serenityouo.github.io/howausa-site"
TESTFLIGHT = "https://testflight.apple.com/join/cSRpbd5j"
THREADS = "https://www.threads.com/@yuzuki.tw"

LANGS = [  # (資料夾, md 段落標題, html lang, 切換列顯示)
    ("zh-Hant", "繁體中文", "zh-Hant", "繁中"),
    ("ja", "日本語", "ja", "日本語"),
    ("en", "English", "en", "English"),
    ("zh-Hans", "简体中文", "zh-Hans", "简中"),
]
PAGES = {"privacy": "隱私權政策.md", "terms": "使用條款.md"}
TEXT = json.loads((ROOT / "landing.json").read_text(encoding="utf-8"))
SHOTS = ["s01", "s06", "s08", "s09", "s04", "s03", "s05"]
ICONS = ["pen", "home", "ring", "stamp", "two", "widget", "plane", "cal"]

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Huninn&family=LXGW+WenKai+TC:wght@400;700&display=swap">'

CSS = """
/* 版面照旅圖官網：窄單欄置中、頂上膠囊分頁、一段一張卡片。白天＝午後手帳、夜晚（html.dark）＝雨夜床邊窗 */
:root{
  --bg:#fcf4e6;--card:#fffaf1;--ink:#5a3826;--mute:#8f6f5c;--line:#5a3826;
  --honey:#f6dcab;--peach:#f5cdbf;--cta:#f0a08e;--cta-ink:#4a2a1c;--chip:#fbe7c6;--tag:#cfe3b8;--tag-ink:#3f5a2a;--link:#a2553a;
  --shadow:4px 4px 0 var(--line);--bw:2.5px;--r:22px;
  --hand:"LXGW WenKai TC","Huninn","PingFang TC","Hiragino Sans",serif;--ui:"Huninn","PingFang TC","PingFang SC","Hiragino Sans",system-ui,sans-serif;
  color-scheme:light;
}
html.dark{
  --bg:#1b1e3b;--card:rgba(52,58,112,.72);--ink:#fff1dc;--mute:#c7bfd6;--line:rgba(243,234,240,.28);
  --honey:rgba(255,178,106,.16);--peach:rgba(233,166,92,.10);--cta:#ffb26a;--cta-ink:#2a1d18;--chip:rgba(255,178,106,.18);--tag:rgba(255,178,106,.25);--tag-ink:#ffd9ad;--link:#ffc98f;
  --shadow:0 18px 40px -22px rgba(0,0,0,.8),0 0 0 1px rgba(243,234,240,.08) inset;--bw:1px;--r:24px;
  color-scheme:dark;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--ui);font-size:15px;line-height:1.7}
html.dark body{background:linear-gradient(180deg,#2b3060,#1b1e3b 40%) fixed,#1b1e3b}
img{max-width:100%}
[hidden]{display:none!important}
.deco{position:fixed;inset:0;pointer-events:none;z-index:0}
html:not(.dark) .deco{background:radial-gradient(260px 200px at 0 0,rgba(255,214,150,.55),transparent 70%),radial-gradient(240px 220px at 100% 100%,rgba(245,205,191,.6),transparent 70%)}
html.dark .deco{background:repeating-linear-gradient(105deg,transparent 0 22px,rgba(220,225,255,.05) 22px 23px),radial-gradient(320px 260px at 92% 6%,rgba(255,178,106,.22),transparent 70%)}
.wrap{position:relative;z-index:1;max-width:520px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:16px 40px;display:grid;gap:18px}
a{color:inherit}
h1,h2,h3{font-family:var(--hand);font-weight:700;margin:0;text-wrap:balance}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.card,.feat,.nav a,.btn,.trust div,.ic,.theme,.lang select{transition:background-color .4s,border-color .4s,color .4s,box-shadow .4s}

/* 頁首 */
.top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.brand{display:flex;align-items:center;gap:10px;min-width:0;text-decoration:none}
.brand img{flex:none;width:40px;height:40px;border-radius:50%;object-fit:cover;border:var(--bw) solid var(--line)}
.brand b{font:700 19px var(--hand);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tools{display:flex;gap:8px;flex:none}
.theme,.lang select{display:inline-flex;align-items:center;gap:6px;height:36px;font:600 14px var(--ui);color:var(--ink);background:var(--card);border:var(--bw) solid var(--line);border-radius:999px;box-shadow:2px 2px 0 var(--line);cursor:pointer}
.theme{padding:0 13px 0 10px}
.theme:active{transform:translate(1px,1px)}
.theme svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round}
.theme .moon{display:none}
html.dark .theme .sun{display:none}html.dark .theme .moon{display:block}
.lang{position:relative;display:flex}
.lang select{appearance:none;-webkit-appearance:none;padding:0 28px 0 12px}
.lang::after{content:"";position:absolute;right:12px;top:50%;width:6px;height:6px;margin-top:-5px;border-right:1.8px solid var(--ink);border-bottom:1.8px solid var(--ink);transform:rotate(45deg);pointer-events:none}
html.dark .theme,html.dark .lang select{box-shadow:none;backdrop-filter:blur(8px)}
.theme:focus-visible,.lang select:focus-visible,.btn:focus-visible,.nav a:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
.nav{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding:2px 2px 6px;margin-inline:-2px}
.nav a{flex:none;text-decoration:none;font-size:14px;padding:7px 14px;border-radius:999px;background:var(--card);border:var(--bw) solid var(--line);box-shadow:2px 2px 0 var(--line)}
.nav a.on{background:var(--honey)}
html.dark .nav a{box-shadow:none;backdrop-filter:blur(8px)}
html.dark .nav a.on{background:rgba(255,178,106,.28)}

/* 卡片 */
.card{background:var(--card);border:var(--bw) solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);padding:18px 16px 20px;position:relative;min-width:0}
html.dark .card{backdrop-filter:blur(14px)}
.card.honey{background-color:var(--honey)}
.card.peach{background-color:var(--peach)}
.card h2{font-size:21px;margin-bottom:6px}
.sub{color:var(--mute);font-size:13.5px;margin:0 0 14px}

/* 大圖 */
.hero{padding:0;overflow:hidden}
.hero .pic{position:relative;aspect-ratio:1092/510;max-width:100%;background:linear-gradient(180deg,rgba(60,30,14,.5),rgba(60,30,14,0) 64%),url(../img/day.jpg) center/cover no-repeat}
.hero .pic::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(12,14,40,.45),rgba(12,14,40,0) 64%),url(../img/night.jpg) center/cover;opacity:0;transition:opacity .6s ease}
html.dark .hero .pic::before{opacity:1}
.hero .txt{position:absolute;z-index:1;left:16px;top:14px;right:16px;color:#fff8ec;text-shadow:0 1px 10px rgba(60,30,15,.5)}
.hero h1{font-size:clamp(24px,7vw,30px);line-height:1.2}
.hero p{margin:4px 0 0;font-size:14px;max-width:24em}

/* 功能格 */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.feat{display:flex;gap:10px;align-items:flex-start;padding:11px 12px;border-radius:14px;background:var(--card);border:var(--bw) solid var(--line);box-shadow:2px 2px 0 var(--line);min-width:0}
html.dark .feat{background:rgba(255,255,255,.05);box-shadow:none}
.ic{flex:none;width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:var(--chip);border:var(--bw) solid var(--line)}
.ic svg{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.feat h3{font-size:15.5px;line-height:1.35}
.feat p{margin:2px 0 0;font-size:12.5px;color:var(--mute);line-height:1.55}
.cta{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
.btn{display:flex;align-items:center;justify-content:center;text-align:center;min-height:46px;padding:8px 12px;border-radius:999px;font:700 15px var(--hand);text-decoration:none;background:var(--cta);color:var(--cta-ink);border:var(--bw) solid var(--line);box-shadow:3px 3px 0 var(--line)}
.btn:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--line)}
.btn.off{background:transparent;color:var(--mute);box-shadow:none;cursor:default}
html.dark .btn{box-shadow:0 8px 20px -10px rgba(255,178,106,.8)}
html.dark .btn.off{box-shadow:none}
.note{font-size:12.5px;color:var(--mute);margin:12px 0 0}

/* 看畫面 */
.strip{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 4px 10px;margin-inline:-4px;scrollbar-width:thin}
.shot{flex:none;width:46%;max-width:200px;scroll-snap-align:start;margin:0}
.shot img{display:block;width:100%;height:auto;aspect-ratio:600/1305;object-fit:cover;border-radius:14px;border:var(--bw) solid var(--line)}
.shot figcaption{font-size:12.5px;color:var(--mute);text-align:center;margin-top:6px}

/* 隱私四格 */
.trust{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.trust div{background:var(--card);border:var(--bw) solid var(--line);border-radius:14px;padding:10px 12px;font-size:13px}
html.dark .trust div{background:rgba(255,255,255,.05)}
.trust b{display:block;font:700 15px var(--hand)}

/* 條款、隱私權政策 */
.doc article{max-width:62ch}
.doc h1{font-size:24px;line-height:1.35;margin-bottom:4px}
.doc h2{font-size:18px;margin:24px 0 6px}
.doc p,.doc li{font-size:14.5px}
.doc p{margin:0 0 10px}
.doc ul{margin:0 0 10px;padding-left:1.2em;display:grid;gap:4px}
.doc .date{color:var(--mute);font-size:13px}
.doc a{color:var(--link);word-break:break-word;text-underline-offset:3px}
.table{overflow-x:auto;margin:0 0 12px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:8px 6px}
th{color:var(--mute);font-weight:600;white-space:nowrap}
td:first-child{white-space:nowrap;font-weight:600}

footer{text-align:center;font-size:12.5px;color:var(--mute);display:grid;gap:6px}
footer nav{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 14px}
footer a{text-underline-offset:3px}
@media (max-width:380px){.grid{grid-template-columns:1fr}.cta{grid-template-columns:1fr}.brand b{font-size:17px}.theme span{display:none}.theme{padding:0 9px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

SVG = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-pen" viewBox="0 0 24 24"><path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 6l3 3"/></symbol>
<symbol id="i-home" viewBox="0 0 24 24"><path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-5h4v5"/></symbol>
<symbol id="i-ring" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 8 8"/><path d="M12 9v3l2 2"/></symbol>
<symbol id="i-stamp" viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="10" r="1.8"/><circle cx="15" cy="10" r="1.8"/><circle cx="9" cy="15" r="1.8"/><path d="M14 15h2"/></symbol>
<symbol id="i-two" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><circle cx="16.5" cy="9" r="2.5"/><path d="M3.5 19c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><path d="M15 14.2c2.6-.4 4.8 1.2 5.5 4.3"/></symbol>
<symbol id="i-widget" viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="16" height="7" rx="2"/></symbol>
<symbol id="i-plane" viewBox="0 0 24 24"><path d="M3 13l18-7-5 14-4-5-5 2z"/><path d="M12 15l9-9"/></symbol>
<symbol id="i-cal" viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/><path d="M9 14l2 2 4-4"/></symbol>
</svg>"""

# 先決定白天／夜晚，避免閃一下：記住的選擇 > 手機深淺色
EARLY = """<script>(function(){var t=null;try{t=localStorage.getItem('mm-theme')}catch(e){}if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';if(t==='dark')document.documentElement.classList.add('dark')})()</script>"""

TAIL = """<script>
var root=document.documentElement,mq=matchMedia('(prefers-color-scheme: dark)'),tb=document.getElementById('theme-toggle'),saved=null;
try{saved=localStorage.getItem('mm-theme')}catch(e){}
function eff(){return saved||(mq.matches?'dark':'light')}
function apply(){var d=eff()==='dark';root.classList.toggle('dark',d);tb.querySelector('span').textContent=d?tb.dataset.night:tb.dataset.day;tb.setAttribute('aria-label',d?tb.dataset.toDay:tb.dataset.toNight)}
tb.onclick=function(){saved=eff()==='dark'?'light':'dark';try{localStorage.setItem('mm-theme',saved)}catch(e){}apply()};
mq.addEventListener&&mq.addEventListener('change',apply);apply();
document.getElementById('lang-select').onchange=function(e){var v=e.target.value;try{localStorage.setItem('mm-lang',v)}catch(x){}location.href='../'+v+'/'+e.target.dataset.page};
</script>"""


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


def shell(lang, html_lang, page_key, title, desc, body):
    T = TEXT[lang]
    file = "index.html" if page_key == "index" else f"{page_key}.html"
    tabs = "".join(
        f'<a class="{"on" if key == page_key else ""}" href="{"index" if key == "index" else key}.html"{" aria-current=\"page\"" if key == page_key else ""}>{html.escape(T["nav"][n])}</a>'
        for n, key in enumerate(["index", "privacy", "terms"])
    )
    opts = "".join(
        f'<option value="{code}"{" selected" if code == lang else ""}>{short}</option>' for code, _, _, short in LANGS
    )
    alts = "".join(
        f'<link rel="alternate" hreflang="{hl}" href="{SITE}/{code}/{file}">' for code, _, hl, _ in LANGS
    )
    brand = T["name"].split(":")[0]
    return f"""<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE}/img/day.jpg">
<meta property="og:url" content="{SITE}/{lang}/{file}">
<meta name="theme-color" content="#fcf4e6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1b1e3b" media="(prefers-color-scheme: dark)">
<link rel="icon" href="../img/avatar.png">
<link rel="apple-touch-icon" href="../img/avatar.png">
{alts}
{FONTS}
<style>{CSS}</style>
{EARLY}
</head>
<body>
<div class="deco"></div>
<div class="wrap">
<header class="top">
<a class="brand" href="index.html"><img src="../img/avatar.png" alt=""><b>{html.escape(brand)}</b></a>
<div class="tools">
<label class="lang"><span class="sr">{html.escape(T["langLabel"])}</span><select id="lang-select" data-page="{file}">{opts}</select></label>
<button type="button" class="theme" id="theme-toggle" data-day="{html.escape(T["day"])}" data-night="{html.escape(T["night"])}" data-to-day="{html.escape(T["toDay"])}" data-to-night="{html.escape(T["toNight"])}" aria-label="{html.escape(T["toNight"])}"><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M19 14.5A7.5 7.5 0 0 1 9.5 5a7.5 7.5 0 1 0 9.5 9.5z"/></svg><span>{html.escape(T["day"])}</span></button>
</div>
</header>
<nav class="nav">{tabs}</nav>
{body}
<footer>
<nav><a href="privacy.html">{html.escape(T["nav"][1])}</a><a href="terms.html">{html.escape(T["nav"][2])}</a><a href="{THREADS}" target="_blank" rel="noopener">{html.escape(T["threads"])} @yuzuki.tw</a></nav>
<div>{html.escape(T["studio"])} · © 2026</div>
</footer>
</div>
{TAIL}
</body>
</html>
"""


def landing(lang) -> str:
    T = TEXT[lang]
    e = html.escape
    feats = "".join(
        f'<div class="feat"><span class="ic"><svg aria-hidden="true"><use href="#i-{icon}"/></svg></span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>'
        for icon, (t, d) in zip(ICONS, T["feats"])
    )
    shots = "".join(
        f'<figure class="shot"><img src="../img/{name}.jpg" alt="{e(cap)}"{"" if i == 0 else " loading=\"lazy\""} width="600" height="1305"><figcaption>{e(cap)}</figcaption></figure>'
        for i, (name, cap) in enumerate(zip(SHOTS, T["shots"]))
    )
    trust = "".join(f"<div><b>{e(t)}</b>{e(d)}</div>" for t, d in T["trust"])
    return f"""{SVG}
<section class="card hero"><div class="pic" role="img" aria-label="{e(T["heroAlt"])}"><div class="txt"><h1>{e(T["name"])}</h1><p>{e(T["tagline"])}</p></div></div></section>
<section class="card"><h2>{e(T["featTitle"])}</h2><div class="grid">{feats}</div>
<div class="cta"><a class="btn" href="{TESTFLIGHT}" target="_blank" rel="noopener">{e(T["ctaTest"])}</a><span class="btn off">{e(T["ctaStore"])}</span></div>
<p class="note">{e(T["note"])}</p></section>
<section class="card" id="shots"><h2>{e(T["shotsTitle"])}</h2><p class="sub">{e(T["shotsSub"])}</p><div class="strip">{shots}</div></section>
<section class="card peach"><h2>{e(T["trustTitle"])}</h2><div class="trust">{trust}</div></section>"""


def main():
    for code, label, hl, _ in LANGS:
        T = TEXT[code]
        out = ROOT / code / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(shell(code, hl, "index", T["title"], T["description"], landing(code)), encoding="utf-8")
        print("寫入", out.relative_to(ROOT))
    for key, filename in PAGES.items():
        parts = sections((SRC / filename).read_text(encoding="utf-8"))
        for code, label, hl, _ in LANGS:
            title, body = md_to_html(parts[label])
            out = ROOT / code / f"{key}.html"
            doc = f'<section class="card doc"><article>\n{body}\n</article></section>'
            out.write_text(shell(code, hl, key, title, TEXT[code]["description"], doc), encoding="utf-8")
            print("寫入", out.relative_to(ROOT))
    # 網站根目錄：記住的語言 > 瀏覽器語言，跳到那個語言的首頁
    links = "".join(f'<li><a href="{c}/">{TEXT[c]["name"]}</a></li>' for c, _, _, _ in LANGS)
    (ROOT / "index.html").write_text(f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Howausa</title>
<script>
var d=null;try{{d=localStorage.getItem('mm-lang')}}catch(e){{}}
if(!/^(zh-Hant|zh-Hans|ja|en)$/.test(d||'')){{var l=(navigator.language||'en').toLowerCase();d='en';
if(l.indexOf('ja')===0)d='ja';else if(/^zh-(hans|cn|sg)/.test(l))d='zh-Hans';else if(l.indexOf('zh')===0)d='zh-Hant';}}
location.replace(d+'/'+location.hash);
</script></head>
<body style="font-family:system-ui;background:#fcf4e6;color:#5a3826"><ul>{links}</ul></body></html>
""", encoding="utf-8")
    print("寫入 index.html")


if __name__ == "__main__":
    main()
