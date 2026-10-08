# ============================================================
#  ☁️ MAKTAB BUXGALTERIYA — PREMIUM DIZAYN (Python/Streamlit)
# ============================================================

import io
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

DB_URL = "https://maktab-buxgalteriya-default-rtdb.firebaseio.com"
OYLAR = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
         "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
STANDART = {"user": "admin", "pass": "123", "user2": "", "pass2": "",
            "orgName": "Maktab", "phone": "+998", "tgToken": "", "chatId": "",
            "defaultPrice": 0, "monthlyPlan": 0}

st.set_page_config(page_title="Maktab Buxgalteriya", page_icon="☁️", layout="wide")

# ================== PREMIUM DIZAYN (CSS) ==================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    /* Umumiy fon va shrift */
    .stApp { background: #0b1120; font-family: 'Plus Jakarta Sans', sans-serif; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111a2e 0%, #0b1120 100%);
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    /* Streamlit standart elementlarini yashirish */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.2rem; max-width: 1300px; }

    /* Gradient banner */
    .hero {
        background: linear-gradient(135deg, #4f46e5, #7c3aed 60%, #9333ea);
        border-radius: 22px; padding: 26px 30px; color: #fff;
        margin-bottom: 18px; position: relative; overflow: hidden;
        box-shadow: 0 12px 30px rgba(79,70,229,.35);
    }
    .hero::after { content:''; position:absolute; right:-50px; top:-60px;
        width:220px; height:220px; background:rgba(255,255,255,.12); border-radius:50%; }
    .hero h1 { margin:0; font-size:26px; font-weight:800; }
    .hero p { margin:6px 0 0; opacity:.85; font-size:14px; }

    /* Statistika kartalar */
    .stats-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
        gap:12px; margin:16px 0; }
    .stat-card {
        background: linear-gradient(145deg,#151e31,#101828);
        border: 1px solid #253048; border-radius: 18px;
        padding: 16px 18px; position: relative;
    }
    .stat-card::before { content:''; position:absolute; top:0; left:0; right:0;
        height:4px; border-radius:18px 18px 0 0; background: var(--ac,#6366f1); }
    .stat-card .lbl { font-size:12px; color:#94a3b8; font-weight:600; }
    .stat-card .val { font-size:22px; font-weight:800; color:#f1f5f9; margin-top:4px; }

    /* Tugmalar */
    .stButton > button {
        border-radius: 12px; font-weight: 700; border: 1px solid #253048;
        background: #151e31; color: #f1f5f9; transition: .2s;
    }
    .stButton > button:hover { transform: translateY(-2px); border-color:#6366f1; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#6366f1,#8b5cf6); border: none; color:#fff;
    }

    /* Inputlar va jadvallar */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background: #101828 !important; border: 1px solid #253048 !important;
        border-radius: 12px !important; color: #f1f5f9 !important;
    }
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        border: 1px solid #253048; border-radius: 16px; overflow: hidden;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg,#151e31,#101828);
        border: 1px solid #253048; border-radius: 16px; padding: 14px 18px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px; background:#151e31; border:1px solid #253048;
        font-weight:700; padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#6366f1,#8b5cf6); color:#fff !important;
    }
    h1, h2, h3 { color: #f1f5f9 !important; font-weight: 800 !important; }
    .stInfo, .stSuccess, .stWarning, .stError { border-radius: 14px; }
</style>
""", unsafe_allow_html=True)

# ================== FIREBASE ==================

def fb_get(yol):
    try:
        r = requests.get(f"{DB_URL}/{yol}.json", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def fb_put(yol, qiymat):
    try:
        r = requests.put(f"{DB_URL}/{yol}.json", json=qiymat, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def royxat(v):
    if not v:
        return []
    if isinstance(v, list):
        return [x for x in v if x]
    return [x for x in v.values() if x]

def sof(s):
    return (+s.get("price", 0) or 0) - (+s.get("disc", 0) or 0) - (+s.get("food", 0) or 0)

def holat_uz(kod):
    return {"st-paid": "TO'LANDI", "st-partial": "QISMAN"}.get(kod, "QARZ")

def holat_kod(uz):
    return {"TO'LANDI": "st-paid", "QISMAN": "st-partial"}.get(uz, "QARZ")

# ================== DIZAYN KOMPONENTLARI ==================

def hero(sarlavha, ostki=""):
    st.markdown(f"""<div class="hero"><h1>{sarlavha}</h1>
        <p>{ostki}</p></div>""", unsafe_allow_html=True)

def stat_cards(kartalar):
    """kartalar: [(ikonka, nom, qiymat, rang), ...]"""
    html = '<div class="stats-row">'
    for icon, nom, qiymat, rang in kartalar:
        html += f"""<div class="stat-card" style="--ac:{rang}">
            <div class="lbl">{icon} {nom}</div>
            <div class="val">{qiymat}</div></div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ================== SESSION ==================
if "kirgan" not in st.session_state:
    st.session_state.kirgan = False
    st.session_state.roll = "admin"
    st.session_state.data = {}
    st.session_state.yuklandi = False
    st.session_state.versiya = 0
    st.session_state.cfg = dict(STANDART)

def bulutdan_yukla():
    st.session_state.data = fb_get("accounting/data") or {}
    st.session_state.yuklandi = True

def bulutga_saqla():
    if fb_put("accounting/data", st.session_state.data):
        st.toast("✅ Bulutga saqlandi!")
    else:
        st.toast("⚠️ Bulutga yozib bo'lmadi!", icon="⚠️")

def oy_ma(oy):
    return royxat(st.session_state.data.get(oy))

# ================== CHIROYLI KIRISH ==================
if not st.session_state.kirgan:
    st.markdown("""<div style="text-align:center; padding:20px 0 8px;">
        <div style="font-size:56px;">☁️</div>
        <h1 style="margin:0; background:linear-gradient(90deg,#a5b4fc,#f0abfc);
        -webkit-background-clip:text; background-clip:text; color:transparent;">
        Cloud Buxgalteriya</h1>
        <p style="color:#94a3b8;">Talabalar hisob-kitobi tizimi — Python versiya</p></div>""",
        unsafe_allow_html=True)
    _, c, _ = st.columns([1.5, 2, 1.5])
    with c:
        u = st.text_input("👤 Login", key="lg_u")
        p = st.text_input("🔒 Parol", type="password", key="lg_p")
        if st.button("🚀 Kirish", use_container_width=True, type="primary"):
            cfg = {**STANDART, **(fb_get("accounting/config") or {})}
            st.session_state.cfg = cfg
            if u.strip() == cfg["user"] and p == cfg["pass"]:
                st.session_state.kirgan, st.session_state.roll = True, "admin"
                st.rerun()
            elif cfg.get("user2") and u.strip() == cfg["user2"] and p == cfg.get("pass2", ""):
                st.session_state.kirgan = True
                st.session_state.roll = "admin" if cfg.get("role2") == "full" else "view"
                st.rerun()
            else:
                st.error("Login yoki parol xato! (Standart: admin / 123)")
        with st.expander("❓ Parolni unutdim"):
            tel = st.text_input("Telefon raqamingiz", key="rec")
            if st.button("Parolni ko'rish"):
                cfg = {**STANDART, **(fb_get("accounting/config") or {})}
                if tel.strip() and tel.strip() == (cfg.get("phone") or ""):
                    st.info(f"Login: {cfg['user']} | Parol: {cfg['pass']}")
                else:
                    st.error("Bu raqam ro'yxatda yo'q!")
    st.stop()

if not st.session_state.yuklandi:
    st.session_state.cfg = {**STANDART, **(fb_get("accounting/config") or {})}
    bulutdan_yukla()

cfg = st.session_state.cfg
ADMIN = st.session_state.roll == "admin"

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:8px 0 16px;">
        <div style="font-size:40px;">☁️</div>
        <div style="font-weight:800; font-size:16px; color:#fff;">Maktab Pro</div>
        <div style="font-size:11px; color:#64748b;">Python versiya</div></div>""",
        unsafe_allow_html=True)
    sahifa = st.radio("Bo'lim", [
        "🏠 Dashboard", "💰 Hisob", "📅 Kunlik davomat", "📊 Taqqoslash",
        "🔴 Qarzdorlar", "📈 Yillik", "🧾 To'lovlar", "💸 Xarajatlar",
        "👨‍🎓 Baza", "⚙️ Sozlamalar"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 Bulutdan yangilash", use_container_width=True):
        bulutdan_yukla()
        st.session_state.versiya += 1
        st.rerun()
    if st.button("🚪 Chiqish", use_container_width=True):
        st.session_state.kirgan = False
        st.rerun()
    st.caption("Python + Streamlit 💛")

# ================== 🏠 DASHBOARD ==================
if sahifa == "🏠 Dashboard":
    hero("👋 Xush kelibsiz!", f"{cfg.get('orgName','Maktab')} — barcha hisoblar bir joyda")
    jami_o = sum(len(oy_ma(oy)) for oy in OYLAR)
    jami_t = sum((+s.get("price", 0) or 0) for oy in OYLAR for s in oy_ma(oy))
    jami_q = sum(max(sof(s), 0) for oy in OYLAR for s in oy_ma(oy)
                 if s.get("st") == "st-debt")
    stat_cards([
        ("👥", "O'quvchi yozuvlari", jami_o, "#6366f1"),
        ("💰", "Umumiy tushum", f"{int(jami_t):,} so'm".replace(",", " "), "#10b981"),
        ("🔴", "Umumiy qarz", f"{int(jami_q):,} so'm".replace(",", " "), "#ef4444"),
        ("📚", "Oylar", f"{sum(1 for oy in OYLAR if oy_ma(oy))}/12", "#f59e0b"),
    ])
    if not ADMIN:
        st.info("👀 Siz faqat ko'rish rejimidasiz")

# ================== 💰 HISOB ==================
elif sahifa == "💰 Hisob":
    hero("💰 Hisob", "Jadvalni tahrirlang va «Saqlash»ni bosing")
    oy = st.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="h_oy")
    cls_f = st.text_input("🎓 Sinf filtri (bo'sh = barchasi)", key="h_cls")

    mal = oy_ma(oy)
    df = pd.DataFrame([{
        "Ism": str(s.get("name") or ""), "Sinf": str(s.get("cls") or ""),
        "Narx": float(s.get("price") or 0), "Chegirma": float(s.get("disc") or 0),
        "Ovqat": float(s.get("food") or 0), "Holat": holat_uz(s.get("st")),
        "Keldi": bool(s.get("att", True)),
    } for s in mal])
    if cls_f.strip():
        df = df[df["Sinf"].str.strip() == cls_f.strip()]

    tahrir = st.data_editor(df, num_rows="dynamic" if ADMIN else "fixed",
        hide_index=True, use_container_width=True,
        column_config={
            "Ism": st.column_config.TextColumn("👤 Ism", width="large"),
            "Narx": st.column_config.NumberColumn("💰 Narx", step=1000),
            "Chegirma": st.column_config.NumberColumn("🎗 Chegirma", step=1000),
            "Ovqat": st.column_config.NumberColumn("🍽 Ovqat", step=1000),
            "Holat": st.column_config.SelectboxColumn("Holat", options=["QARZ", "QISMAN", "TO'LANDI"]),
            "Keldi": st.column_config.CheckboxColumn("✅ Keldi"),
        }, key=f"jadval_{oy}_{st.session_state.versiya}")

    if ADMIN and st.button("💾 Bulutga saqlash", type="primary", use_container_width=True):
        taza = tahrir.fillna({"Ism": "", "Sinf": "", "Narx": 0, "Chegirma": 0, "Ovqat": 0, "Holat": "QARZ"})
        taza["Keldi"] = taza["Keldi"].fillna(True)
        st.session_state.data[oy] = [{
            "name": str(r["Ism"]), "cls": str(r["Sinf"]), "price": float(r["Narx"]),
            "disc": float(r["Chegirma"]), "food": float(r["Ovqat"]),
            "st": holat_kod(r["Holat"]), "att": bool(r["Keldi"]),
        } for _, r in taza.iterrows()]
        bulutga_saqla()

    if not tahrir.empty:
        t = tahrir.fillna({"Narx": 0, "Chegirma": 0, "Ovqat": 0})
        sof_s = t["Narx"] - t["Chegirma"] - t["Ovqat"]
        qarz_s = sof_s[t["Holat"] == "QARZ"].clip(lower=0).sum()
        stat_cards([
            ("💰", "Tushum", f"{int(t['Narx'].sum()):,}".replace(",", " "), "#6366f1"),
            ("🎗", "Chegirma", f"{int(t['Chegirma'].sum()):,}".replace(",", " "), "#f59e0b"),
            ("🍽", "Ovqat", f"{int(t['Ovqat'].sum()):,}".replace(",", " "), "#ef4444"),
            ("✅", "Foyda", f"{int(sof_s.sum()):,}".replace(",", " "), "#10b981"),
            ("👥", "O'quvchi", len(t), "#8b5cf6"),
            ("🔴", "Qarz", f"{int(qarz_s):,}".replace(",", " "), "#ef4444"),
        ])
        st.bar_chart(pd.DataFrame({"so'm": [t["Narx"].sum(), t["Ovqat"].sum(), sof_s.sum()]},
            index=["Tushum", "Ovqat", "Foyda"]), color="#6366f1")
        buf = io.BytesIO()
        exc = t.copy(); exc["Sof"] = sof_s
        exc.to_excel(buf, index=False, sheet_name=oy)
        st.download_button("📊 Excel yuklab olish", buf.getvalue(),
                           file_name=f"Hisobot_{oy}.xlsx", use_container_width=True)
    else:
        st.info("Bu oyda ma'lumot yo'q — jadvalga qator qo'shing!")

# ================== 📅 KUNLIK DAVOMAT ==================
elif sahifa == "📅 Kunlik davomat":
    hero("📅 Kunlik davomat", "Har kuni kim kelganini belgilang")
    sana = str(st.date_input("Sana", value=datetime.now()))
    bazalar = royxat(fb_get("accounting/students"))
    if not bazalar:
        st.warning("Baza bo'sh! Avval «👨‍🎓 Baza» bo'limida o'quvchi qo'shing.")
    else:
        dav = (st.session_state.data.get("__davomat__") or {}).get(sana) or {}
        st.markdown(f"#### 📆 {sana}")
        belgilar = {}
        for b in bazalar:
            nom = b.get("name") or "?"
            hozir = dav.get(nom)
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{nom}**" + (f" · {b.get('cls','')}" if b.get('cls') else ""))
            belgilar[nom] = c2.radio(nom, ["—", "✅ Keldi", "❌ Kelmadi"],
                index=0 if hozir is None else (1 if hozir is True else 2),
                key=f"a_{sana}_{nom}", horizontal=True, label_visibility="collapsed")
        if st.button("💾 Saqlash", type="primary"):
            natija = {n: (True if t == "✅ Keldi" else False if t == "❌ Kelmadi" else None)
                      for n, t in belgilar.items()}
            dav = st.session_state.data.get("__davomat__") or {}
            dav[sana] = {k: v for k, v in natija.items() if v is not None}
            st.session_state.data["__davomat__"] = dav
            bulutga_saqla()
        kel = sum(1 for v in dav.values() if v is True)
        kelma = sum(1 for v in dav.values() if v is False)
        stat_cards([("✅", "Keldi", kel, "#10b981"), ("❌", "Kelmadi", kelma, "#ef4444")])

# ================== 📊 TAQQOSLASH ==================
elif sahifa == "📊 Taqqoslash":
    hero("📊 Sinflar taqqoslash")
    oy = st.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="t_oy")
    groups = {}
    for s in oy_ma(oy):
        groups.setdefault((s.get("cls") or "").strip() or "Sinfsiz", []).append(s)
    if not groups:
        st.info("Bu oyda ma'lumot yo'q")
    else:
        rows = [{"Sinf": c, "O'quvchi": len(g),
                 "Tushum": sum(+s.get("price", 0) or 0 for s in g),
                 "Ovqat": sum(+s.get("food", 0) or 0 for s in g),
                 "Qarz": sum(max(sof(s), 0) for s in g if s.get("st") == "st-debt"),
                 "Davomat %": round(sum(1 for s in g if s.get("att", True)) / len(g) * 100)}
                for c, g in sorted(groups.items())]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ================== 🔴 QARZDORLAR ==================
elif sahifa == "🔴 Qarzdorlar":
    hero("🔴 Qarzdorlar", "Barcha oylar bo'yicha")
    rows = [{"Oy": oy, "Ism": s["name"], "Sinf": (s.get("cls") or "").strip() or "—",
             "Qarz": int(sof(s))}
            for oy in OYLAR for s in oy_ma(oy)
            if s.get("st") == "st-debt" and s.get("name") and sof(s) > 0]
    if rows:
        df = pd.DataFrame(rows)
        stat_cards([("🔴", "Umumiy qarz", f"{int(df['Qarz'].sum()):,}".replace(",", " "), "#ef4444"),
                    ("👥", "Qarzdorlar", len(df), "#f59e0b")])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Qarzdor yo'q — hammasi to'lagan!")

# ================== 📈 YILLIK ==================
elif sahifa == "📈 Yillik":
    hero("📈 Yillik hisobot", "12 oy natijalari")
    xarajatlar = royxat(fb_get("accounting/expenses"))
    rows = []
    for i, oy in enumerate(OYLAR):
        mal = oy_ma(oy)
        tushum = sum(+s.get("price", 0) or 0 for s in mal)
        cheg = sum(+s.get("disc", 0) or 0 for s in mal)
        ovqat = sum(+s.get("food", 0) or 0 for s in mal)
        xar = sum(+x.get("amount", 0) or 0 for x in xarajatlar
                  if str(x.get("date", ""))[5:7] == f"{i+1:02d}")
        rows.append({"Oy": oy, "O'quvchi": len(mal), "Tushum": int(tushum),
                     "Chegirma": int(cheg), "Ovqat": int(ovqat), "Xarajat": int(xar),
                     "Sof foyda": int(tushum - cheg - ovqat - xar)})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.set_index("Oy")[["Tushum", "Ovqat", "Xarajat", "Sof foyda"]])
    stat_cards([("💰", "Yillik tushum", f"{int(df['Tushum'].sum()):,}".replace(",", " "), "#6366f1"),
                ("💸", "Xarajat", f"{int(df['Xarajat'].sum()):,}".replace(",", " "), "#f59e0b"),
                ("🏆", "Sof foyda", f"{int(df['Sof foyda'].sum()):,}".replace(",", " "), "#10b981")])
    buf = io.BytesIO(); df.to_excel(buf, index=False, sheet_name="Yillik")
    st.download_button("📊 Yillik Excel", buf.getvalue(),
                       file_name="Yillik_hisobot.xlsx", use_container_width=True)

# ================== 🧾 TO'LOVLAR ==================
elif sahifa == "🧾 To'lovlar":
    hero("🧾 To'lovlar jurnali")
    payments = royxat(fb_get("accounting/payments"))
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    p_name = c1.text_input("Ism Sharif")
    p_amount = c2.number_input("Summa", min_value=0, step=10000)
    p_type = c3.selectbox("Turi", ["💵 Naqd", "💳 Plastik", "🏦 O'tkazma"])
    p_date = c4.date_input("Sana", value=datetime.now())
    p_note = st.text_input("Izoh (masalan: mart oyi)")
    if st.button("💾 Qayd etish", type="primary") and ADMIN:
        if p_name.strip() and p_amount > 0:
            payments.insert(0, {"name": p_name.strip(), "amount": p_amount,
                "type": p_type, "date": str(p_date), "note": p_note})
            if fb_put("accounting/payments", payments):
                st.success("✅ Saqlandi!")
                st.rerun()
        else:
            st.warning("Ism va summani kiriting!")
    if payments:
        df = pd.DataFrame(payments)
        stat_cards([("💰", "Jami to'lovlar",
                     f"{int(df['amount'].sum()):,} so'm".replace(",", " "), "#10b981")])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("To'lovlar yo'q")

# ================== 💸 XARAJATLAR ==================
elif sahifa == "💸 Xarajatlar":
    hero("💸 Xarajatlar", "Gaz, svet, suv, ta'mirlash...")
    expenses = royxat(fb_get("accounting/expenses"))
    c1, c2, c3 = st.columns([2, 1, 1])
    e_title = c1.text_input("Nima uchun?")
    e_amount = c2.number_input("Summa", min_value=0, step=10000)
    e_date = c3.date_input("Sana", value=datetime.now())
    if st.button("💾 Qayd etish", type="primary") and ADMIN:
        if e_title.strip() and e_amount > 0:
            expenses.insert(0, {"title": e_title.strip(), "amount": e_amount, "date": str(e_date)})
            if fb_put("accounting/expenses", expenses):
                st.success("✅ Saqlandi!")
                st.rerun()
        else:
            st.warning("Maydonlarni to'ldiring!")
    if expenses:
        df = pd.DataFrame(expenses)
        stat_cards([("💸", "Jami xarajat", f"{int(df['amount'].sum()):,} so'm".replace(",", " "), "#ef4444")])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Xarajatlar yo'q")

# ================== 👨‍🎓 BAZA ==================
elif sahifa == "👨‍🎓 Baza":
    hero("👨‍🎓 O'quvchilar bazasi", "Bir marta kiritiladi — har oy ishlatiladi")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    b_name = c1.text_input("Ism Sharif")
    b_cls = c2.text_input("Sinf (1-A)")
    b_price = c3.number_input("Oylik narx", min_value=0, step=10000)
    b_phone = c4.text_input("Telefon")
    if st.button("💾 Qo'shish", type="primary") and ADMIN:
        if b_name.strip():
            bazalar = royxat(fb_get("accounting/students"))
            bazalar.append({"name": b_name.strip(), "cls": b_cls.strip(),
                            "price": b_price, "phone": b_phone.strip()})
            if fb_put("accounting/students", bazalar):
                st.success(f"✅ Qo'shildi!")
                st.rerun()
        else:
            st.warning("Ismni kiriting!")
    bazalar = royxat(fb_get("accounting/students"))
    if bazalar:
        df = pd.DataFrame(bazalar)
        df.columns = ["Ism", "Sinf", "Narx", "Telefon"][:len(df.columns)]
        stat_cards([("👨‍🎓", "Bazadagi o'quvchilar", len(df), "#6366f1")])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Baza bo'sh")

# ================== ⚙️ SOZLAMALAR ==================
elif sahifa == "⚙️ Sozlamalar":
    hero("⚙️ Sozlamalar")
    if not ADMIN:
        st.warning("Faqat asosiy admin o'zgartira oladi!")
    else:
        c1, c2 = st.columns(2)
        u1 = c1.text_input("Asosiy login", value=cfg.get("user", ""))
        p1 = c2.text_input("Asosiy parol", value=cfg.get("pass", ""))
        st.markdown("**👥 Ikkinchi akkaunt (o'rinbosar)**")
        c1, c2, c3 = st.columns(3)
        u2 = c1.text_input("2-akkaunt login (bo'sh = o'chirilgan)", value=cfg.get("user2", ""))
        p2 = c2.text_input("2-akkaunt parol", value=cfg.get("pass2", ""))
        r2 = c3.selectbox("Huquqi", ["view", "full"], index=0 if cfg.get("role2") != "full" else 1)
        c1, c2 = st.columns(2)
        org = c1.text_input("Muassasa nomi", value=cfg.get("orgName", ""))
        tel = c2.text_input("Telefon (parol tiklash)", value=cfg.get("phone", ""))
        c1, c2 = st.columns(2)
        tg = c1.text_input("Telegram Bot Token", value=cfg.get("tgToken", ""))
        ch = c2.text_input("Telegram Chat ID", value=cfg.get("chatId", ""))
        if st.button("💾 Saqlash", type="primary"):
            yangi = {"user": u1 or "admin", "pass": p1 or "123", "user2": u2, "pass2": p2,
                     "role2": r2, "orgName": org or "Maktab", "phone": tel,
                     "tgToken": tg, "chatId": ch,
                     "defaultPrice": cfg.get("defaultPrice", 0),
                     "monthlyPlan": cfg.get("monthlyPlan", 0)}
            if fb_put("accounting/config", yangi):
                st.session_state.cfg = yangi
                st.success("✅ Saqlandi!")
            else:
                st.error("Bulutga yozib bo'lmadi!")
