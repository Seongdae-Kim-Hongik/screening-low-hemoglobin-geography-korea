# 99G — 30호 ANEM 판정 구성 대조 게이트(2026-11-18; 00_PLAYBOOK/17 「32호 KIDS 교훈」 1·2항).
#  판정 「빈혈증 질환의심」(N103·N104)을 공표 혈색소 분포(KOSIS DT_35007_N066 시도별, N067 연령별)의 판정 기준 미만 인원과 연도·성별로 대조.
#  기준(보건복지부 건강검진 실시기준 판정기준): 질환의심 남 혈색소 <12.0, 여 <10.0 g/dL; 정상B 남 12.0–12.9, 여 10.0–11.9 g/dL.
#  키 ~/.kosis_key(내용 출력 금지). 산출 04_분석/ANEM/results_std3/S0_judgement_national.csv, S0_judgement_province.csv (원본 json은 04_분석/ANEM/judgement_gate_261118/)
import os, json, csv, math, statistics as st, urllib.request, urllib.parse, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = os.path.join(ROOT, "04_분석", "ANEM"); RAW = os.path.join(A, "judgement_gate_261118"); RS = os.path.join(A, "results_std3")
SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험"); os.makedirs(RAW, exist_ok=True)
def fetch(t):
    p = os.path.join(RAW, t + ".json")
    if os.path.exists(p): return json.load(open(p))
    K = open(os.path.expanduser("~/.kosis_key")).read().strip(); out = []
    for y in range(2010, 2025):
        u = "https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(dict(method="getList", apiKey=K, orgId="350", tblId=t, itmId="ALL", objL1="ALL", objL2="ALL", objL3="ALL", format="json", jsonVD="Y", prdSe="Y", startPrdDe=str(y), endPrdDe=str(y)))
        d = json.loads(urllib.request.urlopen(u, timeout=60).read().decode()); out += d if isinstance(d, list) else []
    json.dump(out, open(p, "w"), ensure_ascii=False); return out
def load(f):
    with open(os.path.join(SRC, f), encoding="utf-8-sig") as fh: return list(csv.DictReader(fh))
num = lambda x: float(x) if x not in ("", "-", None) else None
BIN = ["10.0g/dL 미만", "10.0-10.9g/dL", "11.0-11.9g/dL", "12.0-12.9g/dL"]
def below(h, key, sx): return h[key + (BIN[0],)] + ((h[key + (BIN[1],)] + h[key + (BIN[2],)]) if sx == "M" else 0)
def border(h, key, sx): return (h[key + (BIN[3],)]) if sx == "M" else (h[key + (BIN[1],)] + h[key + (BIN[2],)])
SX = {"남자": "M", "여자": "F"}
# 전국(N067 연령별 '계')
H = collections.defaultdict(float)
for r in fetch("DT_35007_N067"):
    if r["C1_NM"] == "계" and num(r["DT"]) is not None: H[(r["PRD_DE"], r["C2_NM"], r["C3_NM"])] = num(r["DT"])
S = {(r["PRD_DE"], r["C2_NM"]): num(r["DT"]) for r in load("DT_35007_N103.csv") if r["C1_NM"] == "계" and r["C3_NM"] == "빈혈증" and num(r["DT"]) is not None}
B = {(r["PRD_DE"], r["C2_NM"]): num(r["DT"]) for r in load("DT_35007_N101.csv") if r["C1_NM"] == "계" and r["C3_NM"] == "빈혈관리" and num(r["DT"]) is not None}
nat = []
for y in map(str, range(2011, 2025)):
    for s, sx in SX.items():
        k = (y, s); tot = H[k + ("계",)]; lo = below(H, k, sx); bd = border(H, k, sx)
        nat.append(dict(year=int(y), sex=sx, hb_tested=int(tot), hb_below_cut=int(lo), hb_borderline=int(bd), flagged_suspected=int(S[k]), flagged_borderline=int(B[k]),
                        ratio_suspected=round(S[k] / lo, 4), ratio_borderline=round(B[k] / bd, 4), pct_hb_below=round(100 * lo / tot, 3), pct_flagged=round(100 * S[k] / tot, 3)))
# 시도(N066 vs N103 시도 행)
SH = {"강원특별자치도": "강원", "경기도": "경기", "경상남도": "경남", "경상북도": "경북", "광주광역시": "광주", "대구광역시": "대구", "대전광역시": "대전", "부산광역시": "부산", "서울특별시": "서울",
      "울산광역시": "울산", "인천광역시": "인천", "전라남도": "전남", "전북특별자치도": "전북", "제주특별자치도": "제주", "충청남도": "충남", "충청북도": "충북"}
P = collections.defaultdict(float)
for r in fetch("DT_35007_N066"):
    if r["C1_NM"] in SH and num(r["DT"]) is not None: P[(r["PRD_DE"], SH[r["C1_NM"]], r["C2_NM"], r["C3_NM"])] = num(r["DT"])
SP = {(r["PRD_DE"], r["C1_NM"], r["C2_NM"]): num(r["DT"]) for r in load("DT_35007_N103.csv") if len(r["C1"]) == 12 and r["C3_NM"] == "빈혈증" and num(r["DT"]) is not None}
def cor(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b); return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
prov = []
for y in map(str, range(2011, 2025)):
    for s, sx in SX.items():
        rs, fp, hp = [], [], []
        for sd in sorted(set(SH.values())):
            k = (y, sd, s)
            if k not in SP: continue
            lo = below(P, k, sx); tot = P[k + ("계",)]
            rs.append(SP[k] / lo); fp.append(100 * SP[k] / tot); hp.append(100 * lo / tot)
        prov.append(dict(year=int(y), sex=sx, n_provinces=len(rs), ratio_median=round(st.median(rs), 3), ratio_min=round(min(rs), 3), ratio_max=round(max(rs), 3),
                         ratio_cv=round(st.pstdev(rs) / st.mean(rs), 3), r_flag_vs_hb=round(cor(fp, hp), 3)))
for f, rows in (("S0_judgement_national.csv", nat), ("S0_judgement_province.csv", prov)):
    w = csv.DictWriter(open(os.path.join(RS, f), "w", encoding="utf-8"), fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print("national", len(nat), "province", len(prov))
