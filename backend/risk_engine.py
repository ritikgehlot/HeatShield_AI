"""Explainable heat-risk scoring.

V1 of this file trained a RandomForestRegressor at every process startup on
3,500 synthetic rows generated from a hand-written linear formula — a
black-box wrapper around a formula, mis-calibrated (11/12 demo wards landed
"High" risk or above). V2 replaces it with the formula directly: a documented,
weighted min-max-normalized hybrid score. This is what Phase 5 asks for
("do not train fake ML on tiny/demo data... use a transparent hybrid scoring
formula") and it has a real, useful property: because the score is a weighted
sum, each feature's contribution to the final number is exact, not an
approximation — there's no need for SHAP or any post-hoc explainer, because
for a linear/additive model the exact Shapley attribution of a feature IS its
weighted term. See docs/MODEL_CARD.md for the full rationale, bounds, and
limitations.

Random Forest / XGBoost loading is still supported (`load_trained_model`)
for the day a validated, sufficiently large labelled dataset exists — but
nothing in this file trains one on fake data to look more sophisticated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# --- Feature bounds used for min-max normalization -------------------------
# Chosen from plausible ranges for hot semi-arid Indian cities (Jodhpur-like
# climate). These are documented assumptions, not measured constants — see
# docs/MODEL_CARD.md "Assumptions".
BOUNDS = {
    "lst_c": (25.0, 56.0),               # land surface temperature, degC
    "air_temp_c": (20.0, 48.0),          # ambient air temperature, degC
    "heat_index_c": (20.0, 55.0),        # apparent temperature, degC
    "ndvi": (0.0, 0.65),                 # inverted: low NDVI -> high risk
    "ndbi": (0.0, 1.0),
    "built_up_pct": (0.0, 100.0),
    "road_density_km_km2": (0.0, 12.0),
    "population_density": (0.0, 32000.0),
    "vulnerability_index": (0.0, 1.0),
}

# Weights must sum to 1.0 across the full feature set; renormalized among
# whichever features are actually present for a given ward (see `_score`).
WEIGHTS = {
    "lst_c": 0.22,
    "air_temp_c": 0.08,
    "heat_index_c": 0.05,
    "ndvi": 0.15,
    "ndbi": 0.10,
    "built_up_pct": 0.10,
    "road_density_km_km2": 0.08,
    "population_density": 0.07,
    "vulnerability_index": 0.15,
}

FEATURE_LABELS = {
    "lst_c": "Land surface temperature",
    "air_temp_c": "Air temperature",
    "heat_index_c": "Apparent temperature (heat index)",
    "ndvi": "Low green cover (NDVI)",
    "ndbi": "Built-up index (NDBI)",
    "built_up_pct": "Built-up area share",
    "road_density_km_km2": "Road density",
    "population_density": "Population density",
    "vulnerability_index": "Population vulnerability",
}

CATEGORY_THRESHOLDS = [
    (80, "Extreme"),
    (60, "Severe"),
    (40, "High"),
    (20, "Moderate"),
    (0, "Low"),
]


@dataclass
class FeatureContribution:
    key: str
    label: str
    value: Optional[float]
    normalized_risk: Optional[float]  # 0-1, None if missing
    weight: float
    contribution_pts: float  # exact contribution to the 0-100 score


@dataclass
class RiskResult:
    score: float
    category: str
    confidence: float
    top_factors: list[FeatureContribution] = field(default_factory=list)
    all_factors: list[FeatureContribution] = field(default_factory=list)
    missing_data_warnings: list[str] = field(default_factory=list)
    explanation: str = ""
    model_version: str = "hybrid-v2"

    def top_factor_labels(self) -> list[str]:
        return [f.label for f in self.top_factors]


def estimate_heat_index_c(air_temp_c: float, humidity_pct: float) -> float:
    """NWS/Rothfusz regression approximation of apparent temperature.

    Valid roughly above 27 degC and 40% relative humidity; outside that range
    the heat index converges to air temperature, which is what this returns.
    """
    if air_temp_c < 27 or humidity_pct < 40:
        return air_temp_c
    t = air_temp_c * 9 / 5 + 32
    r = humidity_pct
    hi_f = (
        -42.379 + 2.04901523 * t + 10.14333127 * r - 0.22475541 * t * r
        - 0.00683783 * t * t - 0.05481717 * r * r + 0.00122874 * t * t * r
        + 0.00085282 * t * r * r - 0.00000199 * t * t * r * r
    )
    return round((hi_f - 32) * 5 / 9, 1)


def _normalize(key: str, value: float) -> float:
    lo, hi = BOUNDS[key]
    clipped = max(lo, min(hi, value))
    normalized = (clipped - lo) / (hi - lo) if hi > lo else 0.0
    if key == "ndvi":
        normalized = 1.0 - normalized  # low vegetation -> high risk
    return round(normalized, 4)


def _category(score: float) -> str:
    for threshold, label in CATEGORY_THRESHOLDS:
        if score >= threshold:
            return label
    return "Low"


def _freshness_factor(observed_at: Optional[datetime]) -> float:
    if observed_at is None:
        return 0.6  # unknown age -> moderate penalty, not zero
    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - observed_at).total_seconds() / 86400
    if age_days <= 14:
        return 1.0
    if age_days <= 60:
        return 0.8
    if age_days <= 180:
        return 0.6
    return 0.4


def score_ward(features: dict[str, Any], observed_at: Optional[datetime] = None) -> RiskResult:
    """Computes the 0-100 heat risk score from whatever features are present.

    Missing features are excluded and their weight is redistributed among the
    features that ARE present (not silently treated as zero-risk), and every
    exclusion is recorded as a missing-data warning. Confidence blends data
    completeness with data freshness.
    """
    # Derive heat_index_c if we have the ingredients and it wasn't supplied directly.
    working = dict(features)
    if working.get("heat_index_c") is None and working.get("air_temp_c") is not None and working.get("humidity_pct") is not None:
        working["heat_index_c"] = estimate_heat_index_c(float(working["air_temp_c"]), float(working["humidity_pct"]))

    present_keys = [k for k in WEIGHTS if working.get(k) is not None]
    missing_keys = [k for k in WEIGHTS if k not in present_keys]
    weight_sum = sum(WEIGHTS[k] for k in present_keys) or 1.0

    contributions: list[FeatureContribution] = []
    score = 0.0
    for key in WEIGHTS:
        raw_value = working.get(key)
        if raw_value is None:
            contributions.append(FeatureContribution(key, FEATURE_LABELS[key], None, None, WEIGHTS[key], 0.0))
            continue
        normalized_weight = WEIGHTS[key] / weight_sum
        normalized_risk = _normalize(key, float(raw_value))
        contribution_pts = round(normalized_risk * normalized_weight * 100, 2)
        score += contribution_pts
        contributions.append(
            FeatureContribution(key, FEATURE_LABELS[key], float(raw_value), normalized_risk, WEIGHTS[key], contribution_pts)
        )

    score = round(min(100.0, max(0.0, score)), 1)
    category = _category(score)

    completeness = len(present_keys) / len(WEIGHTS)
    freshness = _freshness_factor(observed_at)
    confidence = round(max(0.15, min(0.95, 0.5 * completeness + 0.5 * freshness)), 2)

    warnings = [
        f"{FEATURE_LABELS[k]} not available — excluded from score, weight redistributed"
        for k in missing_keys
    ]
    if observed_at is None:
        warnings.append("No observation timestamp available — freshness assumed moderate")

    ranked = sorted((c for c in contributions if c.value is not None), key=lambda c: c.contribution_pts, reverse=True)
    top = ranked[:3]

    explanation = _build_explanation(category, score, top, warnings, confidence)

    return RiskResult(
        score=score,
        category=category,
        confidence=confidence,
        top_factors=top,
        all_factors=contributions,
        missing_data_warnings=warnings,
        explanation=explanation,
    )


def _build_explanation(category: str, score: float, top: list[FeatureContribution], warnings: list[str], confidence: float) -> str:
    if not top:
        return "Not enough data was available to explain this score."
    driver_text = "; ".join(f"{f.label.lower()} ({f.value:.1f})" if f.value is not None else f.label for f in top)
    base = (
        f"This ward is rated {category} ({score:.0f}/100). The biggest contributors are "
        f"{driver_text}. This is a decision-support estimate, not a validated physical "
        f"measurement — confirm with local observations before acting on it."
    )
    if confidence < 0.5:
        base += f" Confidence is low ({confidence:.0%}) because some inputs are missing or outdated."
    if warnings:
        base += f" {len(warnings)} data quality note(s) apply — see missing_data_warnings."
    return base


def derive_recommendations(features: dict[str, Any]) -> list[str]:
    """Short driver-based recommendation strings for the ward detail summary.

    The fuller ranked/costed intervention optimizer lives in interventions.py —
    this stays intentionally lightweight for places that just need 2-3 lines.
    """
    actions: list[str] = []
    built_up_pct = features.get("built_up_pct")
    lst_c = features.get("lst_c")
    ndvi = features.get("ndvi")
    road_density = features.get("road_density_km_km2")
    vulnerability = features.get("vulnerability_index")

    if (built_up_pct is not None and built_up_pct >= 55) or (lst_c is not None and lst_c >= 46):
        actions.append("Prioritise cool-roof coating on schools, clinics and dense housing")
    if ndvi is not None and ndvi < 0.30:
        actions.append("Create shaded green corridors and native-tree micro-forests")
    if road_density is not None and road_density >= 5:
        actions.append("Install shaded bus stops and heat-safe pedestrian segments")
    if vulnerability is not None and vulnerability >= 0.55:
        actions.append("Place drinking-water and heat-alert points for vulnerable residents")
    if not actions:
        actions.append("Maintain tree canopy and monitor the ward through the heat season")
    return actions[:3]


# --- Optional path for a real, validated model ------------------------------
def load_trained_model(model_path: str | Path):
    """Loads a validated Random Forest / XGBoost model from disk, IF one exists.

    Intentionally does not train anything here. This is only wired up when a
    real, validated model file trained on real labelled data is provided —
    see docs/MODEL_CARD.md "Validation strategy" for what "validated" means.
    """
    path = Path(model_path)
    if not path.exists():
        return None
    import joblib  # local import: optional dependency, only needed on this path

    return joblib.load(path)
