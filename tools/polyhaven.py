#!/usr/bin/env python3
"""Poly Haven (CC0) downloader with a local cache (~/.cache/polyhaven).
  python3 polyhaven.py list textures [category]      list asset ids
  python3 polyhaven.py tex ID [res]                   diffuse/normal/rough/disp/ao maps -> dict of paths
  python3 polyhaven.py hdri ID [res]                  .hdr / .exr
  python3 polyhaven.py model ID [res]                 glTF (+ its textures)
"""
import json, os, sys, urllib.request

API = "https://api.polyhaven.com"
CACHE = os.path.expanduser("~/.cache/polyhaven")
UA = {"User-Agent": "cartoon-shorts-pipeline/1.0"}


def _get(url, path=None):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path + ".part", "wb").write(data); os.replace(path + ".part", path)
        return path
    return json.loads(data)


def assets(kind="textures", cat=None):
    q = f"{API}/assets?t={kind}" + (f"&c={cat}" if cat else "")
    return _get(q)


def files(aid):
    p = os.path.join(CACHE, aid, "files.json")
    if os.path.exists(p): return json.load(open(p))
    d = _get(f"{API}/files/{aid}"); os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(d, open(p, "w")); return d


def _fetch(url):
    p = os.path.join(CACHE, url.split("polyhaven.org/")[-1])
    if not os.path.exists(p): _get(url, p)
    return p


def tex(aid, res="2k"):
    """returns {'diff','nor','rough','disp','ao','arm'} -> local paths (whatever exists)"""
    f = files(aid); out = {}
    keys = {"diff": ["Diffuse", "diff"], "nor": ["nor_gl"], "rough": ["Rough", "rough"], "disp": ["Displacement", "disp"], "ao": ["AO", "ao"], "arm": ["arm"]}
    for k, names in keys.items():
        for n in names:
            if n in f and res in f[n]:
                fmt = "jpg" if "jpg" in f[n][res] else ("png" if "png" in f[n][res] else list(f[n][res])[0])
                out[k] = _fetch(f[n][res][fmt]["url"]); break
    return out


def hdri(aid, res="2k"):
    f = files(aid)["hdri"][res]
    return _fetch(f["hdr"]["url"] if "hdr" in f else f["exr"]["url"])


def model(aid, res="1k"):
    g = files(aid)["gltf"][res]["gltf"]
    main = _fetch(g["url"])
    for rel, info in g.get("include", {}).items():
        dst = os.path.join(os.path.dirname(main), rel)
        if not os.path.exists(dst): _get(info["url"], dst)
    return main


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "list": print(" ".join(sorted(assets(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))))
    elif cmd == "tex": print(json.dumps(tex(sys.argv[2], *(sys.argv[3:4])), indent=1))
    elif cmd == "hdri": print(hdri(sys.argv[2], *(sys.argv[3:4])))
    elif cmd == "model": print(model(sys.argv[2], *(sys.argv[3:4])))
