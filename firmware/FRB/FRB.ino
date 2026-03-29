#include <WiFi.h>
#include <Wire.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <arduinoFFT.h>
#include "esp_wifi.h"
#include <driver/i2s.h>
#include <SPIFFS.h>

// ===== Wi-Fi =====
const char* ssid = "hutsub";
const char* password = "bbbbbbbbz";

// ===== MPU-6050 I2C =====
static const uint8_t MPU_ADDR = 0x68; // AD0=GND なら 0x68（多くのGY-521はこれ）
static const int SDA_PIN = 21;
static const int SCL_PIN = 22;
static unsigned long last = 0;

// 0〜200Hzのbinだけ送る
static const uint16_t MIN_HZ = 10;

// ===== ACC FFT =====
static const uint16_t N_A = 128;
//static const double   FS_A = 500;
static const double   FS_A = 1000;
static const double   DF_A = FS_A / N_A;
//static const uint16_t MAX_HZ_A = 400;
static const uint16_t MAX_HZ_A = 500;

static const uint16_t MAX_BIN_A = (uint16_t)(MAX_HZ_A / DF_A);

double vRealA[N_A];
double vImagA[N_A];
arduinoFFT FFT_A(vRealA, vImagA, N_A, FS_A);

// ===== MIC FFT =====
static const uint16_t N_M = 256;
static const double   FS_M = 800;          // 400Hz見たい→最低800Hz（まずは800でOK）
static const double   DF_M = FS_M / N_M;
static const uint16_t MAX_HZ_M = 400;
static const uint16_t MAX_BIN_M = (uint16_t)(MAX_HZ_M / DF_M);

double vRealM[N_M];
double vImagM[N_M];
arduinoFFT FFT_M(vRealM, vImagM, N_M, FS_M);

// ===== I2S (INMP441) =====
// よくある配線例：BCLK=26, LRCL=25, DOUT=33
// もしあなたの配線が違うならここだけ変えればOK
static const int I2S_BCLK = 26;
static const int I2S_LRCL = 25;
static const int I2S_DIN  = 33;

static const i2s_port_t I2S_PORT = I2S_NUM_0;

// I2Sは高めのサンプルレートで安定動作させる（ここは 16000 推奨）
static const uint32_t MIC_I2S_FS = 16000;

// 16k → 800 に落とす（20分の1）。整数で割り切れる必要あり。
static const uint32_t MIC_DECIM = (MIC_I2S_FS / (uint32_t)FS_M); // 16000/800=20
static_assert((16000 % 800) == 0, "MIC_I2S_FS must be divisible by FS_M");

// 1フレームでI2Sから読む生サンプル数
static const uint32_t MIC_RAW_N = (uint32_t)N_M * MIC_DECIM;

// I2S受け取り用バッファ（大きいのでstatic推奨）
static int32_t micRaw[MIC_RAW_N];

// ===== Touch Sensor (digital) =====
//static const int TOUCH_PIN = 4;       // ←SIGをつないだGPIOに変更
//static const int TOUCH_ACTIVE = LOW;  // 多くのモジュールは押すとLOW。逆ならHIGHに

#define TOUCH_PIN 4

unsigned long touchStart = 0;
unsigned long lastRelease = 0;
unsigned long lastChange = 0;

int tapCount = 0;

bool touching = false;
bool longSent = false;

int rawPrev = 0;
int stableV = 0;

const int DEBOUNCE_MS = 10;
const int LONG_MS = 800;
const int MULTI_MS = 800;



//--------------------------------------------------------------

static String wsMsg;
static uint32_t lastRssiMs = 0;

static uint32_t lastSendMs = 0;
const uint32_t SEND_INTERVAL_MS = 50;  // 20Hz

// ===== Web =====
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");


// MPUレジスタ書き込み
void mpuWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission(true);
}

// MPUから加速度(AX,AY,AZ)を一括読み出し（最速）
bool mpuReadAccelRaw(int16_t &ax, int16_t &ay, int16_t &az) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); // ACCEL_XOUT_H
  if (Wire.endTransmission(false) != 0) return false;

  const uint8_t need = 6;
  uint8_t got = Wire.requestFrom((int)MPU_ADDR, (int)need, (int)true);
  if (got != need) return false;

  ax = (int16_t)((Wire.read() << 8) | Wire.read());
  ay = (int16_t)((Wire.read() << 8) | Wire.read());
  az = (int16_t)((Wire.read() << 8) | Wire.read());
  return true;
}

void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
               AwsEventType type, void *arg, uint8_t *data, size_t len) {
  // 受信は使わない（送信専用）
}

void setupMPU() {
  // Wake up
  mpuWrite(0x6B, 0x00); // PWR_MGMT_1 = 0 (sleep解除)
  delay(50);

  // DLPF設定（CONFIG 0x1A）
  // DLPF=1 : 約184Hz帯域（0-200Hzを見るならここから開始が無難）
  mpuWrite(0x1A, 0x01);

  // サンプルレート（SMPLRT_DIV 0x19）
  // DLPF有効時、内部サンプルは 1kHz。FS=500Hzにしたいので divider=1 => 1000/(1+1)=500Hz
  mpuWrite(0x19, 1);

  // 加速度レンジ（ACCEL_CONFIG 0x1C）
  // 0: ±2g, 1: ±4g, 2: ±8g, 3: ±16g
  // 振動が強いなら±4g〜±8g推奨。まずは±4g。
  mpuWrite(0x1C, (1 << 3)); // AFS_SEL=1 => ±4g
}

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pins = {};
  pins.bck_io_num = I2S_BCLK;
  pins.ws_io_num = I2S_LRCL;
  pins.data_out_num = I2S_PIN_NO_CHANGE;
  pins.data_in_num = I2S_DIN;

  i2s_driver_install(I2S_PORT, &i2s_config, 0, nullptr);
  i2s_set_pin(I2S_PORT, &pins);
  i2s_zero_dma_buffer(I2S_PORT);
}

void setup() {
  Serial.begin(115200);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setTimeOut(20);  // 20msでI2Cを諦める（ハング防止）

  Wire.setClock(400000); // I2C 400kHz（重要：取りこぼし減る）

  setupMPU();
  setupI2S();   // ★追加

  //touchセンサー
  pinMode(TOUCH_PIN, INPUT_PULLUP);  // open collector想定。必要ならINPUTに変更

  // ===== AP + STA 同時モード =====

  // ルータ接続用（STA）
  const char* sta_ssid = ssid;
  const char* sta_pass = password;

  // ESP32アクセスポイント（AP）
  const char* ap_ssid = "ESP32_FFT";
  const char* ap_pass = "12345678";

  WiFi.mode(WIFI_AP_STA);
  //WiFi.mode(WIFI_STA);
/*
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; ++i) {
    Serial.println(WiFi.SSID(i));
  }
*/
  // STA開始
  WiFi.begin(sta_ssid, sta_pass);
  WiFi.setSleep(false);   // ←重要（安定する）

  // ===== WiFi送信出力 最大化 =====
  WiFi.setTxPower(WIFI_POWER_19_5dBm);
  // 確認表示
  Serial.print("TX Power: ");
  Serial.println(WiFi.getTxPower());


  // 確認表示
  Serial.print("TX Power: ");
  Serial.println(WiFi.getTxPower());
  Serial.print("STA connecting");
  Serial.println(WiFi.status());

  unsigned long t0 = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 8000) {
    delay(300);
    Serial.print(".");
  }
  Serial.println();

  // STA結果
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("STA IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("STA connect failed");
  }

  // AP開始（常時ON）
  WiFi.softAP(ap_ssid, ap_pass);

  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  ws.onEvent(onWsEvent);
  server.addHandler(&ws);

  //index.html分離
  if(!SPIFFS.begin(true)){
    Serial.println("SPIFFS mount failed");

    return;
  }
  listSpiffsFiles();
  // data/ の中身をそのまま配信
  server.serveStatic("/", SPIFFS, "/").setDefaultFile("index.html");

  server.begin();

  wsMsg.reserve(4096);  // 余裕を持って確保（小さすぎると再確保が走る）
  Serial.println("=== setup done ===");

  WiFi.setSleep(false);

  Wire.beginTransmission(MPU_ADDR);
  uint8_t err = Wire.endTransmission(true);
  Serial.print("MPU I2C check: ");
  Serial.println(err); // 0ならOK、0以外はNG


}

// 簡易サンプル（500Hz）
// ※I2Cが間に合わない場合は、後で“取りこぼし検知/対策”を入れます
void sampleMPU(uint32_t &t0_us) {
  const uint32_t period_us = (uint32_t)(1000000.0 / FS_A);
  t0_us = micros();
  uint32_t t = t0_us;

  for (uint16_t i = 0; i < N_A; i++) {
    updateTouch(digitalRead(TOUCH_PIN), millis());

    int16_t ax, ay, az;
    bool ok = mpuReadAccelRaw(ax, ay, az);
    if (!ok) { ax = ay = az = 0; }

    vRealA[i] = (double)az;
    vImagA[i] = 0;

    t += period_us;
    while ((int32_t)(micros() - t) < 0) {}
  }
}

bool sampleMic(uint32_t &t0_us) {
  t0_us = micros();

  const size_t bytesToRead = (size_t)MIC_RAW_N * sizeof(int32_t);
  size_t bytesRead = 0;

  esp_err_t err = i2s_read(I2S_PORT, (void*)micRaw, bytesToRead, &bytesRead, portMAX_DELAY);
  if (err != ESP_OK || bytesRead != bytesToRead) {
    Serial.printf("I2S read err=%d bytesRead=%u/%u\n",
                  (int)err, (unsigned)bytesRead, (unsigned)bytesToRead);
    return false;
  }

  // 16kHzで取ったものを 20分の1に間引いて 800Hz相当にする
  // ※「平均化ダウンサンプル」にすると更に安定するけど、まずは単純間引きでOK
  for (uint16_t i = 0; i < N_M; i++) {
    updateTouch(digitalRead(TOUCH_PIN), millis());

    int32_t s32 = micRaw[(uint32_t)i * MIC_DECIM];

    // INMP441は上位24bit相当が有効なことが多いので軽く右シフト（ボードにより差あり）
    // 音が小さすぎ/大きすぎなら、このシフト量を 0〜12 くらいで調整してOK
    int32_t s = (s32 >> 14);

    vRealM[i] = (double)s;
    vImagM[i] = 0.0;
  }

  return true;
}

void sendFftCsv(char type, uint32_t t0_us, double fs, uint16_t n, uint16_t maxHz,
                double *mag, uint16_t maxBin) {

  //Serial.printf("send 010...");

  static uint32_t lastPrint = 0;
  if (millis() - lastPrint > 1000) {
    lastPrint = millis();
    //Serial.printf("send %c  clients=%u  heap=%u\n", type, ws.count(), (unsigned)ESP.getFreeHeap());
  }

  if (ws.count() == 0) return;   // クライアント居ないなら送らない

  wsMsg = "";
  wsMsg += type; wsMsg += ",";
  wsMsg += String(t0_us); wsMsg += ",";
  wsMsg += String(fs, 0); wsMsg += ",";
  wsMsg += String(n);     wsMsg += ",";
  wsMsg += String(maxHz);
  wsMsg += "|";

  for (uint16_t i = 0; i <= maxBin; i++) {
    wsMsg += String((int)mag[i]);
    if (i < maxBin) wsMsg += ",";
  }

  ws.textAll(wsMsg);
}

void sendTouchEvent(uint32_t t_us, int state){
  if (ws.count() == 0) return;

  wsMsg = "";
  wsMsg += 'T'; wsMsg += ",";
  wsMsg += String(t_us); wsMsg += ",";
  wsMsg += "0,0,0|";                 // JSが5項目期待なので合わせる
  wsMsg += String(state);            // 1 or 0

  Serial.printf("TouchEvent --- 010\n");
  ws.textAll(wsMsg);
}


void loop() {

  // ===== Touch debounce & event =====
  int v = digitalRead(TOUCH_PIN);

  unsigned long now = millis();

 
  updateTouch(v,now);
  
  //-----------------------------------------------------------------------------
  static bool sendAccelNext = true;

  if (millis() - lastSendMs < SEND_INTERVAL_MS) {
    ws.cleanupClients();
    delay(1);
    //Serial.printf("loop return 010...");

    return;
  }
  lastSendMs = millis();

  uint32_t t0_us = 0;

  if (sendAccelNext) {
    // ===== ACCEL =====
    sampleMPU(t0_us);

    FFT_A.DCRemoval();
    FFT_A.Windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT_A.Compute(FFT_FORWARD);
    FFT_A.ComplexToMagnitude();

    sendFftCsv('A', t0_us, FS_A, N_A, MAX_HZ_A, vRealA, MAX_BIN_A);

  } else {
    //Serial.print("Mic check: \n");

    // ===== MIC =====
    if (sampleMic(t0_us)) {
      FFT_M.DCRemoval();
      FFT_M.Windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
      FFT_M.Compute(FFT_FORWARD);
      FFT_M.ComplexToMagnitude();

      sendFftCsv('M', t0_us, FS_M, N_M, MAX_HZ_M, vRealM, MAX_BIN_M);
    }
  }

  sendAccelNext = !sendAccelNext;

  ws.cleanupClients();
  delay(1); // 200msは重すぎるのでまず1msへ（必要なら後で調整）
}

void sendTouch(int v, int count, bool isLong){

  unsigned long now = millis();   // ←これを追加




  String payload =
    String(v) + "," +
    String(count) + "," +
    String(isLong ? 1 : 0);

  String msg = "T,0,0,0,0|" + payload;

  //Serial.printf("TouchEvent v=%d count=%d long=%d\n", v, count, isLong ? 1 : 0);
  Serial.printf("FINALIZE taps=%d dt=%lu\n", tapCount, now - lastRelease);

  ws.textAll(msg);
}

void updateTouch(int v, unsigned long now){

  // 1) 生値変化
  if(v != rawPrev){
    Serial.printf("RAW CHANGE %d -> %d  now=%lu\n", rawPrev, v, now);
    rawPrev = v;
    lastChange = now;
  }

  // 2) stable反映
  if((now - lastChange) >= DEBOUNCE_MS && stableV != rawPrev){
    int oldStable = stableV;
    stableV = rawPrev;

    Serial.printf("STABLE CHANGE %d -> %d  now=%lu  dt=%lu\n",
                  oldStable, stableV, now, now - lastChange);

    // 押した瞬間
    if(stableV == 1){
      touching = true;
      touchStart = now;
      longSent = false;
      Serial.printf("PRESS  now=%lu  tapCount=%d\n", now, tapCount);
    }

    // 離した瞬間
    if(stableV == 0 && touching){
      touching = false;
      Serial.printf("RELEASE now=%lu  tapCount(before)=%d\n", now, tapCount);

      if(!longSent){
        tapCount++;
        lastRelease = now;
        Serial.printf("tapCount increment -> %d  lastRelease=%lu\n",
                      tapCount, lastRelease);
      }
    }
  }

  // 3) 長押し
  if(touching && !longSent){
    if(now - touchStart >= LONG_MS){
      Serial.printf("LONG  now=%lu  hold=%lu\n", now, now - touchStart);
      sendTouch(1, 1, true);
      longSent = true;
      tapCount = 0;
    }
  }

  // 4) タップ確定
  if(!touching && tapCount > 0){
    unsigned long dt = now - lastRelease;
    if(dt >= MULTI_MS){
      // sendTouch(1, tapCount, false);
      if (tapCount >= 2) {
        Serial.printf("FINALIZE DOUBLE taps=%d\n", tapCount);
        sendTouch(1, 2, false);   // 2回以上は全部ダブル扱い
      } else {
        Serial.printf("FINALIZE SINGLE taps=%d\n", tapCount);
        sendTouch(1, 1, false);   // 1回
      }
      tapCount = 0;
    }
  }
}

void listSpiffsFiles() {
  File root = SPIFFS.open("/");
  File file = root.openNextFile();

  Serial.println("=== SPIFFS files ===");
  while (file) {
    Serial.print("name: ");
    Serial.print(file.name());
    Serial.print("  size: ");
    Serial.println(file.size());
    file = root.openNextFile();
  }
  Serial.println("====================");
}

