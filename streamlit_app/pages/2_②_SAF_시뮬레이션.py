"""모듈② — SAF 시뮬레이션 (인터랙티브)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import CSS, apply_layout, page_header, sidebar_nav, load_m2, ACCENT, GRID_COLOR

st.set_page_config(page_title="모듈② SAF | GreenSky", page_icon="🌱", layout="wide")
sidebar_nav("모듈② SAF 시뮬레이션")
page_header(
    "Module 2 · SAF Optimization",
    "SAF 도입 시뮬레이션",
    "α∈{1%, 3%, 5%, 7%, 10%} 의무비율 × SAF 가격 grid × <strong>5 전략</strong>(균등·탄소·CII·트렌드·복합) × "
    "<strong>4 감축률</strong> 시나리오. "
    "<span style='color:#6ee7b7;'>v2.0 — CORSIA Default 84.4% + 시장가 1.2 USD/L 권장.</span>",
)

data = load_m2()
sim = data["2_시뮬레이션_96조합"]
scenarios = data["3_시나리오_ABC_헤드라인"]
sens = data["4_소비자영향_α민감도"]
routes = data["5_소비자영향_노선별"]
baseline = data["1_베이스라인_v4"]

# v2 신규 데이터
DATA_V2 = Path(__file__).parent.parent / "data" / "v2"
@st.cache_data
def load_v2():
    d = {}
    try:
        d['reduction'] = pd.read_excel(DATA_V2 / "greensky_module2_v7_reduction_scenarios.xlsx",
                                        sheet_name='3_시장가_1.2_USD')
    except Exception:
        d['reduction'] = None
    try:
        d['allocation'] = pd.read_excel(DATA_V2 / "greensky_module2_v6_allocation.xlsx",
                                         sheet_name='1_5전략_요약')
    except Exception:
        d['allocation'] = None
    try:
        d['airline'] = pd.read_excel(DATA_V2 / "greensky_module2_v6_airline_burden.xlsx",
                                      sheet_name='3_합병효과')
    except Exception:
        d['airline'] = None
    return d
v2 = load_v2()

# 핵심 지표 (v2 갱신 — CORSIA Default 권장)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("<div class='metric-card'><div class='eyebrow'>2027 SAF 1% · CORSIA</div>"
                "<div class='hero-num'>45.2<span class='hero-unit'>kt/yr</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>HEFA-UCO Default 84.4%</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='metric-card'><div class='eyebrow'>비용 (시장가)</div>"
                "<div class='hero-num'>331<span class='hero-unit'>억/yr</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>1.2 USD/L 기준</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='metric-card'><div class='eyebrow'>정부 16만 t 정합</div>"
                "<div class='hero-num'>1.06<span class='hero-unit'>× ✓</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>사실상 정합</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='metric-card'><div class='eyebrow'>소비자 부담</div>"
                "<div class='hero-num'>1,323<span class='hero-unit'>원/명</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>단계 0.58 (체감 없음)</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "🎛 인터랙티브 시뮬", "📈 시나리오 A/B/C", "💰 소비자 민감도", "🛫 노선별 영향",
    "📋 원본 데이터", "🎯 4 감축률 ★", "🏢 5 전략 + 항공사 ★"
])

with t1:
    st.markdown("### 시뮬레이션 96 조합 — Pareto Frontier 탐색")

    col1, col2 = st.columns([1, 3])
    with col1:
        sel_strategy = st.multiselect("전략", sim['strategy'].unique().tolist(), default=sim['strategy'].unique().tolist())
        sel_alpha = st.multiselect("α (의무비율)", sorted(sim['alpha'].unique().tolist()), default=sorted(sim['alpha'].unique().tolist()))
        sel_price = st.slider("SAF 가격 (USD/L)", float(sim['price_USD'].min()), float(sim['price_USD'].max()),
                             (float(sim['price_USD'].min()), float(sim['price_USD'].max())), step=0.5)

    with col2:
        f = sim[
            sim['strategy'].isin(sel_strategy) &
            sim['alpha'].isin(sel_alpha) &
            sim['price_USD'].between(sel_price[0], sel_price[1])
        ]
        fig = px.scatter(
            f, x='추가비용_억원', y='CO2_감축_kt',
            color='strategy', symbol='alpha',
            size='평균CII_감소' if '평균CII_감소' in f.columns else None,
            hover_data={'price_USD': True, 'alpha': True, 'strategy': True},
            color_discrete_sequence=[ACCENT, '#7dd3fc', '#fcd34d', '#f472b6'],
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color='rgba(0,0,0,0.3)')))
        fig.update_layout(
            title=dict(text='SAF 도입 — 추가비용 vs CO₂ 감축 (Pareto Frontier)', font=dict(size=14)),
            xaxis_title='추가 비용 (억 원/년)',
            yaxis_title='CO₂ 감축 (kt/년)',
        )
        apply_layout(fig, height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>최적 조합 탐색</strong> · 동일 의무비율(α)에서 전략별로 추가비용·감축량이 다릅니다. "
        "<span class='serif-accent'>탄소우선 전략</span>이 일반적으로 효율적이나, α=5% 고비율에서는 균등 분배의 행정 부담이 낮습니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t2:
    st.markdown("### 시나리오 A/B/C — 2027/2030/2035 SAF 의무화 로드맵")
    fig = go.Figure()
    for sc in scenarios['시나리오'].unique():
        d = scenarios[scenarios['시나리오']==sc]
        fig.add_trace(go.Scatter(
            x=d['연도'], y=d['CO2_감축_kt'],
            mode='lines+markers', name=f'{sc}',
            line=dict(width=2.5), marker=dict(size=10),
        ))
    fig.update_layout(
        title=dict(text='시나리오별 연도 × CO₂ 감축 경로', font=dict(size=14)),
        xaxis_title='연도', yaxis_title='CO₂ 감축 (kt/년)',
    )
    apply_layout(fig, height=440)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(scenarios, use_container_width=True, hide_index=True)

with t3:
    st.markdown("### 소비자 영향 — α 민감도 분석")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"α={a*100:.0f}%" for a in sens['α']],
        y=sens['단거리_단가_원'],
        marker_color=[ACCENT if a<=0.01 else ('#fcd34d' if a<=0.03 else '#f87171') for a in sens['α']],
        text=[f"{v:,}원" for v in sens['단거리_단가_원']],
        textposition='outside',
    ))
    fig.update_layout(
        title=dict(text='α별 단거리 1편 유류할증료 영향', font=dict(size=14)),
        xaxis_title='SAF 의무비율 α', yaxis_title='단거리 단가 (원/명/편도)',
    )
    apply_layout(fig, height=420, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>핵심 메시지</strong> · α=1% 의무화 시 MOPS 환산 단계 변동이 거의 없어 "
        "소비자 단가는 <strong>변동 없음</strong>에 가깝습니다. α=3%·5%에서 단계 1~3 인상 가능."
        "</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(sens, use_container_width=True, hide_index=True)

with t4:
    st.markdown("### 10 노선별 SAF 도입 영향")
    st.dataframe(routes, use_container_width=True, hide_index=True, height=400)

with t5:
    st.markdown("### 베이스라인 (모듈② 입력)")
    st.dataframe(baseline, use_container_width=True, hide_index=True)
    st.markdown("### 시뮬레이션 96 조합 (전체)")
    st.dataframe(sim, use_container_width=True, hide_index=True, height=300)

with t6:
    st.markdown("### 4 감축률 시나리오 — 정책 위험 평가 ★ v2 신규")
    st.caption("v4 원본의 93% 감축률은 낙관. CORSIA Default 84.4% = 정부 1% 목표와 사실상 정합.")
    st.markdown(
        """
        | 시나리오 | 감축률 | 2027 α=1% CO2 | 정부 16만t 정합 |
        |---|---|---|---|
        | Pessimistic | **60%** | 32.2 kt | 1.49× 필요 |
        | Conservative (Neste 실측) | **80%** | 42.9 kt | 1.12× 필요 |
        | **CORSIA Default ★ 권장** | **84.4%** | **45.2 kt** | **1.06× 정합 ✓** |
        | Optimistic (v4 원본) | **93%** | 49.8 kt | 0.96× (여유) |
        """
    )

    if v2['reduction'] is not None:
        st.markdown("##### 전체 감축률 × α 매트릭스 (시장가 1.2 USD/L 기준)")
        red_df = v2['reduction'].copy()
        red_df['alpha_%'] = red_df['alpha'] * 100
        show = red_df[['reduce_scenario','alpha_%','co2_saved_kt','cost_oku','burden_per_pax_won','stage_equiv']]
        show.columns = ['시나리오','α (%)','CO2 감축 (kt)','비용 (억)','부담 (원/명)','단계']
        st.dataframe(show, use_container_width=True, hide_index=True, height=380)

    st.markdown(
        """
        <div class='callout-good'>
            <strong>💡 정직 공개</strong> — 모듈② v4 원본의 49.8 kt는 93% 감축률 가정에 의존.
            CORSIA HEFA-UCO Default 표준 84.4% (=89−13.9/89) 적용 시 45.2 kt가 권장값.
            GreenSky는 4 감축률 시나리오를 모두 제공해 <strong>정책 위험 평가 도구</strong>로 차별화.
        </div>
        """,
        unsafe_allow_html=True
    )

with t7:
    st.markdown("### 5 배분 전략 비교 — CII우선 1.91× 효과 ★ v2 신규")

    if v2['allocation'] is not None:
        alloc = v2['allocation']
        st.dataframe(alloc, use_container_width=True, hide_index=True)

        # 막대 차트 — 평균 CII 감소
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=alloc['전략'],
            y=alloc['평균_CII_감소'],
            marker=dict(color=['#94a3b8','#94a3b8','#6ee7b7','#7dd3fc','#fcd34d']),
            text=alloc['평균_CII_감소'].round(2),
            textposition='outside',
        ))
        fig.update_layout(
            title="평균 CII 감소량 (g/PKT) — 같은 SAF 21,200 kL, 다른 배분",
            yaxis_title="g/PKT (높을수록 우수)",
        )
        apply_layout(fig, height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class='callout-good'>
            ★ <strong>CII우선 전략</strong>: 균등 대비 평균 CII 감소 1.91배 (0.603 → 1.153 g/PKT).
            <strong>총 CO2 감축은 동일</strong>(SAF량 동일), 그러나 노선 간 효율 격차 해소가 빠름.
            <br>→ 5년 누적 시 잔여 CII 표준편차 σ=9.74 vs 균등 σ=12.62 (23% 격차 해소)
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("##### 🏢 항공사별 SAF 부담 — 합병 효과")
    if v2['airline'] is not None:
        st.dataframe(v2['airline'], use_container_width=True, hide_index=True, height=320)

    st.markdown(
        """
        <div class='callout'>
            <strong>2026.12 한진통합 (대한항공+아시아나) 효과</strong>:
            <br>· 운항 점유 <strong>40.7%</strong> 단일 의사결정
            <br>· 2027 SAF 1% 부담 <strong>134.6억 원/yr</strong>
            <br>· B2B 영업 타겟이 30+ 항공사에서 사실상 5~6개로 단순화
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)
st.caption("Sources: 산업부·국토부 SAF 보도자료 (2024.08, 2025.09) · CORSIA HEFA-UCO · ICAO ICEC v13")
