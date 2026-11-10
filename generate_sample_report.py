#!/usr/bin/env python3
"""Build a synthetic human-review report from T11 checker output; never reads ground truth."""
from pathlib import Path
import json, datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
ROOT=Path(__file__).resolve().parent
res=json.loads((ROOT/'04_VERIFICATION_SPIKE/results/T11.json').read_text())
assert res['case_id']=='T11'
assert len(res['findings'])==2, 'T11 report expects exactly two independent checker warnings'
out=ROOT/'07_SAMPLE_VERIFICATION_REPORT.pdf'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCenter',parent=styles['Title'],alignment=TA_CENTER,textColor=colors.HexColor('#12304A'),fontName='Helvetica-Bold',fontSize=17,leading=20,spaceAfter=5))
styles.add(ParagraphStyle(name='Subtle',parent=styles['BodyText'],fontSize=8,leading=10,textColor=colors.HexColor('#536273')))
styles.add(ParagraphStyle(name='Cell',parent=styles['BodyText'],fontSize=8,leading=10,spaceAfter=0))
styles.add(ParagraphStyle(name='CellBold',parent=styles['Cell'],fontName='Helvetica-Bold'))
styles.add(ParagraphStyle(name='HeaderCell',parent=styles['Cell'],fontName='Helvetica-Bold',textColor=colors.white))
styles.add(ParagraphStyle(name='Alert',parent=styles['BodyText'],fontSize=8.5,leading=11,textColor=colors.HexColor('#7A341A')))

doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=13*mm,bottomMargin=14*mm,title='Synthetic Administrative Verification Report T11',author='Experimental checker')
story=[]
story.append(Paragraph('SYNTHETIC BUNDLE — TEST ONLY',styles['Subtle']))
story.append(Paragraph('Administrative Verification Report',styles['TitleCenter']))
story.append(Paragraph('Case T11 · two independent warnings · generated from the checker output',ParagraphStyle('center',parent=styles['BodyText'],alignment=TA_CENTER,fontSize=9,textColor=colors.HexColor('#425466'))))
story.append(Spacer(1,4*mm))
meta=[['Input file',res['pdf'],'Pages',str(res['pages'])],['Input SHA-256',res['sha256'],'Checker',res['checker_version']],['Reference inputs','Synthetic expected inventory + version register','OCR / AI','Not used']]
t=Table([[Paragraph(str(x),styles['CellBold'] if i%2==0 else styles['Cell']) for i,x in enumerate(row)] for row in meta],colWidths=[26*mm,69*mm,20*mm,54*mm])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),colors.HexColor('#EEF3F7')),('BACKGROUND',(2,0),(2,-1),colors.HexColor('#EEF3F7')),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#CFD8E0')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story += [t,Spacer(1,4*mm),Paragraph('Warnings for human verification',styles['Heading2'])]

def p(text,bold=False):
    if bold: text='<b>'+text+'</b>'
    return Paragraph(text,styles['Cell'])
rows=[[Paragraph('ID',styles['HeaderCell']),Paragraph('Document / location',styles['HeaderCell']),Paragraph('Discrepancy and supporting evidence',styles['HeaderCell']),Paragraph('Suggested human action / uncertainty',styles['HeaderCell'])]]
for i,f in enumerate(res['findings'],1):
    typ=f['type']
    if typ=='MISSING_EXPECTED_DOCUMENT':
        ident=f['location']; loc='No physical page; expected item '+ident
        confidence='Medium-high for absence of this identifier from the supplied text layer; depends on inventory correctness and readable identifiers.'
    elif typ=='BUNDLE_PAGINATION_MISMATCH':
        ident='Not applicable — bundle-level page label'; loc=f['location']
        confidence='High that the printed label and PDF physical position disagree; does not establish which numbering convention is required.'
    else:
        ident=f['location']; loc=f['location']; confidence='Review required.'
    details='<b>'+f['type'].replace('_',' ')+'</b><br/>'+f['evidence']
    action=f['human_action']+'<br/><br/><font color="#536273"><b>Confidence:</b> {}</font>'.format(confidence)
    rows.append([p(f'W{i:02d}',True),p('<b>'+ident+'</b><br/>'+loc),Paragraph(details,styles['Cell']),Paragraph(action,styles['Cell'])])
t=Table(rows,colWidths=[11*mm,43*mm,62*mm,53*mm],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#12304A')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#CFD8E0')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FB')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story += [t,Spacer(1,4*mm),Paragraph('Scope and limitations',styles['Heading2']),Paragraph('This report reflects only text markers and reference data supplied with a fictional 40–60 page test bundle. The checker did not use OCR or AI and did not inspect semantic content, legal relevance, authenticity, admissibility or court-specific requirements. A warning is a prompt to compare the source material, not a legal conclusion. No real case or person is represented.',styles['BodyText']),Spacer(1,3*mm)]
required='Administrative verification only. This report does not establish legal completeness, procedural compliance or filing readiness. Final review remains the responsibility of the qualified legal professional.'
story.append(Paragraph('<b>'+required+'</b>',styles['Alert']))
story.append(Spacer(1,3*mm))
story.append(Paragraph('Generated '+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')+' · Local checker processing time: '+str(res['processing_seconds'])+' seconds · For evaluation only; not for filing.',styles['Subtle']))
doc.build(story)
print(out)
