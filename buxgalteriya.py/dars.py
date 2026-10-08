# ============================================================
#  ☁️ MAKTAB BUXGALTERIYA — PYTHON/STREAMLIT VERSIYA
# ============================================================
#  Bulut: Firebase (HTML versiya bilan BIR XIL baza — ma'lumotlar umumiy!)
#  Ishga tushirish:  streamlit run buxgalteriya.py
# ============================================================

import io
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# ---------------- SOZLAMALAR ----------------
DB_URL = "https://maktab-buxgalteriya-default-rtdb.firebaseio.com"
OYLAR = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
         "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
STANDART = {"user": "admin", "pass": "123", "user2": "", "pass2": "",
            "orgName": "Maktab", "phone": "+998", "tgToken": "", "chatId": "",
            "defaultPrice": 0, "monthlyPlan": 0}

st.set_page_config(page_title="Maktab Buxgalteriya", page_icon="☁️", layout="wide")

# ---------------- FIREBASE (REST API) ----------------

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

def fb_delete(yol):
    try:
        requests.delete(f"{DB_URL}/{yol}.json", timeout=10)
    except Exception:
        pass

# ---------------- YORDAMCHILAR ----------------

def royxat(v):
    """Firebase obyekt/massivni doim ro'yxatga aylantiradi"""
    if not v:
        return []
    if isinstance(v, list):
        return [x for x in v if x]
    return [x for x in v.values() if x]

def sof(s):
    return (+s.get("price", 0) or 0) - (+s.get("disc", 0) or 0) - (+s.get("food", 0) or 0)

def holat_uz(st_code):
    return {"st-paid": "TO'LANDI", "st-partial": "QISMAN"}.get(st_code, "QARZ")

def holat_kod(uz):
    return {"TO'LANDI": "st-paid", "QISMAN": "st-partial"}.get(uz, "QARZ")

def bulutga_saqla():
    ok = fb_put("accounting/data", st.session_state.data)
    if ok:
        st.toast("✅ Bulutga saqlandi!")
    else:
        st.toast("⚠️ Bulutga yozib bo'lmadi — internetni tekshiring!", icon="⚠️")
    return ok

# ---------------- SESSION ----------------
if "kirgan" not in st.session_state:
    st.session_state.kirgan = False
    st.session_state.roll = "admin"
    st.session_state.data = {}
    st.session_state.yuklandi = False
    st.session_state.versiya = 0

def bulutdan_yukla():
    st.session_state.data = fb_get("accounting/data") or {}
    st.session_state.yuklandi = True

def oy_ma(lumoti_oy):
    return royxat(st.session_state.data.get(lumoti_oy))

# ---------------- KIRISH ----------------
if not st.session_state.kirgan:
    st.markdown("## ☁️ Maktab Buxgalteriya (Python)")
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown("###### Kirish")
        u = st.text_input("Login", key="lg_u")
        p = st.text_input("Parol", type="password", key="lg_p")
        if st.button("🔑 Kirish", use_container_width=True, type="primary"):
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
            tel = st.text_input("Telefon raqamingiz")
            if st.button("Parolni ko'rish"):
                cfg = {**STANDART, **(fb_get("accounting/config") or {})}
                if tel.strip() and tel.strip() == (cfg.get("phone") or ""):
                    st.info(f"Login: {cfg['user']} | Parol: {cfg['pass']}")
                else:
                    st.error("Bu raqam ro'yxatda yo'q!")
    st.stop()

# ---------------- BULUTDAN YUKLASH ----------------
if not st.session_state.yuklandi:
    st.session_state.cfg = {**STANDART, **(fb_get("accounting/config") or {})}
    bulutdan_yukla()

cfg = st.session_state.cfg
ADMIN = st.session_state.roll == "admin"

# ---------------- SARLAVHA + MENU ----------------
s1, s2 = st.columns([4, 1])
with s1:
    st.markdown(f"## Maktab ☁️ — Python versiya")
with s2:
    if st.button("🔄 Yangilash", use_container_width=True):
        bulutdan_yukla()
        st.session_state.versiya += 1
        st.rerun()

sahifa = st.sidebar.radio("🧰 Bo'lim tanlang:", [
    "💰 Hisob", "📅 Kunlik davomat", "📊 Taqqoslash", "🔴 Qarzdorlar",
    "📈 Yillik", "🧾 To'lovlar", "💸 Xarajatlar", "👨‍🎓 Baza", "⚙️ Sozlamalar"])
st.sidebar.caption("Python + Streamlit 💛")

# ================= 💰 HISOB =================
if sahifa == "💰 Hisob":
    oy = st.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="h_oy")
    cls_f = st.text_input("🎓 Sinf filtri (bo'sh = barchasi)", key="h_cls")

    mal = oy_ma(oy)
    df = pd.DataFrame([{
        "Ism": str(s.get("name") or ""),
        "Sinf": str(s.get("cls") or ""),
        "Narx": float(s.get("price") or 0),
        "Chegirma": float(s.get("disc") or 0),
        "Ovqat": float(s.get("food") or 0),
        "Holat": holat_uz(s.get("st")),
        "Keldi": bool(s.get("att", True)),
    } for s in mal])

    if cls_f.strip():
        df = df[df["Sinf"].str.strip() == cls_f.strip()]

    tahrir = st.data_editor(
        df,
        column_config={
            "Ism": st.column_config.TextColumn("👤 Ism", width="large"),
            "Narx": st.column_config.NumberColumn("💰 Narx", step=1000),
            "Chegirma": st.column_config.NumberColumn("🎗 Chegirma", step=1000),
            "Ovqat": st.column_config.NumberColumn("🍽 Ovqat", step=1000),
            "Holat": st.column_config.SelectboxColumn(
                "Holat", options=["QARZ", "QISMAN", "TO'LANDI"]),
            "Keldi": st.column_config.CheckboxColumn("✅ Darsga keldi"),
        },
        num_rows="dynamic" if ADMIN else "fixed",
        hide_index=True,
        use_container_width=True,
        key=f"jadval_{oy}_{st.session_state.versiya}",
    )

    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 Bulutga saqlash", type="primary", use_container_width=True):
            if ADMIN:
                taza = tahrir.fillna({"Ism": "", "Sinf": "", "Narx": 0, "Chegirma": 0, "Ovqat": 0})
                taza["Holat"] = taza["Holat"].fillna("QARZ")
                taza["Keldi"] = taza["Keldi"].fillna(True)
                royxat_yang = [{
                    "name": str(r["Ism"]), "cls": str(r["Sinf"]),
                    "price": float(r["Narx"]), "disc": float(r["Chegirma"]),
                    "food": float(r["Ovqat"]), "st": holat_kod(r["Holat"]),
                    "att": bool(r["Keldi"]),
                } for _, r in taza.iterrows()]
                st.session_state.data[oy] = royxat_yang
                bulutga_saqla()
            else:
                st.warning("Sizda faqat ko'rish huquqi bor 👀")

    # Statistika
    if not tahrir.empty:
        t = tahrir.fillna(0)
        sof_s = t["Narx"] - t["Chegirma"] - t["Ovqat"]
        qarz_s = sof_s[t["Holat"] == "QARZ"].clip(lower=0).sum()
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("💰 Tushum", f"{int(t['Narx'].sum()):,} so'm".replace(",", " "))
        m2.metric("🎗 Chegirma", f"{int(t['Chegirma'].sum()):,} so'm".replace(",", " "))
        m3.metric("🍽 Ovqat", f"{int(t['Ovqat'].sum()):,} so'm".replace(",", " "))
        m4.metric("✅ Foyda", f"{int(sof_s.sum()):,} so'm".replace(",", " "))
        m5.metric("👥 O'quvchi", len(t))
        m6.metric("🔴 Qarz", f"{int(qarz_s):,} so'm".replace(",", " "))
        dav = int(t["Keldi"].fillna(True).mean() * 100) if len(t) else 0
        m5.metric("📅 Davomat", f"{dav}%")

        st.bar_chart(pd.DataFrame(
            {"so'm": [t["Narx"].sum(), t["Ovqat"].sum(), sof_s.sum()]},
            index=["Tushum", "Ovqat", "Foyda"]))

        # Excel
        buf = io.BytesIO()
        exc = t.copy()
        exc["Sof"] = sof_s
        exc.rename(columns={"Keldi": "Davomat"}).to_excel(buf, index=False, sheet_name=oy)
        st.download_button("📊 Excel yuklab olish", buf.getvalue(),
                           file_name=f"Hisobot_{oy}.xlsx", use_container_width=True)
    else:
        st.info("Bu oyda ma'lumot yo'q — jadvalga qator qo'shing va saqlang!")

# ================= 📅 KUNLIK DAVOMAT =================
elif sahifa == "📅 Kunlik davomat":
    sana = st.date_input("📅 Sana", value=datetime.now())
    st.caption("O'quvchilar bazasidan olinadi (👨‍🎓 Baza bo'limida kiriting)")

    bazalar = royxat(fb_get("accounting/students"))
    if not bazalar:
        st.warning("Baza bo'sh! Avval «👨‍🎓 Baza» bo'limida o'quvchi qo'shing.")
    else:
        kalit = str(sana)
        bugun = (st.session_state.data.get("__davomat__") or {}).get(kalit) or {}
        st.markdown(f"### {kalit}")
        oyna = st.container()
        belgilar = {}
        for b in bazalar:
            nom = b.get("name") or "?"
            hozir = bugun.get(nom)
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{nom}**" + (f"  ({b.get('cls','')})" if b.get('cls') else ""))
            belgilar[nom] = c2.radio(nom, ["—", "✅ Keldi", "❌ Kelmadi"],
                                     index=0 if hozir is None else (1 if hozir is True else 2),
                                     key=f"att_{kalit}_{nom}", horizontal=True,
                                     label_visibility="collapsed")
        if st.button("💾 Davomatni saqlash", type="primary"):
            natija = {}
            for nom, tanlov in belgilar.items():
                if tanlov == "✅ Keldi":
                    natija[nom] = True
                elif tanlov == "❌ Kelmadi":
                    natija[nom] = False
            dav = st.session_state.data.get("__davomat__") or {}
            dav[kalit] = natija
            st.session_state.data["__davomat__"] = dav
            if bulutga_saqla():
                st.success("Saqlandi ✅")
        kel = sum(1 for v in bugun.values() if v is True)
        kelma = sum(1 for v in bugun.values() if v is False)
        st.info(f"✅ {kel} keldi | ❌ {kelma} kelmadi")

# ================= 📊 TAQQOSLASH =================
elif sahifa == "📊 Taqqoslash":
    oy = st.selectbox("📅 Oy", OYLAR, index=datetime.now().month - 1, key="t_oy")
    mal = oy_ma(oy)
    groups = {}
    for s in mal:
        c = (s.get("cls") or "").strip() or "Sinfsiz"
        groups.setdefault(c, []).append(s)
    if not groups:
        st.info("Bu oyda ma'lumot yo'q")
    else:
        satrlar = []
        for c, g in sorted(groups.items()):
            tushum = sum(+s.get("price", 0) or 0 for s in g)
            ovqat = sum(+s.get("food", 0) or 0 for s in g)
            qarz = sum(max(sof(s), 0) for s in g if s.get("st") == "st-debt")
            dav = round(sum(1 for s in g if s.get("att", True)) / len(g) * 100) if g else 0
            satrlar.append({"Sinf": c, "O'quvchi": len(g), "Tushum": int(tushum),
                            "Ovqat": int(ovqat), "Qarz": int(qarz), "Davomat %": dav})
        df = pd.DataFrame(satrlar)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.dataframe(pd.DataFrame([{
            "Sinf": "JAMI", "O'quvchi": df["O'quvchi"].sum(),
            "Tushum": df["Tushum"].sum(), "Ovqat": df["Ovqat"].sum(),
            "Qarz": df["Qarz"].sum(),
            "Davomat %": round((df["Davomat %"] * df["O'quvchi"]).sum() / max(1, df["O'quvchi"].sum()))}]),
            use_container_width=True, hide_index=True)

# ================= 🔴 QARZDORLAR =================
elif sahifa == "🔴 Qarzdorlar":
    rows = []
    for oy in OYLAR:
        for s in oy_ma(oy):
            if s.get("st") == "st-debt" and s.get("name") and sof(s) > 0:
                rows.append({"Oy": oy, "Ism": s["name"],
                             "Sinf": (s.get("cls") or "").strip() or "—",
                             "Qarz": int(sof(s))})
    if rows:
        df = pd.DataFrame(rows)
        m1, m2 = st.columns(2)
        m1.metric("🔴 Umumiy qarz", f"{int(df['Qarz'].sum()):,} so'm".replace(",", " "))
        m2.metric("👥 Qarzdorlar", len(df))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Qarzdor yo'q — hammasi to'lagan!")

# ================= 📈 YILLIK =================
elif sahifa == "📈 Yillik":
    xarajatlar = royxat(fb_get("accounting/expenses"))
    satrlar = []
    for i, oy in enumerate(OYLAR):
        mal = oy_ma(oy)
        tushum = sum(+s.get("price", 0) or 0 for s in mal)
        cheg = sum(+s.get("disc", 0) or 0 for s in mal)
        ovqat = sum(+s.get("food", 0) or 0 for s in mal)
        mm = f"{i+1:02d}"
        xar = sum(+x.get("amount", 0) or 0 for x in xarajatlar
                  if str(x.get("date", ""))[5:7] == mm)
        satrlar.append({"Oy": oy, "O'quvchi": len(mal), "Tushum": int(tushum),
                        "Chegirma": int(cheg), "Ovqat": int(ovqat),
                        "Xarajat": int(xar), "Sof foyda": int(tushum - cheg - ovqat - xar)})
    df = pd.DataFrame(satrlar)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.set_index("Oy")[["Tushum", "Ovqat", "Xarajat", "Sof foyda"]])
    buf = io.BytesIO()
    df.to_excel(buf, index=False, sheet_name="Yillik")
    st.download_button("📊 Yillik Excel", buf.getvalue(),
                       file_name="Yillik_hisobot.xlsx", use_container_width=True)

# ================= 🧾 TO'LOVLAR =================
elif sahifa == "🧾 To'lovlar":
    payments = royxat(fb_get("accounting/payments"))
    st.markdown("### ➕ Yangi to'lov")
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
                st.success("✅ To'lov qayd etildi va bulutga saqlandi!")
                st.rerun()
        else:
            st.warning("Ism va summani kiriting!")
    if payments:
        df = pd.DataFrame(payments)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.metric("💰 Jami to'lovlar", f"{int(df['amount'].sum()):,} so'm".replace(",", " "))
    else:
        st.info("To'lovlar yo'q")

# ================= 💸 XARAJATLAR =================
elif sahifa == "💸 Xarajatlar":
    expenses = royxat(fb_get("accounting/expenses"))
    st.markdown("### ➕ Yangi xarajat")
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
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.metric("💸 Jami xarajat", f"{int(df['amount'].sum()):,} so'm".replace(",", " "))
    else:
        st.info("Xarajatlar yo'q")

# ================= 👨‍🎓 BAZA =================
elif sahifa == "👨‍🎓 Baza":
    st.markdown("### ➕ Yangi o'quvchi (bir marta kiritiladi!)")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    b_name = c1.text_input("Ism Sharif")
    b_cls = c2.text_input("Sinf (1-A)")
    b_price = c3.number_input("Oylik narx", min_value=0, step=10000)
    b_phone = c4.text_input("Telefon")
    if st.button("💾 Bazaga qo'shish", type="primary") and ADMIN:
        if b_name.strip():
            bazalar = royxat(fb_get("accounting/students"))
            bazalar.append({"name": b_name.strip(), "cls": b_cls.strip(),
                            "price": b_price, "phone": b_phone.strip()})
            if fb_put("accounting/students", bazalar):
                st.success(f"✅ «{b_cls}» sinfiga qo'shildi!")
                st.rerun()
        else:
            st.warning("Ismni kiriting!")
    bazalar = royxat(fb_get("accounting/students"))
    if bazalar:
        df = pd.DataFrame(bazalar)
        df.columns = ["Ism", "Sinf", "Narx", "Telefon"][:len(df.columns)]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("💡 Hisob bo'limida jadvalga qo'lda qator qo'shib ismlarni yozasiz (bazadan nusxa olish HTML versiyada bor)")
    else:
        st.info("Baza bo'sh")

# ================= ⚙️ SOZLAMALAR =================
elif sahifa == "⚙️ Sozlamalar":
    st.markdown("### ⚙️ Sozlamalar")
    if not ADMIN:
        st.warning("Faqat asosiy admin o'zgartira oladi!")
    else:
        u1 = st.text_input("Asosiy login", value=cfg.get("user", ""))
        p1 = st.text_input("Asosiy parol", value=cfg.get("pass", ""))
        st.markdown("**👥 Ikkinchi akkaunt (o'rinbosar)**")
        u2 = st.text_input("2-akkaunt login (bo'sh = o'chirilgan)", value=cfg.get("user2", ""))
        p2 = st.text_input("2-akkaunt parol", value=cfg.get("pass2", ""))
        r2 = st.selectbox("2-akkaunt huquqi", ["view", "full"],
                          index=0 if cfg.get("role2") != "full" else 1)
        org = st.text_input("Muassasa nomi", value=cfg.get("orgName", ""))
        tel = st.text_input("Telefon (parol tiklash uchun)", value=cfg.get("phone", ""))
        tg = st.text_input("Telegram Bot Token", value=cfg.get("tgToken", ""))
        ch = st.text_input("Telegram Chat ID", value=cfg.get("chatId", ""))
        if st.button("💾 Saqlash", type="primary"):
            yangi = {"user": u1 or "admin", "pass": p1 or "123", "user2": u2,
                     "pass2": p2, "role2": r2, "orgName": org or "Maktab",
                     "phone": tel, "tgToken": tg, "chatId": ch,
                     "defaultPrice": cfg.get("defaultPrice", 0),
                     "monthlyPlan": cfg.get("monthlyPlan", 0)}
            if fb_put("accounting/config", yangi):
                st.session_state.cfg = yangi
                st.success("✅ Saqlandi va bulutga yozildi!")
            else:
                st.error("Bulutga yozib bo'lmadi!")