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
- Everything else lives behind the ☰ menu button (top-right) so the map itself stays uncluttered: **Save all parcel data** and **Clear parcel download**.
- "Save all parcel data" saves the owner/parcel records (about 45 MB) to the phone so property lookups — tapping a house and seeing the owner — keep working with no signal, even though the map picture itself will still need a connection to load. Do this once over Wi-Fi before heading out.

## Sept 2026 cleanup — what changed and why

- **Tried switching the basemap to OpenStreetMap/Leaflet, then reverted.** The goal was a map that could be fully cached for offline use (Google's tiles can't be, by Google's own rules). In testing, OpenStreetMap's building outlines turned out to be missing or incomplete on many streets in the coverage area — worse than Google's — so it was reverted. Google Maps is back as the only basemap. The map picture itself now simply requires a live connection; only the owner/parcel data is saved for offline use.
- **The two-button offline panel became one ☰ menu.** The old "Save all parcel data" / "Clear parcel download" buttons floated permanently next to the locate button. They now live behind a small ☰ button next to the search bar, so the map only ever shows three controls: search, ☰, and locate.
- **Fixed the "won't start until you refresh" bug.** Tapping "Save all parcel data" right after opening the app used to fail with "Offline saving will be ready after one refresh" if the service worker hadn't finished starting up yet, with no indication that a refresh would even help. It now waits (up to 5 seconds) for the service worker to be ready and only shows an error if that genuinely times out.
- **Added a proper app icon and install manifest** (`manifest.json`, `icon-192.png`, `icon-512.png`) so the phone can install this as a real app via "Add to Home Screen" / "Install app" in Chrome, instead of just a browser bookmark. Installing it this way also makes Android less likely to silently clear the saved offline data.
- **Removed the unused Cloudflare Worker / GitHub Actions / R2 pipeline.** A previous pass had added a whole backend (Worker + GitHub Action + private R2 bucket) meant to build custom offline map packages on demand. It was never finished being deployed and was never wired into the app — no button in `index.html` ever called it. It's been moved to `_to_delete/` in this folder (along with the Leaflet library files from the reverted experiment above), not deleted outright since this assistant can't delete files on this computer without your say-so. Safe to delete that folder yourself once you've confirmed you don't need anything in it. Two now-empty folders, `.github/workflows` and `.github`, were left behind for the same reason and are also safe to delete.

## Files that matter

- `index.html` — the entire app UI and map logic. All future edits should be made here.
- `offline-controls.js` — builds the ☰ menu's offline-download controls and talks to the service worker.
- `service-worker.js` — handles the app cache and the parcel-data offline download.
- `manifest.json`, `icon-192.png`, `icon-512.png` — enable "Add to Home Screen" install.
- `parcel-data/` — the locally hosted parcel GeoJSON tiles plus `index.json`. Do not rename or remove; `index.html` needs it exactly where it is.

## Data coverage

Parcel data includes selected Cuyahoga municipalities (including Chagrin Falls, Chagrin Falls Township, Moreland Hills, Hunting Valley, Bentleyville, and Pepper Pike) and selected Geauga areas (including Russell, South Russell, Bainbridge, Chester/Chesterland, and other nearby areas downloaded earlier). Locations outside these areas won't have a tappable parcel.

## Google Maps setup

The site uses the Google Maps JavaScript API, with a key embedded in `index.html`.

- Google Cloud project: `Default Gemini Project` (`gen-lang-client-0385870968`)
- API enabled: Maps JavaScript API
- Key name: `The Map App website key`
- Key restriction: `https://chabadchagrin.github.io/*`
- API restriction: Maps JavaScript API only

The key is intentionally usable in browser code but is restricted to the GitHub Pages website and the Maps JavaScript API. Do not replace it with an unrestricted key.

## Publishing updates

1. Edit files in this folder.
2. In GitHub repository `chabadchagrin/mapapp`, upload the changed files to the repository root and commit directly to `main`. A full refresh of the app should include: `index.html`, `offline-controls.js`, `service-worker.js`, `manifest.json`, `icon-192.png`, `icon-512.png`.
3. GitHub Pages normally updates https://chabadchagrin.github.io/mapapp/ within a minute or two.

No build process, package install, or server is needed.

## Testing checklist after any change

**Test on the actual published GitHub Pages URL (or a real local web server), never by double-clicking `index.html` to open it as a `file://` page.** Opening it directly from a folder blocks the browser call that loads the parcel data, so nothing will be clickable — that's true of every version of this app, not a bug.

- Open the site, confirm the map, search, locate button, and ☰ menu all work.
- Tap a house and confirm the owner card appears.
- Tap ☰ → Save all parcel data, and confirm it finishes (watch the toast at the bottom).
- Turn on airplane mode WITHOUT closing or reloading the app, then pan to an already-visited house: it should still tap and show its owner card. This is the realistic "spotty service" case — open the app once with signal, then lose it.
- Force-close the app (or restart the phone) while still offline, then reopen it: expect the whole thing to fail to load. The entire app — map, search, and even the already-saved owner lookups — is bootstrapped by Google's own map script, which itself needs a live connection to fetch. Once that script has loaded and the map is running, losing signal only breaks new map tiles (they'll show gray); it does not affect anything already on screen. But a fresh, cold open of the app with zero signal will not work at all, even with parcel data saved. If that turns out to matter in practice (e.g., your phone dies and restarts mid-route), the fix is a deeper rework — decoupling parcel lookup from Google's script so it works even when the map picture can't load — not something in place today.
