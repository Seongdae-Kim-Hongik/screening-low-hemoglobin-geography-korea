# esm_anem.py — JAH Supplemental material(Appendix S1-S9, 본문 첫 인용 순서; S2 판정 대조 신설 2026-11-18) + STROBE(S9). 수치는 결과 CSV에서만. 이중 익명 → 저자 정보 없음, 미국식 철자.
#  단일 익명이지만 보충 파일은 저자 정보 없이 제목만. 영국식 철자(TX._emit에서 brit 적용).
import os, json, subprocess, pandas as pd
from docx.shared import Cm
import content_anem as C
from build_jah_anem import LABEL, GROUPS, TX, TITLE as DTITLE, foot_row, EXPECT
from american import amer as brit
HERE = os.path.dirname(os.path.abspath(__file__)); MSD = os.path.dirname(HERE); OUT = os.path.join(MSD, "out"); B = os.path.dirname(MSD); RS = os.path.join(B, "results_std3")
N = C.N
f3 = lambda t: f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
B1 = "Intervals with a bound shown as 1.000 were classified from unrounded values."
ROBV = [C.OLD, C.DM, C.NUT, C.UPT]
SH = {C.OLD: "Living alone", C.DM: "Diagnosed diabetes", C.NUT: "Nutrition-label literacy", C.UPT: "Screening uptake"}
J = TX(cite="ay")
_NB = [False]
def TF(title, header, rows, foot="", fs=8, fixed=1, per=None):
    title = brit(title); header = [brit(h) for h in header]; rows = [[brit(x) for x in r] for r in rows]
    if per is None or len(header) - fixed <= per:
        (None if _NB[0] else J.page_break()); _NB[0] = False; J.table_fit(title, header, rows, "", fs_max=fs)
        if foot: foot_row(J, foot, 8, 12)
        return
    rest = list(range(fixed, len(header))); chunks = [rest[i:i + per] for i in range(0, len(rest), per)]
    _f = _NB[0]; _NB[0] = False
    for n, ch in enumerate(chunks):
        cols = list(range(fixed)) + ch; tt = f"{title} (part {'ABCD'[n]})"
        rr = [r if r and r[0] == "__H__" else [r[c] for c in cols] for r in rows]
        (None if (_f and n == 0) else J.page_break()); J.table_fit(tt, [header[c] for c in cols], rr, "", fs_max=fs)
        if foot: foot_row(J, foot, 8, 12)
J.para("<b>Supplemental material</b>"); J.para(f"Article title: {DTITLE}"); J.para("Journal: Journal of Aging and Health")
J.para("Contents: Appendix S1 (supplementary methods); Appendix S2 (judgement criterion and reconciliation with the haemoglobin distribution); Appendix S3 (covariates); Appendix S4 (panel checks); Appendix S5 (persistence, Figure S1); Appendix S6 (windows and the COVID-19 period); Appendix S7 (robustness, comparison outcomes, negative controls and model checks); Appendix S8 (post hoc analyses); Appendix S9 (STROBE checklist).")
_MT = pd.read_csv(os.path.join(B, "panel_META_ANEM_std3.csv"), encoding="utf-8-sig").set_index("variable")
_imp = lambda v: int(_MT.loc[v, "n_imputed_interp"] + _MT.loc[v, "n_imputed_sgg_mean"] + _MT.loc[v, "n_imputed_year_mean"])
# Appendix 1
J.page_break(); J.head("Appendix S1. Supplementary methods", 2)
SM = [("Outcome and denominator.", f"The national statistics portal publishes, for each year, the number of general health screening records with a recorded judgement and the number flagged as suspected anaemia by administrative district, and the same numbers nationally by sex and age group (19 years or younger, 5-year groups from 20–24 to 80–84 years, and 85 years or older). District rows were harmonised to the 2024 boundary set; seven missing district-year cells in the master panel (one city in 2016 and three cities in 2011–2012) were filled from the sum of the ward rows of the same source table, which matched the reference database in every overlapping cell. Sejong was reported separately in only 1 of 14 years and was kept in the adjacency graph but not modelled. District sums were 99.1–99.8% of national totals in each year."),
      ("Standardisation.", f"Expected numbers E = Σ over sex s and age a of (estimated attendees in s and a) × (national positivity in s and a in the same year), where estimated attendees are the resident population in s and a multiplied by national uptake in s and a, rescaled within each district, year and sex to the observed number of attendees. The ratio of standardised to crude expected numbers ranged from {N['estd_ecrude'][0]:.2f} to {N['estd_ecrude'][1]:.2f} across district-years. In the population-based sensitivity analysis, expected numbers were computed from the resident population instead of attendees (Spearman correlation of district-year ratios {N['rho_std_pop']:.2f}). National positivity among people aged 55 years or older fell by about a fifth to over a quarter between 2016 and 2017 and rose among older men between 2012 and 2013; using year-specific national positivity accounts for these nationwide changes in the reference rates but does not remove district-specific changes in selection or measurement; the calendar windows were set at the 2016–2017 change."),
      ("Covariates.", "Community Health Survey indicators (smoking, drinking, walking, moderate-or-vigorous physical activity and nutrition-label literacy) are age-standardised district estimates. Diagnosed diabetes is the share of general health screening attendees reporting diagnosed or treated diabetes. Tertiary education is the census share of adults with tertiary education (2015 and 2020, interpolated and held at the 2020 value thereafter). The share of older adults living alone is the share of households consisting of one person aged 65 years or older (observed from 2015; earlier years filled with the district mean). Basic livelihood security values for 2021–2023 that fell below 20% or above five times the mean of 2020 and 2024 (33 cells in 11 districts) were treated as missing and interpolated within districts. Screening uptake is the general health screening uptake among people eligible for the programme. Internal medicine specialists per 100,000 population entered on a log(1+x) scale."),
      ("Models.", f"Software: R 4.6.0 with R-INLA; Python 3.9 for data preparation, emerging hot spot analysis and figures. Negative binomial likelihood, chosen because its widely applicable information criterion (WAIC) for the forced-controls model was lower than that of a Poisson likelihood ({N['waic_nb']:,.1f} vs {N['waic_pois']:,.1f}); log expected numbers as offset; Besag–York–Mollié 2 (BYM2) district effect with penalised-complexity priors (P(σ>0.5)=0.01; P(φ<0.5)=2/3); first-order random-walk and independent year effects. District adjacency was taken from an audited 593-edge contact graph with island districts linked to the nearest mainland district. Knorr-Held interactions were fitted on the full 229-district graph with Sejong unobserved (3,192 observed district-years)."),
      ("Post hoc analyses.", "The decomposition into district means and two-way-centred deviations was planned. After the principal results were seen, covariates associated against their expected direction (screening uptake, basic livelihood security and the total fertility rate) were examined with Spearman correlations of district means of the covariate and the log ratio, correlations with related covariates, and within-district correlations after removing district and year means. These analyses did not change the principal model.")]
for h, x in SM: J.para(f"<b>{h}</b> {x}")
# Appendix 2 판정 구성 대조(2026-11-18)
JN = pd.read_csv(os.path.join(RS, "S0_judgement_national.csv")); JP = pd.read_csv(os.path.join(RS, "S0_judgement_province.csv")).set_index(["year", "sex"])
J.page_break(); J.head("Appendix S2. Judgement criterion and reconciliation with the haemoglobin distribution", 2)
J.para("<b>Criterion.</b> Under the Ministry of Health and Welfare's standards for health screening (Appendix 4, criteria for judging general health screening results), haemoglobin is judged normal at 13.0–16.5 g/dL in men and 12.0–15.5 g/dL in women, borderline at 12.0–12.9 g/dL in men and 10.0–11.9 g/dL in women, and suspected anaemia below 12.0 g/dL in men and below 10.0 g/dL in women. No other test enters the anaemia judgement, and there is no upper threshold.")
J.para("<b>Reconciliation.</b> The national statistics portal publishes the distribution of measured haemoglobin at general health screening in 1-g/dL bands by province and sex (DT_35007_N066) and by sex and age group (DT_35007_N067). For each year and sex, the number flagged as suspected anaemia (DT_35007_N103 national and provincial rows) was divided by the number of attendees with haemoglobin below the threshold for suspected anaemia (Table S1), and the same ratio was computed in each of the 16 provinces outside Sejong (Table S2). The principal model was then refitted after excluding 2011–2012 and separately to 2013–2017 and 2018–2024, either side of the largest step in the ratio (Table S3). The ratio also fell in 2015 (men 0.97 to 0.92; women 1.08 to 1.00), so the period-restricted refits are not free of steps.")
rows = [[str(int(r.year)), "Men" if r.sex == "M" else "Women", f"{r.hb_tested:,}", f"{r.hb_below_cut:,}", f"{r.flagged_suspected:,}", f"{r.ratio_suspected:.3f}", f"{r.pct_hb_below:.2f}", f"{r.pct_flagged:.2f}", f"{r.ratio_borderline:.3f}"] for r in JN.sort_values(["sex", "year"]).itertuples()]
TF("Table S1. Records flagged as suspected anaemia and records with haemoglobin below the threshold, national, by year and sex", ["Year", "Sex", "Haemoglobin measured", "Below threshold", "Flagged", "Flagged / below", "Below, %", "Flagged, %", "Borderline flag / band"], rows,
   "Threshold for suspected anaemia: haemoglobin below 12.0 g/dL in men and below 10.0 g/dL in women. Borderline flag / band: records flagged borderline for anaemia divided by records with haemoglobin of 12.0–12.9 g/dL in men and 10.0–11.9 g/dL in women. Flagged, % and Below, % use the number with haemoglobin measured as the denominator; national positivity in the main text uses records with a recorded judgement (DT_35007_N099). Sources: KOSIS DT_35007_N067, N101 and N103.", fs=8)
rows = [[str(int(y)), "Men" if sx == "M" else "Women", f"{r.ratio_median:.3f}", f"{r.ratio_min:.3f}–{r.ratio_max:.3f}", f"{r.ratio_cv:.3f}", f"{r.r_flag_vs_hb:.3f}"] for (y, sx), r in JP.sort_index(level=[1, 0]).iterrows()]
TF("Table S2. Ratio of flagged to below-threshold records across 16 provinces, by year and sex", ["Year", "Sex", "Median ratio", "Range", "Coefficient of variation", "r, flagged % vs below %"], rows,
   "r, Pearson correlation across provinces between the percentage flagged and the percentage with haemoglobin below the threshold. Sejong excluded. Source: KOSIS DT_35007_N066 and N103.", fs=8)
JWT = pd.read_csv(os.path.join(RS, "S4j_judgement_windows_IRR.csv")).set_index(["cov", "window"]); JWN = ("J2_2013_17", "J3_2018_24", "J23_2013_24")
rows = []
for g, vs in GROUPS[:-1]:
    rows.append(["__H__", g])
    for v in vs: rows.append([f"  {LABEL[v]}", f3(tuple(N["main"][v][x] for x in ("IRR", "lo", "hi")))] + [f3(tuple(JWT.loc[(v, w), ["IRR", "lo", "hi"]])) for w in JWN])
TF("Table S3. Rate ratios for the hypothesis covariates in the principal model and in period-restricted refits", ["Covariate", "2011–2024 (principal)", "2013–2017", "2018–2024", "2013–2024"], rows,
   f"Rate ratio per 1 standard deviation (95% credible interval). Same covariates, forced controls, likelihood and random effects as the principal model; district-years: principal {N['n_rows']:,}; 2013–2017 {N['jwin_n']['J2_2013_17']:,}; 2018–2024 {N['jwin_n']['J3_2018_24']:,}; 2013–2024 {N['jwin_n']['J23_2013_24']:,}. 2011–2012 were excluded because the ratio of flagged to below-threshold records was about 0.8 in men. " + B1, fs=7.5, fixed=1, per=2)
# Appendix 3
J_SETS = json.load(open(os.path.join(B, "sets_ANEM_std3.json"), encoding="utf-8"))
MAPV = {_MT.loc[v, "source_column"]: v for v in _MT.index}
SRC = {"kchs": "KCHS", "chk": "NHIS screening", "eloc": "KOSIS", "ext": "KOSIS", "nhis": "NHIS"}
EXTSRC = {"ext__pop80_share": "Population registry", "ext__tertiary_educated_share": "Census", "ext__basic_livelihood_rate": "KOSIS", "ext__dx_dm_share": "NHIS screening", "ext__total_fertility_rate": "Vital statistics", "ext__im_specialists_per100k": "HIRA"}
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = _MT.loc[v]; sc = str(m.source_column); src = EXTSRC.get(sc, SRC.get(sc.split("__")[0], sc.split("__")[0]))
        rows.append([f"  {LABEL[v]}", src, f"{int(m.obs_year_min)}–{int(m.obs_year_max)}", EXPECT.get(v, "NA"), f"{_imp(v):,}", f"{m.vif_final:.1f}"])
J.page_break(); J.head("Appendix S3. Covariates", 2); _NB[0] = True
TF("Table S4. Source, observed years, expected direction, filled cells and variance inflation factor for each covariate", ["Covariate", "Source", "Years", "Direction", "Filled", "VIF"], rows,
   f"HIRA, Health Insurance Review and Assessment Service; KCHS, Community Health Survey; KOSIS, Korean Statistical Information Service; NHIS, National Health Insurance Service; NA, no direction specified (forced control); Filled, filled cells of {N['n_rows']:,} district-years; VIF, variance inflation factor in the full covariate set (values above 10 were reported and retained). Directions were recorded before covariate models were fitted. Tertiary education was observed in the 2015 and 2020 censuses, interpolated between them and held at the nearest census value outside 2015–2020; 33 basic livelihood security cells (2021–2023) were set to missing and interpolated before panel construction. These cells are not counted as filled.", fs=7.5)
# Appendix 3
J.page_break(); J.head("Appendix S4. Panel checks before modelling", 2); _NB[0] = True
rows = [["Year with all districts zero or missing", "≥98% of districts in a year", "1 (COVID-19 period indicator)", "None (indicator by design)"],
                ["Year means differ twofold or more", "Largest/smallest positive yearly mean ≥2", "Standardised columns with yearly means near 0", "Original-scale columns checked; retained"],
        ["Ratio-type column above 100", "Maximum >100 for a rate or ratio", "1 (sex ratio, men per 100 women)", "Retained (definition)"],
        ["Missing district-years", "No observation", f"{sum(json.load(open(os.path.join(RS, 'S41_imputed_cells.json'))).values()):,} cells", "Filled within districts; perturbation sensitivity"],
        ["Outcome reconstruction", "District sums against national totals", "District sums 99.1–99.8% of national totals", "None"],
        ["Implausible source value", "2021–2023 value <20% or >5 times adjacent mean", "Basic livelihood security, 33 cells", "Set to missing and interpolated"]]
TF("Table S5. Panel checks: rules, thresholds, flags and actions", ["Check", "Threshold", "Flags in this panel", "Action"], rows, f"Checks were run on the analytic panel ({N['n_rows']:,} district-years) before any covariate model was fitted.", fs=8)
# Appendix 4
_T1 = N["T1"]; _eh = N["ehsa"]
J.page_break(); J.head("Appendix S5. Persistence of the district pattern", 2)
J.para(f"The 10th–90th percentile range of district anaemia ratios was {_T1['W1_2011-16']['sir_p10']:.2f}–{_T1['W1_2011-16']['sir_p90']:.2f} in 2011–2016 and {_T1['W2_2017-24']['sir_p10']:.2f}–{_T1['W2_2017-24']['sir_p90']:.2f} in 2017–2024. "
       f"Hot spots numbered {N['win_hot']['W1_2011-16']} and {N['win_hot']['W2_2017-24']}, and cold spots {N['win_cold']['W1_2011-16']} and {N['win_cold']['W2_2017-24']}, in the two windows; Kendall's W of annual district rankings of empirical Bayes-smoothed ratios was {N['kendall_W']:.2f}. "
       f"Emerging hot spot analysis classified the 228 districts as follows: " + "; ".join(f"{k.lower()} {v}" for k, v in _eh.items() if v) + f" (Figure S1).")
_pp = J.para(""); _pp.add_run().add_picture(os.path.join(HERE, "figs", "Fig_S1.png"), width=Cm(11))
J.para("<b>Figure S1.</b> Emerging hot spot analysis (Getis–Ord Gi* with Mann–Kendall trend) of empirical Bayes-smoothed anaemia ratios, 2011–2024; numbers of districts in parentheses. Sejong (hatched) was excluded.")
# Appendix 5
WI = pd.read_csv(os.path.join(RS, "S4_window_IRR.csv")).set_index(["cov", "window"]); IT = pd.read_csv(os.path.join(RS, "S4_interaction.csv")).set_index("cov")
CV = pd.read_csv(os.path.join(RS, "S5_covid.csv")); CVX = CV[CV.term == "var_x_post"].set_index("cov")
rows = []
for g, vs in GROUPS[:-1]:
    rows.append(["__H__", g])
    for v in vs: rows.append([f"  {LABEL[v]}"] + [f3(tuple(WI.loc[(v, w), ["IRR", "lo", "hi", "cred"]])) for w in ("W1_2011-16", "W2_2017-24")] + [f3(tuple(IT.loc[v, ["IRR_ratio", "lo", "hi", "cred"]])), f3(tuple(CVX.loc[v, ["IRR", "lo", "hi", "cred"]]))])
J.page_break(); J.head("Appendix S6. Calendar windows and the COVID-19 period", 2); _NB[0] = True
TF("Table S6. Rate ratios for the hypothesis covariates by calendar window and interactions with the window and with the COVID-19 period", ["Covariate", "2011–2016", "2017–2024", "Ratio, 2017–2024 vs 2011–2016", "Interaction with 2020 onwards"], rows,
   "Rate ratio per 1 standard deviation (95% credible interval). Window columns: principal model structure fitted separately to each window with all forced controls. Ratio: window interaction in a single model. Interaction with 2020 onwards: ratio of the rate ratio from 2020 onwards to that before 2020. " + B1, fs=7.5, fixed=1, per=2)
# Appendix 6
LO = pd.read_csv(os.path.join(RS, "S41_leaveout_ranges.csv")).set_index(["set", "cov"])
def rrow(lab, fn): return [lab] + [fn(v) for v in ROBV]
rows = [rrow("Subsets credible / same sign, %", lambda v: f"{100*N['mv'][v]['cred_frac']:.0f} / {100*N['mv'][v]['sign_agree']:.0f}"),
        rrow(f"{N['retention'][C.OLD]['n_specs']} alternative, province and year fits retained", lambda v: f"{N['retention'][v]['kept']}/{N['retention'][v]['n_specs']}"),
        rrow("Leave-one-province retained", lambda v: f"{LO.loc[('province', v), 'n_cred_same_sign']}/{LO.loc[('province', v), 'n']}"),
        rrow("Leave-one-year retained", lambda v: f"{LO.loc[('year', v), 'n_cred_same_sign']}/{LO.loc[('year', v), 'n']}"),
        rrow("Perturbed filled values, pooled RR", lambda v: f"{N['rubin'][v]['IRR_pooled']:.3f} ({N['rubin'][v]['lo']:.3f}–{N['rubin'][v]['hi']:.3f})"),
        rrow("Sex ignored in expected numbers", lambda v: f3(N["sens_main"]["s8"][v])),
        rrow("Share aged 80+ omitted", lambda v: f3(N["sens_main"]["s2"][v])),
        rrow("Queen contiguity graph", lambda v: f3(N["sens_main"]["s577"][v])),
        rrow("Expected numbers from residents", lambda v: f3(N["epop"][v])),
        rrow("Knorr-Held type I", lambda v: f3(N["s43"][("KH_typeI", v)])),
        rrow("Knorr-Held type III", lambda v: f3(N["s43"][("KH_typeIII", v)])),
        rrow("District mean (between)", lambda v: f3(N["bw"][v + "__between"])),
        rrow("Two-way-centred deviation (within)", lambda v: f3(N["bw"][v + "__within"])),
        rrow("Gastric cancer care (comparison outcome)", lambda v: f3(N["nco"][("GCA", v)])),
        rrow("Infectious disease care (comparison outcome)", lambda v: f3(N["nco"][("INFECT", v)])),
        rrow("Covariates lagged 1 year", lambda v: f3(N["s41"][("E1_lag1", v)])),
        rrow("Covariates lagged 2 years", lambda v: f3(N["s41"][("E2_lag2", v)])),
        rrow("E-value, point / limit", lambda v: f"{N['evalue'][v]['E_point']:.2f} / {N['evalue'][v]['E_limit']:.2f}")]
J.page_break(); J.head("Appendix S7. Robustness, comparison outcomes, negative controls and model checks", 2); _NB[0] = True
TF("Table S7. Robustness of the four subset-stable district characteristics", ["Analysis"] + [SH[v] for v in ROBV], rows,
   "RR, rate ratio per 1 standard deviation (95% credible or pooled interval). Retained = credible with the principal-model sign. Alternative fits: forced controls smoothed; Poisson with observation-level effect; second-order random-walk and first-order autoregressive year effects; province-by-year effect; Spatial+-type adjustment; covariates lagged 1 and 2 years and the matching unlagged years; extreme district-years refilled; survey covariates averaged over 3 years; odd and even years; plus leave-one-province and leave-one-year fits. Comparison outcomes are numbers of people treated for gastric cancer (C16) and infectious diseases (A00–B99), each with its own expected counts. " + B1, fs=7.5, per=2)
NCN = {"hit_and_run_rate": "Hit-and-run accidents", "fires_per_10000": "Fires per 10,000", "waste_recycling_rate": "Household waste recycling"}
rows = [["__H__", "Negative-control exposures (added one at a time)"]] + [[f"  {NCN[k]}", f"{v['IRR']:.3f} ({v['lo']:.3f}–{v['hi']:.3f})"] for k, v in N["negctl"].items()]
rows += [["__H__", "Model checks"], ["  95% posterior predictive coverage, %", f"{100*N['ppc']['coverage95']:.1f}"], ["  50% posterior predictive coverage, %", f"{100*N['ppc']['coverage50']:.1f}"],
         ["  PIT Kolmogorov–Smirnov P", f"{N['ppc']['pit_ks_p']:.2g}"], ["  Held-out 2024 coverage (95%), %", f"{100*N['oos']['coverage95']:.1f}"],
         ["  Residual Moran's I (permutation P)", f"{N['moran_resid']:.2f} ({N['moran_resid_p']:.2f})"]]
TF("Table S8. Negative-control exposures and model checks", ["Analysis", "Result"], rows, "Rate ratios per 1 standard deviation (95% credible interval). PIT, probability integral transform; a small P indicates imperfect calibration of predictive distributions. " + B1, fs=9)
# Appendix 7
rows = [["Screening uptake", EXPECT[C.UPT], f3((N['main'][C.UPT]['IRR'], N['main'][C.UPT]['lo'], N['main'][C.UPT]['hi'])), f3(N['bw'][C.UPT + '__between']), f3(N['bw'][C.UPT + '__within']), f"{N['rho_between'][C.UPT]:.2f}", f"Within-district ρ {N['rho_within_upt']:.2f}; comparison outcome gastric cancer {f3(N['nco'][('GCA', C.UPT)])}"],
        ["Basic livelihood security receipt", "+", f3((N['main']['basic_livelihood_rate']['IRR'], N['main']['basic_livelihood_rate']['lo'], N['main']['basic_livelihood_rate']['hi'])), "–", "–", f"{N['rho_between']['basic_livelihood_rate']:.2f}", f"ρ with living alone {N['rho_bl_old']:.2f}, with aged 80+ {N['rho_bl_pop80']:.2f}; subsets credible {100*N['mv']['basic_livelihood_rate']['cred_frac']:.0f}%"],
        ["Total fertility rate", "+", f3((N['main']['ext__total_fertility_rate']['IRR'], N['main']['ext__total_fertility_rate']['lo'], N['main']['ext__total_fertility_rate']['hi'])), "–", "–", f"{N['rho_between']['ext__total_fertility_rate']:.2f}", f"ρ with urban population share {N['rho_tfr_urban']:.2f}; subsets credible {100*N['mv']['ext__total_fertility_rate']['cred_frac']:.0f}%"]]
J.page_break(); J.head("Appendix S8. Post hoc analyses", 2); _NB[0] = True
TF("Table S9. Examination of characteristics associated against their expected direction", ["Characteristic", "Expected", "Principal RR (95% CrI)", "Between RR", "Within RR", "ρ, district means", "Other checks"], rows,
   "RR, rate ratio per 1 standard deviation; CrI, credible interval; ρ, Spearman rank correlation of 2011–2024 district means of the characteristic with the log of the anaemia ratio. Between and within: planned two-way-centred decomposition for subset-stable characteristics only ('–', not decomposed). All correlation analyses were added after the results were seen and did not change the principal model.", fs=7.5, per=3)
# Appendix 8 STROBE
DS = [x[4:].strip() for x in C.DISCUSSION if x.startswith("### ")]; MH = [h for h, _ in C.METHODS]; RH = [h for h, _ in C.RESULTS]
assert "Strengths and limitations" in DS
CK = [("Title and abstract", "1", "Title; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"), ("Study design", "4", f"Methods, {MH[0]}"), ("Setting", "5", f"Methods, {MH[0]}"),
      ("Participants", "6", f"Methods, {MH[0]} (district aggregates; ecological)"), ("Variables", "7", f"Methods, {MH[0]}; {MH[3]}; Appendix S3"), ("Data sources/measurement", "8", "Methods; Appendices S1 and S2"),
      ("Bias", "9", f"Methods, {MH[1]}; {MH[5]}; Appendices S2, S4, S7 and S8"), ("Study size", "10", f"Methods, {MH[0]} (all {N['n_districts']} districts)"), ("Quantitative variables", "11", f"Methods, {MH[2]}; {MH[3]}"),
      ("Statistical methods", "12", f"Methods, {MH[4]}; {MH[5]}"), ("Participants (flow)", "13", f"Methods, {MH[0]} (aggregate district data; Sejong excluded, reported in 1 of 14 years)"), ("Descriptive data", "14", f"Results, {RH[0]}; Table 1"), ("Outcome data", "15", f"Results, {RH[0]}"),
      ("Main results", "16", f"Results, {RH[1]}; {RH[2]}; Table 2; Figures 1–2"), ("Other analyses", "17", f"Results, {RH[3]}; {RH[4]}; Figure 3; Appendices S2 and S5–S8"),
      ("Key results", "18", "Discussion, first paragraph"), ("Limitations", "19", "Discussion, Strengths and limitations"), ("Interpretation", "20", "Discussion"), ("Generalisability", "21", "Discussion, Strengths and limitations"),
      ("Funding", "22", "Title page")]
J.page_break(); J.head("Appendix S9. STROBE checklist", 2)
J.table_fit("Table S10. STROBE checklist for this ecological study", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], "", fs_max=9)
foot_row(J, "STROBE, Strengthening the Reporting of Observational Studies in Epidemiology.", 8, 12)
ps = os.path.join(OUT, "Supplementary_material.docx"); J.doc_title = "Supplementary material"; J.save(ps)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_anem_esm", "--convert-to", "pdf", "--outdir", OUT, ps], check=True, capture_output=True)
print("saved", os.path.basename(ps))
