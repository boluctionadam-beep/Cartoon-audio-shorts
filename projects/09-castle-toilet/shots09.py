"""Shot list for short 09 — single source of truth (PLAN.md and timeline.json are generated from it).
  python3 shots09.py cards                 pre-render every character card the shots need
  python3 shots09.py plan                  write PLAN.md + work/timeline.json
  python3 shots09.py render ID [W H SPP]   build the 3D set for shot ID and render the background still (+ json)
"""
import os, sys, json, re, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "../../tools"))

FR = [(120, 130, 170, 255), (150, 110, 80, 255), (110, 120, 100, 255), (160, 150, 120, 255)]   # French extras (muted)
EN = [(150, 70, 70, 255), (120, 110, 100, 255), (100, 104, 112, 255), (140, 120, 90, 255)]     # English defenders
WALL_HERO = (-0.25, -4.5, 0.0)

# char: n=name e=expr p=pose look=(x,y) at=(x,y,z) h=card height, anim, swaps=[(word snippet, expr)], clip=point, travel=(dx,dy) frac of frame
SHOTS = [
 dict(id="s01", at="He climbed", set="cut2", opt=dict(light="night"), move="up", amt=0.10,
      cam=dict(loc=(0.4, -6.5, 7.6), target=(0, 1, 6.4), lens=30),
      chars=[dict(n="bogis", e="determined", p="arms_up", look=(0.2, -1), at=(0, 0.9, 4.9), anim="climb")],
      fx=[], sfx=["scrape", "drip"], note="HOOK: Bogis inside the toilet chute, climbing up, determined. Night, torchlight from above."),
 dict(id="s02", at="From the bottom", set="wall3", opt=dict(light="night", grass=False), move="in", amt=0.10,
      cam=dict(loc=(1.0, -1.2, 3.2), target=(2.0, 3.2, 7.4), lens=24),
      chars=[dict(n="bogis", e="determined", p="arms_up", at=(2.0, 2.85, 6.35), baked=True)],
      fx=[dict(t="flies", pt="hole")], sfx=["scrape"], note="Low angle: Bogis's legs dangling out of the toilet hole in the wall."),
 dict(id="s03", at="This was", set="world2", opt=dict(light="golden"), move="out", amt=0.10,
      cam=dict(loc=(-118, -128, 58), target=(16, 10, 2), lens=34), chars=[], sfx=["wind", "birds"], note="Aerial: Château Gaillard on its cliff above the Seine."),
 dict(id="s04", at="the toughest", set="world2", opt=dict(light="golden"), move="in", amt=0.08,
      cam=dict(loc=(-50, -52, None), target=(0, 0, 16), lens=22, dz=1.8), chars=[], sfx=["whoosh"], note="Low angle up at walls, towers and the keep."),
 dict(id="s05", at="Richard the", set="world2", opt=dict(light="golden", scaffold=True, flags=None), move="out", amt=0.10,
      cam=dict(loc=(-58, -50, None), target=(-25, -12, 6), lens=24, dz=1.7, dof="richard", fstop=2.8),
      chars=[dict(n="richard", e="smug", p="hips", look=(0.6, 0), at=(-52.5, -45.5, None), swaps=[("two years", "laughing")])],
      sign=dict(text="1196 → 1198", at=(-49.6, -44.6), w=1.6, h=0.8, yaw=-35), sfx=["hammer", "hammer"],
      note="Richard, hands on hips, proud in front of the castle under construction; sign 1196 → 1198."),
 dict(id="s06", at="Three rings", set="world2", opt=dict(light="golden"), move="in", amt=0.10,
      cam=dict(loc=(-20, -70, 120), target=(0, 0, 0), lens=30), chars=[], sfx=["whoosh"], note="Top-down: three rings of walls + the moat."),
 dict(id="s07", at="towers everywhere", set="world2", opt=dict(light="golden"), move="up", amt=0.08,
      cam=dict(loc=(-50, -44, 20), target=(0, 2, 13), lens=26), chars=[], sfx=["whoosh"], note="Worm's-eye: towers everywhere."),
 dict(id="s08", at="The French king", set="world2", opt=dict(light="dusk", camp=True, trebuchet=True), move="in", amt=0.08,
      cam=dict(loc=(-88, -74, None), target=(-30, -15, 10), lens=26, dz=1.6, dof="philip", fstop=2.8),
      chars=[dict(n="philip", e="angry", p="arms_up", look=(0.8, -0.4), at=(-83.1, -69.6, None), anim="shake")],
      tents=[(-74.6, -67.6), (-80.4, -56.3)],
      sfx=["crowd_murmur"], note="Philip in his camp, furious, swearing at the castle on the cliff."),
 dict(id="s09", at="even with walls of iron", set="world2", opt=dict(light="dusk", variant="iron", camp=True), move="in", amt=0.10,
      cam=dict(loc=(-72, -58, None), target=(0, 0, 9), lens=30, dz=1.6, dof="philip", fstop=4),
      chars=[dict(n="philip", e="determined", p="stand", look=(0.8, -0.3), at=(-67.4, -53.4, None), prop="map")],
      sfx=["clang"], note="Imagined: the castle made of iron plates; Philip, determined: 'I'd still take it'."),
 dict(id="s10", at="Richard just laughed", set="battle2", opt=dict(light="golden"), move="in", amt=0.08,
      cam=dict(loc=(0.6, 4.6, 1.5), target=(-0.2, -1, 1.45), lens=28, dof="richard", fstop=2.8),
      chars=[dict(n="richard", e="laughing", p="stand", at=(-0.2, -0.6, 0), anim="laugh", prop="goblet")], sfx=["laugh"], note="Richard on the battlements, laughing."),
 dict(id="s11", at="He'd hold it", set="battle2", opt=dict(variant="butter", light="golden", knife=True), move="out", amt=0.08,
      cam=dict(loc=(1.9, 4.3, 1.9), target=(0, -1, 1.35), lens=26, dof="richard", fstop=2.8),
      chars=[dict(n="richard", e="smug", p="hips", look=(0.6, 0), at=(-0.3, -0.5, 0))], sfx=["squish"], note="Walls of butter (with a knife in it). Richard smug."),
 dict(id="s12", at="So in twelve", set="world2", opt=dict(light="golden", camp=True), move="out", amt=0.10,
      cam=dict(loc=(-76, -74, None), target=(0, 0, 8), lens=22, dz=2.0),
      crowd=dict(n=36, area=(-62, -42, -62, -44), colors="FR", expr=("determined", "angry", "determined", "neutral"), pose=("stand", "arms_up", "stand"), anim="march", seed=200),
      sign=dict(text="1203", at=(-72.2, -70.6), w=1.4, h=0.8, yaw=-45), sfx=["march", "drums"], note="1203: the French army marches on the castle."),
 dict(id="s13", at="They dug", set="wall3", opt=dict(light="day", grass=False, rubble=True), move="in", amt=0.10,
      cam=dict(loc=(0.5, -9.0, 1.6), target=(0, 4, 1.8), lens=20),
      chars=[dict(n="gaston", e="determined", p="stand", look=(0, 0.5), at=(-1.4, 1.4, 0), anim="dig", prop="shovel"), dict(n="tibo", e="angry", p="stand", look=(0, 0.5), at=(1.6, 1.0, 0), anim="dig", prop="shovel")],
      crowd=dict(n=6, area=(-6, 6, 1.0, 2.8), colors="FR", expr=("determined", "angry"), pose=("arms_up",), anim="dig", seed=230),
      fx=[dict(t="dust", y=0.80)], sfx=["dig", "dig", "dig"], note="Miners digging at the foot of the wall."),
 dict(id="s14", at="they smashed", set="world2", opt=dict(light="golden", camp=True, trebuchet=True), move="in", amt=0.12,
      cam=dict(loc=(-78, -54, None), target=(-36, -12, 8), lens=22, dz=2.0),
      fx=[dict(t="boulder", a="treb_tip", b="castle"), dict(t="shake", at=0.55)], sfx=["catapult", "boom"], note="Trebuchet hurls a boulder; impact."),
 dict(id="s15", at="they starved", set="gate2", opt=dict(light="golden", open_=False), move="in", amt=0.08,
      cam=dict(loc=(1.0, -7.0, 1.7), target=(-0.5, 0, 1.5), lens=26, dof="roger", fstop=2.8),
      chars=[dict(n="roger", e="sad", p="stand", look=(0, 0.6), at=(-0.6, -1.8, 0), prop="bowl")],
      crowd=dict(n=4, area=(-4.5, 4.0, 0.0, 3.5), colors="EN", expr=("sad",), pose=("stand", "shrug"), anim="idle", seed=260),
      sfx=["stomach", "wind"], note="Inside: Roger and the defenders, hungry and sad, months pass."),
 dict(id="s16", at="The first wall", set="world2", opt=dict(light="golden", camp=True, breach=True, smoke=True), move="in", amt=0.10,
      cam=dict(loc=(-80, -12, None), target=(-46, 2, 4), lens=24, dz=3.5),
      crowd=dict(n=14, area=(-70, -60, -14, -2), colors="FR", expr=("laughing", "laughing", "determined"), pose=("arms_up",), anim="cheer", seed=300),
      fx=[dict(t="shake", at=0.1)], sfx=["collapse", "cheer"], note="The outer wall collapses, French cheer."),
 dict(id="s17", at="The second wouldn't", set="wall3", opt=dict(light="day", grass=True), move="out", amt=0.08,
      cam=dict(loc=(1.0, -6.0, 1.4), target=(0, 4, 2.2), lens=22),
      chars=[dict(n="gaston", e="shocked", p="shrug", look=(-0.4, -0.3), at=(-0.9, 1.4, 0), anim="bounce"), dict(n="tibo", e="angry", p="hips", look=(-0.6, 0), at=(1.4, 0.6, 0))],
      log=True, sfx=["thud", "boing"], note="Battering ram bounces off the second wall. Gaston dazed, Tibo furious."),
 dict(id="s18", at="Then, the story", set="wall3", opt=dict(light="golden"), move="in", amt=0.10,
      cam=dict(loc=(0.6, -5.2, 1.55), target=(-0.25, -2.4, 1.5), lens=30, dof="bogis", fstop=2.0),
      chars=[dict(n="bogis", e="neutral", p="hold_spear", look=(0, 0), at=(-0.25, -2.4, 0), swaps=[("story goes", "curious")])],
      sfx=["birds"], note="Meet Bogis (neutral → curious)."),
 dict(id="s19", at="a soldier named", set="wall3", opt=dict(light="golden"), move="in", amt=0.08,
      cam=dict(loc=(0.05, -6.5, 0.8), rot=(106, 0, -3), lens=15, dof="bogis", fstop=1.0),
      chars=[dict(n="bogis", e="curious", p="point_up", look=(0.5, -0.6), at=WALL_HERO)], sfx=["sting"], note="Bogis looks up and points (approved frame)."),
 dict(id="s20", at="spotted a little", set="wall3", opt=dict(light="golden"), move="in", amt=0.14,
      cam=dict(loc=(0.8, -1.0, 1.6), target=(2.2, 3.1, 8.4), lens=20), fx=[dict(t="flies", pt="garderobe")],
      sfx=["flies"], note="POV: the little stone box sticking out of the wall."),
 dict(id="s21", at="With a hole", set="wall3", opt=dict(light="golden"), move="in", amt=0.12,
      cam=dict(loc=(1.8, 1.4, 3.6), target=(2.0, 2.9, 7.3), lens=35), fx=[dict(t="flies", pt="hole")], sfx=["flies"], note="ECU from below: the hole."),
 dict(id="s22", at="Yep", set="wall3", opt=dict(light="golden"), move="in", amt=0.06,
      cam=dict(loc=(0.05, -6.7, 1.85), target=(-0.25, -4.5, 1.6), lens=40, dof="bogis", fstop=2.0),
      chars=[dict(n="bogis", e="disgusted", p="stand", look=(0.3, -0.4), at=WALL_HERO, anim="recoil")], sfx=["bleh"], note="Bogis close-up: disgusted 'Yep.'"),
 dict(id="s23", at="That's the toilet", set="toilet2", move="in", amt=0.10,
      cam=dict(loc=(0.0, -1.7, 2.5), target=(0, 1.7, 0.9), lens=24), fx=[dict(t="flies", pt="seat_hole")], sfx=["flies", "drip"], note="Inside the garderobe: the wooden seat over the chute."),
 dict(id="s24", at="He and a few", set="cut2", opt=dict(light="night"), move="up", amt=0.12,
      cam=dict(loc=(0.3, -9.5, 6.0), target=(0, 1, 6.0), lens=26),
      chars=[dict(n="bogis", e="determined", p="arms_up", look=(0, -1), at=(0, 0.9, 6.9), anim="climb"),
             dict(n="tibo", e="scared", p="arms_up", look=(0, -1), at=(0.05, 1.0, 4.6), anim="climb"),
             dict(n="gaston", e="angry", p="arms_up", look=(0, -1), at=(-0.05, 1.1, 2.3), anim="climb")],
      sfx=["scrape", "grunt", "scrape"], note="Cutaway: Bogis, Tibo and Gaston crawl up the chute."),
 dict(id="s25", at="popped out", set="chapel2", move="in", amt=0.08,
      cam=dict(loc=(0.6, -4.6, 1.7), target=(-0.9, 2.0, 1.0), lens=24),
      chars=[dict(n="bogis", e="smug", p="stand", look=(0.6, 0), at=(-1.6, 0.6, -0.62), anim="pop", clip="floor_hole")],
      sfx=["pop", "choir"], note="Bogis pops out of the latrine hole into the chapel, smug."),
 dict(id="s26", at="and threw open", set="gate2", opt=dict(light="dawn", open_=True), move="in", amt=0.10,
      cam=dict(loc=(0, -9.5, 1.8), target=(0, 6, 3.0), lens=22),
      chars=[dict(n="bogis", e="laughing", p="arms_up", at=(-1.6, -3.0, 0), anim="cheer")],
      crowd=dict(n=16, area=(-2.6, 2.6, 5.5, 30), colors="FR", expr=("angry", "determined", "laughing"), pose=("arms_up", "stand"), anim="run", seed=330),
      sfx=["gate_creak", "charge"], note="Bogis throws the gate open, the French army charges in."),
 dict(id="s27", at="The defenders", set="gate2", opt=dict(light="dawn", open_=True), move="in", amt=0.06,
      cam=dict(loc=(3.0, -8.0, 1.8), target=(-1.0, 2.0, 2.0), lens=22, dof="roger", fstop=2.8),
      chars=[dict(n="roger", e="scared", p="shrug", look=(0.6, 0), at=(-1.0, -1.8, 0), anim="panic")],
      crowd=dict(n=5, area=(-6, 4, -1, 4), colors="EN", expr=("scared", "shocked"), pose=("arms_up", "shrug"), anim="panic", seed=360),
      fx=[dict(t="shake", at=0.2)], sfx=["panic", "scream"], note="Roger and the defenders panic."),
 dict(id="s28", at="and soon the whole", set="world2", opt=dict(light="golden", flags="french", camp=True), move="out", amt=0.12,
      cam=dict(loc=(-82, -72, None), target=(0, 4, 24), lens=28, dz=1.8, dof="philip", fstop=4),
      chars=[dict(n="philip", e="smug", p="hips", look=(0.7, -0.6), at=(-76.0, -66.4, None), swaps=[("surrendered", "laughing")])],
      sfx=["fanfare"], note="French flag over the keep. Philip smug."),
 dict(id="s29", at="You see", set="cut2", opt=dict(light="day"), move="in", amt=0.08,
      cam=dict(loc=(-3.6, -16.5, 4.8), target=(-2.6, 1, 4.6), lens=24),
      sign=dict(text="GARDEROBE", at=(-4.6, -2.0), w=2.4, h=0.8, yaw=0, z=1.4), sfx=["whoosh"], note="Mechanism: a clean cutaway of the wall, the toilet and its chute over the moat."),
 dict(id="s30", at="Everything just", set="cut2", opt=dict(light="day"), move="in", amt=0.06,
      cam=dict(loc=(-1.6, -11.5, 6.0), target=(-0.6, 1, 5.0), lens=24),
      fx=[dict(t="blob", a="seat", b="chute_bottom", c="moat"), dict(t="splash", pt="moat", at=0.8)], sfx=["drop", "splash"], note="Everything just drops outside (into the moat)."),
 dict(id="s31", at="Clean,", set="battle2", opt=dict(light="golden"), move="in", amt=0.08,
      cam=dict(loc=(1.2, 4.4, 1.6), target=(-0.1, -1, 1.5), lens=30, dof="richard", fstop=2.8),
      chars=[dict(n="richard", e="smug", p="stand", look=(0.5, 0), at=(-0.1, -0.5, 0), swaps=[("genius", "laughing")], prop="goblet")], sfx=["ding", "ding", "ding"], note="Clean, simple, genius — Richard proud."),
 dict(id="s32", at="Except a hole", set="cut2", opt=dict(light="day"), move="in", amt=0.06,
      cam=dict(loc=(-1.6, -12.5, 6.0), target=(-0.6, 1, 5.2), lens=24),
      fx=[dict(t="blob", a="seat", b="chute_bottom", c="moat"), dict(t="arrow", dir="down", pt="chute_top")], sfx=["drop"], note="A hole that lets things out…"),
 dict(id="s33", at="also lets things in", set="cut2", opt=dict(light="day"), move="in", amt=0.06,
      cam=dict(loc=(-1.6, -12.5, 6.0), target=(-0.6, 1, 5.2), lens=24),
      chars=[dict(n="bogis", e="smug", p="arms_up", look=(0, -1), at=(0, 0.9, 1.6), anim="climb_fast")],
      fx=[dict(t="arrow", dir="up", pt="chute_bottom")], sfx=["scrape", "sting"], note="…also lets things in: Bogis climbs up."),
 dict(id="s34", at="The castle that", set="battle2", opt=dict(variant="butter", light="dusk", drips=True), move="in", amt=0.10,
      cam=dict(loc=(1.0, 4.6, 1.6), target=(-0.2, -1, 1.45), lens=28, dof="richard", fstop=2.8),
      chars=[dict(n="richard", e="shocked", p="shrug", look=(0, 0.4), at=(-0.2, -0.6, 0), anim="shake")], sfx=["melt"], note="The 'butter' castle melts; Richard shocked."),
 dict(id="s35", at="was taken through", set="toilet2", move="in", amt=0.10, hold=0.9,
      cam=dict(loc=(0.25, -1.35, 1.95), target=(0, 1.7, 1.45), lens=24),
      chars=[dict(n="bogis", e="laughing", p="arms_up", look=(0, 0), at=(0, 1.62, 0.32), anim="pop_final", clip="seat_hole", prop="banner")],
      fx=[dict(t="flash", word="toilet"), dict(t="shake", word="toilet")], sfx=["pop", "boom", "fanfare"], note="PAYOFF: Bogis bursts out of the toilet with the French banner on 'toilet'."),
]

# ------------------------------------------------------------------ timing from the aligned words
def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def timings(words_path=os.path.join(HERE, "work/words.json"), xf=0.25):
    W = json.load(open(words_path)); toks = [norm(w["w"]) for w in W]; idx = 0; starts = []; widx = []
    for sh in SHOTS:
        q = [norm(x) for x in sh["at"].split()]
        for i in range(idx, len(toks)):
            if toks[i:i + len(q)] == q:
                starts.append(W[i]["s"]); widx.append(i); idx = i + 1; break
        else:
            raise SystemExit(f"cannot find '{sh['at']}'")
    starts[0] = 0.0
    end = W[-1]["e"]
    out = []
    for k, sh in enumerate(SHOTS):
        t0 = max(0.0, starts[k] - 0.05) if k else 0.0
        t1 = (starts[k + 1] - 0.05 + xf) if k + 1 < len(SHOTS) else end + sh.get("hold", 0.8)
        out.append((t0, t1, widx[k]))
    return out, W


def word_time(W, snippet, after=0):
    q = [norm(x) for x in snippet.split()]; toks = [norm(w["w"]) for w in W]
    for i in range(after, len(toks)):
        if toks[i:i + len(q)] == q: return W[i]["s"]
    return None


# ------------------------------------------------------------------ cards
CARD_DIR = os.path.join(HERE, "renders", "cards")


def card_path(n, e, p, look=(0, 0), prop=None):
    return os.path.join(CARD_DIR, f"{n}_{e}_{p}_{look[0]:+.1f}_{look[1]:+.1f}{'_' + prop if prop else ''}.png")


def all_card_jobs():
    jobs = []
    for sh in SHOTS:
        for c in sh.get("chars", []):
            exprs = [c["e"]] + [e for _, e in c.get("swaps", [])]
            for e in exprs:
                jobs.append(("hero", c["n"], e, c["p"], tuple(c.get("look", (0, 0))), c.get("prop")))
        cr = sh.get("crowd")
        if cr:
            import random
            g = random.Random(cr["seed"])
            for i in range(cr["n"]):
                jobs.append(("extra", cr["seed"] + i, g.choice(cr["expr"]), g.choice(cr["pose"]), (round(g.uniform(-0.5, 0.5), 1), 0), cr["colors"]))
    return jobs


def crowd_members(sh):
    import random
    cr = sh["crowd"]; g = random.Random(cr["seed"]); out = []; pos = random.Random(cr["seed"] + 999)
    x0, x1, y0, y1 = cr["area"]
    for i in range(cr["n"]):
        e = g.choice(cr["expr"]); p = g.choice(cr["pose"]); look = (round(g.uniform(-0.5, 0.5), 1), 0)
        out.append(dict(seed=cr["seed"] + i, e=e, p=p, look=look, xy=(pos.uniform(x0, x1), pos.uniform(y0, y1)),
                        img=os.path.join(CARD_DIR, f"extra{cr['seed'] + i}_{e}_{p}_{cr['colors']}.png")))
    return out


def make_cards():
    from cast import draw_full, extra_spec
    import cast as projcast_unused  # noqa
    sys.path.insert(0, HERE)
    import importlib.util
    spec = importlib.util.spec_from_file_location("projcast", os.path.join(HERE, "cast.py")); pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
    os.makedirs(CARD_DIR, exist_ok=True); n = 0
    for job in all_card_jobs():
        if job[0] == "hero":
            _, name, e, p, look, prop = job; out = card_path(name, e, p, look, prop)
            if not os.path.exists(out):
                sp = dict(pc.SPECS[name])
                if prop: sp["prop"] = prop
                if p in ("arms_up", "shrug", "hips") and sp.get("prop") == "spear": sp["prop"] = None
                draw_full(sp, out, e, p, look); n += 1
        else:
            _, seed, e, p, look, cols = job; out = os.path.join(CARD_DIR, f"extra{seed}_{e}_{p}_{cols}.png")
            if not os.path.exists(out):
                draw_full(extra_spec(seed, FR if cols == "FR" else EN, hats=("kettle", "cap", "none") if cols == "FR" else ("coif", "kettle", "none")), out, e, p, look); n += 1
    print("cards rendered:", n)


# ------------------------------------------------------------------ plan + timeline
def write_plan():
    T, W = timings(); lines = ["# PLAN — 09 The Castle That Fell Through Its Toilet", "",
        f"Voice: audio/voice.wav ({W[-1]['e']:.1f} s, tightened ×1.1 from 72.1 s). 1440×2560, 60 fps, no captions. Dissolve 0.25 s.", "",
        "| # | time | words | set / light | camera | characters (expression · pose · look) | FX / SFX | notes |", "|---|---|---|---|---|---|---|---|"]
    timeline = []
    for (t0, t1, wi), sh in zip(T, SHOTS):
        nxt = T[SHOTS.index(sh) + 1][2] if SHOTS.index(sh) + 1 < len(SHOTS) else len(W)
        words = " ".join(w["w"] for w in W[wi:nxt])
        chars = "; ".join(f"**{c['n']}** {c['e']}{''.join(' → ' + e + ' @' + s for s, e in c.get('swaps', []))} · {c['p']} · look {tuple(c.get('look', (0, 0)))}" for c in sh.get("chars", []))
        if sh.get("crowd"): chars += f"; crowd ×{sh['crowd']['n']} {'/'.join(sh['crowd']['expr'])} ({sh['crowd']['anim']})"
        lines.append(f"| {sh['id']} | {t0:.2f}–{t1:.2f} | {words} | {sh['set']} {sh.get('opt', {}).get('light', '')} | {sh['move']} {sh['amt']:.0%} | {chars or '—'} | {', '.join(f['t'] for f in sh.get('fx', []))} / {', '.join(sh.get('sfx', []))} | {sh['note']} |")
        sw = []
        for c in sh.get("chars", []):
            for s, e in c.get("swaps", []):
                sw.append(dict(n=c["n"], t=word_time(W, s, wi), e=e))
        fx = []
        for f in sh.get("fx", []):
            f = dict(f)
            if "word" in f: f["time"] = word_time(W, f["word"], wi)
            fx.append(f)
        timeline.append(dict(id=sh["id"], t0=round(t0, 3), t1=round(t1, 3), move=sh["move"], amt=sh["amt"], chars=sh.get("chars", []),
                             crowd=crowd_members(sh) if sh.get("crowd") else [], crowd_anim=sh.get("crowd", {}).get("anim"), swaps=sw, fx=fx, sfx=sh.get("sfx", []),
                             light=sh.get("opt", {}).get("light", "interior"), set=sh["set"]))
    open(os.path.join(HERE, "PLAN.md"), "w").write("\n".join(lines) + "\n")
    json.dump(timeline, open(os.path.join(HERE, "work/timeline.json"), "w"), indent=1, default=list)
    print(f"PLAN.md: {len(SHOTS)} shots, total {T[-1][1]:.2f} s")


# ------------------------------------------------------------------ build + render one shot (inside bpy)
def build(sh):
    import bpy
    from scene_kit import reset, card, camera, point, render, sign as mksign, text_image, cyl, wood, POINTS
    import sets09 as S
    from mathutils import Vector
    reset()
    o = dict(sh.get("opt", {}))
    import sets09b as S2
    if sh["set"] == "wall3": S2.set_wall3(**o)
    elif sh["set"] == "battle2": S2.set_battlements2(**o)
    elif sh["set"] == "cut2": S2.set_cutaway2(**o)
    elif sh["set"] == "toilet2": S2.set_toilet2()
    elif sh["set"] == "chapel2": S2.set_chapel2()
    elif sh["set"] == "gate2": S2.set_gate2(**o)
    elif sh["set"] == "world2": S2.set_world2(**o)
    elif sh["set"] == "wall": S.set_wall(**o)
    elif sh["set"] == "wall2": S.set_wall2(**o)
    elif sh["set"] == "world": S.set_world(**o)
    elif sh["set"] == "battlements": S.set_battlements(**o)
    elif sh["set"] == "cutaway": S.set_cutaway(**o)
    elif sh["set"] == "toilet": S.set_toilet_room()
    elif sh["set"] == "chapel": S.set_chapel()
    elif sh["set"] == "gate": S.set_gate(**o)
    gz = (lambda x, y: S.world_h(x, y)) if sh["set"] in ("world", "world2") else (lambda x, y: 0.0)
    objs = {}
    for c in sh.get("chars", []):
        x, y, z = c["at"]; z = gz(x, y) if z is None else z
        img = card_path(c["n"], c["e"], c["p"], tuple(c.get("look", (0, 0))), c.get("prop"))
        objs[c["n"]] = card(c["n"], img, (x, y, z), None, h=2.1, baked=c.get("baked", False))
    for m in crowd_members(sh) if sh.get("crowd") else []:
        x, y = m["xy"]; card(f"x{m['seed']}", m["img"], (x, y, gz(x, y)), None, h=2.1)
    if sh.get("sign"):
        sg = sh["sign"]; x, y = sg["at"]; z = gz(x, y) + sg.get("z", 1.2)
        img = text_image(os.path.join(S.TEX, f"sign_{sh['id']}.png"), sg["text"], font_size=150 if len(sg["text"]) > 6 else 220)
        p = mksign(img, (x, y, z), sg["w"], sg["h"], math.radians(sg.get("yaw", 0)), post=False)
        cyl((x, y + 0.05, (z + gz(x, y)) / 2), 0.07, z - gz(x, y), wood("post"), 8)
    for i, (x, y) in enumerate(sh.get("tents", [])):
        from scene_kit import flat as _flat, cyl as _cyl
        z = gz(x, y); T1, T2 = _flat("tentw", (0.92, 0.90, 0.84), 0.9), _flat("tentb2", (0.14, 0.24, 0.62), 0.8)
        _cyl((x, y, z + 2.2), 3.0, 4.4, T1 if i % 2 else T2, 20, "tent", r2=0.0); _cyl((x, y, z + 0.6), 3.05, 1.2, T2 if i % 2 else T1, 20, "tentb")
    if sh.get("log"):
        lg = cyl((0.2, 2.3, 0.45), 0.42, 5.0, wood("ram", (0.32, 0.20, 0.10), (0.5, 0.34, 0.18)), 20); lg.rotation_euler = (math.radians(90), 0, math.radians(70))
    cm = sh["cam"]; loc = list(cm["loc"])
    if loc[2] is None: loc[2] = gz(loc[0], loc[1]) + cm.get("dz", 1.7)
    dof = objs.get(cm["dof"]) if isinstance(cm.get("dof"), str) else cm.get("dof")
    camera(tuple(loc), cm.get("target"), cm.get("rot"), cm.get("lens", 24), cm.get("shift", (0, 0)), dof, cm.get("fstop", 2.8))
    if sh["set"] == "world2" and loc[2] - gz(loc[0], loc[1]) < 6:          # foreground dressing near the camera (CLAUDE.md 5c.2)
        import props as PR, sets09b as S2, random
        from scene_kit import grid_ground, grass_field, scatter
        tgt = cm.get("target") or (loc[0] + 1, loc[1] + 1, loc[2]); fx_, fy_ = tgt[0] - loc[0], tgt[1] - loc[1]; L_ = math.hypot(fx_, fy_) or 1; fx_, fy_ = fx_ / L_, fy_ / L_
        rx_, ry_ = fy_, -fx_; cx_, cy_ = loc[0] + fx_ * 12, loc[1] + fy_ * 12
        g = grid_ground(34, 50, S2.mat("ground"), lambda x, y: S.world_h(x, y) + 0.03, loc=(cx_, cy_, 0))
        heroes = [(c["at"][0], c["at"][1]) for c in sh.get("chars", [])]
        def keep(x, y):
            u = (x - loc[0]) * fx_ + (y - loc[1]) * fy_; v = (x - loc[0]) * rx_ + (y - loc[1]) * ry_
            return u < 2.5 or u > 26 or any(math.hypot(x - hx, y - hy) < 1.8 for hx, hy in heroes) or (abs(v) < 0.8)
        grass_field(g, "grass_medium_01", 26000, lambda c: True, size=2.6)
        side = lambda u, v: (loc[0] + fx_ * u + rx_ * v, loc[1] + fy_ * u + ry_ * v)
        rg = random.Random(sum(map(ord, sh["id"])))
        for i in range(14):
            u = rg.uniform(2.8, 11); v = rg.choice([-1, 1]) * rg.uniform(0.9, 0.35 * u + 0.8)
            x, y = side(u, v)
            if keep(x, y): continue
            k = rg.choice(["shrub", "rocks", "sack", "barrels", "crates", "hay", "shrub"])
            PR.dress((x - 0.1, x + 0.1, y - 0.1, y + 0.1), 1, [k], z=S.world_h, seed=i)
        for (u, v) in ((4.0, -2.6), (4.6, 2.9)):                                 # a fence post / bush right at the frame edges
            x, y = side(u, v); PR.dress((x - 0.1, x + 0.1, y - 0.1, y + 0.1), 1, ["shrub"], z=S.world_h, seed=int(u * 10))
    for ob in list(bpy.data.objects):                                     # no tree in front of the lens
        if ob.get("tree") and math.hypot(ob.location.x - loc[0], ob.location.y - loc[1]) < 16:
            bpy.data.objects.remove(ob)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "cards": make_cards()
    elif cmd == "plan": write_plan()
    elif cmd == "render":
        sid = sys.argv[2]; W, H, spp = (int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1440, 2560, 40)
        out = sys.argv[6] if len(sys.argv) > 6 else os.path.join(HERE, "renders", "shots", f"{sid}.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sh = [s for s in SHOTS if s["id"] == sid][0]; build(sh)
        from scene_kit import render
        ex = 0.6 if sh.get("opt", {}).get("light") == "night" else (0.5 if sh["set"] in ("toilet", "chapel") else (0.2 if sh["set"] == "gate" else -0.3))
        render(out, W, H, spp, exposure=ex)
        print("WROTE", out)
