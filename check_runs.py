# -*- coding: utf-8 -*-
"""把 paper.md 附录 A.4 的 39 局表与 data-v2/runs-v2.csv 逐行比对。

历史：v2.2 及以前表在 §5.1，v2.3 起移到「附录 A.4 39 局明细」，并多出一列
「连续 Day1→」。因此本脚本只扫 A.4 小节内的表，且允许 5 列（旧）与 6 列（新）两种形态。

    py ./check_runs.py
"""
import io, csv, re, sys
sys.stdout.reconfigure(encoding="utf-8")

rows = list(csv.DictReader(io.open("data-v2/runs-v2.csv", encoding="utf-8-sig")))
csv_by_id = {int(r["id"]): r for r in rows}
print("csv rows:", len(rows))

lines = io.open("paper.md", encoding="utf-8-sig").read().splitlines()

# 只扫「附录 A.4」小节：从标题行起，到下一个同级或更高级标题（## / ### 之外的 --- 或 ## ）结束
in_section = False
table_lines = []
for ln in lines:
    s = ln.strip()
    if s.startswith("###") and "A.4" in s:
        in_section = True
        continue
    if in_section:
        if s.startswith("## ") or s.startswith("### "):
            break
        if s.startswith("|"):
            table_lines.append(s)

DAY_RANGE = re.compile(r"^D(\d+)\s*[→>-]+\s*D(\d+)$")


def cells_of(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


seen = {}
for line in table_lines:
    cs = cells_of(line)
    if len(cs) < 5:
        continue
    if not cs[0].isdigit() or not re.match(r"^\d\d-\d\d$", cs[1]):
        continue
    i = int(cs[0])
    if not 1 <= i <= 39:
        continue
    m = DAY_RANGE.match(cs[2])
    if m:
        seen[i] = ("B", cs[1], m.group(1), m.group(2), cs[3], cs[4])
    elif cs[2].isdigit():
        seen[i] = ("A", cs[1], cs[2], cs[2], cs[3], cs[4])
    else:
        print("UNPARSED id=%s day=%r" % (i, cs[2]))

print("paper table rows parsed:", len(seen))


def norm_fans(s):
    s = s.replace(",", "").replace("~", "").replace("*", "").strip()
    if s in ("—", "-", ""):
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
