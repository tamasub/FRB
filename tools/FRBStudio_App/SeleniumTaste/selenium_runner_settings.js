'use strict';

const fs = require('node:fs');
const path = require('node:path');

const DEFAULT_SETTINGS = Object.freeze({
  timing: Object.freeze({
    after_value_input_ms: 0,
  }),
});

const SETTINGS_FILE = process.env.FRB_SELENIUM_RUNNER_SETTINGS
  || path.join(__dirname, 'config', 'selenium_runner_settings_v0_1.json');

function toNonNegativeMs(value, fallback=0) {
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? Math.floor(number) : fallback;
}

function loadSeleniumRunnerSettings() {
  if (!fs.existsSync(SETTINGS_FILE)) {
    return {
      settings_file: SETTINGS_FILE,
      timing: {
        after_value_input_ms: DEFAULT_SETTINGS.timing.after_value_input_ms,
      },
    };
  }

  const parsed = JSON.parse(fs.readFileSync(SETTINGS_FILE, 'utf8'));
  return {
    ...parsed,
    settings_file: SETTINGS_FILE,
    timing: {
      ...(parsed.timing ?? {}),
      after_value_input_ms: toNonNegativeMs(
        parsed?.timing?.after_value_input_ms,
        DEFAULT_SETTINGS.timing.after_value_input_ms,
      ),
    },
  };
}

const SeleniumRunnerSettings = Object.freeze(loadSeleniumRunnerSettings());

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pauseAfterValueInput() {
  const ms = SeleniumRunnerSettings.timing.after_value_input_ms;
  if (ms > 0) await sleep(ms);
}

function printSeleniumRunnerTiming() {
  console.log(
    `Selenium Timing: after_value_input_ms=${SeleniumRunnerSettings.timing.after_value_input_ms}`
    + ` / ${path.relative(__dirname, SeleniumRunnerSettings.settings_file).replace(/\\\\/g, '/')}`,
  );
}

module.exports = {
  SeleniumRunnerSettings,
  pauseAfterValueInput,
  printSeleniumRunnerTiming,
};
