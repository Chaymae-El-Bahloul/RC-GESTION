"""
db.py — Couche données SQLite pour CR Gestion Pro
"""
import sqlite3
import pandas as pd
from datetime import date
import random

DB_PATH = "crgestion.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_personne TEXT NOT NULL,
        nom TEXT DEFAULT '', prenom TEXT DEFAULT '', cin TEXT DEFAULT '',
        raison_sociale TEXT DEFAULT '', forme_juridique TEXT DEFAULT '',
        capital_social REAL DEFAULT 0,
        rc TEXT DEFAULT '', if_fiscal TEXT DEFAULT '',
        patente TEXT DEFAULT '', ice TEXT DEFAULT '',
        secteur_activite TEXT DEFAULT '',
        mode_declaration TEXT NOT NULL DEFAULT 'Annuel',
        regime_fiscal TEXT DEFAULT 'RNR',
        telephone TEXT DEFAULT '', email TEXT DEFAULT '',
        adresse TEXT DEFAULT '', ville TEXT DEFAULT '',
        statut TEXT NOT NULL DEFAULT 'Actif',
        date_creation TEXT DEFAULT (DATE('now')),
        notes TEXT DEFAULT ''
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS declarations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        type_decl TEXT NOT NULL,
        annee INTEGER NOT NULL,
        periode TEXT NOT NULL DEFAULT '',
        date_echeance TEXT DEFAULT '',
        date_depot TEXT DEFAULT '',
        montant_du REAL DEFAULT 0,
        montant_paye REAL DEFAULT 0,
        statut TEXT NOT NULL DEFAULT 'En attente',
        notes TEXT DEFAULT '',
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS pieces_comptables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        type_piece TEXT NOT NULL,
        numero TEXT DEFAULT '',
        date_piece TEXT NOT NULL DEFAULT (DATE('now')),
        libelle TEXT NOT NULL,
        compte_debit TEXT DEFAULT '',
        compte_credit TEXT DEFAULT '',
        montant_ht REAL DEFAULT 0,
        taux_tva REAL DEFAULT 20,
        montant_tva REAL DEFAULT 0,
        montant_ttc REAL DEFAULT 0,
        statut TEXT DEFAULT 'Validee',
        notes TEXT DEFAULT '',
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS paie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        employe_nom TEXT NOT NULL,
        employe_prenom TEXT NOT NULL,
        employe_cin TEXT DEFAULT '',
        mois INTEGER NOT NULL,
        annee INTEGER NOT NULL,
        salaire_brut REAL NOT NULL DEFAULT 0,
        nb_jours INTEGER DEFAULT 26,
        avances REAL DEFAULT 0,
        cnss_salariale REAL DEFAULT 0,
        amo_salariale REAL DEFAULT 0,
        ir_mensuel REAL DEFAULT 0,
        cnss_patronale REAL DEFAULT 0,
        amo_patronale REAL DEFAULT 0,
        salaire_net REAL DEFAULT 0,
        statut TEXT DEFAULT 'Calculee',
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS creations_entreprises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        nom_entreprise TEXT NOT NULL,
        forme_juridique TEXT NOT NULL,
        capital_prevu REAL DEFAULT 0,
        associes TEXT DEFAULT '',
        objet_social TEXT DEFAULT '',
        siege_social TEXT DEFAULT '',
        date_debut TEXT DEFAULT (DATE('now')),
        etape_statuts TEXT DEFAULT 'En cours',
        etape_rc TEXT DEFAULT 'En attente',
        etape_if TEXT DEFAULT 'En attente',
        etape_patente TEXT DEFAULT 'En attente',
        etape_ice TEXT DEFAULT 'En attente',
        etape_cnss TEXT DEFAULT 'En attente',
        etape_compte_bancaire TEXT DEFAULT 'En attente',
        statut_global TEXT DEFAULT 'En cours',
        notes TEXT DEFAULT ''
    )""")
    conn.commit()
    conn.close()

ETAPES = ['etape_statuts','etape_rc','etape_if','etape_patente','etape_ice','etape_cnss','etape_compte_bancaire']
ETAPES_LABELS = ['Statuts','Reg. Commerce','IF Fiscal','Patente','ICE','CNSS','Cpt. Bancaire']
MOIS_NOMS = ["","Janvier","Fevrier","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Decembre"]

# ── CLIENTS ──
def add_client(d):
    conn = get_conn()
    conn.execute("""INSERT INTO clients
        (type_personne,nom,prenom,cin,raison_sociale,forme_juridique,capital_social,
         rc,if_fiscal,patente,ice,secteur_activite,mode_declaration,regime_fiscal,
         telephone,email,adresse,ville,statut,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d['type_personne'], d.get('nom',''), d.get('prenom',''), d.get('cin',''),
         d.get('raison_sociale',''), d.get('forme_juridique',''), d.get('capital_social',0),
         d.get('rc',''), d.get('if_fiscal',''), d.get('patente',''), d.get('ice',''),
         d.get('secteur_activite',''), d.get('mode_declaration','Annuel'),
         d.get('regime_fiscal','RNR'), d.get('telephone',''), d.get('email',''),
         d.get('adresse',''), d.get('ville',''), d.get('statut','Actif'), d.get('notes','')))
    conn.commit(); conn.close()

def update_client(cid, d):
    conn = get_conn()
    conn.execute("""UPDATE clients SET type_personne=?,nom=?,prenom=?,cin=?,
        raison_sociale=?,forme_juridique=?,capital_social=?,rc=?,if_fiscal=?,
        patente=?,ice=?,secteur_activite=?,mode_declaration=?,regime_fiscal=?,
        telephone=?,email=?,adresse=?,ville=?,statut=?,notes=? WHERE id=?""",
        (d['type_personne'], d.get('nom',''), d.get('prenom',''), d.get('cin',''),
         d.get('raison_sociale',''), d.get('forme_juridique',''), d.get('capital_social',0),
         d.get('rc',''), d.get('if_fiscal',''), d.get('patente',''), d.get('ice',''),
         d.get('secteur_activite',''), d.get('mode_declaration','Annuel'),
         d.get('regime_fiscal','RNR'), d.get('telephone',''), d.get('email',''),
         d.get('adresse',''), d.get('ville',''), d.get('statut','Actif'), d.get('notes',''), cid))
    conn.commit(); conn.close()

def delete_client(cid):
    conn = get_conn()
    conn.execute("DELETE FROM clients WHERE id=?", (cid,))
    conn.commit(); conn.close()

def get_clients(type_p="Tous", statut="Tous", q=""):
    conn = get_conn()
    conds, params = [], []
    if type_p != "Tous": conds.append("type_personne=?"); params.append(type_p)
    if statut != "Tous": conds.append("statut=?"); params.append(statut)
    if q.strip():
        like = f"%{q.strip()}%"
        conds.append("(nom LIKE ? OR prenom LIKE ? OR raison_sociale LIKE ? OR cin LIKE ? OR rc LIKE ? OR if_fiscal LIKE ?)")
        params.extend([like]*6)
    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    df = pd.read_sql(f"SELECT * FROM clients {where} ORDER BY COALESCE(NULLIF(raison_sociale,''),nom)", conn, params=params)
    conn.close()
    return df

def get_client(cid):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM clients WHERE id=?", conn, params=(cid,))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else {}

def client_label(r):
    if r['type_personne'] == 'Physique':
        return f"[PP] {r.get('prenom','')} {r.get('nom','')} | CIN: {r.get('cin','')}"
    return f"[PM] {r.get('raison_sociale','')} | RC: {r.get('rc','')}"

# ── DECLARATIONS ──
def add_declaration(d):
    conn = get_conn()
    conn.execute("""INSERT INTO declarations
        (client_id,type_decl,annee,periode,date_echeance,date_depot,montant_du,montant_paye,statut,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (d['client_id'], d['type_decl'], d['annee'], d.get('periode',''),
         d.get('date_echeance',''), d.get('date_depot',''),
         d.get('montant_du',0), d.get('montant_paye',0), d.get('statut','En attente'), d.get('notes','')))
    conn.commit(); conn.close()

def get_declarations(client_id=None, type_d="Tous", statut="Tous"):
    conn = get_conn()
    q = """SELECT d.id, d.client_id, c.type_personne,
           COALESCE(NULLIF(c.raison_sociale,''), TRIM(c.prenom||' '||c.nom)) as client,
           COALESCE(NULLIF(c.raison_sociale,''), TRIM(c.prenom||' '||c.nom)) as client_label,
           d.type_decl, d.annee, d.periode, d.date_echeance, d.date_depot,
           d.montant_du, d.montant_paye, d.statut, d.notes
           FROM declarations d JOIN clients c ON d.client_id=c.id"""
    conds, params = [], []
    if client_id: conds.append("d.client_id=?"); params.append(client_id)
    if type_d != "Tous": conds.append("d.type_decl=?"); params.append(type_d)
    if statut != "Tous": conds.append("d.statut=?"); params.append(statut)
    if conds: q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY d.annee DESC"
    df = pd.read_sql(q, conn, params=params); conn.close()
    return df

def update_decl(did, statut, montant_paye=None):
    conn = get_conn()
    if montant_paye is not None:
        conn.execute("UPDATE declarations SET statut=?,montant_paye=? WHERE id=?", (statut, montant_paye, did))
    else:
        conn.execute("UPDATE declarations SET statut=? WHERE id=?", (statut, did))
    conn.commit(); conn.close()

# ── PIECES COMPTABLES ──
def add_piece(d):
    ht = d.get('montant_ht',0); tva = d.get('taux_tva',20)
    montant_tva = round(ht * tva/100, 2); ttc = round(ht + montant_tva, 2)
    conn = get_conn()
    conn.execute("""INSERT INTO pieces_comptables
        (client_id,type_piece,numero,date_piece,libelle,compte_debit,compte_credit,
         montant_ht,taux_tva,montant_tva,montant_ttc,statut,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d['client_id'], d['type_piece'], d.get('numero',''), d.get('date_piece',str(date.today())),
         d['libelle'], d.get('compte_debit',''), d.get('compte_credit',''),
         ht, tva, montant_tva, ttc, d.get('statut','Validee'), d.get('notes','')))
    conn.commit(); conn.close()

def get_pieces(client_id=None, type_p="Tous"):
    conn = get_conn()
    q = """SELECT p.id, COALESCE(NULLIF(c.raison_sociale,''), TRIM(c.prenom||' '||c.nom)) as client,
           p.type_piece, p.numero, p.date_piece, p.libelle,
           p.montant_ht, p.taux_tva, p.montant_tva, p.montant_ttc, p.statut
           FROM pieces_comptables p JOIN clients c ON p.client_id=c.id"""
    conds, params = [], []
    if client_id: conds.append("p.client_id=?"); params.append(client_id)
    if type_p != "Tous": conds.append("p.type_piece=?"); params.append(type_p)
    if conds: q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY p.date_piece DESC"
    df = pd.read_sql(q, conn, params=params); conn.close()
    return df

# ── PAIE ──
def calculer_paie(brut):
    cnss_sal = round(min(brut, 6000) * 0.0448, 2)
    amo_sal  = round(brut * 0.0226, 2)
    frais    = min(brut * 0.20, 2500)
    rni      = max(brut - cnss_sal - amo_sal - frais, 0)
    rni_an   = rni * 12
    if   rni_an <= 30000:  ir_an = 0
    elif rni_an <= 50000:  ir_an = (rni_an - 30000) * 0.10
    elif rni_an <= 60000:  ir_an = 2000  + (rni_an - 50000) * 0.20
    elif rni_an <= 80000:  ir_an = 4000  + (rni_an - 60000) * 0.30
    elif rni_an <= 180000: ir_an = 10000 + (rni_an - 80000) * 0.34
    else:                  ir_an = 44000 + (rni_an - 180000) * 0.38
    ir = round(ir_an/12, 2)
    cnss_pat = round(min(brut, 6000) * 0.0898, 2)
    amo_pat  = round(brut * 0.0396, 2)
    net      = round(brut - cnss_sal - amo_sal - ir, 2)
    return dict(cnss_salariale=cnss_sal, amo_salariale=amo_sal, ir_mensuel=ir,
                cnss_patronale=cnss_pat, amo_patronale=amo_pat, salaire_net=net)

def add_paie(d):
    c = calculer_paie(d['salaire_brut'])
    net = c['salaire_net'] - d.get('avances', 0)
    conn = get_conn()
    conn.execute("""INSERT INTO paie
        (client_id,employe_nom,employe_prenom,employe_cin,mois,annee,salaire_brut,
         nb_jours,avances,cnss_salariale,amo_salariale,ir_mensuel,cnss_patronale,amo_patronale,salaire_net,statut)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d['client_id'], d['employe_nom'], d['employe_prenom'], d.get('employe_cin',''),
         d['mois'], d['annee'], d['salaire_brut'], d.get('nb_jours',26), d.get('avances',0),
         c['cnss_salariale'], c['amo_salariale'], c['ir_mensuel'],
         c['cnss_patronale'], c['amo_patronale'], net, 'Calculee'))
    conn.commit(); conn.close()

def get_paie(client_id=None):
    conn = get_conn()
    q = """SELECT p.id, COALESCE(NULLIF(c.raison_sociale,''), TRIM(c.prenom||' '||c.nom)) as client,
           p.employe_prenom||' '||p.employe_nom as employe,
           p.mois, p.annee, p.salaire_brut, p.cnss_salariale, p.amo_salariale,
           p.ir_mensuel, p.cnss_patronale, p.amo_patronale, p.avances, p.salaire_net, p.statut
           FROM paie p JOIN clients c ON p.client_id=c.id"""
    if client_id:
        df = pd.read_sql(q+" WHERE p.client_id=? ORDER BY p.annee DESC,p.mois DESC", conn, params=(client_id,))
    else:
        df = pd.read_sql(q+" ORDER BY p.annee DESC,p.mois DESC", conn)
    conn.close(); return df

# ── CREATIONS ──
def add_creation(d):
    conn = get_conn()
    conn.execute("""INSERT INTO creations_entreprises
        (client_id,nom_entreprise,forme_juridique,capital_prevu,associes,objet_social,siege_social,date_debut,notes)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (d.get('client_id'), d['nom_entreprise'], d['forme_juridique'],
         d.get('capital_prevu',0), d.get('associes',''), d.get('objet_social',''),
         d.get('siege_social',''), d.get('date_debut',str(date.today())), d.get('notes','')))
    conn.commit(); conn.close()

def update_creation_etape(cid, etape_col, statut):
    conn = get_conn()
    conn.execute(f"UPDATE creations_entreprises SET {etape_col}=? WHERE id=?", (statut, cid))
    conn.commit(); conn.close()

def get_creations():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM creations_entreprises ORDER BY date_debut DESC", conn)
    conn.close(); return df

# ── STATS ──
def get_stats():
    conn = get_conn(); cur = conn.cursor(); s = {}
    for k,q in {
        'total_clients':"SELECT COUNT(*) FROM clients",
        'pp':"SELECT COUNT(*) FROM clients WHERE type_personne='Physique'",
        'pm':"SELECT COUNT(*) FROM clients WHERE type_personne='Morale'",
        'actifs':"SELECT COUNT(*) FROM clients WHERE statut='Actif'",
        'decl_total':"SELECT COUNT(*) FROM declarations",
        'decl_retard':"SELECT COUNT(*) FROM declarations WHERE statut='En retard'",
        'montant_du':"SELECT COALESCE(SUM(montant_du),0) FROM declarations",
        'pieces_total':"SELECT COUNT(*) FROM pieces_comptables",
        'ca_total':"SELECT COALESCE(SUM(montant_ttc),0) FROM pieces_comptables WHERE type_piece='Facture Vente'",
        'creations':"SELECT COUNT(*) FROM creations_entreprises WHERE statut_global='En cours'",
    }.items():
        s[k] = cur.execute(q).fetchone()[0]
    conn.close(); return s

def get_clients_par_mois():
    conn = get_conn()
    df = pd.read_sql("""SELECT SUBSTR(date_creation,1,7) as mois, type_personne, COUNT(*) as nb
        FROM clients GROUP BY mois,type_personne ORDER BY mois""", conn)
    conn.close(); return df

def get_decl_par_type():
    conn = get_conn()
    df = pd.read_sql("""SELECT type_decl, statut, COUNT(*) as nb, COALESCE(SUM(montant_du),0) as total_du
        FROM declarations GROUP BY type_decl,statut""", conn)
    conn.close(); return df

# ── DEMO ──
def seed_demo():
    rows_pp = [
        ('Physique','ALAOUI','Mohammed','AB123456','','',0,'RC001','IF001','PAT001','','Commerce','Trimestriel','RNR','0612000001','alaoui@mail.ma','Rue Hassan II','El Kelaa des Sraghna','Actif'),
        ('Physique','BENALI','Fatima','CD789012','','',0,'RC002','IF002','PAT002','','Artisanat','Annuel','RNR','0613000002','benali@mail.ma','Av Mohammed V','Marrakech','Actif'),
        ('Physique','CHRAIBI','Youssef','EF345678','','',0,'RC003','IF003','PAT003','','Transport','Trimestriel','RF','0614000003','','Rue Ibn Sina','El Kelaa des Sraghna','Actif'),
    ]
    rows_pm = [
        ('Morale','','','','SARL ATLAS TRANSIT','SARL',500000,'RC100','IF100','PAT100','ICE100','Transport','Mensuel','RNR','0520000100','atlas@mail.ma','Zone Industrielle','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','STE IMMOBILIER SRAGHNA','SA',2000000,'RC101','IF101','PAT101','ICE101','Immobilier','Mensuel','RNR','0520000101','','Hay Riad','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','AUTO-ECOLE NAJAH','SARL',200000,'RC102','IF102','PAT102','ICE102','Formation','Trimestriel','RF','0520000102','najah@mail.ma','Centre Ville','El Kelaa des Sraghna','Actif'),
    ]
    conn = get_conn(); c = conn.cursor()
    for r in rows_pp + rows_pm:
        try:
            c.execute("""INSERT INTO clients (type_personne,nom,prenom,cin,raison_sociale,forme_juridique,
                capital_social,rc,if_fiscal,patente,ice,secteur_activite,mode_declaration,regime_fiscal,
                telephone,email,adresse,ville,statut) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", r)
        except: pass
    conn.commit()
    df_c = pd.read_sql("SELECT id FROM clients LIMIT 5", conn)
    for cid in df_c['id'].tolist():
        for tp,per in [('TVA','T1 2024'),('TVA','T2 2024'),('IS','Annuel 2023'),('IR','Annuel 2023'),('CNSS','Janvier 2024')]:
            try:
                c.execute("""INSERT INTO declarations (client_id,type_decl,annee,periode,montant_du,montant_paye,statut)
                    VALUES (?,?,?,?,?,?,?)""",
                    (cid, tp, 2024, per, round(random.uniform(1000,50000),2),
                     round(random.uniform(0,30000),2),
                     random.choice(['Deposee','En attente','En retard'])))
            except: pass
    conn.commit(); conn.close()
