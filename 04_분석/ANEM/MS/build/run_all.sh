#!/bin/bash
# 30호 ANEM 전체 빌드(2026-11-18): 그림 → 원고 → 보충 → 검사기
set -e; cd "$(dirname "$0")"
python3 figs_anem.py
python3 build_ggi_anem.py
python3 esm_anem.py
python3 check_ggi_anem.py
