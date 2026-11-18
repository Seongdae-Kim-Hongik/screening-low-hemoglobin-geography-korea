# numbers_anem.py — 30호 검진 빈혈증 질환의심(ANEM) 원고의 모든 수치를 결과 CSV에서 읽는다.
#  기억·손입력 금지, assert로 정합 확인. 사용: from numbers_anem import load; N = load()
import os, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(os.path.dirname(HERE)); RS = os.path.join(B, "results_std3")
ROOT = os.path.dirname(os.path.dirname(B)); PAN = os.path.join(ROOT, "02_패널"); SRC = os.path.join(ROOT, "00_원천", "C_NHIS_검진보험")
WIN = [("W1_2011-16", 2011, 2016), ("W2_2017-24", 2017, 2024)]
rd = lambda f, **k: pd.read_csv(os.path.join(RS, f), encoding="utf-8-sig", **k)
OLD, DM, NUT, UPT = "older_single_household_share", "ext__dx_dm_share", "ext__nutrition_label_literacy", "screening_uptake"
ROB = [OLD, DM, NUT, UPT]
SHP = os.environ.get("ST_SHP", os.path.join(HERE, "..", "..", "..", "..", "data", "boundary", "final.shp"))
HYP = ["basic_livelihood_rate", "tertiary_educated_share", NUT, OLD, "multicultural_marriage_share", "ext__total_fertility_rate", DM,
       "current_smoking_rate", "high_risk_drinking_rate", "walking_practice_rate", "moderate_pa_rate", "im_specialists_per_100k", UPT]
FORCED = ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"]
LOG1P = {"im_specialists_per_100k"}   # sets transform log1p: 패널 _raw는 변환 척도 → 표 1은 원척도(expm1)
BANDS = ["0-19"] + [f"{lo}-{lo+4}" for lo in range(20, 85, 5)] + ["85+"]

def _band(a):
    a = str(a).replace(" ", "")
    if a == "19세이하": return "0-19"
    if a == "85세이상": return "85+"
    if a.endswith("세") and "~" in a:
        lo, hi = a[:-1].split("~"); return f"{lo}-{hi}"
    return None

def national():   # 전국 성×연령 의심률(분모 N099 '계', 분자 N104 00307) — 99A2와 같은 원표
    A = pd.read_csv(os.path.join(SRC, "DT_35007_N099_national_long.csv"), encoding="utf-8-sig"); A = A[(A.grp == "계") & A.year.between(2011, 2024)]
    Bn = pd.read_csv(os.path.join(SRC, "DT_35007_N104_national_long.csv"), encoding="utf-8-sig", dtype={"grp_code": str}); Bn = Bn[(Bn.grp_code == "00307") & Bn.year.between(2011, 2024)]
    for X in (A, Bn): X["band"] = X.age.map(_band)
    ex = A[A.band.notna() & A.sex.isin(["남자", "여자"])].groupby(["year", "sex", "band"]).value.sum()
    nu = Bn[Bn.band.notna() & Bn.sex.isin(["남자", "여자"])].groupby(["year", "sex", "band"]).value.sum()
    D = pd.concat({"exam": ex, "cases": nu}, axis=1).fillna(0).reset_index(); D["rate"] = 100 * D.cases / D.exam
    return D

def load():
    N = {}
    P = pd.read_csv(os.path.join(B, "panel_ANEM_std3.csv")); N["n_rows"] = len(P); N["n_districts"] = P.fbd_region.nunique()
    assert (N["n_rows"], N["n_districts"]) == (3192, 228)
    E = pd.read_csv(os.path.join(PAN, "ANEM_Estd3.csv"))
    assert int(E.cases.sum()) == int(P.cases.sum()) and abs(E.examinees.sum() - P.offset.sum()) < 1
    N["cases_total"] = int(P.cases.sum()); N["exam_total"] = float(E.examinees.sum())
    y = E.groupby("year")[["examinees", "cases"]].sum(); N["pos_y"] = (100 * y.cases / y.examinees).to_dict(); N["exam_y"] = y.examinees.to_dict()
    NA = national(); N["nat"] = NA
    ny = NA.groupby("year")[["exam", "cases"]].sum(); N["nat_pos_y"] = (100 * ny.cases / ny.exam).to_dict()
    nsx = NA.groupby(["year", "sex"])[["exam", "cases"]].sum(); N["nat_pos_sex"] = (100 * nsx.cases / nsx.exam).to_dict()
    r = NA.set_index(["year", "sex", "band"]).rate; N["rate"] = r.to_dict()
    old = NA[NA.band.isin(["55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85+"])]
    o = old.groupby(["year", "sex"])[["exam", "cases"]].sum(); o = 100 * o.cases / o.exam; N["old_rate"] = o.to_dict()
    N["drop1617"] = {s: 100 * (o[(2017, s)] / o[(2016, s)] - 1) for s in ("남자", "여자")}
    N["estd_ecrude"] = (float((E.E_std / E.E_crude).min()), float((E.E_std / E.E_crude).max()))
    N["rho_std_pop"] = float(E[["SIR_std", "SIR_pop"]].corr(method="spearman").iloc[0, 1])
    T1 = {}
    for wn, a, b in WIN + [("2011-2024", 2011, 2024)]:
        q = P[(P.year >= a) & (P.year <= b)]; e = E[(E.year >= a) & (E.year <= b)]
        sir = q.groupby("fbd_region").apply(lambda d: d.cases.sum() / d.E.sum(), include_groups=False)
        T1[wn] = dict(n=len(q), cases=int(q.cases.sum()), exam=float(e.examinees.sum()), pos=100 * q.cases.sum() / e.examinees.sum(),
                      sir_p10=sir.quantile(.1), sir_p90=sir.quantile(.9), sir_med=sir.median(),
                      cov={v: ((lambda x: (x.mean(), x.std()))(np.expm1(q[f"{v}_raw"]) if v in LOG1P else q[f"{v}_raw"])) for v in HYP + FORCED})
    N["T1"] = T1
    s6m = rd("S6_moran_year.csv"); N["moran_year_min"], N["moran_year_max"] = s6m.moran_I.min(), s6m.moran_I.max()
    r8 = rd("S8_residual_moran.csv").set_index("quantity"); N["moran_pooled"] = r8.loc["observed_logSIR_pooled", "moran_I"]
    N["moran_resid"] = r8.loc["pearson_residual_area_mean", "moran_I"]; N["moran_resid_p"] = r8.loc["pearson_residual_area_mean", "p_perm"]
    h = rd("S3_main_hyper.csv"); ph = h[h.hyperpar.str.startswith("Phi")].iloc[0]; N["phi"] = (ph["mean"], ph["X0.025quant"], ph["X0.975quant"])
    s6 = rd("S6_spatial_RR.csv"); s6o = s6[s6["class"] != "unobserved"]; assert len(s6o) == 228
    N["rr_min"], N["rr_max"] = s6o.RR.min(), s6o.RR.max()
    N["n_hot"], N["n_cold"] = int((s6["class"] == "hotspot").sum()), int((s6["class"] == "coldspot").sum())
    sido = s6.fbd_region.str.extract(r"^(\S+?(?:도|시))")[0]
    N["hot_by_sido"] = s6[s6["class"] == "hotspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    N["cold_by_sido"] = s6[s6["class"] == "coldspot"].groupby(sido).size().sort_values(ascending=False).to_dict()
    gu = s6.fbd_region.str.endswith("구"); N["cold_gu"] = int(((s6["class"] == "coldspot") & gu).sum()); N["hot_gun"] = int(((s6["class"] == "hotspot") & s6.fbd_region.str.endswith("군")).sum())
    N["n_gun"] = int(s6.fbd_region.str.endswith("군").sum())
    wm = rd("S4b_window_spatialRR.csv"); N["win_hot"] = wm[wm["class"] == "hotspot"].groupby("window").size().to_dict(); N["win_cold"] = wm[wm["class"] == "coldspot"].groupby("window").size().to_dict()
    hs = {w: set(wm[(wm.window == w) & (wm["class"] == "hotspot")].fbd_region) for w in wm.window.unique()}; N["hot_all_windows"] = len(set.intersection(*hs.values()))
    cs = {w: set(wm[(wm.window == w) & (wm["class"] == "coldspot")].fbd_region) for w in wm.window.unique()}; N["cold_all_windows"] = len(set.intersection(*cs.values()))
    pe = rd("S12_persistence.csv").set_index("set"); N["kendall_W"] = pe.loc["2011-2024", "kendall_W"]
    N["ehsa"] = rd("S11_ehsa_summary.csv").set_index("category").n.to_dict()
    m3 = rd("S3_main_IRR.csv").set_index("cov"); N["main"] = m3[["IRR", "lo", "hi", "cred", "role", "label_en", "P_gt1"]].to_dict("index")
    assert set(m3.index) == set(HYP + FORCED)
    N["n_hyp"] = int((m3.role == "hypothesis").sum()); N["n_cred_hyp"] = int(((m3.role == "hypothesis") & m3.cred).sum())
    s7 = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = s7[["n_specs", "cred_frac", "sign_agree", "robust"]].to_dict("index")
    N["n_robust"] = int(s7.robust.sum()); assert set(s7.index[s7.robust]) == set(ROB), s7.index[s7.robust].tolist()
    hb = open(os.path.join(B, "HM_best_ANEM_std3.txt")).read(); N["waic_forced"] = float(hb.split("ref_forced_only_WAIC=")[1].split()[0])
    N["waic_main"] = float(hb.split("S1_narrative_full(")[1].split(",")[0])
    lk = rd("S1_likelihood.csv"); lk = lk[lk.set == "REF_forced_only"].set_index("family").WAIC; N["waic_pois"], N["waic_nb"] = float(lk["poisson"]), float(lk["nbinomial"])
    nc = rd("S3_negcontrol.csv").set_index("cov"); N["negctl"] = nc[["IRR", "lo", "hi", "cred"]].to_dict("index")
    wi = rd("S4_window_IRR.csv"); N["win_irr"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, r.cred) for r in wi.itertuples()}
    it = rd("S4_interaction.csv"); N["win_int"] = {r.cov: (r.IRR_ratio, r.lo, r.hi, bool(r.cred)) for r in it.itertuples()}; N["n_win_int"] = int(it.cred.sum()); N["win_int_cov"] = it[it.cred]["cov"].tolist()
    S43 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S43_part_*.csv"))]); N["s43"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S43.itertuples()}
    N["s43_waic"] = S43.groupby("analysis").WAIC.first().to_dict()
    T9 = rd("S9_typeI_IRR.csv"); N["s43"].update({("KH_typeI", r.cov): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in T9.itertuples()}); N["s43_waic"]["KH_typeI"] = float(T9.WAIC.iloc[0])
    S41 = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RS, "S41_part_*.csv"))]); N["s41"] = {(r.analysis, r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in S41.itertuples()}
    N["s41_waic"] = S41.groupby("analysis").WAIC.first().to_dict()
    N["retention"] = rd("S41_retention_by_cov.csv").set_index("cov").to_dict("index"); N["rubin"] = rd("S41_noise_rubin.csv").set_index("cov").to_dict("index")
    N["evalue"] = rd("S41_evalues.csv").set_index("cov").to_dict("index"); N["oos"] = rd("S41_oos2024.csv").iloc[0].to_dict()
    N["ppc"] = rd("S42_ppc.csv").iloc[0].to_dict(); N["varpart"] = rd("S42_variance_partition.csv").set_index("component").to_dict("index")
    N["nco"] = {(r.analysis.replace("H1_nco_", ""), r.cov): (r.IRR, r.lo, r.hi, r.cred) for r in rd("S41_nco_detail.csv").itertuples()}
    N["bw"] = {r.cov: (r.IRR, r.lo, r.hi, r.cred) for r in S41[S41.analysis == "bw_twoway"].itertuples()}
    N["drop_prov_min"] = int(S41[S41.analysis.str.startswith("F1_")].groupby("analysis").robust_kept.first().min())
    N["drop_year_min"] = int(S41[S41.analysis.str.startswith("F2_")].groupby("analysis").robust_kept.first().min())
    N["lag"] = {a: int(S41[S41.analysis == a].robust_kept.iloc[0]) for a in ("E1_lag1", "E2_lag2")}
    so = rd("S10_offset_sensitivity_IRR.csv"); N["epop"] = {r.cov: (r.IRR, r.lo, r.hi, bool(r.cred)) for r in so.itertuples()}
    N["sens_main"] = {}
    for v in ["s577", "s2", "s8"]:
        m = pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_IRR.csv")).set_index("cov"); N["sens_main"][v] = {c: (m.loc[c, "IRR"], m.loc[c, "lo"], m.loc[c, "hi"], bool(m.loc[c, "cred"])) for c in m.index}
    N["s50_moran"] = rd("S50_resid_moran_by_spec.csv").set_index("spec").to_dict("index")
    cv = rd("S5_covid.csv"); N["covid_nint"] = int(cv[(cv.term == "var_x_post") & cv.cred].shape[0])
    # 사후 검정(역방향): 시군구 평균 수준 순위상관과 지역 내 연도 편차 상관(결과요약 261112와 같은 계산)
    P["logSIR"] = np.log((P.cases + 0.5) / P.E)
    cols = [f"{v}_raw" for v in (UPT, "basic_livelihood_rate", "ext__total_fertility_rate", OLD, "pop80_share", "urban_population_share")] + ["logSIR"]
    M_ = P.groupby("fbd_region")[cols].mean(); C_ = M_.corr(method="spearman")
    N["rho_between"] = {c.replace("_raw", ""): float(C_.loc[c, "logSIR"]) for c in cols[:-1]}
    N["rho_bl_old"] = float(C_.loc["basic_livelihood_rate_raw", f"{OLD}_raw"]); N["rho_bl_pop80"] = float(C_.loc["basic_livelihood_rate_raw", "pop80_share_raw"])
    N["rho_tfr_urban"] = float(C_.loc["ext__total_fertility_rate_raw", "urban_population_share_raw"])
    W_ = P[[f"{UPT}_raw", "logSIR", "fbd_region", "year"]].copy()
    for c in (f"{UPT}_raw", "logSIR"): W_[c] = W_[c] - W_.groupby("fbd_region")[c].transform("mean") - W_.groupby("year")[c].transform("mean") + W_[c].mean()
    N["rho_within_upt"] = float(W_[[f"{UPT}_raw", "logSIR"]].corr(method="spearman").iloc[0, 1])
    vif = pd.read_csv(os.path.join(B, "panel_META_ANEM_std3.csv")) if os.path.exists(os.path.join(B, "panel_META_ANEM_std3.csv")) else None
    N["vif"] = vif
    if vif is not None: _v = vif.set_index("variable").vif_final; N["vif_old"], N["vif_80"] = float(_v[OLD]), float(_v["pop80_share"])
    # 판정 구성 대조 게이트(2026-11-18, 99G·81W)
    jn = rd("S0_judgement_national.csv"); jp = rd("S0_judgement_province.csv")
    N["jn"] = {(int(r.year), r.sex): r._asdict() for r in jn.itertuples()}
    rg = lambda sx, y0, y1: (float(jn[(jn.sex == sx) & jn.year.between(y0, y1)].ratio_suspected.min()), float(jn[(jn.sex == sx) & jn.year.between(y0, y1)].ratio_suspected.max()))
    N["jr"] = {"M_1112": rg("M", 2011, 2012), "M_1317": rg("M", 2013, 2017), "M_1824": rg("M", 2018, 2024), "F_1117": rg("F", 2011, 2017), "F_1824": rg("F", 2018, 2024),
                "M_1314": rg("M", 2013, 2014), "M_1517": rg("M", 2015, 2017), "F_1114": rg("F", 2011, 2014), "F_1517": rg("F", 2015, 2017)}
    N["jcv_max"] = float(jp.ratio_cv.max()); N["jcv_min"] = float(jp.ratio_cv.min())
    N["jr_M"] = (float(jp[jp.sex == "M"].r_flag_vs_hb.min()), float(jp[jp.sex == "M"].r_flag_vs_hb.max())); N["jr_F"] = (float(jp[jp.sex == "F"].r_flag_vs_hb.min()), float(jp[jp.sex == "F"].r_flag_vs_hb.max()))
    N["hb1617"] = {sx: (N["jn"][(2016, sx)]["pct_hb_below"], N["jn"][(2017, sx)]["pct_hb_below"], N["jn"][(2016, sx)]["ratio_suspected"], N["jn"][(2017, sx)]["ratio_suspected"]) for sx in ("M", "F")}
    jw = rd("S4j_judgement_windows_IRR.csv"); N["jwin"] = {(r.cov, r.window): (r.IRR, r.lo, r.hi, bool(r.cred)) for r in jw.itertuples()}
    N["jwin_n"] = {r.window: int(r.n_obs) for r in jw.itertuples()}
    return N

if __name__ == "__main__":
    N = load()
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items() if not isinstance(v, (dict, list, pd.DataFrame)) and v is not None})
    print("hot_by_sido", N["hot_by_sido"]); print("cold_by_sido", N["cold_by_sido"]); print("ehsa", N["ehsa"]); print("win", N["win_hot"], N["win_cold"])
    print("nat_pos_y", {k: round(v, 2) for k, v in N["nat_pos_y"].items()}); print("pos_y", {k: round(v, 2) for k, v in N["pos_y"].items()})
    print("drop1617", N["drop1617"]); print("KH WAIC", {k: v for k, v in N["s43_waic"].items() if "KH" in k}, "main", N["waic_main"])
    print("rho_between", N["rho_between"], "within upt", N["rho_within_upt"]); print("lag", N["lag"], "drop prov/year min", N["drop_prov_min"], N["drop_year_min"])
    print("win_int", N["win_int_cov"]); print("ppc", N["ppc"]); print("nat 85+ M", {y: round(N["rate"][(y, "남자", "85+")], 1) for y in (2011, 2016, 2017, 2024)})
    print("F 40-44/45-49", {y: (round(N["rate"][(y, "여자", "40-44")], 1), round(N["rate"][(y, "여자", "45-49")], 1)) for y in (2011, 2024)})
