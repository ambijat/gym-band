# AGENTS.md — gym-band

Guidance for any AI agent or developer working in this repository.

## Read first

- **`docs/DEEP_LINKS_VERIFICATION.md`** — how deep link verification works for this app, and why
  Play Console kept reporting `ambijat.github.io` as unverified (resolved 2026-10-23). **Read it
  before** touching `AndroidManifest.xml` intent filters, `strings.xml` (`assetStatements`,
  `hostName`), `twa-manifest.json` (`host`, `fullScopeUrl`, `fingerprints`), or anything about
  `assetlinks.json` / Digital Asset Links / App Links verification. The same misdiagnosis has been
  made once already — do not repeat it.
- `docs/RELEASE_PROTOCOL.md` — the command-line release flow (SDK/JDK, signing, upload).

## Do not

- Do not try to fix deep link verification **inside this repository**. The file Android fetches
  lives at the domain root (`https://ambijat.github.io/.well-known/assetlinks.json`), which is
  served only by the separate repo `ambijat/ambijat.github.io` (local copy:
  `../ambijat.github.io/`). This repo is a GitHub Pages *project* page and cannot serve it.
- Do not delete `../ambijat.github.io/.nojekyll` — Jekyll would drop `.well-known/` and the
  verification would break again.
- Do not cut a release to "force" domain verification. See the doc: it cannot help, because a new
  version ships an identical manifest.
- Do not commit passwords, `local.properties`, keystores, APKs or AABs (see `RELEASE_PROTOCOL.md`).

## Repo facts

- Package: `com.ambijat.bandtraining`. Host: `ambijat.github.io`, scope `/gym-band/`.
- Play App Signing is **on** — the installed APK is signed by Google, not by `android.keystore`.
- Sibling TWAs on the same host (`gym-log`, `gym-companion`) need their own entries in the *same*
  `assetlinks.json` array.
