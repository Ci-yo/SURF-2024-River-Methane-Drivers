# Methodology

## Public analysis boundary

The working folder contained large seasonal exports, generated bookdown files, repeated RDS objects and draft reports. This repository keeps the smallest coherent layer needed to inspect the research question: one matched CSV, one clean R analysis, a standard-library audit and generated visuals.

## Screening

1. Preserve all 1,113 rows in `data/grime_curated.csv`.
2. For log-flux summaries, retain finite positive diffusive CH₄ fluxes.
3. Use the 5th and 95th percentiles as a sensitivity window rather than deleting source rows.
4. Apply `log1p` to non-negative skewed catchment variables.

## Models

- **Geography:** log flux ~ latitude + longitude + log elevation.
- **River network:** log flux ~ log slope + Strahler order + log basin size.

Models use complete cases independently, so sample sizes differ. Diagnostics and coefficients are written to CSV rather than rounded into the README.

## Interpretation guardrails

- Pairwise correlations are descriptive.
- Linear-model coefficients are conditional associations.
- Missingness is substantial for slope, Strahler order and channel type.
- Measurements combine methods, regions and sampling periods.
- Spatial dependence and study-level clustering are not modelled in this compact public layer.

These limitations make the repository an auditable project showcase, not a replacement for the upstream global analysis.
