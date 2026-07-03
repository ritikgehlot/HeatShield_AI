from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import City, Ward
from ..schemas import CityOut, DashboardOut
from ..services import get_dashboard

router = APIRouter(tags=["cities"])


@router.get("/api/cities", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db)):
    cities = db.scalars(select(City)).all()
    counts = dict(db.execute(select(Ward.city_id, func.count(Ward.id)).group_by(Ward.city_id)).all())
    return [
        {
            "id": c.id, "name": c.name, "state": c.state, "country": c.country,
            "center_lat": c.center_lat, "center_lon": c.center_lon,
            "ward_count": counts.get(c.id, 0),
        }
        for c in cities
    ]


@router.get("/api/cities/{city_id}/dashboard", response_model=DashboardOut)
def city_dashboard(city_id: int, db: Session = Depends(get_db)):
    city = db.get(City, city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return get_dashboard(db, city)
