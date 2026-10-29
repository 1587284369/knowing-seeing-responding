# -*- coding: utf-8 -*-
"""Quantify the NEEDY GIRL OVERDOSE automation logs -> UTF-8 report."""
import re, csv, io, os, sys, glob
from collections import Counter, defaultdict
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
# 游戏项目与论文项目分开放：默认指向同级目录下的 06-游戏自动化，可用环境变量覆盖
GAME = os.environ.get("NGO_GAME_DIR") or os.path.join(
    HERE, "..", "06-游戏自动化", "NEEDY-GIRL-OVERDOSE")
BASE = os.path.abspath(GAME)
# 优先使用本目录下冻结的数据快照（保证论文数字不随游戏继续游玩而变化）
FROZEN = os.path.join(HERE, "data-v1")
LOG = FROZEN if os.path.isdir(FROZEN) else os.path.join(BASE, "log")
OUT = []

def W(*a):
    OUT.append(" ".join(str(x) for x in a))

# ---------------------------------------------------------------- actions.log
rows = []
raw = 0
with io.open(os.path.join(LOG, "actions.log"), encoding="utf-8", errors="replace") as f:
    for line in f:
        raw += 1
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2:
            continue
        try:
            t = datetime.strptime(parts[0].strip(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        rest = "\t".join(parts[1:])
        verb, _, detail = rest.partition(":")
        rows.append((t, verb.strip(), detail.strip()))

W("# 自动化行为日志量化报告")
W()
W("## 1. actions.log")
W()
W("- 原始行数：%d，可解析事件：%d" % (raw, len(rows)))
W("- 时间跨度：%s → %s（%.1f 小时 / %.1f 天）" % (
    rows[0][0], rows[-1][0],
    (rows[-1][0]-rows[0][0]).total_seconds()/3600,
    (rows[-1][0]-rows[0][0]).total_seconds()/86400))
W()
verbs = Counter(v for _, v, _ in rows)
W("| 动作类型 | 次数 |")
W("|---|---:|")
for v, c in verbs.most_common():
    W("| `%s` | %d |" % (v, c))
W()

# sessions
sessions, cur = [], [rows[0]] if rows else []
for prev, currow in zip(rows, rows[1:]):
    if (currow[0]-prev[0]) > timedelta(minutes=30):
        sessions.append(cur); cur = [currow]
    else:
        cur.append(currow)
if cur: sessions.append(cur)
W("## 2. 会话切分（间隔 > 30 分钟）")
W()
W("共 **%d** 个会话。总事件 %d。" % (len(sessions), len(rows)))
W()
W("| # | 开始 | 结束 | 时长(h) | 事件 | 点击 | 截图 | 截图/点击 |")
W("|---|---|---|---:|---:|---:|---:|---:|")
tot_dur = 0.0
for i, s in enumerate(sessions, 1):
    d = (s[-1][0]-s[0][0]).total_seconds()/3600
    tot_dur += d
    c = sum(1 for _, v, _ in s if v == "click")
    sh = sum(1 for _, v, _ in s if v in ("shot", "zoom"))
    W("| S%02d | %s | %s | %.2f | %d | %d | %d | %.2f |" % (
        i, s[0][0].strftime("%m-%d %H:%M"), s[-1][0].strftime("%m-%d %H:%M"),
        d, len(s), c, sh, (sh/c if c else float('nan'))))
W()
W("活跃时长合计：**%.2f 小时**（墙钟跨度 %.1f 小时，%.0f%% 为在线时间）" % (
    tot_dur, (rows[-1][0]-rows[0][0]).total_seconds()/3600,
    100*tot_dur/((rows[-1][0]-rows[0][0]).total_seconds()/3600)))
W()

by_day = Counter(t.strftime("%Y-%m-%d") for t, _, _ in rows)
W("## 3. 每日事件量")
W()
W("| 日期 | 事件 | 点击 | 截图 |")
W("|---|---:|---:|---:|")
for d in sorted(by_day):
    c = sum(1 for t, v, _ in rows if t.strftime("%Y-%m-%d") == d and v == "click")
    sh = sum(1 for t, v, _ in rows if t.strftime("%Y-%m-%d") == d and v in ("shot", "zoom"))
    W("| %s | %d | %d | %d |" % (d, by_day[d], c, sh))
W()

# clicks
clicks = [(t, d) for t, v, d in rows if v == "click"]
coords = Counter()
for _, d in clicks:
    m = re.match(r"(-?\d+),(-?\d+)", d)
    if m: coords[(int(m.group(1)), int(m.group(2)))] += 1
W("## 4. 点击分布（策略狭窄度）")
W()
W("- 总点击：%d；不同坐标：%d" % (len(clicks), len(coords)))
tot = sum(coords.values())
srt = coords.most_common()
top1 = srt[0][1]/tot
top10 = sum(c for _, c in srt[:10])/tot
top50 = sum(c for _, c in srt[:50])/tot
W("- 最高频单点占 **%.1f%%**；前 10 点占 **%.1f%%**；前 50 点占 **%.1f%%**" % (100*top1, 100*top10, 100*top50))
W()
W("Top 15 坐标：")
W()
W("| 坐标 | 次数 | 占比 |")
W("|---|---:|---:|")
for (x, y), c in srt[:15]:
    W("| (%d,%d) | %d | %.1f%% |" % (x, y, c, 100*c/tot))
W()

# gaps
gaps = sorted((b[0]-a[0]).total_seconds() for s in sessions for a, b in zip(s, s[1:]))
def pct(p): return gaps[min(len(gaps)-1, int(len(gaps)*p))]
W("## 5. 步间时延")
W()
W("- n=%d，p10=%.1fs，p50=%.1fs，p90=%.1fs，均值=%.2fs" % (
    len(gaps), pct(.1), pct(.5), pct(.9), sum(gaps)/len(gaps)))
W()

# screenshot reuse
shot_ev = [(t, d) for t, v, d in rows if v in ("shot", "zoom")]
files = Counter(os.path.basename(re.match(r"(\S+)", d).group(1)) for _, d in shot_ev if re.match(r"(\S+)", d))
W("## 6. 截图")
W()
W("- 截图/缩放事件 %d，唯一文件 %d，事件/文件比 %.2f" % (len(shot_ev), len(files), len(shot_ev)/len(files)))
if LOG == FROZEN:
    W("- 数据来自冻结快照 `data-v1/`（论文口径）；截图唯一文件即上行的 %d" % len(files))
else:
    W("- `shots/` 目录实际 png 数：%d（注意：游戏继续游玩会让此数变化）"
      % len(glob.glob(os.path.join(BASE, "shots", "*.png"))))
W()

# STOP
stops = [t for t, v, _ in rows if v.startswith("BLOCKED")]
W("## 7. 急停拦截")
W()
W("- `BLOCKED by STOP` 事件：%d 次" % len(stops))
for t in stops[:10]: W("  - %s" % t)
W()

# ------------------------------------------------------------------ daybook
W("## 8. daybook.csv（OCR 账本）")
W()
with io.open(os.path.join(LOG, "daybook.csv"), encoding="utf-8-sig", errors="replace") as f:
    txt = f.read()
if "天使" not in txt and "\ufffd" in txt:
    txt = txt.encode("utf-8", "ignore").decode("gbk", "replace")
    txt = txt.replace("\ufeff", "")
dr = list(csv.DictReader(io.StringIO(txt)))
W("- 记录行数：%d" % len(dr))
W()
W("| 字段 | 有效值 | 读不出(-1) | 缺失率 |")
W("|---|---:|---:|---:|")
for fld in ["fans", "stress", "love", "dark", "day"]:
    vals = [r.get(fld, "") for r in dr]
    bad = sum(1 for v in vals if v.strip() in ("", "-1"))
    W("| %s | %d | %d | %.1f%% |" % (fld, len(vals)-bad, bad, 100*bad/max(1, len(vals))))
W()
W("- 出现的 `day` 取值：%s" % dict(sorted(Counter(r.get("day", "") for r in dr).items(), key=lambda k: (len(k[0]), k[0]))))
W("- `day=18` 行数：%d（第 10 天被 OCR 读成 18 的已知错误）" % sum(1 for r in dr if r.get("day") == "18"))
impl = [(r.get("time"), r.get("fans")) for r in dr if r.get("fans", "").strip() not in ("", "-1") and r["fans"].isdigit() and int(r["fans"]) < 10]
W("- 粉丝数 <10 的行（明显误读）：%s" % impl)
loves = [(r.get("time"), r.get("love"), r.get("day")) for r in dr if r.get("love", "").strip() not in ("", "-1")]
bad_love = [(t, v) for t, v, _ in loves if v.isdigit() and int(v) < 10]
W("- 好感 <10 的行：%d 个 %s" % (len(bad_love), bad_love))
W()
W("最后 12 行原始值：")
W()
W("```")
W("time,day,fans,stress,love,dark,lastPlan")
for r in dr[-12:]:
    W("%s,%s,%s,%s,%s,%s,%s" % tuple(r.get(k, "") for k in ["time", "day", "fans", "stress", "love", "dark", "lastPlan"]))
W("```")
W()

# ----------------------------------------------------------------- brain.log
W("## 9. brain.log（决策循环）")
W()
with io.open(os.path.join(LOG, "brain.log"), encoding="utf-8", errors="replace") as f:
    bl = [l.rstrip("\n") for l in f]
W("- 行数：%d" % len(bl))
ev = Counter()
for l in bl:
    p = l.split("\t")
    if len(p) >= 2:
        ev[p[1].split()[0] if p[1].split() else ""] += 1
W()
W("| 事件 | 次数 |")
W("|---|---:|")
for k, c in ev.most_common(25):
    W("| `%s` | %d |" % (k, c))
W()
ocr_restart = sum(1 for l in bl if "OCR 服务已启动" in l)
W("- `OCR 服务已启动`：**%d** 次（进程/服务重启次数）" % ocr_restart)
states = Counter()
for l in bl:
    m = re.search(r"STATE (\w+)", l)
    if m: states[m.group(1)] += 1
W("- STATE 判定分布：%s" % dict(states.most_common(20)))
W()
tails = [l for l in bl if any(k in l for k in ("exit", "退出", "pause", "ABORT", "GATE", "闸"))]
W("- 含 exit/pause/abort/gate 的行：%d，示例：" % len(tails))
for l in tails[:12]: W("  - %s" % l[:160])
W()

# --------------------------------------------------------------- backups
W("## 10. 存档备份（局数推断）")
W()
bdirs = sorted(glob.glob(os.path.join(BASE, "save-backup", "*")))
W("| 备份目录 | 文件数 | Data3 最大天 |")
W("|---|---:|---:|")
for b in bdirs:
    fs = glob.glob(os.path.join(b, "**", "*.es3"), recursive=True)
    ds = []
    for p in fs:
        m = re.search(r"Data3_Day(\d+)", os.path.basename(p))
        if m: ds.append(int(m.group(1)))
    W("| %s | %d | %s |" % (os.path.basename(b), len(fs), max(ds) if ds else "-"))
W()
W("备份目录总数：%d" % len(bdirs))

with io.open(os.path.join(HERE, "log-report-v1.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
print("written log-report-v1.md, lines:", len(OUT))
