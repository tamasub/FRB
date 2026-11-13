// Thought Evolution Studio v0.4 / Evolution Engine Overlay
// External library free: SVG + CSS + plain JavaScript.

(function () {
  'use strict';

  const PLUGIN_ID = 'thought_evolution.graph_studio';
  const ACTION_ID = 'thought_evolution.open';
  const STYLE_ID = 'thoughtEvolutionStudioV04Styles';
  const DIALOG_ID = 'thoughtEvolutionStudioV04';
  const SVG_NS = 'http://www.w3.org/2000/svg';

  function clone(value) {
    if (value == null) return value;
    try {
      return typeof structuredClone === 'function'
        ? structuredClone(value)
        : JSON.parse(JSON.stringify(value));
    } catch {
      return value;
    }
  }

  function normalizeArray(value) {
    if (Array.isArray(value)) return value;
    if (value == null || value === '') return [];
    return [value];
  }

  function text(value) {
    return value == null ? '' : String(value);
  }

  function escapeHtml(value) {
    return text(value).replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
  }

  function safeId(value, fallback = '') {
    const id = text(value).trim();
    return /^[A-Za-z0-9_.:-]+$/.test(id) ? id : fallback;
  }

  function safeRelativePath(value) {
    const raw = text(value).trim().replace(/\\/g, '/').replace(/^\/+/, '');
    if (!raw || raw.includes('://') || /^[A-Za-z]:/.test(raw)) return '';
    const parts = raw.split('/');
    if (parts.some(part => !part || part === '.' || part === '..')) return '';
    return parts.join('/');
  }

  function pathCandidates(defaultOverlayId, rawPath) {
    const raw = text(rawPath).trim().replace(/\\/g, '/');
    if (!raw) return [];

    if (raw.startsWith('/api/overlays/')) return [raw];
    if (raw.startsWith('studio_overlays/')) return [raw];

    if (raw.startsWith('overlay/')) {
      const parts = raw.split('/').filter(Boolean);
      if (parts.length < 3) return [];
      const overlayId = safeId(parts[1]);
      const rel = safeRelativePath(parts.slice(2).join('/'));
      if (!overlayId || !rel) return [];
      return [
        `/api/overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`,
        `studio_overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`
      ];
    }

    const overlayId = safeId(defaultOverlayId, 'thought_evolution');
    const rel = safeRelativePath(raw);
    if (!rel) return [];
    return [
      `/api/overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`,
      `studio_overlays/${encodeURIComponent(overlayId)}/${rel.split('/').map(encodeURIComponent).join('/')}`
    ];
  }

  async function fetchJson(defaultOverlayId, rawPath, options = {}) {
    const candidates = pathCandidates(defaultOverlayId, rawPath);
    let lastError = null;
    for (const url of candidates) {
      try {
        const response = await fetch(url, { cache: options.cache || 'no-store' });
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
        return { json: await response.json(), url };
      } catch (error) {
        lastError = error;
      }
    }
    if (options.optional) return null;
    throw new Error(`${rawPath} を読み込めませんでした${lastError ? `: ${lastError.message}` : ''}`);
  }

  function safeManagedJsonPath(value, kind = 'data') {
    let raw = text(value).trim().replace(/\\/g, '/').replace(/^\/+/, '');
    if (!raw || raw.includes('://') || /^[A-Za-z]:/.test(raw) || /[?#]/.test(raw)) return '';
    if (raw.startsWith('data/json/')) raw = raw.slice('data/json/'.length);
    else if (raw.startsWith('data/')) raw = raw.slice('data/'.length);
    if (kind === 'view') {
      if (raw.startsWith('defs/')) raw = raw.slice('defs/'.length);
    }
    const parts = raw.split('/');
    if (parts.some(part => !part || part === '.' || part === '..')) return '';
    if (!raw.toLowerCase().endsWith('.json')) return '';
    return parts.join('/');
  }

  function coreStaticPath(apiName, kind = 'data') {
    return `${kind === 'view' ? 'defs' : 'data/json'}/${apiName}`;
  }

  function coreApiUrl(apiName, kind = 'data') {
    const encoded = apiName.split('/').map(encodeURIComponent).join('/');
    return `/api/${kind === 'view' ? 'defs' : 'data'}/${encoded}`;
  }

  function createStudioDataBridge() {
    return {
      async readJson(rawPath, options = {}) {
        const kind = options.kind === 'view' ? 'view' : 'data';
        const apiName = safeManagedJsonPath(rawPath, kind);
        if (!apiName) {
          if (options.optional) return null;
          throw new Error(`${kind === 'view' ? 'ViewDef' : 'Data'}参照パスが不正です: ${rawPath}`);
        }
        const candidates = [coreApiUrl(apiName, kind), coreStaticPath(apiName, kind)];
        let lastError = null;
        for (const url of candidates) {
          try {
            const response = await fetch(url, { cache: 'no-store' });
            if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
            return { json: await response.json(), url, apiName, kind };
          } catch (error) {
            lastError = error;
          }
        }
        if (options.optional) return null;
        throw new Error(`${rawPath} をStudio DataBridgeで読み込めませんでした${lastError ? `: ${lastError.message}` : ''}`);
      },
      async writeJson(rawPath, value) {
        const apiName = safeManagedJsonPath(rawPath, 'data');
        if (!apiName) throw new Error(`Data保存パスが不正です: ${rawPath}`);
        const response = await fetch(coreApiUrl(apiName, 'data'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(value)
        });
        if (!response.ok) throw new Error(`Studio Data保存に失敗しました: ${response.status} ${response.statusText}`);
        return { apiName, result: await response.json().catch(() => ({})) };
      },
      editorUrl(resourceRef = {}) {
        const dataName = safeManagedJsonPath(resourceRef.data_file || resourceRef.data || '', 'data');
        if (!dataName) throw new Error('resource_ref.data_file がありません');
        const viewName = safeManagedJsonPath(resourceRef.view_def || resourceRef.view || '', 'view');
        const url = new URL(window.location.href);
        url.search = '';
        url.hash = '';
        url.searchParams.set('data', dataName);
        if (viewName) url.searchParams.set('view', viewName);
        const field = text(resourceRef.record_field || resourceRef.key_field || '').trim();
        const value = resourceRef.record_id ?? resourceRef.record_value;
        if (field && value != null && value !== '') {
          url.searchParams.set('focusField', field);
          url.searchParams.set('focusValue', text(value));
          url.searchParams.set('openDetail', 'true');
        }
        if (resourceRef.field_path) url.searchParams.set('focusPath', text(resourceRef.field_path));
        return url.toString();
      },
      openEditor(resourceRef = {}) {
        const url = this.editorUrl(resourceRef);
        const opened = window.open(url, '_blank');
        if (!opened) throw new Error('標準エディターを開けませんでした。ポップアップ許可を確認してください。');
        try { opened.opener = null; } catch { /* cross-origin guard */ }
        return url;
      }
    };
  }

  function normalizeRelationStatus(value) {
    const status = text(value || 'AI_PROPOSED').trim().toUpperCase();
    return status || 'AI_PROPOSED';
  }

  function relationStatusDefinitions(graphDef) {
    const configured = normalizeArray(graphDef?.relation_statuses);
    const defaults = [
      { id: 'AI_PROPOSED', label: 'AI提案', stroke: '#ffd166', dasharray: '7 4' },
      { id: 'HUMAN_APPROVED', label: '人間承認', stroke: '#2ee6d6', dasharray: '' },
      { id: 'REJECTED', label: '却下', stroke: '#ff6b7a', dasharray: '3 5' },
      { id: 'PENDING', label: '保留', stroke: '#b58cff', dasharray: '2 4' }
    ];
    return configured.length ? configured : defaults;
  }

  function relationStatusMap(graphDef) {
    return Object.fromEntries(relationStatusDefinitions(graphDef).map(item => [normalizeRelationStatus(item.id), item]));
  }

  function relationStatusDef(state, status) {
    return relationStatusMap(state.graphDef)[normalizeRelationStatus(status)] || {
      id: normalizeRelationStatus(status), label: normalizeRelationStatus(status), stroke: '#8fa7b8', dasharray: '4 4'
    };
  }

  function normalizeDifferenceCategory(value) {
    return text(value || 'UNCLASSIFIED').trim().toUpperCase() || 'UNCLASSIFIED';
  }

  function differenceCategoryDefinitions(profile) {
    const configured = normalizeArray(profile?.categories)
      .filter(item => item && item.id)
      .sort((a, b) => Number(a.sort_order || 0) - Number(b.sort_order || 0));
    const defaults = [
      { id: 'COMMON', label: 'Common', caption: '共通構造', color: '#6f8798', default_visible: false },
      { id: 'ASYMMETRY', label: 'Asymmetry', caption: '非対称', color: '#ff9e64', default_visible: true },
      { id: 'MISSING_LINK', label: 'Missing Link', caption: '欠落・未接続', color: '#ff6bb5', default_visible: true },
      { id: 'CONTRADICTION', label: 'Contradiction', caption: '矛盾候補', color: '#ff7070', default_visible: true },
      { id: 'TRANSFER_CANDIDATE', label: 'Transfer Candidate', caption: '転用候補', color: '#8be28b', default_visible: true },
      { id: 'CONCEPT_DRIFT', label: 'Concept Drift', caption: '概念ドリフト', color: '#b58cff', default_visible: true },
      { id: 'UNEXPLAINED_JUMP', label: 'Unexplained Jump', caption: '説明のない跳躍', color: '#ffd166', default_visible: true }
    ];
    return configured.length ? configured : defaults;
  }

  function differenceCategoryMap(profile) {
    return Object.fromEntries(differenceCategoryDefinitions(profile).map(item => [normalizeDifferenceCategory(item.id), item]));
  }

  function differenceCategoryDef(state, category) {
    const normalized = normalizeDifferenceCategory(category);
    return differenceCategoryMap(state.analysisProfile)[normalized] || {
      id: normalized, label: normalized, caption: normalized, color: '#8fa7b8', default_visible: true
    };
  }


  function normalizeEvolutionState(value) {
    return text(value || 'OBSERVATION').trim().toUpperCase() || 'OBSERVATION';
  }

  function evolutionStateDefinitions(profile) {
    const configured = normalizeArray(profile?.proposal_states)
      .filter(item => item && item.id)
      .sort((a, b) => Number(a.sort_order || 0) - Number(b.sort_order || 0));
    const defaults = [
      { id: 'OBSERVATION', label: '観測', color: '#8fa7b8' },
      { id: 'CANDIDATE', label: '候補', color: '#ffd166' },
      { id: 'PROVISIONAL', label: '仮採用', color: '#b58cff' },
      { id: 'APPROVED', label: '承認', color: '#2ee6d6' },
      { id: 'VALIDATED', label: '検証済み', color: '#8be28b' },
      { id: 'SUPERSEDED', label: '廃止・置換済み', color: '#ff6b7a' }
    ];
    return configured.length ? configured : defaults;
  }

  function evolutionStateDef(state, value) {
    const normalized = normalizeEvolutionState(value);
    return evolutionStateDefinitions(state.evolutionProfile).find(item => normalizeEvolutionState(item.id) === normalized)
      || { id: normalized, label: normalized, color: '#8fa7b8' };
  }

  function evolutionTypeDefinitions(profile) {
    const configured = normalizeArray(profile?.proposal_types).filter(item => item && item.id);
    const defaults = [
      { id: 'decision_axis_add', label: '判断軸追加', color: '#70a7ff' },
      { id: 'constraint_add', label: '制約追加', color: '#ff7070' },
      { id: 'applicability_change', label: '適用条件変更', color: '#ff9e64' },
      { id: 'relation_change', label: '関係変更', color: '#2ee6d6' },
      { id: 'thought_class_split', label: '思考クラス分離', color: '#ff6bb5' },
      { id: 'baseline_terrain_candidate', label: '基準地形候補', color: '#ffffff' }
    ];
    return configured.length ? configured : defaults;
  }

  function evolutionTypeDef(state, value) {
    return evolutionTypeDefinitions(state.evolutionProfile).find(item => item.id === value)
      || { id: value || 'unknown', label: value || 'unknown', color: '#8fa7b8' };
  }

  function evolutionProposalFromRecord(record, index = 0) {
    return {
      ...clone(record),
      proposal_id: record.proposal_id || record.id || `evolution_proposal_${index + 1}`,
      state: normalizeEvolutionState(record.state),
      node_ids: normalizeArray(record.node_ids),
      source_observation_ids: normalizeArray(record.source_observation_ids),
      evidence_refs: normalizeArray(record.evidence_refs),
      counterexamples: normalizeArray(record.counterexamples),
      proposed_definition: clone(record.proposed_definition || {}),
      source_definition_ref: clone(record.source_definition_ref || {}),
      approval: clone(record.approval || {}),
      next_version: clone(record.next_version || { status: 'NOT_GENERATED' }),
      version_history: normalizeArray(record.version_history),
      _proposal_record: record
    };
  }

  function evolutionEvidenceRecords(state) {
    const records = normalizeArray(state.evolutionObservationData?.observations).map((item, index) => ({
      evidence_id: item.observation_id || `observation_${index + 1}`,
      candidate_keys: normalizeArray(item.candidate_keys),
      source_type: item.source_type || 'Observation',
      source_id: item.source_id || '',
      human_approved: Boolean(item.human_approved),
      outcome: text(item.outcome).trim().toUpperCase(),
      reason: item.reason || '',
      applicability_scope: item.applicability_scope || '',
      evidence_refs: normalizeArray(item.evidence_refs),
      observed_at: item.observed_at || '',
      raw: item
    }));
    normalizeArray(state.relationData?.relations).forEach((item, index) => {
      const keys = normalizeArray(item.evolution_candidate_keys);
      if (!keys.length) return;
      records.push({
        evidence_id: `relation:${item.relation_id || index + 1}`,
        candidate_keys: keys,
        source_type: 'RelationApproval',
        source_id: item.relation_id || '',
        human_approved: normalizeRelationStatus(item.status) === 'HUMAN_APPROVED',
        outcome: normalizeRelationStatus(item.status) === 'HUMAN_APPROVED' ? 'APPROVED' : normalizeRelationStatus(item.status),
        reason: item.approval?.comment || item.reason || '',
        applicability_scope: 'Relation Approval',
        evidence_refs: normalizeArray(item.evidence_refs),
        observed_at: item.approval?.decided_at || item.proposed_at || '',
        raw: item
      });
    });
    normalizeArray(state.differenceResults).forEach((item, index) => {
      const source = item._result_record || item;
      const keys = normalizeArray(source.evolution_candidate_keys);
      if (!keys.length) return;
      const decision = normalizeRelationStatus(source.approval?.decision || source.status);
      records.push({
        evidence_id: `difference:${source.result_id || index + 1}`,
        candidate_keys: keys,
        source_type: 'Difference',
        source_id: source.result_id || '',
        human_approved: decision === 'HUMAN_APPROVED',
        outcome: decision,
        reason: source.approval?.comment || source.summary || '',
        applicability_scope: 'Thought Difference Radar',
        evidence_refs: normalizeArray(source.evidence_refs),
        observed_at: source.approval?.decided_at || source.generated_at || '',
        raw: source
      });
    });
    return records;
  }

  function positiveEvolutionOutcome(value) {
    return ['SUCCESS', 'PASS', 'APPROVED', 'VALIDATED', 'POSITIVE', 'HUMAN_APPROVED'].includes(text(value).trim().toUpperCase());
  }

  function negativeEvolutionOutcome(value) {
    return ['NEGATIVE', 'FAIL', 'REJECTED', 'COUNTEREXAMPLE'].includes(text(value).trim().toUpperCase());
  }

  function evaluateEvolutionSeed(state, seed, evidence) {
    const policy = state.evolutionProfile?.promotion_policy || {};
    const supporting = evidence.filter(item => normalizeArray(item.candidate_keys).includes(seed.candidate_key));
    const positive = supporting.filter(item => positiveEvolutionOutcome(item.outcome));
    const counterexamples = supporting.filter(item => negativeEvolutionOutcome(item.outcome));
    const humanApproved = supporting.filter(item => item.human_approved);
    const reasoned = supporting.filter(item => text(item.reason).trim());
    const required = {
      observations: Number(seed.minimum_observations ?? policy.minimum_observations ?? 2),
      positive: Number(seed.minimum_positive_outcomes ?? policy.minimum_positive_outcomes ?? 1),
      humanApproved: Number(seed.minimum_human_approved_evidence ?? policy.minimum_human_approved_evidence ?? 1),
      reasoned: Number(seed.minimum_reasoned_evidence ?? policy.minimum_reasoned_evidence ?? 1)
    };
    const scopeOk = policy.require_applicability_scope === false || Boolean(text(seed.applicability_scope).trim());
    const eligible = supporting.length >= required.observations
      && positive.length >= required.positive
      && humanApproved.length >= required.humanApproved
      && reasoned.length >= required.reasoned
      && scopeOk;
    return { supporting, positive, counterexamples, humanApproved, reasoned, required, scopeOk, eligible };
  }

  function syncEvolutionRecord(proposal) {
    const record = proposal?._proposal_record;
    if (!record) return;
    for (const key of ['proposal_id','candidate_key','proposal_type','title','summary','state','confidence','applicability_scope','source_version','target_version','supporting_count','positive_outcome_count','human_approved_evidence_count','reasoned_evidence_count','counterexample_count']) record[key] = clone(proposal[key]);
    record.node_ids = normalizeArray(proposal.node_ids);
    record.source_observation_ids = normalizeArray(proposal.source_observation_ids);
    record.evidence_refs = normalizeArray(proposal.evidence_refs);
    record.counterexamples = normalizeArray(proposal.counterexamples);
    record.proposed_definition = clone(proposal.proposed_definition || {});
    record.source_definition_ref = clone(proposal.source_definition_ref || {});
    record.generation_result = clone(proposal.generation_result || {});
    record.approval = clone(proposal.approval || {});
    record.next_version = clone(proposal.next_version || {});
    record.version_history = normalizeArray(proposal.version_history);
  }

  function generateEvolutionProposals(state) {
    if (!state.evolutionProfile || !state.evolutionObservationData || !state.evolutionProposalData) throw new Error('Evolution Engine用Dataがありません');
    const now = new Date().toISOString();
    const evidence = evolutionEvidenceRecords(state);
    const existing = new Map(normalizeArray(state.evolutionProposals).map(item => [item.candidate_key, item]));
    const generated = normalizeArray(state.evolutionObservationData.candidate_seeds).map((seed, index) => {
      const evaluation = evaluateEvolutionSeed(state, seed, evidence);
      let proposal = existing.get(seed.candidate_key);
      if (!proposal) {
        const record = { proposal_id: `evolution_${state.graphData?.graph_id || 'graph'}_${index + 1}`, candidate_key: seed.candidate_key };
        state.evolutionProposalData.proposals = normalizeArray(state.evolutionProposalData.proposals);
        state.evolutionProposalData.proposals.push(record);
        proposal = evolutionProposalFromRecord(record, index);
      }
      const preserved = ['PROVISIONAL','APPROVED','VALIDATED','SUPERSEDED'].includes(normalizeEvolutionState(proposal.state));
      const previousState = normalizeEvolutionState(proposal.state);
      proposal.proposal_type = seed.proposal_type || proposal.proposal_type || 'decision_axis_add';
      proposal.title = seed.title || proposal.title || seed.candidate_key;
      proposal.summary = seed.summary || proposal.summary || '';
      proposal.applicability_scope = seed.applicability_scope || proposal.applicability_scope || '';
      proposal.node_ids = normalizeArray(seed.node_ids).length ? normalizeArray(seed.node_ids) : normalizeArray(proposal.node_ids);
      proposal.source_definition_ref = clone(seed.source_definition_ref || proposal.source_definition_ref || {});
      proposal.source_version = seed.source_version || seed.source_definition_ref?.version || proposal.source_version || '';
      proposal.target_version = seed.target_version || proposal.target_version || 'next';
      proposal.proposed_definition = clone(seed.proposed_definition || proposal.proposed_definition || {});
      proposal.source_observation_ids = evaluation.supporting.map(item => item.evidence_id);
      proposal.evidence_refs = [...new Set(evaluation.supporting.flatMap(item => normalizeArray(item.evidence_refs)).filter(Boolean))];
      proposal.supporting_count = evaluation.supporting.length;
      proposal.positive_outcome_count = evaluation.positive.length;
      proposal.human_approved_evidence_count = evaluation.humanApproved.length;
      proposal.reasoned_evidence_count = evaluation.reasoned.length;
      proposal.counterexample_count = evaluation.counterexamples.length;
      proposal.counterexamples = evaluation.counterexamples.map(item => ({ evidence_id: item.evidence_id, source_type: item.source_type, reason: item.reason }));
      proposal.confidence = evaluation.eligible ? (evaluation.counterexamples.length ? '中' : '高') : '低';
      proposal.generation_result = { eligible: evaluation.eligible, required: evaluation.required, scope_ok: evaluation.scopeOk, evaluated_at: now };
      if (!preserved) proposal.state = evaluation.eligible ? 'CANDIDATE' : 'OBSERVATION';
      proposal.approval = clone(proposal.approval || { decision: 'UNDECIDED', decided_by: '', decided_at: '', comment: '' });
      proposal.next_version = clone(proposal.next_version || { status: 'NOT_GENERATED', version_snapshot_id: '', generated_at: '' });
      proposal.version_history = normalizeArray(proposal.version_history);
      if (previousState !== proposal.state) proposal.version_history.push({ history_id: `${proposal.proposal_id}_evaluated_${Date.now()}`, at: now, change_type: 'engine_re_evaluation', before: previousState, after: proposal.state, reason: 'Evolution Engine Profileによる再評価' });
      syncEvolutionRecord(proposal);
      return proposal;
    });
    state.evolutionProposals = generated;
    state.evolutionProposalById = Object.fromEntries(generated.map(item => [item.proposal_id, item]));
    state.evolutionProposalData.updated_at = now;
    setEvolutionDirty(state, true);
    renderEvolution(state);
    toast(state, `Evolution Proposalを再評価しました: ${generated.length}件`);
  }

  async function saveEvolutionData(state) {
    if (!state.evolutionProposalData || !state.currentRow?.evolution_proposal_data_file) throw new Error('Evolution Proposal保存先がありません');
    state.evolutionProposals.forEach(syncEvolutionRecord);
    state.evolutionProposalData.updated_at = new Date().toISOString();
    state.evolutionProposalData.proposals = state.evolutionProposals.map(item => item._proposal_record || item);
    const tasks = [state.dataBridge.writeJson(state.currentRow.evolution_proposal_data_file, state.evolutionProposalData)];
    if (state.evolutionVersionData && state.currentRow?.evolution_version_data_file) {
      state.evolutionVersionData.updated_at = new Date().toISOString();
      tasks.push(state.dataBridge.writeJson(state.currentRow.evolution_version_data_file, state.evolutionVersionData));
    }
    await Promise.all(tasks);
    setEvolutionDirty(state, false);
    toast(state, 'Evolution Proposal / Version Snapshotを保存しました');
  }

  async function applyEvolutionDecision(state, proposal, nextState, comment = '') {
    const now = new Date().toISOString();
    const previous = normalizeEvolutionState(proposal.state);
    proposal.state = normalizeEvolutionState(nextState);
    proposal.approval = {
      ...(proposal.approval || {}), decision: proposal.state,
      decided_by: state.evolutionProposalData?.owner || 'Human', decided_at: now, comment: comment || proposal.approval?.comment || ''
    };
    proposal.version_history = normalizeArray(proposal.version_history);
    proposal.version_history.push({ history_id: `${proposal.proposal_id}_${Date.now()}`, at: now, change_type: 'human_evolution_decision', before: previous, after: proposal.state, reason: proposal.approval.comment || 'Thought Evolution Studio Evolution Approval' });
    syncEvolutionRecord(proposal);
    setEvolutionDirty(state, true);
    await saveEvolutionData(state);
    renderEvolution(state);
  }

  async function generateNextVersionSnapshot(state, proposal) {
    if (!['APPROVED','VALIDATED'].includes(normalizeEvolutionState(proposal.state))) throw new Error('次版生成にはAPPROVEDまたはVALIDATEDが必要です');
    if (!state.evolutionVersionData || !state.currentRow?.evolution_version_data_file) throw new Error('Version Snapshot保存先がありません');
    const now = new Date().toISOString();
    state.evolutionVersionData.snapshots = normalizeArray(state.evolutionVersionData.snapshots);
    const snapshotId = proposal.next_version?.version_snapshot_id || `${proposal.proposal_id}_${text(proposal.target_version || 'next').replace(/[^A-Za-z0-9_.-]/g, '_')}`;
    let snapshot = state.evolutionVersionData.snapshots.find(item => item.version_snapshot_id === snapshotId);
    if (!snapshot) {
      snapshot = { version_snapshot_id: snapshotId, proposal_id: proposal.proposal_id };
      state.evolutionVersionData.snapshots.push(snapshot);
    }
    snapshot.source_definition_ref = clone(proposal.source_definition_ref || {});
    snapshot.source_version = proposal.source_version || proposal.source_definition_ref?.version || '';
    snapshot.target_version = proposal.target_version || 'next';
    snapshot.status = 'GENERATED_FROM_HUMAN_APPROVED_PROPOSAL';
    snapshot.generated_at = now;
    snapshot.generated_by = 'Thought Evolution Studio v0.4';
    snapshot.definition_snapshot = { ...clone(proposal.proposed_definition || {}), version: proposal.target_version || proposal.proposed_definition?.version || 'next' };
    snapshot.provenance = {
      proposal_state: proposal.state,
      approval: clone(proposal.approval || {}),
      source_observation_ids: normalizeArray(proposal.source_observation_ids),
      evidence_refs: normalizeArray(proposal.evidence_refs),
      counterexamples: normalizeArray(proposal.counterexamples),
      mutation_policy: 'SOURCE_DEFINITION_NOT_MUTATED'
    };
    proposal.next_version = { status: 'GENERATED', version_snapshot_id: snapshotId, generated_at: now, target_version: snapshot.target_version };
    proposal.version_history = normalizeArray(proposal.version_history);
    proposal.version_history.push({ history_id: `${proposal.proposal_id}_snapshot_${Date.now()}`, at: now, change_type: 'next_version_snapshot_generated', before: '', after: snapshotId, reason: '人間承認済みProposalから元定義を上書きせず次版Snapshotを生成' });
    syncEvolutionRecord(proposal);
    setEvolutionDirty(state, true);
    await saveEvolutionData(state);
    renderEvolution(state);
    toast(state, `次版Snapshotを生成しました: ${snapshotId}`);
  }

  function analysisResultFromRecord(record, index = 0) {
    return {
      ...clone(record),
      result_id: record.result_id || record.id || `difference_result_${index + 1}`,
      category: normalizeDifferenceCategory(record.category),
      status: normalizeRelationStatus(record.status || 'AI_PROPOSED'),
      node_ids: normalizeArray(record.node_ids),
      evidence_refs: normalizeArray(record.evidence_refs),
      relation_proposal: clone(record.relation_proposal || null),
      approval: clone(record.approval || {}),
      _result_record: record
    };
  }

  function analysisProposalEdgeFromResult(result, index = 0) {
    const proposal = result?.relation_proposal;
    if (!proposal) return null;
    const source = proposal.source_node_id || proposal.source;
    const target = proposal.target_node_id || proposal.target;
    if (!source || !target) return null;
    return {
      id: proposal.relation_id || proposal.id || `radar_relation_${index + 1}`,
      source,
      target,
      type: proposal.relation_type || proposal.type || 'related_to',
      label: proposal.label || result.title || '',
      status: normalizeRelationStatus(result.status || 'AI_PROPOSED'),
      reason: proposal.reason || result.summary || '',
      evidence_refs: normalizeArray(proposal.evidence_refs).length ? normalizeArray(proposal.evidence_refs) : normalizeArray(result.evidence_refs),
      approval: clone(result.approval || {}),
      proposed_by: result.proposed_by || 'AI',
      proposed_at: result.proposed_at || '',
      source_ref: clone(proposal.source_ref || {}),
      target_ref: clone(proposal.target_ref || {}),
      change_history: [],
      analysis_category: normalizeDifferenceCategory(result.category),
      analysis_result_id: result.result_id,
      _analysis_result: result,
      _proposal_only: true,
      _editable: false
    };
  }

  function relationEdgeFromRecord(record, index = 0) {
    return {
      id: record.relation_id || record.id || `relation_${index + 1}`,
      source: record.source_node_id || record.source_ref?.node_id || record.from_id || record.source,
      target: record.target_node_id || record.target_ref?.node_id || record.to_id || record.target,
      type: record.relation_type || record.relation || record.type || 'related_to',
      label: record.label || '',
      status: normalizeRelationStatus(record.status),
      reason: record.reason || '',
      evidence_refs: normalizeArray(record.evidence_refs),
      approval: clone(record.approval || {}),
      proposed_by: record.proposed_by || '',
      proposed_at: record.proposed_at || '',
      source_ref: clone(record.source_ref || {}),
      target_ref: clone(record.target_ref || {}),
      change_history: normalizeArray(record.change_history),
      _relation_record: record,
      _editable: true
    };
  }

  function mergeRelationEdges(graphEdges, relationData, differenceResults = []) {
    const relations = normalizeArray(relationData?.relations);
    const base = relations.length
      ? relations.map(relationEdgeFromRecord)
      : normalizeArray(graphEdges).map((edge, index) => ({
          id: edge.id || `edge_${index + 1}`,
          status: normalizeRelationStatus(edge.status || 'HUMAN_APPROVED'),
          ...clone(edge),
          _editable: false
        }));
    const existingIds = new Set(base.map(edge => edge.id));
    normalizeArray(differenceResults).forEach((result, index) => {
      const edge = analysisProposalEdgeFromResult(result, index);
      if (!edge || existingIds.has(edge.id)) return;
      base.push(edge);
      existingIds.add(edge.id);
    });
    return base;
  }

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      .tes-backdrop{position:fixed;inset:0;z-index:10080;background:rgba(2,8,14,.78);backdrop-filter:blur(4px);padding:12px;color:#e9f2f8;font-family:Inter,"Yu Gothic UI","Meiryo",sans-serif}.tes-backdrop.is-dedicated{padding:4px;background:#061018;backdrop-filter:none}
      .tes-shell{height:100%;min-height:0;display:grid;grid-template-rows:auto 1fr;background:#081018;border:1px solid #355067;border-radius:14px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.55)}
      .tes-header{display:flex;align-items:center;gap:12px;min-width:0;padding:10px 12px;background:linear-gradient(90deg,#0d1e2c,#18283b);border-bottom:1px solid #294258}
      .tes-brand{font-size:17px;font-weight:800;white-space:nowrap}.tes-brand-a{color:#2ee6d6}.tes-brand-b{color:#ff6bb5}
      .tes-graph-select{min-width:260px;max-width:460px;flex:1;background:#08131d;color:#edf7fc;border:1px solid #35536b;border-radius:7px;padding:7px 9px}
      .tes-badge{font-size:10px;border:1px solid #3d596f;border-radius:999px;padding:3px 7px;color:#bcd0dc;background:#0b1722;white-space:nowrap}
      .tes-badge.is-dirty{color:#ffe5a3;border-color:#8f6d25}.tes-header-spacer{flex:1}
      .tes-button{background:#162a3a;color:#dbeaf3;border:1px solid #35536b;border-radius:7px;padding:7px 9px;cursor:pointer;font-size:12px;white-space:nowrap}
      .tes-button:hover{border-color:#2ee6d6;color:#fff}.tes-button.is-primary{background:#163a45;border-color:#2d7d83}.tes-button.is-active{border-color:#ffd166;color:#fff3c2;background:#3a321b}.tes-button:disabled{opacity:.45;cursor:default}
      .tes-close{font-size:19px;line-height:1;width:34px;height:32px;padding:0}
      .tes-layout{min-height:0;display:grid;grid-template-columns:260px minmax(0,1fr) 360px}
      .tes-left,.tes-right{min-height:0;overflow:auto;background:#0f1b27;padding:13px}.tes-left{border-right:1px solid #294258}.tes-right{border-left:1px solid #294258}
      .tes-main{min-width:0;min-height:0;position:relative;background:radial-gradient(circle at 24% 22%,rgba(46,230,214,.06),transparent 30%),radial-gradient(circle at 76% 78%,rgba(255,107,181,.06),transparent 30%),#081018}
      .tes-section-title{font-size:12px;margin:5px 0 9px;color:#d9e7f0;text-transform:uppercase;letter-spacing:.08em}
      .tes-search{width:100%;padding:8px 9px;background:#08131d;color:#fff;border:1px solid #304a60;border-radius:7px;outline:none}
      .tes-filter-group{margin:14px 0}.tes-check{display:flex;align-items:center;gap:7px;margin:7px 0;font-size:12px;color:#c9d8e2}.tes-check input{accent-color:#2ee6d6}.tes-dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex:0 0 auto}
      .tes-presets{display:grid;gap:5px}.tes-preset{text-align:left;width:100%}.tes-help,.tes-stats{font-size:11px;color:#8fa7b8;line-height:1.62}.tes-help{border-top:1px solid #243b4d;margin-top:14px;padding-top:11px}
      .tes-svg{width:100%;height:100%;display:block;cursor:grab;touch-action:none;user-select:none}.tes-svg.is-dragging{cursor:grabbing}
      .tes-edge{fill:none;stroke-width:2;opacity:.86;pointer-events:none}.tes-edge.is-dim{opacity:.08}.tes-edge.is-active{stroke:#fff3bf!important;stroke-width:3.6;opacity:1}.tes-edge.is-rejected{opacity:.48}
      .tes-edge-hit{fill:none;stroke:transparent;stroke-width:16;pointer-events:stroke;cursor:pointer}.tes-edge-label{fill:#8ea6b7;font-size:10px;pointer-events:none;text-anchor:middle}.tes-edge-label.is-active{fill:#ffe6a0;font-weight:700}.tes-relation-dot{stroke:#081018;stroke-width:2;pointer-events:none;filter:drop-shadow(0 0 4px rgba(0,0,0,.7))}
      .tes-node{cursor:move}.tes-node .tes-shape{stroke:#dceaf2;stroke-width:1.25;filter:drop-shadow(0 2px 4px rgba(0,0,0,.58))}.tes-node text{fill:#f5fbff;font-size:11px;font-weight:700;text-anchor:middle;pointer-events:none}.tes-node .tes-node-sub{font-size:8px;fill:#a9bcc9;font-weight:500}.tes-node.is-dim{opacity:.12}.tes-node.is-active .tes-shape{stroke:#ffd166;stroke-width:3;filter:drop-shadow(0 0 8px rgba(255,209,102,.65))}.tes-node.is-neighbor .tes-shape{stroke:#fff;stroke-width:2}.tes-node.is-radar-hit .tes-shape{stroke-width:2.8;filter:drop-shadow(0 0 8px var(--tes-radar-color,#ffd166))}.tes-radar-badge{stroke:#081018;stroke-width:2;filter:drop-shadow(0 0 4px rgba(0,0,0,.75));pointer-events:none}
      .tes-zoom-controls{position:absolute;right:12px;top:12px;display:flex;gap:5px}.tes-zoom-controls .tes-button{width:35px;height:33px;padding:0;font-size:16px;background:#0c1924dd}
      .tes-canvas-status{position:absolute;left:12px;bottom:10px;max-width:72%;background:#07111add;border:1px solid #2b4255;border-radius:8px;padding:7px 9px;font-size:10px;color:#abc0ce;display:flex;gap:10px;flex-wrap:wrap}
      .tes-tabs{display:flex;gap:6px;margin-bottom:10px;position:sticky;top:-13px;background:#0f1b27;padding:13px 0 8px;z-index:3}.tes-tab.is-active{background:#20445a;border-color:#2ee6d6;color:#fff}
      .tes-card{background:#132333;border:1px solid #29445a;border-radius:10px;padding:12px;margin-bottom:10px}.tes-card h3{font-size:15px;margin:0 0 7px;line-height:1.4}.tes-meta{font-size:10px;color:#8eabba;margin-bottom:8px;display:flex;gap:6px;flex-wrap:wrap}.tes-pill{border-radius:999px;border:1px solid #3c566d;padding:2px 6px}.tes-pill.is-proposed{border-color:#9c7728;color:#ffe3a0}.tes-pill.is-approved{border-color:#2d8e87;color:#91fff3}.tes-pill.is-rejected{border-color:#9d4455;color:#ffb7c1}.tes-pill.is-pending{border-color:#775bb0;color:#d8c5ff}.tes-summary{font-size:12px;line-height:1.65;color:#d3e0e8}.tes-evidence{margin-top:9px;padding:9px;border-left:3px solid #2ee6d6;background:#0a1722;font-size:11px;line-height:1.55;color:#bcd0dc}.tes-tags{margin-top:9px;display:flex;flex-wrap:wrap;gap:5px}.tes-tag{font-size:9px;background:#1d3447;padding:3px 6px;border-radius:999px;color:#bfd1dd}.tes-empty{color:#7f97a7;font-size:12px;padding:30px 5px;text-align:center}.tes-insight{cursor:pointer;transition:.15s}.tes-insight:hover{border-color:#ff6bb5;transform:translateY(-1px)}.tes-insight-confidence{color:#ffd166;font-size:10px}.tes-hidden{display:none!important}
      .tes-form-field{display:grid;gap:5px;margin:10px 0}.tes-form-field label{font-size:10px;color:#8fa7b8;text-transform:uppercase;letter-spacing:.06em}.tes-input,.tes-textarea,.tes-select{width:100%;box-sizing:border-box;background:#08131d;color:#eef8fd;border:1px solid #35536b;border-radius:7px;padding:8px 9px;font:inherit;font-size:12px}.tes-textarea{min-height:82px;resize:vertical;line-height:1.5}.tes-input:focus,.tes-textarea:focus,.tes-select:focus{outline:none;border-color:#2ee6d6;box-shadow:0 0 0 2px rgba(46,230,214,.12)}.tes-action-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:11px}.tes-button.is-approve{background:#123c39;border-color:#2d8e87;color:#a7fff5}.tes-button.is-reject{background:#3b1d26;border-color:#9d4455;color:#ffc0ca}.tes-button.is-pending{background:#2b2242;border-color:#775bb0;color:#ddceff}.tes-resource{font-size:10px;line-height:1.5;color:#9eb5c4;word-break:break-all;background:#0a1722;padding:8px;border-radius:7px;border:1px solid #243d50}.tes-relation-readonly{font-size:10px;color:#ffd166;margin:8px 0}.tes-status-legend{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 2px;font-size:10px;color:#a9bdca}.tes-status-legend span{display:inline-flex;align-items:center;gap:5px}.tes-status-line{width:18px;height:0;border-top:2px solid currentColor}.tes-status-line.is-dashed{border-top-style:dashed}.tes-header-relation-badge.is-dirty{color:#ffe5a3;border-color:#8f6d25}.tes-header-relation-badge.is-saved{color:#9efff2;border-color:#2d7d83}.tes-radar-pill{border-color:var(--tes-radar-color,#8fa7b8)!important;color:var(--tes-radar-color,#8fa7b8)!important}.tes-radar-card{border-left:4px solid var(--tes-radar-color,#8fa7b8)}.tes-radar-count{margin-left:auto;font-size:9px;color:#8fa7b8}.tes-radar-proposal-note{font-size:10px;color:#ffd166;margin:8px 0}.tes-edge.is-radar-proposal{stroke-width:2.8;filter:drop-shadow(0 0 5px rgba(255,255,255,.2))}.tes-header-evolution-badge.is-dirty{color:#ffe5a3;border-color:#8f6d25}.tes-header-evolution-badge.is-saved{color:#a9ffd2;border-color:#397a58}.tes-evolution-card{border-left:4px solid var(--tes-evolution-color,#8fa7b8)}.tes-evolution-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;margin:9px 0}.tes-evolution-metric{background:#0a1722;border:1px solid #263f52;border-radius:7px;padding:7px;text-align:center}.tes-evolution-metric b{display:block;font-size:15px;color:#fff}.tes-evolution-metric span{font-size:8px;color:#8fa7b8}.tes-definition-preview{max-height:190px;overflow:auto;white-space:pre-wrap;font-family:Consolas,monospace;font-size:10px}.tes-counterexample{border-left-color:#ff6b7a}.tes-evolution-policy{font-size:10px;color:#9eb5c4;line-height:1.55}.tes-button.is-validated{background:#183923;border-color:#4b9b62;color:#c7ffd5}.tes-button.is-superseded{background:#3b1d26;border-color:#9d4455;color:#ffc0ca}
      .tes-loading{position:absolute;inset:0;display:grid;place-items:center;background:rgba(5,12,18,.82);z-index:5;color:#cde1ec;font-size:13px}.tes-loading.tes-hidden{display:none}
      .tes-error{border-color:#8f3c4e;background:#2b1720;color:#ffd7df}.tes-toast{position:absolute;left:50%;top:14px;transform:translateX(-50%);z-index:10;background:#102432;border:1px solid #42647a;border-radius:8px;padding:8px 12px;font-size:11px;color:#d9edf7;box-shadow:0 8px 22px rgba(0,0,0,.35)}
      @media(max-width:1050px){.tes-layout{grid-template-columns:220px minmax(0,1fr) 300px}.tes-badge{display:none}.tes-graph-select{min-width:180px}}
    `;
    document.head.appendChild(style);
  }

  function createSvgElement(name, attrs = {}) {
    const el = document.createElementNS(SVG_NS, name);
    Object.entries(attrs).forEach(([key, value]) => {
      if (value != null && value !== '') el.setAttribute(key, String(value));
    });
    return el;
  }

  function typeMap(graphDef) {
    return Object.fromEntries(normalizeArray(graphDef?.node_types).map(item => [text(item?.id), item]));
  }

  function edgeTypeMap(graphDef) {
    return Object.fromEntries(normalizeArray(graphDef?.edge_types).map(item => [text(item?.id), item]));
  }

  function fieldValues(nodes, field) {
    const values = new Set();
    nodes.forEach(node => {
      normalizeArray(node?.[field]).forEach(value => {
        const s = text(value).trim();
        if (s) values.add(s);
      });
    });
    return [...values].sort((a, b) => a.localeCompare(b, 'ja'));
  }

  function graphCanvas(graphDef) {
    return {
      width: Math.max(600, Number(graphDef?.canvas?.width) || 1600),
      height: Math.max(400, Number(graphDef?.canvas?.height) || 920),
      minScale: Math.max(0.1, Number(graphDef?.canvas?.min_scale) || 0.32),
      maxScale: Math.max(1, Number(graphDef?.canvas?.max_scale) || 3.2),
      initialScale: Math.max(0.1, Number(graphDef?.canvas?.initial_scale) || 1)
    };
  }

  function defaultPosition(index, canvas) {
    const columns = Math.max(2, Math.floor(Math.sqrt(index + 5)));
    const column = index % columns;
    const row = Math.floor(index / columns);
    return {
      x: 130 + column * Math.max(150, (canvas.width - 260) / Math.max(1, columns - 1)),
      y: 130 + row * 175
    };
  }

  function normalizeLayout(graphData, rawLayout, graphDef) {
    const canvas = graphCanvas(graphDef);
    const source = rawLayout && typeof rawLayout === 'object' ? rawLayout : {};
    const positions = source.positions && typeof source.positions === 'object' ? source.positions : {};
    const nodes = normalizeArray(graphData?.nodes).map((node, index) => {
      const fromLayout = positions[node?.id] || {};
      const fallback = defaultPosition(index, canvas);
      return {
        ...clone(node),
        x: Number.isFinite(Number(fromLayout.x)) ? Number(fromLayout.x) : fallback.x,
        y: Number.isFinite(Number(fromLayout.y)) ? Number(fromLayout.y) : fallback.y
      };
    });
    const viewport = source.viewport || {};
    return {
      nodes,
      viewport: {
        x: Number.isFinite(Number(viewport.x)) ? Number(viewport.x) : 0,
        y: Number.isFinite(Number(viewport.y)) ? Number(viewport.y) : 0,
        scale: Number.isFinite(Number(viewport.scale)) ? Number(viewport.scale) : canvas.initialScale
      }
    };
  }

  function layoutPayload(state) {
    return {
      schema_version: 'thought_graph_layout_state_v0_1',
      document_type: 'thought_graph_layout_state',
      graph_id: state.graphData?.graph_id || state.currentRow?.graph_id || '',
      updated_at: new Date().toISOString(),
      viewport: {
        x: Number(state.transform.x.toFixed(3)),
        y: Number(state.transform.y.toFixed(3)),
        scale: Number(state.transform.k.toFixed(5))
      },
      positions: Object.fromEntries(state.nodes.map(node => [node.id, {
        x: Number(node.x.toFixed(3)),
        y: Number(node.y.toFixed(3))
      }]))
    };
  }

  function localStorageKey(overlayId, row) {
    return `thought-evolution-layout:${overlayId}:${row?.graph_id || row?.layout_save_file || 'default'}`;
  }

  async function loadLayout(state, row) {
    const initialResult = await fetchJson(state.overlayId, row.layout_state_file, { optional: true });
    const initial = initialResult?.json || { graph_id: row.graph_id, viewport: {}, positions: {} };
    let saved = null;
    const saveName = safeRelativePath(row.layout_save_file || `${row.graph_id || 'graph'}.json`);
    if (saveName) {
      const sidecar = await fetchJson(state.overlayId, `sidecars/${saveName}`, { optional: true });
      saved = sidecar?.json || null;
    }
    if (!saved) {
      try {
        const raw = localStorage.getItem(localStorageKey(state.overlayId, row));
        if (raw) saved = JSON.parse(raw);
      } catch { /* ignore local cache errors */ }
    }
    if (saved?.graph_id && row.graph_id && saved.graph_id !== row.graph_id) saved = null;
    return { initial, active: saved || initial, source: saved ? 'saved' : 'initial' };
  }

  async function saveLayout(state) {
    const row = state.currentRow;
    if (!row) return;
    const payload = layoutPayload(state);
    const saveName = safeRelativePath(row.layout_save_file || `${row.graph_id || 'graph'}.json`);
    if (!saveName) throw new Error('layout_save_file が不正です');
    const apiUrl = `/api/overlays/${encodeURIComponent(state.overlayId)}/sidecars/${saveName.split('/').map(encodeURIComponent).join('/')}`;
    let apiError = null;
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      localStorage.setItem(localStorageKey(state.overlayId, row), JSON.stringify(payload));
      state.dirty = false;
      updateDirtyBadge(state);
      toast(state, 'レイアウトをOverlay sidecarへ保存しました');
      return;
    } catch (error) {
      apiError = error;
    }
    try {
      localStorage.setItem(localStorageKey(state.overlayId, row), JSON.stringify(payload));
      state.dirty = false;
      updateDirtyBadge(state);
      toast(state, `API保存不可のためブラウザへ保存しました${apiError ? ` (${apiError.message})` : ''}`);
    } catch (error) {
      throw new Error(`レイアウト保存に失敗しました: ${error.message}`);
    }
  }

  function updateDirtyBadge(state) {
    const badge = state.root?.querySelector('[data-role="dirty-badge"]');
    if (!badge) return;
    badge.textContent = state.dirty ? '● レイアウト未保存' : 'レイアウト保存済み';
    badge.classList.toggle('is-dirty', state.dirty);
  }

  function setDirty(state, value = true) {
    state.dirty = Boolean(value);
    updateDirtyBadge(state);
  }

  function updateRelationDirtyBadge(state) {
    const badge = state.root?.querySelector('[data-role="relation-dirty-badge"]');
    const saveButton = state.root?.querySelector('[data-action="save-relations"]');
    if (!badge) return;
    const editable = Boolean(state.relationData && state.currentRow?.relation_data_file);
    badge.classList.toggle('tes-hidden', !editable);
    if (saveButton) saveButton.classList.toggle('tes-hidden', !editable);
    if (!editable) return;
    badge.textContent = state.relationDirty ? '● Relation未保存' : 'Relation保存済み';
    badge.classList.toggle('is-dirty', state.relationDirty);
    badge.classList.toggle('is-saved', !state.relationDirty);
  }

  function setRelationDirty(state, value = true) {
    state.relationDirty = Boolean(value);
    updateRelationDirtyBadge(state);
  }


  function updateEvolutionDirtyBadge(state) {
    const badge = state.root?.querySelector('[data-role="evolution-dirty-badge"]');
    const saveButton = state.root?.querySelector('[data-action="save-evolution"]');
    if (!badge) return;
    const enabled = Boolean(state.evolutionProposalData && state.currentRow?.evolution_proposal_data_file);
    badge.classList.toggle('tes-hidden', !enabled);
    if (saveButton) saveButton.classList.toggle('tes-hidden', !enabled);
    if (!enabled) return;
    badge.textContent = state.evolutionDirty ? '● Evolution未保存' : 'Evolution保存済み';
    badge.classList.toggle('is-dirty', state.evolutionDirty);
    badge.classList.toggle('is-saved', !state.evolutionDirty);
  }

  function setEvolutionDirty(state, value = true) {
    state.evolutionDirty = Boolean(value);
    updateEvolutionDirtyBadge(state);
  }

  function syncRelationRecordFromEdge(edge) {
    const record = edge?._relation_record;
    if (!record) return;
    record.relation_id = edge.id;
    record.source_node_id = edge.source;
    record.target_node_id = edge.target;
    record.relation_type = edge.type;
    record.label = edge.label || '';
    record.status = normalizeRelationStatus(edge.status);
    record.reason = edge.reason || '';
    record.evidence_refs = normalizeArray(edge.evidence_refs);
    record.approval = clone(edge.approval || {});
    record.proposed_by = edge.proposed_by || record.proposed_by || '';
    record.proposed_at = edge.proposed_at || record.proposed_at || '';
    record.source_ref = clone(edge.source_ref || record.source_ref || {});
    record.target_ref = clone(edge.target_ref || record.target_ref || {});
    record.change_history = normalizeArray(edge.change_history || record.change_history);
  }

  async function saveRelations(state) {
    if (!state.relationData || !state.currentRow?.relation_data_file) {
      throw new Error('このグラフには編集可能なRelationDataがありません');
    }
    state.edges.forEach(syncRelationRecordFromEdge);
    state.relationData.updated_at = new Date().toISOString();
    state.relationData.relations = state.edges.filter(edge => edge._relation_record).map(edge => edge._relation_record);
    await state.dataBridge.writeJson(state.currentRow.relation_data_file, state.relationData);
    setRelationDirty(state, false);
    toast(state, 'RelationDataを本体Data JSONへ保存しました');
  }

  function toast(state, message, kind = 'info') {
    const main = state.root?.querySelector('.tes-main');
    if (!main) return;
    main.querySelector('.tes-toast')?.remove();
    const el = document.createElement('div');
    el.className = `tes-toast${kind === 'error' ? ' tes-error' : ''}`;
    el.textContent = message;
    main.appendChild(el);
    window.setTimeout(() => el.remove(), kind === 'error' ? 5200 : 2600);
  }

  function createDialog(state) {
    document.getElementById(DIALOG_ID)?.remove();
    const root = document.createElement('div');
    root.id = DIALOG_ID;
    root.className = 'tes-backdrop';
    root.innerHTML = `
      <div class="tes-shell" role="dialog" aria-modal="true" aria-label="Thought Evolution Studio">
        <header class="tes-header">
          <div class="tes-brand"><span class="tes-brand-a">Thought Evolution</span> <span class="tes-brand-b">Studio</span></div>
          <select class="tes-graph-select" data-role="graph-select" aria-label="グラフ選択"></select>
          <span class="tes-badge">v0.4 Evolution Engine</span>
          <span class="tes-badge">外部ライブラリなし</span>
          <span class="tes-badge" data-role="dirty-badge">レイアウト保存済み</span>
          <span class="tes-badge tes-header-relation-badge is-saved" data-role="relation-dirty-badge">Relation保存済み</span>
          <span class="tes-badge tes-header-evolution-badge is-saved" data-role="evolution-dirty-badge">Evolution保存済み</span>
          <div class="tes-header-spacer"></div>
          <button class="tes-button" data-action="reload">再読込</button>
          <button class="tes-button" data-action="reset-layout">初期配置</button>
          <button class="tes-button" data-action="save-relations">Relation保存</button>
          <button class="tes-button" data-action="save-evolution">Evolution保存</button>
          <button class="tes-button is-primary" data-action="save-layout">配置保存</button>
          <button class="tes-button tes-close" data-action="close" aria-label="閉じる">×</button>
        </header>
        <div class="tes-layout">
          <aside class="tes-left">
            <div class="tes-section-title">Search</div>
            <input class="tes-search" data-role="search" type="text" placeholder="ノード・タグを検索">
            <div data-role="filters"></div>
            <div data-role="relation-status-filter"></div>
            <div data-role="difference-filter"></div>
            <div class="tes-filter-group">
              <div class="tes-section-title">Preset Path</div>
              <div class="tes-presets" data-role="presets"></div>
            </div>
            <div class="tes-stats" data-role="stats"></div>
            <div class="tes-help" data-role="help">ノードをドラッグ。背景ドラッグで移動。ホイールでカーソル位置を中心に拡大縮小。<br><br>配置保存はOverlay sidecarへ保存します。Difference RadarはAI提案を発光し、Evolution Engineは判断履歴をProposalへ蒸留します。Proposalは人間承認後にだけ次版Snapshotを生成します。</div>
          </aside>
          <main class="tes-main">
            <svg class="tes-svg" data-role="svg" preserveAspectRatio="xMidYMid meet">
              <defs>
                <marker id="tes-arrow-v01" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><polygon points="0 0, 8 3.5, 0 7" fill="#647f91"></polygon></marker>
                <marker id="tes-arrow-active-v01" markerWidth="8" markerHeight="8" refX="7" refY="3.5" orient="auto"><polygon points="0 0, 8 3.5, 0 7" fill="#ffd166"></polygon></marker>
              </defs>
              <g data-role="viewport"><g data-role="edges"></g><g data-role="edge-labels"></g><g data-role="nodes"></g></g>
            </svg>
            <div class="tes-zoom-controls">
              <button class="tes-button" data-action="zoom-in" title="拡大">＋</button>
              <button class="tes-button" data-action="zoom-out" title="縮小">−</button>
              <button class="tes-button" data-action="fit" title="全体表示">□</button>
            </div>
            <div class="tes-canvas-status" data-role="legend"></div>
            <div class="tes-loading" data-role="loading">GraphDef / GraphData / LayoutState を読み込み中...</div>
          </main>
          <section class="tes-right">
            <div class="tes-tabs"><button class="tes-button tes-tab is-active" data-tab="detail">Detail</button><button class="tes-button tes-tab" data-tab="insights">Insights / Radar</button><button class="tes-button tes-tab" data-tab="evolution">Evolution</button></div>
            <div data-panel="detail"></div>
            <div class="tes-hidden" data-panel="insights"></div>
            <div class="tes-hidden" data-panel="evolution"></div>
          </section>
        </div>
      </div>`;
    if (state.dedicatedWindow) root.classList.add('is-dedicated');
    document.body.appendChild(root);
    state.root = root;
    state.svg = root.querySelector('[data-role="svg"]');
    state.viewport = root.querySelector('[data-role="viewport"]');
    state.edgeGroup = root.querySelector('[data-role="edges"]');
    state.edgeLabelGroup = root.querySelector('[data-role="edge-labels"]');
    state.nodeGroup = root.querySelector('[data-role="nodes"]');
    populateGraphSelect(state);
    bindShellEvents(state);
    updateDirtyBadge(state);
    updateRelationDirtyBadge(state);
    updateEvolutionDirtyBadge(state);
    return root;
  }

  function populateGraphSelect(state) {
    const select = state.root.querySelector('[data-role="graph-select"]');
    select.innerHTML = state.catalogRows.map((row, index) =>
      `<option value="${index}">${escapeHtml(row.title || row.graph_id || `Graph ${index + 1}`)}</option>`
    ).join('');
    const currentIndex = Math.max(0, state.catalogRows.indexOf(state.currentRow));
    select.value = String(currentIndex);
  }

  function showLoading(state, message = '') {
    const loading = state.root?.querySelector('[data-role="loading"]');
    if (!loading) return;
    loading.textContent = message || '読み込み中...';
    loading.classList.remove('tes-hidden');
  }

  function hideLoading(state) {
    state.root?.querySelector('[data-role="loading"]')?.classList.add('tes-hidden');
  }

  function showLoadError(state, error) {
    const loading = state.root?.querySelector('[data-role="loading"]');
    if (!loading) return;
    loading.innerHTML = `<div class="tes-card tes-error"><h3>グラフ読込エラー</h3><div class="tes-summary">${escapeHtml(error?.message || error)}</div></div>`;
    loading.classList.remove('tes-hidden');
  }

  async function loadGraph(state, row, options = {}) {
    if (!row) throw new Error('グラフ定義行がありません');
    showLoading(state, `${row.title || row.graph_id || 'Graph'} を読み込み中...`);
    state.currentRow = row;
    state.selected = null;
    state.highlightNodes = null;
    state.search = '';
    state.activePreset = 'all';
    state.root.querySelector('[data-role="search"]').value = '';
    try {
      const relationPromise = row.relation_data_file
        ? state.dataBridge.readJson(row.relation_data_file, { optional: false })
        : Promise.resolve(null);
      const analysisProfilePromise = row.analysis_profile_file
        ? state.dataBridge.readJson(row.analysis_profile_file, { optional: false })
        : Promise.resolve(null);
      const differenceResultPromise = row.difference_result_data_file
        ? state.dataBridge.readJson(row.difference_result_data_file, { optional: false })
        : Promise.resolve(null);
      const evolutionProfilePromise = row.evolution_profile_file
        ? state.dataBridge.readJson(row.evolution_profile_file, { optional: false })
        : Promise.resolve(null);
      const evolutionObservationPromise = row.evolution_observation_data_file
        ? state.dataBridge.readJson(row.evolution_observation_data_file, { optional: false })
        : Promise.resolve(null);
      const evolutionProposalPromise = row.evolution_proposal_data_file
        ? state.dataBridge.readJson(row.evolution_proposal_data_file, { optional: false })
        : Promise.resolve(null);
      const evolutionVersionPromise = row.evolution_version_data_file
        ? state.dataBridge.readJson(row.evolution_version_data_file, { optional: false })
        : Promise.resolve(null);
      const [defResult, dataResult, layoutResult, relationResult, analysisProfileResult, differenceResult, evolutionProfileResult, evolutionObservationResult, evolutionProposalResult, evolutionVersionResult] = await Promise.all([
        fetchJson(state.overlayId, row.graph_def_file),
        fetchJson(state.overlayId, row.graph_data_file),
        loadLayout(state, row),
        relationPromise,
        analysisProfilePromise,
        differenceResultPromise,
        evolutionProfilePromise,
        evolutionObservationPromise,
        evolutionProposalPromise,
        evolutionVersionPromise
      ]);
      state.graphDef = defResult.json;
      state.graphData = dataResult.json;
      state.relationData = relationResult?.json || null;
      state.analysisProfile = analysisProfileResult?.json || null;
      state.differenceData = differenceResult?.json || null;
      state.differenceResults = normalizeArray(state.differenceData?.results).map(analysisResultFromRecord);
      state.differenceResultById = Object.fromEntries(state.differenceResults.map(item => [item.result_id, item]));
      state.evolutionProfile = evolutionProfileResult?.json || null;
      state.evolutionObservationData = evolutionObservationResult?.json || null;
      state.evolutionProposalData = evolutionProposalResult?.json || null;
      state.evolutionVersionData = evolutionVersionResult?.json || null;
      state.evolutionProposals = normalizeArray(state.evolutionProposalData?.proposals).map(evolutionProposalFromRecord);
      state.evolutionProposalById = Object.fromEntries(state.evolutionProposals.map(item => [item.proposal_id, item]));
      state.relationSourcePath = row.relation_data_file || '';
      state.initialLayout = clone(layoutResult.initial);
      state.layoutSource = layoutResult.source;
      const normalized = normalizeLayout(state.graphData, layoutResult.active, state.graphDef);
      state.nodes = normalized.nodes;
      state.nodeById = Object.fromEntries(state.nodes.map(node => [node.id, node]));
      state.edges = mergeRelationEdges(state.graphData?.edges, state.relationData, state.differenceResults);
      state.edgeById = Object.fromEntries(state.edges.map(edge => [edge.id, edge]));
      state.transform = {
        x: normalized.viewport.x,
        y: normalized.viewport.y,
        k: normalized.viewport.scale
      };
      const canvas = graphCanvas(state.graphDef);
      state.transform.k = Math.max(canvas.minScale, Math.min(canvas.maxScale, state.transform.k));
      state.filterSelections = {};
      state.relationStatusSelection = new Set([...relationStatusDefinitions(state.graphDef).map(item => normalizeRelationStatus(item.id)), ...state.edges.map(edge => normalizeRelationStatus(edge.status))]);
      state.differenceCategorySelection = new Set(differenceCategoryDefinitions(state.analysisProfile).filter(item => item.default_visible !== false).map(item => normalizeDifferenceCategory(item.id)));
      buildFilters(state);
      buildRelationStatusFilter(state);
      buildDifferenceFilter(state);
      buildPresets(state);
      renderInsights(state);
      renderEvolution(state);
      switchTab(state, 'detail');
      renderEmptyDetail(state);
      applyTransform(state);
      renderGraph(state);
      setDirty(state, false);
      setRelationDirty(state, false);
      setEvolutionDirty(state, false);
      const select = state.root.querySelector('[data-role="graph-select"]');
      select.value = String(Math.max(0, state.catalogRows.indexOf(row)));
      hideLoading(state);
      if (!options.silent) toast(state, `読込完了: ${state.graphData.title || row.title || row.graph_id}`);
    } catch (error) {
      showLoadError(state, error);
      throw error;
    }
  }

  function buildFilters(state) {
    const wrap = state.root.querySelector('[data-role="filters"]');
    const nodeTypes = typeMap(state.graphDef);
    const usedTypes = [...new Set(state.nodes.map(node => text(node.type)).filter(Boolean))];
    state.typeSelection = new Set(usedTypes);

    const typeHtml = usedTypes.map(typeId => {
      const def = nodeTypes[typeId] || {};
      return `<label class="tes-check"><input type="checkbox" data-filter-kind="type" value="${escapeHtml(typeId)}" checked><span class="tes-dot" style="background:${escapeHtml(def.color || '#8fa7b8')}"></span>${escapeHtml(def.label || typeId)}</label>`;
    }).join('');

    const customHtml = normalizeArray(state.graphDef?.filters).map(filter => {
      const field = text(filter?.field).trim();
      if (!field) return '';
      const values = fieldValues(state.nodes, field);
      state.filterSelections[field] = new Set(values);
      return `<div class="tes-filter-group"><div class="tes-section-title">${escapeHtml(filter.caption || field)}</div>${values.map(value =>
        `<label class="tes-check"><input type="checkbox" data-filter-kind="field" data-filter-field="${escapeHtml(field)}" value="${escapeHtml(value)}" checked>${escapeHtml(value)}</label>`
      ).join('')}</div>`;
    }).join('');

    wrap.innerHTML = `<div class="tes-filter-group"><div class="tes-section-title">Node Type</div>${typeHtml}</div>${customHtml}`;
    wrap.querySelectorAll('input[type="checkbox"]').forEach(input => {
      input.addEventListener('change', () => {
        const kind = input.dataset.filterKind;
        if (kind === 'type') {
          if (input.checked) state.typeSelection.add(input.value); else state.typeSelection.delete(input.value);
        } else {
          const field = input.dataset.filterField;
          const set = state.filterSelections[field] || new Set();
          if (input.checked) set.add(input.value); else set.delete(input.value);
          state.filterSelections[field] = set;
        }
        state.selected = null;
        renderEmptyDetail(state);
        renderGraph(state);
      });
    });
  }

  function buildRelationStatusFilter(state) {
    const wrap = state.root.querySelector('[data-role="relation-status-filter"]');
    if (!wrap) return;
    const statuses = relationStatusDefinitions(state.graphDef);
    const used = new Set(state.edges.map(edge => normalizeRelationStatus(edge.status)));
    const visible = statuses.filter(item => used.has(normalizeRelationStatus(item.id)));
    if (!visible.length) {
      wrap.innerHTML = '';
      return;
    }
    wrap.innerHTML = `<div class="tes-filter-group"><div class="tes-section-title">Relation Status</div>${visible.map(item => {
      const id = normalizeRelationStatus(item.id);
      return `<label class="tes-check"><input type="checkbox" data-relation-status="${escapeHtml(id)}" checked><span class="tes-status-line${item.dasharray ? ' is-dashed' : ''}" style="color:${escapeHtml(item.stroke || '#8fa7b8')}"></span>${escapeHtml(item.label || id)}</label>`;
    }).join('')}</div>`;
    wrap.querySelectorAll('[data-relation-status]').forEach(input => {
      input.addEventListener('change', () => {
        const status = normalizeRelationStatus(input.dataset.relationStatus);
        if (input.checked) state.relationStatusSelection.add(status);
        else state.relationStatusSelection.delete(status);
        state.selected = null;
        renderEmptyDetail(state);
        renderGraph(state);
      });
    });
  }

  function buildDifferenceFilter(state) {
    const wrap = state.root.querySelector('[data-role="difference-filter"]');
    if (!wrap) return;
    const results = normalizeArray(state.differenceResults);
    const categories = differenceCategoryDefinitions(state.analysisProfile)
      .filter(item => results.some(result => normalizeDifferenceCategory(result.category) === normalizeDifferenceCategory(item.id)));
    if (!categories.length) {
      wrap.innerHTML = '';
      return;
    }
    wrap.innerHTML = `<div class="tes-filter-group"><div class="tes-section-title">Difference Radar</div>${categories.map(item => {
      const id = normalizeDifferenceCategory(item.id);
      const count = results.filter(result => normalizeDifferenceCategory(result.category) === id).length;
      const checked = state.differenceCategorySelection.has(id) ? ' checked' : '';
      return `<label class="tes-check" title="${escapeHtml(item.description || '')}"><input type="checkbox" data-difference-category="${escapeHtml(id)}"${checked}><span class="tes-dot" style="background:${escapeHtml(item.color || '#8fa7b8')}"></span>${escapeHtml(item.label || item.caption || id)}<span class="tes-radar-count">${count}</span></label>`;
    }).join('')}</div>`;
    wrap.querySelectorAll('[data-difference-category]').forEach(input => {
      input.addEventListener('change', () => {
        const category = normalizeDifferenceCategory(input.dataset.differenceCategory);
        if (input.checked) state.differenceCategorySelection.add(category);
        else state.differenceCategorySelection.delete(category);
        state.selected = null;
        state.highlightNodes = null;
        renderEmptyDetail(state);
        renderInsights(state);
        renderGraph(state);
      });
    });
  }

  function resultCategoryVisible(result, state) {
    return state.differenceCategorySelection?.has(normalizeDifferenceCategory(result?.category));
  }

  function radarResultsForNode(state, nodeId) {
    return normalizeArray(state.differenceResults).filter(result => resultCategoryVisible(result, state) && normalizeArray(result.node_ids).includes(nodeId));
  }

  function buildPresets(state) {
    const wrap = state.root.querySelector('[data-role="presets"]');
    const presets = normalizeArray(state.graphData?.presets);
    const list = presets.length ? presets : [{ id: 'all', label: '全体表示', match: { all: true } }];
    if (!list.some(item => item.id === 'all')) list.unshift({ id: 'all', label: '全体表示', match: { all: true } });
    state.presets = list;
    wrap.innerHTML = list.map(item => `<button class="tes-button tes-preset${item.id === state.activePreset ? ' is-active' : ''}" data-preset="${escapeHtml(item.id)}">${escapeHtml(item.label || item.id)}</button>`).join('');
    wrap.querySelectorAll('[data-preset]').forEach(button => {
      button.addEventListener('click', () => {
        state.activePreset = button.dataset.preset || 'all';
        state.selected = null;
        state.highlightNodes = null;
        wrap.querySelectorAll('[data-preset]').forEach(x => x.classList.toggle('is-active', x === button));
        renderEmptyDetail(state);
        renderGraph(state);
      });
    });
  }

  function matchPreset(node, state) {
    const preset = normalizeArray(state.presets).find(item => item.id === state.activePreset);
    const match = preset?.match || {};
    if (!preset || match.all === true || state.activePreset === 'all') return true;
    const checks = [];
    if (Array.isArray(match.node_ids)) checks.push(match.node_ids.includes(node.id));
    if (Array.isArray(match.clusters)) checks.push(match.clusters.includes(node.cluster));
    if (Array.isArray(match.types)) checks.push(match.types.includes(node.type));
    if (Array.isArray(match.tags_any)) checks.push(normalizeArray(node.tags).some(tag => match.tags_any.includes(tag)));
    return checks.length ? checks.some(Boolean) : true;
  }

  function nodeVisible(node, state) {
    if (!state.typeSelection?.has(text(node.type))) return false;
    for (const [field, selected] of Object.entries(state.filterSelections || {})) {
      const values = normalizeArray(node?.[field]).map(text);
      if (!values.some(value => selected.has(value))) return false;
    }
    if (!matchPreset(node, state)) return false;
    const query = text(state.search).trim().toLowerCase();
    if (!query) return true;
    const fields = normalizeArray(state.graphDef?.search_fields);
    const haystack = fields.flatMap(field => normalizeArray(node?.[field])).map(text).join(' ').toLowerCase();
    return haystack.includes(query);
  }

  function nodeRadius(node, state) {
    const def = typeMap(state.graphDef)[node.type] || {};
    return Math.max(18, Number(def.radius) || 27);
  }

  function edgeBoundaryRadius(node, state) {
    const def = typeMap(state.graphDef)[node.type] || {};
    const radius = nodeRadius(node, state);
    return def.shape === 'rounded_rect' ? radius * 1.38 : radius * 1.08;
  }

  function shapeElement(node, state) {
    const def = typeMap(state.graphDef)[node.type] || {};
    const radius = nodeRadius(node, state);
    const shape = text(def.shape || 'circle');
    const common = { class: 'tes-shape', fill: def.color || '#7790a2' };
    if (shape === 'rounded_rect') {
      return createSvgElement('rect', { ...common, x: -radius * 1.38, y: -radius * .82, width: radius * 2.76, height: radius * 1.64, rx: Math.max(8, radius * .34) });
    }
    if (shape === 'diamond') {
      return createSvgElement('polygon', { ...common, points: `0,${-radius} ${radius * 1.12},0 0,${radius} ${-radius * 1.12},0` });
    }
    if (shape === 'hexagon') {
      const r = radius * 1.06;
      const points = [0,1,2,3,4,5].map(i => {
        const angle = Math.PI / 3 * i - Math.PI / 2;
        return `${Math.cos(angle) * r},${Math.sin(angle) * r}`;
      }).join(' ');
      return createSvgElement('polygon', { ...common, points });
    }
    return createSvgElement('circle', { ...common, r: radius });
  }

  function wrapLabel(value, maxChars = 10) {
    const s = text(value);
    if (s.length <= maxChars) return [s];
    const result = [];
    for (let i = 0; i < s.length; i += maxChars) result.push(s.slice(i, i + maxChars));
    return result.slice(0, 3);
  }

  function selectionContext(state) {
    const selected = state.selected;
    const activeNodes = new Set();
    const activeEdges = new Set();
    if (!selected) return { activeNodes, activeEdges };
    if (selected.kind === 'node') {
      activeNodes.add(selected.id);
      state.edges.forEach(edge => {
        if (edge.source === selected.id || edge.target === selected.id) {
          activeEdges.add(edge.id);
          activeNodes.add(edge.source);
          activeNodes.add(edge.target);
        }
      });
    } else if (selected.kind === 'edge') {
      const edge = state.edgeById[selected.id];
      if (edge) {
        activeEdges.add(edge.id);
        activeNodes.add(edge.source);
        activeNodes.add(edge.target);
      }
    }
    return { activeNodes, activeEdges };
  }

  function renderGraph(state) {
    if (!state.graphDef || !state.graphData) return;
    const canvas = graphCanvas(state.graphDef);
    state.svg.setAttribute('viewBox', `0 0 ${canvas.width} ${canvas.height}`);
    state.edgeGroup.innerHTML = '';
    state.edgeLabelGroup.innerHTML = '';
    state.nodeGroup.innerHTML = '';

    const visibleNodes = state.nodes.filter(node => nodeVisible(node, state));
    const visibleIds = new Set(visibleNodes.map(node => node.id));
    const visibleEdges = state.edges.filter(edge => visibleIds.has(edge.source) && visibleIds.has(edge.target) && state.relationStatusSelection.has(normalizeRelationStatus(edge.status)) && (!edge._analysis_result || resultCategoryVisible(edge._analysis_result, state)));
    const { activeNodes, activeEdges } = selectionContext(state);
    const highlight = state.highlightNodes;
    const edgeTypes = edgeTypeMap(state.graphDef);

    visibleEdges.forEach(edge => {
      const source = state.nodeById[edge.source];
      const target = state.nodeById[edge.target];
      if (!source || !target) return;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const length = Math.hypot(dx, dy) || 1;
      const startR = edgeBoundaryRadius(source, state) + 4;
      const endR = edgeBoundaryRadius(target, state) + 10;
      const x1 = source.x + dx / length * startR;
      const y1 = source.y + dy / length * startR;
      const x2 = target.x - dx / length * endR;
      const y2 = target.y - dy / length * endR;
      const edgeDef = edgeTypes[edge.type] || {};
      const status = normalizeRelationStatus(edge.status);
      const statusDef = relationStatusDef(state, status);
      const radarDef = edge._analysis_result ? differenceCategoryDef(state, edge.analysis_category) : null;
      const isActive = activeEdges.has(edge.id);
      const isDim = Boolean(state.selected) && !isActive;
      const line = createSvgElement('line', {
        x1, y1, x2, y2,
        class: `tes-edge${isActive ? ' is-active' : ''}${isDim ? ' is-dim' : ''}${status === 'REJECTED' ? ' is-rejected' : ''}${edge._analysis_result ? ' is-radar-proposal' : ''}`,
        stroke: radarDef?.color || statusDef.stroke || edgeDef.stroke || '#526b7d',
        'stroke-dasharray': edge._analysis_result ? '8 5' : (statusDef.dasharray ?? edgeDef.dasharray ?? ''),
        'marker-end': isActive ? 'url(#tes-arrow-active-v01)' : 'url(#tes-arrow-v01)'
      });
      state.edgeGroup.appendChild(line);

      const hit = createSvgElement('line', { x1, y1, x2, y2, class: 'tes-edge-hit' });
      hit.dataset.edgeId = edge.id;
      hit.addEventListener('pointerdown', event => event.stopPropagation());
      hit.addEventListener('click', event => {
        event.stopPropagation();
        selectEdge(state, edge.id);
      });
      state.edgeGroup.appendChild(hit);

      const statusDot = createSvgElement('circle', {
        cx: (x1 + x2) / 2,
        cy: (y1 + y2) / 2,
        r: isActive ? 6 : 4.5,
        class: 'tes-relation-dot',
        fill: radarDef?.color || statusDef.stroke || '#8fa7b8'
      });
      const statusTitle = createSvgElement('title');
      statusTitle.textContent = `${edge._analysis_result ? `${radarDef?.label || edge.analysis_category} / ` : ''}${statusDef.label || status} / ${edge.label || edge.type || edge.id}`;
      statusDot.appendChild(statusTitle);
      state.edgeLabelGroup.appendChild(statusDot);

      if (isActive || state.selected?.kind === 'edge') {
        const label = createSvgElement('text', {
          x: (x1 + x2) / 2,
          y: (y1 + y2) / 2 - 7,
          class: `tes-edge-label${isActive ? ' is-active' : ''}`
        });
        label.textContent = `${edge.label || edgeDef.label || edge.type || ''} / ${edge._analysis_result ? `${radarDef?.label || edge.analysis_category} / ` : ''}${statusDef.label || status}`;
        state.edgeLabelGroup.appendChild(label);
      }
    });

    visibleNodes.forEach(node => {
      const group = createSvgElement('g', { transform: `translate(${node.x} ${node.y})`, class: 'tes-node' });
      group.dataset.nodeId = node.id;
      const selectedNode = state.selected?.kind === 'node' && state.selected.id === node.id;
      const activeNode = activeNodes.has(node.id);
      const highlighted = highlight instanceof Set ? highlight.has(node.id) : false;
      const shouldDim = (Boolean(state.selected) && !activeNode) || (highlight instanceof Set && !highlighted);
      group.classList.toggle('is-active', selectedNode || highlighted);
      group.classList.toggle('is-neighbor', !selectedNode && activeNode);
      group.classList.toggle('is-dim', shouldDim);
      const radarResults = radarResultsForNode(state, node.id);
      if (radarResults.length) {
        const primaryRadarDef = differenceCategoryDef(state, radarResults[0].category);
        group.classList.add('is-radar-hit');
        group.style.setProperty('--tes-radar-color', primaryRadarDef.color || '#ffd166');
      }
      group.appendChild(shapeElement(node, state));

      const typeDef = typeMap(state.graphDef)[node.type] || {};
      const lines = wrapLabel(node.label || node.id, Number(typeDef.label_max_chars) || 10);
      lines.forEach((lineText, index) => {
        const label = createSvgElement('text', { y: (index - (lines.length - 1) / 2) * 12 + 3 });
        label.textContent = lineText;
        group.appendChild(label);
      });
      const sub = createSvgElement('text', { class: 'tes-node-sub', y: nodeRadius(node, state) + 16 });
      sub.textContent = node.cluster || typeDef.label || node.type || '';
      group.appendChild(sub);
      radarResults.slice(0, 4).forEach((result, index) => {
        const categoryDef = differenceCategoryDef(state, result.category);
        const badge = createSvgElement('circle', {
          cx: nodeRadius(node, state) * .74 + index * 9,
          cy: -nodeRadius(node, state) * .8,
          r: 5,
          class: 'tes-radar-badge',
          fill: categoryDef.color || '#8fa7b8'
        });
        const title = createSvgElement('title');
        title.textContent = `${categoryDef.label || result.category}: ${result.title || result.result_id}`;
        badge.appendChild(title);
        group.appendChild(badge);
      });

      group.addEventListener('pointerdown', event => startNodeDrag(state, event, node));
      state.nodeGroup.appendChild(group);
    });

    renderLegendAndStats(state, visibleNodes, visibleEdges);
    applyTransform(state);
  }

  function renderLegendAndStats(state, visibleNodes, visibleEdges) {
    const typeDefs = typeMap(state.graphDef);
    const used = [...new Set(visibleNodes.map(node => node.type))];
    const nodeLegend = used.map(typeId => {
      const def = typeDefs[typeId] || {};
      return `<span><span class="tes-dot" style="background:${escapeHtml(def.color || '#8fa7b8')}"></span> ${escapeHtml(def.label || typeId)}</span>`;
    }).join('');
    const relationLegend = relationStatusDefinitions(state.graphDef)
      .filter(item => state.edges.some(edge => normalizeRelationStatus(edge.status) === normalizeRelationStatus(item.id)))
      .map(item => `<span><span class="tes-status-line${item.dasharray ? ' is-dashed' : ''}" style="color:${escapeHtml(item.stroke || '#8fa7b8')}"></span>${escapeHtml(item.label || item.id)}</span>`)
      .join('');
    state.root.querySelector('[data-role="legend"]').innerHTML = `${nodeLegend}${relationLegend}`;
    const relationSource = state.relationData ? escapeHtml(state.relationSourcePath || 'RelationData') : 'GraphData / read only';
    const radarVisible = normalizeArray(state.differenceResults).filter(result => resultCategoryVisible(result, state)).length;
    const radarSource = state.differenceData ? escapeHtml(state.currentRow?.difference_result_data_file || 'DifferenceResult') : 'なし';
    state.root.querySelector('[data-role="stats"]').innerHTML = `表示ノード：<b>${visibleNodes.length}</b> / ${state.nodes.length}<br>表示リレーション：<b>${visibleEdges.length}</b> / ${state.edges.length}<br>Radar：<b>${radarVisible}</b> / ${normalizeArray(state.differenceResults).length}<br>Evolution Proposal：<b>${normalizeArray(state.evolutionProposals).length}</b><br>Radar Data：<b>${radarSource}</b><br>Relation：<b>${relationSource}</b><br>Layout：<b>${escapeHtml(state.layoutSource || 'initial')}</b>`;
  }

  function renderEmptyDetail(state) {
    const panel = state.root.querySelector('[data-panel="detail"]');
    const empty = state.graphDef?.labels?.empty || 'グラフのノードまたはリレーションを選択してください。';
    panel.innerHTML = `<div class="tes-empty">${escapeHtml(empty)}</div>`;
  }

  function statusPillClass(status) {
    const normalized = normalizeRelationStatus(status);
    if (normalized === 'HUMAN_APPROVED') return 'is-approved';
    if (normalized === 'REJECTED') return 'is-rejected';
    if (normalized === 'PENDING') return 'is-pending';
    return 'is-proposed';
  }

  function resourceRefSummary(resourceRef = {}) {
    const parts = [resourceRef.data_file || resourceRef.data, resourceRef.view_def || resourceRef.view]
      .map(text).filter(Boolean);
    if (resourceRef.record_field && (resourceRef.record_id ?? resourceRef.record_value) != null) {
      parts.push(`${resourceRef.record_field}=${resourceRef.record_id ?? resourceRef.record_value}`);
    }
    if (resourceRef.field_path) parts.push(resourceRef.field_path);
    return parts.join('\n');
  }

  function bindOpenEditorButton(state, panel, resourceRef) {
    const button = panel.querySelector('[data-action="open-resource-editor"]');
    if (!button) return;
    button.addEventListener('click', () => {
      try {
        state.dataBridge.openEditor(resourceRef);
      } catch (error) {
        console.error(error);
        toast(state, error.message, 'error');
      }
    });
  }

  function selectNode(state, nodeId) {
    state.selected = { kind: 'node', id: nodeId };
    state.highlightNodes = null;
    const node = state.nodeById[nodeId];
    if (!node) return;
    const typeDef = typeMap(state.graphDef)[node.type] || {};
    const relations = state.edges.filter(edge => edge.source === nodeId || edge.target === nodeId);
    const relationHtml = relations.map(edge => {
      const otherId = edge.source === nodeId ? edge.target : edge.source;
      const other = state.nodeById[otherId];
      const arrow = edge.source === nodeId ? '→' : '←';
      const statusDef = relationStatusDef(state, edge.status);
      return `<button class="tes-button" data-related-edge="${escapeHtml(edge.id)}" style="width:100%;text-align:left;margin:4px 0"><b>${arrow} ${escapeHtml(other?.label || otherId)}</b><br><span style="color:${escapeHtml(statusDef.stroke || '#8fa7b8')}">${escapeHtml(edge.label || edge.type || '')} / ${escapeHtml(statusDef.label || edge.status || '')}</span></button>`;
    }).join('') || '<div class="tes-summary">なし</div>';
    const evidence = normalizeArray(node.evidence);
    const tags = normalizeArray(node.tags);
    const resourceRef = node.resource_ref || null;
    const panel = state.root.querySelector('[data-panel="detail"]');
    panel.innerHTML = `
      <div class="tes-card"><h3>${escapeHtml(node.label || node.id)}</h3>
        <div class="tes-meta"><span class="tes-pill">${escapeHtml(typeDef.label || node.type || '')}</span><span class="tes-pill">${escapeHtml(node.cluster || '')}</span><span class="tes-pill">${escapeHtml(node.source || '')}</span></div>
        <div class="tes-summary">${escapeHtml(node.summary || '')}</div>
        ${evidence.length ? `<div class="tes-evidence"><b>根拠メモ</b><br>${evidence.map(escapeHtml).join('<br>')}</div>` : ''}
        ${tags.length ? `<div class="tes-tags">${tags.map(tag => `<span class="tes-tag">${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
        ${resourceRef ? `<div class="tes-form-field"><label>Resource Ref / 本体原本</label><div class="tes-resource">${escapeHtml(resourceRefSummary(resourceRef)).replace(/\n/g, '<br>')}</div></div><div class="tes-action-row"><button class="tes-button is-primary" data-action="open-resource-editor">Studio標準エディターで開く</button></div>` : '<div class="tes-relation-readonly">このノードにはresource_refがありません。</div>'}
      </div>
      <div class="tes-card"><h3>直接リレーション</h3>${relationHtml}</div>`;
    panel.querySelectorAll('[data-related-edge]').forEach(button => {
      button.addEventListener('click', () => selectEdge(state, button.dataset.relatedEdge));
    });
    if (resourceRef) bindOpenEditorButton(state, panel, resourceRef);
    switchTab(state, 'detail');
    renderGraph(state);
  }

  function edgeEvidenceText(edge) {
    return normalizeArray(edge.evidence_refs).map(item => {
      if (typeof item === 'string') return item;
      return item?.ref || item?.path || item?.title || JSON.stringify(item);
    }).join('\n');
  }

  function updateRelationEdgeFromPanel(state, edge, panel) {
    const type = panel.querySelector('[data-relation-field="type"]')?.value;
    const label = panel.querySelector('[data-relation-field="label"]')?.value;
    const reason = panel.querySelector('[data-relation-field="reason"]')?.value;
    const evidence = panel.querySelector('[data-relation-field="evidence"]')?.value;
    if (type) edge.type = type;
    edge.label = label || '';
    edge.reason = reason || '';
    edge.evidence_refs = text(evidence).split(/\r?\n/).map(x => x.trim()).filter(Boolean);
    syncRelationRecordFromEdge(edge);
    setRelationDirty(state, true);
    renderGraph(state);
  }

  async function applyRelationDecision(state, edge, status, panel) {
    updateRelationEdgeFromPanel(state, edge, panel);
    const now = new Date().toISOString();
    const normalized = normalizeRelationStatus(status);
    const previous = normalizeRelationStatus(edge.status);
    edge.status = normalized;
    edge.approval = {
      ...(edge.approval || {}),
      decision: normalized,
      decided_by: normalized === 'AI_PROPOSED' ? '' : (state.relationData?.owner || 'Human'),
      decided_at: normalized === 'AI_PROPOSED' ? '' : now,
      comment: panel.querySelector('[data-relation-field="approval-comment"]')?.value || ''
    };
    edge.change_history = normalizeArray(edge.change_history);
    edge.change_history.push({
      history_id: `relation_${edge.id}_${Date.now()}`,
      at: now,
      change_type: 'approval_status_change',
      before: previous,
      after: normalized,
      reason: edge.approval.comment || edge.reason || 'Thought Evolution Studio Relation Approval'
    });
    syncRelationRecordFromEdge(edge);
    setRelationDirty(state, true);
    await saveRelations(state);
    selectEdge(state, edge.id);
  }

  async function saveDifferenceResults(state) {
    if (!state.differenceData || !state.currentRow?.difference_result_data_file) return;
    state.differenceData.updated_at = new Date().toISOString();
    state.differenceData.results = state.differenceResults.map(result => result._result_record || result);
    await state.dataBridge.writeJson(state.currentRow.difference_result_data_file, state.differenceData);
  }

  function relationRecordFromProposalEdge(edge) {
    return {
      relation_id: edge.id,
      source_node_id: edge.source,
      target_node_id: edge.target,
      source_ref: clone(edge.source_ref || { node_id: edge.source }),
      target_ref: clone(edge.target_ref || { node_id: edge.target }),
      relation_type: edge.type,
      label: edge.label || '',
      status: 'AI_PROPOSED',
      reason: edge.reason || '',
      evidence_refs: normalizeArray(edge.evidence_refs),
      proposed_by: edge.proposed_by || 'Thought Difference Radar',
      proposed_at: edge.proposed_at || new Date().toISOString(),
      approval: { decision: 'AI_PROPOSED', decided_by: '', decided_at: '', comment: '' },
      change_history: [{
        history_id: `relation_${edge.id}_radar_transfer_${Date.now()}`,
        at: new Date().toISOString(),
        change_type: 'difference_radar_transfer',
        before: 'DIFFERENCE_RESULT_PROPOSAL',
        after: 'RELATION_AI_PROPOSED',
        reason: `Thought Difference Radar ${edge.analysis_result_id || ''} からRelation Approvalへ送付`
      }]
    };
  }

  async function transferProposalToRelationApproval(state, edge) {
    if (!edge?._analysis_result) throw new Error('Difference RadarのRelation Proposalではありません');
    if (!state.relationData || !state.currentRow?.relation_data_file) throw new Error('このグラフには保存先RelationDataがありません');
    state.relationData.relations = normalizeArray(state.relationData.relations);
    const exists = state.relationData.relations.find(item => (item.relation_id || item.id) === edge.id);
    const record = exists || relationRecordFromProposalEdge(edge);
    if (!exists) state.relationData.relations.push(record);
    edge._relation_record = record;
    edge._editable = true;
    edge._proposal_only = false;
    edge.status = normalizeRelationStatus(record.status || 'AI_PROPOSED');
    edge.approval = clone(record.approval || {});
    const result = edge._analysis_result;
    result.transfer_status = 'TRANSFERRED_TO_RELATION_APPROVAL';
    result.transferred_relation_id = edge.id;
    result.transferred_at = new Date().toISOString();
    if (result._result_record) {
      result._result_record.transfer_status = result.transfer_status;
      result._result_record.transferred_relation_id = result.transferred_relation_id;
      result._result_record.transferred_at = result.transferred_at;
    }
    syncRelationRecordFromEdge(edge);
    setRelationDirty(state, true);
    await Promise.all([saveRelations(state), saveDifferenceResults(state)]);
    toast(state, 'Relation ProposalをRelation Approvalへ送りました');
    selectEdge(state, edge.id);
  }

  function selectEdge(state, edgeId) {
    state.selected = { kind: 'edge', id: edgeId };
    state.highlightNodes = null;
    const edge = state.edgeById[edgeId];
    if (!edge) return;
    const source = state.nodeById[edge.source];
    const target = state.nodeById[edge.target];
    const edgeDef = edgeTypeMap(state.graphDef)[edge.type] || {};
    const statusDef = relationStatusDef(state, edge.status);
    const editable = Boolean(edge._editable && state.relationData);
    const radarResult = edge._analysis_result || null;
    const radarDef = radarResult ? differenceCategoryDef(state, radarResult.category) : null;
    const typeOptions = normalizeArray(state.graphDef?.edge_types).map(item => `<option value="${escapeHtml(item.id)}"${item.id === edge.type ? ' selected' : ''}>${escapeHtml(item.label || item.id)}</option>`).join('');
    const approval = edge.approval || {};
    const panel = state.root.querySelector('[data-panel="detail"]');
    panel.innerHTML = `
      <div class="tes-card"><h3>${escapeHtml(edge.label || edgeDef.label || edge.type || edge.id)}</h3>
        <div class="tes-meta"><span class="tes-pill ${statusPillClass(edge.status)}">${escapeHtml(statusDef.label || edge.status || '')}</span>${radarResult ? `<span class="tes-pill tes-radar-pill" style="--tes-radar-color:${escapeHtml(radarDef?.color || '#8fa7b8')}">${escapeHtml(radarDef?.label || radarResult.category)}</span>` : ''}<span class="tes-pill">${escapeHtml(edge.id || '')}</span></div>
        <div class="tes-summary"><b>${escapeHtml(source?.label || edge.source)}</b><br>↓<br><b>${escapeHtml(target?.label || edge.target)}</b></div>
        ${radarResult && edge._proposal_only ? '<div class="tes-radar-proposal-note">Difference RadarのAI提案です。Relation Approvalへ送るまでは正本Relationではありません。</div>' : ''}
        ${editable ? '' : (radarResult ? '' : '<div class="tes-relation-readonly">このリレーションはGraphData由来のRead Onlyです。RelationDataを設定すると承認可能になります。</div>')}
        <div class="tes-form-field"><label>Relation Type</label><select class="tes-select" data-relation-field="type" ${editable ? '' : 'disabled'}>${typeOptions}</select></div>
        <div class="tes-form-field"><label>Label</label><input class="tes-input" data-relation-field="label" value="${escapeHtml(edge.label || '')}" ${editable ? '' : 'disabled'}></div>
        <div class="tes-form-field"><label>Reason / 接続理由</label><textarea class="tes-textarea" data-relation-field="reason" ${editable ? '' : 'disabled'}>${escapeHtml(edge.reason || edge.summary || '')}</textarea></div>
        <div class="tes-form-field"><label>Evidence Refs / 1行1件</label><textarea class="tes-textarea" data-relation-field="evidence" ${editable ? '' : 'disabled'}>${escapeHtml(edgeEvidenceText(edge))}</textarea></div>
        <div class="tes-form-field"><label>Approval Comment</label><textarea class="tes-textarea" data-relation-field="approval-comment" ${editable ? '' : 'disabled'}>${escapeHtml(approval.comment || '')}</textarea></div>
        <div class="tes-meta"><span>提案: ${escapeHtml(edge.proposed_by || '-')} ${escapeHtml(edge.proposed_at || '')}</span><span>判断: ${escapeHtml(approval.decided_by || '-')} ${escapeHtml(approval.decided_at || '')}</span></div>
        ${radarResult && edge._proposal_only ? `<div class="tes-action-row"><button class="tes-button is-primary" data-analysis-action="send-relation">Relation Approvalへ送る</button></div>` : ''}
        ${editable ? `<div class="tes-action-row"><button class="tes-button" data-relation-action="draft">下書き保存</button><button class="tes-button is-approve" data-relation-action="approve">承認</button><button class="tes-button is-pending" data-relation-action="pending">保留</button><button class="tes-button is-reject" data-relation-action="reject">却下</button></div>` : ''}
      </div>
      <div class="tes-card"><h3>接続ノード</h3>
        ${source?.resource_ref ? `<button class="tes-button" data-open-endpoint="source">接続元を標準エディターで開く</button>` : ''}
        ${target?.resource_ref ? `<button class="tes-button" data-open-endpoint="target">接続先を標準エディターで開く</button>` : ''}
      </div>`;

    panel.querySelector('[data-analysis-action="send-relation"]')?.addEventListener('click', async () => {
      try { await transferProposalToRelationApproval(state, edge); }
      catch (error) { console.error(error); toast(state, error.message, 'error'); }
    });
    if (editable) {
      panel.querySelectorAll('[data-relation-field]').forEach(control => {
        control.addEventListener('input', () => updateRelationEdgeFromPanel(state, edge, panel));
        control.addEventListener('change', () => updateRelationEdgeFromPanel(state, edge, panel));
      });
      panel.querySelector('[data-relation-action="draft"]')?.addEventListener('click', async () => {
        try { updateRelationEdgeFromPanel(state, edge, panel); await saveRelations(state); selectEdge(state, edge.id); }
        catch (error) { console.error(error); toast(state, error.message, 'error'); }
      });
      panel.querySelector('[data-relation-action="approve"]')?.addEventListener('click', async () => {
        try { await applyRelationDecision(state, edge, 'HUMAN_APPROVED', panel); }
        catch (error) { console.error(error); toast(state, error.message, 'error'); }
      });
      panel.querySelector('[data-relation-action="pending"]')?.addEventListener('click', async () => {
        try { await applyRelationDecision(state, edge, 'PENDING', panel); }
        catch (error) { console.error(error); toast(state, error.message, 'error'); }
      });
      panel.querySelector('[data-relation-action="reject"]')?.addEventListener('click', async () => {
        try { await applyRelationDecision(state, edge, 'REJECTED', panel); }
        catch (error) { console.error(error); toast(state, error.message, 'error'); }
      });
    }
    panel.querySelector('[data-open-endpoint="source"]')?.addEventListener('click', () => {
      try { state.dataBridge.openEditor(source.resource_ref); } catch (error) { toast(state, error.message, 'error'); }
    });
    panel.querySelector('[data-open-endpoint="target"]')?.addEventListener('click', () => {
      try { state.dataBridge.openEditor(target.resource_ref); } catch (error) { toast(state, error.message, 'error'); }
    });
    switchTab(state, 'detail');
    renderGraph(state);
  }

  function renderInsights(state) {
    const panel = state.root.querySelector('[data-panel="insights"]');
    const radarResults = normalizeArray(state.differenceResults).filter(result => resultCategoryVisible(result, state));
    const insights = normalizeArray(state.graphData?.insights);
    if (!radarResults.length && !insights.length) {
      panel.innerHTML = '<div class="tes-empty">Insight / Difference Radar結果は定義されていません。</div>';
      return;
    }
    const radarHtml = radarResults.length ? `
      <div class="tes-section-title">Thought Difference Radar</div>
      ${radarResults.map((item, index) => {
        const categoryDef = differenceCategoryDef(state, item.category);
        const proposal = item.relation_proposal;
        return `<div class="tes-card tes-insight tes-radar-card" style="--tes-radar-color:${escapeHtml(categoryDef.color || '#8fa7b8')}" data-radar-index="${index}">
          <div class="tes-meta"><span class="tes-pill tes-radar-pill" style="--tes-radar-color:${escapeHtml(categoryDef.color || '#8fa7b8')}">${escapeHtml(categoryDef.label || item.category)}</span><span class="tes-pill">${escapeHtml(item.result_type || '')}</span><span class="tes-pill ${statusPillClass(item.status)}">${escapeHtml(item.status || '')}</span></div>
          <div class="tes-insight-confidence">信頼度：${escapeHtml(item.confidence || '')}</div>
          <h3>${escapeHtml(item.title || item.result_id)}</h3>
          <div class="tes-summary">${escapeHtml(item.summary || '')}</div>
          ${proposal ? `<div class="tes-evidence"><b>Relation Proposal</b><br>${escapeHtml(proposal.source_node_id || '')} → ${escapeHtml(proposal.target_node_id || '')}<br>${escapeHtml(proposal.label || '')}</div>` : ''}
        </div>`;
      }).join('')}` : '';
    const insightHtml = insights.length ? `
      <div class="tes-section-title">Generated Insights</div>
      ${insights.map((item, index) => `<div class="tes-card tes-insight" data-insight-index="${index}"><div class="tes-insight-confidence">信頼度：${escapeHtml(item.confidence || '')}</div><h3>${escapeHtml(item.title || `Insight ${index + 1}`)}</h3><div class="tes-summary">${escapeHtml(item.body || '')}</div></div>`).join('')}` : '';
    panel.innerHTML = radarHtml + insightHtml;
    panel.querySelectorAll('[data-radar-index]').forEach(card => {
      card.addEventListener('click', () => {
        const item = radarResults[Number(card.dataset.radarIndex)];
        state.selected = null;
        state.highlightNodes = new Set(normalizeArray(item?.node_ids));
        const relationId = item?.relation_proposal?.relation_id || item?.relation_proposal?.id;
        if (relationId && state.edgeById[relationId]) selectEdge(state, relationId);
        else renderGraph(state);
      });
    });
    panel.querySelectorAll('[data-insight-index]').forEach(card => {
      card.addEventListener('click', () => {
        const item = insights[Number(card.dataset.insightIndex)];
        state.selected = null;
        state.highlightNodes = new Set(normalizeArray(item?.node_ids || item?.nodes));
        renderGraph(state);
      });
    });
  }


  function renderEvolution(state) {
    const panel = state.root.querySelector('[data-panel="evolution"]');
    if (!panel) return;
    if (!state.evolutionProfile || !state.evolutionProposalData) {
      panel.innerHTML = '<div class="tes-empty">このグラフにはEvolution Engine Dataが設定されていません。</div>';
      return;
    }
    const policy = state.evolutionProfile.promotion_policy || {};
    const evidence = evolutionEvidenceRecords(state);
    const snapshots = normalizeArray(state.evolutionVersionData?.snapshots);
    const proposals = normalizeArray(state.evolutionProposals);
    panel.innerHTML = `
      <div class="tes-card">
        <h3>Evolution Engine</h3>
        <div class="tes-evolution-policy">反復は候補を生みますが、正当性は生みません。最低根拠 ${escapeHtml(policy.minimum_observations ?? 2)}件 / 成功 ${escapeHtml(policy.minimum_positive_outcomes ?? 1)}件 / 人間承認根拠 ${escapeHtml(policy.minimum_human_approved_evidence ?? 1)}件 / 理由付き ${escapeHtml(policy.minimum_reasoned_evidence ?? 1)}件。自動昇格・元定義上書きは行いません。</div>
        <div class="tes-evolution-metrics"><div class="tes-evolution-metric"><b>${evidence.length}</b><span>Evidence</span></div><div class="tes-evolution-metric"><b>${proposals.length}</b><span>Proposal</span></div><div class="tes-evolution-metric"><b>${proposals.filter(x => ['APPROVED','VALIDATED'].includes(normalizeEvolutionState(x.state))).length}</b><span>Approved</span></div><div class="tes-evolution-metric"><b>${snapshots.length}</b><span>Next Version</span></div></div>
        <div class="tes-action-row"><button class="tes-button is-primary" data-evolution-global="generate">候補生成・再評価</button><button class="tes-button" data-evolution-global="save">Evolution保存</button></div>
      </div>
      ${proposals.length ? proposals.map((proposal, index) => {
        const stateDef = evolutionStateDef(state, proposal.state);
        const typeDef = evolutionTypeDef(state, proposal.proposal_type);
        const next = proposal.next_version || {};
        return `<div class="tes-card tes-evolution-card" style="--tes-evolution-color:${escapeHtml(stateDef.color || typeDef.color || '#8fa7b8')}" data-evolution-index="${index}">
          <div class="tes-meta"><span class="tes-pill" style="border-color:${escapeHtml(stateDef.color || '#8fa7b8')};color:${escapeHtml(stateDef.color || '#8fa7b8')}">${escapeHtml(stateDef.label || proposal.state)}</span><span class="tes-pill" style="border-color:${escapeHtml(typeDef.color || '#8fa7b8')};color:${escapeHtml(typeDef.color || '#8fa7b8')}">${escapeHtml(typeDef.label || proposal.proposal_type)}</span><span class="tes-pill">${escapeHtml(proposal.confidence || '')}</span></div>
          <h3>${escapeHtml(proposal.title || proposal.proposal_id)}</h3>
          <div class="tes-summary">${escapeHtml(proposal.summary || '')}</div>
          <div class="tes-evolution-metrics"><div class="tes-evolution-metric"><b>${Number(proposal.supporting_count || 0)}</b><span>根拠</span></div><div class="tes-evolution-metric"><b>${Number(proposal.positive_outcome_count || 0)}</b><span>成功</span></div><div class="tes-evolution-metric"><b>${Number(proposal.human_approved_evidence_count || 0)}</b><span>人間承認</span></div><div class="tes-evolution-metric"><b>${Number(proposal.counterexample_count || 0)}</b><span>反例</span></div></div>
          <div class="tes-evidence"><b>適用範囲</b><br>${escapeHtml(proposal.applicability_scope || '未定義')}</div>
          ${normalizeArray(proposal.counterexamples).length ? `<div class="tes-evidence tes-counterexample"><b>反例</b><br>${normalizeArray(proposal.counterexamples).map(x => escapeHtml(x.reason || x.evidence_id || '')).join('<br>')}</div>` : ''}
          <div class="tes-evidence tes-definition-preview"><b>Proposed Definition</b>\n${escapeHtml(JSON.stringify(proposal.proposed_definition || {}, null, 2))}</div>
          <div class="tes-form-field"><label>Approval Comment</label><textarea class="tes-textarea" data-evolution-comment="${escapeHtml(proposal.proposal_id)}">${escapeHtml(proposal.approval?.comment || '')}</textarea></div>
          <div class="tes-meta"><span>Source ${escapeHtml(proposal.source_version || '-')} → Target ${escapeHtml(proposal.target_version || 'next')}</span><span>Next Version: ${escapeHtml(next.status || 'NOT_GENERATED')} ${escapeHtml(next.version_snapshot_id || '')}</span></div>
          <div class="tes-action-row">
            <button class="tes-button is-pending" data-evolution-action="provisional" data-proposal-id="${escapeHtml(proposal.proposal_id)}">仮採用</button>
            <button class="tes-button is-approve" data-evolution-action="approve" data-proposal-id="${escapeHtml(proposal.proposal_id)}">承認</button>
            <button class="tes-button is-validated" data-evolution-action="validate" data-proposal-id="${escapeHtml(proposal.proposal_id)}">検証済み</button>
            <button class="tes-button" data-evolution-action="candidate" data-proposal-id="${escapeHtml(proposal.proposal_id)}">候補へ戻す</button>
            <button class="tes-button is-superseded" data-evolution-action="supersede" data-proposal-id="${escapeHtml(proposal.proposal_id)}">廃止</button>
            ${['APPROVED','VALIDATED'].includes(normalizeEvolutionState(proposal.state)) ? `<button class="tes-button is-primary" data-evolution-action="next-version" data-proposal-id="${escapeHtml(proposal.proposal_id)}">次版Snapshot生成</button>` : ''}
          </div>
        </div>`;
      }).join('') : '<div class="tes-empty">Proposalはまだありません。「候補生成・再評価」を実行してください。</div>'}`;

    panel.querySelector('[data-evolution-global="generate"]')?.addEventListener('click', () => {
      try { generateEvolutionProposals(state); } catch (error) { console.error(error); toast(state, error.message, 'error'); }
    });
    panel.querySelector('[data-evolution-global="save"]')?.addEventListener('click', async event => {
      try { event.currentTarget.disabled = true; await saveEvolutionData(state); }
      catch (error) { console.error(error); toast(state, error.message, 'error'); }
      finally { event.currentTarget.disabled = false; }
    });
    panel.querySelectorAll('[data-evolution-index]').forEach(card => card.addEventListener('click', event => {
      if (event.target.closest('button,textarea,input,select')) return;
      const proposal = proposals[Number(card.dataset.evolutionIndex)];
      state.selected = null;
      state.highlightNodes = new Set(normalizeArray(proposal?.node_ids));
      renderGraph(state);
    }));
    panel.querySelectorAll('[data-evolution-action]').forEach(button => button.addEventListener('click', async event => {
      const proposal = state.evolutionProposalById[event.currentTarget.dataset.proposalId];
      if (!proposal) return;
      const comment = panel.querySelector(`[data-evolution-comment="${CSS.escape(proposal.proposal_id)}"]`)?.value || '';
      const action = event.currentTarget.dataset.evolutionAction;
      try {
        event.currentTarget.disabled = true;
        if (action === 'next-version') await generateNextVersionSnapshot(state, proposal);
        else {
          const next = { provisional:'PROVISIONAL', approve:'APPROVED', validate:'VALIDATED', candidate:'CANDIDATE', supersede:'SUPERSEDED' }[action];
          await applyEvolutionDecision(state, proposal, next, comment);
        }
      } catch (error) { console.error(error); toast(state, error.message, 'error'); }
      finally { event.currentTarget.disabled = false; }
    }));
  }

  function switchTab(state, tab) {
    state.root.querySelectorAll('[data-tab]').forEach(button => button.classList.toggle('is-active', button.dataset.tab === tab));
    state.root.querySelector('[data-panel="detail"]').classList.toggle('tes-hidden', tab !== 'detail');
    state.root.querySelector('[data-panel="insights"]').classList.toggle('tes-hidden', tab !== 'insights');
    state.root.querySelector('[data-panel="evolution"]').classList.toggle('tes-hidden', tab !== 'evolution');
    if (tab === 'evolution') renderEvolution(state);
  }

  function svgPoint(state, clientX, clientY) {
    const point = state.svg.createSVGPoint();
    point.x = clientX;
    point.y = clientY;
    const matrix = state.svg.getScreenCTM();
    return matrix ? point.matrixTransform(matrix.inverse()) : point;
  }

  function graphPoint(state, clientX, clientY) {
    const point = svgPoint(state, clientX, clientY);
    return {
      x: (point.x - state.transform.x) / state.transform.k,
      y: (point.y - state.transform.y) / state.transform.k
    };
  }

  function applyTransform(state) {
    state.viewport?.setAttribute('transform', `translate(${state.transform.x} ${state.transform.y}) scale(${state.transform.k})`);
  }

  function zoomAt(state, factor, clientX, clientY) {
    const canvas = graphCanvas(state.graphDef);
    const cursor = svgPoint(state, clientX, clientY);
    const graphX = (cursor.x - state.transform.x) / state.transform.k;
    const graphY = (cursor.y - state.transform.y) / state.transform.k;
    const next = Math.max(canvas.minScale, Math.min(canvas.maxScale, state.transform.k * factor));
    state.transform.x = cursor.x - graphX * next;
    state.transform.y = cursor.y - graphY * next;
    state.transform.k = next;
    applyTransform(state);
    setDirty(state);
  }

  function fitGraph(state) {
    const visible = state.nodes.filter(node => nodeVisible(node, state));
    if (!visible.length) return;
    const canvas = graphCanvas(state.graphDef);
    const minX = Math.min(...visible.map(node => node.x)) - 80;
    const maxX = Math.max(...visible.map(node => node.x)) + 80;
    const minY = Math.min(...visible.map(node => node.y)) - 80;
    const maxY = Math.max(...visible.map(node => node.y)) + 80;
    const width = Math.max(100, maxX - minX);
    const height = Math.max(100, maxY - minY);
    const scale = Math.max(canvas.minScale, Math.min(canvas.maxScale, Math.min(canvas.width / width, canvas.height / height) * .9));
    state.transform.k = scale;
    state.transform.x = (canvas.width - (minX + maxX) * scale) / 2;
    state.transform.y = (canvas.height - (minY + maxY) * scale) / 2;
    applyTransform(state);
    setDirty(state);
  }

  function startNodeDrag(state, event, node) {
    event.preventDefault();
    event.stopPropagation();
    state.svg.setPointerCapture?.(event.pointerId);
    const point = graphPoint(state, event.clientX, event.clientY);
    state.drag = {
      kind: 'node', pointerId: event.pointerId, nodeId: node.id,
      offsetX: point.x - node.x, offsetY: point.y - node.y,
      startClientX: event.clientX, startClientY: event.clientY, moved: false
    };
    state.svg.classList.add('is-dragging');
  }

  function bindShellEvents(state) {
    const root = state.root;
    const closeStudio = () => {
      if ((state.dirty || state.relationDirty || state.evolutionDirty) && !window.confirm('未保存の変更があります。閉じますか？')) return;
      if (state.dedicatedWindow) {
        window.close();
        window.setTimeout(() => root.remove(), 80);
      } else root.remove();
    };
    root.querySelector('[data-action="close"]').addEventListener('click', closeStudio);
    root.querySelector('[data-role="graph-select"]').addEventListener('change', async event => {
      const row = state.catalogRows[Number(event.target.value)] || state.catalogRows[0];
      try { await loadGraph(state, row); } catch (error) { console.error(error); }
    });
    root.querySelector('[data-role="search"]').addEventListener('input', event => {
      state.search = event.target.value || '';
      state.selected = null;
      state.highlightNodes = null;
      renderEmptyDetail(state);
      renderGraph(state);
    });
    root.querySelector('[data-action="reload"]').addEventListener('click', async () => {
      try { await loadGraph(state, state.currentRow); } catch (error) { console.error(error); }
    });
    root.querySelector('[data-action="reset-layout"]').addEventListener('click', () => {
      const normalized = normalizeLayout(state.graphData, state.initialLayout, state.graphDef);
      state.nodes = normalized.nodes;
      state.nodeById = Object.fromEntries(state.nodes.map(node => [node.id, node]));
      state.transform = { x: normalized.viewport.x, y: normalized.viewport.y, k: normalized.viewport.scale };
      state.layoutSource = 'initial';
      setDirty(state);
      renderGraph(state);
      toast(state, '初期配置へ戻しました。保存するまではSidecarへ反映されません。');
    });
    root.querySelector('[data-action="save-relations"]').addEventListener('click', async event => {
      try {
        event.currentTarget.disabled = true;
        await saveRelations(state);
        if (state.selected?.kind === 'edge') selectEdge(state, state.selected.id);
      } catch (error) {
        console.error(error);
        toast(state, error.message, 'error');
      } finally {
        event.currentTarget.disabled = false;
      }
    });
    root.querySelector('[data-action="save-evolution"]').addEventListener('click', async event => {
      try {
        event.currentTarget.disabled = true;
        await saveEvolutionData(state);
      } catch (error) {
        console.error(error);
        toast(state, error.message, 'error');
      } finally {
        event.currentTarget.disabled = false;
      }
    });
    root.querySelector('[data-action="save-layout"]').addEventListener('click', async event => {
      try {
        event.currentTarget.disabled = true;
        await saveLayout(state);
      } catch (error) {
        console.error(error);
        toast(state, error.message, 'error');
      } finally {
        event.currentTarget.disabled = false;
      }
    });
    root.querySelector('[data-action="zoom-in"]').addEventListener('click', () => {
      const rect = state.svg.getBoundingClientRect();
      zoomAt(state, 1.2, rect.left + rect.width / 2, rect.top + rect.height / 2);
    });
    root.querySelector('[data-action="zoom-out"]').addEventListener('click', () => {
      const rect = state.svg.getBoundingClientRect();
      zoomAt(state, 1 / 1.2, rect.left + rect.width / 2, rect.top + rect.height / 2);
    });
    root.querySelector('[data-action="fit"]').addEventListener('click', () => fitGraph(state));
    root.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => switchTab(state, button.dataset.tab)));

    state.svg.addEventListener('pointerdown', event => {
      if (event.target.closest?.('.tes-node') || event.target.closest?.('.tes-edge-hit')) return;
      event.preventDefault();
      state.svg.setPointerCapture?.(event.pointerId);
      const point = svgPoint(state, event.clientX, event.clientY);
      state.drag = {
        kind: 'pan', pointerId: event.pointerId,
        startX: point.x, startY: point.y,
        originX: state.transform.x, originY: state.transform.y,
        startClientX: event.clientX, startClientY: event.clientY, moved: false
      };
      state.svg.classList.add('is-dragging');
    });

    state.svg.addEventListener('pointermove', event => {
      const drag = state.drag;
      if (!drag || drag.pointerId !== event.pointerId) return;
      const distance = Math.hypot(event.clientX - drag.startClientX, event.clientY - drag.startClientY);
      if (distance > 3) drag.moved = true;
      if (drag.kind === 'node') {
        const point = graphPoint(state, event.clientX, event.clientY);
        const node = state.nodeById[drag.nodeId];
        if (!node) return;
        node.x = point.x - drag.offsetX;
        node.y = point.y - drag.offsetY;
        setDirty(state);
        renderGraph(state);
      } else {
        const point = svgPoint(state, event.clientX, event.clientY);
        state.transform.x = drag.originX + point.x - drag.startX;
        state.transform.y = drag.originY + point.y - drag.startY;
        applyTransform(state);
        setDirty(state);
      }
    });

    const finishPointer = event => {
      const drag = state.drag;
      if (!drag || drag.pointerId !== event.pointerId) return;
      if (drag.kind === 'node' && !drag.moved) selectNode(state, drag.nodeId);
      if (drag.kind === 'pan' && !drag.moved) {
        state.selected = null;
        state.highlightNodes = null;
        renderEmptyDetail(state);
        renderGraph(state);
      }
      state.drag = null;
      state.svg.classList.remove('is-dragging');
      try { state.svg.releasePointerCapture?.(event.pointerId); } catch { /* ignore */ }
    };
    state.svg.addEventListener('pointerup', finishPointer);
    state.svg.addEventListener('pointercancel', finishPointer);
    state.svg.addEventListener('wheel', event => {
      event.preventDefault();
      zoomAt(state, event.deltaY < 0 ? 1.12 : 0.89, event.clientX, event.clientY);
    }, { passive: false });

    root.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeStudio();
    });
    root.tabIndex = -1;
    root.focus();
  }

  function catalogRowsFromContext(studio, context) {
    const source = context?.sourceData || context?.getSourceData?.() || studio.getSourceData?.() || {};
    return normalizeArray(source?.graphs).filter(row => row && row.status !== 'disabled');
  }

  function selectedRowFromContext(studio, context, rows) {
    const launchGraphId = text(context?.launchParams?.graphId || context?.launchParams?.graph_id || context?.urlParams?.graphId).trim();
    if (launchGraphId) {
      const fromLaunch = rows.find(row => row.graph_id === launchGraphId);
      if (fromLaunch) return fromLaunch;
    }
    const selected = context?.selectedRow || context?.getSelectedRow?.() || studio.getSelectedRow?.();
    if (selected && rows.includes(selected)) return selected;
    if (selected?.graph_id) return rows.find(row => row.graph_id === selected.graph_id) || selected;
    return rows[0] || null;
  }

  function isDedicatedWindowLaunch(context = {}) {
    const params = context.launchParams || context.urlParams || {};
    return ['1', 'true', 'yes', 'on'].includes(text(params.tesWindow || params.thoughtEvolutionWindow).trim().toLowerCase());
  }

  function dedicatedStudioUrl(row) {
    const url = new URL(window.location.href);
    url.search = '';
    url.hash = '';
    url.searchParams.set('data', 'overlay/thought_evolution/data/thought_evolution_graph_catalog_v0_1.json');
    url.searchParams.set('view', 'overlay/thought_evolution/view_defs/thought_evolution_graph_catalog_view_def_v0_1.json');
    url.searchParams.set('action', ACTION_ID);
    url.searchParams.set('tesWindow', '1');
    if (row?.graph_id) url.searchParams.set('graphId', row.graph_id);
    return url.toString();
  }

  function openDedicatedStudioWindow(row) {
    const url = dedicatedStudioUrl(row);
    const opened = window.open(url, '_blank');
    if (!opened) throw new Error('Thought Evolution Studioの新規ウィンドウを開けませんでした。ポップアップ許可を確認してください。');
    try { opened.opener = null; } catch { /* cross-origin guard */ }
    return url;
  }

  async function openStudio(studio, context = {}) {
    ensureStyles();
    const catalogRows = catalogRowsFromContext(studio, context);
    if (!catalogRows.length) throw new Error('現在のDataに graphs[] がありません。Graph Catalog Dataを開いてください。');
    const currentRow = selectedRowFromContext(studio, context, catalogRows);
    const overlayId = safeId(studio.plugin?.overlayId || context?.overlayId || 'thought_evolution', 'thought_evolution');
    const state = {
      studio, context, overlayId, catalogRows, currentRow,
      graphDef: null, graphData: null, relationData: null, relationSourcePath: '',
      nodes: [], edges: [], nodeById: {}, edgeById: {},
      initialLayout: null, transform: { x: 0, y: 0, k: 1 },
      filterSelections: {}, typeSelection: new Set(), relationStatusSelection: new Set(), presets: [], activePreset: 'all',
      search: '', selected: null, highlightNodes: null, drag: null, dirty: false, relationDirty: false,
      analysisProfile: null, differenceData: null, differenceResults: [], differenceResultById: {}, differenceCategorySelection: new Set(),
      evolutionProfile: null, evolutionObservationData: null, evolutionProposalData: null, evolutionVersionData: null, evolutionProposals: [], evolutionProposalById: {}, evolutionDirty: false,
      dedicatedWindow: isDedicatedWindowLaunch(context),
      dataBridge: createStudioDataBridge()
    };
    createDialog(state);
    await loadGraph(state, currentRow, { silent: true });
    const api = { state, reload: () => loadGraph(state, state.currentRow), saveLayout: () => saveLayout(state), saveRelations: () => saveRelations(state), saveDifferenceResults: () => saveDifferenceResults(state), generateEvolutionProposals: () => generateEvolutionProposals(state), saveEvolutionData: () => saveEvolutionData(state), generateNextVersionSnapshot: proposal => generateNextVersionSnapshot(state, proposal), dataBridge: state.dataBridge };
    window.ThoughtEvolutionStudioV04 = api;
    window.ThoughtEvolutionStudioV03 = api;
    window.ThoughtEvolutionStudioV02 = api;
    return state;
  }

  const plugin = {
    id: PLUGIN_ID,
    activate(studio) {
      studio.registerAction(ACTION_ID, async context => {
        const rows = catalogRowsFromContext(studio, context);
        const row = selectedRowFromContext(studio, context, rows);
        if (!isDedicatedWindowLaunch(context)) {
          openDedicatedStudioWindow(row);
          return {
            message: `Thought Evolution Studioを新規ウィンドウで開きました: ${row?.title || row?.graph_id || ''}`,
            statusOptions: { kind: 'success', title: 'Thought Evolution Studio' }
          };
        }
        const state = await openStudio(studio, context);
        return {
          message: `Thought Evolution Studioを開きました: ${state.graphData?.title || state.currentRow?.title || ''}`,
          statusOptions: { kind: 'success', title: 'Thought Evolution Studio' }
        };
      }, ['OpenThoughtEvolutionStudio', 'OpenThoughtGraph']);
    }
  };

  window.StudioOverlayPlugins = window.StudioOverlayPlugins || {};
  window.StudioOverlayPlugins[PLUGIN_ID] = plugin;
})();
