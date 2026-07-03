# Model Card — HeatShield AI Heat Risk Engine

**Model version:** `hybrid-v2`
**Type:** Transparent weighted additive formula (not a trained black-box model)
**Purpose:** Decision support for prioritising urban heat interventions at ward level.

## What changed from V1, and why

The original prototype trained a `RandomForestRegressor` at every startup on
3,500 synthetic rows that were themselves generated from a hand-written linear
formula. That is a black box wrapping a formula: it added opacity and
mis-calibration (in the seeded demo, 11 of 12 wards scored "High" or above, one
at 99.9/100) without adding any real learning. It also conflicts with the
principle "do not train fake ML on tiny/demo data."

V2 uses the formula directly. Because the score is a weighted sum of normalized
features, each feature's contribution to the final number is **exact** — for an
additive model the exact per-feature attribution *is* the Shapley value, so no
SHAP approximation is needed. What the UI shows as "why this score" is literally
the arithmetic, not a post-hoc guess at it.

## Input features (9)

| Feature | Weight | Normalization range | Direction |
|---|---|---|---|
| Land surface temperature (°C) | 0.22 | 25–56 | higher = riskier |
| Low green cover (NDVI) | 0.15 | 0–0.65 | **inverted**: lower NDVI = riskier |
| Population vulnerability (0–1) | 0.15 | 0–1 | higher = riskier |
| Built-up index (NDBI) | 0.10 | 0–1 | higher = riskier |
| Built-up area share (%) | 0.10 | 0–100 | higher = riskier |
| Air temperature (°C) | 0.08 | 20–48 | higher = riskier |
| Road density (km/km²) | 0.08 | 0–12 | higher = riskier |
| Population density (/km²) | 0.07 | 0–32,000 | higher = riskier |
| Apparent temperature / heat index (°C) | 0.05 | 20–55 | higher = riskier |

Weights sum to 1.0. Apparent temperature is derived from air temperature and
humidity via the NWS Rothfusz regression when not supplied directly.

## Formula

For each present feature: `normalized_risk = clip((value − lo) / (hi − lo), 0, 1)`
(inverted for NDVI). Missing features are excluded and their weight redistributed
proportionally among present features — never treated as zero-risk. The score is
`100 × Σ(normalized_risk × renormalized_weight)`, clipped to 0–100.

**Categories:** Low (0–19), Moderate (20–39), High (40–59), Severe (60–79),
Extreme (80–100).

**Confidence** blends data completeness (how many of the 9 features are present)
with data freshness (age of the observation): `0.5 × completeness + 0.5 × freshness`,
clamped to 0.15–0.95.

## Assumptions

- Normalization ranges are chosen for hot semi-arid Indian cities (Jodhpur-like).
  They are documented judgment, not locally-calibrated constants.
- Feature weights encode relative importance based on urban-heat literature and
  domain reasoning, **not** regression against local heat-morbidity outcomes.
- Equal 0.5/0.5 weighting of completeness and freshness in confidence is a
  deliberate simple default, not an optimized value.

## Limitations

- The model is **not validated against health or mortality outcomes.** It ranks
  relative risk; it does not predict absolute harm.
- Demo/seeded feature values are illustrative, not measured.
- It cannot capture micro-scale effects (single-building shade, street-canyon
  geometry, local water bodies) below ward resolution.

## Validation strategy (for the optional trained-model path)

`risk_engine.load_trained_model()` supports loading a real RandomForest/XGBoost
model **only** when one exists. "Validated" here means: trained on real labelled
data (e.g. ward-level heat-morbidity or validated LST-mortality associations),
evaluated with spatial cross-validation (hold out whole wards/cities, not random
rows, to avoid spatial leakage), and reporting calibration — not just R². Until
that exists, the transparent formula is the honest choice.

## Ethical warnings

- **Outputs are decision support, not decisions.** They inform human municipal
  judgment; they must not be used to automatically allocate or deny resources.
- Vulnerability weighting means denser, poorer wards will often rank higher —
  this is intended (they face greater heat harm) but must not become a pretext
  for surveillance or punitive action toward those communities.
- Every value in the product carries source, timestamp, freshness, and
  confidence precisely so that no one mistakes an estimate for ground truth.
