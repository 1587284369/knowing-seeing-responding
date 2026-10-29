# -*- coding: utf-8 -*-
"""Generate paper figures from raw logs using PIL + numpy (no matplotlib)."""
import os, re, io, csv
from collections import Counter
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
# 游戏项目与论文项目分开放：默认指向同级目录下的 06-游戏自动化，可用环境变量覆盖
GAME = os.environ.get("NGO_GAME_DIR") or os.path.join(
    HERE, "..", "06-游戏自动化", "NEEDY-GIRL-OVERDOSE")
BASE = os.path.abspath(GAME)
# 优先使用本目录下冻结的数据快照（保证论文图表不随游戏继续游玩而变化）
FROZEN = os.path.join(HERE, "data-v1")
LOG = FROZEN if os.path.isdir(FROZEN) else os.path.join(BASE, "log")
FIG = os.path.join(HERE, "figs-v1")
os.makedirs(FIG, exist_ok=True)

FONT = "C:/Windows/Fonts/msyh.ttc"
def f(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc" if bold else FONT, size)

INK = (32, 36, 44)
MUTED = (98, 106, 118)
GRID = (210, 214, 222)
ACC = (192, 57, 43)
ACC2 = (41, 98, 155)
BG = (255, 255, 255)

# ---------------------------------------------------------------- load actions
rows = []
with io.open(os.path.join(LOG, "actions.log"), encoding="utf-8", errors="replace") as fh:
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) < 2:
            continue
        try:
            t = datetime.strptime(p[0].strip(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
        verb = "\t".join(p[1:]).partition(":")[0].strip()
        rows.append((t, verb))

coords = []
for t, v in rows:
    pass
with io.open(os.path.join(LOG, "actions.log"), encoding="utf-8", errors="replace") as fh:
    for line in fh:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2 and "\t".join(p[1:]).startswith("click:"):
            m = re.search(r"(-?\d+),(-?\d+)", p[1])
            if m:
                coords.append((int(m.group(1)), int(m.group(2))))

# ============================================================ FIG 1 architecture
def fig_arch():
    W, H = 1700, 1080
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    def box(x0, y0, x1, y1, title, lines, fill=(246, 248, 251), edge=(150, 158, 172), tc=INK):
        d.rounded_rectangle([x0, y0, x1, y1], 14, fill=fill, outline=edge, width=2)
        d.text((x0 + 18, y0 + 12), title, font=f(25, True), fill=tc)
        yy = y0 + 50
        for ln in lines:
            d.text((x0 + 18, yy), ln, font=f(19), fill=MUTED)
            yy += 28

    d.text((40, 30), "图 1  系统架构：像素级 GUI 智能体的四层结构", font=f(34, True), fill=INK)
    d.text((40, 76), "游戏没有任何 API；智能体只能看见截图、只能通过合成鼠标键盘事件行动。",
           font=f(20), fill=MUTED)

    # game
    box(620, 130, 1080, 238, "游戏进程  Windose.exe（Unity, 960×540 窗口）",
        ["《主播女孩重度依赖》Steam 版；无控制台 / 无存档读接口"], fill=(255, 246, 238), edge=(214, 148, 96))

    # perception
    box(120, 300, 520, 470, "① 感知层",
        ["dsh-game.ps1 -Action shot：GDI 截图", "ocr_srv.py：RapidOCR PP-OCRv4 常驻",
         "裁剪 + 2× 放大后再识别（小字）", "输出：文本 + 置信度 + 包围盒"])
    box(560, 300, 960, 470, "state.ps1",
        ["规则判定 20+ 个界面状态", "（IDLE / JINE / PLAN_LIST /", "ADVANCE / ENDING …）",
         "输出 state / 动作 / 坐标 / 数值"])
    box(1000, 300, 1580, 470, "OCR 失败即显式退化（−1 哨兵）",
        ["读不到 → 记 −1，而不是猜一个数", "残片校验：无「/100」且 <10 → −1",
         "仍会误读：第 10 天 → 第 18 天"], fill=(252, 244, 244), edge=(200, 130, 130))

    # decision
    box(120, 510, 700, 700, "② 决策层  brain.ps1（规则状态机）",
        ["switch(state) → 动作；硬闸：",
         "exit 56 同一动作重复 3 次无效", "exit 50 连续 5 步无进展",
         "exit 55 JINE 卡住 / exit 60 渲染偏移"])
    box(740, 510, 1260, 700, "contract.ps1（日合同判定）",
        ["状态：Phase / Tweeted / Inventory / SourcesUsed", "决策空间里没有 Sleep（空转不许变新的一天）",
         "exit 70 傍晚/夜里库存为 0 → Abort", "账本闸门：连续 3 天 0 空转才放行"])
    box(1300, 510, 1580, 700, "人类监督",
        ["pause.json + exit 42", "STOP 文件 → 拒绝一切输入",
         "（26 次实际拦截）"], fill=(240, 247, 240), edge=(120, 160, 120))

    # action
    box(120, 740, 700, 880, "③ 执行层  dsh-game.ps1",
        ["click / dclick / type / key / close", "AppActivate 前置（焦点即权限）",
         "写入 actions.log（24,121 条）"])
    box(740, 740, 1260, 880, "④ 记忆层（跨会话的唯一载体）",
        ["log/daybook.csv（110 行账本）", "log/state.json、log/brain.log（40,925 行）",
         "31 份 Markdown 交接 / 铁律 / 复盘"])

    def arrow(x0, y0, x1, y1, col=(120, 128, 140), dash=False, w=2):
        if dash:
            n = 14
            for i in range(n):
                if i % 2:
                    continue
                xa = x0 + (x1 - x0) * i / n; ya = y0 + (y1 - y0) * i / n
                xb = x0 + (x1 - x0) * (i + 1) / n; yb = y0 + (y1 - y0) * (i + 1) / n
                d.line([xa, ya, xb, yb], fill=col, width=w)
        else:
            d.line([x0, y0, x1, y1], fill=col, width=w)
        # head
        import math
        ang = math.atan2(y1 - y0, x1 - x0)
        L = 12
        d.polygon([(x1, y1),
                   (x1 - L * math.cos(ang - 0.4), y1 - L * math.sin(ang - 0.4)),
                   (x1 - L * math.cos(ang + 0.4), y1 - L * math.sin(ang + 0.4))], fill=col)

    arrow(850, 238, 330, 298)
    arrow(520, 385, 558, 385)
    arrow(960, 385, 998, 385)
    arrow(410, 470, 410, 508)
    arrow(830, 470, 900, 508)
    arrow(410, 700, 410, 738)
    arrow(1000, 700, 1000, 738)
    arrow(1296, 605, 1264, 605, col=(120, 160, 120))
    arrow(700, 810, 738, 810, col=(120, 128, 140))
    d.text((42, 940), "注：绿色为人类监督/中断路径，其余为数据与动作流向。感知层每一步约 2–3 秒，构成整个系统的速度上限。",
           font=f(19), fill=MUTED)
    im.save(os.path.join(FIG, "fig1_architecture.png"))
    print("fig1 ok")

# ================================================================ FIG 2 heatmap
def fig_heat():
    W, H = 1700, 1100
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 30), "图 2  9,731 次点击在 960×540 屏幕上的空间分布", font=f(34, True), fill=INK)
    d.text((40, 76), "动作高度集中在少数固定坐标：前 10 个坐标点占 47.8%，前 50 个占 76.5%（共 785 个不同坐标）。",
           font=f(20), fill=MUTED)

    GW, GH = 1440, 810
    x0, y0 = 100, 150
    hist, _, _ = np.histogram2d([c[0] for c in coords], [c[1] for c in coords],
                                bins=[160, 90], range=[[0, 960], [0, 540]])
    # gaussian-ish smoothing
    k = np.array([1, 2, 3, 2, 1], dtype=float); k /= k.sum()
    def blur(a):
        b = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 0, a)
        return np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), 1, b)
    h = blur(blur(hist.T))  # rows = y
    h = h / (h.max() or 1)
    h = np.power(h, 0.55)

    # colormap: white -> pale yellow -> orange -> red -> dark red
    stops = np.array([[255, 255, 255], [255, 240, 200], [253, 190, 90], [230, 90, 40], [120, 10, 20]], float)
    pos = np.array([0.0, 0.25, 0.5, 0.78, 1.0])
    rgb = np.zeros(h.shape + (3,), dtype=np.uint8)
    for ch in range(3):
        rgb[..., ch] = np.interp(h, pos, stops[:, ch]).astype(np.uint8)

    heat = Image.fromarray(rgb, "RGB").resize((GW, GH), Image.BICUBIC)
    # pale game screen under it
    screen = Image.new("RGB", (GW, GH), (238, 240, 244))
    ds = ImageDraw.Draw(screen)
    for gx in range(0, GW, 120):
        ds.line([gx, 0, gx, GH], fill=(228, 231, 236))
    for gy in range(0, GH, 90):
        ds.line([0, gy, GW, gy], fill=(228, 231, 236))
    screen = Image.blend(screen, heat, 0.82)
    im.paste(screen, (x0, y0))
    d.rectangle([x0, y0, x0 + GW, y0 + GH], outline=(140, 148, 160), width=2)

    # axes
    d.text((x0, y0 + GH + 12), "x →  0", font=f(18), fill=MUTED)
    d.text((x0 + GW - 30, y0 + GH + 12), "960", font=f(18), fill=MUTED)
    d.text((x0 + GW / 2 - 20, y0 + GH + 12), "480", font=f(18), fill=MUTED)
    d.text((x0 - 96, y0), "y = 0", font=f(18), fill=MUTED)
    d.text((x0 - 96, y0 + GH - 20), "540", font=f(18), fill=MUTED)

    # legend
    lx, ly = x0 + GW - 300, y0 + 20
    d.rounded_rectangle([lx - 12, ly - 10, lx + 250, ly + 58], 8, fill=(255, 255, 255), outline=(200, 205, 214))
    d.text((lx, ly - 4), "点击密度", font=f(18), fill=INK)
    for i in range(220):
        v = i / 219
        c = tuple(int(np.interp(v, pos, stops[:, ch])) for ch in range(3))
        d.rectangle([lx + i, ly + 24, lx + i + 1, ly + 40], fill=c)
    d.rectangle([lx, ly + 24, lx + 220, ly + 40], outline=(200, 205, 214))
    d.text((lx, ly + 44), "低 → 高", font=f(15), fill=MUTED)

    d.text((100, 1010), "可辨识的高频区域：JINE 贴纸「好」(548,370)、桌面上排图标 (172,300)/(295,302)/(276,348)、"
                        "企划列表左列 (276,386)、时段按钮 (492,528)。",
           font=f(19), fill=MUTED)
    im.save(os.path.join(FIG, "fig2_click_heatmap.png"))
    print("fig2 ok")

# =============================================================== FIG 3 timeline
def fig_timeline():
    t0 = rows[0][0]
    hours = [(t - t0).total_seconds() / 3600 for t, v in rows if v in ("shot", "click")]
    nb = 121
    cnt, edges = np.histogram(hours, bins=np.arange(0, nb + 1, 1))
    W, H = 1700, 760
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 30), "图 3  逐小时动作量：探索 → 状态机 → 人机分工", font=f(34, True), fill=INK)
    d.text((40, 76), "5 个自然日，16 段会话，28.5 小时活跃操作；空白段是离线时间（智能体不运行）。",
           font=f(20), fill=MUTED)

    L, R, T, B = 110, 1620, 140, 600
    d.line([L, B, R, B], fill=INK, width=2)
    d.line([L, T, L, B], fill=INK, width=2)
    mx = max(cnt) or 1
    for i in range(0, int(mx) + 1, 100):
        y = B - (i / mx) * (B - T)
        d.line([L, y, R, y], fill=(232, 235, 240), width=1)
        d.text((L - 58, y - 11), str(i), font=f(17), fill=MUTED)
    d.text((24, T - 34), "事件/小时", font=f(18), fill=MUTED)

    bw = (R - L) / nb
    for i, c in enumerate(cnt):
        xx = L + i * bw
        hh = (c / mx) * (B - T)
        if c == 0:
            continue
        col = (60, 90, 140) if i < 76 else ((176, 78, 48) if i >= 114 else (70, 130, 110))
        d.rectangle([xx, B - hh, xx + max(2, bw - 3), B], fill=col)

    # day separators
    for hh, lab in [(0, "10-20 19:46"), (21, "10-21"), (45, "10-22"), (69, "10-23"),
                    (93, "10-24"), (117, "10-25")]:
        x = L + hh * bw
        if hh:
            d.line([x, T, x, B], fill=(180, 185, 195), width=1)
        d.text((x + 4, B + 10), lab, font=f(17), fill=MUTED)

    def note(x, txt, col, dy=0, anchor="left"):
        d.line([x, T + 10, x, B - 4], fill=col, width=2)
        if anchor == "left":
            d.text((x + 6, T + 6 + dy), txt, font=f(17), fill=col)
        else:
            tw = d.textlength(txt, font=f(17))
            d.text((x - 6 - tw, T + 6 + dy), txt, font=f(17), fill=col)

    note(L + 76 * bw, "写 contract.ps1", ACC2, 0)
    note(L + 114 * bw, "跑腿模式 exit 42", ACC, 34, "right")

    d.text((110, 668), "阶段 1 的动作统计：试开播 302 次、摸头 228 次、选企划 233 次，真正拿到素材仅 41 次。",
           font=f(18), fill=MUTED)
    d.text((110, 700), "颜色：深蓝 = 阶段 1（探索 + 自建状态机）；绿 = 阶段 2（规则写成判定层 contract.ps1）；"
                        "橙红 = 阶段 3（人机分工，每屏由人判断）。横轴为距首个事件的绝对小时数。",
           font=f(17), fill=MUTED)
    im.save(os.path.join(FIG, "fig3_timeline.png"))
    print("fig3 ok")

# ============================================================ FIG 4 perception
def fig_perc():
    W, H = 1700, 720
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((40, 30), "图 4  感知与结局：读不出数字，与死在哪儿", font=f(34, True), fill=INK)

    # left: OCR missing
    lx, ly, lw, lh = 110, 190, 700, 320
    d.text((lx, ly - 42), "4a  OCR 读数缺失率（daybook.csv，n=110 行）", font=f(21, True), fill=INK)
    d.line([lx, ly + lh, lx + lw, ly + lh], fill=INK, width=2)
    d.line([lx, ly, lx, ly + lh], fill=INK, width=2)
    data = [("粉丝", 23.6), ("压力", 38.2), ("好感", 30.0), ("阴暗", 44.5)]
    for i in range(0, 51, 10):
        y = ly + lh - (i / 50) * lh
        d.line([lx, y, lx + lw, y], fill=(232, 235, 240))
        d.text((lx - 46, y - 10), f"{i}%", font=f(16), fill=MUTED)
    bw = lw / len(data)
    for i, (name, v) in enumerate(data):
        xx = lx + i * bw + bw * 0.22
        hh = (v / 50) * lh
        d.rectangle([xx, ly + lh - hh, xx + bw * 0.52, ly + lh], fill=(176, 78, 48))
        d.text((xx + 4, ly + lh - hh - 28), f"{v}%", font=f(19, True), fill=(176, 78, 48))
        d.text((xx + 16, ly + lh + 12), name, font=f(20), fill=INK)

    # right: ending distribution
    rx, ry, rw, rh = 980, 190, 620, 320
    d.text((rx, ry - 42), "4b  24 局有记录的结局分布", font=f(21, True), fill=INK)
    d.line([rx, ry + rh, rx + rw, ry + rh], fill=INK, width=2)
    data2 = [("Die Set Down", 10, (60, 90, 140)), ("Crossing the line", 8, (176, 78, 48)),
             ("Healthy Party", 2, (70, 130, 110)), ("Os-Alien", 1, (120, 84, 150)),
             ("未到结局", 3, (150, 155, 165))]
    bw2 = rw / len(data2)
    for i, (name, v, col) in enumerate(data2):
        xx = rx + i * bw2 + bw2 * 0.16
        hh = (v / 11.5) * rh
        d.rectangle([xx, ry + rh - hh, xx + bw2 * 0.64, ry + rh], fill=col)
        d.text((xx + 8, ry + rh - hh - 30), str(v), font=f(21, True), fill=col)
        d.text((xx + 4, ry + rh + 12), name, font=f(13), fill=INK)
    d.text((110, 620), "注：结局名来自游戏内结算画面（截图存档）；缺失率 = 账本中该字段被记为 −1（不可信/未读到）的比例。"
                        "账本里出现过把 21,915 粉读成 5、把第 10 天读成第 18 天的误读。",
           font=f(18), fill=MUTED)
    im.save(os.path.join(FIG, "fig4_perception_outcome.png"))
    print("fig4 ok")

fig_arch()
fig_heat()
fig_timeline()
fig_perc()
print("figures written to", FIG)
