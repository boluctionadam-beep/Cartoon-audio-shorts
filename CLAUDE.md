# Cartoon-audio-shorts — production rules

Read this first in every session. The user should never have to explain these again.
Talk to the user in Russian. Videos are in English (US).

## 1. What we make
- Vertical animated history/"why" shorts in the *style grammar* of the Ricks Clips channel (the 5 reference videos the user sent).
  Original stories, characters and shots only; never copy their videos, characters or scenes.
- Output: **1440×2560, 60 fps**, H.264, −14 LUFS. ~55–70 s.
- **No captions/subtitles.**
- Look: 2D hand-drawn characters (cards) inside stylised 3D worlds rendered in Blender (Cycles, CPU, `pip install bpy`).
- Every shot moves (slow push-in / pull-out), shots ~1.5–2.5 s, 0.25 s dissolves, voice from frame 0, payoff on the last word.

## 2. Workflow (always in this order, preview before long renders)
1. 10 ideas → user picks a number. Verify facts with web search; mark legend/disputed honestly in the script ("the story goes").
2. Script with beats: Hook (0–3 s) → Setup → Doubt/escalation → Catastrophe/reveal → Mechanism ("You see, …") → Punchline on a showable noun.
   Save to `projects/<NN-slug>/script.md`.
3. Voice: the user generates it in **ElevenLabs** from the text we give: **one continuous block, no blank lines**, with v3 audio tags
   (`[mischievously] [deadpan] [chuckles] [sighs] [curious] [disgusted] [whispers] [excited] [sarcastic] [laughs]`).
   Fallback local voice: `tools/tts.py` (Kokoro), default blend `am_michael:0.5,am_adam:0.5`, speed **1.1** (user's choice).
   The pace does NOT have to match Ricks Clips.
4. `PLAN.md`: one row per shot — time, words, setting, light, framing, camera move, **every character's expression + look direction + pose**, props, SFX.
5. Characters: specs in `projects/<id>/cast.py` → lineup sheet → user approval.
6. Scenes in Blender → low-res previews (360×640 or 540×960) → user approval → final renders.
7. Assemble, sound, QA. Commit and push to the session branch as work progresses.

## 3. Characters — style rules (learned from user feedback, keep them)
- **Head:** near-round, pure white, soft grey shading crescent on the side away from light. NOT a perfect circle: small
  hand-drawn bumps (`head_pts(bumps≈0.03)`). No nose, no ears.
- **Head is NOT centred on the body:** offset sideways (`head_offset` ±30–60 px) and slightly tilted; face features shift toward the look direction.
- **Body:** soft capsule/sack, no shoulders, no neck; head sits right on top. Clothes with fabric pattern (quilting, mail, emblems), belt, shading.
- **Outline:** brush-like, varying thickness (never uniform vector lines).
- **Limbs:** thick tapered curved black strokes (legs ≈30 px, arms ≈26 px at r=225), knees bend, small hooked feet, small dark mitten hands.
- **Hair:** textured masses with curly/scribbled edges and strands; fringe under hats. **Headwear:** volumetric — shading,
  highlight streak, underside darker, details (ridge, rivets, band, gems).
- **Eyes:** black dots, half-moon eyes with eyelid lines, wide white eyes with pupils, closed arcs. **Brows:** thick, fattest in the
  middle, tapered, angled — they carry most of the emotion. Small expressive mouths (o, smirk, D-laugh, squiggle, yell).
- Asymmetry everywhere (one brow up, one eye squinting, lean, bent leg).

## 4. Every character must be distinct (check before showing the user)
Each character in a short gets a unique combination of:
- dominant colour (no two share it), headwear silhouette, hair type/colour or facial hair,
- height class (legs 360 / 410 / 505 / 560) and body shape (thin tall, round short, broad, chubby),
- head size/squash and personality (default expression + pose).
Run the **silhouette test**: `python3 cast.py lineup out.jpg` renders full bodies, black silhouettes and expression rows —
every silhouette must be recognisable on its own. Show the lineup to the user before using new characters.

## 5. Emotions & acting (mandatory in every shot)
- Every character in every shot has an expression that fits **that moment** of the story, plus a look direction at the
  thing they react to (`look=(x,y)`) and a pose. Never leave a character "neutral" unless the beat is deadpan on purpose.
- Typical mapping by beat:
  | Beat | Hero | Doubters / others |
  |---|---|---|
  | Hook | curious / determined / smug | — |
  | Setup / boasting | smug, determined | smug, laughing |
  | Doubt / mocking | determined, sad, disgusted | laughing, smug, angry |
  | Discovery | curious (one eye wide, one squint) | — |
  | Catastrophe | smug or determined | shocked, scared (sweat), angry |
  | Mechanism | neutral/curious (explainer) | — |
  | Punchline | smug or laughing | shocked / sad |
- Reaction extras: sweat drops (scared/shocked), steam + purple face for rage, squash on impacts, double takes.
- Expression set (tools/cast.py): `neutral curious smug shocked disgusted laughing angry scared sad determined`.
  Poses: `stand point_up hips arms_up shrug hold_sword` (+ `prop: spear|sword`). Add new presets to the kit, not ad hoc.

## 5b. Crowds and extras — keep them simple on purpose
Only named characters (hero, villain, the 2–4 people the story is about) get full detail. A crowd (army, townsfolk,
guards, spectators, prisoners) is background and must NOT get the same effort:
- Use `extra_spec()` / `crowd_cards()` in `tools/cast.py`: same style grammar, but `detail="low"` — flat clothes and hair
  (no fabric/hair textures), half-size cards, built from a few templates with random swaps (hat, hair, build, colour,
  head offset/tilt) so they never look like clones.
- Colours: the faction's muted palette (French army: dull blue/brown/green/khaki). Never a hero's unique colour; extras
  must not draw the eye away from the heroes.
- Emotion: one shared crowd emotion for the beat (laughing / cheering / shocked / scared), with 1–2 variants mixed in.
  Poses from a small set (stand, arms_up, hips).
- Depth: the nearest row as cards, rows behind smaller and blurred by depth of field / haze; far rows can be simple
  silhouettes or tiny blobs; very far = instanced copies of the same few cards. Never place extras in front of a hero's face.
- In Blender reuse the same card images on many planes (instancing) instead of drawing new ones per person.

## 6. Code map
- `tools/charkit.py` — drawing primitives (brush-outlined shapes, shading, tapered limbs, heads, hair, eyes, brows, mouths).
- `tools/cast.py` — character system: `draw_full(spec, out, expr, pose, look)`, `draw_head(...)`, `lineup(...)`.
- `projects/<id>/cast.py` — the cast specs of one short (`python3 cast.py card NAME EXPR POSE OUT.png lookx looky`).
- `projects/<id>/scenes/*.py` — Blender scenes (2D card on a plane in a 3D world). Solve camera framing numerically
  (world_to_camera_view search) instead of guessing; preview at low res first.
- `tools/grade.py` — colour grade (contrast, saturation, warm highs, bloom, vignette).
- `tools/tts.py` — local narrator voice with delivery tags `[slow] [fast] [pause]`.

## 6b. Production pipeline (learned on short 09)
- `projects/<id>/shots<id>.py` is the single source of truth (timing from words, set, camera, chars with expression/pose/look/
  swaps/anim, crowd, fx, sfx). `python3 shots09.py plan|cards|render ID`. `bash make.sh` builds everything, resumable.
- Voice: `tools/tighten.py` (shorten pauses + rubberband tempo) → `tools/align.py` (sherpa-onnx ASR from GitHub models,
  word timestamps mapped to the script) → `work/words.json`.
- Backgrounds: Blender stills at 1.1× overscan, ~3.5–6 min each at 1440×2560 / 32 spp on 4 CPU cores. Characters are
  shadow-only cards in 3D and animated in 2D by `tools/compose.py` (camera moves, idle/laugh/cheer/climb/pop…, expression
  swaps on words, flies/dust/boulder/blob/splash/arrows/flash/shake), 60 fps, 0.25 s dissolves. `baked=True` only where
  geometry must hide the character; `clip=<point>` hides a card below a line (popping out of holes).
- Heavy sets (castle world) are built once and cached as a .blend; trees near the camera are culled automatically.
- Booleans: cutters must pass THROUGH the visible face; never hide_viewport a cutter. Cards face the camera via
  yaw = atan2(dx, -dy).
- Always do a low-res preview pass of every shot (`preview_frames.py` composed contact sheet) before the full render,
  check cameras inside objects, characters out of frame, empty voids, cut-off signs.
- Sound: `tools/sound.py` (synth SFX + Kokoro crowd voices + Karplus-Strong music by story sections) → `tools/mix.py`
  (music −12, SFX −8, bus compression, −14 LUFS, TP ≤ −1.5) → `tools/qa.py`.

## 7. Accounts / money
- Higgsfield: **never spend credits**. Trial auto-renewal was cancelled by the user (Nov 2026); unlimited was off. Use only `use_unlim`
  generations when available; otherwise render locally.
