#!/usr/bin/env python3
"""Deterministically generate synthetic, fictional court-bundle PDFs and separate ground truth.
All documents are explicitly simulated and are not legal filings or real records.
"""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import json, csv, hashlib, io

ROOT = Path(__file__).resolve().parent
PDFDIR = ROOT / 'pdfs'
META = ROOT / 'metadata'
PRIVATE = ROOT.parent / 'ground_truth_private'
for p in [PDFDIR, META, PRIVATE]: p.mkdir(parents=True, exist_ok=True)

DOCS = [
 {'id':'DOC-01','title':'Simulated Statement of Claim','kind':'Pleading','pages':5,'version':'V2','exhibit_label':''},
 {'id':'DOC-02','title':'Simulated Supporting Affidavit','kind':'Affidavit','pages':5,'version':'V3','exhibit_label':''},
 {'id':'DOC-03','title':'Simulated Annexure A — Schedule of Items','kind':'Annexure','pages':8,'version':'V1','exhibit_label':'A'},
 {'id':'DOC-04','title':'Simulated Annexure B — Correspondence','kind':'Annexure','pages':6,'version':'V2','exhibit_label':'B'},
 {'id':'DOC-05','title':'Simulated Service Correspondence','kind':'Correspondence','pages':4,'version':'V1','exhibit_label':''},
 {'id':'DOC-06','title':'Simulated Statement of Response','kind':'Pleading','pages':5,'version':'V2','exhibit_label':''},
 {'id':'DOC-07','title':'Simulated Replying Affidavit','kind':'Affidavit','pages':4,'version':'V1','exhibit_label':''},
 {'id':'DOC-08','title':'Simulated Annexure C — Summary Table','kind':'Annexure','pages':7,'version':'V1','exhibit_label':'C'},
]

# Fictional expected inventory and version register, supplied to the checker.
inventory = {
 'scenario':'FICTIONAL TEST SCENARIO — NOT A REAL CASE OR COURT FILING',
 'case_reference':'SIM-CIV-2026-0042',
 'documents':[{'document_id':d['id'],'title':d['title'],'expected_pages':d['pages'],'version':d['version'],'exhibit_label':d['exhibit_label']} for d in DOCS]
}
versions = {'case_reference':inventory['case_reference'],'expected_versions':{d['id']:d['version'] for d in DOCS}}
(META/'expected_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
(META/'version_register.json').write_text(json.dumps(versions,indent=2)+'\n')
with (META/'expected_inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['document_id','title','expected_pages','version','exhibit_label']); w.writeheader(); w.writerows(inventory['documents'])
with (META/'version_register.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['document_id','expected_version']); w.writerows(versions['expected_versions'].items())

# Each page contains stable, unique synthetic content so exact/near duplicates are testable.
def paragraph(doc, page, seed=0):
    anchors = [
      'Fictional record category: procedural narrative for testing page assembly.',
      'Fictional location code: KIF-ALPHA; this code has no real-world address or owner.',
      'Simulated event date: 14 February 2026; generated only for this experiment.',
      'This page contains no real names, accounts, signatures, evidence, bank details or client material.',
      'Reference token: '+hashlib.sha256(f"{doc['id']}|{page}|{seed}".encode()).hexdigest()[:16]+'.',
      'The words on this page are synthetic filler. They assert no fact and have no legal effect.',
      'For repeatability, this fixed sentence is paired with a unique document and page marker.',
      'A checker may compare the supplied identifier and page sequence but must not infer legal completeness.'
    ]
    if seed:
      anchors[0] = anchors[0].replace('procedural narrative','synthetic procedural narrative')
    return anchors

def draw_text_page(c, doc, page_num, bundle_num, *, version=None, exhibit=None, seed=0, global_override=None, layout='normal', near_change=False):
    size = landscape(A4) if layout == 'landscape' else A4
    c.setPageSize(size)
    w,h=size
    c.setFont('Helvetica-Bold',13)
    c.drawString(22*mm,h-22*mm,'SIMULATION ONLY — NOT A REAL COURT FILING')
    c.setStrokeColor(colors.HexColor('#888888'))
    c.line(22*mm,h-26*mm,w-22*mm,h-26*mm)
    c.setFont('Helvetica-Bold',11)
    c.drawString(22*mm,h-39*mm,doc['title'])
    c.setFont('Courier',8.5)
    c.drawString(22*mm,h-48*mm,f"DOCUMENT_ID: {doc['id']}")
    c.drawString(22*mm,h-55*mm,f"DOCUMENT_PAGE: {page_num}/{doc['pages']}")
    c.drawString(22*mm,h-62*mm,f"DOCUMENT_VERSION: {version or doc['version']}")
    ex = doc['exhibit_label'] if exhibit is None else exhibit
    c.drawString(22*mm,h-69*mm,f"EXHIBIT_LABEL: {ex if ex else 'NONE'}")
    c.setFont('Helvetica',8.5 if near_change else 9)
    yy=h-84*mm
    lines=paragraph(doc,page_num,seed)
    if near_change:
      lines[0]=lines[0].replace('procedural narrative','procedural account')
    for line in lines:
      c.drawString((25.4 if near_change else 25)*mm,yy,line); yy-=(7.8 if near_change else 8)*mm
    c.setFont('Helvetica-Oblique',8)
    c.drawString(22*mm,24*mm,'SIMULATED DOCUMENT — NO ACTUAL PARTIES, FACTS, ADVOCATES OR EVIDENCE')
    label = global_override if global_override is not None else bundle_num
    c.setFont('Courier-Bold',9)
    c.drawRightString(w-22*mm,12*mm,f'BUNDLE_PAGE: {label}')
    c.showPage()

def draw_cover(c, bundle_num=1, seed=0):
    c.setPageSize(A4); w,h=A4
    c.setFont('Helvetica-Bold',16); c.drawCentredString(w/2,h-45*mm,'SYNTHETIC BUNDLE — TEST ONLY')
    c.setFont('Helvetica-Bold',12); c.drawCentredString(w/2,h-62*mm,'NOT FOR FILING — FICTIONAL CONTENT')
    c.setFont('Courier',10); c.drawString(25*mm,h-90*mm,'SIMULATED_REFERENCE: SIM-CIV-2026-0042')
    c.drawString(25*mm,h-102*mm,'SIMULATED_PARTY_A: Aster Vale (fictional)')
    c.drawString(25*mm,h-114*mm,'SIMULATED_PARTY_B: Brindle Quay (fictional)')
    c.drawString(25*mm,h-126*mm,'No real court, client, person, matter or legal claim is represented.')
    c.setFont('Courier-Bold',9); c.drawRightString(w-22*mm,12*mm,f'BUNDLE_PAGE: {bundle_num}')
    c.showPage()

def draw_index(c, docs_order, start_pages, bundle_num=2, seed=0, index_override=None):
    c.setPageSize(A4); w,h=A4
    c.setFont('Helvetica-Bold',15); c.drawString(22*mm,h-25*mm,'SIMULATED DOCUMENT INDEX')
    c.setFont('Helvetica',9); c.drawString(22*mm,h-34*mm,'Generated for mechanical verification only; not a court-approved format.')
    y=h-49*mm
    c.setFont('Courier-Bold',8)
    c.drawString(22*mm,y,'DOCUMENT_ID | DESCRIPTION | EXPECTED START PAGE'); y-=8*mm
    c.setFont('Courier',8)
    for d in docs_order:
      start = start_pages[d['id']]
      if index_override and d['id'] in index_override: start=index_override[d['id']]
      c.drawString(22*mm,y,f"INDEX_ENTRY: {d['id']} | start={start} | {d['title'][:38]}")
      y-=7*mm
    c.setFont('Helvetica-Oblique',8)
    c.drawString(22*mm,28*mm,'Inventory and version register are separate supplied test inputs.')
    c.setFont('Courier-Bold',9); c.drawRightString(w-22*mm,12*mm,f'BUNDLE_PAGE: {bundle_num}')
    c.showPage()

def make_bundle(path, *, docs_order=None, omit_doc=None, omit_page=None, duplicate_page=None, near_duplicate_page=None,
                page_label_error=None, index_error=None, wrong_version=None, wrong_exhibit=None, unreadable_page=None,
                seed=0, landscape_page=None, stale_index=False):
    docs_order=docs_order or list(DOCS)
    original_order=list(DOCS)
    # Build ordered page specs, retaining printed document-local page labels after omissions/insertion.
    specs=[]
    for d in docs_order:
      if d['id']==omit_doc: continue
      for p in range(1,d['pages']+1):
        if omit_page==(d['id'],p): continue
        specs.append({'doc':d,'p':p,'version':(wrong_version[1] if wrong_version and d['id']==wrong_version[0] else d['version']),
                      'exhibit':(wrong_exhibit[1] if wrong_exhibit and d['id']==wrong_exhibit[0] else d['exhibit_label']),
                      'near':False,'dup':False,'layout':'normal'})
        if duplicate_page==(d['id'],p):
          specs.append({'doc':d,'p':p,'version':d['version'],'exhibit':d['exhibit_label'],'near':False,'dup':True,'layout':'normal'})
        if near_duplicate_page==(d['id'],p):
          specs.append({'doc':d,'p':p,'version':d['version'],'exhibit':d['exhibit_label'],'near':True,'dup':False,'layout':'normal'})
        if landscape_page==(d['id'],p): specs[-1]['layout']='landscape'
    # Physical position starts after cover + index. Index lists expected docs, including an intentionally missing T02 item.
    page_of={}
    for i,s in enumerate(specs, start=3):
      page_of.setdefault(s['doc']['id'],i)
    index_docs=docs_order
    start_map={}
    for d in index_docs:
      if d['id'] in page_of: start_map[d['id']]=page_of[d['id']]
      else:
        # Preserve the clean-baseline expected start for a missing document.
        start_map[d['id']]=3+sum(x['pages'] for x in original_order[:original_order.index(d)])
    if stale_index:
      start_map={d['id']:3+sum(x['pages'] for x in original_order[:original_order.index(d)]) for d in index_docs}
    overrides={}
    if index_error:
      docid,delta=index_error; overrides[docid]=start_map[docid]+delta
    c=canvas.Canvas(str(path),pagesize=A4,pageCompression=0)
    draw_cover(c,1,seed)
    draw_index(c,index_docs,start_map,2,seed,overrides)
    for pos,s in enumerate(specs,start=3):
      if unreadable_page==(s['doc']['id'],s['p']) and not s['dup'] and not s['near']:
        draw_low_quality_scan(c,s['doc'],s['p'],pos)
      else:
        global_override=(pos+1 if page_label_error==pos else None)
        draw_text_page(c,s['doc'],s['p'],pos,version=s['version'],exhibit=s['exhibit'],seed=seed,
                       global_override=global_override,layout=s['layout'],near_change=s['near'])
    c.save()

def draw_low_quality_scan(c,doc,p,bundle_num):
    # Low-resolution synthetic raster only: deliberately no searchable text layer.
    im=Image.new('RGB',(160,220),'white'); d=ImageDraw.Draw(im)
    try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',7)
    except Exception: font=ImageFont.load_default()
    d.text((5,5),'SIMULATION ONLY',fill='black',font=font)
    d.text((5,25),doc['id'],fill='black',font=font)
    d.text((5,38),f'DOCUMENT_PAGE {p}/{doc["pages"]}',fill='black',font=font)
    d.text((5,50),f'VERSION {doc["version"]}',fill='black',font=font)
    d.text((5,75),'LOW RESOLUTION SYNTHETIC SCAN',fill='black',font=font)
    bio=io.BytesIO(); im.save(bio,format='PNG'); bio.seek(0)
    c.setPageSize(A4); c.drawImage(ImageReader(bio),0,0,width=A4[0],height=A4[1])
    # Page label is part of the same image: text extraction must report this page as opaque.
    c.showPage()

# Baseline and independent variants.
make_bundle(PDFDIR/'T01_clean_baseline.pdf')
make_bundle(PDFDIR/'T02_missing_annexure.pdf',omit_doc='DOC-03',stale_index=True)
make_bundle(PDFDIR/'T03_missing_internal_page.pdf',omit_page=('DOC-03',4))
make_bundle(PDFDIR/'T04_exact_duplicate_page.pdf',duplicate_page=('DOC-03',3))
make_bundle(PDFDIR/'T05_near_duplicate_page.pdf',near_duplicate_page=('DOC-03',3))
make_bundle(PDFDIR/'T06_broken_continuous_pagination.pdf',page_label_error=15)
make_bundle(PDFDIR/'T07_index_reference_mismatch.pdf',index_error=('DOC-04',2))
make_bundle(PDFDIR/'T08_wrong_document_version.pdf',wrong_version=('DOC-02','V1'))
make_bundle(PDFDIR/'T09_exhibit_label_mismatch.pdf',wrong_exhibit=('DOC-03','Z'))
make_bundle(PDFDIR/'T10_low_quality_raster_page.pdf',unreadable_page=('DOC-04',3))
make_bundle(PDFDIR/'T11_two_independent_defects.pdf',omit_doc='DOC-03',page_label_error=12,stale_index=True)
make_bundle(PDFDIR/'T12_clean_unusual_landscape.pdf',landscape_page=('DOC-04',3))
# Additional clean variations for false-alarm checking.
make_bundle(PDFDIR/'C01_clean_text_variation.pdf',seed=1)
make_bundle(PDFDIR/'C02_clean_reordered_documents.pdf',docs_order=list(reversed(DOCS)))

cases=[
('T01','T01_clean_baseline.pdf',[]),('T02','T02_missing_annexure.pdf',['MISSING_EXPECTED_DOCUMENT']),
('T03','T03_missing_internal_page.pdf',['DOCUMENT_PAGE_SEQUENCE_GAP']),
('T04','T04_exact_duplicate_page.pdf',['EXACT_DUPLICATE_PAGE']),
('T05','T05_near_duplicate_page.pdf',['NEAR_DUPLICATE_PAGE']),
('T06','T06_broken_continuous_pagination.pdf',['BUNDLE_PAGINATION_MISMATCH']),
('T07','T07_index_reference_mismatch.pdf',['INDEX_START_PAGE_MISMATCH']),
('T08','T08_wrong_document_version.pdf',['VERSION_MISMATCH']),
('T09','T09_exhibit_label_mismatch.pdf',['EXHIBIT_LABEL_MISMATCH']),
('T10','T10_low_quality_raster_page.pdf',['NO_EXTRACTABLE_TEXT_LAYER']),
('T11','T11_two_independent_defects.pdf',['MISSING_EXPECTED_DOCUMENT','BUNDLE_PAGINATION_MISMATCH']),
('T12','T12_clean_unusual_landscape.pdf',[]),
('C01','C01_clean_text_variation.pdf',[]),('C02','C02_clean_reordered_documents.pdf',[])
]
# Ground truth is isolated from the checker and runner inputs. This file is not copied into checker path.
gt={'notice':'GROUND TRUTH — DO NOT PASS TO CHECKER DURING DETECTION','cases':[]}
for case_id,filename,defects in cases:
    locations=[]
    if case_id=='T02': locations=['DOC-03 absent; listed in expected inventory']
    elif case_id=='T03': locations=['DOC-03 local page 4/8 absent']
    elif case_id in ('T04','T05'): locations=['DOC-03 local page 3/8 duplicated or near-duplicated']
    elif case_id=='T06': locations=['physical bundle page 15 carries printed BUNDLE_PAGE 16']
    elif case_id=='T07': locations=['DOC-04 index start page deliberately increased by 2']
    elif case_id=='T08': locations=['DOC-02 included version V1; expected register says V3']
    elif case_id=='T09': locations=['DOC-03 label Z; inventory says exhibit A']
    elif case_id=='T10': locations=['DOC-04 local page 3/6 is a low-resolution raster without text layer']
    elif case_id=='T11': locations=['DOC-03 absent from page text; physical page 12 has incorrect bundle label']
    gt['cases'].append({'case_id':case_id,'file':filename,'injected_defects':defects,'locations':locations,'expected_result':'flag' if defects else 'no flag'})
(PRIVATE/'ground_truth.json').write_text(json.dumps(gt,indent=2)+'\n')
with (META/'test_manifest.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['case_id','pdf','purpose','checker_inputs'])
 for cid,fn,defs in cases:
  label='clean control' if not defs else 'known defective variant; defect labels withheld from checker'
  w.writerow([cid,f'pdfs/{fn}',label,'metadata/expected_inventory.json; metadata/version_register.json'])
# Hash every input artifact.
manifest=[]
for p in sorted([*PDFDIR.glob('*.pdf'),*META.glob('*')]):
 if p.is_file(): manifest.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(META/'sha256_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'pdf_count':len(list(PDFDIR.glob('*.pdf'))),'baseline_pdf':str(PDFDIR/'T01_clean_baseline.pdf'),'baseline_pages':46,'ground_truth_path':str(PRIVATE/'ground_truth.json'),'manifest_path':str(META/'test_manifest.csv')},indent=2))
