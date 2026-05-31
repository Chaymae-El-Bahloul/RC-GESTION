"""
ai.py — Module Intelligence Artificielle pour RC Gestion Pro
Modeles utilises :
  - Random Forest    → Prediction du risque de retard de declaration
  - Linear Regression → Prevision du chiffre d'affaires mensuel
  - Isolation Forest  → Detection d'anomalies sur les montants
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import db


# ── 1. PREDICTION DE RETARD (Random Forest) ─────────────────────────────────

def _build_model_retard():
    """
    Construit et retourne (model, encoders, feature_names).
    Les encoders sont conserves pour encoder correctement les nouvelles donnees.
    """
    df = db.get_declarations()
    if df.empty or len(df) < 5:
        return None, None, None

    df_clients = db.get_clients()
    client_map = {}
    for _, c in df_clients.iterrows():
        client_map[c["id"]] = {
            "secteur": c.get("secteur_activite", "Autre"),
            "mode":    c.get("mode_declaration", "Annuel"),
            "type_p":  c.get("type_personne", "Physique"),
        }

    rows = []
    for _, r in df.iterrows():
        ci = client_map.get(r.get("client_id", 0), {})
        rows.append({
            "type_decl":  str(r.get("type_decl", "Autre")),
            "montant_du": float(r.get("montant_du", 0) or 0),
            "secteur":    ci.get("secteur", "Autre"),
            "mode_decl":  ci.get("mode",    "Annuel"),
            "type_p":     ci.get("type_p",  "Physique"),
            "en_retard":  1 if r.get("statut") == "En retard" else 0,
        })

    df_ml = pd.DataFrame(rows)
    CAT_COLS = ["type_decl", "secteur", "mode_decl", "type_p"]

    # Garder les encodeurs pour reutilisation lors de la prediction
    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        df_ml[col] = le.fit_transform(df_ml[col].astype(str))
        encoders[col] = le

    X = df_ml.drop("en_retard", axis=1)
    y = df_ml["en_retard"]

    if len(y.unique()) < 2:
        return None, None, None

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X, y)
    return model, encoders, list(X.columns)


def predire_risque_retard(client_id: int, type_decl: str):
    """
    Retourne la probabilite (0.0 a 1.0) qu'un client soit en retard.
    Retourne None si les donnees sont insuffisantes.
    """
    model, encoders, feat_cols = _build_model_retard()
    if model is None:
        return None

    client = db.get_client(client_id)
    if not client:
        return None

    # Construire la ligne de prediction avec les MEMES encodeurs que l'entrainement
    row = {
        "type_decl":  str(type_decl),
        "montant_du": 0.0,
        "secteur":    str(client.get("secteur_activite", "Autre")),
        "mode_decl":  str(client.get("mode_declaration", "Annuel")),
        "type_p":     str(client.get("type_personne",    "Physique")),
    }

    df_pred = pd.DataFrame([row])
    for col in ["type_decl", "secteur", "mode_decl", "type_p"]:
        le = encoders[col]
        val = df_pred[col].astype(str)
        # Remplacer les valeurs inconnues par la premiere classe connue
        df_pred[col] = val.apply(
            lambda v: le.transform([v])[0] if v in le.classes_ else 0
        )

    df_pred = df_pred[feat_cols]  # ordre exact des colonnes

    try:
        proba = model.predict_proba(df_pred)[0]
        return round(float(proba[1]) if len(proba) > 1 else float(proba[0]), 2)
    except Exception:
        return None


# ── 2. PREVISION CA (Regression Lineaire) ───────────────────────────────────
def prevoir_ca_prochain_mois(client_id: int):
    """
    Retourne le CA prevu (MAD) pour le mois suivant base sur les factures de vente.
    Retourne None si les donnees sont insuffisantes (< 3 mois).
    """
    df = db.get_pieces(client_id=client_id, type_p="Facture Vente")
    if df.empty or len(df) < 3:
        return None

    df["date_piece"] = pd.to_datetime(df["date_piece"], errors="coerce")
    df = df.dropna(subset=["date_piece"])
    if df.empty:
        return None

    df_mois = (df.groupby(df["date_piece"].dt.to_period("M"))["montant_ttc"]
               .sum().reset_index())
    df_mois["idx"] = range(len(df_mois))

    if len(df_mois) < 2:
        return None

    X = df_mois[["idx"]]
    y = df_mois["montant_ttc"]

    model = LinearRegression()
    model.fit(X, y)

    next_idx = pd.DataFrame({"idx": [len(df_mois)]})
    prediction = model.predict(next_idx)[0]
    return round(max(float(prediction), 0), 2)


# ── 3. DETECTION D'ANOMALIES (Isolation Forest) ─────────────────────────────
def detecter_anomalies_declarations(client_id: int = None):
    """
    Detecte les declarations avec des montants statistiquement anormaux.
    Retourne un DataFrame des anomalies, ou None/vide si pas assez de donnees.
    """
    df = db.get_declarations(client_id=client_id)
    if df.empty or len(df) < 5:
        return pd.DataFrame()

    X = df[["montant_du", "montant_paye"]].fillna(0)

    model = IsolationForest(contamination=0.1, random_state=42)
    labels = model.fit_predict(X)
    df = df.copy()
    df["_anomalie"] = labels

    cols = [c for c in ["client", "type_decl", "annee", "periode", "montant_du", "statut"]
            if c in df.columns]
    return df[df["_anomalie"] == -1][cols].copy()