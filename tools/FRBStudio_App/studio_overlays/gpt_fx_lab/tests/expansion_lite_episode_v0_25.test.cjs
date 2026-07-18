const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const root = path.resolve(process.argv[2] || process.cwd());
function artifactPath(...parts) {
  const p = path.join(root, ...parts);
  if (fs.existsSync(p)) return p;
  const w = path.join(root, parts.join('\\'));
  if (fs.existsSync(w)) return w;
  throw new Error(`missing ${parts.join('/')}`);
}

const pluginPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.js');
const manifestPath = artifactPath('studio_overlays','gpt_fx_lab','plugins','fx_chart_viewer','plugin.json');
const profilePath = artifactPath('studio_overlays','gpt_fx_lab','simulation','fx_simulation_run_profile_expansion_lite_v0_1.json');
const source = fs.readFileSync(pluginPath, 'utf8');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf8'));

assert.equal(manifest.version, '0.9.1.21');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.rule_version, 'v0.26');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.m5_dow_confirmation_required, false);
assert.equal(profile.m5_execution_policy.expansion_lite_policy.episode_unit, 'EXPANSION_EPISODE');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.other_lane_trade_state_input, 'FORBIDDEN');
assert.equal(profile.m5_execution_policy.expansion_lite_policy.same_episode_reentry, 'NOT_DEFINED_DISABLED');

const hook = `
window.__liteV025 = {
  normalizeSimulationRunProfile,
  validateSimulationRunDraft,
  m5ExecutionExpansionLiteAnchorResolution,
  m5ExecutionExpansionLiteFacts,
  m5ExecutionLevelTouch,
  m5ExecutionExpansionLiteEpisode,
  expansionLiteRuleLaneEntryDecision
};`;
const closeIndex = source.lastIndexOf('})();');
assert.ok(closeIndex > 0);
const instrumented = source.slice(0, closeIndex) + hook + source.slice(closeIndex);
const context = { window:{}, console, setTimeout, clearTimeout, URL, structuredClone, Intl, Date, Math, JSON, Map, Set, Promise };
vm.runInNewContext(instrumented, context, { filename: pluginPath });
const api = context.window.__liteV025;
const normalized = api.normalizeSimulationRunProfile(profile);
const validation = api.validateSimulationRunDraft(normalized);
assert.equal(validation.valid, true, validation.errors.join('\n'));

const episodeStart = '2025-12-01 14:59';
const referenceTime = '2025-12-01 15:04';
const referenceMs = Date.parse('2025-12-01T15:04:00+09:00');
const snapshot = {
  timeframes: {
    H4: { latest_confirmed_bar: { close:154.100, t3_20_0_2:154.500 } },
    H1: {
      latest_confirmed_bar: { index:100, close:154.200, t3_20_0_2:154.400 },
      swing_state: {
        latest_pending_high: { point_id:'h1_high_33', type:'swing_high', source_index:96, pivot_time:'2025-12-01 11:00', pivot_price:155.200, confirm_bars:7 },
        latest_active_high: { point_id:'h1_high_old', type:'swing_high', source_index:80, pivot_time:'2025-11-28 18:00', pivot_price:155.560, confirm_bars:7 }
      },
      cycle_state: { elapsed_bars:4, origin:{ point_id:'h1_high_33', source_index:96, confirm_bars:7 } }
    },
    M5: {
      trend_state:'DOWN',
      latest_confirmed_bar:{ open:154.800, high:154.820, low:154.680, close:154.696 },
      hsi_anchor_state: {
        expansion_detection: {
          status:'RESOLVED_REFERENCE',
          anchor_id:'m5_expansion_detection_high_001',
          anchor:{
            anchor_id:'m5_expansion_detection_high_001',
            anchor_type:'HIGH', direction:'DOWN', pivot_time:'2025-12-01 13:30', price:155.560,
            confirmed_time:episodeStart,
            expansion_detection_regime:{ direction:'DOWN', started_at:referenceTime, started_at_ms:referenceMs, reset_policy:'OPPOSITE_DIRECTIONAL_DOW_CONFIRMED' }
          }
        },
        rule_lanes: {
          EXPANSION_LITE: {
            entry_anchor: {
              status:'RESOLVED_REFERENCE',
              anchor_id:'m5_expansion_detection_high_001',
              anchor:{
                anchor_id:'m5_expansion_detection_high_001', anchor_type:'HIGH', direction:'DOWN',
                pivot_time:'2025-12-01 13:30', price:155.560,
                expansion_detection_regime:{ direction:'DOWN', started_at:referenceTime, started_at_ms:referenceMs }
              }
            }
          }
        }
      },
      trend_detail:{ high_relation:'LOWER', low_relation:'LOWER' }
    }
  }
};

const resolution = api.m5ExecutionExpansionLiteAnchorResolution(snapshot);
assert.equal(resolution.status, 'RESOLVED_REFERENCE');
assert.equal(resolution.direction, 'DOWN');
assert.equal(resolution.anchor.price, 155.560);
const facts = api.m5ExecutionExpansionLiteFacts(snapshot, normalized, resolution);
assert.equal(facts.episode_side, 'SHORT');
assert.equal(facts.direction, 'SHORT');
assert.equal(facts.entry_direction_ready, true);
assert.equal(facts.other_lane_trade_state_used, false);

const policy = normalized.m5_execution_policy;
const r3 = api.m5ExecutionLevelTouch(snapshot.timeframes.M5.latest_confirmed_bar, resolution.anchor.price, 'SHORT', 144, 'R3', policy);
assert.equal(r3.touched, true);
const portfolio = {
  // 他Laneの売買状態をわざと混在させても、Lite判断は参照しない。
  trades:[{ trade_id:'normal_closed_001', rule_lane:'NORMAL', status:'CLOSED', close_class:'CLOSE_OK' }],
  positions:[{ position_id:'normal_pos_001', trade_id:'normal_closed_001', rule_lane:'NORMAL', status:'CLOSED', units_open:0 }],
  normal_entry_opportunities:[{ opportunity_id:'normal_opp', status:'USED' }],
  expansion_lite_episodes:[], expansion_lite_entry_opportunities:[], used_expansion_lite_episode_ids:[]
};
const decision = api.expansionLiteRuleLaneEntryDecision({
  portfolio, referenceMs, referenceTime, price:154.696,
  currentBar:snapshot.timeframes.M5.latest_confirmed_bar,
  expansionLiteFacts:facts,
  // 新しいDow Confirmationは渡さない。EpisodeだけでEntryできることを確認。
  dowConfirmation:null,
  entryResolution:resolution, entryAnchor:resolution.anchor, anchorPrice:resolution.anchor.price,
  distanceRaw:144, r3Touch:r3, policy, timeframeSnapshot:snapshot
});
assert.equal(decision.action, 'ENTRY');
assert.equal(decision.execution_candidate.entry_level, 'R3');
assert.equal(decision.entry_opportunity.initial_entry_status, 'USED');
assert.equal(decision.entry_opportunity.direction, 'SHORT');
assert.ok(decision.entry_opportunity.episode_id.startsWith('expansion_lite_episode_short_'));
assert.ok(decision.reason_codes.includes('EXPANSION_LITE_OTHER_LANE_TRADE_STATE_NOT_USED'));
assert.equal(decision.execution_candidate.anchor_price, 155.560);

// 同じEpisodeではInitial Entryを二重実行しない。
const second = api.expansionLiteRuleLaneEntryDecision({
  portfolio, referenceMs:referenceMs+300000, referenceTime:'2025-12-01 15:09', price:154.650,
  currentBar:{ open:154.700, high:154.720, low:154.620, close:154.650 },
  expansionLiteFacts:facts, dowConfirmation:{ confirmation_id:'normal_only_new_confirmation_should_be_ignored', direction:'DOWN' },
  entryResolution:resolution, entryAnchor:resolution.anchor, anchorPrice:resolution.anchor.price,
  distanceRaw:150, r3Touch:{...r3,touched:true}, policy, timeframeSnapshot:snapshot
});
assert.equal(second.action, 'WAIT');
assert.equal(second.entry_opportunity.initial_entry_status, 'USED');
assert.ok(second.reason_codes.includes('EXPANSION_LITE_EPISODE_INITIAL_ENTRY_USED'));

// 反対方向Detectionは別Episodeを開始する。
const longResolution = {
  status:'RESOLVED_REFERENCE', direction:'UP', anchor_id:'m5_expansion_detection_low_002', detection_anchor_id:'m5_expansion_detection_low_002',
  anchor:{ anchor_id:'m5_expansion_detection_low_002', direction:'UP', pivot_time:'2025-12-02 09:00', price:153.000,
    expansion_detection_regime:{ direction:'UP', started_at:'2025-12-02 10:00', started_at_ms:referenceMs+86400000 } }
};
const nextEpisode = api.m5ExecutionExpansionLiteEpisode(portfolio, longResolution, referenceMs+86400000, '2025-12-02 10:00');
assert.equal(nextEpisode.direction, 'LONG');
assert.notEqual(nextEpisode.episode_id, decision.entry_opportunity.episode_id);
const previousEpisode = portfolio.expansion_lite_episodes.find(x => x.episode_id === decision.entry_opportunity.episode_id);
assert.equal(previousEpisode.status, 'ENDED');
assert.equal(previousEpisode.episode_end_reason_code, 'EXPANSION_LITE_EPISODE_ENDED_BY_OPPOSITE_DETECTION');

assert.match(source, /OWN_PREVIOUS_STATE_PLUS_SHARED_MARKET_FACTS_ONLY/);
assert.doesNotMatch(source, /FIRST_R3_TOUCH_AFTER_DOW_CONFIRMATION/);
console.log('PASS expansion_lite_episode_v0_25');
console.log(`entry=${decision.action_label} episode=${decision.entry_opportunity.episode_id}`);
