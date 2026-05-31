#  RC Gestion  — Plateforme Intelligente de Gestion Comptable et Fiscale

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=for-the-badge&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?style=for-the-badge&logo=sqlite)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange?style=for-the-badge&logo=scikit-learn)


**Plateforme web de gestion comptable, fiscale et sociale enrichie d'Intelligence Artificielle**

*Projet de Stage Technique — EST El Kelaa des Sraghna · Université Cadi Ayyad · 2025–2026*

</div>

---

##  Présentation

**RC Gestion** est une application web complète développée pour le bureau **RC Gestion** d'El Kelaa des Sraghna, spécialisé dans la création d'entreprises, la gestion comptable et les déclarations fiscales.

L'application centralise la gestion des clients, déclarations, comptabilité et paie, et intègre un **module d'Intelligence Artificielle** capable de prédire les risques de retard fiscal, prévoir le chiffre d'affaires et détecter les anomalies comptables.

---

##  Fonctionnalités

###  Gestion des Clients
- Gestion des **Personnes Physiques** (PP) et **Personnes Morales** (PM)
- Fiche client complète : CIN / RC / IF / Patente / ICE / secteur / régime fiscal
- Filtres avancés, export Excel, recherche en temps réel

###  Déclarations Fiscales
- Suivi TVA, IS, IR, CNSS, Patente
- Historique par client avec statuts (Déposée / En attente / En retard)
- Mise à jour rapide des statuts et montants payés
- Export Excel & PDF

###  Comptabilité
- Journal des opérations (Factures Vente/Achat, Notes de frais)
- Bilan simplifié automatique (Actif / Passif / Résultat)
- Calcul automatique TVA (HT → TVA → TTC)

###  Gestion de la Paie
- Simulateur de salaire avec calcul automatique :
  - CNSS salariale & patronale
  - AMO salariale & patronale
  - IR mensuel (barème marocain 2024)
- Bulletins de paie PDF téléchargeables
- Historique par employé

###  Création d'Entreprises
- Suivi des étapes : Statuts → RC → IF → Patente → ICE → CNSS → Compte bancaire
- Tableau de bord visuel de progression

###  Intelligence Artificielle
| Modèle | Fonctionnalité |
|--------|----------------|
| **Random Forest** | Prédiction du risque de retard fiscal par client |
| **Régression Linéaire** | Prévision du chiffre d'affaires mensuel |
| **Isolation Forest** | Détection d'anomalies sur les montants déclarés |

###  Rapports & Exports
- Rapport général PDF du cabinet
- Fiches clients PDF individuelles
- Export Excel multi-feuilles complet

---

##  Stack Technique

```
Backend & Data    →  Python 3.11 · SQLite · Pandas · NumPy
Machine Learning  →  Scikit-learn (RandomForest · LinearRegression · IsolationForest)
Interface Web     →  Streamlit · Plotly Express · Plotly Graph Objects
Exports           →  ReportLab (PDF) · OpenPyXL (Excel)
Base de données   →  SQLite3 (local, sans serveur)
```

---

##  Structure du Projet

```
RC_Gestion_/
│
├── app.py              # Application principale Streamlit (UI + navigation)
├── db.py               # Couche données SQLite (CRUD + seed demo)
├── ai.py               # Module IA (Random Forest, Régression, Isolation Forest)
├── pdf_reports.py      # Génération des rapports PDF (ReportLab)
│
├── requirements.txt    # Dépendances Python
├── .gitignore          # Fichiers exclus du versioning
└── README.md           # Documentation
```

---

##  Installation & Lancement

### 1. Cloner le projet
```bash
git clone https://github.com/votre-username/rc-gestion-pro.git
cd rc-gestion
```

### 2. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
```bash
streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

---

##  Comptes de démonstration

| Rôle | Identifiant | Mot de passe | Accès |
|------|-------------|--------------|-------|
| Administrateur | `admin` | `admin123` | Toutes les fonctionnalités |
| Comptable | `comptable` | `compta456` | Déclarations, comptabilité, paie |
| Client | `client` | `client789` | Consultation dossier personnel |

---

##  Module Intelligence Artificielle

### Prédiction de Retard (Random Forest)
Analyse l'historique des déclarations de tous les clients pour entraîner un modèle de classification. Prédit la probabilité qu'un client soit en retard pour une déclaration donnée.

```
Entrées  : type_déclaration · secteur_activité · mode_déclaration · type_personne · montant
Sortie   : probabilité de retard (0% → 100%) + niveau (Faible / Modéré / Élevé)
```

### Prévision CA (Régression Linéaire)
Analyse les factures de vente historiques du client et projette le chiffre d'affaires probable pour le mois suivant.

```
Entrées  : historique des factures de vente (minimum 3 mois)
Sortie   : CA prévisionnel en MAD + graphique de tendance
```

### Détection d'Anomalies (Isolation Forest)
Détecte les déclarations dont les montants sont statistiquement anormaux par rapport à l'historique du cabinet.

```
Entrées  : montant_dû · montant_payé de toutes les déclarations
Sortie   : liste des déclarations suspectes avec client et type
```

---

##  Dépendances

```txt
streamlit
pandas
numpy
scikit-learn
plotly
reportlab
openpyxl
```

> Installation complète : `pip install -r requirements.txt`

---

##  Auteure

**Chaymae  EL BAHLOUL—** Étudiante en 2ème année Ingénierie des Données  
École Supérieure de Technologie (EST) El Kelaa des Sraghna  
Université Cadi Ayyad — Marrakech

**Stage réalisé chez :** RC Gestion · Bureau de Conseil et Gestion d'Entreprises · El Kelaa des Sraghna

---




