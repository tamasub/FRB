#pragma once
#include <Arduino.h>
#include <FS.h>
class AviWriter {
  File file;
  uint32_t moviListPos=0, moviDataPos=0, width=0,height=0, largest=0;
  uint32_t frames=0;
  bool writeRaw(const char *s, size_t n);
  bool w32(uint32_t n);
  bool w16(uint16_t n);
  bool patch32(uint32_t pos,uint32_t n);
public:
  bool begin(fs::FS &fs, const String &path, uint16_t w, uint16_t h);
  bool add(const uint8_t *jpg,uint32_t size);
  bool finish(uint32_t durationMs);
  void abort();
  uint32_t count() const {return frames;}
};
