"""2D cartoon character drawing kit (Ricks-like look): wavy bean heads, thick black outlines,
flat colours, stick limbs. Draws at SS x supersampling and downsamples, output RGBA PNG.
All coordinates are in final pixels; helpers scale them."""
import math, random
from PIL import Image, ImageDraw

INK = (22, 18, 20, 255)


class Canvas:
    def __init__(self, w, h, ss=4, seed=1):
        self.w, self.h, self.ss = w, h, ss
        self.im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.rng = random.Random(seed)

    def P(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    # ---- primitives -------------------------------------------------------
    def blob(self, cx, cy, rx, ry, fill, outline=14, wobble=0.03, bean=0.0, rot=0.0, n=220, seed=None):
        """Irregular closed shape: ellipse with low-frequency radial wobble; bean>0 widens the bottom."""
        r = random.Random(seed if seed is not None else self.rng.random())
        ph = [r.uniform(0, 6.28) for _ in range(4)]
        def pts(extra):
            out = []
            for i in range(n):
                t = 2 * math.pi * i / n
                k = 1 + wobble * (math.sin(2 * t + ph[0]) * .6 + math.sin(3 * t + ph[1]) + .5 * math.sin(5 * t + ph[2]) + .25 * math.sin(7 * t + ph[3])) / 2.35
                x = math.cos(t) * rx * k; y = math.sin(t) * ry * k
                x *= 1 + bean * (y / ry)
                xr = x * math.cos(rot) - y * math.sin(rot); yr = x * math.sin(rot) + y * math.cos(rot)
                L = math.hypot(xr, yr) or 1
                out.append((cx + xr + xr / L * extra, cy + yr + yr / L * extra))
            return out
        if outline:
            self.d.polygon(self.P(pts(outline / 2)), fill=INK)
        self.d.polygon(self.P(pts(-outline / 2 if outline else 0)), fill=fill)

    def poly(self, pts, fill, outline=12):
        if outline:
            self.d.polygon(self.P(pts), fill=INK)
            # inset by shrinking toward centroid (good enough for convex-ish shapes)
            cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
            ins = []
            for x, y in pts:
                dx, dy = x - cx, y - cy; L = math.hypot(dx, dy) or 1
                ins.append((x - dx / L * outline, y - dy / L * outline))
            self.d.polygon(self.P(ins), fill=fill)
        else:
            self.d.polygon(self.P(pts), fill=fill)

    def line(self, pts, width=10, fill=INK):
        p = self.P(pts); w = int(width * self.ss)
        self.d.line(p, fill=fill, width=w, joint="curve")
        for x, y in (p[0], p[-1]):
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fill)

    def stroke(self, pts, width, color, outline=6):
        """coloured stick with black outline (spear shaft, etc.)"""
        self.line(pts, width + 2 * outline, INK); self.line(pts, width, color)

    def dot(self, x, y, rx, ry=None, fill=INK):
        ry = ry or rx; s = self.ss
        self.d.ellipse([(x - rx) * s, (y - ry) * s, (x + rx) * s, (y + ry) * s], fill=fill)

    def arc(self, box, a0, a1, width=10, fill=INK):
        s = self.ss
        self.d.arc([v * s for v in box], a0, a1, fill=fill, width=int(width * s))

    def save(self, path):
        self.im.resize((self.w, self.h), Image.LANCZOS).save(path)
        return path
