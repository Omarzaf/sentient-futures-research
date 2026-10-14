"""Build a network-independent dashboard from the local reviewed CSV snapshots."""

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def boundary_paths(path: Path) -> list[dict[str, str]]:
    """Project every original boundary vertex to a fixed SVG viewbox, without simplification."""
    data = json.loads(path.read_text())
    rings = []
    for feature in data["features"]:
        geometry = feature["geometry"]
        polygons = (
            [geometry["coordinates"]]
            if geometry["type"] == "Polygon"
            else geometry["coordinates"]
        )
        projected = [
            [
                (
                    lon,
                    -math.degrees(
                        math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
                    ),
                )
                for lon, lat, *_ in ring
            ]
            for polygon in polygons
            for ring in polygon
        ]
        rings.append((feature["properties"], projected))
    points = [p for _, feature in rings for ring in feature for p in ring]
    left, right = min(p[0] for p in points), max(p[0] for p in points)
    top, bottom = min(p[1] for p in points), max(p[1] for p in points)
    scale = min(440 / (right - left), 400 / (bottom - top))
    dx, dy = (480 - (right - left) * scale) / 2, (440 - (bottom - top) * scale) / 2
    return [
        {
            "name": properties["shapeName"],
            "id": properties["shapeID"],
            "d": " ".join(
                "M"
                + " L".join(
                    f"{(x-left)*scale+dx:.2f},{(y-top)*scale+dy:.2f}" for x, y in ring
                )
                + "Z"
                for ring in feature
            ),
        }
        for properties, feature in rings
    ]


def build() -> None:
    """Embed reviewed rows, provenance hashes and projected boundaries in one HTML file."""
    data = {}
    hashes = {}
    excluded = []
    for path in sorted((ROOT / "data/processed").glob("*.csv")):
        if path.stem.startswith("newsframing_"):
            # The selected news analysis belongs only in the report appendix,
            # including its downloads and otherwise hidden JSON payload.
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        data[path.stem] = []
        for row in rows:
            if row.get("evidence_status", "").upper().startswith("HELD"):
                # Whitelist nonnumeric provenance; never copy held values into HTML.
                excluded.append(
                    {
                        "dataset": path.stem,
                        "country": row.get("country", ""),
                        "segment": row.get("segment", ""),
                        "source_id": row.get("source_id", ""),
                        "methodology_source_id": row.get("methodology_source_id", ""),
                        "evidence_status": row["evidence_status"],
                        "factor_scenario": row.get("factor_scenario", ""),
                        "scenario_id": row.get("scenario_id", ""),
                        "scenario_role": row.get("scenario_role", ""),
                        "grouping_scenario": row.get("grouping_scenario", ""),
                        "price_scenario": row.get("price_scenario", ""),
                        "reason": row.get("evidence_hold_reason", "Evidence held"),
                        "retained_local_file": str(path.relative_to(ROOT)),
                    }
                )
            else:
                data[path.stem].append(row)
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    maps = {}
    for code, country in [("IND", "India"), ("PAK", "Pakistan")]:
        path = ROOT / f"dashboard/geo/geoBoundaries-{code}-ADM1.geojson"
        maps[country] = boundary_paths(path)
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    snapshot = {
        "tables": data,
        "maps": maps,
        "hashes": hashes,
        "excluded_evidence": excluded,
        "supporting_documents": {},
    }
    for name, relative in {
        "protein_method": "scripts/diet/supervisor_model_20261013/README.md",
        "protein_history": "scripts/diet/m3_modelled_release_20261013/superseded_protein_gap.csv",
        "protein_history_receipt": "scripts/diet/m3_modelled_release_20261013/preservation.json",
    }.items():
        path = ROOT / relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        snapshot["supporting_documents"][name] = {
            "path": relative,
            "sha256": hashes[relative],
            "text": path.open(encoding="utf-8", newline="").read(),
        }
    payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    payload = (
        payload.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    template = (ROOT / "dashboard/template.html").read_text()
    assert template.count("__SNAPSHOT_JSON__") == 1
    output = template.replace("__SNAPSHOT_JSON__", payload)
    (ROOT / "dashboard/index.html").write_text(output)
    print(
        f"Built dashboard/index.html: {len(output.encode()):,} bytes; {len(data)} tables; no runtime network dependencies"
    )


if __name__ == "__main__":
    build()
