// ---------- world: gold-rush western town ----------
const DECK = 0;
const world = new THREE.Group(); scene.add(world);
const rr = P.rng(11);
const NDSKIP = (m) => { m.userData.ndSkip = true; return m; };
const C = (c) => toon({ color: c });
const V3 = (a) => new THREE.Vector3(...a);
const rays = [], kelps = [];
const SXs = SETX;

// ---- canvas helpers ----
const plankLines = (g, w, h, step, a = 0.14, vertical = true) => { g.fillStyle = `rgba(30,15,5,${a})`; for (let i = 0; i < (vertical ? w : h); i += step) { if (vertical) g.fillRect(i, 0, 2, h); else g.fillRect(0, i, w, 2); } };
const paintText = (g, text, cx, cy, size, fill, ol = 0.14) => { g.save(); g.font = `900 ${size}px 'Arial Black', Impact, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round'; g.lineWidth = size * ol; g.strokeStyle = '#2a1a14'; g.strokeText(text, cx, cy); g.fillStyle = fill; g.fillText(text, cx, cy); g.restore(); };
const dirtTex = cvTex(512, 512, (g, w, h) => {
  g.fillStyle = '#dcb888'; g.fillRect(0, 0, w, h); const r = P.rng(5);
  for (let i = 0; i < 700; i++) { g.fillStyle = r() < 0.5 ? 'rgba(150,100,55,0.18)' : 'rgba(255,235,190,0.25)'; const s = 2 + r() * 8; g.fillRect(r() * w, r() * h, s, s * 0.6); }
  for (let i = 0; i < 40; i++) { g.fillStyle = 'rgba(110,80,50,0.5)'; g.beginPath(); g.ellipse(r() * w, r() * h, 3 + r() * 5, 2 + r() * 3, 0, 0, 7); g.fill(); }
  g.fillStyle = 'rgba(130,90,50,0.22)'; g.fillRect(w * 0.3, 0, 22, h); g.fillRect(w * 0.62, 0, 22, h);
}, 5, 12);
const cloudTex = cvTex(512, 256, (g, w, h) => { g.fillStyle = '#ffffff'; for (const [x, y, r] of [[120, 160, 70], [210, 120, 90], [320, 140, 80], [400, 170, 60], [260, 175, 70]]) { g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); } g.fillRect(100, 170, 330, 40); g.fillStyle = 'rgba(190,210,235,0.5)'; g.fillRect(100, 190, 330, 24); });
const facadeTex = (o) => { const S = 52, wpx = Math.round(o.w * S), hpx = Math.round((o.h + o.ff) * S);
  return cvTex(wpx, hpx, (g, w, h) => {
    g.fillStyle = o.col; g.fillRect(0, 0, w, h); plankLines(g, w, h, 13, 0.16);
    const rg = P.rng(o.seed || 3); for (let i = 0; i < 30; i++) { g.fillStyle = `rgba(255,255,255,${0.04 + rg() * 0.05})`; g.fillRect(rg() * w, rg() * h, 3, 10 + rg() * 30); }
    const ffH = o.ff * S; g.fillStyle = 'rgba(0,0,0,0.18)'; g.fillRect(0, ffH - 6, w, 6); g.fillStyle = o.trim || '#f1e6c8'; g.fillRect(0, 0, w, 10); g.fillRect(0, ffH - 12, w, 12);
    if (o.sign) { g.fillStyle = o.signBg || '#f4e7c0'; g.fillRect(w * 0.08, 16, w * 0.84, ffH - 34); g.strokeStyle = '#3a2418'; g.lineWidth = 5; g.strokeRect(w * 0.08, 16, w * 0.84, ffH - 34); paintText(g, o.sign, w / 2, 16 + (ffH - 34) / 2 + 2, Math.min((ffH - 44), w * 0.84 / (o.sign.length * 0.72)), o.signCol || '#7a2a1c', 0.06); }
    const wy = ffH + 0.55 * S, ww = 0.9 * S, wh = 1.25 * S;
    for (const wx of [0.18 * w, 0.82 * w - ww]) { g.fillStyle = '#2a1a14'; g.fillRect(wx - 6, wy - 6, ww + 12, wh + 12); g.fillStyle = o.glass || '#9fd2f0'; g.fillRect(wx, wy, ww, wh); g.fillStyle = 'rgba(255,255,255,0.4)'; g.beginPath(); g.moveTo(wx + 8, wy + wh - 6); g.lineTo(wx + 8 + 18, wy + 6); g.lineTo(wx + 8 + 36, wy + 6); g.lineTo(wx + 8 + 18, wy + wh - 6); g.fill(); g.fillStyle = '#2a1a14'; g.fillRect(wx + ww / 2 - 2, wy, 4, wh); g.fillRect(wx, wy + wh / 2 - 2, ww, 4); }
    const dw = 0.95 * S, dh = 1.9 * S; g.fillStyle = '#2a1a14'; g.fillRect(w / 2 - dw / 2 - 6, h - dh - 6, dw + 12, dh + 6); g.fillStyle = o.door || '#6a4328'; g.fillRect(w / 2 - dw / 2, h - dh, dw, dh); g.fillStyle = 'rgba(0,0,0,0.2)'; g.fillRect(w / 2 - 2, h - dh, 4, dh); g.fillStyle = '#e8c45a'; g.beginPath(); g.arc(w / 2 + 12, h - dh / 2, 4, 0, 7); g.fill();
    if (o.banner) paintText(g, o.banner, w / 2, ffH + 0.2 * S, 0.34 * S, '#f4e7c0', 0.16);
  }); };
const signTex = (text, bg, fg, w = 512, h = 256) => cvTex(w, h, (g, W, H) => { g.fillStyle = bg; g.fillRect(0, 0, W, H); plankLines(g, W, H, 22, 0.15, false); g.strokeStyle = '#3a2418'; g.lineWidth = 12; g.strokeRect(6, 6, W - 12, H - 12); const lines = text.split('\n'); lines.forEach((l, i) => paintText(g, l, W / 2, H / 2 + (i - (lines.length - 1) / 2) * H * 0.4, Math.min(H * 0.38, W * 0.88 / (l.length * 0.68)), fg, 0.1)); });

const mat = (map, extra = {}) => toon({ map, ...extra });
/** street-facing building. side -1 = left row (faces +x), +1 = right row (faces -x) */
const building = (side, zc, o) => {
  const d = o.d || 5, bx = side * (3.5 + d / 2), g = new THREE.Group(); g.position.set(bx, 0, zc); world.add(g);
  add(box(d, o.h, o.w), C(o.wall || '#8a6a48'), 0, o.h / 2, 0, g);
  add(box(0.5, o.ff, o.w), C(o.col), -side * (d / 2 - 0.25), o.h + o.ff / 2, 0, g);
  const fp = add(new THREE.PlaneGeometry(o.w, o.h + o.ff), mat(facadeTex(o)), -side * (d / 2 + 0.012), (o.h + o.ff) / 2, 0, g, { cast: false });
  fp.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
  // porch
  const pw = o.w - 0.3, px = -side * (d / 2 + 0.9);
  add(box(1.8, 0.14, pw), C('#a87a4a'), px, 0.07, 0, g, { cast: false });
  add(box(1.9, 0.12, pw + 0.1), C(o.trim || '#e8d9b0'), px, 3.4, 0, g);
  for (const zz of [-pw / 2 + 0.2, pw / 2 - 0.2, 0]) add(new THREE.CylinderGeometry(0.07, 0.07, 3.4, 8), C('#7a5230'), -side * (d / 2 + 1.6), 1.7, zz, g);
  add(box(d + 0.1, 0.12, o.w + 0.1), C('#6a5038'), 0, o.h + 0.06, 0, g);
  return g;
};
const post = (x, z, h = 2.2, col = '#6a4a2c') => add(new THREE.CylinderGeometry(0.09, 0.11, h, 8), C(col), x, h / 2, z, world);
const signPost = (x, z, text, bg = '#d9b36a', fg = '#3a1c10', ry = 0, w = 1.9, h = 0.95, y = 1.9) => {
  const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; world.add(grp);
  for (const dx of [-w / 2 + 0.15, w / 2 - 0.15]) add(new THREE.CylinderGeometry(0.07, 0.08, y + h / 2, 8), C('#5a3a20'), dx, (y + h / 2) / 2, 0, grp);
  const fb = add(new THREE.PlaneGeometry(w, h), mat(signTex(text, bg, fg, 512, Math.round(512 * h / w))), 0, y, 0.09, grp); add(box(w + 0.1, h + 0.1, 0.12), C('#3a2418'), 0, y, 0, grp);
  const bk = add(new THREE.PlaneGeometry(w, h), C('#5a3a20'), 0, y, -0.07, grp); bk.rotation.y = Math.PI; return grp;
};
const barrel = (x, z, r = 0.38) => { const g = add(new THREE.CylinderGeometry(r, r * 0.92, r * 2.1, 14), C('#8a5a30'), x, r * 1.05, z, world); add(new THREE.TorusGeometry(r * 0.97, 0.03, 6, 20), C('#2a1a14'), x, r * 0.55, z, world).rotation.x = Math.PI / 2; add(new THREE.TorusGeometry(r * 0.97, 0.03, 6, 20), C('#2a1a14'), x, r * 1.55, z, world).rotation.x = Math.PI / 2; return g; };
const crate = (x, z, s = 0.7, ry = 0) => { const c = add(box(s, s, s), C('#a67a46'), x, s / 2, z, world); c.rotation.y = ry; return c; };
const cactus = (x, z, h = 1.6) => { const g = new THREE.Group(); g.position.set(x, 0, z); world.add(g); add(new THREE.CapsuleGeometry(0.2, h, 6, 10), C('#4f8a4a'), 0, h / 2 + 0.2, 0, g); add(new THREE.CapsuleGeometry(0.12, 0.5, 6, 8), C('#4f8a4a'), 0.35, h * 0.55, 0, g).rotation.z = 0.2; add(new THREE.CapsuleGeometry(0.12, 0.4, 6, 8), C('#4f8a4a'), -0.32, h * 0.7, 0, g).rotation.z = -0.2; };
const rock = (x, y, z, r, col = '#a07a58') => { const k = add(new THREE.DodecahedronGeometry(r, 0), C(col), x, y + r * 0.5, z, world); k.scale.set(1.3, 0.8, 1); k.rotation.y = rr() * 3; return k; };
const mesa = (x, z, rb, rt, h, col) => add(new THREE.CylinderGeometry(rt, rb, h, 7, 1), mat(cvTex(64, 256, (g, w, hh) => { const gr = g.createLinearGradient(0, 0, 0, hh); gr.addColorStop(0, '#e08a56'); gr.addColorStop(0.35, '#c8643c'); gr.addColorStop(0.7, '#a8482c'); gr.addColorStop(1, '#8a3a26'); g.fillStyle = gr; g.fillRect(0, 0, w, hh); for (let i = 0; i < 8; i++) { g.fillStyle = 'rgba(60,20,10,0.16)'; g.fillRect(0, i * 32 + 8, w, 5); } }), { color: col || '#ffffff' }), x, h / 2 - 0.2, z, world, { cast: false });

// ---- the town street (set at x = 0), runs along -z ----
{
  const gr = add(new THREE.PlaneGeometry(160, 320), mat(dirtTex), 0, 0, -90, world, { cast: false }); gr.rotation.x = -Math.PI / 2; gr.material.map.repeat.set(10, 26);
  const walls = ['#8a5a3a', '#6a4a30', '#7a5a40'];
  const L = [
    { z: -4.5, w: 6.2, h: 3.8, ff: 1.5, col: '#2f6a4a', sign: 'BRANNAN STORE', signCol: '#7a1c14', seed: 2, banner: 'SHOVELS  PICKS  PANS', trim: '#f4e7c0' },
    { z: -12, w: 5.6, h: 3.6, ff: 1.2, col: '#3f6aa8', sign: 'HOTEL', signCol: '#1d3a6a', seed: 4 },
    { z: -19.5, w: 6.4, h: 3.9, ff: 1.4, col: '#d9c79a', sign: 'GENERAL STORE', signCol: '#6a4a1c', seed: 6, banner: '' },
    { z: -27.5, w: 5.8, h: 3.5, ff: 1.2, col: '#4a8a7a', sign: 'BARBER', signCol: '#1d4a3a', seed: 9 },
    { z: -35.5, w: 6.4, h: 3.9, ff: 1.5, col: '#8a4a32', sign: 'FEED & LIVERY', signCol: '#5a2a1a', seed: 12 },
    { z: -44, w: 6, h: 3.6, ff: 1.2, col: '#c9a86a', sign: 'ASSAY OFFICE', signCol: '#5a3a10', seed: 15 },
    { z: -53, w: 6.4, h: 3.8, ff: 1.4, col: '#a8533a', sign: 'HOTEL', signCol: '#5a2218', seed: 18 },
  ];
  const Rr = [
    { z: -5.5, w: 6, h: 3.7, ff: 1.3, col: '#c9a86a', sign: 'GOLD BUYER', signCol: '#5a3a10', seed: 21 },
    { z: -13.5, w: 6.2, h: 3.9, ff: 1.5, col: '#5a74a8', sign: 'BANK', signCol: '#1d2f5a', seed: 24 },
    { z: -21.5, w: 5.8, h: 3.5, ff: 1.2, col: '#b24a3a', sign: 'GUNS & PICKS', signCol: '#8a1c14', seed: 27 },
    { z: -29.5, w: 6.4, h: 3.8, ff: 1.4, col: '#d9c79a', sign: 'BEER 5¢', signCol: '#6a3a10', seed: 30 },
    { z: -38, w: 6, h: 3.6, ff: 1.3, col: '#6a4a8a', sign: 'PHOTOGRAPHS', signCol: '#3a1d5a', seed: 33 },
    { z: -47, w: 6.4, h: 3.9, ff: 1.4, col: '#3f8a6a', sign: 'LAND OFFICE', signCol: '#1d4a2a', seed: 36 },
    { z: -56, w: 6, h: 3.7, ff: 1.2, col: '#b8704a', sign: 'SALOON', signCol: '#7a2a1c', seed: 39 },
  ];
  L.forEach((o, i) => building(-1, o.z, { ...o, wall: walls[i % 3] })); Rr.forEach((o, i) => building(1, o.z, { ...o, wall: walls[(i + 1) % 3] }));
  // end of the street: open desert + mesas
  for (const [x, z, rb, rt, h] of [[-38, -120, 16, 12, 26], [-8, -150, 22, 16, 22], [34, -135, 18, 13, 30], [70, -110, 14, 10, 18], [-70, -100, 15, 11, 20], [10, -190, 30, 24, 24]]) mesa(x, z, rb, rt, h);
  for (let i = 0; i < 6; i++) add(new THREE.ConeGeometry(18 + rr() * 10, 14 + rr() * 12, 6), C('#7d93b8'), -70 + i * 28, 7, -230, world, { cast: false });
  // props along the street
  signPost(2.7, 1.4, 'TO\nCALIFORNIA!', '#e8c45a', '#3a1c10', -0.35, 1.5, 0.9, 1.5);
  { const g = new THREE.Group(); g.position.set(0, 0, -17); world.add(g);
    for (const x of [-3.3, 3.3]) add(new THREE.CylinderGeometry(0.12, 0.15, 5.4, 8), C('#5a3a20'), x, 2.7, 0, g);
    add(new THREE.PlaneGeometry(6.6, 1.35), mat(signTex('GOLD RUSH 1848!', '#e8c45a', '#8a1c14', 1024, 210)), 0, 4.6, 0.09, g); add(box(6.8, 1.5, 0.15), C('#3a2418'), 0, 4.6, 0, g); }
  for (const [x, z] of [[-3.2, -9], [3.3, -17], [-3.3, -25], [3.2, -33]]) barrel(x, z);
  crate(3.2, -9.5, 0.7, 0.4); crate(-3.3, -16, 0.6, 0.2); crate(-3.2, -30, 0.8, 0.1);
  for (const [x, z] of [[-2.6, -3.0], [3.4, -2], [5.4, -10], [-6, -8]]) cactus(x, z, 1.1 + rr() * 0.9);
  for (const [x, z, r] of [[5, 0.5, 0.3], [-5.5, 2, 0.4], [7, -3, 0.5], [-8, -1, 0.35]]) rock(x, 0, z, r);
  for (let i = 0; i < 7; i++) { const z = -6 - i * 9, pole = add(new THREE.CylinderGeometry(0.08, 0.1, 6, 8), C('#5a3a20'), 3.55, 3, z, world); add(box(1.2, 0.1, 0.1), C('#5a3a20'), 3.55, 5.6, z, world); }
  // hitching rails
  for (const [x, z] of [[-3.0, -4.5], [3.0, -6]]) { post(x, z - 0.9, 1.1); post(x, z + 0.9, 1.1); add(box(0.1, 0.1, 2.0), C('#6a4a2c'), x, 0.95, z, world); }
  // sky clouds
  const cm = new THREE.MeshBasicMaterial({ map: cloudTex, transparent: true, depthWrite: false, fog: false });
  for (const [x, y, z, s] of [[-30, 36, -160, 26], [20, 42, -170, 32], [60, 30, -150, 22], [-70, 26, -140, 24], [0, 55, -120, 20]]) { const c = NDSKIP(add(new THREE.PlaneGeometry(s, s / 2), cm, x, y, z, world, { cast: false })); c.userData.cloud = 1; }
}
// ---------- shared props ----------
const woodTex = (col, step = 40, vertical = true) => cvTex(256, 256, (g, ww, hh) => { g.fillStyle = col; g.fillRect(0, 0, ww, hh); plankLines(g, ww, hh, step, 0.2, vertical); const r = P.rng(9); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(255,255,255,${0.03 + r() * 0.05})`; g.fillRect(r() * ww, r() * hh, 4, 30 + r() * 50); } }, 6, 6);
const shovelG = (parent, x, y, z, ry = 0, kind = 'shovel', tilt = 0) => {
  const g = new THREE.Group(); g.position.set(x, y, z); g.rotation.set(0, ry, tilt); parent.add(g);
  add(new THREE.CylinderGeometry(0.03, 0.03, 1.5, 6), C('#8a5a30'), 0, 0.75, 0, g, { cast: false });
  if (kind === 'shovel') add(box(0.3, 0.38, 0.03), C('#aab4be'), 0, 1.66, 0, g, { cast: false }); else add(box(0.7, 0.09, 0.06), C('#8f9aa6'), 0, 1.5, 0, g, { cast: false });
  return g;
};
const sack = (x, z, s = 0.5, col = '#d9c79a') => add(new THREE.CapsuleGeometry(s * 0.5, s * 0.6, 6, 10), C(col), x, s * 0.55, z, world);
const stackCrates = (x, z, nx, ny, s = 0.8) => { for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const c = add(box(s, s, s), C(['#a67a46', '#b58a52', '#96703e'][(i + j) % 3]), x + i * (s + 0.03), s / 2 + j * s, z, world); c.rotation.y = 0.04 * ((i * 3 + j * 5) % 5 - 2); } };
const lampG = (x, y, z) => { add(new THREE.SphereGeometry(0.22, 12, 10), new THREE.MeshBasicMaterial({ color: '#ffe9a8' }), x, y, z, world, { cast: false }); add(new THREE.CylinderGeometry(0.01, 0.01, 1.2, 4), C('#2a1a14'), x, y + 0.7, z, world, { cast: false }); };
const glowPlane = (x, y, z, w, h, col = '#fff6d8', ry = 0) => { const m = NDSKIP(add(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: col }), x, y, z, world, { cast: false })); m.rotation.y = ry; return m; };
const room = (x0, W, D, zFront, wallCol, floorCol) => {
  const fl = add(new THREE.PlaneGeometry(W, D), mat(woodTex(floorCol, 36, true)), x0, 0.0, zFront - D / 2, world, { cast: false }); fl.rotation.x = -Math.PI / 2; fl.material.map.repeat.set(W / 3, D / 3);
  const wt = mat(woodTex(wallCol, 30, true)); wt.map.repeat.set(4, 2);
  add(box(W, 6, 0.3), wt, x0, 3, zFront - D, world, { cast: false });
  add(box(0.3, 6, D), wt, x0 - W / 2, 3, zFront - D / 2, world, { cast: false }); add(box(0.3, 6, D), wt, x0 + W / 2, 3, zFront - D / 2, world, { cast: false });
  const ce = add(new THREE.PlaneGeometry(W, D), new THREE.MeshBasicMaterial({ color: '#5a3d28' }), x0, 6, zFront - D / 2, world, { cast: false }); ce.rotation.x = Math.PI / 2; NDSKIP(ce);
  for (let z = zFront - 1; z > zFront - D; z -= 3.2) { add(box(W, 0.25, 0.25), C('#5a3a20'), x0, 4.6, z, world); }
  for (const dx of [-W / 2 + 0.2, W / 2 - 0.2]) for (let z = zFront - 1; z > zFront - D; z -= 3.2) add(box(0.22, 4.6, 0.22), C('#5a3a20'), x0 + dx, 2.3, z, world);
};
// ---- hills: the gold fields (x = 100) ----
{
  const x0 = SXs.hills, rg = P.rng(31);
  const gr = add(new THREE.PlaneGeometry(130, 240), mat(dirtTex), x0, -0.01, -80, world, { cast: false }); gr.rotation.x = -Math.PI / 2; gr.material.map.repeat.set(9, 20);
  // river on the left with sandy banks and ripples
  const rv = add(new THREE.PlaneGeometry(5.4, 160), toon({ color: '#4fb0da' }), x0 - 8.6, 0.03, -50, world, { cast: false }); rv.rotation.x = -Math.PI / 2;
  for (const s of [-1, 1]) { const b = add(new THREE.PlaneGeometry(1.4, 160), toon({ color: '#e6cf9a' }), x0 - 8.6 + s * 3.4, 0.02, -50, world, { cast: false }); b.rotation.x = -Math.PI / 2; }
  for (let i = 0; i < 40; i++) { const l = NDSKIP(add(new THREE.PlaneGeometry(0.08, 0.7 + rg() * 1.4), new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, opacity: 0.7 }), x0 - 10.6 + rg() * 4.0, 0.05, 6 - rg() * 60, world, { cast: false })); l.rotation.x = -Math.PI / 2; }
  for (let i = 0; i < 14; i++) add(new THREE.SphereGeometry(0.28 + rg() * 0.3, 8, 6), C(['#8a8a82', '#a0a096', '#74746c'][i % 3]), x0 - 6.2 + (i % 2) * 5.4 + rg() * 0.6, 0.12, 5 - i * 4.2, world).scale.y = 0.6;
  // dirt piles (diggings)
  for (let i = 0; i < 46; i++) { const mx = x0 - 3.6 + rg() * 21, mz = 2 - rg() * 36, r = 0.45 + rg() * 0.55; const m = add(new THREE.SphereGeometry(r, 10, 8), C(['#b88a58', '#a87a4a', '#c99a68'][i % 3]), mx, r * 0.18, mz, world); m.scale.y = 0.6; if (rg() < 0.7) { const h = add(new THREE.CircleGeometry(r * 0.8, 12), C('#5a3a22'), mx + r * 1.1, 0.02, mz + 0.5, world, { cast: false }); h.rotation.x = -Math.PI / 2; } }
  // tents with dark door flaps
  for (let i = 0; i < 16; i++) { const tx = x0 - 13 + (i % 8) * 4.4 + rg() * 1.2, tz = -30 - Math.floor(i / 8) * 5 - rg() * 2; const g = new THREE.Group(); g.position.set(tx, 0, tz); g.rotation.y = rg() * 0.6 - 0.3; world.add(g); add(new THREE.ConeGeometry(1.5, 1.8, 4), C(['#f1e8d0', '#e0d4b4', '#d8dcc8'][i % 3]), 0, 0.9, 0, g).rotation.y = Math.PI / 4; const d = add(new THREE.PlaneGeometry(0.55, 0.9), C('#3a2a1e'), 0, 0.5, 1.07, g, { cast: false }); d.rotation.x = -0.08; }
  // sluice boxes
  for (let i = 0; i < 5; i++) { const g = new THREE.Group(); g.position.set(x0 + 5 + i * 2.8, 0, -3 - i * 4.4); g.rotation.y = 0.3; world.add(g); add(box(3, 0.35, 0.7), C('#a67a46'), 0, 0.7, 0, g); for (const dx of [-1.2, 1.2]) add(box(0.12, 0.7, 0.5), C('#6a4a2c'), dx, 0.35, 0, g); }
  // far land: rolling green hills, pines, red mesas, snowy peaks
  for (let i = 0; i < 14; i++) { const s = add(new THREE.SphereGeometry(1, 14, 10), C(['#8f9d5c', '#a8a463', '#7a8a52'][i % 3]), x0 - 60 + i * 11 + rg() * 5, 0, -62 - rg() * 22, world, { cast: false }); s.scale.set(10 + rg() * 8, 5 + rg() * 5, 9 + rg() * 6); }
  for (let i = 0; i < 70; i++) { const tx = x0 - 30 + rg() * 70, tz = -38 - rg() * 34, h = 1.6 + rg() * 1.6; const g = new THREE.Group(); g.position.set(tx, 0, tz); world.add(g); add(new THREE.CylinderGeometry(0.1, 0.12, 0.7, 5), C('#5a3a22'), 0, 0.35, 0, g); add(new THREE.ConeGeometry(0.7 + 0.2 * rg(), h, 7), C(['#4f7a3a', '#3f6a34', '#5a8a42'][i % 3]), 0, 0.7 + h / 2, 0, g); }
  for (const [x, z, rb, rt, h] of [[-50, -105, 15, 11, 22], [-8, -125, 20, 14, 26], [40, -115, 16, 12, 18], [90, -100, 14, 10, 20], [8, -170, 28, 22, 24]]) mesa(x0 + x, z, rb, rt, h);
  for (const x of [-34, 30]) add(new THREE.ConeGeometry(24, 30, 7), C('#8ea4c8'), x0 + x, 15, -165, world, { cast: false });
  const cm2 = new THREE.MeshBasicMaterial({ map: cloudTex, transparent: true, depthWrite: false, fog: false });
  for (const [x, y, z, s] of [[-30, 36, -160, 26], [20, 42, -170, 32], [60, 30, -150, 22]]) NDSKIP(add(new THREE.PlaneGeometry(s, s / 2), cm2, x0 + x, y, z, world, { cast: false }));
}
// ---- warehouse interior (x = 200): rows of shovels and picks ----
{
  const x0 = SXs.wh; room(x0, 12, 20, 6, '#8a6a48', '#a98558');
  for (const s of [-1, 1]) { add(box(0.7, 0.4, 17), C('#6a4a2c'), x0 + s * 5.5, 0.2, -4.5, world); for (let z = 5; z > -13; z -= 0.17) { const k = Math.round(z * 10) % 3; shovelG(world, x0 + s * 5.5 + (k === 1 ? -0.0 : 0), 0.3, z, Math.PI / 2, k === 2 ? 'pick' : 'shovel'); } }
  for (const s of [-1, 1]) { add(box(0.7, 0.4, 17), C('#6a4a2c'), x0 + s * 4.6, 0.2, -4.5, world); for (let z = 5; z > -13; z -= 0.17) { const k = Math.round(z * 10 + 1) % 4; shovelG(world, x0 + s * 4.6, 0.3, z, Math.PI / 2, k === 0 ? 'pick' : 'shovel'); } }
  add(box(11, 0.5, 0.7), C('#6a4a2c'), x0, 0.25, -12.2, world); for (let x = -5; x < 5; x += 0.17) { const k = Math.round(x * 10) % 3; shovelG(world, x0 + x, 0.5, -12.2, 0, k === 0 ? 'pick' : 'shovel'); }
  add(box(11, 0.5, 0.7), C('#6a4a2c'), x0, 0.25, -11.2, world); for (let x = -5; x < 5; x += 0.17) shovelG(world, x0 + x, 0.5, -11.2, 0, Math.round(x * 10) % 2 ? 'shovel' : 'pick');
  stackCrates(x0 - 3.2, -6, 3, 3); stackCrates(x0 + 1.8, -8, 3, 2); sack(x0 + 0.8, -3.2, 0.6); sack(x0 + 1.4, -3.6, 0.55, '#c9b78a'); sack(x0 - 1.4, -2.6, 0.6, '#bfae82'); barrel(x0 + 3.0, -3.5); barrel(x0 + 3.7, -3.9); barrel(x0 - 2.8, -2.0);
  for (let z = 4; z > -12; z -= 3.2) for (let k = 0; k < 3; k++) add(new THREE.CylinderGeometry(0.28, 0.28, 0.03, 14), C('#9aa6b2'), x0 - 3 + k * 3, 3.5, z, world, { cast: false });
  for (const [dx, t, col] of [[-3.6, 'SHOVELS', '#2f6a4a'], [0, 'PICKS', '#7a1c14'], [3.6, 'PANS', '#2a4f7a']]) add(new THREE.PlaneGeometry(3.1, 0.95), mat(signTex(t, col, '#ffe9a0', 768, 236)), x0 + dx, 4.4, -13.7, world, { cast: false });
  for (const s of [-1, 1]) add(new THREE.PlaneGeometry(4.2, 1.1), mat(signTex('BRANNAN & CO.', '#3a2418', '#ffe9a0', 1024, 272)), x0 + s * 5.82, 4.4, -4.5, world, { cast: false }).rotation.y = -s * Math.PI / 2;
  glowPlane(x0, 2.2, -12.9, 5, 4.4, '#fff6d8');
}
// ---- Brannan's shop interior (x = 300) ----
{
  const x0 = SXs.shop; room(x0, 11, 15, 6, '#9a7650', '#a98558');
  for (const [y, n] of [[1.1, 0], [1.9, 1], [2.7, 2]]) { add(box(9.6, 0.1, 0.6), C('#6a4a2c'), x0, y, -7.0, world); for (let x = -4.4; x < 4.5; x += 0.55) { if ((n + Math.round(x * 2)) % 3 === 0) add(new THREE.CylinderGeometry(0.22, 0.22, 0.04, 14), C('#9aa6b2'), x0 + x, y + 0.08, -7.0, world, { cast: false }); else if ((n + Math.round(x * 2)) % 3 === 1) sack(x0 + x, -7.0, 0.3, ['#e8dcc0', '#cfc09a', '#d9c79a'][(x * 7 | 0) % 3]).position.y = y + 0.22; else add(box(0.3, 0.26, 0.3), C('#b58a52'), x0 + x, y + 0.18, -7.0, world); } }
  for (let x = -4.6; x < 4.7; x += 0.2) shovelG(world, x0 + x, 3.2, -7.4, 0, Math.round(x * 5) % 3 ? 'shovel' : 'pick').rotation.x = 0;
  add(box(7.6, 1.15, 1.0), C('#7a5230'), x0, 0.575, -3.2, world); add(box(7.9, 0.12, 1.2), C('#a8784a'), x0, 1.2, -3.2, world);
  for (const [x, n] of [[-2.8, 4], [-0.3, 6], [2.0, 3], [3.0, 5]]) for (let i = 0; i < n; i++) add(new THREE.CylinderGeometry(0.17, 0.17, 0.035, 14), C(i % 2 ? '#e0a512' : '#ffd75a'), x0 + x, 1.28 + i * 0.04, -3.1, world, { cast: false });
  glowPlane(x0 - 5.3, 2.4, -2.0, 3.0, 2.2, '#fff6d8', Math.PI / 2); lampG(x0 + 1, 4.0, -2); lampG(x0 - 2.6, 4.0, -5);
  barrel(x0 - 4.6, -6.2); barrel(x0 + 4.6, -6.0); sack(x0 + 4.2, -4.6, 0.7); crate(x0 - 4.5, -4.5, 0.8, 0.2);
  add(new THREE.PlaneGeometry(4.6, 1.2), mat(signTex('BRANNAN STORE', '#2f6a4a', '#ffe9a0', 1024, 267)), x0, 4.5, -8.82, world, { cast: false });
  add(box(1.2, 0.5, 0.06), mat(signTex('OPEN', '#d9b36a', '#8a1c14', 256, 110)), x0 + 4.6, 2.3, -7.3, world, { cast: false });
}
