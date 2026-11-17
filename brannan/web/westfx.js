// ===== westfx.js — gold-rush cast: every miner has his own head shape, hat, face and body; plus western fx cards =====
// Heads are wobbly superellipse blobs (never perfect circles); each cast member overrides the blob parameters.
const WB = { thin: { torso: 1.0, legs: 1.5, tw: 0.8 }, normal: { torso: 1.06, legs: 1.36, tw: 0.92 }, stout: { torso: 1.08, legs: 1.2, tw: 1.2 }, short: { torso: 0.95, legs: 1.05, tw: 1.0 }, tall: { torso: 1.12, legs: 1.6, tw: 0.82 } };
export const MINERS = {
  jack: { seed: 21, head: { a: 100, b: 132, nTop: 1.7, nBot: 2.4, egg: -0.06, noise: 0.03, asym: 0.05 }, skin: '#f0c49a', hat: 'cowboy', hatCol: '#c8a468', band: '#5a3a22', stache: ['handle', '#4a3020'], shirt: '#b3402f', pants: '#4a5570', boots: '#2a1f18', build: 'tall', tool: 'shovel', nose: 'long' },
  moe: { seed: 34, head: { a: 132, b: 102, nTop: 2.15, nBot: 1.95, egg: 0.05, noise: 0.034, asym: 0.0 }, skin: '#e8b48a', hat: 'none', bald: true, hair: '#8c8c88', beard: ['full', '#9c9c98'], shirt: '#5f7f4a', pants: '#6a5a44', boots: '#2a1f18', build: 'stout', suspenders: '#7a3b2a', tool: 'pick', nose: 'bulb' },
  pete: { seed: 47, head: { a: 106, b: 114, nTop: 1.55, nBot: 2.9, egg: 0.24, noise: 0.026, asym: -0.07 }, skin: '#f5cba2', hat: 'flat', hatCol: '#3d5a8a', mutton: '#7a4a28', shirt: '#e0b04a', pants: '#5a4a3a', boots: '#2a1f18', build: 'short', tool: 'pan', nose: 'small' },
  sam: { seed: 58, head: { a: 122, b: 106, nTop: 2.0, nBot: 3.4, egg: -0.1, noise: 0.022, asym: 0.04 }, skin: '#d9a77c', hat: 'bowler', hatCol: '#2a2630', stache: ['handle', '#1c1612'], shirt: '#d9d2c0', vest: '#6a3a3a', pants: '#3a3f58', boots: '#2a1f18', build: 'normal', tool: 'shovel', nose: 'bulb' },
  lou: { seed: 63, head: { a: 116, b: 120, nTop: 2.25, nBot: 2.05, egg: 0.0, noise: 0.048, asym: 0.1, rot: 0.12 }, skin: '#ecc19a', hat: 'straw', hatCol: '#e6cf8a', stubble: true, shirt: '#4a7aa8', pants: '#7a6a50', boots: '#3a2a20', build: 'normal', tool: 'pick', nose: 'small' },
  abe: { seed: 72, head: { a: 94, b: 138, nTop: 1.6, nBot: 2.2, egg: 0.1, noise: 0.03, asym: -0.04 }, skin: '#f2cfae', hat: 'tophat', hatCol: '#2f2a32', beard: ['goatee', '#2e2018'], shirt: '#7b5a8a', pants: '#2f3548', boots: '#1d1612', build: 'thin', tool: 'shovel', nose: 'long' },
  ned: { seed: 85, head: { a: 124, b: 108, nTop: 1.8, nBot: 2.2, egg: -0.15, noise: 0.036, asym: 0.07, rot: -0.1 }, skin: '#f7d2b0', hat: 'bandana', hatCol: '#c9382e', hair: '#b86a2a', shirt: '#3f8a7a', pants: '#5a5a6a', boots: '#2a1f18', build: 'thin', tool: 'shovel', nose: 'pointy' },
  ada: { seed: 97, head: { a: 112, b: 116, nTop: 2.4, nBot: 2.0, egg: 0.02, noise: 0.03, asym: 0.0 }, skin: '#f3c9a4', hat: 'floppy', hatCol: '#8e6fb0', hair: '#5a3220', braids: true, shirt: '#e8e0d0', skirt: '#a8523f', pants: '#4a3a3a', boots: '#2a1f18', build: 'normal', tool: 'pan', nose: 'small', lashes: true },
  gus: { seed: 108, head: { a: 128, b: 112, nTop: 1.9, nBot: 2.6, egg: 0.12, noise: 0.04, asym: -0.08, rot: 0.08 }, skin: '#c99067', hat: 'cap', hatCol: '#8a5a2a', stache: ['walrus', '#2a1c14'], shirt: '#c25a2a', pants: '#464a5a', boots: '#2a1f18', build: 'stout', suspenders: '#2a2a2a', tool: 'pick', nose: 'bulb' },
  brannan: { seed: 131, head: { a: 120, b: 110, nTop: 2.0, nBot: 3.0, egg: -0.08, noise: 0.026, asym: 0.05 }, skin: '#f1c7a0', hat: 'bowler', hatCol: '#2b2420', stache: ['handle', '#241812'], shirt: '#efe8d6', vest: '#2f6a4a', pants: '#3a3f58', boots: '#241a14', build: 'normal', tool: 'none', nose: 'bulb', watch: true },
  rex: { seed: 119, head: { a: 110, b: 124, nTop: 2.05, nBot: 2.35, egg: -0.02, noise: 0.05, asym: 0.12, rot: -0.14 }, skin: '#e9b890', hat: 'cowboy', hatCol: '#6a4a32', band: '#d8c070', mutton: '#4a3020', shirt: '#6a8a3a', pants: '#2f3a4a', boots: '#2a1f18', build: 'normal', tool: 'shovel', nose: 'long' },
};
const gHead = (S, facing) => ({ ...headBlob(S.seed, S.head?.a ?? 118, facing), ...(S.head || {}) });
const SHN = [0.96, 0.86, 0.84];

// ---------- tools ----------
const STEELC = '#aab4be', WOODC = '#8a5a30';
/** tool drawn from a hand point along a direction (deg from straight-up, +clockwise) */
const toolAt = (p, kind, hand, ang, len, u) => {
  const a = rad(ang), d = [Math.sin(a), -Math.cos(a)], nrm = [-d[1], d[0]];
  const P = (k, s = 0) => [hand[0] + d[0] * k + nrm[0] * s, hand[1] + d[1] * k + nrm[1] * s];
  if (kind === 'pan') { // flat prospecting pan held by its rim
    const c = P(len * 0.45); p.ell(c[0], c[1], len * 0.42, len * 0.14, STEELC, 5 * u, 0, 360, ang - 90); p.ell(c[0], c[1] + u, len * 0.28, len * 0.07, '#7e8996', 0, 0, 360, ang - 90); return;
  }
  const e0 = P(-0.18 * len), e1 = P(len);
  p.stroke([e0, e1], 7 * u + 6, INK); p.stroke([e0, e1], 7 * u, WOODC);
  if (kind === 'shovel') {
    const blade = [P(len * 0.98, -13 * u), P(len * 1.02, 13 * u), P(len * 1.3, 17 * u), P(len * 1.42, 0), P(len * 1.3, -17 * u)];
    p.poly(blade, STEELC, 5 * u); p.stroke([P(len * 1.08, 0), P(len * 1.34, 0)], 3 * u, '#e6edf3');
  } else if (kind === 'pick') {
    const head = [P(len * 0.93, -44 * u), P(len * 1.0, -8 * u), P(len * 1.0, 8 * u), P(len * 0.93, 44 * u), P(len * 1.08, 10 * u), P(len * 1.08, -10 * u)];
    p.poly(head, STEELC, 5 * u); p.stroke([P(len * 0.99, -30 * u), P(len * 1.03, -8 * u)], 3 * u, '#e6edf3');
  }
};

// ---------- hats / hair / beards ----------
const hatDraw = (p, S, H, cx, hc, light, ow, u, side = 0) => {
  const W = 2 * H.a, HH = 2 * H.b, crown = hc - H.b, hat = S.hat, col = S.hatCol || '#8a6a40', a = H.rot * 0.7;
  const R = (pts) => rotPts(pts, a, cx, hc), sh = (c) => mul(c, SH_FELT), fx = side ? 6 * u : 0;
  const brimE = (yb, rx, ry, c) => { const [bx, by] = R([[cx + fx, yb]])[0]; p.ell(bx, by, rx, ry, c, ow, 0, 360, a * 180 / Math.PI); };
  const fill = (pts, c, k = 0.4) => { p.shadedFill(pts, c, sh(c), light, W * 0.4, k); p.poly(pts, null, ow); };
  if (hat === 'cowboy') {
    const yb = crown + 0.3 * HH, cr = R([[cx - 0.34 * W + fx, yb], [cx - 0.31 * W + fx, yb - 0.5 * HH], [cx - 0.12 * W + fx, yb - 0.6 * HH], [cx + fx, yb - 0.5 * HH], [cx + 0.12 * W + fx, yb - 0.6 * HH], [cx + 0.31 * W + fx, yb - 0.5 * HH], [cx + 0.34 * W + fx, yb]]);
    fill(cr, col);
    p.clip(cr, () => p.band(R([[cx - 0.4 * W + fx, yb - 0.1 * HH], [cx + 0.4 * W + fx, yb - 0.1 * HH]]), S.band || '#4a3320', 0.12 * HH, 0.8 * u));
    p.poly(cr, null, ow);
    brimE(yb + 2 * u, 0.82 * W, 0.12 * HH, mix(col, '#ffffff', 0.08));
    const [lx, ly] = R([[cx + fx, yb + 0.11 * HH]])[0]; p.arc(lx, ly - 0.05 * HH, 0.7 * W, 0.07 * HH, 20, 160, 3 * u, mul(col, [0.6, 0.55, 0.5]));
  } else if (hat === 'flat') {
    const yb = crown + 0.36 * HH, dome = R([...ellPts(cx + fx, yb, 0.5 * W, 0.42 * HH, 180, 360, 0, 36), [cx + 0.5 * W + fx, yb + 2 * u], [cx - 0.5 * W + fx, yb + 2 * u]]);
    fill(dome, col);
    const pk = R([[cx + 0.1 * W + fx, yb + 1 * u], [cx + 0.62 * W + fx, yb + 0.02 * HH], [cx + 0.6 * W + fx, yb + 0.1 * HH], [cx + 0.05 * W + fx, yb + 0.07 * HH]]);
    p.poly(pk, mul(col, [0.8, 0.8, 0.85]), ow); p.dot(cx + fx, yb - 0.38 * HH, 3.5 * u, mul(col, [0.7, 0.7, 0.8]));
  } else if (hat === 'bowler') {
    const yb = crown + 0.32 * HH, dome = R([...ellPts(cx + fx, yb, 0.4 * W, 0.62 * HH, 180, 360, 0, 40), [cx + 0.4 * W + fx, yb], [cx - 0.4 * W + fx, yb]]);
    fill(dome, col, 0.5); p.stroke(R(ellPts(cx - 0.12 * W + fx, yb - 0.4 * HH, 0.12 * W, 0.12 * HH, 200, 290, 0, 10)), 4 * u, '#ffffff44');
    p.clip(dome, () => p.band(R([[cx - 0.5 * W + fx, yb - 0.08 * HH], [cx + 0.5 * W + fx, yb - 0.08 * HH]]), '#c9a84a', 0.07 * HH, 0.6 * u)); p.poly(dome, null, ow);
    brimE(yb + 2 * u, 0.56 * W, 0.075 * HH, mul(col, [1.15, 1.15, 1.2]));
  } else if (hat === 'tophat') {
    const yb = crown + 0.3 * HH, body = R([[cx - 0.31 * W + fx, yb], [cx - 0.33 * W + fx, yb - 0.95 * HH], [cx + 0.33 * W + fx, yb - 0.95 * HH], [cx + 0.31 * W + fx, yb]]);
    fill(body, col, 0.4); p.clip(body, () => p.band(R([[cx - 0.4 * W + fx, yb - 0.14 * HH], [cx + 0.4 * W + fx, yb - 0.14 * HH]]), '#a8323a', 0.14 * HH, 0.8 * u)); p.poly(body, null, ow);
    const [tx, ty] = R([[cx + fx, yb - 0.95 * HH]])[0]; p.ell(tx, ty, 0.33 * W, 0.05 * HH, mul(col, [1.3, 1.3, 1.35]), ow, 0, 360, a * 180 / Math.PI);
    brimE(yb + 2 * u, 0.5 * W, 0.075 * HH, mul(col, [0.9, 0.9, 0.95]));
  } else if (hat === 'straw') {
    const yb = crown + 0.32 * HH, cr = R([[cx - 0.3 * W + fx, yb], [cx - 0.26 * W + fx, yb - 0.34 * HH], [cx + 0.26 * W + fx, yb - 0.34 * HH], [cx + 0.3 * W + fx, yb]]);
    brimE(yb + 3 * u, 0.9 * W, 0.15 * HH, mix(col, '#ffffff', 0.1));
    for (let i = 0; i < 16; i++) { const t = i / 15 * Math.PI, [sx, sy] = R([[cx + fx + Math.cos(t) * 0.86 * W, yb + 3 * u + Math.sin(t) * 0.12 * HH]])[0]; p.stroke([[sx, sy], [sx + Math.cos(t) * 10 * u, sy + 6 * u]], 2 * u, mul(col, [0.7, 0.62, 0.5])); }
    fill(cr, col, 0.5); p.clip(cr, () => p.band(R([[cx - 0.4 * W + fx, yb - 0.06 * HH], [cx + 0.4 * W + fx, yb - 0.06 * HH]]), '#7a4a2a', 0.1 * HH, 0.6 * u)); p.poly(cr, null, ow);
    for (let i = 0; i < 6; i++) { const [sx, sy] = R([[cx + fx + (i - 2.5) * 0.09 * W, yb - 0.3 * HH]])[0]; p.stroke([[sx, sy], [sx + 3 * u, sy + 0.22 * HH]], 1.6 * u, mul(col, [0.7, 0.62, 0.5])); }
  } else if (hat === 'bandana') {
    const hp = blobPts(cx, hc, H), cap = hp.filter((q) => q[1] < crown + 0.38 * HH);
    const poly = [...cap, [cx - 1.04 * H.a, crown + 0.34 * HH], [cx + 1.04 * H.a, crown + 0.34 * HH]];
    p.clip(hp, () => { p.poly([[cx - 1.1 * H.a, crown - 0.2 * HH], [cx + 1.1 * H.a, crown - 0.2 * HH], [cx + 1.1 * H.a, crown + 0.36 * HH], [cx + 0.4 * H.a, crown + 0.3 * HH], [cx - 0.4 * H.a, crown + 0.38 * HH], [cx - 1.1 * H.a, crown + 0.3 * HH]], col, 0); for (let i = 0; i < 9; i++) p.dot(cx + (i % 5 - 2) * 0.35 * H.a + (i < 5 ? 0 : 0.17 * H.a), crown + (i < 5 ? 0.12 : 0.27) * HH, 3.2 * u, '#ffffff'); });
    p.poly([[cx - 1.0 * H.a, crown + 0.3 * HH], [cx - 0.4 * H.a, crown + 0.38 * HH], [cx + 0.4 * H.a, crown + 0.3 * HH], [cx + 1.0 * H.a, crown + 0.3 * HH]], null, 0);
    p.stroke([[cx - 1.0 * H.a, crown + 0.3 * HH], [cx - 0.4 * H.a, crown + 0.38 * HH], [cx + 0.4 * H.a, crown + 0.31 * HH], [cx + 1.0 * H.a, crown + 0.3 * HH]], 4.5 * u, INK);
    const kx = cx + 0.9 * H.a, ky = crown + 0.3 * HH; p.poly([[kx, ky], [kx + 0.34 * H.a, ky - 0.18 * HH], [kx + 0.42 * H.a, ky + 0.05 * HH]], col, ow * 0.8); p.poly([[kx, ky], [kx + 0.3 * H.a, ky + 0.2 * HH], [kx + 0.5 * H.a, ky + 0.25 * HH]], col, ow * 0.8); p.dot(kx, ky, 6 * u, mul(col, [0.8, 0.8, 0.8]));
    if (S.hair) for (let i = 0; i < 3; i++) p.poly([[cx - 0.2 * H.a + i * 0.2 * H.a, crown + 0.04 * HH], [cx - 0.34 * H.a + i * 0.26 * H.a, crown - 0.24 * HH], [cx - 0.06 * H.a + i * 0.2 * H.a, crown + 0.04 * HH]], S.hair, ow * 0.7);
  } else if (hat === 'floppy') {
    const yb = crown + 0.32 * HH, cr = R([[cx - 0.32 * W + fx, yb], [cx - 0.28 * W + fx, yb - 0.4 * HH], [cx + 0.28 * W + fx, yb - 0.4 * HH], [cx + 0.32 * W + fx, yb]]);
    const brim = R([[cx - 0.9 * W + fx, yb + 0.2 * HH], [cx - 0.5 * W + fx, yb - 0.03 * HH], [cx + 0.5 * W + fx, yb - 0.03 * HH], [cx + 0.9 * W + fx, yb + 0.2 * HH], [cx + 0.4 * W + fx, yb + 0.1 * HH], [cx - 0.4 * W + fx, yb + 0.1 * HH]]);
    fill(brim, mul(col, [0.9, 0.9, 0.95])); fill(cr, col, 0.5);
    p.clip(cr, () => p.band(R([[cx - 0.4 * W + fx, yb - 0.05 * HH], [cx + 0.4 * W + fx, yb - 0.05 * HH]]), '#f2d0e8', 0.1 * HH, 0.6 * u)); p.poly(cr, null, ow);
    const fx2 = cx + 0.3 * W + fx; p.poly([[fx2, yb - 0.04 * HH], [fx2 + 0.18 * W, yb - 0.22 * HH], [fx2 + 0.2 * W, yb + 0.02 * HH]], '#f2d0e8', ow * 0.7);
  } else if (hat === 'cap') {
    const yb = crown + 0.38 * HH, dome = R([...ellPts(cx + fx, yb, 0.52 * W, 0.46 * HH, 180, 360, 0, 36), [cx + 0.52 * W + fx, yb + 2 * u], [cx - 0.52 * W + fx, yb + 2 * u]]);
    fill(dome, col, 0.5);
    p.clip(dome, () => { for (let i = -3; i <= 3; i++) p.stroke(R([[cx + fx + i * 0.14 * W, yb], [cx + fx + i * 0.09 * W, yb - 0.5 * HH]]), 2 * u, mul(col, [0.6, 0.55, 0.5])); });
    p.poly(R([[cx - 0.55 * W + fx, yb + 0.02 * HH], [cx + 0.55 * W + fx, yb + 0.02 * HH], [cx + 0.5 * W + fx, yb + 0.1 * HH], [cx - 0.5 * W + fx, yb + 0.1 * HH]]), mul(col, [0.78, 0.76, 0.76]), ow);
  } else if (hat === 'none' && S.bald) { // bald: shine + side tufts
    p.stroke(R(ellPts(cx - 0.3 * H.a, crown + 0.2 * HH, 0.2 * H.a, 0.1 * HH, 200, 300, 0, 10)), 5 * u, '#ffffff77');
    for (const s of [-1, 1]) { const x0 = cx + s * 0.98 * H.a; p.poly([[x0, hc - 0.55 * H.b], [x0 + s * 0.2 * H.a, hc - 0.3 * H.b], [x0 + s * 0.16 * H.a, hc + 0.1 * H.b], [x0 - s * 0.02 * H.a, hc - 0.05 * H.b]], S.hair, ow * 0.7); }
    p.poly([[cx - 0.22 * H.a, crown + 0.02 * HH], [cx - 0.1 * H.a, crown - 0.14 * HH], [cx + 0.04 * H.a, crown + 0.0 * HH], [cx + 0.12 * H.a, crown - 0.12 * HH], [cx + 0.26 * H.a, crown + 0.04 * HH]], S.hair, ow * 0.7);
  }
};
const beardDraw = (p, S, H, cx, hc, light, ow, u, hp, side = 0) => {
  const [kind, col] = S.beard || [], HH = 2 * H.b, off = side ? 0.12 * H.a : 0;
  if (S.mutton) for (const s of [-1, 1]) { const x0 = cx + s * 0.86 * H.a + (s > 0 ? off : -off * 0.3); p.poly(ellPts(x0, hc + 0.22 * H.b, 0.2 * H.a, 0.5 * H.b, 0, 360, s * 0.12), S.mutton, ow * 0.8); }
  if (kind === 'full') {
    const lower = hp.filter((q) => q[1] > hc + 0.1 * H.b).map(([x, y]) => [x + (x - cx) * 0.1 + off, y + (y - hc) * 0.2 + 0.05 * HH * Math.abs(Math.sin((x - cx) * 0.12))]);
    lower.sort((A, B) => Math.atan2(A[1] - hc, A[0] - cx) - Math.atan2(B[1] - hc, B[0] - cx));
    const poly = [...lower, [cx + 0.98 * H.a + off, hc + 0.0 * H.b], [cx + 0.5 * H.a + off, hc + 0.2 * H.b], [cx + off, hc + 0.12 * H.b], [cx - 0.5 * H.a + off, hc + 0.2 * H.b], [cx - 0.98 * H.a + off, hc + 0.0 * H.b]];
    p.shadedFill(poly, col, mul(col, [0.7, 0.7, 0.72]), light, H.a, 0.3); p.poly(poly, null, ow * 0.9);
    for (let i = 0; i < 7; i++) p.stroke([[cx + (i - 3) * 0.28 * H.a + off, hc + 0.55 * H.b], [cx + (i - 3) * 0.3 * H.a + off, hc + 1.05 * H.b]], 2 * u, mul(col, [0.7, 0.7, 0.7]));
  } else if (kind === 'goatee') {
    const pts = [[cx - 0.22 * H.a + off, hc + 0.5 * H.b], [cx + 0.22 * H.a + off, hc + 0.5 * H.b], [cx + 0.14 * H.a + off, hc + 1.12 * H.b], [cx + off, hc + 1.4 * H.b], [cx - 0.14 * H.a + off, hc + 1.12 * H.b]];
    p.poly(pts, col, ow * 0.9);
  }
  if (S.stubble) { p.g.save(); p.g.globalAlpha = 0.5; for (let i = 0; i < 38; i++) { const a = Math.PI * (0.1 + 0.8 * rnd(S.seed, 40 + i)), r = (0.55 + 0.4 * rnd(S.seed, 90 + i)); p.dot(cx + Math.cos(a) * 0.82 * H.a * r + off, hc + Math.sin(a) * 0.9 * H.b * r + 0.1 * H.b, 2 * u, '#4a3a30'); } p.g.restore(); }
  if (S.stache) { // moustache: own shapes
    const [k, c] = S.stache, y = hc + 0.3 * H.b, mx = cx + 8 * u * (side ? 3 : 1) * 0.5 + off;
    for (const s of [-1, 1]) {
      if (k === 'handle') { p.poly([[mx + s * 2 * u, y - 4 * u], [mx + s * 30 * u, y + 2 * u], [mx + s * 46 * u, y - 12 * u], [mx + s * 38 * u, y + 8 * u], [mx + s * 18 * u, y + 11 * u], [mx + s * 2 * u, y + 8 * u]], c, ow * 0.6); }
      else if (k === 'walrus') { p.poly(ellPts(mx + s * 16 * u, y + 4 * u, 20 * u, 11 * u, 0, 360, s * 0.25), c, ow * 0.7); p.poly([[mx + s * 28 * u, y + 8 * u], [mx + s * 34 * u, y + 26 * u], [mx + s * 22 * u, y + 14 * u]], c, ow * 0.5); }
    }
  }
};
const noseDraw = (p, S, cx, hc, u, H, side = 0) => {
  const k = S.nose || 'small', x = cx + (side ? 30 * u : 5 * u * 0), y = hc + 6 * u;
  if (side) { const L = { small: 5, bulb: 12, long: 16, pointy: 18 }[k] || 6; p.poly([[x + 12 * u, y - 4 * u], [x + 12 * u + L * u, y + 8 * u], [x + 12 * u, y + 11 * u]], S.skin, 3 * u); return; }
  if (k === 'bulb') p.ell(cx + 6 * u, y + 4 * u, 12 * u, 10 * u, mul(S.skin, [1, 0.88, 0.86]), 3.5 * u);
  else if (k === 'long') p.poly([[cx + 2 * u, y - 10 * u], [cx + 12 * u, y + 20 * u], [cx - 2 * u, y + 22 * u]], mul(S.skin, [1, 0.9, 0.88]), 3.5 * u);
  else if (k === 'pointy') p.poly([[cx + 3 * u, y - 8 * u], [cx + 20 * u, y + 20 * u], [cx - 2 * u, y + 18 * u]], mul(S.skin, [1, 0.9, 0.88]), 3.5 * u);
  else p.arc(cx + 5 * u, y + 12 * u, 5 * u, 4 * u, 20, 160, 3 * u);
};

// ---------- front-facing miner ----------
export const goldFront = (p, key, o = {}) => {
  const S = typeof key === 'string' ? MINERS[key] : key;
  const { expr = 'neutral', blink = 0, look = 0, facing = 0, step = 0, run = 0, L = 'hang', R = 'hang', tilt = 0, headTilt = 0, bob = 0, light = rad(-120), toolAng = 20, tool = true, crouch = 0, dg = 0 } = o;
  const dd = 0.5 - 0.5 * Math.cos(Math.PI * 2 * dg);
  const Bd = WB[S.build || 'normal'], H = gHead(S, facing), W = 2 * H.a, HH = 2 * H.b, u = W / 100, lid = lidOf(blink), skin = S.skin;
  const sole = 975, legsL = Bd.legs * HH, torsoL = Bd.torso * HH, bounce = run ? Math.abs(Math.sin(Math.PI * 2 * step)) * 0.05 * HH : 0;
  const torsoBot = sole - legsL * (1 - 0.32 * crouch) - bounce - bob * HH, chin = torsoBot - torsoL, hc = chin - H.b, hipY = torsoBot - 0.12 * HH, cx = 300;
  const thick = thickAngle(light), ow = 5 * u, legCol = mix(S.pants, INK, 0.62), armCol = mix(S.shirt, INK, 0.55);
  p.rot = null;
  const T = { a: (0.4 * W) / 1.06 * Bd.tw * 1.1, b: 0.5 * (torsoBot - (chin - 0.25 * HH)), nTop: 2.2, nBot: 2.6, egg: 0.12, asym: 0.04 * facing, rot: 0, noise: 0.012, seed: S.seed + 7 };
  const tcx = cx + 3 * u * facing, tcy = torsoBot - T.b, sh = (side) => [tcx + side * 0.85 * T.a, chin + 0.14 * HH];
  const hand = {};
  // tool behind body when held high
  const toolFront = tool && S.tool && S.tool !== 'none';
  // legs
  for (const side of [-1, 1]) {
    const k = Math.sin(Math.PI * 2 * (step + (side > 0 ? 0.5 : 0))), up = step ? Math.max(0, k) * (run ? 58 : 30) : 0;
    const hx = cx + side * 14 * u * Bd.tw, fx = cx + side * ((run ? 25 : 20) + crouch * 14) * u, fy = sole - 4 * u - up;
    p.stroke(curve([hx, hipY], [(hx + fx) / 2 + side * (2 + up * 0.1 + crouch * 34) * u, (hipY + fy) / 2 - up * 0.12], [fx, fy]), 6 * u, legCol);
    p.ell(fx + side * 5 * u, fy + 1 * u, 14 * u, 7.5 * u, S.boots, 3.4 * u);
  }
  p.rot = tilt ? [rad(tilt), cx, hipY] : null;
  if (S.skirt) { const sk = [[tcx - 0.8 * T.a, torsoBot - 0.2 * HH], [tcx + 0.8 * T.a, torsoBot - 0.2 * HH], [tcx + 1.5 * T.a, torsoBot + 0.55 * HH], [tcx, torsoBot + 0.62 * HH], [tcx - 1.5 * T.a, torsoBot + 0.55 * HH]]; p.shadedFill(sk, S.skirt, mul(S.skirt, [0.65, 0.6, 0.7]), light, T.a); p.poly(sk, null, ow * 0.8); }
  // torso
  const tp = blobPts(tcx, tcy, T);
  p.shadedFill(tp, S.shirt, mul(S.shirt, SH_CLOTH), light, T.a, 0.42); p.inkRing(tp, ow, thick);
  if (S.vest) { p.clip(tp, () => { for (const s of [-1, 1]) p.poly([[tcx + s * 0.1 * T.a, chin + 0.02 * HH], [tcx + s * 1.1 * T.a, chin + 0.02 * HH], [tcx + s * 1.1 * T.a, torsoBot], [tcx + s * 0.1 * T.a, torsoBot]], S.vest, 0); }); p.stroke([[tcx, chin + 0.05 * HH], [tcx, torsoBot - 0.05 * HH]], 3 * u); for (let i = 0; i < 3; i++) p.dot(tcx + 0.06 * T.a, chin + (0.22 + i * 0.2) * HH, 3.2 * u, '#e8c45a'); p.inkRing(tp, ow, thick); }
  if (S.suspenders) p.clip(tp, () => { for (const s of [-1, 1]) p.stroke([[tcx + s * 0.55 * T.a, chin - 0.1 * HH], [tcx + s * 0.4 * T.a, torsoBot]], 7 * u, S.suspenders); });
  p.band([[tcx - T.a * 0.98, torsoBot - 0.14 * HH], [tcx + T.a * 0.98, torsoBot - 0.14 * HH]], '#3a2a1e', 0.1 * HH, 1.2 * u); p.poly(rrect(tcx - 8 * u, torsoBot - 0.2 * HH, tcx + 8 * u, torsoBot - 0.08 * HH, 2 * u), '#e8c45a', 2 * u);
  if (S.apron) { const ap = [[tcx - 0.62 * T.a, chin + 0.46 * HH], [tcx + 0.62 * T.a, chin + 0.46 * HH], [tcx + 0.84 * T.a, torsoBot + 0.03 * HH], [tcx - 0.84 * T.a, torsoBot + 0.03 * HH]]; p.shadedFill(ap, S.apron, mul(S.apron, [0.8, 0.78, 0.8]), light, T.a, 0.3); p.poly(ap, null, ow * 0.8); p.stroke([[tcx - 0.5 * T.a, chin + 0.46 * HH], [tcx - 0.3 * T.a, chin + 0.06 * HH]], 3.2 * u); p.stroke([[tcx + 0.5 * T.a, chin + 0.46 * HH], [tcx + 0.3 * T.a, chin + 0.06 * HH]], 3.2 * u); }
  if (S.watch) { p.stroke(curve([tcx - 0.55 * T.a, chin + 0.3 * HH], [tcx, chin + 0.66 * HH], [tcx + 0.35 * T.a, chin + 0.34 * HH]), 3.4 * u, '#e8c45a'); p.dot(tcx + 0.05 * T.a, chin + 0.58 * HH, 5.5 * u, '#f3d66a'); }
  // arms (near/far identical in this simple stick style)
  const swing = (side) => Math.sin(Math.PI * 2 * (step + (side > 0 ? 0 : 0.5)));
  const armOf = (side, pose) => {
    const s = sh(side), X = (k) => tcx + side * (T.a * 1.1 + k * u), sw = swing(side);
    switch (pose) {
      case 'pump': return [s, [X(26), s[1] + 0.34 * HH], [X(14), s[1] + 0.06 * HH - sw * 0.2 * HH]];
      case 'swing': return [s, [X(10), s[1] + 0.3 * HH], [X(8 + sw * 6), s[1] + 0.5 * HH - sw * 0.25 * HH]];
      case 'cheer': return [s, [X(20), s[1] - 0.28 * HH], [X(26), s[1] - 0.78 * HH]];
      case 'hip': return [s, [X(26), s[1] + 0.3 * HH], [tcx + side * T.a * 0.95, torsoBot - 0.3 * HH]];
      case 'tool': return [s, [X(30), s[1] + 0.3 * HH], [X(16), s[1] + 0.02 * HH]];
      case 'point': return [s, [X(30), s[1] - 0.02 * HH], [X(66), s[1] - 0.12 * HH]];
      case 'dig': return side > 0 ? [s, [X(16), s[1] + (0.22 + 0.2 * dd) * HH], [tcx + 12 * u, chin + (0.2 + 0.6 * dd) * HH]] : [s, [X(8), s[1] + (0.4 + 0.2 * dd) * HH], [tcx - 4 * u, chin + (0.5 + 0.55 * dd) * HH]];
      case 'cross': return [s, [X(-6), s[1] + 0.4 * HH], [tcx - side * 0.5 * T.a, chin + (0.5 + 0.04 * side) * HH]];
      case 'mouth': return [s, [X(36), s[1] - 0.12 * HH], [cx + side * 0.74 * H.a, hc + 0.5 * H.b]];
      case 'hold': return [s, [X(16), s[1] + 0.42 * HH], [tcx + side * 11 * u, chin + 0.62 * HH]];
      case 'count': return [s, [X(10), s[1] + 0.46 * HH], [tcx + side * 18 * u, chin + 0.78 * HH]];
      default: return [s, [X(4), s[1] + 0.48 * HH], [X(3), chin + 1.0 * HH]];
    }
  };
  if (toolFront && (R === 'tool' || L === 'tool')) { const side = R === 'tool' ? 1 : -1, a = armOf(side, 'tool'); hand.p = a[2]; hand.side = side; toolAt(p, S.tool, a[2], side * -toolAng, 1.45 * HH, u); }
  if (toolFront && R === 'dig') { const a = armOf(1, 'dig'); toolAt(p, S.tool, a[2], 172 + 8 * dd, 1.45 * HH, u); }
  for (const [side, pose] of [[-1, L], [1, R]]) { const a = armOf(side, pose); p.stroke(curve(a[0], a[1], a[2]), 5.2 * u, armCol); p.ell(a[2][0], a[2][1], 7 * u, 7 * u, skin, 2.6 * u); }
  // head
  p.rot = [rad(tilt + headTilt), cx, chin + 0.1 * HH];
  const hp = blobPts(cx, hc, H);
  for (const s of [-1, 1]) p.ell(cx + s * 0.97 * H.a, hc + 0.12 * H.b, 0.13 * H.a, 0.2 * H.b, skin, ow * 0.8);
  if (S.braids) for (const s of [-1, 1]) { const bx = cx + s * 1.0 * H.a; p.poly([[bx, hc - 0.2 * H.b], [bx + s * 0.22 * H.a, hc + 0.3 * H.b], [bx + s * 0.16 * H.a, hc + 1.15 * H.b], [bx - s * 0.02 * H.a, hc + 1.05 * H.b]], S.hair, ow * 0.8); p.dot(bx + s * 0.1 * H.a, hc + 1.12 * H.b, 7 * u, '#d9473a'); }
  p.shadedFill(hp, skin, mul(skin, SHN), light, H.a, 0.45); p.inkRing(hp, ow * 1.1, thick);
  p.g.save(); p.g.globalAlpha = 0.35; for (const s of [-1, 1]) p.ell(cx + s * 0.6 * H.a, hc + 0.3 * H.b, 0.2 * H.a, 0.1 * H.b, '#f06a5a', 0); p.g.restore();
  p.clip(hp, () => { if (S.hat === 'cowboy' || S.hat === 'straw' || S.hat === 'floppy') { /* hat shades forehead */ } });
  if (S.beard && S.beard[0] === 'full') beardDraw(p, S, H, cx, hc, light, ow, u, hp);
  faceFront(p, cx, hc + 0.04 * HH, W, expr, facing, look, lid, !!S.hat && S.hat !== 'none', skin, null, !!S.stout);
  noseDraw(p, S, cx, hc, u, H);
  beardDraw(p, S.beard && S.beard[0] === 'full' ? { ...S, beard: null, mutton: S.mutton } : S, H, cx, hc, light, ow, u, hp);
  hatDraw(p, S, H, cx, hc, light, ow * 0.85, u);
  if (S.lashes) for (const s of [-1, 1]) p.stroke([[cx + s * 13 * u + 7 * u * facing + s * 8 * u, hc - 4 * u], [cx + s * 13 * u + 7 * u * facing + s * 14 * u, hc - 10 * u]], 2.4 * u);
  p.rot = null;
};

// ---------- side-view runner (faces right; flip the card with sx = -1) ----------
const ikK = (hip, ank, l1, l2) => { const dx = ank[0] - hip[0], dy = ank[1] - hip[1], d = clamp(Math.hypot(dx, dy), 1, l1 + l2 - 0.01), A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)), k = Math.atan2(dy, dx) - A; return [hip[0] + l1 * Math.cos(k), hip[1] + l1 * Math.sin(k)]; };
export const goldSide = (p, key, o = {}) => {
  const S = typeof key === 'string' ? MINERS[key] : key;
  const { expr = 'neutral', blink = 0, phase = 0, stride = 1.15, lean = 12, light = rad(-120), toolAng = 100, tool = true, arms = 'run', lift = 150, swingA = 55 } = o;
  const Bd = WB[S.build || 'normal'], H = { ...gHead(S, 1), asym: 0.12 }, W = 2 * H.a, HH = 2 * H.b, u = W / 100, lid = lidOf(blink), skin = S.skin;
  const sole = 975, ankY = sole - 4 * u, legLen = (Bd.legs + 0.1) * HH - 4 * u, l1 = legLen / 2, cx = 300;
  const thick = thickAngle(light), ow = 5 * u, nearCol = mix(S.pants, INK, 0.55), farCol = mix(S.pants, INK, 0.75), armCol = mix(S.shirt, INK, 0.5);
  const st = (ph) => { const c = ((phase + ph) % 1 + 1) % 1, Sx = 320 * stride; if (c < 0.42) { const s = c / 0.42; return { x: Sx / 2 - Sx * s, h: 0, stance: true, s }; } const s = (c - 0.42) / 0.58; return { x: -Sx / 2 + Sx * s - Sx / Math.PI * 0.3 * Math.sin(2 * Math.PI * s), h: lift * Math.sin(Math.PI * s), stance: false, s }; };
  const nL = st(0), fL = st(0.5), stance = nL.stance ? nL : fL;
  const hipY = ankY - Math.sqrt(Math.max(1, (legLen * 0.97) ** 2 - stance.x ** 2)) - 0.03 * HH * Math.max(0, Math.sin(Math.PI * 2 * 2 * (phase + 0.05)));
  const hipX = cx - 8 * u;
  p.rot = null;
  // back items
  if (S.tool && tool) { /* tool drawn later over the hands */ }
  for (const [Lg, near] of [[fL, false], [nL, true]]) {
    const ank = [cx + Lg.x, ankY - Lg.h], hip = [hipX, hipY], kn = ikK(hip, ank, l1, l1), col = near ? nearCol : farCol;
    p.stroke([hip, kn, ank], 6 * u, col);
    const pitch = Lg.stance ? 0 : rad(-30 * Math.sin(Math.PI * Lg.s)); p.g.save();
    p.ell(ank[0] + 8 * u, ank[1] + 1 * u, 16 * u, 7 * u, S.boots, 3.4 * u, 0, 360, pitch * 180 / Math.PI); p.g.restore();
  }
  p.rot = [rad(lean), hipX, hipY];
  const torsoL = Bd.torso * HH, torsoBot = hipY + 0.12 * HH, chin = torsoBot - torsoL, hc = chin - H.b;
  const T = { a: 0.34 * W * Bd.tw * 1.1, b: 0.5 * (torsoBot - (chin - 0.25 * HH)), nTop: 2.2, nBot: 2.6, egg: 0.1, asym: 0.1, rot: 0, noise: 0.012, seed: S.seed + 7 };
  const tcx = hipX + 6 * u, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
  if (S.bag !== false && (S.tool === 'pick' || S.tool === 'pan' || S.bag)) { const bg = rrect(tcx - T.a * 1.5, chin + 0.12 * HH, tcx - T.a * 0.5, torsoBot - 0.08 * HH, 14 * u); p.shadedFill(bg, '#8a6a42', '#5a432a', light, T.a); p.poly(bg, null, ow * 0.8); p.ell(tcx - T.a * 1.0, chin + 0.1 * HH, 0.45 * T.a, 0.14 * HH, '#c9a86a', ow * 0.8); }
  if (S.skirt) { const sk = [[tcx - 0.8 * T.a, torsoBot - 0.2 * HH], [tcx + 0.7 * T.a, torsoBot - 0.2 * HH], [tcx + 1.2 * T.a, torsoBot + 0.5 * HH], [tcx - 1.3 * T.a, torsoBot + 0.55 * HH]]; p.shadedFill(sk, S.skirt, mul(S.skirt, [0.65, 0.6, 0.7]), light, T.a); p.poly(sk, null, ow * 0.8); }
  p.shadedFill(tp, S.shirt, mul(S.shirt, SH_CLOTH), light, T.a, 0.42); p.inkRing(tp, ow, thick);
  if (S.suspenders) p.clip(tp, () => p.stroke([[tcx + 0.3 * T.a, chin - 0.1 * HH], [tcx + 0.1 * T.a, torsoBot]], 7 * u, S.suspenders));
  if (S.vest) p.clip(tp, () => p.poly([[tcx + 0.1 * T.a, chin], [tcx + 1.1 * T.a, chin], [tcx + 1.1 * T.a, torsoBot], [tcx + 0.1 * T.a, torsoBot]], S.vest, 0));
  p.band([[tcx - T.a * 0.9, torsoBot - 0.14 * HH], [tcx + T.a * 0.9, torsoBot - 0.14 * HH]], '#3a2a1e', 0.1 * HH, 1.2 * u);
  // arms: pumping, opposite to the near leg
  const shd = [tcx + 2 * u, chin + 0.14 * HH], aL = 0.48 * HH;
  const arm = (swg, bend) => { const el = [shd[0] + aL * Math.sin(swg), shd[1] + aL * Math.cos(swg)], fa = swg + bend, ha = [el[0] + aL * 0.9 * Math.sin(fa), el[1] + aL * 0.9 * Math.cos(fa)]; return [shd, el, ha]; };
  const sw = Math.sin(Math.PI * 2 * phase), A = rad(swingA); let farArm, nearArm;
  if (arms === 'cross') { const e = [shd[0] + 4 * u, shd[1] + 0.46 * HH], h1 = [shd[0] + 0.62 * T.a + 8 * u, shd[1] + 0.5 * HH]; nearArm = [shd, e, h1]; farArm = [shd, [e[0] - 4 * u, e[1] + 3 * u], [h1[0] - 8 * u, h1[1] - 6 * u]]; }
  else if (arms === 'pull') { const e = [shd[0] + 0.3 * aL, shd[1] + 0.85 * aL], h1 = [e[0] + 0.9 * aL, e[1] + 0.15 * aL]; nearArm = [shd, e, h1]; farArm = [shd, [e[0] - 3 * u, e[1]], [h1[0] - 8 * u, h1[1] - 4 * u]]; }
  else { const bend = arms === 'run' ? rad(75) : arms === 'hang' ? 0.12 : rad(48); farArm = arm(-A * sw, bend); nearArm = arm(A * sw, bend); }
  p.stroke(farArm, 5.2 * u, mix(armCol, INK, 0.3)); p.ell(farArm[2][0], farArm[2][1], 6.5 * u, 6.5 * u, mul(skin, [0.85, 0.8, 0.8]), 2.4 * u);
  p.stroke(nearArm, 5.2 * u, armCol); p.ell(nearArm[2][0], nearArm[2][1], 7 * u, 7 * u, skin, 2.6 * u);
  if (tool && S.tool && S.tool !== 'none') toolAt(p, S.tool, nearArm[2], toolAng, 1.35 * HH, u);
  // head
  const hx = tcx + 14 * u, hhc = hc;
  const hp = blobPts(hx, hhc, H);
  if (S.braids) { p.poly([[hx - H.a * 0.9, hhc - 0.2 * H.b], [hx - H.a * 1.25, hhc + 0.4 * H.b], [hx - H.a * 1.2, hhc + 1.2 * H.b], [hx - H.a * 0.85, hhc + 0.9 * H.b]], S.hair, ow * 0.8); p.dot(hx - H.a * 1.1, hhc + 1.1 * H.b, 7 * u, '#d9473a'); }
  p.ell(hx - 0.1 * H.a, hhc + 0.12 * H.b, 0.14 * H.a, 0.2 * H.b, skin, ow * 0.8);
  p.shadedFill(hp, skin, mul(skin, SHN), light, H.a, 0.45); p.inkRing(hp, ow * 1.1, thick);
  p.g.save(); p.g.globalAlpha = 0.35; p.ell(hx + 0.3 * H.a, hhc + 0.3 * H.b, 0.2 * H.a, 0.1 * H.b, '#f06a5a', 0); p.g.restore();
  if (S.beard && S.beard[0] === 'full') beardDraw(p, S, H, hx, hhc, light, ow, u, hp, 1);
  faceSide(p, hx, hhc + 0.04 * HH, W, expr, lid, !!S.hat && S.hat !== 'none', skin, null, !!S.stout);
  noseDraw(p, S, hx, hhc, u, H, 1);
  beardDraw(p, S.beard && S.beard[0] === 'full' ? { ...S, beard: null } : S, H, hx, hhc, light, ow, u, hp, 1);
  hatDraw(p, S, H, hx, hhc, light, ow * 0.85, u, 1);
  p.rot = null;
};

// ---------- western fx cards (design space 600x1000, centre 300,500) ----------
export const fxStar4 = (p, t, col = '#fff3b0', r = 120) => {
  const g = p.g, k = Math.sin(Math.min(1, Math.max(0, t)) * Math.PI), s = r * k; if (s < 2) return;
  g.save(); g.translate(300, 500); g.rotate(t * 0.6); const pts = []; for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, rr = i % 2 ? s * 0.28 : s; pts.push([Math.cos(a) * rr, Math.sin(a) * rr]); } p.poly(pts, col, 6); g.restore();
};
export const fxNugget = (p, t = 0) => {
  const g = p.g; g.save(); g.translate(300, 500); const pts = [[-130, 40], [-90, -50], [-20, -90], [60, -70], [120, -10], [100, 70], [20, 100], [-70, 90]];
  p.poly(pts, '#f2b81f', 12); p.poly([[-70, -40], [-20, -70], [30, -55], [-10, -20], [-60, -10]], '#ffe27a', 0); p.poly([[40, 20], [90, 0], [85, 50], [40, 70]], '#c98a0c', 0); p.stroke([[-50, 55], [10, 62]], 7, '#ffe9a0');
  const k = (t * 3) % 1; if (t >= 0) { g.globalAlpha = Math.sin(k * Math.PI); p.poly([[60 - 40, -50], [60, -50 - 8], [60 + 40, -50], [60, -50 + 8]], '#ffffff', 0); }
  g.restore();
};
export const fxCoin = (p, t = 0, ch = '$') => {
  const g = p.g; g.save(); g.translate(300, 500); const sx = Math.max(0.12, Math.abs(Math.cos(t * Math.PI * 2))); g.scale(sx, 1);
  p.ell(0, 0, 130, 130, '#f2b81f', 12); p.ell(0, 0, 100, 100, '#ffd75a', 6); g.fillStyle = '#b87a0a'; g.font = "900 130px 'Arial Black', Impact, sans-serif"; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(ch, 0, 8); g.restore();
};
export const fxSpeed = (p, t, dir = 1, col = '#ffffff') => {
  const g = p.g; g.save(); for (let i = 0; i < 8; i++) { const k = (t * 2.2 + i * 0.173) % 1, y = 200 + (i * 97) % 640, len = 140 + (i % 3) * 70, x0 = 300 - dir * 220 + dir * k * 200; g.globalAlpha = 0.7 * Math.sin(k * Math.PI); p.stroke([[x0, y], [x0 - dir * len, y]], 7, col); } g.restore();
};
export const fxDustTrail = (p, k, col = '#e9cf9a') => {
  const g = p.g; g.save(); g.globalAlpha = Math.max(0, 1 - k * k);
  for (let i = 0; i < 6; i++) { const a = i * 1.1, r = 40 + 130 * k; p.ell(300 + Math.cos(a) * r, 700 + Math.sin(a) * r * 0.35 - 60 * k, 70 + 70 * k, 56 + 50 * k, col, 10); }
  g.restore();
};
export const fxSignText = (p, text, size = 96) => {
  const g = p.g; g.save(); g.translate(300, 500); g.font = `900 ${size}px 'Arial Black', Impact, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 16; g.strokeStyle = INK; g.lineJoin = 'round'; g.strokeText(text, 0, 0); g.fillStyle = '#ffe9a0'; g.fillText(text, 0, 0); g.restore();
};

// ---------- more fx cards ----------
export const fxPan = (p, t = 0) => {
  const g = p.g; g.save(); g.translate(300, 500); g.rotate(-0.22);
  p.ell(0, 20, 250, 118, '#8f9ba7', 12); p.ell(0, 14, 220, 98, '#b7c2cc', 6); p.ell(0, 20, 200, 84, '#6a5a38', 0);
  p.ell(-40, 24, 150, 52, '#8a7545', 0); p.stroke([[-120, 8], [-30, 0], [70, 12]], 5, '#c9b27a');
  for (const [x, y, r] of [[-70, 30, 26], [10, 40, 34], [86, 22, 22]]) { p.poly([[x - r, y + 6], [x - r * 0.4, y - r * 0.8], [x + r * 0.7, y - r * 0.6], [x + r, y + r * 0.3], [x, y + r * 0.7]], '#f2b81f', 7); p.stroke([[x - r * 0.4, y - r * 0.3], [x + r * 0.2, y - r * 0.4]], 5, '#fff0a0'); }
  p.poly([[236, 8], [330, -14], [336, 8], [240, 30]], '#6a4a2c', 8);
  g.restore();
  const k = (t * 2.4) % 1; g.save(); g.translate(300, 500); const sr = 70 * Math.sin(k * Math.PI); if (sr > 3) p.poly([[10, 20 - sr], [10 + sr * 0.28, 20 - sr * 0.28], [10 + sr, 20], [10 + sr * 0.28, 20 + sr * 0.28], [10, 20 + sr], [10 - sr * 0.28, 20 + sr * 0.28], [10 - sr, 20], [10 - sr * 0.28, 20 - sr * 0.28]], '#ffffff', 0); g.restore();
};
export const fxPaper = (p, t = 0, head = 'GOLD!', sub = 'FOUND IN CALIFORNIA') => {
  const g = p.g; g.save(); g.translate(300, 500); g.rotate(-0.05 + 0.03 * Math.sin(t * 6.28)); const pop_ = Math.min(1, t * 6 + 0.4); g.scale(pop_, pop_);
  p.poly(rrect(-250, -330, 250, 330, 14), '#efe4c4', 11); g.fillStyle = '#2a1a14'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = "900 40px 'Times New Roman', serif"; g.fillText('THE CALIFORNIA STAR', 0, -290); g.fillRect(-220, -262, 440, 5); g.fillRect(-220, -252, 440, 2);
  g.font = "900 190px 'Arial Black', Impact, sans-serif"; g.lineWidth = 14; g.strokeStyle = '#2a1a14'; g.lineJoin = 'round'; g.strokeText(head, 0, -130); g.fillStyle = '#c9262a'; g.fillText(head, 0, -130);
  g.fillStyle = '#2a1a14'; g.font = "900 44px 'Arial Black', Impact, sans-serif"; g.fillText(sub, 0, -22);
  p.poly(rrect(-210, 20, -20, 150, 6), '#d9c9a0', 5); p.poly([[-190, 130], [-120, 50], [-60, 110], [-40, 90], [-30, 130]], '#8aa070', 0); p.dot(-80, 62, 12, '#f2b81f');
  for (let i = 0; i < 5; i++) { g.fillRect(10, 30 + i * 28, 230, 8); g.fillRect(-210, 175 + i * 28, 450, 8); }
  g.restore();
};
export const fxCoinStack = (p, n = 3) => {
  const g = p.g; g.save(); g.translate(300, 500);
  const stacks = [[-120, 5], [0, 7], [120, 4]].slice(0, Math.max(1, Math.min(3, n)));
  for (const [x, h] of stacks) for (let i = 0; i < h; i++) { const y = 130 - i * 30; p.ell(x, y, 62, 22, '#e0a512', 6); p.ell(x, y - 9, 62, 22, '#ffd75a', 6); }
  for (const [x, h] of stacks) p.ell(x, 130 - h * 30 - 10, 40, 11, '#ffe9a0', 0);
  g.restore();
};
export const fxBag = (p) => {
  const g = p.g; g.save(); g.translate(300, 500);
  p.poly([[-90, -70], [-60, -130], [-10, -100], [40, -130], [90, -70], [150, 40], [120, 130], [0, 160], [-120, 130], [-150, 40]], '#c9a86a', 10);
  p.poly([[-70, -80], [70, -80], [60, -60], [-60, -60]], '#a8864a', 6); p.stroke([[-70, -70], [70, -70]], 8, '#5a3a20');
  g.fillStyle = '#4a3320'; g.font = "900 130px 'Arial Black', Impact, sans-serif"; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('$', 0, 40);
  g.restore();
};
export const fxStamp = (p, text, t = 1) => {
  const g = p.g, s = 1 + 1.4 * Math.max(0, 1 - Math.min(1, t * 5)); g.save(); g.translate(300, 500); g.rotate(-0.2); g.scale(s, s); g.globalAlpha = Math.min(1, t * 6);
  g.font = "900 150px 'Arial Black', Impact, sans-serif"; const w = g.measureText(text).width;
  p.poly(rrect(-w / 2 - 36, -105, w / 2 + 36, 105, 24), 'rgba(0,0,0,0)', 16); g.strokeStyle = '#c9262a'; g.lineWidth = 18; g.beginPath(); g.roundRect(-w / 2 - 36, -105, w + 72, 210, 24); g.stroke();
  g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineWidth = 22; g.strokeStyle = '#2a1a14'; g.lineJoin = 'round'; g.strokeText(text, 0, 6); g.fillStyle = '#d9372b'; g.fillText(text, 0, 6); g.restore();
};
export const fxPlate = (p, text, sub = '', t = 1) => {
  const g = p.g, k = Math.min(1, t * 1.15), sc = 1 - Math.pow(1 - k, 3) * 1 + 0.0; g.save(); g.translate(300, 500); g.scale(Math.max(0.05, sc), Math.max(0.05, sc));
  g.font = "900 84px 'Arial Black', Impact, sans-serif"; const w = Math.min(560, g.measureText(text).width + 90), h = sub ? 230 : 160;
  p.poly(rrect(-w / 2, -h / 2, w / 2, h / 2, 18), '#c99a5a', 12); g.fillStyle = 'rgba(60,30,10,0.2)'; for (let i = 1; i < 4; i++) g.fillRect(-w / 2 + 8, -h / 2 + i * h / 4, w - 16, 3);
  p.poly(rrect(-w / 2 + 14, -h / 2 + 14, w / 2 - 14, h / 2 - 14, 10), null, 5);
  const fs = Math.min(84, (w - 60) / (text.length * 0.66)); g.font = `900 ${fs}px 'Arial Black', Impact, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round'; g.lineWidth = fs * 0.16; g.strokeStyle = '#2a1a14';
  const ty = sub ? -30 : 0; g.strokeText(text, 0, ty); g.fillStyle = '#ffe9a0'; g.fillText(text, 0, ty);
  if (sub) { g.font = "900 46px 'Arial Black', Impact, sans-serif"; g.lineWidth = 8; g.strokeText(sub, 0, 52); g.fillStyle = '#ffffff'; g.fillText(sub, 0, 52); }
  g.restore();
};
export const fxShovelIcon = (p, t = 0) => {
  const g = p.g; g.save(); g.translate(300, 500); g.rotate(0.5 + 0.05 * Math.sin(t * 6.28));
  p.stroke([[0, -200], [0, 70]], 34, INK); p.stroke([[0, -200], [0, 70]], 22, '#8a5a30'); p.poly([[-60, 60], [60, 60], [90, 150], [0, 230], [-90, 150]], '#aab4be', 12); p.stroke([[0, 90], [0, 190]], 8, '#e6edf3');
  p.poly([[-40, -230], [40, -230], [40, -200], [-40, -200]], '#8a5a30', 9);
  g.restore();
};
export const fxBangText = (p, text, t = 1) => {
  const g = p.g, s = Math.min(1.1, 0.3 + t * 2.2); g.save(); g.translate(300, 500); g.scale(s, s); g.rotate(-0.1);
  const pts = []; for (let i = 0; i < 28; i++) { const a = i / 28 * Math.PI * 2, r = i % 2 ? 190 : 270; pts.push([Math.cos(a) * r * 1.25, Math.sin(a) * r * 0.9]); }
  p.poly(pts, '#ffd83a', 14);
  g.font = "900 150px 'Arial Black', Impact, sans-serif"; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round'; g.lineWidth = 26; g.strokeStyle = '#2a1a14'; g.strokeText(text, 0, 8); g.fillStyle = '#d9372b'; g.fillText(text, 0, 8);
  g.restore();
};
export const fxCrate = (p) => {
  const g = p.g; g.save(); g.translate(300, 500);
  p.poly(rrect(-170, -140, 170, 140, 10), '#b98a52', 12); for (const y of [-70, 0, 70]) p.stroke([[-165, y], [165, y]], 6, '#7a5230'); p.stroke([[-165, -135], [165, 135]], 14, '#8a6238'); p.stroke([[-165, 135], [165, -135]], 14, '#8a6238');
  g.restore();
};
export const fxDirt = (p, k) => {
  const g = p.g; g.save(); g.globalAlpha = Math.max(0, 1 - k);
  for (let i = 0; i < 9; i++) { const a = -0.9 - i * 0.2 + (i % 2) * 0.3, r = 40 + 210 * k * (0.6 + (i % 3) * 0.25), x = 300 + Math.cos(a) * r * 1.2, y = 600 + Math.sin(a) * r - 150 * k * k * 2; p.poly(ellPts(x, y, 24 - i, 17 - i * 0.6, 0, 360, i * 0.5), i % 2 ? '#8a5e38' : '#a87848', 6); }
  g.restore();
};
