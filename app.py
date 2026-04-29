import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# CONFIG PAGE
st.set_page_config(page_title="Feedback Resto", page_icon="🍽️", layout="centered")

# =========================
# 🎨 STYLE FIX COMPLET
# =========================
st.markdown("""
<style>

/* FOND */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1555396273-367ea4eb4db5");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* OVERLAY */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.80);
    z-index: 0;
}

/* CONTENU */
.block-container {
    position: relative;
    z-index: 1;
    background-color: rgba(0,0,0,0.70);
    padding: 25px;
    border-radius: 15px;
}

/* TITRES */
h1 {
    font-size: 52px !important;
    color: #ff6b9d !important;
    text-align: center;
    text-shadow: 3px 3px 10px black;
}

h2 {
    font-size: 36px !important;
    color: #ff85a2 !important;
    text-shadow: 2px 2px 6px black;
}

h3 {
    font-size: 26px !important;
    color: #ffc0cb !important;
}

/* TEXTE */
body, p, label, div, span {
    color: white !important;
    font-size: 17px;
}

/* SELECT & INPUT */
.stSelectbox div[data-baseweb="select"] * {
    color: #b30059 !important;
    font-weight: bold;
}

input, textarea {
    color: #b30059 !important;
    font-weight: bold;
}

/* BOUTONS */
.stButton>button {
    background-color: #ff4b7d;
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# DB (FIX DEFINITIF)
# =========================
def get_connection():
    return sqlite3.connect('feedback.db', check_same_thread=False)

# 🔥 CREATION TABLE (ULTRA IMPORTANT)
conn = get_connection()
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu TEXT,
    note INTEGER,
    commentaire TEXT,
    date TEXT
)
''')
conn.commit()
conn.close()

# NAVIGATION
page = st.sidebar.radio("Navigation", ["🏠 Accueil", "📝 Donner un avis", "📊 Dashboard"])

# =========================
# 🏠 ACCUEIL
# =========================
if page == "🏠 Accueil":
    st.title("🍽️ Bienvenue chez K.M Restaurant")

    st.image(
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
        width='stretch'
    )

    st.markdown("""
    ### 🌸 Une expérience culinaire unique

    🔹 Plats frais et délicieux 🍲  
    🔹 Service rapide ⚡  
    🔹 Cuisine locale et internationale 🌍  

    💡 Votre avis nous aide à nous améliorer !

    👉 Cliquez sur **Donner un avis** pour noter nos plats.
    """)

    st.success("💖 Merci pour votre confiance !")

# =========================
# 📝 FORMULAIRE
# =========================
elif page == "📝 Donner un avis":
    st.title("📝 Donnez votre avis")

    conn = get_connection()
    c = conn.cursor()

    with st.form("form_feedback"):
        menu = st.selectbox(
            "🍝 Choisissez votre plat",
            ["Spaghetti", "Eru and Waterfufu", "Fried Rice", "Fried Chicken", "Ndole and Plantain", "Bifteck", "Others"]
        )

        note = st.slider("⭐ Note", 1, 10)
        commentaire = st.text_area("💬 Commentaire")

        submit = st.form_submit_button("Envoyer")

        if submit:
            if commentaire.strip() == "":
                st.warning("⚠️ Veuillez écrire un commentaire")
            else:
                c.execute(
                    "INSERT INTO feedback (menu, note, commentaire, date) VALUES (?, ?, ?, ?)",
                    (menu, note, commentaire, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                st.success("✅ Feedback enregistré !")

    conn.close()

# =========================
# 📊 DASHBOARD FIX TOTAL
# =========================
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    conn = get_connection()
    c = conn.cursor()

    data = c.execute("SELECT * FROM feedback ORDER BY id DESC").fetchall()

    if data:
        df = pd.DataFrame(data, columns=["ID", "Menu", "Note", "Commentaire", "Date"])

        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"])

        st.caption(f"🔄 Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

        menu_filter = st.selectbox("Filtrer par plat", ["Tous"] + list(df["Menu"].unique()))

        if menu_filter == "Tous":
            df_filtre = df.copy()
        else:
            df_filtre = df[df["Menu"] == menu_filter]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📈 Feedbacks", len(df_filtre))
        with col2:
            st.metric("⭐ Moyenne", round(df_filtre["Note"].mean(), 2))

        if not df.empty:
            best_menu = df.groupby("Menu")["Note"].mean().idxmax()
            st.success(f"🏆 Meilleur plat : {best_menu}")

        st.markdown("### 💬 Dernier commentaire")
        if not df_filtre.empty:
            last = df_filtre.sort_values(by="Date", ascending=False).iloc[0]
            st.info(f"{last['Commentaire']} (⭐ {last['Note']}) - {last['Date']}")
        else:
            st.warning("Aucun commentaire.")

        st.markdown("### 📊 Moyenne par plat")
        st.bar_chart(df.groupby("Menu")["Note"].mean())

        st.markdown("### 📉 Evolution des notes")
        st.line_chart(df_filtre.set_index("Date")["Note"])

        with st.expander("📋 Voir les données"):
            st.dataframe(df_filtre)

    else:
        st.info("Pas encore de données.")

    conn.close()
