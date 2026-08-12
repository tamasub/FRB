// v0.18.40-studio-editor-component-model
// Editor-specific lifecycle base. It consumes an Editor Context but does not know domain-specific meaning.

class EditorComponent extends StudioComponent {
  get row() {
    return this.context?.row ?? null;
  }

  get rowIndex() {
    return Number.isInteger(this.context?.rowIndex) ? this.context.rowIndex : -1;
  }

  get editorMode() {
    return this.context?.mode ?? 'edit';
  }

  get viewDef() {
    return this.context?.viewDef ?? null;
  }

  get gridDef() {
    return this.context?.gridDef ?? null;
  }

  get sourceData() {
    return this.context?.sourceData ?? null;
  }

  get serviceContext() {
    return this.context?.services ?? this.services ?? {};
  }
}

globalThis.EditorComponent = EditorComponent;
