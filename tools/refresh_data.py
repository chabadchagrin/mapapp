#!/usr/bin/env python3
"""Rebuild parcel-data/ from the two county GIS services.

    python3 tools/refresh_data.py

What it does:
  1. Downloads every parcel in the covered areas (owner, address, last sale
     date and price, outline) from Cuyahoga's and Geauga's public map services.
  2. Compares owners with the data currently in parcel-data/ and records
     any change of hands (prev_owner, changed_on) plus a running log in
     parcel-data/changes.json.
  3. Cleans owner names (tools/clean_owner_names.py) and writes the map
     tiles and parcel-data/index.json.

It stops without writing anything if either county returns far fewer
parcels than last time, so a county outage can't wipe the app's data.
"""
import collections
import datetime as dt
import glob
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clean_owner_names as names  # noqa: E402

DATA = "parcel-data"
CELL = 0.025
PRECISION = 6  # decimal places in coordinates (~10 cm)

CUY_URL = "https://gis.cuyahogacounty.gov/server/rest/services/Open_Data_Parcels/MapServer/1"
CUY_CITIES = ["BENTLEYVILLE", "CHAGRIN FALLS", "CHAGRIN FALLS TOWNSHIP", "HUNTING VALLEY",
              "MORELAND HILLS", "PEPPER PIKE"]

GEA_URL = "https://gcgis.geauga.oh.gov/parcel/rest/services/AzureParcels/Parcels/FeatureServer/0"
# Geauga tax-district code -> area name used in the app
GEA_DISTRICTS = {
    "01": "Auburn Township",
    "02": "Bainbridge Township", "03": "Bainbridge Township",
    "06": "Chardon Township", "07": "Chardon Township", "08": "Chardon Township", "09": "Chardon Township",
    "10": "City of Chardon",
    "11": "Chester Township",
    "21": "Munson Township", "22": "Munson Township",
    "26": "Russell Township", "28": "Russell Township",
    "27": "Hunting Valley Village",
    "29": "South Russell Village",
}
NEW_OWNER_DAYS = 120  # how long the app shows the "New owner" badge


# ------------------------------------------------------------------ download
def get_json(url, params, tries=5):
    full = url + "?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "chabadchagrin-mapapp-refresh"})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            if "error" in d:
                raise RuntimeError(d["error"])
            return d
        except Exception as e:  # noqa
            if attempt == tries - 1:
                raise
            print(f"  retry {attempt + 1} after {e!r}", flush=True)
            time.sleep(5 * (attempt + 1))


def fetch_all(url, where, fields, order):
    feats, offset = [], 0
    while True:
        d = get_json(url + "/query", {
            "where": where, "outFields": ",".join(fields), "returnGeometry": "true",
            "outSR": 4326, "geometryPrecision": PRECISION, "orderByFields": order,
            "resultOffset": offset, "resultRecordCount": 2000, "f": "geojson"})
        batch = d.get("features", [])
        feats += batch
        print(f"  {len(feats)} features", flush=True)
        if len(batch) < 2000 and not d.get("exceededTransferLimit") and not d.get("properties", {}).get("exceededTransferLimit"):
            break
        if not batch:
            break
        offset += len(batch)
    return feats


def epoch_ms_to_date(v):
    if v in (None, ""):
        return None
    return (dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=float(v))).date().isoformat()


def money(v):
    if v in (None, ""):
        return None
    try:
        n = int(round(float(str(v).replace(",", "").replace("$", ""))))
    except ValueError:
        return None
    return n


def fetch_cuyahoga():
    print("Cuyahoga…", flush=True)
    where = "par_city IN (%s)" % ",".join("'%s'" % c for c in CUY_CITIES)
    fields = ["parcel_id", "parcelpin", "deeded_owner", "par_addr_all", "par_city", "par_zip",
              "transfer_date", "sales_amount"]
    out = []
    for f in fetch_all(CUY_URL, where, fields, "OBJECTID"):
        a = f.get("properties") or {}
        pid = (a.get("parcel_id") or a.get("parcelpin") or "").replace("-", "")
        if not pid or not f.get("geometry"):
            continue
        out.append((f["geometry"], {
            "source_county": "Cuyahoga",
            "jurisdiction": a.get("par_city") or "",
            "parcel_id": pid,
            "owner_raw": (a.get("deeded_owner") or "").strip(),
            "property_address": a.get("par_addr_all") or "",
            "property_city": a.get("par_city") or "",
            "property_zip": str(int(a["par_zip"])) if a.get("par_zip") else "",
            "sale_date": epoch_ms_to_date(a.get("transfer_date")),
            "sale_price": money(a.get("sales_amount")),
        }))
    return out


def fetch_geauga():
    print("Geauga…", flush=True)
    where = " OR ".join(f"TaxDist LIKE '{c}-%'" for c in GEA_DISTRICTS)
    fields = ["PARCEL_ID", "Oname1", "LOCATION_A", "LOCATION_C", "LOCATION_Z", "Sale_Date",
              "Sale_Amt", "TaxDist", "Par_Status"]
    out = []
    for f in fetch_all(GEA_URL, where, fields, "OBJECTID_1"):
        a = f.get("properties") or {}
        pid = (a.get("PARCEL_ID") or "").strip()
        code = (a.get("TaxDist") or "")[:2]
        if not pid or not f.get("geometry") or code not in GEA_DISTRICTS:
            continue
        sd = a.get("Sale_Date") or ""
        m = re.match(r"(\d\d)-(\d\d)-(\d{4})", sd)
        out.append((f["geometry"], {
            "source_county": "Geauga",
            "jurisdiction": GEA_DISTRICTS[code],
            "parcel_id": pid,
            "owner_raw": (a.get("Oname1") or "").strip(),
            "property_address": (a.get("LOCATION_A") or "").strip(),
            "property_city": (a.get("LOCATION_C") or "").strip(),
            "property_zip": (a.get("LOCATION_Z") or "").strip(),
            "sale_date": f"{m.group(3)}-{m.group(1)}-{m.group(2)}" if m else None,
            "sale_price": money(a.get("Sale_Amt")),
        }))
    return out


# ------------------------------------------------------------ previous data
def load_previous():
    prev = {}
    for path in glob.glob(os.path.join(DATA, "*.geojson")):
        with open(path, encoding="utf-8") as fh:
            for ft in json.load(fh)["features"]:
                p = ft["properties"]
                key = (p["source_county"], p["parcel_id"])
                prev[key] = p
    meta = {}
    if os.path.exists(os.path.join(DATA, "index.json")):
        with open(os.path.join(DATA, "index.json")) as fh:
            meta = {k: v for k, v in json.load(fh).items() if k != "tiles"}
    log = {"refreshes": [], "changes": []}
    if os.path.exists(os.path.join(DATA, "changes.json")):
        with open(os.path.join(DATA, "changes.json")) as fh:
            log = json.load(fh)
    return prev, meta, log


def norm_owner(s):
    return re.sub(r"[^A-Z0-9&]+", " ", (s or "").upper()).strip()


# ------------------------------------------------------------------- tiles
def bbox(geom):
    xs, ys = [], []

    def walk(c):
        if isinstance(c[0], (int, float)):
            xs.append(c[0]); ys.append(c[1])
        else:
            for x in c:
                walk(x)
    walk(geom["coordinates"])
    return min(xs), min(ys), max(xs), max(ys)


def main():
    today = dt.date.today().isoformat()
    prev, prev_meta, log = load_previous()
    prev_date = prev_meta.get("updated") or "2026-09-01"

    records = fetch_cuyahoga() + fetch_geauga()

    # ---- sanity check against last time
    new_counts = collections.Counter(p["source_county"] for _, p in records)
    new_unique = collections.Counter(c for c, _ in {(p["source_county"], p["parcel_id"]) for _, p in records})
    old_unique = collections.Counter(c for c, _ in prev)
    for county in ("Cuyahoga", "Geauga"):
        print(f"{county}: {new_counts[county]} features, {new_unique[county]} parcels (was {old_unique[county]})")
        if old_unique[county] and new_unique[county] < 0.95 * old_unique[county]:
            sys.exit(f"ABORT: {county} returned {new_unique[county]} parcels, last time {old_unique[county]}.")

    # ---- names
    sur, giv = names.learn([p["owner_raw"] for _, p in records])

    # ---- change detection
    changes, seen = [], set()
    for _, p in records:
        key = (p["source_county"], p["parcel_id"])
        old = prev.get(key)
        p["owner_name"] = names.clean_name(p["owner_raw"], sur, giv)
        if old:
            old_raw = old.get("owner_raw", old.get("owner_name")) or ""
            if norm_owner(old_raw) != norm_owner(p["owner_raw"]) and p["owner_raw"]:
                p["prev_owner"] = names.clean_name(old_raw, sur, giv) if old_raw else ""
                p["changed_on"] = today
                if key not in seen:
                    seen.add(key)
                    changes.append({
                        "county": p["source_county"], "parcel_id": p["parcel_id"],
                        "detected": today, "address": p["property_address"],
                        "jurisdiction": p["jurisdiction"],
                        "from": old_raw, "to": p["owner_raw"],
                        "sale_date": p["sale_date"], "sale_price": p["sale_price"],
                    })
            else:
                for k in ("prev_owner", "changed_on"):
                    if old.get(k):
                        p[k] = old[k]

    log["refreshes"].append({"date": today, "previous": prev_date, "parcels": sum(new_unique.values()),
                             "owner_changes": len(changes)})
    log["changes"] = changes + log.get("changes", [])

    # ---- tiles
    tiles = collections.defaultdict(list)
    for geom, p in records:
        props = {k: p[k] for k in ("source_county", "jurisdiction", "parcel_id", "owner_name", "owner_raw",
                                   "property_address", "property_city", "property_zip")}
        for k in ("sale_date", "sale_price", "prev_owner", "changed_on"):
            if p.get(k) not in (None, ""):
                props[k] = p[k]
        x0, y0, x1, y1 = bbox(geom)
        for x in range(math.floor(x0 / CELL), math.floor(x1 / CELL) + 1):
            for y in range(math.floor(y0 / CELL), math.floor(y1 / CELL) + 1):
                tiles[f"{x}_{y}"].append({"type": "Feature", "geometry": geom, "properties": props})

    for old in glob.glob(os.path.join(DATA, "*.geojson")):
        os.remove(old)
    index = {"cellSize": CELL, "updated": today, "previous_update": prev_date,
             "new_owner_days": NEW_OWNER_DAYS, "tiles": []}
    for key, feats in sorted(tiles.items()):
        with open(os.path.join(DATA, f"{key}.geojson"), "w", encoding="utf-8") as fh:
            json.dump({"type": "FeatureCollection", "features": feats}, fh, ensure_ascii=False, separators=(",", ":"))
        x, y = map(int, key.split("_"))
        index["tiles"].append({"key": key, "x": x, "y": y, "url": f"/parcel-data/{key}.geojson?v={today}",
                               "count": len(feats)})
    with open(os.path.join(DATA, "index.json"), "w") as fh:
        json.dump(index, fh, indent=1)
    with open(os.path.join(DATA, "changes.json"), "w", encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=0)

    print(f"Wrote {len(tiles)} tiles. {len(changes)} owner changes since {prev_date}.")
    with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a") as fh:
        fh.write(f"### Parcel refresh {today}\n\n{sum(new_unique.values())} parcels, "
                 f"{len(changes)} owner changes since {prev_date}.\n")


if __name__ == "__main__":
    main()
