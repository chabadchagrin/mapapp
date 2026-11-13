# The Map App — handoff

## Live site

https://chabadchagrin.github.io/mapapp/

GitHub repository: https://github.com/chabadchagrin/mapapp

## What the app does

A phone-friendly map for canvassing in selected areas of Cuyahoga and Geauga Counties, Ohio. Built to run entirely on one phone, with as few on-screen controls as possible.

- Google Maps is the background map (unchanged from before — its imagery and building outlines need a live connection to load; that's a Google restriction, not something this app can work around).
- Parcel boundaries are invisible by default but tappable. Tapping a property opens the owner name, address, municipality, and county.
- The search bar (top) accepts an address or an owner name.
- The only other always-visible control is the circular locate button (bottom-right), which shows your location as a blue dot with a blue accuracy ring and keeps updating while the app is open.
- Everything else lives behind the ☰ menu button (top-right) so the map itself stays uncluttered: **Highlight recent sales**, the date the owner data was last refreshed, **Save all parcel data** and **Clear parcel download**.
- The owner card shows the cleaned-up owner name, "Owner since … · bought for $…" (or "Deed recorded … (no sale price)" when the last deed had no price, e.g. a move into a trust), and a **NEW OWNER** badge with the previous owner for 120 days after a change of hands is detected.
- "Save all parcel data" saves the owner/parcel records (about 30 MB) to the phone so property lookups — tapping a house and seeing the owner — keep working with no signal, even though the map picture itself will still need a connection to load. Do this once over Wi-Fi before heading out.

## Sept 2026 cleanup — what changed and why

- **Tried switching the basemap to OpenStreetMap/Leaflet, then reverted.** The goal was a map that could be fully cached for offline use (Google's tiles can't be, by Google's own rules). In testing, OpenStreetMap's building outlines turned out to be missing or incomplete on many streets in the coverage area — worse than Google's — so it was reverted. Google Maps is back as the only basemap. The map picture itself now simply requires a live connection; only the owner/parcel data is saved for offline use.
- **The two-button offline panel became one ☰ menu.** The old "Save all parcel data" / "Clear parcel download" buttons floated permanently next to the locate button. They now live behind a small ☰ button next to the search bar, so the map only ever shows three controls: search, ☰, and locate.
- **Fixed the "won't start until you refresh" bug.** Tapping "Save all parcel data" right after opening the app used to fail with "Offline saving will be ready after one refresh" if the service worker hadn't finished starting up yet, with no indication that a refresh would even help. It now waits (up to 5 seconds) for the service worker to be ready and only shows an error if that genuinely times out.
- **Added a proper app icon and install manifest** (`manifest.json`, `icon-192.png`, `icon-512.png`) so the phone can install this as a real app via "Add to Home Screen" / "Install app" in Chrome, instead of just a browser bookmark. Installing it this way also makes Android less likely to silently clear the saved offline data.
- **Removed the unused Cloudflare Worker / GitHub Actions / R2 pipeline.** A previous pass had added a whole backend (Worker + GitHub Action + private R2 bucket) meant to build custom offline map packages on demand. It was never finished being deployed and was never wired into the app — no button in `index.html` ever called it. It's been moved to `_to_delete/` in this folder (along with the Leaflet library files from the reverted experiment above), not deleted outright since this assistant can't delete files on this computer without your say-so. Safe to delete that folder yourself once you've confirmed you don't need anything in it. Two now-empty folders, `.github/workflows` and `.github`, were left behind for the same reason and are also safe to delete.

## Monthly data refresh (Nov 2026)

Owner data refreshes itself on the 1st of every month via the GitHub Action `.github/workflows/refresh-data.yml`, which runs `tools/refresh_data.py`. To refresh sooner: GitHub → Actions → "Refresh parcel data" → **Run workflow** (also linked from the app's ☰ menu as "refresh now").

- **Sources:** Cuyahoga — `CCFO/Parcel_Fabric_Taxparcels` map service (updated daily; the older `Open_Data_Parcels` layer stopped updating in March 2026, don't go back to it). Geauga — `AzureParcels/Parcels` map service from Geauga GIS. Both are public; nothing is downloaded by hand.
- **Areas covered** are listed at the top of `tools/refresh_data.py` (6 Cuyahoga cities, 9 Geauga areas by tax-district code). Add an area there.
- **Names** are cleaned by `tools/clean_owner_names.py` (drops TRUSTEE/TOD/ETAL/AKA, first names first, normal capitalization). The county's original text is kept as `owner_raw`, and owner search matches either.
- **Changes of hands:** each run compares owners with the previous data. Changes get `prev_owner`, `changed_on`, `change_kind` (`sale` / `transfer` / `family` — family = same surname, e.g. retitled into a trust; no badge) and are appended to `parcel-data/changes.json`.
- **Who lives here (added Nov 2026):** each parcel also gets `use` (from the Ohio land-use code: single-family home, condo, vacant lot, commercial, public land…), `home` (1 = has a dwelling; parcels with 0 are grayed out in the app), `built` (Geauga only), `occ` (`here` = tax bill goes to the property, so the owner lives there; `away` / `po` with the tax-bill address in `mail`), and `otype` (company / government / school / hoa / religious; blank = people).
- **Likely owner behind a company** (`likely`, `likely_why`): a person named on the tax bill, or a person who deeded the property to the company for $0 (the previous owner on the last deed — Cuyahoga's `grantor` field; Geauga's seller from `Parcel Transfer.xml` in the Auditor's daily Public Records Extract). When the company paid for the property, the seller is not shown, since they're not the owner. Ohio's Secretary of State doesn't record LLC owners (only a statutory agent), so the app's "Look up company" button just copies the name and opens https://businesssearch.ohiosos.gov.
- **Safety:** the run stops without publishing if a county or any area returns noticeably fewer parcels than last time.
- After a refresh, phones see "New owner data is available" in the ☰ menu; tap Save all parcel data again to update the offline copy.

## Files that matter

- `index.html` — the entire app UI and map logic. All future edits should be made here.
- `offline-controls.js` — builds the ☰ menu's offline-download controls and talks to the service worker.
- `service-worker.js` — handles the app cache and the parcel-data offline download.
- `manifest.json`, `icon-192.png`, `icon-512.png` — enable "Add to Home Screen" install.
- `parcel-data/` — parcel GeoJSON tiles, `index.json` (tile list + data date) and `changes.json` (owner-change log). Generated by the refresh; don't edit by hand.
- `tools/refresh_data.py`, `tools/clean_owner_names.py`, `.github/workflows/refresh-data.yml` — the monthly refresh.

## Data coverage

Cuyahoga (6 areas, matched on the county's `parcel_city` field): Bentleyville, Chagrin Falls, Chagrin Falls Township, Hunting Valley, Moreland Hills, Pepper Pike.

Geauga (9 areas, matched on the first two digits of the county's `TaxDist` field, which are also the first two digits of the parcel number): Auburn Twp (01), Bainbridge Twp (02, 03), Chardon Twp (06–09), City of Chardon (10), Chester Twp (11), Munson Twp (21, 22), Russell Twp (26, 28), Hunting Valley Village (27), South Russell Village (29).

About 36,500 parcels total. Each parcel is written into every 0.025° map tile its outline touches, so the tile files contain more records than there are parcels — that's intentional.

## Where the data comes from (and how to find it again)

Both counties publish their parcels as free, public ArcGIS map services. `tools/refresh_data.py` queries them page by page (2,000 records per request) and asks for GeoJSON in latitude/longitude (`outSR=4326`).

### Cuyahoga County

- **Service in use:** https://gis.cuyahogacounty.gov/server/rest/services/CCFO/Parcel_Fabric_Taxparcels/FeatureServer/0 ("Parcel Fabric Taxparcels", run by the Cuyahoga County Fiscal Office). Updated daily.
- **Fields used:** `parcel_id` (8 digits, no dashes), `parcel_owner` (owner as deeded), `par_addr_all` (full address), `parcel_city`, `parcel_zip`, `last_transfer_date` (milliseconds since 1970), `last_sales_amount`.
- Other useful fields there if ever wanted: `grantor` (seller), `second_owner`, `mail_name` and mailing address, `tax_market_total`, `parcel_acreage`, land-use codes.
- **Do not use** `Open_Data_Parcels/MapServer/1` — it looks the same but stopped updating in March 2026 (the September 2026 download came from it, which is why its sales were months old).
- **If the service moves:** the full list of the county's services is at https://gis.cuyahogacounty.gov/server/rest/services (add `?f=json` for machine-readable). Look for a parcel layer with an owner field and a transfer-date field, and check it's current by asking for the newest transfer date: `…/query?where=1=1&outStatistics=[{"statisticType":"max","onStatisticField":"last_transfer_date","outStatisticFieldName":"mx"}]&f=json`. In Nov 2026 the county also had current copies at `MyPlace/Full_Map_Parcel_Fabric/MapServer/0` and a no-outline table at `CCGIS/Parcel_RP_CAMA_Table/MapServer/1`.
- Manual lookup of one property: MyPlace, https://myplace.cuyahogacounty.gov

### Geauga County

- **Service in use:** https://gcgis.geauga.oh.gov/parcel/rest/services/AzureParcels/Parcels/FeatureServer/0 ("Parcels", Geauga County GIS). Current to within a few days.
- **Fields used:** `PARCEL_ID` (e.g. `01-109800`), `Oname1` (owner), `LOCATION_A` / `LOCATION_C` / `LOCATION_Z` (address, city, ZIP), `Sale_Date` (text, `MM-DD-YYYY`), `Sale_Amt` (text with commas), `TaxDist` (e.g. `01-AUBURN TWP-KENSTON LSD`).
- Other useful fields: `MailName1` and mailing address, `MktTotVal` (market value), `YearBuilt`, `LivingArea`, `ACRES`, `Sale_Valid`.
- **If the service moves:** search the county's GIS hub, https://geauga-county-hub-geauga.hub.arcgis.com (search "parcels"), or its API: `https://geauga-county-hub-geauga.hub.arcgis.com/api/search/v1/collections/all/items?q=parcel`. The hub also has yearly "Parcel History" services (e.g. 2021–2025) if past owners are ever needed.
- **Backup downloads** (no outlines, but owner and sale info) on the Auditor's site, https://realestate.geauga.oh.gov, under "Real Estate & GIS Data Downloads":
  - GIS Extract (daily, ~12 MB zip with one spreadsheet, `Parcel GIS.xlsx`: parcel number, Listed Name, Date Conveyed, Consideration, address, values): https://realestate.geauga.oh.gov/api/Document/GISExtract.zip
  - Public Records Extract (daily, ~370 MB zip of XML tables incl. `Parcel Transfer.xml` full sales history and `Parcel Owner.xml`; layout in `File Layout.xlsx`): https://realestate.geauga.oh.gov/api/Document/PublicRecordsExtract.zip
  - Yearly complete transfer reports (Excel) are linked on the same page.

### Testing a source without changing the app

The workspace Claude uses can't always reach county servers directly, but GitHub's servers can. The pattern used in Nov 2026: put a small Python script in `tools/`, add a temporary workflow that runs it on a side branch and commits its output (a report file) back to that branch, read the report, then delete both. To try the real refresh safely, push changes to a branch named `data-refresh` — the refresh workflow runs there too, and publishes only to that branch.

## Passcode screen

The app opens with a simple passcode screen (added Nov 2026). Each device asks once and then remembers it (browser storage); clearing site data or using a new device asks again. It also tells search engines not to list the site. It is a curtain, not a lock: the passcode check runs in the page and the data files and this repository are still public. A real lock (encrypted data published from a private repo) was discussed and deferred.

To change the passcode: compute its SHA-256 (e.g. `printf 'NEWCODE' | sha256sum`) and replace the `H='…'` value in the passcode script near the top of `index.html`. Every device will ask for the new code.

## Google Maps setup

The site uses the Google Maps JavaScript API, with a key embedded in `index.html`.

- Google Cloud project: `Default Gemini Project` (`gen-lang-client-0385870968`)
- API enabled: Maps JavaScript API
- Key name: `The Map App website key`
- Key restriction: `https://chabadchagrin.github.io/*`
- API restriction: Maps JavaScript API only

The key is intentionally usable in browser code but is restricted to the GitHub Pages website and the Maps JavaScript API. Do not replace it with an unrestricted key.

## Publishing updates

1. Edit the files (in a clone of the repository, or directly on GitHub).
2. Commit to `main`. The service worker loads app files network-first, so phones pick up changes the next time they open the app with signal — no cache-version bump needed.
3. GitHub Pages normally updates https://chabadchagrin.github.io/mapapp/ within a minute or two.

No build process, package install, or server is needed.

## Testing checklist after any change

**Test on the actual published GitHub Pages URL (or a real local web server), never by double-clicking `index.html` to open it as a `file://` page.** Opening it directly from a folder blocks the browser call that loads the parcel data, so nothing will be clickable — that's true of every version of this app, not a bug.

- Open the site, confirm the map, search, locate button, and ☰ menu all work.
- Tap a house and confirm the owner card appears.
- Tap ☰ → Save all parcel data, and confirm it finishes (watch the toast at the bottom).
- Turn on airplane mode WITHOUT closing or reloading the app, then pan to an already-visited house: it should still tap and show its owner card. This is the realistic "spotty service" case — open the app once with signal, then lose it.
- Force-close the app (or restart the phone) while still offline, then reopen it: expect the whole thing to fail to load. The entire app — map, search, and even the already-saved owner lookups — is bootstrapped by Google's own map script, which itself needs a live connection to fetch. Once that script has loaded and the map is running, losing signal only breaks new map tiles (they'll show gray); it does not affect anything already on screen. But a fresh, cold open of the app with zero signal will not work at all, even with parcel data saved. If that turns out to matter in practice (e.g., your phone dies and restarts mid-route), the fix is a deeper rework — decoupling parcel lookup from Google's script so it works even when the map picture can't load — not something in place today.
