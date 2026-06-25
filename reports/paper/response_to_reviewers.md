# Response to Simulated Reviewer

Dear Reviewer,

Thank you for the careful and constructive comments. We agree that the manuscript should be positioned as a reproducible safety-aware benchmark study rather than as a new state-of-the-art method. We revised the paper accordingly.

## Response 1: Reproducibility and Method Detail

We expanded the methodology section with dataset scope, engine-level validation splitting, train-only scaling, capped RUL labeling, low-variance feature removal, sliding-window generation, last-window test evaluation, model configurations, optimizer settings, early stopping, and seed settings.

**Change made:** Added Table 1 for dataset scope and Table 2 for the experimental protocol.

## Response 2: Three Seeds and Statistical Claims

We agree that three seeds are only a minimum robustness check. The revised manuscript reports RMSE as mean ± standard deviation and clarifies that full mean/std/min/max CSV summaries are available for every metric. We also added a threats-to-validity section that explicitly notes the limited statistical power of three seeds.

**Change made:** Revised the Results section and added Threats to Validity.

## Response 3: Safety-Aware Loss Definition

We defined the safety-aware loss mathematically. The revised loss uses additive weights for critical samples and overestimation errors:

`w_i = 1 + (alpha - 1) I(y_i <= 50) + (beta - 1) I(y_hat_i > y_i)`.

For the focused safety-aware runs, `alpha = beta = 1.5`, so samples that are both critical and overestimated receive weight 2.0.

**Change made:** Replaced the vague loss description with the exact equation used by the code.

## Response 4: Safety Metrics

We retained RMSE and MAE, and emphasized NASA S-score, critical RMSE50, and overestimation ratio. We added the NASA S-score equation to remove ambiguity about the stronger overestimation penalty.

**Change made:** Added NASA S-score formula and clarified positive error as RUL overestimation.

## Response 5: Scope of FD001/FD003

We agree that FD001 and FD003 do not support broad C-MAPSS claims. The revised manuscript scopes claims to FD001/FD003 and states that FD002/FD004 remain future work because they involve multiple operating conditions.

**Change made:** Revised Abstract, Introduction, Conclusion, and Threats to Validity.

## Response 6: Window50 Interpretation

We softened the window50 claim. The revised paper describes the FD003 window50 GRU result as an empirical observation among tested 20/30/50-cycle configurations, not as a general proof that longer windows always help recurrent models.

**Change made:** Revised Results and Discussion.

## Response 7: Classical vs Deep Fairness

We agree that the comparison is a pipeline comparison. The revised Methodology explicitly states that classical models receive handcrafted window summaries while deep models receive ordered sequences.

**Change made:** Added a practical pipeline comparison caveat in Methodology and Threats to Validity.

## Remaining Limitations

The manuscript is now stronger as a student paper draft, but it still needs more evidence before formal submission:

- More seeds or paired bootstrap confidence intervals.
- FD002/FD004 experiments.
- More complete residual plots and late-life error distributions.
- Citation verification and venue-specific formatting.
- A stronger safety objective or decision-policy simulation if aiming beyond a course or undergraduate research venue.
