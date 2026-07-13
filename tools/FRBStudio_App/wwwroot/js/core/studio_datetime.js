// v0.18.19-studio-datetime-format-contract
// Studio common date/time formatter for human-facing browser output.
// Default human format: yyyy-MM-dd_HH:mm:ss in JST.
(function installStudioDateTime(global) {
  if (global.StudioDateTime && global.StudioDateTime.version === 'v0.18.19') return;

  const JST_TIME_ZONE = 'Asia/Tokyo';

  function pad(value, length = 2) {
    return String(value).padStart(length, '0');
  }

  function partsOf(date = new Date()) {
    const d = date instanceof Date ? date : new Date(date);
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: JST_TIME_ZONE,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).formatToParts(d).reduce((acc, part) => {
      if (part.type !== 'literal') acc[part.type] = part.value;
      return acc;
    }, {});

    return {
      year: parts.year,
      month: parts.month,
      day: parts.day,
      hour: parts.hour,
      minute: parts.minute,
      second: parts.second,
      millisecond: pad(d.getMilliseconds(), 3)
    };
  }

  function formatDateTime(date = new Date(), options = {}) {
    const p = partsOf(date);
    const base = `${p.year}-${p.month}-${p.day}_${p.hour}:${p.minute}:${p.second}`;
    return options.includeMillis ? `${base}.${p.millisecond}` : base;
  }

  function formatFileTimestamp(date = new Date(), options = {}) {
    const p = partsOf(date);
    const base = `${p.year}${p.month}${p.day}_${p.hour}${p.minute}${p.second}`;
    return options.includeMillis ? `${base}_${p.millisecond}` : base;
  }

  function formatIsoJst(date = new Date(), options = {}) {
    const p = partsOf(date);
    const millis = options.includeMillis ? `.${p.millisecond}` : '';
    return `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}:${p.second}${millis}+09:00`;
  }

  const api = Object.freeze({
    version: 'v0.18.19',
    timeZone: JST_TIME_ZONE,
    formatDateTime,
    formatFileTimestamp,
    formatIsoJst
  });

  global.StudioDateTime = api;
  global.studioFormatDateTime = formatDateTime;
  global.studioFormatFileTimestamp = formatFileTimestamp;
  global.studioFormatIsoJst = formatIsoJst;
})(window);
