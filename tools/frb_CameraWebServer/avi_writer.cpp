#include "avi_writer.h"
#include <SD_MMC.h>
#include <esp_camera.h>
#include <cstring>
static uint32_t fourcc(const char *s) { return uint32_t(uint8_t(s[0])) | (uint32_t(uint8_t(s[1]))<<8) | (uint32_t(uint8_t(s[2]))<<16) | (uint32_t(uint8_t(s[3]))<<24); }
bool AviWriter::writeRaw(const char *s,size_t n){return file.write((const uint8_t*)s,n)==n;}
bool AviWriter::w32(uint32_t n){uint8_t v[4]={uint8_t(n),uint8_t(n>>8),uint8_t(n>>16),uint8_t(n>>24)};return file.write(v,4)==4;}
bool AviWriter::w16(uint16_t n){uint8_t v[2]={uint8_t(n),uint8_t(n>>8)};return file.write(v,2)==2;}
bool AviWriter::patch32(uint32_t p,uint32_t n){uint32_t at=file.position();if(!file.seek(p))return false;bool ok=w32(n);return file.seek(at)&&ok;}
bool AviWriter::begin(fs::FS &fs,const String &path,uint16_t w,uint16_t h){
  width=w;height=h;frames=0;largest=0;
  // The file MUST be opened read/write. At STOP we re-read each JPEG chunk
  // to build idx1; opening with FILE_WRITE ("w") makes File::read() fail
  // on ESP32 VFS and leaves an unfinished/unplayable RIFF file.
  file=fs.open(path.c_str(),"w+");if(!file)return false;
  // AVI 1.0 / MJPG / one video stream, no audio; offsets are fixed for patching.
  bool ok=writeRaw("RIFF",4)&&w32(0)&&writeRaw("AVI ",4)
    // 'hdrl' = 4-byte type + (avih 8+56) + (strl LIST 8+116) = 192.
    &&writeRaw("LIST",4)&&w32(192)&&writeRaw("hdrl",4)
    &&writeRaw("avih",4)&&w32(56)
    &&w32(200000)&&w32(0)&&w32(0)&&w32(0x10)&&w32(0)&&w32(0)&&w32(1)&&w32(0)&&w32(w)&&w32(h)
    &&w32(0)&&w32(0)&&w32(0)&&w32(0)
    &&writeRaw("LIST",4)&&w32(116)&&writeRaw("strl",4)
    &&writeRaw("strh",4)&&w32(56)&&writeRaw("vids",4)&&writeRaw("MJPG",4)
    &&w32(0)&&w16(0)&&w16(0)&&w32(0)&&w32(1)&&w32(5)&&w32(0)&&w32(0)&&w32(0)
    &&w32(0xFFFFFFFF)&&w32(0)&&w16(0)&&w16(0)&&w16(w)&&w16(h)
    &&writeRaw("strf",4)&&w32(40)&&w32(40)&&w32(w)&&w32(h)&&w16(1)&&w16(24)
    &&writeRaw("MJPG",4)&&w32(0)&&w32(0)&&w32(0)&&w32(0)&&w32(0)
    &&writeRaw("LIST",4)&&w32(0)&&writeRaw("movi",4);
  if(!ok){abort();return false;}
  moviListPos=file.position()-8; // movi LIST size offset
  moviDataPos=file.position();
  Serial.printf("AVI header end=%u\n",moviDataPos);
  return true;
}
bool AviWriter::add(const uint8_t *jpg,uint32_t size){
  if(!file || !jpg || !size || file.position()>0xF0000000U-size-32)return false;
  if(!writeRaw("00dc",4)||!w32(size)||file.write(jpg,size)!=size)return false;
  if(size&1){const uint8_t pad=0;if(file.write(&pad,1)!=1)return false;}
  frames++;if(size>largest)largest=size;
  return true;
}
bool AviWriter::finish(uint32_t durationMs){
  if(!file)return false;
  // A seek (after flush) is required when switching w+ from writing to reading.
  file.flush();
  uint32_t indexPos=file.position();
  bool ok=patch32(moviListPos,indexPos-(moviListPos+4));
  if(!file.seek(indexPos))ok=false;
  if(ok)ok=writeRaw("idx1",4)&&w32(frames*16);
  // Re-scan chunks to construct index, avoiding PSRAM use / per-frame sidecar writes.
  uint32_t scan=moviDataPos;
  for(uint32_t i=0;ok&&i<frames;i++){
    if(!file.seek(scan)) {ok=false;break;}
    uint8_t hdr[8];if(file.read(hdr,8)!=8){ok=false;break;}
    uint32_t size=uint32_t(hdr[4])|(uint32_t(hdr[5])<<8)|(uint32_t(hdr[6])<<16)|(uint32_t(hdr[7])<<24);
    uint32_t next=scan+8+size+(size&1);
    if(memcmp(hdr,"00dc",4)!=0||next>indexPos){ok=false;break;}
    if(!file.seek(indexPos+8+i*16)){ok=false;break;}
    ok=w32(fourcc("00dc"))&&w32(0x10)&&w32(scan-(moviDataPos-4))&&w32(size);
    scan=next;
    if((i & 63u)==63u)delay(1); // Yield during a long per-minute SD index build.
  }
  if(ok){
    uint32_t end=indexPos+8+frames*16;
    uint32_t fps1000=(frames>1&&durationMs>0)?uint32_t((uint64_t(frames-1)*1000000ULL)/durationMs):5000;
    if(fps1000<100)fps1000=100;
    // avih and strh fixed header positions. Timescale = 1000/fps1000.
    ok=patch32(4,end-8)&&patch32(32,uint32_t(1000000000ULL/fps1000))
       &&patch32(48,frames)&&patch32(60,largest)
       &&patch32(128,1000)&&patch32(132,fps1000)&&patch32(140,frames)&&patch32(144,largest);
    file.seek(end);
  }
  file.flush();file.close();
  Serial.printf("AVI finalize: frames=%u bytes=%u index=%u result=%s\n", frames,
                indexPos+8+frames*16, indexPos, ok ? "OK" : "FAILED");
  return ok;
}
void AviWriter::abort(){if(file)file.close();}
