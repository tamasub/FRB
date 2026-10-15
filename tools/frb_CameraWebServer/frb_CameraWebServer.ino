/**********************************************************************
  Filename    : Camera Web Server
  Description : The camera images captured by the ESP32S3 are displayed on the web page.
  Auther      : www.freenove.com
  Modification: 2026/05/16
**********************************************************************/
#include "esp_camera.h"
#include <WiFi.h>
#include "board_config.h"
#include "sd_recorder.h"
#include "battery_monitor.h"

// FRB Sea Camera: field operation is AP-only.
static const char *CAMERA_AP_SSID = "FRB_CAM";

// ===================
// Select camera model
// ===================
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
//#define CAMERA_MODEL_ESP_EYE // Has PSRAM
#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_UNITCAM // No PSRAM
//#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
// ** Espressif Internal Boards **
//#define CAMERA_MODEL_ESP32_CAM_BOARD
//#define CAMERA_MODEL_ESP32S2_CAM_BOARD
//#define CAMERA_MODEL_ESP32S3_CAM_LCD

#include "camera_pins.h"

camera_config_t config;

void startCameraServer();
bool camera_init();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Battery divider: LiPo+ -> 20k -> GPIO1 -> 20k -> GND.
  batteryMonitorInit();

  // IMPORTANT: initialize SD_MMC before the camera.
  // Freenove Sketch_07.3 uses this order on this board; initializing the
  // camera first can leave SD_MMC unable to complete card initialization.
  recorderInit();
  if (!camera_init()) {
    Serial.println("FRB: camera failed to initialize after retries. Restarting to recover.");
    Serial.flush();
    delay(1200);
    ESP.restart();
  }

  // Field-only AP mode: no STA/home Wi-Fi connection is attempted.
  WiFi.mode(WIFI_AP);
  WiFi.setSleep(false);
  if (WiFi.softAP(CAMERA_AP_SSID)) {
    Serial.print("Camera AP ready (AP-only): http://");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.println("Camera AP start failed");
  }

  startCameraServer();

  // Independent supervisor watches for stalled camera / SD capture and AP mode.
  recorderStartSupervisor();
  // JPEG resumes the old session. AVI always starts a NEW REC folder after a
  // reset to avoid overwriting its most recent (possibly unfinished) AVI.
  recorderAutoResume();

  Serial.print("Direct AP URL: http://");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  // Keep recovery alive even when the SD card did not remount immediately.
  recorderService();
  delay(500);
}

bool camera_init() {
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;
  //config.frame_size = FRAMESIZE_XGA;
  config.frame_size = FRAMESIZE_UXGA;
  
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 2; // streaming/recording headroom (OV2640 + PSRAM)
  
  // Retry a failed sensor configuration once. Never dereference a null
  // sensor (the original implementation could panic before AP was started).
  esp_err_t err=ESP_FAIL;
  for(int attempt=1; attempt<=2; ++attempt){
    err=esp_camera_init(&config);
    if(err==ESP_ERR_NOT_SUPPORTED && config.pixel_format==PIXFORMAT_JPEG){
      config.pixel_format=PIXFORMAT_RGB565;
      err=esp_camera_init(&config);
    }
    if(err==ESP_OK && esp_camera_sensor_get()!=nullptr)break;
    Serial.printf("FRB camera init attempt %d failed (0x%x)\n",attempt,(unsigned)err);
    esp_camera_deinit();
    delay(450);
  }
  if(err!=ESP_OK || !esp_camera_sensor_get())return false;

  sensor_t * s = esp_camera_sensor_get();
  // drop down frame size for higher initial frame rate
  uint16_t pid = s->id.PID;
  if(pid == OV2640_PID){
    s->set_framesize(s, FRAMESIZE_XGA);
    s->set_hmirror(s, 1);
    s->set_vflip(s, 0);     
  }
  else if(pid == OV3660_PID){
    s->set_hmirror(s, 1);
    s->set_vflip(s, 0);     
  }
  else if(pid == GC2145_PID){
    s->set_hmirror(s, 0);
    delay(500);
    s->set_vflip(s, 0);      
  }
  else if(pid == GC0308_PID){
    // FRB Sea Camera: default mirror ON so the live/recorded image has the expected orientation.
    s->set_hmirror(s, 1);
    delay(500);
    s->set_vflip(s, 0);     
  }
  else{
    s->set_hmirror(s, 1);
    s->set_vflip(s, 0);       
  }
  s->set_brightness(s, 1);  // Slightly increase brightness
  s->set_saturation(s, 0);  // Reduce saturation
  s->set_ae_level(s, -3);   // Set exposure compensation level
  return true;
}
