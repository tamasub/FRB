Freenove ESP32-S3 Camera Web Server + SD Recorder prototype
============================================================

Added:
- SD_MMC init using Freenove 07.3 board pins: CLK=39, CMD=38, D0=40 (1-bit)
- Browser REC / STOP controls
- MJPEG AVI recording to /recordings/REC_XXXX.avi
- Recording status (seconds / frames / filename)
- SD recording file list
- Browser download endpoint
- Original Freenove camera UI preserved under /camera and embedded in recorder page

Target camera:
- OV2640 in JPEG mode is required for REC in this prototype.
- Current GC0308 will still run the camera UI, but REC intentionally returns an error.

Arduino IDE settings used in this project conversation:
- Board: ESP32S3 Dev Module
- Flash Size: 8MB
- PSRAM: OPI PSRAM
- Flash Mode: QIO

Usage:
1. Insert microSD card.
2. Replace Wi-Fi ssid/password in Sketch_07.1_CameraWebServer.ino.
3. Upload to ESP32-S3.
4. Open the printed IP address in a browser.
5. With OV2640 installed, click REC. Click STOP before downloading.
6. Files appear in the SD recordings pane; click Download.

Notes:
- This is a first prototype intended for bench testing, not a finalized loss-proof recorder.
- AVI contains MJPEG video only (no audio).
- Do not change resolution/camera settings during recording.
- If live streaming and recording together causes dropped frames, stop the live Stream while recording.
- AVI FPS is calculated from actual frames captured / elapsed recording time when STOP is pressed.


v0.4 PLAY fix:
- Playback is embedded in the recordings pane (Android-friendly).
- Frames are fetched as Blob with HTTP/JPEG diagnostics.
- Added pause, previous/next, FPS control.
- Main sketch renamed to CameraWebServer.ino.

v0.6 PLAY fix
- Based on the uploaded app(2).zip as the latest source.
- Keeps main sketch filename: frb_CameraWebServer.ino
- /record/frame HTTP buffer reduced from 4096 to 1024 bytes.
- HTTP server task stack increased to 8192 bytes.
- PLAY transfer diagnostics added to Serial Monitor.


v0.9 camera exclusive recording:
- REC closes /camera iframe before recording, waits 800 ms for MJPEG connection to release camera.
- /stream rejects new connections while recording and exits an existing stream when REC becomes active.
- During recording the live camera UI stays paused. After recording completes/stops, Files refreshes and camera UI is reloaded.
- Goal: prevent GC0308 frame-buffer contention that caused 0.19 fps recordings / delayed camera recovery.

v0.10 Files performance improvement
- Each completed recording now writes summary.csv (frames,duration_ms,recorded_fps).
- /record/files reads summary.csv only; it no longer enumerates every JPEG file.
- Legacy recordings without summary.csv are migrated once from frames.csv and cached.
- Initial page load no longer automatically runs the Files scan. Press Files when needed.
- Files shows its own Loading recordings... state and does not own the main READY status.


v0.11 Player scroll improvement
- Added an independent vertical scrollbar inside the recorded-frame player.
- Player height is capped so long/tall playback content no longer forces the whole recordings pane to scroll.
- Playback controls remain sticky at the top while scrolling inside the player.


v0.12 Player frame seek
- Replaced the v0.11 inner vertical scrollbar with a frame-position seek slider.
- Drag the slider to jump directly to any recorded frame (e.g. near the end of a 1900-frame session).
- Seeking pauses playback; the JPEG is fetched when the slider is released.
- The slider follows the current frame during normal playback and previous/next stepping.


v0.13 Segmented JPEG storage experiment
- New recordings store JPEGs in 300-frame subfolders to keep FAT directory size bounded.
- Layout example: REC_0015/SEG_0001/frame_000001.jpg ... SEG_0010/frame_003000.jpg.
- frames.csv and summary.csv remain directly under REC_xxxx.
- PLAY/seek automatically maps a frame number to the correct SEG_xxxx folder.
- Old flat recordings remain playable without migration.
- DELETE already removes subfolders recursively, so segmented recordings can still be deleted as one REC session.
- Goal: test whether the progressive FPS drop seen with thousands of JPEGs in one FAT directory is reduced.


v0.14 Battery voltage monitor
- GPIO1 is used as ESP32-S3 ADC1 input.
- Hardware divider expected: LiPo+ -> 20kΩ -> GPIO1 -> 20kΩ -> GND.
- The web header now shows BAT x.xxV and GOOD / LOW / CRITICAL.
- /record/status also returns batteryV, batteryAdcMv and batteryLevel once per status refresh.
- ADC readings are averaged (12 samples) to reduce noise.
- BATTERY_CALIBRATION in battery_monitor.cpp can be adjusted later against a multimeter.
- Voltage thresholds are broad operational indicators, not an exact battery percentage.
