# Premise check: is there a site-level forecast bias worth modelling?

**Date:** 25 September 2026
**Outcome:** No. The site-correction model was cut before it was built.

## Why this was tested first

SiteHeat's original pitch was that a gridded weather forecast misses what a specific
worksite actually experiences, and that a model could learn each site's offset. That is
an assumption, not a fact. Both checks below were run before any model was written, and
the pass/fail rule for each was fixed in code before the data was seen.

## Data

| Source | Use |
|---|---|
| City of Melbourne `microclimate-sensors-data` | Street-level air temperature, 15-minute readings |
| Open-Meteo Historical Forecast Archive | Archived forecasts at the sensor coordinates |

Processing: readings converted from UTC to `Australia/Melbourne` before taking the daily
maximum, so a hot evening is not filed under the wrong day. Days with fewer than 60
readings were dropped, since a maximum built from a handful of samples is not a maximum.

Sensors are grouped by device. Rooftop devices were excluded: a rooftop is not where
work happens.

## Check 1 — single station vs forecast

**Question:** at one fixed point, is the forecast error consistent or random?
**Rule set in advance:** the premise holds if `|mean error| > sd/2`.

Station: `ICTMicroclimate-08`, Swanston St tram stop (asphalt, no canopy).
Window: 2024-04-09 to 2026-09-23, 898 days.

| Metric | Value |
|---|---|
| Mean error (observed − forecast) | +1.32 °C |
| Standard deviation | 1.09 °C |
| Days the street was hotter | 89% |
| Verdict rule | PASSED (1.32 > 0.54) |

But the error is not evenly distributed across temperatures:

| Forecast max | Mean error | Days |
|---|---|---|
| <20 °C | +1.51 | 581 |
| 20–25 °C | +1.13 | 165 |
| 25–30 °C | +0.98 | 89 |
| 30–35 °C | +0.62 | 42 |
| 35+ °C | +0.28 | 21 |

Correlation of error with forecast temperature: **−0.28**.

The headline bias is carried by 581 cool days. On days above 30 °C — the only days a
heat-safety tool matters — the bias falls below the ±1 °C threshold at which a correction
would change any decision on site.

Note: the bias *shrinking* with heat argues against sensor radiation error as the cause.
An unshielded sensor in sun would show the opposite pattern.

## Check 2 — two stations against each other

**Question:** do two sites in the same city diverge from each other on hot days? This is
the sharper test, because sites 1.5 km apart fall in the same forecast grid cell and
receive an identical forecast. Any gap between them is a gap no forecast can capture.

**Rule set in advance:** site effect is real if, on days where the park reaches 30 °C,
`|mean gap| > 1.0 °C` and `sd < |mean gap|`.

Stations: `ICTMicroclimate-08` (asphalt tram stop) vs `ICTMicroclimate-01` (Birrarung
Marr parkland). Window: 2024-04-09 to 2026-06-30, 813 overlapping days.

| Metric | Value |
|---|---|
| Mean difference (street − park) | +0.03 °C |
| Standard deviation | 0.86 °C |
| Street hotter on | 54% of days |
| Hot days (park ≥ 30 °C) | 89 |
| Mean gap on hot days | −0.25 °C (sd 0.85, range −2.6 to +1.3) |
| Verdict rule | FAILED |

The asphalt tram stop is not hotter than the park. On hot days it is marginally cooler,
with a spread three times the size of the gap.

## Conclusion

Taken together: a city-wide offset of roughly +1.3 °C on cool days, no measurable
difference between sites, and both effects decaying toward zero as temperature rises.
There is no site-level signal in air temperature to learn.

The physical intuition behind the project is not wrong — asphalt in full sun is harder on
a worker than a shaded park. But that difference is radiant load, not air temperature,
and air mixes freely across a city on a hot day. Capturing it would require globe
temperature or sky-view data that is not available for these sites and could not be
validated.

## Decisions taken

- The LightGBM site-correction model was cut before being built.
- `get_corrected_forecast` became `get_forecast`; the stub offset, fake uncertainty range
  and `confidence: stub` field were removed rather than left in place.
- The system prompt now states that the forecast is regional and uncorrected.
- SiteHeat's scope narrows to what it can support: retrieved forecasts, heat-stress
  indices from published BoM formulas, and answers grounded in real safety guidance.

## Limitations

- Two stations, one city, two summers. Rural or industrial sites were not tested.
- Birrarung Marr is open parkland with limited canopy, so this compares two open urban
  sites rather than full sun against deep shade.
- The two sensors are separate installations; mounting and shielding differences cannot
  be separated from microclimate with this data.
- Confidence intervals assume independent days. Hot days cluster, so the true intervals
  are wider than reported.
- Roughly four months of early readings for `ICTMicroclimate-08` were absent from the
  export, cause unconfirmed.
