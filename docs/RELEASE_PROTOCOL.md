# Band Training Release Protocol

This document records the command-line release flow used for the Band Training Android Trusted Web Activity.

It covers:

- checking the repo
- configuring local SDK/JDK paths
- building debug and release artifacts
- signing the release AAB/APK
- verifying the signed files
- committing and pushing source changes
- uploading the AAB to Google Play Console

Do not commit passwords, `local.properties`, keystores, APKs, or AAB files.

## 1. Project Location

Run commands from the project root:

```bash
cd /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band
```

## 2. Check Repo State

```bash
git status --short --branch
git log --oneline --decorate -5
git remote -v
```

Expected remote:

```text
origin  https://github.com/ambijat/gym-band.git
```

## 3. Local SDK/JDK Setup

The Android SDK on this machine is:

```text
/home/ambijat/Android/Sdk
```

The usable JDK bundled with Android Studio is:

```text
/home/ambijat/android-studio/jbr
```

Create or confirm `local.properties`:

```bash
printf 'sdk.dir=/home/ambijat/Android/Sdk\n' > local.properties
```

For the current shell:

```bash
export ANDROID_HOME=/home/ambijat/Android/Sdk
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export JAVA_HOME=/home/ambijat/android-studio/jbr
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"
```

Confirm tools:

```bash
java -version
javac -version
```

## 4. Edit App Code And Assets

For app behavior or catalogue changes, the main web files are:

```text
index.html
videos.json
```

For generated visual assets, use:

```bash
python3 tools/generate_brand_assets.py
```

Screenshots should be live captures of the rendered app, not static mockups. Current screenshot targets:

```text
screenshots/log-mobile.png  390x844
screenshots/log-wide.png    1280x720
```

Syntax check for the inline JavaScript:

```bash
awk '/<script>/{flag=1;next}/<\/script>/{flag=0}flag' index.html | node --check
```

## 4A. Hosted Video Rule

The videos are intentionally hosted from the GitHub repo/GitHub Pages, not bundled into Google Play artifacts.

`videos.json` should contain absolute hosted URLs such as:

```text
https://ambijat.github.io/gym-band/videos/stability.mp4
```

Generate that catalogue with:

```bash
python3 tools/generate_video_index.py \
  --source /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/videos \
  --out videos.json
```

The `videos/` directory belongs in the GitHub repo so GitHub Pages can serve it. The Android APK/AAB should remain a lightweight TWA wrapper and must not contain `.mp4`, `.webm`, `.mov`, `.m4v`, `.avi`, or `.mkv` files.

## 5. Bump Release Version

Edit:

```text
app/build.gradle
twa-manifest.json
```

For the current release we used:

```text
versionCode 1
versionName "1.0"
```

Check version fields:

```bash
rg -n "versionCode|versionName|appVersionCode|appVersionName|appVersion" app/build.gradle twa-manifest.json
```

## 6. Clean Build

Build debug APK, release APK, and release AAB:

```bash
JAVA_HOME=/home/ambijat/android-studio/jbr ./gradlew clean :app:assembleDebug :app:assembleRelease :app:bundleRelease
```

If only the Play Store artifact is needed:

```bash
JAVA_HOME=/home/ambijat/android-studio/jbr ./gradlew clean :app:bundleRelease
```

Expected unsigned build outputs:

```text
app/build/outputs/apk/debug/app-debug.apk
app/build/outputs/apk/release/app-release-unsigned.apk
app/build/outputs/bundle/release/app-release.aab
```

List generated artifacts:

```bash
find app/build/outputs -maxdepth 5 -type f \( -name '*.apk' -o -name '*.aab' \) -printf '%p %TY-%Tm-%Td %TH:%TM:%TS %s bytes\n' | sort
```

Confirm that debug/release Android archives do not bundle exercise videos:

```bash
zipinfo -1 app/build/outputs/apk/debug/app-debug.apk | rg -i '\.(mp4|webm|mov|m4v|avi|mkv)$' || true
zipinfo -1 app/build/outputs/apk/release/app-release-unsigned.apk | rg -i '\.(mp4|webm|mov|m4v|avi|mkv)$' || true
zipinfo -1 app/build/outputs/bundle/release/app-release.aab | rg -i '\.(mp4|webm|mov|m4v|avi|mkv)$' || true
```

Expected output: no matching files.

## 7. Signing Setup

Keystore file:

```text
android.keystore
```

Key alias:

```text
bandtrainingkey
```

Set the keystore password for the current terminal session.

Important: do not write the real password into this file or into Git.

```bash
read -rsp "Keystore password: " KEYSTORE_PASSWORD
printf '\n'
```

Confirm the keystore opens:

```bash
/home/ambijat/android-studio/jbr/bin/keytool \
  -list -v \
  -keystore android.keystore \
  -alias bandtrainingkey \
  -storepass "$KEYSTORE_PASSWORD" | sed -n '1,45p'
```

Expected certificate identity:

```text
CN=Ambijat, OU=Independent Developer, O=Ambijat, C=IN
```

## 8. Sign The Release AAB

Sign the Play Console bundle:

```bash
/home/ambijat/android-studio/jbr/bin/jarsigner \
  -sigalg SHA256withRSA \
  -digestalg SHA-256 \
  -keystore android.keystore \
  -storepass "$KEYSTORE_PASSWORD" \
  -keypass "$KEYSTORE_PASSWORD" \
  -signedjar app/build/outputs/bundle/release/app-release-signed.aab \
  app/build/outputs/bundle/release/app-release.aab \
  bandtrainingkey
```

Final Play Console upload file:

```text
app/build/outputs/bundle/release/app-release-signed.aab
```

## 9. Sign The Release APK

The signed APK is optional, useful for sideload testing.

Align the unsigned APK:

```bash
/home/ambijat/Android/Sdk/build-tools/36.1.0/zipalign \
  -p -f 4 \
  app/build/outputs/apk/release/app-release-unsigned.apk \
  app/build/outputs/apk/release/app-release-unsigned-aligned.apk
```

Sign the aligned APK:

```bash
/home/ambijat/Android/Sdk/build-tools/36.1.0/apksigner sign \
  --ks android.keystore \
  --ks-key-alias bandtrainingkey \
  --ks-pass pass:"$KEYSTORE_PASSWORD" \
  --key-pass pass:"$KEYSTORE_PASSWORD" \
  --out app/build/outputs/apk/release/app-release-signed.apk \
  app/build/outputs/apk/release/app-release-unsigned-aligned.apk
```

Optional sideload test file:

```text
app/build/outputs/apk/release/app-release-signed.apk
```

## 10. Verify Signed Artifacts

Verify AAB:

```bash
/home/ambijat/android-studio/jbr/bin/jarsigner \
  -verify -verbose -certs \
  app/build/outputs/bundle/release/app-release-signed.aab 2>&1 | tail -35
```

Expected important line:

```text
jar verified.
```

Self-signed certificate warnings are expected for this local upload key.

Verify APK:

```bash
/home/ambijat/Android/Sdk/build-tools/36.1.0/apksigner verify \
  --verbose --print-certs \
  app/build/outputs/apk/release/app-release-signed.apk | sed -n '1,24p'
```

Expected important line:

```text
Verifies
```

Confirm APK version metadata:

```bash
/home/ambijat/Android/Sdk/build-tools/36.1.0/aapt2 dump badging \
  app/build/outputs/apk/release/app-release-signed.apk 2>/dev/null | sed -n '1,12p'
```

For release 1.0, expected:

```text
versionCode='1' versionName='1.0'
```

## 11. Commit And Push Source Changes

Generated artifacts are ignored and should not be committed.

Review tracked changes:

```bash
git status --short --branch
git diff -- app/build.gradle twa-manifest.json index.html manifest.json app/src/main/res/raw/web_app_manifest.json
```

Stage intended files only:

```bash
git add index.html manifest.json app/src/main/res/raw/web_app_manifest.json app/build.gradle twa-manifest.json
git add icons graphics screenshots store_icon.png app/src/main/res
git add tools/generate_video_index.py tools/generate_brand_assets.py README_BAND_TRAINING.md docs/RELEASE_PROTOCOL.md
```

Commit examples:

```bash
git commit -m "Refresh Band Training assets"
git commit -m "Bump release version to 1.1"
```

Push:

```bash
git push origin main
```

Confirm clean synced repo:

```bash
git status --short --branch
git rev-parse HEAD origin/main
```

## 12. Google Play Console Upload

In Google Play Console:

1. Open the app.
2. Go to `Testing > Internal testing`, or the target release track.
3. Click `Create new release`.
4. Upload:

```text
app/build/outputs/bundle/release/app-release-signed.aab
```

5. Wait for processing.
6. Add release notes:

```text
Refreshed Band Training launch assets and screenshots.

- New band-training themed icons, splash image, store icon, and feature graphic.
- Updated mobile and wide screenshots from the live app.
- Keeps video catalogue, completion logging, and CSV/JSON export behavior.
```

7. Review warnings.
8. Roll out to internal testing first.
9. Add testers from the `Testers` tab.
10. Use the testing link on a tester Google account to install from Play Store.

## 13. Smoke Test Checklist

After installing the internal test build:

- Confirm the launcher icon, splash image, and shortcut icon use the Band Training mark.
- Open the app and confirm `videos.json` loads hosted GitHub Pages video URLs.
- Use search and body-area filters.
- Play a video card.
- Mark at least one exercise done.
- Confirm the completion appears in the scrollable log.
- Test both CSV and JSON modes.
- Test Copy and Download from the export modal.

## 14. Current Release Snapshot

Current source state:

```text
package: com.ambijat.bandtraining
versionCode: 1
versionName: 1.0
web path: https://ambijat.github.io/gym-band/
```

Current release artifact:

```text
app/build/outputs/bundle/release/app-release-signed.aab
```

Current signed test APK:

```text
app/build/outputs/apk/release/app-release-signed.apk
```
