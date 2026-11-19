"""Cut-out rig for the cast characters: body / head (per expression + blink) / hands / props are pre-rendered sprites,
arms and legs are re-drawn every frame as tapered curved strokes through shoulder-elbow-hand and hip-knee-foot (2-bone IK).
Actions give the character real acting instead of sliding a flat card around.

    r = Rig(spec, look=(0.5, -0.6), post=lambda im: im)
    img = r.render(t, action="idle", pose="point_up", expr="curious", dur=2.0)   # RGBA, 2000x3600 (2x card space)

Actions: idle stand point_up hips arms_up shrug hold_spear hold_sword laugh cheer shake march walk run climb climb_fast
         dig panic recoil bounce pop pop_final (unknown names fall back to idle + the static pose)
"""
import math, random
from PIL import Image
from charkit import Canvas, INK, ellipse_pts, capsule_pts
import cast as C

S = 2  # sprite / output scale relative to card space (1000x1800)


def _ik(a, b, l1, l2, bend):
    dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy)
    d = max(1e-3, min(d, l1 + l2 - 0.5))
    base = math.atan2(dy, dx)
    ca = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d); th = math.acos(max(-1, min(1, ca)))
    e = (a[0] + l1 * math.cos(base + bend * th), a[1] + l1 * math.sin(base + bend * th))
    end = (a[0] + d * math.cos(base), a[1] + d * math.sin(base))
    return e, end


def _ctrl(a, e, b):
    return (2 * e[0] - (a[0] + b[0]) / 2, 2 * e[1] - (a[1] + b[1]) / 2)


def _rot(p, c, deg):
    r = math.radians(deg); x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(r) - y * math.sin(r), c[1] + x * math.sin(r) + y * math.cos(r))


def _crop(im, pivot):
    bb = im.getbbox() or (0, 0, 1, 1); bb = (max(0, bb[0] - 4), max(0, bb[1] - 4), min(im.width, bb[2] + 4), min(im.height, bb[3] + 4))
    return im.crop(bb), (pivot[0] - bb[0], pivot[1] - bb[1])


class Rig:
    def __init__(self, spec, look=(0, 0), post=None, prop=None):
        self.spec, self.look, self.post = spec, tuple(look), post or (lambda im: im)
        self.prop = prop if prop is not None else spec.get("prop")
        B = spec["body"]; self.bw_t, self.bw_b, self.bh = B["w_top"], B["w_bot"], B["h"]
        legs = spec.get("legs", 500); self.r = spec["head"].get("r", 225); off = spec.get("head_offset", 50)
        self.feet_y = 1800 - 210
        self.by = self.feet_y - legs - self.bh * 0.40 + 30; self.bx = 500 + spec.get("body_x", 0)
        bx, by, bh = self.bx, self.by, self.bh
        self.head0 = (bx + off, by - bh / 2 - self.r * 0.62)
        self.neck0 = (bx + off * 0.6, by - bh / 2 + 10)
        self.sL0, self.sR0 = (bx - self.bw_t * 0.38, by - bh * 0.30), (bx + self.bw_t * 0.40, by - bh * 0.28)
        self.hipL0, self.hipR0 = (bx - self.bw_b * 0.17, by + bh * 0.38), (bx + self.bw_b * 0.19, by + bh * 0.38)
        self.hipC = (bx, by + bh * 0.38)
        self.lim, self.arm = spec.get("limb", 30), spec.get("arm", 26)
        self.A = 400 * bh / 580                                     # arm reach (long thin arms)
        self.l_up = self.l_fore = self.A * 0.53
        self.l_th = self.l_sh = (self.feet_y - self.hipL0[1]) * 0.53
        self.footL0, self.footR0 = (self.hipL0[0] - 16, self.feet_y), (self.hipR0[0] + 20, self.feet_y - 7)
        self.seed = random.Random(spec.get("name", "x")).random() * 10
        self._body = self._make_body(); self._heads = {}; self._hand = self._make_hand(); self._flag = None
        self.blink_times = self._blinks()

    # ---------------- sprites
    def _make_body(self):
        c = Canvas(1000, 1800, ss=4, seed=7, light=(-0.75, -0.65)); c.no_pattern = self.spec.get("detail") == "low"
        B = self.spec["body"]; col = B["color"]
        pat = B.get("pattern"); pat = pat(self.bx, self.by, self.bw_t, self.bw_b, self.bh) if pat else None
        c.shape(capsule_pts(self.bx, self.by, self.bw_t, self.bw_b, self.bh, rot=B.get("rot", 0.10), seed=4), col, outline=15, shade=0.38,
                shade_col=C._darker(col, 0.35)[:3], pattern=pat, seed=4)
        for ex in B.get("extras", []): ex(c, self.bx, self.by, self.bw_t, self.bw_b, self.bh)
        im = c.im.resize((1000 * S, 1800 * S), Image.LANCZOS)
        return _crop(self.post(im), (self.hipC[0] * S, self.hipC[1] * S))

    def _make_hand(self):
        c = Canvas(120, 120, ss=4); mitt = self.spec.get("hands", (70, 48, 34, 255))
        c.shape(ellipse_pts(60, 60, 33, 35, rot=0.3, seed=3), mitt, outline=7, shade=0.2, seed=3)
        return self.post(c.im.resize((120 * S, 120 * S), Image.LANCZOS))

    def head(self, expr, blink=False):
        key = (expr, blink)
        if key not in self._heads:
            c = Canvas(1100, 1100, ss=3, seed=9, light=(-0.75, -0.65)); c.blink = blink; c.no_pattern = self.spec.get("detail") == "low"
            hx, hy = 550, 560
            C.draw_head(c, self.spec, hx, hy, 1.0, expr, self.spec.get("tilt", -0.08), self.look)
            im = c.im.resize((1100 * S, 1100 * S), Image.LANCZOS)
            piv = ((hx + (self.neck0[0] - self.head0[0])) * S, (hy + (self.neck0[1] - self.head0[1])) * S)
            self._heads[key] = _crop(self.post(im), piv)
        return self._heads[key]

    def flag(self):
        if self._flag is None:
            c = Canvas(420, 300, ss=3); top = (390, 20)
            fl = [(top[0], top[1] + 10), (top[0] - 330, top[1] + 40), (top[0] - 300, top[1] + 150), (top[0] - 330, top[1] + 250), (top[0], top[1] + 220)]
            c.shape(fl, (40, 70, 170, 255), outline=10, var=0.25, shade=0.3, shade_col=(10, 20, 60), seed=77)
            for dx, dy in ((-90, 80), (-220, 95), (-150, 170)):
                for ex, ey, rx, ry in ((0, -14, 9, 18), (-13, 0, 10, 7), (13, 0, 10, 7)):
                    c.dot(top[0] + dx + ex, top[1] + dy + ey, rx, ry, (240, 196, 60, 255))
            self._flag = (self.post(c.im.resize((420 * S, 300 * S), Image.LANCZOS)), (top[0] * S, top[1] * S))
        return self._flag

    def _blinks(self):
        g = random.Random(self.seed); t = g.uniform(0.4, 1.6); out = []
        while t < 120: out.append(t); t += g.uniform(2.4, 4.2)
        return out

    # ---------------- pose
    def pose(self, t, action, pose, dur):
        A, sL, sR, ph = self.A, self.sL0, self.sR0, self.seed
        P = dict(bdx=0.0, bdy=0.0, brot=0.0, bsy=1.0, hrot=0.0, hdx=0.0, hdy=0.0, fly=0.0, sh_up=0.0, finger=False,
                 hL=(sL[0] - 0.18 * A, sL[1] + 0.97 * A), hR=(sR[0] + 0.18 * A, sR[1] + 0.97 * A), fL=self.footL0, fR=self.footR0, liftL=0.0, liftR=0.0)
        # base pose
        base = pose if pose else "stand"
        if base == "hips" or action == "hips":
            P["hL"] = (self.bx - self.bw_b * 0.47, self.by + self.bh * 0.08); P["hR"] = (self.bx + self.bw_b * 0.47, self.by + self.bh * 0.08)
        elif base == "point_up":
            P["hR"] = (sR[0] + 0.66 * A, sR[1] - 0.62 * A); P["finger"] = True
        elif base == "arms_up":
            P["hL"] = (sL[0] - 0.72 * A, sL[1] - 0.62 * A); P["hR"] = (sR[0] + 0.72 * A, sR[1] - 0.62 * A)
        elif base == "shrug":
            P["hL"] = (sL[0] - 0.62 * A, sL[1] + 0.05 * A); P["hR"] = (sR[0] + 0.62 * A, sR[1] + 0.05 * A); P["sh_up"] = 14
        elif base == "hold_sword":
            P["hR"] = (sR[0] + 0.32 * A, sR[1] + 0.72 * A)
        if self.prop == "spear" and base not in ("arms_up", "shrug", "hips"):
            P["hL"] = (sL[0] - 0.44 * A, sL[1] + 0.63 * A)
        # idle life (always)
        P["bsy"] = 1 + 0.012 * math.sin(2 * math.pi * t / 2.4 + ph); P["brot"] = 0.9 * math.sin(2 * math.pi * t / 3.3 + ph)
        P["hrot"] = 2.2 * math.sin(2 * math.pi * t / 2.9 + ph + 1)
        sway = 5 * math.sin(2 * math.pi * t / 2.6 + ph)
        P["hL"] = (P["hL"][0] - sway * 0.3, P["hL"][1] + sway * 0.5); P["hR"] = (P["hR"][0] + sway * 0.3, P["hR"][1] - sway * 0.4)
        a = action or "idle"; w = 2 * math.pi
        if a == "laugh":
            P["brot"] += 4 * math.sin(w * t * 4); P["bdy"] -= 7 * abs(math.sin(w * t * 4)); P["hrot"] = -9 + 4 * math.sin(w * t * 4)
            if base != "arms_up":
                P["hL"] = (self.bx - 0.18 * self.bw_b, self.by + 0.12 * self.bh); P["hR"] = (self.bx + 0.2 * self.bw_b, self.by + 0.14 * self.bh)
            else:
                k = 30 * math.sin(w * t * 3); P["hL"] = (P["hL"][0] - k * 0.3, P["hL"][1] + k); P["hR"] = (P["hR"][0] + k * 0.3, P["hR"][1] - k)
        elif a == "cheer" or a == "pop_final":
            j = abs(math.sin(math.pi * t * 2.2 + ph)); P["fly"] = -55 * j if a == "cheer" else -18 * j
            P["bsy"] *= 1 + 0.05 * math.cos(w * t * 2.2)
            k = 40 * math.sin(w * t * 2.2 + ph)
            P["hL"] = (sL[0] - 0.72 * A - k * 0.4, sL[1] - 0.62 * A + k); P["hR"] = (sR[0] + 0.72 * A + k * 0.4, sR[1] - 0.62 * A - k)
            P["hrot"] += 5 * math.sin(w * t * 2.2)
        elif a == "shake":
            jx = 9 * math.sin(t * 115 + ph); jy = 7 * math.cos(t * 97)
            P["hL"] = (sL[0] - 0.45 * A + jx, sL[1] - 0.58 * A + jy); P["hR"] = (sR[0] + 0.45 * A - jx, sR[1] - 0.58 * A - jy)
            P["bdx"] += 3 * math.sin(t * 80); P["hrot"] += 3 * math.sin(t * 60)
        elif a in ("march", "walk", "run"):
            f = {"march": 2.0, "walk": 1.6, "run": 3.0}[a]; amp = {"march": 46, "walk": 36, "run": 80}[a]
            phi = w * f * t + ph; s_ = math.sin(phi)
            P["liftL"] = amp * max(0, s_); P["liftR"] = amp * max(0, -s_); P["bdy"] -= (12 if a == "run" else 8) * abs(s_)
            sw = (0.32 if a == "run" else 0.22) * A * s_
            P["hL"] = (sL[0] - 0.2 * A, sL[1] + 0.9 * A - sw); P["hR"] = (sR[0] + 0.2 * A, sR[1] + 0.9 * A + sw)
            if self.prop == "spear": P["hL"] = (sL[0] - 0.44 * A, sL[1] + 0.63 * A - sw * 0.3)
            P["brot"] += (3 if a == "run" else 1.5) * s_; P["hrot"] += 2 * s_
        elif a in ("climb", "climb_fast"):
            f = 1.6 if a == "climb" else 2.6; phi = w * f * t + ph; s_ = math.sin(phi)
            P["hL"] = (sL[0] - 0.62 * A, sL[1] - 0.66 * A + 0.22 * A * s_); P["hR"] = (sR[0] + 0.62 * A, sR[1] - 0.66 * A - 0.22 * A * s_)
            P["liftL"] = 60 * max(0, -s_); P["liftR"] = 60 * max(0, s_); P["brot"] += 3 * s_; P["hrot"] = -6 + 2 * s_
        elif a == "dig":
            th = w * 1.5 * t + ph
            hx, hy = self.bx + 0.30 * A * math.cos(th), self.by + 0.25 * self.bh + 0.22 * A * math.sin(th)
            P["hL"] = (hx - 25, hy); P["hR"] = (hx + 25, hy - 10); P["brot"] += 7 * math.sin(th); P["bdy"] += 10 * (1 + math.sin(th))
        elif a == "panic":
            phi = w * 2.6 * t + ph
            P["hL"] = (sL[0] - (0.5 + 0.2 * math.sin(phi * 1.7)) * A, sL[1] - (0.6 + 0.3 * math.sin(phi)) * A)
            P["hR"] = (sR[0] + (0.5 + 0.2 * math.cos(phi * 1.3)) * A, sR[1] - (0.6 + 0.3 * math.cos(phi)) * A)
            P["liftL"] = 45 * max(0, math.sin(phi * 2)); P["liftR"] = 45 * max(0, -math.sin(phi * 2)); P["brot"] += 5 * math.sin(phi * 2); P["hrot"] += 6 * math.sin(phi * 3)
        elif a == "recoil":
            e = min(1, t / 0.28); P["brot"] -= 9 * e; P["bdx"] -= 18 * e
            hx, hy = self.head0
            P["hL"] = (hx - 0.42 * self.r, hy + 0.55 * self.r); P["hR"] = (hx + 0.30 * self.r, hy + 0.65 * self.r)
        elif a == "bounce":
            d = math.exp(-t * 2.0); P["brot"] += 9 * math.sin(t * 6) * (0.4 + d); P["hrot"] += 12 * math.sin(t * 5 + 1) * (0.4 + d)
            P["bsy"] *= 1 + 0.08 * d * math.sin(t * 22)
            P["hL"] = (sL[0] - 0.25 * A + 25 * math.sin(t * 6), sL[1] + 0.95 * A); P["hR"] = (sR[0] + 0.25 * A - 25 * math.sin(t * 6), sR[1] + 0.95 * A)
        elif a == "pop":
            P["hL"] = (sL[0] - 0.55 * A, sL[1] - 0.1 * A); P["hR"] = (sR[0] + 0.55 * A, sR[1] - 0.15 * A)
        elif base == "point_up":                                    # raise the arm at the start of the shot
            e = min(1, t / 0.35); rest = (sR[0] + 0.18 * A, sR[1] + 0.97 * A); tgt = (sR[0] + 0.66 * A, sR[1] - 0.62 * A)
            P["hR"] = (rest[0] + (tgt[0] - rest[0]) * e, rest[1] + (tgt[1] - rest[1]) * e)
        return P

    # ---------------- render
    NO_SPEAR = {"arms_up", "shrug", "hips", "cheer", "climb", "climb_fast", "panic", "pop", "pop_final", "dig", "laugh", "shake"}

    def render(self, t, action="idle", pose="stand", expr="neutral", dur=2.0):
        keep = self.prop
        if self.prop == "spear" and (pose in self.NO_SPEAR or action in self.NO_SPEAR): self.prop = None
        try:
            return self._render(t, action, pose, expr, dur)
        finally:
            self.prop = keep

    def _render(self, t, action, pose, expr, dur):
        P = self.pose(t, action, pose, dur)
        c = Canvas(1000, 1800, ss=S)
        hip = self.hipC; dx, dy = P["bdx"], P["bdy"] + P["fly"]
        T = lambda p: _rot((p[0] + dx, (p[1] - hip[1]) * P["bsy"] + hip[1] + dy), (hip[0] + dx, hip[1] + dy), P["brot"])
        sL = T((self.sL0[0], self.sL0[1] - P["sh_up"])); sR = T((self.sR0[0], self.sR0[1] - P["sh_up"]))
        hipL = (self.hipL0[0] + dx, self.hipL0[1] + dy); hipR = (self.hipR0[0] + dx, self.hipR0[1] + dy)
        neck = T(self.neck0)
        hL = (P["hL"][0] + dx, P["hL"][1] + dy) if P["fly"] or P["bdy"] else P["hL"]; hR = (P["hR"][0] + dx, P["hR"][1] + dy) if P["fly"] or P["bdy"] else P["hR"]
        fy = P["fly"]
        fL = (self.footL0[0], self.footL0[1] - P["liftL"] + fy * 0.9); fR = (self.footR0[0], self.footR0[1] - P["liftR"] + fy * 0.9)
        lim, arm = self.lim, self.arm
        # spear behind
        if self.prop == "spear":
            px = hL[0]; off = hL[1] - (self.sL0[1] + 0.63 * self.A)
            c.limb((px, 175 + off), (px, 900 + off), (px, self.feet_y + 60 + off), 15, 14, (138, 96, 58, 255), outline=5)
            c.shape([(px, 30 + off), (px + 34, 150 + off), (px, 200 + off), (px - 34, 150 + off)], (196, 204, 216, 255), outline=10, var=0.2, shade=0.25, seed=2)
        # back arm
        self._arm(c, sL, hL, 1 if hL[1] > sL[1] else -1, arm)                      # elbows bulge outward
        # legs
        for hp, ft, side in ((hipL, fL, -1), (hipR, fR, 1)):
            kn, end = _ik(hp, ft, self.l_th, self.l_sh, 1 if side < 0 else -1)          # knees bulge outward
            c.limb(hp, _ctrl(hp, kn, end), end, lim, lim * 0.8)
            c.limb(end, (end[0] + side * 32, end[1] + 15), (end[0] + side * 64, end[1] + 11), lim * 0.8, lim * 0.6)
        # body sprite
        bim, bpiv = self._body
        if abs(P["brot"]) > 0.05 or abs(P["bsy"] - 1) > 1e-3:
            bim2 = bim.resize((bim.width, max(1, int(bim.height * P["bsy"]))), Image.BICUBIC) if abs(P["bsy"] - 1) > 1e-3 else bim
            piv = (bpiv[0], bpiv[1] * P["bsy"])
            bim2, piv = self._rot_sprite(bim2, piv, P["brot"])
        else:
            bim2, piv = bim, bpiv
        c.im.alpha_composite(bim2, (int((hip[0] + dx) * S - piv[0]), int((hip[1] + dy) * S - piv[1])))
        # front arm (+ props in the right hand)
        if self.prop == "sword":
            ang = math.atan2(hR[1] - sR[1], hR[0] - sR[0]); tip = (hR[0] + 330 * math.cos(ang - 1.9), hR[1] + 330 * math.sin(ang - 1.9))
            c.limb(hR, ((hR[0] + tip[0]) / 2, (hR[1] + tip[1]) / 2), tip, 22, 10, (205, 212, 222, 255), outline=6)
        if self.prop == "banner":
            top = (hR[0] + 40, hR[1] - 520)
            c.limb((hR[0] - 10, hR[1] + 120), ((hR[0] + top[0]) / 2, (hR[1] + top[1]) / 2), top, 16, 14, (138, 96, 58, 255), outline=5)
            fim, fpiv = self.flag(); wav = 4 * math.sin(t * 7)
            fim2, fp2 = self._rot_sprite(fim, fpiv, wav)
            c.im.alpha_composite(fim2, (int(top[0] * S - fp2[0]), int(top[1] * S - fp2[1])))
        self._arm(c, sR, hR, -1 if hR[1] > sR[1] else 1, arm, finger=P["finger"])
        # head
        blink = any(0 <= t - bt < 0.12 for bt in self.blink_times) and expr not in ("laughing",)
        him, hpiv = self.head(expr, blink)
        him2, hp2 = self._rot_sprite(him, hpiv, P["hrot"] + P["brot"] * 0.6)
        c.im.alpha_composite(him2, (int((neck[0] + P["hdx"]) * S - hp2[0]), int((neck[1] + P["hdy"]) * S - hp2[1])))
        return c.im

    def _arm(self, c, s, h, bend, w, finger=False):
        el, end = _ik(s, h, self.l_up, self.l_fore, bend)
        c.limb(s, _ctrl(s, el, end), end, w, w * 0.77)
        hand = self._hand
        c.im.alpha_composite(hand, (int(end[0] * S - hand.width / 2), int(end[1] * S - hand.height / 2)))
        if finger:
            ang = math.atan2(end[1] - el[1], end[0] - el[0])
            f0 = (end[0] + 22 * math.cos(ang), end[1] + 22 * math.sin(ang)); f1 = (end[0] + 70 * math.cos(ang), end[1] + 70 * math.sin(ang))
            c.limb(f0, ((f0[0] + f1[0]) / 2, (f0[1] + f1[1]) / 2), f1, 20, 16)

    @staticmethod
    def _rot_sprite(im, piv, deg):
        """rotate a sprite clockwise by deg around its pivot; returns (image, new pivot)"""
        if abs(deg) < 0.05: return im, piv
        w, h = im.size; c = (w / 2, h / 2)
        r = im.rotate(-deg, resample=Image.BILINEAR, expand=True)
        c2 = (r.width / 2, r.height / 2); a = math.radians(deg); x, y = piv[0] - c[0], piv[1] - c[1]
        return r, (c2[0] + x * math.cos(a) - y * math.sin(a), c2[1] + x * math.sin(a) + y * math.cos(a))
