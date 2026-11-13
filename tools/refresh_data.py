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
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clean_owner_names as names  # noqa: E402

DATA = "parcel-data"
CELL = 0.025
PRECISION = 6  # decimal places in coordinates (~10 cm)

# "Parcel Fabric" is updated daily; the Open_Data_Parcels layer stopped updating in March 2026.
CUY_URL = "https://gis.cuyahogacounty.gov/server/rest/services/CCFO/Parcel_Fabric_Taxparcels/FeatureServer/0"
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
GEA_RECORDS = "https://realestate.geauga.oh.gov/api/Document/PublicRecordsExtract.zip"  # daily, ~370 MB


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
    where = ("parcel_city IN (%s) OR parcel_city LIKE 'CHAGRIN FALLS T%%'"
             % ",".join("'%s'" % c for c in CUY_CITIES))
    out = []
    for f in fetch_all(CUY_URL, where, ["*"], "ObjectID"):
        a = f.get("properties") or {}
        pid = (a.get("parcel_id") or "").replace("-", "").strip()
        if not pid or not f.get("geometry"):
            continue
        city = (a.get("parcel_city") or "").strip().upper()
        if city.startswith("CHAGRIN FALLS T"):
            city = "CHAGRIN FALLS TOWNSHIP"
        out.append((f["geometry"], {
            "source_county": "Cuyahoga",
            "jurisdiction": city,
            "parcel_id": pid,
            "owner_raw": re.sub(r"\s+", " ", a.get("parcel_owner") or "").strip(),
            "property_address": a.get("par_addr_all") or "",
            "property_city": city,
            "property_zip": str(int(float(a["parcel_zip"]))) if a.get("parcel_zip") else "",
            "sale_date": epoch_ms_to_date(a.get("last_transfer_date")),
            "sale_price": money(a.get("last_sales_amount")),
            **extras(
                use=land_use(first(a, "tax_luc", "ext_luc"), first(a, "tax_luc_description", "ext_luc_description") or ""),
                built=first(a, "year_built", "yr_built", "res_year_built", "yearbuilt"),
                occ=occupancy(a.get("par_addr_all"), " ".join(x for x in [a.get("mail_addr_street"), a.get("mail_unit_no")] if x),
                              a.get("mail_name"), a.get("mail_city")),
                owner=a.get("parcel_owner")),
            "_grantor": a.get("grantor") or "",
            "_mail_name": a.get("mail_name") or "",
        }))
    return out


def extras(use, built, occ, owner):
    label, home = use
    out = {"use": label, "home": None if home is None else int(bool(home)),
           "occ": occ[0], "mail": occ[1], "otype": owner_type(owner)}
    try:
        y = int(str(built).strip()[:4]) if built else 0
        if 1700 < y <= dt.date.today().year + 1:
            out["built"] = y
    except ValueError:
        pass
    return out


def fetch_geauga():
    print("Geauga…", flush=True)
    where = " OR ".join(f"TaxDist LIKE '{c}-%'" for c in GEA_DISTRICTS)
    fields = ["PARCEL_ID", "Oname1", "LOCATION_A", "LOCATION_C", "LOCATION_Z", "Sale_Date",
              "Sale_Amt", "TaxDist", "Par_Status", "PropClass", "HomeFlag", "YearBuilt",
              "MailName1", "MailStreet", "MailCity"]
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
            **extras(
                use=land_use(a.get("PropClass"), "",
                             {"YES": True, "NO": False}.get((a.get("HomeFlag") or "").strip().upper())),
                built=a.get("YearBuilt"),
                occ=occupancy(a.get("LOCATION_A"), a.get("MailStreet"), a.get("MailName1"), a.get("MailCity")),
                owner=a.get("Oname1")),
            "_grantor": "",
            "_mail_name": a.get("MailName1") or "",
        }))
    return out


# ------------------------------------------------- land use / occupancy / owner
EXEMPT = {"61": "Federal land", "62": "State land", "63": "County land", "64": "City / village land",
          "65": "School", "66": "Park", "67": "College / private school", "68": "Charity / church",
          "69": "Cemetery"}


def land_use(code, desc="", home_flag=None):
    """Ohio land-use code (3 digits) -> (short label, has a home)."""
    code = re.sub(r"\D", "", str(code or ""))[:3]
    d = (desc or "").upper()
    label, home = None, None
    if len(code) == 3:
        c = int(code)
        if 100 <= c < 200:
            label, home = ("Farmland", False) if "VACANT" in d or c == 100 else ("Farm", True)
        elif 200 <= c < 300:
            label, home = "Mineral rights", False
        elif 300 <= c < 400:
            label, home = "Industrial", False
        elif c == 400:
            label, home = "Vacant commercial land", False
        elif 401 <= c <= 403:
            label, home = "Apartments", True
        elif 400 < c < 500:
            label, home = "Commercial", False
        elif 500 <= c <= 509:
            label, home = "Vacant lot", False
        elif 510 <= c <= 519:
            label, home = "Single-family home", True
        elif c == 520:
            label, home = "Two-family home", True
        elif c == 530:
            label, home = "Three-family home", True
        elif 550 <= c <= 559:
            label, home = "Condo", True
        elif c == 560:
            label, home = "Mobile home", True
        elif 500 <= c < 600:
            label, home = "Other residential (no house)", False
        elif 600 <= c < 700:
            label, home = EXEMPT.get(code[:2], "Tax-exempt land"), False
            if c == 685:
                label = "Church"
    if label is None:
        if "VACANT" in d:
            label, home = "Vacant land", False
        elif d:
            label, home = d.title()[:40], None
    if home_flag is not None:          # Geauga says directly whether there's a dwelling
        home = home_flag
        if home and label in ("Vacant lot", "Other residential (no house)", None):
            label = "Home"
    return label, home


def street_key(addr):
    """'490  WALTERS RD, CHAGRIN FALLS…' -> '490 WALTERS' (house number + first street word)."""
    a = re.sub(r"[^A-Z0-9 ]", " ", (addr or "").upper().split(",")[0])
    w = a.split()
    if len(w) >= 2 and w[0].isdigit() and w[0] != "0":
        nxt = [x for x in w[1:] if x not in ("N", "S", "E", "W", "NORTH", "SOUTH", "EAST", "WEST")]
        return w[0] + " " + (nxt[0] if nxt else w[1])
    return None


def occupancy(prop_addr, mail_street, mail_name, mail_city):
    """('here'|'po'|'away', text shown on the card or '')."""
    ms = (mail_street or "").upper()
    if not ms.strip():
        return None, ""
    if re.search(r"\bP\.? ?O\.? ?BOX\b|\bBOX \d", ms):
        return "po", f"PO Box, {mail_city.title()}" if mail_city else "PO Box"
    pk, mk = street_key(prop_addr), street_key(ms)
    if pk and mk and pk == mk:
        return "here", ""
    return "away", (mail_name or "", ms, mail_city or "")


def fmt_street(s):
    s = re.sub(r"\s+", " ", s or "").strip().title()
    s = re.sub(r"(\d)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), s)
    return re.sub(r"\bC/O\b", "c/o", s, flags=re.I)


GOV_RE = re.compile(r"(?<![\w-])(CITY|VILLAGE|TOWNSHIP|TWP|COUNTY|STATE OF|BOARD OF|COMMISSIONERS|PARK DISTRICT|"
                    r"METROPARKS|EDUCATION|LIBRARY|UNITED STATES|USA|DEPT|DEPARTMENT|AUTHORITY|"
                    r"LAND BANK|REUTILIZATION|TRUSTEES)(?![\w-])")
REL_RE = re.compile(r"(?<![\w-])(CHURCH|PARISH|TEMPLE|SYNAGOGUE|CONGREGATION|DIOCESE|BISHOP|MINISTR\w*|FELLOWSHIP|"
                    r"CHABAD|LUTHERAN|METHODIST|PRESBYTERIAN|BAPTIST|EPISCOPAL|CATHOLIC|CEMETERY)(?![\w-])")
HOA_RE = re.compile(r"(?<![\w-])(HOMEOWNERS?|HOME OWNERS|ASSOC|ASSN|ASSOCIATION|CONDOMINIUMS?|CONDO|COLONY)(?![\w-])")
BIZ_RE = re.compile(r"(?<![\w-])(LLC|L L C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LP|LLP|PLL|PARTNERS|"
                    r"PARTNERSHIP|HOLDINGS?|PROPERTIES|PROPERTY|INVESTMENTS?|REALTY|BANK|DEVELOPMENT|"
                    r"ENTERPRISES|GROUP|BUILDERS|NVR|VENTURES?|CAPITAL|MANAGEMENT|RENTALS?)(?![\w-])")


def owner_type(raw):
    """'' for people (including family trusts) or company / government / hoa / religious."""
    n = " ".join(re.split(r"[\s,.]+", (raw or "").upper()))   # keeps 'CO-TRS' as one token
    if not n.strip():
        return ""
    if REL_RE.search(n):
        return "religious"
    if re.search(r"(?<![\w-])(SCHOOLS?|ACADEMY|COLLEGE|UNIVERSITY)(?![\w-])", n):
        return "school"
    if HOA_RE.search(n):
        return "hoa"
    if BIZ_RE.search(n):
        return "company"
    if GOV_RE.search(n) and not re.search(r"\bTRUSTEES?\b", n.replace("TWP TRUSTEES", "TWP")):
        return "government"
    if re.search(r"\bTWP TRUSTEES\b|\bTOWNSHIP TRUSTEES\b", n):
        return "government"
    return ""


def first(a, *keys):
    for k in keys:
        if a.get(k) not in (None, "", 0, "0"):
            return a[k]
    return None


def geauga_sellers():
    """parcel number -> (date, price, seller) of its latest transfer, from the Auditor's daily extract."""
    print("Geauga transfer records…", flush=True)
    path = "/tmp/geauga_records.zip"
    req = urllib.request.Request(GEA_RECORDS, headers={"User-Agent": "chabadchagrin-mapapp-refresh"})
    with urllib.request.urlopen(req, timeout=1800) as r, open(path, "wb") as fh:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)
    zf = zipfile.ZipFile(path)
    name = next(n for n in zf.namelist() if n.lower() == "parcel transfer.xml")
    best = {}
    with zf.open(name) as fh:
        depth = 0
        for ev, el in ET.iterparse(fh, events=("start", "end")):
            if ev == "start":
                depth += 1
                continue
            depth -= 1
            if depth != 1:
                continue
            rec = {k.lower(): (v or "").strip() for k, v in el.attrib.items()}
            rec.update({c.tag.lower(): (c.text or "").strip() for c in el})
            el.clear()
            pid = rec.get("parcel_number", "")
            seller = rec.get("seller_listed_name") or rec.get("seller_deeded_name") or ""
            date = (rec.get("date_conveyed") or "")[:10]
            try:
                seq = int(rec.get("sequence") or 0)
            except ValueError:
                seq = 0
            if not pid:
                continue
            key = (date, seq)
            if pid not in best or key > best[pid][0]:
                best[pid] = (key, money(rec.get("consideration")), seller)
    os.remove(path)
    print(f"  {len(best)} parcels with transfers", flush=True)
    return {pid: v[1:] for pid, v in best.items()}


def person_from_mail(mail_name, owner_raw):
    """A person's name hidden in the tax-bill name, e.g. 'SHELTER HILL FARM LLC PETER DRAGO' -> 'PETER DRAGO'."""
    m = re.sub(r"\s+", " ", mail_name or "").strip()
    if not m or norm_owner(m) == norm_owner(owner_raw):
        return ""
    tail = re.split(r"(?<![\w-])(?:L\.?L\.?C\.?|INC\.?|LTD\.?|CORP\.?)(?![\w-])[\s,.]*", m, flags=re.I)[-1]
    tail = re.sub(r"^(C/O|ATTN:?)\s+", "", tail.strip(), flags=re.I)
    if len(tail.split()) >= 2 and owner_type(tail) == "":
        return tail
    return ""


def likely_owner(p):
    """For company-owned parcels: (raw name, reason) of the person most likely behind the company."""
    if p.get("otype") != "company":
        return "", ""
    who = person_from_mail(p.get("_mail_name"), p["owner_raw"])
    if who:
        return who, "tax bill"
    g = (p.get("_grantor") or "").strip()
    if g and not p.get("sale_price") and owner_type(g) == "" and norm_owner(g) != norm_owner(p["owner_raw"]):
        year = (p.get("sale_date") or "")[:4]
        return g, f"deeded it to the company{' in ' + year if year else ''} for $0"
    return "", ""


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


def surnames(raw):
    """First word of each owner segment: 'SMITH JOHN & DOE JANE' -> {SMITH, DOE}."""
    out = set()
    for seg in re.split(r"&|\bAND\b", (raw or "").upper()):
        words = [w for w in re.split(r"[^A-Z]+", seg) if len(w) > 1 and w not in ("MC", "DE", "DI", "LA", "VAN", "ST", "THE")]
        if words:
            out.add(words[0])
    return out


def change_kind(old_raw, new_raw, price):
    """sale: money changed hands; family: same surname (retitled, into a trust, TOD...); transfer: other."""
    if surnames(old_raw) & surnames(new_raw):
        return "family"
    if price and price >= 10000:
        return "sale"
    return "transfer"


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
    stats = {}
    try:
        sellers = geauga_sellers()
        matched = 0
        for _, p in records:
            if p["source_county"] == "Geauga" and p["parcel_id"] in sellers:
                _, price, seller = sellers[p["parcel_id"]]
                p["_grantor"] = seller
                matched += 1
        stats["geauga_transfer_parcels"] = len(sellers)
        stats["geauga_matched"] = matched
    except Exception as e:  # noqa — the rest of the refresh still runs without it
        print(f"WARNING: Geauga transfer records unavailable: {e!r}", flush=True)
        stats["geauga_transfer_error"] = repr(e)[:200]

    # ---- sanity check against last time
    new_counts = collections.Counter(p["source_county"] for _, p in records)
    new_unique = collections.Counter(c for c, _ in {(p["source_county"], p["parcel_id"]) for _, p in records})
    old_unique = collections.Counter(c for c, _ in prev)
    for county in ("Cuyahoga", "Geauga"):
        print(f"{county}: {new_counts[county]} features, {new_unique[county]} parcels (was {old_unique[county]})")
        if old_unique[county] and new_unique[county] < 0.95 * old_unique[county]:
            sys.exit(f"ABORT: {county} returned {new_unique[county]} parcels, last time {old_unique[county]}.")
    new_j = collections.Counter((p["source_county"], p["jurisdiction"]) for p in {k: p for _, p in records for k in [(p["source_county"], p["parcel_id"])]}.values())
    old_j = collections.Counter((p["source_county"], p["jurisdiction"]) for p in prev.values())
    for key, n in sorted(old_j.items()):
        print(f"  {key[0]} / {key[1]}: {new_j[key]} (was {n})")
        if n >= 20 and new_j[key] < 0.9 * n:
            sys.exit(f"ABORT: {key} returned {new_j[key]} parcels, last time {n}.")

    # ---- names
    sur, giv = names.learn([p["owner_raw"] for _, p in records])

    # ---- change detection
    changes, seen = [], set()
    for _, p in records:
        key = (p["source_county"], p["parcel_id"])
        old = prev.get(key)
        p["owner_name"] = names.clean_name(p["owner_raw"], sur, giv)
        lo, why = likely_owner(p)
        if lo:
            p["likely"] = names.clean_name(lo, sur, giv)
            p["likely_why"] = why
        if p.get("occ") == "away" and isinstance(p.get("mail"), tuple):
            mn, ms, mc = p["mail"]
            mname = names.clean_name(mn, sur, giv) if mn.strip() else ""
            p["mail"] = ", ".join(x for x in [mname, fmt_street(ms), mc.strip().title()] if x)
        if old:
            old_raw = old.get("owner_raw", old.get("owner_name")) or ""
            if norm_owner(old_raw) != norm_owner(p["owner_raw"]) and p["owner_raw"]:
                p["prev_owner"] = names.clean_name(old_raw, sur, giv) if old_raw else ""
                p["changed_on"] = today
                p["change_kind"] = change_kind(old_raw, p["owner_raw"], p["sale_price"])
                if key not in seen:
                    seen.add(key)
                    changes.append({
                        "county": p["source_county"], "parcel_id": p["parcel_id"],
                        "detected": today, "address": p["property_address"],
                        "jurisdiction": p["jurisdiction"],
                        "kind": p["change_kind"], "from": old_raw, "to": p["owner_raw"],
                        "sale_date": p["sale_date"], "sale_price": p["sale_price"],
                    })
            else:
                for k in ("prev_owner", "changed_on", "change_kind"):
                    if old.get(k):
                        p[k] = old[k]

    stats["company_parcels"] = sum(1 for _, p in records if p.get("otype") == "company")
    stats["likely_owner_tax_bill"] = sum(1 for _, p in records if p.get("likely_why") == "tax bill")
    stats["likely_owner_deed"] = sum(1 for _, p in records if (p.get("likely_why") or "").startswith("deeded"))
    stats["homes"] = sum(1 for _, p in records if p.get("home") == 1)
    stats["not_homes"] = sum(1 for _, p in records if p.get("home") == 0)
    stats["occ"] = dict(collections.Counter(p.get("occ") or "none" for _, p in records))
    log["refreshes"].append({"date": today, "previous": prev_date, "parcels": sum(new_unique.values()),
                             "owner_changes": len(changes)})
    log["changes"] = changes + log.get("changes", [])

    # ---- tiles
    tiles = collections.defaultdict(list)
    for geom, p in records:
        props = {k: p[k] for k in ("source_county", "jurisdiction", "parcel_id", "owner_name", "owner_raw",
                                   "property_address", "property_city", "property_zip")}
        for k in ("sale_date", "sale_price", "prev_owner", "changed_on", "change_kind",
                  "use", "home", "built", "occ", "mail", "otype", "likely", "likely_why"):
            if p.get(k) not in (None, ""):
                props[k] = p[k]
        x0, y0, x1, y1 = bbox(geom)
        for x in range(math.floor(x0 / CELL), math.floor(x1 / CELL) + 1):
            for y in range(math.floor(y0 / CELL), math.floor(y1 / CELL) + 1):
                tiles[f"{x}_{y}"].append({"type": "Feature", "geometry": geom, "properties": props})

    for old in glob.glob(os.path.join(DATA, "*.geojson")):
        os.remove(old)
    index = {"cellSize": CELL, "updated": today, "previous_update": prev_date,
             "new_owner_days": NEW_OWNER_DAYS, "stats": stats, "tiles": []}
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
