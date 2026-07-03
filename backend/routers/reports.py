from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..interventions import rank_interventions
from ..models import Ward
from ..schemas import WardReportOut
from ..services import latest_snapshot, serialize_ward_detail, snapshot_features

router = APIRouter(tags=["reports"])


@router.get("/api/reports/ward/{ward_id}", response_model=WardReportOut)
def ward_report(ward_id: int, db: Session = Depends(get_db)):
    ward = db.get(Ward, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")

    detail = serialize_ward_detail(db, ward)
    snapshot = latest_snapshot(db, ward.id)
    features = snapshot_features(snapshot)
    recommendations = rank_interventions(features, population=ward.population)

    return {
        "ward": detail,
        "recommended_interventions": [
            {
                "key": r.key, "name": r.name, "priority_rank": r.priority_rank,
                "risk_reduction_range": r.risk_reduction_range, "cooling_impact_range_c": r.cooling_impact_range_c,
                "cost_range_inr_lakh": r.cost_range_inr_lakh, "timeline_weeks": r.timeline_weeks,
                "population_affected_range": r.population_affected_range, "confidence": r.confidence,
                "assumptions": r.assumptions, "why_selected": r.why_selected,
            }
            for r in recommendations
        ],
        "generated_at": datetime.now(timezone.utc),
        "disclaimer": (
            "This report is a decision-support estimate generated from the current data snapshot. "
            "It is not a validated engineering or policy document — confirm drivers and costs with "
            "local observations and vendor quotes before committing budget."
        ),
    }
