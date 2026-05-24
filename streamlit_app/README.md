# GreenSky Streamlit 시제품 v2.0

> SAF 시대 대비 항공 노선·운항 탄소-비용 통합 최적화 플랫폼
> **2026 국토교통 데이터 활용 경진대회 — 제품·서비스 개발 부문**

## 🚀 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 자동 열림.

## 📁 6 페이지 구조 (v2.0)

| 페이지 | 모듈 | 핵심 |
|---|---|---|
| Home (`app.py`) | Hero + 6 모듈 카드 | 89,566 t/yr · 1,323원/명 · 단계 0.58 |
| `1_①_CII_베이스라인.py` | 모듈① | 5,358.9 kt · ICAO ICEC v13 · GIR 0.008% |
| `2_②_SAF_시뮬레이션.py` | 모듈② | 96 조합 + 4 감축률 + 5 전략 + 항공사 부담 (7 탭) |
| `3_③_지상운항.py` | 모듈③ | 137만 편 + GBM 회귀 + 결항 41개월 (7 탭) |
| `4_④_유가예측.py` | 모듈④ | 8 모델 비교 + DM 검정 + α 매트릭스 (6 탭) |
| `5_⑤_통합의사결정.py` ★ | 신규 | 정부·항공사·소비자 3 주체 인터랙티브 |
| `6_⑥_4차원매트릭스.py` ★ | 신규 | 노선×α×가격×감축률 450 조합 |

## 🔑 v2.0 핵심 권장 수치 (CORSIA Default 84.4%)

- **2027 SAF 1% 감축**: 45.2 kt/yr (정부 16만 t 목표와 1.06× 정합 ✓)
- **비용 (시장가 1.2 USD/L)**: 331억 원/yr
- **소비자 부담**: 1,323원/명 (단계 0.58 = 체감 없음)
- **합병사 부담 (40.7%)**: 134.6억 원/yr
- **8 모델 비교**: Naive Val MAE 4.22 ★ (Transformer 12.53 = 최악, AI 만능론 반박)

## 📦 데이터 구조

```
data/
├── greensky_module{1,2,3,4}_v4.xlsx   # v1.0 데이터 (이전 분석)
├── flights_summary.xlsx                # 137만 편 출도착 집계
├── mops_full.csv                       # MOPS Jet-A1 77개월
└── v2/                                  # v2.0 신규 분석
    ├── greensky_module2_v6_allocation.xlsx       # 5 배분 전략
    ├── greensky_module2_v6_airline_burden.xlsx   # 항공사 부담
    ├── greensky_module2_v7_reduction_scenarios.xlsx  # 4 감축률
    ├── greensky_module2_v9_matrix.xlsx           # 4차원 450 조합
    ├── greensky_module3_gbm_v1.xlsx              # GBM 회귀
    ├── greensky_module3_v2_cancellation.xlsx     # 결항 41개월
    ├── greensky_module4_v2_scenarios.xlsx        # α 시나리오
    └── greensky_decision_engine_v1.xlsx          # 의사결정 엔진
```

## 🛠 의존성

```
streamlit>=1.30
pandas>=2.0
plotly>=5.18
openpyxl>=3.1
numpy>=1.24
```
