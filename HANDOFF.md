# The Map App — handoff

## Live site

https://chabadchagrin.github.io/mapapp/

GitHub repository: https://github.com/chabadchagrin/mapapp

## What the app does

This is a mobile-friendly map for finding property owners in selected areas of Cuyahoga and Geauga Counties, Ohio.

- Google Maps is the background map.
- Parcel boundaries are invisible by default, but can be tapped.
- Tapping a property highlights its parcel and opens the owner name, property address, municipality, and county.
- The search field accepts an address or an owner name.
- Choosing a search result moves the map to the property, highlights the parcel, and opens its owner card.
- The circular location button shows the device’s location as a blue pin, with a blue accuracy area. The pin continues to update while the app is open.
- The app offers **Save all parcel data** (about 45 MB) and **Clear parcel download** controls. Saving keeps all locally hosted owner and parcel records on the device; clearing removes only that download.
- Google’s background map and address search still require a connection. For actual offline streets and driving directions, download the needed area in the regular Google Maps phone app before leaving.

## Files that matter

- `index.html` — the entire app. All future edits should be made here.
- `parcel-data/` — the locally hosted parcel GeoJSON tiles plus `index.json`. Do not rename or remove this folder; `index.html` needs it.
- `service-worker.js` — handles the app cache and the full parcel-data download. Keep it in the repository root beside `index.html`.
- `offline-controls.js` — displays and operates the Save all / Clear parcel download controls. Keep it in the repository root beside `index.html`.

## Data coverage

Parcel data includes selected Cuyahoga municipalities (including Chagrin Falls, Chagrin Falls Township, Moreland Hills, Hunting Valley, Bentleyville, and Pepper Pike) and selected Geauga areas (including Russell, South Russell, Bainbridge, Chester/Chesterland, and other nearby areas downloaded earlier). Some locations outside these selected areas will not have a tappable parcel.

## Google Maps setup

The site uses Google Maps JavaScript API, with a key embedded in `index.html`.

- Google Cloud project: `Default Gemini Project` (`gen-lang-client-0385870968`)
- API enabled: Maps JavaScript API
- Key name: `The Map App website key`
- Key restriction: `https://chabadchagrin.github.io/*`
- API restriction: Maps JavaScript API only

The key is intentionally usable in browser code but is restricted to the GitHub Pages website and the Maps JavaScript API. Do not replace it with an unrestricted key.

## Publishing updates

1. Edit `index.html` in this folder.
2. In GitHub repository `chabadchagrin/mapapp`, upload the new `index.html`, `service-worker.js`, and `offline-controls.js` to the repository root and commit directly to `main`.
3. GitHub Pages normally updates https://chabadchagrin.github.io/mapapp/ within a minute or two.

No build process, package install, or server is needed.

## Current UI choices

- No visible parcel grid; a selected parcel only is highlighted.
- No persistent instructional toast.
- Google Maps is used instead of OpenStreetMap because its visual building/map coverage is more familiar to the owner.
