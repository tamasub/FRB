FRB Sea Camera - Auto Resume / SD Recovery patch

Key behavior:
1. Recording start metadata (session/target/interval) is stored in ESP32 NVS.
2. If ESP32 brownouts/reboots mid-recording, the same REC_xxxx is resumed from the last durable frames.csv row.
3. frames.csv remains the durable progress marker (flushed every 20 frames). Up to the unflushed tail can be overwritten safely after reboot.
4. Three consecutive JPEG write failures or a segment mkdir/CSV failure triggers ESP.restart(). NVS remains active, so recording resumes after reboot.
5. If SD does not remount immediately after reboot, AP/server can remain up and recorderService() retries SD mount every 5 seconds; recording resumes once SD returns.
6. STOP or target completion clears the NVS resume marker.
7. /record/status now exposes resetReason, resumePending, autoResumed, and lastFault.
8. Files no longer creates a summary.csv for an active/pending incomplete recording.

Important limitation:
- Software recovery cannot repair a physically failed/corrupted/removed SD card or a power rail that never recovers. In that case status stays SD ERROR / RESUME PENDING and retries continue.
