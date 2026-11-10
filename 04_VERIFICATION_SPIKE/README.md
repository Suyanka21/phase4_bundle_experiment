# Experimental PDF Administrative Checker — 0.1.0

A deterministic, local-only spike for comparing extracted synthetic PDF text with a supplied expected-document inventory and version register. It is not an MVP or legal tool. It does not use ground-truth labels, OCR, AI, remote services, network calls, or legal judgment. It does not decide authenticity, admissibility, relevance, legal completeness, rule compliance or filing readiness.

## Environment and dependency

Executed on Python 3.12.3, Linux x86_64, with `pypdf==6.21.3`. The PDF generator uses ReportLab 5.1.0 and Pillow 13.0.0; those dependencies are recorded with the dataset-generation files. Checker install:

```bash
python3 -m pip install -r requirements.txt
```

## Single-file check

```bash
python3 check_bundle.py \
  ../02_SYNTHETIC_TEST_DATASET/pdfs/T01_clean_baseline.pdf \
  --inventory ../02_SYNTHETIC_TEST_DATASET/metadata/expected_inventory.json \
  --versions ../02_SYNTHETIC_TEST_DATASET/metadata/version_register.json \
  --json-out results/T01.json
```

## Suite runs

`run_all.py` uses the public test manifest and the separate post-implementation `unseen_manifest.csv`; it runs the same generic checker on all listed PDFs and writes JSON/CSV output. It never opens a ground-truth file. To run twice and preserve both full outputs plus a comparison of file hashes and flags:

```bash
./repeat_validation.sh
```

The script clears its prior result archives before running, temporarily moves the delivered ground-truth files and any generator-side labels outside the experiment tree, then restores them on exit. It is reproducible but not intended as a production pipeline.

## Checks implemented

- Missing expected document identifier: compare pages found in the PDF with the supplied inventory.
- Missing document-local page numbers: detect gaps in `DOCUMENT_PAGE: n/total` labels, unless at least one page lacks readable embedded text.
- Exact repeated pages and text near-duplicates: normalize extracted text, remove the printed global page number, compare pairs; near-match threshold is SequenceMatcher ratio ≥ 0.99.
- Printed global page label against physical PDF position.
- Index start page against first physical occurrence of the document identifier.
- Document version and exhibit label against the supplied JSON inventory/register.
- Pages with fewer than 20 non-whitespace extracted characters: warning that no usable text layer was read, **not** a claim that the page is visually illegible.

All checks rely on stable synthetic markers such as `DOCUMENT_ID`, `DOCUMENT_PAGE`, `DOCUMENT_VERSION`, `EXHIBIT_LABEL`, `BUNDLE_PAGE` and `INDEX_ENTRY`. They are fixtures, not a parser for uncontrolled Kenyan pleadings.

## Important limitations

A warning’s truth is limited to the supplied text and reference data. Missing-document and version results depend directly on accurate, complete expected inventory/version register inputs. OCR is not run, so image quality, legibility and image-only contents are not inspected. The checker's low-text warning is only a proxy for human review. SequenceMatcher can raise false duplicate alarms on repetitive real documents and cannot assess semantic equivalence. Index extraction depends on the synthetic index marker. Continuous numbering assumptions can be wrong for legitimate front matter, non-continuous sections, separate volumes or court-specific instructions. Page rotation/orientation is not interpreted. The synthetic case carries no court-approved filing format. See `../05_VERIFICATION_RESULTS.md` for the measured result and held-out challenge cases.
