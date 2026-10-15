#pragma once
#include <Arduino.h>

bool recorderInit();
bool recorderStart(uint32_t targetFrames, uint32_t intervalMs, const String &startedAt="", bool video=false);
String recorderLastStartError();
bool recorderAutoResume();
void recorderService();
void recorderStartSupervisor();
bool recorderStop();
bool recorderIsRecording();
String recorderStatusJson();
String recorderFilesJson();
bool recorderFrameExists(const String &session, uint32_t frameNo);
String recorderFramePath(const String &session, uint32_t frameNo);
bool recorderDeleteSession(const String &session);

bool recorderVideoExists(const String &session,uint32_t part=0);
String recorderVideoPath(const String &session,uint32_t part=0);
