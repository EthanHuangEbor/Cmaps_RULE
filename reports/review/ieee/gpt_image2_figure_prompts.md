# GPT-Image2 Figure Prompt Pack for the IEEE RUL Review

Use these prompts to generate conceptual IEEE-style figures for `aero_engine_rul_ieee_review.tex`.
Save each image under `reports/review/ieee/figures/` using the exact filename shown.

Global style to prepend to every prompt:

```text
Create a clean IEEE-style technical research figure on a white background. Use a restrained colorblind-safe palette: deep blue #0072B2, vermilion #D55E00, teal #009E73, sky blue #56B4E9, purple #CC79A7, gray #666666. Use vector-like crisp shapes, thin lines, high contrast, minimal shadows, and professional conference-paper aesthetics. Keep text labels short, legible, and in English. Do not invent numerical results, curves, or benchmark scores. Do not include logos, aircraft manufacturer branding, watermarks, decorative gradients, or photorealistic engines unless explicitly requested. Leave enough whitespace for a caption in LaTeX.
```

## Figure 1

Filename: `fig01_cmapss_benchmark_map.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw a benchmark landscape map for aero-engine RUL research. Center title: "C-MAPSS and N-CMAPSS Benchmark Landscape". Left panel: "C-MAPSS simulated turbofan run-to-failure" with four labeled tiles: FD001 single condition / single fault, FD002 multiple conditions / single fault, FD003 single condition / multiple faults, FD004 multiple conditions / multiple faults. Right panel: "N-CMAPSS richer benchmark" with labels "real flight profiles", "richer operating histories", "higher realism". Add a bottom caution strip: "Benchmark evidence, not real fleet deployment evidence". Use simple engine-sensor icons, no numeric results.
```

Placement: Section II, caption about the benchmark landscape.

## Figure 2

Filename: `fig02_phm_rul_pipeline.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw an end-to-end PHM RUL pipeline as a left-to-right flow diagram. Blocks: "Raw multivariate sensors", "Cleaning and normalization", "Sliding windows", "Feature or sequence input", "RUL model", "Point / interval prediction", "Safety-aware metrics", "Maintenance decision simulation". Add thin arrows between blocks. Add small side notes near the metric block: "critical zone", "overestimation", "calibration". Keep the diagram flat and publication-ready.
```

Placement: Section II, pipeline protocol.

## Figure 3

Filename: `fig03_taxonomy_six_lines.png`

Aspect ratio: 4:3, recommended size 2100 x 1575 px.

Prompt:

```text
[Global style] Create a taxonomy diagram with one central node labeled "Aero-engine RUL Prediction". Surround it with six branches: "Feature-engineered ML", "LSTM / GRU / CNN", "Attention / Transformer / TCN / GNN", "Transfer / Domain Adaptation", "Uncertainty / Safety-aware RUL", "Maintenance Decision Evaluation". Under each branch add 2-3 tiny keyword chips: ML branch has "Ridge", "RF", "GB"; sequence branch has "window", "temporal state"; transfer branch has "FD shift", "target domain"; uncertainty branch has "PICP", "risk"; decision branch has "cost", "trigger". No fake metrics.
```

Placement: Section III, taxonomy of six technical lines.

## Figure 4

Filename: `fig04_ml_vs_deep_protocol.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw a two-lane comparison of modeling pipelines. Top lane title: "Feature-engineered ML". Blocks: "sensor window", "mean/std/slope/last/delta features", "Ridge / RF / GB", "RUL output". Bottom lane title: "Deep sequence models". Blocks: "sensor window", "raw multivariate sequence", "CNN / LSTM / GRU", "RUL output". Add a shared evaluation block on the right: "same test engines, same metrics". Add a small warning label: "Compare pipelines, not only architectures". Use clean arrows and no numeric values.
```

Placement: Section IV, fair protocol comparison.

## Figure 5

Filename: `fig05_sequence_model_evolution.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Create a chronological evolution diagram for RUL model families. A horizontal timeline with six stations: "Feature statistics", "CNN", "LSTM / GRU", "Attention", "Transformer / TCN", "Graph neural networks". For each station show a small abstract icon: table, convolution filter, recurrent loop, attention weights, layered transformer blocks, sensor graph. Do not include years or performance numbers. Add a bottom note: "Architecture novelty must be evaluated with safety and decision metrics".
```

Placement: Section V, deep sequence and advanced architectures.

## Figure 6

Filename: `fig06_domain_shift_adaptation.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw a domain shift and adaptation concept diagram for C-MAPSS. Left side: "Source domain" with FD001 and FD003 sensor distributions shown as abstract clusters. Right side: "Target domain" with FD002 and FD004 clusters shifted in position. Center arrows: one dashed arrow labeled "stress test only" and one solid arrow labeled "adaptation with target data". Add three small labels near the shift: "operating condition shift", "fault-mode shift", "sensor distribution shift". No numeric axes or fake distributions.
```

Placement: Section VI, transfer and domain shift.

## Figure 7

Filename: `fig07_uncertainty_calibration.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw a conceptual uncertainty calibration panel for RUL prediction. Use a simple schematic line labeled "true RUL trajectory" and a prediction band labeled "prediction interval"; keep it abstract and avoid numerical tick labels. Add three callout boxes: "Coverage: PICP", "Width: MPIW", "Critical-zone PICP". Add a small scatter-like inset labeled "uncertainty vs error" with generic dots but no numbers. Make clear this is a schematic, not reported data.
```

Placement: Section VII, uncertainty calibration.

## Figure 8

Filename: `fig08_overestimation_safety.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Create a two-panel safety interpretation figure. Left panel: "Conservative underestimation" showing predicted RUL lower than true RUL, arrow to "early maintenance cost". Right panel: "Optimistic overestimation" showing predicted RUL higher than true RUL near failure, arrow to "delayed maintenance risk". Use a late-life shaded region labeled "critical zone". Keep the visual symbolic with simple lines and warning icons, no real failure probabilities or numeric values.
```

Placement: Section VII, overestimation risk.

## Figure 9

Filename: `fig09_maintenance_decision_loop.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw a circular maintenance decision loop. Nodes around the loop: "RUL forecast", "uncertainty estimate", "threshold or policy rule", "maintenance action", "early / late cost", "policy evaluation". Add a feedback arrow from policy evaluation back to model evaluation. Add two small side boxes: "point estimate trigger" and "lower-bound trigger". The figure should look like an IEEE systems diagram, not a business infographic.
```

Placement: Section VIII, decision-oriented RUL prediction.

## Figure 10

Filename: `fig10_sensor_robustness_xai.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Draw a sensor robustness and XAI workflow. Left: vertical stack of sensor channels. Middle top: "importance / occlusion / LIME" producing highlighted important sensors. Middle bottom: stress test blocks "masking", "noise", "dropout". Right: evaluation outputs "RMSE change", "critical-zone error", "overestimation change". Add arrows showing that explanations guide stress tests. Do not imply physical causality; use label "model reliance, not causal fault source".
```

Placement: Section IX, explainability and robustness.

## Figure 11

Filename: `fig11_project_positioning_roadmap.png`

Aspect ratio: 16:9, recommended size 2400 x 1350 px.

Prompt:

```text
[Global style] Create a project positioning roadmap for "Cmaps_RULE". Use a horizontal maturity map with four columns: "Mature evidence", "Near-term paper", "Prototype extensions", "Future generalization". In mature evidence list: "FD001/FD003 baselines", "safety metrics", "seeded runs". In near-term paper list: "critical-zone RUL", "overestimation risk", "safety-aware GRU". In prototype extensions list: "uncertainty", "decision simulation", "sensor robustness", "domain shift". In future generalization list: "FD002/FD004", "N-CMAPSS", "domain adaptation". Keep text compact and legible.
```

Placement: Section XI, project positioning and roadmap.

## Notes for Insertion

1. Generate PNG files with transparent or white background; white is safer for IEEE PDF.
2. Save images exactly under `reports/review/ieee/figures/`.
3. Keep all chart-like figures schematic unless you regenerate them from real CSV data.
4. If GPT-Image2 distorts text, regenerate with fewer words and use the LaTeX caption for detail.
5. Do not use generated figures as evidence for numeric performance claims.
