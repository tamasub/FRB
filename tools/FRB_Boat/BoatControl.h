#pragma once
#include <stdint.h>
struct BoatControl {
  uint32_t token=0, sequence=0, lastBeat=0, started=0, duration=0;
  int left=0, right=0;
  bool active=false;
  const char* reason="起動・停止中";
  void stop(const char* why) { active=false; left=right=0; reason=why; }
  void tick(uint32_t now) {
    if (!active) return;
    if (now-lastBeat >= 800) { stop("通信切れで停止"); token=0; }
    else if (duration && now-started >= duration) stop("運転時間終了");
  }
  void session(uint32_t id) { stop("接続・停止中"); token=id; sequence=0; }
  bool accept(uint32_t id,uint32_t seq,uint32_t now) {
    tick(now);
    if (!token || id!=token || seq<=sequence) return false;
    sequence=seq; return true;
  }
  bool drive(uint32_t id,uint32_t seq,uint32_t now,int l,int r,uint32_t ms) {
    if (!accept(id,seq,now)) return false;
    left=l;right=r;duration=ms;started=lastBeat=now;active=true;reason="運転中";return true;
  }
  bool beat(uint32_t id,uint32_t seq,uint32_t now) {
    tick(now);
    // Heartbeats never supersede a pending STOP command.
    if (!token || id!=token || seq<sequence) return false;
    if(active) lastBeat=now;
    return true;
  }
  bool halt(uint32_t id,uint32_t seq,uint32_t now) {
    if(!accept(id,seq,now)) return false;
    stop("停止"); return true;
  }
};
