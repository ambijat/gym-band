# Band Training App

This is a separate stretch-band exercise app cloned from the provided prototype, but with a new Android identity:

- Android package: `com.ambijat.bandtraining`
- App name: `Band Training`
- Launcher name: `Band Log`
- Web path expected for TWA: `https://ambijat.github.io/gym-band/`
- Local storage key: `bandtraining:entries`

Because the package name is different from the prototype (`com.ambijat.gymlog`), this APK will install as a separate app rather than as an update to the DS5 logger.

## What changed

The original muscle-group tap logger has been replaced with a band-training video catalogue:

1. `videos.json` supplies the exercise-video repository.
2. The app can filter videos by body area/group.
3. Each card can open a video player.
4. Each exercise can be marked as completed.
5. Completion history is stored locally and can be exported as CSV or JSON.
6. The history is in a scrollable window, so the app height does not grow endlessly.

## Expected video layout

Place your videos under:

```text
/media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/
  index.html
  videos.json
  videos/
    band-row.mp4
    band-squat.mp4
    ...
```

The repository path you mentioned is:

```text
/media/ambijat/FIGHTER/ANDROIDWORKS/gym-band
```

So the recommended final structure is:

```text
/media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/
  index.html
  manifest.json
  sw.js
  videos.json
  videos/
    <all stretch-band exercise videos>
```

## Generate `videos.json`

A helper script is included:

```bash
python3 tools/generate_video_index.py \
  --source /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/videos \
  --out videos.json
```

By default, generated video entries use absolute GitHub Pages URLs like:

```text
https://ambijat.github.io/gym-band/videos/quadriceps.mp4
```

This is intentional. The videos are hosted by the GitHub repo/GitHub Pages and streamed by the app. They are not packaged inside the Android APK or AAB that goes to Google Play.

If your video files are directly inside the project root instead of `videos/`, run:

```bash
python3 tools/generate_video_index.py \
  --source /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band \
  --out videos.json \
  --prefix .
```

The script infers body-area groups from filenames and folder names. You can manually edit `videos.json` afterwards.

If you need local relative URLs for offline browser testing, pass an explicit prefix:

```bash
python3 tools/generate_video_index.py \
  --source /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/videos \
  --out videos.json \
  --prefix videos
```

## Visual assets

App icons, shortcut icons, notification icons, splash images, the store icon, and the Play feature graphic are generated from the Band Training theme:

```bash
python3 tools/generate_brand_assets.py
```

Screenshots are live captures of the real app, not static mockups. The current files are:

```text
screenshots/log-mobile.png  390x844
screenshots/log-wide.png    1280x720
```

## Build notes

This project remains a Bubblewrap/TWA Android project. To build on your machine:

```bash
cd /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band
./gradlew assembleDebug
```

The debug APK is written to:

```text
app/build/outputs/apk/debug/app-debug.apk
```

The Android artifact is a lightweight Trusted Web Activity wrapper. It points to:

```text
https://ambijat.github.io/gym-band/
```

The release checklist in `docs/RELEASE_PROTOCOL.md` includes archive checks to confirm no `.mp4`/video files are bundled into APK or AAB outputs.
