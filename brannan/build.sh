#!/usr/bin/env bash
# rebuild main.js + toon.js from parts
cd "$(dirname "$0")/web" && python3 - <<'PY'
T=open('/root/shorts/throat/web/main.js').read().split('\n')
head='\n'.join(T[:73]).replace("fxAt, NOSE }","fxAt, SETX }")
m=head+'\n'+open('world_part.js').read()+'\n'+'\n'.join(T[151:241])+'\n'+open('ws_part.js').read()+'\n'+'\n'.join(T[266:])+'\n'
m=m.replace("s * (a.flip ? -1 : 1)","s * (a.sx ?? (a.flip ? -1 : 1))")
m=m.replace("if (a.blob !== false && a.y < DECK + 0.5)","if (a.blob !== false && a.y < (a.ground ?? DECK) + 0.5)")
open('main.js','w').write(m)
PY
cat toonbase.js roman.js intfx.js seafx.js westfx.js > toon.js
for f in main.js story.js toon.js; do cp $f /tmp/chk.mjs; node --check /tmp/chk.mjs || echo "SYNTAX $f"; done
