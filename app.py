import hashlib
import io
from datetime import datetime

import pandas as pd
import streamlit as st
from sklearn.ensemble import IsolationForest


st.set_page_config(
    page_title="DataClean Djibouti",
    page_icon="🇩🇯",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f8fc;
        color: #172033;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #006bb6, #00a896);
        padding: 45px;
        border-radius: 24px;
        color: white;
        margin-bottom: 25px;
    }

    .hero h1,
    .hero p {
        color: white !important;
    }

    .hero h1 {
        font-size: 44px;
        margin-bottom: 12px;
    }

    .hero p {
        font-size: 19px;
        margin-bottom: 0;
    }

    .card {
        background-color: white;
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        min-height: 150px;
    }

    .card h2,
    .card h3 {
        color: #006bb6 !important;
        margin-top: 0;
    }

    .card p {
        color: #26364d !important;
        line-height: 1.6;
    }

    .section-title {
        color: #006bb6 !important;
        margin-top: 30px;
    }

    .badge {
        display: inline-block;
        background-color: #e4f4f1;
        color: #007d70;
        padding: 8px 14px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 600;
    }

    .footer {
        background-color: #202330;
        color: white;
        padding: 28px;
        border-radius: 18px;
        margin-top: 40px;
    }

    .footer h3,
    .footer p {
        color: white !important;
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
    correction,
    niveau="Moyen"
):
    anomalies.append(
        {
            "Ligne": ligne,
            "Colonne": colonne,
            "Type": type_anomalie,
            "Valeur": valeur,
            "Explication": explication,
            "Correction proposée": correction,
            "Niveau": niveau
        }
    )


def lire_fichier(fichier):
    nom = fichier.name.lower()
    contenu = fichier.getvalue()

    if nom.endswith(".csv"):
        try:
            return pd.read_csv(
                io.BytesIO(contenu)
            )
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


def creer_donnees_demo():
    return pd.DataFrame(
        {
            "identifiant": [
                "DJ001",
                "DJ002",
                "DJ003",
                "DJ003",
                "DJ005",
                "DJ006",
                "DJ007",
                "DJ008",
                "DJ009",
                "DJ010"
            ],
            "nom": [
                "Ahmed Ali",
                "Fatou Hassan",
                "Mohamed Omar",
                "Mohamed Omar",
                "Sahra Ismail",
                None,
                "Ali Hassan",
                "Hawa Omar",
                "Omar Said",
                "Amina Yusuf"
            ],
            "commune": [
                "Djibouti",
                "Balbala",
                "Boulaos",
                "Boulaos",
                "Inconnu",
                "Balbala",
                "Djibouti",
                "Balbala",
                "Boulaos",
                "Djibouti"
            ],
            "age": [
                28,
                None,
                145,
                145,
                32,
                26,
                -4,
                31,
                29,
                200
            ],
            "revenu_mensuel": [
                85000,
                90000,
                87000,
                87000,
                92000,
                88000,
                91000,
                89500,
                90500,
                1500000
            ],
            "date_inscription": [
                "2025-01-12",
                "2025-02-30",
                "2025-03-10",
                "2025-03-10",
                "2025-04-18",
                "2025-05-02",
                "2025-06-20",
                "2025-07-01",
                "2025-07-05",
                "2025-07-10"
            ],
            "telephone": [
                "77881234",
                "77881235",
                None,
                None,
                "123",
                "77881239",
                "77881240",
                "77881241",
                "77881242",
                "77881243"
            ],
            "statut": [
                "Actif",
                "Actif",
                "Actif",
                "Actif",
                "Inactif",
                "Inactif",
                "Actif",
                "Actif",
                "Actif",
                "Actif"
            ]
        }
    )


def analyser_regles(df):
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
                    "Compléter la valeur après vérification.",
                    "Moyen"
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
                            "L'âge doit être compris entre 0 et 120 ans.",
                            "Vérifier l'âge dans la source officielle.",
                            "Élevé"
                        )

                except (ValueError, TypeError):
                    ajouter_anomalie(
                        anomalies,
                        numero_ligne,
                        "age",
                        "Format incorrect",
                        str(age),
                        "L'âge doit être numérique.",
                        "Convertir la valeur en nombre.",
                        "Élevé"
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
                    "Choisir une commune valide.",
                    "Moyen"
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
                        "Vérifier le numéro de téléphone.",
                        "Élevé"
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
                        "Corriger au format AAAA-MM-JJ.",
                        "Élevé"
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
                "Conserver une seule fiche après vérification.",
                "Élevé"
            )

    return pd.DataFrame(anomalies)


def analyser_isolation_forest(df):
    resultat = df.copy()
    anomalies = []

    colonnes_numeriques = list(
        resultat.select_dtypes(
            include="number"
        ).columns
    )

    if len(colonnes_numeriques) == 0:
        return resultat, pd.DataFrame(anomalies), []

    donnees_numeriques = resultat[
        colonnes_numeriques
    ].copy()

    donnees_numeriques = donnees_numeriques.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    donnees_numeriques = donnees_numeriques.apply(
        pd.to_numeric,
        errors="coerce"
    )

    donnees_numeriques = donnees_numeriques.fillna(
        donnees_numeriques.median()
    )

    donnees_numeriques = donnees_numeriques.fillna(0)

    if len(donnees_numeriques) < 5:
        return resultat, pd.DataFrame(anomalies), colonnes_numeriques

    contamination = min(
        0.20,
        max(
            0.05,
            1 / len(donnees_numeriques)
        )
    )

    modele = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42
    )

    predictions = modele.fit_predict(
        donnees_numeriques
    )

    scores = modele.decision_function(
        donnees_numeriques
    )

    resultat["Score IA"] = scores.round(4)
    resultat["Anomalie IA"] = [
        "Oui"
        if prediction == -1
        else "Non"
        for prediction in predictions
    ]

    colonnes_fondamentales = [
        colonne
        for colonne in colonnes_numeriques
        if colonne in resultat.columns
    ]

    for position, prediction in enumerate(predictions):
        if prediction == -1:
            index = resultat.index[position]
            numero_ligne = index + 2

            valeurs = []

            for colonne in colonnes_fondamentales:
                valeurs.append(
                    f"{colonne}={resultat.loc[index, colonne]}"
                )

            ajouter_anomalie(
                anomalies,
                numero_ligne,
                ", ".join(colonnes_fondamentales),
                "Anomalie statistique IA",
                "; ".join(valeurs),
                (
                    "IsolationForest considère cette ligne comme "
                    "atypique par rapport aux autres lignes."
                ),
                (
                    "Vérifier les valeurs avec la source officielle "
                    "avant toute correction."
                ),
                "À vérifier"
            )

    return (
        resultat,
        pd.DataFrame(anomalies),
        colonnes_numeriques
    )


def analyser_complet(df, activer_ia=True):
    rapport_regles = analyser_regles(df)

    if not activer_ia:
        return df.copy(), rapport_regles, []

    donnees_ia, rapport_ia, colonnes_numeriques = (
        analyser_isolation_forest(df)
    )

    if rapport_regles.empty and rapport_ia.empty:
        rapport_final = pd.DataFrame()

    elif rapport_regles.empty:
        rapport_final = rapport_ia

    elif rapport_ia.empty:
        rapport_final = rapport_regles

    else:
        rapport_final = pd.concat(
            [
                rapport_regles,
                rapport_ia
            ],
            ignore_index=True
        )

    return (
        donnees_ia,
        rapport_final,
        colonnes_numeriques
    )


def nettoyer_donnees(df):
    nettoye = df.copy()
    modifications = []

    for colonne in nettoye.columns:
        if nettoye[colonne].dtype == "object":
            anciennes_valeurs = nettoye[colonne].copy()

            nettoye[colonne] = (
                nettoye[colonne]
                .astype("string")
                .str.strip()
            )

            changements = (
                anciennes_valeurs.astype("string")
                != nettoye[colonne]
            )

            for index in nettoye.index[
                changements.fillna(False)
            ]:
                modifications.append(
                    {
                        "Ligne": index + 2,
                        "Colonne": colonne,
                        "Ancienne valeur": str(
                            anciennes_valeurs.loc[index]
                        ),
                        "Nouvelle valeur": str(
                            nettoye.loc[index, colonne]
                        ),
                        "Raison": (
                            "Suppression des espaces inutiles"
                        )
                    }
                )

    if "commune" in nettoye.columns:
        correspondances = {
            "djibouti ville": "Djibouti",
            "djibouti-ville": "Djibouti",
            "balbala": "Balbala",
            "boulaos": "Boulaos",
            "ras dika": "Ras-Dika"
        }

        for index, valeur in nettoye["commune"].items():
            if pd.isna(valeur):
                continue

            ancienne_valeur = str(valeur).strip()
            nouvelle_valeur = correspondances.get(
                ancienne_valeur.lower(),
                ancienne_valeur
            )

            if ancienne_valeur != nouvelle_valeur:
                nettoye.loc[index, "commune"] = nouvelle_valeur

                modifications.append(
                    {
                        "Ligne": index + 2,
                        "Colonne": "commune",
                        "Ancienne valeur": ancienne_valeur,
                        "Nouvelle valeur": nouvelle_valeur,
                        "Raison": (
                            "Harmonisation du nom de la commune"
                        )
                    }
                )

    if "telephone" in nettoye.columns:
        anciennes_valeurs = nettoye["telephone"].copy()

        nettoye["telephone"] = (
            nettoye["telephone"]
            .astype("string")
            .str.replace(
                r"\.0$",
                "",
                regex=True
            )
            .str.replace(
                r"\s+",
                "",
                regex=True
            )
        )

        changements = (
            anciennes_valeurs.astype("string")
            != nettoye["telephone"]
        )

        for index in nettoye.index[
            changements.fillna(False)
        ]:
            modifications.append(
                {
                    "Ligne": index + 2,
                    "Colonne": "telephone",
                    "Ancienne valeur": str(
                        anciennes_valeurs.loc[index]
                    ),
                    "Nouvelle valeur": str(
                        nettoye.loc[index, "telephone"]
                    ),
                    "Raison": (
                        "Normalisation du téléphone"
                    )
                }
            )

    if "identifiant" in nettoye.columns:
        indices_doublons = nettoye.index[
            nettoye.duplicated(
                subset=["identifiant"],
                keep="first"
            )
        ]

        for index in indices_doublons:
            modifications.append(
                {
                    "Ligne": index + 2,
                    "Colonne": "identifiant",
                    "Ancienne valeur": str(
                        nettoye.loc[index, "identifiant"]
                    ),
                    "Nouvelle valeur": "Ligne supprimée",
                    "Raison": (
                        "Suppression contrôlée d'un doublon"
                    )
                }
            )

        nettoye = nettoye.drop_duplicates(
            subset=["identifiant"],
            keep="first"
        )

    journal = pd.DataFrame(modifications)

    return nettoye, journal


def afficher_analyse(df):
    activer_ia = st.checkbox(
        "🤖 Activer la détection intelligente IsolationForest",
        value=True
    )

    donnees_analysees, rapport, colonnes_ia = (
        analyser_complet(
            df,
            activer_ia=activer_ia
        )
    )

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

    st.markdown(
        '<h2 class="section-title">📊 Tableau de bord</h2>',
        unsafe_allow_html=True
    )

    st.dataframe(
        donnees_analysees,
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

    if activer_ia:
        if colonnes_ia:
            st.info(
                "Colonnes analysées par IA : "
                + ", ".join(colonnes_ia)
            )
        else:
            st.warning(
                "Aucune colonne numérique disponible "
                "pour l'analyse IA."
            )

    if total_anomalies == 0:
        st.success(
            "Aucune anomalie détectée."
        )

    else:
        st.markdown(
            '<h3 class="section-title">🚨 Rapport des anomalies</h3>',
            unsafe_allow_html=True
        )

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

        st.subheader("📌 Résumé")

        st.dataframe(
            resume,
            use_container_width=True
        )

        csv_rapport = rapport.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Télécharger le rapport",
            data=csv_rapport,
            file_name="rapport_anomalies.csv",
            mime="text/csv",
            key="telecharger_rapport"
        )

    st.markdown(
        '<h3 class="section-title">🛠️ Nettoyage contrôlé</h3>',
        unsafe_allow_html=True
    )

    st.write(
        "Le fichier original reste inchangé. "
        "Une copie nettoyée sera générée."
    )

    if st.button(
        "✨ Générer une version nettoyée",
        key="bouton_nettoyage"
    ):
        donnees_nettoyees, journal = nettoyer_donnees(
            df
        )

        st.session_state["donnees_nettoyees"] = (
            donnees_nettoyees
        )

        st.session_state["journal_modifications"] = (
            journal
        )

    if "donnees_nettoyees" in st.session_state:
        donnees_nettoyees = st.session_state[
            "donnees_nettoyees"
        ]

        journal = st.session_state[
            "journal_modifications"
        ]

        st.success(
            "Une version nettoyée a été générée."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Lignes avant",
                len(df)
            )

        with col2:
            st.metric(
                "Lignes après",
                len(donnees_nettoyees)
            )

        st.dataframe(
            donnees_nettoyees,
            use_container_width=True
        )

        if journal.empty:
            st.info(
                "Aucune modification automatique effectuée."
            )

        else:
            st.subheader("📝 Journal des modifications")

            st.dataframe(
                journal,
                use_container_width=True
            )

            csv_journal = journal.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "⬇️ Télécharger le journal",
                data=csv_journal,
                file_name="journal_modifications.csv",
                mime="text/csv",
                key="telecharger_journal"
            )

        csv_nettoye = donnees_nettoyees.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Télécharger le fichier nettoyé",
            data=csv_nettoye,
            file_name="donnees_nettoyees.csv",
            mime="text/csv",
            key="telecharger_nettoye"
        )

    st.markdown(
        '<h3 class="section-title">📈 Répartition des statuts</h3>',
        unsafe_allow_html=True
    )

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

    empreinte = hashlib.sha256(
        pd.util.hash_pandas_object(
            df,
            index=True
        ).values
    ).hexdigest()[:16]

    st.caption(
        f"Traçabilité : empreinte du fichier analysé = {empreinte}"
    )


def afficher_accueil():
    st.markdown(
        """
        <div class="hero">
            <h1>🇩🇯 DataClean Djibouti</h1>
            <p>
                Une solution intelligente pour améliorer la qualité,
                la fiabilité et la gouvernance des données publiques.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <h2>Des données fiables pour de meilleures décisions</h2>
            <p>
                DataClean Djibouti aide les administrations et institutions
                à identifier les erreurs présentes dans leurs fichiers.
            </p>
            <p>
                La solution combine des règles de contrôle et un modèle
                IsolationForest pour détecter les lignes atypiques.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>🎯 Objectif</h3>
                <p>
                    Améliorer la qualité des données publiques.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>🤖 Intelligence</h3>
                <p>
                    Repérer les comportements numériques atypiques.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <h3>📊 Résultat</h3>
                <p>
                    Produire un rapport clair et téléchargeable.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


def afficher_objectifs():
    st.markdown(
        '<h1 class="section-title">🎯 Objectifs du projet</h1>',
        unsafe_allow_html=True
    )

    objectifs = [
        (
            "Fiabiliser les données",
            "Identifier les erreurs avant l'utilisation des fichiers."
        ),
        (
            "Automatiser les contrôles",
            "Réduire le temps consacré aux vérifications manuelles."
        ),
        (
            "Détecter les anomalies",
            "Combiner règles métier et détection statistique."
        ),
        (
            "Améliorer la décision",
            "Fournir des données plus propres aux analystes."
        ),
        (
            "Renforcer la traçabilité",
            "Conserver un rapport et un journal des modifications."
        ),
        (
            "Respecter la confidentialité",
            "Utiliser des données publiques ou anonymisées."
        )
    ]

    for debut in range(0, len(objectifs), 3):
        colonnes = st.columns(3)

        for position, colonne in enumerate(colonnes):
            if debut + position < len(objectifs):
                titre, texte = objectifs[debut + position]

                with colonne:
                    st.markdown(
                        f"""
                        <div class="card">
                            <h3>{titre}</h3>
                            <p>{texte}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


def afficher_fonctionnalites():
    st.markdown(
        '<h1 class="section-title">⚙️ Fonctionnalités</h1>',
        unsafe_allow_html=True
    )

    fonctionnalites = [
        (
            "📂 Importation",
            "CSV, Excel, JSON et ODS."
        ),
        (
            "🔎 Contrôle des règles",
            "Valeurs manquantes, doublons et formats invalides."
        ),
        (
            "🤖 IsolationForest",
            "Détection des lignes numériques atypiques."
        ),
        (
            "📊 Score de qualité",
            "Indicateur synthétique de l'état du fichier."
        ),
        (
            "🛠️ Nettoyage",
            "Génération d'une copie nettoyée."
        ),
        (
            "📝 Journal",
            "Historique des modifications proposées."
        ),
        (
            "⬇️ Rapports",
            "Téléchargement des résultats en CSV."
        ),
        (
            "🔐 Traçabilité",
            "Empreinte technique du fichier analysé."
        ),
        (
            "✅ Validation humaine",
            "Les corrections doivent être vérifiées."
        )
    ]

    for debut in range(0, len(fonctionnalites), 3):
        colonnes = st.columns(3)

        for position, colonne in enumerate(colonnes):
            if debut + position < len(fonctionnalites):
                titre, texte = fonctionnalites[debut + position]

                with colonne:
                    st.markdown(
                        f"""
                        <div class="card">
                            <h3>{titre}</h3>
                            <p>{texte}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


def afficher_cible():
    st.markdown(
        '<h1 class="section-title">👥 Public cible</h1>',
        unsafe_allow_html=True
    )

    st.write(
        "DataClean Djibouti s'adresse aux organisations qui produisent, "
        "gèrent ou utilisent des données."
    )

    cibles = [
        "Administrations publiques",
        "Établissements publics",
        "Collectivités locales",
        "Services de suivi-évaluation",
        "Analystes de données",
        "Chercheurs",
        "ONG",
        "Startups numériques"
    ]

    for cible in cibles:
        st.markdown(
            f'<span class="badge">{cible}</span>',
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="card">
            <h3>Exemple d'utilisation</h3>
            <p>
                Un agent charge un fichier administratif, observe les erreurs
                détectées par les règles et par IsolationForest, vérifie les
                résultats, puis télécharge le rapport.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def afficher_methode():
    st.markdown(
        '<h1 class="section-title">🔄 Comment ça marche ?</h1>',
        unsafe_allow_html=True
    )

    etapes = [
        (
            "1",
            "Importer",
            "Charger un fichier synthétique, public ou anonymisé."
        ),
        (
            "2",
            "Contrôler",
            "Appliquer les règles de qualité."
        ),
        (
            "3",
            "Apprendre",
            "IsolationForest observe les colonnes numériques."
        ),
        (
            "4",
            "Détecter",
            "Identifier les lignes statistiquement atypiques."
        ),
        (
            "5",
            "Expliquer",
            "Présenter le type et la cause du problème."
        ),
        (
            "6",
            "Exporter",
            "Télécharger le rapport et la copie nettoyée."
        )
    ]

    for debut in range(0, len(etapes), 3):
        colonnes = st.columns(3)

        for position, colonne in enumerate(colonnes):
            if debut + position < len(etapes):
                numero, titre, texte = etapes[debut + position]

                with colonne:
                    st.markdown(
                        f"""
                        <div class="card">
                            <h3>{numero}. {titre}</h3>
                            <p>{texte}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


def afficher_donnees():
    st.markdown(
        '<h1 class="section-title">🔐 Données et confidentialité</h1>',
        unsafe_allow_html=True
    )

    st.warning(
        "N'importez pas de données personnelles réelles."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>Données recommandées</h3>
                <p>
                    Données synthétiques, publiques ou anonymisées.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>Validation humaine</h3>
                <p>
                    Une anomalie détectée par l'IA n'est pas forcément
                    une erreur. Elle doit être vérifiée par un agent.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="card">
            <h3>Limites d'IsolationForest</h3>
            <p>
                Le modèle détecte des comportements atypiques dans les
                colonnes numériques. Il ne connaît pas automatiquement
                la vérité administrative et peut produire des faux positifs.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def afficher_a_propos():
    st.markdown(
        '<h1 class="section-title">ℹ️ À propos du projet</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <h2>DataClean Djibouti</h2>
            <p>
                DataClean Djibouti est un prototype d'aide à la qualité
                et à la gouvernance des données publiques.
            </p>
            <p>
                Il combine des règles métier explicables et une méthode
                d'apprentissage automatique non supervisé.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Version", "Prototype 2.0")

    with col2:
        st.metric("Pays cible", "Djibouti")

    with col3:
        st.metric("Modèle IA", "IsolationForest")


def afficher_contact():
    st.markdown(
        '<h1 class="section-title">📩 Contact</h1>',
        unsafe_allow_html=True
    )

    st.write(
        "Cette page permet de demander une présentation "
        "ou une démonstration du projet."
    )

    with st.form("formulaire_contact"):
        nom = st.text_input("Nom")
        email = st.text_input("Adresse e-mail")
        message = st.text_area("Message")

        envoyer = st.form_submit_button(
            "Envoyer"
        )

        if envoyer:
            if not nom or not email or not message:
                st.warning(
                    "Veuillez remplir tous les champs."
                )
            else:
                st.success(
                    "Message enregistré pour la démonstration."
                )


def afficher_plan_du_site():
    st.markdown(
        '<h1 class="section-title">🗺️ Plan du site</h1>',
        unsafe_allow_html=True
    )

    sections = [
        "Accueil",
        "Objectifs",
        "Fonctionnalités",
        "Public cible",
        "Comment ça marche",
        "Analyser un fichier",
        "Données et confidentialité",
        "À propos",
        "Contact",
        "Plan du site"
    ]

    for section in sections:
        st.markdown(
            f"- **{section}**"
        )


def afficher_analyseur():
    st.markdown(
        """
        <div class="hero">
            <h1>📊 Analyseur intelligent</h1>
            <p>
                Détection des erreurs par règles et IsolationForest.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    fichier_demo = creer_donnees_demo().to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Télécharger un fichier exemple",
        data=fichier_demo,
        file_name="exemple_dataclean_djibouti.csv",
        mime="text/csv",
        key="telecharger_exemple"
    )

    st.markdown("---")

    fichier = st.file_uploader(
        "📂 Choisissez un fichier CSV, Excel, JSON ou ODS",
        type=[
            "csv",
            "xlsx",
            "json",
            "ods"
        ],
        key="chargeur_fichier"
    )

    col1, col2 = st.columns(2)

    with col1:
        charger_demo = st.button(
            "🧪 Charger les données de démonstration"
        )

    with col2:
        reinitialiser = st.button(
            "🗑️ Réinitialiser"
        )

    if reinitialiser:
        cles = [
            "donnees",
            "donnees_nettoyees",
            "journal_modifications"
        ]

        for cle in cles:
            if cle in st.session_state:
                del st.session_state[cle]

        st.rerun()

    if charger_demo:
        st.session_state["donnees"] = creer_donnees_demo()

    if fichier is not None:
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

    else:
        st.info(
            "Importez un fichier ou chargez les données de démonstration."
        )


st.sidebar.title("🌍 DataClean Djibouti")
st.sidebar.caption(
    "Prototype de gouvernance des données"
)
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Menu principal",
    [
        "Accueil",
        "Objectifs",
        "Fonctionnalités",
        "Public cible",
        "Comment ça marche",
        "Analyser un fichier",
        "Données et confidentialité",
        "À propos",
        "Contact",
        "Plan du site"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Utilisez uniquement des données publiques, "
    "synthétiques ou anonymisées."
)


if page == "Accueil":
    afficher_accueil()

elif page == "Objectifs":
    afficher_objectifs()

elif page == "Fonctionnalités":
    afficher_fonctionnalites()

elif page == "Public cible":
    afficher_cible()

elif page == "Comment ça marche":
    afficher_methode()

elif page == "Analyser un fichier":
    afficher_analyseur()

elif page == "Données et confidentialité":
    afficher_donnees()

elif page == "À propos":
    afficher_a_propos()

elif page == "Contact":
    afficher_contact()

elif page == "Plan du site":
    afficher_plan_du_site()


st.markdown(
    f"""
    <div class="footer">
        <h3>🇩🇯 DataClean Djibouti</h3>
        <p>
            Qualité des données publiques • Innovation •
            Transformation numérique
        </p>
        <p>
            Prototype utilisant des données publiques,
            synthétiques ou anonymisées.
        </p>
        <p>
            Mise à jour :
            {datetime.now().strftime("%d/%m/%Y")}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
