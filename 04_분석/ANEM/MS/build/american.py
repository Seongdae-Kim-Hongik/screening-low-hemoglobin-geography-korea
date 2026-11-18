# american.py — 미국식 철자: british.py 사전을 거꾸로 적용(본문·표·범례 출력 직전, 참고문헌 서지는 원문 유지). 2026-11-18.
import re
from british import STEMS, WORDS
INV = {v: k for k, v in WORDS.items()}
INV.update({"anaemic": "anemic", "anaemias": "anemias", "haemoglobins": "hemoglobins", "haematological": "hematological", "thalassaemia": "thalassemia", "oesophageal": "esophageal",
            "licence": "license", "organisation": "organization", "organisations": "organizations", "programmes": "programs", "per cent": "percent", "ageing-related": "aging-related",
            "recognised": "recognized", "hypothesised": "hypothesized", "standardisation": "standardization", "harmonised": "harmonized", "labelled": "labeled", "modelling": "modeling",
            "judgements": "judgments", "behaviour": "behavior", "neighbourhoods": "neighborhoods", "colour": "color", "centre": "center"})
for _w in ("analyses",): INV.pop(_w, None)
BSTEMS = [(s[:-1] + "s", s) for s in STEMS]
def amer(t):
    if not t: return t
    t = t.replace("per cent", "percent")
    def stem(m):
        w = m.group(0); low = w.lower()
        for b, a in BSTEMS:
            if low.startswith(b) and re.fullmatch(r"(e|ed|es|ing|ation|ations|er|ers)", low[len(b):] or "x"):
                r = a + low[len(b):]; return r[0].upper() + r[1:] if w[0].isupper() else r
        return w
    t = re.sub(r"\b[A-Za-z]*is(?:e|ed|es|ing|ation|ations|er|ers)\b", stem, t)
    def word(m):
        w = m.group(0); r = INV.get(w.lower())
        if r is None: return w
        return r[0].upper() + r[1:] if w[0].isupper() else r
    return re.sub(r"\b[A-Za-z]+(?:-[A-Za-z]+)?\b", word, t)
if __name__ == "__main__":
    print(amer("Standardised anaemia ratios were harmonised; haemoglobin judgement, ageing, modelled neighbourhoods, programme, recognised, hypothesised, Standardisation, labelled, licence, analysed, centre, otherwise, rise, raised, exercise."))
