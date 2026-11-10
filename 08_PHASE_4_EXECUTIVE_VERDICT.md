# 08 — Phase 4 Executive Verdict

## Verdict B — Technical feasibility demonstrated, differentiation unknown

A small deterministic checker detected all 13 deliberately injected defect instances in 16 fictional PDFs, including two post-implementation challenge cases, and raised no flags on four clean variants. Two full runs produced identical input hashes and finding lists. This demonstrates that marker- and reference-driven administrative checks can be implemented and reproduced on this synthetic corpus.

It does **not** demonstrate technical differentiation over any existing product. KortiBundle’s public interface was reached, but the authorized browser upload control could not target its hidden file input; no product accepted or processed the synthetic PDF. No other product was tested on the documents. Public feature claims overlap with parts of this checker, but are not independent validation. The 100% precision/recall is a description of 13 curated injections and four clean examples only, not an expected real-world score.

## Direct answers

1. **Which defects were detected?** On the synthetic corpus: missing inventory-listed document; missing document-local page number; exact duplicate page; near-duplicate text page; printed bundle-page/physical-position mismatch; index start-page mismatch; version mismatch; exhibit-label mismatch; and a page with no useful embedded text layer. T11’s two defects were both flagged. The two additional unseen-location variants—duplicate in DOC-07 and shifted DOC-08 index—were also detected. The near-duplicate test was a 0.99 text-similarity heuristic.

2. **Which defects were missed?** None of the 13 injected defect instances in this constructed dataset. Unlisted/missing documents cannot be found unless the inventory contains them. The test does not establish performance on arbitrary, image-only, handwritten, semantically altered or genuine records.

3. **How many false alarms occurred?** Zero across four clean synthetic cases (T01, T12, C01, C02). This is a very small, curated control set and not an operational false-alarm rate.

4. **Which results depended on an expected-document inventory?** T02/T11 missing-document checks, T09 exhibit-label comparison, and index/reference checks depend on supplied structured data. DOC-03’s absence was detectable only because the supplied inventory listed it. T08 depends on the supplied version register. If a reference file is incomplete or wrong, the warning may be wrong or a real issue may be missed.

5. **Which results depended on OCR or AI?** None. The checker used pypdf 6.21.3 to extract embedded PDF text and deterministic comparisons. It made no OCR or AI calls and transferred no test data externally. T10 only produced `NO_EXTRACTABLE_TEXT_LAYER`; actual visual readability was not assessed.

6. **Which existing products were actually tested?** Only KortiBundle’s publicly accessible page/interface was exercised. Three synthetic-file upload attempts were blocked by the browser tool before acceptance; therefore no existing product processed a document. Adobe Acrobat, Word/SharePoint, Bundledocs, TrialView and Tricostar were researched from public documentation only. No existing product’s test outcome is claimed.

7. **Did an accessible existing product already perform the same checks?** Public vendor sources describe overlapping bundle assembly, indexing and pagination. TrialView advertises de-duplication; Adobe documents PDF comparison and Bates numbering; SharePoint documents version history; Bundledocs advertises automated indexes and pagination. These claims do not settle whether any product validates a complete expected-document/version register or emits the same warnings. No synthetic test comparison was completed, so the answer is **unknown**.

8. **What technical advantage was demonstrated?** No comparative advantage. The narrow technical result is feasibility: local deterministic checks over supplied IDs, page labels and reference files can produce actionable warnings on labelled synthetic documents. That is not differentiated from existing products, and no real-world benefit, time saving or user need was measured.

9. **What security or operational constraints remain?** The checker itself was local-only, but it is a prototype tied to synthetic text markers and does not have production security controls. KortiBundle’s public privacy notice claims local/ephemeral processing and no training, but this was not independently verified because no file was processed. The upload test was blocked by browser tooling. Other trials require account creation or sales contact; no identity was invented, terms accepted or payment submitted. No real client material was used. The applicable procedural requirements depend on court and filing type; the checker does not encode legal rules or establish compliance. [1] [2]

10. **Is there enough evidence to justify further experimentation?** Enough for a carefully scoped, non-commercial follow-up: resolve authorized upload access, use the same fictional dataset, and compare generated warnings/outputs against those from an actually tested existing product. Before any real data use, independently verify data flow, retention, deletion, access controls and contractual terms. This experiment does not justify building a commercial product or assert customer demand or willingness to pay.

## What happened / what remains unknown

**Executed:** generated the 46-page synthetic baseline; created 10 primary defective cases containing 11 injected defects, four clean cases and two post-implementation challenges; ran the local checker twice across 16 PDFs; compared against withheld ground truth only after both runs; created a defect-level CSV matrix; rendered and inspected a one-page human review example.

**Researched only:** public source claims, help documentation, access pathways and prices for KortiBundle, Adobe, Microsoft, Bundledocs, TrialView and Tricostar. Primary court sources were consulted to avoid treating one generic checker as procedural-compliance software: Court of Appeal requirements and Supreme Court guidance are court-specific. [1] [2]

**Unknown:** whether a tested commercial tool detects the same anomalies on the same inputs; whether KortiBundle actually processes or flags the synthetic cases; real-world accuracy on unstructured documents; whether an inventory/version register can be maintained accurately; security/data-processing facts not independently verified; time saved, buyer demand, adoption or commercial viability.

**Next:** first obtain a properly authorized test route (or an offline export/configuration) for a synthetic-only comparison; then add varied, non-marker PDFs and more clean/defective controls; retain human adjudication of every warning. Keep the test outside actual filings and real case material until the legal professional confirms its appropriateness and data controls.

### References

[1]: https://new.kenyalaw.org/akn/ke/act/ln/2022/40/eng@2022-12-31 "Kenya Law, Court of Appeal Rules 2022, revised version; court-specific record requirements"
[2]: https://supremecourt.judiciary.go.ke/guidelines-for-filing-of-documents/ "Supreme Court of Kenya, Guidelines for filing of documents"
