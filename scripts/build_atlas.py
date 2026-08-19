#!/usr/bin/env python3
"""Build the lightweight audit tables and coordinate atlas used in the README."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "grime_curated.csv"


def number(row: dict[str, str], key: str) -> float | None:
    try:
        value = float(row[key])
        return value if math.isfinite(value) else None
    except (KeyError, TypeError, ValueError):
        return None


def quantile(values: list[float], q: float) -> float:
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - pos) + values[hi] * (pos - lo)


def pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    top = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    bottom = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return top / bottom if bottom else float("nan")


def svg_atlas(rows: list[dict[str, str]], low: float, high: float) -> str:
    width, height = 1200, 620
    points = []
    for row in rows:
        lon = number(row, "Longitude")
        lat = number(row, "Latitude")
        flux = number(row, "Diffusive_CH4_Flux_Mean")
        if lon is None or lat is None or flux is None or flux <= 0:
            continue
        clipped = min(max(flux, low), high)
        strength = (math.log(clipped) - math.log(low)) / (math.log(high) - math.log(low))
        x = 65 + (lon + 180) / 360 * 1070
        y = 555 - (lat + 60) / 150 * 480
        radius = 2.0 + 4.8 * strength
        color = f"rgb({int(46 + 206 * strength)},{int(196 - 73 * strength)},{int(182 - 125 * strength)})"
        points.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.2f}" fill="{color}" fill-opacity="0.64"/>')

    grid = []
    for lon in range(-180, 181, 60):
        x = 65 + (lon + 180) / 360 * 1070
        grid.append(f'<line x1="{x:.1f}" y1="75" x2="{x:.1f}" y2="555"/>')
    for lat in range(-60, 91, 30):
        y = 555 - (lat + 60) / 150 * 480
        grid.append(f'<line x1="65" y1="{y:.1f}" x2="1135" y2="{y:.1f}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620">
  <rect width="1200" height="620" rx="30" fill="#071b26"/>
  <text x="65" y="48" fill="#e9fbf7" font-family="Segoe UI, sans-serif" font-size="26" font-weight="700">The coordinate atlas</text>
  <text x="1135" y="48" fill="#86aaa8" font-family="Segoe UI, sans-serif" font-size="14" text-anchor="end">point size + colour = clipped positive CH₄ flux</text>
  <g stroke="#31505a" stroke-width="1" stroke-opacity="0.55">{''.join(grid)}</g>
  <rect x="65" y="75" width="1070" height="480" fill="none" stroke="#466a70"/>
  <g>{''.join(points)}</g>
  <circle cx="865" cy="589" r="4" fill="#2ec4b6"/><text x="878" y="594" fill="#86aaa8" font-family="Segoe UI, sans-serif" font-size="13">lower</text>
  <circle cx="965" cy="589" r="7" fill="#f47b39"/><text x="980" y="594" fill="#86aaa8" font-family="Segoe UI, sans-serif" font-size="13">higher</text>
  <text x="65" y="594" fill="#86aaa8" font-family="Segoe UI, sans-serif" font-size="13">A coordinate view, not a political basemap · 5th–95th percentile colour scale</text>
</svg>'''


def main() -> None:
    with DATA.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    fluxes = [v for row in rows if (v := number(row, "Diffusive_CH4_Flux_Mean")) is not None and v > 0]
    low, high = quantile(fluxes, 0.05), quantile(fluxes, 0.95)
    filtered = [row for row in rows if (v := number(row, "Diffusive_CH4_Flux_Mean")) is not None and low <= v <= high]

    transforms = {
        "Latitude": lambda x: x,
        "Elevation_m": math.log1p,
        "Slope_m_per_m": math.log1p,
        "Strahler_order": lambda x: x,
        "Basin_size_km2": math.log1p,
    }
    correlations = []
    for field, transform in transforms.items():
        pairs = []
        for row in filtered:
            x, y = number(row, field), number(row, "Diffusive_CH4_Flux_Mean")
            if x is not None and y is not None and y > 0 and x >= 0 if field != "Latitude" else x is not None and y is not None and y > 0:
                pairs.append((transform(x), math.log(y)))
        correlations.append({"driver": field, "n": len(pairs), "pearson_r": pearson([p[0] for p in pairs], [p[1] for p in pairs])})

    summary = {
        "records": len(rows),
        "unique_sites": len({row["Site_ID"] for row in rows}),
        "positive_flux_records": len(fluxes),
        "analysis_records_after_5_95_filter": len(filtered),
        "positive_flux_p05": low,
        "positive_flux_p95": high,
        "note": "Correlations are descriptive and pairwise; they are not causal estimates.",
    }
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (ROOT / "results" / "driver_correlations.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["driver", "n", "pearson_r"])
        writer.writeheader()
        writer.writerows(correlations)
    (ROOT / "assets" / "site-atlas.svg").write_text(svg_atlas(rows, low, high), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
