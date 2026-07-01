# Data contract

The dashboard starts with **seeded demonstration ward data** so that the project runs immediately. It is not a validated municipal dataset.

For real use, prepare one row per ward/zone and import it from the UI or command line. Required columns:

- `name`, `latitude`, `longitude`
- `lst_c`: land surface temperature in °C
- `ndvi`: green-cover index, typically -1 to +1
- `ndbi`: built-up index, typically -1 to +1
- `built_up_pct`: percentage of built-up area
- `road_density_km_km2`
- `population_density`: people per km²
- `vulnerability_index`: local composite score from 0 to 1

Optional: `city`, `map_x`, `map_y`, `data_source`.

## Recommended real-data workflow

1. Derive LST from Landsat thermal bands or a validated product.
2. Compute NDVI from Sentinel-2/Landsat red and near-infrared bands.
3. Compute NDBI or a comparable built-up feature.
4. Aggregate raster values to ward boundaries in GIS.
5. Join roads/buildings/population from approved municipal, Census or OpenStreetMap sources.
6. Validate model output with weather-station readings and local expert review.

Do not present the seeded figures as official city heat measurements.
