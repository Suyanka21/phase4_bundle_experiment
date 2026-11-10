#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPIKE="$ROOT/04_VERIFICATION_SPIKE"
DATA="$ROOT/02_SYNTHETIC_TEST_DATASET"
GT_HOLD="$(mktemp -d "${TMPDIR:-/tmp}/phase4-gt.XXXXXX")"
restore_ground_truth() {
  for f in ground_truth.json unseen_ground_truth.json; do
    if [ -f "$GT_HOLD/$f" ]; then mv "$GT_HOLD/$f" "$DATA/$f"; fi
  done
  if [ -d "$GT_HOLD/ground_truth_private" ]; then mv "$GT_HOLD/ground_truth_private" "$ROOT/ground_truth_private"; fi
  rmdir "$GT_HOLD" 2>/dev/null || true
}
trap restore_ground_truth EXIT
for f in ground_truth.json unseen_ground_truth.json; do
  if [ -f "$DATA/$f" ]; then mv "$DATA/$f" "$GT_HOLD/$f"; fi
done
if [ -d "$ROOT/ground_truth_private" ]; then mv "$ROOT/ground_truth_private" "$GT_HOLD/ground_truth_private"; fi
rm -rf "$SPIKE/results" "$SPIKE/results_run01" "$SPIKE/results_run02"
mkdir -p "$SPIKE/results"
python3 "$SPIKE/run_all.py"
cp -a "$SPIKE/results" "$SPIKE/results_run01"
rm -rf "$SPIKE/results"
mkdir -p "$SPIKE/results"
python3 "$SPIKE/run_all.py"
cp -a "$SPIKE/results" "$SPIKE/results_run02"
SPIKE_ROOT="$SPIKE" python3 - <<'PY'
from pathlib import Path
import json,os
root=Path(os.environ['SPIKE_ROOT'])
a=json.loads((root/'results_run01/all_results.json').read_text())
b=json.loads((root/'results_run02/all_results.json').read_text())
A={x['case_id']:x for x in a['results']}; B={x['case_id']:x for x in b['results']}
rows=[]
for case in sorted(set(A)|set(B)):
 x=A.get(case,{}); y=B.get(case,{})
 fx=sorted((z['type'],z['location'],z['evidence']) for z in x.get('findings',[]))
 fy=sorted((z['type'],z['location'],z['evidence']) for z in y.get('findings',[]))
 rows.append({'case_id':case,'present_in_both':case in A and case in B,'pdf_sha256_same':x.get('sha256')==y.get('sha256'),'findings_identical':fx==fy})
out={'run_count':2,'case_count':len(rows),'all_pdf_hashes_same':all(r['pdf_sha256_same'] for r in rows),'all_findings_identical':all(r['findings_identical'] and r['present_in_both'] for r in rows),'cases':rows}
(root/'results'/'reproducibility_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
PY
