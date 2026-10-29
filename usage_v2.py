# -*- coding: utf-8 -*-
"""统计 DSH 会话日志里的 token 用量，并按项目关键词归类。"""
import os, io, json, glob
import zstandard

ROOT = os.path.expanduser(r"~/.dsh/sessions")
FILES = sorted(glob.glob(os.path.join(ROOT, "**", "session.v4.jsonl.zstd"), recursive=True),
               key=os.path.getmtime)
KEYS = ("JINE", "超天酱", "NEEDY", "Crossing the line", "糖糖", "主播女孩", "超天")

def usage_of(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("usage"), dict):
            return obj["usage"]
        for v in obj.values():
            r = usage_of(v)
            if r: return r
    elif isinstance(obj, list):
        for v in obj:
            r = usage_of(v)
            if r: return r
    return None

tot_proj = [0, 0, 0, 0]
tot_all = [0, 0, 0, 0]
rows = []
for path in FILES:
    mt = os.path.getmtime(path)
    if mt < 1760000000:  # 2026-10 之前
        continue
    hit = False
    s = [0, 0, 0]
    n = 0
    try:
        with open(path, "rb") as fh:
            reader = zstandard.ZstdDecompressor().stream_reader(fh, read_across_frames=True)
            for raw in io.TextIOWrapper(reader, encoding="utf-8", errors="replace"):
                if not hit and any(k in raw for k in KEYS):
                    hit = True
                try:
                    o = json.loads(raw)
                except Exception:
                    continue
                u = usage_of(o.get("data", {}))
                if not u: continue
                n += 1
                s[0] += int(u.get("inputTokens", 0))
                s[1] += int(u.get("outputTokens", 0))
                s[2] += int(u.get("cacheReadTokens", 0))
    except Exception as e:
        rows.append((path, -1, 0, 0, 0, str(e)))
        continue
    tot_all[0] += s[0]; tot_all[1] += s[1]; tot_all[2] += s[2]; tot_all[3] += n
    if hit:
        tot_proj[0] += s[0]; tot_proj[1] += s[1]; tot_proj[2] += s[2]; tot_proj[3] += n
    rows.append((os.path.basename(os.path.dirname(path))[:22], n, s[0], s[1], s[2], hit))

print("%-24s %5s %10s %10s %14s %6s" % ("session", "msgs", "in", "out", "cacheR", "proj"))
for r in rows:
    print("%-24s %5d %10d %10d %14d %6s" % (r[0], r[1], r[2], r[3], r[4], "Y" if r[5] else ""))
print()
for name, t in (("PROJECT", tot_proj), ("ALL", tot_all)):
    total = t[0] + t[1] + t[2]
    print("%s: msgs=%d in=%d out=%d cacheR=%d total=%d (%.2fB)" % (name, t[3], t[0], t[1], t[2], total, total/1e9))
    # 公开价：缓存 ¥0.2/M，未命中 ¥2/M，输出 ¥3/M
    rmb = t[2]/1e6*0.2 + t[0]/1e6*2 + t[1]/1e6*3
    print("   按公开价 ≈ ¥%.1f；按项目旧口径(¥103.12/3.19B) ≈ ¥%.1f" % (rmb, total*103.12/3187771601))
