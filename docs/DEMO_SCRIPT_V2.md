# Demo Script V2

A 5-minute walkthrough for judges. Also usable as a manual visual-QA checklist,
since automated visual testing wasn't possible in the build environment.

## Setup (once)

```powershell
# Terminal 1 — backend
cd heatshield-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000 — the backend serves the pre-built React app.
(To develop the frontend with hot reload, run `npm install && npm run dev` in
`frontend/` and use http://localhost:5173 instead.)

## The narrative

1. **Landing page.** Lead with the story: Jodhpur is the Blue City — its indigo
   walls are centuries-old passive cooling. HeatShield brings that instinct to
   the satellite era. Point out the thermal-scan hero and the "works with zero
   API keys · every value shows source, freshness & confidence" line. Click
   **Launch Dashboard**.

2. **Dashboard.** 16 Jodhpur wards. Walk the KPI row — city heat risk,
   severe/extreme ward count, population exposed, green deficit, latest weather,
   latest satellite scene. Hover the weather/satellite badges: show that demo
   data is *labelled* demo, with source and timestamp. Note the map colors wards
   on a continuous thermal gradient, not flat buckets.

3. **Click a hot ward** (e.g. Jalori Gate or Sojati Gate → Extreme). On the ward
   detail page, show the "Why this score" panel: the bar chart is the **exact**
   points each factor contributed — this is the explanation, not an approximation.
   Point out the missing-data warnings and confidence. Note the honest
   "simplified placeholder boundary" banner.

4. **Load ranked interventions.** Show that recommendations are ranked by the
   ward's *actual* top drivers, each with risk-reduction/cost/timeline ranges and
   a "why selected" line. Nothing promises an exact temperature drop.

5. **What-If Simulator.** Pick the same ward. Set a budget, drag roof/tree/shade
   sliders, Run. Show baseline → projected with a **range**, indicative budget
   allocation, and the assumptions block. Emphasise: decision support, not a
   physical simulation.

6. **Data Sources.** Show all four providers with live/demo status and last
   refresh. Download the V2 CSV template. Upload `data/sample_jodhpur_wards_v2.csv`
   — watch the import log and the scores update. Optionally upload
   `data/sample_jodhpur_boundaries.geojson`.

7. **Model & Method.** Close on transparency: the weighting table, limitations,
   and ethical commitments. "This informs municipal judgment; it doesn't replace it."

## Manual QA checklist

- [ ] Landing renders, hero animates (and respects reduced-motion).
- [ ] Dashboard KPIs populate; map shows colored wards + legend.
- [ ] Provenance badges show tooltips with source/timestamp.
- [ ] Ward detail explainability chart matches the score.
- [ ] Simulator produces baseline vs projected with a range.
- [ ] CSV upload updates data and logs the run; invalid CSV shows a clear error.
- [ ] Data Sources shows satellite as demo (no GEE keys) — not fake "live".
- [ ] Mobile: sidebar collapses to a drawer; layout is usable at ~380px.
- [ ] Keyboard: Tab reaches controls with a visible focus ring.
