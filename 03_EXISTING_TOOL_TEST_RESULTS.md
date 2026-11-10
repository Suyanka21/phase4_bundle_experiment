# 03 — Existing-Tool Test Results

**Scope and method.** This is an execution log, not a feature comparison based on marketing. The fictional PDFs in `02_SYNTHETIC_TEST_DATASET/pdfs/` were offered only to KortiBundle’s publicly visible upload control, because that was the only unauthenticated, stateful bundle interface reached. The authorized browser tool could not target the hidden file input; no PDF was accepted. No test was performed inside Acrobat, Word/SharePoint, Bundledocs, TrialView or Tricostar. The public product pages and documentation were reviewed separately in `01_COMPETITOR_ACCESS_AUDIT.md`. A document displayed to a human is not recorded as automatic detection.

## Per-test record

Status definitions: **BLOCKED** = a documented upload attempt did not reach product processing; **NOT TESTED** = no product accepted the input or ran the check; **DOCUMENTATION-ONLY** = public feature claims were reviewed but not executed. `Not measured` means no basis to count either detection or false alarm.

| Case | Synthetic input / check | KortiBundle input accepted? / result | Acrobat result | Word / SharePoint result | Bundledocs result | TrialView result | Tricostar result |
|---|---|---|---|---|---|---|---|
| T01 | Clean 46-page synthetic baseline | **No — BLOCKED** before file acceptance; no detection result | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T02 | Expected annexure DOC-03 absent | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T03 | Internal page sequence gap in DOC-03 | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T04 | Exact duplicate page | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T05 | Near-duplicate page with slight text/typographic change | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T06 | Printed continuous bundle-page mismatch | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T07 | Index start-page reference mismatch | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T08 | Document version differs from supplied register | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T09 | Exhibit label differs from supplied inventory | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T10 | Low-quality raster page with no usable embedded text layer | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T11 | Missing expected DOC-03 plus pagination mismatch | No — BLOCKED; no warnings observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| T12 | Clean unusual landscape page | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| C01 | Clean text variation control | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| C02 | Clean re-ordered document control with matching index | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| U01 | Post-implementation challenge: repeated page in DOC-07 | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| U02 | Post-implementation challenge: DOC-08 index start shifted | No — BLOCKED; no warning observed | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

For all rows, existing-tool **automatic detection: not established; manual discovery: not tested; actionable warning: none observed because no product processed a document; false alarm: not measurable**. “None observed” is not a zero-false-alarm claim.

## Reproducible access evidence

On 10 November 2026, the public KortiBundle page rendered and exposed its interface. The DOM showed one enabled multiple-PDF input and a disabled “Compile & Open Interactive Inspector” control before upload. The browser upload tool was tried three times with the clean synthetic baseline: for index 10 it reported that the node was not a file input; at indices 0 and 87 it reported that it could not locate the file input. Clicking the visible upload-area label did not produce an accepted file. No file transfer, server-side processing or product output was observed. Screenshot: `evidence/kortibundle_public_interface_2026-11-10.webp`; detailed trace and cited pages are in the companion access audit.

The other products were intentionally not enrolled or accessed through accounts. Bundledocs’ publicly advertised 30-day trial routes to account creation; Adobe’s trial link routes to an account/commerce flow; TrialView’s public path is a sales demo; Tricostar’s government listing states no free trial. No misleading identity was created. Public documentation claims (e.g., Adobe PDF comparison/Bates numbering, Bundledocs indexing/pagination, TrialView de-duplication, Tricostar revision history) are **DOCUMENTATION-ONLY**, not a positive or negative test result.

**Reproduction:** exact browser operations, timestamps and page links are in `01_COMPETITOR_ACCESS_AUDIT.md`; the screenshot is preserved under `evidence/`. The local synthetic checker’s results are distinct and reported in `05_VERIFICATION_RESULTS.md`; they must not be attributed to any existing product.
