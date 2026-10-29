# -*- coding: utf-8 -*-
"""v2 论文图 1-5，全部由 data-v2 的冻结日志与重建账本生成。"""
import os, re, io, csv
from collections import Counter
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data-v2")
FIG = os.path.join(HERE, "figs-v2")
os.makedirs(FIG, exist_ok=True)

FONT = "C:/Windows/Fonts/msyh.ttc"
def f(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc" if bold else FONT, size)

INK, MUTED, GRID = (32, 36, 44), (98, 106, 118), (214, 218, 226)
ACC, ACC2, ACC3 = (176, 78, 48), (52, 92, 150), (58, 130, 110)
BG = (255, 255, 255)

rows = []
with io.open(os.path.join(DATA, "actions.log"), encoding="utf-8", errors="replace") as fh:
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) < 2: continue
        try: t = datetime.strptime(p[0].strip(), "%Y-%m-%d %H:%M:%S")
        except Exception: continue
        rows.append((t, "\t".join(p[1:])))

coords = []
for t, v in rows:
    if v.startswith("click:"):
        m = re.search(r"(-?\d+),(-?\d+)", v)
        if m: coords.append((int(m.group(1)), int(m.group(2))))

# ------------------------------------------------------------------ fig 1
def fig_arch():
    W, H = 1700, 1100
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    def box(x0, y0, x1, y1, title, lines, fill=(246, 248, 251), edge=(150, 158, 172)):
        d.rounded_rectangle([x0, y0, x1, y1], 14, fill=fill, outline=edge, width=2)
        d.text((x0 + 18, y0 + 12), title, font=f(24, True), fill=INK)
        yy = y0 + 50
        for ln in lines:
            d.text((x0 + 18, yy), ln, font=f(18), fill=MUTED); yy += 27
    import math
    def arrow(x0, y0, x1, y1, col=(120, 128, 140)):
        d.line([x0, y0, x1, y1], fill=col, width=2)
        ang = math.atan2(y1 - y0, x1 - x0); L = 11
        d.polygon([(x1, y1),
                   (x1 - L*math.cos(ang-0.4), y1 - L*math.sin(ang-0.4)),
                   (x1 - L*math.cos(ang+0.4), y1 - L*math.sin(ang+0.4))], fill=col)

    d.text((40, 28), "图 1  系统架构：四层 + 两道闸门", font=f(34, True), fill=INK)
    d.text((40, 74), "游戏没有任何 API。第 9 天加的那道「拒绝执行」闸门，是通关的前提之一。", font=f(20), fill=MUTED)

    box(620, 128, 1080, 232, "游戏进程  Windose.exe（Unity，960×540）",
        ["《NEEDY STREAMER OVERDOSE》Steam 版；无控制台 / 无存档接口"], fill=(255, 246, 238), edge=(214, 148, 96))
    box(120, 292, 520, 462, "① 感知层",
        ["截图（GDI，960×540）", "RapidOCR 常驻，2× 放大", "state.ps1：20+ 个界面状态",
         "输出 state / 动作 / 坐标 / 数值"])
    box(560, 292, 960, 462, "数值一律降级为「不可信」",
        ["读不到 → −1，不猜", "FANS / DAY 会读错（595308→802565）", "粉丝只信截图与存档"], fill=(252, 244, 244), edge=(200, 130, 130))
    box(1000, 292, 1580, 462, "OCR 失败即显式退化（−1 哨兵）",
        ["5 天账本缺失率 23.6%–44.5%", "第 10 天→第 18 天；30→38", "OCR 服务重启 196 次"],
        fill=(252, 244, 244), edge=(200, 130, 130))

    box(120, 500, 700, 700, "② 决策层  brain.ps1 / contract.ps1",
        ["规则状态机 + 日合同（11 项自测）", "exit 56 同一动作重复 → 停手（28 次）",
         "exit 70 夜晚无素材 → Abort", "决策空间里没有 Sleep"])
    box(740, 500, 1260, 700, "③ 执行层：闸门  act.ps1 / batch.ps1",
        ["一次只做一个动作", "JINE 未清 或 STOP 存在 → 拒绝执行",
         "front.ps1 抢前台；sweep.ps1 现场量命中点"], fill=(240, 247, 240), edge=(110, 160, 110))
    box(1300, 500, 1600, 700, "人类监督",
        ["pause.json + exit 42", "STOP → 拒绝一切输入（27 次）"], fill=(240, 247, 240), edge=(120, 160, 120))

    box(120, 740, 700, 890, "记忆层（跨会话的唯一载体）",
        ["daybook.csv（110 行，仅前 5 天）", "brain.log / runbook / happyend 日志",
         "51 份 Markdown 交接、铁律、战报"])
    box(740, 740, 1260, 890, "动作原语  dsh-game.ps1 / slowclick.ps1",
        ["click / dclick / type / key / close", "写 actions.log（32,558 条事件）",
         "点击 13,285 次、截图 18,326 次"])

    arrow(850, 232, 330, 290); arrow(320, 462, 320, 498); arrow(700, 600, 738, 600)
    arrow(1000, 700, 1000, 738); arrow(420, 700, 420, 738)
    arrow(1298, 600, 1262, 600, col=(110, 160, 110))
    d.text((42, 950), "注：绿色为「拒绝执行」与人类监督路径。感知一步 2–3 秒，是整个系统的速度上限。",
           font=f(19), fill=MUTED)
    im.save(os.path.join(FIG, "fig1_architecture.png")); print("fig1 ok")

# ------------------------------------------------------------------ fig 2
def fig_heat():
    W, H = 1700, 1100
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((40, 28), "图 3  13,285 次点击在 960×540 屏幕上的分布", font=f(34, True), fill=INK)
    d.text((40, 74), "前 10 个坐标占 41.0%，前 50 个占 70.2%；共 1,166 个不同坐标。", font=f(20), fill=MUTED)

    GW, GH = 1440, 810; x0, y0 = 100, 150
    hist, _, _ = np.histogram2d([c[0] for c in coords], [c[1] for c in coords],
                                bins=[160, 90], range=[[0, 960], [0, 540]])
    k = np.array([1, 2, 3, 2, 1], float); k /= k.sum()
    def blur(a):
        b = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
        return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, b)
    h = blur(blur(hist.T)); h = h / (h.max() or 1); h = np.power(h, 0.55)
    stops = np.array([[255, 255, 255], [255, 240, 200], [253, 190, 90], [230, 90, 40], [120, 10, 20]], float)
    pos = np.array([0.0, 0.25, 0.5, 0.78, 1.0])
    rgb = np.zeros(h.shape + (3,), np.uint8)
    for ch in range(3): rgb[..., ch] = np.interp(h, pos, stops[:, ch]).astype(np.uint8)
    heat = Image.fromarray(rgb, "RGB").resize((GW, GH), Image.BICUBIC)
    screen = Image.new("RGB", (GW, GH), (238, 240, 244)); ds = ImageDraw.Draw(screen)
    for gx in range(0, GW, 120): ds.line([gx, 0, gx, GH], fill=(228, 231, 236))
    for gy in range(0, GH, 90): ds.line([0, gy, GW, gy], fill=(228, 231, 236))
    im.paste(Image.blend(screen, heat, 0.82), (x0, y0))
    d.rectangle([x0, y0, x0 + GW, y0 + GH], outline=(140, 148, 160), width=2)
    d.text((x0, y0 + GH + 10), "x → 0", font=f(17), fill=MUTED)
    d.text((x0 + GW - 30, y0 + GH + 10), "960", font=f(17), fill=MUTED)
    d.text((x0 + GW/2 - 16, y0 + GH + 10), "480", font=f(17), fill=MUTED)
    d.text((x0 - 92, y0), "y = 0", font=f(17), fill=MUTED)
    d.text((x0 - 92, y0 + GH - 18), "540", font=f(17), fill=MUTED)
    lx, ly = x0 + GW - 290, y0 + 18
    d.rounded_rectangle([lx - 12, ly - 10, lx + 250, ly + 74], 8, fill=(255, 255, 255), outline=(200, 205, 214))
    d.text((lx, ly - 4), "点击密度", font=f(18), fill=INK)
    for i in range(220):
        v = i / 219; c = tuple(int(np.interp(v, pos, stops[:, ch])) for ch in range(3))
        d.rectangle([lx + i, ly + 24, lx + i + 1, ly + 40], fill=c)
    d.rectangle([lx, ly + 24, lx + 220, ly + 40], outline=(200, 205, 214))
    d.text((lx, ly + 46), "低 → 高", font=f(15), fill=MUTED)
    d.text((100, 1005), "高频区：JINE 贴纸「好」(548,370)、摸头 (372,118)、桌面图标 (172,300)/(295,302)、"
                        "企划列 (276,386)、时段按钮 (492,528)。", font=f(18), fill=MUTED)
    im.save(os.path.join(FIG, "fig3_heatmap.png")); print("fig2 ok")

# ------------------------------------------------------------------ fig 3
def fig_timeline():
    t0 = rows[0][0]
    hours = [(t - t0).total_seconds()/3600 for t, v in rows if v.startswith("shot:") or v.startswith("click:")]
    nb = int(max(hours)) + 1
    cnt, _ = np.histogram(hours, bins=np.arange(0, nb + 1, 1))
    W, H = 1700, 780
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((40, 28), "图 2  逐小时动作量：探索 → 规则化 → 测量驱动", font=f(34, True), fill=INK)
    d.text((40, 74), "9 天、31 段会话、41.3 小时活跃操作；空白段是离线时间。", font=f(20), fill=MUTED)
    L, R, T, B = 110, 1620, 140, 600
    d.line([L, B, R, B], fill=INK, width=2); d.line([L, T, L, B], fill=INK, width=2)
    mx = int((max(cnt) // 200 + 1) * 200) or 1
    for i in range(0, int(mx) + 1, 100):
        y = B - (i/mx)*(B-T); d.line([L, y, R, y], fill=(232, 235, 240))
        d.text((L - 58, y - 11), str(i), font=f(16), fill=MUTED)
    d.text((22, T - 34), "事件/小时", font=f(18), fill=MUTED)
    bw = (R - L)/nb
    cut1, cut2 = 100.2, 148.2   # 10-24 00:00 / 10-26 00:00
    for i, c in enumerate(cnt):
        xx = L + i*bw; hh = (c/mx)*(B-T)
        if c == 0: continue
        col = ACC2 if i < cut1 else (ACC3 if i < cut2 else ACC)
        d.rectangle([xx, B - hh, xx + max(2, bw - 3), B], fill=col)
    for hh, lab in [(0, "10-20"), (24, "10-21"), (48, "10-22"), (72, "10-23"),
                    (96, "10-24"), (120, "10-25"), (144, "10-26"), (168, "10-27"),
                    (192, "10-28"), (216, "10-29")]:
        x = L + hh*bw
        if hh: d.line([x, T, x, B], fill=(182, 187, 197))
        d.text((x + 3, B + 10), lab, font=f(16), fill=MUTED)
    def note(x, txt, col, dy=0, anchor="left"):
        d.line([x, T + 10, x, B - 4], fill=col, width=2)
        if anchor == "left": d.text((x + 6, T + 6 + dy), txt, font=f(17), fill=col)
        else:
            tw = d.textlength(txt, font=f(17)); d.text((x - 6 - tw, T + 6 + dy), txt, font=f(17), fill=col)
    note(L + cut1*bw, "写 contract.ps1", ACC2, 0)
    note(L + cut2*bw, "转向测量驱动", ACC3, 0)
    note(L + 216.4*bw, "Happy End 20:52", ACC, 34, "right")
    d.text((110, 660), "阶段 1 的动作统计：试开播 302 次、摸头 228 次、选企划 233 次，真正拿到素材仅 41 次。", font=f(18), fill=MUTED)
    d.text((110, 694), "颜色：深蓝 = S1 探索（10-20→23）；绿 = S2 规则化（10-24→25）；橙红 = S3 测量驱动（10-26→29）。", font=f(17), fill=MUTED)
    im.save(os.path.join(FIG, "fig2_timeline.png")); print("fig3 ok")

# ------------------------------------------------------------------ fig 4
def fig_perc():
    W, H = 1700, 760
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((40, 28), "图 5  读不出数字，与死在哪儿", font=f(34, True), fill=INK)

    lx, ly, lw, lh = 110, 190, 640, 330
    d.text((lx, ly - 40), "5a  OCR 数值缺失率（Phase A 账本，n=110）", font=f(20, True), fill=INK)
    d.line([lx, ly + lh, lx + lw, ly + lh], fill=INK, width=2); d.line([lx, ly, lx, ly + lh], fill=INK, width=2)
    data = [("粉丝", 23.6), ("压力", 38.2), ("好感", 30.0), ("阴暗", 44.5)]
    for i in range(0, 51, 10):
        y = ly + lh - (i/50)*lh
        d.line([lx, y, lx + lw, y], fill=(232, 235, 240)); d.text((lx - 44, y - 9), f"{i}%", font=f(15), fill=MUTED)
    bw = lw/len(data)
    for i, (name, v) in enumerate(data):
        xx = lx + i*bw + bw*0.22; hh = (v/50)*lh
        d.rectangle([xx, ly + lh - hh, xx + bw*0.52, ly + lh], fill=ACC)
        d.text((xx + 2, ly + lh - hh - 26), f"{v}%", font=f(18, True), fill=ACC)
        d.text((xx + 14, ly + lh + 10), name, font=f(19), fill=INK)

    rx, ry, rw = 1000, 150, 620
    d.text((rx, ry - 40), "5b  39 局的结局分布", font=f(20, True), fill=INK)
    endings = [("Crossing the line", 16, ACC), ("Die Set Down", 10, ACC2), ("Utopian Parody", 3, (120, 84, 150)),
               ("未到结局", 3, (150, 155, 165)), ("Healthy Party", 2, ACC3), ("Labor is Evil", 2, (150, 110, 60)),
               ("Os-Alien", 1, (120, 84, 150)), ("(Un)happy End World", 1, (90, 90, 110)), ("Happy End World", 1, (30, 130, 80))]
    rowh = 48
    for i, (name, v, col) in enumerate(endings):
        y = ry + i*rowh
        d.text((rx, y + 6), name, font=f(17), fill=INK)
        bw2 = (v/16)*(rw - 260)
        d.rectangle([rx + 210, y + 8, rx + 210 + max(6, bw2), y + 32], fill=col)
        d.text((rx + 218 + bw2, y + 6), str(v), font=f(17, True), fill=col)
    im.save(os.path.join(FIG, "fig5_perception.png")); print("fig4 ok")

# ------------------------------------------------------------------ fig 5
def fig_fans():
    runs = {
        "19": dict(color=(140, 145, 160), label="第19局 5,472（Die Set Down）",
                   pts=[(1, 1001), (2, 2351), (3, 2890), (4, 3114), (5, 3114), (6, 3114), (7, 3610), (8, 4064), (9, 5472)]),
        "25": dict(color=(52, 92, 150), label="第25局 317,588（Labor is Evil）",
                   pts=[(20, 88400), (21, 88648), (22, 172853), (23, 172853), (24, 195539),
                        (25, 223364), (26, 246877), (27, 246877), (28, 278790), (29, 317588)]),
        "30": dict(color=(58, 130, 110), label="第30局 424,521（Labor is Evil）",
                   pts=[(24, 239980), (25, 240653), (26, 240653), (27, 382367), (28, 423817), (29, 424521)]),
        "28": dict(color=(150, 110, 60), label="第28局 803,508（Utopian Parody）",
                   pts=[(26, 466650), (27, 522774), (28, 595308), (29, 803508)]),
        "38": dict(color=ACC, label="第38局 1,015,334（(Un)happy）",
                   pts=[(26, 382367), (27, 423817), (28, 937734), (29, 1015334)]),
    }
    W, H = 1700, 820
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((40, 28), "图 4  五条增长曲线：断播与不断播的差别", font=f(34, True), fill=INK)
    d.text((40, 74), "纵轴为对数。第 19 局九晚只到 5,472；第 38 局一晚从 42 万跳到 93 万——差别在连播倍率是否被断掉。", font=f(20), fill=MUTED)
    L, R, T, B = 120, 1560, 150, 620
    d.line([L, B, R, B], fill=INK, width=2); d.line([L, T, L, B], fill=INK, width=2)
    lo, hi = 3.0, 6.2   # log10
    def yy(v): return B - (np.log10(v) - lo)/(hi - lo)*(B - T)
    def xx(day): return L + (day - 1)/29*(R - L)
    for v in (1000, 10000, 100000, 1000000):
        y = yy(v); d.line([L, y, R, y], fill=(232, 235, 240))
        d.text((L - 78, y - 10), ("1M" if v == 1000000 else "%dk" % (v//1000)), font=f(15), fill=MUTED)
    for day in range(1, 31, 3):
        d.text((xx(day) - 12, B + 10), str(day), font=f(15), fill=MUTED)
    d.text((L, B + 36), "游戏日 →", font=f(17), fill=MUTED)
    # 100万 threshold
    yth = yy(1000000)
    for x in range(L, R, 18):
        d.line([x, yth, x + 9, yth], fill=(30, 130, 80), width=2)
    d.text((L + 8, yth - 28), "Happy End 门槛：100 万粉", font=f(17, True), fill=(30, 130, 80))

    for k, r in runs.items():
        pts = [(xx(day), yy(v)) for day, v in r["pts"]]
        d.line(pts, fill=r["color"], width=4)
        for (px, py) in pts:
            d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=r["color"])
    # win marker
    d.polygon([(xx(29), yy(1015334) - 16), (xx(29) + 9, yy(1015334) - 2),
               (xx(29), yy(1015334) + 12), (xx(29) - 9, yy(1015334) - 2)], fill=(30, 130, 80))
    d.text((xx(29) - 168, yy(1015334) - 46), "第39局 Happy End", font=f(16, True), fill=(30, 130, 80))

    ly = 700
    for i, (k, r) in enumerate(runs.items()):
        y = ly + (i // 3)*32; x = 120 + (i % 3)*470
        d.line([x, y + 9, x + 26, y + 9], fill=r["color"], width=4)
        d.text((x + 34, y - 2), r["label"], font=f(16), fill=INK)
    im.save(os.path.join(FIG, "fig4_fans.png")); print("fig5 ok")

fig_arch(); fig_heat(); fig_timeline(); fig_perc(); fig_fans()
print("done ->", FIG)
