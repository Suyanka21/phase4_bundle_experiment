#!/usr/bin/env python3
"""Post-run evaluation only: this script reads ground truth after detection is complete."""
from pathlib import Path
import json,csv,statistics
ROOT=Path(__file__).resolve().parent
D=ROOT/'02_SYNTHETIC_TEST_DATASET'; S=ROOT/'04_VERIFICATION_SPIKE'
GT=[]
for p in [D/'ground_truth.json',D/'unseen_ground_truth.json']:
    GT.extend(json.loads(p.read_text())['cases'])
truth={x['case_id']:x for x in GT}
run1=json.loads((S/'results_run01/all_results.json').read_text())
run2=json.loads((S/'results_run02/all_results.json').read_text())
A={x['case_id']:x for x in run1['results']}; B={x['case_id']:x for x in run2['results']}
rows=[]; TP=FP=FN=0
for case,gt in sorted(truth.items()):
    expected=set(gt.get('injected_defects',[]))
    r1=A[case]; r2=B[case]
    observed=set(f['type'] for f in r1.get('findings',[]))
    obs_by_type={t:[f for f in r1.get('findings',[]) if f['type']==t] for t in observed}
    fp=observed-expected; TP+=len(observed&expected); FN+=len(expected-observed); FP+=len(fp)
    base={'case_id':case,'input_pdf':f'02_SYNTHETIC_TEST_DATASET/pdfs/{gt["file"]}','run1_output':f'04_VERIFICATION_SPIKE/results_run01/{case}.json','run2_output':f'04_VERIFICATION_SPIKE/results_run02/{case}.json'}
    if not expected:
        rows.append({**base,'defect_category':'CLEAN_CONTROL','expected_outcome':'NO_FLAG','observed_outcome':'FALSE_ALARM' if observed else 'NO_FLAG','ground_truth_location':'No injected defect','observed_evidence':'; '.join(sorted(observed)) or 'No findings','run1_run2_identical':r1['findings']==r2['findings']})
    for typ in sorted(expected):
        fs=obs_by_type.get(typ,[])
        gt_locations=gt.get('locations') or ([gt['location']] if gt.get('location') else [])
        rows.append({**base,'defect_category':typ,'expected_outcome':'FLAG','observed_outcome':'DETECTED' if fs else 'MISSED','ground_truth_location':'; '.join(gt_locations),'observed_evidence':' | '.join(f"{f['location']}: {f['evidence']}" for f in fs) or 'No matching finding','run1_run2_identical':r1['findings']==r2['findings']})
    for typ in sorted(fp):
        fs=obs_by_type[typ]
        rows.append({**base,'defect_category':'UNEXPECTED_'+typ,'expected_outcome':'NO_FLAG_FOR_THIS_CATEGORY','observed_outcome':'FALSE_ALARM','ground_truth_location':'No such injected defect in this case','observed_evidence':' | '.join(f"{f['location']}: {f['evidence']}" for f in fs),'run1_run2_identical':r1['findings']==r2['findings']})
cols=['case_id','input_pdf','defect_category','expected_outcome','observed_outcome','ground_truth_location','observed_evidence','run1_output','run2_output','run1_run2_identical']
outcsv=ROOT/'06_EVALUATION_MATRIX.csv'
with outcsv.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
positive=TP+FN
precision=TP/(TP+FP) if TP+FP else None
recall=TP/positive if positive else None
clean_cases=[c for c,g in truth.items() if not g.get('injected_defects')]
clean_flags=sum(len(A[c].get('findings',[])) for c in clean_cases)
all_times=[x['processing_seconds'] for x in run2['results']]
all_wall=[x['wall_seconds'] for x in run2['results']]
summary={
 'cases_evaluated':len(truth),'defect_level_true_positives':TP,'defect_level_false_positives':FP,'defect_level_false_negatives':FN,
 'precision':precision,'recall':recall,'clean_cases':len(clean_cases),'clean_case_false_alarms':clean_flags,
 'mean_checker_processing_seconds_run2':statistics.mean(all_times),'median_checker_processing_seconds_run2':statistics.median(all_times),
 'min_checker_processing_seconds_run2':min(all_times),'max_checker_processing_seconds_run2':max(all_times),
 'mean_end_to_end_wall_seconds_run2':statistics.mean(all_wall),'median_end_to_end_wall_seconds_run2':statistics.median(all_wall),
 'two_run_hashes_and_findings_identical':json.loads((S/'results/reproducibility_comparison.json').read_text())['all_pdf_hashes_same'] and json.loads((S/'results/reproducibility_comparison.json').read_text())['all_findings_identical'],
 'ground_truth_read_during_detection':False,'scope_note':'Metrics only on 13 injected defect instances and four clean synthetic cases across 16 fictional PDFs. The two post-implementation variants are narrow challenge cases. These are not estimates for real Kenyan bundles.'
}
(ROOT/'evaluation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2)); print('matrix',outcsv)
