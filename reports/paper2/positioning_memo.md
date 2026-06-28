# Paper 2 Positioning Memo

Working title: Cycle-Consistent Safety-Oriented Dual-LSTM for Aero-Engine RUL Prediction.

Paper 2 is a method-response paper built on Paper 1's safety-oriented C-MAPSS evaluation protocol. It tests whether a Dual-LSTM with target-conditioned degradation transition and cycle consistency can shift late-life and optimistic-overestimation risk while keeping aggregate RMSE interpretable.

Current matrix state: complete.
Observed subsets: FD001, FD002, FD003, FD004.
Observed jobs: lstm_baseline_h64_l1_w30, dual_no_cycle_h64_l1_w30, dual_cycle_h64_l1_w30, dual_cycle_safety_w2_h64_l1_w30.
Minimum seed coverage per subset/job: 3.

Protocol cautions:

- The LSTM baseline trains on all sequence windows, while Dual-LSTM jobs train on paired windows that require a same-engine future window. Interpret model differences as branch/loss/protocol evidence, not as pure parameter-count effects.
- Inference still uses only the current last window; future windows and future RUL are training-only regularization signals.

Trade-off warnings:

- FD002 critical_rmse_50: dual_cycle_safety_w2_h64_l1_w30 is risk-best with +13.2% RMSE versus dual_no_cycle_h64_l1_w30; write as a trade-off.
- FD002 overestimation_magnitude: dual_cycle_safety_w2_h64_l1_w30 is risk-best with +13.2% RMSE versus dual_no_cycle_h64_l1_w30; write as a trade-off.
- FD002 overestimation_ratio: dual_cycle_safety_w2_h64_l1_w30 is risk-best with +13.2% RMSE versus dual_no_cycle_h64_l1_w30; write as a trade-off.

Claim boundaries:

- Do not claim first-ever Dual-LSTM RUL.
- Do not claim new architecture SOTA.
- Do not claim aviation safety certification or real fleet validation.
- Treat negative FD002/FD003 results as subset-dependent trade-offs, not failures to hide.
