#include "sd_recorder.h"
#include "avi_writer.h"
#include "esp_camera.h"
#include "img_converters.h"
#include "SD_MMC.h"
#include "FS.h"
#include <Preferences.h>
#include "esp_system.h"
#include "esp_attr.h"
#include <WiFi.h>
#include "esp_task_wdt.h"
#include "esp_idf_version.h"
#include <cstring>

#define SD_MMC_CMD 38
#define SD_MMC_CLK 39
#define SD_MMC_D0  40
#define RECORD_DIR "/recordings"
#define FRAMES_PER_SEGMENT 300
#define SD_WRITE_FAIL_RESTART_COUNT 3
#define SD_RECOVERY_RETRY_MS 5000
#define AVI_ROLL_MS 60000UL // Each finalized AVI contains approximately one minute.
// No completed frame for 25s is abnormal even at the slowest supported XGA rate.
#define REC_STALL_RESTART_MS 25000UL
#define REC_SUPERVISOR_POLL_MS 1500
#define AVI_RECOVERY_MAX_RESTARTS 5


static volatile bool recording=false, stopRequested=false;
static bool sdReady=false;
static bool videoMode=false;
static volatile uint32_t activeVideoPart=0, finalizedVideoParts=0, videoPartStartedMs=0;
static String lastVideoError="";
static TaskHandle_t recTaskHandle=nullptr;
static String currentSession="";
static uint32_t frameCount=0, targetCount=0, intervalMsCfg=0, startedMs=0;
static uint32_t elapsedBaseMs=0;
static bool resumeMode=false;
static bool autoResumed=false;

// Resume metadata intentionally lives in ESP32 NVS, not on the SD card.
// That way a temporary SD disappearance or a brownout can still be recovered.
static bool resumePending=false;
static String pendingSession="";
static uint32_t pendingTarget=0, pendingInterval=0;
static String pendingFault="";
static String lastStartError="";
static Preferences recPrefs;

// Software-reset-resistant diagnostic marker. It is updated without SD/NVS I/O,
// so even a stuck filesystem should not prevent a supervisor-requested reset.
static RTC_NOINIT_ATTR uint32_t rtcFaultMagic;
static RTC_NOINIT_ATTR char rtcFaultText[40];
static const uint32_t RTC_FAULT_MAGIC = 0x46524221UL;
static String lastRecoveryFault="";

// AVI recovery intent lives in NVS, separate from the JPEG resume contract.
// Only finalized AVI frames count as durable. Recovery always starts a NEW REC
// folder to avoid overwriting an AVI that was interrupted by the reset.
static bool aviRecoveryPending=false;
static uint32_t aviOriginalTarget=0, aviDurableFrames=0, aviRecoverInterval=0;
static uint8_t aviRecoveryRestarts=0;
static String aviRecoveryFrom="";
static bool startingRecoveredAvi=false;
static volatile uint32_t recordingHeartbeatMs=0;
static bool supervisorStarted=false;

static void touchRecordingHeartbeat(){recordingHeartbeatMs=millis();}

static void markRecoveryFault(const char *why){
  rtcFaultMagic=RTC_FAULT_MAGIC;
  memset(rtcFaultText,0,sizeof(rtcFaultText));
  if(why)strncpy(rtcFaultText,why,sizeof(rtcFaultText)-1);
}

static void immediateRestart(const char *why){
  Serial.printf("FRB AUTO-RESTART: %s | REC=%s part=%u frames=%u\n",
                why?why:"UNKNOWN",currentSession.c_str(),(unsigned)activeVideoPart,(unsigned)frameCount);
  markRecoveryFault(why);
  Serial.flush();
  esp_restart(); // Works even when the web browser / AP is unresponsive.
  while(true)vTaskDelay(pdMS_TO_TICKS(1000));
}

static void persistAviRecovery(){
  Preferences pref;
  if(!pref.begin("frbavi",false))return;
  pref.putUInt("target",aviOriginalTarget);
  pref.putUInt("done",aviDurableFrames);
  pref.putUInt("interval",aviRecoverInterval);
  pref.putUChar("restarts",aviRecoveryRestarts);
  pref.putString("from",aviRecoveryFrom);
  pref.putBool("active",aviRecoveryPending); // Always write the intent LAST.
  pref.end();
}
static void loadAviRecovery(){
  Preferences pref;
  if(!pref.begin("frbavi",true))return;
  aviRecoveryPending=pref.getBool("active",false);
  aviOriginalTarget=pref.getUInt("target",0);
  aviDurableFrames=pref.getUInt("done",0);
  aviRecoverInterval=pref.getUInt("interval",200);
  aviRecoveryRestarts=pref.getUChar("restarts",0);
  aviRecoveryFrom=pref.getString("from","");
  pref.end();
  if(aviRecoveryPending)
    Serial.printf("AVI RECOVERY pending: durable=%u target=%u interval=%u attempts=%u from=%s\n",
                  aviDurableFrames,aviOriginalTarget,aviRecoverInterval,aviRecoveryRestarts,aviRecoveryFrom.c_str());
}
static void clearAviRecovery(){
  aviRecoveryPending=false;
  Preferences pref;
  if(pref.begin("frbavi",false)){pref.putBool("active",false);pref.end();}
}
static void onAviPartFinalized(uint32_t partFrames){
  aviDurableFrames+=partFrames;
  // Completing a segment proves the recovered system is healthy again.
  aviRecoveryRestarts=0;
  persistAviRecovery();
  touchRecordingHeartbeat();
}

// Monitor runs on core 0, independently of the recorder on core 1 and Arduino
// loop(). A stuck esp_camera_fb_get() / SD write cannot update the heartbeat.
static void recordingSupervisor(void *){
#if ESP_IDF_VERSION_MAJOR >= 5
  esp_task_wdt_config_t cfg = {};
  cfg.timeout_ms=35000;
  cfg.idle_core_mask=0;
  cfg.trigger_panic=true;
  esp_err_t initResult=esp_task_wdt_init(&cfg);
  if(initResult==ESP_ERR_INVALID_STATE) initResult=esp_task_wdt_reconfigure(&cfg);
  if(initResult==ESP_OK) esp_task_wdt_add(nullptr);
  else Serial.printf("FRB TWDT configure failed: 0x%x (software supervisor still active)\n",initResult);
#else
  esp_task_wdt_init(35,true);
  esp_task_wdt_add(nullptr);
#endif
  uint32_t lastApCheck=0;
  for(;;){
    esp_task_wdt_reset();
    if(recording){
      uint32_t quiet=millis()-recordingHeartbeatMs;
      if(quiet>(intervalMsCfg>REC_STALL_RESTART_MS-15000UL ? intervalMsCfg+15000UL : REC_STALL_RESTART_MS)){
        immediateRestart("REC_TASK_STALLED");
      }
    }
    // AP stations may be absent while submerged: station count is NOT a
    // health check. Only restart if the device lost AP mode / its local IP.
    if(millis()-lastApCheck>=10000){
      lastApCheck=millis();
      wifi_mode_t wm=WiFi.getMode();
      if((wm&WIFI_AP)==0 || WiFi.softAPIP()==IPAddress(0,0,0,0)){
        immediateRestart("AP_MODE_LOST");
      }
    }
    vTaskDelay(pdMS_TO_TICKS(REC_SUPERVISOR_POLL_MS));
  }
}

void recorderStartSupervisor(){
  if(supervisorStarted)return;
  supervisorStarted=true;
  if(xTaskCreatePinnedToCore(recordingSupervisor,"frb-supervisor",4096,nullptr,3,nullptr,0)!=pdPASS){
    supervisorStarted=false;
    Serial.println("FRB: recovery supervisor task creation FAILED");
  }
}


static String safeSession(const String &s){
  if(s.length()<1 || s.indexOf('/')>=0 || s.indexOf("..")>=0) return "";
  for(size_t i=0;i<s.length();i++){ char c=s[i]; if(!(isalnum((unsigned char)c)||c=='_'||c=='-')) return ""; }
  return s;
}

static const char* resetReasonName(){
  switch(esp_reset_reason()){
    case ESP_RST_POWERON: return "POWERON";
    case ESP_RST_EXT: return "EXT";
    case ESP_RST_SW: return "SW";
    case ESP_RST_PANIC: return "PANIC";
    case ESP_RST_INT_WDT: return "INT_WDT";
    case ESP_RST_TASK_WDT: return "TASK_WDT";
    case ESP_RST_WDT: return "WDT";
    case ESP_RST_DEEPSLEEP: return "DEEPSLEEP";
    case ESP_RST_BROWNOUT: return "BROWNOUT";
    case ESP_RST_SDIO: return "SDIO";
    default: return "UNKNOWN";
  }
}

static void loadResumeState(){
  recPrefs.begin("frbrec", true);
  resumePending=recPrefs.getBool("active",false);
  pendingSession=recPrefs.getString("session","");
  pendingTarget=recPrefs.getUInt("target",0);
  pendingInterval=recPrefs.getUInt("interval",0);
  pendingFault=recPrefs.getString("fault","");
  recPrefs.end();
  if(resumePending){
    Serial.printf("REC: pending resume session=%s target=%u interval=%u fault=%s\n",
                  pendingSession.c_str(),pendingTarget,pendingInterval,pendingFault.c_str());
  }
}

static void saveResumeState(const String &session,uint32_t target,uint32_t interval){
  recPrefs.begin("frbrec", false);
  recPrefs.putString("session",session);
  recPrefs.putUInt("target",target);
  recPrefs.putUInt("interval",interval);
  recPrefs.putString("fault","");
  recPrefs.putBool("active",true); // write active last
  recPrefs.end();
  resumePending=true; pendingSession=session; pendingTarget=target; pendingInterval=interval; pendingFault="";
}

static void saveFault(const char *fault){
  pendingFault=fault?fault:"";
  recPrefs.begin("frbrec", false);
  recPrefs.putString("fault",pendingFault);
  recPrefs.end();
}

static void clearResumeState(){
  recPrefs.begin("frbrec", false);
  recPrefs.putBool("active",false);
  recPrefs.putString("fault","");
  recPrefs.end();
  resumePending=false; pendingSession=""; pendingTarget=0; pendingInterval=0; pendingFault="";
}

static bool mountSd(){
  sdReady=false;
  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
  if(!SD_MMC.begin("/sdcard",true,false,SDMMC_FREQ_DEFAULT,5)){ Serial.println("REC: SD mount failed"); return false; }
  uint8_t t=SD_MMC.cardType(); if(t==CARD_NONE){Serial.println("REC: no SD card");return false;}
  Serial.print("REC: SD_MMC Card Type: "); Serial.println(t==CARD_MMC?"MMC":t==CARD_SD?"SDSC":t==CARD_SDHC?"SDHC":"UNKNOWN");
  Serial.printf("REC: SD_MMC Card Size: %lluMB\n",SD_MMC.cardSize()/(1024ULL*1024ULL));
  Serial.printf("REC: Total space: %lluMB\n",SD_MMC.totalBytes()/(1024ULL*1024ULL));
  Serial.printf("REC: Used space: %lluMB\n",SD_MMC.usedBytes()/(1024ULL*1024ULL));
  if(!SD_MMC.exists(RECORD_DIR)&&!SD_MMC.mkdir(RECORD_DIR)){Serial.println("REC: failed to create /recordings");return false;}
  sdReady=true; Serial.printf("REC: SD ready, %llu MB free\n",(SD_MMC.totalBytes()-SD_MMC.usedBytes())/(1024ULL*1024ULL)); return true;
}

bool recorderInit(){
  if(rtcFaultMagic==RTC_FAULT_MAGIC){
    lastRecoveryFault=String(rtcFaultText);
    Serial.printf("FRB PREVIOUS AUTO-RESTART: %s\n",lastRecoveryFault.c_str());
    rtcFaultMagic=0; // Consume marker so a later manual reset is distinguishable.
  }
  loadResumeState();
  loadAviRecovery();
  return mountSd();
}

static bool saveFrame(camera_fb_t *fb,const String &path){
  File f=SD_MMC.open(path.c_str(),FILE_WRITE); if(!f)return false;
  bool ok=false;
  if(fb->format==PIXFORMAT_JPEG){ ok=f.write(fb->buf,fb->len)==fb->len; }
  else { uint8_t *jpg=nullptr; size_t len=0; if(frame2jpg(fb,80,&jpg,&len)){ok=f.write(jpg,len)==len; free(jpg);} }
  f.close(); return ok;
}

static bool writeRecordingSummary(const String &session, uint32_t frames, uint32_t firstTs, uint32_t lastTs){
  String path=String(RECORD_DIR)+"/"+session+"/summary.csv";
  File f=SD_MMC.open(path.c_str(),FILE_WRITE); if(!f)return false;
  uint32_t duration=(frames>1 && lastTs>firstTs)?(lastTs-firstTs):0;
  float fps=duration?((float)(frames-1)*1000.0f/(float)duration):0.0f;
  f.println("frames,duration_ms,recorded_fps");
  f.printf("%u,%u,%.2f\n",frames,duration,fps);
  f.flush(); f.close();
  return true;
}

// Reads only frames.csv. It never scans thousands of JPEGs.
// The last valid CSV row is the durable resume point. Any JPEGs written after
// the last CSV flush may simply be overwritten after reboot, which is safe.
static bool readRecordingProgress(const String &session,uint32_t &lastFrame,uint32_t &firstTs,uint32_t &lastTs){
  lastFrame=0; firstTs=0; lastTs=0;
  String csvPath=String(RECORD_DIR)+"/"+session+"/frames.csv";
  File csv=SD_MMC.open(csvPath.c_str(),FILE_READ); if(!csv)return false;
  csv.readStringUntil('\n');
  bool have=false;
  while(csv.available()){
    String line=csv.readStringUntil('\n'); line.trim(); if(!line.length())continue;
    int comma=line.indexOf(','); if(comma<0)continue;
    uint32_t no=strtoul(line.substring(0,comma).c_str(),nullptr,10);
    uint32_t ts=strtoul(line.substring(comma+1).c_str(),nullptr,10);
    if(no<1)continue;
    if(!have){firstTs=ts;have=true;}
    lastFrame=no; lastTs=ts;
  }
  csv.close();
  return true; // header-only file is still a valid zero-frame recording
}

static void restartForSdFault(const char *fault, File *csv=nullptr){
  Serial.printf("REC: fatal SD fault -> restart: %s\n",fault?fault:"UNKNOWN");
  saveFault(fault?fault:"SD_ERROR");
  if(csv && *csv){ csv->flush(); csv->close(); }
  sdReady=false;
  delay(250);
  ESP.restart();
  while(true) delay(1000);
}

// AVI segmentation: keep a single REC_xxxx session and finalize an AVI every
// ~60 seconds. A power cut can damage only the currently open part, not parts
// already finished with RIFF sizes and idx1 indexes.
static void videoTask(void*){
  AviWriter avi;
  touchRecordingHeartbeat();
  camera_fb_t *first=esp_camera_fb_get();
  if(!first){
    lastVideoError="CAMERA_NO_FRAME";
    // A clean reboot reinitializes the sensor, buffers, AP and SD controller.
    immediateRestart("CAMERA_NO_FRAME");
  }
  const uint16_t w=first->width,h=first->height;
  uint32_t nextDue=millis();
  uint32_t firstSavedMs=0,lastSavedMs=0;
  uint32_t partFirstMs=0,partLastMs=0,partStartedMs=0;
  uint32_t partFrames=0,partNo=0;
  bool partOpen=false;
  uint8_t failures=0;
  activeVideoPart=0;finalizedVideoParts=0;videoPartStartedMs=0;

  while(!stopRequested && frameCount<targetCount){
    if(intervalMsCfg){
      int32_t wait=(int32_t)(nextDue-millis());
      if(wait>0)delay(wait);
    }
    if(stopRequested)break;
    // Close the previous minute BEFORE taking the next frame. Opening the
    // next AVI lazily avoids creating an empty file when STOP is pressed.
    if(partOpen && partFrames>0 && (uint32_t)(millis()-partStartedMs)>=AVI_ROLL_MS){
      uint32_t partDuration=partFrames>1 ? partLastMs-partFirstMs : 0;
      bool ok=avi.finish(partDuration);
      partOpen=false;activeVideoPart=0;
      if(!ok){lastVideoError="AVI_ROLLOVER_FINALIZE_FAILED";break;}
      finalizedVideoParts=partNo;
      onAviPartFinalized(partFrames);
      nextDue=millis(); // Do not burst-capture to catch up after idx1 SD I/O.
      Serial.printf("AVI part finalized: %s video_%04u.avi frames=%u total=%u\n",
                    currentSession.c_str(),partNo,partFrames,frameCount);
      partFrames=0;
    }
    camera_fb_t *fb=first?first:esp_camera_fb_get();first=nullptr;
    if(!fb){
      // Do not allow a transient camera timeout to silently end an unattended
      // underwater recording. The task finalizes what it can, then reboots.
      if(++failures>=3){lastVideoError="CAMERA_TIMEOUT";break;}
      delay(20);continue;
    }
    if(fb->width!=w || fb->height!=h){
      esp_camera_fb_return(fb);lastVideoError="FRAME_SIZE_CHANGED";break;
    }
    if(!partOpen){
      ++partNo;
      char partName[32];snprintf(partName,sizeof(partName),"video_%04u.avi",partNo);
      String path=String(RECORD_DIR)+"/"+currentSession+"/"+partName;
      if(!avi.begin(SD_MMC,path,w,h)){
        esp_camera_fb_return(fb);lastVideoError="AVI_PART_OPEN_FAILED";break;
      }
      partOpen=true;
      partStartedMs=millis();videoPartStartedMs=partStartedMs;
      activeVideoPart=partNo;
      partFrames=0;
      Serial.printf("AVI part started: %s/%s\n",currentSession.c_str(),partName);
    }
    uint32_t ts=millis()-startedMs;
    bool ok=false;
    if(fb->format==PIXFORMAT_JPEG){
      ok=avi.add(fb->buf,fb->len);
    }else{
      uint8_t *jpg=nullptr;size_t jpgSize=0;
      if(frame2jpg(fb,75,&jpg,&jpgSize)){
        ok=avi.add(jpg,jpgSize);free(jpg);
      }else lastVideoError="JPEG_CONVERSION_FAILED";
    }
    esp_camera_fb_return(fb);
    if(!ok){lastVideoError="AVI_WRITE_FAILED";break;}
    if(frameCount==0)firstSavedMs=ts;
    if(partFrames==0)partFirstMs=ts;
    lastSavedMs=ts;partLastMs=ts;
    frameCount++;partFrames++;failures=0;
    touchRecordingHeartbeat();
    if(frameCount%20==0)
      Serial.printf("AVI REC: %s part=%u frames=%u/%u\n",
                    currentSession.c_str(),partNo,frameCount,targetCount);
    nextDue=intervalMsCfg?nextDue+intervalMsCfg:millis();
    delay(1);
  }
  // STOP / target reached / camera error: finalize the current nonempty part.
  if(partOpen){
    touchRecordingHeartbeat();
    uint32_t partDuration=partFrames>1 ? partLastMs-partFirstMs : 0;
    bool finalized=avi.finish(partDuration);
    activeVideoPart=0;
    if(finalized){
      finalizedVideoParts=partNo;
      onAviPartFinalized(partFrames);
    }
    else lastVideoError="AVI_FINALIZE_FAILED";
    Serial.printf("AVI final part: %s part=%u frames=%u finalize=%d\n",
                  currentSession.c_str(),partNo,partFrames,finalized);
  }
  if(frameCount>0 && !writeRecordingSummary(currentSession,frameCount,firstSavedMs,lastSavedMs))
    Serial.println("AVI summary write failed");
  Serial.printf("AVI done: %s frames=%u parts=%u error=%s\n",
                currentSession.c_str(),frameCount,(uint32_t)finalizedVideoParts,lastVideoError.c_str());
  // Only user STOP or target reached cancels the automatic restart intent.
  if(stopRequested || frameCount>=targetCount){
    clearAviRecovery();
  }else{
    immediateRestart(lastVideoError.length()?lastVideoError.c_str():"AVI_REC_UNEXPECTED_END");
  }
  recording=false;stopRequested=false;videoMode=false;recTaskHandle=nullptr;vTaskDelete(nullptr);
}

static void recordTask(void*){
  touchRecordingHeartbeat();
  String dir=String(RECORD_DIR)+"/"+currentSession;
  String csvPath=dir+"/frames.csv";

  // Read durable progress before reopening frames.csv for append.
  uint32_t firstSavedTs=0, lastSavedTs=0;
  bool haveFirst=false;
  if(resumeMode && frameCount>0){
    uint32_t durableFrame=0;
    if(readRecordingProgress(currentSession,durableFrame,firstSavedTs,lastSavedTs) && durableFrame>0){
      frameCount=durableFrame;
      haveFirst=true;
      elapsedBaseMs=lastSavedTs + intervalMsCfg;
    }
  }

  File csv=SD_MMC.open(csvPath.c_str(), resumeMode ? FILE_APPEND : FILE_WRITE);
  if(!csv){ restartForSdFault("CSV_OPEN_FAILED"); }
  if(!resumeMode || csv.size()==0) csv.println("frame,timestamp_ms");

  uint32_t nextDue=millis();

  uint32_t activeSegment=0;
  String segmentDir="";
  uint8_t consecutiveWriteFailures=0;

  while(!stopRequested && frameCount<targetCount){
    if(intervalMsCfg){ int32_t wait=(int32_t)(nextDue-millis()); if(wait>0)delay(wait); }

    uint32_t frameNo=frameCount+1;
    uint32_t segmentNo=((frameNo-1)/FRAMES_PER_SEGMENT)+1;
    if(segmentNo!=activeSegment){
      char segName[24]; snprintf(segName,sizeof(segName),"SEG_%04u",segmentNo);
      segmentDir=dir+"/"+segName;
      if(!SD_MMC.exists(segmentDir.c_str()) && !SD_MMC.mkdir(segmentDir.c_str())){
        restartForSdFault("SEGMENT_MKDIR_FAILED",&csv);
      }
      activeSegment=segmentNo;
      Serial.printf("REC: segment %u -> %s\n",activeSegment,segmentDir.c_str());
    }

    uint32_t ts=elapsedBaseMs + (millis()-startedMs);
    camera_fb_t *fb=esp_camera_fb_get();
    if(!fb){delay(5);continue;}
    char name[32]; snprintf(name,sizeof(name),"frame_%06u.jpg",frameNo);
    bool ok=saveFrame(fb,segmentDir+"/"+name); esp_camera_fb_return(fb);
    if(ok){
      consecutiveWriteFailures=0;
      frameCount++; touchRecordingHeartbeat();
      if(!haveFirst){firstSavedTs=ts;haveFirst=true;} lastSavedTs=ts;
      if(csv){
        int written=csv.printf("%u,%u\n",frameCount,ts);
        if(written<=0) restartForSdFault("CSV_WRITE_FAILED",&csv);
        if((frameCount%20)==0)csv.flush();
      }
    } else {
      consecutiveWriteFailures++;
      Serial.printf("REC: JPEG save failed (%u/%u) frame=%u\n",consecutiveWriteFailures,SD_WRITE_FAIL_RESTART_COUNT,frameNo);
      if(consecutiveWriteFailures>=SD_WRITE_FAIL_RESTART_COUNT){
        restartForSdFault("JPEG_WRITE_FAILED",&csv);
      }
    }
    nextDue = intervalMsCfg ? nextDue+intervalMsCfg : millis();
    delay(1);
  }

  if(csv){csv.flush();csv.close();}

  bool normalStop=stopRequested;
  bool targetComplete=(frameCount>=targetCount);
  if(!writeRecordingSummary(currentSession,frameCount,firstSavedTs,lastSavedTs)) Serial.println("REC: summary write failed");
  Serial.printf("REC saved: %s frames=%u elapsed=%ums reason=%s\n",currentSession.c_str(),frameCount,
                elapsedBaseMs+(millis()-startedMs), targetComplete?"TARGET_COMPLETE":normalStop?"USER_STOP":"ENDED");

  // Only a deliberate STOP or reaching the target marks this recording complete.
  // Any crash/brownout/SD restart happens before this point and leaves NVS active.
  if(normalStop || targetComplete) clearResumeState();
  recording=false; stopRequested=false; resumeMode=false; autoResumed=false; recTaskHandle=nullptr; vTaskDelete(nullptr);
}

// Find the highest directory number currently present. Never fill holes.
static uint32_t nextSessionNumber(){
  uint32_t maxNo=0;
  File root=SD_MMC.open(RECORD_DIR);
  if(!root)return 1;
  File d=root.openNextFile();
  while(d){
    if(d.isDirectory()){
      String name=String(d.name()); int slash=name.lastIndexOf('/');
      if(slash>=0)name=name.substring(slash+1);
      if(name.startsWith("REC_") && name.length()>4){
        bool digits=true;
        for(size_t i=4;i<name.length();i++)if(!isdigit((unsigned char)name[i])){digits=false;break;}
        if(digits){uint32_t n=strtoul(name.c_str()+4,nullptr,10);if(n>maxNo)maxNo=n;}
      }
    }
    d.close();d=root.openNextFile();
  }
  root.close();
  return maxNo<UINT32_MAX ? maxNo+1 : 0;
}

static bool saveStartDate(const String &session,const String &date){
  if(date.length()<19 || date.length()>40)return false;
  // Only accept an ISO-like browser timestamp (avoid path/content injection).
  for(size_t i=0;i<date.length();i++){
    char c=date[i];
    if(!(isdigit((unsigned char)c)||c=='-'||c==':'||c=='T'||c=='+'||c=='Z'||c=='.'))return false;
  }
  String path=String(RECORD_DIR)+"/"+session+"/started_at.txt";
  File f=SD_MMC.open(path.c_str(),FILE_WRITE);
  if(!f)return false;
  f.println(date);f.close();return true;
}

bool recorderStart(uint32_t frames,uint32_t intervalMs,const String &startedAt,bool video){
  lastStartError="";lastVideoError="";
  if(recording){ lastStartError="ALREADY_RECORDING"; return false; }
  if(video && resumePending){lastStartError="JPEG_RESUME_PENDING";return false;}

  // A boot-time SD mount can fail transiently. Retry once when the user presses REC
  // instead of leaving the recorder permanently stuck in 409 until the next reboot.
  if(!sdReady){
    Serial.println("REC: SD not ready at start; retrying mount...");
    SD_MMC.end();
    delay(100);
    if(!mountSd()){
      lastStartError="SD_NOT_READY";
      return false;
    }
  }

  if(frames<1)frames=1; if(frames>10000)frames=10000; if(intervalMs>60000)intervalMs=60000;
  uint32_t n=nextSessionNumber();
  if(!n){lastStartError="SESSION_NUMBER_OVERFLOW";return false;}
  char session[32],path[64];
  snprintf(session,sizeof(session),"REC_%04u",n);
  snprintf(path,sizeof(path),RECORD_DIR "/%s",session);
  if(SD_MMC.exists(path)){lastStartError="SESSION_NUMBER_COLLISION";return false;}
  if(!SD_MMC.mkdir(path)){Serial.println("REC: session mkdir failed");lastStartError="SESSION_MKDIR_FAILED";return false;}
  if(!startedAt.isEmpty() && !saveStartDate(session,startedAt))
    Serial.println("REC: start timestamp unavailable");
  // Remember the recording format even if the first AVI is interrupted.
  File mf=SD_MMC.open((String(path)+"/format.txt").c_str(),FILE_WRITE);
  if(mf){mf.println(video?"avi":"jpg");mf.close();}
  currentSession=session; frameCount=0; targetCount=frames; intervalMsCfg=intervalMs; stopRequested=false; startedMs=millis(); elapsedBaseMs=0; recording=true; resumeMode=false; autoResumed=startingRecoveredAvi;
  videoMode=video;activeVideoPart=0;finalizedVideoParts=0;videoPartStartedMs=0;
  touchRecordingHeartbeat();
  if(!video)saveResumeState(currentSession,targetCount,intervalMsCfg);
  if(video){
    if(startingRecoveredAvi){
      String marker=String(path)+"/recovered_from.txt";
      File f=SD_MMC.open(marker.c_str(),FILE_WRITE);
      if(f){f.printf("Recovered after reset from %s\n",aviRecoveryFrom.c_str());f.close();}
    }
    if(!startingRecoveredAvi){
      aviOriginalTarget=frames;aviDurableFrames=0;aviRecoveryRestarts=0;
    }
    aviRecoverInterval=intervalMs;
    aviRecoveryFrom=currentSession;
    aviRecoveryPending=true;
    persistAviRecovery();
  }
  if(xTaskCreatePinnedToCore(video?videoTask:recordTask,video?"avi-rec":"jpg-rec",12288,nullptr,2,&recTaskHandle,1)!=pdPASS){
    recording=false;
    if(!video)clearResumeState();else clearAviRecovery();
    lastStartError="TASK_CREATE_FAILED"; return false;
  }
  Serial.printf("REC started: %s target=%u interval=%ums\n",currentSession.c_str(),targetCount,intervalMsCfg);return true;
}

String recorderLastStartError(){
  return lastStartError;
}

bool recorderAutoResume(){
  if(recording || !sdReady) return false;
  if(!resumePending && aviRecoveryPending){
    if(aviDurableFrames>=aviOriginalTarget){
      Serial.println("AVI RECOVERY: target already complete");
      clearAviRecovery();return false;
    }
    if(aviRecoveryRestarts>=AVI_RECOVERY_MAX_RESTARTS){
      Serial.println("AVI RECOVERY: too many consecutive restarts; stopping to avoid reboot loop");
      clearAviRecovery();return false;
    }
    String previous=aviRecoveryFrom;
    uint32_t remain=aviOriginalTarget-aviDurableFrames;
    ++aviRecoveryRestarts;
    persistAviRecovery(); // Persist the retry count BEFORE starting again.
    startingRecoveredAvi=true;
    bool started=recorderStart(remain,aviRecoverInterval,"",true);
    startingRecoveredAvi=false;
    if(started){
      Serial.printf("AVI AUTO-RESUME: new=%s previous=%s durable=%u remaining=%u attempt=%u\n",
                    currentSession.c_str(),previous.c_str(),aviDurableFrames,remain,aviRecoveryRestarts);
    }else{
      // Failed to *start* is not another camera failure. Retry later if SD
      // comes back, without burning all five allowed reset attempts at once.
      if(aviRecoveryRestarts>0)--aviRecoveryRestarts;
      persistAviRecovery();
      Serial.printf("AVI AUTO-RESUME deferred: %s\n",lastStartError.c_str());
    }
    return started;
  }
  if(!resumePending) return false;
  String s=safeSession(pendingSession);
  if(s.length()==0 || pendingTarget<1){ Serial.println("REC: invalid pending resume metadata"); return false; }
  String dir=String(RECORD_DIR)+"/"+s;
  if(!SD_MMC.exists(dir.c_str())){ Serial.printf("REC: resume directory missing: %s\n",dir.c_str()); return false; }

  uint32_t lastFrame=0,firstTs=0,lastTs=0;
  readRecordingProgress(s,lastFrame,firstTs,lastTs);
  if(lastFrame>=pendingTarget){
    Serial.printf("REC: pending session already complete (%u/%u)\n",lastFrame,pendingTarget);
    writeRecordingSummary(s,lastFrame,firstTs,lastTs);
    clearResumeState();
    return false;
  }

  // An old summary can exist if Files was opened during an earlier interrupted run.
  String summaryPath=dir+"/summary.csv";
  if(SD_MMC.exists(summaryPath.c_str())) SD_MMC.remove(summaryPath.c_str());

  currentSession=s; frameCount=lastFrame; targetCount=pendingTarget; intervalMsCfg=pendingInterval;
  stopRequested=false; startedMs=millis(); elapsedBaseMs=(lastFrame>0)?(lastTs+intervalMsCfg):0;
  recording=true; resumeMode=true; autoResumed=true;
  if(xTaskCreatePinnedToCore(recordTask,"jpg-rec",12288,nullptr,2,&recTaskHandle,1)!=pdPASS){recording=false;resumeMode=false;autoResumed=false;return false;}
  Serial.printf("REC AUTO-RESUME: %s from frame=%u target=%u reset=%s fault=%s\n",
                currentSession.c_str(),frameCount,targetCount,resetReasonName(),pendingFault.c_str());
  return true;
}

void recorderService(){
  static uint32_t lastTry=0;
  if(recording) return;

  // Self-heal SD even when there is no pending resume session.
  if(!sdReady){
    if(millis()-lastTry<SD_RECOVERY_RETRY_MS) return;
    lastTry=millis();
    Serial.println("REC: SD not ready; retrying mount...");
    SD_MMC.end();
    delay(50);
    mountSd();
  }

  if((resumePending || aviRecoveryPending) && sdReady) recorderAutoResume();
}

bool recorderStop(){if(!recording)return false;stopRequested=true;return true;}
bool recorderIsRecording(){return recording;}
String recorderStatusJson(){
  uint32_t elapsed=recording?(elapsedBaseMs+(millis()-startedMs)):0;
  return String("{\"sdReady\":")+(sdReady?"true":"false")+
    ",\"recording\":"+(recording?"true":"false")+
    ",\"session\":\""+currentSession+"\""+
    ",\"mode\":\""+String(videoMode?"avi":"jpg")+"\""+
    ",\"videoError\":\""+lastVideoError+"\""+
    ",\"frames\":"+frameCount+
    ",\"target\":"+targetCount+
    ",\"intervalMs\":"+intervalMsCfg+
    ",\"seconds\":"+(elapsed/1000)+
    ",\"aviPart\":"+String((uint32_t)activeVideoPart)+
    ",\"aviFinalized\":"+String((uint32_t)finalizedVideoParts)+
    ",\"aviPartSeconds\":"+String(activeVideoPart?(millis()-videoPartStartedMs)/1000:0)+
    ",\"resumePending\":"+(resumePending?"true":"false")+
    ",\"autoResumed\":"+(autoResumed?"true":"false")+
    ",\"resetReason\":\""+String(resetReasonName())+"\""+
    ",\"recoveryFault\":\""+lastRecoveryFault+"\""+
    ",\"aviRecoveryPending\":"+String(aviRecoveryPending?"true":"false")+
    ",\"aviRecoveredFrames\":"+String(aviDurableFrames)+
    ",\"aviRecoveryAttempts\":"+String(aviRecoveryRestarts)+
    ",\"lastFault\":\""+pendingFault+"\"}";
}

static bool readSummary(const String &session,uint32_t &frames,uint32_t &durationMs,float &recordedFps){
  frames=0; durationMs=0; recordedFps=0.0f;
  String path=String(RECORD_DIR)+"/"+session+"/summary.csv";
  File f=SD_MMC.open(path.c_str(),FILE_READ); if(!f)return false;
  f.readStringUntil('\n'); String line=f.readStringUntil('\n'); f.close(); line.trim();
  int c1=line.indexOf(','), c2=(c1>=0)?line.indexOf(',',c1+1):-1; if(c1<0||c2<0)return false;
  frames=strtoul(line.substring(0,c1).c_str(),nullptr,10);
  durationMs=strtoul(line.substring(c1+1,c2).c_str(),nullptr,10);
  recordedFps=line.substring(c2+1).toFloat(); return true;
}

// One-time migration for recordings made before summary.csv existed.
// Reads only frames.csv (never scans thousands of JPEG files), then caches the result.
static bool migrateLegacySummary(const String &session,uint32_t &frames,uint32_t &durationMs,float &recordedFps){
  uint32_t firstTs=0,lastTs=0;
  if(!readRecordingProgress(session,frames,firstTs,lastTs) || frames==0){frames=0;durationMs=0;recordedFps=0.0f;return false;}
  durationMs=(frames>1&&lastTs>firstTs)?lastTs-firstTs:0;
  recordedFps=durationMs?((float)(frames-1)*1000.0f/(float)durationMs):0.0f;
  writeRecordingSummary(session,frames,firstTs,lastTs); return true;
}

// Read metadata directly from a FINALIZED AVI (RIFF/idx1). No full video
// scan required; works after restart, without a separate sidecar database.
static uint32_t aviU32(const uint8_t *p){
  return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);
}
static bool aviPartMetadata(const String &path,uint32_t &frames,float &fps){
  frames=0;fps=0;
  File f=SD_MMC.open(path.c_str(),FILE_READ);
  if(!f)return false;
  uint8_t head[12],loc[12],tail[8],rates[8];
  bool ok=f.size()>=248 && f.seek(0) && f.read(head,12)==12 &&
          memcmp(head,"RIFF",4)==0 && memcmp(head+8,"AVI ",4)==0 &&
          f.seek(212) && f.read(loc,12)==12 &&
          memcmp(loc,"LIST",4)==0 && memcmp(loc+8,"movi",4)==0;
  uint64_t idxAt=ok?uint64_t(220)+aviU32(loc+4):0;
  if(ok)ok=idxAt+8<=f.size() && f.seek(uint32_t(idxAt)) &&
           f.read(tail,8)==8 && memcmp(tail,"idx1",4)==0;
  if(ok){
    uint32_t indexBytes=aviU32(tail+4);
    ok=indexBytes>=16 && (indexBytes%16)==0 &&
       idxAt+8+indexBytes<=f.size() && f.seek(128) && f.read(rates,8)==8;
    if(ok){
      frames=indexBytes/16;
      uint32_t scale=aviU32(rates),rate=aviU32(rates+4);
      fps=scale?float(rate)/float(scale):0.0f;
    }
  }
  f.close();return ok;
}

static bool parseVideoPart(const String &fileName,uint32_t &part){
  if(!fileName.startsWith("video_") || !fileName.endsWith(".avi"))return false;
  String num=fileName.substring(6,fileName.length()-4);
  if(num.length()<4 || num.length()>10)return false;
  for(size_t i=0;i<num.length();i++)if(!isdigit((unsigned char)num[i]))return false;
  part=strtoul(num.c_str(),nullptr,10);
  return part>=1 && part<=10000;
}

String recorderFilesJson(){
  String j="[";
  if(!sdReady)return j+"]";
  File root=SD_MMC.open(RECORD_DIR);
  if(!root)return j+"]";
  bool first=true;
  File d=root.openNextFile();
  while(d){
    if(d.isDirectory()){
      String n=String(d.name());int p=n.lastIndexOf('/');if(p>=0)n=n.substring(p+1);
      if(n.startsWith("REC_")){
        uint32_t frames=0,durationMs=0;float recordedFps=0.0f;
        bool incomplete=((recording && n==currentSession) || (resumePending && n==pendingSession));
        if(incomplete){
          uint32_t firstTs=0,lastTs=0;
          if(recording && n==currentSession){
            frames=frameCount;
            durationMs=frames>1?elapsedBaseMs+(millis()-startedMs):0;
          }else if(readRecordingProgress(n,frames,firstTs,lastTs)){
            durationMs=(frames>1&&lastTs>firstTs)?lastTs-firstTs:0;
          }
          recordedFps=durationMs&&frames>1?float(frames-1)*1000.0f/float(durationMs):0.0f;
        }else if(!readSummary(n,frames,durationMs,recordedFps)){
          migrateLegacySummary(n,frames,durationMs,recordedFps);
        }

        // Existing single-file AVI and new rolling AVI parts are both supported.
        // Only announce files with a valid finalized index. During recording the
        // currently open part is intentionally hidden.
        String parts="[";bool firstPart=true;uint32_t totalVideoFrames=0;
        uint32_t totalVideoMs=0;uint32_t videoFiles=0;
        String folder=String(RECORD_DIR)+"/"+n;
        File sdDir=SD_MMC.open(folder.c_str());
        if(sdDir){
          File item=sdDir.openNextFile();
          while(item){
            if(!item.isDirectory()){
              String fileName=String(item.name());int slash=fileName.lastIndexOf('/');
              if(slash>=0)fileName=fileName.substring(slash+1);
              uint32_t part=0;
              bool eligible=(fileName=="video.avi" || parseVideoPart(fileName,part));
              if(eligible && !(recording && n==currentSession && part>0 && part==activeVideoPart)){
                String aviPath=folder+"/"+fileName;
                // Close the directory entry before opening the video for metadata.
                item.close();
                uint32_t nf=0;float fps=0;
                if(aviPartMetadata(aviPath,nf,fps)){
                  if(!firstPart)parts+=",";firstPart=false;
                  uint32_t ms=(nf>1&&fps>0)?uint32_t(float(nf-1)*1000.0f/fps):0;
                  parts += "{\"part\":";
                  parts += String(part);
                  parts += ",\"file\":\"";
                  parts += fileName;
                  parts += "\",\"frames\":";
                  parts += String(nf);
                  parts += ",\"recordedFps\":";
                  parts += String(fps,2);
                  parts += ",\"durationMs\":";
                  parts += String(ms);
                  parts += "}";
                  totalVideoFrames+=nf;totalVideoMs+=ms;videoFiles++;
                }
              }else item.close();
            }else item.close();
            item=sdDir.openNextFile();
          }
          sdDir.close();
        }
        parts+="]";
        bool currentAvi=recording && videoMode && n==currentSession;
        bool savedAsAvi=false;
        File mf=SD_MMC.open((folder+"/format.txt").c_str(),FILE_READ);
        if(mf){String t=mf.readStringUntil('\n');t.trim();savedAsAvi=(t=="avi");mf.close();}
        bool hasVideo=(videoFiles>0 || currentAvi || savedAsAvi);
        // A crash may leave the last AVI unfinished. Its already finalized
        // parts still show up with reconstructed totals.
        if(!incomplete && frames==0 && totalVideoFrames>0){
          frames=totalVideoFrames;durationMs=totalVideoMs;
          recordedFps=totalVideoMs&&frames>1?float(frames-1)*1000.0f/float(totalVideoMs):0.0f;
        }
        String startedAt="";
        File tf=SD_MMC.open((folder+"/started_at.txt").c_str(),FILE_READ);
        if(tf){startedAt=tf.readStringUntil('\n');startedAt.trim();tf.close();}
        if(!first)j+=",";first=false;
        j+="{\"video\":";j+=(hasVideo?"true":"false");
        j+=",\"segments\":";j+=parts;
        j+=",\"startedAt\":\"";j+=startedAt;
        j+="\",\"name\":\"";j+=n;
        j+="\",\"frames\":";j+=String(frames);
        j+=",\"durationMs\":";j+=String(durationMs);
        j+=",\"recordedFps\":";j+=String(recordedFps,2);
        j+=",\"incomplete\":";j+=(incomplete?"true":"false");
        j+="}";
      }
    }
    d.close();d=root.openNextFile();
  }
  root.close();return j+"]";
}

String recorderFramePath(const String &session,uint32_t n){
  String s=safeSession(session);
  if(s.length()==0 || n<1)return "";
  char fn[32]; snprintf(fn,sizeof(fn),"frame_%06u.jpg",n);
  uint32_t segmentNo=((n-1)/FRAMES_PER_SEGMENT)+1;
  char segName[24]; snprintf(segName,sizeof(segName),"SEG_%04u",segmentNo);
  String sessionDir=String(RECORD_DIR)+"/"+s;
  String segmentDir=sessionDir+"/"+segName;
  if(sdReady && SD_MMC.exists(segmentDir.c_str())) return segmentDir+"/"+fn;
  return sessionDir+"/"+fn;
}

bool recorderFrameExists(const String &session,uint32_t n){
  if(!sdReady||n<1)return false;
  String path=recorderFramePath(session,n);
  return path.length() && SD_MMC.exists(path.c_str());
}

static bool removeTree(File dir) {
  bool ok = true;
  File entry = dir.openNextFile();
  while (entry) {
    String path = String(entry.path());
    bool isDir = entry.isDirectory();
    entry.close();
    if (isDir) {
      File child = SD_MMC.open(path.c_str());
      if (child) { if (!removeTree(child)) ok = false; child.close(); } else ok = false;
      if (!SD_MMC.rmdir(path.c_str())) ok = false;
    } else {
      if (!SD_MMC.remove(path.c_str())) ok = false;
    }
    entry = dir.openNextFile();
  }
  return ok;
}

bool recorderDeleteSession(const String &session) {
  String s = safeSession(session);
  if (!sdReady || recording || s.length() == 0 || !s.startsWith("REC_")) return false;
  // Never delete the session that is waiting to be resumed.
  if(resumePending && s==pendingSession) return false;
  String path = String(RECORD_DIR) + "/" + s;
  if (!SD_MMC.exists(path.c_str())) return false;
  File dir = SD_MMC.open(path.c_str());
  if (!dir || !dir.isDirectory()) { if (dir) dir.close(); return false; }
  bool ok = removeTree(dir);
  dir.close();
  if (!SD_MMC.rmdir(path.c_str())) ok = false;
  Serial.printf("REC delete: %s result=%s\n", path.c_str(), ok ? "OK" : "FAILED");
  return ok;
}

String recorderVideoPath(const String &session,uint32_t part){
  String s=safeSession(session);
  if(s.isEmpty() || !s.startsWith("REC_") || part>10000)return "";
  String dir=String(RECORD_DIR)+"/"+s+"/";
  if(part==0)return dir+"video.avi"; // existing recordings
  char name[32];snprintf(name,sizeof(name),"video_%04u.avi",part);
  return dir+name;
}
bool recorderVideoExists(const String &session,uint32_t part){
  if(!sdReady || recording)return false; // avoid SD reads during active capture
  String p=recorderVideoPath(session,part);
  return p.length()&&SD_MMC.exists(p.c_str());
}
