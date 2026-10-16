# Code, Git and dataset audit

The workspace already contains substantial usable data. The immediate India work is chiefly estimator implementation and source-method interpretation, rather than asking the author to supply the same processed household files again. Neither official reproduction is accepted by this audit.

## What was checked

Seven local Git databases, thirty stored refs, relevant reachable/deleted object paths, eight bundle indexes, ignored/untracked dataset filenames and archive central directories. Repository commit counts total120 before deduplication across shared histories. This is a local-history audit, not a fresh remote/GitHub verification or a claim that every historical blob was manually read. The private audit package preserves exact paths, source/code hashes, schemas, source passages and inspection receipts. No third-party code, old model or recovery bundle was executed or imported.

## Findings

1. **HCES unit data are present.** The supplied checkout has fifteen cleaned Parquet levels, dictionaries and import code. Household, person, food, visit, weight and design fields are available. Its omitted original text-file lineage and redistribution licence remain unverified; that is different from having no household dataset. The earlier request for original files must not block development and diagnostics using this explicitly identified candidate.

2. **The target is unadjusted protein.** Original Report594 Table3.18R/U, printed51/PDF70, explicitly separates unadjusted61.8/63.4 from adjusted61.2/62.9 g/person/day. Table3.8 reports the brief's unadjusted values. An older deleted narrative already recorded that distinction. Section2.9.8.1's meal correction is valid for a separate adjusted series, not an extra prerequisite for the unadjusted target. The code now parses the source comparison columns and rejects a swapped definition.

3. **The grain coefficients are already supplied and used.** Official Table2.2 specifies parent070/001/002 coefficients. The current physical join counts coefficient-bearing parents once and omits unmapped child rows. The quantity reconciliation verifies a hierarchy; it does not require new child-specific nutrient factors to reproduce the official composite. A regression test protects against double-counting a parent and its breakdown. This does not establish that a composite coefficient precisely measures every individual grain variety.

4. **The CPI issue was overstated.** Section2.10.1 specifies December2024 prices, the survey-period average and separate rural/urban indices. It does not expressly require the item-by-item crosswalk previously described as missing. Exact series/base/normalization still need identification and validation. All36 monetary-factor rows exist; their contribution is not implemented in the physical-only diagnostic. Existing Pakistan CPI extracts are not substitutes for India indices. No index was selected to tune the answer to a target.

5. **Pakistan data and prior checks are reusable.** The earlier Dashboard raw ZIP and current research ZIP have identical bytes. Existing code checks positive weights, household/roster/PSU joins, source codes, acquisition channels, recall conventions and report/workbook disagreements. The official coding workbook supplies administrative code mappings. Mapping a PSU to an administrative area, establishing its final survey stratum and implementing variance are separate tasks. The earlier profile narrows these tasks; it is not a complete baseline. Older complete Pakistan totals used pooled imputation and were withdrawn in Dashboard commit302f383; they must not be reinstated as official reproduction.

6. **HOLD is currently fixed diagnostic behavior.** The India/Pakistan scripts set HOLD/false, and the rebuild returns exit2 after successful integrity checks. They are incomplete diagnostics, with no implemented passing estimator/gate path. Their green tests show that the bounded software checks work. They do not show that a complete estimator attempted and failed all required calculations. The executable outputs now make that distinction explicit. No boolean was flipped to manufacture success.

7. **Two separate inputs were not recovered.** The scoped search found NFHS reports/tables/metadata but no NFHS respondent files. It also found no completed author policy-coding submission. The twenty frozen agent labels and older news-annotation agreement files are different evidence and cannot become the author's twenty independent policy responses. US outputs remain deferred at the author's request; Q3 acceptance remains recorded for its existing fixed passages.

## Meal-input usability

Meal fields exist in the H roster and F household file. Filtering the person file to questionnaire F would remove its rows. Null/negative counts, household-size differences and zero/missing home-meal denominators require source-defined handling; fields being present does not establish a valid adjusted estimator. This is technical work for the separate adjusted series, not a request that the author do statistical coding.

## Pakistan administrative mapping

The fresh crosswalk maps all2,153 analytic PSUs without unmatched or ambiguous administrative keys. Sixteen PSUs covering212 households have ICT geography in the official workbook while the analytical file codes them as province2/Punjab. They are not unused weight records. Preserve both classifications, do not silently drop or relabel households, and retain the applicability question for ICT because the captured index's stratification wording explicitly names the four provinces. A complete administrative match narrows the design task; it does not by itself certify every final variance stratum.

## Repairs and next execution

Current code/requirements/access notes now distinguish available inputs, ambiguous methodology, unfinished estimators and genuinely unrecovered files. The unadjusted target is source-bound; parent factors and the narrower CPI issue are explicit. Source preimages and prior output/claim bindings were preserved before rebuilding.

The next estimator work is to implement and validate the monetary component under a justified sector CPI recipe, use the available design evidence without confusing administrative groups with strata, and compare the complete unadjusted output with the brief. Pakistan's all-channel source conflict must be resolved without dropping channels to force a match. Only a complete estimator with genuine passing/failing acceptance tests can replace the diagnostic gate. The brief's stop on downstream estimation remains in force.

```text
MODERATOR REVIEW
Scope: local audit and explanatory metadata repairs
[BLOCK] None for the bounded audit/metadata repair.
[WARN] Complete estimators, official lineage/design checks and the Pakistan
       source disagreement remain unresolved; no empirical acceptance.
[WARN] NFHS respondent files and actual author policy responses were not
       recovered within the recorded search scope.
[NIT] Keep person-row counts distinct from household counts.
Verdict: PASS for bounded repairs, subject to saved verification receipts.

RETROSPECTIVE
Worked: original table headings, local data and Git history corrected the scope.
Didn't: earlier explanations conflated absent inputs with unfinished code;
        an initial meal-method interpretation overlooked the target heading.
Rule: bind each target to its source heading and inventory existing inputs
      before requesting more files or treating a fixed status as test evidence.
```

No new intake/market/elasticity estimate or projection was computed. No raw data was deleted, no memory/rule file amended, and no push or publication authorised.
