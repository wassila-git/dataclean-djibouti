import io
import re
from urllib.parse import urlparse

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


def ajouter_anomalie(
    anomalies,
    ligne,
    colonne,
    type_anomalie,
    valeur,
    explication,
    correction
):
    types_eleves = {
        "Identifiant dupliqué",
        "Date invalide",
        "Valeur impossible",
        "Format incorrect"
    }

    anomalies.append(
        {
            "Ligne": ligne,
            "Colonne": colonne,
            "Type": type_anomalie,
            "Valeur": valeur,
            "Explication": explication,
            "Correction proposée": correction,
            "Niveau": (
                "Élevé"
                if type_anomalie in types_eleves
                else "Moyen"
            )
        }
    )


def lire_fichier(fichier):
    nom = fichier.name.lower()
    contenu = fichier.getvalue()

    if nom.endswith(".csv"):
        try:
            return pd.read_csv(io.BytesIO(contenu))
        except UnicodeDecodeError:
            return pd.read_csv(
                io.BytesIO(contenu),
                encoding="latin-1"
            )

    if nom.endswith(".xlsx"):
        return pd.read_excel(
            io.BytesIO(contenu),
            engine="openpyxl"
        )

    if nom.endswith(".json"):
        return pd.read_json(
            io.BytesIO(contenu)
        )

    if nom.endswith(".ods"):
        return pd.read_excel(
            io.BytesIO(contenu),
            engine="odf"
        )

    raise ValueError(
        "Format non pris en charge. "
        "Utilisez CSV, XLSX, JSON ou ODS."
    )


def analyser_donnees(df):
    anomalies = []

    communes_valides = {
        "Djibouti",
        "Balbala",
        "Boulaos",
        "Ras-Dika",
        "Haramous"
    }

    for index, ligne in df.iterrows():
        numero_ligne = index + 2

        for colonne in df.columns:
            valeur = ligne[colonne]

            if pd.isna(valeur) or str(valeur).strip() == "":
                ajouter_anomalie(
                    anomalies,
                    numero_ligne,
                    colonne,
                    "Valeur manquante",
                    "",
                    "Une information est absente.",
                    "Compléter la valeur après vérification."
                )

        if "age" in df.columns:
            age = ligne["age"]

            if not pd.isna(age):
                try:
                    age_nombre = float(age)

                    if age_nombre < 0 or age_nombre > 120:
                        ajouter_anomalie(
                            anomalies,
                            numero_ligne,
                            "age",
                            "Valeur impossible",
                            str(age),
                            "L'âge doit être entre 0 et 120 ans.",
                            "Vérifier l'âge dans la source officielle."
                        )

                except (ValueError, TypeError):
                    ajouter_anomalie(
                        anomalies,
                        numero_ligne,
                        "age",
                        "Format incorrect",
                        str(age),
                        "L'âge doit être numérique.",
                        "Convertir la valeur en nombre."
                    )

        if "commune" in df.columns:
            commune = ligne["commune"]

            if (
                not pd.isna(commune)
                and str(commune).strip() not in communes_valides
            ):
                ajouter_anomalie(
                    anomalies,
                    numero_ligne,
                    "commune",
                    "Valeur non reconnue",
                    str(commune),
                    "La commune n'est pas dans la liste de référence.",
                    "Choisir une commune valide."
                )

        if "telephone" in df.columns:
            telephone = ligne["telephone"]

            if not pd.isna(telephone):
                telephone = str(telephone).strip()

                if telephone.endswith(".0"):
                    telephone = telephone[:-2]

                if (
                    not telephone.isdigit()
                    or len(telephone) != 8
                ):
                    ajouter_anomalie(
                        anomalies,
                        numero_ligne,
                        "telephone",
                        "Format incorrect",
                        telephone,
                        "Le numéro doit contenir 8 chiffres.",
                        "Vérifier le numéro de téléphone."
                    )

        if "date_inscription" in df.columns:
            date_valeur = ligne["date_inscription"]

            if not pd.isna(date_valeur):
                date_convertie = pd.to_datetime(
                    date_valeur,
                    errors="coerce"
                )

                if pd.isna(date_convertie):
                    ajouter_anomalie(
                        anomalies,
                        numero_ligne,
                        "date_inscription",
                        "Date invalide",
                        str(date_valeur),
                        "La date n'est pas reconnue.",
                        "Corriger au format AAAA-MM-JJ."
                    )

    if "identifiant" in df.columns:
        doublons = df.duplicated(
            subset=["identifiant"],
            keep=False
        )

        for index in df.index[doublons]:
            ajouter_anomalie(
                anomalies,
                index + 2,
                "identifiant",
                "Identifiant dupliqué",
                str(df.loc[index, "identifiant"]),
                "Cet identifiant apparaît plusieurs fois.",
                "Conserver une seule fiche après vérification."
            )

    for colonne in df.columns:
        if df[colonne].isna().all():
            ajouter_anomalie(
                anomalies,
                0,
                colonne,
                "Colonne vide",
                "",
                "La colonne ne contient aucune donnée.",
                "Supprimer ou compléter la colonne."
            )

    noms_normalises = {}

    for colonne in df.columns:
        nom = re.sub(
            r"[^a-z0-9]",
            "",
            str(colonne).lower()
        )

        if nom in noms_normalises:
            ajouter_anomalie(
                anomalies,
                1,
                colonne,
                "Colonne similaire",
                str(colonne),
                "Deux colonnes ont des noms très similaires.",
                "Renommer les colonnes."
            )

        noms_normalises[nom] = colonne

    return pd.DataFrame(anomalies)


def analyser_url(url):
    url = url.strip()

    try:
        adresse = urlparse(url)

        if adresse.scheme not in {"http", "https"}:
            return None, (
                "L'URL doit commencer par http:// ou https://"
            )

        if not adresse.netloc:
            return None, "L'URL semble incomplète."

        reponse = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "DataClean-Djibouti/1.0"
            }
        )

        reponse.raise_for_status()

        contenu = reponse.text[:2_000_000]

        soup = BeautifulSoup(
            contenu,
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

        motifs = [
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
            for motif in motifs
            if motif in texte_minuscule
        ]

        if len(indices) == 0:
            score = 5
            decision = "AUTORISER"
            explication = (
                "Aucun indice évident détecté dans le texte analysé."
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
                "Plusieurs indices potentiellement suspects ont été détectés."
            )

        resultat = {
            "Score": score,
            "Décision": decision,
            "Indices": indices,
            "Explication": explication,
            "Caractères analysés": len(texte)
        }

        return resultat, None

    except requests.exceptions.RequestException as erreur:
        return None, (
            f"Impossible d'accéder à cette URL : {erreur}"
        )


def afficher_analyse(df):
    rapport = analyser_donnees(df)

    total_anomalies = len(rapport)
    total_lignes = len(df)

    if total_anomalies == 0:
        lignes_concernees = 0
    else:
        lignes_concernees = rapport[
            rapport["Ligne"] > 0
        ]["Ligne"].nunique()

    if total_lignes > 0:
        score = max(
            0,
            round(
                100 * (
                    1 - lignes_concernees / total_lignes
                )
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
        st.metric(
            "Lignes",
            df.shape[0]
        )

    with col2:
        st.metric(
            "Colonnes",
            df.shape[1]
        )

    with col3:
        st.metric(
            "Anomalies",
            total_anomalies
        )

    with col4:
        st.metric(
            "Score de qualité",
            f"{score} %"
        )

    if total_anomalies == 0:
        st.success(
            "Aucune anomalie détectée dans ce fichier."
        )

    else:
        st.subheader("🚨 Rapport des anomalies")

        st.dataframe(
            rapport,
            use_container_width=True
        )

        resume = (
            rapport["Type"]
            .value_counts()
            .rename_axis("Type d'anomalie")
            .reset_index(name="Nombre")
        )

        st.subheader("📌 Résumé des anomalies")

        st.dataframe(
            resume,
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            anomalies_elevees = int(
                (
                    rapport["Niveau"] == "Élevé"
                ).sum()
            )

            st.metric(
                "Anomalies élevées",
                anomalies_elevees
            )

        with col2:
            st.metric(
                "Lignes concernées",
                lignes_concernees
            )

        with col3:
            st.metric(
                "Types d'erreurs",
                rapport["Type"].nunique()
            )

        csv_rapport = rapport.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Télécharger le rapport",
            data=csv_rapport,
            file_name="rapport_dataclean_djibouti.csv",
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
            "Aucune colonne statut trouvée."
        )


st.sidebar.title("🌍 DataClean Djibouti")
st.sidebar.write("Prototype d'analyse de données")
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
            DataClean détecte les valeurs manquantes,
            doublons, formats incorrects et valeurs impossibles.
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
    ]
)


if fichier is None:
    st.info(
        "Aucun fichier importé. "
        "Vous pouvez lancer la démonstration."
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
                    "DJ005",
                    "DJ006",
                    "DJ007"
                ],
                "nom": [
                    "Ahmed Ali",
                    "Fatou Hassan",
                    "Mohamed Omar",
                    "Mohamed Omar",
                    "Sahra Ismail",
                    None,
                    "Ali Hassan"
                ],
                "commune": [
                    "Djibouti",
                    "Balbala",
                    "Boulaos",
                    "Boulaos",
                    "Inconnu",
                    "Balbala",
                    "Djibouti"
                ],
                "age": [
                    28,
                    None,
                    145,
                    145,
                    32,
                    26,
                    -4
                ],
                "date_inscription": [
                    "2025-01-12",
                    "2025-02-30",
                    "2025-03-10",
                    "2025-03-10",
                    "2025-04-18",
                    "2025-05-02",
                    "2025-06-20"
                ],
                "telephone": [
                    "77881234",
                    "77881235",
                    None,
                    None,
                    "123",
                    "77881239",
                    "77881240"
                ],
                "statut": [
                    "Actif",
                    "Actif",
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
    "d'une page web publique."
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
                    f'{resultat_url["Score"]} %'
                )

            with col2:
                st.metric(
                    "Décision",
                    resultat_url["Décision"]
                )

            st.write(
                "**Explication :**",
                resultat_url["Explication"]
            )

            indices = resultat_url["Indices"]

            st.write(
                "**Indices détectés :**",
                ", ".join(indices)
                if indices
                else "Aucun"
            )

            st.write(
                "**Contenu analysé :**",
                (
                    f'{resultat_url["Caractères analysés"]:,} '
                    "caractères"
                )
            )
