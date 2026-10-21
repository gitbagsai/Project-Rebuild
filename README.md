# Project Rebuild · Android installable web app

Project Rebuild v1.0.1 packaged as a **static, installable PWA** for GitHub Pages. This copy uses the approved silver-and-green **R** app icon and opens in Android standalone mode after installation (no browser address bar). It caches the local app shell and exercise images for offline use after a successful first visit.

## Privacy & data safety

- **This repository contains app code and artwork only.** Workout history, meal records, and the app assessment are stored in the browser's local storage on your own phone, not uploaded to this repository.
- The GitHub Pages site is **publicly available** if published, even though its local app data is not shared. Don't commit exports, API keys, or personal logs.
- **Export JSON from your existing app** before moving to this URL. Your old Chrome HTML file, Netlify-hosted copy and GitHub Pages copy have **separate storage**. Open the new site, import your saved JSON, and verify a few previous workouts before deleting anything.
- Avoid incognito mode, clearing Chrome/site storage, uninstalling Chrome or changing the GitHub Pages address without exporting first. Keep occasional backup copies off-device.
- Offline access depends on the service worker installing and caching assets after an online visit; verify it in airplane mode before relying on it.

## Publish with GitHub Pages

1. Create a **public** GitHub repository named `project-rebuild`. (Free GitHub Pages works with public repositories.)
2. Upload **the contents** of this extracted folder to the repository root, retaining the `assets/exercises/` folder tree. Don't upload the ZIP file alone; GitHub Pages will not unpack it.
3. Go to repository **Settings → Pages → Build and deployment → Deploy from a branch → main / (root) → Save**.
4. After GitHub finishes deployment, open `https://YOUR_USERNAME.github.io/project-rebuild/` in Chrome on your Android phone.
5. Chrome menu (⋮) → **Add to Home screen → Install**. Remove the old blue HTML shortcut only after verifying the new icon and backup import.

The relative manifest scope and start URL work when the site is published under a GitHub project subpath.

## AI Coach limitation

GitHub Pages only hosts static files. The offline rules-based Coach and workout tracking work, but the live AI Coach feature in this release still calls a same-origin **Netlify Function** (`/.netlify/functions/coach`). That function **does not exist on GitHub Pages**, so online AI Coach and AI-powered nutrition will not work from this site until a separate secure API service is configured, with correct endpoint, authentication and CORS. Do not put an OpenAI key in public client-side JavaScript.

This build was checked for JavaScript syntax and relative PWA asset paths; it has **not** been deployed to the user's account or tested installed on their phone.
