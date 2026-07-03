from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..interventions import simulate_scenario
from ..models import InterventionSimulation, Ward
from ..schemas import SimulationOut, SimulationRequest
from ..services import latest_snapshot, snapshot_features

router = APIRouter(tags=["simulations"])


@router.post("/api/simulations", response_model=SimulationOut)
def create_simulation(payload: SimulationRequest, db: Session = Depends(get_db)):
    ward = db.get(Ward, payload.ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")

    snapshot = latest_snapshot(db, ward.id)
    features = snapshot_features(snapshot)
    if all(v is None for v in features.values()):
        raise HTTPException(status_code=400, detail="This ward has no feature data yet — import CSV data before simulating.")

    outcome = simulate_scenario(
        features, payload.budget_inr_lakh, payload.roof_treatment_pct, payload.tree_canopy_target_pct,
        payload.shade_structures, payload.infra_focus,
    )

    row = InterventionSimulation(
        ward_id=ward.id, budget_inr_lakh=payload.budget_inr_lakh, roof_treatment_pct=payload.roof_treatment_pct,
        tree_canopy_target_pct=payload.tree_canopy_target_pct, shade_structures=payload.shade_structures,
        infra_focus=payload.infra_focus, baseline_score=outcome.baseline_score, projected_score=outcome.projected_score,
        risk_reduction_pts=outcome.risk_reduction_pts, allocations=outcome.allocations, assumptions=outcome.assumptions,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "id": row.id, "ward_id": ward.id, "ward_name": ward.name,
        "baseline_score": outcome.baseline_score, "baseline_category": outcome.baseline_category,
        "projected_score": outcome.projected_score, "projected_category": outcome.projected_category,
        "risk_reduction_pts": outcome.risk_reduction_pts, "risk_reduction_range_pts": outcome.risk_reduction_range_pts,
        "projected_lst_c": outcome.projected_lst_c, "allocations": outcome.allocations, "assumptions": outcome.assumptions,
        "created_at": row.created_at,
    }


@router.get("/api/simulations/{simulation_id}", response_model=SimulationOut)
def get_simulation(simulation_id: int, db: Session = Depends(get_db)):
    row = db.get(InterventionSimulation, simulation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Simulation not found")
    ward = db.get(Ward, row.ward_id)
    baseline_category = _category_for(row.baseline_score)
    projected_category = _category_for(row.projected_score)
    return {
        "id": row.id, "ward_id": row.ward_id, "ward_name": ward.name if ward else "Unknown ward",
        "baseline_score": row.baseline_score, "baseline_category": baseline_category,
        "projected_score": row.projected_score, "projected_category": projected_category,
        "risk_reduction_pts": row.risk_reduction_pts, "risk_reduction_range_pts": (round(row.risk_reduction_pts * 0.7, 1), round(row.risk_reduction_pts * 1.3, 1)),
        "projected_lst_c": 0.0, "allocations": row.allocations, "assumptions": row.assumptions, "created_at": row.created_at,
    }


def _category_for(score: float) -> str:
    from ..risk_engine import _category

    return _category(score)
