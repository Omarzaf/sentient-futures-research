# Why these scenarios sit below GFI India: numerical diagnostics

Conditional retained conversion: the GFI source price and retail valuation bases are unstated; treat both its anchor and targets as 2022 rupees, inflate to 2025 and convert at the retained 2025 market exchange rate.

Supplementary arithmetic and assumption sensitivity; not a validated forecast, causal gap attribution, or replacement for the retained 127 rows.

The source fermentation baseline is a dash, preserved as missing. Its CAGR and absolute increase are undefined. Source-value growth rates cannot yet be classified as nominal or real.

## GFI source categories

| Category | Scenario | 2022 crore | 2030 crore | Absolute increase | Implied annual growth |
|---|---|---:|---:|---:|---:|
| Plant-based meat | low | 100 | 1,803 | 1,703 | 43.55% |
| Plant-based meat | medium | 100 | 3,525 | 3,425 | 56.10% |
| Plant-based meat | high | 100 | 5,884 | 5,784 | 66.42% |
| Plant-based dairy | low | 250 | 4,827 | 4,577 | 44.78% |
| Plant-based dairy | medium | 250 | 7,643 | 7,393 | 53.34% |
| Plant-based dairy | high | 250 | 10,625 | 10,375 | 59.79% |
| Plant-based eggs | low | 1 | 527 | 526 | 118.89% |
| Plant-based eggs | medium | 1 | 989 | 988 | 136.81% |
| Plant-based eggs | high | 1 | 1,416 | 1,415 | 147.68% |
| Fermentation-derived meat | low | - | 318 | N/A | N/A |
| Fermentation-derived meat | medium | - | 622 | N/A | N/A |
| Fermentation-derived meat | high | - | 1,038 | N/A | N/A |
| Overall domestic market | low | 351 | 7,475 | 7,124 | 46.57% |
| Overall domestic market | medium | 351 | 12,779 | 12,428 | 56.73% |
| Overall domestic market | high | 351 | 18,963 | 18,612 | 64.66% |

All three 2030 category sums reconcile to the reported totals. The known 2022 cells sum to 351 crore, but this does not resolve the fermentation dash as zero.

## Targets and required extra annual growth

| Scenario | GFI multiple | Conditional USD million | Required growth at midpoint elasticity | Range across elasticity bounds | Fermentation / GFI total | Arithmetic reduction in gap if fermentation subtracted |
|---|---:|---:|---:|---:|---:|---:|
| low | 21.296x | 964.438 | 32.38% | 29.19–35.65% | 4.254% | 5.283% |
| medium | 36.407x | 1648.769 | 41.56% | 38.14–45.05% | 4.867% | 5.493% |
| high | 54.026x | 2446.640 | 48.72% | 45.13–52.39% | 5.474% | 5.929% |

Required growth solves the existing equation for an eight-year extra-growth rate. The elasticity range is assumption sensitivity, not a predictive interval. The current extra-growth ceiling is 17.832570% annually.

Subtracting fermentation from the target is a scope diagnostic, not causal attribution. The proxy's intended aggregate already includes fermentation, but has no separately estimated category-entry term.

## Exact factorization

At midpoint parameter values, the 2022–2030 factors are population 1.069955 × income 1.968639 × urban share 1.072066 × extra growth 1.839483. This gives USD 188.113110 million. It is an illustrative parameter scenario, not the simulated median. Per-draw factors and additive log factors are in factor-draws.csv; neither identifies causal contributions.

The fastest sampled draw grows 33.556509% annually; the analytical upper-bound case grows 33.686486% and reaches USD 462.029988 million. Its failure to reach the conditional GFI low target is a property of the chosen bounds, not validation of either forecast.

## Paired diagnostic cases

Million USD at 2025 prices. P10/P50/P90 describe chosen assumption draws, not calibrated predictive intervals. All cases consume the same four random draws before overrides.

| Case | Country | Year | P10 | P50 | P90 | Median change |
|---|---|---:|---:|---:|---:|---:|
| baseline | India | 2026 | 68.638 | 93.237 | 124.506 | +0.000% |
| baseline | India | 2030 | 101.825 | 187.812 | 334.480 | +0.000% |
| baseline | India | 2035 | 165.637 | 447.504 | 1141.553 | +0.000% |
| baseline | Pakistan | 2026 | 1.472 | 3.645 | 6.617 | +0.000% |
| baseline | Pakistan | 2030 | 2.280 | 5.977 | 13.682 | +0.000% |
| baseline | Pakistan | 2035 | 3.593 | 11.759 | 36.100 | +0.000% |
| drift_floor_zero | India | 2026 | 73.608 | 96.714 | 125.580 | +3.729% |
| drift_floor_zero | India | 2030 | 117.211 | 202.214 | 339.899 | +7.668% |
| drift_floor_zero | India | 2035 | 208.119 | 504.760 | 1174.295 | +12.794% |
| drift_floor_zero | Pakistan | 2026 | 1.545 | 3.808 | 6.777 | +4.488% |
| drift_floor_zero | Pakistan | 2030 | 2.523 | 6.504 | 14.125 | +8.813% |
| drift_floor_zero | Pakistan | 2035 | 4.386 | 13.303 | 37.538 | +13.126% |
| elasticity_grid_00 | India | 2026 | 62.127 | 84.771 | 112.056 | -9.081% |
| elasticity_grid_00 | India | 2030 | 83.810 | 156.034 | 272.643 | -16.920% |
| elasticity_grid_00 | India | 2035 | 121.083 | 332.439 | 823.328 | -25.713% |
| elasticity_grid_00 | Pakistan | 2026 | 1.680 | 4.157 | 7.486 | +14.064% |
| elasticity_grid_00 | Pakistan | 2030 | 2.504 | 6.566 | 14.906 | +9.850% |
| elasticity_grid_00 | Pakistan | 2035 | 3.757 | 12.293 | 37.583 | +4.542% |
| elasticity_grid_01 | India | 2026 | 65.322 | 89.129 | 117.817 | -4.406% |
| elasticity_grid_01 | India | 2030 | 92.407 | 172.041 | 300.612 | -8.397% |
| elasticity_grid_01 | India | 2035 | 141.632 | 388.857 | 963.053 | -13.105% |
| elasticity_grid_01 | Pakistan | 2026 | 1.574 | 3.895 | 7.013 | +6.862% |
| elasticity_grid_01 | Pakistan | 2030 | 2.388 | 6.263 | 14.217 | +4.771% |
| elasticity_grid_01 | Pakistan | 2035 | 3.675 | 12.025 | 36.763 | +2.262% |
| elasticity_grid_02 | India | 2026 | 68.680 | 93.711 | 123.874 | +0.508% |
| elasticity_grid_02 | India | 2030 | 101.887 | 189.689 | 331.451 | +1.000% |
| elasticity_grid_02 | India | 2035 | 165.668 | 454.849 | 1126.492 | +1.641% |
| elasticity_grid_02 | Pakistan | 2026 | 1.475 | 3.649 | 6.570 | +0.114% |
| elasticity_grid_02 | Pakistan | 2030 | 2.278 | 5.973 | 13.560 | -0.072% |
| elasticity_grid_02 | Pakistan | 2035 | 3.595 | 11.763 | 35.961 | +0.032% |
| elasticity_grid_03 | India | 2026 | 72.211 | 98.529 | 130.243 | +5.676% |
| elasticity_grid_03 | India | 2030 | 112.339 | 209.149 | 365.453 | +11.361% |
| elasticity_grid_03 | India | 2035 | 193.784 | 532.041 | 1317.667 | +18.891% |
| elasticity_grid_03 | Pakistan | 2026 | 1.381 | 3.418 | 6.156 | -6.207% |
| elasticity_grid_03 | Pakistan | 2030 | 2.172 | 5.697 | 12.933 | -4.692% |
| elasticity_grid_03 | Pakistan | 2035 | 3.517 | 11.506 | 35.177 | -2.150% |
| elasticity_grid_04 | India | 2026 | 75.924 | 103.595 | 136.939 | +11.109% |
| elasticity_grid_04 | India | 2030 | 123.863 | 230.604 | 402.943 | +22.785% |
| elasticity_grid_04 | India | 2035 | 226.670 | 622.333 | 1541.286 | +39.067% |
| elasticity_grid_04 | Pakistan | 2026 | 1.294 | 3.203 | 5.767 | -12.129% |
| elasticity_grid_04 | Pakistan | 2030 | 2.072 | 5.434 | 12.335 | -9.098% |
| elasticity_grid_04 | Pakistan | 2035 | 3.440 | 11.255 | 34.410 | -4.284% |
| combined_zero_floor_elasticity_1 | India | 2026 | 66.733 | 87.917 | 112.838 | -5.706% |
| combined_zero_floor_elasticity_1 | India | 2030 | 96.695 | 167.830 | 276.461 | -10.639% |
| combined_zero_floor_elasticity_1 | India | 2035 | 152.762 | 374.236 | 842.144 | -16.373% |
| combined_zero_floor_elasticity_1 | Pakistan | 2026 | 1.756 | 4.337 | 7.643 | +18.982% |
| combined_zero_floor_elasticity_1 | Pakistan | 2030 | 2.778 | 7.143 | 15.390 | +19.506% |
| combined_zero_floor_elasticity_1 | Pakistan | 2035 | 4.586 | 13.884 | 39.157 | +18.070% |
| income_drift_overlap | India | 2026 | 64.322 | 74.380 | 85.934 | -20.226% |
| income_drift_overlap | India | 2030 | 89.628 | 119.642 | 159.145 | -36.297% |
| income_drift_overlap | India | 2035 | 134.658 | 215.061 | 341.253 | -51.942% |
| income_drift_overlap | Pakistan | 2026 | 1.207 | 2.967 | 4.991 | -18.606% |
| income_drift_overlap | Pakistan | 2030 | 1.637 | 4.037 | 7.080 | -32.464% |
| income_drift_overlap | Pakistan | 2035 | 2.382 | 5.965 | 11.691 | -49.275% |
| pakistan_no_urban_animal | India | 2026 | 68.638 | 93.237 | 124.506 | +0.000% |
| pakistan_no_urban_animal | India | 2030 | 101.825 | 187.812 | 334.480 | +0.000% |
| pakistan_no_urban_animal | India | 2035 | 165.637 | 447.504 | 1141.553 | +0.000% |
| pakistan_no_urban_animal | Pakistan | 2026 | 1.059 | 2.612 | 4.626 | -28.327% |
| pakistan_no_urban_animal | Pakistan | 2030 | 1.645 | 4.264 | 9.590 | -28.663% |
| pakistan_no_urban_animal | Pakistan | 2035 | 2.576 | 8.318 | 25.341 | -29.262% |
| pakistan_industry_low | India | 2026 | 68.638 | 93.237 | 124.506 | +0.000% |
| pakistan_industry_low | India | 2030 | 101.825 | 187.812 | 334.480 | +0.000% |
| pakistan_industry_low | India | 2035 | 165.637 | 447.504 | 1141.553 | +0.000% |
| pakistan_industry_low | Pakistan | 2026 | 0.700 | 1.001 | 1.413 | -72.544% |
| pakistan_industry_low | Pakistan | 2030 | 0.927 | 1.726 | 3.086 | -71.121% |
| pakistan_industry_low | Pakistan | 2035 | 1.283 | 3.469 | 8.713 | -70.503% |
| pakistan_industry_high | India | 2026 | 68.638 | 93.237 | 124.506 | +0.000% |
| pakistan_industry_high | India | 2030 | 101.825 | 187.812 | 334.480 | +0.000% |
| pakistan_industry_high | India | 2035 | 165.637 | 447.504 | 1141.553 | +0.000% |
| pakistan_industry_high | Pakistan | 2026 | 4.565 | 6.528 | 9.221 | +79.116% |
| pakistan_industry_high | Pakistan | 2030 | 6.046 | 11.261 | 20.132 | +88.398% |
| pakistan_industry_high | Pakistan | 2035 | 8.369 | 22.628 | 56.843 | +92.425% |
| drift_fixed_low | India | 2026 | 58.494 | 63.336 | 68.693 | -32.070% |
| drift_fixed_low | India | 2030 | 74.221 | 86.658 | 101.507 | -53.859% |
| drift_fixed_low | India | 2035 | 99.316 | 127.357 | 164.163 | -71.541% |
| drift_fixed_low | Pakistan | 2026 | 1.033 | 2.521 | 4.220 | -30.820% |
| drift_fixed_low | Pakistan | 2030 | 1.206 | 2.951 | 4.916 | -50.632% |
| drift_fixed_low | Pakistan | 2035 | 1.498 | 3.652 | 6.061 | -68.940% |
| drift_fixed_high | India | 2026 | 122.255 | 132.376 | 143.573 | +41.978% |
| drift_fixed_high | India | 2030 | 324.220 | 378.551 | 443.415 | +101.559% |
| drift_fixed_high | India | 2035 | 1090.264 | 1398.085 | 1802.125 | +212.418% |
| drift_fixed_high | Pakistan | 2026 | 2.160 | 5.270 | 8.820 | +44.590% |
| drift_fixed_high | Pakistan | 2030 | 5.267 | 12.890 | 21.475 | +115.654% |
| drift_fixed_high | Pakistan | 2035 | 16.446 | 40.095 | 66.535 | +240.965% |
| animal_weight_low | India | 2026 | 68.638 | 93.237 | 124.506 | +0.000% |
| animal_weight_low | India | 2030 | 101.825 | 187.812 | 334.480 | +0.000% |
| animal_weight_low | India | 2035 | 165.637 | 447.504 | 1141.553 | +0.000% |
| animal_weight_low | Pakistan | 2026 | 1.174 | 2.895 | 5.126 | -20.565% |
| animal_weight_low | Pakistan | 2030 | 1.829 | 4.739 | 10.658 | -20.723% |
| animal_weight_low | Pakistan | 2035 | 2.871 | 9.273 | 28.251 | -21.141% |
| animal_weight_high | India | 2026 | 68.638 | 93.237 | 124.506 | +0.000% |
| animal_weight_high | India | 2030 | 101.825 | 187.812 | 334.480 | +0.000% |
| animal_weight_high | India | 2035 | 165.637 | 447.504 | 1141.553 | +0.000% |
| animal_weight_high | Pakistan | 2026 | 1.881 | 4.639 | 8.215 | +27.289% |
| animal_weight_high | Pakistan | 2030 | 2.930 | 7.593 | 17.078 | +27.037% |
| animal_weight_high | Pakistan | 2035 | 4.601 | 14.860 | 45.270 | +26.367% |

The zero-floor case rescales the same uniform variate into [0, d_max]; it does not clamp negative baseline draws. It tests only the US-derived drift floor. The separate elasticity grid exposes dependence on the US-derived elasticity ceiling without claiming an empirically estimated local correction. The combined case fixes e=1 and uses the zero floor. The historical US comparison remains descriptive.

The income/drift overlap case narrows the extra-growth ceiling and lowers the India result, widening the GFI difference. Pakistan's omitted urban/animal and fixed industry-factor cases remain transfer diagnostics without a Pakistan sales baseline. Job-board indicators are not measured demand or independently identified effects.

## Reproduction receipt

55 retained reference values agree at their six-decimal output precision. Inputs, category extraction and the 127-row reference file have identical pre/post SHA-256 checksums. No baseline engine or panel file is written.

CSV and JSON values keep 12 significant digits, so outputs match across operating systems; display rounding is only for readability. diagnostics.json contains source checksums, the comparison contract and complete summary values. The full factor table is separate to keep the JSON compact.
