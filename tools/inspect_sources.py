#!/usr/bin/env python3
"""One-time look at the county data sources; writes inspect/report.md.

Run by .github/workflows/inspect-sources.yml (GitHub can reach the county
servers; the report is committed back so it can be read without the logs).
"""
import csv
import io
import json
import os
import struct
import sys
import urllib.parse
import urllib.request
import zipfile

CUY = "https://gis.cuyahogacounty.gov/server/rest/services/Open_Data_Parcels/MapServer/1"
GEA_GIS = "https://realestate.geauga.oh.gov/api/Document/GISExtract.zip"
GEA_PR = "https://realestate.geauga.oh.gov/api/Document/PublicRecordsExtract.zip"
CUY_SAMPLES = ["93213009", "94121009", "91321008", "92108007", "88225005", "87229030"]
GEA_SAMPLES = ["01-109800", "21-001850", "02-065110", "29-012300", "11-019200", "27-000100"]

out = []


def w(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    out.append(line)


def get(url, timeout=600):
    req = urllib.request.Request(url, headers={"User-Agent": "mapapp-refresh/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def cuyahoga():
    w("## Cuyahoga\n")
    meta = json.loads(get(CUY + "?f=json"))
    w("maxRecordCount:", meta.get("maxRecordCount"))
    w("fields:", ", ".join(f["name"] for f in meta.get("fields", [])))
    for where in [
        "parcel_id IN (%s)" % ",".join("'%s'" % p for p in CUY_SAMPLES),
        "parcelpin IN (%s)" % ",".join("'%s-%s-%s'" % (p[:3], p[3:5], p[5:]) for p in CUY_SAMPLES),
        "parcelpin IN (%s)" % ",".join("'%s'" % p for p in CUY_SAMPLES),
    ]:
        q = urllib.parse.urlencode({"where": where, "outFields": "*", "returnGeometry": "false", "f": "json"})
        try:
            d = json.loads(get(CUY + "/query?" + q))
        except Exception as e:  # noqa
            w("query failed:", where, e)
            continue
        feats = d.get("features", [])
        w(f"\nwhere {where!r}: {len(feats)} features {d.get('error','')}")
        for f in feats[:6]:
            a = {k: v for k, v in f["attributes"].items() if v not in (None, "", 0)}
            w("```\n" + json.dumps(a, indent=1)[:3000] + "\n```")
        if feats:
            break
    for city in ["CHAGRIN FALLS", "BENTLEYVILLE", "MORELAND HILLS", "CHAGRIN FALLS TOWNSHIP",
                 "HUNTING VALLEY", "PEPPER PIKE"]:
        q = urllib.parse.urlencode({"where": f"par_city='{city}'", "returnCountOnly": "true", "f": "json"})
        try:
            w(f"count par_city={city}:", json.loads(get(CUY + "/query?" + q)).get("count"))
        except Exception as e:  # noqa
            w("count failed", city, e)


def dbf_fields_and_rows(data, want_key_values, max_rows=4):
    n = struct.unpack("<I", data[4:8])[0]
    hlen, rlen = struct.unpack("<HH", data[8:12])
    fields, pos = [], 32
    while data[pos] != 0x0D:
        name = data[pos:pos + 11].split(b"\0")[0].decode("latin1")
        ftype = chr(data[pos + 11]); flen = data[pos + 16]
        fields.append((name, ftype, flen)); pos += 32
    rows, firsts = [], []
    for i in range(n):
        off = hlen + i * rlen
        rec = data[off + 1: off + rlen]
        vals, p = {}, 0
        for name, ftype, flen in fields:
            vals[name] = rec[p:p + flen].decode("latin1").strip(); p += flen
        if i < 2:
            firsts.append(vals)
        if any(v in want_key_values for v in vals.values()):
            rows.append(vals)
            if len(rows) >= max_rows:
                break
    return n, fields, firsts, rows


def geauga(url, label):
    w(f"\n## Geauga — {label}\n")
    data = get(url, timeout=1800)
    w("zip bytes:", len(data))
    z = zipfile.ZipFile(io.BytesIO(data))
    for i in z.infolist():
        w(f"- {i.filename}  {i.file_size:,} bytes")
    for i in z.infolist():
        name = i.filename.lower()
        if name.endswith(".dbf"):
            n, fields, firsts, rows = dbf_fields_and_rows(z.read(i), set(GEA_SAMPLES))
            w(f"\n### {i.filename}: {n} records")
            w("fields:", ", ".join(f"{a}({b}{c})" for a, b, c in fields))
            for r in (rows or firsts):
                w("```\n" + json.dumps({k: v for k, v in r.items() if v}, indent=1)[:2500] + "\n```")
        elif name.endswith((".txt", ".csv", ".tsv", ".htm", ".html")) and i.file_size > 0:
            raw = z.read(i).decode("latin1", "replace")
            lines = raw.splitlines()
            w(f"\n### {i.filename}: {len(lines)} lines")
            w("```\n" + "\n".join(lines[:3])[:2000] + "\n```")
            hits = [l for l in lines if any(s in l for s in GEA_SAMPLES[:3])][:6]
            if hits:
                w("sample-parcel rows:\n```\n" + "\n".join(hits)[:3000] + "\n```")
        elif name.endswith(".prj"):
            w(f"\n{i.filename}: " + z.read(i).decode("latin1")[:300])
        elif name.endswith((".xlsx", ".xls")):
            w(f"\n{i.filename}: (spreadsheet layout file, {i.file_size} bytes)")


def main():
    for fn, args in [(cuyahoga, ()), (geauga, (GEA_GIS, "GIS Extract")), (geauga, (GEA_PR, "Public Records Extract"))]:
        try:
            fn(*args)
        except Exception as e:  # noqa
            w(f"\n**{fn.__name__}{args[1:] if args else ''} failed:** {e!r}")
    os.makedirs("inspect", exist_ok=True)
    with open("inspect/report.md", "w") as fh:
        fh.write("# Source inspection\n\n" + "\n".join(out) + "\n")


if __name__ == "__main__":
    main()
