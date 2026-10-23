# Copilot instructions — gym-band

**Before doing anything with deep links, App Links, Digital Asset Links, `assetlinks.json`,
Play Console → Deep links, or the `host` / `autoVerify` / `assetStatements` values:
read `docs/DEEP_LINKS_VERIFICATION.md` and `AGENTS.md` first.**

Summary of that issue (RESOLVED 2026-10-23), so it is not misdiagnosed again:

- Play reported `ambijat.github.io` as *domain ownership not verified* for path `/gym-band/`.
- The app was **never** at fault: `autoVerify="true"`, host, and path prefix are all correct.
- The fix lives in a **separate repo**, `ambijat/ambijat.github.io` (local `../ambijat.github.io/`),
  which serves `/.well-known/assetlinks.json` at the domain root plus a `.nojekyll` file.
  This repo is a project page and cannot serve the root path.
- The red rows were a **missing file plus Google cache latency** (~1 h TTL) — never a manifest bug.
- **Closed 2026-10-23:** Play reports "All links working" and the row reads "Deep linked".
  A transient "not working on Android 11 or older" warning also appeared and cleared itself;
  it was never an invitation to cut a release.

Rest of the project: see `docs/RELEASE_PROTOCOL.md` for the release flow.
