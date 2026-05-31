"""
pdf_reports.py — Génération de rapports PDF pour RC Gestion 
Bibliothèque : reportlab
Ajouter dans requirements.txt : reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date
import io

# ── PALETTE COULEURS ───────────────────────────────────────────
BLEU_NAVY  = colors.HexColor("#0C2A4A")
BLEU_SKY   = colors.HexColor("#1E90D4")
BLEU_LIGHT = colors.HexColor("#E2F0FB")
VERT       = colors.HexColor("#578B78")
VERT_LIGHT = colors.HexColor("#E6F7F1")
AMBER      = colors.HexColor("#D4890A")
AMBER_LT   = colors.HexColor("#FEF3CD")
ROUGE      = colors.HexColor("#C0392B")
GRIS       = colors.HexColor("#64748B")
GRIS_LIGHT = colors.HexColor("#F0F7FF")
BLANC      = colors.white

# ── STYLES ─────────────────────────────────────────────────────
def get_styles():
    styles = getSampleStyleSheet()
    custom = {
        "titre_doc": ParagraphStyle(
            "titre_doc", fontSize=18, textColor=BLANC,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4
        ),
        "sous_titre_doc": ParagraphStyle(
            "sous_titre_doc", fontSize=10, textColor=BLEU_LIGHT,
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=2
        ),
        "section": ParagraphStyle(
            "section", fontSize=11, textColor=BLEU_NAVY,
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4,
            borderPad=4
        ),
        "corps": ParagraphStyle(
            "corps", fontSize=9, textColor=GRIS,
            fontName="Helvetica", spaceAfter=3
        ),
        "corps_bold": ParagraphStyle(
            "corps_bold", fontSize=9, textColor=BLEU_NAVY,
            fontName="Helvetica-Bold", spaceAfter=2
        ),
        "label": ParagraphStyle(
            "label", fontSize=8, textColor=GRIS,
            fontName="Helvetica"
        ),
        "valeur": ParagraphStyle(
            "valeur", fontSize=9, textColor=BLEU_NAVY,
            fontName="Helvetica-Bold"
        ),
        "note_bas": ParagraphStyle(
            "note_bas", fontSize=7, textColor=GRIS,
            fontName="Helvetica-Oblique", alignment=TA_CENTER
        ),
        "alerte": ParagraphStyle(
            "alerte", fontSize=9, textColor=ROUGE,
            fontName="Helvetica-Bold"
        ),
    }
    return custom

# ── ENTÊTE + PIED DE PAGE ──────────────────────────────────────
def entete_pied(canvas, doc):
    """Dessine l'en-tête navy et le pied de page sur chaque page"""
    w, h = A4
    canvas.saveState()

    # Bandeau en-tête
    canvas.setFillColor(BLEU_NAVY)
    canvas.rect(0, h - 2.2*cm, w, 2.2*cm, fill=True, stroke=False)

    canvas.setFillColor(BLEU_SKY)
    canvas.rect(0, h - 2.2*cm, 0.4*cm, 2.2*cm, fill=True, stroke=False)

    canvas.setFont("Helvetica-Bold", 13)
    canvas.setFillColor(BLANC)
    canvas.drawString(1*cm, h - 1.1*cm, "RC Gestion ")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(BLEU_LIGHT)
    canvas.drawString(1*cm, h - 1.55*cm, "Cabinet Comptable — El Kelaa des Sraghna")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(BLEU_SKY)
    canvas.drawRightString(w - 1*cm, h - 1.1*cm, f"Généré le {date.today().strftime('%d/%m/%Y')}")
    canvas.drawRightString(w - 1*cm, h - 1.55*cm, f"Page {doc.page}")

    # Ligne pied de page
    canvas.setStrokeColor(BLEU_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(1*cm, 1.2*cm, w - 1*cm, 1.2*cm)
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.setFillColor(GRIS)
    canvas.drawCentredString(w/2, 0.7*cm,
        "RC Gestion — Document confidentiel — Reproduire uniquement avec autorisation du cabinet")

    canvas.restoreState()

# ── STYLE TABLEAU ──────────────────────────────────────────────
def style_tableau_base(header_color=None):
    hc = header_color or BLEU_NAVY
    return TableStyle([
        # Entête
        ("BACKGROUND",    (0,0), (-1,0), hc),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANC),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 8),
        ("ALIGN",         (0,0), (-1,0), "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING",    (0,0), (-1,0), 6),
        # Corps
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 8),
        ("TOPPADDING",    (0,1), (-1,-1), 4),
        ("BOTTOMPADDING", (0,1), (-1,-1), 4),
        # Grille
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#C5DDF2")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [BLANC, GRIS_LIGHT]),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ])


# ══════════════════════════════════════════════════════════════
#   1. RAPPORT CLIENT (Fiche complète d'un client)
# ══════════════════════════════════════════════════════════════
def rapport_client(client: dict, declarations=None, paie=None, pieces=None) -> bytes:
    """
    Génère la fiche PDF complète d'un client avec ses déclarations,
    paie et pièces comptables.

    Utilisation dans app.py :
        import pdf_reports
        client = db.get_client(client_id)
        decl   = db.get_declarations(client_id=client_id)
        pdf    = pdf_reports.rapport_client(client, declarations=decl)
        st.download_button("Télécharger PDF", pdf,
                           file_name=f"client_{client_id}.pdf",
                           mime="application/pdf")
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=2.8*cm, bottomMargin=2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = get_styles()
    story = []

    # ── Titre section client ──
    story.append(Spacer(1, 0.3*cm))
    nom = client.get("raison_sociale") or f"{client.get('prenom','')} {client.get('nom','')}".strip()
    story.append(Paragraph(f"Fiche Client — {nom}", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLEU_SKY))
    story.append(Spacer(1, 0.3*cm))

    # ── Bloc identité ──
    tp = client.get("type_personne", "")
    if tp == "Physique":
        infos = [
            ["CIN", client.get("cin","—"),        "Prénom", client.get("prenom","—")],
            ["Nom", client.get("nom","—"),         "Ville",  client.get("ville","—")],
            ["Tél", client.get("telephone","—"),   "Email",  client.get("email","—")],
            ["Secteur", client.get("secteur_activite","—"), "Régime", client.get("regime_fiscal","—")],
            ["Mode décl.", client.get("mode_declaration","—"), "Statut", client.get("statut","—")],
        ]
    else:
        infos = [
            ["Raison sociale", client.get("raison_sociale","—"), "Forme",   client.get("forme_juridique","—")],
            ["RC",             client.get("rc","—"),             "IF",      client.get("if_fiscal","—")],
            ["ICE",            client.get("ice","—"),            "Patente", client.get("patente","—")],
            ["Capital",        f"{client.get('capital_social',0):,.0f} MAD", "Secteur", client.get("secteur_activite","—")],
            ["Tél",            client.get("telephone","—"),      "Email",   client.get("email","—")],
            ["Mode décl.",     client.get("mode_declaration","—"), "Régime", client.get("regime_fiscal","—")],
        ]

    tbl = Table([[Paragraph(str(c), S["label"] if i%2==0 else S["valeur"])
                  for i,c in enumerate(row)] for row in infos],
                colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRIS_LIGHT),
        ("GRID",       (0,0), (-1,-1), 0.4, colors.HexColor("#C5DDF2")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0), (-1,-1), 8),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Déclarations ──
    if declarations is not None and not declarations.empty:
        story.append(Paragraph("Déclarations Fiscales", S["section"]))
        story.append(HRFlowable(width="100%", thickness=0.8, color=BLEU_LIGHT))
        story.append(Spacer(1, 0.2*cm))

        cols_decl = ["Type", "Année", "Période", "Montant dû (MAD)", "Montant payé (MAD)", "Statut"]
        rows = [cols_decl]
        for _, r in declarations.iterrows():
            statut = str(r.get("statut",""))
            rows.append([
                str(r.get("type_decl","")),
                str(r.get("annee","")),
                str(r.get("periode","")),
                f"{float(r.get('montant_du',0)):,.2f}",
                f"{float(r.get('montant_paye',0)):,.2f}",
                statut,
            ])

        t = Table(rows, colWidths=[2.5*cm, 1.8*cm, 3*cm, 3.8*cm, 3.8*cm, 2.5*cm])
        ts = style_tableau_base()
        # Colorier statuts
        for i, row in enumerate(rows[1:], 1):
            st = row[5]
            if st == "En retard":
                ts.add("TEXTCOLOR", (5,i), (5,i), ROUGE)
                ts.add("FONTNAME",  (5,i), (5,i), "Helvetica-Bold")
            elif st == "Deposee":
                ts.add("TEXTCOLOR", (5,i), (5,i), VERT)
        t.setStyle(ts)
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    # ── Paie ──
    if paie is not None and not paie.empty:
        story.append(Paragraph("Bulletins de Paie", S["section"]))
        story.append(HRFlowable(width="100%", thickness=0.8, color=BLEU_LIGHT))
        story.append(Spacer(1, 0.2*cm))

        cols_paie = ["Employé", "Mois", "Brut (MAD)", "CNSS", "AMO", "IR", "Net (MAD)"]
        rows_p = [cols_paie]
        for _, r in paie.iterrows():
            rows_p.append([
                str(r.get("employe","")),
                f"{int(r.get('mois',0))}/{int(r.get('annee',0))}",
                f"{float(r.get('salaire_brut',0)):,.2f}",
                f"{float(r.get('cnss_salariale',0)):,.2f}",
                f"{float(r.get('amo_salariale',0)):,.2f}",
                f"{float(r.get('ir_mensuel',0)):,.2f}",
                f"{float(r.get('salaire_net',0)):,.2f}",
            ])

        t = Table(rows_p, colWidths=[4*cm, 2*cm, 3*cm, 2*cm, 2*cm, 2*cm, 2.5*cm])
        t.setStyle(style_tableau_base(VERT))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Document généré automatiquement par RC Gestion  le {date.today().strftime('%d/%m/%Y')}",
        S["note_bas"]
    ))

    doc.build(story, onFirstPage=entete_pied, onLaterPages=entete_pied)
    return buffer.getvalue()


# ══════════════════════════════════════════════════════════════
#   2. RAPPORT DÉCLARATIONS (Synthèse globale)
# ══════════════════════════════════════════════════════════════
def rapport_declarations(declarations_df, titre="Rapport des Déclarations Fiscales") -> bytes:
    """
    Rapport PDF de toutes les déclarations avec récapitulatif par type.

    Utilisation dans app.py :
        df   = db.get_declarations()
        pdf  = pdf_reports.rapport_declarations(df)
        st.download_button("Rapport Déclarations", pdf,
                           file_name="declarations.pdf",
                           mime="application/pdf")
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=2.8*cm, bottomMargin=2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = get_styles()
    story = []
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(titre, S["section"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLEU_SKY))
    story.append(Spacer(1, 0.3*cm))

    if declarations_df.empty:
        story.append(Paragraph("Aucune déclaration enregistrée.", S["corps"]))
        doc.build(story, onFirstPage=entete_pied, onLaterPages=entete_pied)
        return buffer.getvalue()

    # ── KPIs récap ──
    total_du   = declarations_df["montant_du"].sum()
    total_paye = declarations_df["montant_paye"].sum()
    nb_retard  = (declarations_df["statut"] == "En retard").sum()
    nb_total   = len(declarations_df)

    kpis = [
        ["Total déclarations", str(nb_total),
         "Montant total dû", f"{total_du:,.2f} MAD"],
        ["Montant total payé", f"{total_paye:,.2f} MAD",
         "En retard", str(nb_retard)],
    ]
    t_kpi = Table(kpis, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLEU_LIGHT),
        ("BACKGROUND",    (0,1), (1,1), AMBER_LT),
        ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME",      (1,0), (1,0), "Helvetica-Bold"),
        ("FONTNAME",      (1,1), (1,1), "Helvetica-Bold"),
        ("FONTNAME",      (3,0), (3,0), "Helvetica-Bold"),
        ("FONTNAME",      (3,1), (3,1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (3,1), (3,1), ROUGE),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#C5DDF2")),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 0.5*cm))

    # ── Récap par type ──
    story.append(Paragraph("Récapitulatif par type de déclaration", S["section"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=BLEU_LIGHT))
    story.append(Spacer(1, 0.2*cm))

    grp = declarations_df.groupby("type_decl").agg(
        nb=("id","count"),
        du=("montant_du","sum"),
        paye=("montant_paye","sum")
    ).reset_index()

    rows_grp = [["Type", "Nb décl.", "Total dû (MAD)", "Total payé (MAD)", "Solde (MAD)"]]
    for _, r in grp.iterrows():
        solde = r["du"] - r["paye"]
        rows_grp.append([
            str(r["type_decl"]),
            str(int(r["nb"])),
            f"{r['du']:,.2f}",
            f"{r['paye']:,.2f}",
            f"{solde:,.2f}",
        ])
    t_grp = Table(rows_grp, colWidths=[3.5*cm, 2.5*cm, 4.5*cm, 4.5*cm, 3.5*cm])
    ts = style_tableau_base()
    for i in range(1, len(rows_grp)):
        ts.add("ALIGN", (1,i), (4,i), "RIGHT")
    t_grp.setStyle(ts)
    story.append(t_grp)
    story.append(Spacer(1, 0.5*cm))

    # ── Déclarations en retard ──
    retards = declarations_df[declarations_df["statut"] == "En retard"]
    if not retards.empty:
        story.append(Paragraph(f"Déclarations en retard ({len(retards)})", S["alerte"]))
        story.append(HRFlowable(width="100%", thickness=0.8, color=ROUGE))
        story.append(Spacer(1, 0.2*cm))

        rows_r = [["Client", "Type", "Année", "Période", "Montant dû (MAD)"]]
        for _, r in retards.iterrows():
            rows_r.append([
                str(r.get("client","")),
                str(r.get("type_decl","")),
                str(r.get("annee","")),
                str(r.get("periode","")),
                f"{float(r.get('montant_du',0)):,.2f}",
            ])
        t_r = Table(rows_r, colWidths=[5*cm, 2.5*cm, 2*cm, 3*cm, 4*cm])
        ts_r = style_tableau_base(colors.HexColor("#C0392B"))
        for i in range(1, len(rows_r)):
            ts_r.add("TEXTCOLOR", (4,i), (4,i), ROUGE)
            ts_r.add("FONTNAME",  (4,i), (4,i), "Helvetica-Bold")
        t_r.setStyle(ts_r)
        story.append(t_r)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Rapport généré automatiquement par RC Gestion le {date.today().strftime('%d/%m/%Y')}",
        S["note_bas"]
    ))

    doc.build(story, onFirstPage=entete_pied, onLaterPages=entete_pied)
    return buffer.getvalue()


# ══════════════════════════════════════════════════════════════
#   3. BULLETIN DE PAIE (1 employé / 1 mois)
# ══════════════════════════════════════════════════════════════
MOIS_NOMS = ["","Janvier","Février","Mars","Avril","Mai","Juin",
             "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

def bulletin_paie(paie_row: dict, client: dict) -> bytes:
    """
    Génère un bulletin de paie PDF pour un employé.

    Utilisation dans app.py :
        df   = db.get_paie(client_id=client_id)
        row  = df.iloc[idx].to_dict()
        cli  = db.get_client(client_id)
        pdf  = pdf_reports.bulletin_paie(row, cli)
        st.download_button("Bulletin PDF", pdf,
                           file_name=f"bulletin_{row['employe']}_{row['mois']}_{row['annee']}.pdf",
                           mime="application/pdf")
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=2.8*cm, bottomMargin=2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = get_styles()
    story = []

    mois_nom = MOIS_NOMS[int(paie_row.get("mois", 1))]
    annee    = int(paie_row.get("annee", date.today().year))
    employe  = str(paie_row.get("employe",""))
    nom_soc  = client.get("raison_sociale") or f"{client.get('prenom','')} {client.get('nom','')}".strip()

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Bulletin de Paie — {mois_nom} {annee}", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLEU_SKY))
    story.append(Spacer(1, 0.3*cm))

    # Infos employeur / employé
    infos = [
        ["Employeur", nom_soc,        "Employé", employe],
        ["CIN",       paie_row.get("employe_cin","—"), "Mois", f"{mois_nom} {annee}"],
    ]
    t_info = Table(infos, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    t_info.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), GRIS_LIGHT),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#C5DDF2")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 0.5*cm))

    # Détail du bulletin
    brut     = float(paie_row.get("salaire_brut", 0))
    cnss_sal = float(paie_row.get("cnss_salariale", 0))
    amo_sal  = float(paie_row.get("amo_salariale", 0))
    ir       = float(paie_row.get("ir_mensuel", 0))
    avances  = float(paie_row.get("avances", 0))
    net      = float(paie_row.get("salaire_net", 0))
    cnss_pat = float(paie_row.get("cnss_patronale", 0))
    amo_pat  = float(paie_row.get("amo_patronale", 0))

    lignes = [
        ["Rubrique",                       "Taux",    "Montant (MAD)"],
        ["Salaire Brut",                   "",        f"{brut:,.2f}"],
        ["CNSS Salariale",                 "4,48%",   f"- {cnss_sal:,.2f}"],
        ["AMO Salariale",                  "2,26%",   f"- {amo_sal:,.2f}"],
        ["IR Mensuel (barème DGI)",        "Progressif", f"- {ir:,.2f}"],
        ["Avances sur salaire",            "",        f"- {avances:,.2f}"],
        ["SALAIRE NET A PAYER",            "",        f"{net:,.2f}"],
    ]

    t_bul = Table(lignes, colWidths=[9*cm, 3.5*cm, 5*cm])
    ts_bul = TableStyle([
        # Entête
        ("BACKGROUND",    (0,0), (-1,0), BLEU_NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANC),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 9),
        ("ALIGN",         (1,0), (-1,0), "CENTER"),
        # Corps
        ("FONTNAME",      (0,1), (-1,-2), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (2,1), (2,-1), "RIGHT"),
        ("TEXTCOLOR",     (2,2), (2,5), ROUGE),
        # Ligne net
        ("BACKGROUND",    (0,-1), (-1,-1), VERT_LIGHT),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (2,-1), (2,-1), VERT),
        ("FONTSIZE",      (0,-1), (-1,-1), 11),
        # Grille
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#C5DDF2")),
        ("ROWBACKGROUNDS",(0,1), (-1,-2), [BLANC, GRIS_LIGHT]),
    ])
    t_bul.setStyle(ts_bul)
    story.append(t_bul)
    story.append(Spacer(1, 0.5*cm))

    # Charges patronales
    story.append(Paragraph("Charges Patronales (à titre indicatif)", S["corps_bold"]))
    t_pat = Table([
        ["CNSS Patronale (8,98%)", f"{cnss_pat:,.2f} MAD"],
        ["AMO Patronale (3,96%)",  f"{amo_pat:,.2f} MAD"],
        ["Total charges patronales", f"{cnss_pat + amo_pat:,.2f} MAD"],
    ], colWidths=[9*cm, 9*cm])
    t_pat.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-2), "Helvetica"),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("BACKGROUND",    (0,0), (-1,-1), AMBER_LT),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#C5DDF2")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (1,0), (1,-1), "RIGHT"),
    ]))
    story.append(t_pat)
    story.append(Spacer(1, 0.5*cm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=BLEU_LIGHT))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Bulletin généré automatiquement selon le barème IR DGI Maroc et les taux CNSS/AMO en vigueur.",
        S["note_bas"]
    ))

    doc.build(story, onFirstPage=entete_pied, onLaterPages=entete_pied)
    return buffer.getvalue()


# ══════════════════════════════════════════════════════════════
#   4. RAPPORT GÉNÉRAL DU CABINET
# ══════════════════════════════════════════════════════════════
def rapport_general(stats: dict, clients_df=None, declarations_df=None) -> bytes:
    """
    Rapport de synthèse global du cabinet (tableau de bord exporté en PDF).

    Utilisation dans app.py :
        stats = db.get_stats()
        cli   = db.get_clients()
        decl  = db.get_declarations()
        pdf   = pdf_reports.rapport_general(stats, cli, decl)
        st.download_button("Rapport Général", pdf,
                           file_name="rapport_cabinet.pdf",
                           mime="application/pdf")
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=2.8*cm, bottomMargin=2*cm,
                            leftMargin=1.5*cm, rightMargin=1.5*cm)
    S = get_styles()
    story = []
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Rapport Général du Cabinet", S["section"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLEU_SKY))
    story.append(Spacer(1, 0.4*cm))

    # ── KPIs ──
    story.append(Paragraph("Indicateurs Clés", S["corps_bold"]))
    story.append(Spacer(1, 0.2*cm))
    kpis = [
        ["Total clients", str(stats.get("total_clients",0)),
         "dont PP",       str(stats.get("pp",0))],
        ["dont PM",       str(stats.get("pm",0)),
         "Clients actifs",str(stats.get("actifs",0))],
        ["Déclarations",  str(stats.get("decl_total",0)),
         "En retard",     str(stats.get("decl_retard",0))],
        ["CA total (TTC)", f"{float(stats.get('ca_total',0)):,.0f} MAD",
         "Montant dû total", f"{float(stats.get('montant_du',0)):,.0f} MAD"],
    ]
    t_kpi = Table(kpis, colWidths=[5*cm, 4.5*cm, 5*cm, 4*cm])
    t_kpi.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("BACKGROUND",    (0,0), (-1,-1), GRIS_LIGHT),
        ("BACKGROUND",    (2,2), (3,2), AMBER_LT),
        ("TEXTCOLOR",     (3,2), (3,2), ROUGE),
        ("FONTNAME",      (3,2), (3,2), "Helvetica-Bold"),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#C5DDF2")),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 0.5*cm))

    # ── Liste clients ──
    if clients_df is not None and not clients_df.empty:
        story.append(Paragraph("Liste des Clients", S["section"]))
        story.append(HRFlowable(width="100%", thickness=0.8, color=BLEU_LIGHT))
        story.append(Spacer(1, 0.2*cm))

        rows_c = [["Type","Nom / Raison sociale","Secteur","Ville","Mode décl.","Statut"]]
        for _, r in clients_df.iterrows():
            nom = r.get("raison_sociale") or f"{r.get('prenom','')} {r.get('nom','')}".strip()
            rows_c.append([
                "PP" if r.get("type_personne")=="Physique" else "PM",
                nom[:30],
                str(r.get("secteur_activite",""))[:15],
                str(r.get("ville",""))[:15],
                str(r.get("mode_declaration","")),
                str(r.get("statut","")),
            ])
        t_c = Table(rows_c, colWidths=[1.5*cm, 5.5*cm, 3*cm, 3*cm, 2.5*cm, 2*cm])
        ts_c = style_tableau_base()
        for i, row in enumerate(rows_c[1:], 1):
            if row[5] != "Actif":
                ts_c.add("TEXTCOLOR", (5,i), (5,i), ROUGE)
        t_c.setStyle(ts_c)
        story.append(t_c)

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        f"Rapport généré automatiquement par RC Gestion le {date.today().strftime('%d/%m/%Y')}",
        S["note_bas"]
    ))

    doc.build(story, onFirstPage=entete_pied, onLaterPages=entete_pied)
    return buffer.getvalue()
