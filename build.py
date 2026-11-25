"""產生棉棉兔記帳的網站：首頁、隱私權政策、使用條款，四種語言。

- 隱私權政策、使用條款：主程式儲存庫的 `上架準備/隱私權政策.md`、`上架準備/使用條款.md`，
  只取「## 繁體中文」「## 日本語」「## English」「## 简体中文」各段的內容。
- 首頁文字：這個儲存庫的 `landing.json`。
- 外觀照 `設計稿/產品介紹網站_2026-11-12/定案.md`：白天＝午後手帳、夜晚＝夜晚床邊窗，右上切換。

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
# Android 封閉測試（2026-11-15）：先加入 Google 群組 → 成為測試人員 → Play 下載
GROUP = "https://groups.google.com/g/howausa-testers"
PLAY_TEST = "https://play.google.com/apps/testing/com.yuzuki.howausa"
PLAY_STORE = "https://play.google.com/store/apps/details?id=com.yuzuki.howausa"

LANGS = [  # (資料夾, md 段落標題, html lang, 切換列顯示)
    ("zh-Hant", "繁體中文", "zh-Hant", "繁中"),
    ("ja", "日本語", "ja", "日本語"),
    ("en", "English", "en", "English"),
    ("zh-Hans", "简体中文", "zh-Hans", "简中"),
]
PAGES = {"privacy": "隱私權政策.md", "terms": "使用條款.md"}
TEXT = json.loads((ROOT / "landing.json").read_text(encoding="utf-8"))
# 各語言的頁尾社群連結（沒列的用脆）
SOCIAL = {"ja": ("X @yuzuki_studio", "https://x.com/yuzuki_studio")}
# 日文用 X 專用的 TestFlight 連結；也不放 Android 測試按鈕
TESTFLIGHT_BY_LANG = {"ja": "https://testflight.apple.com/join/gyKC5Jf5"}
NO_ANDROID_BUTTON = {"ja"}

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Huninn&family=LXGW+WenKai+TC:wght@400;700&display=swap">'

CSS = """
/* 版面照旅圖官網：窄單欄置中、頂上膠囊分頁、一段一張卡片。白天＝午後手帳、夜晚（html.dark）＝App 的夜晚配色（暖黑、琥珀、深咖啡毛玻璃；11-16 選 B 房間照片當背景） */
:root{
  --bg:#fcf4e6;--card:#fffaf1;--ink:#5a3826;--mute:#8f6f5c;--line:#5a3826;
  --honey:#f6dcab;--peach:#f5cdbf;--cta:#f0a08e;--cta-ink:#4a2a1c;--chip:#fbe7c6;--tag:#cfe3b8;--tag-ink:#3f5a2a;--link:#a2553a;
  --shadow:4px 4px 0 var(--line);--bw:2.5px;--r:22px;
  --hand:"LXGW WenKai TC","Huninn","PingFang TC","Hiragino Sans",serif;--ui:"Huninn","PingFang TC","PingFang SC","Hiragino Sans",system-ui,sans-serif;
  color-scheme:light;
}
html.dark{
  --bg:#0A0806;--card:rgba(24,19,15,.80);--ink:#FFF3E3;--mute:rgba(255,243,227,.62);--line:rgba(255,236,214,.13);
  --honey:rgba(255,194,122,.10);--peach:rgba(246,177,168,.08);--cta:#FFC27A;--cta-ink:#2B1A12;--chip:rgba(255,194,122,.14);--tag:rgba(175,221,191,.16);--tag-ink:#AFDDBF;--link:#FFC27A;
  --shadow:0 18px 40px -22px rgba(0,0,0,.9),0 0 0 1px rgba(255,236,214,.07) inset;--bw:1px;--r:24px;
  color-scheme:dark;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--ui);font-size:15px;line-height:1.7}
html.dark body{background:#0A0806}
img{max-width:100%}
[hidden]{display:none!important}
.deco{position:fixed;inset:0;pointer-events:none;z-index:0}
html:not(.dark) .deco{background:radial-gradient(260px 200px at 0 0,rgba(255,214,150,.55),transparent 70%),radial-gradient(240px 220px at 100% 100%,rgba(245,205,191,.6),transparent 70%)}
html.dark .deco::before{content:"";position:absolute;inset:-60px;background:url(../img/home/zh-Hant-room-night.jpg) center/cover;filter:blur(26px) brightness(.58) saturate(1.15)}
html.dark .deco::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,8,6,.15),rgba(10,8,6,.6))}
.wrap{position:relative;z-index:1;max-width:520px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:16px 40px;display:grid;gap:18px}
a{color:inherit}
h1,h2,h3{font-family:var(--hand);font-weight:700;margin:0;text-wrap:balance}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.card,.nav a,.btn,.theme,.lang select{transition:background-color .4s,border-color .4s,color .4s,box-shadow .4s}

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
html.dark .nav a.on{background:rgba(255,194,122,.22)}

/* 卡片 */
.card{background:var(--card);border:var(--bw) solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);padding:18px 16px 20px;position:relative;min-width:0}
html.dark .card{backdrop-filter:blur(14px)}
.card.honey{background-color:var(--honey)}
.card.peach{background-color:var(--peach)}
.card h2{font-size:21px;margin-bottom:6px}
.sub{color:var(--mute);font-size:13.5px;margin:0 0 14px}

/* 首頁：主圖是會動的房間；影片沒播時就是同一張圖，不留空洞 */
.hero{padding:0;overflow:hidden}
.hero .txt{padding:18px 18px 12px}
.hero h1{font-size:clamp(26px,7.6vw,34px);line-height:1.25}
.hero .txt p{margin:6px 0 0;font-size:15.5px;color:var(--mute)}
.hero .get{padding:14px 16px 16px}
.vid{position:relative;overflow:hidden;background:var(--chip)}
.vid img,.vid video{display:block;width:100%;height:auto;aspect-ratio:var(--ar)}
.vid img{object-fit:cover}
.vid video{position:absolute;inset:0;height:100%;object-fit:cover;opacity:0;transition:opacity .3s}
.vid video.on{opacity:1}
.hero .vid{border-block:var(--bw) solid var(--line)}
html.dark .d,html:not(.dark) .n{display:none!important}
.cta{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}
.cta.one{grid-template-columns:1fr}
.hero .cta{margin-top:0}
.btn{display:flex;align-items:center;justify-content:center;text-align:center;min-height:46px;padding:8px 12px;border-radius:999px;font:700 15px var(--hand);text-decoration:none;background:var(--cta);color:var(--cta-ink);border:var(--bw) solid var(--line);box-shadow:3px 3px 0 var(--line)}
.btn:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--line)}
.btn.off{background:transparent;color:var(--mute);box-shadow:none;cursor:default}
html.dark .btn{box-shadow:0 8px 22px -10px rgba(255,180,94,.75)}
html.dark .btn.off{box-shadow:none}
.note{font-size:12.5px;color:var(--mute);margin:12px 0 0}
.big h2{font-size:25px;line-height:1.35;margin-bottom:4px}
.big .lead,.pt p,.pic figcaption{text-wrap:pretty}
.big .lead{text-wrap:balance;margin:0 0 14px;font-size:14.5px;color:var(--mute)}
/* 圖框：上緣貼一截紙膠帶 */
.pic{position:relative;margin:0}
.pic>img,.pic>.vid,.draw{display:block;width:100%;height:auto;border-radius:16px;border:var(--bw) solid var(--line);overflow:hidden}
.pic.t::before{content:"";position:absolute;z-index:2;left:50%;top:-11px;width:92px;height:24px;margin-left:-46px;transform:rotate(-3deg);background:repeating-linear-gradient(90deg,rgba(244,205,120,.94) 0 8px,rgba(250,224,164,.94) 8px 16px);clip-path:polygon(0 0,100% 0,97% 25%,100% 50%,97% 75%,100% 100%,0 100%,3% 75%,0 50%,3% 25%)}
.pic.t.pink::before{background:repeating-linear-gradient(90deg,rgba(232,160,174,.92) 0 7px,rgba(242,190,200,.92) 7px 14px)}
.pic.t.green::before{background:repeating-linear-gradient(90deg,rgba(164,190,160,.94) 0 7px,rgba(196,214,190,.94) 7px 14px)}
.pic figcaption{margin:8px 2px 0;font-size:14px;line-height:1.6;color:var(--mute)}
.gap{display:grid;gap:24px;margin-top:20px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
/* 三點 */
.pt h3{font-size:19px;line-height:1.4}
.pt>p{margin:3px 0 18px;font-size:14.5px;color:var(--mute)}
.tip{margin:22px 0 0;font:400 15.5px/1.7 var(--hand)}
.tip span,.mark{background:linear-gradient(transparent 58%,rgba(244,205,120,.55) 58% 94%,transparent 94%)}
html.dark .tip span,html.dark .mark{background:linear-gradient(transparent 58%,rgba(255,194,122,.28) 58% 94%,transparent 94%)}
/* 網頁自己畫的小示意（沒有對應語言的截圖時用） */
.draw{position:relative;padding:20px 16px 26px;background:#efe6d6;color:#4a3a31;font:400 14px/1.5 var(--ui)}
html.dark .draw{background:#191410;color:#FFF3E3}
.sheet{background:#fbf7ef;border-radius:16px;padding:14px;box-shadow:0 6px 18px -10px rgba(90,56,38,.5)}
html.dark .sheet{background:#241c16;box-shadow:none;border:1px solid rgba(255,236,214,.1)}
.lab{position:absolute;right:14px;bottom:5px;font-size:11px;line-height:1.4;opacity:.62}
.noti{display:flex;gap:10px;align-items:center;background:#fffdf9;border-radius:14px;padding:10px 12px;box-shadow:0 6px 16px -10px rgba(90,56,38,.6)}
html.dark .noti{background:#2b221b;box-shadow:none}
.app{flex:none;width:34px;height:34px;border-radius:9px;display:grid;place-items:center;background:#c97378;color:#fff;font-size:11px;font-weight:700}
.app.b{background:#8f7d6b}.app.s{width:22px;height:22px;border-radius:6px;font-size:8px}
.noti b,.row b{display:block;font-size:14px}
.noti small,.row small{display:block;font-size:12.5px;opacity:.72}
.amt{font:700 34px/1.2 Georgia,"Times New Roman",serif;color:#c97378;margin:8px 0 6px}
html.dark .amt{color:#F6B1A8}
.kv{display:flex;justify-content:space-between;gap:10px;border-top:1px solid rgba(120,90,70,.18);padding:7px 0;font-size:13.5px}
html.dark .kv{border-color:rgba(255,236,214,.12)}
.kv span{opacity:.7}
.ok{margin-top:10px;background:#c97378;color:#fff;border-radius:999px;text-align:center;padding:9px;font-weight:700}
html.dark .ok{background:#FFC27A;color:#2B1A12}
.row{display:flex;gap:10px;align-items:center}
.row>div{flex:1;min-width:0}
.row em{font:700 16px Georgia,serif;font-style:normal;color:#c97378}
html.dark .row em{color:#F6B1A8}
.row img{width:44px;height:44px;flex:none;border-radius:50%;background:#f0cdbb;object-fit:contain;padding:2px}
html.dark .row img{background:#6b5040}
.sheet .row+.row{border-top:1px dashed rgba(120,90,70,.3);margin-top:10px;padding-top:10px}
html.dark .sheet .row+.row{border-color:rgba(255,236,214,.18)}
.pill{flex:none;border:1.5px solid #c97378;color:#c97378;border-radius:999px;padding:2px 14px;font-weight:700;font-size:13.5px}
html.dark .pill{border-color:#FFC27A;color:#FFC27A}
.hid{background:#a893c0;color:#fff;border-radius:6px;padding:1px 8px;font-size:13px;white-space:nowrap}
.sent{margin:10px 0 0;font-size:13px;opacity:.75}
.flow{display:grid;gap:12px}
.flow>:nth-child(2){animation:flow2 8s infinite}.flow>:nth-child(3){animation:flow3 8s infinite}
@keyframes flow2{0%,10%{opacity:0;transform:translateY(8px)}18%,92%{opacity:1;transform:none}98%,100%{opacity:0}}
@keyframes flow3{0%,44%{opacity:0;transform:translateY(8px)}52%,92%{opacity:1;transform:none}98%,100%{opacity:0}}
:lang(ja) h1,:lang(ja) h2,:lang(ja) .txt p,:lang(ja) .lead,:lang(ja) figcaption{word-break:auto-phrase;line-break:strict}
.bye{text-align:center}
.bye p{font:700 18px/1.75 var(--hand);margin:0;text-wrap:balance}
.bye span{display:inline-block;white-space:pre-wrap}

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
/* Android 測試步驟 */
.steps{list-style:none;margin:0;padding:0;display:grid;gap:16px}
.step{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:start}
.num{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:var(--card);border:var(--bw) solid var(--line);font:700 16px var(--hand)}
.step h3{font-size:16.5px;line-height:1.4}
.step p{margin:2px 0 10px;font-size:13.5px;color:var(--mute)}
.step .btn{display:inline-flex;min-height:42px;padding:6px 20px;font-size:14.5px}
.step .wait{display:flex;gap:6px;align-items:flex-start;margin:-4px 0 12px;font-size:12.5px;line-height:1.6;color:var(--mute)}
.wait svg{flex:none;width:13px;height:13px;margin-top:4px}
.guide{margin-top:10px}.guide summary{cursor:pointer;width:max-content;font-size:13.5px;color:var(--mute);text-decoration:underline;text-underline-offset:3px}
.guide .pics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}
.guide img{width:100%;height:auto;border-radius:12px;border:var(--bw) solid var(--line)}
.tips{margin:0;padding-left:1.2em;display:grid;gap:6px;font-size:13.5px}
@media (max-width:380px){.cta{grid-template-columns:1fr}.brand b{font-size:17px}.theme span{display:none}.theme{padding:0 9px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

# 影片：看得到才載、看不到就停；省流量、2G、減少動態時只留圖片；切換日夜時換另一支
VIDEO_JS = """
<script>(function(){
var c=navigator.connection||{},rm=matchMedia('(prefers-reduced-motion: reduce)');
function quiet(){return rm.matches||c.saveData||/2g/.test(c.effectiveType||'')}
var R=document.documentElement,vs=[].slice.call(document.querySelectorAll('.vid video'));
function src(v){return R.classList.contains('dark')?v.dataset.night:v.dataset.day}
function sync(v){
  if(!v.seen||quiet()){v.pause();if(quiet())v.classList.remove('on');return}
  var s=src(v);if(v.getAttribute('src')!==s){v.classList.remove('on');v.setAttribute('src',s)}
  var p=v.play();if(p&&p.catch)p.catch(function(){v.classList.remove('on')});
}
vs.forEach(function(v){v.muted=true;v.addEventListener('playing',function(){v.classList.add('on')});v.addEventListener('error',function(){v.classList.remove('on')})});
function start(){
  if(!('IntersectionObserver' in window)){vs.forEach(function(v){v.seen=true;sync(v)});return}
  var io=new IntersectionObserver(function(es){es.forEach(function(x){x.target.seen=x.isIntersecting;sync(x.target)})},{rootMargin:'120px 0px',threshold:.05});
  vs.forEach(function(v){io.observe(v)});
}
if(document.readyState==='complete')start();else addEventListener('load',start);
new MutationObserver(function(){vs.forEach(sync)}).observe(R,{attributes:true,attributeFilter:['class']});
rm.addEventListener&&rm.addEventListener('change',function(){vs.forEach(sync)});
})()</script>"""

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
    social_label, social_url = SOCIAL.get(lang, (f'{T["threads"]} @yuzuki.tw', THREADS))
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
<meta property="og:image" content="{SITE}/img/home/{lang}-room-day.jpg">
<meta property="og:url" content="{SITE}/{lang}/{file}">
<meta name="theme-color" content="#fcf4e6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0A0806" media="(prefers-color-scheme: dark)">
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
<nav><a href="privacy.html">{html.escape(T["nav"][1])}</a><a href="terms.html">{html.escape(T["nav"][2])}</a><a href="{social_url}" target="_blank" rel="noopener">{html.escape(social_label)}</a></nav>
<div>{html.escape(T["studio"])} · © 2026</div>
</footer>
</div>
{TAIL}
</body>
</html>
"""


def IOS_LINK(lang):
    return TESTFLIGHT_BY_LANG.get(lang, TESTFLIGHT)


def picture(name, alt, ar=None, eager=False, cls=""):
    """img/home/ 的圖；給 ar 時固定比例，避免載入時跳動。"""
    size = f' width="{ar[0]}" height="{ar[1]}"' if ar else ""
    load = "" if eager else ' loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="../img/home/{name}.jpg" alt="{html.escape(alt)}"{size}{load}>'


def video(day, night, alt, w, h):
    """會動的圖：平常就是一張圖，能播時才把影片疊上去（不擋首頁、省流量或減少動態時不載影片）。"""
    if night:
        imgs = picture(day, alt, (w, h), cls="d") + picture(night, alt, (w, h), cls="n")
    else:
        imgs = picture(day, alt, (w, h))
    return (f'<div class="vid" style="--ar:{w}/{h}">{imgs}<video muted loop playsinline preload="none" tabindex="-1" aria-hidden="true" '
            f'data-day="../img/home/{day}.mp4" data-night="../img/home/{night or day}.mp4"></video></div>')


def auto_block(lang, A) -> str:
    """自動記帳：繁中用影片、真畫面與宣傳圖，其他語言用網頁畫的小示意。"""
    e = html.escape
    D = A.get("demo")
    lab = f'<span class="lab">{e(TEXT[lang]["home"]["demoLabel"])}</span>'
    if D:
        kv = "".join(f'<div class="kv"><span>{e(a)}</span>{e(b)}</div>' for a, b in D["fields"])
        top = (f'<figure class="pic t"><div class="draw"><div class="flow"><div class="noti"><span class="app">{e(D["bankTag"])}</span><div><b>{e(D["bank"])}</b><small>{e(D["alert"])}</small></div></div>'
               f'<div class="sheet"><b>{e(D["shop"])}</b><div class="amt">{e(D["amount"])}</div>{kv}<div class="ok">✓ {e(D["save"])}</div></div>'
               f'<div class="sheet"><div class="row"><div><b>{e(D["cat"])}</b><small>{e(D["shop"])}</small></div><em>{e(D["minus"])}</em></div></div></div>{lab}</div></figure>')
        merge = (f'<div class="draw"><div class="sheet"><div class="row"><span class="app b s">{e(D["bankTag"])}</span><div><b>{e(D["bank"])}</b><small>{e(D["alert"])}</small></div></div>'
                 f'<div class="row"><span class="app s">Pay</span><div><b>{e(D["wallet"])}</b><small>{e(D["shop"])}</small></div><span class="pill">{e(D["split"])}</span></div><div class="amt">{e(D["amount"])}</div></div>{lab}</div>')
        mask = (f'<div class="draw"><div class="sheet">{D["masked"]}<p class="sent">{e(D["sent"])}</p></div>{lab}</div>')
    else:
        top = f'<figure class="pic">{video("auto", None, A["alt"], 720, 900)}</figure>'
        merge = picture(f"{lang}-merge-day", A["points"][0][0], (900, 716), cls="d") + picture(f"{lang}-merge-night", A["points"][0][0], (900, 716), cls="n")
        mask = picture("promo5", A["points"][2][0], (720, 491))
    shows = [merge, video(f"{lang}-swipe", None, A["points"][1][0], 720, 400), mask]
    pts = "".join(
        f'<div class="pt"><h3>{e(t)}</h3><p>{e(d)}</p><figure class="pic">{show}</figure></div>'
        for (t, d), show in zip(A["points"], shows)
    )
    return (f'<section class="card big" id="auto"><h2>{e(A["h"])}</h2><p class="lead">{e(A["p"])}</p>{top}'
            f'<div class="gap">{pts}</div><p class="tip"><span>{e(A["tip"])}</span></p></section>')


def landing(lang) -> str:
    T = TEXT[lang]
    H = T["home"]
    e = html.escape
    androidbtn = "" if lang in NO_ANDROID_BUTTON else f'<a class="btn" href="android.html">{e(T["ctaAndroid"])}</a>'
    cta = f'<div class="cta{"" if androidbtn else " one"}"><a class="btn" href="{IOS_LINK(lang)}" target="_blank" rel="noopener">{e(T["ctaTest"])}</a>{androidbtn}</div>'
    parts = [f"""<section class="card hero"><div class="txt"><h1>{e(H["h1"])}</h1><p>{e(H["p"])}</p></div>
{video(f"{lang}-day", f"{lang}-night", T["heroAlt"], 720, 561)}
<div class="get">{cta}</div></section>"""]
    if "auto" in H:
        parts.append(auto_block(lang, H["auto"]))
    R = H["room"]
    parts.append(f'<section class="card big honey" id="room"><h2>{e(R["h"])}</h2><p class="lead">{e(R["p"])}</p><div class="gap">'
                 f'<figure class="pic t">{picture(f"{lang}-room-day", T["day"], (900, 534))}</figure>'
                 f'<figure class="pic t pink">{picture(f"{lang}-room-night", T["night"], (900, 534))}</figure></div></section>')
    D = H["detail"]
    figs = "".join(
        f'<figure class="pic">{picture(f"{lang}-{n}", cap, size)}<figcaption>{e(cap)}</figcaption></figure>'
        for (n, size), cap in zip([("tape", (900, 537)), ("paper", (900, 481)), ("tag", (900, 496))], D["caps"])
    )
    parts.append(f'<section class="card big" id="detail"><h2>{e(D["h"])}</h2><div class="gap">{figs}</div></section>')
    if "couple" in H:
        C = H["couple"]
        rows = "".join(f'<div class="row"><img src="../img/home/av-{av}.png" alt="{e(who)}" loading="lazy" width="44" height="44"><div><b>{e(t)}</b><small>{e(who)}</small></div><em>{e(m)}</em></div>' for av, t, who, m in C["rows"])
        parts.append(f'<section class="card big peach" id="couple"><h2>{e(C["h"])}</h2><p class="lead">{e(C["p"])}</p><figure class="pic t pink"><div class="draw"><div class="sheet"><p style="margin:0 0 10px;font:700 17px var(--hand)"><span class="mark">{e(C["book"])}</span></p>{rows}</div><span class="lab">{e(H["demoLabel"])}</span></div></figure></section>')
    if "budget" in H:
        B = H["budget"]
        parts.append(f'<section class="card big" id="budget"><h2>{e(B["h"])}</h2><p class="lead">{e(B["p"])}</p><figure class="pic">'
                     f'{picture(f"{lang}-bud-day", B["h"], (900, 724), cls="d")}{picture(f"{lang}-bud-night", B["h"], (900, 724), cls="n")}</figure></section>')
    parts.append(f'<section class="card bye"><p>{"".join(f"<span>{e(x)}</span>" for x in H["bye"])}</p>{cta}</section>')
    return "\n".join(parts) + VIDEO_JS


def android(lang) -> str:
    A = TEXT[lang]["android"]
    e = html.escape
    links = [GROUP, PLAY_TEST, PLAY_STORE]
    # 第 4 欄（選填）：要等 Google 處理的步驟，說明下面加一行淡色小字「等 5～15 分鐘」（11-16 選 B）（使用者 2026-11-16）
    clock = ('<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.6"/>'
             '<path d="M8 4.6V8l2.3 1.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>')
    wait = lambda st: f'<p class="wait">{clock}<span>{e(st[3])}</span></p>' if len(st) > 3 else ""
    # 第 1、2 步按鈕下方「看教學」，點開才顯示標註好的截圖（個資已換成兔子）（使用者 2026-11-16）
    # 教學截圖是中文畫面，日文、英文頁不放
    pics = {} if lang in ("ja", "en") else {0: ["guide-1a", "guide-1b"], 1: ["guide-2"]}
    guide = lambda i, t: (f'<details class="guide"><summary>{e(A["guide"])}</summary><div class="pics">'
                          + "".join(f'<img src="../img/{n}.jpg" alt="{e(t)}" loading="lazy" width="600" height="1304">' for n in pics[i])
                          + '</div></details>') if i in pics else ""
    steps = "".join(
        f'<li class="step"><span class="num" aria-hidden="true">{i + 1}</span><div><h3>{e(t)}</h3><p>{e(p)}</p>{wait(st)}'
        f'<a class="btn" href="{url}" target="_blank" rel="noopener">{e(st[2])}</a>{guide(i, t)}</div></li>'
        for i, (st, url) in enumerate(zip(A["steps"], links))
        for t, p in [st[:2]]
    )
    tips = "".join(f"<li>{e(t)}</li>" for t in A["tips"])
    # 從脆／IG／LINE 等 App 內建瀏覽器打開時（沒登入 Google，進不了群組）：最上面提示改用 Chrome 打開
    chrome = f"intent://serenityouo.github.io/howausa-site/{lang}/android.html#Intent;scheme=https;package=com.android.chrome;end"
    inapp = (f'<section class="card peach" id="inapp" hidden><h2>{e(A["inappTitle"])}</h2><p class="sub">{e(A["inappBody"])}</p>'
             f'<a class="btn" href="{chrome}">{e(A["inappBtn"])}</a><p class="note">{e(A["inappHint"])}</p></section>'
             '<script>(function(){var u=navigator.userAgent||"";if(/Android/i.test(u)&&/Barcelona|Instagram|FBAN|FBAV|FB_IAB|Line\\/|; wv\\)/i.test(u)){document.getElementById("inapp").hidden=false}})()</script>')
    # Android 上第 3 步改開完整的 Play 商店 App（market://）；網頁連結會跳出常常空白的 Play 小視窗
    market = ('<script>(function(){if(/Android/i.test(navigator.userAgent||"")){var a=document.querySelector(".steps li:last-child a");'
              'if(a){a.href="market://details?id=com.yuzuki.howausa";a.removeAttribute("target")}}})()</script>')
    return inapp + f"""<section class="card honey"><h2>{e(A["h"])}</h2><p class="sub">{e(A["sub"])}</p><ol class="steps">{steps}</ol></section>
<section class="card"><h2>{e(A["tipsTitle"])}</h2><ul class="tips">{tips}</ul></section>{market}"""


def main():
    for code, label, hl, _ in LANGS:
        T = TEXT[code]
        out = ROOT / code / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(shell(code, hl, "index", T["title"], T["description"], landing(code)), encoding="utf-8")
        print("寫入", out.relative_to(ROOT))
    for code, label, hl, _ in LANGS:
        A = TEXT[code]["android"]
        out = ROOT / code / "android.html"
        out.write_text(shell(code, hl, "android", A["title"], A["desc"], android(code)), encoding="utf-8")
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
