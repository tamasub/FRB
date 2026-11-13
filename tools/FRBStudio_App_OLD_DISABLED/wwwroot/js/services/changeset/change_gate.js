// studio_work_0269 / Step 5: shared acceptance gate for browser F12 and Node CLI.
// Reuses existing Studio Field Definition evaluator; no DOM or file I/O.
(function exposeFrbStudioChangeGate(root) {
  'use strict';
  const diff = typeof module !== 'undefined' && module.exports
    ? require('./change_diff.js') : root?.FrbStudioChangeDiff;
  if (!diff) throw new Error('FrbStudioChangeDiff is required before FrbStudioChangeGate');

  function assessFieldValidation(result) {
    // SKIPPED means only that no Field Definition was declared. Do not treat
    // an unavailable evaluator or unresolved contract as success.
    const accepted = result?.status === 'ACCEPT' ||
      (result?.status === 'SKIPPED' && result?.reason_code === 'FIELD_DEFINITION_NOT_DECLARED');
    return {
      accepted,
      status: result?.status ?? 'UNRESOLVED',
      reason_code: result?.reason_code ?? 'FIELD_DEFINITION_VALIDATION_UNAVAILABLE',
      blocking_checks: Array.isArray(result?.blocking_checks) ? result.blocking_checks : []
    };
  }

  function assessExpectedActual(expectedDiff, actualDiff) {
    const unexpected_diff = diff.compareExpectedActual(expectedDiff, actualDiff);
    return { accepted: unexpected_diff.length === 0, unexpected_diff };
  }

  // Check the *committed* row against an independently captured pre-commit
  // snapshot and the accepted editor intent; do not inspect or modify the DOM.
  function assessRowCommit(beforeRow, proposedRow, committedRow, path = '/row') {
    const expected_diff = diff.compareDiff(beforeRow, proposedRow, path);
    const actual_diff = diff.compareDiff(beforeRow, committedRow, path);
    return { ...assessExpectedActual(expected_diff, actual_diff), expected_diff, actual_diff };
  }

  const api = Object.freeze({ assessFieldValidation, assessExpectedActual, assessRowCommit });
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.FrbStudioChangeGate = api;
})(typeof window !== 'undefined' ? window : null);
