#!/usr/bin/env python3
"""Experimental administrative PDF checker. No ground truth is read.
Deterministic, text-layer-only checks; no OCR, AI, legal judgment, or network use.
"""
from pathlib import Path
from pypdf import PdfReader
from difflib import SequenceMatcher
import argparse, csv, hashlib, json, re, time

VERSION='0.1.0'
PAGE_RE=re.compile(r'DOCUMENT_PAGE:\s*(\d+)\s*/\s*(\d+)',re.I)
ID_RE=re.compile(r'DOCUMENT_ID:\s*(DOC-[A-Z0-9-]+)',re.I)
BUNDLE_RE=re.compile(r'BUNDLE_PAGE:\s*(\d+)',re.I)
VERSION_RE=re.compile(r'DOCUMENT_VERSION:\s*([A-Z0-9._-]+)',re.I)
EXHIBIT_RE=re.compile(r'EXHIBIT_LABEL:\s*([^\r\n]+)',re.I)
INDEX_RE=re.compile(r'INDEX_ENTRY:\s*(DOC-[A-Z0-9-]+)\s*\|\s*start=(\d+)',re.I)


def norm_text(t):
    t=t or ''
    t=re.sub(r'BUNDLE_PAGE:\s*\d+','',t,flags=re.I)
    return re.sub(r'\s+',' ',t).strip().casefold()


def load_json(p):
    return json.loads(Path(p).read_text())


def flag(kind, severity, location, evidence, action):
    return {'type':kind,'severity':severity,'location':location,'evidence':evidence,'human_action':action}


def check(pdf_path, inventory_path, versions_path):
    start=time.perf_counter()
    inv=load_json(inventory_path)
    vers=load_json(versions_path).get('expected_versions',{})
    reader=PdfReader(str(pdf_path),strict=False)
    pages=[]; findings=[]
    for i,page in enumerate(reader.pages,1):
        try: text=page.extract_text() or ''
        except Exception: text=''
        pages.append({'physical':i,'text':text})
    if not pages: findings.append(flag('EMPTY_PDF','error','document','No PDF pages were read.','Verify the source file opens and is not corrupt.'))

    opaque=[]
    for p in pages:
        if len(re.sub(r'\s+','',p['text'])) < 20:
            opaque.append(p['physical'])
            findings.append(flag('NO_EXTRACTABLE_TEXT_LAYER','warning',f"PDF page {p['physical']}",
              'The page yielded fewer than 20 non-whitespace characters from the embedded text layer; visual readability was not assessed.',
              'Open the page visually and confirm legibility; OCR or another accessible source may be needed.'))

    doc_pages={}; doc_versions={}; doc_exhibits={}; actual_starts={}; normalized=[]
    for p in pages:
        txt=p['text']; m=ID_RE.search(txt)
        if m:
            doc=m.group(1).upper(); doc_pages.setdefault(doc,[]).append((p['physical'],txt))
            actual_starts.setdefault(doc,p['physical'])
            vm=VERSION_RE.search(txt)
            if vm: doc_versions.setdefault(doc,set()).add(vm.group(1).upper())
            em=EXHIBIT_RE.search(txt)
            if em: doc_exhibits.setdefault(doc,set()).add(em.group(1).strip().upper())
        bm=BUNDLE_RE.search(txt)
        if bm and int(bm.group(1))!=p['physical']:
            findings.append(flag('BUNDLE_PAGINATION_MISMATCH','error',f"PDF page {p['physical']}",
              f"Printed BUNDLE_PAGE is {bm.group(1)}; PDF physical position is {p['physical']}.",
              'Check continuous page numbering and its starting point.'))
        normalized.append(norm_text(txt))

    expected={d['document_id']:d for d in inv.get('documents',[])}
    absent=sorted(set(expected)-set(doc_pages))
    for doc in absent:
        findings.append(flag('MISSING_EXPECTED_DOCUMENT','error',doc,
          'Document is listed in the supplied expected inventory but no page carries this document identifier.',
          'Check the source file set and confirm whether the expected document belongs in this bundle.'))

    # Local page-sequence labels can expose missing internal pages when pages are text-readable.
    # If any opaque page exists, do not infer a missing page from absent labels alone.
    if not opaque:
        for doc, seen in doc_pages.items():
            nums=[]
            totals=set()
            for _,txt in seen:
                m=PAGE_RE.search(txt)
                if m: nums.append(int(m.group(1))); totals.add(int(m.group(2)))
            if nums:
                expected_total=max(totals) if totals else None
                missing=sorted(set(range(1,expected_total+1))-set(nums)) if expected_total else []
                repeated=sorted(n for n in set(nums) if nums.count(n)>1)
                if missing:
                    findings.append(flag('DOCUMENT_PAGE_SEQUENCE_GAP','error',doc,
                      f"Printed document-local page sequence omits page number(s): {', '.join(map(str,missing))}.",
                      'Compare the assembled PDF with the authoritative source document.'))
                # Repeated local page numbers are retained as supporting evidence, but not separately scored.

    # Compare one consistent expected version and exhibit label per document.
    for doc, rec in expected.items():
        if doc not in doc_pages: continue
        actual=doc_versions.get(doc,set()); want=str(vers.get(doc,rec.get('version',''))).upper()
        if want and actual and actual!={want}:
            findings.append(flag('VERSION_MISMATCH','error',doc,
              f"Version register expects {want}; text-layer page labels contain: {', '.join(sorted(actual))}.",
              'Confirm the operative source version with the responsible legal professional.'))
        want_ex=str(rec.get('exhibit_label','')).strip().upper()
        if want_ex:
            actual_ex=doc_exhibits.get(doc,set())
            if actual_ex and actual_ex!={want_ex}:
                findings.append(flag('EXHIBIT_LABEL_MISMATCH','error',doc,
                  f"Inventory expects exhibit label {want_ex}; text-layer page labels contain: {', '.join(sorted(actual_ex))}.",
                  'Compare the exhibit divider and source inventory; do not infer legal identity from the label alone.'))

    # Compare index starts with first observed occurrence; suppress cascade if an expected document is absent.
    if not absent:
        for p in pages:
            for m in INDEX_RE.finditer(p['text']):
                doc=m.group(1).upper(); stated=int(m.group(2))
                observed=actual_starts.get(doc)
                if observed is not None and observed!=stated:
                    findings.append(flag('INDEX_START_PAGE_MISMATCH','error',doc,
                      f"Index states start page {stated}; first text-layer occurrence is PDF page {observed}.",
                      'Check index references against the assembled document order.'))

    # Exact/near duplicate comparisons on normalized extracted text, excluding dynamic global page labels.
    texts=[(p['physical'],normalized[p['physical']-1]) for p in pages if normalized[p['physical']-1]]
    exact_pairs=[]; near_pairs=[]
    for i in range(len(texts)):
        for j in range(i+1,len(texts)):
            pi,ti=texts[i]; pj,tj=texts[j]
            if len(ti)<80 or len(tj)<80: continue
            if ti==tj:
                exact_pairs.append((pi,pj))
            elif SequenceMatcher(None,ti,tj,autojunk=False).ratio()>=0.99:
                near_pairs.append((pi,pj))
    for a,b in exact_pairs:
        findings.append(flag('EXACT_DUPLICATE_PAGE','warning',f"PDF pages {a} and {b}",
          'Normalized extracted page text is identical after removing the printed global page label.',
          'Compare both pages with the source and determine whether the repeat is intentional.'))
    for a,b in near_pairs:
        findings.append(flag('NEAR_DUPLICATE_PAGE','review',f"PDF pages {a} and {b}",
          'Normalized extracted text similarity is at least 0.99; this is a heuristic, not semantic duplicate detection.',
          'Visually compare the pages and source versions; similar text is not proof of duplication.'))

    elapsed=time.perf_counter()-start
    return {'pdf':Path(pdf_path).name,'sha256':hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest(),
            'pages':len(pages),'opaque_pages':opaque,'findings':findings,
            'processing_seconds':round(elapsed,6),'checker_version':VERSION}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pdf',type=Path)
    ap.add_argument('--inventory',required=True,type=Path)
    ap.add_argument('--versions',required=True,type=Path)
    ap.add_argument('--json-out',type=Path)
    args=ap.parse_args()
    result=check(args.pdf,args.inventory,args.versions)
    encoded=json.dumps(result,indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True,exist_ok=True); args.json_out.write_text(encoded+'\n')
    print(encoded)

if __name__=='__main__': main()
