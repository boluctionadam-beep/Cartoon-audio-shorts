#!/usr/bin/env python3
"""2.5D compositor: background stills (Blender, overscan) + animated 2D character cards + FX -> per-shot video segments,
then joined with 0.25 s dissolves.
  python3 compose.py PROJECT_DIR [--w 1440 --h 2560 --fps 60 --shots s01,s02 --jobs 4 --out out/picture.mp4]
Reads PROJECT/work/timeline.json and PROJECT/renders/shots/<id>.png/.json"""
import argparse, json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RIG_ACTIONS = {"idle", "laugh", "cheer", "shake", "march", "walk", "run", "climb", "climb_fast", "dig", "panic", "recoil", "bounce", "pop", "pop_final"}
_SPECS = {}


def _specs(proj):
    """cast specs of the project (projects/<id>/cast.py SPECS)"""
    if proj not in _SPECS:
        import importlib.util
        p = os.path.join(proj, "cast.py")
        if os.path.exists(p):
            sp = importlib.util.spec_from_file_location("projcast_" + str(abs(hash(proj))), p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
            _SPECS[proj] = m.SPECS
        else:
            _SPECS[proj] = {}
    return _SPECS[proj]


TINT = {"golden": (1.0, 0.93, 0.80), "day": (1.0, 0.99, 0.96), "dusk": (1.0, 0.84, 0.72), "dawn": (1.0, 0.90, 0.82),
        "night": (0.60, 0.68, 0.95), "interior": (1.0, 0.90, 0.76)}


# ------------------------------------------------------------------ helpers
def ease(t):
    t = min(1, max(0, t)); return 0.5 - 0.5 * math.cos(math.pi * t)


def out_back(t, s=1.7):
    t = min(1, max(0, t)) - 1; return t * t * ((s + 1) * t + s) + 1


def grade_np(x, sat=1.22, contrast=0.2, warm=0.6):
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    x = lum + (x - lum) * sat; x = np.clip(x, 0, 1)
    x = x + contrast * (x - 0.5) * (1 - np.abs(2 * x - 1))
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    hi = np.array([1.05, 1.0, 0.90], np.float32); lo = np.array([0.93, 0.97, 1.06], np.float32)
    return np.clip(x * (lo + (hi - lo) * lum) ** warm, 0, 1)


def grade_bg(im):
    x = np.asarray(im.convert("RGB")).astype(np.float32) / 255; x = grade_np(x)
    bright = np.clip((x - 0.72) / 0.28, 0, 1) * x
    b = np.asarray(Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(x.shape[1] / 60))).astype(np.float32) / 255
    x = 1 - (1 - x) * (1 - b * 0.35)
    return Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8))


def grade_card(im, tint):
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    rgb = grade_np(a[..., :3], sat=1.12, contrast=0.12, warm=0.4) * np.array(tint, np.float32)
    return Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a[..., 3:]]) * 255 + 0.5).astype(np.uint8), "RGBA")


def persp_coeffs(src, dst):
    """coefficients mapping output (dst) pixel -> input (src) pixel for Image.transform PERSPECTIVE"""
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


# ------------------------------------------------------------------ sprites
def sprites(scale):
    from charkit import Canvas, ellipse_pts
    S = {}
    c = Canvas(160, 160, ss=3); c.shape(ellipse_pts(80, 84, 58, 52, wobble=0.1, seed=3), (140, 140, 150, 255), outline=9, shade=0.4, seed=3, hi=0.3); S["boulder"] = c.im.resize((160, 160), Image.LANCZOS)
    c = Canvas(140, 150, ss=3)
    for i, (y, rx) in enumerate(((112, 56), (82, 44), (56, 30))):
        c.shape(ellipse_pts(70, y, rx, 22, wobble=0.06, seed=10 + i), (110, 70, 30, 255), outline=8, shade=0.35, shade_col=(40, 20, 5), seed=10 + i)
    c.limb((70, 40), (82, 22), (92, 16), 12, 6, (110, 70, 30, 255), outline=4); S["blob"] = c.im.resize((140, 150), Image.LANCZOS)
    def arrow(col):
        c = Canvas(260, 420, ss=3)
        c.shape([(130, 410), (10, 250), (80, 250), (80, 10), (180, 10), (180, 250), (250, 250)], col, outline=14, var=0.2, shade=0.3, seed=5)
        return c.im.resize((260, 420), Image.LANCZOS)
    S["arrow_down"] = arrow((220, 60, 50, 255)); S["arrow_up"] = arrow((70, 180, 80, 255)).transpose(Image.FLIP_TOP_BOTTOM)
    c = Canvas(40, 30, ss=4); c.dot(20, 17, 7, 6, (20, 20, 20, 255)); c.dot(13, 9, 7, 5, (230, 235, 245, 180)); c.dot(27, 9, 7, 5, (230, 235, 245, 180)); S["fly"] = c.im.resize((40, 30), Image.LANCZOS)
    for k in list(S):
        im = S[k]; S[k] = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    return S


# ------------------------------------------------------------------ one shot -> frames
class Shot:
    def __init__(self, proj, sh, W, H, fps, words):
        self.sh, self.W, self.H, self.fps = sh, W, H, fps
        sd = os.environ.get("SHOT_DIR", os.path.join(proj, "renders/shots"))
        meta = json.load(open(os.path.join(sd, sh["id"] + ".json")))
        bg = Image.open(os.path.join(sd, sh["id"] + ".png")).convert("RGB")
        self.os_ = meta["overscan"]; Wo, Ho = meta["size"]
        k = (W * self.os_) / Wo                                      # rescale everything to output scale
        self.bg = grade_bg(bg.resize((int(Wo * k), int(Ho * k)), Image.LANCZOS)) if abs(k - 1) > 1e-3 else grade_bg(bg)
        self.Wo, self.Ho = self.bg.size
        self.points = {n: (p[0] * k, p[1] * k) for n, p in meta["points"].items()}
        tint = TINT.get(sh.get("light") or "interior", TINT["interior"])
        self.cards = []
        chars = {c["n"]: c for c in sh.get("chars", [])}
        for cd in meta["cards"]:
            if cd["baked"]: continue
            quad = [(p[0] * k, p[1] * k) for p in cd["quad"]]
            name = cd["name"]; c = chars.get(name)
            imgs = {}
            base = Image.open(cd["img"]).convert("RGBA")
            rig = None
            if c and c.get("rig", True) and not cd["baked"] and _specs(proj).get(c["n"]):
                from rig import Rig
                rig = Rig(_specs(proj)[c["n"]], look=tuple(c.get("look", (0, 0))), post=lambda im, _t=tint: grade_card(im, _t), prop=c.get("prop") or _specs(proj)[c["n"]].get("prop"))
            if c:
                imgs[c["e"]] = grade_card(base, tint)
                for sw in sh.get("swaps", []):
                    if sw["n"] == name:
                        p = cd["img"].replace(f"_{c['e']}_", f"_{sw['e']}_", 1)
                        if os.path.exists(p): imgs[sw["e"]] = grade_card(Image.open(p).convert("RGBA"), tint)
                anim = c.get("anim", "idle"); clip = c.get("clip"); first = c["e"]
            else:
                imgs["x"] = grade_card(base, tint); anim = sh.get("crowd_anim") or "idle"; clip = None; first = "x"
            self.cards.append(dict(name=name, quad=quad, imgs=imgs, first=first, anim=anim, clip=clip, dist=cd["dist"],
                                   hero=bool(c), seed=random.Random(name).random() * 10, rig=rig, pose=c["p"] if c else None))
        self.cards.sort(key=lambda c: -c["dist"])                     # far to near
        self.swaps = [(sw["t"] - sh["t0"], sw["n"], sw["e"]) for sw in sh.get("swaps", []) if sw["t"] is not None]
        self.dur = sh["t1"] - sh["t0"]
        self.S = sprites(W / 1440)
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
        self.vig = (1 - 0.32 * np.clip(r - 0.35, 0, 1) ** 1.5 / 0.65 ** 1.5)[..., None].astype(np.float32)
        self.fx = sh.get("fx", [])
        self.rng = random.Random(sh["id"])

    # camera window in overscan pixels
    def window(self, u):
        mv, amt = self.sh["move"], self.sh["amt"]; Wn, Hn = self.Wo / self.os_, self.Ho / self.os_
        cx, cy = self.Wo / 2, self.Ho / 2; e = ease(u)
        if mv == "in": z = 1 + amt * e
        elif mv == "out": z = 1 + amt * (1 - e)
        else: z = 1 + amt * 0.6
        w, h = Wn / z, Hn / z
        if mv == "up": cy += (self.Ho - h) / 2 * (1 - 2 * e) * 0.9
        if mv == "down": cy -= (self.Ho - h) / 2 * (1 - 2 * e) * 0.9
        # camera shake
        sx = sy = 0.0
        t = u * self.dur
        for f in self.fx:
            if f["t"] == "shake":
                ts = f.get("time", self.sh["t0"] + f.get("at", 0.5) * self.dur) - self.sh["t0"]
                if 0 <= t - ts < 0.45:
                    a = (1 - (t - ts) / 0.45) * 0.012 * Hn
                    sx += a * math.sin(t * 93); sy += a * math.cos(t * 71)
        return cx + sx, cy + sy, w, h

    def frame(self, i):
        t = i / self.fps; u = t / self.dur; W, H = self.W, self.H
        cx, cy, w, h = self.window(u)
        x0, y0 = cx - w / 2, cy - h / 2; s = W / w
        img = self.bg.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BILINEAR).convert("RGBA")
        to = lambda p: ((p[0] - x0) * s, (p[1] - y0) * s)
        for c in self.cards:
            self.draw_card(img, c, t, to)
        self.draw_fx(img, t, to, s)
        x = np.asarray(img.convert("RGB")).astype(np.float32) * self.vig
        for f in self.fx:
            if f["t"] == "flash" and f.get("time") is not None:
                d = (self.sh["t0"] + t) - f["time"]
                if 0 <= d < 0.35: x = x + (255 - x) * (1 - d / 0.35) * 0.85
        return np.clip(x, 0, 255).astype(np.uint8)

    def card_img(self, c, t):
        e = c["first"]
        for ts, n, ex in self.swaps:
            if n == c["name"] and t >= ts: e = ex
        if c.get("rig") is not None:
            act = c["anim"] if c["anim"] in RIG_ACTIONS else "idle"
            return c["rig"].render(t, act, c["pose"], e, self.dur)
        return c["imgs"].get(e, c["imgs"][c["first"]])

    def anim(self, c, t):
        if c.get("rig") is not None:
            a = c["anim"]; dx = dy = 0.0; sx = sy = 1.0
            if a == "climb": dy -= 0.16 * (t / self.dur)
            elif a == "climb_fast": dy -= 2.6 * ease(t / self.dur * 1.1)
            elif a == "pop": dy += 0.75 * (1 - out_back(t / 0.42))
            elif a == "pop_final": dy += 0.95 * (1 - out_back((t - 0.15) / 0.5))
            elif a == "march": dx += 0.05 * t
            elif a == "run": sx = sy = 1 + 0.12 * t
            elif a == "panic": dx += 0.04 * math.sin(2 * math.pi * t * 1.2 + c["seed"])
            return sx, sy, 0.0, dx, dy
        a = c["anim"]; ph = c["seed"]; sx = sy = 1.0; rot = 0.0; dx = dy = 0.0
        sy *= 1 + 0.012 * math.sin(2 * math.pi * t / 2.2 + ph); rot += 0.8 * math.sin(2 * math.pi * t / 3.1 + ph)
        if a == "shake": dx += 0.006 * math.sin(t * 120 + ph); rot += 1.2 * math.sin(t * 40)
        elif a in ("laugh",): dy -= 0.02 * abs(math.sin(2 * math.pi * t * 3 + ph)); rot += 2.5 * math.sin(2 * math.pi * t * 1.5)
        elif a == "cheer": dy -= 0.07 * abs(math.sin(2 * math.pi * t * 2.2 + ph)); sy *= 1 + 0.04 * math.sin(2 * math.pi * t * 4.4 + ph)
        elif a == "march": dy -= 0.03 * abs(math.sin(2 * math.pi * t * 2.0 + ph)); dx += 0.05 * t; rot += 2 * math.sin(2 * math.pi * t * 2 + ph)
        elif a == "run": dy -= 0.05 * abs(math.sin(2 * math.pi * t * 3 + ph)); rot += 4 * math.sin(2 * math.pi * t * 3 + ph); sx = sy = sy * (1 + 0.12 * t)
        elif a == "dig": rot += 7 * math.sin(2 * math.pi * t * 2.6 + ph); dy -= 0.025 * abs(math.sin(2 * math.pi * t * 2.6 + ph))
        elif a == "panic": dx += 0.05 * math.sin(2 * math.pi * t * 2.5 + ph); dy -= 0.04 * abs(math.sin(2 * math.pi * t * 5 + ph)); rot += 5 * math.sin(2 * math.pi * t * 5 + ph)
        elif a == "climb": dy -= 0.16 * (t / self.dur) + 0.02 * abs(math.sin(2 * math.pi * t * 2.2 + ph)); rot += 3 * math.sin(2 * math.pi * t * 2.2 + ph)
        elif a == "climb_fast": dy -= 2.6 * ease(t / self.dur * 1.1) + 0.03 * abs(math.sin(2 * math.pi * t * 3 + ph)); rot += 4 * math.sin(2 * math.pi * t * 3 + ph)
        elif a == "pop": dy += 0.75 * (1 - out_back(t / 0.42))
        elif a == "pop_final":
            dy += 0.95 * (1 - out_back((t - 0.15) / 0.5)); dy -= 0.04 * abs(math.sin(2 * math.pi * t * 2.5)) * (t > 0.7)
        elif a == "recoil": rot -= 6 * ease(t / 0.3); dy -= 0.02 * ease(t / 0.3); sx *= 1 - 0.04 * ease(t / 0.3)
        elif a == "bounce": d = math.exp(-t * 2.2); sy *= 1 + 0.10 * d * math.sin(t * 22); sx *= 1 - 0.06 * d * math.sin(t * 22); rot += 6 * math.sin(t * 5) * (0.4 + d)
        for ts, n, ex in self.swaps:                                  # small squash-pop on an expression change
            if n == c["name"] and 0 <= t - ts < 0.18:
                k = math.sin(math.pi * (t - ts) / 0.18); sy *= 1 + 0.05 * k; sx *= 1 - 0.03 * k
        return sx, sy, rot, dx, dy

    def draw_card(self, img, c, t, to):
        q = [to(p) for p in c["quad"]]                                 # tl, tr, br, bl in output px
        hpx = math.dist(((q[0][0] + q[1][0]) / 2, (q[0][1] + q[1][1]) / 2), ((q[2][0] + q[3][0]) / 2, (q[2][1] + q[3][1]) / 2))
        feet = 210 / 1800
        bx = (q[2][0] + q[3][0]) / 2; by = (q[2][1] + q[3][1]) / 2 - feet * hpx   # pivot at the feet line
        sx, sy, rot, dx, dy = self.anim(c, t); r = math.radians(rot)
        dst = []
        for x, y in q:
            u, v = (x - bx) * sx, (y - by) * sy
            dst.append((bx + u * math.cos(r) - v * math.sin(r) + dx * hpx, by + u * math.sin(r) + v * math.cos(r) + dy * hpx))
        xs = [p[0] for p in dst]; ys = [p[1] for p in dst]
        X0, Y0, X1, Y1 = int(max(0, min(xs) - 2)), int(max(0, min(ys) - 2)), int(min(self.W, max(xs) + 2)), int(min(self.H, max(ys) + 2))
        if X1 <= X0 or Y1 <= Y0: return
        im = self.card_img(c, t); cw, ch = im.size
        src = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
        coeffs = persp_coeffs(src, [(x - X0, y - Y0) for x, y in dst])
        layer = im.transform((X1 - X0, Y1 - Y0), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
        if not c["hero"] and c["dist"] > 8:
            layer = layer.filter(ImageFilter.GaussianBlur(min(3, (c["dist"] - 8) / 25 + 0.8) * self.W / 1440))
        if c["clip"] and c["clip"] in self.points:
            cy_ = to(self.points[c["clip"]])[1] - Y0
            if cy_ < layer.height:
                a = layer.getchannel("A"); d = ImageDraw.Draw(a); d.rectangle([0, max(0, cy_), layer.width, layer.height], fill=0); layer.putalpha(a)
        img.alpha_composite(layer, (X0, Y0))

    def draw_fx(self, img, t, to, s):
        u = t / self.dur; S = self.S; W, H = self.W, self.H
        for f in self.fx:
            k = f["t"]
            if k == "flies" and f.get("pt") in self.points:
                px, py = to(self.points[f["pt"]])
                for j in range(6):
                    a = t * (2.3 + j * 0.37) + j * 1.7; rr = (40 + 22 * j) * W / 1440
                    x = px + rr * math.cos(a) + 12 * math.sin(t * 31 + j); y = py + 0.6 * rr * math.sin(a * 1.3) + 10 * math.cos(t * 27 + j)
                    img.alpha_composite(S["fly"], (int(x), int(y)))
            elif k == "dust":
                rg = random.Random(3)
                for j in range(14):
                    x = rg.uniform(0.05, 0.95) * W; y = f.get("y", 0.8) * H + rg.uniform(-0.05, 0.05) * H
                    ph = (u * 2 + j * 0.13) % 1.0; rad = (20 + 120 * ph) * W / 1440; al = int(140 * (1 - ph))
                    d = Image.new("RGBA", (int(rad * 2) + 2,) * 2, (0, 0, 0, 0)); ImageDraw.Draw(d).ellipse([0, 0, rad * 2, rad * 2], fill=(205, 185, 150, al))
                    img.alpha_composite(d.filter(ImageFilter.GaussianBlur(rad * 0.25)), (int(x - rad), int(y - rad - ph * 60)))
            elif k == "boulder" and f["a"] in self.points and f["b"] in self.points:
                A, B = to(self.points[f["a"]]), to(self.points[f["b"]])
                v = (u - 0.12) / 0.45
                if 0 <= v <= 1:
                    x = A[0] + (B[0] - A[0]) * v; y = A[1] + (B[1] - A[1]) * v - math.sin(math.pi * v) * 0.25 * H
                    sp = S["boulder"].rotate(-v * 720, resample=Image.BICUBIC); sz = int(sp.width * (1.2 - 0.6 * v)); sp = sp.resize((sz, sz))
                    img.alpha_composite(sp, (int(x - sz / 2), int(y - sz / 2)))
                if v > 1:
                    ph = min(1, (v - 1) * 1.2); rad = (40 + 220 * ph) * W / 1440; al = int(220 * (1 - ph))
                    d = Image.new("RGBA", (int(rad * 2) + 2,) * 2, (0, 0, 0, 0)); ImageDraw.Draw(d).ellipse([0, 0, rad * 2, rad * 2], fill=(200, 180, 150, al))
                    img.alpha_composite(d.filter(ImageFilter.GaussianBlur(rad * 0.2)), (int(B[0] - rad), int(B[1] - rad)))
            elif k == "blob" and all(p in self.points for p in (f["a"], f["b"], f["c"])):
                A, B, C = (to(self.points[f[p]]) for p in ("a", "b", "c"))
                v = (u - 0.08) / 0.6
                if 0 <= v <= 1:
                    if v < 0.7: w_ = (v / 0.7) ** 1.6; x = A[0] + (B[0] - A[0]) * w_; y = A[1] + (B[1] - A[1]) * w_
                    else: w_ = (v - 0.7) / 0.3; x = B[0] + (C[0] - B[0]) * w_; y = B[1] + (C[1] - B[1]) * w_ - math.sin(math.pi * w_) * 0.05 * H
                    sp = S["blob"]; img.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
            elif k == "splash" and f.get("pt") in self.points:
                P = to(self.points[f["pt"]]); v = (u - f.get("at", 0.8)) / 0.35
                if 0 <= v <= 1:
                    rg = random.Random(5)
                    for j in range(14):
                        a = rg.uniform(math.pi * 1.05, math.pi * 1.95); sp = rg.uniform(120, 300) * W / 1440
                        x = P[0] + math.cos(a) * sp * v; y = P[1] + math.sin(a) * sp * v + 400 * v * v * W / 1440; rad = 12 * (1 - v * 0.5) * W / 1440
                        ImageDraw.Draw(img).ellipse([x - rad, y - rad, x + rad, y + rad], fill=(120, 190, 230, int(255 * (1 - v))))
            elif k == "arrow" and f.get("pt") in self.points:
                P = to(self.points[f["pt"]]); sp = S["arrow_down" if f["dir"] == "down" else "arrow_up"]
                pop = out_back(min(1, u / 0.15)); bob = 18 * math.sin(t * 6) * W / 1440
                if pop > 0.01:
                    sp2 = sp.resize((max(1, int(sp.width * pop)), max(1, int(sp.height * pop))))
                    img.alpha_composite(sp2, (int(P[0] + 0.16 * W - sp2.width / 2), int(P[1] - sp2.height / 2 + bob)))


def render_segment(args):
    proj, sh, W, H, fps, out, words = args
    if os.environ.get("REUSE") and os.path.exists(out) and sh["id"] not in os.environ.get("REDO", "").split(","):
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
        return out, round(d * fps) / fps
    S = Shot(proj, sh, W, H, fps, words); n = int(round(S.dur * fps))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(S.frame(i).tobytes())
    p.stdin.close(); p.wait()
    return out, n / fps


def join(segs, out, xf=0.25, fps=60):
    args = []; [args.extend(["-i", s]) for s, _ in segs]
    fc = []; cur = "[0:v]"; t = segs[0][1]
    for k in range(1, len(segs)):
        off = t - xf; o = f"[v{k}]"
        fc.append(f"{cur}[{k}:v]xfade=transition=fade:duration={xf}:offset={off:.4f}{o}"); cur = o; t = off + segs[k][1]
    cmd = ["ffmpeg", "-v", "error", "-y", *args]
    if len(segs) > 1: cmd += ["-filter_complex", ";".join(fc), "-map", cur]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-r", str(fps), out]
    subprocess.run(cmd, check=True); return t


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("proj"); ap.add_argument("--w", type=int, default=1440); ap.add_argument("--h", type=int, default=2560)
    ap.add_argument("--fps", type=int, default=60); ap.add_argument("--shots"); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default="out/picture.mp4"); ap.add_argument("--segdir", default="work/segs")
    a = ap.parse_args()
    TL = json.load(open(os.path.join(a.proj, "work/timeline.json"))); words = json.load(open(os.path.join(a.proj, "work/words.json")))
    if a.shots: TL = [s for s in TL if s["id"] in a.shots.split(",")]
    sd = os.path.join(a.proj, a.segdir); os.makedirs(sd, exist_ok=True); os.makedirs(os.path.dirname(os.path.join(a.proj, a.out)), exist_ok=True)
    jobs = [(a.proj, sh, a.w, a.h, a.fps, os.path.join(sd, f"{sh['id']}_{a.w}.mp4"), words) for sh in TL]
    from multiprocessing import Pool
    with Pool(a.jobs) as pool:
        segs = pool.map(render_segment, jobs)
    total = join(segs, os.path.join(a.proj, a.out), fps=a.fps)
    print(f"picture {total:.2f}s -> {a.out}")
