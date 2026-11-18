# check_ggi_anem.py — GGI 투고 전 검사(2026-11-18): 한도·필수 절·인용 순서·철자·문체·표 3선·그림·이전 투고 흔적.
import os, re, subprocess, zipfile
from docx import Document
from PIL import Image
import content_anem as C
from build_ggi_anem import KEYS, TITLE, counts
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out"); R = []
def ok(n, c, i=""): R.append(("PASS" if c else "FAIL", n, i))
d = Document(os.path.join(OUT, "Manuscript_GGI_ANEM.docx")); ps = [p.text for p in d.paragraphs]; ms = "\n".join(ps)
aw, bw = counts(); ok("본문 ≤3,000", bw <= 3000, bw); ok("초록 ≤250, Aim/Methods/Results/Conclusions", aw <= 250 and list(C.ABSTRACT) == ["Aim", "Methods", "Results", "Conclusions"], aw); ok("키워드 ≤5", len(C.KEYWORDS) <= 5)
ok("표+그림 ≤5", len(d.tables) + 3 <= 5, len(d.tables)); ok("제목 쌍점·약어 없음", ":" not in TITLE and not re.search(r"\b[A-Z]{2,}\b", TITLE))
for h in ("Introduction", "Methods", "Results", "Discussion", "Author Contributions", "Acknowledgments", "Funding Statement", "Disclosure Statement", "Data Availability Statement", "Ethics Approval Statement", "Patient Consent Statement", "Clinical Trial Registration", "References", "Figure Legends"):
    ok(f"절 {h}", h in ps)
ok("AI 고지 Methods 안", "translation and English-language editing" in ms.split("\nResults\n")[0])
ok("이해상충 문구", "The author declares no conflict of interest." in ms)
r = subprocess.run(["python3", "/Users/seongdaekim/Library/CloudStorage/GoogleDrive-wwwwrte@gmail.com/내 드라이브/S.K/G.Downloads/00_PLAYBOOK/검증기록/check_citation_order.py", os.path.join(OUT, "Manuscript_GGI_ANEM.docx")], capture_output=True, text=True).stdout
ok("인용 순서 PASS", "결과: PASS" in r, r[-80:])
body = ms.split("\nReferences\n")[0]
bl = re.findall(r"\b(\w*(?:anaem|haem|standardis|harmonis|judgement|ageing|programme|neighbour|modelled|recognis|analysed|centre)\w*)\b", body); ok("미국식 철자", not bl, sorted(set(bl))[:8])
ok("1인칭 없음", not re.search(r"\b(we|our|us)\b", body)); ok("em dash 없음", "—" not in ms)
ok("참고문헌에 GitHub·Zenodo 없음", not re.search(r"zenodo|github", ms.split("\nReferences\n")[1].split("Table 1.")[0], re.I))
allt = ms + "\n".join(p.text for p in Document(os.path.join(OUT, "Supplementary_material.docx")).paragraphs) + open(os.path.join(OUT, "Cover_Letter_GGI_ANEM_paste.txt")).read()
ok("이전 투고 흔적 없음", not re.search(r"Maturitas|Haematology \(|European Journal of Haematology|Journal of Aging and Health|EJH|MAT-D", allt), re.findall(r"Maturitas|Journal of Aging and Health", allt)[:3])
x = zipfile.ZipFile(os.path.join(OUT, "Manuscript_GGI_ANEM.docx")).read("word/document.xml").decode(); ok("표 세로선 없음", 'w:insideV w:val="single"' not in x)
for i in (1, 2, 3):
    im = Image.open(os.path.join(OUT, "Figures", f"Figure_{i}.tif")); ok(f"Figure {i} ≥300 dpi", im.info.get("dpi", (0, 0))[0] >= 299)
for s, n, i in R: print(s, n, i if s == "FAIL" else "")
print("FAIL", sum(1 for s, _, _ in R if s == "FAIL"), "/", len(R)); open(os.path.join(OUT, "check_ggi.txt"), "w").write("\n".join(f"{s} {n} {i}" for s, n, i in R))
