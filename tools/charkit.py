"""2D cartoon character kit in the Ricks-like grammar (original designs only):
- near-round white heads with a soft grey shading crescent, no neck, head sits on a soft capsule body
- brush-like outlines of varying thickness
- tiny black dot eyes (optional eyelids), thick angled tapered eyebrows carry the emotion
- tapered curved stick limbs, small hooked feet, small dark mitten hands
- clothes with fabric patterns and shading
Draws at SS x supersampling and downsamples. Coordinates are final pixels."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

INK = (24, 20, 22, 255)
WHITE = (250, 250, 248, 255)


def _norm(x, y):
    L = math.hypot(x, y) or 1.0
    return x / L, y / L


def resample(pts, n):
    """resample a closed polyline to n evenly spaced points"""
    seg = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    total = sum(seg); out = []; i = 0; acc = 0.0
    for k in range(n):
        target = total * k / n
        while acc + seg[i] < target:
            acc += seg[i]; i = (i + 1) % len(pts)
        t = (target - acc) / (seg[i] or 1)
        a, b = pts[i], pts[(i + 1) % len(pts)]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def ellipse_pts(cx, cy, rx, ry, n=240, wobble=0.0, bean=0.0, rot=0.0, seed=1):
    r = random.Random(seed); ph = [r.uniform(0, 6.3) for _ in range(4)]
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1 + wobble * (0.6 * math.sin(2 * t + ph[0]) + math.sin(3 * t + ph[1]) + 0.5 * math.sin(5 * t + ph[2]) + 0.25 * math.sin(7 * t + ph[3])) / 2.35
        x = math.cos(t) * rx * k; y = math.sin(t) * ry * k
        x *= 1 + bean * (y / ry)
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def head_pts(cx, cy, r, squash=0.97, bumps=0.022, rot=0.0, seed=1, n=300):
    """near-round head with small hand-drawn irregularities (low + a little high frequency)"""
    g = random.Random(seed); ph = [g.uniform(0, 6.3) for _ in range(7)]; amp = [1, .8, .55, .35, .25, .18, .12]
    fr = [2, 3, 4, 5, 7, 9, 13]; pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1 + bumps * sum(a * math.sin(f * t + p) for a, f, p in zip(amp, fr, ph)) / 1.6
        x = math.cos(t) * r * k; y = math.sin(t) * r * squash * k
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def shaggy_pts(cx, cy, rx, ry, curls=26, depth=0.08, rot=0.0, seed=1, n=520):
    """hair mass with a curly/spiky scalloped edge"""
    g = random.Random(seed); pts = []
    jit = [g.uniform(0.6, 1.3) for _ in range(curls)]
    for i in range(n):
        t = 2 * math.pi * i / n; u = (t / (2 * math.pi)) * curls; j = int(u) % curls; fr = u - int(u)
        k = 1 + depth * jit[j] * (math.sin(math.pi * fr) ** 0.6 - 0.5)
        x = math.cos(t) * rx * k; y = math.sin(t) * ry * k
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def capsule_pts(cx, cy, w_top, w_bot, h, rot=0.0, wobble=0.015, seed=1, n=260):
    """soft pill/sack body: rounded top of width w_top, rounded bottom of width w_bot"""
    rt, rb = w_top / 2, w_bot / 2; pts = []
    yt = -h / 2 + rt; yb = h / 2 - rb
    for i in range(41):                                   # top arc (left -> right over the top)
        a = math.pi + math.pi * i / 40; pts.append((rt * math.cos(a), yt + rt * math.sin(a)))
    for i in range(41):                                   # bottom arc (right -> left under the bottom)
        a = math.pi * i / 40; pts.append((rb * math.cos(a), yb + rb * math.sin(a)))
    pts = resample(pts, n)
    r = random.Random(seed); ph = [r.uniform(0, 6.3) for _ in range(3)]; out = []
    for i, (x, y) in enumerate(pts):
        t = 2 * math.pi * i / n
        k = 1 + wobble * (math.sin(3 * t + ph[0]) + 0.5 * math.sin(5 * t + ph[1]) + 0.3 * math.sin(9 * t + ph[2]))
        x, y = x * k, y * k
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


def offset(pts, d):
    """offset a closed polygon along vertex normals; d is a list (per vertex) or a number. +d = outward"""
    n = len(pts); cx = sum(p[0] for p in pts) / n; cy = sum(p[1] for p in pts) / n
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        ax, ay = pts[i - 1]; bx, by = pts[(i + 1) % n]
        nx, ny = _norm(by - ay, -(bx - ax)); nx, ny = nx * sgn, ny * sgn
        di = d[i] if isinstance(d, (list, tuple)) else d
        out.append((pts[i][0] + nx * di, pts[i][1] + ny * di))
    return out


class Canvas:
    def __init__(self, w, h, ss=4, seed=1, light=(-0.7, -0.7)):
        self.w, self.h, self.ss = w, h, ss
        self.im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.rng = random.Random(seed); self.light = _norm(*light)

    def P(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def _mask(self, pts):
        m = Image.new("L", self.im.size, 0); ImageDraw.Draw(m).polygon(self.P(pts), fill=255); return m

    # ---- filled shape with brush outline, shading and optional pattern ---------------------------------
    def shape(self, pts, fill, outline=14, var=0.35, shade=0.32, shade_col=(120, 128, 150), pattern=None, seed=None, hi=0.0, light=None, shade_dist=0.16):
        r = random.Random(seed if seed is not None else self.rng.random()); ph = [r.uniform(0, 6.3) for _ in range(3)]
        n = len(pts)
        th = [outline * (1 + var * (0.6 * math.sin(2 * math.pi * i / n * 2 + ph[0]) + 0.4 * math.sin(2 * math.pi * i / n * 5 + ph[1]))) for i in range(n)]
        if outline:
            self.d.polygon(self.P(offset(pts, [t * 0.5 for t in th])), fill=INK)
            inner = offset(pts, [-t * 0.5 for t in th])
        else:
            inner = pts
        mask = self._mask(inner)
        layer = Image.new("RGBA", self.im.size, fill)
        if pattern and not getattr(self, 'no_pattern', False):
            pattern(ImageDraw.Draw(layer), self)
        if shade or hi:
            xs = [p[0] for p in inner]; ys = [p[1] for p in inner]
            size = max(max(xs) - min(xs), max(ys) - min(ys))
            lx, ly = _norm(*light) if light else self.light
            if shade:
                sh = offset(inner, 0); dx, dy = lx * size * shade_dist, ly * size * shade_dist
                lit = self._mask([(x + dx, y + dy) for x, y in sh])
                cres = ImageChops.subtract(mask, lit).filter(ImageFilter.GaussianBlur(size * self.ss * 0.035))
                sl = Image.new("RGBA", self.im.size, (*shade_col, 255)); sl.putalpha(cres.point(lambda v: int(v * shade)))
                layer = Image.alpha_composite(layer, sl)
            if hi:
                cx = (max(xs) + min(xs)) / 2 + lx * size * 0.22; cy = (max(ys) + min(ys)) / 2 + ly * size * 0.22
                hm = self._mask(ellipse_pts(cx, cy, size * 0.12, size * 0.07, rot=math.atan2(ly, lx) + 1.57)).filter(ImageFilter.GaussianBlur(size * self.ss * 0.02))
                hl = Image.new("RGBA", self.im.size, (255, 255, 255, 255)); hl.putalpha(hm.point(lambda v: int(v * hi)))
                layer = Image.alpha_composite(layer, hl)
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
        self.im.alpha_composite(layer)

    # ---- tapered curved stroke (limbs, brows, hair) ------------------------------------------------------
    def limb(self, a, c, b, w0=12, w1=8, fill=INK, outline=0, n=40, profile=None):
        pts = []
        for i in range(n + 1):
            t = i / n
            pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]))
        left, right = [], []
        for i, p in enumerate(pts):
            q0 = pts[max(0, i - 1)]; q1 = pts[min(n, i + 1)]
            nx, ny = _norm(-(q1[1] - q0[1]), q1[0] - q0[0])
            w = (profile(i / n) if profile else (w0 + (w1 - w0) * i / n)) / 2 + outline
            left.append((p[0] + nx * w, p[1] + ny * w)); right.append((p[0] - nx * w, p[1] - ny * w))
        col = INK if outline else fill
        self.d.polygon(self.P(left + right[::-1]), fill=col)
        e0 = profile(0) if profile else w0; e1 = profile(1) if profile else w1
        for p, w in ((pts[0], e0 / 2 + outline), (pts[-1], e1 / 2 + outline)):
            self.dot(p[0], p[1], w, w, col)
        if outline:
            self.limb(a, c, b, w0, w1, fill, 0, n, profile)
        return pts

    def dot(self, x, y, rx, ry=None, fill=INK, rot=0.0):
        ry = ry or rx
        if rot:
            self.d.polygon(self.P(ellipse_pts(x, y, rx, ry, n=60, rot=rot)), fill=fill)
        else:
            s = self.ss; self.d.ellipse([(x - rx) * s, (y - ry) * s, (x + rx) * s, (y + ry) * s], fill=fill)

    def poly(self, pts, fill):
        self.d.polygon(self.P(pts), fill=fill)

    # ---- face helpers ------------------------------------------------------------------------------------
    def eye(self, x, y, size=13, lid=0.0, look=(0, 0), lid_tilt=0.0, skin=WHITE):
        """dot eye; lid 0..1 covers the top part with an eyelid line (smug / tired / suspicious)"""
        ex, ey = x + look[0] * size * 0.25, y + look[1] * size * 0.25
        self.dot(ex, ey, size * 0.8, size)
        if lid > 0:
            ly = y - size + 2 * size * lid
            ang = lid_tilt
            pts = [(x - size * 2, ly - size * 3), (x + size * 2, ly - size * 3), (x + size * 2, ly + math.tan(ang) * size * 2), (x - size * 2, ly - math.tan(ang) * size * 2)]
            self.poly(pts, skin)
            self.limb((x - size * 1.5, ly - math.tan(ang) * size * 1.5), (x, ly), (x + size * 1.5, ly + math.tan(ang) * size * 1.5), size * 0.55, size * 0.4)

    def brow(self, x, y, length=70, angle=0.0, arch=0.0, w=16):
        """thick tapered eyebrow; angle in degrees (+ = inner end down / angry when mirrored), arch = curve up"""
        a = math.radians(angle); dx, dy = math.cos(a) * length / 2, math.sin(a) * length / 2
        self.limb((x - dx, y - dy), (x, y - arch), (x + dx, y + dy), w, w * 0.55)

    def brow2(self, x, y, length=90, angle=0.0, arch=14, w=26, hook=0.0):
        """thick brow, fattest in the middle, tapered ends; hook bends the outer end down"""
        a = math.radians(angle); dx, dy = math.cos(a) * length / 2, math.sin(a) * length / 2
        prof = lambda t: w * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.15)) ** 0.7)
        pts = self.limb((x - dx, y - dy), (x, y - arch), (x + dx, y + dy), w, w, profile=prof)
        if hook:
            e = pts[-1]; self.limb(e, (e[0] + hook * 0.4, e[1] + hook * 0.2), (e[0] + hook * 0.5, e[1] + hook), w * 0.4, w * 0.2)

    def eye_dot(self, x, y, s, look=(0, 0)):
        if getattr(self, "blink", False): return self.eye_arc(x, y, s * 0.9, up=False)
        self.dot(x + look[0] * s * 0.3, y + look[1] * s * 0.3, s * 0.72, s)

    def eye_lid(self, x, y, s, lid=0.45, tilt=0.0, look=(0, 0), skin=WHITE):
        """half-moon eye: black oval cut by a straight eyelid line (smug, suspicious, tired)"""
        if getattr(self, "blink", False): return self.eye_arc(x, y, s * 0.9, up=False)
        self.eye_dot(x, y, s, look)
        ly = y - s + 2 * s * lid; t = math.tan(math.radians(tilt))
        L = s * 1.25
        top = y - s * 1.08 + look[1] * s * 0.3
        self.poly([(x - L * 0.85, top), (x + L * 0.85, top), (x + L * 0.85, ly + t * L * 0.85), (x - L * 0.85, ly - t * L * 0.85)], skin)
        self.limb((x - L, ly - t * L), (x, ly), (x + L, ly + t * L), s * 0.42, s * 0.42)

    def eye_white(self, x, y, s, look=(0, 0), pupil=0.38):
        """wide white eye with a black pupil (shock, surprise, fear)"""
        if getattr(self, "blink", False): return self.eye_arc(x, y, s, up=False)
        self.dot(x, y, s * 0.95 + 6, s * 1.15 + 6, INK); self.dot(x, y, s * 0.95, s * 1.15, WHITE)
        self.dot(x + look[0] * s * 0.45, y + look[1] * s * 0.55, s * pupil, s * pupil * 1.15)

    def eye_arc(self, x, y, s, up=True):
        """closed eye: happy arch (up) or relaxed line (up=False)"""
        h = -s * 0.7 if up else s * 0.15
        self.limb((x - s, y + s * 0.2), (x, y + h * 2), (x + s, y + s * 0.2), s * 0.42, s * 0.42)

    def mouth_o(self, x, y, s, tongue=(232, 120, 140, 255)):
        pts = ellipse_pts(x, y, s * 0.75, s, wobble=0.05, seed=9)
        self.shape(pts, (110, 34, 44, 255), outline=s * 0.32, shade=0, var=0.2, seed=9)
        self.dot(x + s * 0.05, y + s * 0.45, s * 0.42, s * 0.3, tongue)

    def mouth_open(self, x, y, w, h, teeth=True, smile=0.25, tongue=(232, 120, 140, 255)):
        """D-shaped open mouth: laugh (smile>0) or yell (smile<0)"""
        n = 40; top = []; bot = []
        for i in range(n + 1):
            t = i / n; xx = x - w / 2 + w * t
            top.append((xx, y - smile * h * math.sin(math.pi * t) * 0.6 * (-1)))
            bot.append((xx, y + h * math.sin(math.pi * t) ** 0.8 - smile * h * 0.2))
        pts = top + bot[::-1][1:-1]
        self.shape(pts, (100, 28, 38, 255), outline=max(6, w * 0.07), shade=0, var=0.2, seed=8)
        if teeth:
            self.poly([(x - w * 0.36, y + h * 0.04), (x + w * 0.36, y + h * 0.04), (x + w * 0.3, y + h * 0.2), (x - w * 0.3, y + h * 0.2)], (250, 250, 245, 255))
        self.dot(x, y + h * 0.72, w * 0.22, h * 0.18, tongue)

    def mouth_line(self, x, y, w, curve=0.0, tilt=0.0, thick=12):
        """curve>0 frown, curve<0 smile, tilt for smirk"""
        self.limb((x - w / 2, y + tilt), (x, y - curve), (x + w / 2, y - tilt), thick, thick * 0.8)

    def mouth_squiggle(self, x, y, w, amp=8, waves=3, thick=11):
        n = waves * 2; seg = w / n; px = x - w / 2
        for i in range(n):
            a = (px + seg * i, y); b = (px + seg * (i + 1), y); c = (px + seg * (i + 0.5), y + (amp if i % 2 else -amp) * 2)
            self.limb(a, c, b, thick, thick)

    def sweat(self, x, y, s):
        pts = [(x, y - s * 1.4)] + [(x + math.cos(t) * s * 0.7, y + math.sin(t) * s * 0.7) for t in [i / 20 * math.pi for i in range(-2, 23)]]
        self.shape(pts, (170, 215, 245, 255), outline=s * 0.25, shade=0.2, seed=4, hi=0.6)

    def save(self, path):
        self.im.resize((self.w, self.h), Image.LANCZOS).save(path)
        return path
