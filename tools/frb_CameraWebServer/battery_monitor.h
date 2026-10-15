#pragma once
#include <Arduino.h>

// FRB Sea Camera battery monitor.
// Hardware: LiPo+ -- R1 -- GPIO1 -- R2 -- GND, with R1=R2 (nominally 20kΩ).
// The divider halves the LiPo voltage so a 4.2V battery appears as ~2.1V at GPIO1.

void batteryMonitorInit();
float batteryVoltage();
uint32_t batteryAdcMilliVolts();
float batteryVoltageFromAdcMilliVolts(uint32_t adcMilliVolts);
const char* batteryLevelText(float voltage);
