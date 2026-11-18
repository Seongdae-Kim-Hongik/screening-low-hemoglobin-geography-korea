# build_refs_cogn.py — 만성하기도질환 Thorax 판 참고문헌(build_refs_crc.py 복제, 2026-11-06) 메타데이터 캐시(refs_anem.json). 네트워크는 이 스크립트에서만(2026-11-06).
#  키 = 원고 원천(draft md + content_anem.py)의 [@key]. manifest(ALL_refs.csv) PMID → PubMed esummary, 없으면 DOI → Crossref. 웹 문헌은 WEB 사전.
#  EJCP 저자-연도 서식은 build_ejcp_crc.py가 이 캐시로 만든다(저자 성 = PubMed 이름에서 이니셜 제거).
import os, re, json, time, urllib.request, urllib.parse, glob
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE)
man = pd.read_csv(os.path.join(MS, "refs", "manifest", "ALL_refs.csv"), dtype=str).fillna("")
man["pmid"] = man.pmid.str.replace(r"\.0$", "", regex=True); M = man.set_index("key")
src = open(os.path.join(HERE, "content_anem.py"), encoding="utf-8").read() 
src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
keys = sorted({k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")})
keys = [k for k in keys if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k)]
WEB = {
 "web:kosis2026screening": dict(type="web", authors="National Health Insurance Service", title="National health screening statistics: general health screening judgement by administrative district (DT_35007_N098, DT_35007_N103) and by sex and age group (DT_35007_N099, DT_35007_N104), 2011-2024. Korean Statistical Information Service", url="https://kosis.kr", year=2026, accessed="11 November 2026"),
 "web:mois2026population": dict(type="web", authors="Ministry of the Interior and Safety", title="Resident registration population by district, sex and 5-year age group, 2011-2024", url="https://jumin.mois.go.kr", year=2026, accessed="20 October 2026"),
 "web:rcore2026": dict(type="web", authors="R Core Team", title="R: a language and environment for statistical computing. Version 4.6.0. Vienna: R Foundation for Statistical Computing", url="https://www.R-project.org/", year=2026, accessed="20 October 2026"),
}
out = {}
miss = [k for k in keys if not k.startswith("web:") and k not in M.index]; assert not miss, miss
pm = [k for k in keys if not k.startswith("web:") and M.loc[k, "pmid"]]
for i in range(0, len(pm), 150):
    ids = ",".join(M.loc[k, "pmid"] for k in pm[i:i + 150])
    d = json.load(urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ids, timeout=60))["result"]
    for k in pm[i:i + 150]:
        r = d[M.loc[k, "pmid"]]
        au = [a["name"] for a in r["authors"] if a.get("authtype", "Author") == "Author"] or [a["name"] for a in r["authors"]]
        doi = next((a["value"] for a in r["articleids"] if a["idtype"] == "doi"), "") or M.loc[k, "doi"]
        pages = r.get("pages", "") or (r.get("elocationid", "").replace("pii: ", "").split(" doi")[0] if r.get("elocationid", "").startswith("pii:") else "")
        out[k] = dict(type="journal", authors=au, title=r["title"].rstrip("."), journal=r["source"], year=int(r["pubdate"][:4]), vol=r.get("volume", ""), issue=r.get("issue", ""), pages=pages, doi=doi, pmid=M.loc[k, "pmid"], verified="PubMed esummary " + time.strftime("%Y-%m-%d"))
    time.sleep(0.4)
JABBR = {"Political Science Research and Methods": "Polit Sci Res Methods", "Geographical Analysis": "Geogr Anal", "Econometrica": "Econometrica", "Statistical Science": "Stat Sci"}
for k in keys:
    if k.startswith("web:"): out[k] = WEB[k]; continue
    if k in out: continue
    doi = M.loc[k, "doi"]; assert doi, k
    m = json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/" + urllib.parse.quote(doi), headers={"User-Agent": "research (kimsd@hongik.ac.kr)"}), timeout=60))["message"]
    au = [f"{a.get('family','')} {''.join(x[0] for x in re.split(r'[ -]', a.get('given','')) if x)}".strip() for a in m.get("author", [])]
    ct = (m.get("container-title") or [""])[0]; jt = JABBR.get(ct, (m.get("short-container-title") or [ct])[0])
    yr = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
    out[k] = dict(type="journal", authors=au, title=re.sub(r"<[^>]+>", "", (m.get("title") or [""])[0]), journal=jt, year=int(yr), vol=m.get("volume", ""), issue=m.get("issue", ""), pages=m.get("page", "") or m.get("article-number", ""), doi=doi, verified="Crossref " + time.strftime("%Y-%m-%d"))
    time.sleep(0.3)
# 서식 통일: 학술지 MEDLINE 약어(마침표 없음), 쪽 범위 전체 표기, 대문자 제목 문장형
JN = {"Polit. Sci. Res. Methods": "Polit Sci Res Methods", "Geogr. Anal.": "Geogr Anal", "Stat. Sci.": "Stat Sci", "J R Stat Soc Series B Stat Methodol": "J R Stat Soc Series B Stat Methodol",
      "Journal of the Royal Statistical Society Series B: Statistical Methodology": "J R Stat Soc Series B Stat Methodol"}
def fullp(p):
    m = re.match(r"^(\d+)-(\d+)$", str(p))
    if not m: return p
    a, b = m.groups(); return p if len(b) >= len(a) else f"{a}-{a[:len(a)-len(b)]+b}"
FIXP = {"besoramoreno2020social": "737", "lopes2023food": "1074"}   # 전자 논문 번호(PubMed esummary pages 없음·마침표 붙음)
AHEAD = set()
for k, v in out.items():
    if v.get("type") != "journal": continue
    if k in FIXP: v["pages"] = FIXP[k]
    if k in AHEAD: v["pages"] = ""; v["vol"] = ""; v["ahead"] = True
    v["journal"] = JN.get(v["journal"], v["journal"]).replace(".", "")
    v["pages"] = fullp(v.get("pages", "")) if k not in AHEAD else ""
    if v["title"].isupper(): v["title"] = v["title"].capitalize()
    v["authors"] = [a.title() if a.isupper() else a for a in v["authors"]]
# 문장형 제목(제목형 대소문자 문헌만 직접 지정, 고유명사 유지)
SENT = {
 "besoramoreno2020social": "Social and economic factors and malnutrition or the risk of malnutrition in the elderly: a systematic review and meta-analysis of observational studies",
 "lopes2023food": "Food insecurity and micronutrient deficiency in adults: a systematic review and meta-analysis",
 "kang2015korea": "Korea Community Health Survey data profiles",
 "kim2014association": "Association between nutrition label reading and nutrient intake in Korean adults: Korea National Health and Nutritional Examination Survey, 2007-2009 (KNHANES IV)",
 "lee2019increased": "Increased prevalence of thalassemia in young people in Korea: impact of increasing immigration",
 "shin2018association": "The association between socioeconomic status and adherence to health check-up in Korean adults, based on the 2010-2012 Korean National Health and Nutrition Examination Survey",
 "simpson2017penalising": "Penalising model component complexity: a principled, practical approach to constructing priors",
 "suh2016prevalence": "Prevalence and relationships of iron deficiency anemia with blood cadmium and vitamin D levels in Korean women",
 "kim2019anemia": "Anemia and health-related quality of life in South Korea: data from the Korean National Health and Nutrition Examination Survey 2008-2016",

 "blanc2019occupational": "The occupational burden of nonmalignant respiratory diseases. An official American Thoracic Society and European Respiratory Society statement",
 "choi2020regional": "Regional variation of suicide mortality in South Korea",
 "dwyerlindgren2017trends": "Trends and patterns of differences in chronic respiratory disease mortality among US counties, 1980-2014",
 "hwang2017recent": "Recent trends in the prevalence of chronic obstructive pulmonary disease in Korea",
 "kim2022trends": "Trends in regional disparity in cardiovascular mortality in Korea, 1983-2019",
 "lee2016risk": "The risk factors and characteristics of COPD among nonsmokers in Korea: an analysis of KNHANES IV and V",
 "raju2019rural": "Rural residence and poverty are independent risk factors for chronic obstructive pulmonary disease in the United States",
 "luo2026copd": "COPD burden across 48 Asian locations, 2009-2023: demographic drivers and socioeconomic inequality",
 "kim2017income": "Income differences in smoking prevalences in 245 districts of South Korea: patterns by area deprivation and urbanity, 2008-2014",
 "cheolseong2017data": "Data resource profile: the National Health Information Database of the National Health Insurance Service in South Korea",
 "steegen2016increasing": "Increasing transparency through a multiverse analysis",
 "vanderweele2017sensitivity": "Sensitivity analysis in observational research: introducing the E-value",
 "bell2015explaining": "Explaining fixed effects: random effects modeling of time-series cross-sectional and panel data",
 "rue2009approximate": "Approximate Bayesian inference for latent Gaussian models by using integrated nested Laplace approximations",
 "morgenstern1995ecologic": "Ecologic studies in epidemiology: concepts, principles, and methods",
 "inskip1983methods": "Methods for age-adjustment of rates",
 "knorrheld2000bayesian": "Bayesian modelling of inseparable space-time variation in disease risk",
 "dupont2022spatial": "Spatial+: a novel approach to spatial confounding",
 "lipsitch2010negative": "Negative controls: a tool for detecting confounding and bias in observational studies",
 "vonelm2007strengthening": "The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies",
 "lederer2019control": "Control of confounding and reporting of results in causal inference studies. Guidance for authors from editors of respiratory, sleep, and critical care journals",
}
for k, t in SENT.items():
    if k in out: out[k]["title"] = t
for k, v in out.items():   # 콜론 뒤 첫 글자 소문자(고유명사·약어 제외)
    if v.get("type") == "journal":
        v["title"] = re.sub(r":\s+([A-Z][a-z]*)\b", lambda m: ": " + (m.group(1) if m.group(1) in ("Korea", "Korean", "South", "Bayesian", "Spatial", "E", "GLOBOCAN", "COPD") else m.group(1).lower()), v["title"])
# PubMed 저자명 뒤집힘 교정(2026-11-06 조테로 검증에서 발견: PubMed 27794523이 "Cheol Seong S", "Heon Park J"로 색인 — 원문 Sang Cheol Seong, Jong Heon Park)
AUTHOR_FIX = {"Cheol Seong S": "Seong SC", "Heon Park J": "Park JH", "Hyon Bang J": "Bang JH", "Ae Shin S": "Shin SA"}
for _k, _v in out.items():
    if isinstance(_v.get("authors"), list): _v["authors"] = [AUTHOR_FIX.get(a, a) for a in _v["authors"]]
assert not any("Cheol Seong" in a for v in out.values() if isinstance(v.get("authors"), list) for a in v["authors"])
# 13호 review 1회차: 출처 메타 오류 교정(PubMed 제목 역따옴표, MDPI 논문 번호 누락)
if "salerno2023alzheimers" in out: out["salerno2023alzheimers"]["title"] = out["salerno2023alzheimers"]["title"].replace("`", "'")
if "lim2022predictive" in out: out["lim2022predictive"].update(issue="9", pages="1388")
json.dump(out, open(os.path.join(HERE, "refs_anem.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import re as _re
for _k, _v in out.items():   # 9호부터: 한국인 이름 뒤집힘 검사(두 음절 이름 + 한 글자 이니셜)
    if isinstance(_v.get("authors"), list): assert not [a for a in _v["authors"] if a not in ("Tchetgen Tchetgen E", "Mejia Arango S") and _re.fullmatch(r"[A-Z][a-z]+ [A-Z][a-z]+ [A-Z]", a)], (_k, _v["authors"])
print(len(keys), "keys;", sum(v["type"] == "journal" for v in out.values()), "journal,", sum(v["type"] == "web" for v in out.values()), "web")
