#!/usr/bin/env python3
"""Second look at Geauga sources; writes inspect/report2.md."""
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(__file__))
from inspect_sources import dbf_fields_and_rows, GEA_SAMPLES  # noqa: E402

out = []


def w(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    out.append(line)


def get(url, timeout=1800):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 mapapp-refresh"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def links():
    w("## Links on realestate.geauga.oh.gov\n")
    html = get("https://realestate.geauga.oh.gov/").decode("utf8", "replace")
    found = []
    for href, text in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        t = re.sub(r"<[^>]+>|\s+", " ", text).strip()
        if re.search(r"shape|extract|gis|download|hub|rest|zip|parcel", t + href, re.I):
            found.append((t, urllib.parse.urljoin("https://realestate.geauga.oh.gov/", href)))
    for t, h in found:
        w(f"- {t} -> {h}")
    return found


def shapefile(found):
    url = next((h for t, h in found if re.search(r"parcel shapefile", t, re.I)), None)
    w("\n## Monthly parcel shapefile:", url)
    if not url:
        return
    data = get(url)
    z = zipfile.ZipFile(io.BytesIO(data))
    w("zip bytes:", len(data))
    for i in z.infolist():
        w(f"- {i.filename} {i.file_size:,}")
    for i in z.infolist():
        if i.filename.lower().endswith(".dbf"):
            n, fields, firsts, rows = dbf_fields_and_rows(z.read(i), set(GEA_SAMPLES), 6)
            w(f"\n### {i.filename}: {n} records\nfields: " + ", ".join(f"{a}({b}{c})" for a, b, c in fields))
            for r in rows or firsts:
                w("```\n" + json.dumps({k: v for k, v in r.items() if v}, indent=1) + "\n```")
        if i.filename.lower().endswith(".prj"):
            w(i.filename, z.read(i).decode("latin1")[:400])


def hub():
    w("\n## Geauga hub search")
    for q in ["parcel", "parcels", "tax parcel"]:
        try:
            u = ("https://geauga-county-hub-geauga.hub.arcgis.com/api/search/v1/collections/all/items?"
                 + urllib.parse.urlencode({"q": q, "limit": 20}))
            d = json.loads(get(u, 120))
            for f in d.get("features", []):
                p = f.get("properties", {})
                w(f"- {p.get('title')} | {p.get('type')} | {p.get('url')} | id={f.get('id')}")
            break
        except Exception as e:  # noqa
            w("hub search failed", q, e)


def xlsx_rows(data, want, max_rows=5):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True)
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True)
        header = next(it, None)
        w(f"\nsheet {ws.title!r} header: {header}")
        shown = 0
        for i, row in enumerate(it):
            if i < 2 or any(str(v) in want for v in row if v is not None):
                w("  ", row)
                shown += 1
            if shown >= max_rows + 2:
                break


def gis_extract():
    w("\n## GIS Extract spreadsheet")
    z = zipfile.ZipFile(io.BytesIO(get("https://realestate.geauga.oh.gov/api/Document/GISExtract.zip")))
    for n in z.namelist():
        w(f"\n### {n}")
        xlsx_rows(z.read(n), set(GEA_SAMPLES))


def xml_records(zf, name, want, max_show=6, scan_limit=None):
    w(f"\n### {name}")
    shown, firsts, n = 0, 0, 0
    with zf.open(name) as fh:
        depth = 0
        for ev, el in ET.iterparse(fh, events=("start", "end")):
            if ev == "start":
                depth += 1
                continue
            depth -= 1
            if depth == 1:  # a record
                n += 1
                rec = {c.tag: (c.text or "").strip() for c in el}
                hit = any(v in want for v in rec.values())
                if firsts < 2 or (hit and shown < max_show):
                    w(f"<{el.tag}> " + json.dumps({k: v for k, v in rec.items() if v}))
                    if hit:
                        shown += 1
                    else:
                        firsts += 1
                el.clear()
                if scan_limit and n >= scan_limit:
                    break
    w(f"records scanned: {n}")


def public_records():
    w("\n## Public Records Extract tables")
    path = "/tmp/pr.zip"
    with open(path, "wb") as fh:
        fh.write(get("https://realestate.geauga.oh.gov/api/Document/PublicRecordsExtract.zip"))
    zf = zipfile.ZipFile(path)
    w("\n### File Layout.xlsx")
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(zf.read("File Layout.xlsx")), read_only=True)
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        w(f"sheet {ws.title!r}: {len(rows)} rows")
        for r in rows:
            if r and any(isinstance(v, str) and re.match(r"^Parcel( Owner| Transfer| Location)?$", v.strip()) for v in r):
                w("  ", r)
        keep = [r for r in rows if r and any(isinstance(v, str) and re.search(r"Transfer|Owner|Location|^Parcel$", v) for v in r[:2])]
        for r in keep[:120]:
            w("  ", r)
    want = set(GEA_SAMPLES)
    for name in ["Parcel Owner.xml", "Parcel Transfer.xml", "Parcel Location.xml", "Parcel.xml"]:
        try:
            xml_records(zf, name, want)
        except Exception as e:  # noqa
            w(name, "failed", repr(e))


def main():
    found = []
    for fn in [links, lambda: shapefile(found), hub, gis_extract, public_records]:
        try:
            r = fn()
            if fn is links:
                found.extend(r)
        except Exception as e:  # noqa
            w(f"\n**{getattr(fn, '__name__', 'step')} failed:** {e!r}")
    os.makedirs("inspect", exist_ok=True)
    with open("inspect/report2.md", "w") as fh:
        fh.write("# Source inspection 2\n\n" + "\n".join(out) + "\n")


if __name__ == "__main__":
    main()
