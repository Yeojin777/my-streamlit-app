"""
GreenSky — SAF 시대 대비 항공 노선·운항 탄소-비용 통합 최적화 플랫폼
시제품 v1.0 (2026 국토교통 데이터 활용 경진대회 제출용)

실행:
  pip install streamlit pandas plotly openpyxl numpy
  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ============================================================
# 페이지 설정 + 글로벌 스타일
# ============================================================
st.set_page_config(
    page_title="GreenSky — 항공 탄소-비용 통합 최적화",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Editorial dashboard 스타일 — 다크모드, 시리프 액센트
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;700&family=IBM+Plex+Sans+KR:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans KR', -apple-system, sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #0a0e1a 0%, #0d1320 100%);
    color: #e8eaed;
}
.main .block-container {
    padding-top: 2.5rem;
    max-width: 1280px;
}
h1, h2, h3 {
    font-family: 'IBM Plex Sans KR', sans-serif;
    font-weight: 600;
    letter-spacing: -0.02em;
}
.serif-accent {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 500;
    color: #6ee7b7;
}
.eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 0.72rem;
    color: #6ee7b7;
    font-weight: 500;
}
.hero-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3.4rem;
    font-weight: 500;
    color: #f0f4f8;
    line-height: 1.0;
    letter-spacing: -0.04em;
}
.hero-unit {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    color: #94a3b8;
    margin-left: 0.4rem;
}
.metric-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(110, 231, 183, 0.15);
    border-radius: 4px;
    padding: 1.6rem 1.4rem;
    margin-bottom: 0.8rem;
}
.metric-card:hover {
    border-color: rgba(110, 231, 183, 0.4);
    transition: border-color 0.3s ease;
}
.divider-thin {
    border: 0;
    border-top: 1px solid rgba(148, 163, 184, 0.15);
    margin: 2.2rem 0;
}
.tag {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 2px;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    margin-right: 0.4rem;
}
.tag-policy { background: rgba(244, 114, 182, 0.12); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); }
.tag-data   { background: rgba(110, 231, 183, 0.10); color: #6ee7b7; border: 1px solid rgba(110, 231, 183, 0.3); }
.tag-ai     { background: rgba(125, 211, 252, 0.10); color: #7dd3fc; border: 1px solid rgba(125, 211, 252, 0.3); }
.tag-saf    { background: rgba(252, 211, 77, 0.10); color: #fcd34d; border: 1px solid rgba(252, 211, 77, 0.3); }
section[data-testid="stSidebar"] {
    background: #060912;
    border-right: 1px solid rgba(148, 163, 184, 0.1);
}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #6ee7b7;
}
.stPlotlyChart {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.08);
    border-radius: 4px;
    padding: 0.6rem;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #f0f4f8 !important;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.72rem !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(15, 23, 42, 0.4);
    border-radius: 2px;
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.1);
    padding: 0.5rem 1.1rem;
}
.stTabs [aria-selected="true"] {
    background: rgba(110, 231, 183, 0.08) !important;
    color: #6ee7b7 !important;
    border-color: rgba(110, 231, 183, 0.4) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown("# 🛫 GreenSky")
    st.markdown("<span class='serif-accent'>Carbon × Cost Co-optimization</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📍 개요")
    st.markdown("""
**대회**: 2026 국토교통 데이터 활용 경진대회
**분야**: 항공 데이터 활용
**부문**: 제품·서비스 개발

**핵심 문제의식**
2027년 SAF(지속가능항공유) 1% 의무화 시대에
**노선별 탄소집약도·연료비·지상 운영**을
하나의 의사결정 프레임으로 통합 최적화.
""")
    st.markdown("---")
    st.markdown("### 🧭 페이지 가이드")
    st.markdown("""
- **🏠 Overview** — 통합 메시지
- **① CII 베이스라인** — 모듈①
- **② SAF 시뮬레이션** — 모듈②
- **③ 지상운항 분석** — 모듈③
- **④ 유가·할증료 예측** — 모듈④
- **⑤ 통합 의사결정 엔진** — 3주체
- **⑥ 4차원 매트릭스** — 정책 시뮬
""")
    st.caption("v2.0 · 2026-05-24 · CORSIA Default 84.4% 권장")

# ============================================================
# 메인 — Hero
# ============================================================
col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("<span class='eyebrow'>2027 SAF Mandate Readiness</span>", unsafe_allow_html=True)
    st.markdown("# GreenSky")
    st.markdown(
        "<h3 style='font-weight:300; color:#94a3b8; letter-spacing:-0.01em;'>"
        "항공 노선·운항 <span class='serif-accent'>탄소-비용</span> 통합 최적화 플랫폼"
        "</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p style='font-size:1.05rem; line-height:1.7; color:#cbd5e1; margin-top:1.2rem;'>
        2027년 국내 출발 모든 국제선에 SAF 1% 혼합이 의무화됩니다.
        유류할증료 인상 부담은 소비자가, SAF 도입 비용은 항공사·정부가 떠안습니다.
        둘은 결국 <span class='serif-accent'>같은 연료비 효율화 축</span>입니다.
        <br><br>
        GreenSky는 ICAO 표준 방법론과 4-Layer 데이터 검증 위에서
        <strong>노선별 탄소집약도(CII)</strong>, <strong>SAF 도입 시나리오</strong>,
        <strong>지상 운영 효율</strong>, <strong>유가·할증료 예측</strong>을 통합하여
        정부·항공사·소비자 3주체의 의사결정을 돕는 SaaS 시제품입니다.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='margin-top:1.2rem;'>"
        "<span class='tag tag-policy'>POLICY READINESS</span>"
        "<span class='tag tag-data'>DATA FUSION</span>"
        "<span class='tag tag-ai'>AI · LSTM · GBM</span>"
        "<span class='tag tag-saf'>SAF 2027</span>"
        "</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style='background:rgba(110,231,183,0.04); border:1px solid rgba(110,231,183,0.25);
                    border-radius:4px; padding:1.8rem 1.6rem; margin-top:2rem;'>
            <div class='eyebrow'>핵심 정량 메시지 · CORSIA Default 84.4%</div>
            <div style='margin-top:1.1rem;'>
                <div class='hero-num'>89,566<span class='hero-unit'>tCO₂/yr</span></div>
                <div style='color:#94a3b8; margin-top:0.3rem;'>
                    SAF 1% + 지상 운영 통합 개입 시 감축량 <br>
                    <span style='color:#6ee7b7;'>(SAF 45,200 + A-SMGCS 44,366)</span>
                </div>
            </div>
            <hr class='divider-thin' style='margin:1.2rem 0;'>
            <div style='display:flex; justify-content:space-between; gap:1rem;'>
                <div>
                    <div style='color:#94a3b8; font-size:0.78rem;'>소비자 1인당 부담</div>
                    <div style='font-family:"IBM Plex Mono",monospace; font-size:1.6rem; color:#f0f4f8;'>
                        1,323<span style='font-size:0.9rem; color:#94a3b8;'>원</span>
                    </div>
                </div>
                <div>
                    <div style='color:#94a3b8; font-size:0.78rem;'>흡수 단계</div>
                    <div style='font-family:"IBM Plex Mono",monospace; font-size:1.6rem; color:#f0f4f8;'>
                        0.58<span style='font-size:0.9rem; color:#94a3b8;'>단계</span>
                    </div>
                </div>
            </div>
            <div style='margin-top:0.9rem; font-size:0.72rem; color:#64748b; line-height:1.5;'>
                시장가 1.2 USD/L · CORSIA HEFA-UCO Default 감축률 84.4%<br>
                정부 16만 t 목표와 1.06× 정합 ✓
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# ============================================================
# 6 모듈 카드 (v2.0 — 의사결정·매트릭스 추가)
# ============================================================
st.markdown("<span class='eyebrow'>Six Modules · One Framework</span>", unsafe_allow_html=True)
st.markdown("## 6개 분석 모듈 — 단일 의사결정 프레임")

# 1행
c1, c2, c3 = st.columns(3)
# 2행
c4, c5, c6 = st.columns(3)

modules = [
    ("①", "CII 베이스라인", "탄소집약도 산출",
     "10개 파일럿 노선 × ICAO ICEC v13<br>4-Layer 검증, GIR↔KAC <strong>0.008%</strong> 일치",
     "5,358,900 tCO₂/yr"),
    ("②", "SAF 시뮬레이션", "5 전략 · 4 감축률",
     "α∈{1%,3%,5%,7%,10%} × 가격 grid × 감축률<br>2027 SAF 1% = <strong>45.2 kt</strong> (CORSIA)",
     "331억 원/년"),
    ("③", "지상운항 + GBM", "137만 편 · AI 회귀",
     "GBM Top 피처: <strong>flights 58.9%</strong><br>A-SMGCS 41% = <strong>44,366 t</strong>",
     "108,209 tCO₂/yr"),
    ("④", "유가·할증료 예측", "8 모델 비교",
     "Naive·SARIMA·LSTM·Prophet·HW·Transformer<br>Naive Val MAE <strong>4.22 ★</strong> (DM 검정)",
     "단계 0.58 흡수"),
    ("⑤", "통합 의사결정", "정부·항공사·소비자",
     "3주체별 단일 함수<br>합병사 부담 <strong>134.6억/yr</strong>",
     "정부 1.06× 정합 ✓"),
    ("⑥", "4차원 매트릭스", "노선×α×가격×감축률",
     "450 조합 시뮬레이션<br>정부 목표 달성 <strong>39/45 (87%)</strong>",
     "5 전략 1.91×"),
]
for col, (idx, name, sub, body, key) in zip([c1, c2, c3, c4, c5, c6], modules):
    with col:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div style='font-family:"Cormorant Garamond",serif; font-size:2.6rem; color:#6ee7b7; line-height:1; margin-bottom:0.3rem;'>{idx}</div>
                <div style='font-weight:600; font-size:1.05rem; color:#f0f4f8;'>{name}</div>
                <div style='font-size:0.78rem; color:#94a3b8; letter-spacing:0.05em; margin-bottom:0.9rem;'>{sub}</div>
                <div style='font-size:0.85rem; color:#cbd5e1; line-height:1.6; min-height:60px;'>{body}</div>
                <hr class='divider-thin' style='margin:0.9rem 0;'>
                <div style='font-family:"IBM Plex Mono",monospace; font-size:1.05rem; color:#fcd34d;'>{key}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# ============================================================
# 분석 흐름 다이어그램
# ============================================================
st.markdown("<span class='eyebrow'>Analysis Storyline</span>", unsafe_allow_html=True)
st.markdown("## 분석 흐름")

flow_svg = """
<svg viewBox="0 0 1200 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">
  <defs>
    <linearGradient id="grad1" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#6ee7b7" stop-opacity="0.0"/>
      <stop offset="0.5" stop-color="#6ee7b7" stop-opacity="0.4"/>
      <stop offset="1" stop-color="#6ee7b7" stop-opacity="0.0"/>
    </linearGradient>
    <marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L9,3 L0,6 Z" fill="#6ee7b7" opacity="0.6"/>
    </marker>
  </defs>

  <!-- 가로 라인 -->
  <line x1="60" y1="180" x2="1140" y2="180" stroke="url(#grad1)" stroke-width="1.5"/>

  <!-- 4 노드 -->
  <g font-family="IBM Plex Sans KR, sans-serif" fill="#e8eaed">
    <!-- 모듈① -->
    <circle cx="160" cy="180" r="44" fill="rgba(110,231,183,0.06)" stroke="#6ee7b7" stroke-width="1.2"/>
    <text x="160" y="174" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="36" fill="#6ee7b7">①</text>
    <text x="160" y="200" text-anchor="middle" font-size="11" fill="#94a3b8">CII</text>
    <text x="160" y="78" text-anchor="middle" font-size="13" font-weight="600">현실 진단</text>
    <text x="160" y="98" text-anchor="middle" font-size="11" fill="#94a3b8">베이스라인 5.36 MtCO₂/yr</text>
    <text x="160" y="280" text-anchor="middle" font-size="11" fill="#94a3b8">v2→v4 우선순위 뒤집힘</text>
    <text x="160" y="296" text-anchor="middle" font-size="11" fill="#94a3b8">단거리 PVG·PEK·KIX worst</text>

    <!-- 모듈② -->
    <circle cx="450" cy="180" r="44" fill="rgba(110,231,183,0.06)" stroke="#6ee7b7" stroke-width="1.2"/>
    <text x="450" y="174" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="36" fill="#6ee7b7">②</text>
    <text x="450" y="200" text-anchor="middle" font-size="11" fill="#94a3b8">SAF</text>
    <text x="450" y="78" text-anchor="middle" font-size="13" font-weight="600">정책 대응</text>
    <text x="450" y="98" text-anchor="middle" font-size="11" fill="#94a3b8">2027 1% → 49,816 tCO₂</text>
    <text x="450" y="280" text-anchor="middle" font-size="11" fill="#94a3b8">96 조합 × 시나리오 A/B/C</text>
    <text x="450" y="296" text-anchor="middle" font-size="11" fill="#94a3b8">정부 발표 16만t ÷ 30% = 정합</text>

    <!-- 모듈③ -->
    <circle cx="740" cy="180" r="44" fill="rgba(110,231,183,0.06)" stroke="#6ee7b7" stroke-width="1.2"/>
    <text x="740" y="174" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="36" fill="#6ee7b7">③</text>
    <text x="740" y="200" text-anchor="middle" font-size="11" fill="#94a3b8">Ground</text>
    <text x="740" y="78" text-anchor="middle" font-size="13" font-weight="600">숨겨진 비용</text>
    <text x="740" y="98" text-anchor="middle" font-size="11" fill="#94a3b8">지연→탄소 108,209 tCO₂/yr</text>
    <text x="740" y="280" text-anchor="middle" font-size="11" fill="#94a3b8">A-SMGCS 44,366 t (비용≈0)</text>
    <text x="740" y="296" text-anchor="middle" font-size="11" fill="#94a3b8">SAF 1%의 89% 효과</text>

    <!-- 모듈④ -->
    <circle cx="1030" cy="180" r="44" fill="rgba(110,231,183,0.06)" stroke="#6ee7b7" stroke-width="1.2"/>
    <text x="1030" y="174" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="36" fill="#6ee7b7">④</text>
    <text x="1030" y="200" text-anchor="middle" font-size="11" fill="#94a3b8">Fuel</text>
    <text x="1030" y="78" text-anchor="middle" font-size="13" font-weight="600">소비자 흡수</text>
    <text x="1030" y="98" text-anchor="middle" font-size="11" fill="#94a3b8">SAF 부담 1,756원/명</text>
    <text x="1030" y="280" text-anchor="middle" font-size="11" fill="#94a3b8">단계 0.77 = 단계 1 미만</text>
    <text x="1030" y="296" text-anchor="middle" font-size="11" fill="#94a3b8">체감 거의 없음</text>
  </g>

  <!-- 화살표 (라인 위 ▶) -->
  <g>
    <path d="M 215 180 L 396 180" stroke="#6ee7b7" stroke-width="1" opacity="0.4" marker-end="url(#arr)" fill="none"/>
    <path d="M 505 180 L 686 180" stroke="#6ee7b7" stroke-width="1" opacity="0.4" marker-end="url(#arr)" fill="none"/>
    <path d="M 795 180 L 976 180" stroke="#6ee7b7" stroke-width="1" opacity="0.4" marker-end="url(#arr)" fill="none"/>
  </g>

  <!-- 통합 메시지 박스 -->
  <g transform="translate(420, 326)">
    <text x="180" y="14" text-anchor="middle" font-family="Cormorant Garamond, serif" font-style="italic" font-size="16" fill="#fcd34d">
      SAF만으로는 부족. SAF + 지상 운영 = 같은 비용, 2배 효과.
    </text>
  </g>
</svg>
"""
st.markdown(flow_svg, unsafe_allow_html=True)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# ============================================================
# 데이터 융합 가점 어필
# ============================================================
c1, c2 = st.columns([1.2, 1])
with c1:
    st.markdown("<span class='eyebrow'>Data Fusion · Bonus</span>", unsafe_allow_html=True)
    st.markdown("## 데이터 융합")
    st.markdown(
        """
        <p style='line-height:1.75; color:#cbd5e1;'>
        GreenSky는 <strong>11개 출처 × 5개 부처·기관</strong>의 데이터를
        ICAO ICEC v13 + EG-TIPS + CORSIA 방법론으로 통합 검증합니다.
        분석 핵심 동등성으로 <strong>페트로넷 등유 = KAL MOPS Jet-A1</strong> (3개월 대조 Δ 0.01 이내),
        <strong>GIR ↔ KAC 0.008% 일치</strong>가 확인되었습니다.
        </p>
        """,
        unsafe_allow_html=True,
    )
    fusion = pd.DataFrame({
        "출처": ["국토교통부 항공정보포털", "기상청 항공기상청", "한국석유공사 페트로넷",
                "한국공항공사 (KAC) ESG", "인천국제공항공사 (IIAC) ESG",
                "환경부 GIR 명세서", "산업부·국토부 SAF 보도자료",
                "대한항공 유류할증료 공지", "ICAO ICEC v13 + Appx A",
                "EG-TIPS (국가고유 EF)", "U.S. EIA (보조)"],
        "역할": ["운항·여객·노선·출도착", "기상 14종 (시정·RVR·풍속 등)", "MOPS Jet-A1 77개월",
                "Scope1·2·3, A-CDM 16,239t", "Scope1·2·3, A-SMGCS 41%·2045 탄소중립",
                "L2-A 교차검증", "2027 1% 의무화 정책 지표",
                "MOPS·단계·9구간 단가", "P/C·LF 한국 4 Route Group",
                "EF_jet 2.49 kgCO₂/L", "장기 시계열 보조"],
        "모듈": ["①②③", "③ GBM", "②④", "①②③", "①②③", "①", "②", "②④", "①", "①", "④"],
    })
    st.dataframe(fusion, use_container_width=True, hide_index=True, height=440)

with c2:
    st.markdown("<span class='eyebrow'>Differentiation</span>", unsafe_allow_html=True)
    st.markdown("## 수상작 대비 차별점")
    diff = pd.DataFrame({
        "항목": ["주제 영역", "시의성", "데이터 검증", "융합 가점",
                "AI 가점", "정직 공개"],
        "2024·2025 수상작": ["소음·조류·주차 (운영)", "운영 개선", "단일 데이터",
                          "1~2개 출처", "분야별 상이", "없음"],
        "GreenSky v1.3": ["탄소·비용·정책 (구조)", "2027 SAF 직전", "4-Layer 0.008%",
                         "11개 × 5개 부처", "LSTM + GBM 2종", "Naive > LSTM 인정"],
    })
    st.dataframe(diff, use_container_width=True, hide_index=True, height=300)

    st.markdown(
        """
        <div style='background:rgba(252,211,77,0.05); border-left:3px solid #fcd34d;
                    padding:1rem 1.2rem; margin-top:1rem;'>
            <div style='font-family:"Cormorant Garamond",serif; font-style:italic; font-size:1.1rem; color:#fcd34d;'>
                "정량 입증과 학술적 정직성"
            </div>
            <div style='font-size:0.85rem; color:#cbd5e1; margin-top:0.4rem; line-height:1.6;'>
                GreenSky는 LSTM이 Naive보다 떨어지는 구간을 숨기지 않고 공개합니다.
                심사위원이 신뢰할 수 있는 분석 도구의 기본입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div style='text-align:center; color:#64748b; font-size:0.8rem; padding:1.5rem 0;'>
        <span class='serif-accent'>GreenSky</span> · v1.0 prototype · 2026 국토교통 데이터 활용 경진대회<br>
        Data: 항공정보포털 · 기상청 · 페트로넷 · KAC/IIAC ESG · GIR · ICAO · EIA<br>
        Methodology: ICAO ICEC v13 · CORSIA · EG-TIPS · 자체 §9 검증 회귀
    </div>
    """,
    unsafe_allow_html=True,
)
