# Paper 2 Submission Readiness Checklist

## Generated

- [x] `main.tex`
- [x] `supplement.tex`
- [x] `references.bib`
- [x] Figure PDFs/SVG/PNG/TIFF under `figures/`
- [x] `figure_table_manifest.md`
- [x] `citation_audit.md`
- [x] `paper2_value_trace.csv`
- [x] `build_paper2.ps1`
- [x] `package_paper2_source.ps1`

## To Run After Manual LaTeX Installation

```powershell
cd D:\Beihang\Cmaps_RULE
.\reports\paper2\build_paper2.ps1
.\reports\paper2\package_paper2_source.ps1
```

## Human Checks Before Submission

- [ ] Read `main.tex` for voice and target-journal fit.
- [ ] Confirm all references are acceptable for the selected journal.
- [ ] Confirm figures render correctly in the compiled PDF.
- [ ] Decide whether TIFF previews should be excluded from Git history.
- [ ] If submitting externally, replace the internal acknowledgement sentence.
