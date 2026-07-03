"""Intervention optimisation engine for HeatShield AI.

Provides a catalog of evidence-based cooling interventions and a what-if
simulator.  All cost estimates are in INR (lakhs) and all temperature
reductions are expressed as conservative ranges with explicit assumptions.

Intervention types:
  cool_roofs, tree_canopy, shade_structures, reflective_pavements,
  water_points, priority_alerts

Every result includes:
  estimated_cooling_range, cost_range, timeline, priority,
  assumptions, confidence, affected_population

No scientifically unsupported exact temperature promises are made.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ── Intervention definitions ─────────────────────────────────────────────

@dataclass
class InterventionSpec:
    """Specification for a single intervention type."""
    name: str
    category: str
    description: str
    cooling_min_c: float  # Conservative minimum cooling (°C)
    cooling_max_c: float  # Optimistic maximum cooling (°C)
    cost_per_unit_min_lakh: float
    cost_per_unit_max_lakh: float
    unit: str
    timeline_months: int
    evidence_source: str
    assumptions: str
    # How this intervention affects risk model features
    lst_reduction_per_pct: float  # °C reduction per 1% coverage
    ndvi_gain_per_pct: float
    built_up_reduction_per_pct: float
    vuln_reduction_per_unit: float


INTERVENTION_CATALOG: dict[str, InterventionSpec] = {
    "cool_roofs": InterventionSpec(
        name="Cool Roof Coatings",
        category="Building envelope",
        description=(
            "High-albedo roof coatings that reflect solar radiation, reducing "
            "indoor and ambient temperatures.  Prioritise schools, clinics, and "
            "dense residential areas."
        ),
        cooling_min_c=0.5,
        cooling_max_c=3.0,
        cost_per_unit_min_lakh=0.3,
        cost_per_unit_max_lakh=1.2,
        unit="1000 sqm roofing",
        timeline_months=3,
        evidence_source=(
            "Akbari et al. (2009) Global Cooling; TERI India cool-roof pilots; "
            "GBPN Urban Heat Island review"
        ),
        assumptions=(
            "Assumes 0.6+ solar reflectance coating on flat concrete roofs. "
            "Actual cooling depends on roof material, building density, and "
            "maintenance.  Range represents 1-year field measurements from "
            "Indian pilot cities."
        ),
        lst_reduction_per_pct=0.035,
        ndvi_gain_per_pct=0.0,
        built_up_reduction_per_pct=0.08,
        vuln_reduction_per_unit=0.0,
    ),
    "tree_canopy": InterventionSpec(
        name="Urban Tree Canopy Expansion",
        category="Green infrastructure",
        description=(
            "Planting native drought-resistant trees (Neem, Sheesham, Babool) "
            "along streets, parks, and community spaces to increase shade and "
            "evapotranspiration."
        ),
        cooling_min_c=0.5,
        cooling_max_c=4.0,
        cost_per_unit_min_lakh=0.5,
        cost_per_unit_max_lakh=2.5,
        unit="1% canopy cover gain",
        timeline_months=24,
        evidence_source=(
            "Bowler et al. (2010) Urban greening meta-analysis; "
            "CEPT Ahmedabad tree-cover study; India UFSI guidelines"
        ),
        assumptions=(
            "Assumes native species suited to Thar Desert climate with "
            "drip irrigation for first 2 years.  Cooling effect matures "
            "over 3–5 years.  Range covers 1-year to 5-year projections."
        ),
        lst_reduction_per_pct=0.14,
        ndvi_gain_per_pct=0.012,
        built_up_reduction_per_pct=0.0,
        vuln_reduction_per_unit=0.0,
    ),
    "shade_structures": InterventionSpec(
        name="Shade Structures & Cool Corridors",
        category="Public infrastructure",
        description=(
            "Tensile fabric shades, pergolas, and covered walkways at bus stops, "
            "markets, and pedestrian zones to reduce direct solar exposure."
        ),
        cooling_min_c=0.3,
        cooling_max_c=2.0,
        cost_per_unit_min_lakh=0.8,
        cost_per_unit_max_lakh=3.0,
        unit="shade unit (bus stop / 50m corridor)",
        timeline_months=6,
        evidence_source=(
            "Middel & Krayenhoff (2019) shade and MRT review; "
            "NIUA India Smart Cities shade guidelines"
        ),
        assumptions=(
            "Each shade unit covers ~200 sqm of public space.  Ambient "
            "temperature reduction is localised (10–50m radius).  Cost "
            "includes foundation and 3-year maintenance."
        ),
        lst_reduction_per_pct=0.025,
        ndvi_gain_per_pct=0.0,
        built_up_reduction_per_pct=0.0,
        vuln_reduction_per_unit=0.003,
    ),
    "reflective_pavements": InterventionSpec(
        name="Reflective / Cool Pavements",
        category="Road infrastructure",
        description=(
            "High-albedo or permeable pavement coatings on roads and public "
            "plazas to reduce heat absorption from asphalt."
        ),
        cooling_min_c=0.2,
        cooling_max_c=1.5,
        cost_per_unit_min_lakh=1.0,
        cost_per_unit_max_lakh=4.0,
        unit="1 km road surface",
        timeline_months=6,
        evidence_source=(
            "Santamouris (2013) cool pavement review; "
            "US EPA cool pavement compendium"
        ),
        assumptions=(
            "Assumes standard 7m-wide urban road.  Effectiveness varies with "
            "traffic volume and maintenance.  Higher end assumes permeable "
            "pavement with drainage layer."
        ),
        lst_reduction_per_pct=0.02,
        ndvi_gain_per_pct=0.0,
        built_up_reduction_per_pct=0.05,
        vuln_reduction_per_unit=0.0,
    ),
    "water_points": InterventionSpec(
        name="Public Drinking Water & Mist Points",
        category="Public health",
        description=(
            "Filtered drinking-water stations and mist sprayers at high-footfall "
            "public locations for immediate relief during heat waves."
        ),
        cooling_min_c=0.0,
        cooling_max_c=0.5,
        cost_per_unit_min_lakh=0.2,
        cost_per_unit_max_lakh=0.8,
        unit="water / mist station",
        timeline_months=2,
        evidence_source=(
            "WHO Heat–Health Action Plans; "
            "NDMA India Heat Action Plan guidelines"
        ),
        assumptions=(
            "Ambient temperature effect is negligible beyond 10m radius. "
            "Primary benefit is reducing heat-stroke incidence through "
            "hydration access, not urban cooling."
        ),
        lst_reduction_per_pct=0.0,
        ndvi_gain_per_pct=0.0,
        built_up_reduction_per_pct=0.0,
        vuln_reduction_per_unit=0.005,
    ),
    "priority_alerts": InterventionSpec(
        name="Heat-Wave Early Warning System",
        category="Public health",
        description=(
            "SMS/WhatsApp alerts, community loudspeaker warnings, and colour-coded "
            "heat flags at public buildings when temperatures exceed thresholds."
        ),
        cooling_min_c=0.0,
        cooling_max_c=0.0,
        cost_per_unit_min_lakh=0.1,
        cost_per_unit_max_lakh=0.3,
        unit="ward-level alert system",
        timeline_months=1,
        evidence_source=(
            "Ahmedabad Heat Action Plan (2013); "
            "India National Disaster Management Authority HAP framework"
        ),
        assumptions=(
            "No direct temperature reduction — reduces mortality and morbidity "
            "by 30–40% during declared heat waves (Ahmedabad HAP evaluation). "
            "Cost covers SMS gateway, loudspeaker maintenance, and community "
            "health worker training per ward."
        ),
        lst_reduction_per_pct=0.0,
        ndvi_gain_per_pct=0.0,
        built_up_reduction_per_pct=0.0,
        vuln_reduction_per_unit=0.01,
    ),
}


# ── Simulation result ────────────────────────────────────────────────────

@dataclass
class InterventionResult:
    """Result for a single intervention in a simulation."""
    type: str
    estimated_cooling_range: str
    cost_range_lakh: str
    timeline_months: int
    priority: str
    assumptions: str
    confidence: float


@dataclass
class SimulationResult:
    """Full simulation result for a ward."""
    ward_id: int
    ward_name: str
    baseline_score: float
    projected_score: float
    risk_reduction: float
    cost_estimate_lakh: float
    priority_impact: str
    interventions: list[InterventionResult]
    assumptions: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ── Intervention optimizer ───────────────────────────────────────────────

class InterventionOptimizer:
    """Simulates combined intervention effects on a ward's heat-risk score.

    All estimates show confidence bounds and assumptions.  Temperature
    reductions are conservative ranges, not exact promises.
    """

    def __init__(self) -> None:
        self.catalog = INTERVENTION_CATALOG

    def get_catalog(self) -> list[dict[str, Any]]:
        """Return the full intervention catalog as dicts."""
        result = []
        for key, spec in self.catalog.items():
            result.append({
                "key": key,
                "name": spec.name,
                "category": spec.category,
                "description": spec.description,
                "estimated_cooling_min": spec.cooling_min_c,
                "estimated_cooling_max": spec.cooling_max_c,
                "cost_per_unit_min": spec.cost_per_unit_min_lakh,
                "cost_per_unit_max": spec.cost_per_unit_max_lakh,
                "unit": spec.unit,
                "timeline_months": spec.timeline_months,
                "evidence_source": spec.evidence_source,
                "assumptions": spec.assumptions,
            })
        return result

    def simulate(
        self,
        ward_id: int,
        ward_name: str,
        features: dict[str, Any],
        interventions: list[dict[str, Any]],
        budget_lakh: float = 50.0,
    ) -> SimulationResult:
        """Run a what-if simulation for a combination of interventions.

        Parameters
        ----------
        ward_id : int
        ward_name : str
        features : dict
            Current ward feature values (lst_c, ndvi, etc.)
        interventions : list of dict
            Each with 'intervention_type', 'coverage_pct' and/or 'units'.
        budget_lakh : float
            Total available budget in INR lakhs.

        Returns
        -------
        SimulationResult
        """
        from .risk_engine import predict_risk, risk_category

        baseline = predict_risk(features)
        adjusted = dict(features)

        total_cost_min = 0.0
        total_cost_max = 0.0
        intervention_results: list[InterventionResult] = []
        all_assumptions: list[str] = []

        for item in interventions:
            itype = item.get("intervention_type", "")
            spec = self.catalog.get(itype)
            if not spec:
                continue

            coverage = float(item.get("coverage_pct", 25))
            units = int(item.get("units", max(1, int(coverage / 10))))

            # Apply conservative feature adjustments
            if spec.lst_reduction_per_pct > 0:
                reduction = min(coverage, 100) * spec.lst_reduction_per_pct
                adjusted["lst_c"] = max(25, float(adjusted["lst_c"]) - reduction)

            if spec.ndvi_gain_per_pct > 0:
                gain = coverage * spec.ndvi_gain_per_pct
                adjusted["ndvi"] = min(0.90, float(adjusted["ndvi"]) + gain)

            if spec.built_up_reduction_per_pct > 0:
                reduction = coverage * spec.built_up_reduction_per_pct
                adjusted["built_up_pct"] = max(0, float(adjusted["built_up_pct"]) - reduction)

            if spec.vuln_reduction_per_unit > 0:
                reduction = units * spec.vuln_reduction_per_unit
                adjusted["vulnerability_index"] = max(
                    0.03, float(adjusted["vulnerability_index"]) - reduction,
                )

            # Cost estimation
            cost_min = units * spec.cost_per_unit_min_lakh
            cost_max = units * spec.cost_per_unit_max_lakh
            total_cost_min += cost_min
            total_cost_max += cost_max

            # Priority based on cooling potential vs cost
            efficiency = (spec.cooling_max_c / max(spec.cost_per_unit_max_lakh, 0.01))
            if efficiency > 1.5:
                priority = "high"
            elif efficiency > 0.5:
                priority = "medium"
            else:
                priority = "low"

            intervention_results.append(InterventionResult(
                type=spec.name,
                estimated_cooling_range=f"{spec.cooling_min_c}–{spec.cooling_max_c} °C",
                cost_range_lakh=f"₹{cost_min:.1f}–{cost_max:.1f} lakh",
                timeline_months=spec.timeline_months,
                priority=priority,
                assumptions=spec.assumptions,
                confidence=0.55,  # Honest: based on literature ranges, not local calibration
            ))
            all_assumptions.append(f"{spec.name}: {spec.assumptions}")

        # Cap total adjustments to physically plausible limits
        adjusted["lst_c"] = max(25, float(adjusted["lst_c"]))
        adjusted["ndvi"] = min(0.90, float(adjusted["ndvi"]))
        adjusted["built_up_pct"] = max(0, float(adjusted["built_up_pct"]))
        adjusted["vulnerability_index"] = max(0.03, float(adjusted["vulnerability_index"]))

        projected = predict_risk(adjusted)
        risk_red = max(0.0, baseline.score - projected.score)
        avg_cost = round((total_cost_min + total_cost_max) / 2, 1)

        # Priority impact
        if risk_red >= 15:
            impact = "high"
        elif risk_red >= 5:
            impact = "medium"
        else:
            impact = "low"

        combined_assumptions = (
            "Combined simulation uses additive feature adjustments — "
            "interaction effects between interventions are not modelled.  "
            "All cost estimates are indicative ranges in 2024 INR.  "
            + " | ".join(all_assumptions)
        )

        return SimulationResult(
            ward_id=ward_id,
            ward_name=ward_name,
            baseline_score=baseline.score,
            projected_score=projected.score,
            risk_reduction=round(risk_red, 1),
            cost_estimate_lakh=avg_cost,
            priority_impact=impact,
            interventions=intervention_results,
            assumptions=combined_assumptions,
        )


# ── Module-level convenience ────────────────────────────────────────────

_optimizer: Optional[InterventionOptimizer] = None


def get_optimizer() -> InterventionOptimizer:
    """Return a singleton InterventionOptimizer."""
    global _optimizer
    if _optimizer is None:
        _optimizer = InterventionOptimizer()
    return _optimizer
