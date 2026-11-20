#!/usr/bin/env python3
"""Write exports/owner-names.csv: one row per parcel, sortable by name.

    python3 tools/export_names.py

Columns: Name (likely owner when a company holds the property, otherwise the
owner), ID (C-<parcel> for Cuyahoga, G-<parcel> for Geauga — use it to match
results back to the map), owner on record, owner type, has a home, address,
area, county, and the county's original name text. The monthly refresh runs
this automatically, so the file always matches the map.
"""
import csv
import glob
import json
import os

TYPES = {"company": "Company", "government": "Public", "school": "School", "hoa": "HOA",
         "religious": "Church"}


def main(out="exports/owner-names.csv"):
    best = {}
    for path in glob.glob("parcel-data/*.geojson"):
        with open(path, encoding="utf-8") as fh:
            for ft in json.load(fh)["features"]:
                p = ft["properties"]
                best[(p["source_county"], p["parcel_id"])] = p
    rows = []
    for (county, pid), p in best.items():
        addr = " ".join((p.get("property_address") or "").split(",")[0].split())
        area = p["jurisdiction"].title() if county == "Cuyahoga" else p["jurisdiction"]
        home = {1: "Yes", 0: "No"}.get(p.get("home"), "")
        rows.append([p.get("likely") or p.get("owner_name") or "",
                     f"{county[0]}-{pid}", p.get("owner_name") or "",
                     TYPES.get(p.get("otype") or "", "Person"), home, addr, area, county,
                     p.get("owner_raw") or ""])
    rows.sort(key=lambda r: (r[7], r[6], r[5]))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["Name", "ID", "Owner on record", "Owner type", "Has a home", "Address", "Area",
                    "County", "County original name"])
        w.writerows(rows)
    print(f"Wrote {out}: {len(rows)} parcels")


if __name__ == "__main__":
    main()
