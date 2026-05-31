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
    q += " ORDER BY d.id ASC"
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
    """Insere des donnees demo realistes pour El Kelaa des Sraghna."""
    conn = get_conn(); c = conn.cursor()

    # ── PERSONNES PHYSIQUES (commerçants, artisans, prestataires locaux) ──
    pp = [
        # (type_p, nom, prenom, cin, rs, fj, cap, rc, if_, pat, ice, secteur, mode_decl, regime, tel, email, adresse, ville, statut)
        ('Physique','QACIMI','Rachid','A789456','','',0,'47821/2018','45612318','P-47821','','Commerce de detail','Trimestriel','RNR','0661234501','r.qacimi@gmail.com','Derb Lalla Fatima N12','El Kelaa des Sraghna','Actif'),
        ('Physique','BOUTALEB','Khadija','BK234789','','',0,'51203/2019','48903127','P-51203','','Alimentation generale','Annuel','RNR','0672345602','','Hay El Massira Bloc 3','El Kelaa des Sraghna','Actif'),
        ('Physique','HAMDAOUI','Abderrahim','T456123','','',0,'39847/2016','37821409','P-39847','','Boulangerie Patisserie','Trimestriel','RNR','0655678903','hamdaoui.boulangerie@gmail.com','Avenue Hassan II N45','El Kelaa des Sraghna','Actif'),
        ('Physique','RHAZALI','Nadia','D234567','','',0,'62104/2021','59034218','P-62104','','Coiffure Beaute','Annuel','RF','0647891204','nadia.rhazali@hotmail.com','Rue Moulay Ismail N8','El Kelaa des Sraghna','Actif'),
        ('Physique','MANSOURI','Hamid','S901234','','',0,'44512/2017','42301876','P-44512','','Materiel Agricole','Trimestriel','RNR','0660123405','mansouri.agri@gmail.com','Route de Benguerir Km2','El Kelaa des Sraghna','Actif'),
        ('Physique','ZOUITEN','Amina','L567890','','',0,'58934/2020','55678234','P-58934','','Pharmacie','Mensuel','RNR','0678901236','','Avenue Mohammed V N22','El Kelaa des Sraghna','Actif'),
        ('Physique','LAHRICHI','Mustapha','E123789','','',0,'36201/2015','34109823','P-36201','','Transport Marchandises','Trimestriel','RF','0664512307','lahrichi.trans@gmail.com','Quartier Industriel','El Kelaa des Sraghna','Actif'),
        ('Physique','OUALI','Sanae','F890123','','',0,'70345/2022','67234901','P-70345','','Vetements Confection','Annuel','RNR','0651234508','sanae.ouali@gmail.com','Souk Had N17','El Kelaa des Sraghna','Actif'),
        ('Physique','BENCHEKROUN','Yassine','G456789','','',0,'41789/2017','39567234','P-41789','','Informatique Reparation','Trimestriel','RNR','0692345609','yassine.tech@gmail.com','Hay Riad Rue 4 N3','El Kelaa des Sraghna','Actif'),
        ('Physique','TAZI','Hafida','H234567','','',0,'55123/2019','52890341','P-55123','','Epicerie Fine Import','Annuel','RNR','0683456710','','Rue Ibn Khaldoun N31','Sidi Bou Othmane','Actif'),
    ]

    # ── PERSONNES MORALES (societes locales) ──
    pm = [
        ('Morale','','','','SARL TRANSPORT SRAGHNA','SARL',300000,'RC12345/Kelaa','43219087','PAT-RC12345','ICE-001234567000','Transport Voyageurs','Mensuel','RNR','0528471201','transport.sraghna@gmail.com','Zone Industrielle Lot 14','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','STE AGRICOLE HAOUZ PLUS','SARL',500000,'RC23456/Kelaa','54320198','PAT-RC23456','ICE-002345678000','Agriculture Elevage','Trimestriel','RNR','0528471302','haouz.agri@gmail.com','Route Marrakech Km5','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','AUTO-ECOLE AL AMAL','SARL',150000,'RC34567/Kelaa','61230987','PAT-RC34567','ICE-003456789000','Formation Conduite','Trimestriel','RF','0528471403','autoecole.alamal@gmail.com','Avenue Bir Anzarane N7','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','SARL BATI CONSTRUCT','SARL',800000,'RC45678/Kelaa','72341098','PAT-RC45678','ICE-004567890000','BTP Construction','Mensuel','RNR','0528471504','bati.construct@gmail.com','Hay El Wifaq Lot 8','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','STE IMMOBILIER REGHAYA','SA',2000000,'RC56789/Kelaa','83452109','PAT-RC56789','ICE-005678901000','Immobilier Promotion','Mensuel','RNR','0528471605','immo.reghaya@gmail.com','Rue Al Qods N15','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','SARL AL BARAKA COMMERCE','SARL',200000,'RC67890/Kelaa','91234567','PAT-RC67890','ICE-006789012000','Commerce Gros Detail','Trimestriel','RNR','0528471706','albaraka.com@gmail.com','Souk Hebdomadaire Bloc B','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','STE OLIVE OR','SARL',1200000,'RC78901/Kelaa','10234567','PAT-RC78901','ICE-007890123000','Huilerie Olive','Trimestriel','RNR','0528471807','olive.or@gmail.com','Route Oulad Berhil Km3','El Kelaa des Sraghna','Actif'),
        ('Morale','','','','SARL MINOTERIE ATLAS','SARL',600000,'RC89012/Kelaa','11345678','PAT-RC89012','ICE-008901234000','Minoterie Stockage','Mensuel','RNR','0528471908','minoterie.atlas@gmail.com','Zone Industrielle Lot 22','El Kelaa des Sraghna','Actif'),
    ]

    # Insertion clients
    for r in pp + pm:
        try:
            c.execute("""INSERT INTO clients (type_personne,nom,prenom,cin,raison_sociale,forme_juridique,
                capital_social,rc,if_fiscal,patente,ice,secteur_activite,mode_declaration,regime_fiscal,
                telephone,email,adresse,ville,statut) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", r)
        except: pass
    conn.commit()

    # Recuperer tous les IDs inseres
    df_c = pd.read_sql("SELECT id, mode_declaration, secteur_activite, type_personne FROM clients ORDER BY id", conn)

    # ── DECLARATIONS realistes par client ──
    decls_pp = {
        "Trimestriel": [
            ("TVA","T1 2024",2024), ("TVA","T2 2024",2024), ("TVA","T3 2024",2024), ("TVA","T4 2023",2023),
            ("IR","Annuel 2023",2023), ("CNSS","Janvier 2024",2024), ("CNSS","Fevrier 2024",2024),
            ("CNSS","Mars 2024",2024),
        ],
        "Annuel": [
            ("IR","Annuel 2023",2023), ("IR","Annuel 2022",2022),
            ("TVA","Annuel 2023",2023), ("CNSS","Annuel 2023",2023),
        ],
        "Mensuel": [
            ("TVA","Janvier 2024",2024), ("TVA","Fevrier 2024",2024), ("TVA","Mars 2024",2024),
            ("TVA","Avril 2024",2024), ("IR","Annuel 2023",2023), ("CNSS","Janvier 2024",2024),
        ],
    }
    decls_pm = {
        "Mensuel": [
            ("TVA","Janvier 2024",2024), ("TVA","Fevrier 2024",2024), ("TVA","Mars 2024",2024),
            ("TVA","Avril 2024",2024), ("TVA","Mai 2024",2024),
            ("IS","Annuel 2023",2023), ("IS","Annuel 2022",2022),
            ("CNSS","Janvier 2024",2024), ("CNSS","Fevrier 2024",2024), ("CNSS","Mars 2024",2024),
        ],
        "Trimestriel": [
            ("TVA","T1 2024",2024), ("TVA","T2 2024",2024), ("TVA","T3 2023",2023), ("TVA","T4 2023",2023),
            ("IS","Annuel 2023",2023), ("CNSS","T1 2024",2024), ("CNSS","T2 2024",2024),
        ],
    }

    montants_secteur = {
        "Transport Voyageurs": (8000, 45000),
        "Agriculture Elevage": (5000, 30000),
        "BTP Construction": (15000, 90000),
        "Immobilier Promotion": (20000, 120000),
        "Commerce Gros Detail": (3000, 20000),
        "Huilerie Olive": (10000, 60000),
        "Minoterie Stockage": (12000, 70000),
        "Commerce de detail": (1500, 8000),
        "Alimentation generale": (800, 5000),
        "Boulangerie Patisserie": (1200, 6000),
        "Pharmacie": (3000, 15000),
        "Transport Marchandises": (2000, 12000),
        "Materiel Agricole": (2500, 14000),
        "Informatique Reparation": (500, 3000),
    }

    # Profil de risque par secteur : probabilite d etre en retard (0.0 = jamais, 1.0 = toujours)
    risque_secteur = {
        # Faible risque — secteurs organises, grands chiffres
        "Pharmacie":              0.05,
        "Immobilier Promotion":   0.08,
        "Minoterie Stockage":     0.10,
        "Huilerie Olive":         0.10,
        "BTP Construction":       0.15,
        # Risque moyen
        "Transport Voyageurs":    0.25,
        "Agriculture Elevage":    0.30,
        "Materiel Agricole":      0.30,
        "Transport Marchandises": 0.35,
        "Formation Conduite":     0.35,
        # Risque eleve — petits commercants, gestion manuelle
        "Commerce Gros Detail":   0.55,
        "Commerce de detail":     0.60,
        "Alimentation generale":  0.65,
        "Boulangerie Patisserie":  0.50,
        "Vetements Confection":   0.70,
        "Informatique Reparation":0.75,
        "Coiffure Beaute":        0.80,
    }

    for _, row in df_c.iterrows():
        cid = int(row["id"])
        mode = row["mode_declaration"]
        secteur = row["secteur_activite"]
        is_pm = row["type_personne"] == "Morale"
        decl_list = (decls_pm if is_pm else decls_pp).get(mode, decls_pp["Annuel"])
        min_m, max_m = montants_secteur.get(secteur, (1000, 15000))
        prob_retard = risque_secteur.get(secteur, 0.40)
        for tp, per, annee in decl_list:
            montant = round(random.uniform(min_m, max_m), 2)
            # Paiement coherent avec le risque : les bons payeurs paient plus
            if random.random() > prob_retard:
                paye = round(montant * random.uniform(0.90, 1.0), 2)
                statut = "Deposee"
            else:
                rand = random.random()
                if rand < 0.5:
                    statut = "En retard"
                    paye = round(montant * random.uniform(0, 0.4), 2)
                else:
                    statut = "En attente"
                    paye = round(montant * random.uniform(0.3, 0.7), 2)
            try:
                c.execute("""INSERT INTO declarations (client_id,type_decl,annee,periode,montant_du,montant_paye,statut)
                    VALUES (?,?,?,?,?,?,?)""", (cid, tp, annee, per, montant, paye, statut))
            except: pass

    # ── PIECES COMPTABLES realistes (6 mois de factures) ──
    import calendar as cal
    pieces_types = ["Facture Vente","Facture Achat","Note de Frais"]
    today = date.today()
    for _, row in df_c.iterrows():
        cid = int(row["id"])
        secteur = row["secteur_activite"]
        min_m, max_m = montants_secteur.get(secteur, (1000, 15000))
        for i in range(6, 0, -1):
            y = today.year if today.month > i else today.year - 1
            m = (today.month - i) % 12 or 12
            last_day = cal.monthrange(y, m)[1]
            # Facture vente (CA)
            d_p = f"{y}-{m:02d}-{random.randint(5, last_day):02d}"
            ht = round(random.uniform(min_m, max_m), 2)
            tva = round(ht * 0.20, 2)
            ttc = round(ht + tva, 2)
            try:
                c.execute("""INSERT INTO pieces_comptables
                    (client_id,type_piece,numero,date_piece,libelle,montant_ht,taux_tva,montant_tva,montant_ttc,statut)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (cid, "Facture Vente", f"FV-{cid:03d}-{y}{m:02d}",
                     d_p, f"Vente {cal.month_name[m]} {y}", ht, 20.0, tva, ttc, "Validee"))
            except: pass
            # Facture achat (charges)
            ht2 = round(random.uniform(min_m*0.3, min_m*0.9), 2)
            tva2 = round(ht2 * 0.20, 2)
            ttc2 = round(ht2 + tva2, 2)
            d_p2 = f"{y}-{m:02d}-{random.randint(1, 10):02d}"
            try:
                c.execute("""INSERT INTO pieces_comptables
                    (client_id,type_piece,numero,date_piece,libelle,montant_ht,taux_tva,montant_tva,montant_ttc,statut)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (cid, "Facture Achat", f"FA-{cid:03d}-{y}{m:02d}",
                     d_p2, f"Achat fournisseur {cal.month_name[m]} {y}", ht2, 20.0, tva2, ttc2, "Validee"))
            except: pass

    # ── PAIE (employes pour les PM) ──
    employes = [
        ("KARIMI","Said","BE456789"), ("SENHAJI","Malika","F234901"),
        ("RAMI","Omar","G789234"), ("IDRISSI","Zineb","H345678"),
    ]
    for _, row in df_c.iterrows():
        if row["type_personne"] != "Morale": continue
        cid = int(row["id"])
        nb_emp = random.randint(1, 3)
        for emp in employes[:nb_emp]:
            for mois in [1, 2, 3, 4]:
                brut = round(random.uniform(3500, 12000), 2)
                calc = calculer_paie(brut)
                net = round(brut - calc["cnss_salariale"] - calc["amo_salariale"] - calc["ir_mensuel"], 2)
                try:
                    c.execute("""INSERT INTO paie
                        (client_id,employe_nom,employe_prenom,employe_cin,mois,annee,salaire_brut,
                         cnss_salariale,amo_salariale,ir_mensuel,cnss_patronale,amo_patronale,salaire_net,statut)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (cid, emp[0], emp[1], emp[2], mois, 2024, brut,
                         calc["cnss_salariale"], calc["amo_salariale"], calc["ir_mensuel"],
                         calc["cnss_patronale"], calc["amo_patronale"], net, "Calculee"))
                except: pass

    conn.commit(); conn.close()