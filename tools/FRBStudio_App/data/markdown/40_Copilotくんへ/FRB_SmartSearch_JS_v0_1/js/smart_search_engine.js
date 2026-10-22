// studio_work_0268 / Step 1: Search expression parser and evaluator for JSON rows.
// UI/DOM independent. Existing individual SearchFilter criteria remain unchanged.
// Contract: whitespace AND, OR, parentheses, Field=Value and typed operators.
var StudioSmartSearch = (function () {
  'use strict';

  const OPERATOR = Object.freeze({
    '=': 'default', '==': 'exact', '!=': 'not_default', '=!': 'not_default',
    '>': 'gt', '<': 'lt', '>=': 'gte', '=>': 'gte', '<=': 'lte', '=<': 'lte'
  });
  const COMPARATORS = ['==', '!=', '=!', '>=', '=>', '<=', '=<', '=', '>', '<'];
  const ORDERED_FAMILIES = new Set(['number', 'date', 'datetime', 'instant']);

  function error(code, message, offset=0) {
    const err = new Error(message);
    err.name = 'StudioSmartSearchError';
    err.code = code;
    err.offset = offset;
    return err;
  }

  // Quotes delimit whitespace/brackets ONLY at a value or token boundary.
  // An apostrophe inside O'Reilly is literal, not the start of a quoted string.
  function tokenize(source) {
    const tokens = [];
    let i = 0;
    while (i < source.length) {
      if (/\s/u.test(source[i])) { i++; continue; }
      const start = i;
      if (source[i] === '(' || source[i] === ')') {
        tokens.push({type: source[i], value: source[i], offset:start}); i++; continue;
      }
      let value = '', quoted = false, operatorOutsideQuote = false, atSegmentStart = true;
      while (i < source.length && !/\s/u.test(source[i]) && source[i] !== '(' && source[i] !== ')') {
        const c = source[i];
        if ((c === '"' || c === "'") && atSegmentStart) {
          const quote = c;
          quoted = true;
          i++;
          let closed = false;
          while (i < source.length) {
            if (source[i] === '\\' && (source[i+1] === quote || source[i+1] === '\\')) {
              value += source[i+1]; i += 2;
            } else if (source[i] === quote) { i++; closed = true; break; }
            else value += source[i++];
          }
          if (!closed) throw error('UNCLOSED_QUOTE', '引用符が閉じられていません', start);
          atSegmentStart = false;
        } else {
          value += c;
          if ('=!<>'.includes(c)) operatorOutsideQuote = true;
          i++;
          atSegmentStart = c === '=' || c === '!' || c === '<' || c === '>';
        }
      }
      if (!value && !quoted) throw error('EMPTY_TOKEN', '空の検索語です', start);
      const type = !quoted && /^or$/i.test(value) ? 'OR'
        : !quoted && /^and$/i.test(value) ? 'AND' : 'TERM';
      tokens.push({type, value, offset:start, literalQuoted:quoted && !operatorOutsideQuote});
    }
    return tokens;
  }

  function familyFor(field) {
    const explicit = String(field?.value_family ?? field?.valueFamily ?? field?.resolved_value_family ?? '').toLowerCase();
    const type = String(field?.type ?? '').toLowerCase();
    const validation = String(field?.validation_type ?? '').toLowerCase();
    const family = explicit || (
      /^(studio\.)?(number|integer|float|decimal)(\.|$)/.test(validation) ? 'number' :
      /^(studio\.)?datetime(\.|$)/.test(validation) ? 'datetime' :
      /^(studio\.)?instant(\.|$)/.test(validation) ? 'instant' :
      /^(studio\.)?date(\.|$)/.test(validation) ? 'date' :
      /^(studio\.)?boolean(\.|$)/.test(validation) ? 'boolean' : type
    );
    if (['number', 'integer', 'float', 'decimal'].includes(family)) return 'number';
    if (['date','datetime','instant','boolean','select'].includes(family)) return family;
    return 'string';
  }

  function fieldIndex(fields) {
    const map = new Map();
    for (const field of (Array.isArray(fields) ? fields : [])) {
      if (!field?.field) continue;
      const names = [field.field, field.caption, field.label].filter(Boolean);
      for (const name of new Set(names.map(x=>String(x).trim().toLowerCase()))) {
        const arr = map.get(name) ?? [];
        if (!arr.includes(field)) arr.push(field);
        map.set(name, arr);
      }
    }
    return map;
  }

  function resolveField(name, index, offset) {
    const found = index.get(String(name).trim().toLowerCase()) ?? [];
    if (!found.length) throw error('UNKNOWN_FIELD', `検索項目が見つかりません: ${name}`, offset);
    const distinct = new Set(found.map(x=>String(x.field)));
    if (distinct.size > 1) throw error('AMBIGUOUS_FIELD', `検索項目名が重複しています: ${name}（項目IDを指定してください）`, offset);
    return found[0];
  }

  function parseTerm(token, index, parseValue) {
    const text = token.value;
    if (token.literalQuoted) return {kind:'text', value:text.toLowerCase()};
    // Comparator belongs to a field-specific search. No comparator = cross-field search.
    const match = /^(.+?)(==|!=|=!|>=|=>|<=|=<|=|>|<)(.*)$/u.exec(text);
    if (!match) return {kind:'text', value:text.toLowerCase()};
    const [, name, spelling, rest] = match;
    const field = resolveField(name, index, token.offset);
    const family = familyFor(field);
    const operator = OPERATOR[spelling];
    let value = rest;
    if (!value) {
      const next = parseValue();
      if (!next) throw error('MISSING_VALUE', `検索値を指定してください: ${name}`, token.offset);
      value = next;
    }
    const node = {kind:'field', field:field.field, family, operator, value, fieldDef:field};
    if (value.includes('..') && (operator === 'default' || operator === 'exact') && ORDERED_FAMILIES.has(family)) {
      if (value.indexOf('..') !== value.lastIndexOf('..')) throw error('INVALID_RANGE', `範囲指定が不正です: ${text}`, token.offset);
      const [from, to] = value.split('..');
      if (!from && !to) throw error('INVALID_RANGE', '範囲の開始値または終了値を指定してください', token.offset);
      if ((from && comparable(from,family) == null) || (to && comparable(to,family) == null)) {
        throw error('INVALID_RANGE', `範囲指定の値が不正です: ${text}`, token.offset);
      }
      if (from && to && comparable(from,family) > comparable(to,family)) {
        throw error('REVERSED_RANGE', `開始値が終了値を超えています: ${text}`, token.offset);
      }
      node.kind = 'range'; node.from = from; node.to = to;
    } else if (ORDERED_FAMILIES.has(family) && comparable(value,family) == null) {
      throw error('INVALID_VALUE', `数値・日付の検索値が不正です: ${name}=${value}`,token.offset);
    } else if (family === 'boolean' && boolValue(value) == null) {
      throw error('INVALID_VALUE', `Boolean検索値が不正です: ${name}=${value}`,token.offset);
    }
    if (['gt','gte','lt','lte'].includes(operator) && !ORDERED_FAMILIES.has(family)) {
      throw error('INCOMPATIBLE_OPERATOR', `この項目型では大小比較できません: ${name}`,token.offset);
    }
    return node;
  }

  function parse(query, fields=[]) {
    const tokens = tokenize(String(query ?? ''));
    const index = fieldIndex(fields);
    let pos = 0;
    if (!tokens.length) return {kind:'all'};
    function primary() {
      const t = tokens[pos];
      if (!t || t.type === 'OR' || t.type === 'AND' || t.type === ')') {
        throw error('MISSING_OPERAND', '検索条件が不足しています', t?.offset ?? String(query).length);
      }
      if (t.type === '(') {
        pos++;
        const expression = orExpression();
        if (tokens[pos]?.type !== ')') throw error('UNCLOSED_PAREN', '閉じ括弧 ) がありません',t.offset);
        pos++;
        return expression;
      }
      pos++;
      return parseTerm(t, index, () => {
        const next = tokens[pos];
        if (!next || next.type !== 'TERM') return null;
        pos++;
        return next.value;
      });
    }
    function andExpression() {
      let left = primary();
      while (pos < tokens.length && tokens[pos].type !== ')' && tokens[pos].type !== 'OR') {
        if (tokens[pos].type === 'AND') {
          const current = tokens[pos++];
          if (!tokens[pos] || ['AND','OR',')'].includes(tokens[pos].type)) {
            throw error('MISSING_OPERAND','ANDの右側に検索条件がありません',current.offset);
          }
        }
        left = {kind:'and', left, right:primary()};
      }
      return left;
    }
    function orExpression() {
      let left = andExpression();
      while (tokens[pos]?.type === 'OR') {
        const current = tokens[pos++];
        if (!tokens[pos] || ['OR','AND',')'].includes(tokens[pos].type)) {
          throw error('MISSING_OPERAND','ORの右側に検索条件がありません',current.offset);
        }
        left = {kind:'or', left, right:andExpression()};
      }
      return left;
    }
    const ast = orExpression();
    if (pos !== tokens.length) throw error('UNEXPECTED_TOKEN', `予期しない構文です: ${tokens[pos].value}`,tokens[pos].offset);
    return ast;
  }

  function validParts(y,m,d,h=0,min=0,s=0,ms=0) {
    const date = new Date(Date.UTC(y,m-1,d,h,min,s,ms));
    return date.getUTCFullYear()===y && date.getUTCMonth()===m-1 && date.getUTCDate()===d && date.getUTCHours()===h && date.getUTCMinutes()===min && date.getUTCSeconds()===s && date.getUTCMilliseconds()===ms;
  }
  function comparable(raw,family) {
    if (raw == null || raw === '') return null;
    if (family === 'number') {
      const text = String(raw).trim();
      if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(text)) return null;
      const n = Number(text); return Number.isFinite(n) ? n : null;
    }
    const text = String(raw).trim();
    if (family === 'date') {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
      if (!m) return null;
      const parts=m.slice(1).map(Number);
      return validParts(...parts) ? Date.UTC(parts[0],parts[1]-1,parts[2]) : null;
    }
    if (family === 'datetime') {
      const m = /^(\d{4})-(\d{2})-(\d{2})[T_ ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,3}))?)?$/.exec(text);
      if (!m) return null;
      const [y,mo,d,h,mi,s,ms] = [Number(m[1]),Number(m[2]),Number(m[3]),Number(m[4]),Number(m[5]),Number(m[6]??0),Number((m[7]??'0').padEnd(3,'0'))];
      return validParts(y,mo,d,h,mi,s,ms) ? Date.UTC(y,mo-1,d,h,mi,s,ms) : null;
    }
    if (family === 'instant') {
      if (!/(Z|[+-]\d{2}:\d{2})$/i.test(text)) return null;
      const millis = Date.parse(text); return Number.isFinite(millis) ? millis : null;
    }
    return null;
  }

  function boolValue(raw) {
    if (raw === true || raw === 1) return true;
    if (raw === false || raw === 0) return false;
    const text = String(raw ?? '').toLowerCase();
    if (['true','1','はい'].includes(text)) return true;
    if (['false','0','いいえ'].includes(text)) return false;
    return null;
  }

  function getByField(row,path) {
    const text=String(path ?? '').replace(/^\$\.?/,'');
    if (row && Object.prototype.hasOwnProperty.call(row,text)) return row[text];
    return text.split('.').reduce((obj,segment)=>obj == null ? undefined : obj[segment],row);
  }

  function optionValues(field, input) {
    const needle=String(input).toLowerCase();
    const matches=[];
    for (const option of Array.isArray(field.options) ? field.options : []) {
      const valueKey=field.valueField ?? field.value_field ?? field.optionValueField ?? field.option_value_field ?? 'cd';
      const labelKey=field.labelField ?? field.label_field ?? field.optionLabelField ?? field.option_label_field ?? 'name';
      const value = option && typeof option === 'object' ? option[valueKey] ?? option.cd ?? option.value ?? option.id ?? option.key : option;
      const label = option && typeof option === 'object' ? option[labelKey] ?? option.name ?? option.label ?? option.caption ?? option.text ?? value : option;
      if (String(label ?? '').toLowerCase()===needle || String(value ?? '').toLowerCase()===needle) matches.push(String(value));
    }
    return matches.length ? matches : [String(input)];
  }

  function matchesValue(row, node) {
    const actual = getByField(row,node.field);
    // Missing values are not treated as ordinary values, even for !=.
    if (actual == null || actual === '') return false;
    const family=node.family;
    const values = Array.isArray(actual) ? actual : [actual];
    if (node.kind === 'range') return values.some(value => {
      const n = comparable(value,family);
      return n != null && (!node.from || n>=comparable(node.from,family)) && (!node.to || n<=comparable(node.to,family));
    });
    const expected = family==='select' ? optionValues(node.fieldDef,node.value) : [node.value];
    const positive = values.some(value => expected.some(candidate => {
      if (ORDERED_FAMILIES.has(family)) {
        const a=comparable(value,family), b=comparable(candidate,family);
        if (a==null || b==null) return false;
        if (node.operator==='gt') return a>b;
        if (node.operator==='gte') return a>=b;
        if (node.operator==='lt') return a<b;
        if (node.operator==='lte') return a<=b;
        return a===b;
      }
      if (family==='boolean') return boolValue(value)!=null && boolValue(value)===boolValue(candidate);
      const a=String(value).toLowerCase(), b=String(candidate).toLowerCase();
      if (family==='string' && ['default','not_default'].includes(node.operator)) return a.includes(b);
      return a===b;
    }));
    return node.operator==='not_default' ? !positive : positive;
  }

  function collectStrings(value,out=[],seen=new Set()) {
    if (typeof value==='string') {out.push(value);return out;}
    if (value==null || typeof value!=='object' || seen.has(value)) return out;
    seen.add(value);
    for (const child of Object.values(value)) collectStrings(child,out,seen);
    return out;
  }
  function evaluate(row,ast,cache={}) {
    if (ast.kind==='all') return true;
    if (ast.kind==='and') return evaluate(row,ast.left,cache) && evaluate(row,ast.right,cache);
    if (ast.kind==='or') return evaluate(row,ast.left,cache) || evaluate(row,ast.right,cache);
    if (ast.kind==='text') {
      if (!cache.textValues) cache.textValues = collectStrings(row).map(v=>v.toLowerCase());
      return cache.textValues.some(value=>value.includes(ast.value));
    }
    if (ast.kind==='field' || ast.kind==='range') return matchesValue(row,ast);
    throw error('INVALID_AST','未対応の検索構文です');
  }

  return Object.freeze({parse, evaluate, tokenize, familyFor, error});
})();
