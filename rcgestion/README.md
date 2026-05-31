# RC Gestion 
## Plateforme Integree de Gestion Comptable et Fiscale
> Stage Technique — 2eme annee Ingenierie des Donnees
> Ecole Superieure de Technologie — El Kelaa des Sraghna
> Universite Cadi Ayyad — Marrakech

---

## Lancement rapide

```bash
# 1. Installer les dependances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run app.py
```

Ouvrir dans le navigateur : http://localhost:8501

---

## Structure du projet

```
crgestion/
├── app.py              Application principale Streamlit (7 pages)
├── db.py               Couche donnees SQLite (toutes les requetes)
├── requirements.txt    Dependances Python
├── README.md           Documentation
└── crgestion.db        Base SQLite (creee au premier lancement)
```

---

## Modules de la plateforme

| Module | Fonctionnalites |
|--------|----------------|
| Tableau de Bord | KPIs dynamiques, graphiques, alertes retards |
| Gestion Clients | Personnes Physiques et Morales, CRUD complet |
| Declarations Fiscales | TVA, IS, IR, CNSS, Patente — suivi et alertes |
| Comptabilite | Saisie pieces, journal, bilan simplifie |
| Paie & CNSS | Simulateur + bulletins, calcul CNSS/AMO/IR |
| Creation Entreprises | Suivi etapes : Statuts → RC → IF → ... |
| Rapports | Analyses visuelles, export Excel multi-feuilles |

---

## Schema de la Base de Donnees

### clients
Personnes Physiques (CIN, nom, prenom...) et Morales (RC, IF, ICE, capital...)
Mode de declaration : Annuel / Trimestriel / Mensuel
Regime fiscal : RNR / RF / Auto-Entrepreneur

### declarations
TVA, IS, IR, CNSS, Patente, Taxe Professionnelle
Suivi : date echeance, depot, montants dus/payes, statut

### pieces_comptables
Factures vente/achat, recus, OD
Calcul automatique TVA et TTC

### paie
Bulletins mensuels avec calcul auto :
CNSS salariale (4.48%) + AMO (2.26%) + IR progressif

### creations_entreprises
Suivi des 7 etapes : Statuts, RC, IF, Patente, ICE, CNSS, Compte Bancaire

---

## Technologies

- Python 3.10+
- Streamlit (interface web)
- SQLite (base de donnees)
- Pandas (manipulation des donnees)
- Plotly (graphiques interactifs)
- OpenPyXL (export Excel)
