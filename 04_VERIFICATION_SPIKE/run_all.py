#!/usr/bin/env python3
"""Run all listed PDFs; intentionally never opens any ground_truth file."""
from pathlib import Path
import csv, subprocess, json, sys, hashlib, platform, datetime, time
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'02_SYNTHETIC_TEST_DATASET'
OUT=ROOT/'04_VERIFICATION_SPIKE'/'results'
OUT.mkdir(parents=True,exist_ok=True)
checker=Path(__file__).with_name('check_bundle.py')
inv=DATA/'metadata'/'expected_inventory.json'
vers=DATA/'metadata'/'version_register.json'
manifests=[('primary',DATA/'metadata'/'test_manifest.csv'),('unseen',DATA/'metadata'/'unseen_manifest.csv')]
rows=[]; start=datetime.datetime.now(datetime.timezone.utc).isoformat()
for suite,manifest in manifests:
 if not manifest.exists(): continue
 with manifest.open(newline='') as f:
  for row in csv.DictReader(f):
   pdf=DATA/row['pdf']; case=row['case_id']; dest=OUT/f'{case}.json'
   cmd=[sys.executable,str(checker),str(pdf),'--inventory',str(inv),'--versions',str(vers),'--json-out',str(dest)]
   before=time.perf_counter(); proc=subprocess.run(cmd,text=True,capture_output=True); wall=time.perf_counter()-before
   if proc.returncode:
    rows.append({'suite':suite,'case_id':case,'file':pdf.name,'exit_code':proc.returncode,'error':proc.stderr,'wall_seconds':round(wall,6)})
    continue
   result=json.loads(dest.read_text())
   result['suite']=suite; result['case_id']=case; result['wall_seconds']=round(wall,6); result['command']=cmd
   dest.write_text(json.dumps(result,indent=2)+'\n')
   rows.append(result)
summary={'run_started_utc':start,'run_finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'python':platform.python_version(),'platform':platform.platform(),'pypdf':__import__('pypdf').__version__,
 'checker_sha256':hashlib.sha256(checker.read_bytes()).hexdigest(),'inventory_sha256':hashlib.sha256(inv.read_bytes()).hexdigest(),
 'version_register_sha256':hashlib.sha256(vers.read_bytes()).hexdigest(),'ground_truth_read':False,'results':rows}
(OUT/'all_results.json').write_text(json.dumps(summary,indent=2)+'\n')
with (OUT/'detection_results.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['suite','case_id','pdf','pages','finding_types','finding_count','processing_seconds','wall_seconds','exit_code'])
 for r in rows:
  types=';'.join(x['type'] for x in r.get('findings',[]))
  w.writerow([r.get('suite',''),r.get('case_id',''),r.get('pdf',''),r.get('pages',''),types,len(r.get('findings',[])),r.get('processing_seconds',''),r.get('wall_seconds',''),r.get('exit_code',0)])
print(json.dumps({'cases':len(rows),'failures':sum(1 for x in rows if x.get('exit_code',0)),'results':str(OUT/'all_results.json'),'csv':str(OUT/'detection_results.csv'),'ground_truth_read':False},indent=2))
