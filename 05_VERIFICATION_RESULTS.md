# 05 — Verification Spike Results

## Executive result

The deterministic checker issued the expected category flag for **all 13 injected defect instances** across 16 fictional PDFs, including two additional variants generated after checker implementation. It issued no flags on the four clean cases. These are 13 curated synthetic injections and four clean synthetic examples, not estimates of accuracy on real Kenyan court bundles.

| Metric | Observed |
|---|---:|
| Defect-level true positives | 13 |
| Defect-level false positives | 0 |
| Defect-level false negatives | 0 |
| Precision | 100% (13 / 13) |
| Recall | 100% (13 / 13) |
| Clean synthetic cases | 4 |
| False alarms on clean cases | 0 |
| Primary + post-implementation challenge cases | 16 |
| Full suite executions | 2; all PDF hashes and finding lists identical |

“100%” describes only this small, designed test set. It is not a general performance claim. A matching warning on a fabricated marker confirms the checker’s mechanical pathway, not the real-world truth, legal significance or cause of an issue.

## Defect-level outcomes

| Cases | Injected condition | Finding observed | Result |
|---|---|---|---|
| T02 | DOC-03 omitted though listed in the supplied expected inventory | `MISSING_EXPECTED_DOCUMENT` at DOC-03 | Detected; depends on complete/accurate inventory |
| T03 | DOC-03 local page 4 omitted | `DOCUMENT_PAGE_SEQUENCE_GAP`; local sequence omits 4 | Detected from printed page markers |
| T04, U01 | Exact text-identical page repeated | `EXACT_DUPLICATE_PAGE` with PDF page pair | Detected; U01 is the post-implementation challenge at DOC-07 rather than DOC-03 |
| T05 | Near-copy of DOC-03 page with wording, type-size and layout change | `NEAR_DUPLICATE_PAGE`; extracted-text similarity ≥ 0.99 | Detected by heuristic; not semantic matching |
| T06 | Printed bundle page label disagrees with physical PDF position | `BUNDLE_PAGINATION_MISMATCH` | Detected against the checker’s assumed physical sequence |
| T07, U02 | Index start page is wrong | `INDEX_START_PAGE_MISMATCH` | Detected; U02 uses DOC-08 and a different offset from T07 |
| T08 | DOC-02 label is V1 but supplied register says V3 | `VERSION_MISMATCH` | Detected; depends on correct version register and readable version markers |
| T09 | DOC-03 label is Z but supplied inventory says A | `EXHIBIT_LABEL_MISMATCH` | Detected against supplied inventory |
| T10 | Low-resolution raster page contains no useful embedded text | `NO_EXTRACTABLE_TEXT_LAYER` at PDF page 23 | Detected only as a missing/short text layer; visual legibility was **not** assessed |
| T11a | DOC-03 absent from the PDF but present in expected inventory | `MISSING_EXPECTED_DOCUMENT` | Detected |
| T11b | PDF page 12 prints bundle page 13 | `BUNDLE_PAGINATION_MISMATCH` | Detected independently of T11a |

T01 baseline, T12 unusual landscape page, C01 clean text variation and C02 clean reordering produced no flags. These four clean examples yielded zero observed false alarms. C02’s expected index was generated for its reordered source list; it does not test a stale but otherwise valid index.

**Misses:** none of the 13 deliberate defect instances was missed. The test corpus does not establish that the checker will find unmarked defects in arbitrary documents. In particular, the no-text-layer finding does not establish unreadability or OCR accuracy.

## Processing time and reproducibility

Executed on Python 3.12.3 / Linux x86_64 using pypdf 6.21.3. On the final second complete run, per-file checker processing averaged **5.56 seconds**, median **5.77 seconds**, minimum **3.97 seconds**, maximum **6.24 seconds** across 16 PDFs (38–47 pages). End-to-end subprocess wall time averaged **5.91 seconds**, median **6.11 seconds**. Both full runs had matching SHA-256 hashes for all 16 PDF inputs and identical finding lists for all cases; both runs completed with 0 checker process failures. During these final detection runs, known-case and challenge ground-truth files were moved outside the experiment tree, then restored for post-run scoring. Per-case JSON, CSV, commands, hashes, tool versions and timing are in `04_VERIFICATION_SPIKE/results_run01/`, `results_run02/` and `results/reproducibility_comparison.json`.

## What the checker actually depends on

- **Expected-document inventory:** required for T02 and T11 missing-document flags. The checker can say only that a listed identifier was not found in text-extracted pages; it cannot prove that the inventory itself is complete or correct.
- **Version register:** required for T08. The result is only a disagreement between a supplied register and readable in-document version markers.
- **Expected exhibit label:** the supplied inventory is the source of truth for T09. It does not independently identify an exhibit.
- **PDF embedded text:** required for document IDs, local page sequences, index markers, versions, exhibit labels and text-based duplicate checks.
- **No OCR or AI:** no OCR engine or model was called, no external data was transferred, and no human label was passed to the checker.

## Known failure modes and untested areas

The prototype does not reliably evaluate real scanned pages, handwritten documents, rotated or damaged pages, optical legibility, semantic or image-only duplicates, signature/authenticity, the legal identity or operative status of versions, missing unlisted documents, source-record completeness, exhibit evidentiary correspondence, or legal relevance/admissibility. A page can have legible extracted text and still be visually poor; an image can be visibly readable and lack an embedded text layer. The 0.99 similarity rule may over-flag boilerplate or miss meaningful changes. An incorrect inventory/register can produce an incorrect warning or conceal a real issue. Its global-page comparison assumes the supplied synthetic convention that physical PDF page numbers start at 1; it is not a court-specific rule engine.

The Kenyan Judiciary’s published requirements vary by court and filing type. The Court of Appeal Rules address that court’s records, consecutively numbered pages, an index and a 500-page-per-volume limit; Supreme Court guidance separately states that documents be both printed and electronic and consistent. Those sources are cited to show why no generic format should be called legally compliant; this checker does not encode or determine procedural compliance. [1] [2]

## Reproduction and artifacts

See `04_VERIFICATION_SPIKE/README.md` for single-file and suite commands. The post-run evaluation script `evaluate_results.py` reads withheld ground truth **only after both detection runs** and writes the defect-level `06_EVALUATION_MATRIX.csv` and `evaluation_summary.json`. The checker and runner source do not read ground truth. The final repeat script moves the delivered ground-truth files and any generator-side labels outside the experiment tree during detection, restoring them for post-run scoring.

### Primary legal references

[1]: https://new.kenyalaw.org/akn/ke/act/ln/2022/40/eng@2022-12-31 "Kenya Law, Court of Appeal Rules 2022 (revised version), rules 13, 14 and 89"
[2]: https://supremecourt.judiciary.go.ke/guidelines-for-filing-of-documents/ "Supreme Court of Kenya, Guidelines for filing of documents"
