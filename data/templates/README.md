# Ward feature import templates

Two CSV contracts are supported. The importer auto-detects which one you're
using from the header row (presence of `ward_name` => V2).

## V2 (recommended) — `ward_features_v2.csv`
Columns:
`city, ward_id, ward_name, observed_at, latitude, longitude, lst_c, air_temp_c,
humidity_pct, wind_speed_mps, ndvi, ndbi, built_up_pct, road_density_km_km2,
population_density, vulnerability_index, source, confidence`

- `ward_id` may be left blank for new wards (they're created by name).
- `observed_at` ISO-8601 UTC (e.g. `2026-07-01T10:00:00`); defaults to now if blank.
- `source` and `confidence` (0–1) attach provenance to every row.
- `air_temp_c`, `humidity_pct`, `wind_speed_mps` are optional.

## V1 (legacy, still supported)
Columns:
`city, name, latitude, longitude, map_x, map_y, lst_c, ndvi, ndbi, built_up_pct,
road_density_km_km2, population_density, vulnerability_index, data_source`

## Field meanings
- `lst_c` — Land Surface Temperature (°C), from satellite thermal bands.
- `ndvi` — vegetation index 0–1 (higher = greener = cooler).
- `ndbi` — built-up index 0–1 (higher = more concrete = hotter).
- `vulnerability_index` — 0–1 composite of heat-health vulnerability.

## Validation
Rows with missing required columns are rejected with a clear error. Rows with
unparseable numbers are skipped and counted; the rest still import. Every import
is recorded as an ingestion run and recomputes risk scores immediately.

All example values here are illustrative demo values — replace with validated data.
