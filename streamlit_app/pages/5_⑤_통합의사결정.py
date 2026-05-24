"""
페이지 ⑤ — 통합 의사결정 엔진
=================================
3주체(정부·항공사·소비자) 인터랙티브 시뮬레이터
사용자가 슬라이더로 α·가격·감축률·점유율 조정 → 즉시 결과 산출
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import apply_global_style, hero_metric

apply_global_style()

# ============================================================
# 상수 (검증 완료)
# ============================================================
EF_KG_L = 2.528  # ICAO EF
USD_KRW = 1300
SHORT_STAGE = 2275
PAX_10ROUTES = 25_000_000
TOTAL_FUEL_L = 2_119_800_000

HEFA_RATES = {
    'Pessimistic (60%)': 0.60,
    'Conservative (Neste 80%)': 0.80,
    'CORSIA Default (84.4%) ★ 권장': 0.844,
    'Optimistic (v4 원본 93%)': 0.93,
}

ROUTE_MULTI = {
    'short': 1.36, 'mid': 3.42, 'long': 7.52,
}
ROUTE_LABELS = {
    'short': '단거리 (m=1.36)', 'mid': '중거리 (m=3.42)', 'long': '장거리 (m=7.52)',
}

# ============================================================
# 헤더
# ============================================================
st.markdown("<span class='eyebrow'>Module 5 · Integrated Decision Engine</span>", unsafe_allow_html=True)
st.markdown("# ⑤ 통합 의사결정 엔진")
st.markdown(
    "<p style='color:#94a3b8; font-size:1.05rem;'>"
    "정부·항공사·소비자 <span class='serif-accent'>3주체</span>가 각자의 입력으로 즉시 정책 효과를 시뮬레이션."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# ============================================================
# 3 탭 — 주체별
# ============================================================
tab_gov, tab_air, tab_con, tab_about = st.tabs([
    "🏛 정부", "✈ 항공사", "👤 소비자", "📊 의사결정 가이드"
])

# ─────────────────────────────────────────────────────
# 정부 탭
# ─────────────────────────────────────────────────────
with tab_gov:
    st.markdown("### 정부 — 목표 감축량 달성에 필요한 α 추정")
    st.markdown(
        "<p style='color:#94a3b8; font-size:0.9rem;'>"
        "정부 16만 t 감축 목표 (우리 커버리지 30% = 48 kt 도달 기준)"
        "</p>",
        unsafe_allow_html=True,
    )

    g1, g2, g3 = st.columns([2, 2, 3])
    with g1:
        gov_target = st.slider(
            "감축 목표 (kt/yr)", 20.0, 100.0, 48.0, 1.0,
            help="우리 10 노선 커버리지 30% 기준 목표"
        )
    with g2:
        gov_price = st.slider(
            "SAF 시장가 (USD/L)", 0.8, 2.5, 1.2, 0.05,
            help="HEFA-SAF 시장 실측 1.1~1.4 USD/L"
        )
    with g3:
        gov_scenario = st.selectbox(
            "감축률 시나리오",
            list(HEFA_RATES.keys()),
            index=2,  # CORSIA Default 기본
        )

    rate = HEFA_RATES[gov_scenario]
    needed_alpha = gov_target * 1e6 / (TOTAL_FUEL_L * EF_KG_L * rate)
    saf_L = TOTAL_FUEL_L * needed_alpha
    cost_oku = saf_L * gov_price * USD_KRW / 1e8
    burden_per_pax = cost_oku * 1e8 / PAX_10ROUTES
    stage = burden_per_pax / SHORT_STAGE

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(hero_metric("권장 α", f"{needed_alpha*100:.2f}%",
                                 "정부 1% 정합 ✓" if abs(needed_alpha - 0.01) < 0.002
                                 else f"정부 1% 대비 {needed_alpha/0.01:.2f}×"), unsafe_allow_html=True)
    with m2:
        st.markdown(hero_metric("예상 비용", f"{cost_oku:.0f} 억", f"USD/L {gov_price}"), unsafe_allow_html=True)
    with m3:
        st.markdown(hero_metric("소비자 부담", f"{burden_per_pax:,.0f} 원", f"단계 {stage:.2f}"), unsafe_allow_html=True)
    with m4:
        match_status = "정합 ✓" if abs(needed_alpha - 0.01) < 0.002 else ("초과" if needed_alpha < 0.01 else "추가 필요")
        st.markdown(hero_metric("정부 1% 정합", match_status, ""), unsafe_allow_html=True)

    # 시나리오 비교 표 (4 감축률 모두)
    st.markdown("##### 🔍 4 감축률 시나리오 동시 비교")
    rows = []
    for sc, r in HEFA_RATES.items():
        a = gov_target * 1e6 / (TOTAL_FUEL_L * EF_KG_L * r)
        c = TOTAL_FUEL_L * a * gov_price * USD_KRW / 1e8
        rows.append({
            "시나리오": sc,
            "감축률": f"{r*100:.1f}%",
            "필요 α": f"{a*100:.2f}%",
            "비용 (억)": f"{c:.0f}",
            "정부 1% 대비": f"{a/0.01:.2f}×",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────
# 항공사 탭
# ─────────────────────────────────────────────────────
with tab_air:
    st.markdown("### 항공사 — 점유율 기준 SAF 부담 추정")
    st.markdown(
        "<p style='color:#94a3b8; font-size:0.9rem;'>"
        "한진통합사 운항 점유 40.7% (2026.12 이후) 기준 권장"
        "</p>",
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns(3)
    with a1:
        air_share = st.slider("자사 운항 점유율 (%)", 5.0, 50.0, 40.7, 0.1)
    with a2:
        air_alpha = st.slider("의무비율 α (%)", 0.5, 10.0, 1.0, 0.1)
    with a3:
        air_strategy = st.selectbox(
            "배분 전략",
            ['균등', '탄소우선', 'CII우선 ★ 효율 최우수', '트렌드우선', '복합'],
            index=2,
        )

    strategy_effects = {
        '균등': (0.603, 13.20, '행정 단순'),
        '탄소우선': (0.603, 13.20, 'CO2 비례, 균등과 동일'),
        'CII우선 ★ 효율 최우수': (1.153, 12.42, '효율 1.91× 균등'),
        '트렌드우선': (1.135, 12.46, '악화 노선 가중'),
        '복합': (0.871, 12.93, '50CII+30Δ+20CO2'),
    }
    cii_red, cii_sigma, note = strategy_effects[air_strategy]

    saf_total = TOTAL_FUEL_L * air_alpha/100
    cost_total = saf_total * 1.2 * USD_KRW / 1e8
    co2_total = saf_total * EF_KG_L * 0.844 / 1e6  # CORSIA 기준

    own_share = air_share / 100
    own_cost = cost_total * own_share
    own_co2 = co2_total * own_share
    own_5yr = own_cost * 5

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(hero_metric("자사 SAF 부담", f"{own_cost:.1f} 억/yr",
                                 f"점유율 {air_share}%"), unsafe_allow_html=True)
    with m2:
        st.markdown(hero_metric("자사 CO2 감축", f"{own_co2:.2f} kt/yr", "CORSIA 84.4%"), unsafe_allow_html=True)
    with m3:
        st.markdown(hero_metric("5년 누적 비용", f"{own_5yr:.0f} 억", f"α=t{air_alpha}% 고정"), unsafe_allow_html=True)
    with m4:
        st.markdown(hero_metric("평균 CII 감소", f"{cii_red:.2f} g/PKT",
                                 f"σ {cii_sigma:.2f}"), unsafe_allow_html=True)

    st.info(f"💡 **{air_strategy}**: {note}")

    # 5 전략 비교
    st.markdown("##### 🔍 5 배분 전략 효율 비교 (동일 비용·동일 총 CO2)")
    df_strat = pd.DataFrame([
        {"전략": s, "평균 CII 감소": f"{e[0]:.2f}", "잔여 CII σ": f"{e[1]:.2f}",
         "1.91× 효과": f"{e[0]/0.603:.2f}×", "메모": e[2]}
        for s, e in strategy_effects.items()
    ])
    st.dataframe(df_strat, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────
# 소비자 탭
# ─────────────────────────────────────────────────────
with tab_con:
    st.markdown("### 소비자 — 노선 type별 1편 추가 부담")
    st.markdown(
        "<p style='color:#94a3b8; font-size:0.9rem;'>"
        "현재 2026.05 단계 23 부담 대비 SAF 의무화 추가 부담"
        "</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        con_route = st.selectbox(
            "노선 type",
            ['short', 'mid', 'long'],
            format_func=lambda x: ROUTE_LABELS[x],
        )
    with c2:
        con_alpha = st.slider("의무비율 α (%)", 0.5, 10.0, 1.0, 0.1, key="con_alpha")
    with c3:
        con_price = st.slider("SAF 가격 (USD/L)", 0.8, 2.5, 1.2, 0.05, key="con_price")

    m = ROUTE_MULTI[con_route]
    saf_L = TOTAL_FUEL_L * con_alpha/100
    cost_oku = saf_L * con_price * USD_KRW / 1e8
    avg_burden = cost_oku * 1e8 / PAX_10ROUTES
    route_extra = avg_burden * m
    stage = avg_burden / SHORT_STAGE
    current_fare = 23 * SHORT_STAGE * m  # 현재 단계 23
    pct_inc = route_extra / current_fare * 100
    perception = "거의 없음" if stage < 1 else ("체감 약함" if stage < 2 else "체감 있음")

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(hero_metric("1편 추가 부담", f"{route_extra:,.0f} 원",
                                 f"{ROUTE_LABELS[con_route].split(' ')[0]}"), unsafe_allow_html=True)
    with m2:
        st.markdown(hero_metric("평균 부담 (전체 노선)", f"{avg_burden:,.0f} 원",
                                 f"단계 {stage:.2f}"), unsafe_allow_html=True)
    with m3:
        st.markdown(hero_metric("현재 부담 대비", f"+{pct_inc:.2f}%",
                                 f"현재 {current_fare:,.0f}원"), unsafe_allow_html=True)
    with m4:
        st.markdown(hero_metric("체감 평가", perception, ""), unsafe_allow_html=True)

    # 3 노선 type 동시 비교
    st.markdown("##### 🔍 3 노선 type 동시 비교 (선택된 α, 가격 적용)")
    rows = []
    for rt in ['short', 'mid', 'long']:
        m_ = ROUTE_MULTI[rt]
        extra = avg_burden * m_
        current = 23 * SHORT_STAGE * m_
        rows.append({
            "노선 type": ROUTE_LABELS[rt],
            "1편 추가 (원)": f"{extra:,.0f}",
            "현재 (단계 23)": f"{current:,.0f}",
            "% 증가": f"+{extra/current*100:.2f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────
# 가이드 탭
# ─────────────────────────────────────────────────────
with tab_about:
    st.markdown("### 의사결정 가이드 — 누가 무엇을 묻는가")

    st.markdown(
        """
        | 주체 | 핵심 질문 | 권장 답 |
        |---|---|---|
        | **정부** | "16만 t 목표 달성에 필요한 α는?" | CORSIA 84.4% 기준 **α=1.06%** (정부 1% 정합 ✓) |
        | **항공사** | "우리 회사 SAF 부담은?" | 한진통합 40.7% × 331억 = **134.6억/yr** |
        | **소비자** | "내 항공권은 얼마 오르나?" | 단거리 +536원, 장거리 +6,750원 (단계 0.20~0.40) |
        """
    )

    st.markdown("##### 📊 권장 시나리오 (CORSIA Default 84.4%)")
    st.success(
        """
        - **2027 α=1%**: 감축 45.2 kt, 비용 331억, 소비자 단계 0.58
        - **정부 16만 t 정합**: 1.06× = 사실상 정합 ✓
        - **한진통합사 분담**: 134.6억/yr (40.7%)
        - **5 전략 1.91× 효과**: CII우선 추천 (동일 비용·1.91배 효율)
        """
    )

    st.markdown("##### ⚠️ 4 감축률 시나리오 — 위험 평가")
    df_risk = pd.DataFrame([
        {"시나리오": "Pessimistic (60%)", "필요 α": "1.49%", "비용": "494억", "정부 1%": "1.49× 필요"},
        {"시나리오": "Conservative (80%)", "필요 α": "1.12%", "비용": "370억", "정부 1%": "정합 ✓"},
        {"시나리오": "CORSIA Default (84.4%) ★", "필요 α": "1.06%", "비용": "351억", "정부 1%": "정합 ✓"},
        {"시나리오": "Optimistic (93%)", "필요 α": "0.96%", "비용": "319억", "정부 1%": "정합 (여유)"},
    ])
    st.dataframe(df_risk, use_container_width=True, hide_index=True)

st.markdown("<hr class='divider-thin' style='margin-top:3rem;'>", unsafe_allow_html=True)
st.caption("GreenSky v2.0 · 통합 의사결정 엔진 · 카탈로그 §35 / §28 / §47")
