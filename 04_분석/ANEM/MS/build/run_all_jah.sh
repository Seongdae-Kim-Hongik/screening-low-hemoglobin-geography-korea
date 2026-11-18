#!/bin/bash
# 30호 ANEM Journal of Aging and Health 전체 빌드(2026-11-18): 그림 → 제목면·원고 → 보충 → 검사기
set -e; cd "$(dirname "$0")"
python3 figs_anem.py
python3 build_jah_anem.py
python3 esm_anem.py
python3 check_jah_anem.py
