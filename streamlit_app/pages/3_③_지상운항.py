"""모듈③ — 지상운항 분석"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import CSS, apply_layout, page_header, sidebar_nav, load_m3, load_flights_summary, ACCENT, GRID_COLOR

st.set_page_config(page_title="모듈③ 지상운항 | GreenSky", page_icon="⏱", layout="wide")
sidebar_nav("모듈③ 지상운항 분석")
page_header(
    "Module 3 · Ground Operations + AI Regression",
    "지상운항 분석 — 지연 → 연료 → 탄소 인과사슬",
    "<strong>137만 편 실측 (23.01~26.05, 41개월)</strong> · DEP 출발 지연 발생률 평균 82%. "
    "<span style='color:#6ee7b7;'>v2.0 — GBM 회귀(AI 가점) + 결항 41개월 시계열 추가</span>",
)

data = load_m3()
routes = data["1_노선별"]
monthly = data["2_월별시계열"]
reasons = data["3_지연원인"]
scenarios = data["4_개입시나리오"]
consts = data["0_상수"]

# v2 신규
DATA_V2 = Path(__file__).parent.parent / "data" / "v2"
@st.cache_data
def load_v2():
    d = {}
    try:
        d['gbm'] = pd.read_excel(DATA_V2 / "greensky_module3_gbm_v1.xlsx", sheet_name='1_요약')
        d['gbm_imp'] = pd.read_excel(DATA_V2 / "greensky_module3_gbm_v1.xlsx", sheet_name='2_피처중요도')
        d['gbm_pred'] = pd.read_excel(DATA_V2 / "greensky_module3_gbm_v1.xlsx", sheet_name='3_예측_시계열')
        d['gbm_ins'] = pd.read_excel(DATA_V2 / "greensky_module3_gbm_v1.xlsx", sheet_name='5_정책인사이트')
    except Exception:
        d.update({'gbm': None, 'gbm_imp': None, 'gbm_pred': None, 'gbm_ins': None})
    try:
        d['canc'] = pd.read_excel(DATA_V2 / "greensky_module3_v2_cancellation.xlsx", sheet_name='1_월별시계열')
        d['canc_cause'] = pd.read_excel(DATA_V2 / "greensky_module3_v2_cancellation.xlsx", sheet_name='2_원인별누적')
    except Exception:
        d.update({'canc': None, 'canc_cause': None})
    return d
v2 = load_v2()

# 핵심 지표 (v2 갱신)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("<div class='metric-card'><div class='eyebrow'>분석 데이터</div>"
                "<div class='hero-num'>137<span class='hero-unit'>만 편</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>23.01~26.05 (41개월)</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='metric-card'><div class='eyebrow'>10 노선 DEP CO₂</div>"
                "<div class='hero-num'>108,209<span class='hero-unit'>tCO₂/yr</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>인천 전체 = 425,196 (9.4×)</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='metric-card'><div class='eyebrow'>A-SMGCS 효과</div>"
                "<div class='hero-num'>44,366<span class='hero-unit'>tCO₂/yr</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>비용 ≈ 0 (IIAC ESG)</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='metric-card'><div class='eyebrow'>GBM Top 피처</div>"
                "<div class='hero-num'>58.9<span class='hero-unit'>%</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>flights (운항량) ★</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "📅 월별 시계열", "🔧 지연 원인", "🛬 노선별", "🎯 개입 시나리오",
    "📋 원본 데이터", "🤖 GBM 회귀 ★", "✈️ 결항 분석 ★"
])

with t1:
    st.markdown("### 월별 운항·지연 시계열 (41개월)")
    monthly = monthly.copy()
    monthly['date'] = pd.to_datetime(monthly['file_year'].astype(str) + '-' + monthly['file_month'].astype(str).str.zfill(2))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['date'], y=monthly['delay_15plus'],
        name='15분 초과 지연 편수', marker_color=ACCENT, opacity=0.7,
    ))
    fig.add_trace(go.Scatter(
        x=monthly['date'], y=monthly['flights'],
        name='총 운항 편수', yaxis='y2',
        line=dict(color='#7dd3fc', width=2),
    ))
    fig.update_layout(
        title=dict(text='월별 운항·지연 추세 (41개월)', font=dict(size=14)),
        xaxis_title='년월',
        yaxis=dict(title='15분 초과 지연 편수', side='left'),
        yaxis2=dict(title='총 운항 편수', side='right', overlaying='y'),
        hovermode='x unified',
    )
    apply_layout(fig, height=440)
    st.plotly_chart(fig, use_container_width=True)

    if 'extra_fuel_kg' in monthly.columns:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=monthly['date'], y=monthly['extra_fuel_kg']/1000,
            mode='lines+markers', name='지연 추가 연료',
            line=dict(color='#fcd34d', width=2),
            fill='tozeroy', fillcolor='rgba(252,211,77,0.1)',
        ))
        fig2.update_layout(
            title=dict(text='월별 지연→추가 연료 (톤)', font=dict(size=14)),
            xaxis_title='년월', yaxis_title='추가 연료 (톤)',
        )
        apply_layout(fig2, height=380)
        st.plotly_chart(fig2, use_container_width=True)

with t2:
    st.markdown("### 지연 원인 분해 — '줄일 수 있는' 부분 = 약 50%")
    r = reasons.sort_values('cases', ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=r['reason'], x=r['cases'], orientation='h',
        marker_color=ACCENT,
        text=[f"{v:,}건 ({s:.1f}%)" for v, s in zip(r['cases'], r['share_%'])],
        textposition='outside',
        textfont=dict(color='#cbd5e1', size=10),
    ))
    fig.update_layout(
        title=dict(text='지연 원인별 발생 건수 (총 41개월)', font=dict(size=14)),
        xaxis_title='건수',
    )
    apply_layout(fig, height=520, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout'>"
        "<strong>인사이트</strong> · '항공기 연결' '항공교통흐름' '지상조업' 등 "
        "<strong>운영 개선으로 줄일 수 있는 원인이 약 50%</strong>를 차지합니다. "
        "이것이 모듈③의 정책 근거 — A-SMGCS·A-CDM 같은 인프라 투자 가성비가 SAF보다 압도적인 이유입니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t3:
    st.markdown("### 10 파일럿 노선별 지연·연료·CO₂")
    st.dataframe(routes, use_container_width=True, hide_index=True, height=380)

with t4:
    st.markdown("### 개입 시나리오 — IIAC·KAC ESG 검증값 기반")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=scenarios['시나리오'], y=scenarios['감축_tCO2/yr'],
        marker_color=['#94a3b8', ACCENT, '#7dd3fc', '#fcd34d', '#f472b6'],
        text=[f"{v:,.0f} t" for v in scenarios['감축_tCO2/yr']],
        textposition='outside',
    ))
    fig.update_layout(
        title=dict(text='개입 시나리오별 연간 CO₂ 감축량', font=dict(size=14)),
        yaxis_title='tCO₂/년', xaxis_title='시나리오',
    )
    apply_layout(fig, height=440, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(scenarios, use_container_width=True, hide_index=True)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>가성비 비교</strong> · 모듈② SAF 1% = 88만 원/t (439억÷49,816t) vs 모듈③ A-SMGCS ≈ 0원/t. "
        "정책 시그널: <span class='serif-accent'>2027 SAF 의무화는 불가피하나, 동시에 지상 운영 개선 인프라 투자가 가성비 압도적</span>."
        "</div>",
        unsafe_allow_html=True,
    )

with t5:
    st.markdown("### 상수")
    st.dataframe(consts, use_container_width=True, hide_index=True)
    fs = load_flights_summary()
    st.markdown("### flights_summary 시트")
    sheet = st.selectbox("시트 선택", list(fs.keys()))
    st.dataframe(fs[sheet], use_container_width=True, hide_index=True, height=400)

with t6:
    st.markdown("### GBM 회귀 — 기상×운항량 → 지연률 ★ v2 신규 (AI 가점)")
    st.caption("scikit-learn GradientBoostingRegressor (n=120, depth=3, lr=0.05) · TimeSeriesSplit 5-fold")

    if v2['gbm_imp'] is not None:
        # 피처 중요도 차트
        imp = v2['gbm_imp'].sort_values('importance', ascending=True)
        fig = go.Figure()
        colors = ['#6ee7b7' if v == imp['importance'].max() else
                  ('#7dd3fc' if v > 0.1 else '#94a3b8') for v in imp['importance']]
        fig.add_trace(go.Bar(
            y=imp['feature'],
            x=imp['importance'] * 100,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{v*100:.1f}%" for v in imp['importance']],
            textposition='outside',
        ))
        fig.update_layout(
            title="피처 중요도 — 무엇이 지연률을 결정하는가",
            xaxis_title="중요도 (%)",
        )
        apply_layout(fig, height=460, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div class='callout-good'>
                ★ <strong>핵심 발견</strong>: 운항량(flights) 58.9% + 계절성(sin_m) 18.4% + 회복기 4.2% = <strong>81.5%</strong>가 지연 결정.
                기상 변수 합 약 12%. → <strong>운영 정책 우선순위가 단순 기상 대응보다 슬롯·계절 분산</strong>임을 데이터로 입증.
            </div>
            """,
            unsafe_allow_html=True
        )

    if v2['gbm_pred'] is not None:
        st.markdown("##### 예측 시계열 (41개월 in-sample)")
        pred = v2['gbm_pred'].copy()
        pred['date'] = pd.to_datetime(pred['date'])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=pred['date'], y=pred['delay_rate_%'],
                                    name='실측', line=dict(color='#f0f4f8', width=2),
                                    mode='lines+markers'))
        fig2.add_trace(go.Scatter(x=pred['date'], y=pred['predicted_delay_rate'],
                                    name='GBM 예측', line=dict(color='#f87171', width=2, dash='dash')))
        fig2.add_trace(go.Scatter(x=pred['date'], y=pred['naive_pred'],
                                    name='Naive 월평균', line=dict(color='#94a3b8', width=1.5, dash='dot')))
        fig2.update_layout(title="월별 지연률 — 실측 vs GBM vs Naive",
                            xaxis_title="년월", yaxis_title="지연률 (%)")
        apply_layout(fig2, height=400)
        st.plotly_chart(fig2, use_container_width=True)

    if v2['gbm'] is not None:
        st.markdown("##### 성능 요약 (정직 공개)")
        st.dataframe(v2['gbm'], use_container_width=True, hide_index=True)

    if v2['gbm_ins'] is not None:
        st.markdown("##### 정책 인사이트 6개")
        st.dataframe(v2['gbm_ins'], use_container_width=True, hide_index=True)

with t7:
    st.markdown("### 인천공항 결항 41개월 분석 ★ v2 신규")
    st.caption("결항통계_20260519142520.xlsx · 인천 한정 (2023.01~2026.04, 40개월)")

    if v2['canc_cause'] is not None:
        st.markdown("##### 원인별 누적 결항 (41개월, 총 1,432편)")
        cc = v2['canc_cause']
        fig = go.Figure(data=[
            go.Pie(labels=cc['원인'], values=cc['결항편수'],
                   marker=dict(colors=['#6ee7b7','#7dd3fc','#94a3b8','#fcd34d','#f87171']*3),
                   textinfo='label+percent', textfont=dict(size=11))
        ])
        fig.update_layout(title="결항 원인 분포 — 기상이 53.8%")
        apply_layout(fig, height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(cc, use_container_width=True, hide_index=True)

    if v2['canc'] is not None:
        st.markdown("##### 결항 시계열 — 2024.11 폭설 이상치")
        canc = v2['canc'].copy()
        canc['date'] = pd.to_datetime(canc['date'])
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=canc['date'], y=canc['cancel_total'],
                                name='총 결항', marker=dict(color='#94a3b8')))
        fig2.add_trace(go.Bar(x=canc['date'], y=canc['cancel_weather'],
                                name='기상 결항', marker=dict(color='#7dd3fc')))
        fig2.update_layout(barmode='overlay', title="월별 결항 추이 (2024.11 = 폭설 286편)",
                            yaxis_title="편수")
        apply_layout(fig2, height=380)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        """
        <div class='callout'>
            <strong>결항 → CO2 직접 절감 효과</strong>
            <br>· 41개월 결항: 1,432편 (기상 53.8%)
            <br>· 직접 절감: 19,812 t/yr
            <br>· 대체편 30% 가정 시 net: <strong>13,868 t/yr</strong> (SAF 1%의 30.7%)
            <br>· 의도적 정책 아닌 부수 효과 — 베이스라인 검증용
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)
st.caption("Sources: 항공정보포털 월별 출도착 (23.01~26.05) · IIAC ESG 2024 (A-SMGCS 41%) · KAC ESG 2024 (A-CDM 16,239t)")
