// FRB Boat v1.2 / ESP32-WROOM / Arduino ESP32 core 3.x
// AIN1=25 AIN2=26 BIN1=27 BIN2=14 STBY=3.3V
// VM=motor battery+, GND=battery- AND ESP32 GND. ESP32 powered via USB.
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <esp_system.h>
#include "BoatControl.h"
#include "BoatPage.h"
constexpr uint8_t MOTOR_PINS[]={25,26,27,14};
// Compare against v1 (20 kHz): lower PWM frequency to diagnose 99%/100% jump.
constexpr uint32_t PWM_HZ = 1000;
WebServer server(80);
SemaphoreHandle_t lockHandle;
BoatControl control;
bool pwmReady=false;
void motor(uint8_t p,uint8_t q,int value) {
  // Both low before changing polarity.
  ledcWrite(p,0);ledcWrite(q,0);
  if(value>0) ledcWrite(p,value*255/100);
  if(value<0) ledcWrite(q,-value*255/100);
}
void motorTask(void*) {
  int previousL=999,previousR=999;
  for(;;) {
    xSemaphoreTake(lockHandle,portMAX_DELAY);
    control.tick(millis());
    int l=control.left,r=control.right;
    if(l!=previousL || r!=previousR) {
      motor(25,26,l);motor(27,14,r);previousL=l;previousR=r;
    }
    xSemaphoreGive(lockHandle);
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
uint32_t number(const char* key) { return strtoul(server.arg(key).c_str(),nullptr,10); }
void statusReply(int code=200) {
  xSemaphoreTake(lockHandle,portMAX_DELAY);
  control.tick(millis());
  String result="{\"active\":"+String(control.active?"true":"false")+
    ",\"valid\":"+String(control.token && number("token")==control.token?"true":"false")+
    ",\"left\":"+String(control.left)+",\"right\":"+String(control.right)+
    ",\"remaining\":"+String(control.active && control.duration?(control.duration-(millis()-control.started)+999)/1000:0)+
    ",\"reason\":\""+String(control.reason)+"\"}";
  xSemaphoreGive(lockHandle);
  server.sendHeader("Cache-Control","no-store");server.send(code,"application/json",result);
}
void setup() {
  Serial.begin(115200);
  for(auto p:MOTOR_PINS) { digitalWrite(p,LOW);pinMode(p,OUTPUT); }
  lockHandle=xSemaphoreCreateMutex();
  if(!lockHandle) { Serial.println("Mutex failed");while(true) delay(1000); }
  pwmReady=true;
  for(auto p:MOTOR_PINS) if(!ledcAttach(p,PWM_HZ,8)) pwmReady=false;
  if(!pwmReady) { for(auto p:MOTOR_PINS) {ledcDetach(p);digitalWrite(p,LOW);} Serial.println("PWM failed");while(true) delay(1000); }
  for(auto p:MOTOR_PINS) ledcWrite(p,0);
  if(xTaskCreate(motorTask,"boatMotor",4096,nullptr,3,nullptr)!=pdPASS) { Serial.println("Task failed");while(true) delay(1000); }
  WiFi.mode(WIFI_AP);
  IPAddress ip(192,168,4,3),mask(255,255,255,0);
  if(!WiFi.softAPConfig(ip,ip,mask) || !WiFi.softAP("FRB_BOAT","frbboat123",6,0,1)) { Serial.println("WiFi failed");while(true) delay(1000); }
  server.on("/",HTTP_GET,[]{server.sendHeader("Cache-Control","no-store");server.send_P(200,"text/html; charset=utf-8",BOAT_PAGE);});
  server.on("/session",HTTP_POST,[]{
    uint32_t id=esp_random();if(!id) id=1;
    xSemaphoreTake(lockHandle,portMAX_DELAY);control.session(id);xSemaphoreGive(lockHandle);
    server.send(200,"application/json","{\"token\":"+String(id)+"}");
  });
  server.on("/drive",HTTP_POST,[]{
    String mode=server.arg("mode");
    if(mode!="forward" && mode!="back" && mode!="left" && mode!="right" && mode!="circleL" && mode!="circleR") {server.send(400,"text/plain","Bad mode");return;}
    int speed=constrain(server.arg("speed").toInt(),0,100),trim=constrain(server.arg("trim").toInt(),-100,100);
    int turn=constrain(server.arg("turn").toInt(),0,100);
    int l=speed,r=speed;
    if(trim>0) l=l*(100-trim)/100; else r=r*(100+trim)/100;
    if(mode=="left" || mode=="circleL") l=l*(100-turn)/100;
    if(mode=="right" || mode=="circleR") r=r*(100-turn)/100;
    if(mode=="back") {l=-l;r=-r;}
    if(server.arg("invL")=="1") l=-l;
    if(server.arg("invR")=="1") r=-r;
    uint32_t duration=(mode=="circleL" || mode=="circleR")?constrain(server.arg("seconds").toInt(),1,300)*1000UL:0;
    xSemaphoreTake(lockHandle,portMAX_DELAY);
    bool ok=control.drive(number("token"),number("seq"),millis(),l,r,duration);
    xSemaphoreGive(lockHandle);statusReply(ok?200:409);
  });
  server.on("/beat",HTTP_POST,[]{
    xSemaphoreTake(lockHandle,portMAX_DELAY);bool ok=control.beat(number("token"),number("seq"),millis());xSemaphoreGive(lockHandle);statusReply(ok?200:409);
  });
  server.on("/stop",HTTP_POST,[]{
    xSemaphoreTake(lockHandle,portMAX_DELAY);bool ok=control.halt(number("token"),number("seq"),millis());xSemaphoreGive(lockHandle);statusReply(ok?200:409);
  });
  server.onNotFound([]{server.send(404,"text/plain","Not found");});
  server.begin();Serial.println("FRB_BOAT / password: frbboat123 / http://192.168.4.3");
}
void loop() { server.handleClient();delay(1); }
