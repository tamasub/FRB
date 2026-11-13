// v0.18.19-studio-datetime-format-contract
// Studio common date/time helpers for Node.js test evidence.
// Default human format: yyyy-MM-dd_HH:mm:ss in JST.

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

export function toStudioDateTime(date = new Date(), options = {}) {
  const p = partsOf(date);
  const base = `${p.year}-${p.month}-${p.day}_${p.hour}:${p.minute}:${p.second}`;
  return options.includeMillis ? `${base}.${p.millisecond}` : base;
}

export function toStudioFileTimestamp(date = new Date(), options = {}) {
  const p = partsOf(date);
  const base = `${p.year}${p.month}${p.day}_${p.hour}${p.minute}${p.second}`;
  return options.includeMillis ? `${base}_${p.millisecond}` : base;
}

export function toStudioIsoJst(date = new Date(), options = {}) {
  const p = partsOf(date);
  const millis = options.includeMillis ? `.${p.millisecond}` : '';
  return `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}:${p.second}${millis}+09:00`;
}

// Compatibility aliases for the v0.18.18 follow-up names.
export const toJstIsoString = toStudioDateTime;
export const toJstFileTimestamp = toStudioFileTimestamp;
