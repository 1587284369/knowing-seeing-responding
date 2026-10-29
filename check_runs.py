# -*- coding: utf-8 -*-
"""把 paper.md §5.1 的 39 局表与 data-v2/runs-v2.csv 逐行比对。"""
import io, csv, re, sys
sys.stdout.reconfigure(encoding="utf-8")

rows = list(csv.DictReader(io.open("data-v2/runs-v2.csv", encoding="utf-8-sig")))
csv_by_id = {int(r["id"]): r for r in rows}
print("csv rows:", len(rows))

paper = io.open("paper.md", encoding="utf-8-sig").read().splitlines()
CELL = r"\s*\**\s*([^|]*?)\s*\**\s*\|"
pat_a = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d\d-\d\d)\s*\|\s*(\d+)\s*\|" + CELL + CELL + r"\s*$")
pat_b = re.compile(r"^\|\s*(\d+)\s*\|\s*(\d\d-\d\d)\s*\|\s*D(\d+)\s*→\s*D(\d+)\s*\|" + CELL + CELL + CELL + r"\s*$")

seen = {}
for ln in paper:
    m = pat_a.match(ln)
    if m:
        i = int(m.group(1))
        if i <= 24:
            seen[i] = ("A", m.group(2), m.group(3), m.group(3), m.group(4), m.group(5))
        continue
    m = pat_b.match(ln)
    if m:
        i = int(m.group(1))
        seen[i] = ("B", m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))

print("paper table rows parsed:", len(seen))


def norm_fans(s):
    s = s.replace(",", "").replace("~", "").replace("*", "").strip()
    if s in ("—", ""):
        return None
    return int(s)


def norm_end(s):
    return s.strip().strip("`").strip().strip("*").strip()


bad = 0
for i in range(1, 40):
    r = csv_by_id.get(i)
    p = seen.get(i)
    if not r or not p:
        print("MISSING", i, bool(r), bool(p))
        bad += 1
        continue
    csv_fans = int(r["fans_end"] or 0)
    pf = norm_fans(p[4])
    pe = norm_end(p[5])
    ce = norm_end(r["ending"])
    ok_end = (pe == ce) or (pe in ("主动停止", "实验停止", "收尾")) or (ce in ("未到结局",))
    ok_fans = (pf is None) or (pf == csv_fans)
    if p[0] == "B":
        ok_day = (p[2], p[3]) == (r["start_day"], r["end_day"])
    else:
        ok_day = p[2] == r["end_day"]
    if not (ok_end and ok_fans and ok_day):
        bad += 1
        print("DIFF id=%s paper: day=%s..%s fans=%s end=%s | csv: %s..%s fans=%s end=%s"
              % (i, p[2], p[3], p[4], pe, r["start_day"], r["end_day"], csv_fans, ce))
print("mismatches:", bad)
