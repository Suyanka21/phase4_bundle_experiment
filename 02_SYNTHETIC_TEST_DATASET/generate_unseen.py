#!/usr/bin/env python3
"""Generate additional challenge variants after checker implementation, without using hidden labels in detection."""
from pathlib import Path
import importlib.util, csv, json, hashlib
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dataset_generator',root/'generate_dataset.py')
g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
out=root/'pdfs'
g.make_bundle(out/'U01_unseen_duplicate_other_document.pdf',duplicate_page=('DOC-07',2))
g.make_bundle(out/'U02_unseen_index_shift_other_document.pdf',index_error=('DOC-08',1))
with (root/'metadata'/'unseen_manifest.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['case_id','pdf','checker_inputs'])
 w.writerow(['U01','pdfs/U01_unseen_duplicate_other_document.pdf','metadata/expected_inventory.json; metadata/version_register.json'])
 w.writerow(['U02','pdfs/U02_unseen_index_shift_other_document.pdf','metadata/expected_inventory.json; metadata/version_register.json'])
# This private file is for evaluation only; do not copy it to the checker or runner input paths.
private=root.parent/'ground_truth_private'
private.mkdir(exist_ok=True)
truth={'notice':'POST-IMPLEMENTATION CHALLENGE GROUND TRUTH — open only after checker runs complete','cases':[
 {'case_id':'U01','file':'U01_unseen_duplicate_other_document.pdf','injected_defects':['EXACT_DUPLICATE_PAGE'],'location':'DOC-07 local page 2 duplicated'},
 {'case_id':'U02','file':'U02_unseen_index_shift_other_document.pdf','injected_defects':['INDEX_START_PAGE_MISMATCH'],'location':'DOC-08 index start page increased by 1'}
]}
(private/'unseen_ground_truth.json').write_text(json.dumps(truth,indent=2)+'\n')
print(json.dumps({'unseen_cases':2,'labels_not_in_unseen_manifest':True,'manifest':str(root/'metadata'/'unseen_manifest.csv'),'ground_truth_private':str(private/'unseen_ground_truth.json')},indent=2))
