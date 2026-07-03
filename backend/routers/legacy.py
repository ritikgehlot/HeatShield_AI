"""Original V1 endpoints, preserved so backend/static/ (the original prototype
dashboard) keeps working unchanged. Backed by the new schema under the hood via
services.serialize_ward_legacy — confirmed by reading backend/static/app.js
that it only ever calls /api/summary, /api/wards (list), /api/simulate,
/api/data/upload and /api/data/template, never /api/wards/{id} directly, so
that path is free for the new V2 shape in routers/wards.py without breaking
anything here.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..interventions import simulate_scenario
from ..models import InterventionSimulation, ScenarioRun, Ward
from ..schemas import ScenarioOut, ScenarioRequest, SummaryOut, UploadResult, WardOut
from ..services import import_wards_from_csv, latest_score, latest_snapshot, serialize_ward_legacy, snapshot_features

router = APIRouter(tags=["legacy-v1"])


@router.get("/api/wards", response_model=list[WardOut])
def list_wards_legacy(city: str | None = None, db: Session = Depends(get_db)):
    wards = db.scalars(select(Ward)).all()
    if city:
        wards = [w for w in wards if w.city.name == city]
    serialized = [serialize_ward_legacy(db, w) for w in wards]
    serialized.sort(key=lambda w: w["risk_score"], reverse=True)
    return serialized


@router.get("/api/summary", response_model=SummaryOut)
def get_summary_legacy(db: Session = Depends(get_db)):
    wards = db.scalars(select(Ward)).all()
    if not wards:
        raise HTTPException(status_code=404, detail="No wards available")
    serialized = [serialize_ward_legacy(db, w) for w in wards]
    lst_values = [w["lst_c"] for w in serialized if w.get("lst_c") is not None]
    ndvi_values = [w["ndvi"] for w in serialized if w.get("ndvi") is not None]
    return {
        "city": wards[0].city.name,
        "total_wards": len(wards),
        "high_risk_wards": sum(w["risk_score"] >= 60 for w in serialized),
        "average_risk_score": round(sum(w["risk_score"] for w in serialized) / len(serialized), 1),
        "average_lst_c": round(sum(lst_values) / len(lst_values), 1) if lst_values else 0.0,
        "green_cover_average": round(sum(ndvi_values) / len(ndvi_values), 2) if ndvi_values else 0.0,
        "data_note": "V1-compatible view. Categories now include Moderate/Severe — see /api/wards/{id} for the full V2 breakdown.",
    }


@router.post("/api/simulate", response_model=ScenarioOut)
def run_simulation_legacy(payload: ScenarioRequest, db: Session = Depends(get_db)):
    ward = db.get(Ward, payload.ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")

    snapshot = latest_snapshot(db, ward.id)
    features = snapshot_features(snapshot)
    if all(v is None for v in features.values()):
        raise HTTPException(status_code=400, detail="This ward has no feature data yet.")

    outcome = simulate_scenario(features, payload.budget_lakh, payload.cool_roof_coverage, payload.tree_cover_gain, payload.shade_units, "mixed")

    db.add(
        InterventionSimulation(
            ward_id=ward.id, budget_inr_lakh=payload.budget_lakh, roof_treatment_pct=payload.cool_roof_coverage,
            tree_canopy_target_pct=payload.tree_cover_gain, shade_structures=payload.shade_units, infra_focus="mixed",
            baseline_score=outcome.baseline_score, projected_score=outcome.projected_score,
            risk_reduction_pts=outcome.risk_reduction_pts, allocations=outcome.allocations, assumptions=outcome.assumptions,
        )
    )
    # Also write the original scenario_runs row so any legacy tooling reading that table keeps working.
    db.add(
        ScenarioRun(
            ward_id=ward.id, cool_roof_coverage=payload.cool_roof_coverage, tree_cover_gain=payload.tree_cover_gain,
            shade_units=payload.shade_units, budget_lakh=payload.budget_lakh, baseline_score=outcome.baseline_score,
            projected_score=outcome.projected_score, projected_lst_c=outcome.projected_lst_c,
        )
    )
    db.commit()

    action_brief = (
        f"For {ward.name}, prioritise a phased heat-action package. "
        f"The estimate suggests the Heat Risk Score could move from {outcome.baseline_score:.1f}/100 "
        f"to {outcome.projected_score:.1f}/100 (range {outcome.risk_reduction_range_pts[0]}-{outcome.risk_reduction_range_pts[1]} pts reduction), "
        f"subject to local validation and implementation quality."
    )

    return {
        "ward_id": ward.id, "ward_name": ward.name, "baseline_score": outcome.baseline_score,
        "projected_score": outcome.projected_score, "risk_reduction": outcome.risk_reduction_pts,
        "baseline_lst_c": features.get("lst_c") or 0.0, "projected_lst_c": outcome.projected_lst_c,
        "risk_level": outcome.projected_category,
        "intervention_summary": [a["label"] for a in outcome.allocations] or ["No intervention selected"],
        "action_brief": action_brief,
        "model_note": "Transparent hybrid-formula planning comparison; validate against local observations before policy deployment.",
    }


@router.post("/api/data/upload", response_model=UploadResult)
async def upload_ward_data_legacy(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")
    try:
        raw = await file.read()
        imported, updated, skipped, run = import_wards_from_csv(db, raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"imported": imported, "updated": updated, "skipped": skipped, "message": "Data imported. Risk scores and recommendations were recomputed."}


@router.get("/api/recent-scenarios")
def recent_scenarios_legacy(db: Session = Depends(get_db)):
    runs = db.scalars(select(ScenarioRun).order_by(ScenarioRun.created_at.desc()).limit(8)).all()
    return [
        {"id": r.id, "ward_id": r.ward_id, "baseline_score": r.baseline_score, "projected_score": r.projected_score, "created_at": r.created_at}
        for r in runs
    ]
