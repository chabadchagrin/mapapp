# Custom offline-map package service

This adds the backend for the “save this map area” feature. It has not been deployed yet.

## What it does

1. The map sends the current visible area to the Cloudflare Worker.
2. The Worker starts the GitHub Action in this repository.
3. The Action extracts a compact PMTiles road map for that area and saves it in the private R2 bucket.
4. The phone downloads that finished package and uses it without service.

## Required configuration before deployment

- A GitHub fine-grained token limited to this repository, with **Actions: read and write**. Store it in the Worker as `GITHUB_TOKEN`.
- An R2 API token limited to the `mapapp-offline-packs` bucket. Store its credentials in GitHub Secrets as `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`.
- GitHub Variables: `R2_S3_ENDPOINT` and `OFFLINE_BASEMAP_URL`.
- Cloudflare Worker Secrets: `OFFLINE_ACCESS_CODE`, `GITHUB_TOKEN`, and `GITHUB_REPOSITORY` (`chabadchagrin/mapapp`).

The access code prevents the public map page from letting strangers create downloads. The worker permits only modest areas in northeast Ohio and a maximum zoom of 14.

## Before publishing

The Action and Worker are source code only until the tokens and variables above are created. Do not make the R2 bucket public.
