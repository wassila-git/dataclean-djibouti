import io
import re
import json
import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="DataClean Djibouti",
    page_icon="🇩🇯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# STYLE CSS
# ============================================================

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

    section[data-testid="stSidebar"] {
        background-color: #202330;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #ffffff;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label span {
        color: #ffffff !important;
    }

    .hero {
        background: linear-gradient(135deg, #006bb6, #00a896);
        padding: 42px;
        border-radius: 24px;
        color: white;
        margin-bottom: 28px;
    }

    .hero h1,
    .hero p {
        color: white !important;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 12px;
    }

    .hero p {
        font-size: 19px;
        margin-bottom: 0;
    }

    .card {
        background-color: #ffffff;
        color: #172033;
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }

    .card h2,
    .card h3 {
        color: #005a9c !important;
        margin-top: 0;
    }

    .card p {
        color: #26364d !important;
        line-height: 1.6;
    }

    .section-title {
        color: #005a9c !important;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    .badge {
        display: inline-block;
        background-color: #d8f3ee;
        color: #00695c !important;
        padding: 8px 14px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 700;
    }

    div.stButton > button {
        background-color: #006bb6 !important;
        color: #ffffff !important;
        border: 1px solid #00558f !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        min-height: 42px !important;
    }

    div.stButton > button:hover {
        background-color: #004f86 !important;
        color: #ffffff !important;
    }

    div[data-testid="stDownloadButton"] button {
        background-color: #006bb6 !important;
        color: #ffffff !important;
        border: 1px solid #00558f !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        min-height: 42px !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #004f86 !important;
        color: #ffffff !important;
    }

    div[data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 2px dashed #006bb6 !important;
        border-radius: 12px !important;
        padding: 14px !important;
    }

    div[data-testid="stFileUploader"] *,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] span {
        color: #172033 !important;
    }

    div[data-testid="stFileUploader"] button {
        background-color: #006bb6 !important;
        color: #ffffff !important;
        border: none !important;
    }

    [data-testid="stMetricLabel"] {
        color: #26364d !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        color: #172033 !important;
        font-weight: 800 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #526174 !important;
    }

    div[data-testid="stAlert"] p {
        color: #172033 !important;
    }

    div[data-testid="stSuccess"] p {
        color: #14532d !important;
    }

    div[data-testid="stWarning"] p {
        color: #713f12 !important;
    }

    div[data-testid="stInfo"] p {
        color: #164e63 !important;
    }

    .footer {
        background-color: #202330;
        color: #ffffff;
        padding: 28px;
        border-radius: 18px;
        margin-top: 40px;
    }

    .footer h3,
    .footer p {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DONNÉES DE DÉMONSTRATION
# ============================================================

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
            "nom_organisation": [
                "Organisation A",
                "Organisation B",
                "Organisation C",
                "Organisation C",
                "Organisation D",
                "Organisation E",
                "Organisation F",
                "Organisation G",
                "Organisation H",
                "Organisation I"
            ],
            "secteur": [
                "Éducation",
                "Santé",
                "Administration",
                "Administration",
                "Transport",
                "Finance",
                "Éducation",
                "Santé",
                "Transport",
                "Finance"
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
            ],
            "date_mise_a_jour": [
                "2026-01-10",
                "2026-01-11",
                "2026-01-12",
                "2026-01-12",
                "2025-08-15",
                "2025-09-20",
                "2026-01-15",
                "2026-01-17",
                "2026-01-18",
                "2026-01-20"
            ]
        }
    )


# ============================================================
# LECTURE DES FICHIERS
# ============================================================

def lire_fichier(fichier):
    nom = fichier.name.lower()
    contenu = fichier.getvalue()

    if nom.endswith(".csv"):
        essais = ["utf-8", "utf-8-sig", "latin-1"]

        for encodage in essais:
            try:
                return pd.read_csv(
                    io.BytesIO(contenu),
                    encoding=encodage
                )
            except UnicodeDecodeError:
                continue

        raise ValueError(
            "Impossible de lire l'encodage du fichier CSV."
        )

    if nom.endswith(".xlsx") or nom.endswith(".xls"):
        return pd.read_excel(io.BytesIO(contenu))

    if nom.endswith(".json"):
        return pd.read_json(io.BytesIO(contenu))

    if nom.endswith(".ods"):
        return pd.read_excel(
            io.BytesIO(contenu),
            engine="odf"
        )

    raise ValueError(
        "Format non pris en charge."
    )


# ============================================================
# NETTOYAGE DES NOMS DE COLONNES
# ============================================================

def normaliser_nom_colonne(nom):
    nom = str(nom).strip().lower()
    nom = re.sub(r"\s+", "_", nom)
    nom = re.sub(r"[^a-z0-9_àâçéèêëîïôùûüÿ-]", "", nom)
    return nom


def normaliser_colonnes(df):
    resultat = df.copy()
    resultat.columns = [
        normaliser_nom_colonne(colonne)
        for colonne in resultat.columns
    ]
    return resultat


# ============================================================
# ANALYSE DES DONNÉES
# ============================================================

def analyser_donnees(df):
    total_lignes = len(df)
    total_colonnes = len(df.columns)

    valeurs_manquantes = int(df.isna().sum().sum())
    lignes_dupliquees = int(df.duplicated().sum())

    cellules_totales = total_lignes * total_colonnes

    if cellules_totales > 0:
        taux_completude = (
            (cellules_totales - valeurs_manquantes)
            / cellules_totales
        ) * 100
    else:
        taux_completude = 0

    resume_colonnes = pd.DataFrame(
        {
            "colonne": df.columns,
            "type": [
                str(df[colonne].dtype)
                for colonne in df.columns
            ],
            "valeurs_manquantes": [
                int(df[colonne].isna().sum())
                for colonne in df.columns
            ],
            "valeurs_uniques": [
                int(df[colonne].nunique(dropna=True))
                for colonne in df.columns
            ]
        }
    )

    return {
        "total_lignes": total_lignes,
        "total_colonnes": total_colonnes,
        "valeurs_manquantes": valeurs_manquantes,
        "lignes_dupliquees": lignes_dupliquees,
        "taux_completude": taux_completude,
        "resume_colonnes": resume_colonnes
    }


# ============================================================
# EMPREINTE DU FICHIER
# ============================================================

def calculer_empreinte(fichier):
    contenu = fichier.getvalue()
    return hashlib.sha256(contenu).hexdigest()[:16]


# ============================================================
# PAGE ACCUEIL
# ============================================================

def afficher_accueil():
    st.markdown(
        """
        <div class="hero">
            <h1>🌍 DataClean Djibouti</h1>
            <p>
                Prototype de gouvernance, de qualité et de
                traçabilité des données.
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
                <h3>📊 Qualité des données</h3>
                <p>
                    Détecter les valeurs manquantes, les doublons
                    et les incohérences dans les fichiers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>🔐 Traçabilité</h3>
                <p>
                    Générer une empreinte permettant d'identifier
                    le fichier analysé.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
                <h3>🇩🇯 Contexte djiboutien</h3>
                <p>
                    Proposer une solution simple pour améliorer
                    la gestion des données publiques.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="card">
            <h3>Comment utiliser l'application ?</h3>
            <p>
                Sélectionnez « Analyser un fichier » dans le menu
                à gauche, puis importez un fichier CSV, Excel,
                JSON ou ODS.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE OBJECTIFS
# ============================================================

def afficher_objectifs():
    st.markdown(
        '<h1 class="section-title">🎯 Objectifs du projet</h1>',
        unsafe_allow_html=True
    )

    objectifs = [
        "Améliorer la qualité des données.",
        "Faciliter la détection des erreurs.",
        "Identifier les doublons et les valeurs manquantes.",
        "Renforcer la traçabilité des fichiers.",
        "Sensibiliser à la gouvernance des données."
    ]

    for objectif in objectifs:
        st.success(objectif)


# ============================================================
# PAGE FONCTIONNALITÉS
# ============================================================

def afficher_fonctionnalites():
    st.markdown(
        '<h1 class="section-title">⚙️ Fonctionnalités</h1>',
        unsafe_allow_html=True
    )

    fonctionnalites = [
        ("Importation", "CSV, Excel, JSON et ODS."),
        ("Profilage", "Analyse des colonnes et des types."),
        ("Qualité", "Détection des valeurs manquantes."),
        ("Doublons", "Identification des lignes répétées."),
        ("Statuts", "Répartition des valeurs de statut."),
        ("Traçabilité", "Calcul d'une empreinte du fichier."),
        ("Export", "Téléchargement des résultats nettoyés.")
    ]

    for titre, description in fonctionnalites:
        st.markdown(
            f"""
            <div class="card">
                <h3>{titre}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PAGE PUBLIC CIBLE
# ============================================================

def afficher_public_cible():
    st.markdown(
        '<h1 class="section-title">👥 Public cible</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <h3>Administrations publiques</h3>
            <p>
                Pour améliorer la qualité des registres et des
                fichiers administratifs.
            </p>
        </div>

        <div class="card">
            <h3>Organisations et entreprises</h3>
            <p>
                Pour contrôler les fichiers avant leur utilisation
                dans un rapport ou une application.
            </p>
        </div>

        <div class="card">
            <h3>Étudiants et chercheurs</h3>
            <p>
                Pour comprendre les problèmes de qualité des données
                et les corriger.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE COMMENT ÇA MARCHE
# ============================================================

def afficher_comment_ca_marche():
    st.markdown(
        '<h1 class="section-title">❓ Comment ça marche ?</h1>',
        unsafe_allow_html=True
    )

    etapes = [
        "L'utilisateur importe un fichier.",
        "L'application lit les données.",
        "Les colonnes sont examinées.",
        "Les valeurs manquantes sont comptées.",
        "Les doublons sont identifiés.",
        "Les résultats sont affichés sous forme de tableaux et graphiques.",
        "L'utilisateur peut télécharger le fichier nettoyé."
    ]

    for numero, etape in enumerate(etapes, start=1):
        st.markdown(
            f"""
            <div class="card">
                <h3>Étape {numero}</h3>
                <p>{etape}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PAGE ANALYSEUR
# ============================================================

def afficher_analyseur():
    st.markdown(
        '<h1 class="section-title">📊 Analyseur intelligent</h1>',
        unsafe_allow_html=True
    )

    st.info(
        "Les fichiers doivent être publics, synthétiques "
        "ou anonymisés. Évitez les données personnelles sensibles."
    )

    fichier = st.file_uploader(
        "Choisissez un fichier à analyser",
        type=["csv", "xlsx", "xls", "json", "ods"],
        help=(
            "Formats acceptés : CSV, Excel, JSON et ODS."
        )
    )

    utiliser_demo = st.checkbox(
        "Utiliser les données de démonstration",
        value=False
    )

    if fichier is None and not utiliser_demo:
        st.markdown(
            """
            <div class="card">
                <h3>📁 Aucun fichier sélectionné</h3>
                <p>
                    Importez un fichier ou activez les données
                    de démonstration pour voir le fonctionnement
                    de l'analyseur.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    try:
        if fichier is not None:
            df_original = lire_fichier(fichier)
            nom_fichier = fichier.name
            empreinte = calculer_empreinte(fichier)
            source_demo = False
        else:
            df_original = creer_donnees_demo()
            nom_fichier = "donnees_demo.csv"
            contenu_demo = df_original.to_csv(
                index=False
            ).encode("utf-8")
            empreinte = hashlib.sha256(
                contenu_demo
            ).hexdigest()[:16]
            source_demo = True

        df = normaliser_colonnes(df_original)
        analyse = analyser_donnees(df)

    except Exception as erreur:
        st.error(
            f"Erreur lors de la lecture du fichier : {erreur}"
        )
        return

    if source_demo:
        st.warning(
            "Vous utilisez des données synthétiques de démonstration. "
            "Les résultats ne représentent pas des statistiques officielles."
        )
    else:
        st.success(
            f"Fichier chargé avec succès : {nom_fichier}"
        )

    st.markdown(
        '<h2 class="section-title">📌 Résumé général</h2>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Nombre de lignes",
            analyse["total_lignes"]
        )

    with col2:
        st.metric(
            "Nombre de colonnes",
            analyse["total_colonnes"]
        )

    with col3:
        st.metric(
            "Valeurs manquantes",
            analyse["valeurs_manquantes"]
        )

    with col4:
        st.metric(
            "Doublons",
            analyse["lignes_dupliquees"]
        )

    st.markdown(
        '<h2 class="section-title">📋 Aperçu des données</h2>',
        unsafe_allow_html=True
    )

    st.dataframe(
        df.head(100),
        use_container_width=True
    )

    st.markdown(
        '<h2 class="section-title">🔍 Profil des colonnes</h2>',
        unsafe_allow_html=True
    )

    st.dataframe(
        analyse["resume_colonnes"],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        '<h2 class="section-title">📈 Répartition des statuts dans le fichier</h2>',
        unsafe_allow_html=True
    )

    colonnes_statut = [
        colonne
        for colonne in df.columns
        if colonne in [
            "statut",
            "status",
            "etat",
            "état"
        ]
    ]

    if colonnes_statut:
        colonne_statut = colonnes_statut[0]

        compte_statuts = (
            df[colonne_statut]
            .fillna("Manquant")
            .astype(str)
            .value_counts()
        )

        st.bar_chart(
            compte_statuts,
            color="#006bb6"
        )

        if source_demo:
            st.caption(
                "Dans cet exemple synthétique, 8 lignes sont "
                "marquées « Actif » et 2 lignes « Inactif ». "
                "Avec un fichier réel, les chiffres dépendront "
                "de son contenu."
            )
        else:
            st.caption(
                "Ce graphique présente les valeurs de la colonne "
                "« statut » contenues dans le fichier analysé."
            )

    else:
        st.info(
            "Aucune colonne de statut n'a été trouvée dans ce fichier."
        )

    st.markdown(
        '<h2 class="section-title">⚠️ Contrôles de qualité</h2>',
        unsafe_allow_html=True
    )

    if analyse["valeurs_manquantes"] == 0:
        st.success(
            "Aucune valeur manquante détectée."
        )
    else:
        st.warning(
            f"{analyse['valeurs_manquantes']} valeur(s) "
            "manquante(s) détectée(s)."
        )

    if analyse["lignes_dupliquees"] == 0:
        st.success(
            "Aucune ligne dupliquée détectée."
        )
    else:
        st.warning(
            f"{analyse['lignes_dupliquees']} ligne(s) "
            "dupliquée(s) détectée(s)."
        )

    st.write(
        f"Taux de complétude : "
        f"{analyse['taux_completude']:.2f} %"
    )

    st.markdown(
        '<h2 class="section-title">🧹 Nettoyage</h2>',
        unsafe_allow_html=True
    )

    df_nettoye = df.copy()

    for colonne in df_nettoye.select_dtypes(
        include=["object"]
    ).columns:
        df_nettoye[colonne] = (
            df_nettoye[colonne]
            .astype("string")
            .str.strip()
        )

    df_nettoye = df_nettoye.drop_duplicates()

    st.write(
        f"Après nettoyage, le fichier contient "
        f"{len(df_nettoye)} ligne(s)."
    )

    st.markdown(
        '<h2 class="section-title">⬇️ Téléchargements</h2>',
        unsafe_allow_html=True
    )

    fichier_nettoye = df_nettoye.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    rapport = {
        "nom_fichier": nom_fichier,
        "date_analyse": datetime.now().isoformat(
            timespec="seconds"
        ),
        "nombre_lignes": analyse["total_lignes"],
        "nombre_colonnes": analyse["total_colonnes"],
        "valeurs_manquantes": analyse["valeurs_manquantes"],
        "doublons": analyse["lignes_dupliquees"],
        "taux_completude": round(
            analyse["taux_completude"],
            2
        ),
        "empreinte": empreinte,
        "donnees_synthetiques": source_demo
    }

    rapport_json = json.dumps(
        rapport,
        ensure_ascii=False,
        indent=4
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="⬇️ Télécharger le fichier nettoyé",
            data=fichier_nettoye,
            file_name="fichier_nettoye.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="⬇️ Télécharger le rapport",
            data=rapport_json,
            file_name="rapport_analyse.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown(
        f"""
        <div style="
            background-color: #e8f1f8;
            color: #26364d;
            padding: 14px 18px;
            border-radius: 8px;
            border-left: 5px solid #006bb6;
            margin-top: 20px;
        ">
            <strong>Traçabilité :</strong>
            empreinte du fichier analysé :
            <code style="color: #005a9c;">
                {empreinte}
            </code>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE DONNÉES ET CONFIDENTIALITÉ
# ============================================================

def afficher_confidentialite():
    st.markdown(
        '<h1 class="section-title">🔐 Données et confidentialité</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <h3>Bonnes pratiques</h3>
            <p>
                Utilisez uniquement des données publiques, synthétiques
                ou anonymisées.
            </p>
            <p>
                Ne téléversez pas de mots de passe, de numéros de
                téléphone, de documents d'identité ou de données
                médicales.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE À PROPOS
# ============================================================

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
                DataClean Djibouti est un prototype destiné à montrer
                comment une application simple peut aider à analyser
                la qualité et la traçabilité des données.
            </p>
            <p>
                Le prototype peut évoluer vers une solution adaptée
                aux besoins des administrations et organisations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE CONTACT
# ============================================================

def afficher_contact():
    st.markdown(
        '<h1 class="section-title">📞 Contact</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <h3>Nous contacter</h3>
            <p>
                Pour toute question ou suggestion concernant le
                prototype, contactez l'équipe du projet.
            </p>
        </div>
        """,
        unsafe_allow_html=True
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
                    "Votre message a été enregistré "
                    "pour la démonstration."
                )


# ============================================================
# PAGE PLAN DU SITE
# ============================================================

def afficher_plan_du_site():
    st.markdown(
        '<h1 class="section-title">🗺️ Plan du site</h1>',
        unsafe_allow_html=True
    )

    pages = [
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

    for page in pages:
        st.write(f"• {page}")


# ============================================================
# MENU LATÉRAL
# ============================================================

st.sidebar.markdown(
    """
    <h1>🌍 DataClean Djibouti</h1>
    <p>Prototype de gouvernance des données</p>
    """,
    unsafe_allow_html=True
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


# ============================================================
# AFFICHAGE DE LA PAGE SÉLECTIONNÉE
# ============================================================

if page == "Accueil":
    afficher_accueil()

elif page == "Objectifs":
    afficher_objectifs()

elif page == "Fonctionnalités":
    afficher_fonctionnalites()

elif page == "Public cible":
    afficher_public_cible()

elif page == "Comment ça marche":
    afficher_comment_ca_marche()

elif page == "Analyser un fichier":
    afficher_analyseur()

elif page == "Données et confidentialité":
    afficher_confidentialite()

elif page == "À propos":
    afficher_a_propos()

elif page == "Contact":
    afficher_contact()

elif page == "Plan du site":
    afficher_plan_du_site()


# ============================================================
# PIED DE PAGE
# ============================================================

st.markdown(
    """
    <div class="footer">
        <h3>DataClean Djibouti</h3>
        <p>
            Prototype de qualité, gouvernance et traçabilité
            des données.
        </p>
        <p>
            Projet académique — Données publiques, synthétiques
            ou anonymisées uniquement.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
