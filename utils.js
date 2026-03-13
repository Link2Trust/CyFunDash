/**
 * Shared utility functions for CyFun Dashboard pages.
 */

export function avgOrNull(arr) {
  return arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : null;
}

export function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

export function effectiveScore(scores, reqId, type) {
  const s = scores[reqId]?.[type];
  if (!s || s === '0') return 1; // N/A = 1
  return Number.parseInt(s);
}

export function collectSubScores(sub, fnName, ci, si, maxLevel, ctx) {
  const { scores, levelHierarchy, keyMeasuresOnly = false } = ctx;
  const doc = [], impl = [];
  for (let ri = 0; ri < sub.requirements.length; ri++) {
    const req = sub.requirements[ri];
    const reqLevel = levelHierarchy[req.assurance_level] || 99;
    if (reqLevel > maxLevel) continue;
    if (keyMeasuresOnly && !req.key_measure) continue;
    const reqId = `${fnName}-${ci}-${si}-${ri}`;
    doc.push(effectiveScore(scores, reqId, 'doc'));
    impl.push(effectiveScore(scores, reqId, 'impl'));
  }
  return { doc, impl };
}
