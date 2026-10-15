FRB Sea Camera v0.16.2 - SD start recovery

Changes from app(3):
- REC retries SD mount once when sdReady is false.
- Background service retries a failed SD mount every 5 seconds even without a pending resume.
- HTTP 409 now reports the specific start failure:
  SD_NOT_READY / ALREADY_RECORDING / SESSION_MKDIR_FAILED / TASK_CREATE_FAILED.
- SD_MMC.begin format_if_mount_failed changed from true to false.
  A transient mount failure must never auto-format field recordings.
- Auto Resume / SD recovery remains enabled.
