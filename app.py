import io
import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st


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
        padding: 48px 42px;
        border-radius: 24px;
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white !important;
        font-size: 46px;
        margin-bottom: 12px;
    }

    .hero p {
        color: white !important;
        font-size: 20px;
        margin-bottom: 0;
    }

    .card {
        background-color: white;
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        min-height: 170px;
    }

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
        margin-top: 35px;
        margin-bottom: 12px;
    }

    .badge {
        display: inline-block;
        background-color: #e4f4f1;
        color: #007d70;
        padding: 7px 13px;
        border-radius: 20px;
        margin: 4px;
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
                            "L'âge doit être compris entre 0 et 120 ans.",
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

    return pd.DataFrame(anomalies)


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

    st.markdown(
        '<h2 class="section-title">📊 Tableau de bord</h2>',
        unsafe_allow_html=True
    )

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

        st.markdown(
            '<h3 class="section-title">📌 Résumé des anomalies</h3>',
            unsafe_allow_html=True
        )

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
                DataClean Djibouti aide les administrations, les institutions
                et les acteurs publics à identifier les erreurs présentes
                dans leurs jeux de données avant leur utilisation.
            </p>
            <p>
                Notre solution analyse les fichiers, détecte les anomalies,
                explique les problèmes et propose des actions de vérification.
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
                <h3>🎯 Notre objectif</h3>
                <p>
                    Améliorer la qualité des données publiques et renforcer
                    la confiance dans les indicateurs utilisés pour la décision.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>🤖 Notre approche</h3>
                <p>
                    Combiner des règles de contrôle, l'analyse statistique
                    et des explications compréhensibles par les utilisateurs.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <h3>🇩🇯 Notre impact</h3>
                <p>
                    Contribuer à une administration numérique plus efficace,
                    plus transparente et mieux adaptée au contexte djiboutien.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<h2 class="section-title">Pourquoi DataClean ?</h2>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>Le problème</h3>
                <p>
                    Les bases de données peuvent contenir des doublons,
                    des informations manquantes, des formats invalides
                    ou des valeurs incohérentes.
                </p>
                <p>
                    Ces problèmes peuvent fausser les statistiques
                    et réduire la qualité des décisions publiques.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>La réponse</h3>
                <p>
                    DataClean fournit une analyse rapide, structurée
                    et explicable afin d'aider les agents à vérifier
                    et améliorer leurs données.
                </p>
                <p>
                    L'outil conserve les données originales et propose
                    des actions qui doivent être validées par un humain.
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

    st.write(
        "DataClean Djibouti répond à un besoin concret : "
        "améliorer la qualité des données utilisées par les organisations "
        "publiques et les acteurs de la transformation numérique."
    )

    objectifs = [
        (
            "Fiabiliser les données",
            "Identifier rapidement les erreurs qui peuvent fausser les indicateurs."
        ),
        (
            "Faciliter le travail des agents",
            "Réduire le temps consacré aux contrôles manuels répétitifs."
        ),
        (
            "Améliorer la décision",
            "Fournir des indicateurs fiables et un tableau de bord compréhensible."
        ),
        (
            "Renforcer la gouvernance",
            "Favoriser des données mieux documentées, traçables et contrôlées."
        ),
        (
            "Respecter la confidentialité",
            "Utiliser des données synthétiques, publiques ou anonymisées."
        ),
        (
            "Préparer le déploiement local",
            "Proposer une solution réaliste dans le contexte djiboutien."
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
            "📂 Importation de fichiers",
            "Import de fichiers CSV, Excel, JSON et ODS."
        ),
        (
            "🔎 Valeurs manquantes",
            "Repérage des cellules vides ou incomplètes."
        ),
        (
            "🔁 Doublons",
            "Détection des identifiants ou lignes répétées."
        ),
        (
            "📅 Formats invalides",
            "Contrôle des dates, numéros de téléphone et valeurs numériques."
        ),
        (
            "⚠️ Valeurs impossibles",
            "Détection des valeurs hors limites, comme un âge négatif ou supérieur à 120 ans."
        ),
        (
            "📊 Score de qualité",
            "Calcul d'un score synthétique pour apprécier l'état général du fichier."
        ),
        (
            "💡 Explications",
            "Chaque anomalie est accompagnée d'une explication claire."
        ),
        (
            "✅ Actions proposées",
            "Le système propose une correction ou une vérification humaine."
        ),
        (
            "⬇️ Rapport téléchargeable",
            "Export du rapport complet au format CSV."
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
        "La solution est conçue pour les organisations qui produisent, "
        "utilisent ou publient des données."
    )

    cibles = [
        "Administrations publiques",
        "Établissements publics",
        "Collectivités et services locaux",
        "Organisations de développement",
        "Chercheurs et analystes",
        "PME et startups numériques",
        "Responsables de bases de données",
        "Agents chargés du suivi-évaluation"
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
                Un service public reçoit un fichier contenant des dossiers
                administratifs. Avant de calculer ses statistiques, l'agent
                charge le fichier dans DataClean, examine les anomalies,
                vérifie les corrections proposées et télécharge le rapport.
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
            "L'utilisateur charge un fichier public, synthétique ou anonymisé."
        ),
        (
            "2",
            "Analyser",
            "DataClean examine la structure et le contenu du fichier."
        ),
        (
            "3",
            "Détecter",
            "Les valeurs manquantes, doublons, incohérences et formats invalides sont identifiés."
        ),
        (
            "4",
            "Expliquer",
            "Chaque problème est présenté avec son niveau et son explication."
        ),
        (
            "5",
            "Vérifier",
            "L'agent examine les corrections proposées avant toute modification."
        ),
        (
            "6",
            "Décider",
            "Les indicateurs propres peuvent ensuite être utilisés pour l'analyse."
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
        "N'utilisez pas de données personnelles réelles dans cette démonstration."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>Types de données autorisés</h3>
                <p>
                    Données synthétiques, données publiques ou données
                    anonymisées produites pour la démonstration.
                </p>
                <p>
                    Les exemples utilisés par DataClean ne représentent
                    pas de personnes réelles.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>Principe de validation humaine</h3>
                <p>
                    DataClean ne modifie pas automatiquement les données
                    originales. Il propose des corrections qui doivent
                    être vérifiées par un agent compétent.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="card">
            <h3>Traçabilité</h3>
            <p>
                Chaque fichier analysé peut être associé à une empreinte
                technique afin de faciliter le suivi de la démonstration
                sans afficher le contenu des données.
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
            <h3>DataClean Djibouti</h3>
            <p>
                DataClean Djibouti est un prototype d'aide à la gouvernance
                des données publiques. Il a été conçu pour montrer comment
                l'intelligence artificielle et l'analyse automatisée peuvent
                contribuer à une meilleure qualité des données.
            </p>
            <p>
                Le projet s'inscrit dans une démarche de transformation
                numérique, de modernisation administrative et de prise
                de décision fondée sur des informations plus fiables.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Version", "Prototype 1.0")

    with col2:
        st.metric("Pays cible", "Djibouti")

    with col3:
        st.metric("Données", "Synthétiques")


def afficher_contact():
    st.markdown(
        '<h1 class="section-title">📩 Contact et démonstration</h1>',
        unsafe_allow_html=True
    )

    st.write(
        "Pour une présentation, une démonstration ou une collaboration, "
        "utilisez les coordonnées de l'équipe du projet."
    )

    st.info(
        "Cette application est une démonstration. "
        "Les données confidentielles ne doivent pas être importées."
    )

    with st.form("formulaire_contact"):
        nom = st.text_input("Votre nom")
        email = st.text_input("Votre adresse e-mail")
        message = st.text_area("Votre message")

        envoyer = st.form_submit_button(
            "Envoyer le message"
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

    st.markdown(
        """
        <div class="card">
            <p>🏠 Accueil — Présentation générale de DataClean.</p>
            <p>🎯 Objectifs — Problème traité et objectifs du projet.</p>
            <p>⚙️ Fonctionnalités — Services proposés par la solution.</p>
            <p>👥 Public cible — Utilisateurs et organisations concernés.</p>
            <p>🔄 Méthode — Étapes d'utilisation de l'outil.</p>
            <p>📊 Analyse — Importation et contrôle d'un fichier.</p>
            <p>🔐 Données — Confidentialité, sécurité et traçabilité.</p>
            <p>ℹ️ À propos — Présentation du prototype.</p>
            <p>📩 Contact — Formulaire de démonstration.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.sidebar.title("🌍 DataClean Djibouti")
st.sidebar.caption("Prototype de gouvernance des données")
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

elif page == "Données et confidentialité":
    afficher_donnees()

elif page == "À propos":
    afficher_a_propos()

elif page == "Contact":
    afficher_contact()

elif page == "Plan du site":
    afficher_plan_du_site()

elif page == "Analyser un fichier":
    st.markdown(
        """
        <div class="hero">
            <h1>📊 Analyseur de données</h1>
            <p>
                Identifiez les anomalies et obtenez un rapport explicable.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    fichier = st.file_uploader(
        "📂 Choisissez un fichier CSV, Excel, JSON ou ODS",
        type=[
            "csv",
            "xlsx",
            "json",
            "ods"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        charger_demo = st.button(
            "🧪 Charger les données de démonstration"
        )

    with col2:
        supprimer_donnees = st.button(
            "🗑️ Réinitialiser"
        )

    if supprimer_donnees:
        if "donnees" in st.session_state:
            del st.session_state["donnees"]

        st.success(
            "Les données de démonstration ont été supprimées."
        )
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


st.markdown(
    f"""
    <div class="footer">
        <h3>🇩🇯 DataClean Djibouti</h3>
        <p>
            Qualité des données publiques • Innovation •
            Transformation numérique
        </p>
        <p>
            Prototype présenté pour démontrer une solution
            réaliste et déployable dans le contexte djiboutien.
        </p>
        <p>
            Dernière mise à jour : {datetime.now().strftime("%d/%m/%Y")}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
