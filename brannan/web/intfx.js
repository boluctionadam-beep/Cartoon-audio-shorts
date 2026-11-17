// ---------------- intuition-short FX (design box 600x1000, centre 300,500) ----------------
const _clampT = (t) => Math.max(0, Math.min(1, t));
/** pop-in label; lines split by \n; auto-fit to 540 design units */
export const fxLabel = (p, s, t = 1, size = 120, fill = "#ffffff", bg = null) => {
  const g = p.g, lines = s.split("\n"); g.save(); g.font = `900 ${size}px 'Arial Black', Impact, sans-serif`;
  let w = 0; for (const l of lines) w = Math.max(w, g.measureText(l).width);
  const k = Math.min(1, 540 / Math.max(1, w)), sc = pop(_clampT(t)) * k, lh = size * 1.08, y0 = -(lines.length - 1) * lh / 2;
  g.translate(300, 500); g.scale(sc, sc);
  if (bg) p.poly(rrect(-w / 2 - 34, y0 - size * 0.72, w / 2 + 34, y0 + (lines.length - 1) * lh + size * 0.72, 44), bg, 14);
  lines.forEach((l, i) => txt(p, l, 0, y0 + i * lh, size, fill, INK, Math.max(10, size * 0.15)));
  g.restore();
};
export const fxHeart = (p, t, beat = 1) => {
  const g = p.g, s = 1 + 0.14 * Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * beat)), 2);
  g.save(); g.translate(300, 500); g.scale(s, s);
  const pts = []; for (let i = 0; i <= 48; i++) { const a = i / 48 * Math.PI * 2, sn = Math.sin(a); pts.push([16 * sn * sn * sn * 12, -(13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)) * 12 + 20]); }
  p.poly(pts, "#ff3b4f", 18); p.ell(-90, -60, 38, 26, "#ffb0b8", 0); g.restore();
};
/** yellow lightning bolt pointing down; t = reveal 0..1 */
export const fxBolt = (p, t) => {
  const g = p.g; g.save(); g.beginPath(); g.rect(0, 0, 600, 170 + 660 * _clampT(t)); g.clip();
  p.poly([[40, 170], [-90, 520], [-5, 520], [-55, 830], [105, 440], [20, 440], [120, 170]].map(([x, y]) => [x + 300 - 20, y]), "#ffd84a", 16); g.restore();
};
/** rocket pointing right */
export const fxRocket = (p, t) => {
  const g = p.g; g.save(); g.translate(300, 500); g.rotate(Math.PI / 2);
  const fl = 90 + 40 * Math.sin(t * 60);
  p.poly([[-50, 150], [0, 150 + fl], [50, 150], [30, 120], [-30, 120]], "#ff9a1f", 12); p.poly([[-24, 140], [0, 140 + fl * 0.55], [24, 140]], "#ffe14a", 0);
  p.poly([[-70, 60], [-140, 190], [-70, 150]], "#e0362f", 12); p.poly([[70, 60], [140, 190], [70, 150]], "#e0362f", 12);
  p.poly([[0, -260], [70, -130], [76, 130], [-76, 130], [-70, -130]], "#f4f7fb", 14);
  p.poly([[0, -260], [70, -130], [-70, -130]], "#e0362f", 14);
  p.ell(0, -20, 40, 40, "#8fd0ff", 12); p.ell(-12, -32, 12, 12, "#ffffff", 0);
  g.restore();
};
/** snail crawling right */
export const fxSnail = (p, t) => {
  const g = p.g, w = Math.sin(t * 9) * 8;
  p.poly([[70, 700], [560, 700], [560, 640], [500, 620], [150, 640]], "#cbd77a", 14);
  p.ell(540, 640, 52, 56, "#cbd77a", 14);
  p.stroke([[550, 600], [572 + w, 500]], 14, INK); p.stroke([[550, 600], [572 + w, 500]], 7, "#cbd77a");
  p.stroke([[520, 600], [520 - w, 510]], 14, INK); p.stroke([[520, 600], [520 - w, 510]], 7, "#cbd77a");
  p.ell(572 + w, 494, 14, 14, "#ffffff", 8); p.ell(520 - w, 504, 14, 14, "#ffffff", 8); p.dot(576 + w, 494, 5); p.dot(524 - w, 504, 5);
  p.stroke([[560, 665], [585, 668]], 5);
  p.ell(260, 540, 160, 150, "#e0a050", 16);
  const sp = []; for (let i = 0; i < 46; i++) { const a = i * 0.34, r = 10 + i * 2.8; sp.push([260 + Math.cos(a) * r, 545 + Math.sin(a) * r * 0.95]); }
  p.stroke(sp, 10, "#a8641f"); p.stroke([[130, 440], [190, 410]], 10, "#ffffff77");
};
/** crystal ball on a stand */
export const fxCrystal = (p, t) => {
  const g = p.g;
  p.poly([[150, 790], [450, 790], [410, 700], [190, 700]], "#7a4a2a", 14); p.poly(rrect(130, 780, 470, 830, 20), "#5a3320", 14);
  p.ell(300, 520, 210, 210, "#a88bff", 16);
  const gr = g.createRadialGradient(240, 440, 20, 300, 520, 220); gr.addColorStop(0, "rgba(255,255,255,0.85)"); gr.addColorStop(0.5, "rgba(190,160,255,0.2)"); gr.addColorStop(1, "rgba(80,40,160,0.35)");
  g.fillStyle = gr; g.beginPath(); g.arc(300, 520, 205, 0, 7); g.fill();
  const sw = []; for (let i = 0; i < 40; i++) sw.push([200 + i * 5, 540 + Math.sin(i * 0.4 + t * 8) * 28]); p.stroke(sw, 12, "#e6dcff");
  for (let i = 0; i < 3; i++) { const k = (t * 1.2 + i / 3) % 1, x = 220 + i * 80, y = 640 - 260 * k; g.save(); g.globalAlpha = Math.sin(k * Math.PI); p.poly([[x, y - 22], [x + 7, y - 7], [x + 22, y], [x + 7, y + 7], [x, y + 22], [x - 7, y + 7], [x - 22, y], [x - 7, y - 7]], "#fff7b0", 4); g.restore(); }
};
/** pop-up result card: good = green check + apple, bad = red X + flame */
export const fxResult = (p, t, good = true) => {
  const g = p.g, s = pop(_clampT(t * 1.3)); g.save(); g.translate(300, 500); g.rotate(rad(good ? -4 : 4)); g.scale(s, s);
  p.poly(rrect(-250, -300, 250, 300, 50), "#fffaf0", 16); p.poly(rrect(-250, -300, 250, -130, 50), good ? "#38b04a" : "#e0362f", 16);
  p.poly(rrect(-250, -200, 250, -130, 4), good ? "#38b04a" : "#e0362f", 0);
  if (good) { for (const w of [46, 30]) p.stroke([[-110, -215], [-60, -165], [20, -255]].map(([x, y]) => [x, y + 0]), w, w === 46 ? INK : "#ffffff"); }
  else for (const w of [46, 30]) { const c = w === 46 ? INK : "#ffffff"; p.stroke([[-80, -250], [-10, -180]], w, c); p.stroke([[-10, -250], [-80, -180]], w, c); }
  if (good) { p.ell(0, 20, 110, 105, "#e0362f", 14); p.stroke([[0, -80], [10, -130]], 12, "#5a3b2a"); p.poly([[10, -110], [70, -150], [60, -100]], "#4fa650", 8); p.ell(-40, -10, 22, 30, "#ff9a9a", 0); }
  else { p.poly([[0, -100], [64, -20], [96, 60], [60, 130], [0, 150], [-60, 130], [-96, 60], [-70, -10], [-30, -50]], "#ff4a1a", 14); p.poly([[0, 10], [40, 70], [0, 130], [-40, 70]], "#ffd84a", 0); }
  txt(p, good ? "FOR THE" : "FOR THE", 0, 190, 64, "#ffffff", INK, 10); txt(p, good ? "BETTER" : "WORSE", 0, 255, 74, good ? "#7bff9a" : "#ff9a8a", INK, 10);
  g.restore();
};
export const fxKettle = (p, t) => {
  const g = p.g;
  for (let i = 0; i < 3; i++) { const k = (t * 1.3 + i / 3) % 1, x = 260 + i * 40 + Math.sin(k * 8 + i) * 14, y = 520 - k * 320; g.save(); g.globalAlpha = Math.sin(k * Math.PI) * 0.9; p.ell(x, y, 26 + k * 20, 22 + k * 14, "#ffffff", 0); g.restore(); }
  p.stroke([[160, 600], [90, 560], [60, 600]], 22, INK); p.stroke([[160, 600], [90, 560], [60, 600]], 12, "#9ba6b4");
  p.stroke([[350, 600], [500, 500], [480, 640]], 30, INK); p.stroke([[350, 600], [500, 500], [480, 640]], 18, "#5a6470");
  p.poly([[160, 760], [420, 760], [440, 640], [380, 560], [200, 560], [140, 640]], "#c5ced8", 16);
  p.poly(rrect(190, 540, 390, 574, 14), "#aab4c0", 12); p.ell(290, 530, 20, 16, "#5a6470", 8);
  p.stroke([[190, 640], [190, 720]], 12, "#ffffff88");
};
export const fxStopwatch = (p, t, s = "0.1 s") => {
  const g = p.g; p.poly(rrect(270, 250, 330, 310, 10), "#8a95a3", 12); p.stroke([[300, 310], [300, 330]], 24, INK);
  p.ell(300, 540, 230, 230, "#fffaf0", 18); g.lineWidth = 16; g.strokeStyle = "#3fb6e8"; g.beginPath(); g.arc(300, 540, 200, 0, 7); g.stroke();
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; p.stroke([[300 + Math.cos(a) * 168, 540 + Math.sin(a) * 168], [300 + Math.cos(a) * 190, 540 + Math.sin(a) * 190]], 8, INK); }
  txt(p, s, 300, 560, 84, "#e0362f", INK, 10);
};
export const fxDice = (p, t) => {
  const g = p.g;
  for (const [x, y, a, n] of [[210, 560, -0.3 + t * 5, 5], [400, 480, 0.4 - t * 4, 2]]) {
    g.save(); g.translate(x, y); g.rotate(a); p.poly(rrect(-90, -90, 90, 90, 26), "#ffffff", 14);
    const pips = { 5: [[-45, -45], [45, -45], [0, 0], [-45, 45], [45, 45]], 2: [[-40, -40], [40, 40]] }[n]; for (const [px, py] of pips) p.dot(px, py, 14); g.restore();
  }
};
export const fxChart = (p, t) => {
  const g = p.g, k = pop(_clampT(t * 1.2)); g.save(); g.translate(300, 500); g.scale(k, k);
  p.poly(rrect(-260, -210, 260, 210, 30), "#fffaf0", 16);
  p.stroke([[-200, 150], [200, 150]], 10); p.stroke([[-200, 150], [-200, -150]], 10);
  const hs = [70, 120, 160, 230]; hs.forEach((h, i) => { const hh = h * _clampT(t * 1.6 - i * 0.12); p.poly(rrect(-150 + i * 90, 150 - hh, -100 + i * 90, 150, 6), ["#3fb6e8", "#5ac8a0", "#ffb84a", "#7a5cf0"][i], 8); });
  p.stroke([[-170, 90], [-80, 20], [10, 30], [120, -80], [190, -130]], 12, "#e0362f");
  g.restore();
};
export const fxStomach = (p, t) => {
  const g = p.g, k = 1 + 0.06 * Math.sin(t * 30); g.save(); g.translate(300, 500); g.scale(k, k);
  p.poly([[-40, -170], [60, -170], [150, -60], [160, 70], [90, 150], [-30, 130], [-110, 60], [-60, -20], [-50, -100]], "#ff9a8a", 16);
  p.stroke([[-60, 20], [20, -30], [-20, -70], [60, -20], [10, 40]], 14, "#c8463a"); p.stroke([[-30, 80], [50, 60], [90, 20]], 10, "#c8463a");
  g.restore();
};
export const fxThought = (p, t) => {
  const g = p.g, s = pop(_clampT(t)); g.save(); g.translate(300, 500); g.scale(s, s);
  for (const [x, y, r] of [[-140, 60, 130], [20, -30, 160], [150, 40, 130], [-30, 110, 130], [60, 120, 120]]) p.ell(x, y, r, r * 0.8, "#ffffff", 14);
  for (const [x, y, r] of [[-140, 60, 130], [20, -30, 160], [150, 40, 130], [-30, 110, 130], [60, 120, 120]]) p.ell(x, y, r - 8, r * 0.8 - 8, "#ffffff", 0);
  p.ell(-60, 260, 34, 28, "#ffffff", 12); p.ell(-90, 330, 20, 16, "#ffffff", 10);
  for (let i = 0; i < 6; i++) { const x = -150 + (i % 3) * 150, y = -10 + Math.floor(i / 3) * 120, on = t * 12 > i * 0.8, sc = on ? 0.38 + 0.04 * Math.sin(t * 20 + i) : 0; if (!on) continue; g.save(); g.translate(x, y); g.scale(sc, sc);
    p.poly([[0, -100], [50, -30], [80, 40], [40, 100], [0, 110], [-50, 100], [-80, 40], [-50, -20]], "#ff4a1a", 14); p.poly([[0, 0], [30, 50], [0, 95], [-30, 50]], "#ffd84a", 0); g.restore(); }
  g.restore();
};
export const fxSpeaker = (p, t, muted = true) => {
  const g = p.g, s = pop(_clampT(t)); g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly([[-150, -50], [-60, -50], [40, -140], [40, 140], [-60, 50], [-150, 50]], "#dfe6ee", 16);
  if (!muted) for (const r of [80, 140]) { g.lineWidth = 16; g.strokeStyle = INK; g.beginPath(); g.arc(30, 0, r, -0.8, 0.8); g.stroke(); }
  else for (const w of [40, 24]) { const c = w === 40 ? INK : "#e0362f"; p.stroke([[90, -90], [210, 30]], w, c); p.stroke([[210, -90], [90, 30]], w, c); }
  g.restore();
};
/** match flash ring */
export const fxMatchRing = (p, t) => { const g = p.g, r = 90 + 160 * t; g.save(); g.globalAlpha = 1 - t; g.lineWidth = 34; g.strokeStyle = "#7bff9a"; g.beginPath(); g.arc(300, 500, r, 0, 7); g.stroke(); g.restore(); };
/** simple filled disc glow */
export const fxGlowDisc = (p, t, col = "#ff9a3a") => { const g = p.g, gr = g.createRadialGradient(300, 500, 10, 300, 500, 300); gr.addColorStop(0, col + "ff"); gr.addColorStop(1, col + "00"); g.save(); g.globalAlpha = 0.65 + 0.25 * Math.sin(t * 40); g.fillStyle = gr; g.beginPath(); g.arc(300, 500, 300, 0, 7); g.fill(); g.restore(); };
/** big burning flame cluster for the basement (animated) */
export const fxInferno = (p, t) => {
  const g = p.g;
  for (const [x, h, ph, col] of [[170, 330, 0, "#ff4a1a"], [430, 360, 1.7, "#ff4a1a"], [300, 440, 0.9, "#ff5a1a"], [90, 240, 2.4, "#ff6a2a"], [510, 250, 3.1, "#ff6a2a"]]) {
    const sw = Math.sin(t * 22 + ph) * 16, hh = h * (0.9 + 0.12 * Math.sin(t * 17 + ph * 2));
    p.poly([[x + sw, 900 - hh], [x + 70, 900 - hh * 0.55], [x + 95, 900 - hh * 0.2], [x + 70, 900], [x - 70, 900], [x - 95, 900 - hh * 0.2], [x - 66, 900 - hh * 0.55]], col, 14);
    p.poly([[x + sw * 0.6, 900 - hh * 0.62], [x + 40, 900 - hh * 0.3], [x + 38, 900], [x - 38, 900], [x - 44, 900 - hh * 0.3]], "#ff9a1f", 0);
    p.poly([[x + sw * 0.3, 900 - hh * 0.3], [x + 22, 900 - hh * 0.12], [x + 20, 900], [x - 20, 900], [x - 22, 900 - hh * 0.12]], "#ffe14a", 0);
  }
};
export const fxSmoke = (p, t) => {
  for (let i = 0; i < 6; i++) { const k = (t * 0.9 + i / 6) % 1, x = 300 + Math.sin(k * 5 + i * 2) * 60 + (i % 3 - 1) * 40, y = 820 - k * 620, r = 50 + k * 90; p.ell(x, y, r, r * 0.85, `rgba(${60 + i * 6},${56 + i * 5},${64 + i * 5},${(0.75 * Math.sin(k * Math.PI)).toFixed(3)})`, 0); }
};
