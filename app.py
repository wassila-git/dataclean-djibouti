import io
import hashlib

import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="DataClean Djibouti",
    page_icon="🇩🇯",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background-color: #f4f8fc;
    color: #172033;
}

.hero {
    background: linear-gradient(135deg, #0072ce, #00a896);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
}

.hero h1, .hero p {
    color: white !important;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

section[data-testid="stSidebar"] {
    background-color: #202330;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


def lire_fichier(fichier):
    nom = fichier.name.lower()

    if nom.endswith(".csv"):
        contenu = fichier.getvalue()
        try:
            return pd.read_csv(io.BytesIO(contenu))
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(contenu), encoding="latin-1")

    if nom.endswith(".xlsx"):
        return pd.read_excel(fichier)

    raise ValueError("Format non pris en charge.")


def analyser_donnees(df):
    anomalies = []

    for index, ligne in df.iterrows():
        numero_ligne = index + 2

        for colonne in df.columns:
            valeur = ligne[colonne]

            if pd.isna(valeur) or str(valeur).strip() == "":
                anomalies.append({
                    "Ligne": numero_ligne,
                    "Colonne": colonne,
                    "Type": "Valeur manquante",
                    "Valeur": "",
                    "Explication": "Une information est absente.",
                    "Action proposée": "Vérifier puis compléter manuellement."
                })

    doublons = df.duplicated(keep=False)

    for index in df.index[doublons]:
        anomalies.append({
            "Ligne": index + 2,
            "Colonne": "Toutes les colonnes",
            "Type": "Doublon",
            "Valeur": "Ligne répétée",
            "Explication": "Cette ligne apparaît plusieurs fois.",
            "Action proposée": "Vérifier s'il s'agit réellement du même dossier."
        })

    for colonne in df.columns:
        valeurs = df[colonne].dropna()

        if pd.api.types.is_numeric_dtype(valeurs):
            if len(valeurs) >= 4:
                moyenne = valeurs.mean()
                ecart = valeurs.std()

                if ecart > 0:
                    atypiques = valeurs[
                        abs(valeurs - moyenne) > 3 * ecart
                    ]

                    for index in atypiques.index:
                        anomalies.append({
                            "Ligne": index + 2,
                            "Colonne": colonne,
                            "Type": "Valeur atypique",
                            "Valeur": str(df.loc[index, colonne]),
                            "Explication": "La valeur est très éloignée des autres.",
                            "Action proposée": "Vérifier la source de cette valeur."
                        })

    return pd.DataFrame(anomalies)


st.sidebar.title("🌍 DataClean Djibouti")
st.sidebar.write("Prototype local")
st.sidebar.markdown("---")
st.sidebar.info(
    "Les données doivent être synthétiques, publiques ou anonymisées."
)


st.markdown("""
<div class="hero">
    <h1>🇩🇯 DataClean Djibouti</h1>
    <p>
        Analyse intelligente de la qualité des données publiques
    </p>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="card">
    <h2>📊 Analysez votre fichier administratif</h2>
    <p>
        Importez un fichier CSV ou Excel. DataClean Djibouti recherchera
        les valeurs manquantes, les doublons et les valeurs atypiques.
    </p>
</div>
""", unsafe_allow_html=True)


fichier = st.file_uploader(
    "📂 Choisissez un fichier CSV ou Excel",
    type=["csv", "xlsx"]
)


if fichier is None:
    st.info(
        "Aucun fichier importé. Vous pouvez utiliser le fichier de démonstration ci-dessous."
    )

    if st.button("🧪 Charger les données de démonstration"):
        df = pd.DataFrame({
            "identifiant": ["DJ001", "DJ002", "DJ003", "DJ003", "DJ005"],
            "commune": ["Djibouti", "Balbala", "Boulaos", "Boulaos", None],
            "age": [25, 34, None, 34, 150],
            "statut": ["Actif", "Actif", "Inactif", "Inactif", "Actif"]
        })
        st.session_state["donnees"] = df

else:
    try:
        st.session_state["donnees"] = lire_fichier(fichier)
    except Exception as erreur:
        st.error(f"Impossible de lire le fichier : {erreur}")


if "donnees" in st.session_state:
    df = st.session_state["donnees"].copy()

    st.subheader("👁️ Aperçu des données")
    st.dataframe(df, use_container_width=True)

    rapport = analyser_donnees(df)

    total_cellules = df.shape[0] * df.shape[1]
    total_anomalies = len(rapport)

    if total_cellules > 0:
        score = max(
            0,
            round(100 * (1 - total_anomalies / total_cellules))
        )
    else:
        score = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Lignes", df.shape[0])

    with col2:
        st.metric("Colonnes", df.shape[1])

    with col3:
        st.metric("Anomalies", total_anomalies)

    with col4:
        st.metric("Score de qualité", f"{score} %")

    if total_anomalies == 0:
        st.success("Aucune anomalie détectée dans ce fichier.")
    else:
        st.subheader("🚨 Rapport des anomalies")
        st.dataframe(rapport, use_container_width=True)

        csv_rapport = rapport.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Télécharger le rapport des anomalies",
            data=csv_rapport,
            file_name="rapport_dataclean_djibouti.csv",
            mime="text/csv"
        )

    st.subheader("📈 Répartition des statuts")

    if "statut" in df.columns:
        compte = df["statut"].fillna("Manquant").value_counts()
        st.bar_chart(compte)
    else:
        st.info(
            "Ajoutez une colonne nommée « statut » pour afficher ce graphique."
        )

    empreinte = hashlib.sha256(
        pd.util.hash_pandas_object(df, index=True).values
    ).hexdigest()[:16]

    st.caption(
        f"Traçabilité : empreinte du fichier analysé = {empreinte}"
    )