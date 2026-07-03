export const FEATURE_DEFINITIONS: Record<string, string> = {
  lst_c: "Land Surface Temperature: how hot the ground/rooftop surface itself is, measured by satellite thermal sensors. Usually higher than air temperature.",
  air_temp_c: "The ambient air temperature at roughly head height, as reported by weather stations or forecasts.",
  humidity_pct: "Relative humidity — how much moisture is in the air, which affects how hot it feels (apparent temperature).",
  wind_speed_mps: "Wind speed in meters per second. Higher wind speeds help disperse heat.",
  ndvi: "Normalized Difference Vegetation Index — a satellite-derived measure of green cover. Higher NDVI means more vegetation, which cools an area.",
  ndbi: "Normalized Difference Built-up Index — a satellite-derived measure of built-up (concrete/asphalt/roofing) density. Higher NDBI means more heat-trapping surfaces.",
  built_up_pct: "Estimated share of the ward's land area covered by buildings and paved surfaces.",
  road_density_km_km2: "Kilometers of road per square kilometer — a proxy for paved-surface heat retention and pedestrian heat exposure.",
  population_density: "People per square kilometer.",
  vulnerability_index: "A 0–1 composite of factors like age, health access, and housing quality that affect how much harm heat exposure causes to residents.",
  heat_index_c: "Apparent temperature: how hot it feels when humidity is factored in alongside air temperature.",
};
