"""Register original geoBoundaries metadata and copy unchanged shapes for offline use."""

from __future__ import annotations

import json
import shutil

from provenance import ROOT, register_raw, upsert_source

__all__ = ["register_boundaries"]


def register_boundaries() -> None:
    """Preserve each source's actual license and metadata rather than assuming one."""
    for iso in ("IND", "PAK"):
        metadata_path = (
            f"data/raw/regional/geoboundaries_{iso.lower()}_adm1_metadata.json"
        )
        metadata = json.loads((ROOT / metadata_path).read_text())
        source_id = f"geoboundaries_{iso.lower()}_adm1_9469f09"
        url = f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/ADM1/"
        geometry_path = f"data/raw/regional/geoBoundaries-{iso}-ADM1_simplified.geojson"
        geometry = json.loads((ROOT / geometry_path).read_text())
        if geometry["type"] != "FeatureCollection" or len(geometry["features"]) != int(
            metadata["admUnitCount"]
        ):
            raise ValueError(f"Boundary metadata/geometry count mismatch: {iso}")
        if any(
            feature["properties"]["shapeGroup"] != iso
            for feature in geometry["features"]
        ):
            raise ValueError(f"Wrong country shape: {iso}")
        upsert_source(
            {
                "source_id": source_id,
                "title": f"geoBoundaries gbOpen {iso} ADM1, commit 9469f09",
                "publisher": "geoBoundaries / William & Mary geoLab",
                "url": url,
                "year": metadata["boundaryYearRepresented"],
                "accessed": "2026-10-13",
                "tier": "B",
                "access_method": "curl official API metadata and pinned simplified GeoJSON",
                "license": metadata["boundaryLicense"],
                "notes": f"Source: {metadata['boundarySource']}. Build {metadata['buildDate']}. Metadata represented-year field preserved verbatim; India geometry contains later subdivisions, so this year is not a verified validity date for each polygon. Shape display is not a statement of territorial sovereignty. License differs from plan's blanket CC BY 4.0 assumption.",
            }
        )
        register_raw(
            metadata_path,
            url,
            source_id,
            metadata["boundaryLicense"],
            "Original geoBoundaries API metadata; per-country license retained.",
        )
        register_raw(
            geometry_path,
            metadata["simplifiedGeometryGeoJSON"],
            source_id,
            metadata["boundaryLicense"],
            "Original download of publisher-simplified geometry. Dashboard copy is byte-identical.",
        )
        destination = ROOT / f"dashboard/geo/geoBoundaries-{iso}-ADM1.geojson"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / geometry_path, destination)
        print(
            f"{iso}: {len(geometry['features'])} features; {metadata['boundaryLicense']}"
        )


if __name__ == "__main__":
    register_boundaries()
