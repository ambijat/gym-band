# Deep link verification (TWA / Digital Asset Links)

**Status: CLOSED 2026-10-23.** Play Console → Deep links now reports **"All links working"** and the
web link row `/gym-band/` → `ambijat.github.io` reads **Deep linked**.
Last updated: 2026-10-23 (UTC). Owner: ambijat. Read this before touching anything related to deep
links, `assetlinks.json`, the Play Console "Deep links" page, or `twa-manifest.json` hosts — the
misdiagnosis below is easy to repeat.

---

## Symptom

Play Console → **Grow → Deep links**, app version 4 (1.2), path `/gym-band/`:

```
ambijat.github.io
  1 domain not verified
  1 link not working
  -> Digital Asset Links JSON file failed
```

Earlier the same dialog also reported **"JSON content type failed"**; that row has since cleared.

## Root cause (confirmed, not a hypothesis)

Android and Play fetch exactly one URL per host, and it is always the **domain root**:

```
https://ambijat.github.io/.well-known/assetlinks.json
```

That URL returned **404**. Two independent reasons:

1. **No repo named `ambijat.github.io` existed.** The host root of a GitHub Pages *user site*
   is served only by a repo with that exact name. `gym-band` is a **project page** and can only
   serve `/gym-band/**`, so a copy at `/gym-band/.well-known/assetlinks.json` would be ignored
   by Android regardless.
2. **A `.well-known` directory needs `.nojekyll`.** GitHub Pages runs Jekyll by default, which
   silently excludes dot-directories. Without `.nojekyll` the file is committed but never published.

The app was never at fault: `android:autoVerify="true"`, `host="ambijat.github.io"`,
`pathPrefix="/gym-band/"` and the `assetStatements` site string were all correct throughout.

---

## What was done

Created **`github.com/ambijat/ambijat.github.io`** (local: `ANDROIDWORKS/ambijat.github.io/`,
deliberately *outside* this repo — it is a separate Pages user site):

| File | Purpose |
| --- | --- |
| `.well-known/assetlinks.json` | the file Play fetches; 3 fingerprints, package `com.ambijat.bandtraining` |
| `.nojekyll` | **load-bearing** — without it the dot-directory is not published |
| `index.html` | landing page so the root is not bare |
| `README.md` | documents which fingerprint is which, and how to add future apps |

Commits: `8a8ce00` (initial site), `0e0ca7c` (third fingerprint requested by Play).

### Certificates

| SHA-256 | What it is |
| --- | --- |
| `22:88:68:5D:58:63:7C:FF:8B:F8:78:50:37:81:0A:84:06:86:CE:40:CD:80:C5:F9:2F:C1:5C:62:6A:61:16:CF` | **Play App Signing** key (Play › Setup › App integrity). This is what signs the installed APK. |
| `CB:AB:28:99:90:AD:D1:84:F7:8B:E5:DC:DE:9E:30:E3:64:AE:8F:8E:19:5D:AC:36:5A:B4:2B:5F:46:B2:4E:A3` | Upload key — local `ANDROIDWORKS/gym-band/android.keystore`, alias `bandtrainingkey`. |
| `22:88:6B:5D:58:63:7C:FF:8B:F8:78:50:37:81:0A:84:06:86:CE:40:CD:80:C5:F9:2F:C1:5C:62:6A:61:16:CF` | **Requested by Play Console.** Identical to the app-signing key except byte 3 (`68` → `6B`). |

**Note on the third value:** two genuinely different certificates cannot produce SHA-256 hashes
that differ in a single byte — a hash changes completely when the input changes. So this is almost
certainly a Play Console artifact, *not* a real second signing key (a Play App Signing reset would
yield a wholly unrelated fingerprint). It is listed anyway because extra entries are harmless
(Android accepts the link if **any** listed fingerprint matches) and Play's checker diffs its
expected array against what is served.

---

## Verified state

```
$ curl -sS -D- https://ambijat.github.io/.well-known/assetlinks.json
HTTP/2 200
content-type: application/json; charset=utf-8
-> 3 fingerprints served, in the order Play requested
```

Google's own validator (the backend Android and Play both use) returned:

```json
{ "linked": true }   for 22:88:68:…  (Play App Signing)
{ "linked": true }   for CB:AB:28:…  (upload key)
```

## Resolution

Play Console now reports **"This domain passed ownership verification"** for `ambijat.github.io`.
The red "Domain ownership not verified" row is gone. Nothing in the app changed — only the served
file.

Two findings worth keeping:

- **The third fingerprint did not matter.** Play verified while Google's `statements:list` still
  returned only the 2-entry snapshot (`22:88:68` + `CB:AB:28`), i.e. the real certificates. This
  confirms `22:88:6B:…` was a Play Console artifact. It is harmless but should be dropped at the
  next natural edit; do not churn the file just to remove it.
- **The earlier "JSON content type failed" was purely the 404's HTML error page.** It cleared by
  itself once the file existed.

### The Android 11 warning (appeared mid-fix, then cleared)

For a few minutes Play showed:

> **Associated links not working on Android 11 or older** — "This domain passed ownership
> verification, but other domains in your app are failing…"

It cleared by itself once verification completed. Why it was noise:

- The app declares exactly **one** web host (`ambijat.github.io`): verified in `AndroidManifest.xml`
  line 174 (`@string/hostName`, generated from `app/build.gradle` `twaManifest.hostName`) and in
  all four merged/packaged manifests. There is no second domain, so the "other domains" clause is
  boilerplate for this app.
- The accurate part: Android 11 and lower verify **all-or-nothing at install/update time**. Devices
  holding build 4 keep the failed verdict until they install a newer version. Android 12+ re-checks
  automatically, and Android 15+ re-checks in the background (up to 7 days).
- Therefore an **optional `versionCode` bump** is the only thing that refreshes existing installs —
  best folded into the next real release, not published on its own.

## If it ever regresses — do these in order

1. Check the real certificate is linked (this is the reliable test — `statements:list` can still
   return 2 statements even when Play says verified):

   ```bash
   curl -sS -G 'https://digitalassetlinks.googleapis.com/v1/assetlinks:check' \
     --data-urlencode 'source.web.site=https://ambijat.github.io' \
     --data-urlencode 'relation=delegate_permission/common.handle_all_urls' \
     --data-urlencode 'target.android_app.package_name=com.ambijat.bandtraining' \
     --data-urlencode 'target.android_app.certificate.sha256_fingerprint=22:88:68:5D:58:63:7C:FF:8B:F8:78:50:37:81:0A:84:06:86:CE:40:CD:80:C5:F9:2F:C1:5C:62:6A:61:16:CF'
   # expect: {"linked": true}
   ```

2. Click **Recheck verification** in Play Console **once**. Do not re-edit `assetlinks.json` and
   do not click repeatedly — each edit or redundant recheck restarts the cache clock.

3. Ground truth on a device:

   ```bash
   adb shell pm get-app-links com.ambijat.bandtraining
   # expect:  ambijat.github.io: verified
   adb shell pm verify-app-links --re-verify com.ambijat.bandtraining   # force a re-fetch
   ```

4. **Do not cut a release for this.** A new version ships an identical manifest and cannot change
   the server-side verdict. A `versionCode` bump only helps *existing* installs, because Android 14
   and lower re-verify on install/update only (Android 15+ re-checks in the background, up to 7 days).
   Fold the bump into the next real release.

5. If the row is still red *after* `statements:list` returns 3, the panel is out of step with Play's
   own backend. The device check in step 3 is then the deciding evidence.

## Consequences for the sibling apps

`gym-log` and `gym-companion` are TWAs on the **same host**. When they are submitted, each needs its
own object appended to the *same* `assetlinks.json` array (one entry per Android package, with that
app's Play App Signing fingerprint). Their project repos cannot serve the file themselves.

## Files to look at

- `ANDROIDWORKS/ambijat.github.io/.well-known/assetlinks.json` — the served file
- `ANDROIDWORKS/ambijat.github.io/.nojekyll` — must not be deleted
- `ANDROIDWORKS/gym-band/app/src/main/AndroidManifest.xml` — intent filter (`autoVerify`)
- `ANDROIDWORKS/gym-band/app/src/main/res/values/strings.xml` — `assetStatements`, `hostName`
- `ANDROIDWORKS/gym-band/twa-manifest.json` — `host`, `fullScopeUrl`, `fingerprints: []`
