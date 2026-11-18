# -*- coding: utf-8 -*-
# figs_anem.py — 30호 ANEM 그림(figs_cogn.py 구조 복제, 2026-11-12).
#  규칙: 컬러, 패널 문자 모두 같은 크기·11/10 기준 2배(48pt)·굵게, 방위표 3배, 그림 안 설명문 금지, 결합은 시군구 코드로만.
#  패널 문자: 저널 지침보다 → 메모리 규칙대로 대문자 A·B, 같은 크기.
#  Fig 1 전국 성×연령 의심률(A 남자 B 여자) · Fig 2 (A) 전 기간 잔차 공간 RR (B) 두 창 핫·콜드스팟 · Fig 3 강건 4개 변수의 모형별 RR · 보충 Fig S1 EHSA
import os, unicodedata, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from numbers_anem import load, ROB, SHP, OLD, DM, NUT, UPT
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
FIG = os.path.join(HERE, "figs"); OUTF = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(FIG, exist_ok=True); os.makedirs(OUTF, exist_ok=True)
MM = 1 / 25.4; W = 174 * MM; DPI = 600; LW = 0.3; PANEL_LABEL_PT = 48
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "legend.fontsize": 7.5, "legend.title_fontsize": 8, "axes.linewidth": 0.5, "pdf.fonttype": 42})
NFC = lambda s: unicodedata.normalize("NFC", str(s)).strip()
N = load()
G = gpd.read_file(SHP); G["cd"] = G.sigungu_cd.astype(str); G["sido"] = G.cd.str[:2]; SIDO = G.dissolve("sido")
XL = (G.total_bounds[0], G.total_bounds[2]); YL = (G.total_bounds[1], G.total_bounds[3])
rd = lambda f: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", dtype={"sigungu_cd": str})
def letter(fig, ch, x, y):   # 그림 좌표 하나의 상수 크기
    fig.text(x, y, ch, fontsize=PANEL_LABEL_PT, fontweight="bold", va="top", ha="left")
def mapax(ax):
    SIDO.boundary.plot(ax=ax, color="#404040", linewidth=0.45); ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_axis_off(); ax.set_aspect("equal")
    x0, x1 = XL; y0, y1 = YL; W_ = x1 - x0; H_ = y1 - y0
    bx, by = x0 + 0.60 * W_, y0 + 0.03 * H_
    ax.plot([bx, bx + 100000], [by, by], color="black", lw=1.2, solid_capstyle="butt"); ax.text(bx + 50000, by + 0.012 * H_, "100 km", ha="center", va="bottom", fontsize=7)
    ax.annotate("N", xy=(x0 + 0.93 * W_, y0 + 0.99 * H_), xytext=(x0 + 0.93 * W_, y0 + 0.80 * H_), ha="center", va="center", fontsize=24, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>,head_length=0.9,head_width=0.45", color="black", lw=2.4))
def save(fig, k):
    p = os.path.join(FIG, f"Fig_{k}.png"); fig.savefig(p, dpi=DPI, facecolor="white"); plt.close(fig)
    im = Image.open(p).convert("RGB"); im.save(p, dpi=(DPI, DPI))
    if not str(k).startswith("S"): im.save(os.path.join(OUTF, f"Figure_{k}.tif"), dpi=(DPI, DPI), compression="tiff_lzw")
    return im.size

S6 = rd("S6_spatial_RR.csv"); assert len(S6) == 229
UNOBS = set(S6[S6["class"] == "unobserved"].sigungu_cd); assert len(UNOBS) == 1

# Fig 1 — 전국 성×연령 의심률(원표 N104/N099), 대표 연도
NA = N["nat"]; AGES = [b for b in [f"{lo}-{lo+4}" for lo in range(20, 85, 5)] + ["85+"]]
YRS = [(2011, "#9ecae1"), (2015, "#2166AC"), (2016, "#7570b3"), (2017, "#d95f02"), (2024, "#B2182B")]
fig, axs = plt.subplots(1, 2, figsize=(W, 3.6), sharey=True); fig.subplots_adjust(left=0.11, right=0.99, top=0.78, bottom=0.22, wspace=0.10)
for ax, sx, nm in zip(axs, ("남자", "여자"), ("Men", "Women")):
    for yr, col in YRS:
        v = [N["rate"][(yr, sx, a)] for a in AGES]; ax.plot(range(len(AGES)), v, color=col, lw=1.1, marker="o", ms=2.4, label=str(yr))
    ax.set_yscale("log"); ax.set_yticks([0.1, 0.2, 0.5, 1, 2, 5, 10, 20]); ax.set_yticklabels(["0.1", "0.2", "0.5", "1", "2", "5", "10", "20"]); ax.minorticks_off()
    ax.set_xticks(range(len(AGES))); ax.set_xticklabels([a.replace("-", "–") for a in AGES], rotation=90, fontsize=6.5); ax.set_xlabel("Age group, years")
    ax.set_title(nm, fontsize=8.5); ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="y", color="#e0e0e0", lw=0.4)
axs[0].set_ylabel("Anemia flagged at screening, % (log scale)")
lo_ = min(N["rate"][(y, s, a)] for y, _ in YRS for s in ("남자", "여자") for a in AGES); hi_ = max(N["rate"][(y, s, a)] for y, _ in YRS for s in ("남자", "여자") for a in AGES); assert 0.1 < lo_ and hi_ < 30, (lo_, hi_)
axs[1].legend(title="Year", loc="upper left", frameon=False, ncol=1)
letter(fig, "A", 0.005, 0.995); letter(fig, "B", 0.52, 0.995)
s1 = save(fig, 1)

# Fig 2 — (A) 잔차 공간 RR (B) 두 창 핫·콜드스팟
BR = [0, 0.67, 0.8, 0.9, 1, 1.1, 1.25, 1.5, 99]; LB = ["<0.67", "0.67–0.79", "0.80–0.89", "0.90–0.99", "1.00–1.09", "1.10–1.24", "1.25–1.49", "≥1.50"]
PAL = ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D", "#B2182B"]
assert BR[0] < N["rr_min"] < BR[2] and N["rr_max"] < 2.5
fig = plt.figure(figsize=(W, 5.0)); a0 = fig.add_axes([0.00, 0.30, 0.49, 0.60]); a1 = fig.add_axes([0.51, 0.30, 0.49, 0.60])
d = S6.set_index("sigungu_cd"); gg = G.copy(); gg["v"] = gg.cd.map(d.RR); gg["c"] = gg.cd.map(d["class"]); assert gg.v.notna().all()
obs = ~gg.cd.isin(UNOBS)
gg[obs].plot(ax=a0, column="v", cmap=ListedColormap(PAL), norm=BoundaryNorm(BR, len(PAL)), edgecolor="#a0a0a0", linewidth=LW)
gg[~obs].plot(ax=a0, color="#d9d9d9", edgecolor="#a0a0a0", linewidth=LW, hatch="////"); mapax(a0)
gg[gg.c == "coldspot"].boundary.plot(ax=a0, color="#2171B5", linewidth=0.6, linestyle=(0, (2.0, 1.2))); gg[gg.c == "hotspot"].boundary.plot(ax=a0, color="black", linewidth=0.6)
h = [Patch(facecolor=c, edgecolor="#777777", linewidth=LW, label=l) for c, l in zip(PAL, LB)] + [Patch(facecolor="none", edgecolor="black", linewidth=0.8, label="Hot spot"), Patch(facecolor="none", edgecolor="#2171B5", linewidth=0.8, linestyle="--", label="Cold spot"), Patch(facecolor="#d9d9d9", edgecolor="#777777", hatch="////", linewidth=LW, label="Not observed")]
a0.legend(handles=h, title="Residual spatial RR", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, columnspacing=0.8, handlelength=1.3)
WM = rd("S4b_window_spatialRR.csv")
nh = WM[WM["class"] == "hotspot"].groupby("sigungu_cd").size(); nc = WM[WM["class"] == "coldspot"].groupby("sigungu_cd").size()
assert int((nh == 2).sum()) == N["hot_all_windows"] and int((nc == 2).sum()) == N["cold_all_windows"]
hh = gg.cd.map(nh).fillna(0).astype(int); cc = gg.cd.map(nc).fillna(0).astype(int)
gg["k"] = np.where(~obs, 8, np.where((hh > 0) & (cc > 0), 9, hh - cc))
KP = {-2: "#2166AC", -1: "#92C5DE", 0: "#f7f7f7", 1: "#F4A582", 2: "#B2182B", 9: "#c2a5cf", 8: "#d9d9d9"}
KL = {-2: "Cold spot in both windows", -1: "Cold spot in one window", 0: "Neither", 1: "Hot spot in one window", 2: "Hot spot in both windows", 9: "Hot in one, cold in the other", 8: "Not observed"}
gg[gg.k != 8].plot(ax=a1, color=[KP[k] for k in gg[gg.k != 8].k], edgecolor="#a0a0a0", linewidth=LW); gg[gg.k == 8].plot(ax=a1, color="#d9d9d9", edgecolor="#a0a0a0", linewidth=LW, hatch="////"); mapax(a1)
kc = gg.k.value_counts()
a1.legend(handles=[Patch(facecolor=KP[k], edgecolor="#777777", linewidth=LW, hatch="////" if k == 8 else None, label=f"{KL[k]} ({kc.get(k, 0)})") for k in (2, 1, 0, -1, -2, 9, 8) if kc.get(k, 0)], title="Windows 2011–2016 and 2017–2024", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
letter(fig, "A", 0.005, 0.995); letter(fig, "B", 0.515, 0.995)
s2 = save(fig, 2)

# Fig 3 — 강건 4개 변수의 모형별 RR
LAB = {OLD: "Older adults\nliving alone", DM: "Diagnosed diabetes\namong attendees", NUT: "Nutrition-label\nliteracy", UPT: "Screening uptake"}
ORD = [OLD, DM, NUT, UPT]; assert set(ORD) == set(ROB)
MOD = [("Principal model", lambda v: (N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"]), "#000000", "o"),
       ("Knorr-Held type II (best fitting)", lambda v: N["s43"][("KH_typeII", v)][:3], "#2166AC", "s"),
       ("Knorr-Held type IV", lambda v: N["s43"][("KH_typeIV", v)][:3], "#B2182B", "D"),
       ("2011–2016 only", lambda v: N["win_irr"][(v, "W1_2011-16")][:3], "#1b7837", "v"),
       ("2017–2024 only", lambda v: N["win_irr"][(v, "W2_2017-24")][:3], "#E08214", "P"),
       ("Expected cases from resident population", lambda v: N["epop"][v][:3], "#7f7f7f", "^")]
lo_all = min(f(v)[1] for v in ORD for _, f, _, _ in MOD); hi_all = max(f(v)[2] for v in ORD for _, f, _, _ in MOD)
fig, ax = plt.subplots(figsize=(W, 3.6)); fig.subplots_adjust(left=0.20, right=0.98, top=0.97, bottom=0.26)
off = np.linspace(-0.32, 0.32, len(MOD))
for i, v in enumerate(ORD):
    for (lab, f, col, mk), o in zip(MOD, off):
        e, lo, hi = f(v); ax.plot([lo, hi], [i + o] * 2, color=col, lw=0.8); ax.plot(e, i + o, marker=mk, color=col, ms=3.4, mew=0, ls="none")
ax.axvline(1, color="#404040", lw=0.5, ls=":"); ax.set_yticks(range(len(ORD))); ax.set_yticklabels([LAB[v] for v in ORD]); ax.invert_yaxis()
xt = [0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25]; assert xt[0] <= lo_all and hi_all <= xt[-1], (lo_all, hi_all)
ax.set_xscale("log"); ax.set_xlim(xt[0], xt[-1]); ax.set_xticks(xt); ax.set_xticklabels([f"{x:.2f}" for x in xt]); ax.minorticks_off()
ax.set_xlabel("Rate ratio per 1 SD (95% credible interval, log scale)"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(handles=[Line2D([0], [0], color=c, marker=m, lw=0.8, ms=3.4, mew=0, label=l) for l, _, c, m in MOD], loc="upper center", bbox_to_anchor=(0.40, -0.16), ncol=3, frameon=False)
s3 = save(fig, 3)

# 보충 Fig S1 — EHSA
EH = rd("S11_ehsa.csv")
CATS = [f"{a} {b}" for b in ("hot", "cold") for a in ("New", "Consecutive", "Intensifying", "Persistent", "Diminishing", "Sporadic", "Oscillating", "Historical")] + ["No pattern"]
EPAL = {"New hot": "#fdd0a2", "Consecutive hot": "#fdae6b", "Intensifying hot": "#a50f15", "Persistent hot": "#de2d26", "Diminishing hot": "#fc9272", "Sporadic hot": "#fee0d2", "Oscillating hot": "#d6a5c9", "Historical hot": "#bcbddc",
        "New cold": "#c6dbef", "Consecutive cold": "#9ecae1", "Intensifying cold": "#08519c", "Persistent cold": "#3182bd", "Diminishing cold": "#6baed6", "Sporadic cold": "#deebf7", "Oscillating cold": "#a1d99b", "Historical cold": "#c7e9c0", "No pattern": "#f7f7f7"}
fig = plt.figure(figsize=(W * 0.62, 5.0)); a0 = fig.add_axes([0.02, 0.32, 0.96, 0.62])
ge = G.copy(); ge["c"] = ge.cd.map(EH.set_index("sigungu_cd").EHSA); eo = ge.c.notna(); assert (~eo).sum() == len(UNOBS)
ge[eo].plot(ax=a0, color=[EPAL[c] for c in ge[eo].c], edgecolor="#a0a0a0", linewidth=LW); ge[~eo].plot(ax=a0, color="#d9d9d9", edgecolor="#a0a0a0", linewidth=LW, hatch="////"); mapax(a0)
cnt = EH.EHSA.value_counts(); pres = [c for c in CATS if c in cnt.index]
a0.legend(handles=[Patch(facecolor=EPAL[c], edgecolor="#777777", linewidth=LW, label=f"{c} ({cnt[c]})") for c in pres], title="Category (districts)", loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2)
s4 = save(fig, "S1")
for k, s in zip((1, 2, 3, "S1"), (s1, s2, s3, s4)): print(f"Fig{k}: {s[0]}x{s[1]} px = {s[0]/DPI*25.4:.0f} x {s[1]/DPI*25.4:.0f} mm")
