// ---------------- ocean animals + FX (design box 600x1000, centre 300,500) ----------------
const _tab = (tab, u) => { for (let i = 1; i < tab.length; i++) if (u <= tab[i][0]) { const [u0, w0] = tab[i - 1], [u1, w1] = tab[i], k = (u - u0) / (u1 - u0), s = k * k * (3 - 2 * k); return w0 + (w1 - w0) * s; } return tab[tab.length - 1][1]; };
const WHALE = { L: 540, H: 100, topK: 0.9, botK: 1.1, body: '#34506b', belly: '#e6eef2', line: '#8fa6b6', tab: [[0, 0], [0.015, 0.45], [0.06, 0.8], [0.15, 0.97], [0.3, 1], [0.45, 0.92], [0.6, 0.7], [0.75, 0.45], [0.88, 0.22], [0.96, 0.1], [1, 0.05]] };
const ORCA = { L: 470, H: 72, topK: 0.95, botK: 1.0, body: '#1c2430', belly: '#f4f6fa', tab: [[0, 0], [0.02, 0.5], [0.08, 0.85], [0.2, 1], [0.35, 1], [0.5, 0.85], [0.65, 0.6], [0.8, 0.38], [0.92, 0.18], [1, 0.06]] };

const swimmer = (p, o, S, kind) => {
  const g = p.g, cx = 300, cy = 500, n = 40, L = S.L, ph = (o.t || 0) * Math.PI * 2, amp = o.amp ?? 14, sil = o.sil || null;
  const col = (c) => sil || c, INKC = sil || INK;
  g.save(); g.translate(cx, cy); g.rotate(((o.rot || 0) * Math.PI) / 180); g.scale(1, o.vy ?? 1); g.translate(-cx, -cy);
  const sp = [], up = [], dd = [];
  for (let i = 0; i <= n; i++) { const u = i / n; sp.push([cx + L * (0.5 - u), cy + amp * (0.1 + 0.9 * Math.pow(u, 1.5)) * Math.sin(ph - 5.5 * u)]); }
  for (let i = 0; i <= n; i++) { const a = sp[Math.max(0, i - 1)], b = sp[Math.min(n, i + 1)]; let dx = b[0] - a[0], dy = b[1] - a[1]; const m = Math.hypot(dx, dy) || 1; dx /= m; dy /= m; dd.push([dx, dy]); up.push([-dy, dx]); }
  const wt = (i) => S.H * _tab(S.tab, i / n) * S.topK, wb = (i) => S.H * _tab(S.tab, i / n) * S.botK;
  const top = sp.map((s, i) => [s[0] + up[i][0] * wt(i), s[1] + up[i][1] * wt(i)]), bot = sp.map((s, i) => [s[0] - up[i][0] * wb(i), s[1] - up[i][1] * wb(i)]);
  const at = (u, off) => { const i = Math.round(u * n); return [sp[i][0] + up[i][0] * off, sp[i][1] + up[i][1] * off]; };
  // flukes (behind)
  { const P = sp[n], d = dd[n], N = up[n], fs = 1 + (o.fluke || 0) * 0.45, fl = kind === 'whale' ? 1 : 0.62;
    const pt = (a, b) => [P[0] + d[0] * a + N[0] * b, P[1] + d[1] * a + N[1] * b];
    p.poly([pt(0, 0), pt(30 * fl, 70 * fs * fl), pt(72 * fl, 108 * fs * fl), pt(58 * fl, 56 * fs * fl), pt(40 * fl, 0), pt(58 * fl, -56 * fs * fl), pt(72 * fl, -108 * fs * fl), pt(30 * fl, -70 * fs * fl)], col(S.body), 11); }
  // far flipper (behind body)
  const flip = (sc, alpha) => {
    const i = Math.round(0.3 * n), B = [sp[i][0] - up[i][0] * wb(i) * 0.8, sp[i][1] - up[i][1] * wb(i) * 0.8], d = dd[i], a = 0.55 + 0.7 * (o.flip || 0), Lf = (kind === 'whale' ? 0.3 : 0.18) * L * sc;
    const dir = [d[0] * Math.cos(a) - up[i][0] * Math.sin(a), d[1] * Math.cos(a) - up[i][1] * Math.sin(a)], pp = [-dir[1], dir[0]], Wf = (kind === 'whale' ? 22 : 30) * sc;
    const ks = [0, 0.25, 0.55, 0.85, 1], ws = [0.7, 1, 0.9, 0.5, 0.05], A = [], Bq = [];
    ks.forEach((k, j) => { A.push([B[0] + dir[0] * Lf * k + pp[0] * Wf * ws[j], B[1] + dir[1] * Lf * k + pp[1] * Wf * ws[j]]); Bq.push([B[0] + dir[0] * Lf * k - pp[0] * Wf * ws[j], B[1] + dir[1] * Lf * k - pp[1] * Wf * ws[j]]); });
    p.poly([...A, ...Bq.reverse()], col(alpha), 11);
  };
  flip(0.85, kind === 'whale' ? '#27415a' : '#141b26');
  // body
  const outline = [...top, ...bot.slice().reverse()];
  p.poly(outline, col(S.body), 13);
  if (!sil) {
    // belly
    const bl = [], inner = []; for (let i = 2; i <= Math.round(n * (kind === 'whale' ? 0.82 : 0.6)); i++) { bl.push(bot[i]); inner.push([sp[i][0] - up[i][0] * wb(i) * (kind === 'whale' ? 0.42 : 0.5), sp[i][1] - up[i][1] * wb(i) * (kind === 'whale' ? 0.42 : 0.5)]); }
    p.poly([...bl, ...inner.reverse()], S.belly, 0);
    if (kind === 'whale') for (let k = 0; k < 6; k++) { const off = 0.5 + k * 0.08, pts = []; for (let i = 4; i <= 20; i++) pts.push([sp[i][0] - up[i][0] * wb(i) * off, sp[i][1] - up[i][1] * wb(i) * off]); p.stroke(pts, 3, S.line); }
    p.stroke([...top, ...bot.slice().reverse(), top[0]], 12, INK);
    if (kind === 'orca') { // eye patch + saddle
      const e = at(0.17, wt(7) * 0.55); p.ell(e[0], e[1], 30, 13, '#ffffff', 0);
      const sd = at(0.5, wt(20) * 0.85); p.ell(sd[0], sd[1], 36, 12, '#aab4c2', 0);
    }
  }
  // dorsal
  { const u0 = kind === 'whale' ? 0.62 : 0.31, u1 = kind === 'whale' ? 0.73 : 0.47, i0 = Math.round(u0 * n), i1 = Math.round(u1 * n), ia = Math.round((u0 + (u1 - u0) * 0.35) * n), hgt = kind === 'whale' ? 34 : 118, sw = kind === 'whale' ? 26 : 62;
    const A = top[i0], B = top[i1], T = [top[ia][0] + dd[ia][0] * sw + up[ia][0] * hgt, top[ia][1] + dd[ia][1] * sw + up[ia][1] * hgt];
    p.poly([A, [(A[0] + T[0]) / 2 + up[ia][0] * 8, (A[1] + T[1]) / 2 + up[ia][1] * 8], T, [(B[0] + T[0]) / 2 - dd[ia][0] * 12, (B[1] + T[1]) / 2 - dd[ia][1] * 12], B], col(S.body), 11); }
  if (!sil) {
    // head details
    const mo = o.mouth || 0;
    if (kind === 'whale') {
      for (let k = 0; k < 5; k++) { const q = at(0.03 + k * 0.035, wt(2 + k * 1.4) * 0.97); p.ell(q[0], q[1], 7, 6, '#6a8296', 0); }
      const m0 = at(0.012, -wb(1) * 0.22), m1 = at(0.12, -wb(5) * 0.5), m2 = at(0.27, -wb(11) * 0.5), mp = [];
      for (let k = 0; k <= 10; k++) { const t = k / 10, x = m0[0] + (m2[0] - m0[0]) * t, y = m0[1] + (m1[1] - m0[1]) * Math.sin(t * Math.PI * 0.5) * 1.0 + (m2[1] - m0[1]) * t * t * 0.4; mp.push([x, y]); }
      if (mo > 0.05) { const lower = mp.map(([x, y], k) => [x, y + mo * 32 * Math.sin((k / 10) * Math.PI * 0.9 + 0.3)]); p.poly([...mp, ...lower.slice().reverse()], '#7a1d2a', 6); }
      else p.stroke(mp, 6, INK);
      const e = at(0.15, -wb(6) * 0.3);
      if (o.eye === 'closed') p.stroke([[e[0] - 11, e[1]], [e[0], e[1] + 5], [e[0] + 11, e[1]]], 5, INK);
      else { p.ell(e[0], e[1], o.eye === 'wide' ? 13 : 10, o.eye === 'wide' ? 13 : 10, '#ffffff', 5); p.ell(e[0] + 2, e[1], o.eye === 'wide' ? 5 : 6, o.eye === 'wide' ? 5 : 6, '#12202c', 0); }
    } else {
      const m0 = at(0.015, -wb(1) * 0.2), m1 = at(0.17, -wb(7) * 0.45), mp = []; for (let k = 0; k <= 8; k++) { const t = k / 8; mp.push([m0[0] + (m1[0] - m0[0]) * t, m0[1] + (m1[1] - m0[1]) * t * t]); }
      if (mo > 0.05) { const lower = mp.map(([x, y], k) => [x, y + mo * 40 * Math.sin((k / 8) * Math.PI * 0.8 + 0.2)]); p.poly([...mp, ...lower.slice().reverse()], '#7a1d2a', 6); for (let k = 1; k < 8; k += 2) { const a = mp[k], b = lower[k]; p.poly([[a[0] - 6, a[1]], [a[0] + 6, a[1]], [a[0], a[1] + 14 * mo]], '#ffffff', 2); } }
      else p.stroke(mp, 6, INK);
      const e = at(0.12, wt(5) * 0.1); p.ell(e[0], e[1], 7, 7, '#ffffff', 3); p.ell(e[0] + 1, e[1], 4, 4, '#101418', 0);
      const sad = o.eye === 'wide'; p.stroke([[e[0] - 16, e[1] - (sad ? 12 : 8)], [e[0] + 14, e[1] - (sad ? 18 : 2) ]], 7, INK);
    }
  }
  // near flipper
  flip(1.0, kind === 'whale' ? '#2a4660' : '#1a222e');
  if (o.dizzy) { for (let k = 0; k < 3; k++) { const a = (o.t || 0) * 12 + k * 2.1, e = at(0.1, wt(4) + 40); const x = e[0] + Math.cos(a) * 34, y = e[1] + Math.sin(a) * 12; p.poly([[x, y - 12], [x + 4, y - 4], [x + 12, y], [x + 4, y + 4], [x, y + 12], [x - 4, y + 4], [x - 12, y], [x - 4, y - 4]], '#ffd84a', 3); } }
  g.restore();
};
export const fxWhale = (p, o = {}) => swimmer(p, o, WHALE, 'whale');
export const fxOrca = (p, o = {}) => swimmer(p, o, ORCA, 'orca');

/** cute seal facing right. o: t, scared, limp, rot */
export const fxSeal = (p, o = {}) => {
  const g = p.g, sh = o.scared ? Math.sin((o.t || 0) * Math.PI * 2 * 6) * 3 : 0, bob = Math.sin((o.t || 0) * Math.PI * 2) * 5;
  g.save(); g.translate(300 + sh, 500 + bob); g.rotate(((o.rot || 0) * Math.PI) / 180); g.translate(-300, -500);
  p.poly([[80, 590], [20, 560], [50, 610], [10, 640], [90, 620]], '#8a95a3', 10);
  p.ell(260, 545, 170, 82, '#9aa6b2', 12); p.ell(270, 590, 130, 40, '#dfe5ea', 0);
  for (const [x, y] of [[190, 510], [240, 495], [300, 510], [215, 545], [275, 535]]) p.ell(x, y, 9, 7, '#6f7b88', 0);
  p.ell(345, 600, 34, 17, '#8a95a3', 10);
  const hy = o.limp ? 505 : 478;
  p.ell(420, hy, 62, 56, '#9aa6b2', 12); p.ell(446, hy + 22, 36, 26, '#dfe5ea', 8);
  p.ell(470, hy + 12, 11, 8, '#14181e', 0);
  const er = o.scared ? 15 : 12;
  if (o.limp) { p.stroke([[395, hy - 8], [418, hy - 2]], 6, INK); p.stroke([[430, hy - 8], [452, hy - 2]], 6, INK); }
  else { p.ell(402, hy - 10, er, er + 2, '#ffffff', 5); p.ell(438, hy - 10, er, er + 2, '#ffffff', 5); p.ell(405, hy - 9, o.scared ? 4 : 7, o.scared ? 4 : 7, '#101418', 0); p.ell(441, hy - 9, o.scared ? 4 : 7, o.scared ? 4 : 7, '#101418', 0); }
  for (const dy of [-6, 4]) { p.stroke([[452, hy + 22 + dy], [500, hy + 14 + dy * 2]], 3, '#ffffffcc'); }
  if (o.scared) { p.poly([[388, hy - 50], [378, hy - 20], [398, hy - 20]], '#8fd0ff', 3); }
  g.restore();
};
/** orca dorsal fin breaking the surface, with V wake (bottom at design y=700) */
export const fxFin = (p, t) => {
  const g = p.g, w = Math.sin(t * Math.PI * 2) * 6;
  g.save(); g.globalAlpha = 0.9; p.stroke([[300, 700], [110 + w, 730]], 8, '#ffffffcc'); p.stroke([[300, 700], [490 - w, 730]], 8, '#ffffffcc'); p.stroke([[300, 700], [180 + w, 760]], 5, '#ffffff88'); p.stroke([[300, 700], [420 - w, 760]], 5, '#ffffff88'); g.restore();
  p.poly([[240, 700], [270, 560], [335, 380], [350, 520], [372, 700]], '#1c2430', 13);
  p.poly([[262, 700], [275, 610], [300, 650], [300, 700]], '#2d3a4c', 0);
};
export const fxBubbles = (p, t) => {
  const g = p.g;
  for (let i = 0; i < 14; i++) { const k = (t * 0.8 + i / 14) % 1, x = 90 + ((i * 97) % 420) + Math.sin(k * 9 + i) * 14, y = 900 - k * 820, r = 10 + (i % 4) * 7; g.save(); g.globalAlpha = Math.sin(k * Math.PI) * 0.9; g.lineWidth = 4; g.strokeStyle = '#ffffff'; g.fillStyle = 'rgba(255,255,255,0.22)'; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); g.stroke(); g.restore(); }
};
export const fxWSplash = (p, t) => {
  const g = p.g, e = Math.max(0, Math.min(1, t)), k = 1 - Math.pow(1 - e, 2.2);
  g.save(); g.globalAlpha = 1 - Math.pow(e, 3);
  for (let i = 0; i < 14; i++) { const a = -Math.PI * (0.14 + 0.72 * (i / 13)), v = 150 + 170 * (0.5 + 0.5 * Math.sin(i * 2.3)), tip = [300 + Math.cos(a) * v * k * 1.2, 700 + Math.sin(a) * v * k * 2.0 + 190 * k * k], base = [300 + Math.cos(a) * v * k * 0.45, 700 + Math.sin(a) * v * k * 0.8];
    p.stroke([base, tip], 20 * (1 - 0.6 * k), '#ffffff'); p.ell(tip[0], tip[1], 13, 13, '#ffffff', 0); }
  p.ell(300, 706, 60 + 160 * k, 26, '#ffffff', 0);
  g.restore();
};
export const fxRings = (p, t) => {
  const g = p.g; for (let i = 0; i < 3; i++) { const k = Math.max(0, Math.min(1, t * 1.2 - i * 0.18)); if (k <= 0) continue; g.save(); g.globalAlpha = (1 - k) * 0.95; g.lineWidth = 12 - 6 * k; g.strokeStyle = '#ffffff'; g.beginPath(); g.ellipse(300, 700, 40 + 280 * k, 12 + 50 * k, 0, 0, 7); g.stroke(); g.restore(); }
};
export const fxStreaks = (p, t) => {
  const g = p.g; for (let i = 0; i < 9; i++) { const y = 380 + i * 30 + (i % 2) * 6, k = (t * 3 + i * 0.37) % 1, x0 = 30 + k * 360, len = 120 + (i % 3) * 60; g.save(); g.globalAlpha = 0.75 * Math.sin(k * Math.PI); p.stroke([[x0, y], [x0 + len, y]], 8, '#ffffff'); g.restore(); }
};
export const fxBubbleShield = (p, t) => {
  const g = p.g, pu = 0.5 + 0.5 * Math.sin(t * Math.PI * 2 * 2), s = Math.min(1, t * 3.2 + 0.0);
  g.save(); g.translate(300, 500); g.scale(Math.max(0.01, s), Math.max(0.01, s));
  const gr = g.createRadialGradient(0, 0, 80, 0, 0, 290); gr.addColorStop(0, 'rgba(140,230,255,0.05)'); gr.addColorStop(0.8, 'rgba(120,225,255,0.30)'); gr.addColorStop(1, 'rgba(210,250,255,0.55)');
  g.fillStyle = gr; g.beginPath(); g.ellipse(0, 0, 150, 440, 0, 0, 7); g.fill();
  g.lineWidth = 10 + 4 * pu; g.strokeStyle = 'rgba(225,252,255,0.95)'; g.beginPath(); g.ellipse(0, 0, 150, 440, 0, 0, 7); g.stroke();
  g.lineWidth = 8; g.strokeStyle = 'rgba(255,255,255,0.75)'; g.beginPath(); g.ellipse(0, 0, 110, 400, 0, 3.6, 4.6); g.stroke();
  g.restore();
};
export const fxThoughtCloud = (p, t) => {
  const g = p.g, s = Math.min(1, t * 1.3), k = 1 - Math.pow(1 - s, 3); g.save(); g.translate(300, 500); g.scale(k, k);
  const bl = [[-170, 40, 150, 120], [-40, -60, 170, 130], [120, -20, 150, 120], [170, 80, 120, 100], [-10, 100, 190, 110], [-190, 120, 100, 80]];
  for (const [x, y, rx, ry] of bl) p.ell(x, y, rx, ry, '#ffffff', 14); for (const [x, y, rx, ry] of bl) p.ell(x, y, rx - 8, ry - 8, '#ffffff', 0);
  p.ell(-60, 270, 40, 32, '#ffffff', 12); p.ell(-100, 345, 22, 18, '#ffffff', 10); g.restore();
};
export const fxArc = (p, t) => {
  const g = p.g, k = Math.max(0, Math.min(1, t)); g.save(); g.globalAlpha = 1 - 0.5 * k; g.lineCap = 'round';
  for (const [r, w] of [[250, 18], [200, 10]]) { g.lineWidth = w; g.strokeStyle = '#ffffff'; g.beginPath(); g.arc(300, 500, r, -1.1 + 1.9 * k * 0.4, -1.1 + 1.9 * k, false); g.stroke(); }
  g.restore();
};
export const fxSparkles = (p, t) => {
  for (let i = 0; i < 8; i++) { const k = (t * 1.4 + i / 8) % 1, a = i * 2.4, x = 300 + Math.cos(a) * (120 + 140 * ((i * 5) % 3) / 2), y = 500 + Math.sin(a) * (90 + 120 * ((i * 3) % 3) / 2), r = 10 + 22 * Math.sin(k * Math.PI);
    p.poly([[x, y - r], [x + r * 0.28, y - r * 0.28], [x + r, y], [x + r * 0.28, y + r * 0.28], [x, y + r], [x - r * 0.28, y + r * 0.28], [x - r, y], [x - r * 0.28, y - r * 0.28]], '#fff7b0', 3); }
};
