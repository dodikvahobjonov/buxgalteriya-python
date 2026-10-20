# -*- coding: utf-8 -*-
# ============================================================
#  🏫 MAKTAB BUXGALTERIYA — Premium Navy admin panel
# ============================================================
import hashlib
import hmac
import html
import io
import json
import math
import re
import secrets
import time
from datetime import date, datetime

import pandas as pd
import requests
import streamlit as st

# ------------------------------------------------------------
# SOZLAMALAR
# ------------------------------------------------------------
def _secret(kalit, standart=""):
    try:
        return st.secrets.get(kalit, standart)
    except Exception:
        return standart


DB_URL = str(_secret("DB_URL", "https://maktab-buxgalteriya-default-rtdb.firebaseio.com")).rstrip("/")
DB_AUTH = str(_secret("DB_AUTH", ""))

OYLAR = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
         "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
HOLATLAR = {"st-paid": "TO'LANDI", "st-partial": "QISMAN", "st-debt": "QARZ"}
STANDART = {
    "user": "admin", "pass": "123", "user2": "", "pass2": "", "role2": "view",
    "orgName": "Maktab", "phone": "", "tgToken": "", "chatId": "",
    "defaultPrice": 0, "monthlyPlan": 0
}
MIN_PAROL = 6

st.set_page_config(page_title="Maktab Buxgalteriya", page_icon="🏫", layout="wide")

try:
    _v = tuple(int(x) for x in re.findall(r"\d+", st.__version__)[:2])
except Exception:
    _v = (1, 0)
KENG = {"width": "stretch"} if _v >= (1, 50) else {"use_container_width": True}

# ------------------------------------------------------------
# DIZAYN (CSS) — Premium Navy
# ------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp { background:#F4F6FA; font-family:'Plus Jakarta Sans',sans-serif; color:#0F172A; }

    /* ============ SIDEBAR — to'q ko'k navy ============ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#0B1220 0%,#111A30 100%);
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] * { color:#94A3B8 !important; }
    section[data-testid="stSidebar"] .block-container { padding-top:1.2rem; }
    section[data-testid="stSidebar"] hr { border-color:#1E293B; }

    .side-logo { display:flex; align-items:center; gap:11px; padding:6px 6px; }
    .side-logo .lg {
        width:44px; height:44px; border-radius:13px; flex-shrink:0;
        background:linear-gradient(135deg,#3B82F6,#8B5CF6);
        display:flex; align-items:center; justify-content:center;
        font-size:22px; box-shadow:0 8px 18px rgba(37,99,235,.4);
    }
    .side-logo .tt { font-weight:800; font-size:15.5px; color:#F8FAFC !important; line-height:1.15; }
    .side-logo .ss { font-size:10.5px; color:#64748B !important; font-weight:700; letter-spacing:.5px; text-transform:uppercase; }

    .side-cap { font-size:10px; font-weight:800; letter-spacing:1.2px; color:#475569 !important;
                text-transform:uppercase; padding:10px 6px 2px; }

    [data-testid="stSidebar"] div[role="radiogroup"] { gap:3px !important; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] {
        padding:9px 13px; border-radius:12px; border:1px solid transparent;
        transition:.15s; background:transparent; margin:0;
    }
    [data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child { display:none !important; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] div[data-baseweb="radio"] { display:none !important; }
    [data-testid="stSidebar"] input[type="radio"] { accent-color:#2563EB; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] p { font-size:13.5px; font-weight:600; }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover { background:rgba(255,255,255,.06); }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover p { color:#F8FAFC !important; }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
        background:linear-gradient(135deg,#2563EB,#4F46E5);
        box-shadow:0 6px 16px rgba(37,99,235,.4);
    }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) div,
    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p {
        color:#fff !important; font-weight:700;
    }

    .mini {
        background:rgba(255,255,255,.04); border:1px solid #1E293B;
        border-radius:16px; padding:12px 14px; margin-top:10px;
    }
    .mini .t { font-size:11px; font-weight:800; color:#60A5FA !important; letter-spacing:.3px; }
    .mini .v { font-size:13.5px; font-weight:800; color:#F1F5F9 !important; margin:4px 0 8px; }
    .mini .s { font-size:10.5px; color:#64748B !important; font-weight:600; margin-top:6px; }
    .bar { height:7px; background:#1E293B; border-radius:99px; overflow:hidden; }
    .bar > i { display:block; height:100%; border-radius:99px; background:linear-gradient(90deg,#3B82F6,#8B5CF6); }

    .user-card {
        background:rgba(255,255,255,.05); border:1px solid #1E293B;
        border-radius:16px; padding:12px 14px; display:flex; align-items:center; gap:10px;
    }
    .user-card .av {
        width:38px; height:38px; border-radius:11px; flex-shrink:0;
        background:linear-gradient(135deg,#3B82F6,#8B5CF6);
        display:flex; align-items:center; justify-content:center; font-size:17px;
    }
    .user-card .nm { font-weight:700; font-size:13px; color:#F1F5F9 !important; }
    .user-card .rl { font-size:11px; color:#64748B !important; font-weight:600; }

    /* ============ TOPBAR ============ */
    .topbar {
        display:flex; justify-content:space-between; align-items:center; gap:12px;
        background:#FFFFFF; border:1px solid #E6EAF2;
        border-radius:18px; padding:14px 20px; margin:4px 0 16px;
        box-shadow:0 2px 10px rgba(15,23,42,.04);
    }
    .topbar h1 { margin:0; font-size:20px; font-weight:800; color:#0F172A !important; letter-spacing:-.3px; }
    .topbar p { margin:3px 0 0; color:#64748B; font-size:12.5px; font-weight:500; }
    .tb-r { display:flex; align-items:center; gap:10px; flex-shrink:0; }
    .tb-chip {
        background:#EFF6FF; color:#2563EB !important; border:1px solid #DBEAFE;
        font-weight:700; font-size:12px; padding:9px 14px; border-radius:12px;
    }
    .tb-bell {
        position:relative; width:40px; height:40px; border-radius:12px;
        background:#F1F5F9; border:1px solid #E6EAF2;
        display:flex; align-items:center; justify-content:center; font-size:16px;
    }
    .tb-bell .dot {
        position:absolute; top:9px; right:10px; width:8px; height:8px;
        border-radius:50%; background:#EF4444; border:2px solid #F1F5F9;
    }
    .tb-av {
        width:40px; height:40px; border-radius:12px;
        background:linear-gradient(135deg,#3B82F6,#8B5CF6);
        color:#fff !important; display:flex; align-items:center; justify-content:center;
        font-weight:800; font-size:14px; box-shadow:0 6px 14px rgba(37,99,235,.3);
    }

    /* ============ STAT KARTALAR ============ */
    .stats-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr));
                 gap:14px; margin:6px 0 18px; }
    .stat-card {
        background:#FFFFFF; border:1px solid #E6EAF2; border-radius:18px;
        padding:16px; display:flex; align-items:center; gap:12px;
        box-shadow:0 2px 10px rgba(15,23,42,.04);
        transition:transform .16s ease, box-shadow .16s ease;
    }
    .stat-card:hover { transform:translateY(-3px); box-shadow:0 10px 22px rgba(15,23,42,.09); }
    .stat-ic { width:46px; height:46px; border-radius:14px; flex-shrink:0;
               display:flex; align-items:center; justify-content:center; font-size:21px; }
    .stat-card .lbl { font-size:11.5px; color:#94A3B8; font-weight:700; letter-spacing:.2px; }
    .stat-card .val { font-size:18px; font-weight:800; color:#0F172A; margin-top:2px; }

    /* ============ OQ KARTALAR ============ */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:#FFFFFF; border:1px solid #E6EAF2 !important;
        border-radius:18px !important; box-shadow:0 2px 10px rgba(15,23,42,.04);
        padding:16px 18px !important;
    }

    /* ============ HTML JADVAL ============ */
    .lcard { background:#fff; border:1px solid #E6EAF2; border-radius:18px;
             box-shadow:0 2px 10px rgba(15,23,42,.04); overflow:hidden; }
    .lcard-h { display:flex; justify-content:space-between; align-items:center;
               padding:14px 18px; border-bottom:1px solid #F1F5F9; }
    .lcard-h .t { font-weight:800; font-size:14.5px; color:#0F172A; }
    .lcard-h .n { font-size:11px; font-weight:800; color:#2563EB;
                  background:#EFF6FF; padding:4px 11px; border-radius:999px; }
    .lbody { max-height:420px; overflow:auto; }
    table.ht { width:100%; border-collapse:collapse; font-size:13px; }
    .ht th { position:sticky; top:0; background:#F8FAFC; color:#64748B; font-size:10.5px;
             text-transform:uppercase; letter-spacing:.5px; text-align:left;
             padding:10px 14px; border-bottom:1px solid #E6EAF2; font-weight:800; z-index:1; }
    .ht td { padding:10px 14px; border-bottom:1px solid #F1F5F9; color:#0F172A; vertical-align:middle; }
    .ht tr:last-child td { border-bottom:none; }
    .ht tr:hover td { background:#F8FAFC; }
    .cell-p { display:flex; align-items:center; gap:10px; font-weight:600; }
    .sub { font-size:11px; color:#94A3B8; font-weight:500; margin-top:1px; }
    .num { font-weight:700; white-space:nowrap; }
    .mut { color:#94A3B8; font-weight:600; font-size:12px; }

    .avatar { display:inline-flex; align-items:center; justify-content:center;
              border-radius:11px; font-weight:800; flex-shrink:0; }
    .cls-chip { width:32px; height:32px; border-radius:11px; flex-shrink:0;
                display:inline-flex; align-items:center; justify-content:center;
                background:#EFF6FF; font-size:15px; }

    /* ============ PILL BADGE ============ */
    .pill { display:inline-block; padding:4px 11px; border-radius:999px;
            font-size:10.5px; font-weight:800; letter-spacing:.3px; white-space:nowrap; }
    .p-ok   { background:#DCFCE7; color:#15803D; }
    .p-warn { background:#FEF3C7; color:#B45309; }
    .p-bad  { background:#FEE2E2; color:#DC2626; }
    .p-info { background:#DBEAFE; color:#1D4ED8; }
    .p-mut  { background:#F1F5F9; color:#64748B; }

    .dwrap { display:flex; justify-content:center; padding:4px 0; }

    /* ============ TUGMALAR ============ */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        border-radius:12px; font-weight:700; border:1px solid #E2E8F0;
        background:#FFFFFF; color:#334155; box-shadow:0 1px 3px rgba(15,23,42,.05); transition:.16s;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform:translateY(-1px); border-color:#93C5FD; color:#2563EB;
        box-shadow:0 6px 14px rgba(37,99,235,.12);
    }
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primaryFormSubmit"] {
        background:linear-gradient(135deg,#2563EB,#4F46E5); border:none; color:#fff !important;
        box-shadow:0 6px 16px rgba(37,99,235,.35);
    }
    .stButton > button[kind="primary"]:hover { filter:brightness(1.07); color:#fff !important; }

    /* ============ INPUTLAR ============ */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiselect div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        background:#FFFFFF !important; border:1px solid #E2E8F0 !important;
        border-radius:12px !important; color:#0F172A !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color:#93C5FD !important; box-shadow:0 0 0 3px rgba(59,130,246,.12) !important;
    }

    /* ============ FORM / EXPANDER / ALERT ============ */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        border:1px solid #E6EAF2; border-radius:16px; overflow:hidden; background:#fff;
    }
    div[data-testid="stForm"] {
        border:1px solid #E6EAF2; border-radius:18px; background:#FFFFFF;
        padding:10px 14px 6px; box-shadow:0 2px 10px rgba(15,23,42,.04);
    }
    div[data-testid="stExpander"] {
        border:1px solid #E6EAF2 !important; border-radius:16px !important;
        background:#fff; box-shadow:0 2px 10px rgba(15,23,42,.04);
    }
    div[data-testid="stAlert"] { border-radius:14px; }

    /* ============ TABS ============ */
    .stTabs [data-baseweb="tab-list"] { gap:6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius:12px; background:#EDF1F8; border:1px solid transparent;
        font-weight:700; padding:7px 15px; color:#475569;
    }
    .stTabs [aria-selected="true"] {
        background:linear-gradient(135deg,#2563EB,#4F46E5) !important; color:#fff !important;
        box-shadow:0 6px 14px rgba(37,99,235,.3);
    }

    h1, h2, h3, h4 { color:#0F172A !important; font-weight:800 !important; }
    hr { border-color:#E6EAF2; }

    ::-webkit-scrollbar { width:8px; height:8px; }
    ::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:8px; }
    ::-webkit-scrollbar-track { background:transparent; }
    .lbody::-webkit-scrollbar-thumb { background:#E2E8F0; }

    /* ============ MOBIL ============ */
    @media (max-width: 640px) {
        .topbar { flex-direction:column; align-items:flex-start; padding:14px 16px; }
        .tb-r { width:100%; justify-content:space-between; }
        .topbar h1 { font-size:17px; }
        .stats-row { grid-template-columns:repeat(2,1fr); gap:10px; }
        .stat-card { padding:12px; }
        .stat-card .val { font-size:15px; }
        .stat-ic { width:38px; height:38px; font-size:17px; }
        .block-container { padding:0.7rem 0.7rem 4rem; }
    }
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] { box-shadow:20px 0 60px rgba(2,6,23,.45); }
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# FIREBASE
# ------------------------------------------------------------
def _params():
    return {"auth": DB_AUTH} if DB_AUTH else {}


def fb_get(yol):
    r = requests.get(f"{DB_URL}/{yol}.json", params=_params(), timeout=12)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=40, show_spinner=False)
def _kesh_oqi(yol):
    return fb_get(yol)


def oqi(yol, yangi=False):
    try:
        return fb_get(yol) if yangi else _kesh_oqi(yol)
    except Exception:
        st.error("☁️ Bulutga ulanib bo‘lmadi. Internetni tekshiring va sidebar’dagi «🔄» tugmasini bosing.")
        st.stop()


def fb_put(yol, qiymat):
    try:
        r = requests.put(f"{DB_URL}/{yol}.json", params=_params(), json=qiymat, timeout=12)
        ok = r.status_code == 200
    except requests.RequestException:
        ok = False
    if ok:
        _kesh_oqi.clear()
    return ok


# ------------------------------------------------------------
# YORDAMCHI FUNKSIYALAR
# ------------------------------------------------------------
def num(x, d=0.0):
    try:
        if x is None or x == "":
            return d
        v = float(str(x).replace(" ", "").replace(",", ""))
        return d if v != v else v
    except (ValueError, TypeError):
        return d


def fmt(x):
    return f"{int(round(num(x))):,}".replace(",", " ")


def som(x):
    return fmt(x) + " so‘m"


def royxat(v):
    if not v:
        return []
    items = v if isinstance(v, list) else list(v.values())
    return [x for x in items if isinstance(x, dict)]


def safe_key(k):
    return re.sub(r"[.$#\[\]/\x00-\x1f]", "_", str(k)).strip() or "_"


def sof(s):
    return num(s.get("price")) - num(s.get("disc")) - num(s.get("food"))


def qarz(s):
    if s.get("st") == "st-paid":
        return 0.0
    return max(sof(s) - num(s.get("paid")), 0.0)


def holat_uz(kod):
    return HOLATLAR.get(kod, "QARZ")


def holat_kod(uz):
    return {v: k for k, v in HOLATLAR.items()}.get(uz, "st-debt")


def eq(a, b):
    return hmac.compare_digest(str(a).encode(), str(b).encode())


def hash_raw(parol, tuz):
    return hashlib.pbkdf2_hmac("sha256", parol.encode(), tuz.encode(), 120_000).hex()


def hash_pw(parol):
    tuz = secrets.token_hex(8)
    return f"pbkdf2${tuz}${hash_raw(parol, tuz)}"


def check_pw(parol, saqlangan):
    if not saqlangan:
        return False
    if str(saqlangan).startswith("pbkdf2$"):
        try:
            _, tuz, h = saqlangan.split("$")
        except ValueError:
            return False
        return eq(hash_raw(parol, tuz), h)
    return eq(parol, saqlangan)


def tg_yubor(c, matn):
    tok, chat = c.get("tgToken"), c.get("chatId")
    if not tok or not chat:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{tok}/sendMessage",
            json={"chat_id": chat, "text": matn[:4000]},
            timeout=10
        )
        return r.ok
    except requests.RequestException:
        return False


def excel_tugma(df, varaq, fayl, key):
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name=varaq[:31])
        st.download_button(
            "📊 Excel yuklab olish", buf.getvalue(),
            file_name=f"{fayl}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=key, **KENG
        )
    except Exception:
        st.download_button(
            "📄 CSV yuklab olish",
            df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{fayl}.csv", mime="text/csv", key=key, **KENG
        )


def eslat(matn):
    st.session_state.flash = matn


# ------------------------------------------------------------
# DIZAYN KOMPONENTLARI
# ------------------------------------------------------------
R_AV = [("#EEF2FF", "#4F46E5"), ("#ECFDF5", "#059669"), ("#FEF3C7", "#B45309"),
        ("#FCE7F3", "#DB2777"), ("#E0F2FE", "#0369A1"), ("#EDE9FE", "#6D28D9"),
        ("#DCFCE7", "#15803D"), ("#FFE4E6", "#E11D48")]


def avatar(nom, size=32):
    nom = str(nom).strip() or "?"
    q = [s for s in nom.split() if s]
    ini = ((q[0][0] if q else "?") + (q[1][0] if len(q) > 1 else "")).upper()
    bg, fg = R_AV[sum(ord(c) for c in nom) % len(R_AV)]
    fs = max(11, int(size * 0.40))
    return (f'<span class="avatar" style="width:{size}px;height:{size}px;'
            f'background:{bg};color:{fg};font-size:{fs}px">{html.escape(ini)}</span>')


def pill(matn, stil):
    return f'<span class="pill {stil}">{html.escape(str(matn))}</span>'


def pill_holat(kod):
    return {"st-paid": "p-ok", "st-partial": "p-warn"}.get(kod, "p-bad")


def topbar(sarlavha, ostki=""):
    ism = str(cfg.get("user", "admin"))
    q = [s for s in ism.split() if s]
    ini = (q[0][0] if q else "A").upper()
    st.markdown(f"""<div class="topbar">
        <div class="tb-l">
            <h1>{html.escape(sarlavha)}</h1>
            <p>{html.escape(ostki)}</p>
        </div>
        <div class="tb-r">
            <div class="tb-chip">📅 {datetime.now().strftime('%d.%m.%Y')}</div>
            <div class="tb-bell">🔔<span class="dot"></span></div>
            <div class="tb-av">{html.escape(ini)}</div>
        </div>
    </div>""", unsafe_allow_html=True)


def stat_cards(kartalar):
    h = '<div class="stats-row">'
    for icon, nom, qiymat, rang in kartalar:
        h += f"""<div class="stat-card">
            <div class="stat-ic" style="background:{rang}1A;color:{rang}">{icon}</div>
            <div class="stat-tx">
                <div class="lbl">{html.escape(str(nom))}</div>
                <div class="val">{html.escape(str(qiymat))}</div>
            </div>
        </div>"""
    h += "</div>"
    st.markdown(h, unsafe_allow_html=True)


def list_card(sarlavha, ustunlar, qatorlar, maxh=420, badge=None):
    if not qatorlar:
        qatorlar = [['<span class="mut">Ma’lumot yo‘q</span>'] + [""] * (len(ustunlar) - 1)]
    th = "".join(f"<th>{html.escape(u)}</th>" for u in ustunlar)
    body = ""
    for q in qatorlar:
        tds = "".join(f"<td>{c}</td>" for c in q)
        body += f"<tr>{tds}</tr>"
    b = f'<span class="n">{html.escape(str(badge))}</span>' if badge else f'<span class="n">{len(qatorlar)} ta</span>'
    return f"""<div class="lcard">
        <div class="lcard-h"><span class="t">{html.escape(sarlavha)}</span>{b}</div>
        <div class="lbody" style="max-height:{maxh}px">
            <table class="ht"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>
        </div>
    </div>"""


def donut(foiz):
    foiz = max(0, min(100, int(foiz)))
    r = 54
    c = 2 * math.pi * r
    off = c * (1 - foiz / 100)
    return f"""<div class="dwrap"><svg width="150" height="150" viewBox="0 0 150 150">
        <circle cx="75" cy="75" r="{r}" fill="none" stroke="#DBEAFE" stroke-width="15"/>
        <circle cx="75" cy="75" r="{r}" fill="none" stroke="#2563EB" stroke-width="15"
            stroke-linecap="round" stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}"
            transform="rotate(-90 75 75)"/>
        <text x="75" y="72" text-anchor="middle" font-size="27" font-weight="800" fill="#0F172A"
            font-family="Plus Jakarta Sans, sans-serif">{foiz}%</text>
        <text x="75" y="94" text-anchor="middle" font-size="10" font-weight="800" fill="#94A3B8"
            letter-spacing="1" font-family="Plus Jakarta Sans, sans-serif">UNDIRILDI</text>
    </svg></div>"""


def plan_html(oy, yigildi, reja):
    p = min(int(yigildi / reja * 100), 100) if reja > 0 else 0
    return f"""<div class="mini">
        <div class="t">🎯 {html.escape(oy)} REJASI</div>
        <div class="v">{html.escape(som(yigildi))} / {html.escape(som(reja))}</div>
        <div class="bar"><i style="width:{p}%"></i></div>
        <div class="s">{p}% bajarildi</div>
    </div>"""


def oylik_grafik(df, ustunlar, ranglar):
    try:
        import altair as alt
        uzun = df.melt(id_vars="Oy", value_vars=ustunlar, var_name="Tur", value_name="Summa")
        ch = alt.Chart(uzun).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Oy:N", sort=OYLAR, title=None),
            xOffset="Tur:N",
            y=alt.Y("Summa:Q", title=None),
            color=alt.Color("Tur:N", scale=alt.Scale(domain=ustunlar, range=ranglar),
                            legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["Oy", "Tur", "Summa"],
        ).properties(height=290)
        st.altair_chart(ch, **KENG)
    except Exception:
        st.bar_chart(df.set_index("Oy")[ustunlar])


# ------------------------------------------------------------
# SESSION
# ------------------------------------------------------------
for k, v in {
    "kirgan": False, "roll": "view", "data": {}, "yuklandi": False,
    "versiya": 0, "cfg": dict(STANDART)
}.items():
    st.session_state.setdefault(k, v)


def bulutdan_yukla():
    d = oqi("accounting/data", yangi=True)
    st.session_state.data = d if isinstance(d, dict) else {}
    st.session_state.yuklandi = True


def oy_ma(oy):
    return royxat(st.session_state.data.get(oy))


def oy_saqla(oy, mal):
    if fb_put(f"accounting/data/{oy}", mal):
        st.session_state.data[oy] = mal
        return True
    return False


# ------------------------------------------------------------
# KIRISH
# ------------------------------------------------------------
def tekshir(u, p):
    try:
        c = {**STANDART, **(fb_get("accounting/config") or {})}
    except Exception:
        st.error("☁️ Bulutga ulanib bo‘lmadi.")
        return
    akk = [(c["user"], c["pass"], "pass", "admin")]
    if c.get("user2"):
        akk.append((
            c["user2"], c.get("pass2", ""), "pass2",
            "admin" if c.get("role2") == "full" else "view"
        ))
    for lg, sp, kalit, roll in akk:
        if lg and eq(u.strip(), lg) and check_pw(p, sp):
            if not str(sp).startswith("pbkdf2$"):
                c[kalit] = hash_pw(p)
                fb_put("accounting/config", c)
            st.session_state.update(
                kirgan=True, roll=roll, cfg=c, xato=0,
                standart_parol=eq(p, "123")
            )
            st.rerun()
    st.session_state.xato = st.session_state.get("xato", 0) + 1
    if st.session_state.xato >= 5:
        st.session_state.blok_vaqt = time.time() + 60
        st.session_state.xato = 0
        st.error("Juda ko‘p xato urinish. 1 daqiqadan so‘ng qayta urining.")
    else:
        st.error("Login yoki parol xato!")


def parol_tiklash():
    st.caption("Tasdiqlash kodi sozlamalarda ko‘rsatilgan Telegram chatga yuboriladi.")
    tel = st.text_input("Ro‘yxatdagi telefon raqam", key="rec_tel")
    if st.button("📨 Telegramga kod yuborish", key="rec_send"):
        try:
            c = {**STANDART, **(fb_get("accounting/config") or {})}
        except Exception:
            st.error("☁️ Bulutga ulanib bo‘lmadi.")
            return
        if not (c.get("tgToken") and c.get("chatId")):
            st.error("Telegram sozlanmagan. Parolni Firebase konsolida qo‘lda tiklang.")
        elif len(tel.strip()) >= 7 and eq(tel.strip(), c.get("phone") or ""):
            kod = f"{secrets.randbelow(10**6):06d}"
            if tg_yubor(c, f"🔐 Parol tiklash kodi: {kod}\n(10 daqiqa amal qiladi)"):
                st.session_state.rec = (kod, time.time() + 600)
                st.success("Kod Telegramga yuborildi.")
            else:
                st.error("Kodni yuborib bo‘lmadi.")
        else:
            st.error("Raqam mos kelmadi.")
    if st.session_state.get("rec"):
        kod_i = st.text_input("Telegramdagi kod", key="rec_kod")
        yangi = st.text_input("Yangi parol", type="password", key="rec_new")
        if st.button("✅ Parolni yangilash", key="rec_ok"):
            kod, muddat = st.session_state.rec
            if time.time() > muddat:
                st.error("Kod muddati tugadi.")
            elif not eq(kod_i.strip(), kod):
                st.error("Kod noto‘g‘ri.")
            elif len(yangi) < MIN_PAROL:
                st.error(f"Parol kamida {MIN_PAROL} belgi bo‘lsin.")
            else:
                c = {**STANDART, **(fb_get("accounting/config") or {})}
                c["pass"] = hash_pw(yangi)
                if fb_put("accounting/config", c):
                    st.session_state.rec = None
                    st.success("Parol yangilandi. Endi kirishingiz mumkin.")
                else:
                    st.error("Saqlab bo‘lmadi.")


def kirish_oynasi():
    st.markdown("""
    <div style="text-align:center; padding:34px 0 16px;">
        <div style="width:74px;height:74px;margin:0 auto 14px;border-radius:20px;
        background:linear-gradient(135deg,#3B82F6,#8B5CF6);display:flex;align-items:center;
        justify-content:center;font-size:35px;box-shadow:0 14px 30px rgba(37,99,235,.4);">🏫</div>
        <h1 style="margin:0;color:#0F172A;font-size:26px;font-weight:800;">
        Maktab Buxgalteriya</h1>
        <p style="color:#64748B;margin-top:6px;font-weight:500;">Talabalar hisob-kitobi — Admin Panel</p>
    </div>""", unsafe_allow_html=True)

    _, c, _ = st.columns([1.15, 2, 1.15])
    with c:
        with st.form("kirish_forma"):
            u = st.text_input("👤 Login")
            p = st.text_input("🔒 Parol", type="password")
            ok = st.form_submit_button("🚀 Kirish", type="primary", **KENG)
        if ok:
            qolgan = st.session_state.get("blok_vaqt", 0) - time.time()
            if qolgan > 0:
                st.error(f"Ko‘p xato urinish. {int(qolgan)} soniyadan so‘ng urinib ko‘ring.")
            else:
                tekshir(u, p)
        with st.expander("❓ Parolni unutdim"):
            parol_tiklash()
    st.stop()


if not st.session_state.kirgan:
    kirish_oynasi()

if not st.session_state.yuklandi:
    bulutdan_yukla()

cfg = st.session_state.cfg
ADMIN = st.session_state.roll == "admin"


# ------------------------------------------------------------
# 🏠 DASHBOARD
# ------------------------------------------------------------
def sahifa_dashboard():
    topbar("👋 Xush kelibsiz!", f"{cfg.get('orgName', 'Maktab')} — barcha hisoblar bir joyda")
    if st.session_state.get("standart_parol"):
        st.warning("⚠️ Siz standart parol (123) bilan kirdingiz. «⚙️ Sozlamalar»da uni darhol almashtiring!")
    if not ADMIN:
        st.info("👀 Siz faqat ko‘rish rejimidasiz")

    hamma = {oy: oy_ma(oy) for oy in OYLAR}
    barcha = [s for m in hamma.values() for s in m]
    jami_t = sum(num(s.get("price")) for s in barcha)
    jami_sof = sum(sof(s) for s in barcha)
    jami_q = sum(qarz(s) for s in barcha)
    foiz = round(max(jami_sof - jami_q, 0) / jami_sof * 100) if jami_sof > 0 else 0

    stat_cards([
        ("👥", "O‘quvchi yozuvlari", len(barcha), "#2563EB"),
        ("💰", "Umumiy tushum", som(jami_t), "#10B981"),
        ("🔴", "Umumiy qarz", som(jami_q), "#EF4444"),
        ("📈", "Undirish darajasi", f"{foiz}%", "#8B5CF6"),
        ("📚", "To‘ldirilgan oylar", f"{sum(1 for m in hamma.values() if m)}/12", "#F59E0B"),
    ])

    reja = num(cfg.get("monthlyPlan"))
    if reja > 0:
        joriy_oy = OYLAR[datetime.now().month - 1]
        yigildi = sum(sof(s) - qarz(s) for s in hamma[joriy_oy])
        st.markdown(plan_html(joriy_oy, yigildi, reja), unsafe_allow_html=True)

    g1, g2 = st.columns([2.4, 1])
    with g1:
        with st.container(border=True):
            st.markdown("#### 📊 Oylar kesimida")
            if barcha:
                grafik_df = pd.DataFrame([{
                    "Oy": oy,
                    "Tushum": sum(num(s.get("price")) for s in m),
                    "Qarz": sum(qarz(s) for s in m)
                } for oy, m in hamma.items()])
                oylik_grafik(grafik_df, ["Tushum", "Qarz"], ["#2563EB", "#EF4444"])
            else:
                st.info("Ma’lumot yo‘q")
    with g2:
        with st.container(border=True):
            st.markdown("#### 🎯 Undirish")
            st.markdown(donut(foiz), unsafe_allow_html=True)
            st.caption(f"Yig‘ildi: **{som(jami_sof - jami_q)}** / {som(jami_sof)}")

    c1, c2, c3 = st.columns(3)
    with c1:
        qd = {}
        for m in hamma.values():
            for s in m:
                q = qarz(s)
                nom = str(s.get("name") or "").strip()
                if q > 0 and nom:
                    qd[nom] = qd.get(nom, 0) + q
        top = sorted(qd.items(), key=lambda x: -x[1])[:5]
        rows = [[
            f'<div class="cell-p">{avatar(n)}<span>{html.escape(n)}</span></div>',
            f'<span class="num" style="color:#DC2626">{fmt(q)}</span>',
            pill("QARZ", "p-bad")
        ] for n, q in top]
        st.markdown(list_card("🔴 Eng katta qarzdorlar", ["O‘quvchi", "Qarz", "Holat"], rows, 300),
                    unsafe_allow_html=True)
    with c2:
        tol = royxat(oqi("accounting/payments"))[:5]
        rows = [[
            f'''<div class="cell-p">{avatar(p.get("name", "?"))}
                <span>{html.escape(str(p.get("name", "")))}
                <div class="sub">{html.escape(str(p.get("note") or p.get("type", "")))}</div></span></div>''',
            f'<span class="mut">{html.escape(str(p.get("date", "")))}</span>',
            f'<span class="num" style="color:#15803D">+{fmt(p.get("amount"))}</span>'
        ] for p in tol]
        st.markdown(list_card("🧾 So‘nggi to‘lovlar", ["O‘quvchi", "Sana", "Summa"], rows, 300),
                    unsafe_allow_html=True)
    with c3:
        dav = (st.session_state.data.get("__davomat__") or {}).get(str(date.today())) or {}
        kel = sum(1 for v in dav.values() if v is True)
        kelma = sum(1 for v in dav.values() if v is False)
        st.markdown("#### 📅 Bugungi davomat")
        if dav:
            stat_cards([
                ("✅", "Keldi", kel, "#10B981"),
                ("❌", "Kelmadi", kelma, "#EF4444"),
            ])
            st.success(f"Jami belgilangan: {kel + kelma} ta o‘quvchi")
        else:
            st.info("Bugun hali belgilanmagan")


# ------------------------------------------------------------
# 💰 HISOB
# ------------------------------------------------------------
USTUN = ["Ism", "Sinf", "Narx", "Chegirma", "Ovqat", "To‘langan", "Holat", "Keldi"]
SONLI = ["Narx", "Chegirma", "Ovqat", "To‘langan"]


def oy_df(mal):
    rows = [{
        "Ism": str(s.get("name") or ""),
        "Sinf": str(s.get("cls") or ""),
        "Narx": num(s.get("price")),
        "Chegirma": num(s.get("disc")),
        "Ovqat": num(s.get("food")),
        "To‘langan": num(s.get("paid")),
        "Holat": holat_uz(s.get("st")),
        "Keldi": bool(s.get("att", True)),
    } for s in mal]
    df = pd.DataFrame(rows, columns=USTUN)
    return df.astype({**{c: float for c in SONLI}, "Keldi": bool})


def df_oy(df):
    df = df.copy()
    df["Ism"] = df["Ism"].fillna("").astype(str).str.strip()
    df["Sinf"] = df["Sinf"].fillna("").astype(str).str.strip()
    df["Holat"] = df["Holat"].fillna("QARZ")
    df["Keldi"] = df["Keldi"].fillna(True)
    for c in SONLI:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    out = []
    for r in df.to_dict("records"):
        if not r["Ism"]:
            continue
        out.append({
            "name": r["Ism"], "cls": r["Sinf"],
            "price": num(r["Narx"]), "disc": num(r["Chegirma"]),
            "food": num(r["Ovqat"]), "paid": num(r["To‘langan"]),
            "st": holat_kod(r["Holat"]), "att": bool(r["Keldi"])
        })
    return out


def bazadan_qosh(oy):
    mal = oy_ma(oy)
    bor = {str(s.get("name", "")).strip().lower() for s in mal}
    n = 0
    for b in royxat(oqi("accounting/students")):
        nom = str(b.get("name") or "").strip()
        if nom and nom.lower() not in bor:
            mal.append({
                "name": nom,
                "cls": str(b.get("cls") or "").strip(),
                "price": num(b.get("price")) or num(cfg.get("defaultPrice")),
                "disc": 0, "food": 0, "paid": 0, "st": "st-debt", "att": True
            })
            bor.add(nom.lower())
            n += 1
    return mal, n


def oldingi_oydan(oy):
    i = OYLAR.index(oy)
    if i == 0:
        return oy_ma(oy), 0
    mal = oy_ma(oy)
    bor = {str(s.get("name", "")).strip().lower() for s in mal}
    n = 0
    for s in oy_ma(OYLAR[i - 1]):
        nom = str(s.get("name") or "").strip()
        if nom and nom.lower() not in bor:
            mal.append({**s, "paid": 0, "st": "st-debt", "att": True})
            bor.add(nom.lower())
            n += 1
    return mal, n


def sahifa_hisob():
    topbar("💰 Hisob", "Jadvalni tahrirlang va «Bulutga saqlash»ni bosing")
    c1, c2 = st.columns(2)
    oy = c1.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="h_oy")
    mal = oy_ma(oy)
    toliq = oy_df(mal)
    sinflar = sorted({x for x in toliq["Sinf"].str.strip() if x})
    sinf_f = c2.selectbox("🎓 Sinf filtri", ["Barchasi"] + sinflar, key="h_cls")

    if ADMIN:
        with st.expander("⚡ Tezkor amallar"):
            a1, a2 = st.columns(2)
            if a1.button("📥 Bazadagi o‘quvchilarni qo‘shish", **KENG):
                yangi, n = bazadan_qosh(oy)
                if n and oy_saqla(oy, yangi):
                    eslat(f"✅ {n} ta o‘quvchi qo‘shildi")
                    st.session_state.versiya += 1
                    st.rerun()
                st.info("Qo‘shiladigan yangi o‘quvchi topilmadi" if not n else "Saqlab bo‘lmadi")
            if a2.button("📋 Oldingi oydan nusxalash", **KENG):
                yangi, n = oldingi_oydan(oy)
                if n and oy_saqla(oy, yangi):
                    eslat(f"✅ {n} ta yozuv ko‘chirildi (holat: QARZ)")
                    st.session_state.versiya += 1
                    st.rerun()
                st.info("Ko‘chiriladigan yozuv topilmadi" if not n else "Saqlab bo‘lmadi")

    mask = (toliq["Sinf"].str.strip() == sinf_f) if sinf_f != "Barchasi" else pd.Series(True, index=toliq.index)
    with st.container(border=True):
        st.markdown("#### 🗓 Oylik jadval")
        tahrir = st.data_editor(
            toliq[mask],
            num_rows="dynamic" if ADMIN else "fixed",
            hide_index=True,
            disabled=not ADMIN,
            **KENG,
            column_config={
                "Ism": st.column_config.TextColumn("👤 Ism", width="large"),
                "Narx": st.column_config.NumberColumn("💰 Narx", step=1000, min_value=0),
                "Chegirma": st.column_config.NumberColumn("🎗 Chegirma", step=1000, min_value=0),
                "Ovqat": st.column_config.NumberColumn("🍽 Ovqat", step=1000, min_value=0),
                "To‘langan": st.column_config.NumberColumn("💵 To‘langan", step=1000, min_value=0),
                "Holat": st.column_config.SelectboxColumn("Holat", options=list(HOLATLAR.values())),
                "Keldi": st.column_config.CheckboxColumn("✅ Keldi"),
            },
            key=f"jadval_{oy}_{sinf_f}_{st.session_state.versiya}"
        )
        if ADMIN and st.button("💾 Bulutga saqlash", type="primary", **KENG):
            yangi = tahrir.copy()
            if sinf_f != "Barchasi":
                yangi["Sinf"] = yangi["Sinf"].fillna("").replace("", sinf_f)
            birlashgan = pd.concat([toliq[~mask], yangi], ignore_index=True)
            if oy_saqla(oy, df_oy(birlashgan)):
                eslat("✅ Bulutga saqlandi!")
                st.session_state.versiya += 1
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")

    joriy = df_oy(tahrir) if len(tahrir) else []
    if joriy:
        stat_cards([
            ("💰", "Tushum", fmt(sum(num(s["price"]) for s in joriy)), "#2563EB"),
            ("🎗", "Chegirma", fmt(sum(num(s["disc"]) for s in joriy)), "#F59E0B"),
            ("🍽", "Ovqat", fmt(sum(num(s["food"]) for s in joriy)), "#EF4444"),
            ("✅", "Sof foyda", fmt(sum(sof(s) for s in joriy)), "#10B981"),
            ("👥", "O‘quvchi", len(joriy), "#8B5CF6"),
            ("🔴", "Qarz", fmt(sum(qarz(s) for s in joriy)), "#EF4444"),
        ])
        exc = pd.DataFrame([{
            "Ism": s["name"], "Sinf": s["cls"], "Narx": s["price"],
            "Chegirma": s["disc"], "Ovqat": s["food"], "Sof": sof(s),
            "To‘langan": s["paid"], "Qarz": qarz(s),
            "Holat": holat_uz(s["st"]), "Keldi": "Ha" if s["att"] else "Yo‘q"
        } for s in joriy])
        excel_tugma(exc, oy, f"Hisobot_{oy}", "xl_hisob")
    else:
        st.info("Bu oyda ma’lumot yo‘q — jadvalga qator qo‘shing yoki «Tezkor amallar»dan foydalaning!")


# ------------------------------------------------------------
# 📅 KUNLIK DAVOMAT
# ------------------------------------------------------------
def sahifa_davomat():
    topbar("📅 Kunlik davomat", "Har kuni kim kelganini belgilang")
    sana_d = st.date_input("Sana", value=date.today())
    sana = str(sana_d)
    bazalar = royxat(oqi("accounting/students"))
    if not bazalar:
        st.warning("Baza bo‘sh! Avval «👨‍🎓 Baza» bo‘limida o‘quvchi qo‘shing.")
        return

    saqlangan = (st.session_state.data.get("__davomat__") or {}).get(sana) or {}
    boshl_kalit = f"dav_def_{sana}"
    boshl = st.session_state.get(boshl_kalit)

    if ADMIN:
        b1, b2, _ = st.columns([1, 1, 2])
        if b1.button("✅ Hammasi keldi", **KENG):
            st.session_state[boshl_kalit] = "Keldi"
            st.rerun()
        if b2.button("↺ Tozalash", **KENG):
            st.session_state[boshl_kalit] = "—"
            st.rerun()

    rows = []
    for b in bazalar:
        nom = str(b.get("name") or "").strip()
        if not nom:
            continue
        v = saqlangan.get(safe_key(nom))
        h = "Keldi" if v is True else "Kelmadi" if v is False else "—"
        rows.append({"Ism": nom, "Sinf": str(b.get("cls") or ""), "Holat": boshl or h})
    df = pd.DataFrame(rows)

    with st.container(border=True):
        st.markdown("#### ✅ Davomat jadvali")
        tahrir = st.data_editor(
            df, hide_index=True,
            disabled=["Ism", "Sinf"] if ADMIN else True,
            **KENG,
            column_config={
                "Holat": st.column_config.SelectboxColumn(
                    "Holat", options=["—", "Keldi", "Kelmadi"], required=True
                )
            },
            key=f"dav_{sana}_{st.session_state.versiya}_{boshl}"
        )

    kel = int((tahrir["Holat"] == "Keldi").sum())
    kelma = int((tahrir["Holat"] == "Kelmadi").sum())
    belgisiz = int((tahrir["Holat"] == "—").sum())
    stat_cards([
        ("✅", "Keldi", kel, "#10B981"),
        ("❌", "Kelmadi", kelma, "#EF4444"),
        ("⏳", "Belgilanmagan", belgisiz, "#F59E0B")
    ])

    if ADMIN and st.button("💾 Davomatni saqlash", type="primary", **KENG):
        natija = {
            safe_key(r["Ism"]): r["Holat"] == "Keldi"
            for r in tahrir.to_dict("records") if r["Holat"] != "—"
        }
        if fb_put(f"accounting/data/__davomat__/{sana}", natija):
            hammasi = dict(st.session_state.data.get("__davomat__") or {})
            hammasi[sana] = natija
            st.session_state.data["__davomat__"] = hammasi
            st.session_state.pop(boshl_kalit, None)
            eslat("✅ Davomat saqlandi!")
            st.rerun()
        else:
            st.error("⚠️ Bulutga yozib bo‘lmadi!")

    with st.expander("📆 Oylik davomat hisoboti"):
        oy_nom = st.selectbox("Oy", OYLAR, index=sana_d.month - 1, key="dv_oy")
        pref = f"{sana_d.year}-{OYLAR.index(oy_nom) + 1:02d}"
        hisob = {}
        for k, kunlar in (st.session_state.data.get("__davomat__") or {}).items():
            if str(k).startswith(pref) and isinstance(kunlar, dict):
                for nom, v in kunlar.items():
                    h = hisob.setdefault(nom, [0, 0])
                    h[0 if v is True else 1] += 1
        if hisob:
            rows = []
            for n, (a, b) in sorted(hisob.items()):
                fo = round(a / (a + b) * 100) if (a + b) else 0
                stil = "p-ok" if fo >= 80 else "p-warn" if fo >= 50 else "p-bad"
                rows.append([
                    f'<div class="cell-p">{avatar(n)}<span>{html.escape(n)}</span></div>',
                    f'<span class="num" style="color:#15803D">{a}</span>',
                    f'<span class="num" style="color:#DC2626">{b}</span>',
                    pill(f"{fo}%", stil)
                ])
            st.markdown(list_card(f"📆 {oy_nom} davomati",
                                  ["O‘quvchi", "Keldi", "Kelmadi", "Davomat %"], rows, 400),
                        unsafe_allow_html=True)
        else:
            st.info("Bu oy uchun davomat yo‘q")


# ------------------------------------------------------------
# 📊 TAQQOSLASH
# ------------------------------------------------------------
def sahifa_taqqoslash():
    topbar("📊 Sinflar taqqoslash", "Sinflar natijalari bir joyda")
    oy = st.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="t_oy")
    groups = {}
    for s in oy_ma(oy):
        groups.setdefault((s.get("cls") or "").strip() or "Sinfsiz", []).append(s)
    if not groups:
        st.info("Bu oyda ma’lumot yo‘q")
        return

    rows = []
    df_data = []
    for c, g in sorted(groups.items()):
        tushum = int(sum(num(s.get("price")) for s in g))
        qarz = int(sum(qarz(s) for s in g))
        fo = round(sum(1 for s in g if s.get("att", True)) / len(g) * 100)
        df_data.append({"Sinf": c, "O‘quvchi": len(g), "Tushum": tushum,
                        "Ovqat": int(sum(num(s.get("food")) for s in g)), "Qarz": qarz,
                        "Davomat %": fo})
        stil = "p-ok" if fo >= 80 else "p-warn" if fo >= 50 else "p-bad"
        rows.append([
            f'<div class="cell-p"><span class="cls-chip">🎓</span>'
            f'<span>{html.escape(c)}<div class="sub">{len(g)} ta o‘quvchi</div></span></div>',
            f'<span class="num">{fmt(tushum)}</span>',
            f'<span class="num" style="color:#DC2626">{fmt(qarz)}</span>',
            pill(f"{fo}%", stil)
        ])
    st.markdown(list_card(f"📊 {oy} — sinflar", ["Sinf", "Tushum", "Qarz", "Davomat %"], rows, 420),
                unsafe_allow_html=True)

    df = pd.DataFrame(df_data)
    with st.container(border=True):
        st.markdown("#### 📈 Grafik")
        st.bar_chart(df.set_index("Sinf")[["Tushum", "Qarz"]], color=["#2563EB", "#EF4444"])
    excel_tugma(df, oy, f"Taqqoslash_{oy}", "xl_taqq")


# ------------------------------------------------------------
# 🔴 QARZDORLAR
# ------------------------------------------------------------
def sahifa_qarzdorlar():
    topbar("🔴 Qarzdorlar", "Barcha oylar bo‘yicha")
    rows_data = [{
        "Oy": oy, "Ism": str(s.get("name")).strip(),
        "Sinf": (s.get("cls") or "").strip() or "—",
        "Sof": int(sof(s)), "To‘langan": int(num(s.get("paid"))),
        "Qarz": int(qarz(s))
    } for oy in OYLAR for s in oy_ma(oy) if s.get("name") and qarz(s) > 0]

    if not rows_data:
        st.success("🎉 Qarzdor yo‘q — hammasi to‘lagan!")
        return

    df = pd.DataFrame(rows_data)
    f1, f2, f3 = st.columns(3)
    oylar_f = f1.multiselect("📅 Oylar", OYLAR, default=[], placeholder="Barcha oylar")
    sinf_f = f2.selectbox("🎓 Sinf", ["Barchasi"] + sorted(df["Sinf"].unique()))
    qidir = f3.text_input("🔎 Ism bo‘yicha qidirish")

    if oylar_f:
        df = df[df["Oy"].isin(oylar_f)]
    if sinf_f != "Barchasi":
        df = df[df["Sinf"] == sinf_f]
    if qidir.strip():
        df = df[df["Ism"].str.lower().str.contains(qidir.strip().lower(), regex=False)]

    stat_cards([
        ("🔴", "Umumiy qarz", som(df["Qarz"].sum()), "#EF4444"),
        ("👥", "Qarzdor yozuvlar", len(df), "#F59E0B"),
        ("🧑", "Qarzdor o‘quvchilar", df["Ism"].nunique(), "#8B5CF6")
    ])

    t1, t2 = st.tabs(["📅 Oylar bo‘yicha", "🧑 O‘quvchilar bo‘yicha"])
    with t1:
        rows = [[
            f'<div class="cell-p">{avatar(r["Ism"])}<span>{html.escape(str(r["Ism"]))}'
            f'<div class="sub">{html.escape(str(r["Sinf"]))}</div></span></div>',
            pill(r["Oy"], "p-info"),
            f'<span class="num">{fmt(r["Sof"])}</span>',
            f'<span class="num" style="color:#15803D">{fmt(r["To‘langan"])}</span>',
            f'<span class="num" style="color:#DC2626">{fmt(r["Qarz"])}</span>'
        ] for r in df.to_dict("records")]
        st.markdown(list_card("🔴 Qarzdor yozuvlar",
                              ["O‘quvchi", "Oy", "Sof", "To‘langan", "Qarz"], rows, 430),
                    unsafe_allow_html=True)
    with t2:
        gr = (df.groupby("Ism", as_index=False)
              .agg(Sinf=("Sinf", "first"), Oylar=("Oy", "count"), Qarz=("Qarz", "sum"))
              .sort_values("Qarz", ascending=False))
        rows = [[
            f'<div class="cell-p">{avatar(r["Ism"])}<span>{html.escape(str(r["Ism"]))}'
            f'<div class="sub">{html.escape(str(r["Sinf"]))}</div></span></div>',
            f'<span class="num">{int(r["Oylar"])} oy</span>',
            f'<span class="num" style="color:#DC2626">{fmt(r["Qarz"])}</span>'
        ] for r in gr.to_dict("records")]
        st.markdown(list_card("🧑 O‘quvchilar kesimida",
                              ["O‘quvchi", "Necha oy", "Umumiy qarz"], rows, 430),
                    unsafe_allow_html=True)

    k1, k2 = st.columns(2)
    with k1:
        excel_tugma(df, "Qarzdorlar", "Qarzdorlar", "xl_qarz")
    with k2:
        if ADMIN and cfg.get("tgToken") and cfg.get("chatId"):
            if st.button("📨 Telegramga yuborish", **KENG):
                matn = "🔴 Qarzdorlar ro‘yxati\n" + "\n".join(
                    f"{r['Ism']} ({r['Oy']}) — {fmt(r['Qarz'])}"
                    for r in df.head(40).to_dict("records")
                )
                st.success("Yuborildi ✅") if tg_yubor(cfg, matn) else st.error("Yuborib bo‘lmadi")


# ------------------------------------------------------------
# 📈 YILLIK
# ------------------------------------------------------------
def sahifa_yillik():
    topbar("📈 Yillik hisobot", "12 oy natijalari")
    xarajatlar = royxat(oqi("accounting/expenses"))
    yillar = sorted(
        {str(x.get("date", ""))[:4] for x in xarajatlar if str(x.get("date", ""))[:4].isdigit()}
        | {str(date.today().year)}, reverse=True
    )
    yil = st.selectbox("📆 Xarajatlar yili", yillar)
    rows_data = []
    for i, oy in enumerate(OYLAR):
        mal = oy_ma(oy)
        tushum = sum(num(s.get("price")) for s in mal)
        cheg = sum(num(s.get("disc")) for s in mal)
        ovqat = sum(num(s.get("food")) for s in mal)
        xar = sum(
            num(x.get("amount")) for x in xarajatlar
            if str(x.get("date", ""))[:7] == f"{yil}-{i + 1:02d}"
        )
        rows_data.append({
            "Oy": oy, "O‘quvchi": len(mal),
            "Tushum": int(tushum), "Chegirma": int(cheg),
            "Ovqat": int(ovqat), "Xarajat": int(xar),
            "Sof foyda": int(tushum - cheg - ovqat - xar)
        })
    df = pd.DataFrame(rows_data)

    rows = []
    for r in df.to_dict("records"):
        foyda = r["Sof foyda"]
        rows.append([
            pill(r["Oy"], "p-info"),
            f'<span class="num">{int(r["O‘quvchi"])}</span>',
            f'<span class="num">{fmt(r["Tushum"])}</span>',
            f'<span class="num" style="color:#B45309">{fmt(r["Chegirma"])}</span>',
            f'<span class="num" style="color:#DC2626">{fmt(r["Ovqat"])}</span>',
            f'<span class="num" style="color:#DC2626">{fmt(r["Xarajat"])}</span>',
            pill(fmt(foyda), "p-ok" if foyda >= 0 else "p-bad")
        ])
    st.markdown(list_card(f"📈 {yil} — oylar kesimi",
                          ["Oy", "O‘quvchi", "Tushum", "Chegirma", "Ovqat", "Xarajat", "Sof foyda"],
                          rows, 430),
                unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("#### 📊 Grafik")
        oylik_grafik(df, ["Tushum", "Ovqat", "Xarajat", "Sof foyda"],
                     ["#2563EB", "#F59E0B", "#EF4444", "#10B981"])

    stat_cards([
        ("💰", "Yillik tushum", som(df["Tushum"].sum()), "#2563EB"),
        ("💸", "Xarajat", som(df["Xarajat"].sum()), "#F59E0B"),
        ("🏆", "Sof foyda", som(df["Sof foyda"].sum()), "#10B981")
    ])
    excel_tugma(df, "Yillik", "Yillik_hisobot", "xl_yil")


# ------------------------------------------------------------
# 🧾 TO‘LOVLAR
# ------------------------------------------------------------
TURLAR = ["💵 Naqd", "💳 Plastik", "🏦 O‘tkazma"]


def hisobga_yoz(oy, ism, summa):
    mal = oy_ma(oy)
    for s in mal:
        if str(s.get("name", "")).strip().lower() == ism.strip().lower():
            s["paid"] = num(s.get("paid")) + summa
            s["st"] = "st-paid" if s["paid"] >= sof(s) else "st-partial"
            return oy_saqla(oy, mal)
    return None


def sahifa_tolovlar():
    topbar("🧾 To‘lovlar jurnali", "To‘lovni yozing — xohlasangiz oylik hisobga ham avtomatik qo‘shiladi")
    payments = royxat(oqi("accounting/payments"))
    baza_nomlar = sorted({
        str(b.get("name")).strip()
        for b in royxat(oqi("accounting/students")) if b.get("name")
    })

    with st.form("tolov_forma", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        tanlov = c1.selectbox("O‘quvchi (bazadan)", [""] + baza_nomlar)
        qol = c2.text_input("…yoki ism yozing")
        summa = c3.number_input("Summa", min_value=0, step=10000, value=0)
        c4, c5, c6 = st.columns([1, 1, 2])
        turi = c4.selectbox("Turi", TURLAR)
        sana = c5.date_input("Sana", value=date.today())
        izoh = c6.text_input("Izoh (masalan: mart oyi)")
        c7, c8 = st.columns([2, 1])
        hisobga = c7.checkbox("Oylik hisobdagi «To‘langan» ustuniga ham qo‘shish", value=True)
        oy = c8.selectbox("Oy", OYLAR, index=sana.month - 1)
        yubor = st.form_submit_button("💾 Qayd etish", type="primary", disabled=not ADMIN, **KENG)

    if yubor:
        ism = (qol.strip() or tanlov).strip()
        if not ism or summa <= 0:
            st.warning("Ism va summani kiriting!")
        else:
            payments.insert(0, {
                "name": ism, "amount": summa, "type": turi,
                "date": str(sana), "note": izoh
            })
            if fb_put("accounting/payments", payments):
                msg = "✅ To‘lov saqlandi!"
                if hisobga:
                    r = hisobga_yoz(oy, ism, summa)
                    msg += (
                        f" {oy} hisobiga qo‘shildi." if r else
                        f" ⚠️ «{ism}» {oy} oyida topilmadi (hisobga yozilmadi)." if r is None else
                        " ⚠️ Hisobga yozib bo‘lmadi."
                    )
                eslat(msg)
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")

    if not payments:
        st.info("To‘lovlar yo‘q")
        return

    bu_oy = f"{date.today().year}-{date.today().month:02d}"
    stat_cards([
        ("💰", "Jami to‘lovlar", som(sum(num(p.get("amount")) for p in payments)), "#10B981"),
        ("📅", "Shu oy", som(sum(
            num(p.get("amount")) for p in payments
            if str(p.get("date", ""))[:7] == bu_oy
        )), "#2563EB"),
        ("🧾", "Yozuvlar soni", len(payments), "#F59E0B")
    ])

    with st.container(border=True):
        st.markdown("#### 🧾 Jurnal")
        st.caption("✏️ Qatorni tahrirlash yoki o‘chirish mumkin (o‘chirish: qatorni belgilab Delete).")
        df = pd.DataFrame([{
            "Sana": p.get("date", ""), "Ism": p.get("name", ""),
            "Summa": num(p.get("amount")), "Turi": p.get("type", TURLAR[0]),
            "Izoh": p.get("note", "")
        } for p in payments], columns=["Sana", "Ism", "Summa", "Turi", "Izoh"])
        tahrir = st.data_editor(
            df, hide_index=True,
            num_rows="dynamic" if ADMIN else "fixed",
            disabled=not ADMIN, **KENG,
            key=f"tolov_ed_{st.session_state.versiya}",
            column_config={
                "Summa": st.column_config.NumberColumn(step=10000, min_value=0),
                "Turi": st.column_config.SelectboxColumn(options=TURLAR)
            }
        )
        if ADMIN and st.button("💾 O‘zgarishlarni saqlash", key="tolov_saqla", **KENG):
            yangi = [{
                "date": str(r["Sana"] or date.today()),
                "name": str(r["Ism"]).strip(),
                "amount": num(r["Summa"]),
                "type": r["Turi"] if isinstance(r["Turi"], str) else TURLAR[0],
                "note": "" if pd.isna(r["Izoh"]) else str(r["Izoh"])
            } for r in tahrir.to_dict("records")
              if isinstance(r["Ism"], str) and r["Ism"].strip()]
            if fb_put("accounting/payments", yangi):
                eslat("✅ Saqlandi!")
                st.session_state.versiya += 1
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")
    excel_tugma(df, "Tolovlar", "Tolovlar", "xl_tolov")


# ------------------------------------------------------------
# 💸 XARAJATLAR
# ------------------------------------------------------------
def sahifa_xarajatlar():
    topbar("💸 Xarajatlar", "Gaz, svet, suv, ta’mirlash...")
    expenses = royxat(oqi("accounting/expenses"))
    with st.form("xar_forma", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nom = c1.text_input("Nima uchun?")
        summa = c2.number_input("Summa", min_value=0, step=10000, value=0)
        sana = c3.date_input("Sana", value=date.today())
        yubor = st.form_submit_button("💾 Qayd etish", type="primary", disabled=not ADMIN, **KENG)
    if yubor:
        if nom.strip() and summa > 0:
            expenses.insert(0, {"title": nom.strip(), "amount": summa, "date": str(sana)})
            if fb_put("accounting/expenses", expenses):
                eslat("✅ Saqlandi!")
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")
        else:
            st.warning("Maydonlarni to‘ldiring!")

    if not expenses:
        st.info("Xarajatlar yo‘q")
        return

    bu_oy = f"{date.today().year}-{date.today().month:02d}"
    stat_cards([
        ("💸", "Jami xarajat", som(sum(num(x.get("amount")) for x in expenses)), "#EF4444"),
        ("📅", "Shu oy", som(sum(
            num(x.get("amount")) for x in expenses
            if str(x.get("date", ""))[:7] == bu_oy
        )), "#F59E0B")
    ])

    df = pd.DataFrame([{
        "Sana": x.get("date", ""),
        "Nima uchun": x.get("title", ""),
        "Summa": num(x.get("amount"))
    } for x in expenses], columns=["Sana", "Nima uchun", "Summa"])

    with st.container(border=True):
        st.markdown("#### 🧾 Xarajatlar jurnali")
        tahrir = st.data_editor(
            df, hide_index=True,
            num_rows="dynamic" if ADMIN else "fixed",
            disabled=not ADMIN, **KENG,
            key=f"xar_ed_{st.session_state.versiya}",
            column_config={"Summa": st.column_config.NumberColumn(step=10000, min_value=0)}
        )
        if ADMIN and st.button("💾 O‘zgarishlarni saqlash", key="xar_saqla", **KENG):
            yangi = [{
                "date": str(r["Sana"] or date.today()),
                "title": str(r["Nima uchun"]).strip(),
                "amount": num(r["Summa"])
            } for r in tahrir.to_dict("records")
              if isinstance(r["Nima uchun"], str) and r["Nima uchun"].strip()]
            if fb_put("accounting/expenses", yangi):
                eslat("✅ Saqlandi!")
                st.session_state.versiya += 1
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")
    excel_tugma(df, "Xarajatlar", "Xarajatlar", "xl_xar")


# ------------------------------------------------------------
# 👨‍🎓 BAZA
# ------------------------------------------------------------
BAZA_USTUN = ["Ism", "Sinf", "Narx", "Telefon"]


def baza_df(bazalar):
    df = pd.DataFrame([{
        "Ism": b.get("name", ""), "Sinf": b.get("cls", ""),
        "Narx": num(b.get("price")), "Telefon": b.get("phone", "")
    } for b in bazalar], columns=BAZA_USTUN)
    return df.astype({"Narx": float})


def df_baza(df):
    out = []
    for r in df.to_dict("records"):
        ism = r["Ism"].strip() if isinstance(r["Ism"], str) else ""
        if ism:
            out.append({
                "name": ism,
                "cls": r["Sinf"].strip() if isinstance(r["Sinf"], str) else "",
                "price": num(r["Narx"]),
                "phone": r["Telefon"].strip() if isinstance(r["Telefon"], str) else ""
            })
    return out


def sahifa_baza():
    topbar("👨‍🎓 O‘quvchilar bazasi", "Bir marta kiritiladi — har oy ishlatiladi")
    bazalar = royxat(oqi("accounting/students"))

    with st.form("baza_forma", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        ism = c1.text_input("Ism Sharif")
        sinf = c2.text_input("Sinf (1-A)")
        narx = c3.number_input(
            "Oylik narx", min_value=0, step=10000,
            value=int(num(cfg.get("defaultPrice")))
        )
        tel = c4.text_input("Telefon")
        yubor = st.form_submit_button("➕ Qo‘shish", type="primary", disabled=not ADMIN, **KENG)

    if yubor:
        if not ism.strip():
            st.warning("Ismni kiriting!")
        elif any(
            str(b.get("name", "")).strip().lower() == ism.strip().lower()
            and str(b.get("cls", "")).strip().lower() == sinf.strip().lower()
            for b in bazalar
        ):
            st.warning("Bu o‘quvchi allaqachon bazada bor!")
        else:
            bazalar.append({
                "name": ism.strip(), "cls": sinf.strip(),
                "price": narx, "phone": tel.strip()
            })
            if fb_put("accounting/students", bazalar):
                eslat("✅ Qo‘shildi!")
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")

    if ADMIN:
        with st.expander("📤 Excel/CSV fayldan ommaviy yuklash"):
            st.caption("Ustunlar: Ism, Sinf, Narx, Telefon (birinchi qator — sarlavha).")
            fayl = st.file_uploader("Fayl", type=["xlsx", "csv"], label_visibility="collapsed")
            if fayl is not None and st.button("📥 Bazaga qo‘shish", key="imp"):
                try:
                    yuk = pd.read_csv(fayl) if fayl.name.endswith(".csv") else pd.read_excel(fayl)
                    yuk = yuk.rename(columns=lambda c: str(c).strip().capitalize())
                    for c in BAZA_USTUN:
                        if c not in yuk.columns:
                            yuk[c] = "" if c != "Narx" else 0
                    bor = {
                        (str(b.get("name", "")).strip().lower(), str(b.get("cls", "")).strip().lower())
                        for b in bazalar
                    }
                    yangi = [
                        b for b in df_baza(yuk[BAZA_USTUN])
                        if (b["name"].lower(), b["cls"].lower()) not in bor
                    ]
                    if yangi and fb_put("accounting/students", bazalar + yangi):
                        eslat(f"✅ {len(yangi)} ta o‘quvchi qo‘shildi")
                        st.rerun()
                    else:
                        st.info("Yangi o‘quvchi topilmadi yoki saqlab bo‘lmadi")
                except Exception as e:
                    st.error(f"Faylni o‘qib bo‘lmadi: {e}")

    if not bazalar:
        st.info("Baza bo‘sh")
        return

    df = baza_df(bazalar)
    stat_cards([
        ("👨‍🎓", "Bazadagi o‘quvchilar", len(df), "#2563EB"),
        ("🎓", "Sinflar soni", df["Sinf"].replace("", pd.NA).nunique(), "#8B5CF6")
    ])

    with st.container(border=True):
        st.markdown("#### 🗂 Baza jadvali")
        tahrir = st.data_editor(
            df, hide_index=True,
            num_rows="dynamic" if ADMIN else "fixed",
            disabled=not ADMIN, **KENG,
            key=f"baza_ed_{st.session_state.versiya}",
            column_config={"Narx": st.column_config.NumberColumn(step=10000, min_value=0)}
        )
        if ADMIN and st.button("💾 O‘zgarishlarni saqlash", key="baza_saqla", **KENG):
            if fb_put("accounting/students", df_baza(tahrir)):
                eslat("✅ Saqlandi!")
                st.session_state.versiya += 1
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")
    excel_tugma(df, "Baza", "Oquvchilar_bazasi", "xl_baza")


# ------------------------------------------------------------
# ⚙️ SOZLAMALAR
# ------------------------------------------------------------
def sahifa_sozlamalar():
    topbar("⚙️ Sozlamalar", "Akkaunt, muassasa va Telegram sozlamalari")
    if not ADMIN:
        st.warning("Faqat asosiy admin o‘zgartira oladi!")
        return

    with st.form("sozlama_forma"):
        st.markdown("**🔐 Asosiy akkaunt**")
        c1, c2 = st.columns(2)
        u1 = c1.text_input("Asosiy login", value=cfg.get("user", ""))
        p1 = c2.text_input(
            f"Yangi parol (bo‘sh = o‘zgarmaydi, kamida {MIN_PAROL} belgi)",
            type="password"
        )
        st.markdown("**👥 Ikkinchi akkaunt (o‘rinbosar)**")
        c1, c2, c3 = st.columns(3)
        u2 = c1.text_input("2-akkaunt login (bo‘sh = o‘chirilgan)", value=cfg.get("user2", ""))
        p2 = c2.text_input("2-akkaunt yangi paroli (bo‘sh = o‘zgarmaydi)", type="password")
        r2 = c3.selectbox(
            "Huquqi", ["view", "full"],
            format_func=lambda x: "👀 Faqat ko‘rish" if x == "view" else "🛠 To‘liq",
            index=1 if cfg.get("role2") == "full" else 0
        )

        st.markdown("**🏫 Muassasa**")
        c1, c2 = st.columns(2)
        org = c1.text_input("Muassasa nomi", value=cfg.get("orgName", ""))
        tel = c2.text_input("Telefon (parolni tiklash uchun)", value=cfg.get("phone", ""))
        c1, c2 = st.columns(2)
        narx = c1.number_input(
            "Standart oylik narx", min_value=0, step=10000,
            value=int(num(cfg.get("defaultPrice")))
        )
        reja = c2.number_input(
            "Oylik tushum rejasi", min_value=0, step=100000,
            value=int(num(cfg.get("monthlyPlan")))
        )

        st.markdown("**📨 Telegram**")
        c1, c2 = st.columns(2)
        tg = c1.text_input("Bot Token", value=cfg.get("tgToken", ""), type="password")
        ch = c2.text_input("Chat ID", value=cfg.get("chatId", ""))
        saqla = st.form_submit_button("💾 Saqlash", type="primary", **KENG)

    if saqla:
        xato = None
        if not u1.strip():
            xato = "Asosiy login bo‘sh bo‘lmasin."
        elif p1 and len(p1) < MIN_PAROL:
            xato = f"Parol kamida {MIN_PAROL} belgi bo‘lsin."
        elif u2.strip() and u2.strip() == u1.strip():
            xato = "Ikkala akkaunt logini bir xil bo‘lmasin."
        elif u2.strip() and not p2 and not cfg.get("pass2"):
            xato = "2-akkaunt uchun parol kiriting."
        elif p2 and len(p2) < MIN_PAROL:
            xato = f"2-akkaunt paroli kamida {MIN_PAROL} belgi bo‘lsin."
        if xato:
            st.error(xato)
        else:
            yangi = {
                **cfg,
                "user": u1.strip(), "user2": u2.strip(), "role2": r2,
                "orgName": org.strip(), "phone": tel.strip(),
                "defaultPrice": narx, "monthlyPlan": reja,
                "tgToken": tg.strip(), "chatId": ch.strip()
            }
            if p1:
                yangi["pass"] = hash_pw(p1)
            if p2:
                yangi["pass2"] = hash_pw(p2)
            if fb_put("accounting/config", yangi):
                st.session_state.cfg = yangi
                eslat("✅ Sozlamalar saqlandi!")
                st.rerun()
            else:
                st.error("⚠️ Bulutga yozib bo‘lmadi!")

    if ADMIN and cfg.get("tgToken") and cfg.get("chatId"):
        if st.button("📨 Test xabar yuborish", **KENG):
            ok = tg_yubor(cfg, f"✅ «{cfg.get('orgName', 'Maktab')}» buxgalteriyasi Telegram ulanishi ishlayapti!")
            (st.success("Test xabar yuborildi!") if ok else st.error("Yuborib bo‘lmadi!"))


# ------------------------------------------------------------
# 🧭 SIDEBAR NAVIGATSIYA
# ------------------------------------------------------------
SAHIFALAR = {
    "🏠 Dashboard": sahifa_dashboard,
    "💰 Hisob": sahifa_hisob,
    "🧾 To‘lovlar": sahifa_tolovlar,
    "📅 Davomat": sahifa_davomat,
    "🔴 Qarzdorlar": sahifa_qarzdorlar,
    "📊 Taqqoslash": sahifa_taqqoslash,
    "📈 Yillik hisobot": sahifa_yillik,
    "💸 Xarajatlar": sahifa_xarajatlar,
    "👨‍🎓 O‘quvchilar": sahifa_baza,
    "⚙️ Sozlamalar": sahifa_sozlamalar,
}

if st.session_state.get("flash"):
    st.success(st.session_state.pop("flash"))

with st.sidebar:
    st.markdown(f"""<div class="side-logo">
        <div class="lg">🏫</div>
        <div>
            <div class="tt">{html.escape(cfg.get("orgName", "Maktab"))}</div>
            <div class="ss">Admin Panel</div>
        </div>
    </div>""", unsafe_allow_html=True)

    try:
        _reja = num(cfg.get("monthlyPlan"))
        if _reja > 0:
            _oy = OYLAR[datetime.now().month - 1]
            _yig = sum(sof(s) - qarz(s) for s in oy_ma(_oy))
            st.markdown(plan_html(_oy, _yig, _reja), unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown('<div class="side-cap">Menyu</div>', unsafe_allow_html=True)
    tanlangan = st.radio("Bo‘lim", list(SAHIFALAR), label_visibility="collapsed", key="nav")

    st.markdown("---")

    st.markdown(f"""<div class="user-card">
        <div class="av">{"👑" if ADMIN else "👀"}</div>
        <div>
            <div class="nm">{html.escape(str(cfg.get("user", "admin")))}</div>
            <div class="rl">{"Asosiy admin" if ADMIN else "Ko‘rish rejimi"}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    if b1.button("🔄", help="Bulutdan yangilash", **KENG):
        bulutdan_yukla()
        st.session_state.versiya += 1
        st.rerun()
    if b2.button("🚪 Chiqish", **KENG):
        st.session_state.clear()
        st.rerun()

SAHIFALAR[tanlangan]()
