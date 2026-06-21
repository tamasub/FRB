# CODING_CONSTRAINTS.md
# Studio Architecture Constraints
## The Constitution of Studio

Version: 0.1-draft  
Status: Draft  
Created: 2026-06-21  

---

## 0. Purpose

This document defines the permanent coding constraints for Studio.

Studio is not merely a JSON editor.

Studio is a platform for turning JSON into experience.

The purpose of this document is to provide a shared architectural constitution for humans and AI collaborators who modify Studio.

Every code change must respect this document.

---

## 1. Core Declaration

Studio is a JSON Experience Platform.

Studio receives structured data and transforms it into human-readable, human-operable, replayable experience.

```text
Data JSON
  + ViewDef JSON
  + Action
  = Experience
```

Studio must not hard-code a single experience.

Studio must allow new experiences to grow through data, ViewDef, and Actions.

---

## 2. Fundamental Architecture

Studio is based on four separated layers.

```text
Data
ViewDef
Action
Runtime
```

### 2.1 Data

Data is the source of truth.

Examples:

- FFT log JSON
- Conversation JSON
- Constraint JSON
- Test pattern JSON
- Expected value JSON
- Test diff JSON
- MIDI JSON

Data must not contain UI-specific assumptions unless explicitly defined as presentation metadata.

### 2.2 ViewDef

ViewDef defines how Data is displayed and experienced.

ViewDef is not a secondary configuration file.

ViewDef is an experience design document.

Examples:

- Grid view
- Form view
- Chat view
- Replay view
- FFT view
- MIDI piano-roll view
- Test result view
- Diff view

New display behavior should be implemented by extending ViewDef whenever possible.

### 2.3 Action

Action defines what happens when the user executes an operation.

Examples:

- Play MIDI
- Replay conversation
- Run test
- Open FFT viewer
- Export Markdown
- Open URL
- Compare diff

Actions must be separated from renderers.

A button caption may change by ViewDef, but the execution behavior must be delegated to an Action implementation.

### 2.4 Runtime

Runtime connects Data, ViewDef, and Action.

Runtime should stay thin.

Runtime should not contain domain-specific logic unless it is part of the shared platform infrastructure.

---

## 3. Strategic Design Pattern

Studio must prefer strategic design patterns.

Different domains should be handled through common interfaces.

```text
FRB
AI-driven development
Conversation replay
MIDI
Testing
```

These may look different, but Studio treats them as experiences driven by Data, ViewDef, and Action.

### 3.1 Core Pattern

```text
detectGap()
executeExperience()
constraints()
```

This pattern appears across Studio-related domains.

- FRB: detect the gap between FFT and body sensation
- AI-driven development: detect the gap between expected and actual behavior
- JSON Studio: detect the gap between Data and View
- Replay: detect the gap in thought process
- Testing: detect the gap between expected and actual result

The implementation differs by domain.

The interface should remain conceptually consistent.

---

## 4. Data First

Always design from Data first.

Before writing UI code, clarify:

- What is the data?
- What is stable?
- What is variable?
- What should be expressed by ViewDef?
- What should be expressed by Action?
- What should remain outside the platform?

Do not start from screen layout alone.

---

## 5. ViewDef First

If a behavior can be described by ViewDef, prefer ViewDef.

Avoid hard-coding:

- Field names
- Chat roles
- Message text keys
- Fixed column structures
- Fixed captions
- Fixed toolbar buttons
- Domain-specific labels

Bad:

```js
message.user
message.assistant
message.text
```

Better:

```json
{
  "chat": {
    "roleField": "speaker",
    "textField": "message",
    "timeField": "timestamp",
    "metaFields": ["pattern", "event_type"]
  }
}
```

---

## 6. Action Separation

UI components must not directly implement domain actions.

Bad:

```js
button.onclick = () => playMidi(data);
```

Better:

```js
actionRegistry.execute("PlayMidi", context);
```

ViewDef may define:

```json
{
  "toolbar": [
    {
      "caption": "再生",
      "action": "PlayMidi"
    }
  ]
}
```

The same UI structure may call different actions depending on ViewDef.

---

## 7. Replay Ready

Studio should prefer replayable structures.

If a process happens over time, consider representing it as events.

Examples:

- Conversation steps
- Test execution steps
- JSON growth history
- MIDI notes
- FFT time-series data
- Review history

Replay is not only playback.

Replay is a way to share discovery experience.

---

## 8. Diff First

Diff is a first-class concept.

Studio should make differences visible.

Examples:

- Expected vs actual
- Before vs after
- Old ViewDef vs new ViewDef
- Old Data vs new Data
- Human intention vs AI output
- Body sensation vs measured FFT

When possible, design features so that differences can be observed, explained, and replayed.

---

## 9. Constraint First

AI collaboration must be driven by constraints.

When asking AI to generate code, data, tests, or ViewDef, provide constraints first.

A good request includes:

- Purpose
- Input structure
- Output structure
- Fixed rules
- Prohibited changes
- Compatibility requirements
- Test expectations

AI should not be asked to freely redesign Studio without constraints.

---

## 10. Small Change Principle

Prefer small, reviewable changes.

Avoid large rewrites unless explicitly requested.

Every modification should aim to preserve existing behavior.

When refactoring:

1. Preserve current behavior.
2. Extract responsibilities.
3. Add extension points.
4. Add new behavior through ViewDef or Action.
5. Verify with sample Data.

---

## 11. Existing Behavior Protection

Do not break existing Studio behavior.

Before changing code, identify affected features.

Examples:

- Grid display
- Form display
- Combo loading
- Markdown viewer link
- Sub-grid editing
- ReadOnly mode
- Save behavior
- Drag and drop
- Data/ViewDef association

If there is risk of regression, explain it clearly.

---

## 12. Chat View Must Be Variable

Chat view must not assume fixed field names.

Conversation JSON may vary by project.

A chat ViewDef should define:

- role field
- text field
- timestamp field
- avatar or label field
- visible metadata fields
- emphasis rules
- related artifacts
- step order

Chat is only one view of Conversation JSON.

The same Conversation JSON may also be shown as:

- Story
- Timeline
- Diff
- Architecture map
- Replay
- Review log

---

## 13. Studio Is Not Only an Editor

Studio may edit JSON.

But editing is not the core identity.

Studio exists to transform JSON into experience.

Examples:

- View FFT vibration
- Replay AI conversation
- Run test patterns
- Play MIDI
- Inspect constraints
- Compare diffs
- Read Markdown
- Follow links to related experiences

Editing is one experience among many.

---

## 14. ReadOnly Mode Is First-Class

ReadOnly mode is not a reduced version.

ReadOnly mode is the public experience mode.

It should support:

- GitHub Pages publication
- URL-based Data/ViewDef loading
- Replay viewing
- FFT viewing
- Markdown viewing
- JSON inspection
- Safe navigation between related experiences

ReadOnly mode is how readers experience the thought process.

---

## 15. URL Launch Support

Studio should support URL-based startup.

Example:

```text
studio.html?data=...&view=...
```

Future extensions may include:

```text
studio.html?data=...&view=...&mode=readonly
studio.html?data=...&view=...&step=12
studio.html?data=...&view=...&action=replay
```

URL launch is required for articles to link directly to Studio experiences.

---

## 16. AI Test Story Compatibility

Studio should support AI Test Story workflows.

Core data candidates:

- constraint JSON
- test pattern JSON
- expected value JSON
- actual result JSON
- diff JSON
- review conversation JSON
- test story JSON

The goal is not only to show test results.

The goal is to let humans experience how test data, constraints, and differences grow.

---

## 17. Characterization as Cognitive Support

Important methods, roles, or concepts may be represented as characters in AI Test Story.

This is not decoration.

This is cognitive support.

Examples:

- detectGap(): 差分刑事
- constraints(): 制約番長
- executeExperience(): 体験隊長
- GenerateDetectGap(): 問い職人
- return;: 逃げる師匠

Characterization must not corrupt source code.

It should appear in ViewDef, Story, Replay, or Review output.

Code remains clean.

Story makes understanding easier.

---

## 18. Naming Policy

Prefer names that express responsibility.

Avoid vague names.

Recommended conceptual names:

- DataStore
- ViewDefLoader
- RendererRegistry
- ActionRegistry
- StudioRuntime
- ChatRenderer
- GridRenderer
- FormRenderer
- ReplayController
- DiffRenderer
- UrlLauncher

Avoid mixing multiple responsibilities in one file.

---

## 19. File Split Policy

Large files should be split by responsibility.

A suggested structure:

```text
app.js
core/
  state.js
  dataStore.js
  viewDefLoader.js
  studioRuntime.js
renderers/
  gridRenderer.js
  formRenderer.js
  chatRenderer.js
  diffRenderer.js
actions/
  actionRegistry.js
  openUrlAction.js
  replayAction.js
  runTestAction.js
features/
  replayController.js
  urlLaunch.js
utils/
  dom.js
  jsonPath.js
  format.js
```

`app.js` should become the startup and wiring layer.

---

## 20. AI Collaboration Rule

When AI modifies Studio code, AI must:

1. Read this file first.
2. Identify the architectural principle involved.
3. Explain the intended change briefly.
4. Avoid unrelated modifications.
5. Keep changes small.
6. Preserve existing behavior.
7. Prefer Data/ViewDef/Action separation.
8. Report any uncertainty.

---

## 21. Human Collaboration Rule

Humans may freely grow Studio.

However, when adding a new branch, ask:

- Is this Data?
- Is this ViewDef?
- Is this Action?
- Is this Runtime?
- Can this become reusable?
- Can this be replayed?
- Can another AI understand this later?

Studio should grow like a tree, not like a pile.

---

## 22. Studio Constitution

This document is the constitution of Studio.

It is not a temporary prompt.

It is a shared promise between humans and AI collaborators.

AI may change.

Tools may change.

Languages may change.

But Studio should continue to grow under the same architectural spirit.

---

## 23. Summary

Studio is:

- not just a JSON editor
- not just a viewer
- not just a replay tool
- not just a test tool
- not just an FFT tool
- not just a MIDI tool

Studio is a platform for turning structured data into experience.

```text
Invisible things
  -> JSON
  -> ViewDef
  -> Action
  -> Experience
  -> Shared understanding
```

The mission of Studio is to make invisible things visible, structured, replayable, and shareable.

---

## Revision History

- 2026-06-21: v0.1-draft initial constitution
