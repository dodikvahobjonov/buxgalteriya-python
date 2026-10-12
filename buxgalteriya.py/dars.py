# -*- coding: utf-8 -*-
# ============================================================
#  ☁️ MAKTAB BUXGALTERIYA — PRO (yaxshilangan versiya)
# ============================================================
import hashlib
import hmac
import html
import io
import json
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

st.set_page_config(page_title="Maktab Buxgalteriya", page_icon="☁️", layout="wide")

try:
    _v = tuple(int(x) for x in re.findall(r"\d+", st.__version__)[:2])
except Exception:
    _v = (1, 0)
KENG = {"width": "stretch"} if _v >= (1, 50) else {"use_container_width": True}

# ------------------------------------------------------------
# DIZAYN (CSS) — yaxshilangan
# ------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: #0b1120;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111a2e 0%, #0b1120 100%);
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    #MainMenu, footer, .stDeployButton { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.1rem; max-width: 1280px; }

    .hero {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #9333ea 100%);
        border-radius: 20px;
        padding: 24px 28px;
        color: #fff;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 28px rgba(79,70,229,.32);
    }
    .hero::after {
        content:'';
        position:absolute; right:-40px; top:-50px;
        width:200px; height:200px;
        background:rgba(255,255,255,.1);
        border-radius:50%;
    }
    .hero h1 {
        margin:0; font-size:24px; font-weight:800;
        color:#fff !important; letter-spacing:-0.3px;
    }
    .hero p { margin:5px 0 0; opacity:.88; font-size:13.5px; }

    .stats-row {
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(145px,1fr));
        gap:12px; margin:14px 0 18px;
    }
    .stat-card {
        background: linear-gradient(145deg,#151e31,#101828);
        border: 1px solid #253048;
        border-radius: 16px;
        padding: 14px 16px;
        position: relative;
        transition: transform .15s ease;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-card::before {
        content:'';
        position:absolute; top:0; left:0; right:0;
        height:3px; border-radius:16px 16px 0 0;
        background: var(--ac,#6366f1);
    }
    .stat-card .lbl { font-size:11.5px; color:#94a3b8; font-weight:600; }
    .stat-card .val { font-size:20px; font-weight:800; color:#f1f5f9; margin-top:3px; }

    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        border-radius: 11px; font-weight: 700;
        border: 1px solid #253048;
        background: #151e31; color: #f1f5f9;
        transition: .18s;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px); border-color:#6366f1;
    }
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        border: none; color:#fff;
    }

    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        background: #101828 !important;
        border: 1px solid #253048 !important;
        border-radius: 11px !important;
        color: #f1f5f9 !important;
    }
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        border: 1px solid #253048;
        border-radius: 14px;
        overflow: hidden;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg,#151e31,#101828);
        border: 1px solid #253048;
        border-radius: 14px;
        padding: 12px 16px;
    }
    div[data-testid="stForm"] {
        border: 1px solid #253048;
        border-radius: 14px;
        background:#0f1626;
        padding: 8px 12px 4px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 11px;
        background:#151e31;
        border:1px solid #253048;
        font-weight:700;
        padding: 7px 14px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
        color:#fff !important;
    }
    h1, h2, h3 { color: #f1f5f9 !important; font-weight: 800 !important; }

    @media (max-width: 640px) {
        .hero { padding: 16px 16px; border-radius: 16px; }
        .hero h1 { font-size: 19px; }
        .stat-card .val { font-size: 17px; }
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
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
        st.error("☁️ Bulutga ulanib bo‘lmadi. Internetni tekshiring va «🔄 Bulutdan yangilash»ni bosing.")
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
def hero(sarlavha, ostki=""):
    st.markdown(
        f"""<div class="hero"><h1>{html.escape(sarlavha)}</h1>
        <p>{html.escape(ostki)}</p></div>""",
        unsafe_allow_html=True
    )


def stat_cards(kartalar):
    h = '<div class="stats-row">'
    for icon, nom, qiymat, rang in kartalar:
        h += f"""<div class="stat-card" style="--ac:{rang}">
            <div class="lbl">{icon} {html.escape(str(nom))}</div>
            <div class="val">{html.escape(str(qiymat))}</div></div>"""
    h += "</div>"
    st.markdown(h, unsafe_allow_html=True)


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
        ).properties(height=300)
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
    <div style="text-align:center; padding:24px 0 10px;">
        <div style="font-size:52px;">☁️</div>
        <h1 style="margin:0; background:linear-gradient(90deg,#a5b4fc,#f0abfc);
        -webkit-background-clip:text; background-clip:text; color:transparent;
        font-size:28px; font-weight:800;">
        Cloud Buxgalteriya</h1>
        <p style="color:#94a3b8; margin-top:4px;">Talabalar hisob-kitobi tizimi</p>
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
    hero("👋 Xush kelibsiz!", f"{cfg.get('orgName', 'Maktab')} — barcha hisoblar bir joyda")
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
        ("👥", "O‘quvchi yozuvlari", len(barcha), "#6366f1"),
        ("💰", "Umumiy tushum", som(jami_t), "#10b981"),
        ("🔴", "Umumiy qarz", som(jami_q), "#ef4444"),
        ("📈", "Undirish darajasi", f"{foiz}%", "#8b5cf6"),
        ("📚", "To‘ldirilgan oylar", f"{sum(1 for m in hamma.values() if m)}/12", "#f59e0b"),
    ])

    reja = num(cfg.get("monthlyPlan"))
    if reja > 0:
        joriy_oy = OYLAR[datetime.now().month - 1]
        yigildi = sum(sof(s) - qarz(s) for s in hamma[joriy_oy])
        st.caption(f"🎯 {joriy_oy} rejasi: {som(yigildi)} / {som(reja)}")
        st.progress(min(max(yigildi / reja, 0.0), 1.0))

    if barcha:
        grafik_df = pd.DataFrame([{
            "Oy": oy,
            "Tushum": sum(num(s.get("price")) for s in m),
            "Qarz": sum(qarz(s) for s in m)
        } for oy, m in hamma.items()])
        st.markdown("#### 📊 Oylar kesimida")
        oylik_grafik(grafik_df, ["Tushum", "Qarz"], ["#6366f1", "#ef4444"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🔴 Eng katta qarzdorlar")
        qd = {}
        for m in hamma.values():
            for s in m:
                q = qarz(s)
                nom = str(s.get("name") or "").strip()
                if q > 0 and nom:
                    qd[nom] = qd.get(nom, 0) + q
        top = sorted(qd.items(), key=lambda x: -x[1])[:5]
        if top:
            st.dataframe(
                pd.DataFrame([{"Ism": n, "Qarz": fmt(q)} for n, q in top]),
                hide_index=True, **KENG
            )
        else:
            st.success("Qarzdor yo‘q 🎉")
    with c2:
        st.markdown("#### 🧾 So‘nggi to‘lovlar")
        tol = royxat(oqi("accounting/payments"))[:5]
        if tol:
            st.dataframe(
                pd.DataFrame([{
                    "Sana": p.get("date", ""),
                    "Ism": p.get("name", ""),
                    "Summa": fmt(p.get("amount"))
                } for p in tol]),
                hide_index=True, **KENG
            )
        else:
            st.info("To‘lovlar yo‘q")
    with c3:
        st.markdown("#### 📅 Bugungi davomat")
        dav = (st.session_state.data.get("__davomat__") or {}).get(str(date.today())) or {}
        kel = sum(1 for v in dav.values() if v is True)
        kelma = sum(1 for v in dav.values() if v is False)
        if dav:
            stat_cards([("✅", "Keldi", kel, "#10b981"), ("❌", "Kelmadi", kelma, "#ef4444")])
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
    hero("💰 Hisob", "Jadvalni tahrirlang va «Bulutga saqlash»ni bosing")
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
            ("💰", "Tushum", fmt(sum(num(s["price"]) for s in joriy)), "#6366f1"),
            ("🎗", "Chegirma", fmt(sum(num(s["disc"]) for s in joriy)), "#f59e0b"),
            ("🍽", "Ovqat", fmt(sum(num(s["food"]) for s in joriy)), "#ef4444"),
            ("✅", "Sof foyda", fmt(sum(sof(s) for s in joriy)), "#10b981"),
            ("👥", "O‘quvchi", len(joriy), "#8b5cf6"),
            ("🔴", "Qarz", fmt(sum(qarz(s) for s in joriy)), "#ef4444"),
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
    hero("📅 Kunlik davomat", "Har kuni kim kelganini belgilang")
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
        ("✅", "Keldi", kel, "#10b981"),
        ("❌", "Kelmadi", kelma, "#ef4444"),
        ("⏳", "Belgilanmagan", belgisiz, "#f59e0b")
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
            st.dataframe(pd.DataFrame([{
                "Ism": n, "Keldi": a, "Kelmadi": b,
                "Davomat %": round(a / (a + b) * 100) if (a + b) else 0
            } for n, (a, b) in sorted(hisob.items())]), hide_index=True, **KENG)
        else:
            st.info("Bu oy uchun davomat yo‘q")


# ------------------------------------------------------------
# 📊 TAQQOSLASH
# ------------------------------------------------------------
def sahifa_taqqoslash():
    hero("📊 Sinflar taqqoslash")
    oy = st.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="t_oy")
    groups = {}
    for s in oy_ma(oy):
        groups.setdefault((s.get("cls") or "").strip() or "Sinfsiz", []).append(s)
    if not groups:
        st.info("Bu oyda ma’lumot yo‘q")
        return
    df = pd.DataFrame([{
        "Sinf": c, "O‘quvchi": len(g),
        "Tushum": int(sum(num(s.get("price")) for s in g)),
        "Ovqat": int(sum(num(s.get("food")) for s in g)),
        "Qarz": int(sum(qarz(s) for s in g)),
        "Davomat %": round(sum(1 for s in g if s.get("att", True)) / len(g) * 100)
    } for c, g in sorted(groups.items())])
    st.dataframe(df, hide_index=True, **KENG)
    st.bar_chart(df.set_index("Sinf")[["Tushum", "Qarz"]], color=["#6366f1", "#ef4444"])
    excel_tugma(df, oy, f"Taqqoslash_{oy}", "xl_taqq")


# ------------------------------------------------------------
# 🔴 QARZDORLAR
# ------------------------------------------------------------
def sahifa_qarzdorlar():
    hero("🔴 Qarzdorlar", "Barcha oylar bo‘yicha")
    rows = [{
        "Oy": oy, "Ism": str(s.get("name")).strip(),
        "Sinf": (s.get("cls") or "").strip() or "—",
        "Sof": int(sof(s)), "To‘langan": int(num(s.get("paid"))),
        "Qarz": int(qarz(s))
    } for oy in OYLAR for s in oy_ma(oy) if s.get("name") and qarz(s) > 0]

    if not rows:
        st.success("🎉 Qarzdor yo‘q — hammasi to‘lagan!")
        return

    df = pd.DataFrame(rows)
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
        ("🔴", "Umumiy qarz", som(df["Qarz"].sum()), "#ef4444"),
        ("👥", "Qarzdor yozuvlar", len(df), "#f59e0b"),
        ("🧑", "Qarzdor o‘quvchilar", df["Ism"].nunique(), "#8b5cf6")
    ])

    t1, t2 = st.tabs(["📅 Oylar bo‘yicha", "🧑 O‘quvchilar bo‘yicha"])
    with t1:
        st.dataframe(
            df, hide_index=True, **KENG,
            column_config={"Qarz": st.column_config.NumberColumn(format="%d")}
        )
    with t2:
        gr = (df.groupby("Ism", as_index=False)
              .agg(Sinf=("Sinf", "first"), Oylar=("Oy", "count"), Qarz=("Qarz", "sum"))
              .sort_values("Qarz", ascending=False))
        st.dataframe(gr, hide_index=True, **KENG)

    k1, k2 = st.columns(2)
    with k1:
        excel_tugma(df, "Qarzdorlar", "Qarzdorlar", "xl_qarz")
    with k2:
        if ADMIN and cfg.get("tgToken") and cfg.get("chatId"):
            if st.button("📨 Telegramga yuborish", **KENG):
                matn = "🔴 Qarzdorlar ro‘yxati\n" + "\n".join(
                    f"{r.Ism} ({r.Oy}) — {fmt(r.Qarz)}" for r in df.head(40).itertuples()
                )
                st.success("Yuborildi ✅") if tg_yubor(cfg, matn) else st.error("Yuborib bo‘lmadi")


# ------------------------------------------------------------
# 📈 YILLIK
# ------------------------------------------------------------
def sahifa_yillik():
    hero("📈 Yillik hisobot", "12 oy natijalari")
    xarajatlar = royxat(oqi("accounting/expenses"))
    yillar = sorted(
        {str(x.get("date", ""))[:4] for x in xarajatlar if str(x.get("date", ""))[:4].isdigit()}
        | {str(date.today().year)}, reverse=True
    )
    yil = st.selectbox("📆 Xarajatlar yili", yillar)
    rows = []
    for i, oy in enumerate(OYLAR):
        mal = oy_ma(oy)
        tushum = sum(num(s.get("price")) for s in mal)
        cheg = sum(num(s.get("disc")) for s in mal)
        ovqat = sum(num(s.get("food")) for s in mal)
        xar = sum(
            num(x.get("amount")) for x in xarajatlar
            if str(x.get("date", ""))[:7] == f"{yil}-{i + 1:02d}"
        )
        rows.append({
            "Oy": oy, "O‘quvchi": len(mal),
            "Tushum": int(tushum), "Chegirma": int(cheg),
            "Ovqat": int(ovqat), "Xarajat": int(xar),
            "Sof foyda": int(tushum - cheg - ovqat - xar)
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, **KENG)
    oylik_grafik(df, ["Tushum", "Ovqat", "Xarajat", "Sof foyda"],
                 ["#6366f1", "#f59e0b", "#ef4444", "#10b981"])
    stat_cards([
        ("💰", "Yillik tushum", som(df["Tushum"].sum()), "#6366f1"),
        ("💸", "Xarajat", som(df["Xarajat"].sum()), "#f59e0b"),
        ("🏆", "Sof foyda", som(df["Sof foyda"].sum()), "#10b981")
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
    hero("🧾 To‘lovlar jurnali", "To‘lovni yozing — xohlasangiz oylik hisobga ham avtomatik qo‘shiladi")
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
        ("💰", "Jami to‘lovlar", som(sum(num(p.get("amount")) for p in payments)), "#10b981"),
        ("📅", "Shu oy", som(sum(
            num(p.get("amount")) for p in payments
            if str(p.get("date", ""))[:7] == bu_oy
        )), "#6366f1"),
        ("🧾", "Yozuvlar soni", len(payments), "#f59e0b")
    ])

    df = pd.DataFrame([{
        "Sana": p.get("date", ""), "Ism": p.get("name", ""),
        "Summa": num(p.get("amount")), "Turi": p.get("type", TURLAR[0]),
        "Izoh": p.get("note", "")
    } for p in payments], columns=["Sana", "Ism", "Summa", "Turi", "Izoh"])

    st.caption("✏️ Qatorni tahrirlash yoki o‘chirish mumkin (o‘chirish: qatorni belgilab Delete).")
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
    hero("💸 Xarajatlar", "Gaz, svet, suv, ta’mirlash...")
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
        ("💸", "Jami xarajat", som(sum(num(x.get("amount")) for x in expenses)), "#ef4444"),
        ("📅", "Shu oy", som(sum(
            num(x.get("amount")) for x in expenses
            if str(x.get("date", ""))[:7] == bu_oy
        )), "#f59e0b")
    ])

    df = pd.DataFrame([{
        "Sana": x.get("date", ""),
        "Nima uchun": x.get("title", ""),
        "Summa": num(x.get("amount"))
    } for x in expenses], columns=["Sana", "Nima uchun", "Summa"])

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
    hero("👨‍🎓 O‘quvchilar bazasi", "Bir marta kiritiladi — har oy ishlatiladi")
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
        ("👨‍🎓", "Bazadagi o‘quvchilar", len(df), "#6366f1"),
        ("🎓", "Sinflar soni", df["Sinf"].replace("", pd.NA).nunique(), "#8b5cf6")
    ])
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
    hero("⚙️ Sozlamalar")
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
        r2 = c3.selectbox("Huquqi", ["view", "full"], index=1 if cfg.get("role2") == "full" else 0)

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
                "user": u1.strip(),
                "pass": hash_pw(p1) if p1 else cfg.get("pass", ""),
                "user2": u2.strip(),
                "pass2": hash_pw(p2) if p2 else cfg.get("pass2", ""),
                "role2": r2,
                "orgName": org.strip() or "Maktab",
                "phone": tel.strip(),
                "tgToken": tg.strip(),
                "chatId": ch.strip(),
                "defaultPrice": narx,
                "monthlyPlan": reja
            }
            if not u2.strip():
                yangi["pass2"] = ""
            if fb_put("accounting/config", yangi):
                st.session_state.cfg = yangi
                if p1:
                    st.session_state.standart_parol = False
                st.success("✅ Saqlandi!")
            else:
                st.error("Bulutga yozib bo‘lmadi!")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📨 Telegramni sinash", **KENG):
            st.success("Xabar yuborildi ✅") if tg_yubor(cfg, "✅ Maktab Buxgalteriya: test xabari") \
                else st.error("Yuborib bo‘lmadi — token va chat ID ni tekshiring.")
    with c2:
        zaxira = {
            "data": st.session_state.data,
            "students": oqi("accounting/students", yangi=True),
            "payments": oqi("accounting/payments", yangi=True),
            "expenses": oqi("accounting/expenses", yangi=True)
        }
        st.download_button(
            "💾 To‘liq zaxira nusxa (JSON)",
            json.dumps(zaxira, ensure_ascii=False, indent=1).encode("utf-8"),
            file_name=f"zaxira_{date.today()}.json",
            mime="application/json", **KENG
        )


# ------------------------------------------------------------
# SIDEBAR + YO‘NALTIRISH
# ------------------------------------------------------------
SAHIFALAR = {
    "🏠 Dashboard": sahifa_dashboard,
    "💰 Hisob": sahifa_hisob,
    "📅 Kunlik davomat": sahifa_davomat,
    "📊 Taqqoslash": sahifa_taqqoslash,
    "🔴 Qarzdorlar": sahifa_qarzdorlar,
    "📈 Yillik": sahifa_yillik,
    "🧾 To‘lovlar": sahifa_tolovlar,
    "💸 Xarajatlar": sahifa_xarajatlar,
    "👨‍🎓 Baza": sahifa_baza,
    "⚙️ Sozlamalar": sahifa_sozlamalar,
}

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:8px 0 16px;">
        <div style="font-size:38px;">☁️</div>
        <div style="font-weight:800; font-size:15px; color:#fff;">
            {html.escape(cfg.get('orgName', 'Maktab'))}
        </div>
        <div style="font-size:11px; color:#64748b;">
            {'Admin' if ADMIN else 'Faqat ko‘rish'} rejimi
        </div>
    </div>""", unsafe_allow_html=True)

    sahifa = st.radio("Bo‘lim", list(SAHIFALAR), label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 Bulutdan yangilash", **KENG):
        _kesh_oqi.clear()
        bulutdan_yukla()
        st.session_state.versiya += 1
        st.rerun()
    if st.button("🚪 Chiqish", **KENG):
        st.session_state.clear()
        st.rerun()
    st.caption("Python + Streamlit 💛")

if st.session_state.get("flash"):
    st.toast(st.session_state.pop("flash"))

SAHIFALAR[sahifa]()
