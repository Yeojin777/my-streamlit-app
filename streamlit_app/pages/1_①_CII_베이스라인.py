"""모듈① — CII 베이스라인"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import CSS, apply_layout, page_header, sidebar_nav, load_m1, ACCENT, GRID_COLOR

st.set_page_config(page_title="모듈① CII | GreenSky", page_icon="🛫", layout="wide")
sidebar_nav("모듈① CII 베이스라인")
page_header(
    "Module 1 · Carbon Intensity",
    "탄소집약도(CII) 베이스라인",
    "ICAO ICEC v13 + 한국 4 Route Group P/C factor 적용. 인천 출발 10개 파일럿 노선, "
    "운항 27% · 여객 30% 커버리지. 4-Layer 검증으로 GIR ↔ KAC <strong>0.008% 일치</strong> 확인.",
)

df = load_m1()
df = df.sort_values(['year','dist_km'])

# 핵심 지표
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("<div class='metric-card'><div class='eyebrow'>분석 노선</div>"
                "<div class='hero-num'>10<span class='hero-unit'>개</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem; margin-top:0.3rem;'>인천 출발 국제선</div></div>",
                unsafe_allow_html=True)
with c2:
    st.markdown("<div class='metric-card'><div class='eyebrow'>본 비행 CO₂</div>"
                "<div class='hero-num'>5.36<span class='hero-unit'>MtCO₂/yr</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem; margin-top:0.3rem;'>2025 베이스라인</div></div>",
                unsafe_allow_html=True)
with c3:
    st.markdown("<div class='metric-card'><div class='eyebrow'>GIR ↔ KAC</div>"
                "<div class='hero-num'>0.008<span class='hero-unit'>%</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem; margin-top:0.3rem;'>L2-A 교차검증 일치</div></div>",
                unsafe_allow_html=True)
with c4:
    st.markdown("<div class='metric-card'><div class='eyebrow'>커버리지</div>"
                "<div class='hero-num'>27<span class='hero-unit'>% / 30%</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem; margin-top:0.3rem;'>운항 / 여객</div></div>",
                unsafe_allow_html=True)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# 탭으로 분할
t1, t2, t3, t4 = st.tabs(["📊 노선별 CII", "🔄 v2 vs v4 우선순위", "🔬 4-Layer 검증", "📋 원본 데이터"])

with t1:
    st.markdown("### 노선별 CII (gCO₂/PKT) — 2025 기준")
    df25 = df[df['year']==2025].copy().sort_values('cii_v4')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df25['iata'], x=df25['cii_v4'], orientation='h',
        marker_color=ACCENT, marker_line_width=0,
        text=df25['cii_v4'].round(1), textposition='outside',
        textfont=dict(color='#cbd5e1'),
        name='CII v4 (ICAO ICEC)',
        hovertemplate='<b>%{y}</b><br>CII: %{x:.1f} gCO₂/PKT<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text='CII v4 (낮을수록 효율적)', font=dict(size=14)),
        xaxis_title='gCO₂ per Passenger·Kilometer (PKT)',
        yaxis_title=None,
    )
    apply_layout(fig, height=440, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout'>"
        "<strong>해석</strong> · 단거리 동북아 노선(PVG·PEK·KIX·NRT)이 장거리(LAX·CDG)보다 "
        "CII가 높습니다. 동일 거리당 연료 효율이 떨어지기 때문이며, "
        "이는 v2(EG-TIPS EF) → v4(ICAO ICEC v13 P/C·LF 정합) 전환 후 더 또렷해졌습니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t2:
    st.markdown("### 모듈① v2 → v4 마이그레이션 — 우선순위 뒤집힘")
    df25 = df[df['year']==2025].copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='v2 (EG-TIPS)', x=df25['iata'], y=df25['cii_v2'], marker_color='#94a3b8'))
    fig.add_trace(go.Bar(name='v4 (ICAO ICEC v13)', x=df25['iata'], y=df25['cii_v4'], marker_color=ACCENT))
    fig.update_layout(
        title=dict(text='v2 vs v4 노선별 CII', font=dict(size=14)),
        barmode='group', xaxis_title='노선', yaxis_title='gCO₂/PKT',
    )
    apply_layout(fig, height=440)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>분석 차별점</strong> · 기존 통념(장거리 = 탄소 많이 배출)은 절대량 기준입니다. "
        "1인-km 효율 기준에서는 단거리 동북아 노선이 더 비효율적이며, "
        "이는 SAF 우선 배분 전략을 완전히 뒤집습니다. 단순 데이터 분석을 넘어 정책 시그널을 만드는 모듈입니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t3:
    st.markdown("### 4-Layer 검증 결과")
    layers = pd.DataFrame({
        "Layer": ["L1 – Spot Check", "L2-A – GIR 교차검증", "L2-B – ICAO 역산",
                 "L3 – 노선·지역 정합성", "L4 – 시계열 일관성"],
        "검증 내용": [
            "6개 노선 임의 추출 → ICAO ICEC 웹툴 수동 계산값과 비교",
            "KAC 명세서(GIR) Scope1 vs 모듈① 산출 본 비행 합",
            "Y_eq 방법 A(ICAO 역산) vs 방법 B(좌석×1.35) 양 방법 비교",
            "Route Group #28/#37/#34/#18 노선 그룹별 평균 CII 상대 순위",
            "2023·2024·2025 3년 추세 + 코로나 회복 패턴 검증",
        ],
        "결과": [
            "오차 ±2.1% 이내",
            "**0.008% 일치** (94,103 t ↔ 94,111 t)",
            "단·중거리는 A, 장거리는 B 정합 → 혼합 적용",
            "전 그룹 단조 증가 (단거리>중거리>장거리 단조 깨짐 → 정합 ✓)",
            "2020 dip → 2023 회복, 단거리 변동성 ↑ (일관)",
        ],
    })
    st.dataframe(layers, use_container_width=True, hide_index=True, height=280)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>검증 핵심</strong> · L2-A에서 환경부 GIR 명세서 공시값과 모듈① 산출값이 "
        "<strong>0.008% 이내로 일치</strong>합니다. 데이터 분석 산출물이 공식 공시 통계와 정합한다는 "
        "강한 신뢰 근거이며, 학술 논문 수준의 검증 깊이입니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t4:
    st.markdown("### 원본 데이터 (xlsx 시트)")
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("CSV 다운로드", csv, "module1_cii.csv", "text/csv")

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)
st.caption("Sources: ICAO ICEC v13 · 항공정보포털 (2023~2025) · KAC ESG · GIR 명세서 · EG-TIPS")
