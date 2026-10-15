// Copyright 2015-2016 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include "esp_http_server.h"
#include "esp_timer.h"
#include "esp_camera.h"
#include "img_converters.h"
#include "fb_gfx.h"
#include "esp32-hal-ledc.h"
#include "sdkconfig.h"
#include "camera_index.h"
#include "board_config.h"
#include "sd_recorder.h"
#include "SD_MMC.h"
#include "battery_monitor.h"

#if defined(ARDUINO_ARCH_ESP32) && defined(CONFIG_ARDUHAL_ESP_LOG)
#include "esp32-hal-log.h"
#endif

// LED FLASH setup
#if defined(LED_GPIO_NUM)
#define CONFIG_LED_MAX_INTENSITY 255

int led_duty = 0;
bool isStreaming = false;

#endif

typedef struct {
  httpd_req_t *req;
  size_t len;
} jpg_chunking_t;

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\nX-Timestamp: %d.%06d\r\n\r\n";

httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

typedef struct {
  size_t size;   //number of values used for filtering
  size_t index;  //current value index
  size_t count;  //value count
  int sum;
  int *values;  //array to be filled with values
} ra_filter_t;

static ra_filter_t ra_filter;

static ra_filter_t *ra_filter_init(ra_filter_t *filter, size_t sample_size) {
  memset(filter, 0, sizeof(ra_filter_t));

  filter->values = (int *)malloc(sample_size * sizeof(int));
  if (!filter->values) {
    return NULL;
  }
  memset(filter->values, 0, sample_size * sizeof(int));

  filter->size = sample_size;
  return filter;
}

#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
static int ra_filter_run(ra_filter_t *filter, int value) {
  if (!filter->values) {
    return value;
  }
  filter->sum -= filter->values[filter->index];
  filter->values[filter->index] = value;
  filter->sum += filter->values[filter->index];
  filter->index++;
  filter->index = filter->index % filter->size;
  if (filter->count < filter->size) {
    filter->count++;
  }
  return filter->sum / filter->count;
}
#endif

#if defined(LED_GPIO_NUM)
void enable_led(bool en) {  // Turn LED On or Off
  int duty = en ? led_duty : 0;
  if (en && isStreaming && (led_duty > CONFIG_LED_MAX_INTENSITY)) {
    duty = CONFIG_LED_MAX_INTENSITY;
  }
  ledcWrite(LED_GPIO_NUM, duty);
  //ledc_set_duty(CONFIG_LED_LEDC_SPEED_MODE, CONFIG_LED_LEDC_CHANNEL, duty);
  //ledc_update_duty(CONFIG_LED_LEDC_SPEED_MODE, CONFIG_LED_LEDC_CHANNEL);
  log_i("Set LED intensity to %d", duty);
}
#endif

static esp_err_t bmp_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
  uint64_t fr_start = esp_timer_get_time();
#endif
  fb = esp_camera_fb_get();
  if (!fb) {
    log_e("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/x-windows-bmp");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.bmp");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  char ts[32];
  snprintf(ts, 32, "%lld.%06ld", fb->timestamp.tv_sec, fb->timestamp.tv_usec);
  httpd_resp_set_hdr(req, "X-Timestamp", (const char *)ts);

  uint8_t *buf = NULL;
  size_t buf_len = 0;
  bool converted = frame2bmp(fb, &buf, &buf_len);
  esp_camera_fb_return(fb);
  if (!converted) {
    log_e("BMP Conversion failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }
  res = httpd_resp_send(req, (const char *)buf, buf_len);
  free(buf);
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
  uint64_t fr_end = esp_timer_get_time();
#endif
  log_i("BMP: %llums, %uB", (uint64_t)((fr_end - fr_start) / 1000), buf_len);
  return res;
}

static size_t jpg_encode_stream(void *arg, size_t index, const void *data, size_t len) {
  jpg_chunking_t *j = (jpg_chunking_t *)arg;
  if (!index) {
    j->len = 0;
  }
  if (httpd_resp_send_chunk(j->req, (const char *)data, len) != ESP_OK) {
    return 0;
  }
  j->len += len;
  return len;
}

static esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
  int64_t fr_start = esp_timer_get_time();
#endif

#if defined(LED_GPIO_NUM)
  enable_led(true);
  vTaskDelay(150 / portTICK_PERIOD_MS);  // The LED needs to be turned on ~150ms before the call to esp_camera_fb_get()
  fb = esp_camera_fb_get();              // or it won't be visible in the frame. A better way to do this is needed.
  enable_led(false);
#else
  fb = esp_camera_fb_get();
#endif

  if (!fb) {
    log_e("Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  char ts[32];
  snprintf(ts, 32, "%lld.%06ld", fb->timestamp.tv_sec, fb->timestamp.tv_usec);
  httpd_resp_set_hdr(req, "X-Timestamp", (const char *)ts);

#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
  size_t fb_len = 0;
#endif
  if (fb->format == PIXFORMAT_JPEG) {
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
    fb_len = fb->len;
#endif
    res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  } else {
    jpg_chunking_t jchunk = {req, 0};
    res = frame2jpg_cb(fb, 80, jpg_encode_stream, &jchunk) ? ESP_OK : ESP_FAIL;
    httpd_resp_send_chunk(req, NULL, 0);
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
    fb_len = jchunk.len;
#endif
  }
  esp_camera_fb_return(fb);
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
  int64_t fr_end = esp_timer_get_time();
#endif
  log_i("JPG: %uB %ums", (uint32_t)(fb_len), (uint32_t)((fr_end - fr_start) / 1000));
  return res;
}

static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t *fb = NULL;
  struct timeval _timestamp;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  char *part_buf[128];

  static int64_t last_frame = 0;
  if (!last_frame) {
    last_frame = esp_timer_get_time();
  }

  // FRB Sea Camera: recording owns the camera exclusively.
  // Reject a new MJPEG stream while SD recording is active.
  if (recorderIsRecording()) {
    httpd_resp_set_status(req, "409 Conflict");
    httpd_resp_set_type(req, "text/plain; charset=utf-8");
    return httpd_resp_sendstr(req, "Camera is recording; live stream is paused.");
  }

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) {
    return res;
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "X-Framerate", "60");

#if defined(LED_GPIO_NUM)
  isStreaming = true;
  enable_led(true);
#endif

  while (true) {
    // If REC starts while a stream connection already exists, release it
    // before the recorder starts competing for camera frame buffers.
    if (recorderIsRecording()) {
      log_i("FRB: live stream stopped because recording started");
      res = ESP_OK;
      break;
    }
    fb = esp_camera_fb_get();
    if (!fb) {
      log_e("Camera capture failed");
      res = ESP_FAIL;
    } else {
      _timestamp.tv_sec = fb->timestamp.tv_sec;
      _timestamp.tv_usec = fb->timestamp.tv_usec;
      if (fb->format != PIXFORMAT_JPEG) {
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!jpeg_converted) {
          log_e("JPEG compression failed");
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }
    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 128, _STREAM_PART, _jpg_buf_len, _timestamp.tv_sec, _timestamp.tv_usec);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }
    if (res != ESP_OK) {
      log_e("Send frame failed");
      break;
    }
    int64_t fr_end = esp_timer_get_time();

    int64_t frame_time = fr_end - last_frame;
    last_frame = fr_end;

    frame_time /= 1000;
#if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_INFO
    uint32_t avg_frame_time = ra_filter_run(&ra_filter, frame_time);
#endif
    log_i(
      "MJPG: %uB %ums (%.1ffps), AVG: %ums (%.1ffps)", (uint32_t)(_jpg_buf_len), (uint32_t)frame_time, 1000.0 / (uint32_t)frame_time, avg_frame_time,
      1000.0 / avg_frame_time
    );
  }

#if defined(LED_GPIO_NUM)
  isStreaming = false;
  enable_led(false);
#endif

  return res;
}

static esp_err_t parse_get(httpd_req_t *req, char **obuf) {
  char *buf = NULL;
  size_t buf_len = 0;

  buf_len = httpd_req_get_url_query_len(req) + 1;
  if (buf_len > 1) {
    buf = (char *)malloc(buf_len);
    if (!buf) {
      httpd_resp_send_500(req);
      return ESP_FAIL;
    }
    if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK) {
      *obuf = buf;
      return ESP_OK;
    }
    free(buf);
  }
  httpd_resp_send_404(req);
  return ESP_FAIL;
}

static esp_err_t cmd_handler(httpd_req_t *req) {
  char *buf = NULL;
  char variable[32];
  char value[32];

  if (parse_get(req, &buf) != ESP_OK) {
    return ESP_FAIL;
  }
  if (httpd_query_key_value(buf, "var", variable, sizeof(variable)) != ESP_OK || httpd_query_key_value(buf, "val", value, sizeof(value)) != ESP_OK) {
    free(buf);
    httpd_resp_send_404(req);
    return ESP_FAIL;
  }
  free(buf);

  int val = atoi(value);
  log_i("%s = %d", variable, val);
  sensor_t *s = esp_camera_sensor_get();
  int res = 0;

  if (!strcmp(variable, "framesize")) {
    if (s->pixformat == PIXFORMAT_JPEG) {
      res = s->set_framesize(s, (framesize_t)val);
    }
  } else if (!strcmp(variable, "quality")) {
    res = s->set_quality(s, val);
  } else if (!strcmp(variable, "contrast")) {
    res = s->set_contrast(s, val);
  } else if (!strcmp(variable, "brightness")) {
    res = s->set_brightness(s, val);
  } else if (!strcmp(variable, "saturation")) {
    res = s->set_saturation(s, val);
  } else if (!strcmp(variable, "gainceiling")) {
    res = s->set_gainceiling(s, (gainceiling_t)val);
  } else if (!strcmp(variable, "colorbar")) {
    res = s->set_colorbar(s, val);
  } else if (!strcmp(variable, "awb")) {
    res = s->set_whitebal(s, val);
  } else if (!strcmp(variable, "agc")) {
    res = s->set_gain_ctrl(s, val);
  } else if (!strcmp(variable, "aec")) {
    res = s->set_exposure_ctrl(s, val);
  } else if (!strcmp(variable, "hmirror")) {
    res = s->set_hmirror(s, val);
  } else if (!strcmp(variable, "vflip")) {
    res = s->set_vflip(s, val);
  } else if (!strcmp(variable, "awb_gain")) {
    res = s->set_awb_gain(s, val);
  } else if (!strcmp(variable, "agc_gain")) {
    res = s->set_agc_gain(s, val);
  } else if (!strcmp(variable, "aec_value")) {
    res = s->set_aec_value(s, val);
  } else if (!strcmp(variable, "aec2")) {
    res = s->set_aec2(s, val);
  } else if (!strcmp(variable, "dcw")) {
    res = s->set_dcw(s, val);
  } else if (!strcmp(variable, "bpc")) {
    res = s->set_bpc(s, val);
  } else if (!strcmp(variable, "wpc")) {
    res = s->set_wpc(s, val);
  } else if (!strcmp(variable, "raw_gma")) {
    res = s->set_raw_gma(s, val);
  } else if (!strcmp(variable, "lenc")) {
    res = s->set_lenc(s, val);
  } else if (!strcmp(variable, "special_effect")) {
    res = s->set_special_effect(s, val);
  } else if (!strcmp(variable, "wb_mode")) {
    res = s->set_wb_mode(s, val);
  } else if (!strcmp(variable, "ae_level")) {
    res = s->set_ae_level(s, val);
  }
#if defined(LED_GPIO_NUM)
  else if (!strcmp(variable, "led_intensity")) {
    led_duty = val;
    if (isStreaming) {
      enable_led(true);
    }
  }
#endif
  else {
    log_i("Unknown command: %s", variable);
    res = -1;
  }

  if (res < 0) {
    return httpd_resp_send_500(req);
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

static int print_reg(char *p, sensor_t *s, uint16_t reg, uint32_t mask) {
  return sprintf(p, "\"0x%x\":%u,", reg, s->get_reg(s, reg, mask));
}

static esp_err_t status_handler(httpd_req_t *req) {
  static char json_response[1024];

  sensor_t *s = esp_camera_sensor_get();
  char *p = json_response;
  *p++ = '{';

  if (s->id.PID == OV5640_PID || s->id.PID == OV3660_PID) {
    for (int reg = 0x3400; reg < 0x3406; reg += 2) {
      p += print_reg(p, s, reg, 0xFFF);  //12 bit
    }
    p += print_reg(p, s, 0x3406, 0xFF);

    p += print_reg(p, s, 0x3500, 0xFFFF0);  //16 bit
    p += print_reg(p, s, 0x3503, 0xFF);
    p += print_reg(p, s, 0x350a, 0x3FF);   //10 bit
    p += print_reg(p, s, 0x350c, 0xFFFF);  //16 bit

    for (int reg = 0x5480; reg <= 0x5490; reg++) {
      p += print_reg(p, s, reg, 0xFF);
    }

    for (int reg = 0x5380; reg <= 0x538b; reg++) {
      p += print_reg(p, s, reg, 0xFF);
    }

    for (int reg = 0x5580; reg < 0x558a; reg++) {
      p += print_reg(p, s, reg, 0xFF);
    }
    p += print_reg(p, s, 0x558a, 0x1FF);  //9 bit
  } else if (s->id.PID == OV2640_PID) {
    p += print_reg(p, s, 0xd3, 0xFF);
    p += print_reg(p, s, 0x111, 0xFF);
    p += print_reg(p, s, 0x132, 0xFF);
  }

  p += sprintf(p, "\"xclk\":%u,", s->xclk_freq_hz / 1000000);
  p += sprintf(p, "\"pixformat\":%u,", s->pixformat);
  p += sprintf(p, "\"framesize\":%u,", s->status.framesize);
  p += sprintf(p, "\"quality\":%u,", s->status.quality);
  p += sprintf(p, "\"brightness\":%d,", s->status.brightness);
  p += sprintf(p, "\"contrast\":%d,", s->status.contrast);
  p += sprintf(p, "\"saturation\":%d,", s->status.saturation);
  p += sprintf(p, "\"sharpness\":%d,", s->status.sharpness);
  p += sprintf(p, "\"special_effect\":%u,", s->status.special_effect);
  p += sprintf(p, "\"wb_mode\":%u,", s->status.wb_mode);
  p += sprintf(p, "\"awb\":%u,", s->status.awb);
  p += sprintf(p, "\"awb_gain\":%u,", s->status.awb_gain);
  p += sprintf(p, "\"aec\":%u,", s->status.aec);
  p += sprintf(p, "\"aec2\":%u,", s->status.aec2);
  p += sprintf(p, "\"ae_level\":%d,", s->status.ae_level);
  p += sprintf(p, "\"aec_value\":%u,", s->status.aec_value);
  p += sprintf(p, "\"agc\":%u,", s->status.agc);
  p += sprintf(p, "\"agc_gain\":%u,", s->status.agc_gain);
  p += sprintf(p, "\"gainceiling\":%u,", s->status.gainceiling);
  p += sprintf(p, "\"bpc\":%u,", s->status.bpc);
  p += sprintf(p, "\"wpc\":%u,", s->status.wpc);
  p += sprintf(p, "\"raw_gma\":%u,", s->status.raw_gma);
  p += sprintf(p, "\"lenc\":%u,", s->status.lenc);
  p += sprintf(p, "\"hmirror\":%u,", s->status.hmirror);
  p += sprintf(p, "\"vflip\":%u,", s->status.vflip);
  p += sprintf(p, "\"dcw\":%u,", s->status.dcw);
  p += sprintf(p, "\"colorbar\":%u", s->status.colorbar);
#if defined(LED_GPIO_NUM)
  p += sprintf(p, ",\"led_intensity\":%u", led_duty);
#else
  p += sprintf(p, ",\"led_intensity\":%d", -1);
#endif
  *p++ = '}';
  *p++ = 0;
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, json_response, strlen(json_response));
}

static esp_err_t xclk_handler(httpd_req_t *req) {
  char *buf = NULL;
  char _xclk[32];

  if (parse_get(req, &buf) != ESP_OK) {
    return ESP_FAIL;
  }
  if (httpd_query_key_value(buf, "xclk", _xclk, sizeof(_xclk)) != ESP_OK) {
    free(buf);
    httpd_resp_send_404(req);
    return ESP_FAIL;
  }
  free(buf);

  int xclk = atoi(_xclk);
  log_i("Set XCLK: %d MHz", xclk);

  sensor_t *s = esp_camera_sensor_get();
  int res = s->set_xclk(s, LEDC_TIMER_0, xclk);
  if (res) {
    return httpd_resp_send_500(req);
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

static esp_err_t reg_handler(httpd_req_t *req) {
  char *buf = NULL;
  char _reg[32];
  char _mask[32];
  char _val[32];

  if (parse_get(req, &buf) != ESP_OK) {
    return ESP_FAIL;
  }
  if (httpd_query_key_value(buf, "reg", _reg, sizeof(_reg)) != ESP_OK || httpd_query_key_value(buf, "mask", _mask, sizeof(_mask)) != ESP_OK
      || httpd_query_key_value(buf, "val", _val, sizeof(_val)) != ESP_OK) {
    free(buf);
    httpd_resp_send_404(req);
    return ESP_FAIL;
  }
  free(buf);

  int reg = atoi(_reg);
  int mask = atoi(_mask);
  int val = atoi(_val);
  log_i("Set Register: reg: 0x%02x, mask: 0x%02x, value: 0x%02x", reg, mask, val);

  sensor_t *s = esp_camera_sensor_get();
  int res = s->set_reg(s, reg, mask, val);
  if (res) {
    return httpd_resp_send_500(req);
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

static esp_err_t greg_handler(httpd_req_t *req) {
  char *buf = NULL;
  char _reg[32];
  char _mask[32];

  if (parse_get(req, &buf) != ESP_OK) {
    return ESP_FAIL;
  }
  if (httpd_query_key_value(buf, "reg", _reg, sizeof(_reg)) != ESP_OK || httpd_query_key_value(buf, "mask", _mask, sizeof(_mask)) != ESP_OK) {
    free(buf);
    httpd_resp_send_404(req);
    return ESP_FAIL;
  }
  free(buf);

  int reg = atoi(_reg);
  int mask = atoi(_mask);
  sensor_t *s = esp_camera_sensor_get();
  int res = s->get_reg(s, reg, mask);
  if (res < 0) {
    return httpd_resp_send_500(req);
  }
  log_i("Get Register: reg: 0x%02x, mask: 0x%02x, value: 0x%02x", reg, mask, res);

  char buffer[20];
  const char *val = itoa(res, buffer, 10);
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, val, strlen(val));
}

static int parse_get_var(char *buf, const char *key, int def) {
  char _int[16];
  if (httpd_query_key_value(buf, key, _int, sizeof(_int)) != ESP_OK) {
    return def;
  }
  return atoi(_int);
}

static esp_err_t pll_handler(httpd_req_t *req) {
  char *buf = NULL;

  if (parse_get(req, &buf) != ESP_OK) {
    return ESP_FAIL;
  }

  int bypass = parse_get_var(buf, "bypass", 0);
  int mul = parse_get_var(buf, "mul", 0);
  int sys = parse_get_var(buf, "sys", 0);
  int root = parse_get_var(buf, "root", 0);
  int pre = parse_get_var(buf, "pre", 0);
  int seld5 = parse_get_var(buf, "seld5", 0);
  int pclken = parse_get_var(buf, "pclken", 0);
  int pclk = parse_get_var(buf, "pclk", 0);
  free(buf);

  log_i("Set Pll: bypass: %d, mul: %d, sys: %d, root: %d, pre: %d, seld5: %d, pclken: %d, pclk: %d", bypass, mul, sys, root, pre, seld5, pclken, pclk);
  sensor_t *s = esp_camera_sensor_get();
  int res = s->set_pll(s, bypass, mul, sys, root, pre, seld5, pclken, pclk);
  if (res) {
    return httpd_resp_send_500(req);
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

static esp_err_t win_handler(httpd_req_t *req) {
  char *buf = NULL;

  if (parse_get(req, &buf) != ESP_OK) {
    return ESP_FAIL;
  }

  int startX = parse_get_var(buf, "sx", 0);
  int startY = parse_get_var(buf, "sy", 0);
  int endX = parse_get_var(buf, "ex", 0);
  int endY = parse_get_var(buf, "ey", 0);
  int offsetX = parse_get_var(buf, "offx", 0);
  int offsetY = parse_get_var(buf, "offy", 0);
  int totalX = parse_get_var(buf, "tx", 0);
  int totalY = parse_get_var(buf, "ty", 0);  // codespell:ignore totaly
  int outputX = parse_get_var(buf, "ox", 0);
  int outputY = parse_get_var(buf, "oy", 0);
  bool scale = parse_get_var(buf, "scale", 0) == 1;
  bool binning = parse_get_var(buf, "binning", 0) == 1;
  free(buf);

  log_i(
    "Set Window: Start: %d %d, End: %d %d, Offset: %d %d, Total: %d %d, Output: %d %d, Scale: %u, Binning: %u", startX, startY, endX, endY, offsetX, offsetY,
    totalX, totalY, outputX, outputY, scale, binning  // codespell:ignore totaly
  );
  sensor_t *s = esp_camera_sensor_get();
  int res = s->set_res_raw(s, startX, startY, endX, endY, offsetX, offsetY, totalX, totalY, outputX, outputY, scale, binning);  // codespell:ignore totaly
  if (res) {
    return httpd_resp_send_500(req);
  }

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  return httpd_resp_send(req, NULL, 0);
}

static esp_err_t camera_ui_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
  sensor_t *s = esp_camera_sensor_get();
  if (s != NULL) {
    if (s->id.PID == OV3660_PID) {
      return httpd_resp_send(req, (const char *)index_ov3660_html_gz, index_ov3660_html_gz_len);
    } else if (s->id.PID == OV5640_PID) {
      return httpd_resp_send(req, (const char *)index_ov5640_html_gz, index_ov5640_html_gz_len);
    } else {
      return httpd_resp_send(req, (const char *)index_ov2640_html_gz, index_ov2640_html_gz_len);
    }
  } else {
    log_e("Camera sensor not found");
    return httpd_resp_send_500(req);
  }
}


static const char REC_HOME[] PROGMEM = R"HTML(
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FRB Sea Camera</title><style>
body{font-family:Arial,sans-serif;margin:0;background:#111;color:#eee}header{padding:10px;background:#1b1b1b;display:flex;gap:8px;align-items:center;flex-wrap:wrap}button,input,select{font-size:16px;border-radius:7px;padding:9px}button{border:0;font-weight:bold}.rec{background:#d22;color:#fff}.stop{background:#555;color:#fff}.blue{background:#2878c8;color:#fff}input{width:86px;border:1px solid #555;background:#222;color:#fff}.wrap{display:grid;grid-template-columns:minmax(320px,1fr) 420px;min-height:calc(100vh - 65px)}iframe{width:100%;height:78vh;border:0;background:white}.files{padding:14px;overflow:auto}.file{padding:12px 0;border-bottom:1px solid #333}.filemeta{font-size:12px;color:#bbb;margin:5px 0 8px}.file button{padding:7px 12px}.file button:disabled{opacity:.55;cursor:not-allowed}.hint{font-size:12px;color:#aaa}.playerbox{display:none;margin-top:12px;padding:10px;background:#000;border:1px solid #444;border-radius:8px}.playerbar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:0 0 6px}.playerbar input[type=number]{width:64px}.seekbar{display:flex;align-items:center;gap:8px;margin:0 0 8px}.seekbar span{font-size:12px;white-space:nowrap}.seekbar input[type=range]{width:100%;max-width:none;padding:0;margin:0;height:24px}.battery{font-weight:bold;padding:4px 8px;border-radius:6px;background:#222}.bat-good{color:#8ef58e}.bat-low{color:#ffd36a}.bat-critical{color:#ff6b6b}.err{color:#ff7070;font-size:12px;word-break:break-all;white-space:pre-wrap;min-height:2.6em;line-height:1.3;padding-top:4px}@media(max-width:850px){.wrap{display:block}iframe{height:55vh}.files{min-height:45vh}}
.nowplaying{font-size:14px;font-weight:bold;color:#8bc9ff;padding:4px 0 9px;overflow-wrap:anywhere}.playerbox{grid-column:1;grid-row:1;min-width:0;margin:0;height:78vh;box-sizing:border-box;display:none;flex-direction:column}.playerbox .playerbar,.playerbox .seekbar,.playerbox .err{flex-shrink:0}.framewrap{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;background:#000;overflow:hidden}.playerbox img{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;background:#000}#cameraFrame{grid-column:1;grid-row:1}.files{grid-column:2;grid-row:1}@media(max-width:850px){.playerbox{height:75vh}}
</style></head><body><header><b>FRB Sea Camera</b><label>形式 <select id="mode"><option value="avi">AVI動画</option><option value="jpg">JPEG連番</option></select></label><label>枚数 <input id="frames" type="number" min="1" max="10000" value="10000"></label><label>間隔ms <input id="interval" type="number" min="0" max="60000" value="200"></label><button class="rec" onclick="rec()">● REC</button><button class="stop" onclick="stopRec()">■ STOP</button><button class="blue" onclick="files()">↻ Files</button><span id="status">loading...</span><span id="battery" class="battery">BAT --.--V</span><span id="clock" title="操作端末の日時"></span></header>
<div class="wrap"><div class="playerbox" id="player"><div class="nowplaying" id="nowPlaying">再生対象：なし</div><div class="playerbar"><button onclick="closePlayer()">✕ Close</button><button onclick="togglePlay()" id="playBtn">⏸ Pause</button><button onclick="stepFrame(-1)">◀</button><button onclick="stepFrame(1)">▶</button><label>fps <input id="fps" type="number" value="5" min="1" max="30"></label><span id="pos"></span></div><div class="seekbar"><span id="seekLabel">Time</span><input id="seek" type="range" min="0" max="1" value="0" step="1" onpointerdown="beginSeek()" onkeydown="beginSeek()" oninput="seekPreview(this.value)" onchange="seekCommit(this.value)" title="録画全体の時間でシーク"></div><div class="framewrap"><img id="frame" alt="recorded frame"></div><div id="playError" class="err"></div></div>
<iframe id="cameraFrame" src="/camera"></iframe><section class="files"><h3>SD recordings</h3><div class="hint">AVI動画は1つのRECにつき1本の連続動画として再生できます。内部保存は60秒ごとにAVIを確定します。タイムバーで録画全体の好きな位置へ移動できます。電源断時は最後の未確定部分を失うことがあります。</div><div id="list"></div>
</section></div>
<script>
// Playback is one virtual timeline per REC folder. The physical AVI parts stay on SD.
let playTimer=null,playSession='',playFrame=1,playMax=0,playing=false;
let lastObjectUrl=null,loadSeq=0,nextFrameDue=0,playIsVideo=false;
let playSegments=[],totalVideoMs=0,recordingsByName=Object.create(null);
let seekInProgress=false,seekWasPlaying=false,openSerial=0;
const SEEK_QUANTUM_MS=200;
function validSessionName(s){return /^REC_[0-9]+$/.test(String(s));}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function formatTime(ms){
  const s=Math.max(0,Math.floor((Number(ms)||0)/1000));
  return [Math.floor(s/3600),Math.floor(s/60)%60,s%60].map(v=>String(v).padStart(2,'0')).join(':');
}
function normalizeSegments(raw){
  let startFrame=1,startMs=0;
  return (Array.isArray(raw)?raw:[])
    .filter(s=>Number.isInteger(Number(s.part)) && Number(s.part)>=0 && Number(s.frames)>0)
    .sort((a,b)=>Number(a.part)-Number(b.part))
    .map(s=>{
      const frames=Math.floor(Number(s.frames));
      const fps=Number(s.recordedFps)>0?Number(s.recordedFps):5;
      const measured=Number(s.durationMs);
      // Usually durationMs=(frames-1)/fps. Use the verified AVI's metadata.
      const durationMs=Number.isFinite(measured)&&measured>0?measured:
                       Math.max(1,Math.round((frames-1)*1000/fps));
      const out={part:Number(s.part),frames,fps,durationMs,startFrame,startMs};
      startFrame+=frames;startMs+=durationMs;
      return out;
    });
}
function segmentAtFrame(frame){
  const f=Math.max(1,Math.min(playMax,Math.floor(Number(frame)||1)));
  let lo=0,hi=playSegments.length-1;
  while(lo<=hi){
    const i=(lo+hi)>>1,s=playSegments[i];
    if(f<s.startFrame)hi=i-1;
    else if(f>=s.startFrame+s.frames)lo=i+1;
    else return {segment:s,n:f-s.startFrame+1};
  }
  return null;
}
function timeAtFrame(frame){
  if(!playIsVideo)return 0;
  const info=segmentAtFrame(frame);
  if(!info)return 0;
  const s=info.segment;
  return s.startMs+(s.frames>1?(info.n-1)*s.durationMs/(s.frames-1):0);
}
function frameAtTime(ms){
  if(!playIsVideo||!playSegments.length)return 1;
  let t=Math.max(0,Math.min(totalVideoMs,Number(ms)||0));
  let lo=0,hi=playSegments.length-1;
  while(lo<=hi){
    const i=(lo+hi)>>1,s=playSegments[i];
    if(t<s.startMs)hi=i-1;
    else if(i<playSegments.length-1 && t>=s.startMs+s.durationMs)lo=i+1;
    else {
      let rel=Math.max(0,Math.min(1,(t-s.startMs)/s.durationMs));
      return s.startFrame+Math.round(rel*(s.frames-1));
    }
  }
  return playMax;
}
async function call(u){let r=await fetch(u,{cache:'no-store'});let t=await r.text();if(!r.ok)throw Error(`HTTP ${r.status}: ${t}`);return t}
let wasRecording=false;
function localIsoTime(){const d=new Date(),pad=n=>String(n).padStart(2,'0');const offset=-d.getTimezoneOffset(),sign=offset>=0?'+':'-';return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}${sign}${pad(Math.floor(Math.abs(offset)/60))}:${pad(Math.abs(offset)%60)}`;}
function updateClock(){document.getElementById('clock').textContent='日時 '+localIsoTime().replace('T',' ').substring(0,19)+' (端末)';}
updateClock();setInterval(updateClock,1000);
function pauseCameraUI(){const f=document.getElementById('cameraFrame');if(f&&f.src!=='about:blank'){f.src='about:blank';}}
function resumeCameraUI(){const f=document.getElementById('cameraFrame');if(f){f.src='/camera?t='+Date.now();}}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
async function rec(){
  let f=+document.getElementById('frames').value||10000,i=+document.getElementById('interval').value||0,mode=document.getElementById('mode').value;
  try{
    // Closing the iframe first closes the port-81 MJPEG connection.
    // Give the ESP HTTP stream task time to return its current frame buffer.
    pauseCameraUI();
    document.getElementById('status').textContent='PREPARING REC...';
    await sleep(800);
    await call(`/record/start?frames=${f}&interval=${i}&mode=${mode}&startedAt=${localIsoTime().slice(0,19)}`);
    wasRecording=true;
    await status();
  }catch(e){resumeCameraUI();alert(e.message)}
}
async function stopRec(){try{await call('/record/stop');document.getElementById('status').textContent='STOPPING...'}catch(e){alert(e.message)}}
async function status(){
  try{
    let s=JSON.parse(await call('/record/status'));
    let recTag=s.autoResumed?` ↻AUTO-RESUME${s.recoveryFault?(' ('+s.recoveryFault+')'):''}`:'';
    let resetTag=(!s.recording&&s.resetReason)?` RESET:${s.resetReason}`:'';
    let faultTag=s.lastFault?` ${s.lastFault}`:(s.recoveryFault?` LAST RESTART:${s.recoveryFault}`:'');
    let pendingTag=(!s.recording&&(s.resumePending||s.aviRecoveryPending))?' RESUME PENDING':'';
    let aviErrorTag=(!s.recording&&s.videoError)?` AVI ERROR:${s.videoError}`:'';
    document.getElementById('status').textContent=s.recording?`REC [${(s.mode||"jpg").toUpperCase()}] ${s.frames}/${s.target} ${s.seconds}s ${s.session}${s.mode==='avi'?` / AVI ${s.aviPart||'-'} ${s.aviPartSeconds||0}/60s (${s.aviFinalized||0}確定)`:''}${recTag}`:(s.sdReady?`READY${pendingTag}${resetTag}${faultTag}${aviErrorTag}`:`SD ERROR${pendingTag}${resetTag}${faultTag}${aviErrorTag}`);
    const bat=document.getElementById('battery');
    if(Number.isFinite(s.batteryV)){
      bat.textContent=`BAT ${s.batteryV.toFixed(2)}V ${s.batteryLevel||''}`;
      bat.className='battery '+(s.batteryLevel==='CRITICAL'?'bat-critical':(s.batteryLevel==='LOW'?'bat-low':'bat-good'));
    }else{
      bat.textContent='BAT --.--V'; bat.className='battery';
    }
    if(s.recording){wasRecording=true;pauseCameraUI();}
    else if(wasRecording){wasRecording=false;await files();setTimeout(resumeCameraUI,500);}
  }catch(e){document.getElementById('status').textContent='ERROR: '+e.message}
}
async function files(){
  const el=document.getElementById('list');
  el.textContent='Loading recordings...';
  try{
    const a=JSON.parse(await call('/record/files'));
    a.sort((x,y)=>Number(y.name.slice(4))-Number(x.name.slice(4)));
    recordingsByName=Object.create(null);
    el.innerHTML=a.length?a.filter(x=>validSessionName(x.name)).map(x=>{
      const name=x.name;
      recordingsByName[name]=x;
      const segs=normalizeSegments(x.segments);
      const videoFrames=segs.reduce((sum,s)=>sum+s.frames,0);
      const videoMs=segs.reduce((sum,s)=>sum+s.durationMs,0);
      const frames=x.video?videoFrames:Number(x.frames)||0;
      const duration=x.video?videoMs:Number(x.durationMs)||0;
      const statusLabel=x.incomplete?'録画中':'録画済み';
      const btn=x.video?
        (videoFrames>0 && !x.incomplete?
          `<button class="blue" onclick="openVideoSession('${name}')">▶ PLAY（全編）</button>`:
          `<span class="hint">${x.incomplete?'録画中です。STOP後に全編再生できます。':'再生可能な確定済みAVIがありません。'}</span>`):
        `<button class="blue" onclick="openPlayer('${name}',${frames},${Number(x.recordedFps)||0})" ${frames?'':'disabled'}>▶ PLAY</button>`;
      const when=x.startedAt?` / 撮影開始 ${escapeHtml(x.startedAt.replace('T',' '))}`:'';
      return `<div class="file"><b>${name}</b>　${x.video?'AVI連続動画':'JPEG連番'}　${statusLabel}`+
        `<div class="filemeta">${formatTime(duration)} / ${frames.toLocaleString()} frames${when}</div>`+
        `${btn} <button class="stop" onclick="deleteRec('${name}')">🗑 DELETE</button></div>`;
    }).join(''):'No recordings';
  }catch(e){el.textContent='Files ERROR: '+e.message;el.className='err';}
}
async function deleteRec(name){
  if(!validSessionName(name))return;
  if(!confirm(`${name} をSDカードから完全に削除しますか？`))return;
  if(playSession===name)closePlayer();
  try{
    await call(`/record/delete?session=${encodeURIComponent(name)}`);
    await files();
    document.getElementById('status').textContent=`DELETED ${name}`;
  }catch(e){alert('DELETE ERROR: '+e.message)}
}
// One REC session == one user-visible movie. Map a global frame to its AVI part.
function frameUrl(){
  if(playIsVideo){
    const info=segmentAtFrame(playFrame);
    if(!info)throw Error('No finalized AVI frame at this position');
    return `/record/video-frame?session=${encodeURIComponent(playSession)}&part=${info.segment.part}&n=${info.n}&t=${Date.now()}`;
  }
  return `/record/frame?session=${encodeURIComponent(playSession)}&n=${playFrame}&t=${Date.now()}`;
}
function syncSeek(updateSlider=true){
  const seek=document.getElementById('seek');
  if(playIsVideo){
    const t=timeAtFrame(playFrame);
    seek.min=0;
    seek.max=Math.max(1,Math.ceil(totalVideoMs/SEEK_QUANTUM_MS));
    if(updateSlider)seek.value=Math.round(t/SEEK_QUANTUM_MS);
    document.getElementById('seekLabel').textContent='Time';
    document.getElementById('pos').textContent=`${formatTime(t)} / ${formatTime(totalVideoMs)}`;
  }else{
    seek.min=1;seek.max=Math.max(1,playMax);
    if(updateSlider)seek.value=Math.max(1,Math.min(playMax||1,playFrame));
    document.getElementById('seekLabel').textContent='Frame';
    document.getElementById('pos').textContent=`${playFrame} / ${playMax}`;
  }
}
function beginSeek(){
  if(!seekInProgress){seekWasPlaying=playing;seekInProgress=true;}
}
function seekPreview(v){
  beginSeek();
  playing=false;nextFrameDue=0;clearTimeout(playTimer);updatePlayButton();
  playFrame=playIsVideo?frameAtTime(Number(v)*SEEK_QUANTUM_MS):
            Math.max(1,Math.min(playMax,Number(v)||1));
  syncSeek(false);
}
async function seekCommit(v){
  if(!seekInProgress)beginSeek();
  const resume=seekWasPlaying;
  seekInProgress=false;seekWasPlaying=false;
  playing=false;clearTimeout(playTimer);
  playFrame=playIsVideo?frameAtTime(Number(v)*SEEK_QUANTUM_MS):
            Math.max(1,Math.min(playMax,Number(v)||1));
  syncSeek();updatePlayButton();
  const serial=openSerial;
  const ok=await showFrame();
  if(ok&&resume&&serial===openSerial){playing=true;nextFrameDue=0;updatePlayButton();schedule();}
}
async function showFrame(){
  const seq=++loadSeq,err=document.getElementById('playError');
  let url;
  try{url=frameUrl();}catch(e){err.textContent='PLAY ERROR: '+e.message;playing=false;updatePlayButton();return false;}
  syncSeek();err.textContent='Loading frame...';
  try{
    const r=await fetch(url,{cache:'no-store'});
    if(!r.ok)throw Error(`HTTP ${r.status}: frame could not be loaded`);
    const blob=await r.blob();
    if(seq!==loadSeq)return false;
    if(!blob.size)throw Error('Empty JPEG frame');
    const obj=URL.createObjectURL(blob),img=document.getElementById('frame');
    return await new Promise(resolve=>{
      img.onload=()=>{
        if(seq!==loadSeq){URL.revokeObjectURL(obj);resolve(false);return;}
        if(lastObjectUrl)URL.revokeObjectURL(lastObjectUrl);
        lastObjectUrl=obj;err.textContent='';resolve(true);
      };
      img.onerror=()=>{
        URL.revokeObjectURL(obj);
        if(seq===loadSeq){err.textContent='JPEG decode error';playing=false;updatePlayButton();}
        resolve(false);
      };
      img.src=obj;
    });
  }catch(e){
    if(seq===loadSeq){err.textContent='PLAY ERROR: '+e.message;playing=false;updatePlayButton();}
    return false;
  }
}
function schedule(){
  clearTimeout(playTimer);if(!playing)return;
  const fps=Math.max(0.1,Math.min(60,Number(document.getElementById('fps').value)||5));
  const period=1000/fps;
  if(!nextFrameDue)nextFrameDue=performance.now()+period;
  const wait=Math.max(0,nextFrameDue-performance.now());
  playTimer=setTimeout(async()=>{
    if(!playing)return;
    if(playFrame>=playMax){playing=false;updatePlayButton();return;}
    playFrame++;
    nextFrameDue+=period;
    const ok=await showFrame();
    if(playing&&ok){
      if(nextFrameDue<performance.now()-period)nextFrameDue=performance.now()+period;
      schedule();
    }
  },wait);
}
function updatePlayButton(){document.getElementById('playBtn').textContent=playing?'⏸ Pause':'▶ Play';}
async function openVideoSession(s){
  const x=recordingsByName[s];
  if(!x||!x.video||x.incomplete){alert('録画終了後に再生してください');return;}
  const segs=normalizeSegments(x.segments);
  if(!segs.length){alert('再生可能なAVIがありません');return;}
  const n=segs.reduce((a,v)=>a+v.frames,0);
  const ms=segs.reduce((a,v)=>a+v.durationMs,0);
  const fps=n>1&&ms>0?(n-1)*1000/ms:Number(x.recordedFps)||5;
  return startPlayback(s,n,fps,true,segs);
}
async function openPlayer(s,n,recordedFps){return startPlayback(s,n,recordedFps,false,[]);}
async function startPlayback(s,n,recordedFps,isVideo,segs){
  if(!validSessionName(s))return;
  const serial=++openSerial;
  ++loadSeq;clearTimeout(playTimer);playing=false;seekInProgress=false;
  playIsVideo=isVideo;
  playSegments=segs;playSession=s;playMax=Math.max(0,Number(n)||0);
  totalVideoMs=isVideo?segs.reduce((a,v)=>a+v.durationMs,0):0;
  playFrame=1;nextFrameDue=0;
  document.getElementById('nowPlaying').textContent='再生中：'+s+(isVideo?'（全編連続再生）':'（JPEG連番）');
  document.getElementById('fps').value=(Math.round((Number(recordedFps)||5)*100)/100).toFixed(2);
  pauseCameraUI();
  document.getElementById('cameraFrame').style.display='none';
  document.getElementById('player').style.display='flex';
  document.getElementById('frame').style.display='block';
  syncSeek();updatePlayButton();
  if(!playMax)return;
  const ok=await showFrame();
  if(ok&&serial===openSerial){playing=true;nextFrameDue=0;updatePlayButton();schedule();}
  document.getElementById('player').scrollIntoView({behavior:'smooth',block:'nearest'});
}
async function togglePlay(){
  if(!playMax)return;
  if(playing){playing=false;clearTimeout(playTimer);nextFrameDue=0;updatePlayButton();return;}
  if(playFrame>=playMax)playFrame=1;
  const serial=openSerial;
  const ok=await showFrame();
  if(ok&&serial===openSerial){playing=true;nextFrameDue=0;updatePlayButton();schedule();}
}
function stepFrame(d){
  playing=false;nextFrameDue=0;clearTimeout(playTimer);updatePlayButton();
  playFrame=Math.max(1,Math.min(playMax,playFrame+d));showFrame();
}
function closePlayer(){
  ++openSerial;++loadSeq;playing=false;nextFrameDue=0;
  seekInProgress=false;clearTimeout(playTimer);
  playIsVideo=false;playSegments=[];totalVideoMs=0;
  document.getElementById('nowPlaying').textContent='再生対象：なし';
  document.getElementById('player').style.display='none';
  document.getElementById('cameraFrame').style.display='block';
  if(!wasRecording)resumeCameraUI();
  document.getElementById('frame').removeAttribute('src');
  if(lastObjectUrl){URL.revokeObjectURL(lastObjectUrl);lastObjectUrl=null;}
}
setInterval(status,1000);status();
</script></body></html>)HTML";
static esp_err_t home_handler(httpd_req_t *req){httpd_resp_set_type(req,"text/html; charset=utf-8");return httpd_resp_send(req,REC_HOME,HTTPD_RESP_USE_STRLEN);}
static esp_err_t rec_start_handler(httpd_req_t *req){
  uint32_t frames=10000,interval=200; char q[192]={0},v[48]={0},date[48]={0},mode[12]={0}; size_t n=httpd_req_get_url_query_len(req)+1;
  if(n>1&&n<=sizeof(q)&&httpd_req_get_url_query_str(req,q,n)==ESP_OK){if(httpd_query_key_value(q,"frames",v,sizeof(v))==ESP_OK)frames=strtoul(v,nullptr,10);if(httpd_query_key_value(q,"interval",v,sizeof(v))==ESP_OK)interval=strtoul(v,nullptr,10);if(httpd_query_key_value(q,"startedAt",date,sizeof(date))!=ESP_OK)date[0]=0;httpd_query_key_value(q,"mode",mode,sizeof(mode));}
  if(!recorderStart(frames,interval,String(date),strcmp(mode,"avi")==0)){
    httpd_resp_set_status(req,"409 Conflict");
    String msg="REC start failed: "+recorderLastStartError();
    return httpd_resp_sendstr(req,msg.c_str());
  }return httpd_resp_sendstr(req,"OK");
}
static esp_err_t rec_stop_handler(httpd_req_t *req){if(!recorderStop()){httpd_resp_set_status(req,"409 Conflict");return httpd_resp_sendstr(req,"Not recording");}return httpd_resp_sendstr(req,"OK");}
static esp_err_t rec_status_handler(httpd_req_t *req){
  String j=recorderStatusJson();
  uint32_t adcMv=batteryAdcMilliVolts();
  float batV=batteryVoltageFromAdcMilliVolts(adcMv);
  if(j.endsWith("}")) j.remove(j.length()-1);
  j += ",\"batteryV\":" + String(batV,3);
  j += ",\"batteryAdcMv\":" + String(adcMv);
  j += ",\"batteryLevel\":\"" + String(batteryLevelText(batV)) + "\"}";
  httpd_resp_set_type(req,"application/json");
  httpd_resp_set_hdr(req,"Cache-Control","no-store");
  return httpd_resp_send(req,j.c_str(),j.length());
}
static esp_err_t rec_files_handler(httpd_req_t *req){String j=recorderFilesJson();httpd_resp_set_type(req,"application/json");return httpd_resp_send(req,j.c_str(),j.length());}
static esp_err_t rec_delete_handler(httpd_req_t *req){
  char q[96]={0}, session[48]={0};
  size_t qn=httpd_req_get_url_query_len(req)+1;
  if(qn<=1 || qn>sizeof(q) || httpd_req_get_url_query_str(req,q,qn)!=ESP_OK ||
     httpd_query_key_value(q,"session",session,sizeof(session))!=ESP_OK){
    httpd_resp_set_status(req,"400 Bad Request");
    return httpd_resp_sendstr(req,"Missing session");
  }
  if(!recorderDeleteSession(String(session))){
    httpd_resp_set_status(req,"409 Conflict");
    return httpd_resp_sendstr(req,"Delete failed (recording, invalid session, or SD error)");
  }
  return httpd_resp_sendstr(req,"OK");
}

static esp_err_t rec_video_handler(httpd_req_t *req){
  char q[128]={0},session[48]={0},pv[20]={0};size_t qn=httpd_req_get_url_query_len(req)+1;
  if(qn<=1||qn>sizeof(q)||httpd_req_get_url_query_str(req,q,qn)!=ESP_OK||httpd_query_key_value(q,"session",session,sizeof(session))!=ESP_OK)return httpd_resp_send_404(req);
  uint32_t part=0;
  if(httpd_query_key_value(q,"part",pv,sizeof(pv))==ESP_OK)part=strtoul(pv,nullptr,10);
  if(!recorderVideoExists(String(session),part))return httpd_resp_send_404(req);
  String path=recorderVideoPath(String(session),part);File f=SD_MMC.open(path.c_str(),FILE_READ);
  if(!f)return httpd_resp_send_404(req);
  httpd_resp_set_type(req,"video/x-msvideo");
  String videoName=path.substring(path.lastIndexOf('/')+1);
  String filename=String("attachment; filename=\"")+String(session)+"_"+videoName+"\"";
  httpd_resp_set_hdr(req,"Content-Disposition",filename.c_str());
  httpd_resp_set_hdr(req,"Cache-Control","no-store");
  uint8_t buf[1024];esp_err_t result=ESP_OK;
  while(f.available()){
    size_t n=f.read(buf,sizeof(buf));if(!n)break;
    if(httpd_resp_send_chunk(req,(const char*)buf,n)!=ESP_OK){result=ESP_FAIL;break;}
  }
  f.close();if(result==ESP_OK)result=httpd_resp_send_chunk(req,nullptr,0);
  return result;
}
// Allow browser playback of MJPEG AVI *without* browser AVI codec support.
// The writer emits a fixed 224-byte AVI header, followed by movi frames and idx1.
// idx1 makes this O(1) per requested frame even for long recordings.
static uint32_t aviLe32(const uint8_t *p){
  return uint32_t(p[0]) | (uint32_t(p[1])<<8) | (uint32_t(p[2])<<16) | (uint32_t(p[3])<<24);
}
static bool aviReadAt(File &f, uint32_t pos, uint8_t *dst, size_t n){
  return f.seek(pos) && f.read(dst,n)==n;
}
static esp_err_t rec_video_frame_handler(httpd_req_t *req){
  char q[192]={0},session[48]={0},nv[20]={0},pv[20]={0};
  size_t qn=httpd_req_get_url_query_len(req)+1;
  if(qn<=1 || qn>sizeof(q) || httpd_req_get_url_query_str(req,q,qn)!=ESP_OK ||
     httpd_query_key_value(q,"session",session,sizeof(session))!=ESP_OK ||
     httpd_query_key_value(q,"n",nv,sizeof(nv))!=ESP_OK)
     return httpd_resp_send_404(req);
  uint32_t n=strtoul(nv,nullptr,10);
  uint32_t part=0;
  if(httpd_query_key_value(q,"part",pv,sizeof(pv))==ESP_OK)part=strtoul(pv,nullptr,10);
  if(n<1 || !recorderVideoExists(String(session),part))return httpd_resp_send_404(req);
  File f=SD_MMC.open(recorderVideoPath(String(session),part).c_str(),FILE_READ);
  if(!f)return httpd_resp_send_404(req);
  // Reject incomplete files or unexpected AVI layouts rather than returning garbage JPEG.
  uint8_t hdr[12];
  bool valid= f.size()>=248 && aviReadAt(f,0,hdr,12) &&
              memcmp(hdr,"RIFF",4)==0 && memcmp(hdr+8,"AVI ",4)==0;
  if(valid){
    valid=aviReadAt(f,212,hdr,12) && memcmp(hdr,"LIST",4)==0 &&
          memcmp(hdr+8,"movi",4)==0;
  }
  uint32_t moviSize=valid?aviLe32(hdr+4):0;
  uint64_t idxPos64=uint64_t(220)+moviSize;
  if(!valid || idxPos64+8>f.size()){
    f.close();return httpd_resp_send_404(req);
  }
  uint32_t idxPos=uint32_t(idxPos64);
  valid=aviReadAt(f,idxPos,hdr,8) && memcmp(hdr,"idx1",4)==0;
  uint32_t idxSize=valid?aviLe32(hdr+4):0;
  uint64_t idxEntry=uint64_t(idxPos)+8+uint64_t(n-1)*16;
  if(!valid || idxSize%16!=0 || n>idxSize/16 || idxEntry+16>f.size()){
    f.close();return httpd_resp_send_404(req);
  }
  uint8_t ent[16];
  valid=aviReadAt(f,uint32_t(idxEntry),ent,16) && memcmp(ent,"00dc",4)==0;
  uint32_t offset=valid?aviLe32(ent+8):0;
  uint32_t size=valid?aviLe32(ent+12):0;
  uint64_t framePos64=uint64_t(220)+offset;
  if(!valid || framePos64+8+size>idxPos){
    f.close();return httpd_resp_send_404(req);
  }
  uint32_t framePos=uint32_t(framePos64);
  valid=aviReadAt(f,framePos,hdr,8) && memcmp(hdr,"00dc",4)==0 &&
        aviLe32(hdr+4)==size;
  if(!valid || !f.seek(framePos+8)){
    f.close();return httpd_resp_send_404(req);
  }
  httpd_resp_set_type(req,"image/jpeg");
  httpd_resp_set_hdr(req,"Cache-Control","no-store");
  uint8_t buf[1024];esp_err_t result=ESP_OK;
  for(uint32_t remaining=size;remaining>0;){
    size_t take=remaining>sizeof(buf)?sizeof(buf):remaining;
    size_t got=f.read(buf,take);
    if(got!=take || httpd_resp_send_chunk(req,(const char*)buf,got)!=ESP_OK){
      result=ESP_FAIL;break;
    }
    remaining-=got;
  }
  f.close();
  if(result==ESP_OK)result=httpd_resp_send_chunk(req,nullptr,0);
  return result;
}
static esp_err_t rec_frame_handler(httpd_req_t *req){
  char q[192]={0},session[48]={0},nv[20]={0},pv[20]={0};size_t qn=httpd_req_get_url_query_len(req)+1;if(qn<=1||qn>sizeof(q)||httpd_req_get_url_query_str(req,q,qn)!=ESP_OK)return httpd_resp_send_404(req);
  if(httpd_query_key_value(q,"session",session,sizeof(session))!=ESP_OK||httpd_query_key_value(q,"n",nv,sizeof(nv))!=ESP_OK)return httpd_resp_send_404(req);uint32_t no=strtoul(nv,nullptr,10);if(!recorderFrameExists(String(session),no))return httpd_resp_send_404(req);
  String path = recorderFramePath(String(session), no);
  File f = SD_MMC.open(path.c_str(), FILE_READ);
  if (!f) {
    Serial.printf("PLAY: open failed: %s\n", path.c_str());
    return httpd_resp_send_500(req);
  }

  const size_t fileSize = f.size();
  Serial.printf("PLAY: send %s (%u bytes)\n", path.c_str(), (unsigned)fileSize);
  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store, no-cache, must-revalidate");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  // Keep this buffer deliberately small. The ESP-IDF HTTP server handler runs
  // on its own task stack; the previous 4096-byte local buffer could consume
  // almost the whole default HTTPD stack and corrupt/fail the response.
  uint8_t buf[1024];
  size_t total = 0;
  while (f.available()) {
    size_t r = f.read(buf, sizeof(buf));
    if (r == 0) break;
    if (httpd_resp_send_chunk(req, (const char *)buf, r) != ESP_OK) {
      Serial.printf("PLAY: send failed after %u/%u bytes\n", (unsigned)total, (unsigned)fileSize);
      f.close();
      return ESP_FAIL;
    }
    total += r;
  }
  f.close();
  esp_err_t endResult = httpd_resp_send_chunk(req, NULL, 0);
  Serial.printf("PLAY: sent %u/%u bytes result=%d\n", (unsigned)total, (unsigned)fileSize, (int)endResult);
  return endResult;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.max_uri_handlers = 24;
  // REC/PLAY handlers do file I/O and JSON work. Give HTTPD enough stack headroom.
  config.stack_size = 8192;

  httpd_uri_t index_uri = {
    .uri = "/",
    .method = HTTP_GET,
    .handler = home_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t camera_ui_uri = { .uri = "/camera", .method = HTTP_GET, .handler = camera_ui_handler, .user_ctx = NULL };
  httpd_uri_t rec_start_uri = { .uri = "/record/start", .method = HTTP_GET, .handler = rec_start_handler, .user_ctx = NULL };
  httpd_uri_t rec_stop_uri = { .uri = "/record/stop", .method = HTTP_GET, .handler = rec_stop_handler, .user_ctx = NULL };
  httpd_uri_t rec_status_uri = { .uri = "/record/status", .method = HTTP_GET, .handler = rec_status_handler, .user_ctx = NULL };
  httpd_uri_t rec_files_uri = { .uri = "/record/files", .method = HTTP_GET, .handler = rec_files_handler, .user_ctx = NULL };
  httpd_uri_t rec_video_uri = { .uri = "/record/video", .method = HTTP_GET, .handler = rec_video_handler, .user_ctx = NULL };
  httpd_uri_t rec_frame_uri = { .uri = "/record/frame", .method = HTTP_GET, .handler = rec_frame_handler, .user_ctx = NULL };
  httpd_uri_t rec_video_frame_uri = { .uri = "/record/video-frame", .method = HTTP_GET, .handler = rec_video_frame_handler, .user_ctx = NULL };
  httpd_uri_t rec_delete_uri = { .uri = "/record/delete", .method = HTTP_GET, .handler = rec_delete_handler, .user_ctx = NULL };

  httpd_uri_t status_uri = {
    .uri = "/status",
    .method = HTTP_GET,
    .handler = status_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t cmd_uri = {
    .uri = "/control",
    .method = HTTP_GET,
    .handler = cmd_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t capture_uri = {
    .uri = "/capture",
    .method = HTTP_GET,
    .handler = capture_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t stream_uri = {
    .uri = "/stream",
    .method = HTTP_GET,
    .handler = stream_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t bmp_uri = {
    .uri = "/bmp",
    .method = HTTP_GET,
    .handler = bmp_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t xclk_uri = {
    .uri = "/xclk",
    .method = HTTP_GET,
    .handler = xclk_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t reg_uri = {
    .uri = "/reg",
    .method = HTTP_GET,
    .handler = reg_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t greg_uri = {
    .uri = "/greg",
    .method = HTTP_GET,
    .handler = greg_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t pll_uri = {
    .uri = "/pll",
    .method = HTTP_GET,
    .handler = pll_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  httpd_uri_t win_uri = {
    .uri = "/resolution",
    .method = HTTP_GET,
    .handler = win_handler,
    .user_ctx = NULL
#ifdef CONFIG_HTTPD_WS_SUPPORT
    ,
    .is_websocket = true,
    .handle_ws_control_frames = false,
    .supported_subprotocol = NULL
#endif
  };

  ra_filter_init(&ra_filter, 20);

  log_i("Starting web server on port: '%d'", config.server_port);
  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &camera_ui_uri);
    httpd_register_uri_handler(camera_httpd, &rec_start_uri);
    httpd_register_uri_handler(camera_httpd, &rec_stop_uri);
    httpd_register_uri_handler(camera_httpd, &rec_status_uri);
    httpd_register_uri_handler(camera_httpd, &rec_files_uri);
    httpd_register_uri_handler(camera_httpd, &rec_frame_uri);
    httpd_register_uri_handler(camera_httpd, &rec_video_frame_uri);
    httpd_register_uri_handler(camera_httpd, &rec_video_uri);
    httpd_register_uri_handler(camera_httpd, &rec_delete_uri);
    httpd_register_uri_handler(camera_httpd, &cmd_uri);
    httpd_register_uri_handler(camera_httpd, &status_uri);
    httpd_register_uri_handler(camera_httpd, &capture_uri);
    httpd_register_uri_handler(camera_httpd, &bmp_uri);

    httpd_register_uri_handler(camera_httpd, &xclk_uri);
    httpd_register_uri_handler(camera_httpd, &reg_uri);
    httpd_register_uri_handler(camera_httpd, &greg_uri);
    httpd_register_uri_handler(camera_httpd, &pll_uri);
    httpd_register_uri_handler(camera_httpd, &win_uri);
  }

  config.server_port += 1;
  config.ctrl_port += 1;
  log_i("Starting stream server on port: '%d'", config.server_port);
  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

void setupLedFlash() {
#if defined(LED_GPIO_NUM)
  ledcAttach(LED_GPIO_NUM, 5000, 8);
#else
  log_i("LED flash is disabled -> LED_GPIO_NUM undefined");
#endif
}
