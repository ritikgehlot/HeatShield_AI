from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import HeatRiskScore, Ward
from ..risk_engine import score_ward
from ..schemas import RiskExplanationOut, TimeseriesOut, WardDetailOut
from ..services import serialize_ward_detail, snapshot_features

router = APIRouter(tags=["wards"])


@router.get("/api/wards/{ward_id}", response_model=WardDetailOut)
def get_ward_detail(ward_id: int, db: Session = Depends(get_db)):
    ward = db.get(Ward, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    return serialize_ward_detail(db, ward)


@router.get("/api/wards/{ward_id}/timeseries", response_model=TimeseriesOut)
def get_ward_timeseries(ward_id: int, db: Session = Depends(get_db)):
    ward = db.get(Ward, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    rows = db.scalars(
        select(HeatRiskScore).where(HeatRiskScore.ward_id == ward_id).order_by(HeatRiskScore.computed_at.asc())
    ).all()
    return {
        "ward_id": ward.id,
        "ward_name": ward.name,
        "points": [{"computed_at": r.computed_at, "score": r.score, "category": r.category} for r in rows],
    }


@router.get("/api/wards/{ward_id}/risk-explanation", response_model=RiskExplanationOut)
def get_ward_risk_explanation(ward_id: int, db: Session = Depends(get_db)):
    ward = db.get(Ward, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    from ..services import latest_snapshot

    snapshot = latest_snapshot(db, ward_id)
    features = snapshot_features(snapshot)
    result = score_ward(features, observed_at=snapshot.observed_at if snapshot else None)
    return {
        "ward_id": ward.id,
        "ward_name": ward.name,
        "score": result.score,
        "category": result.category,
        "confidence": result.confidence,
        "all_factors": [
            {"key": f.key, "label": f.label, "value": f.value, "normalized_risk": f.normalized_risk, "weight": f.weight, "contribution_pts": f.contribution_pts}
            for f in result.all_factors
        ],
        "missing_data_warnings": result.missing_data_warnings,
        "explanation": result.explanation,
        "model_version": result.model_version,
    }
