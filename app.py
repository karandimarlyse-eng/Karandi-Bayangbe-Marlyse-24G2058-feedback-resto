import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG
st.set_page_config(page_title="Feedback Resto", page_icon="🍽️", layout="centered")

# =========================
# STYLE
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Dancing+Script:wght@600&display=swap');

[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1555396273-367ea4eb4db5");
    background-size: cover;
}

[data-testid="stAppViewContainer"]::before {
    content:"";
    position:fixed;
    width:100%;
    height:100%;
    background:rgba(255,182,193,0.35);
    z-index:0;
}

.block-container {
    position:relative;
    z-index:1;
    background:rgba(255,255,255,0.95);
    padding:25px;
    border-radius:20px;
}

h1 {
    font-family:'Dancing Script';
    font-size:55px;
    color:#ff2e88;
    text-align:center;
    font-weight:bold;
}

h2, h3 {
    color:#ff4b7d;
    font-weight:600;
}

body, p, label, div {
    font-family:'Poppins';
    color:#1a1a1a;
    font-weight:500;
}

.stButton>button {
    background:#ff4b7d;
    color:white;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DB
# =========================
def get_connection():
    return sqlite3.connect("feedback.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu TEXT,
        boisson TEXT,
        note INTEGER,
        gout INTEGER,
        service INTEGER,
        proprete INTEGER,
        commentaire TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# NAVIGATION
page = st.sidebar.radio("Navigation", ["🏠 Accueil","📝 Donner un avis","📊 Dashboard"])

# =========================
# ACCUEIL
# =========================
if page == "🏠 Accueil":
    st.title("🍽️ K.M Restaurant")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://images.unsplash.com/photo-1604908176997-125f25cc6f3d", caption="Eru 🍲")
    with col2:
        st.image("https://images.unsplash.com/photo-1604908812025-0b2c1d06b6a6", caption="Poulet 🍗")
    with col3:
        st.image("https://images.unsplash.com/photo-1605478371310-a9f1e96b4ff4", caption="Riz sauté 🍛")

    st.markdown("### 🌸 Nos spécialités")
    st.write("""
    🍝 Spaghetti  
    🍲 Eru & Waterfufu  
    🍲 Ndolé  
    🍃 Okok  
    🥗 Salade  
    🍗 Poulet frit  
    🥩 Bifteck  
    🍛 Riz sauté  
    """)

    st.markdown("### 🥤 Boissons")
    st.write("Bissap • Jus d'ananas • Soda")

    st.success("Votre avis nous aide à nous améliorer 💖")

# =========================
# FORMULAIRE
# =========================
elif page == "📝 Donner un avis":
    st.title("📝 Votre avis")

    conn = get_connection()
    c = conn.cursor()

    with st.form("form"):
        menu = st.selectbox("🍽️ Plat",[
            "Spaghetti","Eru and Waterfufu","Ndole",
            "Okok","Salade","Fried Rice",
            "Fried Chicken","Bifteck"
        ])

        boisson = st.selectbox("🥤 Boisson",[
            "Bissap","Ananas","Soda","Aucune"
        ])

        note = st.slider("⭐ Note globale",1,10)

        avis_options = {
            "😡 Mauvais": 2,
            "😐 Passable": 4,
            "🙂 Bon": 6,
            "😍 Très bon": 8,
            "🔥 Excellent": 10
        }

        gout = avis_options[st.selectbox("🍽️ Goût", list(avis_options.keys()))]
        service = avis_options[st.selectbox("⚡ Service", list(avis_options.keys()))]
        proprete = avis_options[st.selectbox("🧼 Propreté", list(avis_options.keys()))]

        commentaire = st.text_area("💬 Commentaire")

        submit = st.form_submit_button("Envoyer")

        if submit:
            if commentaire.strip() == "":
                st.warning("⚠️ Ajoute un commentaire")
            else:
                c.execute("""
                INSERT INTO feedback 
                (menu,boisson,note,gout,service,proprete,commentaire,date)
                VALUES (?,?,?,?,?,?,?,?)
                """,(menu,boisson,note,gout,service,proprete,commentaire,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("💖 Merci pour votre confiance !")

    conn.close()

# =========================
# DASHBOARD
# =========================
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    conn = get_connection()

    try:
        df = pd.read_sql_query("SELECT * FROM feedback ORDER BY id DESC", conn)

        if not df.empty:

            df["date"] = pd.to_datetime(df["date"], errors='coerce')

            st.metric("⭐ Moyenne", round(df["note"].mean(),2))
            st.metric("📈 Feedbacks", len(df))

            # Analyse
            st.markdown("### 🧠 Analyse rapide")
            if df["note"].mean() >= 8:
                st.success("😍 Les clients sont très satisfaits")
            elif df["note"].mean() >= 5:
                st.info("🙂 Satisfaction moyenne")
            else:
                st.warning("😔 Clients insatisfaits")

            # Classement
            st.markdown("### 🏆 Classement des plats (fiable)")
            ranking = df.groupby("menu").agg({
                "note": "mean",
                "id": "count"
            }).rename(columns={"note": "moyenne", "id": "votes"})

            ranking = ranking[ranking["votes"] >= 2]
            ranking = ranking.sort_values(by="moyenne", ascending=False)

            st.dataframe(ranking)

            # Top 3
            if not ranking.empty:
                st.markdown("### 🥇 Top 3 des plats")
                medals = ["🥇", "🥈", "🥉"]

                for i, (plat, row) in enumerate(ranking.head(3).iterrows()):
                    st.markdown(
                        f"{medals[i]} **{plat}** — ⭐ {row['moyenne']:.1f} ({int(row['votes'])} avis)"
                    )

                st.success(f"🏆 Meilleur plat : {ranking.index[0]}")

            # Pie boissons
            st.markdown("### 🥤 Répartition des boissons")
            fig1, ax1 = plt.subplots(figsize=(4,4))
            df["boisson"].value_counts().plot.pie(
                autopct='%1.1f%%',
                ax=ax1,
                textprops={'fontsize': 10},
                wedgeprops={'edgecolor':'white'}
            )
            ax1.set_ylabel("")
            st.pyplot(fig1)

            # Qualité (bar chart propre)
            st.markdown("### ⭐ Analyse de la qualité")

            quality_means = {
                "Goût": df["gout"].mean(),
                "Service": df["service"].mean(),
                "Propreté": df["proprete"].mean()
            }

            st.bar_chart(quality_means)

            # Graphiques
            st.bar_chart(df.groupby("menu")["note"].mean())
            st.line_chart(df.set_index("date")["note"])

            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger", csv, "feedback.csv")

            st.dataframe(df)

        else:
            st.info("Aucune donnée")

    except Exception as e:
        st.error(f"Erreur: {e}")

    conn.close()
