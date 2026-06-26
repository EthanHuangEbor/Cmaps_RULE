# Reviewer Report: Two-Round Critique and Rebuttal

## Scope

Manuscript reviewed: `reports/review/aero_engine_dl_review.md`

Review target: a paper-level Chinese literature review on deep learning and machine learning for aero-engine health management and RUL prediction, emphasizing C-MAPSS, safety-aware evaluation, transfer generalization, uncertainty, and maintenance decision making.

Reviewers:

- **Reviewer A: PHM/RUL methodology reviewer.** Focus: literature coverage, technical taxonomy, benchmark protocol, experiment plan, and whether the proposed paper cuts are methodologically reasonable.
- **Reviewer B: Aero-engine and safety-decision reviewer.** Focus: whether the review overstates engineering significance, confuses simulation with real engine data, or under-discusses maintenance decision and safety risk.

## Round 1 Critique

### Reviewer A: PHM/RUL Methodology

**Decision: Major revision before using as a thesis/paper foundation.**

Strengths:

1. The review correctly distinguishes direct C-MAPSS baselines from direction-supporting work.
2. The six requested technical lines are all present: traditional ML, LSTM/GRU/CNN, attention/Transformer/TCN/GNN, transfer/domain adaptation, uncertainty/risk-aware RUL, and decision-oriented evaluation.
3. The current project is positioned realistically: FD001/FD003 main matrix is evidence; uncertainty/decision/robustness/domain shift are prototype tools.

Major issues:

1. The first draft risked treating all 2025 architecture papers as equally established. Very recent papers should be used as timeline/frontier evidence unless their protocol is fully inspected.
2. The review needed a clearer distinction between **domain-shift evaluation** and **domain adaptation training**.
3. The future experimental plan needed more concrete metrics for uncertainty calibration: PICP, MPIW, Winkler score, critical-zone PICP, and uncertainty-error correlation.
4. The literature matrix should carry relation-to-project fields for every paper, not just citations.
5. The review needed a stronger warning that fair comparison between classical ML and deep models is pipeline-level, not pure architecture-level, because input representations differ.

### Reviewer B: Aero-Engine and Safety Decision

**Decision: Major revision before safety-oriented framing is acceptable.**

Strengths:

1. The manuscript avoids claiming real aviation safety certification.
2. It acknowledges that C-MAPSS is simulation data and FD001/FD003 are single-operating-condition subsets.
3. It identifies overestimation risk as more safety-relevant than symmetric RMSE.

Major issues:

1. The first draft needed more explicit language that C-MAPSS is simulated benchmark telemetry, not real fleet maintenance evidence.
2. “Safety-aware” could be misread as operational safety validation. The safer phrase is “safety-oriented benchmark evaluation” unless real certification or field data are involved.
3. Maintenance decision simulation must be described as a benchmark-derived policy layer, not as a deployable airline maintenance scheduler.
4. The review should state that real maintenance policy requires constraints absent from C-MAPSS: fleet schedule, spare parts, inspection capacity, regulatory limits, and cost data.
5. The project’s uncertainty smoke run must not be used as scientific evidence.

## Round 1 Rebuttal and Revision Actions

### Response to Reviewer A

We agree with all major points. The final version now:

- Labels 2025 architecture papers as frontier/timeline evidence unless directly connected to the project plan.
- Adds a dedicated paragraph distinguishing domain-shift stress testing from domain adaptation training.
- Lists concrete uncertainty calibration metrics in the future plan.
- Uses `literature_matrix.csv` with 51 entries and fields for year, title, venue, dataset, method, metrics, contribution, limitations, relation to project, verification, and link.
- Frames classical-vs-deep comparison as an engineering pipeline comparison.

### Response to Reviewer B

We agree with the safety-boundary critique. The final version now:

- Repeatedly states that C-MAPSS is a simulated benchmark and does not validate real fleet safety.
- Uses “safety-aware evaluation” and “safety-oriented benchmark” rather than implying certification.
- Describes decision simulation as benchmark-derived cost evaluation.
- Lists missing real-world constraints.
- States that current uncertainty/decision/robustness/domain-shift modules are prototype/smoke-level until systematic experiments are completed.

## Round 2 Critique

### Reviewer A: PHM/RUL Methodology

**Decision: Minor revision / acceptable as a research foundation.**

Residual issues:

1. Some literature rows still have `exact dataset details unverified`; this is acceptable for matrix transparency but should be checked before journal submission.
2. The paper-cut recommendations are realistic, but the “uncertainty calibration paper” requires new experiments before any claim.
3. The review would benefit from adding FD002/FD004 once official data are available.

Positive assessment:

The final draft is methodologically coherent. It does not sell novelty as architecture novelty; it sells novelty as evaluation design. That is a defensible contribution for a C-MAPSS-based student project.

### Reviewer B: Aero-Engine and Safety Decision

**Decision: Minor revision / acceptable with scope caveats.**

Residual issues:

1. The phrase “safety-aware GRU” should always be interpreted as loss-weighting under benchmark metrics, not operational safety assurance.
2. Maintenance decision costs must be hypothetical unless calibrated with real maintenance data.
3. Any future paper should include a short “Responsible Use and Scope” paragraph.

Positive assessment:

The final draft no longer overclaims real-world safety. It properly separates simulated RUL evaluation from deployed aero-engine maintenance. It also identifies the right path from prediction to maintenance policy without pretending that path is already complete.

## Round 2 Rebuttal

We accept the residual issues. The final review keeps unverified details explicit in the matrix and does not convert them into formal claims. The project recommendations now prioritize a modest publishable safety-aware evaluation paper before attempting UQ, robustness, or maintenance-policy claims.

## Final Editorial Synthesis

**Editorial decision: Accept as a project-level literature review and paper-planning artifact.**

The review is suitable for guiding the next manuscript iteration: “Safety- and Policy-Oriented Aero-Engine RUL Prediction.” It is not yet a submission-ready journal article because it does not include full-text extraction for every recent paper and does not execute new uncertainty/decision/robustness experiments. However, it is a strong, evidence-grounded foundation for a short paper built around FD001/FD003 safety-aware evaluation.

## Next Paper Upgrade Advice

Priority order:

1. Freeze the first paper around FD001/FD003 safety-aware evaluation and avoid expanding the claim too far.
2. Add a compact literature table to the paper: direct baselines vs direction-supporting works.
3. Report all metrics consistently: RMSE, MAE, NASA score, critical RMSE30/50, overestimation ratio/magnitude.
4. Add a “Scope and Responsible Use” paragraph: C-MAPSS simulation, no real fleet certification, no deployment claim.
5. Treat uncertainty, maintenance decision, sensor robustness, and domain shift as the next paper or extended version unless systematic experiments are completed.

## Validation Evidence

- Literature matrix: `reports/review/literature_matrix.csv`
- References: `reports/review/references.bib`
- Final review manuscript: `reports/review/aero_engine_dl_review.md`
- Generated figures: `reports/review/figures/*.png`
- Local project scout report: subagent `Kuhn`
- Direction-supporting literature scout report: subagent `Harvey`
- DOI verification sources: Crossref, OpenAlex, DOI/publisher links

No destructive commands were used. No training runs were executed during this review.
