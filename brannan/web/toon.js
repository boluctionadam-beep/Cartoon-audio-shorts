export const INK = "#241726";
export const SKIN = "#ffe2c2";
const WHITE = "#ffffff";
const MOUTH = "#5a1e28";
const TONGUE = "#e86e78";
const SH_SKIN = [
    0.96,
    0.86,
    0.84
];
const SH_CLOTH = [
    0.64,
    0.66,
    0.74
];
const SH_FELT = [
    0.62,
    0.62,
    0.7
];
const rad = (d)=>d * Math.PI / 180;
const clamp = (x, a, b)=>Math.max(a, Math.min(b, x));
export const mul = (c, m)=>{
    const n = parseInt(c.slice(1), 16);
    const ch = (v, k)=>Math.min(255, Math.round(v * k)).toString(16).padStart(2, "0");
    return `#${ch(n >> 16 & 255, m[0])}${ch(n >> 8 & 255, m[1])}${ch(n & 255, m[2])}`;
};
export const shade = (c, k)=>mul(c, [
        k,
        k,
        k
    ]);
export const mix = (a, b, t)=>{
    const A = parseInt(a.slice(1), 16), B = parseInt(b.slice(1), 16);
    const ch = (s)=>Math.round((A >> s & 255) * (1 - t) + (B >> s & 255) * t).toString(16).padStart(2, "0");
    return `#${ch(16)}${ch(8)}${ch(0)}`;
};
const rnd = (seed, k)=>{
    const x = Math.sin(seed * 127.1 + k * 311.7) * 43758.5453;
    return x - Math.floor(x);
};
const rotPts = (pts, a, cx, cy)=>pts.map(([x, y])=>[
            cx + (x - cx) * Math.cos(a) - (y - cy) * Math.sin(a),
            cy + (x - cx) * Math.sin(a) + (y - cy) * Math.cos(a)
        ]);
const rotAbout = (q, a, c)=>rotPts([
        q
    ], a, c[0], c[1])[0];
const lerp2 = (a, b, t)=>[
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t
    ];
const curve = (a, k, b, n = 10)=>{
    const c = [
        2 * k[0] - (a[0] + b[0]) / 2,
        2 * k[1] - (a[1] + b[1]) / 2
    ], out = [];
    for(let i = 0; i <= n; i++){
        const t = i / n, s = 1 - t;
        out.push([
            s * s * a[0] + 2 * s * t * c[0] + t * t * b[0],
            s * s * a[1] + 2 * s * t * c[1] + t * t * b[1]
        ]);
    }
    return out;
};
export const RIFLEMAN = {
    jacket: "#357650",
    pants: "#3d4440",
    boots: INK,
    hat: "shako",
    belt: "#f1efe6",
    buttons: "#d9dde0",
    rifle: true
};
export const OFFICER = {
    ...RIFLEMAN,
    hat: "shako_tall",
    buttons: "#e8c45a",
    sash: "#c0353a",
    sword: true,
    moustache: "#4a3020",
    rifle: false,
    belt: null,
    build: "stout"
};
export const KID = {
    jacket: "#f08a2c",
    pants: "#3b5b9a",
    boots: "#f4f1ea",
    hat: "cap",
    cap: "#e2453c",
    build: "kid"
};
export const PARENT = {
    jacket: "#7b5ac9",
    pants: "#3b3f52",
    boots: "#5a3b2a",
    hat: "hair",
    hair: "#5a3b2a"
};
export const SKINS = [
    SKIN,
    "#f5c9a0",
    "#ecd0b6",
    "#c99067"
];
export const soldier = (v = 0, extra = {})=>{
    const o = {
        ...RIFLEMAN,
        skin: SKINS[v % 4]
    };
    if (v % 4 === 1) o.moustache = "#4a3426";
    if (v % 4 === 3) o.moustache = "#2a201a";
    return {
        ...o,
        ...extra
    };
};
export const townsfolk = (v = 0)=>{
    const coats = [
        "#3f6fb5",
        "#8c3b4a",
        "#5d7a3a",
        "#b5653f",
        "#2f5f6a",
        "#7b5ac9"
    ];
    const o = {
        jacket: coats[v % 6],
        pants: "#3b3f52",
        boots: "#4a3426",
        skin: SKINS[v % 4]
    };
    return v % 2 ? {
        ...o,
        hat: "bonnet",
        dress: [
            "#d9a441",
            "#c25a7a",
            "#5a8fc2"
        ][v % 3]
    } : {
        ...o,
        hat: "tophat"
    };
};
export class Pen {
    g;
    ol = 12;
    rot = null;
    constructor(g){
        this.g = g;
    }
    P(x, y) {
        if (!this.rot) return [
            x,
            y
        ];
        const r = this.rot, a = r[0], cx = r[1], cy = r[2], dx = r.length > 3 ? r[3] : 0, dy = r.length > 4 ? r[4] : 0, c = Math.cos(a), s = Math.sin(a);
        return [
            cx + (x - cx) * c - (y - cy) * s + dx,
            cy + (x - cx) * s + (y - cy) * c + dy
        ];
    }
    path(pts, close) {
        const g = this.g;
        g.beginPath();
        pts.forEach((p, i)=>{
            const [x, y] = this.P(p[0], p[1]);
            if (i) g.lineTo(x, y);
            else g.moveTo(x, y);
        });
        if (close) g.closePath();
    }
    poly(pts, fill, ol) {
        const g = this.g, w = ol ?? this.ol;
        this.path(pts, true);
        if (fill) {
            g.fillStyle = fill;
            g.fill();
        }
        if (w) {
            g.lineWidth = w;
            g.strokeStyle = INK;
            g.lineJoin = "round";
            g.stroke();
        }
    }
    ell(cx, cy, rx, ry, fill, ol, a0 = 0, a1 = 360, rot = 0) {
        this.poly(ellPts(cx, cy, rx, ry, a0, a1, rot), fill, ol);
    }
    line(pts, fill, w, ink = true) {
        const g = this.g;
        g.lineCap = "round";
        g.lineJoin = "round";
        if (ink) {
            this.path(pts, false);
            g.strokeStyle = INK;
            g.lineWidth = w + 2 * this.ol * 0.9;
            g.stroke();
        }
        this.path(pts, false);
        g.strokeStyle = fill;
        g.lineWidth = w;
        g.stroke();
    }
    stroke(pts, w, fill = INK) {
        const g = this.g;
        g.lineCap = "round";
        g.lineJoin = "round";
        this.path(pts, false);
        g.strokeStyle = fill;
        g.lineWidth = w;
        g.stroke();
    }
    arc(cx, cy, rx, ry, a0, a1, w, fill = INK) {
        const pts = [];
        for(let i = 0; i <= 24; i++)pts.push([
            cx + rx * Math.cos(rad(a0 + (a1 - a0) * i / 24)),
            cy + ry * Math.sin(rad(a0 + (a1 - a0) * i / 24))
        ]);
        this.stroke(pts, w, fill);
    }
    dot(cx, cy, r, fill = INK) {
        const [x, y] = this.P(cx, cy);
        this.g.beginPath();
        this.g.arc(x, y, r, 0, Math.PI * 2);
        this.g.fillStyle = fill;
        this.g.fill();
    }
    clip(pts, fn) {
        const g = this.g;
        g.save();
        this.path(pts, true);
        g.clip();
        fn();
        g.restore();
    }
    shadedFill(pts, base, shadow, light, R, shift = 0.45, r0 = 1.05, r1 = 1.25) {
        const g = this.g, n = pts.length;
        let cx = 0, cy = 0;
        for (const [x, y] of pts){
            cx += x / n;
            cy += y / n;
        }
        const [gx, gy] = this.P(cx + Math.cos(light) * shift * R, cy + Math.sin(light) * shift * R);
        const gr = g.createRadialGradient(gx, gy, 0, gx, gy, r1 * R);
        gr.addColorStop(0, base);
        gr.addColorStop(r0 / r1, base);
        gr.addColorStop(1, shadow);
        this.path(pts, true);
        g.fillStyle = gr;
        g.fill();
    }
    gradFill(pts, base, shadow, light, flat = 0.22) {
        const g = this.g, dx = Math.cos(light), dy = Math.sin(light), n = pts.length;
        let cx = 0, cy = 0, lo = Infinity, hi = -Infinity;
        for (const [x, y] of pts){
            cx += x / n;
            cy += y / n;
            const d = x * dx + y * dy;
            lo = Math.min(lo, d);
            hi = Math.max(hi, d);
        }
        const dc = cx * dx + cy * dy;
        const [ax, ay] = this.P(cx + dx * (hi - dc), cy + dy * (hi - dc)), [bx, by] = this.P(cx + dx * (lo - dc), cy + dy * (lo - dc));
        const gr = g.createLinearGradient(ax, ay, bx, by);
        gr.addColorStop(0, base);
        gr.addColorStop(flat, base);
        gr.addColorStop(1, shadow);
        this.path(pts, true);
        g.fillStyle = gr;
        g.fill();
    }
    inkRing(pts, w0, thick, k = 0.45, col = INK) {
        const n = pts.length;
        let cx = 0, cy = 0;
        for (const [x, y] of pts){
            cx += x / n;
            cy += y / n;
        }
        const out = [], inn = [];
        pts.forEach((q, i)=>{
            const a = pts[(i + n - 1) % n], b = pts[(i + 1) % n];
            let nx = b[1] - a[1], ny = a[0] - b[0];
            const l = Math.hypot(nx, ny) || 1;
            nx /= l;
            ny /= l;
            const h = 0.5 * w0 * (1 + k * Math.cos(Math.atan2(q[1] - cy, q[0] - cx) - thick));
            out.push([
                q[0] + nx * h,
                q[1] + ny * h
            ]);
            inn.push([
                q[0] - nx * h,
                q[1] - ny * h
            ]);
        });
        const g = this.g;
        const trace = (r)=>{
            r.forEach(([x0, y0], i)=>{
                const [x, y] = this.P(x0, y0);
                if (i) g.lineTo(x, y);
                else g.moveTo(x, y);
            });
            g.closePath();
        };
        g.beginPath();
        trace(out);
        trace(inn.reverse());
        g.fillStyle = col;
        g.fill("evenodd");
    }
    band(pts, fill, w, rim, cap = "butt") {
        const g = this.g;
        g.lineCap = cap;
        g.lineJoin = "round";
        this.path(pts, false);
        g.strokeStyle = INK;
        g.lineWidth = w + 2 * rim;
        g.stroke();
        this.path(pts, false);
        g.strokeStyle = fill;
        g.lineWidth = w;
        g.stroke();
        g.lineCap = "round";
    }
}
const ellPts = (cx, cy, rx, ry, a0 = 0, a1 = 360, rot = 0, n = 48)=>{
    const r = rad(rot), pts = [];
    for(let i = 0; i <= n; i++){
        const a = rad(a0 + (a1 - a0) * i / n), x = rx * Math.cos(a), y = ry * Math.sin(a);
        pts.push([
            cx + x * Math.cos(r) - y * Math.sin(r),
            cy + x * Math.sin(r) + y * Math.cos(r)
        ]);
    }
    return pts;
};
const rrect = (x0, y0, x1, y1, r, n = 8)=>{
    const pts = [];
    for (const [cx, cy, a] of [
        [
            x1 - r,
            y0 + r,
            -90
        ],
        [
            x1 - r,
            y1 - r,
            0
        ],
        [
            x0 + r,
            y1 - r,
            90
        ],
        [
            x0 + r,
            y0 + r,
            180
        ]
    ])for(let i = 0; i <= n; i++)pts.push([
        cx + r * Math.cos(rad(a + 90 * i / n)),
        cy + r * Math.sin(rad(a + 90 * i / n))
    ]);
    return pts;
};
const taper = (p, a, b, wa, wb, col = INK)=>{
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = -dy / l, ny = dx / l;
    p.poly([
        [
            a[0] + nx * wa / 2,
            a[1] + ny * wa / 2
        ],
        [
            b[0] + nx * wb / 2,
            b[1] + ny * wb / 2
        ],
        [
            b[0] - nx * wb / 2,
            b[1] - ny * wb / 2
        ],
        [
            a[0] - nx * wa / 2,
            a[1] - ny * wa / 2
        ]
    ], col, 0);
    p.dot(a[0], a[1], wa / 2, col);
    p.dot(b[0], b[1], wb / 2, col);
};
export const blobPts = (cx, cy, B, n = 72)=>{
    const ph = [
        rnd(B.seed, 11),
        rnd(B.seed, 12),
        rnd(B.seed, 13)
    ].map((v)=>v * Math.PI * 2);
    const pts = [];
    for(let i = 0; i < n; i++){
        const t = i / n * Math.PI * 2, c = Math.cos(t), s = Math.sin(t), e = 2 / (s < 0 ? B.nTop : B.nBot);
        let X = Math.sign(c) * Math.abs(c) ** e;
        const Y = Math.sign(s) * Math.abs(s) ** e;
        X *= (1 + B.egg * Y) * (1 + B.asym * Math.sign(X));
        const r = 1 + B.noise * (Math.cos(2 * t + ph[0]) + 0.7 * Math.cos(3 * t + ph[1]) + 0.5 * Math.cos(4 * t + ph[2]));
        const x = B.a * X * r, y = B.b * Y * r;
        pts.push([
            cx + x * Math.cos(B.rot) - y * Math.sin(B.rot),
            cy + x * Math.sin(B.rot) + y * Math.cos(B.rot)
        ]);
    }
    return pts;
};
export const headBlob = (seed, a = 118, facing = 0)=>({
        a,
        b: a * (0.94 + 0.08 * (rnd(seed, 1) - 0.5)),
        nTop: 1.75 + 0.3 * (rnd(seed, 2) - 0.5),
        nBot: 2.3 + 0.3 * (rnd(seed, 3) - 0.5),
        egg: -0.12 + 0.06 * (rnd(seed, 4) - 0.5),
        asym: (0.06 + 0.04 * rnd(seed, 5)) * (facing || (rnd(seed, 6) < 0.5 ? -1 : 1)),
        rot: rad(8 * (rnd(seed, 7) - 0.5)),
        noise: 0.008,
        seed
    });
export const thickAngle = (light)=>Math.atan2(-Math.sin(light) + 0.8, -Math.cos(light));
const DEF_LIGHT = rad(-120);
const FACE = {
    neutral: {
        eye: [
            "lid",
            "lid"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "dash"
    },
    stern: {
        eye: [
            "lid",
            "lid"
        ],
        brow: [
            3,
            -2
        ],
        mouth: "frown"
    },
    grin: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            -3,
            -3
        ],
        mouth: "grin"
    },
    laugh: {
        eye: [
            "squeeze",
            "squeeze"
        ],
        brow: [
            -4,
            -4
        ],
        mouth: "laugh"
    },
    whistle: {
        eye: [
            "dash",
            "dash"
        ],
        brow: [
            -2,
            -4
        ],
        mouth: "o"
    },
    nervous: {
        eye: [
            "small",
            "small"
        ],
        brow: [
            -3,
            2
        ],
        mouth: "wave"
    },
    shock: {
        eye: [
            "shock",
            "shock"
        ],
        brow: [
            -7,
            -6
        ],
        mouth: "O"
    },
    relief: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            -2,
            1
        ],
        mouth: "smileWide"
    },
    relief_open: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            -2,
            1
        ],
        mouth: "grin"
    },
    dazed: {
        eye: [
            "spiral",
            "spiral"
        ],
        brow: [
            -3,
            2
        ],
        mouth: "wave"
    },
    pained: {
        eye: [
            "squeeze",
            "lid"
        ],
        brow: [
            -3,
            2
        ],
        mouth: "teeth"
    },
    smile: {
        eye: [
            "dot",
            "dot"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "smirk"
    },
    smile_closed: {
        eye: [
            "happy",
            "happy"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "smile"
    },
    lick: {
        eye: [
            "dot",
            "dot"
        ],
        brow: [
            0,
            -1
        ],
        mouth: "lick"
    }
};
const halfLid = (k)=>k === "dot" || k === "small" ? "lid" : k === "lid" ? "slit" : k === "shock" ? "shockHalf" : k;
const eyeKind = (k, lid)=>lid >= 1 && k !== "happy" && k !== "squeeze" && k !== "spiral" ? "dash" : lid > 0 ? halfLid(k) : k;
const lidOf = (b)=>b === true ? 1 : Number(b) || 0;
const eye = (p, kind, x, ey, u, side, look, skin)=>{
    const lx = x + look * 3 * u, lw = 3.8 * u;
    switch(kind){
        case "dot":
            p.ell(lx, ey, 3.8 * u, 5.5 * u, INK, 0);
            break;
        case "small":
            p.ell(lx, ey, 3 * u, 4.4 * u, INK, 0);
            break;
        case "lid":
            p.ell(lx, ey - u, 7 * u, 6 * u, INK, 0, 0, 180);
            p.stroke([
                [
                    x - 9 * u,
                    ey - u
                ],
                [
                    x + 9 * u,
                    ey - u
                ]
            ], lw);
            break;
        case "slit":
            p.ell(lx, ey, 7 * u, 2.6 * u, INK, 0, 0, 180);
            p.stroke([
                [
                    x - 9 * u,
                    ey
                ],
                [
                    x + 9 * u,
                    ey
                ]
            ], lw);
            break;
        case "happy":
            p.arc(x, ey + 3 * u, 8 * u, 6 * u, 200, 340, lw);
            break;
        case "dash":
            p.stroke([
                [
                    x - 8.5 * u,
                    ey
                ],
                [
                    x + 8.5 * u,
                    ey
                ]
            ], lw);
            break;
        case "squeeze":
            p.stroke([
                [
                    x + 6 * u * side,
                    ey - 5 * u
                ],
                [
                    x - 6 * u * side,
                    ey
                ],
                [
                    x + 6 * u * side,
                    ey + 5 * u
                ]
            ], lw);
            break;
        case "shock":
        case "shockHalf":
            p.ell(x, ey, 11 * u, 11 * u, WHITE, 2.6 * u);
            p.dot(lx - side * 1.5 * u, ey + 1.5 * u, 3 * u);
            if (kind === "shockHalf") {
                p.ell(x, ey, 11 * u, 11 * u, skin, 0, 180, 360);
                p.stroke([
                    [
                        x - 11 * u,
                        ey
                    ],
                    [
                        x + 11 * u,
                        ey
                    ]
                ], 2.6 * u);
            }
            break;
        default:
            {
                const s = [];
                for(let t = 1; t < 15; t++)s.push([
                    x + Math.cos(t * 0.9) * t * 0.55 * u,
                    ey + Math.sin(t * 0.9) * t * 0.55 * u
                ]);
                p.stroke(s, 2.4 * u);
            }
    }
};
const dmouth = (p, mx, y, rx, ry, u, tongue = false)=>{
    p.ell(mx, y, rx, ry, MOUTH, 0, 0, 180);
    p.clip([
        [
            mx - rx,
            y
        ],
        [
            mx + rx,
            y
        ],
        [
            mx + rx,
            y + 3 * u
        ],
        [
            mx - rx,
            y + 3 * u
        ]
    ], ()=>p.ell(mx, y, rx, ry, WHITE, 0, 0, 180));
    if (tongue) p.ell(mx + 2 * u, y + 0.62 * ry, 0.4 * rx, 0.28 * ry, TONGUE, 0);
    p.ell(mx, y, rx, ry, null, 3 * u, 0, 180);
};
const mouth = (p, kind, mx, my, u, k = 1)=>{
    const mw = 4 * u;
    switch(kind){
        case "dash":
            p.stroke([
                [
                    mx - 5.5 * u * k,
                    my
                ],
                [
                    mx + 5.5 * u * k,
                    my - 0.8 * u
                ]
            ], mw);
            break;
        case "frown":
            p.arc(mx, my + 3 * u, 6.5 * u * k, 3.5 * u, 200, 340, mw);
            break;
        case "smirk":
            p.arc(mx + u, my - 3 * u, 7 * u * k, 4 * u, 10, 150, mw);
            break;
        case "smile":
            p.arc(mx, my - 3 * u, 8 * u * k, 4.5 * u, 20, 160, mw);
            break;
        case "smileWide":
            p.arc(mx, my - 4 * u, 11 * u * k, 6 * u, 15, 165, mw);
            break;
        case "grin":
            dmouth(p, mx, my - u, 12 * u * k, 8 * u, u);
            break;
        case "laugh":
            dmouth(p, mx, my, 16 * u * k, 11 * u, u, true);
            break;
        case "o":
            p.ell(mx + 4 * u, my, 3.5 * u, 4 * u, MOUTH, 2.8 * u);
            break;
        case "O":
            p.ell(mx, my + 2 * u, 9 * u * k, 11 * u, MOUTH, 3.2 * u);
            break;
        case "wave":
            {
                const s = [];
                for(let i = 0; i <= 12; i++)s.push([
                    mx - 9 * u * k + i * 1.5 * u * k,
                    my + 1.5 * u * Math.sin(i * 1.3)
                ]);
                p.stroke(s, 3 * u);
                break;
            }
        case "teeth":
            p.poly([
                [
                    mx - 12 * u * k,
                    my - 4 * u
                ],
                [
                    mx + 12 * u * k,
                    my - 4 * u
                ],
                [
                    mx + 11 * u * k,
                    my + 4 * u
                ],
                [
                    mx - 11 * u * k,
                    my + 4 * u
                ]
            ], WHITE, 3 * u);
            for (const j of [
                -1,
                0,
                1
            ])p.stroke([
                [
                    mx + j * 6 * u * k,
                    my - 4 * u
                ],
                [
                    mx + j * 6 * u * k,
                    my + 4 * u
                ]
            ], 1.5 * u);
            break;
        case "lick":
            p.arc(mx, my - 3 * u, 8 * u * k, 4.5 * u, 20, 160, mw);
            p.ell(mx + 6 * u * k, my + 3 * u, 3.6 * u, 4.6 * u, TONGUE, 2.4 * u);
            break;
    }
};
const faceFront = (p, cx, cy, W, expr, facing, look, lid, brim, skin, moustache, stout = false)=>{
    const u = W / 100, F = FACE[expr], fx = cx + 7 * u * facing;
    const ex = (F.eye[0] === "shock" ? 12 : 13) * u, ey = cy;
    for (const side of [
        -1,
        1
    ]){
        const x = fx + side * ex;
        const kind = eyeKind(F.eye[(facing ? side === facing : side > 0) ? 1 : 0], lid);
        eye(p, kind, x, ey, u, side, look, skin);
        const [dI, dO] = F.brow, by = ey - (brim ? 17 : 20) * u;
        if (kind === "shock" || kind === "shockHalf") p.arc(x, by - 6 * u, 9 * u, 3 * u, 200, 340, 4 * u);
        else taper(p, [
            x - side * 8.5 * u,
            by + dI * u
        ], [
            x + side * 8.5 * u,
            by + dO * u
        ], 5 * u, 2.5 * u);
    }
    const mx = cx + 8 * u * facing, my = cy + 20 * u;
    mouth(p, F.mouth, mx, my, u);
    if (moustache) for (const s of [
        -1,
        1
    ])taper(p, [
        mx + s * 1.5 * u,
        cy + 12.5 * u
    ], [
        mx + s * (stout ? 19 : 15) * u,
        cy + (stout ? 10.5 : 15) * u
    ], stout ? 5.5 * u : 4.5 * u, 1.6 * u, moustache);
    if (expr === "nervous") p.ell(cx + 40 * u * (facing || 1), cy - 22 * u, 3 * u, 5 * u, "#9fd4ff", 2 * u);
};
const faceSide = (p, hx, hy, W, expr, lid, brim, skin, moustache, stout = false)=>{
    const u = W / 100, F = FACE[expr], ex = hx + 27 * u, ey = hy;
    const kind = eyeKind(F.eye[1], lid);
    eye(p, kind, ex, ey, u, 1, 0.6, skin);
    const by = ey - (brim ? 17 : 20) * u, [dI, dO] = F.brow;
    if (kind === "shock" || kind === "shockHalf") p.arc(ex, by - 6 * u, 9 * u, 3 * u, 200, 340, 4 * u);
    else taper(p, [
        ex + 8 * u,
        by + dI * u
    ], [
        ex - 7 * u,
        by - u + dO * u
    ], 5 * u, 2.5 * u);
    p.stroke([
        [
            hx + 44 * u,
            hy + 4 * u
        ],
        [
            hx + 47.5 * u,
            hy + 9 * u
        ],
        [
            hx + 43 * u,
            hy + 10 * u
        ]
    ], 3 * u);
    mouth(p, F.mouth, hx + 33 * u, hy + 21 * u, u, 0.62);
    if (moustache) taper(p, [
        hx + 41 * u,
        hy + 13.5 * u
    ], [
        hx + 25 * u,
        hy + (stout ? 11.5 : 16) * u
    ], stout ? 5.5 * u : 4.5 * u, 1.6 * u, moustache);
    if (expr === "nervous") p.ell(hx - 30 * u, hy - 24 * u, 3 * u, 5 * u, "#9fd4ff", 2 * u);
};
const BONNET = "#e9cf8f", BONNET_BRIM = "#d6b46a";
const hatBehind = (p, o, H, cx, hc, light, thick, ow, side)=>{
    if (o.hat !== "bonnet") return;
    const bb = blobPts(cx - (side ? 12 : 0) * (H.a / 50), hc - 0.07 * 2 * H.b, {
        ...H,
        a: H.a * 1.17,
        b: H.b * 1.13,
        asym: 0,
        egg: 0.04,
        seed: H.seed + 3
    });
    p.shadedFill(bb, BONNET, mul(BONNET, SH_CLOTH), light, H.a * 1.17);
    p.inkRing(bb, ow * 0.85, thick);
};
const hatOn = (p, o, hp, H, cx, hc, light, seed, facing, side)=>{
    const W = 2 * H.a, HH = 2 * H.b, u = W / 100, crown = hc - H.b, ow = 0.85 * 5 * u;
    const a = H.rot + rad(4 * (rnd(seed, 20) - 0.5));
    const R = (pts)=>rotPts(pts, a, cx, hc);
    const sag = (yb, wb)=>{
        const base = [];
        for(let i = 0; i <= 12; i++){
            const t = i / 12;
            base.push([
                cx + wb * (2 * t - 1),
                yb + 3 * u * (1 - (2 * t - 1) ** 2)
            ]);
        }
        return base;
    };
    if (o.hat === "shako" || o.hat === "shako_tall") {
        const tall = o.hat === "shako_tall", yb = crown + 0.25 * HH, ht = (tall ? 0.66 : 0.56) * HH, wb = 46 * u, wt = 52 * u;
        const body = R([
            ...sag(yb, wb).reverse(),
            [
                cx - wt,
                yb - ht
            ],
            [
                cx + wt,
                yb - ht
            ]
        ]);
        p.shadedFill(body, "#3a3d47", "#24262d", light, wt, 0.4);
        if (tall) p.clip(body, ()=>p.band(R([
                [
                    cx - wt - 5 * u,
                    yb - ht + 0.07 * HH
                ],
                [
                    cx + wt + 5 * u,
                    yb - ht + 0.07 * HH
                ]
            ]), "#e8c45a", 0.06 * HH, 1.5 * u));
        p.poly(body, null, ow);
        const deg = a * 180 / Math.PI;
        if (side) {
            p.poly(R([
                [
                    cx + 36 * u,
                    yb - 1 * u
                ],
                [
                    cx + 60 * u,
                    yb + 8 * u
                ],
                [
                    cx + 34 * u,
                    yb + 6 * u
                ]
            ]), "#16171b", 2.5 * u);
            const [tx, ty] = R([
                [
                    cx + 24 * u,
                    yb - ht - 6 * u
                ]
            ])[0];
            p.ell(tx, ty, 7 * u, 7 * u, "#2b7a4b", 2.5 * u);
        } else {
            const [px, py] = R([
                [
                    cx + 3 * u * facing,
                    yb + 3 * u
                ]
            ])[0];
            p.ell(px, py, 34 * u, 0.045 * HH, "#16171b", 2.5 * u, 0, 180, deg);
            const [bx, by] = R([
                [
                    cx,
                    yb - 0.45 * ht
                ]
            ])[0];
            p.ell(bx, by, 7 * u, 6 * u, tall ? "#e8c45a" : "#c9ccd2", 2 * u, 0, 360, deg);
            p.arc(bx, by, 3.5 * u, 2.8 * u, 200, 500, 1.6 * u);
            const [tx, ty] = R([
                [
                    cx,
                    yb - ht - 6 * u
                ]
            ])[0];
            p.ell(tx, ty, 7 * u, 7 * u, "#2b7a4b", 2.5 * u);
        }
    } else if (o.hat === "cap" || o.hat === "hair") {
        const cut = crown + (o.hat === "cap" ? 0.3 : 0.42) * HH;
        const keep = (x, y)=>y < cut || side && o.hat === "hair" && x < cx - 6 * u && y < hc + 0.42 * H.b;
        const n = hp.length, startIdx = Math.max(0, hp.findIndex(([x, y], i)=>keep(x, y) && !keep(hp[(i + n - 1) % n][0], hp[(i + n - 1) % n][1])));
        const arc = [
            ...hp.slice(startIdx),
            ...hp.slice(0, startIdx)
        ].filter(([x, y])=>keep(x, y)).map(([x, y])=>[
                cx + (x - cx) * 1.03,
                hc + (y - hc) * 1.03
            ]);
        if (arc.length < 3) return;
        if (o.hat === "hair") {
            const [x0, y0] = arc[arc.length - 1], [x1, y1] = arc[0];
            for(let i = 1; i < 6; i++)arc.push([
                x0 + (x1 - x0) * i / 6,
                y0 + (y1 - y0) * i / 6 + (i % 2 ? 4 * u : 0)
            ]);
        }
        const col = o.hat === "cap" ? o.cap : o.hair;
        p.shadedFill(arc, col, mul(col, SH_FELT), light, H.a, 0.35);
        p.poly(arc, null, ow);
        if (o.hat === "hair") {
            const s = side ? -1 : facing || 1;
            p.stroke([
                [
                    cx + s * 10 * u,
                    cut - 30 * u
                ],
                [
                    cx + s * 2 * u,
                    cut - 12 * u
                ]
            ], 1.2 * u);
        }
        if (o.hat === "cap") {
            const deg = a * 180 / Math.PI;
            if (side) p.poly(R([
                [
                    cx + 40 * u,
                    cut - 2 * u
                ],
                [
                    cx + 74 * u,
                    cut + 4 * u
                ],
                [
                    cx + 40 * u,
                    cut + 6 * u
                ]
            ]), shade(col, 0.8), ow);
            else {
                const s = facing || (rnd(seed, 21) < 0.5 ? -1 : 1), [px, py] = R([
                    [
                        cx + s * 4 * u,
                        cut + 1.5 * u
                    ]
                ])[0];
                p.ell(px, py, 32 * u, 0.06 * HH, shade(col, 0.8), ow, 0, 180, deg);
            }
        }
    } else if (o.hat === "tophat") {
        const yb = crown + 0.22 * HH, ht = 0.8 * HH, wb = 0.31 * W, wt = 0.33 * W, col = "#2e2a36";
        const body = R([
            ...sag(yb, wb).reverse(),
            [
                cx - wt,
                yb - ht
            ],
            [
                cx + wt,
                yb - ht
            ]
        ]);
        p.shadedFill(body, col, mul(col, SH_FELT), light, wt, 0.4);
        p.clip(body, ()=>p.band(R([
                [
                    cx - wt - 4 * u,
                    yb - 0.13 * HH
                ],
                [
                    cx + wt + 4 * u,
                    yb - 0.13 * HH
                ]
            ]), shade(o.jacket, 0.9), 0.14 * HH, 0.8 * u));
        p.poly(body, null, ow);
        const [bx, by] = R([
            [
                cx,
                yb + 1 * u
            ]
        ])[0];
        p.ell(bx, by, 0.45 * W, 0.05 * HH, "#1d1b22", ow, 0, 360, a * 180 / Math.PI);
    } else if (o.hat === "bonnet") {
        const [bx, by] = R([
            [
                cx + (side ? 6 * u : 0),
                crown + 0.16 * HH
            ]
        ])[0];
        p.arc(bx, by, 0.5 * W, 0.2 * HH, 200, 340, 7 * u, BONNET_BRIM);
        p.arc(bx, by, 0.5 * W + 3.5 * u, 0.2 * HH + 3.5 * u, 200, 340, 1.2 * u);
        const cy = hc + H.b * 0.98;
        p.stroke([
            [
                cx - 14 * u,
                cy - 4 * u
            ],
            [
                cx,
                cy + 2 * u
            ],
            [
                cx + 14 * u,
                cy - 4 * u
            ]
        ], 2 * u, BONNET_BRIM);
    }
};
const BUILD = {
    adult: {
        a: 118,
        torso: 1.1,
        legs: 1.4,
        tw: 0.8
    },
    stout: {
        a: 118,
        torso: 1.15,
        legs: 1.32,
        tw: 0.92
    },
    kid: {
        a: 112,
        torso: 0.85,
        legs: 1.0,
        tw: 0.72
    }
};
const footStroke = (p, a, b, w, col)=>{
    if (col !== INK) p.stroke([
        a,
        b
    ], w + 3, INK);
    p.stroke([
        a,
        b
    ], w, col);
};
export const bodyFront = (p, o, opts)=>{
    const { phase = 0, expr = "neutral", mode = "march", look = 0, blink = false, lift = 60, prop = null, tilt = 0, headTilt = 0, wave, light = DEF_LIGHT, facing = 0, seed = 1 } = opts;
    const Bd = BUILD[o.build ?? "adult"], skin = o.skin ?? SKIN, two = Math.PI * 2, lid = lidOf(blink);
    const H = headBlob(seed, Bd.a, facing), W = 2 * H.a, HH = 2 * H.b, u = W / 100;
    const tall = (1 + Bd.torso + Bd.legs) * HH, sole = 975;
    const bob = mode === "march" ? 0.025 * tall * Math.cos(2 * two * phase) : mode === "stroll" ? 0.015 * tall * Math.cos(2 * two * phase) : 0;
    const torsoBot = mode === "sit" ? sole - 0.2 * HH : sole - Bd.legs * HH + bob;
    const chin = torsoBot - Bd.torso * HH, hc = chin - H.b, crown = hc - H.b, hipY = torsoBot - 0.12 * HH;
    const thick = thickAngle(light), ow = 5 * u;
    const legCol = mix(o.pants, INK, 0.55), armCol = mix(o.jacket, INK, 0.5), footCol = o.boots;
    const legW = 5.8 * u, footW = 7.5 * u;
    p.rot = null;
    if (mode === "sit") {
        for (const side of [
            -1,
            1
        ]){
            const h = [
                300 + side * 15 * u,
                hipY
            ], k = [
                300 + side * 36 * u,
                hipY + 0.2 * HH
            ], f = [
                300 + side * 44 * u,
                sole - 8 * u
            ];
            p.stroke(curve(h, k, f), legW, legCol);
            footStroke(p, [
                f[0] - side * 2 * u,
                f[1]
            ], [
                f[0] + side * 12 * u,
                f[1] - 5 * u
            ], footW, footCol);
        }
    } else if (mode === "fall") {
        const legs = [
            [
                [
                    300 - 15 * u,
                    hipY
                ],
                [
                    300 - 46 * u,
                    hipY + 0.5 * HH
                ],
                [
                    300 - 70 * u,
                    hipY + 0.72 * HH
                ]
            ],
            [
                [
                    300 + 15 * u,
                    hipY
                ],
                [
                    300 + 50 * u,
                    hipY + 0.45 * HH
                ],
                [
                    300 + 76 * u,
                    hipY + 0.22 * HH
                ]
            ]
        ];
        legs.forEach(([h, k, f], i)=>{
            p.stroke(curve(h, k, f), legW, legCol);
            footStroke(p, f, [
                f[0] + (i ? 14 : -14) * u,
                f[1] + (i ? -6 : 4) * u
            ], footW, footCol);
        });
    } else if (o.dress) {
        for (const side of [
            -1,
            1
        ]){
            const fx = 300 + side * 12 * u, fy = sole - 4 * u;
            p.stroke([
                [
                    fx,
                    sole - 0.4 * HH
                ],
                [
                    fx + side * u,
                    fy
                ]
            ], legW, legCol);
            footStroke(p, [
                fx - side * 3 * u,
                fy
            ], [
                fx + side * 12 * u,
                fy + u
            ], footW, footCol);
        }
    } else {
        const L = mode === "march" ? lift * 1.25 : mode === "stroll" ? lift * 0.55 : 0;
        for (const [side, ph] of [
            [
                -1,
                0
            ],
            [
                1,
                0.5
            ]
        ]){
            const up = Math.max(0, Math.sin(two * (phase + ph))) * L;
            const hx = 300 + side * 15 * u, fx = 300 + side * 22 * u, fy = sole - 4 * u - up;
            const k = [
                (hx + fx) / 2 + side * (1.5 * u + up * 0.16),
                (hipY + fy) / 2 - up * 0.08
            ];
            p.stroke(curve([
                hx,
                hipY
            ], k, [
                fx,
                fy
            ]), legW, legCol);
            footStroke(p, [
                fx - side * 3 * u,
                fy
            ], [
                fx + side * 13 * u,
                fy + 0.5 * u
            ], footW, footCol);
        }
    }
    const sway = mode === "march" ? 1.6 * Math.sin(two * phase) : mode === "stroll" ? 1.0 * Math.sin(two * phase) : 0;
    const A = tilt + sway;
    p.rot = A ? [
        rad(A),
        300,
        hipY
    ] : null;
    const dress = !!o.dress && mode !== "sit" && mode !== "fall";
    const T = {
        a: Bd.tw / 2 * W / 1.06,
        b: 0.5 * (torsoBot - (chin - 0.25 * HH)),
        nTop: 2.2,
        nBot: 2.6,
        egg: o.build === "stout" ? 0.17 : 0.12,
        asym: 0.04 * facing,
        rot: 0,
        noise: 0.006,
        seed: seed + 7
    };
    const tcx = 300 + 3 * u * facing, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
    const sh = (side)=>[
            tcx + side * 0.85 * T.a,
            chin + 0.12 * HH
        ];
    const hang = (side, fwd)=>{
        const S = sh(side), ex = tcx + side * (1.12 * T.a + 4 * u);
        const hx = ex + side * 3 * u - side * 6 * u * Math.max(0, fwd) + side * 4 * u * Math.max(0, -fwd);
        return [
            S,
            [
                ex,
                S[1] + 0.48 * HH
            ],
            [
                hx,
                chin + 1.04 * HH - Math.abs(fwd) * 9 * u
            ]
        ];
    };
    const sw = mode === "march" || mode === "stroll" ? Math.sin(two * phase) : 0;
    const R0 = [
        300 + 47 * u,
        torsoBot + 0.12 * HH
    ], R1 = [
        300 + 64 * u,
        crown - 0.32 * HH
    ];
    const rifle = !!o.rifle && (mode === "march" || mode === "stand" || mode === "stroll");
    const arms = [];
    if (mode === "sit") for (const side of [
        -1,
        1
    ])arms.push({
        pts: [
            sh(side),
            [
                tcx + side * (1.1 * T.a + 6 * u),
                sh(side)[1] + 0.4 * HH
            ],
            [
                tcx + side * (1.2 * T.a + 10 * u),
                torsoBot + 0.04 * HH
            ]
        ],
        front: false
    });
    else if (mode === "fall") for (const side of [
        -1,
        1
    ])arms.push({
        pts: [
            sh(side),
            [
                tcx + side * (1.15 * T.a + 12 * u),
                sh(side)[1] - 0.25 * HH
            ],
            [
                tcx + side * (1.3 * T.a + 24 * u),
                sh(side)[1] - 0.68 * HH
            ]
        ],
        front: false
    });
    else {
        arms.push({
            pts: prop === "shako" ? hang(-1, 0) : hang(-1, -sw),
            front: false
        });
        if (rifle) {
            const G = lerp2(R0, R1, 0.1);
            arms.push({
                pts: [
                    sh(1),
                    [
                        tcx + 1.12 * T.a + 5 * u,
                        sh(1)[1] + 0.45 * HH
                    ],
                    G
                ],
                front: false
            });
        } else if (wave !== undefined) {
            const S = sh(1);
            arms.push({
                pts: [
                    S,
                    [
                        tcx + 1.1 * T.a + 10 * u + 3 * u * wave,
                        S[1] - 0.22 * HH
                    ],
                    [
                        tcx + 1.18 * T.a + 16 * u + 12 * u * wave,
                        S[1] - 0.6 * HH
                    ]
                ],
                front: false
            });
        } else if (prop === "icecream") {
            const S = sh(1);
            arms.push({
                pts: [
                    S,
                    [
                        tcx + 1.05 * T.a + 4 * u,
                        S[1] + 0.45 * HH
                    ],
                    [
                        tcx + 0.5 * T.a,
                        S[1] + 0.4 * HH
                    ]
                ],
                front: true
            });
        } else if (Array.isArray(prop)) {
            const S = sh(1), k = clamp(prop[1], 0, 1);
            const E = lerp2([
                tcx + 1.1 * T.a + 10 * u,
                S[1] - 0.15 * HH
            ], [
                tcx + 1.2 * T.a + 10 * u,
                S[1] + 0.3 * HH
            ], k);
            const Hd = lerp2([
                tcx + 1.15 * T.a + 14 * u,
                S[1] - 0.55 * HH
            ], [
                tcx + 1.45 * T.a + 22 * u,
                S[1] + 0.35 * HH
            ], k);
            arms.push({
                pts: [
                    S,
                    E,
                    Hd
                ],
                front: true
            });
        } else arms.push({
            pts: hang(1, sw),
            front: false
        });
    }
    const drawArm = (a)=>{
        p.stroke(curve(a.pts[0], a.pts[1], a.pts[2]), 5.2 * u, armCol);
        p.dot(a.pts[2][0], a.pts[2][1], 5.5 * u);
    };
    if (rifle) {
        p.band([
            R0,
            R1
        ], "#7a4b2a", 5 * u, 1.5 * u, "round");
        p.band([
            lerp2(R0, R1, 0.6),
            R1
        ], "#8d949c", 2.4 * u, 1.2 * u, "round");
    }
    if (o.sword && mode !== "sit") {
        const s0 = [
            tcx - 0.75 * T.a,
            torsoBot - 0.2 * HH
        ];
        p.band([
            s0,
            [
                s0[0] - Math.sin(rad(25)) * 0.8 * HH,
                s0[1] + Math.cos(rad(25)) * 0.8 * HH
            ]
        ], "#c9ccd2", 3 * u, 1.2 * u, "round");
    }
    for (const a of arms)if (!a.front) drawArm(a);
    if (dress) {
        const D = {
            a: 0.5 * W * 0.98,
            b: 0.5 * (sole - 0.35 * HH - (chin - 0.2 * HH)),
            nTop: 2.0,
            nBot: 3.0,
            egg: 0.35,
            asym: 0.03 * facing,
            rot: 0,
            noise: 0.006,
            seed: seed + 9
        };
        const dp = blobPts(300, sole - 0.35 * HH - D.b, D);
        p.gradFill(dp, o.dress, mul(o.dress, SH_CLOTH), light);
        p.inkRing(dp, ow, thick);
        const Sw = {
            a: 0.37 * W,
            b: 0.3 * HH,
            nTop: 2.2,
            nBot: 2.4,
            egg: 0.1,
            asym: 0,
            rot: 0,
            noise: 0.006,
            seed: seed + 8
        };
        const sp = blobPts(300, chin + 0.12 * HH, Sw);
        p.gradFill(sp, o.jacket, mul(o.jacket, SH_CLOTH), light);
        p.inkRing(sp, ow * 0.9, thick);
    } else {
        p.gradFill(tp, o.jacket, mul(o.jacket, SH_CLOTH), light);
        p.clip(tp, ()=>{
            if (o.belt) {
                for (const s of [
                    -1,
                    1
                ])p.band([
                    [
                        tcx - s * 0.75 * T.a,
                        chin - 0.05 * HH
                    ],
                    [
                        tcx + s * 0.8 * T.a,
                        torsoBot - 0.1 * HH
                    ]
                ], o.belt, 5.5 * u, 1.8 * u);
                const xc = tcx + 0.025 * T.a, yc = chin - 0.05 * HH + (torsoBot - 0.1 * HH - (chin - 0.05 * HH)) * (0.75 / 1.55);
                p.poly([
                    [
                        xc - 3.5 * u,
                        yc - 3.5 * u
                    ],
                    [
                        xc + 3.5 * u,
                        yc - 3.5 * u
                    ],
                    [
                        xc + 3.5 * u,
                        yc + 3.5 * u
                    ],
                    [
                        xc - 3.5 * u,
                        yc + 3.5 * u
                    ]
                ], "#d9dde0", 1.5 * u);
            }
            if (o.sash) p.band([
                [
                    tcx - 1.3 * T.a,
                    torsoBot - 0.32 * HH
                ],
                [
                    tcx + 1.3 * T.a,
                    torsoBot - 0.32 * HH
                ]
            ], o.sash, 0.13 * HH, 1.8 * u);
            for(let i = 0; i < 4; i++){
                const y = chin + 0.12 * HH + i * 0.2 * HH;
                if (o.sash && Math.abs(y - (torsoBot - 0.32 * HH)) < 0.08 * HH) continue;
                p.dot(tcx + 2 * u * facing, y, 2.2 * u + 0.8 * u, INK);
                p.dot(tcx + 2 * u * facing, y, 2.2 * u, o.buttons ?? shade(o.jacket, 0.7));
            }
        });
        if (o.sash) {
            const s = facing || 1;
            p.poly([
                [
                    tcx + s * 0.55 * T.a,
                    torsoBot - 0.3 * HH
                ],
                [
                    tcx + s * 0.75 * T.a,
                    torsoBot + 0.05 * HH
                ],
                [
                    tcx + s * 0.45 * T.a,
                    torsoBot + 0.02 * HH
                ]
            ], o.sash, 1.6 * u);
        }
        p.inkRing(tp, ow, thick);
    }
    for (const a of arms)if (a.front) {
        drawArm(a);
        const [hx, hy] = a.pts[2];
        if (prop === "icecream") {
            p.poly([
                [
                    hx - 8 * u,
                    hy - 12 * u
                ],
                [
                    hx + 8 * u,
                    hy - 12 * u
                ],
                [
                    hx,
                    hy + 7 * u
                ]
            ], "#e0a35a", 1.8 * u);
            p.ell(hx, hy - 19 * u, 11 * u, 10 * u, "#f7c6d9", 2.2 * u);
            p.dot(hx, hy, 5.5 * u);
        } else if (Array.isArray(prop)) {
            const ang = rad(-70 + 105 * clamp(prop[1], 0, 1));
            const Rh = (pts)=>rotPts(pts, ang, hx, hy);
            p.band(Rh([
                [
                    hx,
                    hy + 12 * u
                ],
                [
                    hx,
                    hy - 44 * u
                ]
            ]), "#8a5a34", 5 * u, 1.5 * u, "round");
            p.poly(Rh([
                [
                    hx - 12 * u,
                    hy - 58 * u
                ],
                [
                    hx + 20 * u,
                    hy - 58 * u
                ],
                [
                    hx + 20 * u,
                    hy - 42 * u
                ],
                [
                    hx - 12 * u,
                    hy - 42 * u
                ]
            ]), "#7d848c", 2.2 * u);
            p.dot(hx, hy, 5.5 * u);
        }
    }
    if (prop === "shako") {
        const [hx, hy] = arms[0].pts[2];
        p.poly([
            [
                hx - 14 * u,
                hy + 3 * u
            ],
            [
                hx + 14 * u,
                hy + 3 * u
            ],
            [
                hx + 16 * u,
                hy + 30 * u
            ],
            [
                hx - 16 * u,
                hy + 30 * u
            ]
        ], "#3a3d47", 2.2 * u);
        p.ell(hx, hy + 31 * u, 3.5 * u, 3.5 * u, "#2b7a4b", 1.5 * u);
        p.dot(hx, hy, 5.5 * u);
    }
    const Ah = A + headTilt, [cpx, cpy] = rotAbout([
        300,
        chin
    ], rad(A), [
        300,
        hipY
    ]);
    p.rot = Ah ? [
        rad(Ah),
        300,
        chin,
        cpx - 300,
        cpy - chin
    ] : null;
    hatBehind(p, o, H, 300, hc, light, thick, ow, false);
    const hp = blobPts(300, hc, H);
    p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
    p.inkRing(hp, ow, thick);
    hatOn(p, o, hp, H, 300, hc, light, seed, facing, false);
    const brim = !!o.hat && o.hat !== "hair" && o.hat !== "bonnet" && o.hat !== "cap";
    faceFront(p, 300, hc, W, expr, facing, look, lid, brim, skin, o.moustache, o.build === "stout");
    p.rot = null;
};
const ik = (hip, ank, l1, l2)=>{
    const dx = ank[0] - hip[0], dy = ank[1] - hip[1], d = clamp(Math.hypot(dx, dy), 1, l1 + l2 - 0.01);
    const A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)), k = Math.atan2(dy, dx) - A;
    return [
        hip[0] + l1 * Math.cos(k),
        hip[1] + l1 * Math.sin(k)
    ];
};
const SWING_HIP = 733;
export const bodySide = (p, o, opts)=>{
    const { phase = 0, expr = "neutral", mode = "march", blink = false, stomp = 1, pose = 0, stride = 1, light = DEF_LIGHT, seed = 1 } = opts;
    const Bd = BUILD[o.build ?? "adult"], skin = o.skin ?? SKIN, two = Math.PI * 2, lid = lidOf(blink);
    const H = {
        ...headBlob(seed, Bd.a, 1),
        asym: 0.12,
        rot: rad(3 + 3 * (rnd(seed, 7) - 0.5))
    };
    const W = 2 * H.a, HH = 2 * H.b, u = W / 100, sole = 975, ankY = sole - 4 * u;
    const thick = thickAngle(light), ow = 5 * u;
    const legLen = (Bd.legs + 0.12) * HH - 4 * u, l1 = legLen / 2, l2 = legLen / 2;
    const nearCol = mix(o.pants, INK, 0.55), farCol = mix(o.pants, INK, 0.75), footCol = o.boots;
    const legs = [];
    let hipY = ankY - legLen * 0.995, lean = 0, nearFwd = 0;
    if (mode === "march") {
        const S = 370 * stride, liftH = Math.max(22, 40 + 70 * (stomp - 1));
        const st = (ph)=>{
            const c = ((phase + ph) % 1 + 1) % 1;
            if (c < 0.5) {
                const s = c / 0.5;
                return {
                    x: S / 2 - S * s,
                    h: 0,
                    stance: true,
                    s
                };
            }
            const s = (c - 0.5) / 0.5;
            return {
                x: -S / 2 + S * s - S / Math.PI * Math.sin(2 * Math.PI * s),
                h: liftH * Math.sin(Math.PI * s),
                stance: false,
                s
            };
        };
        const nL = st(0), fL = st(0.5), stance = nL.stance ? nL : fL;
        const Leff = legLen * (1 - 0.035 * Math.sin(Math.PI * stance.s));
        hipY = ankY - Math.sqrt(Math.max(1, Leff * Leff - stance.x * stance.x));
        for (const [L, near] of [
            [
                fL,
                false
            ],
            [
                nL,
                true
            ]
        ])legs.push({
            ank: [
                300 + L.x,
                ankY - L.h
            ],
            pitch: L.stance ? 0 : rad(35 * Math.sin(Math.PI * L.s) * (1 - 1.6 * L.s)),
            near
        });
        lean = 4 + 3 * Math.cos(2 * two * phase);
        nearFwd = nL.x / (S / 2);
    } else if (mode === "push") {
        hipY = ankY - 0.87 * legLen;
        legs.push({
            ank: [
                300 - 0.5 * legLen,
                ankY
            ],
            pitch: rad(-8),
            near: false
        }, {
            ank: [
                300 + 0.32 * legLen,
                ankY
            ],
            pitch: 0,
            near: true
        });
        lean = 14 * pose;
    } else if (mode === "swing") {
        hipY = SWING_HIP;
        const a = rad(60 * pose);
        for (const [dx, near] of [
            [
                -6,
                false
            ],
            [
                0,
                true
            ]
        ]){
            const knee = [
                300 + l1 * 0.98 + dx * u,
                hipY + 6 * u
            ];
            legs.push({
                ank: [
                    knee[0] + l2 * Math.sin(a),
                    knee[1] + l2 * Math.cos(a)
                ],
                pitch: -a * 0.5,
                near
            });
        }
    } else {
        legs.push({
            ank: [
                300 - 4 * u,
                ankY
            ],
            pitch: 0,
            near: false
        }, {
            ank: [
                300 + 4 * u,
                ankY
            ],
            pitch: 0,
            near: true
        });
    }
    const torsoBot = hipY + 0.12 * HH, chin = torsoBot - Bd.torso * HH, hc = chin - H.b, crown = hc - H.b, hip = [
        300,
        hipY
    ];
    p.rot = null;
    for (const L of legs){
        const knee = mode === "swing" ? [
            300 + l1 * 0.98 + (L.near ? 0 : -6 * u),
            hipY + 6 * u
        ] : ik(hip, L.ank, l1, l2);
        const hp0 = [
            300 + (L.near ? 0 : -5 * u),
            hipY
        ];
        p.stroke([
            hp0,
            knee,
            L.ank
        ], 5.8 * u, L.near ? nearCol : farCol);
        const c = Math.cos(L.pitch), s = Math.sin(L.pitch);
        footStroke(p, [
            L.ank[0] - 3 * u * c,
            L.ank[1] - 3 * u * s
        ], [
            L.ank[0] + 13 * u * c,
            L.ank[1] + 13 * u * s + 0.5 * u
        ], 7.5 * u, L.near ? footCol : footCol === INK ? INK : shade(footCol, 0.82));
    }
    p.rot = lean ? [
        rad(lean),
        300,
        hipY
    ] : null;
    const T = {
        a: (o.build === "stout" ? 0.36 : 0.31) * W,
        b: 0.5 * (torsoBot - (chin - 0.25 * HH)),
        nTop: 2.2,
        nBot: 2.5,
        egg: 0.1,
        asym: 0.06,
        rot: 0,
        noise: 0.006,
        seed: seed + 7
    };
    const tcx = 300 + 2 * u, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
    const armCol = mix(o.jacket, INK, 0.5), farArm = mix(o.jacket, INK, 0.68);
    const S = [
        tcx + 0.05 * T.a,
        chin + 0.14 * HH
    ], aLen = 0.95 * HH;
    const swingArm = (ang)=>{
        const e = [
            S[0] + Math.sin(ang) * aLen * 0.5,
            S[1] + Math.cos(ang) * aLen * 0.5
        ], a2 = ang + rad(16) * Math.sign(ang || 1);
        return [
            S,
            e,
            [
                e[0] + Math.sin(a2) * aLen * 0.5,
                e[1] + Math.cos(a2) * aLen * 0.5
            ]
        ];
    };
    const rifle = !!o.rifle && (mode === "march" || mode === "stand");
    const B0 = [
        tcx + 0.72 * T.a,
        chin + 0.58 * HH
    ], B1 = [
        tcx - 0.95 * T.a - 22 * u,
        crown - 0.4 * HH
    ];
    let near, far;
    if (mode === "swing") {
        near = [
            S,
            [
                S[0] + 12 * u,
                S[1] - 0.16 * HH
            ],
            [
                300 + 6 * u,
                chin - 0.3 * HH
            ]
        ];
        far = [
            S,
            [
                S[0] + 8 * u,
                S[1] - 0.18 * HH
            ],
            [
                300 + 2 * u,
                chin - 0.36 * HH
            ]
        ];
    } else if (mode === "push") {
        const reach = 0.55 * HH + 0.45 * HH * pose;
        let hN = [
            S[0] + reach,
            S[1] + 0.06 * HH
        ];
        if (opts.hand) {
            const th = -rad(lean), dx = opts.hand[0] - 300, dy = opts.hand[1] - hipY;
            const tg = [
                300 + dx * Math.cos(th) - dy * Math.sin(th),
                hipY + dx * Math.sin(th) + dy * Math.cos(th)
            ];
            hN = [
                hN[0] + (tg[0] - hN[0]) * pose,
                hN[1] + (tg[1] - hN[1]) * pose
            ];
        }
        near = [
            S,
            [
                (S[0] + hN[0]) / 2,
                (S[1] + hN[1]) / 2 + 0.06 * HH
            ],
            hN
        ];
        far = [
            S,
            [
                (S[0] + hN[0]) / 2 - 4 * u,
                (S[1] + hN[1]) / 2 - 0.02 * HH
            ],
            [
                hN[0] - 6 * u,
                hN[1] - 0.08 * HH
            ]
        ];
    } else if (rifle) {
        near = [
            S,
            [
                S[0] - 4 * u,
                S[1] + 0.42 * HH
            ],
            B0
        ];
        far = mode === "march" ? swingArm(rad(30) * nearFwd) : swingArm(0);
    } else {
        near = swingArm(rad(-30) * nearFwd);
        far = mode === "march" ? swingArm(rad(30) * nearFwd) : null;
    }
    if (far) {
        p.stroke(curve(far[0], far[1], far[2]), 5.2 * u, farArm);
        p.dot(far[2][0], far[2][1], 5.5 * u);
    }
    p.gradFill(tp, o.jacket, mul(o.jacket, SH_CLOTH), light);
    p.clip(tp, ()=>{
        if (o.belt) p.band([
            [
                tcx - 0.65 * T.a,
                chin - 0.05 * HH
            ],
            [
                tcx + 0.75 * T.a,
                torsoBot - 0.1 * HH
            ]
        ], o.belt, 5.5 * u, 1.8 * u);
        if (o.sash) p.band([
            [
                tcx - 1.3 * T.a,
                torsoBot - 0.32 * HH
            ],
            [
                tcx + 1.3 * T.a,
                torsoBot - 0.32 * HH
            ]
        ], o.sash, 0.13 * HH, 1.8 * u);
        if (!o.dress) for(let i = 0; i < 3; i++){
            const y = chin + 0.16 * HH + i * 0.24 * HH;
            p.dot(tcx + 0.8 * T.a, y, 3 * u, INK);
            p.dot(tcx + 0.8 * T.a, y, 2.2 * u, o.buttons ?? shade(o.jacket, 0.7));
        }
    });
    p.inkRing(tp, ow, thick);
    if (rifle) {
        p.band([
            B0,
            B1
        ], "#7a4b2a", 5 * u, 1.5 * u, "round");
        p.band([
            lerp2(B0, B1, 0.6),
            B1
        ], "#8d949c", 2.4 * u, 1.2 * u, "round");
    }
    p.stroke(curve(near[0], near[1], near[2]), 5.2 * u, armCol);
    p.dot(near[2][0], near[2][1], 5.5 * u);
    const hx = 300 + 4 * u;
    hatBehind(p, o, H, hx, hc, light, thick, ow, true);
    const hp = blobPts(hx, hc, H);
    p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
    p.inkRing(hp, ow, thick);
    hatOn(p, o, hp, H, hx, hc, light, seed, 1, true);
    const brim = !!o.hat && o.hat !== "hair" && o.hat !== "bonnet" && o.hat !== "cap";
    faceSide(p, hx, hc, W, expr, lid, brim, skin, o.moustache, o.build === "stout");
    p.rot = null;
};
export const swingKid = (p, o, kick, expr, light = DEF_LIGHT, blink = 0)=>{
    const rope = 1830, k = 1.1, HH = 2 * headBlob(5, BUILD[o.build ?? "adult"].a, 1).b;
    const seat = rope + 18, x0 = 150, x1 = 550;
    p.line([
        [
            350,
            20
        ],
        [
            x0 + 16,
            seat + 4
        ]
    ], "#a07a4c", 10);
    p.poly(rrect(x0, seat, x1, seat + 36, 10), "#b5653f", 9);
    const g = p.g;
    g.save();
    g.translate(350 - 300 * k, rope + 18 - (SWING_HIP + 0.12 * HH) * k);
    g.scale(k, k);
    bodySide(new Pen(g), o, {
        expr,
        mode: "swing",
        pose: kick,
        light,
        seed: 5,
        blink
    });
    g.restore();
    p.line([
        [
            350,
            20
        ],
        [
            x1 - 16,
            seat + 4
        ]
    ], "#a07a4c", 10);
};
export const fxNote = (p, kind, col = "#1f2a44")=>{
    p.ell(70, 200, 46, 34, col, 8, 0, 360, -20);
    p.stroke([
        [
            110,
            190
        ],
        [
            110,
            40
        ]
    ], 14);
    if (kind === 0) p.poly([
        [
            110,
            40
        ],
        [
            170,
            70
        ],
        [
            170,
            110
        ],
        [
            110,
            82
        ]
    ], col, 8);
    else {
        p.ell(150, 170, 40, 30, col, 8, 0, 360, -20);
        p.stroke([
            [
                186,
                160
            ],
            [
                186,
                20
            ]
        ], 14);
        p.poly([
            [
                110,
                40
            ],
            [
                186,
                20
            ],
            [
                186,
                50
            ],
            [
                110,
                70
            ]
        ], col, 8);
    }
};
export const fxBurst = (p, t, col = "#fff3b0", rays = 10, r0 = 40, r1 = 230)=>{
    const c = 250, e = 1 - (1 - t) ** 3;
    for(let i = 0; i < rays; i++){
        const a = rad(i * 360 / rays + 7 * (i % 2)), ra = r0 + (r1 - r0) * e * (0.75 + 0.25 * (i % 2));
        p.poly([
            [
                c + r0 * 0.5 * Math.cos(a + 0.18),
                c + r0 * 0.5 * Math.sin(a + 0.18)
            ],
            [
                c + ra * Math.cos(a),
                c + ra * Math.sin(a)
            ],
            [
                c + r0 * 0.5 * Math.cos(a - 0.18),
                c + r0 * 0.5 * Math.sin(a - 0.18)
            ]
        ], col, Math.max(3, 8 * (1 - t)));
    }
    if (t < 0.5) p.ell(c, c, r0 * (1.4 - t), r0 * (1.4 - t), WHITE, 8);
};
export const fxSplash = (p, t)=>{
    const c = 400, size = 800, rise = Math.sin(Math.min(1, t * 1.3) * Math.PI);
    const blue = "#bfe8ff", deep = "#6cc0f0";
    if (rise > 0.02) {
        const pts = [];
        for(let i = 0; i < 19; i++){
            const h = (i % 2 ? 260 : 130) * rise * (0.7 + 0.3 * Math.sin(i * 1.7));
            pts.push([
                c - 330 + 660 * i / 18,
                size - 120 - h
            ]);
        }
        p.poly([
            ...pts,
            [
                c + 330,
                size - 90
            ],
            [
                c - 330,
                size - 90
            ]
        ], blue, 10);
        p.ell(c, size - 100, 360, 46, deep, 10);
    }
    for(let i = 0; i < 8; i++){
        const a = rad(200 + i * 18), d = 120 + 380 * t, y = size - 160 + d * Math.sin(a) + 520 * t * t, r = 26 * (1 - t) + 6;
        if (t > 0.08 && y < size - 40) p.ell(c + d * Math.cos(a), y, r, r * 1.25, blue, 7);
    }
};
export const fxPuff = (p, t)=>{
    for(let i = 0; i < 5; i++){
        const a = rad(160 + i * 55), d = 40 + 70 * t, r = (34 + 20 * (i % 2)) * (1 - 0.6 * t);
        p.ell(150 + d * Math.cos(a), 180 + d * 0.45 * Math.sin(a), r, r * 0.8, `rgba(238,225,205,${(1 - t).toFixed(3)})`, 0);
    }
};
export const fxStars = (p, t)=>{
    for(let i = 0; i < 4; i++){
        const a = t * Math.PI * 2 + i * Math.PI / 2, x = 210 + 150 * Math.cos(a), y = 110 + 40 * Math.sin(a), pts = [];
        for(let k = 0; k < 10; k++){
            const r = k % 2 ? 14 : 34, b = rad(k * 36 - 90);
            pts.push([
                x + r * Math.cos(b),
                y + r * Math.sin(b)
            ]);
        }
        p.poly(pts, "#ffd84a", 6);
    }
};
export const fxCreak = (p, t)=>{
    const j = 6 * Math.sin(t * 40);
    for (const a of [
        -30,
        0,
        30
    ]){
        const b = rad(a - 90);
        p.stroke([
            [
                150 + 70 * Math.cos(b) + j,
                230 + 70 * Math.sin(b)
            ],
            [
                150 + 100 * Math.cos(b) + 10 + j,
                230 + 100 * Math.sin(b)
            ],
            [
                150 + 130 * Math.cos(b) + j,
                230 + 130 * Math.sin(b)
            ]
        ], 10);
    }
};
export const fxRing = (p, t)=>{
    const g = p.g;
    for(let k = 0; k < 3; k++){
        const u = t - k * 0.22;
        if (u <= 0 || u >= 1) continue;
        g.beginPath();
        g.ellipse(300, 300, 60 + 230 * u, 60 + 230 * u, 0, 0, Math.PI * 2);
        g.strokeStyle = k === 0 ? "#f6fcff" : "#cfe8fa";
        g.lineWidth = 9 * (1 - u) + 3;
        g.stroke();
    }
};
export const fxSign = (p)=>{
    const g = p.g, RED = "#d42f2f";
    p.poly(rrect(14, 14, 686, 506, 40), "#f6ecd2", 0);
    p.poly(rrect(14, 14, 686, 506, 40), null, 14);
    p.poly(rrect(70, 352, 630, 384, 8), "#8a5a3a", 9);
    g.beginPath();
    g.moveTo(112, 470);
    g.quadraticCurveTo(350, 300, 588, 470);
    g.strokeStyle = INK;
    g.lineWidth = 16;
    g.lineCap = "round";
    g.stroke();
    for (const x of [
        88,
        612
    ])p.poly(rrect(x - 16, 384, x + 16, 470, 4), "#8a5a3a", 9);
    for (const x of [
        150,
        278,
        406,
        534
    ]){
        p.poly(rrect(x - 30, 150, x + 30, 214, 14), "#357650", 9);
        p.stroke([
            [
                x - 8,
                210
            ],
            [
                x + 34,
                262
            ],
            [
                x + 46,
                338
            ]
        ], 15, INK);
        p.stroke([
            [
                x + 6,
                210
            ],
            [
                x - 12,
                274
            ],
            [
                x - 36,
                336
            ]
        ], 15, INK);
        p.poly(rrect(x + 30, 330, x + 74, 350, 9), INK, 0);
        p.poly(rrect(x - 52, 328, x - 8, 348, 9), INK, 0);
    }
    for (const [a, b] of [
        [
            [
                96,
                70
            ],
            [
                604,
                452
            ]
        ],
        [
            [
                604,
                70
            ],
            [
                96,
                452
            ]
        ]
    ]){
        p.stroke([
            a,
            b
        ], 58, "#ffffff");
        p.stroke([
            a,
            b
        ], 42, RED);
    }
};
export const fxCloud = (p, seed)=>{
    const blobs = [
        [
            150,
            190,
            80
        ],
        [
            250,
            150,
            105
        ],
        [
            360,
            160,
            95
        ],
        [
            450,
            195,
            70
        ],
        [
            300,
            210,
            90
        ]
    ];
    for (const [x, y, r] of blobs)p.ell(x + seed * 37 % 20 - 10, y, r, r * 0.8, "#ffffff", 0);
    p.ell(300, 235, 230, 40, "#ffffff", 0);
};
export const fxShadow = (p, col)=>{
    const g = p.g;
    g.fillStyle = WHITE;
    g.fillRect(0, 0, 128, 256);
    g.save();
    g.filter = "blur(9px)";
    const lg = g.createLinearGradient(0, 205, 0, 22);
    lg.addColorStop(0, mix(col, WHITE, 0.08));
    lg.addColorStop(0.55, mix(col, WHITE, 0.3));
    lg.addColorStop(1, mix(col, WHITE, 0.85));
    g.fillStyle = lg;
    g.beginPath();
    g.moveTo(40, 205);
    g.bezierCurveTo(36, 120, 46, 50, 64, 30);
    g.bezierCurveTo(82, 50, 92, 120, 88, 205);
    g.closePath();
    g.fill();
    g.fillStyle = col;
    g.beginPath();
    g.ellipse(64, 205, 30, 17, 0, 0, Math.PI * 2);
    g.fill();
    g.restore();
};
export const fxContact = (p, col)=>{
    const g = p.g;
    g.fillStyle = WHITE;
    g.fillRect(0, 0, 128, 128);
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    for (const [r, k] of [
        [
            0,
            0
        ],
        [
            0.32,
            0.02
        ],
        [
            0.5,
            0.22
        ],
        [
            0.66,
            0.58
        ],
        [
            0.82,
            0.88
        ],
        [
            1,
            1
        ]
    ])gr.addColorStop(r, mix(col, WHITE, k));
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
};
export const fxPlank = (p)=>{
    p.poly(rrect(14, 30, 306, 78, 10), "#a8744a", 9);
    p.line([
        [
            40,
            46
        ],
        [
            150,
            44
        ],
        [
            270,
            50
        ]
    ], "#7d5234", 4);
    p.line([
        [
            60,
            62
        ],
        [
            200,
            64
        ],
        [
            284,
            60
        ]
    ], "#7d5234", 4);
    p.dot(36, 54, 5, INK);
    p.dot(284, 54, 5, INK);
};
export const fxDrum = (p)=>{
    p.poly(rrect(40, 70, 220, 190, 16), "#f1ece0", 9);
    p.poly(rrect(32, 58, 228, 86, 12), "#c9373a", 8);
    p.poly(rrect(32, 176, 228, 204, 12), "#c9373a", 8);
    p.line([
        [
            52,
            88
        ],
        [
            82,
            172
        ],
        [
            112,
            88
        ],
        [
            142,
            172
        ],
        [
            172,
            88
        ],
        [
            202,
            172
        ]
    ], INK, 6);
    p.ell(130, 58, 98, 18, "#f7f3ea", 8);
};
export const fxBlob = (p, col)=>{
    const g = p.g;
    g.fillStyle = WHITE;
    g.fillRect(0, 0, 128, 128);
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    for (const [r, k] of [
        [
            0,
            0
        ],
        [
            0.5,
            0.04
        ],
        [
            0.64,
            0.18
        ],
        [
            0.76,
            0.42
        ],
        [
            0.87,
            0.72
        ],
        [
            0.95,
            0.92
        ],
        [
            1,
            1
        ]
    ])gr.addColorStop(r, mix(col, WHITE, k));
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
};
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
