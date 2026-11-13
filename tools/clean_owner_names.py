#!/usr/bin/env python3
"""Clean up owner names in parcel-data/*.geojson so they read naturally.

    GRISHABER ALLEN G & NICKOLE B          ->  Allen & Nickole Grishaber
    MCCREARY SEAN M & KATHERINE M TRUSTEES ->  Sean & Katherine McCreary
    LAKE LUCERNE CLUB COMPANY THE          ->  The Lake Lucerne Club Company

The county's original text is kept in a new `owner_raw` property, and the
cleaned name goes into `owner_name` (what the app displays). Re-running is
safe: the script always starts again from `owner_raw`.

Usage (from the repository root):
    python3 tools/clean_owner_names.py            # rewrite the files
    python3 tools/clean_owner_names.py --preview  # write owner-name-preview.csv only
"""
import collections
import csv
import glob
import json
import re
import sys

KEEP_MIDDLE_INITIALS = False  # "Allen G. Grishaber" instead of "Allen Grishaber"

# ---------------------------------------------------------------- vocabulary
ORG_WORDS = set("""
LLC L.L.C PLLC LLP LP PLL INC INCORPORATED CORP CORPORATION CO COMPANY LTD LIMITED
PARTNERS PARTNERSHIP ASSOCIATES ASSOC ASSOCIATION ASSN HOLDINGS HOLDING PROPERTIES
PROPERTY INVESTMENTS INVESTMENT INVESTORS REALTY REAL ESTATES DEVELOPMENT DEVELOPERS
GROUP ENTERPRISES ENTERPRISE VENTURES VENTURE CAPITAL FUND MANAGEMENT SERVICES
SERVICING MORTGAGE BANK BANCORP FINANCIAL FEDERAL NATIONAL CHURCH PARISH TEMPLE
SYNAGOGUE CONGREGATION MINISTRIES MINISTRY FELLOWSHIP DIOCESE BISHOP CATHOLIC
LUTHERAN METHODIST PRESBYTERIAN BAPTIST EPISCOPAL CHABAD BOARD COMMISSIONERS
TRUSTEES' COUNTY CITY VILLAGE TOWNSHIP TWP STATE OHIO UNITED AMERICA USA SCHOOL
SCHOOLS DISTRICT ACADEMY UNIVERSITY COLLEGE HOSPITAL CLINIC MEDICAL HEALTH CLUB
COUNTRY GOLF PARK PARKS METROPARKS CEMETERY FOUNDATION SOCIETY INSTITUTE CENTER
CENTRE LIBRARY AUTHORITY DEPARTMENT DEPT COMMISSION CONSERVANCY LAND LANDS FARM
FARMS HOMEOWNERS HOMEOWNER HOA CONDOMINIUM CONDOMINIUMS CONDO OWNERS HOMES
BUILDERS CONSTRUCTION CONTRACTORS RENTALS RENTAL INDUSTRIAL INDUSTRIES
MANUFACTURING SUPPLY SALES MOTORS AUTO TRANSPORTATION RAILROAD RAILWAY UTILITIES
ELECTRIC POWER ENERGY GAS WATER TELEPHONE COMMUNICATIONS ILLUMINATING EDISON
NURSERY NURSERIES GREENHOUSE ORCHARD ORCHARDS DAIRY KENNEL STABLES EQUESTRIAN
RESTAURANT TAVERN HOTEL INN STORAGE PLAZA MALL SQUARE CROSSING COMMONS VILLAS
APARTMENTS APTS TOWERS OFFICE OFFICES BUILDING LODGE POST LEGION VFW YMCA YWCA
CAMP SCOUTS COUNCIL GOVERNMENT REUTILIZATION ESTATE' TRUST'
""".split())
ORG_PHRASES = ["REAL ESTATE", "LAND BANK", "OF AMERICA", "STATE OF", "BOARD OF",
               "CITY OF", "VILLAGE OF", "COUNTY OF", "TOWNSHIP OF", "D B A", "DBA"]

SUFFIXES = {"JR": "Jr.", "SR": "Sr.", "II": "II", "III": "III", "IV": "IV"}
SURNAME_PREFIXES = {"MC", "MAC", "ST", "VAN", "VON", "DE", "DEL", "DELLA", "DI", "DA",
                    "LA", "LE", "DU", "VANDER", "VANDEN", "TEN", "O", "D", "DES"}

# Legal / ownership tags dropped from people's names.
TAG_RE = re.compile(r"""
    \b(?:SUCCESSOR\s+|SUCC\.?\s+)?
    (?:CO-?\s?TRUSTEES?|CO-?\s?TRSTEES|C-?TRUSTEES?|CO-?\s?TRS?\.?|TRUSTEES?|TTEES?|TRS?\.?|
       TOD|ETAL|ET\s+AL|ET\s+UX|ET\s+VIR|JTWROS|SURV(?:IVORSHIP)?|L/E|LIFE\s+ESTATE)
    (?=\W|$)
""", re.X)


def clean_text(s):
    s = (s or "").upper().replace(" ", " ")
    s = re.sub(r"\([^)]*\)", lambda m: " " if TAG_RE.search(m.group()) else m.group()[1:-1], s)
    s = re.sub(r"(?<=\w)-(?=(?:CO-?)?TR|TRUSTEE|ETAL|TTEE)", " ", s)  # "ROBERT S-TR-ETAL"
    s = re.sub(r"\s-\s?(?=[A-Z])", " ", s)                              # "MEGAN B. -TRUSTEE"
    s = re.sub(r"\bAND\b", "&", s)
    s = re.sub(r"\s+", " ", s).strip(" ,.-&")
    return s


# ------------------------------------------------------------ capitalization
def cap_word(w, org=False):
    if not w:
        return w
    if "-" in w:
        return "-".join(cap_word(p, org) for p in w.split("-"))
    if "'" in w:
        a, b = w.split("'", 1)
        return cap_word(a, org) + "'" + (b.lower() if len(b) == 1 else cap_word(b, org))
    if not org and len(w) > 3 and w.startswith("MC"):
        return "Mc" + w[2].upper() + w[3:].lower()
    if len(w) == 1:
        return w.upper()
    return w[0].upper() + w[1:].lower()


ORG_UPPER = {"LLC", "LLP", "LP", "PLL", "PLLC", "USA", "US", "HOA", "YMCA", "YWCA", "VFW",
             "II", "III", "IV", "NA", "RV", "PC", "DDS", "MD", "CPA", "LTD"}
ORG_ABBR = {"INC": "Inc.", "CO": "Co.", "CORP": "Corp.", "ASSOC": "Assoc.", "ASSN": "Assn.",
            "TWP": "Twp.", "LTD": "Ltd.", "DEPT": "Dept.", "ST": "St.", "MT": "Mt.",
            "DBA": "dba", "BROS": "Bros."}
ORG_SMALL = {"OF", "THE", "AND", "FOR", "AT", "IN", "ON", "TO", "A", "AN", "BY"}


def title_org(s):
    s = re.sub(r"\bD B A\b", "DBA", s)
    words = [w for w in re.split(r"\s+", s.replace(",", " ").replace(".", " ")) if w]
    if len(words) > 1 and words[-1] == "THE":
        words = ["THE"] + words[:-1]
    out = []
    for i, w in enumerate(words):
        if w == "S" and out and i > 0:            # "HOMEOWNER S" -> "Homeowner's"
            out[-1] += "'s"
            continue
        if w == "&":
            out.append("&")
        elif w in ORG_ABBR:
            out.append(ORG_ABBR[w])
        elif w in ORG_UPPER:
            out.append(w)
        elif i > 0 and w in ORG_SMALL:
            out.append(w.lower())
        elif re.search(r"\d", w) or (len(w) <= 4 and not re.search(r"[AEIOUY]", w)):
            out.append(w)                          # "BCM", "PLJ", "3RD"
        else:
            out.append(cap_word(w, org=True))
    return " ".join(out)


# ------------------------------------------------------------ name statistics
def learn(raws):
    """Count how often each word appears as a surname vs. a given name."""
    sur, giv = collections.Counter(), collections.Counter()
    for r in raws:
        s = clean_text(r)
        if is_org(s):
            continue
        first = s.split("&")[0]
        if "," in first:
            a, b = first.split(",", 1)
            for w in a.split():
                sur[w] += 1
            for w in b.split()[:1]:
                giv[w] += 1
        else:
            ws = first.replace(",", "").split()
            if len(ws) >= 2:
                sur[ws[0]] += 1
                giv[ws[1]] += 1
    return sur, giv


def is_org(s):
    words = set(re.split(r"[\s,.]+", s))
    if words & ORG_WORDS or any(p in s for p in ORG_PHRASES) or re.search(r"\d", s):
        return True
    return False


# --------------------------------------------------------------- people names
class Person:
    def __init__(self, surname, given, suffix=None):
        self.surname, self.given, self.suffix = surname, given, suffix

    def first(self):
        parts = [cap_word(w) + ("." if len(w) == 1 else "") for w in self.given
                 if KEEP_MIDDLE_INITIALS or len(w) > 1 or w is self.given[0]]
        return " ".join(parts)

    def last(self):
        return " ".join(self.surname_words())

    def surname_words(self):
        out, ws = [], list(self.surname)
        while ws:
            w = ws.pop(0)
            if w == "MC" and ws:
                out.append(cap_word("MC" + ws.pop(0)))
            elif w in ("O", "D") and ws:
                out.append(w + "'" + cap_word(ws.pop(0)))
            elif w == "ST":
                out.append("St.")
            else:
                out.append(cap_word(w))
        return out

    def full(self):
        return " ".join(x for x in [self.first(), self.last(), SUFFIXES.get(self.suffix, "")] if x)


def split_suffix(words):
    suffix = None
    rest = []
    for w in words:
        if w in SUFFIXES and rest:
            suffix = w
        else:
            rest.append(w)
    return rest, suffix


def split_surname_first(words):
    """'MC KENZIE RYAN' -> (['MC','KENZIE'], ['RYAN'])"""
    n = 1
    while n < len(words) - 1 and words[n - 1] in SURNAME_PREFIXES:
        n += 1
    return words[:n], words[n:]


def p_given(w, sur, giv):
    g, s = giv[w], sur[w]
    return (g + 0.3) / (g + s + 1)   # unknown words lean surname: first names are a small set


def parse_people(s, sur, giv):
    s = re.sub(r"\b(?:AKA|FKA|A/K/A|F/K/A)\b[^&]*", "", s)
    segments = [seg.strip(" ,.") for seg in s.split("&")]
    segments = [seg for seg in segments if seg]
    if not segments:
        return None
    people = []
    for i, seg in enumerate(segments):
        has_comma = "," in seg
        words, suffix = split_suffix([w for w in re.split(r"[\s,.]+", seg) if w])
        if not words:
            continue
        if has_comma:
            a, b = seg.split(",", 1)
            sw, _ = split_suffix(a.replace(".", " ").split())
            gw, suffix2 = split_suffix(b.replace(".", " ").replace(",", " ").split())
            people.append(Person(sw, gw, suffix or suffix2))
            continue
        if i == 0:
            if len(words) == 1:
                return None
            sw, gw = split_surname_first(words)
            people.append(Person(sw, gw, suffix))
            continue
        prev = people[-1].surname if people else []
        surname_first = False
        if len(words) >= 2:
            if words[0] == (prev[0] if prev else None):
                surname_first = True
            elif words[0] in SURNAME_PREFIXES and len(words) >= 3:
                surname_first = True
            elif p_given(words[0], sur, giv) < 0.4 and p_given(words[1], sur, giv) > 0.45:
                surname_first = True
        if surname_first:
            sw, gw = split_surname_first(words)
            people.append(Person(sw, gw, suffix))
        else:
            people.append(Person(prev, words, suffix))
    people = [p for p in people if p.given]
    return people or None


def format_people(people):
    # drop exact duplicates left over from AKA removal
    seen, uniq = set(), []
    for p in people:
        key = (tuple(p.surname), p.first())
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    people = uniq
    same = len({tuple(p.surname) for p in people}) == 1 and not any(p.suffix for p in people)
    if same:
        firsts = [p.first() for p in people]
        return join_list(firsts) + " " + people[0].last()
    return join_list([p.full() for p in people])


def join_list(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " & " + items[-1]


# ------------------------------------------------------------------- cleaner
def clean_name(raw, sur, giv):
    s = clean_text(raw)
    if not s:
        return ""
    estate = False
    m = (re.match(r"^ESTATE OF (.+)$", s) or re.match(r"^(.+?) ESTATE OF$", s)
         or re.match(r"^(.+?) (?:ESTATE|EST)$", s))
    if m and not is_org(m.group(1)):
        estate, s = True, m.group(1)
    trust = False
    m = re.match(r"^(?:THE )?(.+?) (?:REVOCABLE |REV |LIVING |FAMILY )*TRUST(?: THE)?$", s)
    if m and len(m.group(1).split()) >= 2 and not is_org(m.group(1)) and "," not in m.group(1) \
            and p_given(m.group(1).split()[0], sur, giv) > 0.6:
        return title_org(TAG_RE.sub(" ", s))   # already first-name-first: "David W Wangler Trust"
    if m and len(m.group(1).split()) >= 2 and not is_org(m.group(1)):
        trust, s = True, m.group(1)
    elif re.search(r"\bTRUST$", s):
        return title_org(TAG_RE.sub(" ", s))   # "Delta Trust"
    s = TAG_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,.-&")
    if is_org(s):
        return title_org(s)
    people = parse_people(s, sur, giv)
    if not people:
        return title_org(s)
    out = format_people(people)
    if estate:
        out = "Estate of " + out
    if trust:
        out = "The " + out + " Trust"
    return out


# ---------------------------------------------------------------------- main
def main():
    preview = "--preview" in sys.argv
    files = sorted(glob.glob("parcel-data/*.geojson"))
    data = {f: json.load(open(f, encoding="utf-8")) for f in files}
    raws = []
    for d in data.values():
        for ft in d["features"]:
            p = ft["properties"]
            raws.append(p.get("owner_raw", p.get("owner_name")) or "")
    sur, giv = learn(raws)

    rows = []
    for f, d in data.items():
        for ft in d["features"]:
            p = ft["properties"]
            raw = p.get("owner_raw", p.get("owner_name")) or ""
            new = clean_name(raw, sur, giv)
            rows.append((raw, new))
            if not preview:
                # keep key order: owner_name stays where it was, owner_raw right after
                props = {}
                for k, v in p.items():
                    if k == "owner_raw":
                        continue
                    props[k] = new if k == "owner_name" else v
                    if k == "owner_name":
                        props["owner_raw"] = raw
                ft["properties"] = props
        if not preview:
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False, separators=(",", ":"))

    with open("owner-name-preview.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["original", "cleaned"])
        w.writerows(sorted(set(rows)))
    print(f"{len(rows)} parcels, {len(set(rows))} distinct names"
          f"{' (preview only)' if preview else ' rewritten'}; see owner-name-preview.csv")


if __name__ == "__main__":
    main()
