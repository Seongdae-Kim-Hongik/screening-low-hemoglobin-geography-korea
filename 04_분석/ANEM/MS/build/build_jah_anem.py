# build_jah_anem.py — Journal of Aging and Health(Sage Track/ScholarOne) Original Article 조립(2026-11-18, 30호 ANEM).
#  규정(journals.sagepub.com/author-instructions/JAH, 2026-11-18 열람): 이중 익명 → 제목면 별도 파일(저자·소속·교신·running head·AUTHOR'S NOTE·Statements and Declarations
#   (Ethical considerations, Consent to participate, Consent for publication, Declaration of conflicting interest, Funding statement, Data availability)), 원고에는 저자 정보 없음,
#   구조 초록 100-150단어, 키워드 3-5(초록 쪽), 초록 쪽과 본문 첫 쪽에 제목, 이중 간격, ≤30쪽(제목면·초록 제외, 표·그림·참고 포함), APA 참고문헌, EQUATOR 체크리스트, 그림 300 dpi.
import os, re, json, unicodedata
from jkms_engine import JKMS
from american import amer as brit   # 미국식 철자(APA)
import content_anem as C
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_anem.json"), encoding="utf-8"))
rdf = lambda f, d: open(os.path.join(OUT, f)).read().strip() if os.path.exists(os.path.join(OUT, f)) else d
ZENODO = rdf("zenodo_doi.txt", "10.5281/zenodo.PENDING"); GITHUB = rdf("github_url.txt", "https://github.com/PENDING")
TAG = "JAH_ANEM"; TITLE = brit(C.TITLE)
ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDR = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
FUNDING = "The author received no financial support for the research, authorship, and/or publication of this article."
AI_STATEMENT = "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript; the author takes full responsibility for the content."
COI = "The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article."
ETHICS = "The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012) and its continuing review on November 3, 2026 (7002340-202611-HR-040). The study used only published aggregate statistics and was conducted in accordance with the Declaration of Helsinki."
CONSENT = "Not applicable. The Institutional Review Board of Hongik University waived the requirement for informed consent because only published aggregate statistics were used and no individual was identifiable."
PUBCONSENT = "Not applicable."
def data_statement():
    return ("The district statistics analyzed are publicly available from the Korean Statistical Information Service (https://kosis.kr) and the other official sources cited in the Methods. "
            "The processed district-year data are available from the author on reasonable request. "
            f"The analysis code that generates every number, table, and figure is openly available under the MIT license on Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB}); it contains code only.")

def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def strip(t): return re.sub(r"\s*\[@[^\]]+\]", "", t)
def all_keys():
    src = open(os.path.join(HERE, "content_anem.py"), encoding="utf-8").read()
    src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

# ── APA 7 ──
def is_group(a): return not re.search(r"\s[A-ZÀ-Ý]{1,4}$", a.strip())
def surname(a): return a if is_group(a) else re.sub(r"\s+[A-ZÀ-Ý]{1,4}$", "", a.strip())
def initials(a):
    m = re.search(r"\s([A-ZÀ-Ý]{1,4})$", a.strip()); return " ".join(f"{c}." for c in m.group(1)) if m else ""
def auths(k): r = REFS[k]; return [r["authors"]] if r["type"] == "web" else r["authors"]
def base_label(k):
    s = [surname(a) for a in auths(k)]
    return s[0] if len(s) == 1 else (f"{s[0]} & {s[1]}" if len(s) == 2 else f"{s[0]} et al.")
def _first_ini(k): a = auths(k)[0]; return "" if is_group(a) else initials(a) + " "
def fold(x): return "".join(c for c in unicodedata.normalize("NFKD", x) if not unicodedata.combining(c)).lower()
def list_sortkey(k): a = auths(k); return (fold(surname(a[0])), tuple(fold(surname(x)) for x in a[1:]), int(REFS[k]["year"]), REFS[k]["title"].lower())
SUFFIX = {}; _g = {}
for k in KEYS: _g.setdefault((base_label(k), int(REFS[k]["year"])), []).append(k)
for ks in _g.values():
    if len(ks) > 1:
        for i, k in enumerate(sorted(ks, key=list_sortkey)): SUFFIX[k] = "abcdefgh"[i]
def year_str(k): return f"{REFS[k]['year']}{SUFFIX.get(k, '')}"
_sn = {}
for k in KEYS: _sn.setdefault(fold(surname(auths(k)[0])), set()).add(auths(k)[0])
def cite_label(k):   # APA 7: 같은 성, 다른 제1저자면 이니셜 붙임(M. Kim et al.)
    return (_first_ini(k) if len(_sn[fold(surname(auths(k)[0]))]) > 1 else "") + base_label(k)
def aylabel(k): return ((fold(base_label(k)), int(REFS[k]["year"]), SUFFIX.get(k, "")), f"{cite_label(k)}, {year_str(k)}")
JFULL = {"The Lancet. Haematology": "The Lancet Haematology", "Lancet (London, England)": "The Lancet", "Epidemiology (Cambridge, Mass.)": "Epidemiology", "PloS one": "PLOS ONE",
         "BMJ open": "BMJ Open", "JAMA": "JAMA", "BMC geriatrics": "BMC Geriatrics", "BMC public health": "BMC Public Health", "BMC endocrine disorders": "BMC Endocrine Disorders",
         "Perspectives on psychological science : a journal of the Association for Psychological Science": "Perspectives on Psychological Science",
         "Geriatrics & gerontology international": "Geriatrics & Gerontology International", "Alcoholism, clinical and experimental research": "Alcoholism: Clinical and Experimental Research",
         "The American journal of medicine": "The American Journal of Medicine",
         "Polit Sci Res Methods": "Political Science Research and Methods", "J R Stat Soc Series B Stat Methodol": "Journal of the Royal Statistical Society: Series B (Statistical Methodology)", "Stat Sci": "Statistical Science"}
SMALL = {"of", "and", "the", "in", "for", "on", "a", "an", "to", "&", "with"}
def jtitle(j):
    if j in JFULL: return JFULL[j]
    w = re.sub(r"\s*[:=].*$", "", j).split()
    return " ".join(x if (i and x.lower() in SMALL) else x[:1].upper() + x[1:] for i, x in enumerate(w))
def apa_author(a): return a if is_group(a) else f"{surname(a)}, {initials(a)}"
def ref(k):   # APA 7: Surname, I. I., Surname, I., & Surname, I. (Year). Title. <i>Journal</i>, <i>Vol</i>(Issue), pages. https://doi.org/...
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. ({year_str(k)}). <i>{r['title'].rstrip('.')}</i>. Retrieved {r['accessed_us']}, from {r['url']}"
    au = [apa_author(a) for a in r["authors"]]
    if len(au) > 20: au = au[:19] + ["... " + au[-1]]
    a = au[0] if len(au) == 1 else (f"{au[0]}, & {au[1]}" if len(au) == 2 else ", ".join(au[:-1]) + ", & " + au[-1])
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    t = re.sub(r"([:?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), t)   # APA: 쌍점 뒤 첫 글자 대문자
    s = f"{a}{'.' if len(au) == 1 and is_group(r['authors'][0]) else ''} ({year_str(k)}). {t} <i>{jtitle(r.get('journal_full') or r['journal'])}</i>"
    if r.get("vol"): s += f", <i>{r['vol']}</i>"
    if r.get("issue"): s += f"({r['issue']})"
    if r.get("pages"): s += f", {str(r['pages']).replace('-', chr(8211))}"
    s += "."
    if r.get("doi"): s += f" https://doi.org/{r['doi']}"
    return s
for _k, _r in REFS.items():
    if _r["type"] == "web":
        import datetime; _d = datetime.datetime.strptime(_r["accessed"], "%d %B %Y"); _r["accessed_us"] = _d.strftime("%B %-d, %Y")

class TX(JKMS):
    raw = False
    def aylabel(self, k): return aylabel(k)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = brit(text); text = re.sub(r"(^|[\s(=])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)
    def head(self, text, level=1):
        p = super().head(text, level)
        if p is not None: p.paragraph_format.keep_with_next = True
        return p

def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    from docx.shared import Pt
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(brit(t[0]), [brit(x) for x in t[1]], [[brit(x) for x in r] for r in t[2]], "", fs_max=fs, title_bold=True); foot_row(J, brit(t[3]), 8); J.counting = c

LABEL = {"basic_livelihood_rate": "Basic livelihood security receipt", "tertiary_educated_share": "Tertiary education", "ext__nutrition_label_literacy": "Nutrition-label literacy",
         "older_single_household_share": "Older adults living alone", "multicultural_marriage_share": "Marriages with a foreign spouse", "ext__total_fertility_rate": "Total fertility rate",
         "ext__dx_dm_share": "Diagnosed diabetes among attendees", "current_smoking_rate": "Current smoking", "high_risk_drinking_rate": "High-risk drinking",
         "walking_practice_rate": "Walking", "moderate_pa_rate": "Moderate or vigorous physical activity", "im_specialists_per_100k": "Internal medicine specialists",
         "screening_uptake": "Screening uptake", "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians",
         "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged 80 years or older"}
GROUPS = [("Deprivation, household and nutrition-label literacy", ["basic_livelihood_rate", "tertiary_educated_share", "ext__nutrition_label_literacy", "older_single_household_share"]),
          ("Women and childbearing", ["multicultural_marriage_share", "ext__total_fertility_rate"]),
          ("Chronic disease", ["ext__dx_dm_share"]),
          ("Lifestyle and physical activity", ["current_smoking_rate", "high_risk_drinking_rate", "walking_practice_rate", "moderate_pa_rate"]),
          ("Access and selection", ["im_specialists_per_100k", "screening_uptake"]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
EXPECT = {"basic_livelihood_rate": "+", "tertiary_educated_share": "−", "ext__nutrition_label_literacy": "−", "older_single_household_share": "+", "multicultural_marriage_share": "+",
          "ext__total_fertility_rate": "+", "ext__dx_dm_share": "+", "current_smoking_rate": "−", "high_risk_drinking_rate": "+", "walking_practice_rate": "−", "moderate_pa_rate": "−",
          "im_specialists_per_100k": "−", "screening_uptake": "−"}
UNIT = {"basic_livelihood_rate": "%", "tertiary_educated_share": "% of adults", "ext__nutrition_label_literacy": "%", "older_single_household_share": "% of households",
        "multicultural_marriage_share": "% of marriages", "ext__total_fertility_rate": "births per woman", "ext__dx_dm_share": "% of attendees", "current_smoking_rate": "%",
        "high_risk_drinking_rate": "%", "walking_practice_rate": "%", "moderate_pa_rate": "%", "im_specialists_per_100k": "per 100,000", "screening_uptake": "%",
        "urban_population_share": "%", "physicians_per_1000": "per 1,000", "sex_ratio": "men per 100 women", "fiscal_independence": "%", "pop80_share": "%"}
assert set(LABEL) == set(N["main"]) and sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"]

def table1():
    T = N["T1"]; cols = ["W1_2011-16", "W2_2017-24", "2011-2024"]
    rows = [["__H__", "Screening"],
            ["  District-years, n"] + [f"{T[c]['n']:,}" for c in cols],
            ["  Screening records, million"] + [f"{T[c]['exam']/1e6:.1f}" for c in cols],
            ["  Records flagged with suspected anaemia, n"] + [f"{T[c]['cases']:,}" for c in cols],
            ["  Crude positivity, %"] + [f"{T[c]['pos']:.2f}" for c in cols],
            ["  Standardised anaemia ratio, median†"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  Standardised anaemia ratio, P10–P90†"] + [f"{T[c]['sir_p10']:.2f}–{T[c]['sir_p90']:.2f}" for c in cols]]
    for g, vs in GROUPS:
        rows.append(["__H__", f"{g}, mean (SD)"])
        for v in vs:
            mx = max(abs(T[c]['cov'][v][0]) for c in cols); dp = 0 if mx >= 100 else (2 if mx < 3 else 1)
            rows.append([f"  {LABEL[v]}, {UNIT[v]}"] + [f"{T[c]['cov'][v][0]:,.{dp}f} ({T[c]['cov'][v][1]:,.{dp}f})" for c in cols])
    foot = ("†Observed over expected number flagged, summed over the window by district; expected numbers from national positivity by year, sex and 5-year age group applied to the estimated age structure of each district's attendees. "
            "Covariates are shown before standardisation. P10–P90, 10th–90th percentile; SD, standard deviation.")
    return ("Table 1. Anaemia flagged at national general health screening and district characteristics by calendar window, Korea, 2011–2024", ["Characteristic", "2011–2016", "2017–2024", "2011–2024"], rows, foot)

def table2():
    rows = []
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k2 = N["s43"][("KH_typeII", v)]; k4 = N["s43"][("KH_typeIV", v)]
            rows.append([f"  {LABEL[v]}", EXPECT.get(v, "NA"), f"{m['IRR']:.3f} ({m['lo']:.3f}–{m['hi']:.3f})", f"{100*mv['cred_frac']:.0f}" if mv else "NA", f"{k2[0]:.3f} ({k2[1]:.3f}–{k2[2]:.3f})", f"{k4[0]:.3f} ({k4[1]:.3f}–{k4[2]:.3f})"])
    foot = (f"RR, rate ratio per 1 standard deviation; CrI, credible interval; NA, not applicable (forced control); expected: + more, − less anaemia. Principal model: negative binomial, Besag–York–Mollié 2 district effect, random-walk and independent year effects (n={N['n_rows']:,} district-years). "
            "†Share of 200 covariate-subset fits containing the covariate with a CrI excluding 1. "
            f"‡Knorr-Held type II (best fitting; ΔWAIC {C.dW('KH_typeII'):,.0f}) or type IV ({C.dW('KH_typeIV'):,.0f}) space–time interaction added; WAIC, widely applicable information criterion. Bounds shown as 1.000 were classified from unrounded values.")
    return ("Table 2. District characteristics and the age- and sex-standardised anaemia ratio in the principal and space–time interaction models", ["Characteristic", "Expected", "Principal RR (95% CrI)", "Subsets credible, %†", "Type II RR (95% CrI)‡", "Type IV RR (95% CrI)‡"], rows, foot)

def tight(tb, fs):   # 가로 표 한 쪽(2026-11-12): 셀 줄간격 고정
    from docx.enum.text import WD_LINE_SPACING
    from docx.shared import Pt
    for row in tb.rows:
        for c in row.cells:
            for p in c.paragraphs: p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(round(1.6 * fs, 1)); p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
FIGCAP = {
 1: "National positivity for suspected anaemia at general health screening by 5-year age group in men (A) and women (B), Korea, selected years 2011–2024. Positivity is the number of screening records flagged divided by the number of screening records with a recorded judgement in each sex and age group, shown on a log scale. Data from the national statistics portal.",
 2: "Geography of the age- and sex-standardised anaemia ratio, Korea, 2011–2024. (A) Residual spatial rate ratio (RR) by district, the posterior mean of the exponentiated Besag–York–Mollié 2 district effect in the principal model. Solid outlines, hot spots (posterior probability of a residual spatial RR above 1 greater than 0.95); dashed outlines, cold spots (less than 0.05); thick lines, province boundaries. (B) Number of calendar windows (2011–2016, 2017–2024) in which each district was a hot or cold spot in the principal model refitted in each window; numbers of districts in parentheses. Sejong (hatched) was excluded. District boundaries as of 2024. Map lines delineate study areas and do not necessarily depict accepted national boundaries.",
 3: "Rate ratios per 1 standard deviation with 95% credible intervals for the four subset-stable district characteristics across models: the principal model, models with Knorr-Held type II (best fitting) and type IV space–time interactions, the principal model fitted to 2011–2016 and to 2017–2024 only, and the principal model with expected numbers computed from the resident population instead of attendees. The dotted vertical line marks a rate ratio of 1; log scale.",
}
APPX = ["Appendix S1. Supplementary methods: data sources, district harmonisation, standardisation and model specification",
        "Appendix S2. Judgement criterion and reconciliation of the screening flag with the published haemoglobin distribution",
        "Appendix S3. Covariate definitions, sources, expected directions and filled values",
        "Appendix S4. Panel checks before modelling",
        "Appendix S5. Emerging hot spot categories and persistence (Figure S1)",
        "Appendix S6. Window-specific rate ratios and interactions with the window and the COVID-19 period",
        "Appendix S7. Robustness of the subset-stable characteristics, comparison outcomes, negative controls and model checks",
        "Appendix S8. Post hoc examination of associations against the expected direction",
        "Appendix S9. STROBE checklist"]

def counts():
    aw = sum(len(t.split()) for t in C.ABSTRACT.values()) + sum(len(h.split()) for h in C.ABSTRACT)
    secs = [("Introduction", C.INTRO), ("Methods", [h for h, _ in C.METHODS] + [t for _, t in C.METHODS]), ("Results", [h for h, _ in C.RESULTS] + [t for _, t in C.RESULTS]), ("Discussion", [x.replace("### ", "") for x in C.DISCUSSION])]
    bw = sum(len(h.split()) + sum(len(strip(t).split()) for t in ts) for h, ts in secs)
    return aw, bw

def title_page():
    aw, bw = counts()
    J = TX(cite="ay")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"Running head: {brit(C.RUNNING)}")
    J.para("Seongdae Kim, PhD", before=12); J.para(AFFIL)
    J.para(f"<b>Corresponding author:</b> Seongdae Kim, {ADDR}. Phone: +82-2-320-1114. Email: kimsd@hongik.ac.kr. ORCID: {ORCID}")
    J.para(f"<b>Word counts:</b> abstract {aw}; main text {bw:,}. <b>Tables:</b> 2. <b>Figures:</b> 3. <b>References:</b> {len(KEYS)}.", before=6)
    J.head("AUTHOR'S NOTE", 1); J.para(f"Acknowledgments: None. {AI_STATEMENT}")
    J.head("Statements and Declarations", 1)
    for h, t in (("Ethical considerations", ETHICS), ("Consent to participate", CONSENT), ("Consent for publication", PUBCONSENT),
                 ("Declaration of conflicting interest", COI), ("Funding statement", FUNDING), ("Data availability", data_statement())):
        J.head(h, 2); J.para(t)
    J.doc_title = TITLE; p = os.path.join(OUT, f"TitlePage_{TAG}.docx"); J.save(p); return p

def build():
    aw, bw = counts(); nref = len(KEYS)
    J = TX(cite="ay")
    J.para(f"<b>{TITLE}</b>")
    J.head("Abstract", 1)
    for h, t in C.ABSTRACT.items(): J.para(f"<b>{h}:</b> {t}")
    J.raw = True; J.para(f"<b>Keywords:</b> {', '.join(C.KEYWORDS)}", before=6); J.raw = False
    J.page_break(); J.para(f"<b>{TITLE}</b>"); J.counting = True
    J.head("Introduction", 1)
    for p in C.INTRO: J.para(pandoc_cites(p), indent=True)
    J.head("Methods", 1)
    for h, p in C.METHODS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for h, p in C.RESULTS: J.head(h, 2); J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in C.DISCUSSION:
        if p.startswith("### Conclusion"): J.head("Conclusion", 1); continue
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True
    for k in sorted(KEYS, key=list_sortkey): J.para(ref(k), indent=False)
    J.raw = False
    J.page_break(); put_table(J, table1()); J.new_page("landscape"); put_table(J, table2(), fs=8); tight(J.doc.tables[-1], 8)
    J.new_page("portrait"); J.head("Figure Captions", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}")
    J.head("Supplemental Material", 1)
    J.para("The supplemental material file contains the following appendices:")
    for a_ in APPX: J.para(a_)
    return J, aw, bw, nref

if __name__ == "__main__":
    title_page()
    J, aw, bw, nref = build()
    assert aw <= 150, aw
    p = os.path.join(OUT, f"Manuscript_{TAG}.docx"); J.doc_title = TITLE; J.save(p)
    from docx import Document   # 이중 익명: 원고 파일 속성에서 저자 제거
    d = Document(p); d.core_properties.author = ""; d.core_properties.last_modified_by = ""; d.save(p)
    open(os.path.join(OUT, "wordcount_jah.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nrefs={nref}\ntables=2\nfigures=3\n")
    print(f"body {bw} | abstract {aw} | refs {nref}")
