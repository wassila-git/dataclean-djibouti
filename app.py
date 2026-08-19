import io
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup


st.set_page_config(
    page_title="DataClean Djibouti",
    page_icon="🇩🇯",
    layout="wide"
)


st.markdown(
    """
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
        margin-bottom: 25px;
    }

    .hero h1,
    .hero p {
        color: white !important;
    }

    .hero h1 {
        font-size: 40px;
    }

    .hero p {
        font-size: 18px;
    }

    .card {
        background-color: white;
        color: #172033;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }

    .card h2 {
        color: #0072ce !important;
    }

    .card p {
        color: #26364d !important;
        font-size: 17px;
    }

    section[data-testid="stSidebar"] {
        background-color: #202330;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stMetricLabel"] {
        color: #26364d !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        color: #172033 !important;
        font-weight: 800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def lire_fichier(fichier):
    """Lit les formats de données pris en charge."""

    nom = fichier.name.lower()

    if nom.endswith(".csv"):
        contenu = fichier.getvalue()

        try:
            return pd.read_csv(io.BytesIO(contenu))
        except UnicodeDecodeError:
            return pd.read_csv(
                io.BytesIO(contenu),
                encoding="latin-1"
            )

    if nom.endswith(".xlsx"):
        return pd.read_excel(
            fichier,
            engine="openpyxl"
        )

    if nom.endswith(".json"):
        return pd.read_json(fichier)

    if nom.endswith(".ods"):
        return pd.read_excel(
            fichier,
            engine="odf"
        )

    raise ValueError(
        "Format non pris en charge. "
        "Utilisez CSV, XLSX, JSON ou ODS."
    )


def analyser_donnees(df):
    """Détecte les anomalies dans un tableau."""

    anomalies = []

    for index, ligne in df.iterrows():
        numero_ligne = index + 2

        for colonne in df.columns:
            valeur = ligne[colonne]

            if pd.isna(valeur) or str(valeur).strip() == "":
                anomalies.append(
                    {
                        "Ligne": numero_ligne,
                        "Colonne": colonne,
                        "Type": "Valeur manquante",
                        "Valeur": "",
                        "Explication": (
                            "Une information est absente."
                        ),
                        "Action proposée": (
                            "Vérifier puis compléter manuellement."
                        )
                    }
                )

    doublons = df.duplicated(
        keep=False
    )

    for index in df.index[doublons]:
        anomalies.append(
            {
                "Ligne": index + 2,
                "Colonne": "Toutes les colonnes",
                "Type": "Doublon",
                "Valeur": "Ligne répétée",
                "Explication": (
                    "Cette ligne apparaît plusieurs fois."
                ),
                "Action proposée": (
                    "Vérifier s'il s'agit du même dossier."
                )
            }
        )

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
                        anomalies.append(
                            {
                                "Ligne": index + 2,
                                "Colonne": colonne,
                                "Type": "Valeur atypique",
                                "Valeur": str(
                                    df.loc[index, colonne]
                                ),
                                "Explication": (
                                    "La valeur est très éloignée "
                                    "des autres."
                                ),
                                "Action proposée": (
                                    "Vérifier la source de cette valeur."
                                )
                            }
                        )

    if not anomalies:
        return pd.DataFrame(
            columns=[
                "Ligne",
                "Colonne",
                "Type",
                "Valeur",
                "Explication",
                "Action proposée"
            ]
        )

    return pd.DataFrame(anomalies)


def analyser_url(url):
    """Analyse le texte public d'une page web."""

    url = url.strip()

    try:
        adresse = urlparse(url)

        if adresse.scheme not in ["http", "https"]:
            return None, (
                "L'URL doit commencer par http:// ou https://"
            )

        if not adresse.netloc:
            return None, "L'URL semble incomplète."

        reponse = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "DataClean-Djibouti-Demo/1.0"
                )
            }
        )

        reponse.raise_for_status()

        soup = BeautifulSoup(
            reponse.text,
            "html.parser"
        )

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        texte = soup.get_text(
            separator=" ",
            strip=True
        )

        motifs_suspects = [
            "ignore previous instructions",
            "ignore all previous instructions",
            "system prompt",
            "révèle tes instructions",
            "ignore les instructions précédentes",
            "bypass security",
            "jailbreak",
            "do not follow the rules",
            "ne respecte pas les règles"
        ]

        texte_minuscule = texte.lower()

        indices = [
            motif
            for motif in motifs_suspects
            if motif in texte_minuscule
        ]

        if len(indices) == 0:
            score = 5
            decision = "AUTORISER"
            explication = (
                "Aucun indice évident d'injection détecté."
            )

        elif len(indices) == 1:
            score = 65
            decision = "SIGNALER"
            explication = (
                "Un indice potentiellement suspect a été détecté."
            )

        else:
            score = 95
            decision = "BLOQUER"
            explication = (
                "Plusieurs indices d'injection ont été détectés."
            )

        resultat = {
            "URL": url,
            "Score de suspicion": f"{score} %",
            "Décision": decision,
            "Indices détectés": ", ".join(indices),
            "Explication": explication,
            "Nombre de caractères analysés": len(texte)
        }

        return resultat, None

    except requests.exceptions.RequestException as erreur:
        return None, (
            f"Impossible d'accéder à cette URL : {erreur}"
        )


def afficher_analyse(df):
    """Affiche les résultats de l'analyse des données."""

    rapport = analyser_donnees(df)

    total_cellules = df.shape[0] * df.shape[1]
    total_anomalies = len(rapport)

    if total_cellules > 0:
        score = max(
            0,
            round(
                100
                * (1 - total_anomalies / total_cellules)
            )
        )
    else:
        score = 0

    st.subheader("👁️ Aperçu des données")
    st.dataframe(
        df,
        use_container_width=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Lignes", df.shape[0])

    with col2:
        st.metric("Colonnes", df.shape[1])

    with col3:
        st.metric("Anomalies", total_anomalies)

    with col4:
        st.metric(
            "Score de qualité",
            f"{score} %"
        )

    st.subheader("🚨 Rapport des anomalies")

    if total_anomalies == 0:
        st.success(
            "Aucune anomalie détectée dans ce fichier."
        )

    else:
        st.dataframe(
            rapport,
            use_container_width=True
        )

        csv_rapport = rapport.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Télécharger le rapport",
            data=csv_rapport,
            file_name=(
                "rapport_dataclean_djibouti.csv"
            ),
            mime="text/csv"
        )

    st.subheader("📈 Répartition des statuts")

    if "statut" in df.columns:
        compte = (
            df["statut"]
            .fillna("Manquant")
            .value_counts()
        )

        st.bar_chart(compte)

    else:
        st.info(
            "Aucune colonne « statut » trouvée."
        )


st.sidebar.title("🌍 DataClean Djibouti")
st.sidebar.write("Prototype local")
st.sidebar.markdown("---")
st.sidebar.info(
    "Utilisez uniquement des données publiques, "
    "synthétiques ou anonymisées."
)


st.markdown(
    """
    <div class="hero">
        <h1>🇩🇯 DataClean Djibouti</h1>
        <p>
            Analyse intelligente de la qualité des données publiques
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="card">
        <h2>📊 Analysez un fichier administratif</h2>
        <p>
            Importez un fichier CSV, Excel, JSON ou ODS.
            L'application recherchera les valeurs manquantes,
            les doublons et les valeurs atypiques.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


fichier = st.file_uploader(
    "📂 Choisissez un fichier de données",
    type=[
        "csv",
        "xlsx",
        "json",
        "ods"
    ],
    max_upload_size=500
)


if fichier is None:
    st.info(
        "Aucun fichier importé. "
        "Vous pouvez utiliser la démonstration."
    )

    if st.button(
        "🧪 Charger les données de démonstration"
    ):
        donnees_demo = pd.DataFrame(
            {
                "identifiant": [
                    "DJ001",
                    "DJ002",
                    "DJ003",
                    "DJ003",
                    "DJ005"
                ],
                "commune": [
                    "Djibouti",
                    "Balbala",
                    "Boulaos",
                    "Boulaos",
                    None
                ],
                "age": [
                    25,
                    34,
                    None,
                    34,
                    150
                ],
                "statut": [
                    "Actif",
                    "Actif",
                    "Inactif",
                    "Inactif",
                    "Actif"
                ]
            }
        )

        st.session_state["donnees"] = donnees_demo

else:
    try:
        st.session_state["donnees"] = lire_fichier(
            fichier
        )

    except Exception as erreur:
        st.error(
            f"Impossible de lire le fichier : {erreur}"
        )


if "donnees" in st.session_state:
    afficher_analyse(
        st.session_state["donnees"]
    )


st.markdown("---")
st.subheader("🌐 Tester une URL publique")

st.caption(
    "Cette fonction analyse uniquement le texte visible "
    "d'une page publique."
)

url = st.text_input(
    "Entrez une adresse web",
    placeholder="https://www.python.org"
)


if st.button("🔍 Analyser l'URL"):
    if not url.strip():
        st.warning(
            "Veuillez saisir une URL."
        )

    else:
        with st.spinner(
            "Analyse de la page en cours..."
        ):
            resultat_url, erreur_url = analyser_url(
                url
            )

        if erreur_url:
            st.error(erreur_url)

        else:
            st.success(
                "Analyse terminée."
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Score de suspicion",
                    resultat_url[
                        "Score de suspicion"
                    ]
                )

            with col2:
                st.metric(
                    "Décision",
                    resultat_url[
                        "Décision"
                    ]
                )

            st.write(
                "**Explication :**",
                resultat_url[
                    "Explication"
                ]
            )

            indices = resultat_url[
                "Indices détectés"
            ]

            st.write(
                "**Indices détectés :**",
                indices if indices else "Aucun"
            )

            st.write(
                "**Contenu analysé :**",
                (
                    f'{resultat_url["Nombre de caractères analysés"]:,} '
                    "caractères"
                )
            )
