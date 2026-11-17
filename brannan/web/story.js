// "Gold rush: sell the shovels" — western short, 60 s = 1800 frames @ 30 fps. 33 shots.
import { q } from './motion.js';
export const FPS = 30, TOTAL = 2050, DECK = 0;
export const SETX = { st: 0, hills: 100, wh: 200, shop: 300 };
const H = SETX.hills, W = SETX.wh, S0 = SETX.shop;

// id, first frame, last frame, light
const SH = (id, a, b, light = 'day') => ({ id, a, b, light });
export const SHOTS = [
  // 0-6 s: the rush
  SH('wide', 0, 35), SH('crowd', 36, 65), SH('side', 66, 101), SH('face', 102, 137), SH('dream', 138, 179),
  // 6-12 s: digging, panning, nuggets
  SH('hillsA', 180, 215), SH('digCU', 216, 255), SH('pan', 256, 305), SH('nugget', 306, 359),
  // 12-18 s: Brannan watches
  SH('brStreet', 360, 419), SH('brFace', 420, 479), SH('brWatch', 480, 539),
  // 18-25 s: warehouses
  SH('whWide', 540, 589, 'int'), SH('whDeal', 590, 639, 'int'), SH('whRack', 640, 689, 'int'), SH('whHero', 690, 749, 'int'),
  // 25-32 s: shouting in the street
  SH('shout', 750, 809), SH('listen', 810, 869), SH('paperCU', 870, 914), SH('turn', 915, 959),
  // 32-40 s: the crowd comes to the store
  SH('crowdBig', 960, 1019), SH('storeDoor', 1020, 1079), SH('shopIn', 1080, 1139, 'int'), SH('coinsCtr', 1140, 1199, 'int'),
  // 40-49 s: counting coins, overflowing store
  SH('count', 1200, 1259, 'int'), SH('overflow', 1260, 1329, 'int'), SH('bags', 1330, 1399, 'int'), SH('whistle', 1400, 1469, 'int'),
  // 49-60 s: contrast
  SH('thousands', 1470, 1529), SH('brCalm', 1530, 1589, 'int'), SH('miner', 1590, 1649), SH('brSit', 1650, 1709, 'gold'), SH('final', 1710, 1799, 'gold'),
];
// real start frame of each shot, locked to the voiceover (shot ranges a..b above are storyboard-time used for animation)
const RS = { wide: 0, crowd: 50, side: 92, face: 142, dream: 192, hillsA: 251, digCU: 286, pan: 325, nugget: 373, brStreet: 426, brFace: 489, brWatch: 551,
  whWide: 614, whDeal: 675, whRack: 736, whHero: 797, shout: 869, listen: 940, paperCU: 1011, turn: 1064, crowdBig: 1116, storeDoor: 1190, shopIn: 1264, coinsCtr: 1338,
  count: 1412, overflow: 1466, bags: 1511, whistle: 1565, thousands: 1600, brCalm: 1682, miner: 1777, brSit: 1857, final: 1926 };
const SHOTS_R = SHOTS.map((s, i) => ({ ...s, rs: RS[s.id], re: i + 1 < SHOTS.length ? RS[SHOTS[i + 1].id] : TOTAL, idx: i }));
export const shotAt = (f) => {
  let S = SHOTS_R[0]; for (const s of SHOTS_R) if (f >= s.rs) S = s;
  const u = Math.max(0, f - S.rs); return { ...S, u, D: S.re - S.rs, fa: S.a + u };
};
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const smooth = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
const ramp = (f, a, b) => clamp((f - a) / (b - a));
const frac = (x) => ((x % 1) + 1) % 1;
const hash = (i, k = 0) => { const x = Math.sin(i * 127.1 + k * 311.7) * 43758.5453; return x - Math.floor(x); };

const L0 = { fogNear: 70, fogFar: 300, sat: 1.14, vig: 0.26, shadowExt: 16 };
export const LIGHTS = {
  day: { ...L0, az: 58, el: 46, sky: '#fff3dd', ground: '#d9a870', hemi: 1.1, sun: '#ffe2b0', sunI: 2.5, fog: '#f1dfc0', skyTop: '#3f9de8', skyHor: '#e2f1ff', gain: '#fff3e2', vig: 0.22 },
  int: { ...L0, fogNear: 40, fogFar: 140, sat: 1.1, vig: 0.34, shadowExt: 12, az: 80, el: 62, sky: '#ffe2b4', ground: '#b88a5a', hemi: 1.15, sun: '#ffd49a', sunI: 1.9, fog: '#d9b888', skyTop: '#5a3c28', skyHor: '#7a5a3c', gain: '#fff0d4', lift: '#080300' },
  gold: { ...L0, az: 18, el: 17, sky: '#ffcf9a', ground: '#b8663a', hemi: 0.95, sun: '#ffa85a', sunI: 3.1, fog: '#f2b27a', fogNear: 40, fogFar: 200, skyTop: '#d9663a', skyHor: '#ffd69a', gain: '#ffe0bc', sat: 1.22, vig: 0.34, shadowExt: 14 },
};
export const lightFor = (S) => ({ ...LIGHTS[S.light] });
const TINT = '#fff6ea', TINT_INT = '#fff0d8', TINT_GOLD = '#ffe2bc';

// ---------- camera: [start, end] per shot (positions are absolute world coordinates) ----------
const K = (pos, look, fov, roll = 0) => ({ pos, look, fov, roll });
const CAM = {
  wide: [K([0.6, 2.6, 12], [0, 1.5, -9], 58), K([0.5, 2.0, 10.2], [0, 1.6, -9], 56, 1.5)],
  crowd: [K([0.5, 0.35, 8], [0, 1.2, -2], 60, -1), K([0.2, 0.3, 6.8], [0, 1.25, -2], 60, 2)],
  side: [K([-0.9, 0.7, 6.2], [-0.7, 1.55, 0], 46, 2), K([0.8, 0.75, 5.8], [0.9, 1.6, 0], 46, -2)],
  face: [K([1.7, 2.15, 3.9], [0, 2.2, 0], 40, -2), K([1.4, 2.2, 3.2], [0, 2.2, 0], 40, 1.5)],
  dream: [K([1.9, 1.3, 5.6], [0.1, 2.0, 0], 50, 1), K([1.6, 1.4, 4.8], [0.2, 2.05, 0], 48, -1)],
  hillsA: [K([H + 3.2, 2.7, 6.8], [H + 3.6, 1.1, -8], 52, 1), K([H + 2.6, 1.9, 4.4], [H + 3.4, 1.2, -9], 50, -1.5)],
  digCU: [K([H + 3.8, 1.55, 3.4], [H + 2.2, 1.35, 0], 42, -2), K([H + 3.2, 1.5, 2.7], [H + 2.2, 1.4, 0], 42, 1)],
  pan: [K([H - 1.0, 1.1, 3.4], [H - 4.5, 1.0, 0], 44, 2), K([H - 2.0, 0.95, 2.7], [H - 4.5, 1.0, 0.1], 40, -1)],
  nugget: [K([H - 2.4, 2.0, 3.3], [H - 4.4, 2.0, 0.4], 46, -2), K([H - 2.9, 2.15, 2.6], [H - 4.4, 2.2, 0.4], 42, 2)],
  brStreet: [K([1.7, 1.45, -1.7], [-2.4, 1.7, -4.5], 48, 1), K([1.2, 1.5, -2.5], [-2.5, 1.8, -4.5], 44, -1)],
  brFace: [K([-0.4, 2.4, -1.9], [-2.6, 2.68, -4.5], 46, -2), K([-0.8, 2.45, -2.5], [-2.6, 2.74, -4.5], 42, 1.5)],
  brWatch: [K([-0.9, 0.9, -0.9], [-2.6, 1.9, -4.5], 48, 2), K([-1.5, 1.2, -2.3], [-2.6, 1.95, -4.5], 44, -2)],
  whWide: [K([W, 1.5, 5.2], [W, 1.5, -10], 54, 0), K([W, 1.65, 5.9], [W, 1.5, -10], 56, 1)],
  whDeal: [K([W - 0.2, 1.6, 4.6], [W + 0.2, 1.75, -0.5], 46, -2), K([W + 0.1, 1.55, 3.9], [W + 0.2, 1.75, -0.5], 44, 1.5)],
  whRack: [K([W - 2.0, 1.0, 4.0], [W - 5.5, 1.5, 1.0], 50, 3), K([W - 2.2, 1.2, -5.0], [W - 5.5, 1.5, -8.0], 50, -3)],
  whHero: [K([W + 0.5, 0.75, 3.2], [W, 1.8, -8], 48, -1.5), K([W + 0.2, 0.85, 2.6], [W, 1.85, -8], 46, 1)],
  shout: [K([1.4, 0.7, 2.4], [0, 2.2, -2.4], 52, -2), K([0.9, 0.85, 1.6], [0, 2.3, -2.4], 48, 2)],
  listen: [K([0, 1.8, -1.4], [0, 1.65, 6], 58, 0), K([0, 1.75, -0.7], [0, 1.65, 6], 54, -2)],
  paperCU: [K([0, 1.8, 1.9], [0, 1.8, -2.5], 38, 0), K([0, 1.85, 1.6], [0, 1.85, -2.5], 36, 0)],
  turn: [K([3.0, 1.2, 0.6], [-2.4, 1.5, -4.0], 54, 2), K([2.6, 1.3, -0.2], [-2.4, 1.55, -4.5], 50, -2)],
  crowdBig: [K([1.6, 1.5, -11], [-1.2, 1.5, 3], 56, 1), K([1.0, 1.2, -10], [-1.0, 1.5, 3], 54, -1)],
  storeDoor: [K([1.1, 1.55, 0.2], [-3.0, 1.8, -4.6], 52, -1.5), K([1.0, 1.5, 0.0], [-3.0, 1.85, -4.7], 50, 1.5)],
  shopIn: [K([S0, 1.7, 5.0], [S0, 1.5, -5], 56, 0), K([S0 + 0.5, 1.8, 4.2], [S0, 1.5, -5], 54, 1.5)],
  coinsCtr: [K([S0 + 1.8, 1.7, -0.3], [S0, 1.4, -3.4], 46, -2), K([S0 + 1.1, 1.6, -0.9], [S0 - 0.2, 1.45, -3.4], 42, 2)],
  count: [K([S0 - 0.9, 2.1, -0.8], [S0 + 0.1, 2.15, -4.3], 44, -1.5), K([S0 - 0.5, 2.1, -1.5], [S0 + 0.1, 2.15, -4.3], 40, 1)],
  overflow: [K([S0 + 0.4, 2.4, 5.6], [S0, 1.5, -3.5], 58, -1.5), K([S0 + 0.9, 2.1, 4.5], [S0, 1.6, -3.5], 54, 1.5)],
  bags: [K([S0 + 0.5, 1.75, 0.4], [S0, 1.55, -3.4], 48, -2), K([S0 + 0.2, 1.85, -0.5], [S0, 1.6, -3.4], 42, 1.5)],
  whistle: [K([S0 - 1.6, 1.7, -0.9], [S0 + 0.1, 2.2, -4.3], 48, 2), K([S0 - 1.3, 1.8, -1.6], [S0 + 0.1, 2.25, -4.3], 44, -1)],
  thousands: [K([H + 4.5, 5.6, 10.5], [H + 5, 0.6, -14], 58, 1), K([H + 3.2, 4.2, 8], [H + 5, 0.7, -14], 56, -1.5)],
  brCalm: [K([S0 + 1.0, 2.1, -0.9], [S0 - 0.1, 2.15, -4.3], 44, 1.5), K([S0 + 0.6, 2.1, -1.6], [S0 - 0.1, 2.15, -4.3], 40, -1)],
  miner: [K([H - 1.6, 1.6, 2.6], [H - 4.5, 1.65, 0], 40, -2), K([H - 2.4, 1.6, 2.0], [H - 4.5, 1.7, 0], 36, 2)],
  brSit: [K([0.3, 1.2, -1.3], [-2.6, 1.8, -4.5], 46, -2), K([0.0, 1.45, -1.7], [-2.6, 1.85, -4.5], 42, 1.5)],
  final: [K([1.0, 1.8, 0.6], [-2.1, 2.6, -4.3], 52, 1), K([2.5, 1.9, -0.5], [-2.0, 2.4, -4.5], 52, 0)],
};
export const camAt = (f) => {
  const S = shotAt(f), KK = CAM[S.id], t = smooth(S.u / Math.max(1, S.D - 1)), a = KK[0], b = KK[1];
  const c = { pos: lerp3(a.pos, b.pos, t), look: lerp3(a.look, b.look, t), fov: lerp(a.fov, b.fov, t), roll: lerp(a.roll, b.roll, t) };
  c.pos[1] += 0.03 * Math.sin(f * 0.9) * (S.id === 'crowd' ? 1 : 0.4); // handheld bob
  c.flash = S.idx > 0 && S.u < 5 ? (1 - S.u / 5) * 0.8 : 0;
  c.shadowAt = [c.look[0], 0.5, c.look[2] - 2]; return c;
};
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const DOF = { wide: [14, 6], side: [null, 10], face: [null, 10], whWide: [9, 5], whRack: [4.2, 8], whHero: [null, 6], listen: [4.5, 8], crowdBig: [12, 6], shopIn: [8, 5], overflow: [null, 6], hillsA: [14, 6], thousands: [20, 6], brStreet: [5.5, 7], brWatch: [null, 8], final: [null, 7] };
export const dofAt = (f) => { const S = shotAt(f), C = camAt(f), d = dist(C.pos, C.look), D = DOF[S.id]; return { focus: D ? (D[0] ?? d) : d, cinf: D ? D[1] : 9, near: 1 }; };
export const worldAt = (f) => ({ light: shotAt(f).light });

// ---------- helpers ----------
const FXC = { blob: false, shadow: false, order: 5 };
const FXW = (key, draw, wp, s, cy = 500, extra = {}) => ({ key, draw, x: wp[0], y: wp[1] - (0.975 - cy / 1000) * 2.25 * s, z: wp[2], s, ...FXC, ...extra });
const CAST = ['jack', 'moe', 'pete', 'sam', 'lou', 'abe', 'ned', 'ada', 'gus', 'rex'];
const CAST2 = ['jack', 'moe', 'pete', 'lou', 'abe', 'ned', 'ada', 'gus', 'rex'];
const SHIRTS = ['#b3402f', '#5f7f4a', '#e0b04a', '#d9d2c0', '#4a7aa8', '#7b5a8a', '#3f8a7a', '#e8e0d0', '#c25a2a', '#6a8a3a'];
const EXPR = ['grin', 'laugh', 'shock', 'smile', 'grin', 'whistle'];
const EX_LISTEN = ['shock', 'smile', 'shock', 'grin', 'laugh', 'shock', 'smile'];
const qd = (x) => Math.round(frac(x) * 8) / 8; // 8-step loop phase for dig cycles

export const actorsAt = (f, T) => {
  const S = shotAt(f); f = S.fa; const out = [], tint = S.light === 'int' ? TINT_INT : S.light === 'gold' ? TINT_GOLD : TINT;
  const sid = (who) => (typeof who === 'string' ? who : `${who.seed}${who.shirt}${who.tool || ''}`);
  const man = (id, who, o, pos, extra = {}) => out.push({ key: id + sid(who) + JSON.stringify(o), draw: (p) => T.goldFront(p, who, o), x: pos[0], y: pos[1], z: pos[2], tint, ...extra });
  const side = (id, who, o, pos, extra = {}) => out.push({ key: 'S' + id + sid(who) + JSON.stringify(o), draw: (p) => T.goldSide(p, who, o), x: pos[0], y: pos[1], z: pos[2], tint, ...extra });
  const spec = (i, list = CAST2) => { const nm = list[i % list.length]; return { ...T.MINERS[nm], shirt: SHIRTS[(i * 3 + 1) % SHIRTS.length] }; };
  const runner = (i, f0, v, laneBase, zBase, scale = 1) => {
    const nm = CAST[i % CAST.length], sp = { ...T.MINERS[nm], shirt: SHIRTS[(i * 3 + 1) % SHIRTS.length], build: T.MINERS[nm].build };
    const x = laneBase + 0.15 * Math.sin(f * 0.35 + i), z = zBase + v * (f - f0), st = q(((f * 0.085 + hash(i, 3)) % 1 + 1) % 1, 2);
    const arm = i % 3 === 0 ? 'cheer' : 'pump', tool = i % 2 === 0;
    man('r' + i, sp, { expr: EXPR[i % EXPR.length], step: st, run: 1, L: arm, R: i % 3 === 1 ? 'tool' : arm, toolAng: 10 + (i % 4) * 12, tool, bob: 0 }, [x, 0, z], { s: scale });
  };
  // a runner seen from the side (faces right on screen)
  const sideRun = (i, x, z, sc = 1.15, sx = 1, extra = {}) => side('sr' + i, spec(i + 2), { expr: EXPR[(i + 1) % 6], phase: q(frac(f * 0.1 + hash(i, 4)), 2), stride: 1.0, lean: 11, toolAng: 100 + (i % 3) * 8, tool: i % 2 === 0, arms: 'run' }, [x, 0, z], { s: sc, sx, ...extra });
  const wrap = (z, lo, span) => ((z - lo) % span + span) % span + lo; // loop z into [lo, lo+span)
  const BR = T.MINERS.brannan;
  const brannan = (o, pos, sc = 1.5, extra = {}) => man('BR', BR, o, pos, { s: sc, ...extra });
  const digger = (i, x, z, sc = 1.0, spd = 0.04) => {
    const sp = spec(i, CAST2), dg = qd(f * spd + hash(i, 7));
    man('dg' + i, { ...sp, tool: ['pick', 'shovel'][i % 2] }, { expr: ['smile', 'grin', 'neutral', 'smile'][i % 4], crouch: 0.55, L: 'dig', R: 'dig', dg, tool: true, bob: 0 }, [x, 0, z], { s: sc });
  };
  const pete = T.MINERS.pete;
  const porchY = 0.14;
  switch (S.id) {
    // ---- 0-6 s (approved preview) ----
    case 'wide': {
      const lanes = [-2.0, -0.9, 0.3, 1.5, 2.3, -1.5, 0.9, -0.3, 1.9, -2.3];
      for (let i = 9; i >= 0; i--) runner(i, 0, 0.23 + 0.04 * hash(i, 1), lanes[i], -5 - i * 2.1 - 2 * hash(i, 2), 1.2);
      break;
    }
    case 'crowd': {
      const lanes = [-2.3, -1.3, -0.5, 0.4, 1.3, 2.2, -1.8, -0.9, 0.1, 0.9, 1.7, -0.4, 2.0, -2.0];
      for (let i = 13; i >= 0; i--) runner(i, 36, 0.3 + 0.04 * hash(i, 1), lanes[i], -6 + 1.4 * (i % 7) - 2.5 * hash(i, 2) - (i < 7 ? 0 : 2.5), 1.15);
      break;
    }
    case 'side': {
      const t = ramp(f, 66, 101), X = lerp(-0.2, 1.4, t);
      side('s1', 'ada', { expr: 'laugh', phase: q((f * 0.1 + 0.3) % 1, 2), stride: 1.0, lean: 11, toolAng: 110, arms: 'run' }, [X - 1.1, 0, -0.9], { s: 1.2, sx: 1 });
      side('s3', 'moe', { expr: 'shock', phase: q((f * 0.1 + 0.6) % 1, 2), stride: 1.0, lean: 11, toolAng: 100, arms: 'run' }, [X + 1.0, 0, -1.4], { s: 1.2, sx: 1 });
      side('s2', 'jack', { expr: 'grin', phase: q((f * 0.1) % 1, 2), stride: 1.0, lean: 11, toolAng: 105, arms: 'run' }, [X, 0, 0], { s: 1.05, sx: 1 });
      break;
    }
    case 'face': {
      const t = ramp(f, 102, 137), bob = q(0.012 * Math.sin(f * 0.8), 3);
      man('fc', 'ned', { expr: f < 120 ? 'grin' : 'shock', step: q((f * 0.09) % 1, 2), run: 1, L: 'cheer', R: 'cheer', facing: 0, bob, tool: false }, [lerp(0.1, -0.05, t), 0, 0.3], { s: 1.5 });
      for (let i = 0; i < 4; i++) man('fb' + i, { ...T.MINERS[CAST[(i * 2 + 3) % 10]], shirt: SHIRTS[(i * 2 + 5) % 10] }, { expr: 'laugh', step: q(((f * 0.09 + i * 0.3) % 1), 2), run: 1, L: 'pump', R: 'pump' }, [-1.6 + i * 1.1, 0, -4.5 - i * 0.6], { s: 1.3 });
      break;
    }
    case 'dream': {
      const t = ramp(f, 138, 179);
      man('mo', 'moe', { expr: f < 150 ? 'smile' : 'grin', step: q((f * 0.07) % 1, 2), run: 1, L: 'hip', R: 'cheer', bob: q(0.01 * Math.sin(f * 0.7), 3) }, [lerp(-0.4, -0.3, t), 0, lerp(0.4, 0.9, t)], { s: 1.45 });
      for (let i = 0; i < 6; i++) man('db' + i, { ...T.MINERS[CAST[(i * 3 + 1) % 10]], shirt: SHIRTS[(i * 3 + 2) % 10] }, { expr: EXPR[i % 6], step: q(((f * 0.085 + i * 0.27) % 1), 2), run: 1, L: 'pump', R: i % 2 ? 'tool' : 'cheer', toolAng: 20 }, [-2.2 + i * 0.9, 0, -3.5 - (i % 3) * 1.5], { s: 1.0 });
      break;
    }
    // ---- 6-12 s: the gold fields ----
    case 'hillsA': {
      for (let i = 29; i >= 0; i--) { const x = H - 0.6 + (i % 5) * 1.9 + 0.7 * hash(i, 5), z = -1.2 - Math.floor(i / 5) * 2.6 - hash(i, 6) * 1.1; digger(i, x, z, 1.3); }
      for (let i = 0; i < 3; i++) man('pn' + i, { ...spec(i + 4), tool: 'pan' }, { expr: 'smile', crouch: 0.9, L: 'hold', R: 'hold', tool: false }, [H - 5.4 + i * 0.2, 0, -3.0 - i * 4.2], { s: 1.15 });
      break;
    }
    case 'digCU': {
      const dg = qd(f * 0.05);
      man('dig1', { ...T.MINERS.lou, tool: 'shovel' }, { expr: dg > 0.4 && dg < 0.8 ? 'grin' : 'smile', crouch: 0.5, L: 'dig', R: 'dig', dg, tool: true }, [H + 2.2, 0, 0], { s: 1.55 });
      for (let i = 0; i < 5; i++) digger(i + 3, H - 0.6 + i * 1.5, -4.2 - (i % 2) * 2.2, 1.2);
      break;
    }
    case 'pan': {
      const sw = Math.sin(f * 0.35);
      man('pn', pete, { expr: f < 285 ? 'smile' : 'nervous', crouch: 0.85, L: 'hold', R: 'hold', tool: false, headTilt: q(4 * sw, 1) }, [H - 4.4, 0, 0.4], { s: 1.5 });
      for (let i = 0; i < 3; i++) digger(i + 2, H - 0.8 + i * 1.8, -4.5 - i, 1.2);
      break;
    }
    case 'nugget': {
      const shk = f < 326;
      man('pn2', pete, { expr: shk ? 'shock' : 'laugh', crouch: shk ? 0.5 : 0, L: shk ? 'hold' : 'cheer', R: shk ? 'hold' : 'cheer', tool: false, bob: q(shk ? 0 : 0.015 * Math.sin(f * 0.9), 3) }, [H - 4.4, 0, 0.4], { s: 1.5 });
      break;
    }
    // ---- 12-18 s: Brannan watches ----
    case 'brStreet': {
      brannan({ expr: f < 392 ? 'neutral' : 'smile', L: 'cross', R: 'cross', headTilt: q(2 + 1.5 * Math.sin(f * 0.1), 1), bob: 0 }, [-2.55, porchY, -4.5], 1.5, { ground: porchY });
      for (let i = 0; i < 6; i++) sideRun(i, 0.2 + 0.35 * (i % 3), wrap(5 - i * 4.0 - 0.26 * (f - 360), -10, 24), 1.05, 1);
      break;
    }
    case 'brFace': {
      brannan({ expr: f < 450 ? 'smile' : 'grin', L: 'cross', R: 'cross', headTilt: q(3, 1), bob: q(0.006 * Math.sin(f * 0.3), 3) }, [-2.55, porchY, -4.5], 1.65, { ground: porchY });
      for (let i = 0; i < 3; i++) sideRun(i + 20, -1.0 + 0.3 * i, wrap(1 - i * 3.6 - 0.27 * (f - 420), -6, 12), 1.2, 1);
      break;
    }
    case 'brWatch': {
      brannan({ expr: f < 510 ? 'smile' : 'grin', L: 'hip', R: 'cross', headTilt: q(-2, 1) }, [-2.55, porchY, -4.5], 1.5, { ground: porchY });
      for (let i = 0; i < 4; i++) sideRun(i + 30, -0.9 + 0.5 * i, wrap(3 - i * 3.0 - 0.3 * (f - 480), -8, 12), 1.2, 1);
      break;
    }
    // ---- 18-25 s: warehouses ----
    case 'whWide': {
      const t = ramp(f, 540, 589);
      brannan({ expr: 'smile', step: q(frac(f * 0.045), 2), run: 0, L: 'hip', R: 'swing', bob: 0 }, [W - 0.3, 0, lerp(-7, -1.2, t)], 1.4);
      man('gs', T.MINERS.gus, { expr: 'laugh', step: q(frac(f * 0.045 + 0.4), 2), run: 0, L: 'point', R: 'hip' }, [W + 1.4, 0, lerp(-8.5, -2.6, t)], { s: 1.35 });
      break;
    }
    case 'whDeal': {
      brannan({ expr: 'smile', L: 'hold', R: 'hip', headTilt: q(2, 1) }, [W - 0.35, 0, -0.5], 1.5);
      man('gs', T.MINERS.gus, { expr: f < 612 ? 'neutral' : 'laugh', L: 'hold', R: 'cheer', bob: q(f > 612 ? 0.012 * Math.sin(f * 0.9) : 0, 3) }, [W + 0.8, 0, -0.3], { s: 1.45 });
      break;
    }
    case 'whRack': break;
    case 'whHero': {
      brannan({ expr: 'grin', L: 'cross', R: 'cross', headTilt: q(2, 1), bob: q(0.006 * Math.sin(f * 0.2), 3) }, [W, 0, -1.6], 1.55);
      break;
    }
    // ---- 25-32 s: shouting about gold ----
    case 'shout': {
      const m = Math.sin(f * 0.8) > 0;
      out.push(FXW('crate', (p) => T.fxCrate(p), [0, 0.41, -2.4], 1.3, 500, { order: 2 }));
      brannan({ expr: m ? 'laugh' : 'shock', L: 'mouth', R: 'mouth', headTilt: q(m ? -4 : 3, 1), bob: q(m ? 0.01 : 0, 3) }, [0, 0.76, -2.4], 1.4, { ground: 0.76, blob: false });
      for (let i = 0; i < 3; i++) man('bg' + i, spec(i + 1), { expr: 'shock', L: 'hang', R: 'hang' }, [-3 + i * 3.1, 0, -8 - i], { s: 1.1 });
      break;
    }
    case 'listen': {
      const pos = [[-0.8, 1.6, 1.0], [0.8, 2.2, 1.0], [-1.5, 3.2, 1.0], [0.2, 3.6, 1.0], [1.7, 4.0, 1.0], [-0.7, 5.0, 1.0], [1.0, 5.6, 1.0], [-2.2, 5.9, 1.0], [2.4, 6.4, 1.0]];
      for (let i = pos.length - 1; i >= 0; i--) { const [x, z, sc] = pos[i]; man('ls' + i, spec(i + 3), { expr: EX_LISTEN[i % 7], L: i % 3 === 0 ? 'point' : 'hang', R: i % 4 === 1 ? 'cheer' : 'hang', headTilt: q(3 * Math.sin(f * 0.07 + i), 1), tool: false, bob: q(0.006 * Math.sin(f * 0.1 + i), 3) }, [x, 0, z], { s: 1.15 * sc }); }
      break;
    }
    case 'paperCU': {
      brannan({ expr: 'laugh', L: 'mouth', R: 'mouth' }, [0, 0.76, -3.4], 1.4, { ground: 0.76, blob: false });
      break;
    }
    case 'turn': {
      for (let i = 0; i < 10; i++) sideRun(i + 40, -1.0 + 0.45 * (i % 4), wrap(3 - i * 2.2 - 0.28 * (f - 915), -10, 22), 1.15, 1);
      brannan({ expr: 'grin', L: 'cross', R: 'cross' }, [-2.55, porchY, -4.5], 1.5, { ground: porchY });
      break;
    }
    // ---- 32-40 s: crowd to the store ----
    case 'crowdBig': {
      for (let i = 31; i >= 0; i--) { const lane = -2.6 + (i % 7) * 0.85 + 0.25 * hash(i, 2), z0 = 1 + Math.floor(i / 7) * 3.0 + 1.2 * hash(i, 3), z = z0 - 0.3 * (f - 960); if (z > -9.5) runner(i, 960, -0.3, lane, z0, 1.1); }
      break;
    }
    case 'storeDoor': {
      const pos = [[-0.1, -2.77], [-0.9, -3.72], [-0.6, -2.74], [-1.27, -4.88], [-1.35, -2.16], [-2.19, -2.56], [-1.97, -2.03], [-2.24, -3.38], [-2.05, -5.49]];
      for (let i = pos.length - 1; i >= 0; i--) { const [x, z] = pos[i]; man('sd' + i, spec(i + 1), { expr: EXPR[i % 6], L: i % 2 ? 'cheer' : 'hang', R: i % 3 === 0 ? 'cheer' : 'hold', bob: q(0.01 * Math.sin(f * 0.7 + i), 3), tool: false }, [x, 0, z], { s: 1.2 }); }
      brannan({ expr: 'grin', L: 'hip', R: 'swing' }, [-2.55, porchY, -4.6], 1.45, { ground: porchY });
      break;
    }
    case 'shopIn': {
      brannan({ expr: 'smile', L: 'hold', R: 'count' }, [S0, 0, -4.4], 1.45);
      const sp7 = [[-1.15, -1.0], [1.15, -1.3], [-0.7, 0.6], [0.95, 0.9], [-1.6, 1.5], [1.7, 1.7], [-0.2, 2.2]]; for (let i = 0; i < 7; i++) { const x = S0 + sp7[i][0], z = sp7[i][1]; man('sc' + i, spec(i + 5), { expr: EXPR[i % 6], L: i % 2 ? 'cheer' : 'hang', R: 'hold', bob: q(0.01 * Math.sin(f * 0.7 + i), 3), tool: false }, [x, 0, z], { s: 1.2 }); }
      break;
    }
    case 'coinsCtr': {
      brannan({ expr: 'smile', L: 'count', R: 'count' }, [S0, 0, -4.3], 1.5);
      break;
    }
    // ---- 40-49 s: the money ----
    case 'count': {
      brannan({ expr: f < 1230 ? 'smile' : 'grin', L: 'count', R: 'count', headTilt: q(-2 + 2 * Math.sin(f * 0.1), 1), bob: q(0.006 * Math.sin(f * 0.6), 3) }, [S0 + 0.1, 0, -4.3], 1.6);
      break;
    }
    case 'overflow': {
      brannan({ expr: 'smile', L: 'count', R: 'cross' }, [S0, 0, -4.4], 1.45);
      for (let i = 17; i >= 0; i--) { const x = S0 - 2.5 + (i % 6) * 1.0 + 0.25 * hash(i, 1), z = -1.6 + Math.floor(i / 6) * 1.5 + 0.3 * hash(i, 2); man('ov' + i, spec(i + 1), { expr: EXPR[i % 6], L: i % 2 ? 'cheer' : 'hang', R: i % 3 ? 'hold' : 'cheer', bob: q(0.012 * Math.sin(f * 0.9 + i), 3), tool: false }, [x, 0, z], { s: 1.2 }); }
      break;
    }
    case 'bags': {
      brannan({ expr: 'grin', L: 'count', R: 'hold', headTilt: q(3, 1) }, [S0, 0, -4.3], 1.5);
      break;
    }
    case 'whistle': {
      brannan({ expr: 'whistle', L: 'hip', R: 'cross', headTilt: q(-3 + 2 * Math.sin(f * 0.2), 1), bob: q(0.006 * Math.sin(f * 0.3), 3) }, [S0, 0, -4.3], 1.5);
      break;
    }
    // ---- 49-60 s: contrast ----
    case 'thousands': {
      for (let i = 59; i >= 0; i--) { const x = H - 1.5 + (i % 9) * 1.65 + 0.8 * hash(i, 5), z = 1.8 - Math.floor(i / 9) * 2.9 - hash(i, 6) * 1.1; digger(i, x, z, 1.15, 0.045); }
      break;
    }
    case 'brCalm': {
      brannan({ expr: 'smile', L: 'count', R: 'count', headTilt: q(2 * Math.sin(f * 0.06), 1), bob: q(0.005 * Math.sin(f * 0.5), 3) }, [S0 - 0.1, 0, -4.3], 1.6);
      break;
    }
    case 'miner': {
      man('mn', { ...T.MINERS.moe, tool: 'pan' }, { expr: f < 1620 ? 'dazed' : 'pained', crouch: 0.6, L: 'hold', R: 'hold', tool: false, headTilt: q(5 * Math.sin(f * 0.12), 1), bob: q(0.01 * Math.sin(f * 0.3), 3) }, [H - 4.5, 0, 0], { s: 1.5 });
      break;
    }
    case 'brSit': {
      brannan({ expr: 'smile', L: 'hip', R: 'cross', headTilt: q(1.5, 1) }, [-2.55, porchY, -4.5], 1.5, { ground: porchY });
      break;
    }
    case 'final': {
      brannan({ expr: 'grin', L: 'hip', R: 'hip', headTilt: q(1.5, 1), bob: q(0.005 * Math.sin(f * 0.3), 3) }, [-2.55, porchY, -4.5], 1.5, { ground: porchY });
      if (f < 1745) for (let i = 0; i < 3; i++) sideRun(i + 60, -1.2 + 0.5 * i, wrap(7 - i * 8.0 - 0.2 * (f - 1710), -14, 24), 1.0, 1);
      break;
    }
  }
  return out;
};

export const fxAt = (f, T) => {
  const S = shotAt(f); f = S.fa; const out = [];
  const tt = (a, per) => q((((f - a) / per) % 1 + 1) % 1, 2);
  const star = (id, a, per, wp, s, col = '#fff3b0', r = 120, order = 9) => { const k = tt(a, per); out.push(FXW(id + k, (p) => T.fxStar4(p, k, col, r), wp, s, 500, { order })); };
  const dust = (id, a, per, wp, s = 1.5, order = 3) => { const k = tt(a, per); out.push(FXW(id + k, (p) => T.fxDustTrail(p, k), wp, s, 700, { order })); };
  switch (S.id) {
    case 'crowd': { for (let i = 0; i < 5; i++) dust('dc' + i, 36 + i * 5, 14, [-2 + i * 1.0, 0.1, 1.6 - i * 1.4]); break; }
    case 'side': { const t = ramp(f, 66, 101), X = lerp(-0.2, 1.4, t); for (let i = 0; i < 4; i++) dust('dl' + i, 66 + i * 4, 12, [X - 0.9 - i * 0.3, 0.05, 0.5 + (i % 2) * 0.3], 1.5, 6); break; }
    case 'face': { for (let i = 0; i < 3; i++) star('sp' + i, 102 + i * 6, 14, [(i === 1 ? 1.0 : (i === 0 ? -1.0 : 0.75)), 2.85 - 0.5 * (i % 2), 0.9], 0.45, '#fff3b0', 130); break; }
    case 'dream': {
      const t = q(ramp(f, 142, 160), 2); if (t > 0) out.push(FXW('cl' + t, (p) => T.fxThoughtCloud(p, t), [0.55, 3.0, 0.2], 0.95, 500, { order: 8 }));
      if (f >= 154) { const c = tt(154, 24); out.push(FXW('nug' + c, (p) => T.fxNugget(p, c), [0.5, 3.08, 0.5], 0.46, 500, { order: 9 })); out.push(FXW('coin' + c, (p) => T.fxCoin(p, c), [0.98, 2.98, 0.5], 0.28, 500, { order: 9 })); out.push(FXW('coin2' + c, (p) => T.fxCoin(p, (c + 0.5) % 1), [0.18, 3.25, 0.5], 0.26, 500, { order: 9 })); }
      for (let i = 0; i < 4; i++) star('ds' + i, 140 + i * 7, 18, [-1.3 + i * 0.9, 2.3 + 0.6 * (i % 2), 0.8], 0.5, '#fff3b0', 120);
      break;
    }
    // ---- gold fields ----
    case 'hillsA': {
      for (let i = 0; i < 6; i++) dust('hd' + i, 180 + i * 6, 20, [H + 2 + i * 1.9, 0.1, -3.5 - (i % 3) * 5], 1.3, 3);
      for (let i = 0; i < 5; i++) star('hs' + i, 182 + i * 7, 22, [H - 5.5 + 0.4 * i, 1.4, -3 - i * 3.5], 0.5, '#ffffff', 110);
      break;
    }
    case 'digCU': {
      const dg = frac(f * 0.05), k = q(clamp((dg - 0.45) / 0.5), 1);
      out.push(FXW('dirt' + k, (p) => T.fxDirt(p, k), [H + 2.0, 0.05, 0.9], 1.35, 700, { order: 6 }));
      star('dc1', 218, 16, [H + 1.0, 1.9, 0.6], 0.45); star('dc2', 226, 16, [H + 3.0, 1.6, 0.5], 0.4);
      break;
    }
    case 'pan': {
      const sw = q(f * 0.04, 2);
      out.push(FXW('pan' + sw, (p) => T.fxPan(p, sw), [H - 4.55 + 0.03 * Math.sin(f * 0.35), 0.78, 0.95], 0.62, 500, { order: 7 }));
      star('ps1', 260, 18, [H - 4.0, 1.35, 1.0], 0.38); star('ps2', 270, 16, [H - 5.2, 1.7, 0.9], 0.36);
      break;
    }
    case 'nugget': {
      const t = q(ramp(f, 306, 326), 2);
      if (f < 326) { out.push(FXW('pan2' + t, (p) => T.fxPan(p, 0), [H - 4.5, 1.05, 0.95], 0.7 + 0.5 * t, 500, { order: 7 })); }
      else { const c = tt(326, 24), pop = q(clamp((f - 326) / 8), 2); out.push(FXW('nug2' + c + pop, (p) => T.fxNugget(p, c), [H - 4.3, 3.15, 0.5], 0.42 * (0.4 + 0.6 * pop), 500, { order: 9 })); }
      for (let i = 0; i < 5; i++) star('ns' + i, 308 + i * 6, 14, [H - 5.4 + i * 0.5, 2.6 + 0.7 * (i % 2), 0.8], 0.5, '#fff3b0', 130);
      if (f >= 330) { const b = q(clamp((f - 330) / 10), 2); out.push(FXW('bn' + b, (p) => T.fxBangText(p, 'GOLD!', b), [H - 5.5, 3.3, 0.3], 0.3, 500, { order: 10 })); }
      break;
    }
    // ---- Brannan watches ----
    case 'brStreet': { for (let i = 0; i < 4; i++) dust('bd' + i, 360 + i * 5, 14, [0.4 + 0.3 * i, 0.1, 1.5 - i * 2.0], 1.5, 3); break; }
    case 'brFace': {
      const t = q(ramp(f, 436, 456), 2);
      if (t > 0) { out.push(FXW('bc' + t, (p) => T.fxThoughtCloud(p, t), [-1.5, 3.55, -4.2], 0.85, 500, { order: 8 })); }
      if (f >= 456) { const c = tt(456, 24); if (f < 468) out.push(FXW('bsh' + c, (p) => T.fxShovelIcon(p, c), [-1.5, 3.62, -4.1], 0.2, 500, { order: 9 })); else out.push(FXW('bco' + c, (p) => T.fxCoin(p, c), [-1.5, 3.62, -4.1], 0.2, 500, { order: 9 })); }
      for (let i = 0; i < 3; i++) dust('bfd' + i, 420 + i * 6, 16, [-0.8 + 0.3 * i, 0.1, -1.3 - 2 * i], 1.3, 3);
      break;
    }
    case 'brWatch': {
      const k = tt(480, 20); out.push(FXW('wsp' + k, (p) => T.fxSpeed(p, k, 1), [-1.2, 1.5, -2.0], 1.6, 500, { order: 6 }));
      star('bw1', 484, 18, [-2.1, 2.7, -4.0], 0.35); star('bw2', 492, 18, [-3.2, 2.9, -4.0], 0.3);
      if (f >= 497) { const pt = q(clamp((f - 497) / 14), 2); out.push(FXW('bnm' + pt, (p) => T.fxPlate(p, 'SAMUEL BRANNAN', '', pt), [-1.6, 3.55, -3.4], 0.78, 500, { order: 10 })); }
      break;
    }
    // ---- warehouse ----
    case 'whWide': {
      for (let i = 0; i < 6; i++) star('wd' + i, 542 + i * 8, 40, [W - 4.8 + (i % 2) * 9.6, 0.9 + (i % 3) * 0.2, 2.0 - i * 3.6], 0.35, '#ffffff', 90);
      for (let i = 0; i < 3; i++) dust('wdu' + i, 542 + i * 10, 40, [W - 2 + i * 2, 0.1, -3 - i * 2], 0.9, 3);
      break;
    }
    case 'whDeal': {
      const stp = q(clamp((f - 612) / 10), 2);
      out.push(FXW('bag', (p) => T.fxBag(p), [W - 0.15, 1.3, 0.15], 0.34, 500, { order: 7 }));
      if (f >= 612) out.push(FXW('stp' + stp, (p) => T.fxStamp(p, 'SOLD!', stp), [W + 0.15, 3.5, 0.3], 0.62, 500, { order: 10 }));
      for (let i = 0; i < 4; i++) star('dls' + i, 596 + i * 8, 14, [W - 1.4 + i * 0.9, 2.9 + 0.4 * (i % 2), 0.4], 0.4);
      break;
    }
    case 'whRack': {
      for (let i = 0; i < 8; i++) star('wrs' + i, 642 + i * 6, 14, [W - 5.0 - 0.2 * (i % 2), 1.4 + 0.2 * (i % 3), 3.2 - i * 1.6], 0.35, '#ffffff', 110);
      break;
    }
    case 'whHero': {
      if (f >= 712) { const pt = q(clamp((f - 712) / 14), 2); out.push(FXW('pl' + pt, (p) => T.fxPlate(p, 'ALL THE SHOVELS', 'BOUGHT!', pt), [W + 0.05, 3.45, -1.2], 0.7, 500, { order: 10 })); }
      for (let i = 0; i < 5; i++) star('hs' + i, 692 + i * 9, 16, [W - 1.6 + i * 0.8, 3.2 + 0.4 * (i % 2), -1.2], 0.38);
      break;
    }
    // ---- shouting ----
    case 'shout': {
      const m = Math.floor((f - 750) / 20) % 3, bt = q(clamp((f - 750 - Math.floor((f - 750) / 20) * 20) / 6), 2), pos = [[-1.9, 3.5, -1.6], [1.6, 3.9, -1.6], [0.1, 4.55, -1.8]][m];
      out.push(FXW('bg' + m + bt, (p) => T.fxBangText(p, 'GOLD!', bt), pos, 0.42, 500, { order: 10 }));
      out.push(FXW('pap', (p) => T.fxPaper(p, 0.5, 'GOLD!', 'FOUND'), [-0.85, 1.3, -2.2], 0.4, 500, { order: 6 }));
      break;
    }
    case 'listen': {
      for (let i = 0; i < 4; i++) { const pt = q(clamp((f - 818 - i * 9) / 8), 2); if (pt > 0) out.push(FXW('bx' + i + pt, (p) => T.fxBangText(p, '!', pt), [-1.0 + i * 0.7, 3.5 - 0.3 * (i % 2), 2.6 + i * 0.5], 0.34, 500, { order: 10 })); }
      break;
    }
    case 'paperCU': {
      const t = clamp((f - 870) / 14), sc = 0.1 + 0.52 * smooth(t), roll = lerp(1.6, -0.04, smooth(t)), qs = q(sc, 2), qr = q(roll, 2);
      out.push(FXW('pc' + qs + qr, (p) => T.fxPaper(p, 0.7, 'GOLD!', 'FOUND IN CALIFORNIA'), [0, 1.75, -0.6], qs, 500, { order: 8, roll: qr }));
      if (f >= 884) { const b = q(clamp((f - 884) / 10), 2); out.push(FXW('pb' + b, (p) => T.fxBangText(p, 'GOLD!', b), [0.35, 3.0, -0.3], 0.34, 500, { order: 10 })); }
      break;
    }
    case 'turn': { for (let i = 0; i < 5; i++) dust('td' + i, 915 + i * 4, 14, [-0.4 + 0.2 * i, 0.1, -0.5 - i * 1.2], 1.6, 3); const k = tt(915, 18); out.push(FXW('tsp' + k, (p) => T.fxSpeed(p, k, 1), [0.5, 1.5, -1.5], 2.0, 500, { order: 6 })); break; }
    case 'crowdBig': { for (let i = 0; i < 6; i++) dust('cb' + i, 960 + i * 5, 14, [-2 + i * 0.85, 0.1, -3 + 2.5 * ((i % 3) - 1)], 1.5, 3); break; }
    case 'storeDoor': {
      const pos0 = [[0.29, -2.87], [-0.01, -4.15], [-0.62, -2.7], [0.1, -5.0], [-1.7, -2.4], [-2.0, -3.4]];
      const cp = pos0.map((p, i) => [p[0], 3.0 + 0.3 * (i % 2), p[1]]).slice(0, 6);
      for (let i = 0; i < 6; i++) { const k = tt(1020 + i * 6, 20); out.push(FXW('sc' + i + k, (p) => T.fxCoin(p, k), cp[i], 0.2, 500, { order: 9 })); }
      for (let i = 0; i < 3; i++) dust('sdd' + i, 1022 + i * 6, 18, [-0.5 + i * 0.4, 0.1, -1.4 - i], 1.2, 3);
      break;
    }
    case 'shopIn': {
      const cp = [[S0 - 1.2, 3.1, -1.0], [S0 + 0.3, 3.3, -1.5], [S0 + 1.3, 3.1, -0.7], [S0 - 0.5, 3.2, 0.3], [S0 + 0.9, 3.4, 0.7], [S0 - 1.6, 3.4, 1.0]];
      for (let i = 0; i < 6; i++) { const k = tt(1080 + i * 6, 22); out.push(FXW('si' + i + k, (p) => T.fxCoin(p, k), cp[i], 0.18, 500, { order: 9 })); }
      break;
    }
    case 'coinsCtr': {
      for (let i = 0; i < 7; i++) { const k = tt(1140 + i * 5, 24), pos = [S0 - 2.6 + i * 0.85, 1.35 + 0.9 * Math.sin(k * Math.PI), -1.3 - k * 1.8]; out.push(FXW('cf' + i + k, (p) => T.fxCoin(p, k * 2), pos, 0.17, 500, { order: 9 })); }
      star('cs1', 1146, 14, [S0 - 0.4, 1.6, -3.0], 0.4); star('cs2', 1154, 14, [S0 + 1.2, 1.6, -3.0], 0.36);
      break;
    }
    case 'count': {
      for (let i = 0; i < 8; i++) { const k = tt(1200 + i * 7, 26), pos = [S0 - 0.6 + 0.17 * i, 1.55 + 0.45 * Math.sin(k * Math.PI), -3.4]; out.push(FXW('ct' + i + k, (p) => T.fxCoin(p, k * 2), pos, 0.17, 500, { order: 9 })); }
      for (let i = 0; i < 4; i++) star('cts' + i, 1204 + i * 9, 16, [S0 - 0.8 + i * 0.5, 2.5 + 0.4 * (i % 2), -3.4], 0.34);
      break;
    }
    case 'overflow': {
      for (let i = 0; i < 5; i++) { const k = tt(1260 + i * 6, 22); out.push(FXW('oc' + i + k, (p) => T.fxCoin(p, k), [S0 - 2.0 + i * 1.0, 3.3 + 0.3 * (i % 2), 0.3 - (i % 3) * 0.6], 0.2, 500, { order: 9 })); }
      for (let i = 0; i < 4; i++) { const pt = q(clamp((f - 1270 - i * 10) / 8), 2); if (pt > 0) out.push(FXW('ob' + i + pt, (p) => T.fxBangText(p, '$', pt), [S0 - 1.8 + i * 1.2, 4.7, 0.2], 0.32, 500, { order: 10 })); }
      break;
    }
    case 'bags': {
      const n = Math.min(3, 1 + Math.floor((f - 1330) / 18));
      out.push(FXW('bgA' + n, (p) => T.fxCoinStack(p, n), [S0 - 0.55, 1.4, -3.0], 0.42, 500, { order: 7 }));
      for (let i = 0; i < 3; i++) { if (f > 1334 + i * 14) { const bp = q(clamp((f - 1334 - i * 14) / 8), 2); out.push(FXW('bgb' + i + bp, (p) => T.fxBag(p), [S0 + 0.05 + i * 0.4, 1.5, -3.0 - 0.1 * i], 0.34 * (0.5 + 0.5 * bp), 500, { order: 7 })); } }
      if (f >= 1352) { const pt = q(clamp((f - 1352) / 14), 2); out.push(FXW('bpl' + pt, (p) => T.fxPlate(p, '$150,000', 'A MONTH', pt), [S0 + 0.05, 3.5, -3.6], 0.8, 500, { order: 10 })); }
      for (let i = 0; i < 5; i++) star('bgs' + i, 1334 + i * 8, 15, [S0 - 0.7 + i * 0.35, 2.0 + 0.5 * (i % 2), -3.0], 0.3);
      break;
    }
    case 'whistle': {
      const k = tt(1400, 30), y = 1.7 + 1.2 * Math.sin(k * Math.PI);
      out.push(FXW('wc' + k, (p) => T.fxCoin(p, k * 3), [S0 + 0.62, y, -3.7], 0.22, 500, { order: 9 }));
      for (let i = 0; i < 5; i++) star('wst' + i, 1402 + i * 9, 16, [S0 - 1.4 + i * 0.8, 2.4 + 0.7 * (i % 2), -4.0], 0.36);
      break;
    }
    case 'thousands': {
      for (let i = 0; i < 9; i++) dust('thd' + i, 1470 + i * 5, 22, [H + 1 + i * 1.6, 0.1, -3 - (i % 4) * 4.5], 1.2, 3);
      break;
    }
    case 'brCalm': {
      for (let i = 0; i < 5; i++) { const k = tt(1530 + i * 9, 30); out.push(FXW('bcc' + i + k, (p) => T.fxCoin(p, k * 2), [S0 - 1.0 + i * 0.5, 1.7 + 0.35 * Math.sin(k * Math.PI), -3.2], 0.15, 500, { order: 9 })); }
      for (let i = 0; i < 4; i++) star('bcs' + i, 1534 + i * 11, 18, [S0 - 1.2 + i * 0.9, 2.6 + 0.4 * (i % 2), -3.4], 0.34);
      break;
    }
    case 'miner': {
      out.push(FXW('mpn', (p) => T.fxPan(p, 5), [H - 4.5, 0.78, 0.75], 0.62, 500, { order: 7 }));
      for (let i = 0; i < 3; i++) { const k = tt(1592 + i * 8, 26); out.push(FXW('sw' + i + k, (p) => T.fxStar4(p, k, '#9bd0ff', 70), [H - 4.9 + i * 0.5, 3.15 - 0.5 * k, 0.9], 0.28, 500, { order: 9 })); }
      for (let i = 0; i < 3; i++) dust('md' + i, 1592 + i * 8, 24, [H - 5 + i * 0.7, 0.1, 0.6 - i], 1.1, 3);
      break;
    }
    case 'brSit': {
      for (let i = 0; i < 3; i++) out.push(FXW('bsb' + i, (p) => T.fxBag(p), [-1.9 + 0.7 * i, 0.48, -3.6 + 0.3 * i], 0.24, 500, { order: 7 }));
      star('bsa', 1652, 18, [-2.0, 3.0, -4.0], 0.4); star('bsb', 1662, 18, [-1.0, 2.7, -4.0], 0.34);
      break;
    }
    case 'final': {
      for (let i = 0; i < 3; i++) out.push(FXW('fb' + i, (p) => T.fxBag(p), [-1.9 + 0.7 * i, 0.48, -3.6 + 0.3 * i], 0.24, 500, { order: 7 }));
      if (f >= 1730) { const pt = q(clamp((f - 1730) / 16), 2); out.push(FXW('fpl' + pt, (p) => T.fxPlate(p, 'SELL SHOVELS', 'NOT DREAMS', pt), [-1.9, 3.03, -3.8], 1.5, 500, { order: 12 })); }
      for (let i = 0; i < 6; i++) star('fs' + i, 1712 + i * 9, 18, [-2.4 + i * 0.7, 3.4 + 0.5 * (i % 2), -4.2], 0.34);
      break;
    }
  }
  return out;
};
