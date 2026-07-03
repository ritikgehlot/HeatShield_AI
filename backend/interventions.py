"""Intervention optimizer and what-if simulator (Phase 6).

Priority ranking is not a second, disconnected heuristic — it reuses the exact
FeatureContribution numbers risk_engine.score_ward already computed for a
ward, so "why this recommendation was selected" can point at the same
normalized-risk figures shown in the ward's explainability panel instead of a
separate, harder-to-justify score. All cost/impact/timeline ranges are
declared assumptions (see CATALOG and docs/MODEL_CARD.md), not measured
figures, and the simulator never promises a single unsupported exact
temperature decrease — it returns ranges plus one clearly-labeled planning
point-estimate for the interactive sliders.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .risk_engine import FeatureContribution, score_ward

# --- Catalog: seeded into intervention_catalog table, also used directly here ---
CATALOG: list[dict[str, Any]] = [
    {
        "key": "cool_roofs",
        "name": "Cool-roof coatings",
        "description": "Reflective/high-albedo coating on schools, clinics, and dense housing roofs.",
        "unit_cost_min_inr_lakh": 8.0, "unit_cost_max_inr_lakh": 18.0,
        "cooling_impact_min_c": 0.5, "cooling_impact_max_c": 1.8,
        "risk_reduction_min_pts": 3.0, "risk_reduction_max_pts": 9.0,
        "timeline_weeks_min": 4, "timeline_weeks_max": 10,
        "assumptions": "Per ~10% of priority-building roof area treated in the ward; based on published cool-roof studies in hot semi-arid climates, not site-measured.",
        "relevance_features": {"built_up_pct": 0.4, "ndbi": 0.35, "lst_c": 0.25},
        "population_coverage_range": (0.25, 0.55),
    },
    {
        "key": "tree_canopy",
        "name": "Tree canopy & green corridors",
        "description": "Native-species street trees, pocket parks, and green corridors linking existing green space.",
        "unit_cost_min_inr_lakh": 3.0, "unit_cost_max_inr_lakh": 9.0,
        "cooling_impact_min_c": 0.3, "cooling_impact_max_c": 1.5,
        "risk_reduction_min_pts": 2.0, "risk_reduction_max_pts": 7.0,
        "timeline_weeks_min": 8, "timeline_weeks_max": 24,
        "assumptions": "Per percentage point of canopy gain; full cooling effect takes multiple growing seasons, not immediate.",
        "relevance_features": {"ndvi": 0.7, "built_up_pct": 0.3},
        "population_coverage_range": (0.4, 0.85),
    },
    {
        "key": "shade_structures",
        "name": "Shade structures",
        "description": "Shaded bus stops, market shade, and walkable heat-safe pedestrian segments.",
        "unit_cost_min_inr_lakh": 0.4, "unit_cost_max_inr_lakh": 1.2,
        "cooling_impact_min_c": 0.1, "cooling_impact_max_c": 0.4,
        "risk_reduction_min_pts": 1.0, "risk_reduction_max_pts": 4.0,
        "timeline_weeks_min": 3, "timeline_weeks_max": 8,
        "assumptions": "Per structure; cooling effect is localized (point-of-use), city-average effect is small per unit.",
        "relevance_features": {"road_density_km_km2": 0.55, "population_density": 0.45},
        "population_coverage_range": (0.1, 0.35),
    },
    {
        "key": "reflective_pavement",
        "name": "Reflective pavements",
        "description": "High-albedo surface treatment on priority road/walkway segments.",
        "unit_cost_min_inr_lakh": 6.0, "unit_cost_max_inr_lakh": 14.0,
        "cooling_impact_min_c": 0.3, "cooling_impact_max_c": 1.0,
        "risk_reduction_min_pts": 2.0, "risk_reduction_max_pts": 5.0,
        "timeline_weeks_min": 6, "timeline_weeks_max": 14,
        "assumptions": "Per km of priority road treated; ambient (not surface) cooling effect is the smaller, cited figure.",
        "relevance_features": {"road_density_km_km2": 0.5, "built_up_pct": 0.5},
        "population_coverage_range": (0.2, 0.5),
    },
    {
        "key": "cooling_points",
        "name": "Water & cooling points",
        "description": "Drinking-water points, misting stations, and shaded rest kiosks for heat-exposed residents.",
        "unit_cost_min_inr_lakh": 1.0, "unit_cost_max_inr_lakh": 3.0,
        "cooling_impact_min_c": 0.0, "cooling_impact_max_c": 0.2,
        "risk_reduction_min_pts": 1.0, "risk_reduction_max_pts": 3.0,
        "timeline_weeks_min": 2, "timeline_weeks_max": 6,
        "assumptions": "Primarily reduces heat-health vulnerability, not ambient temperature; risk reduction reflects that.",
        "relevance_features": {"vulnerability_index": 0.7, "population_density": 0.3},
        "population_coverage_range": (0.15, 0.4),
    },
    {
        "key": "vulnerable_zone_alerts",
        "name": "Schools/hospitals/vulnerable-zone heat alerts",
        "description": "Heat-health early-warning signage and outreach targeted at schools, clinics, and elder-care sites.",
        "unit_cost_min_inr_lakh": 0.5, "unit_cost_max_inr_lakh": 2.0,
        "cooling_impact_min_c": 0.0, "cooling_impact_max_c": 0.0,
        "risk_reduction_min_pts": 1.0, "risk_reduction_max_pts": 3.0,
        "timeline_weeks_min": 2, "timeline_weeks_max": 4,
        "assumptions": "Does not lower temperature; reduces harm through earlier warning and behavior change for vulnerable groups.",
        "relevance_features": {"vulnerability_index": 1.0},
        "population_coverage_range": (0.05, 0.2),
    },
]
CATALOG_BY_KEY = {item["key"]: item for item in CATALOG}


@dataclass
class InterventionRecommendation:
    key: str
    name: str
    priority_rank: int
    risk_reduction_range: tuple[float, float]
    cooling_impact_range_c: tuple[float, float]
    cost_range_inr_lakh: tuple[float, float]
    timeline_weeks: tuple[int, int]
    population_affected_range: tuple[int, int]
    confidence: str
    assumptions: str
    why_selected: str


def _relevance(contributions_by_key: dict[str, FeatureContribution], weights: dict[str, float]) -> float:
    total_weight = sum(weights.values()) or 1.0
    score = 0.0
    for feature_key, weight in weights.items():
        contribution = contributions_by_key.get(feature_key)
        normalized_risk = contribution.normalized_risk if contribution and contribution.normalized_risk is not None else 0.3
        score += (normalized_risk) * (weight / total_weight)
    return round(score, 3)


def rank_interventions(features: dict[str, Any], population: Optional[int] = None) -> list[InterventionRecommendation]:
    result = score_ward(features)
    contributions_by_key = {c.key: c for c in result.all_factors}

    scored: list[tuple[float, dict]] = []
    for entry in CATALOG:
        relevance = _relevance(contributions_by_key, entry["relevance_features"])
        scored.append((relevance, entry))
    scored.sort(key=lambda pair: pair[0], reverse=True)

    recommendations: list[InterventionRecommendation] = []
    pop = population or 15000  # reasonable ward-scale default when unknown, clearly not precise
    for rank, (relevance, entry) in enumerate(scored, start=1):
        scale_low = 0.4 + 0.6 * relevance
        scale_high = 0.6 + 0.9 * relevance
        risk_lo = round(entry["risk_reduction_min_pts"] * scale_low, 1)
        risk_hi = round(entry["risk_reduction_max_pts"] * scale_high, 1)
        cov_lo, cov_hi = entry["population_coverage_range"]
        pop_lo, pop_hi = int(pop * cov_lo * relevance_floor(relevance)), int(pop * cov_hi)

        drivers = sorted(
            entry["relevance_features"].items(), key=lambda kv: (contributions_by_key.get(kv[0]).normalized_risk or 0) * kv[1], reverse=True
        )
        top_driver_key = drivers[0][0] if drivers else None
        driver_label = contributions_by_key[top_driver_key].label if top_driver_key in contributions_by_key else "ward conditions"

        confidence = "High" if relevance >= 0.6 else "Moderate" if relevance >= 0.35 else "Low"
        why = (
            f"Ranked #{rank} because {driver_label.lower()} is a significant contributor to this ward's risk "
            f"score (relevance {relevance:.0%}); this intervention type most directly addresses that driver."
        )

        recommendations.append(
            InterventionRecommendation(
                key=entry["key"],
                name=entry["name"],
                priority_rank=rank,
                risk_reduction_range=(risk_lo, risk_hi),
                cooling_impact_range_c=(entry["cooling_impact_min_c"], entry["cooling_impact_max_c"]),
                cost_range_inr_lakh=(entry["unit_cost_min_inr_lakh"], entry["unit_cost_max_inr_lakh"]),
                timeline_weeks=(entry["timeline_weeks_min"], entry["timeline_weeks_max"]),
                population_affected_range=(pop_lo, pop_hi),
                confidence=confidence,
                assumptions=entry["assumptions"],
                why_selected=why,
            )
        )
    return recommendations


def relevance_floor(relevance: float) -> float:
    return max(0.3, relevance)


@dataclass
class SimulationOutcome:
    baseline_score: float
    baseline_category: str
    projected_score: float
    projected_category: str
    risk_reduction_pts: float
    risk_reduction_range_pts: tuple[float, float]
    projected_lst_c: float
    allocations: list[dict[str, Any]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)


def simulate_scenario(
    features: dict[str, Any],
    budget_inr_lakh: float,
    roof_treatment_pct: float,
    tree_canopy_target_pct: float,
    shade_structures: int,
    infra_focus: str = "mixed",
) -> SimulationOutcome:
    """Transparent, conservative what-if estimate. Returns both a single
    planning point-estimate (for interactive sliders) and a wider range (for
    the "don't over-promise" requirement) — never just one exact number
    framed as certain.
    """
    baseline = score_ward(features)
    adjusted = dict(features)

    roof_treatment_pct = max(0.0, min(100.0, roof_treatment_pct))
    tree_canopy_target_pct = max(0.0, min(30.0, tree_canopy_target_pct))
    shade_structures = max(0, min(200, shade_structures))

    roof_temp_reduction = min(roof_treatment_pct, 75) * 0.035
    tree_temp_reduction = min(tree_canopy_target_pct, 20) * 0.14
    shade_temp_reduction = min(shade_structures, 50) * 0.02
    total_temp_reduction = min(roof_temp_reduction + tree_temp_reduction + shade_temp_reduction, 5.5)

    if adjusted.get("lst_c") is not None:
        adjusted["lst_c"] = max(25.0, float(adjusted["lst_c"]) - total_temp_reduction)
    if adjusted.get("ndvi") is not None:
        adjusted["ndvi"] = min(0.90, float(adjusted["ndvi"]) + tree_canopy_target_pct * 0.012)
    if adjusted.get("built_up_pct") is not None:
        adjusted["built_up_pct"] = max(0.0, float(adjusted["built_up_pct"]) - roof_treatment_pct * 0.05)
    if adjusted.get("vulnerability_index") is not None:
        adjusted["vulnerability_index"] = max(0.05, float(adjusted["vulnerability_index"]) - shade_structures * 0.002)

    projected = score_ward(adjusted)
    reduction = round(max(0.0, baseline.score - projected.score), 1)
    # Uncertainty band: +/-30% around the point estimate, floored at 0.
    reduction_range = (round(max(0.0, reduction * 0.7), 1), round(reduction * 1.3, 1))

    allocations = []
    remaining_budget = budget_inr_lakh
    for key, pct_or_count, label in [
        ("cool_roofs", roof_treatment_pct, f"Cool roofs: {roof_treatment_pct:.0f}% priority-roof coverage"),
        ("tree_canopy", tree_canopy_target_pct, f"Tree canopy: +{tree_canopy_target_pct:.0f}% green-cover target"),
        ("shade_structures", shade_structures, f"Shade assets: {shade_structures} bus-stop / walkway units"),
    ]:
        if pct_or_count <= 0:
            continue
        catalog_entry = CATALOG_BY_KEY[key]
        mid_unit_cost = (catalog_entry["unit_cost_min_inr_lakh"] + catalog_entry["unit_cost_max_inr_lakh"]) / 2
        scale = pct_or_count / 100 if key != "shade_structures" else pct_or_count / 20
        estimated_cost = round(mid_unit_cost * max(0.3, scale), 1)
        allocations.append({"key": key, "label": label, "estimated_cost_inr_lakh": min(estimated_cost, max(remaining_budget, 0))})
        remaining_budget = max(0.0, remaining_budget - estimated_cost)

    assumptions = [
        "Temperature and score reductions are a transparent planning comparison, not a physical/CFD simulation.",
        "Cost estimates use catalog midpoints scaled by intervention intensity — get local quotes before budgeting.",
        f"Total budget available: ₹{budget_inr_lakh:.1f} lakh; allocations above are indicative, not a procurement plan.",
        "Tree canopy benefits accrue over multiple growing seasons, not immediately upon planting.",
    ]
    if not allocations:
        assumptions.insert(0, "No interventions selected — showing baseline only.")

    return SimulationOutcome(
        baseline_score=baseline.score,
        baseline_category=baseline.category,
        projected_score=projected.score,
        projected_category=projected.category,
        risk_reduction_pts=reduction,
        risk_reduction_range_pts=reduction_range,
        projected_lst_c=round(float(adjusted.get("lst_c", features.get("lst_c", 0)) or 0), 1),
        allocations=allocations,
        assumptions=assumptions,
    )
