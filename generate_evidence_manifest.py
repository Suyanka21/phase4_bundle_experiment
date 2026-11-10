#!/usr/bin/env python3
"""Create a result-to-input/output/evidence index for the experiment package."""
from pathlib import Path
import csv
R=Path(__file__).resolve().parent
out=R/'evidence_manifest.csv'
fields=['evidence_id','reported_result','input_or_source','expected_outcome','observed_outcome','run1_output','run2_output','additional_evidence_or_notes']
rows=[]
with (R/'06_EVALUATION_MATRIX.csv').open(newline='') as f:
 for i,x in enumerate(csv.DictReader(f),1):
  rows.append({'evidence_id':f"E{i:02d}",'reported_result':f"{x['case_id']} — {x['defect_category']}",'input_or_source':x['input_pdf'],'expected_outcome':x['expected_outcome'],'observed_outcome':x['observed_outcome'],'run1_output':x['run1_output'],'run2_output':x['run2_output'],'additional_evidence_or_notes':f"Injected location: {x['ground_truth_location']}; observed: {x['observed_evidence']}; see 06_EVALUATION_MATRIX.csv"})
extras=[
 ('KortiBundle interface observed','https://kortibundle.com/','','DOCUMENTATION/OBSERVED UI','evidence/kortibundle_public_interface_2026-11-10.webp; 01_COMPETITOR_ACCESS_AUDIT.md'),
 ('KortiBundle upload blocked before acceptance','https://kortibundle.com/','','BLOCKED; no product result','evidence/kortibundle_upload_attempts.txt; 01_COMPETITOR_ACCESS_AUDIT.md'),
 ('Competitor capability/pricing sources','See direct citations [1]–[15] in 01_COMPETITOR_ACCESS_AUDIT.md','','DOCUMENTATION-ONLY','01_COMPETITOR_ACCESS_AUDIT.md; 03_EXISTING_TOOL_TEST_RESULTS.md'),
 ('Run reproducibility','04_VERIFICATION_SPIKE/repeat_validation.sh','','16 cases; two identical runs','04_VERIFICATION_SPIKE/results/reproducibility_comparison.json; results_run01/all_results.json; results_run02/all_results.json'),
 ('Timing/environment','04_VERIFICATION_SPIKE/results_run02/all_results.json','','Run 2 processing and wall-time fields','evaluation_summary.json; 05_VERIFICATION_RESULTS.md'),
 ('T11 human-review example','02_SYNTHETIC_TEST_DATASET/pdfs/T11_two_independent_defects.pdf','Two injected defects','Two warnings shown','07_SAMPLE_VERIFICATION_REPORT.pdf; 04_VERIFICATION_SPIKE/results/T11.json'),
 ('Checker implementation','04_VERIFICATION_SPIKE/check_bundle.py','','Source and README','04_VERIFICATION_SPIKE/README.md; 04_VERIFICATION_SPIKE/requirements.txt'),
 ('Primary legal-source boundary','[1] and [2] in 05_VERIFICATION_RESULTS.md','','Rules are not encoded as compliance judgments','05_VERIFICATION_RESULTS.md; 08_PHASE_4_EXECUTIVE_VERDICT.md')]
for i,(claim,src,expected,observed,ev) in enumerate(extras,len(rows)+1):
 rows.append({'evidence_id':f'E{i:02d}','reported_result':claim,'input_or_source':src,'expected_outcome':expected,'observed_outcome':observed,'run1_output':'','run2_output':'','additional_evidence_or_notes':ev})
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'{out} rows={len(rows)}')
