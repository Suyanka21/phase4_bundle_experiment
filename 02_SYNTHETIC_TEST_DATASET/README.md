# Synthetic Court-Bundle Dataset

Every page is labeled **SIMULATION ONLY — NOT A REAL COURT FILING** and contains no real people, clients, parties, addresses, signatures, facts, bank data, evidence or legal claim. `SIM-CIV-2026-0042`, the names Aster Vale and Brindle Quay, the dates, document descriptions, exhibit labels and all page text are fabricated. The dataset is not drafted to represent a real filing or court-approved format.

## Baseline

`pdfs/T01_clean_baseline.pdf` is a 46-page A4 PDF: one simulated cover, one structured synthetic index and 44 pages across eight simulated documents (pleading, affidavit, three annexures, response and correspondence). Each document has stable ID, local page/total, version and, where applicable, exhibit-label markers. The supplied `metadata/expected_inventory.json` and `.csv` list the eight expected documents, page totals and labels; `metadata/version_register.json` and `.csv` provide expected versions. The index provides expected physical start pages.

## Required independent variants

`metadata/test_manifest.csv` lists the 12 primary cases T01–T12; C01–C02 are two additional clean controls. Defect labels are not included as checker arguments. `generate_dataset.py` deterministically produces the PDFs, reference data, hashes and separate ground truth under the sibling `ground_truth_private/` folder, outside the checker input directory.

T05 is a near-duplicate of a DOC-03 page with a slight wording change, smaller body type and small horizontal/line-spacing change. T10 is a low-resolution synthetic raster page with no embedded searchable text; the checker can detect only the absence of a usable text layer, not visual unreadability.

## Post-implementation challenge variants

After the checker was implemented, `generate_unseen.py` produced U01 (a duplicate within DOC-07, a different document from T04) and U02 (an index shift on DOC-08, a different index entry from T07). `metadata/unseen_manifest.csv` exposes only case ID, file path and supplied references; the injected labels are held separately in `ground_truth_private/unseen_ground_truth.json`. These challenge cases vary the location/document, not the broad defect family, so they are a modest anti-overfitting check, not broad external validation.

## Ground-truth handling

During final detection runs, `repeat_validation.sh` temporarily moved the two delivered ground-truth files from this directory and any generator-side labels to a temporary directory outside the experiment tree. The runner received only each PDF, expected inventory and version register; its code does not open or pass ground-truth files. The script restored the labels on exit. The two JSON ground-truth files in this folder are included only for post-run evaluation and inspection; they are not checker inputs.

## Rebuild

On Python 3.12.3 with ReportLab 5.1.0 and Pillow 13.0.0:

```bash
python3 generate_dataset.py
python3 generate_unseen.py
```

The first command rebuilds primary PDFs and metadata; the second creates the two challenge PDFs. Both generation scripts write ground-truth files to the sibling `ground_truth_private/` folder, outside the checker input directory. `metadata/sha256_manifest.json` records primary dataset hashes at generation time; run logs record the hashes of every PDF actually tested. After regenerating, rerun the isolated suite before post-run scoring; update the delivered ground-truth copies only after detection is complete. Do not run generation commands during a test run.
