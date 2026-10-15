#include "battery_monitor.h"

// ESP32-S3 ADC1 pin selected for the FRB Sea Camera divider.
static constexpr uint8_t BATTERY_ADC_PIN = 1;

// Equal resistor divider: R1 = 20kΩ, R2 = 20kΩ => Vbat = Vadc * 2.
// Keep this configurable in case the actual resistor values are changed later.
static constexpr float BATTERY_DIVIDER_RATIO = 2.0f;

// Fine calibration multiplier. Start at 1.000. If a multimeter later shows,
// for example, 3.90V while the UI says 3.80V, set this to 3.90/3.80 = 1.0263.
static constexpr float BATTERY_CALIBRATION = 1.000f;

// Short averaging suppresses normal ESP32 ADC noise without adding noticeable UI delay.
static constexpr uint8_t BATTERY_SAMPLE_COUNT = 12;

void batteryMonitorInit() {
  pinMode(BATTERY_ADC_PIN, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(BATTERY_ADC_PIN, ADC_11db);

  delay(10);
  float v = batteryVoltage();
  Serial.printf("BAT: GPIO%u divider=%.2f voltage=%.3fV\n",
                BATTERY_ADC_PIN, BATTERY_DIVIDER_RATIO, v);
}

uint32_t batteryAdcMilliVolts() {
  uint64_t total = 0;
  for (uint8_t i = 0; i < BATTERY_SAMPLE_COUNT; ++i) {
    total += analogReadMilliVolts(BATTERY_ADC_PIN);
    delay(1);
  }
  return (uint32_t)(total / BATTERY_SAMPLE_COUNT);
}

float batteryVoltageFromAdcMilliVolts(uint32_t adcMilliVolts) {
  return ((float)adcMilliVolts / 1000.0f) * BATTERY_DIVIDER_RATIO * BATTERY_CALIBRATION;
}

float batteryVoltage() {
  return batteryVoltageFromAdcMilliVolts(batteryAdcMilliVolts());
}

const char* batteryLevelText(float voltage) {
  // These are intentionally broad indicators, not a precise LiPo percentage.
  // Under Wi-Fi / camera / SD load the voltage can sag, and that sag is useful information.
  if (voltage >= 3.70f) return "GOOD";
  if (voltage >= 3.50f) return "LOW";
  return "CRITICAL";
}
