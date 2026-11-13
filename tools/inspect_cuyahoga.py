#!/usr/bin/env python3
"""Compare owner fields in Cuyahoga Parcel Fabric vs Open Data layer; writes inspect/cuyahoga2.md."""
import json, os, urllib.parse, urllib.request
FAB = "https://gis.cuyahogacounty.gov/server/rest/services/CCFO/Parcel_Fabric_Taxparcels/FeatureServer/0"
OD = "https://gis.cuyahogacounty.gov/server/rest/services/Open_Data_Parcels/MapServer/1"
out = []
def w(*a):
    s = " ".join(map(str, a)); print(s, flush=True); out.append(s)
def get(u, p):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u + "?" + urllib.parse.urlencode(p), headers={"User-Agent": "mapapp"}), timeout=120).read())
m = get(FAB, {"f": "json"})
w("fabric fields with lengths:", [(f["name"], f.get("length")) for f in m["fields"] if f["name"] in ("parcel_id","parcel_owner","second_owner","grantee","mail_name","par_addr_all","parcel_city","last_transfer_date","last_sales_amount","update_date")])
w("formats", m.get("supportedQueryFormats"), "pagination", (m.get("advancedQueryCapabilities") or {}).get("supportsPagination"))
cities = ["BENTLEYVILLE","CHAGRIN FALLS","CHAGRIN FALLS TOWNSHIP","HUNTING VALLEY","MORELAND HILLS","PEPPER PIKE"]
for c in cities:
    n = get(FAB + "/query", {"where": f"parcel_city='{c}'", "returnCountOnly": "true", "f": "json"})
    w("fabric count", c, n.get("count"))
d = get(FAB + "/query", {"where": "parcel_city IN (%s) AND last_transfer_date > DATE '2026-04-01'" % ",".join(f"'{c}'" for c in cities),
                         "outFields": "parcel_id,parcel_owner,second_owner,grantee,grantor,mail_name,par_addr_all,parcel_city,last_transfer_date,last_sales_amount",
                         "orderByFields": "last_transfer_date DESC", "resultRecordCount": 40, "returnGeometry": "false", "f": "json"})
w("\nrecent transfers in our cities:", len(d.get("features", [])), d.get("error", ""))
ids = []
for f in d.get("features", []):
    a = f["attributes"]; ids.append(a["parcel_id"]); w(json.dumps(a))
if ids:
    o = get(OD + "/query", {"where": "parcel_id IN (%s)" % ",".join(f"'{i}'" for i in ids[:40]), "outFields": "parcel_id,deeded_owner,transfer_date", "returnGeometry": "false", "f": "json"})
    w("\nopen-data owner for same parcels:")
    for f in o.get("features", []): w(json.dumps(f["attributes"]))
long = get(FAB + "/query", {"where": "parcel_city='PEPPER PIKE' AND second_owner IS NOT NULL AND second_owner <> ''", "outFields": "parcel_id,parcel_owner,second_owner,grantee,mail_name", "resultRecordCount": 15, "returnGeometry": "false", "f": "json"})
w("\nsamples with second_owner:")
for f in long.get("features", []): w(json.dumps(f["attributes"]))
os.makedirs("inspect", exist_ok=True)
open("inspect/cuyahoga2.md", "w").write("\n".join(out) + "\n")
