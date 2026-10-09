/**
 * Shared utility functions for CyFun Dashboard pages.
 */

export function avgOrNull(arr) {
  return arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : null;
}

// Escapes text for safe use in HTML content *and* quoted attribute values.
export function escapeHtml(str) {
  return String(str ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function effectiveScore(scores, reqId, type) {
  const s = scores[reqId]?.[type];
  if (!s || s === '0') return 1; // N/A = 1
  const n = Number.parseInt(s, 10);
  return Number.isNaN(n) ? 1 : n;
}

export function collectSubScores(sub, fnName, ci, si, maxLevel, ctx) {
  const { scores, levelHierarchy, keyMeasuresOnly = false, managementAspectsOnly = false, managementAspects = null } = ctx;
  const doc = [], impl = [];
  for (let ri = 0; ri < sub.requirements.length; ri++) {
    const req = sub.requirements[ri];
    const reqLevel = levelHierarchy[req.assurance_level] || 99;
    if (reqLevel > maxLevel) continue;
    if (keyMeasuresOnly && !req.key_measure) continue;
    if (managementAspectsOnly && managementAspects) {
      const code = req.requirement.replace(/\s+/g, '').split(':')[0];
      if (!managementAspects.has(code)) continue;
    }
    const reqId = `${fnName}-${ci}-${si}-${ri}`;
    doc.push(effectiveScore(scores, reqId, 'doc'));
    impl.push(effectiveScore(scores, reqId, 'impl'));
  }
  return { doc, impl };
}
