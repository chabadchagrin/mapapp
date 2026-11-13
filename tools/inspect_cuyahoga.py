#!/usr/bin/env python3
"""Find a Cuyahoga parcel layer with current transfer dates; writes inspect/cuyahoga.md."""
import json, os, urllib.parse, urllib.request
ROOT = "https://gis.cuyahogacounty.gov/server/rest/services"
out = []
def w(*a):
    s = " ".join(map(str, a)); print(s, flush=True); out.append(s)
def get(u, p=None):
    if p: u += "?" + urllib.parse.urlencode(p)
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "mapapp"}), timeout=120).read())
def services(folder=""):
    d = get(f"{ROOT}/{folder}".rstrip("/"), {"f": "json"})
    res = [(s["name"], s["type"]) for s in d.get("services", [])]
    for f in d.get("folders", []):
        try: res += services(f)
        except Exception as e: w("folder fail", f, e)
    return res
svcs = services()
w("## services"); [w("-", n, t) for n, t in svcs]
w("\n## parcel-like layers with transfer dates")
for name, typ in svcs:
    if typ not in ("MapServer", "FeatureServer"): continue
    try: d = get(f"{ROOT}/{name}/{typ}/layers", {"f": "json"})
    except Exception as e: continue
    for lyr in d.get("layers", []) + d.get("tables", []):
        flds = {f["name"].lower(): f["name"] for f in lyr.get("fields") or []}
        date_f = next((flds[k] for k in flds if "transfer_date" in k or k in ("sale_date", "saledate", "last_sale_date", "transferdate")), None)
        own_f = next((flds[k] for k in flds if "owner" in k), None)
        if not date_f: continue
        url = f"{ROOT}/{name}/{typ}/{lyr['id']}"
        try:
            st = get(url + "/query", {"where": "1=1", "outStatistics": json.dumps([{"statisticType": "max", "onStatisticField": date_f, "outStatisticFieldName": "mx"}, {"statisticType": "count", "onStatisticField": date_f, "outStatisticFieldName": "n"}]), "f": "json"})
            a = st["features"][0]["attributes"]
        except Exception as e:
            a = {"err": str(e)[:100]}
        w(f"\n- {url} | {lyr['name']} | geom={lyr.get('geometryType')} | date={date_f} owner={own_f} | stats={a} | max={lyr.get('maxRecordCount')}")
        w("  fields:", ", ".join(f["name"] for f in lyr.get("fields") or [])[:1500])
os.makedirs("inspect", exist_ok=True)
open("inspect/cuyahoga.md", "w").write("\n".join(out) + "\n")
