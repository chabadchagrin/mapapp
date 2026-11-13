#!/usr/bin/env python3
"""Third look: Geauga parcel geometry service; writes inspect/report3.md."""
import json, os, urllib.parse, urllib.request
SVC = "https://gcgis.geauga.oh.gov/parcel/rest/services/AzureParcels/Parcels/FeatureServer/0"
S = ["01-109800", "21-001850", "02-065110", "27-000100"]
out = []
def w(*a):
    s = " ".join(map(str, a)); print(s, flush=True); out.append(s)
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "mapapp-refresh"}), timeout=300).read()
try:
    m = json.loads(get(SVC + "?f=json"))
    w("maxRecordCount:", m.get("maxRecordCount"), "formats:", m.get("supportedQueryFormats"),
      "pagination:", (m.get("advancedQueryCapabilities") or {}).get("supportsPagination"))
    w("fields:", ", ".join(f"{f['name']}({f['type'][13:]})" for f in m.get("fields", [])))
    w("count:", json.loads(get(SVC + "/query?where=1%3D1&returnCountOnly=true&f=json")))
    for f in [x["name"] for x in m.get("fields", []) if x["type"] == "esriFieldTypeString"]:
        q = urllib.parse.urlencode({"where": f"{f} IN ({','.join(repr(s) for s in S)})", "outFields": "*",
                                    "returnGeometry": "false", "f": "json"})
        try:
            d = json.loads(get(SVC + "/query?" + q))
        except Exception:
            continue
        if d.get("features"):
            w(f"\nmatched on field {f}:")
            for ft in d["features"]:
                w(json.dumps({k: v for k, v in ft["attributes"].items() if v not in (None, "")}))
            q = urllib.parse.urlencode({"where": f"{f}='{S[0]}'", "outFields": f, "outSR": 4326, "f": "geojson"})
            w("geojson sample:", get(SVC + "/query?" + q).decode()[:600])
            break
    for fld in [x["name"] for x in m.get("fields", [])]:
        if any(k in fld.lower() for k in ("town", "jur", "muni", "dist", "twp", "city")):
            q = urllib.parse.urlencode({"where": "1=1", "outFields": fld, "returnDistinctValues": "true",
                                        "returnGeometry": "false", "f": "json"})
            try:
                vals = sorted({str(ft["attributes"][fld]) for ft in json.loads(get(SVC + "/query?" + q))["features"]})
                w(f"\ndistinct {fld} ({len(vals)}):", vals[:60])
            except Exception as e:
                w("distinct failed", fld, e)
except Exception as e:
    w("failed:", repr(e))
os.makedirs("inspect", exist_ok=True)
open("inspect/report3.md", "w").write("# Source inspection 3\n\n" + "\n".join(out) + "\n")
