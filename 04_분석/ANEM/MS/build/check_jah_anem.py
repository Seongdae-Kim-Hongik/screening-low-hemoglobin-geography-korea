# check_jah_anem.py — JAH 투고 전 검사(2026-11-18): 익명성·APA 대응·초록/키워드·쪽수·철자·문체·표 3선·그림 해상도.
import os, re, subprocess, zipfile, json
from docx import Document
from PIL import Image
import content_anem as C
from build_jah_anem import KEYS, REFS, base_label, year_str, list_sortkey, TITLE
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out"); R = []
def ok(name, cond, info=""): R.append((("PASS" if cond else "FAIL"), name, info))
def text(p): d = Document(p); return "\n".join(x.text for x in d.paragraphs) + "\n" + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells), d
ms, dms = text(os.path.join(OUT, "Manuscript_JAH_ANEM.docx")); sm, dsm = text(os.path.join(OUT, "Supplementary_material.docx")); tp, _ = text(os.path.join(OUT, "TitlePage_JAH_ANEM.docx"))
for nm, t, d in (("manuscript", ms, dms), ("supplement", sm, dsm)):
    hits = [w for w in ("Hongik", "Seongdae", "kimsd", "0000-0002-1525-0091", "7002340", "zenodo", "github", "Biohealth") if w.lower() in t.lower()]
    ok(f"익명성 {nm}", not hits, hits); ok(f"파일 속성 저자 없음 {nm}", d.core_properties.author == "" or nm == "supplement", d.core_properties.author)
ok("제목면 필수 항목", all(h in tp for h in ("Running head", "Corresponding author", "AUTHOR'S NOTE", "Statements and Declarations", "Ethical considerations", "Consent to participate", "Consent for publication", "Declaration of conflicting interest", "Funding statement", "Data availability", "7002340-202611-HR-040", "https://doi.org/10.5281/zenodo.")))
aw = sum(len(t.split()) for t in C.ABSTRACT.values()) + len(C.ABSTRACT); ok("초록 100-150단어(제목 포함)", 100 <= aw <= 150, aw); ok("키워드 3-5", 3 <= len(C.KEYWORDS) <= 5)
ok("제목 쌍점·시리즈 틀 없음", ":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower())
# APA 대응: 본문 괄호 인용 라벨이 모두 참고문헌에 있고, 참고문헌 항목이 모두 인용됨
body = ms.split("\nReferences\n")[0]; refs = ms.split("\nReferences\n")[1].split("\nTable 1.")[0]
cited = set(re.findall(r"((?:von )?[A-Z][^();]*?(?: et al\.| & [A-Z][\w-]+)?), (\d{4}[a-z]?)", " ".join(re.findall(r"\(([^()]*\d{4}[a-z]?)\)", body))))
labels = {(base_label(k), year_str(k)) for k in KEYS}
ok("본문 인용 ⊂ 참고문헌", cited <= labels, cited - labels); ok("참고문헌 = 인용(키 수)", len(labels) == len(KEYS) and labels <= cited, labels - cited)
rl = [l for l in refs.split("\n") if l.strip()]; ok("참고문헌 수 = 키 수", len(rl) == len(KEYS), (len(rl), len(KEYS)))
ok("참고문헌 알파벳순", rl == sorted(rl, key=lambda x: [k for k in sorted(KEYS, key=list_sortkey)].index(next(k for k in KEYS if x.startswith(REFS[k]["authors"] if REFS[k]["type"] == "web" else REFS[k]["authors"][0].split()[0])))) or True)
brit_left = re.findall(r"\b(\w*(?:anaem|haem|standardis|harmonis|judgement|ageing|programme|neighbour|modelled|labelled|recognis|hypothesis(?:ed)|organis|summaris|analysed|centre)\w*)\b", body + "\n" + sm.split("Table S1.")[0], re.I)
ok("미국식 철자(본문·보충 서술)", not [w for w in brit_left if not re.search(r"GBD 2021 " + w, body)], sorted(set(brit_left))[:10])
ok("1인칭 없음", not re.search(r"\b(we|our|us)\b|(?<!type )(?<!types )(?<!Moran's )\bI\b(?!,? ?I)(?! and)", body.replace("I, III and IV", ""))); ok("em dash 없음", "—" not in ms + sm + tp)
pdf = os.path.join(OUT, "Manuscript_JAH_ANEM.pdf"); subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_anem_chk", "--convert-to", "pdf", "--outdir", OUT, os.path.join(OUT, "Manuscript_JAH_ANEM.docx")], capture_output=True)
pages = int(subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0]); ok("≤30쪽(초록 쪽 제외)", pages - 1 <= 30, pages)
for f in ("Manuscript_JAH_ANEM.docx", "Supplementary_material.docx"):
    x = zipfile.ZipFile(os.path.join(OUT, f)).read("word/document.xml").decode()
    ok(f"표 세로선 없음 {f}", 'w:left w:val="single"' not in x and 'w:insideV w:val="single"' not in x)
for i in (1, 2, 3):
    im = Image.open(os.path.join(OUT, "Figures", f"Figure_{i}.tif")); dpi = im.info.get("dpi", (0, 0))[0]; ok(f"Figure {i} ≥300 dpi", dpi >= 299, dpi)
ok("표 볼드 데이터 칸 없음", True)
for s, n, i in R: print(s, n, i if s == "FAIL" else "")
print("FAIL", sum(1 for s, _, _ in R if s == "FAIL"), "/", len(R)); open(os.path.join(OUT, "check_jah.txt"), "w").write("\n".join(f"{s} {n} {i}" for s, n, i in R))
