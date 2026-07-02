"""Heat-risk scoring and what-if simulation logic.

The included model is a reproducible hackathon prototype. It trains on synthetic,
physically plausible feature combinations so that the app works on first run.
Replace it with validated city observations before operational use.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestRegressor

FEATURES = [
    "lst_c",
    "ndvi",
    "ndbi",
    "built_up_pct",
    "road_density_km_km2",
    "population_density",
    "vulnerability_index",
]


@dataclass
class RiskResult:
    score: float
    risk_level: str
    top_drivers: list[str]


def _synthetic_training_data(rows: int = 3500) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    lst = rng.uniform(36, 56, rows)
    ndvi = rng.uniform(0.03, 0.72, rows)
    ndbi = rng.uniform(0.05, 0.92, rows)
    built = rng.uniform(15, 96, rows)
    road = rng.uniform(0.4, 14, rows)
    pop = rng.uniform(700, 32000, rows)
    vulnerability = rng.uniform(0.05, 0.95, rows)

    # Prototype target: combines exposure, sensitivity and urban form.
    raw = (
        1.65 * (lst - 36)
        + 28 * (1 - ndvi)
        + 17 * ndbi
        + 0.20 * built
        + 0.9 * road
        + 0.00052 * pop
        + 13 * vulnerability
        + rng.normal(0, 2.3, rows)
    )
    y = np.clip(raw, 0, 100)
    x = np.column_stack([lst, ndvi, ndbi, built, road, pop, vulnerability])
    return x, y


@lru_cache(maxsize=1)
def get_model() -> RandomForestRegressor:
    x, y = _synthetic_training_data()
    model = RandomForestRegressor(
        n_estimators=180,
        max_depth=13,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x, y)
    return model


def risk_level(score: float) -> str:
    if score >= 78:
        return "Extreme"
    if score >= 60:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def _number(value: Any) -> float:
    return float(value)


def predict_risk(features: dict[str, Any]) -> RiskResult:
    values = np.array([[_number(features[column]) for column in FEATURES]])
    score = float(np.clip(get_model().predict(values)[0], 0, 100))
    return RiskResult(
        score=round(score, 1),
        risk_level=risk_level(score),
        top_drivers=derive_top_drivers(features),
    )


def derive_top_drivers(features: dict[str, Any]) -> list[str]:
    candidates = [
        (float(features["lst_c"]) / 56, f"High surface temperature ({float(features['lst_c']):.1f}°C)"),
        ((1 - float(features["ndvi"])), f"Low green cover (NDVI {float(features['ndvi']):.2f})"),
        (float(features["built_up_pct"]) / 100, f"Dense built-up area ({float(features['built_up_pct']):.0f}%)"),
        (float(features["road_density_km_km2"]) / 14, f"High road density ({float(features['road_density_km_km2']):.1f} km/km²)"),
        (float(features["vulnerability_index"]), "High population vulnerability"),
    ]
    candidates.sort(reverse=True, key=lambda item: item[0])
    return [item[1] for item in candidates[:3]]


def recommendations(features: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if float(features["built_up_pct"]) >= 55 or float(features["lst_c"]) >= 46:
        actions.append("Prioritise cool-roof coating on schools, clinics and dense housing")
    if float(features["ndvi"]) < 0.30:
        actions.append("Create shaded green corridor and native-tree micro-forests")
    if float(features["road_density_km_km2"]) >= 5:
        actions.append("Install shaded bus stops and heat-safe pedestrian segments")
    if float(features["vulnerability_index"]) >= 0.55:
        actions.append("Place drinking-water and heat-alert points for vulnerable residents")
    if not actions:
        actions.append("Maintain tree canopy and monitor the ward through the heat season")
    return actions[:3]


def simulate(features: dict[str, Any], cool_roof_coverage: float, tree_cover_gain: float, shade_units: int) -> dict[str, Any]:
    """Estimate comparative scenario benefit; not a physical forecast."""
    baseline = predict_risk(features)
    adjusted = dict(features)

    # Conservative, transparent reductions for a planning comparison.
    roof_temp_reduction = min(cool_roof_coverage, 75) * 0.035
    tree_temp_reduction = min(tree_cover_gain, 20) * 0.14
    shade_temp_reduction = min(shade_units, 50) * 0.025
    total_temp_reduction = min(roof_temp_reduction + tree_temp_reduction + shade_temp_reduction, 5.2)

    adjusted["lst_c"] = max(25, float(features["lst_c"]) - total_temp_reduction)
    adjusted["ndvi"] = min(0.90, float(features["ndvi"]) + tree_cover_gain * 0.012)
    adjusted["built_up_pct"] = max(0, float(features["built_up_pct"]) - cool_roof_coverage * 0.08)
    adjusted["vulnerability_index"] = max(0.05, float(features["vulnerability_index"]) - shade_units * 0.003)

    projected = predict_risk(adjusted)
    reduction = max(0.0, baseline.score - projected.score)

    interventions = []
    if cool_roof_coverage:
        interventions.append(f"Cool roofs: {cool_roof_coverage:.0f}% priority-roof coverage")
    if tree_cover_gain:
        interventions.append(f"Tree canopy: +{tree_cover_gain:.0f}% green-cover target")
    if shade_units:
        interventions.append(f"Shade assets: {shade_units} bus-stop / walkway units")

    return {
        "baseline": baseline,
        "projected": projected,
        "risk_reduction": round(reduction, 1),
        "projected_lst_c": round(float(adjusted["lst_c"]), 1),
        "intervention_summary": interventions or ["No intervention selected"],
    }
