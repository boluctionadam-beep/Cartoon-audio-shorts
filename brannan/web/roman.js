FACE.snore = { eye: ["dash", "dash"], brow: [0, -1], mouth: "o" };
FACE.stubborn = { eye: ["lid", "lid"], brow: [4, -3], mouth: "frown" };
FACE.squint = { eye: ["slit", "slit"], brow: [3, -2], mouth: "dash" };

// ---------------- Roman-era cast (our own designs), built on the Pen / blob / face helpers above ----------------
const STEEL = "#aeb6bf", BRASS = "#d9a845", LEATHER = "#7a4a2a";
export const OUTFITS = {
  legion: { tunic: "#b8322f", cape: "#8f2228", skin: SKIN, helmet: true, armor: true, spear: true, shield: true },
  old: { tunic: "#9c4a3c", cape: "#6e3330", skin: "#f3d6bb", helmet: "old", armor: true, spear: true, shield: false, beard: "#f4f1ea", brows: "#f4f1ea" },
  toga: { tunic: "#f1ead8", skin: "#f5c9a0", toga: "#6b3c8f", hair: "#3b2a20", stout: true },
  civA: { tunic: "#4f7fb8", skin: "#f5c9a0", hair: "#5a3b2a" },
  civB: { tunic: "#d9a441", skin: SKIN, hair: "#2b211c", dress: "#c25a7a" },
  civC: { tunic: "#5d8a3a", skin: "#c99067", hair: "#1e1714", stout: true },
  workA: { tunic: "#8a5d3b", skin: "#f5c9a0", cap: "#c2733a", apron: "#d8c9a6" },
  hero: { tunic: "#f2a93b", skin: "#f5c9a0", hair: "#4a2f22" },
  pj: { tunic: "#8ec5ff", skin: "#f5c9a0", hair: "#4a2f22" },
  fireA: { tunic: "#e0a526", skin: "#f5c9a0", fire: "#d6302a", stripes: true },
  fireB: { tunic: "#d68a2a", skin: "#ecd0b6", fire: "#c42b25", stripes: true, stout: true },
  fireC: { tunic: "#e6b83a", skin: "#c99067", fire: "#e0482a", stripes: true },
  gm: { tunic: "#46506e", skin: "#f3d6bb", hair: "#d9d9e0", beard: "#d9d9e0", brows: "#d9d9e0", stout: true },
  rookie: { tunic: "#6fc3a0", skin: "#f5c9a0", cap: "#ff7a59" },
  pro: { tunic: "#2f4f8f", skin: "#f5c9a0", hair: "#23233a" },
  workB: { tunic: "#3f6a6f", skin: "#ecd0b6", cap: "#5b4a8a", moustache: "#4a3020" },
};

/** galea: iron bowl, brass brow band, cheek guards, transverse red crest */
const galea = (p, H, cx, hc, light, thick, ow, old, u) => {
  const crest = old ? "#8d4b3f" : "#d2372f", bowl = old ? "#8f8a7e" : STEEL;
  // crest (behind the bowl top)
  const cy0 = hc - H.b * 0.98;
  const cr = ellPts(cx, cy0, 0.66 * 2 * H.a, 0.42 * 2 * H.b, 180, 360, 0, 40);
  cr.push([cx + 0.66 * 2 * H.a * 0.98, cy0 + 4 * u], [cx - 0.66 * 2 * H.a * 0.98, cy0 + 4 * u]);
  const crP = [...ellPts(cx, cy0 + 2 * u, 0.62 * 2 * H.a, 0.36 * 2 * H.b, 180, 360, 0, 40)];
  p.shadedFill(crP, crest, mul(crest, [0.7, 0.62, 0.7]), light, 0.62 * 2 * H.a, 0.3);
  p.clip(crP, () => { for (let i = -9; i <= 9; i++) p.stroke([[cx + i * 7.4 * u, cy0], [cx + i * 9.4 * u, cy0 - 0.62 * H.b * Math.cos(i / 11)]], 1.4 * u, mul(crest, [0.62, 0.55, 0.62])); });
  if (old) p.clip(crP, () => { for (let i = 0; i < 6; i++) p.ell(cx + (i - 3) * 22 * u, cy0 - 18 * u - (i % 2) * 10 * u, 9 * u, 5 * u, "#6f6a5e", 0); });
  p.inkRing(crP, ow * 0.85, thick);
  p.poly(rrect(cx - 10 * u, cy0 - 6 * u, cx + 10 * u, cy0 + 6 * u, 3 * u), BRASS, 2 * u);
  // bowl: upper head cap
  const bandY = hc - H.b * 0.42;
  const bp = ellPts(cx, bandY, H.a * 1.05, H.b * 0.66, 180, 360, 0, 48);
  p.shadedFill(bp, bowl, mul(bowl, [0.62, 0.64, 0.72]), light, H.a, 0.4);
  p.clip(bp, () => {
    p.stroke(ellPts(cx - 20 * u, bandY - 0.3 * H.b, 0.25 * H.a, 0.18 * H.b, 200, 300, 0, 16), 4 * u, "#ffffff55");
    if (old) for (let i = 0; i < 9; i++) p.ell(cx + Math.sin(i * 2.3) * 0.8 * H.a, bandY - (0.08 + 0.5 * ((i * 0.37) % 1)) * H.b, (3 + (i % 3) * 2) * u, (2 + (i % 2)) * u, "#8a4b22", 0);
  });
  p.inkRing(bp, ow * 0.9, thick);
  p.band([[cx - H.a * 1.04, bandY], [cx + H.a * 1.04, bandY]], old ? "#a88a4a" : BRASS, 7 * u, 1.8 * u, "round");
  for (const s of [-1, 1]) p.dot(cx + s * 0.55 * H.a, bandY, 2.2 * u, "#fff3c4");
};
const cheeks = (p, H, cx, hc, light, ow, old, u) => {
  const bowl = old ? "#8f8a7e" : STEEL;
  for (const s of [-1, 1]) {
    const x0 = cx + s * 0.78 * H.a, x1 = cx + s * 1.07 * H.a, y0 = hc - H.b * 0.42, y1 = hc + H.b * 0.48;
    const pts = [[x0, y0], [x1, y0], [x1 - s * 0.04 * H.a, y1 - 0.1 * H.b], [x0 + s * 0.06 * H.a, y1], [x0 - s * 0.05 * H.a, (y0 + y1) / 2]];
    p.shadedFill(pts, bowl, mul(bowl, [0.62, 0.64, 0.72]), light, 0.2 * H.a, 0.3);
    p.poly(pts, null, ow * 0.8);
    p.dot((x0 + x1) / 2, (y0 + y1) / 2 - 0.05 * H.b, 2.2 * u, BRASS);
  }
};
const fireHelmet = (p, H, cx, hc, light, thick, ow, u, col) => {
  const bandY = hc - H.b * 0.26, dome = ellPts(cx, bandY, H.a * 1.1, H.b * 0.86, 180, 360, 0, 48);
  p.shadedFill(dome, col, mul(col, [0.6, 0.6, 0.7]), light, H.a, 0.4);
  p.clip(dome, () => { p.stroke(ellPts(cx - 20 * u, bandY - 0.35 * H.b, 0.3 * H.a, 0.2 * H.b, 200, 300, 0, 16), 5 * u, "#ffffff77"); });
  p.inkRing(dome, ow, thick);
  p.poly(rrect(cx - H.a * 1.32, bandY - 3 * u, cx + H.a * 1.32, bandY + 9 * u, 4 * u), mul(col, [0.82, 0.8, 0.8]), ow * 0.8);
  const y = bandY - 0.45 * H.b;
  p.poly([[cx - 10 * u, y - 10 * u], [cx + 10 * u, y - 10 * u], [cx + 10 * u, y + 4 * u], [cx, y + 15 * u], [cx - 10 * u, y + 4 * u]], "#ffd84a", 2 * u);
};
const cobweb = (p, cx, cy, r, u) => {
  const g = p.g; g.save(); g.globalAlpha = 0.8;
  for (let i = 0; i < 7; i++) { const a = -Math.PI * (0.05 + 0.9 * i / 6); p.stroke([[cx, cy], [cx + Math.cos(a) * r, cy + Math.sin(a) * r]], 1.1 * u, "#f2f2f2"); }
  for (let k = 1; k <= 4; k++) { const rr = r * k / 4.3, pts = []; for (let i = 0; i < 7; i++) { const a = -Math.PI * (0.05 + 0.9 * i / 6); pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); } p.stroke(pts, 1 * u, "#f2f2f2"); }
  g.restore();
};

/** front-facing Roman-era character. opts: expr, blink, look, facing, seed, L/R arm poses, tilt, headTilt, bob, nohelmet, light */
export const romanFront = (p, key, opts = {}) => {
  const O = typeof key === "string" ? OUTFITS[key] : key;
  const { expr = "neutral", blink = 0, look = 0, facing = 0, seed = 3, L = "hang", R = O.spear ? "spear" : "hang", tilt = 0, headTilt = 0,
    bob = 0, nohelmet = false, light = rad(-120), web = false, step = 0 } = opts;
  const lid = lidOf(blink), skin = O.skin ?? SKIN;
  const H = headBlob(seed, 118, facing), W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  const torsoL = O.stout ? 1.12 : 1.08, legsL = 1.38, sole = 975;
  const torsoBot = sole - legsL * HH - bob * HH, chin = torsoBot - torsoL * HH, hc = chin - H.b, hipY = torsoBot - 0.12 * HH;
  const thick = thickAngle(light), ow = 5 * u, cx = 300;
  const legCol = mix(O.tunic, INK, 0.62), armCol = mix(O.tunic, INK, 0.5);
  const helmet = !!O.helmet && !nohelmet, old = O.helmet === "old";
  p.rot = null;
  // ---- cape behind everything ----
  if (O.cape) {
    const cp = [[cx - 0.48 * W, chin + 0.08 * HH], [cx + 0.48 * W, chin + 0.08 * HH], [cx + 0.62 * W, sole - 0.55 * HH], [cx + 0.2 * W, sole - 0.45 * HH], [cx - 0.2 * W, sole - 0.5 * HH], [cx - 0.62 * W, sole - 0.55 * HH]];
    p.gradFill(cp, O.cape, mul(O.cape, [0.6, 0.6, 0.7]), light); p.inkRing(cp, ow * 0.8, thick);
  }
  // ---- legs ----
  const dress = !!O.dress;
  for (const side of [-1, 1]) {
    const up = Math.max(0, Math.sin(Math.PI * 2 * (step + (side > 0 ? 0.5 : 0)))) * 30 * (step ? 1 : 0);
    const hx = cx + side * 16 * u, fx = cx + side * 22 * u, fy = sole - 4 * u - up;
    p.stroke(curve([hx, hipY], [(hx + fx) / 2 + side * 2 * u, (hipY + fy) / 2], [fx, fy]), 5.8 * u, legCol);
    const sandal = O.helmet ? LEATHER : "#5a3b2a";
    p.stroke([[fx - side * 3 * u, fy], [fx + side * 13 * u, fy + 0.5 * u]], 7.5 * u + 3, INK);
    p.stroke([[fx - side * 3 * u, fy], [fx + side * 13 * u, fy + 0.5 * u]], 7.5 * u, sandal);
    if (O.helmet) for (let k = 1; k <= 3; k++) p.stroke([[fx - 4 * u, fy - k * 0.07 * HH], [fx + 4 * u, fy - k * 0.07 * HH - 2 * u]], 2 * u, LEATHER);
  }
  // ---- upper body ----
  p.rot = tilt ? [rad(tilt), cx, hipY] : null;
  const T = { a: (0.4 * W) / 1.06 * (O.stout ? 1.12 : 1), b: 0.5 * (torsoBot - (chin - 0.25 * HH)), nTop: 2.2, nBot: 2.6, egg: O.stout ? 0.17 : 0.12, asym: 0.04 * facing, rot: 0, noise: 0.006, seed: seed + 7 };
  const tcx = cx + 3 * u * facing, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
  const S = (side) => [tcx + side * 0.85 * T.a, chin + 0.12 * HH];
  const arm = (side, pose) => {
    const s = S(side), X = (k) => tcx + side * (T.a * 1.1 + k * u);
    switch (pose) {
      case "spear": return { pts: [s, [X(6), s[1] + 0.42 * HH], [X(10), s[1] + 0.2 * HH]], front: false };
      case "point": return { pts: [s, [X(28), s[1] - 0.02 * HH], [X(62), s[1] - 0.1 * HH]], front: false, finger: true };
      case "up": return { pts: [s, [X(14), s[1] - 0.3 * HH], [X(22), s[1] - 0.75 * HH]], front: false };
      case "wave": return { pts: [s, [X(16), s[1] - 0.2 * HH], [X(30 + 10 * Math.sin(opts.wv || 0)), s[1] - 0.62 * HH]], front: false };
      case "hip": return { pts: [s, [X(22), s[1] + 0.3 * HH], [tcx + side * T.a * 0.95, torsoBot - 0.3 * HH]], front: false };
      case "belly": return { pts: [s, [X(8), s[1] + 0.45 * HH], [tcx + side * 0.25 * T.a, torsoBot - 0.35 * HH]], front: true };
      case "temple": return { pts: [s, [X(26), s[1] + 0.05 * HH], [cx + side * (H.a + 16 * u), hc - 0.1 * HH]], front: false, swirl: true };
      case "lift": return { pts: [s, [X(20), s[1] - 0.25 * HH], [X(4), s[1] - 0.82 * HH]], front: false };
      case "shield": return { pts: [s, [X(4), s[1] + 0.4 * HH], [tcx + side * 0.6 * T.a, torsoBot - 0.1 * HH]], front: true };
      case "cross": return { pts: [s, [X(2), s[1] + 0.38 * HH], [tcx - side * 0.45 * T.a, s[1] + 0.32 * HH]], front: true };
      case "reach": { const lf = (opts.lift || 0) * 0.62 * HH; return { pts: [s, [X(42), s[1] - 0.12 * HH - lf * 0.6], [X(82), s[1] - 0.5 * HH - lf]], front: false }; }
      case "nose": { const k = (side > 0 ? opts.nkR : opts.nkL) ?? opts.nk ?? 1, A = [s, [X(4), s[1] + 0.48 * HH], [X(3), chin + 1.04 * HH]], B = [s, [X(46), s[1] - 0.02 * HH], [cx + side * 9 * u, hc + (opts.nhy ?? 12) * u]]; return { pts: A.map((a, i) => [a[0] + (B[i][0] - a[0]) * k, a[1] + (B[i][1] - a[1]) * k]), front: false, late: k > 0.35, nose: true, k }; }
      case "cheek": return { pts: [s, [X(16), s[1] + 0.05 * HH], [cx + side * (H.a + 2 * u), hc + 0.25 * H.b]], front: false };
      case "thumb": return { pts: [s, [X(20), s[1] + 0.12 * HH], [X(44), s[1] - 0.12 * HH]], front: false, thumb: true };
      default: return { pts: [s, [X(4), s[1] + 0.48 * HH], [X(3), chin + 1.04 * HH]], front: false };
    }
  };
  const arms = [arm(-1, L), arm(1, R)];
  const drawArm = (a) => {
    p.stroke(curve(a.pts[0], a.pts[1], a.pts[2]), 5.2 * u, armCol);
    const [hx, hy] = a.pts[2];
    p.dot(hx, hy, 5.5 * u);
    if (a.finger) { const dx = a.pts[2][0] - a.pts[1][0], dy = a.pts[2][1] - a.pts[1][1], l = Math.hypot(dx, dy); p.stroke([[hx, hy], [hx + dx / l * 14 * u, hy + dy / l * 14 * u]], 2.6 * u); }
    if (a.thumb) p.stroke([[hx, hy], [hx + Math.sign(hx - cx) * 6 * u, hy - 12 * u]], 2.6 * u);
  };
  // spear behind
  if (O.spear && R === "spear") {
    const [hx, hy] = arms[1].pts[2], s0 = [hx + 2 * u, sole - 2 * u], s1 = [hx - 3 * u, 70];
    p.band([s0, s1], old ? "#6d5236" : "#8a5a34", 4.2 * u, 1.4 * u, "round");
    const tip = [[s1[0] - 7 * u, s1[1] + 6 * u], [s1[0], s1[1] - 34 * u], [s1[0] + 7 * u, s1[1] + 6 * u], [s1[0], s1[1] + 14 * u]];
    p.poly(tip, old ? "#8b7c6a" : "#c9cfd6", 2 * u);
    if (web) cobweb(p, s1[0] - 2 * u, s1[1] + 60 * u, 70 * u, u);
  }
  for (const a of arms) if (!a.front && !a.late) drawArm(a);
  // torso
  if (dress) {
    const D = { a: 0.5 * W * 0.98, b: 0.5 * ((sole - 0.35 * HH) - (chin - 0.2 * HH)), nTop: 2.0, nBot: 3.0, egg: 0.35, asym: 0, rot: 0, noise: 0.006, seed: seed + 9 };
    const dp = blobPts(cx, sole - 0.35 * HH - D.b, D);
    p.gradFill(dp, O.dress, mul(O.dress, SH_CLOTH), light); p.inkRing(dp, ow, thick);
  }
  // skirt / pteruges below the torso
  if (!dress) {
    const sk = [[tcx - 0.92 * T.a, torsoBot - 0.2 * HH], [tcx + 0.92 * T.a, torsoBot - 0.2 * HH], [tcx + 1.0 * T.a, torsoBot + 0.3 * HH], [tcx - 1.0 * T.a, torsoBot + 0.3 * HH]];
    p.gradFill(sk, O.tunic, mul(O.tunic, SH_CLOTH), light); p.poly(sk, null, ow * 0.8);
    if (O.armor) for (let i = -3; i <= 3; i++) { const x = tcx + i * 0.27 * T.a, st = [[x - 9 * u, torsoBot - 0.05 * HH], [x + 9 * u, torsoBot - 0.05 * HH], [x + 9 * u, torsoBot + 0.22 * HH], [x - 9 * u, torsoBot + 0.22 * HH]]; p.poly(st, old ? "#5e4632" : LEATHER, 1.6 * u); }
  }
  p.gradFill(tp, O.tunic, mul(O.tunic, SH_CLOTH), light);
  p.clip(tp, () => {
    if (O.armor) {
      const top = chin - 0.1 * HH, bot = torsoBot - 0.25 * HH, n = 5;
      for (let i = 0; i < n; i++) {
        const y0 = top + (bot - top) * i / n, y1 = top + (bot - top) * (i + 1) / n;
        const c = old ? (i % 2 ? "#8d8679" : "#9a9384") : (i % 2 ? "#a7b0ba" : "#bcc4cc");
        p.poly([[tcx - 1.5 * T.a, y0], [tcx + 1.5 * T.a, y0 + 3 * u], [tcx + 1.5 * T.a, y1 + 3 * u], [tcx - 1.5 * T.a, y1]], c, 1.8 * u);
      }
      p.band([[tcx - 1.4 * T.a, torsoBot - 0.2 * HH], [tcx + 1.4 * T.a, torsoBot - 0.2 * HH]], LEATHER, 0.08 * HH, 1.5 * u);
      for (let i = -2; i <= 2; i++) p.dot(tcx + i * 0.3 * T.a, torsoBot - 0.2 * HH, 2.4 * u, BRASS);
      if (old) for (let i = 0; i < 5; i++) p.ell(tcx + Math.sin(i * 1.7) * 0.7 * T.a, top + (bot - top) * ((i * 0.31) % 1), 6 * u, 3 * u, "#8a4b22", 0);
    } else {
      p.band([[tcx - 1.4 * T.a, torsoBot - 0.24 * HH], [tcx + 1.4 * T.a, torsoBot - 0.24 * HH]], O.apron ? "#5a3b2a" : "#e2c27a", 0.05 * HH, 1.2 * u);
      if (O.stripes) { p.band([[tcx - 1.4 * T.a, torsoBot - 0.52 * HH], [tcx + 1.4 * T.a, torsoBot - 0.52 * HH]], "#f2f2f2", 0.055 * HH, 1.2 * u); p.band([[tcx - 1.4 * T.a, torsoBot - 0.36 * HH], [tcx + 1.4 * T.a, torsoBot - 0.36 * HH]], "#d0d6dc", 0.04 * HH, 1.2 * u); }
      if (O.toga) p.band([[tcx - 1.0 * T.a, chin - 0.1 * HH], [tcx + 1.1 * T.a, torsoBot - 0.1 * HH]], O.toga, 0.16 * HH, 1.6 * u);
      if (O.apron) p.poly([[tcx - 0.55 * T.a, torsoBot - 0.2 * HH], [tcx + 0.55 * T.a, torsoBot - 0.2 * HH], [tcx + 0.6 * T.a, torsoBot + 0.2 * HH], [tcx - 0.6 * T.a, torsoBot + 0.2 * HH]], O.apron, 1.6 * u);
      p.stroke([[tcx - 0.2 * T.a, chin + 0.02 * HH], [tcx, chin + 0.16 * HH], [tcx + 0.2 * T.a, chin + 0.02 * HH]], 2 * u);
    }
  });
  p.inkRing(tp, ow, thick);
  if (O.armor) for (const s of [-1, 1]) { // shoulder plates
    const sp = ellPts(tcx + s * 0.72 * T.a, chin + 0.1 * HH, 0.42 * T.a, 0.13 * HH, 180, 360, s * 8, 20);
    p.poly(sp, old ? "#9a9384" : "#c5ccd3", 1.8 * u);
  }
  if (O.moss) {/* reserved */}
  for (const a of arms) if (a.front) drawArm(a);
  // shield in front, held by the left hand
  if (O.shield && L === "shield") {
    const sx = tcx - 0.55 * T.a, sy = torsoBot + 0.05 * HH, sw = 0.36 * W, sh = 0.78 * HH;
    const sp = rrect(sx - sw, sy - sh, sx + sw, sy + sh, 8 * u);
    p.gradFill(sp, "#c0302c", "#7d1d22", light);
    p.clip(sp, () => {
      p.band([[sx - sw, sy], [sx + sw, sy]], BRASS, 6 * u, 1.2 * u);
      p.band([[sx, sy - sh], [sx, sy + sh]], BRASS, 6 * u, 1.2 * u);
      for (const s of [-1, 1]) { p.stroke([[sx + s * 12 * u, sy - 14 * u], [sx + s * 34 * u, sy - 46 * u], [sx + s * 22 * u, sy - 44 * u], [sx + s * 46 * u, sy - 74 * u]], 3.5 * u, BRASS); p.stroke([[sx + s * 12 * u, sy + 14 * u], [sx + s * 34 * u, sy + 46 * u], [sx + s * 22 * u, sy + 44 * u], [sx + s * 46 * u, sy + 74 * u]], 3.5 * u, BRASS); }
      p.stroke(ellPts(sx - sw * 0.5, sy - sh * 0.7, sw * 0.3, sh * 0.1, 200, 320, 0, 10), 3 * u, "#ffffff44");
    });
    p.ell(sx, sy, 13 * u, 13 * u, "#e6c068", 2.2 * u);
    p.inkRing(sp, ow, thick);
  }
  // ---- head ----
  const [cpx, cpy] = rotAbout([cx, chin], rad(tilt), [cx, hipY]);
  const Ah = tilt + headTilt;
  p.rot = Ah ? [rad(Ah), cx, chin, cpx - cx, cpy - chin] : null;
  if (helmet) galea(p, H, cx, hc, light, thick, ow, old, u);
  const hp = blobPts(cx, hc, H);
  if (O.hair && !helmet) { const hb = blobPts(cx, hc - 0.03 * HH, { ...H, a: H.a * 1.04, b: H.b * 1.05 }); p.poly(hb, O.hair, 0); }
  p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
  p.inkRing(hp, ow, thick);
  if (helmet) {
    const bandY = hc - H.b * 0.42, bp = ellPts(cx, bandY, H.a * 1.05, H.b * 0.66, 180, 360, 0, 48);
    p.shadedFill(bp, old ? "#8f8a7e" : STEEL, mul(old ? "#8f8a7e" : STEEL, [0.62, 0.64, 0.72]), light, H.a, 0.4);
    p.clip(bp, () => { p.stroke(ellPts(cx - 20 * u, bandY - 0.3 * H.b, 0.25 * H.a, 0.18 * H.b, 200, 300, 0, 16), 5 * u, "#ffffff66");
      if (old) for (let i = 0; i < 9; i++) p.ell(cx + Math.sin(i * 2.3) * 0.8 * H.a, bandY - (0.08 + 0.5 * ((i * 0.37) % 1)) * H.b, (4 + (i % 3) * 2) * u, (2.5 + (i % 2)) * u, "#8a4b22", 0); });
    p.poly(bp, null, ow * 0.9);
    p.band([[cx - H.a * 1.05, bandY], [cx + H.a * 1.05, bandY]], old ? "#a88a4a" : BRASS, 7 * u, 1.8 * u, "round");
    p.poly(rrect(cx - 4 * u, bandY - 0.55 * H.b, cx + 4 * u, bandY - 3 * u, 2 * u), old ? "#a88a4a" : BRASS, 1.5 * u);
    cheeks(p, H, cx, hc, light, ow, old, u);
  } else if (O.fire) fireHelmet(p, H, cx, hc, light, thick, ow, u, O.fire);
  else if (O.cap) hatOn(p, { hat: "cap", cap: O.cap, jacket: O.tunic }, hp, H, cx, hc, light, seed, facing, false);
  else if (O.hair) hatOn(p, { hat: "hair", hair: O.hair, jacket: O.tunic }, hp, H, cx, hc, light, seed, facing, false);
  else if (O.helmet && nohelmet) { // bald old head with white side tufts
    for (const s of [-1, 1]) p.ell(cx + s * 0.9 * H.a, hc - 0.1 * H.b, 0.22 * H.a, 0.3 * H.b, "#f4f1ea", 3 * u);
  }
  if (O.beard) {
    const bd = blobPts(cx + 6 * u * facing, hc + 0.85 * H.b, { a: 0.62 * H.a, b: 0.75 * H.b, nTop: 2.4, nBot: 1.6, egg: -0.35, asym: 0, rot: 0, noise: 0.02, seed: seed + 4 });
    p.shadedFill(bd, O.beard, mul(O.beard, [0.86, 0.86, 0.92]), light, 0.6 * H.a, 0.3);
    p.clip(bd, () => { for (let i = -3; i <= 3; i++) p.stroke([[cx + i * 9 * u, hc + 0.45 * H.b], [cx + i * 7 * u, hc + 1.35 * H.b]], 1.2 * u, "#c9c4bb"); });
    p.inkRing(bd, ow * 0.8, thick);
  }
  faceFront(p, cx, hc, W, expr, facing, look, lid, helmet, skin, O.beard ? O.beard : O.moustache, !!O.stout);
  if (O.brows) for (const s of [-1, 1]) p.ell(cx + 7 * u * facing + s * 14 * u, hc - 20 * u, 11 * u, 5 * u, O.brows, 2 * u);
  if (O.beard) { // re-draw the mouth over the beard for open mouths
    if (expr === "shock" || expr === "snore") p.ell(cx + 8 * u * facing, hc + 22 * u, 6 * u, 7 * u, "#5a1e28", 2 * u);
  }
  for (const a of arms) if (a.late) { // hand pinching a nostril, drawn over the face
    const side = a.pts[2][0] > cx ? 1 : -1;
    p.stroke(curve(a.pts[0], a.pts[1], a.pts[2]), 5.2 * u, armCol);
    const [hx, hy] = a.pts[2];
    p.ell(hx, hy + 2 * u, 7.5 * u, 6.5 * u, skin, 2.2 * u);
    p.stroke([[hx - side * 3 * u, hy - 3 * u], [hx - side * 8 * u, hy - 9 * u]], 3.6 * u, skin);
  }
  p.rot = null;
  if (arms.some((a) => a.swirl)) { // cuckoo swirl next to the temple
    const a = arms.find((x) => x.swirl), [hx, hy] = a.pts[2], ph = opts.swirl || 0, pts = [];
    for (let i = 0; i < 40; i++) { const t = i / 40 * Math.PI * 4 + ph, r = (4 + i * 0.7) * u; pts.push([hx + Math.cos(t) * r, hy - 40 * u + Math.sin(t) * r]); }
    p.stroke(pts, 3 * u, "#ffffff"); p.stroke(pts, 1.4 * u, INK);
  }
};

/** loose helmet prop card (lifted off the old soldier) */
export const helmetCard = (p) => {
  const H = headBlob(3, 118, 0), u = 2 * H.a / 100, hc = 560, light = rad(-120), thick = thickAngle(light), ow = 5 * u;
  galea(p, H, 300, hc, light, thick, ow, true, u);
  const bandY = hc - H.b * 0.42, bp = ellPts(300, bandY, H.a * 1.05, H.b * 0.66, 180, 360, 0, 48);
  // dark inside visible from below
  p.ell(300, bandY, H.a * 1.05, 0.12 * H.b, "#2a221e", 0);
  p.shadedFill(bp, "#8f8a7e", mul("#8f8a7e", [0.62, 0.64, 0.72]), light, H.a, 0.4);
  p.clip(bp, () => { for (let i = 0; i < 9; i++) p.ell(300 + Math.sin(i * 2.3) * 0.8 * H.a, bandY - (0.08 + 0.5 * ((i * 0.37) % 1)) * H.b, (4 + (i % 3) * 2) * u, (2.5 + (i % 2)) * u, "#8a4b22", 0); });
  p.poly(bp, null, ow * 0.9);
  p.band([[300 - H.a * 1.05, bandY], [300 + H.a * 1.05, bandY]], "#a88a4a", 7 * u, 1.8 * u, "round");
  cheeks(p, H, 300, hc, light, ow, true, u);
};

/** ZZZ for the sleeping guard */
export const fxZ = (p, t) => {
  const g = p.g; g.save(); g.font = "900 120px Arial Black, Arial"; g.lineJoin = "round";
  for (let i = 0; i < 3; i++) {
    const k = (t + i / 3) % 1, x = 220 + i * 70 + Math.sin(k * 6) * 20, y = 700 - k * 500, s = 0.5 + k * 0.7;
    g.save(); g.translate(x, y); g.scale(s, s); g.globalAlpha = Math.min(1, (1 - k) * 2.5);
    g.lineWidth = 16; g.strokeStyle = INK; g.strokeText("Z", 0, 0); g.fillStyle = "#ffffff"; g.fillText("Z", 0, 0); g.restore();
  }
  g.restore();
};
/** falling leaf */
export const fxLeaf = (p, col) => { p.poly([[300, 380], [420, 470], [300, 620], [180, 470]], col, 14); p.stroke([[300, 400], [300, 600]], 8); };
/** dust cloud puff (k 0..1 growth) */
export const fxDust = (p, k, col = "#e8dcc4") => {
  const g = p.g; g.save(); g.globalAlpha = Math.max(0, 1 - k * k);
  for (let i = 0; i < 7; i++) { const a = i / 7 * Math.PI * 2, r = 90 + 150 * k; p.ell(300 + Math.cos(a) * r, 520 + Math.sin(a) * r * 0.6, 120 + 60 * k, 100 + 50 * k, col, 12); }
  p.ell(300, 520, 170 + 110 * k, 140 + 80 * k, col, 0);
  g.restore();
};
export const fxDrip = (p) => p.ell(300, 500, 40, 64, "#9fd4ff", 10);
export const fxWood = (p, seed) => { p.poly([[200, 420], [400, 400], [420, 560], [230, 600]], "#5b3d22", 14); p.stroke([[240, 450], [380, 440]], 6, "#3a2614"); p.ell(330, 520, 26, 18, "#4d7a32", 0); };

export const headCenter = (seed = 3) => { const H = headBlob(seed, 118, 0), HH = 2 * H.b; return 975 - 1.38 * HH - 1.08 * HH - H.b; };


// ---------------- explainer FX cards (design canvas 600x1000, content centred at (300,500)) ----------------
const pop = (t) => { t = Math.max(0, Math.min(1, t)); const x = t - 1; return x * x * (2.7 * x + 1.7) + 1; };
const bigText = (p, txt, x, y, size, fill = "#ffffff", ol = 18) => {
  const g = p.g; g.save(); g.font = `900 ${size}px Arial Black, Arial, sans-serif`; g.textAlign = "center"; g.textBaseline = "middle"; g.lineJoin = "round";
  g.lineWidth = ol; g.strokeStyle = INK; g.strokeText(txt, x, y); g.fillStyle = fill; g.fillText(txt, x, y); g.restore();
};
export const fxQuestion = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.rotate(rad(-8 + 6 * Math.sin(t * 9))); g.scale(s, s); bigText(p, "?", 0, 0, 340, "#ffd84a", 26); g.restore(); };
export const fxCross = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s); for (const w of [64, 44]) { const c = w === 64 ? INK : "#e0362f"; p.stroke([[-190, -190], [190, 190]], w, c); p.stroke([[190, -190], [-190, 190]], w, c); } g.restore(); };
export const fxCheck = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s); for (const w of [62, 42]) { const c = w === 62 ? INK : "#38b04a"; p.stroke([[-170, 10], [-50, 130], [180, -140]], w, c); } g.restore(); };
/** thermometer for "not a cold" (with a red no-sign over it) */
export const fxThermo = (p, t, cross = true) => {
  const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-46, -230, 46, 120, 46), "#f4f7fb", 12); p.ell(0, 150, 84, 84, "#f4f7fb", 12);
  p.poly(rrect(-20, -60, 20, 130, 20), "#e0362f", 0); p.ell(0, 150, 60, 60, "#e0362f", 0);
  for (let i = 0; i < 5; i++) p.stroke([[46, -190 + i * 44], [i % 2 ? 76 : 96, -190 + i * 44]], 9);
  if (cross) { p.ell(0, 0, 250, 250, null, 0); g.lineWidth = 40; g.strokeStyle = INK; g.beginPath(); g.arc(0, 20, 235, 0, 7); g.moveTo(-166, -146); g.lineTo(206, 186); g.stroke();
  g.lineWidth = 24; g.strokeStyle = "#e0362f"; g.beginPath(); g.arc(0, 20, 235, 0, 7); g.moveTo(-166, -146); g.lineTo(206, 186); g.stroke(); }
  g.restore();
};
/** two vertical airflow bars: a, b in 0..1 (screen-left, screen-right) */
export const fxGauge = (p, t, a = 1, b = 0.3) => {
  const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-250, -330, 250, 330, 50), "#fff7e6", 14);
  for (const [x, v, lab, col] of [[-110, a, "L", "#3fb6e8"], [110, b, "R", "#9bd6ef"]]) {
    p.poly(rrect(x - 62, -250, x + 62, 190, 24), "#dfe9ee", 8);
    const h = 440 * v; p.poly(rrect(x - 62, 190 - h, x + 62, 190, 24), col, 8);
    for (let i = 0; i < 3; i++) { const yy = 190 - h * (0.25 + i * 0.28); if (v > 0.5) p.stroke([[x - 30, yy + 18], [x, yy - 14], [x + 30, yy + 18]], 9, "#ffffff"); }
    bigText(p, lab, x, 262, 90, "#ffffff", 14);
  }
  g.restore();
};
export const fxTitle = (p, t, l1 = "NASAL", l2 = "CYCLE") => {
  const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.rotate(rad(-4)); g.scale(s, s);
  bigText(p, l1, 0, -95, 150, "#ffffff", 26); bigText(p, l2, 0, 75, 150, "#ffd84a", 26); g.restore();
};
export const fxSwap = (p, t) => {
  const g = p.g; g.save(); g.translate(300, 500);
  for (const k of [0, 1]) { g.save(); g.rotate(rad(k * 180 + t * 360)); const pts = []; for (let i = 0; i <= 14; i++) { const a = rad(-20 + i * 11); pts.push([Math.cos(a) * 150, Math.sin(a) * 150]); }
    p.stroke(pts, 46, INK); p.stroke(pts, 28, "#ffd84a"); const e = pts[14], a2 = rad(134); p.poly([[e[0] + Math.cos(a2 - 1.1) * 70, e[1] + Math.sin(a2 - 1.1) * 70], [e[0] + Math.cos(a2 + 0.4) * 70, e[1] + Math.sin(a2 + 0.4) * 70], [e[0] + Math.cos(a2 - 0.35) * 8 + 40 * Math.cos(rad(70)), e[1] + 40 * Math.sin(rad(70))]], "#ffd84a", 12); g.restore(); }
  g.restore();
};
export const fxSparkle = (p, t) => {
  for (let i = 0; i < 4; i++) { const k = (t + i * 0.25) % 1, x = 300 + Math.cos(i * 2.1) * 150, y = 500 + Math.sin(i * 1.7) * 150, r = 70 * Math.sin(k * Math.PI), pts = [];
    for (let j = 0; j < 8; j++) { const rr = j % 2 ? r * 0.28 : r, a = rad(j * 45 - 90); pts.push([x + rr * Math.cos(a), y + rr * Math.sin(a)]); } if (r > 4) p.poly(pts, "#fff7b0", 8); }
};
/** inhale: air lines sweeping into the nose */
export const fxBreath = (p, t, dir = 1, col = "#ffffff") => {
  const g = p.g; g.save(); g.translate(300, 500); g.scale(dir, 1);
  for (let i = 0; i < 3; i++) { const k = (t * 1.4 + i / 3) % 1, y = 70 + i * 55, x0 = 210 - 200 * k, a = Math.sin(k * Math.PI);
    g.globalAlpha = a; const pts = []; for (let j = 0; j <= 8; j++) pts.push([x0 + j * 11, y + Math.sin(j * 0.9 + i) * 8 - 50 * (1 - j / 8) * 0]); p.stroke(pts, 14, INK); p.stroke(pts, 7, col); }
  g.restore();
};
export const fxChoice = (p, t, label = "LEFT") => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-270, -120, 270, 120, 70), label === "LEFT" ? "#3fb6e8" : "#ff7a59", 18); bigText(p, label, 0, 6, 150, "#ffffff", 22); g.restore(); };
/** water drops falling (nose moisture) */
export const fxDrops = (p, t) => { for (let i = 0; i < 3; i++) { const k = (t + i / 3) % 1; p.ell(220 + i * 80, 380 + k * 240, 22, 34, "#9fe0ff", 8); } };

// ---------------- throat-short FX ----------------
const ray = (p, n, r1, r2, w1, w2, col, rot = 0) => { for (let i = 0; i < n; i++) { const a = rot + i * Math.PI * 2 / n, pts = [[Math.cos(a) * r1, Math.sin(a) * r1], [Math.cos(a) * r2, Math.sin(a) * r2]]; p.stroke(pts, w1, INK); p.stroke(pts, w2, col); } };
export const fxIce = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.rotate(rad(-14 + 8 * Math.sin(t * 6))); g.scale(s, s);
  p.poly(rrect(-130, -130, 130, 130, 34), "#bfeaff", 16); p.poly(rrect(-95, -95, -20, -20, 12), "#effaff", 0); p.stroke([[40, -60], [90, -60]], 12, "#effaff"); p.stroke([[60, 90], [100, 50]], 12, "#effaff"); g.restore(); };
export const fxBrain = (p, t, alarm = 0) => { const g = p.g; g.save(); g.translate(300 + (alarm ? Math.sin(t * 60) * 6 : 0), 500);
  p.ell(-70, 0, 130, 110, "#f7a1b8", 14); p.ell(70, 0, 130, 110, "#f7a1b8", 14); p.ell(0, -70, 120, 70, "#f7a1b8", 14);
  for (const [x, y] of [[-90, -10], [-50, 50], [-60, -60], [60, -60], [80, -10], [50, 50]]) p.stroke([[x - 30, y], [x, y - 22], [x + 30, y]], 8, "#c8587a");
  p.stroke([[0, -120], [0, 100]], 7, "#c8587a");
  if (alarm) ray(p, 8, 190, 235 + 40 * Math.abs(Math.sin(t * 20)), 18, 10, "#ff3b30", 0.4);
  g.restore(); };
export const fxAlarm = (p, t) => { const g = p.g; g.save(); g.translate(300, 500); const sh = Math.sin(t * 55) * 0.18; g.rotate(sh);
  p.poly([[-130, 110], [-110, -40], [-60, -130], [0, -150], [60, -130], [110, -40], [130, 110]], "#ffd84a", 14); p.poly(rrect(-160, 100, 160, 140, 18), "#ffd84a", 14); p.ell(0, 175, 36, 36, "#c98a14", 12);
  ray(p, 6, 190, 240, 16, 8, "#ff3b30", 0.2 + t * 3); g.restore(); };
export const fxSun = (p, t) => { const g = p.g; g.save(); g.translate(300, 500); ray(p, 12, 150, 215, 26, 14, "#ffb52e", t * 0.8); p.ell(0, 0, 125, 125, "#ffd84a", 14); g.restore(); };
export const fxShield = (p, t, cracked = 1) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly([[-150, -170], [150, -170], [150, 20], [0, 200], [-150, 20]], "#5aa5ff", 16); p.poly([[-100, -120], [100, -120], [100, 10], [0, 140], [-100, 10]], "#8cc4ff", 0);
  if (cracked) { p.stroke([[10, -170], [-25, -90], [35, -30], [-10, 50], [20, 120]], 18, INK); p.stroke([[10, -170], [-25, -90], [35, -30], [-10, 50], [20, 120]], 8, "#ffffff"); } g.restore(); };
export const fxDropX = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly([[-105, 10], [0, -200], [105, 10]], "#58b8ff", 14); p.ell(0, 70, 118, 118, "#58b8ff", 14); p.ell(0, 60, 100, 100, "#58b8ff", 0);
  p.stroke([[-80, -10], [80, 150]], 40, INK); p.stroke([[80, -10], [-80, 150]], 40, INK); p.stroke([[-80, -10], [80, 150]], 24, "#e0362f"); p.stroke([[80, -10], [-80, 150]], 24, "#e0362f"); g.restore(); };
export const fxFlame = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500 + Math.sin(t * 14) * 5); g.scale(s, s);
  p.poly([[0, -220], [60, -100], [120, -20], [100, 100], [0, 180], [-100, 100], [-120, -20], [-60, -100]], "#ff5a2a", 16); p.poly([[0, -60], [50, 40], [30, 120], [-30, 120], [-50, 40]], "#ffd84a", 0); g.restore(); };
export const fxFire = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.rotate(rad(4 * Math.sin(t * 10))); g.scale(s * 1.25, s * 1.25);
  p.poly([[10, -230], [70, -130], [130, -40], [140, 60], [90, 150], [0, 190], [-90, 150], [-140, 60], [-110, -30], [-60, -90], [-30, -40], [-20, -140]], "#ff4a1a", 16);
  p.poly([[0, -80], [60, 10], [80, 90], [0, 160], [-80, 90], [-60, 10], [-20, -40]], "#ff9a1f", 0); p.poly([[0, 20], [40, 90], [0, 150], [-40, 90]], "#ffe14a", 0); g.restore(); };
export const fxHumidifier = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-110, -10, 110, 200, 44), "#f2f7ff", 14); p.poly(rrect(-90, -50, 90, -10, 18), "#7fc8ff", 12); p.stroke([[-30, -50], [-30, -80]], 18, INK); p.stroke([[-30, -50], [-30, -80]], 8, "#7fc8ff"); p.ell(0, 95, 36, 36, "#7fc8ff", 8);
  for (let i = 0; i < 4; i++) { const k = (t * 0.8 + i / 4) % 1, y = -100 - k * 190, x = -30 + Math.sin(i * 2 + k * 4) * 44, r = 36 + k * 34; g.globalAlpha = 1 - k; p.ell(x, y, r, r * 0.8, "#ffffff", 8); } g.restore(); };
export const fxBottle = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-72, -100, 72, 200, 40), "#58b8ff", 14); p.poly(rrect(-34, -170, 34, -100, 10), "#ffffff", 12); p.poly(rrect(-52, 0, 52, 100, 14), "#ffffff", 8);
  p.stroke([[-50, -40], [-20, -55], [10, -40], [40, -55], [60, -40]], 8, "#effaff"); p.ell(0, 50, 20, 26, "#58b8ff", 6); g.restore(); };
export const fxSpray = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-62, 0, 62, 200, 26), "#cfe9ff", 14); p.poly(rrect(-26, -80, 26, 0, 8), "#ffffff", 12); p.poly(rrect(-40, -135, 40, -80, 16), "#7fc8ff", 12); p.stroke([[40, -108], [70, -108]], 14, INK);
  for (let i = 0; i < 4; i++) { const k = (t * 1.4 + i / 4) % 1; g.globalAlpha = 1 - k; p.ell(90 + k * 130, -108 + Math.sin(i * 3) * 20 * k, 14 + k * 16, 14 + k * 16, "#ffffff", 6); } g.restore(); };
export const fxCalendar = (p, t) => { const s = pop(Math.min(1, t * 3)), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly(rrect(-215, -200, 215, 230, 30), "#fffaf0", 14); p.poly(rrect(-215, -200, 215, -110, 30), "#e0362f", 14); p.stroke([[-120, -230], [-120, -170]], 18, INK); p.stroke([[120, -230], [120, -170]], 18, INK);
  const n = Math.floor(t * 8); g.font = "900 60px Arial Black, Arial, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
  for (let i = 0; i < 7; i++) { const cx = -150 + (i % 4) * 100, cy = -45 + Math.floor(i / 4) * 130; g.fillStyle = INK; g.fillText(String(i + 1), cx, cy); if (i < n) { p.stroke([[cx - 34, cy - 34], [cx + 34, cy + 34]], 12, "#e0362f"); p.stroke([[cx + 34, cy - 34], [cx - 34, cy + 34]], 12, "#e0362f"); } } g.restore(); };
export const fxGerm = (p, t) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500 + Math.sin(t * 8) * 8); g.scale(s, s);
  for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 + 0.2, pts = [[Math.cos(a) * 120, Math.sin(a) * 120], [Math.cos(a) * 190, Math.sin(a) * 190]]; p.stroke(pts, 22, INK); p.stroke(pts, 10, "#5fb82f"); p.ell(pts[1][0], pts[1][1], 22, 22, "#7bd04a", 10); }
  p.ell(0, 0, 150, 150, "#7bd04a", 14); p.ell(-48, -20, 30, 36, "#ffffff", 8); p.ell(48, -20, 30, 36, "#ffffff", 8); p.ell(-42, -14, 12, 14, INK, 0); p.ell(42, -14, 12, 14, INK, 0);
  p.stroke([[-85, -70], [-25, -45]], 14, INK); p.stroke([[85, -70], [25, -45]], 14, INK); p.stroke([[-60, 60], [-30, 40], [0, 60], [30, 40], [60, 60]], 12, INK); g.restore(); };
export const fxGlass = (p, t, lvl = 0.7) => { const s = pop(t), g = p.g; g.save(); g.translate(300, 500); g.scale(s, s);
  p.poly([[-100, -150], [100, -150], [78, 170], [-78, 170]], "#e6f4ff", 14); const y = 170 - 300 * lvl, w = 78 + (100 - 78) * (1 - (y + 150) / 320 * 0 ) ;
  p.poly([[-98 + (170 - y > 0 ? 0 : 0), y], [98, y], [78, 160], [-78, 160]], "#58b8ff", 0); p.stroke([[-70, -110], [-58, 90]], 10, "#ffffff"); g.restore(); };
