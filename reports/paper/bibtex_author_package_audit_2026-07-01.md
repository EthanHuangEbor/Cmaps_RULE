# Paper 1 BibTeX, Author, and arXiv Source Package Audit

Date: 2026-07-01

## Executive verdict

Mechanical source-package readiness is good: the clean upload directory and `arxiv_upload.zip` contain the current `main.tex`, `references.bib`, `main.bbl`, the five referenced `figure_09` through `figure_13` PDFs, and `source_manifest.txt`. The zip entries match the clean upload directory, and no raw data, checkpoint, joblib, CSV, spreadsheet, reviewer-response, or LaTeX build-intermediate files were found in the zip.

Submission readiness still requires human decisions. The remaining blockers are not file-assembly blockers; they are author/affiliation confirmation, manual BibTeX metadata verification, arXiv category/license choice, arXiv web metadata entry, and final PDF visual review.

Main local risks:

- `references.bib` has 19 entries, but `main.tex` cites 13 keys. There are no missing BibTeX keys for cited references, but 6 BibTeX entries are currently uncited.
- The author line is not an obvious placeholder, but it is minimal: `Ethan Huang\\Beihang University`. The submitter should confirm the exact public author name, official affiliation wording, and author order.
- The TeX abstract is locally about 1847 characters after whitespace normalization, under arXiv's documented 1920-character metadata limit, but the web form abstract should still be pasted as clean ASCII/plain text and checked manually.

## BibTeX audit

### Counts and key matching

- `references.bib` entries: 19.
- Unique citation keys used in `reports/paper/main.tex`: 13.
- `reports/paper/arxiv_upload/main.bbl` bibitems: 13.
- Cited keys missing from `references.bib`: none.
- Uncited keys present in `references.bib`: `Breiman2001`, `Chung2014`, `Friedman2001`, `Goel2026`, `Hochreiter1997`, `Hoerl1970`.

Interpretation: this is not a compilation blocker because the packaged `main.bbl` contains only the 13 cited entries. It is a bibliography-hygiene risk. The uncited entries mostly look like algorithm/model citations that may have been intended for Ridge, Random Forest, Gradient Boosting, LSTM/GRU, or a recent arXiv comparator. Before public submission, decide whether to cite them in the Methods/Related Work text or remove them from `references.bib`.

### Local metadata completeness

Local field checks found no obvious missing core fields for the current BibTeX entries:

- All entries have `author`, `title`, and `year`.
- Article entries have `journal`.
- Conference/incollection entries have `booktitle`; the incollection entry also has `publisher`.
- Most published paper entries have DOI fields.
- `NASA_PCoE` has `year = {n.d.}` and a URL via `howpublished`, plus an access note. This is acceptable for a web repository citation but should be manually checked for current URL and access date before submission.
- `Chung2014` has arXiv eprint metadata (`eprint = {1412.3555}`, `archivePrefix = {arXiv}`, `primaryClass = {cs.NE}`) but no DOI or URL. This is locally plausible for a workshop/arXiv-style entry and is currently uncited.
- `Goel2026` has arXiv eprint metadata and an arXiv URL, but is currently uncited.

No internet DOI verification was performed for the BibTeX entries. The remaining checklist item "Verify all BibTeX metadata manually before public submission" should stay unchecked until a human verifies titles, author spellings, venues, years, pages/article numbers, DOI strings, arXiv IDs, and the NASA repository URL.

## Author/affiliation audit

`reports/paper/main.tex` and `reports/paper/arxiv_upload/main.tex` both contain:

```tex
\author{Ethan Huang\\Beihang University}
```

This is not an obvious placeholder such as "Author Name" or "Institution". However, it still needs human confirmation because:

- The affiliation is very minimal. Confirm whether the public manuscript should use only `Beihang University` or a fuller official affiliation such as school/department, university, city, and country.
- Confirm the author order. The manuscript is currently single-author, and `Author Contributions` also states that Ethan Huang designed the study, ran/interpreted experiments, maintained the repository, and prepared the manuscript.
- Confirm whether email, ORCID, or a corresponding-author marker should be added to the PDF source. arXiv web metadata does not require these in the TeX author line, but target journals or personal preference may.
- arXiv metadata author format should be checked manually. arXiv's metadata guidance requires complete and accurate author information, and affiliation claims should be current in the conventional sense.

Checklist recommendation: keep "Confirm author affiliation and author order" unchecked until Ethan confirms the exact public name, affiliation wording, and whether there are any coauthors.

## arXiv package audit

### Clean upload directory

`reports/paper/arxiv_upload` contains exactly these 9 files:

- `main.tex`
- `references.bib`
- `main.bbl`
- `source_manifest.txt`
- `figures/figure_09_metric_rank_heatmap.pdf`
- `figures/figure_10_rmse_vs_critical_rmse50.pdf`
- `figures/figure_11_rmse_vs_overestimation_magnitude.pdf`
- `figures/figure_12_ablation_rmse_vs_overestimation.pdf`
- `figures/figure_13_sarbi_weight_sensitivity.pdf`

The `main.tex` in the upload directory has the same SHA256 hash as `reports/paper/main.tex`. The `references.bib` in the upload directory has the same SHA256 hash as `reports/paper/references.bib`.

### Zip package

`reports/paper/arxiv_upload.zip` contains exactly these 9 entries:

- `figures/figure_09_metric_rank_heatmap.pdf`
- `figures/figure_10_rmse_vs_critical_rmse50.pdf`
- `figures/figure_11_rmse_vs_overestimation_magnitude.pdf`
- `figures/figure_12_ablation_rmse_vs_overestimation.pdf`
- `figures/figure_13_sarbi_weight_sensitivity.pdf`
- `main.bbl`
- `main.tex`
- `references.bib`
- `source_manifest.txt`

The zip entries match the clean upload directory. The zip has 9 entries and no matches for excluded/disallowed patterns checked locally: raw data, checkpoints, ckpt, joblib, LaTeX intermediates, reviewer/response files, CSV/XLSX tables, or model pickle/torch files.

### Figures and manifest

`main.tex` references exactly the five packaged figures:

- `figure_09_metric_rank_heatmap.pdf`
- `figure_10_rmse_vs_critical_rmse50.pdf`
- `figure_11_rmse_vs_overestimation_magnitude.pdf`
- `figure_12_ablation_rmse_vs_overestimation.pdf`
- `figure_13_sarbi_weight_sensitivity.pdf`

`source_manifest.txt` lists `main.tex`, `references.bib`, `main.bbl`, and all five figure PDFs as included files. It also states that raw NASA C-MAPSS data, model checkpoints/joblib files, local LaTeX build intermediates, reviewer reports, response drafts, and large experiment tables are excluded by design. It reports "Missing referenced figures: None" and "Skipped files: None".

Minor manifest polish note: `source_manifest.txt` is physically present in both the upload directory and zip, but the manifest's own "Included files" bullet list does not list `source_manifest.txt` itself. This is not a package blocker, only a self-documentation inconsistency.

Checklist recommendation: the package-related checked items can remain checked:

- Clean source directory exists.
- Upload zip exists.
- Source package includes `main.tex`, `references.bib`, `source_manifest.txt`, and referenced figure PDFs.
- Source package excludes raw data, checkpoints, joblib files, build intermediates, reviewer reports, response drafts, and large experiment tables.
- Zip contents match the clean upload directory and contain only the current FD001-FD004 figure set.
- `main.bbl` is included.
- Source package contents have been refreshed from the current manuscript and figures.

## Remaining human decisions

### arXiv category

Recommended primary category: `cs.LG`.

Rationale: the manuscript is framed as a machine-learning benchmark/evaluation paper for RUL prediction, and arXiv's taxonomy states that `cs.LG` covers machine-learning methodology and applications of machine-learning methods.

Possible cross-list: `eess.SY` if the submitter wants stronger systems/control/aerospace positioning. arXiv's taxonomy describes `eess.SY`/`cs.SY` as systems and control, including aerospace control systems and related modeling/simulation/optimization. For the current manuscript, this looks more like a cross-list candidate than the cleanest primary category.

Lower-priority candidate: `cs.AI`. arXiv's taxonomy says `cs.AI` excludes Machine Learning because ML has a separate subject area, so `cs.AI` is less aligned than `cs.LG` for this draft.

Human decision: choose primary `cs.LG` unless the intended audience is explicitly systems/control; consider `eess.SY` as a cross-list if the submission interface and endorsement state allow it.

### arXiv license

Human decision required. arXiv says the selected license is irrevocable and cannot be changed for that version. The submitter should check funder and target-journal policies before choosing.

Practical options:

- `CC BY 4.0`: best for open reuse with attribution and commonly compatible with open-access expectations, if no target journal/funder conflict.
- `CC BY-NC-ND 4.0`: more restrictive for reuse and derivatives; sometimes preferred when journal compatibility or conservative manuscript reuse is a concern.
- `arXiv.org perpetual, non-exclusive license`: conservative default if the submitter wants arXiv distribution without granting broad Creative Commons reuse.
- Avoid `CC0` unless intentionally dedicating the paper to the public domain; arXiv notes this can conflict with many publishers' copyright-transfer expectations.

Checklist recommendation: keep "Choose arXiv license" unchecked until Ethan makes this choice.

### arXiv comments and web metadata

Suggested comments template:

```text
[final PDF page count] pages, 5 figures. Code: https://github.com/EthanHuangEbor/Cmaps_RULE
```

Use the final arXiv-generated PDF page count, not an estimated local count. The current TeX source contains 5 `\includegraphics` commands and 5 table environments.

The TeX abstract is locally about 1847 characters after whitespace normalization, under arXiv's documented 1920-character limit. Still, the web-form abstract should be manually pasted and checked as plain metadata text:

- remove the literal "Abstract" label if copied from the PDF;
- avoid unsupported Unicode punctuation;
- avoid opaque TeX macros where plain text is clearer;
- confirm that title, authors, abstract, comments, category, and code URL match the final PDF.

Checklist recommendation: keep "Fill arXiv web metadata, abstract, comments, and code URL" unchecked until the web form is filled and previewed.

### Final visual skim

Keep "Do one final human visual skim of the regenerated PDF before uploading" unchecked. arXiv itself requires the submitter to view and verify the generated PDF during submission; this local audit did not visually inspect the arXiv-generated PDF.

### Checklist items to auto-check vs keep human

Can remain checked based on this audit:

- Current source package includes `figure_09` through `figure_13`.
- Clean source directory exists.
- Upload zip exists.
- Package includes manuscript, bibliography, `main.bbl`, manifest, and referenced figures.
- Package excludes raw data/checkpoints/joblib/build intermediates/reviewer-response material/large tables.
- Zip contents match clean upload directory.
- `main.bbl` is included.

Must remain human:

- Verify all BibTeX metadata manually before public submission.
- Confirm author affiliation and author order.
- Choose arXiv category.
- Choose arXiv license.
- Fill arXiv web metadata, abstract, comments, and code URL.
- Final human visual skim of regenerated PDF.

## Evidence commands

Local commands run from `D:\Beihang\Cmaps_RULE`:

```powershell
Get-Content -Raw -LiteralPath 'reports\paper\main.tex'
Get-Content -Raw -LiteralPath 'reports\paper\references.bib'
Get-Content -Raw -LiteralPath 'reports\paper\arxiv_readiness_checklist.md'
Get-Content -Raw -LiteralPath 'reports\paper\arxiv_upload\source_manifest.txt'
Get-Content -Raw -LiteralPath 'reports\paper\arxiv_upload\main.tex'
Get-Content -Raw -LiteralPath 'reports\paper\arxiv_upload\main.bbl'
Get-ChildItem -Recurse -File -LiteralPath 'reports\paper\arxiv_upload' | Sort-Object FullName | Select-Object FullName,Length
Get-FileHash -Algorithm SHA256 -LiteralPath 'reports\paper\main.tex','reports\paper\arxiv_upload\main.tex','reports\paper\references.bib','reports\paper\arxiv_upload\references.bib','reports\paper\arxiv_upload.zip' | Select-Object Path,Hash
tar -tf 'reports\paper\arxiv_upload.zip'
```

Citation-key and BibTeX-field checks were performed with PowerShell regex over `main.tex`, `references.bib`, and `arxiv_upload/main.bbl`.

Zip cleanliness checks:

```powershell
$patterns = 'raw|checkpoint|ckpt|joblib|\.aux$|\.log$|\.out$|\.toc$|\.fls$|\.fdb_latexmk$|review|response|\.csv$|\.xlsx$|\.pt$|\.pth$|\.pkl$'
$entries = tar -tf 'reports\paper\arxiv_upload.zip'
$bad = $entries | Where-Object { $_ -match $patterns }
[pscustomobject]@{ZipEntryCount=$entries.Count; DisallowedPatternHits=($bad -join ', ')}
```

Result: `ZipEntryCount = 9`; `DisallowedPatternHits` empty.

Directory-vs-zip comparison:

```powershell
$dir = Get-ChildItem -Recurse -File -LiteralPath 'reports\paper\arxiv_upload' | ForEach-Object { (Resolve-Path -Relative $_.FullName).Replace('.\reports\paper\arxiv_upload\','').Replace('\','/') } | Sort-Object
$zip = tar -tf 'reports\paper\arxiv_upload.zip' | Sort-Object
Compare-Object -ReferenceObject $dir -DifferenceObject $zip
```

Result: `MATCH`.

External arXiv references consulted for category/license/metadata guidance:

- https://arxiv.org/category_taxonomy
- https://info.arxiv.org/help/license/index.html
- https://info.arxiv.org/help/prep.html
- https://info.arxiv.org/help/submit_tex.html
