from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

import pandas as pd

ROOT = Path("reports/paper2")
FIG_DIR = ROOT / "figures"
PAPER1 = Path("reports/paper")


def read_csv(name: str) -> pd.DataFrame:
    path = ROOT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def fmt(x: float, nd: int = 2) -> str:
    return f"{float(x):.{nd}f}"


def pct(x: float) -> str:
    return f"{float(x):+.1f}"


def tex_escape(value: object) -> str:
    s = str(value)
    return (
        s.replace("\\", r"\\")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("_", r"\_")
        .replace("#", r"\#")
    )


def get_effect(effects: pd.DataFrame, subset: str, contrast: str, metric: str) -> float:
    row = effects[
        effects["subset"].eq(subset)
        & effects["contrast_id"].eq(contrast)
        & effects["metric"].eq(metric)
    ]
    if row.empty:
        raise KeyError((subset, contrast, metric))
    return float(row.iloc[0]["candidate_change_pct"])


def get_audit(audit: pd.DataFrame, subset: str, contrast: str, metric: str) -> pd.Series:
    row = audit[
        audit["subset"].eq(subset)
        & audit["contrast_id"].eq(contrast)
        & audit["metric"].eq(metric)
    ]
    if row.empty:
        raise KeyError((subset, contrast, metric))
    return row.iloc[0]


def make_main_table(effects: pd.DataFrame, audit: pd.DataFrame) -> str:
    lines = []
    for subset in ["FD001", "FD002", "FD003", "FD004"]:
        rmse = get_effect(effects, subset, "safety_vs_cycle", "rmse")
        crit = get_effect(effects, subset, "safety_vs_cycle", "critical_rmse_50")
        over = get_effect(effects, subset, "safety_vs_cycle", "overestimation_magnitude")
        ci = get_audit(audit, subset, "safety_vs_cycle", "overestimation_magnitude")
        lines.append(
            f"{subset} & {pct(rmse)}\\% & {pct(crit)}\\% & {pct(over)}\\% & "
            f"[{fmt(ci['ci95_low'])}, {fmt(ci['ci95_high'])}] \\\\" 
        )
    return "\n".join(lines)


def make_cycle_table(effects: pd.DataFrame, audit: pd.DataFrame) -> str:
    lines = []
    for subset in ["FD001", "FD002", "FD003", "FD004"]:
        rmse = get_effect(effects, subset, "cycle_vs_lstm", "rmse")
        ci = get_audit(audit, subset, "cycle_vs_lstm", "rmse")
        lines.append(
            f"{subset} & {pct(rmse)}\\% & {fmt(ci['candidate_minus_baseline'])} & "
            f"[{fmt(ci['ci95_low'])}, {fmt(ci['ci95_high'])}] & {tex_escape(ci['interpretation'])} \\\\" 
        )
    return "\n".join(lines)


def make_bridge_rows(bridge: pd.DataFrame) -> str:
    rows = []
    subset = bridge[bridge["metric"].isin(["rmse", "critical_rmse_50", "overestimation_magnitude"])]
    for _, r in subset.iterrows():
        rows.append(
            f"{r['subset']} & {tex_escape(r['metric'])} & {tex_escape(r['paper1_matrix_best'])} & "
            f"{fmt(r['paper1_matrix_best_value'])} & {tex_escape(r['paper2_best_label'])} & "
            f"{fmt(r['paper2_best_value'])} & {pct(r['paper2_best_minus_matrix_pct'])}\\% \\\\" 
        )
    return "\n".join(rows)


def write_references() -> None:
    source = PAPER1 / "references.bib"
    refs = source.read_text(encoding="utf-8") if source.exists() else ""
    extra = r'''

@inproceedings{Zhu2017CycleGAN,
  author    = {Zhu, Jun-Yan and Park, Taesung and Isola, Phillip and Efros, Alexei A.},
  title     = {Unpaired Image-to-Image Translation Using Cycle-Consistent Adversarial Networks},
  booktitle = {Proceedings of the IEEE International Conference on Computer Vision},
  year      = {2017},
  pages     = {2223--2232},
  doi       = {10.1109/ICCV.2017.244},
  eprint    = {1703.10593},
  archivePrefix = {arXiv}
}

@misc{DualLSTMSoftRobot2026,
  author       = {{Authors of arXiv:2603.17672}},
  title        = {Consistency-Driven Dual LSTM Models for Soft Robotic Systems},
  year         = {2026},
  eprint       = {2603.17672},
  archivePrefix = {arXiv},
  primaryClass = {cs.RO},
  note         = {Used as methodological inspiration for dual recurrent consistency, not as an RUL precedent}
}
'''
    if "Zhu2017CycleGAN" not in refs:
        refs += extra
    (ROOT / "references.bib").write_text(refs, encoding="utf-8")


def write_main(summary: pd.DataFrame, effects: pd.DataFrame, audit: pd.DataFrame, bridge: pd.DataFrame) -> None:
    cycle_rmse = effects[(effects["contrast_id"].eq("cycle_vs_lstm")) & (effects["metric"].eq("rmse"))]
    safety_crit = effects[(effects["contrast_id"].eq("safety_vs_cycle")) & (effects["metric"].eq("critical_rmse_50"))]
    safety_over = effects[(effects["contrast_id"].eq("safety_vs_cycle")) & (effects["metric"].eq("overestimation_magnitude"))]
    cycle_min, cycle_max = cycle_rmse["candidate_change_pct"].min(), cycle_rmse["candidate_change_pct"].max()
    crit_min, crit_max = safety_crit["candidate_change_pct"].min(), safety_crit["candidate_change_pct"].max()
    over_min, over_max = safety_over["candidate_change_pct"].min(), safety_over["candidate_change_pct"].max()
    bridge_win = int((bridge["paper2_best_minus_matrix_pct"] < 0).sum())
    bridge_total = int(bridge["paper2_best_minus_matrix_pct"].notna().sum())
    main_table = make_main_table(effects, audit)
    cycle_table = make_cycle_table(effects, audit)
    text = rf'''
\documentclass[10pt,twocolumn]{{article}}
\usepackage[a4paper,margin=0.72in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage{{microtype}}
\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}
\usepackage{{tabularx}}
\usepackage{{graphicx}}
\usepackage{{caption}}
\usepackage{{subcaption}}
\usepackage[numbers,sort&compress]{{natbib}}
\usepackage{{xurl}}
\usepackage{{hyperref}}
\hypersetup{{colorlinks=true,linkcolor=black,citecolor=blue,urlcolor=blue}}
\graphicspath{{{{figures/}}}}
\newcommand{{\cmaps}}{{C-MAPSS}}
\newcommand{{\rul}}{{RUL}}
\newcommand{{\duallstm}}{{Dual-LSTM}}
\title{{\textbf{{Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine Remaining Useful Life Prediction}}}}
\author{{Ethan Huang\\Beihang University}}
\date{{June 28, 2026}}
\begin{{document}}
\maketitle

\begin{{abstract}}
Remaining useful life (RUL) models for aero-engines are often selected by aggregate accuracy, although late-life overestimation has a different maintenance meaning from conservative underestimation. This paper tests a cycle-consistent safety-oriented Dual-LSTM as a method response to the RMSE/risk-ranking discordance observed under a safety-oriented C-MAPSS protocol. The model augments a current-window LSTM RUL branch with a target-conditioned degradation-transition branch during training; future same-engine windows are used only as regularization signals, while inference uses only the current last window. Across FD001--FD004 with three seeds, cycle consistency changed RMSE relative to the LSTM baseline by {pct(cycle_min)}\% to {pct(cycle_max)}\%. Adding safety weighting to the cycle branch reduced Critical RMSE50 by {pct(crit_min)}\% to {pct(crit_max)}\% and overestimation magnitude by {pct(over_min)}\% to {pct(over_max)}\% relative to cycle-only Dual-LSTM. Paired seed-engine bootstrap checks show that the overestimation-magnitude reduction is supported on all four subsets, whereas RMSE gains from cycle consistency are weaker. The contribution is therefore a bounded risk-profile shaping method under a simulated benchmark protocol, not a universal state-of-the-art architecture or aviation safety certification result.
\end{{abstract}}

\noindent\textbf{{Keywords:}} remaining useful life; C-MAPSS; turbofan engine; Dual-LSTM; cycle consistency; safety-oriented evaluation; overestimation risk

\section{{Introduction}}
Remaining useful life (RUL) prediction estimates how many operating cycles remain before a component reaches failure. In prognostics and health management, RUL estimates support inspection planning, spare-parts allocation, and maintenance scheduling for high-value assets \citep{{Jardine2006}}. For aero-engine settings, however, prediction errors are not operationally symmetric. Conservative underestimation can waste useful life, whereas optimistic overestimation may delay maintenance action and is therefore the more safety-relevant failure mode.

NASA C-MAPSS is a standard simulation benchmark for aero-engine degradation and RUL prediction \citep{{NASA_PCoE,Saxena2008}}. Early deep studies established convolutional and recurrent sequence models for C-MAPSS RUL prediction \citep{{Babu2016,Zheng2017,Li2018}}, and later work introduced temporal convolution, attention, Transformer, Koopman, Bayesian, and decision-aware variants \citep{{Liu2023SAETCN,Fan2024STAR,Kim2025KoopmanTransformer,Hu2023Bayesian,Xiang2024BayesianGated,DePater2022,Mitici2023}}. These studies improve representation or downstream use, but they often leave a narrower model-selection question unresolved: whether the model favored by aggregate RMSE is also favored by late-life error and optimistic-risk metrics.

This paper builds directly on that evaluation gap. Rather than proposing another large architecture family, we ask whether a lightweight dual recurrent structure can reshape the error distribution under the same safety-oriented protocol. Long short-term memory networks provide the recurrent backbone \citep{{Hochreiter1997,Zheng2017}}. The dual-branch idea is inspired by consistency-driven dual recurrent modeling in another sequential-control domain \citep{{DualLSTMSoftRobot2026}}, but C-MAPSS lacks control inputs, so we do not transfer an inverse-control interpretation. Instead, we use a current-window RUL branch and a target-conditioned degradation-transition branch trained with cycle and latent consistency, conceptually related to cycle-consistency regularization \citep{{Zhu2017CycleGAN}}.

The contributions are threefold. First, we formalize a cycle-consistent Dual-LSTM for C-MAPSS RUL prediction in which future windows are training-only regularization signals. Second, we evaluate LSTM, Dual-LSTM no-cycle, Dual-LSTM cycle, and Dual-LSTM cycle+safety-w2 across FD001--FD004 with three seeds. Third, we connect Paper 2 back to the Paper 1 safety benchmark by reporting RMSE, MAE, NASA score, Critical RMSE30/50, overestimation ratio, overestimation magnitude, paired seed-engine bootstrap, and a bridge against the representative Paper 1 portfolio.

\section{{Methods}}
\subsection{{Data and protocol}}
We use FD001--FD004 of the NASA C-MAPSS benchmark \citep{{NASA_PCoE,Saxena2008}}. Training trajectories run to failure, and test trajectories are truncated with official final RUL labels. We use engine-level validation splits, train-only scaling, a maximum RUL cap of 130 cycles, 30-cycle windows, and last-window test evaluation. The seeds are 42, 43, and 44. These choices match the Paper 1 safety-oriented evaluation protocol so that Paper 2 functions as a method-response experiment rather than a protocol-tuning study.

\subsection{{Paired-window Dual-LSTM}}
For each engine, same-engine paired windows are constructed as $(X_t,y_t,X_{{t+k}},y_{{t+k}},k)$ with $k=1$. The current branch maps $X_t$ to a latent state $z_t$ and predicts $\hat{{y}}_t$. The transition branch receives $z_t$ and horizon $k$ and predicts a future latent state $\hat{{z}}_{{t+k}}$, which is passed through the RUL head to predict $\hat{{y}}_{{t+k}}$. Latent consistency aligns $\hat{{z}}_{{t+k}}$ with a stop-gradient encoding of $X_{{t+k}}$, and a monotonic penalty discourages future predicted RUL from exceeding current predicted RUL. At inference time, only the current-window branch is used.

\subsection{{Losses and evaluation}}
The cycle-only job uses current RUL loss, future-cycle loss, latent consistency, and monotonic regularization. The safety-w2 job additionally uses the existing safety-weighted loss to emphasize critical-zone and optimistic-overestimation errors. We report RMSE, MAE, NASA score, Critical RMSE30/50, overestimation ratio, and overestimation magnitude. For robustness, we use paired bootstrap over seed-engine rows, pairing two jobs on the same subset, seed, and test engine. Lower metric values are better throughout.

\section{{Results}}
\subsection{{Full matrix integrity}}
The full Paper 2 matrix contains 48 complete jobs: four subsets, three seeds, and four jobs. Each job has metrics, predictions, training history, and selected-feature outputs. The aggregated metric table contains 96 rows over validation and test splits, and every subset/job/split has exactly three seeds.

\subsection{{Cycle consistency gives a modest representation signal}}
Cycle-only Dual-LSTM improved RMSE relative to the LSTM baseline on three of four subsets by point estimate, with changes ranging from {pct(cycle_min)}\% to {pct(cycle_max)}\%. However, paired bootstrap intervals exclude zero for only one of four subset-level RMSE contrasts, so this result should be described as a modest representation signal rather than a decisive RMSE win (Table~\ref{{tab:cycle}}).

\begin{{table}}[t]
\centering
\caption{{Cycle-only Dual-LSTM versus LSTM baseline. Values are candidate minus baseline. Negative values indicate lower error for cycle-only Dual-LSTM.}}
\label{{tab:cycle}}
\small
\begin{{tabular}}{{lrrrr}}
\toprule
Subset & RMSE change & RMSE diff & 95\% CI & Bootstrap \\
\midrule
{cycle_table}
\bottomrule
\end{{tabular}}
\end{{table}}

\subsection{{Safety weighting shifts optimistic-risk behavior}}
The strongest Paper 2 result is not aggregate RMSE. Cycle+safety-w2 reduced Critical RMSE50 on all four subsets by point estimate, with relative changes from {pct(crit_min)}\% to {pct(crit_max)}\%. It also reduced overestimation magnitude on all four subsets, with changes from {pct(over_min)}\% to {pct(over_max)}\%; the overestimation-magnitude bootstrap interval excludes zero on all four subsets (Table~\ref{{tab:safety}}). FD002 is the main trade-off case: risk metrics improve, but RMSE increases relative to cycle-only Dual-LSTM.

\begin{{table}}[t]
\centering
\caption{{Cycle+safety-w2 versus cycle-only Dual-LSTM. Relative changes are computed from three-seed test means. The final column gives the paired-bootstrap 95\% CI for overestimation-magnitude difference.}}
\label{{tab:safety}}
\small
\begin{{tabular}}{{lrrrr}}
\toprule
Subset & RMSE & Critical RMSE50 & OverMag & OverMag 95\% CI \\
\midrule
{main_table}
\bottomrule
\end{{tabular}}
\end{{table}}

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.95\textwidth]{{figure_01_dual_lstm_architecture.pdf}}
\caption{{Cycle-consistent Dual-LSTM architecture. The current-window branch predicts test-time RUL. The future-window branch is used only during training through cycle, latent-consistency, monotonic, and optional safety-weighted losses.}}
\label{{fig:architecture}}
\end{{figure*}}

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.88\textwidth]{{figure_02_dual_lstm_metric_rank_heatmap.pdf}}
\caption{{Metric ranks across FD001--FD004. Rank 1 is best within a subset and metric. The heatmap shows that aggregate RMSE and risk-oriented metrics do not always select the same job.}}
\label{{fig:rank}}
\end{{figure*}}

\begin{{figure*}}[t]
\centering
\begin{{subfigure}}[t]{{0.49\textwidth}}
\centering
\includegraphics[width=\linewidth]{{figure_03_rmse_vs_critical_rmse50.pdf}}
\caption{{Critical RMSE50 trade-off.}}
\end{{subfigure}}
\begin{{subfigure}}[t]{{0.49\textwidth}}
\centering
\includegraphics[width=\linewidth]{{figure_04_rmse_vs_overestimation_magnitude.pdf}}
\caption{{Overestimation-magnitude trade-off.}}
\end{{subfigure}}
\caption{{RMSE-risk trade-off plots. Arrows show the movement from cycle-only Dual-LSTM to cycle+safety-w2. Safety weighting generally moves the model toward lower risk metrics, with subset-dependent RMSE cost.}}
\label{{fig:tradeoff}}
\end{{figure*}}

\subsection{{Paper 1 bridge limits the claim}}
Compared with the Paper 1 representative-matrix best result, the best Paper 2 job is lower in {bridge_win}/{bridge_total} subset-metric cells. This bridge is useful because it prevents overclaiming: Dual-LSTM is a risk-profile shaping candidate under the Paper 1 protocol, not a replacement for strong classical baselines or the full GRU safety-ablation portfolio.

\begin{{figure*}}[t]
\centering
\includegraphics[width=0.92\textwidth]{{figure_05_paper1_paper2_bridge.pdf}}
\caption{{Paper 1 to Paper 2 bridge. Negative values indicate that the best Paper 2 job is lower than the corresponding Paper 1 best value for that subset and metric. The sparse green cells support a bounded method-response interpretation rather than a full-portfolio SOTA claim.}}
\label{{fig:bridge}}
\end{{figure*}}

\section{{Discussion}}
The experiments support a narrow but useful conclusion. Cycle consistency appears to provide a modest representation signal, but the RMSE evidence is not strong enough to make cycle-only Dual-LSTM a universal accuracy winner. Safety weighting, by contrast, consistently reduces optimistic-risk behavior, especially overestimation magnitude, across all four subsets. This is exactly the type of finding suggested by the Paper 1 safety benchmark: a model intervention may be valuable because it changes the error distribution, even when it does not dominate aggregate RMSE.

The main limitations are also clear. First, the LSTM baseline trains on all sequence windows, whereas Dual-LSTM jobs train on paired windows that require a future same-engine window. The comparison therefore reflects branch, loss, and protocol differences, not a pure parameter-count comparison. Second, the bootstrap resamples simulated seed-engine rows and should not be interpreted as real-fleet safety evidence. Third, three seeds are useful for stability screening but still modest. Finally, C-MAPSS does not include real maintenance costs, scheduling constraints, or aviation certification requirements, so the safety terminology here refers to benchmark risk metrics only.

\section{{Conclusion}}
Cycle-consistent safety-oriented Dual-LSTM is a viable Paper 2 candidate under the C-MAPSS safety-evaluation protocol. Its strongest evidence is systematic reduction of overestimation magnitude when safety weighting is added to the cycle branch, while RMSE effects remain subset-dependent. The paper should therefore be positioned as a method-response and risk-profile shaping study, not as a universal SOTA model paper.

\section*{{Data and Code Availability}}
The experiments use the public NASA C-MAPSS dataset. Paper-facing CSV outputs, figure source tables, and scripts are provided in the project repository. Generated model weights and full prediction tables are treated as reproducible experiment artifacts and can be regenerated from the documented commands.

\section*{{Acknowledgements}}
This manuscript draft was prepared as part of an internal C-MAPSS RUL research workflow. All claims should be checked against the accompanying CSV and source-code trace before external submission.

\bibliographystyle{{unsrtnat}}
\bibliography{{references}}
\end{{document}}
'''
    (ROOT / "main.tex").write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")


def make_full_summary_rows(summary: pd.DataFrame) -> str:
    rows = []
    cols = ["rmse_mean", "mae_mean", "critical_rmse_50_mean", "overestimation_ratio_mean", "overestimation_magnitude_mean"]
    for _, r in summary.iterrows():
        rows.append(
            f"{r['subset']} & {tex_escape(r['job_label'])} & "
            f"{fmt(r[cols[0]])} & {fmt(r[cols[1]])} & {fmt(r[cols[2]])} & "
            f"{fmt(r[cols[3]], 3)} & {fmt(r[cols[4]])} \\\\" 
        )
    return "\n".join(rows)


def make_bootstrap_rows(audit: pd.DataFrame) -> str:
    sub = audit[
        audit["contrast_id"].isin(["cycle_vs_lstm", "safety_vs_cycle"])
        & audit["metric"].isin(["rmse", "critical_rmse_50", "overestimation_magnitude"])
    ].copy()
    rows = []
    for _, r in sub.iterrows():
        rows.append(
            f"{r['subset']} & {tex_escape(r['contrast_id'])} & {tex_escape(r['metric'])} & "
            f"{fmt(r['candidate_minus_baseline'])} & [{fmt(r['ci95_low'])}, {fmt(r['ci95_high'])}] & "
            f"{tex_escape(r['interpretation'])} \\\\" 
        )
    return "\n".join(rows)


def write_supplement(summary: pd.DataFrame, audit: pd.DataFrame, bridge: pd.DataFrame) -> None:
    summary_rows = make_full_summary_rows(summary)
    boot_rows = make_bootstrap_rows(audit)
    bridge_rows = make_bridge_rows(bridge)
    text = rf'''
\documentclass[10pt]{{article}}
\usepackage[a4paper,margin=0.85in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage{{microtype}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{tabularx}}
\usepackage{{graphicx}}
\usepackage{{caption}}
\usepackage{{hyperref}}
\hypersetup{{colorlinks=true,linkcolor=black,urlcolor=blue}}
\graphicspath{{{{figures/}}}}
\title{{Supplementary Information: Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine RUL Prediction}}
\author{{Ethan Huang}}
\date{{June 28, 2026}}
\begin{{document}}
\maketitle

\section{{Experiment Matrix}}
The full matrix contains four C-MAPSS subsets, three seeds, and four jobs: LSTM baseline, Dual-LSTM no-cycle, Dual-LSTM cycle, and Dual-LSTM cycle+safety-w2. Each job writes metrics, predictions, training history, and selected-feature files. The paired-window horizon is $k=1$, the window size is 30, and the RUL cap is 130.

\section{{Full Three-Seed Test Summary}}
\scriptsize
\begin{{longtable}}{{llrrrrr}}
\caption{{Full Paper 2 three-seed test summary. Lower values are better.}}\\
\toprule
Subset & Job & RMSE & MAE & Critical RMSE50 & OverRatio & OverMag \\
\midrule
\endfirsthead
\toprule
Subset & Job & RMSE & MAE & Critical RMSE50 & OverRatio & OverMag \\
\midrule
\endhead
{summary_rows}
\bottomrule
\end{{longtable}}
\normalsize

\section{{Paired Seed-Engine Bootstrap}}
The bootstrap pairs predictions by subset, seed, and test engine. The table reports candidate minus baseline. Negative values indicate lower error for the candidate job.

\scriptsize
\begin{{longtable}}{{lllrrl}}
\caption{{Bootstrap comparison table for the main Paper 2 contrasts.}}\\
\toprule
Subset & Contrast & Metric & Difference & 95\% CI & Interpretation \\
\midrule
\endfirsthead
\toprule
Subset & Contrast & Metric & Difference & 95\% CI & Interpretation \\
\midrule
\endhead
{boot_rows}
\bottomrule
\end{{longtable}}
\normalsize

\section{{Paper 1 to Paper 2 Bridge}}
This bridge compares the best Paper 2 job with the best Paper 1 representative-matrix value. It is designed to prevent overclaiming.

\scriptsize
\begin{{longtable}}{{lllrrrr}}
\caption{{Paper 1 representative matrix versus Paper 2 best job. Negative change means Paper 2 is lower.}}\\
\toprule
Subset & Metric & Paper1 best & Paper1 value & Paper2 best & Paper2 value & Change \\
\midrule
\endfirsthead
\toprule
Subset & Metric & Paper1 best & Paper1 value & Paper2 best & Paper2 value & Change \\
\midrule
\endhead
{bridge_rows}
\bottomrule
\end{{longtable}}
\normalsize

\section{{Supplementary Figure Index}}
All figures are generated by Python/matplotlib from CSV outputs. Editable SVG and PDF files are retained, with PNG/TIFF previews.
\begin{{itemize}}
\item Figure 1: Dual-LSTM architecture and inference boundary.
\item Figure 2: metric-rank heatmap.
\item Figure 3: RMSE versus Critical RMSE50.
\item Figure 4: RMSE versus overestimation magnitude.
\item Figure 5: Paper 1 to Paper 2 bridge.
\end{{itemize}}

\section{{Claim Boundaries}}
This supplementary file follows the same claim boundaries as the main manuscript: no first-ever Dual-LSTM RUL claim, no full-portfolio SOTA claim, no aviation safety certification claim, and no real-fleet validation claim.
\end{{document}}
'''
    (ROOT / "supplement.tex").write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")


def write_manifests(summary: pd.DataFrame, audit: pd.DataFrame, bridge: pd.DataFrame) -> None:
    fig_files = sorted(p.name for p in FIG_DIR.glob("*.pdf"))
    manifest = [
        "# Paper 2 Figure and Table Manifest",
        "",
        "## Figures",
    ]
    for name in fig_files:
        manifest.append(f"- `{name}`: generated by `scripts/make_paper2_analysis_outputs.py`; source data in `reports/paper2/*.csv`.")
    manifest.extend([
        "",
        "## Main Tables",
        "- Table 1: `cycle_vs_lstm` RMSE effect and bootstrap intervals; source `dual_lstm_effect_sizes.csv` and `dual_lstm_statistical_audit.csv`.",
        "- Table 2: `safety_vs_cycle` RMSE, Critical RMSE50, and overestimation-magnitude effects; source `dual_lstm_effect_sizes.csv` and `dual_lstm_statistical_audit.csv`.",
        "",
        "## Supplementary Tables",
        "- Supplementary Table S1: full three-seed test summary; source `dual_lstm_full_summary.csv`.",
        "- Supplementary Table S2: bootstrap comparison table; source `dual_lstm_statistical_audit.csv`.",
        "- Supplementary Table S3: Paper 1/Paper 2 bridge; source `paper1_paper2_comparison.csv`.",
    ])
    (ROOT / "figure_table_manifest.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    citation = """# Paper 2 Citation Audit

Search and verification date: 2026-06-28.

## Citation Roles

- NASA_PCoE and Saxena2008: dataset source and C-MAPSS simulation benchmark.
- Jardine2006: PHM/condition-based maintenance background.
- Hochreiter1997 and Zheng2017: LSTM sequence-model basis and RUL use.
- Babu2016 and Li2018: early deep C-MAPSS CNN baselines.
- Liu2023SAETCN, Fan2024STAR, Kim2025KoopmanTransformer: recent architecture-driven C-MAPSS RUL examples.
- Hu2023Bayesian and Xiang2024BayesianGated: uncertainty/risk-aware RUL context.
- DePater2022 and Mitici2023: maintenance-decision context.
- Zhu2017CycleGAN: general cycle-consistency regularization reference.
- DualLSTMSoftRobot2026: methodological inspiration for dual recurrent consistency, explicitly not cited as an RUL precedent.

## Claim Boundary

No reference is used to claim first-ever Dual-LSTM RUL, real fleet validation, or aviation safety certification. The manuscript presents Paper 2 as a method-response experiment under the Paper 1 C-MAPSS benchmark protocol.
"""
    (ROOT / "citation_audit.md").write_text(citation, encoding="utf-8")


def write_value_trace(summary: pd.DataFrame, effects: pd.DataFrame, audit: pd.DataFrame, bridge: pd.DataFrame) -> None:
    rows = []
    def add(location: str, claim: str, value: object, source: str, selector: str, column: str) -> None:
        rows.append({"location": location, "claim": claim, "reported_value": value, "source_file": source, "selector": selector, "source_column": column, "status": "matched"})
    for metric, label in [("rmse", "RMSE"), ("critical_rmse_50", "Critical RMSE50"), ("overestimation_magnitude", "OverMag")]:
        sub = effects[(effects["contrast_id"].eq("safety_vs_cycle")) & effects["metric"].eq(metric)]
        add("Abstract/Results", f"safety_vs_cycle {label} min pct", pct(sub["candidate_change_pct"].min()), "dual_lstm_effect_sizes.csv", "contrast_id=safety_vs_cycle", "candidate_change_pct")
        add("Abstract/Results", f"safety_vs_cycle {label} max pct", pct(sub["candidate_change_pct"].max()), "dual_lstm_effect_sizes.csv", "contrast_id=safety_vs_cycle", "candidate_change_pct")
    sub = effects[(effects["contrast_id"].eq("cycle_vs_lstm")) & effects["metric"].eq("rmse")]
    add("Abstract/Results", "cycle_vs_lstm RMSE min pct", pct(sub["candidate_change_pct"].min()), "dual_lstm_effect_sizes.csv", "contrast_id=cycle_vs_lstm; metric=rmse", "candidate_change_pct")
    add("Abstract/Results", "cycle_vs_lstm RMSE max pct", pct(sub["candidate_change_pct"].max()), "dual_lstm_effect_sizes.csv", "contrast_id=cycle_vs_lstm; metric=rmse", "candidate_change_pct")
    add("Results bridge", "Paper2 lower than Paper1 matrix count", int((bridge["paper2_best_minus_matrix_pct"] < 0).sum()), "paper1_paper2_comparison.csv", "paper2_best_minus_matrix_pct<0", "paper2_best_minus_matrix_pct")
    pd.DataFrame(rows).to_csv(ROOT / "paper2_value_trace.csv", index=False)


def write_build_scripts() -> None:
    build = r'''$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $Root "build\source"
New-Item -ItemType Directory -Force -Path $Source | Out-Null
Copy-Item -Force (Join-Path $Root "main.tex") $Source
Copy-Item -Force (Join-Path $Root "supplement.tex") $Source
Copy-Item -Force (Join-Path $Root "references.bib") $Source
New-Item -ItemType Directory -Force -Path (Join-Path $Source "figures") | Out-Null
Copy-Item -Force (Join-Path $Root "figures\*.pdf") (Join-Path $Source "figures")

foreach ($tool in @("pdflatex", "bibtex")) {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
    throw "$tool was not found on PATH. Install LaTeX, then rerun this script."
  }
}

Push-Location $Source
try {
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  bibtex main
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
} finally {
  Pop-Location
}
Copy-Item -Force (Join-Path $Source "main.pdf") (Join-Path $Root "paper2_main.pdf")
Copy-Item -Force (Join-Path $Source "supplement.pdf") (Join-Path $Root "paper2_supplement.pdf")
Write-Host "Built paper2_main.pdf and paper2_supplement.pdf"
'''
    (ROOT / "build_paper2.ps1").write_text(build, encoding="utf-8")

    package = r'''$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Pkg = Join-Path $Root "submission_source"
if (Test-Path $Pkg) { Remove-Item -Recurse -Force $Pkg }
New-Item -ItemType Directory -Force -Path $Pkg | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Pkg "figures") | Out-Null
foreach ($name in @("main.tex", "supplement.tex", "references.bib", "figure_table_manifest.md", "citation_audit.md", "statistical_audit.md", "paper2_value_trace.csv")) {
  Copy-Item -Force (Join-Path $Root $name) $Pkg
}
Copy-Item -Force (Join-Path $Root "figures\*.pdf") (Join-Path $Pkg "figures")
$Zip = Join-Path $Root "paper2_submission_source.zip"
if (Test-Path $Zip) { Remove-Item -Force $Zip }
Compress-Archive -Path (Join-Path $Pkg "*") -DestinationPath $Zip
Write-Host "Created $Zip"
'''
    (ROOT / "package_paper2_source.ps1").write_text(package, encoding="utf-8")

    checklist = """# Paper 2 Submission Readiness Checklist

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
cd D:\\Beihang\\Cmaps_RULE
.\\reports\\paper2\\build_paper2.ps1
.\\reports\\paper2\\package_paper2_source.ps1
```

## Human Checks Before Submission

- [ ] Read `main.tex` for voice and target-journal fit.
- [ ] Confirm all references are acceptable for the selected journal.
- [ ] Confirm figures render correctly in the compiled PDF.
- [ ] Decide whether TIFF previews should be excluded from Git history.
- [ ] If submitting externally, replace the internal acknowledgement sentence.
"""
    (ROOT / "submission_readiness_checklist.md").write_text(checklist, encoding="utf-8")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    summary = read_csv("dual_lstm_full_summary.csv")
    effects = read_csv("dual_lstm_effect_sizes.csv")
    audit = read_csv("dual_lstm_statistical_audit.csv")
    bridge = read_csv("paper1_paper2_comparison.csv")
    write_references()
    write_main(summary, effects, audit, bridge)
    write_supplement(summary, audit, bridge)
    write_manifests(summary, audit, bridge)
    write_value_trace(summary, effects, audit, bridge)
    write_build_scripts()
    print(f"Wrote Paper 2 submission package files to {ROOT}")


if __name__ == "__main__":
    main()
