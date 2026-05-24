"""모듈④ — 유가·할증료 예측 (LSTM·SARIMA)"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import CSS, apply_layout, page_header, sidebar_nav, load_m4, load_mops, ACCENT, GRID_COLOR

st.set_page_config(page_title="모듈④ 유가예측 | GreenSky", page_icon="📈", layout="wide")
sidebar_nav("모듈④ 유가·할증료 예측")
page_header(
    "Module 4 · 8-Model Forecast + DM Test",
    "유가·유류할증료 AI 예측",
    "MOPS Jet-A1 <strong>77개월</strong> · Naive · SARIMA · LSTM(uni·multi) · Prophet · Holt-Winters · Transformer "
    "= <strong>8 모델 비교</strong>. <span style='color:#6ee7b7;'>Diebold-Mariano 검정 + 잔차 진단 정직 공개</span>",
)

data = load_m4()
hist = load_mops()
fcst12 = data["S1_12개월_메인예측"]
fcst36 = data["S2_36개월_추세_SAF시나리오"]
perf = data["S3_모델성능비교"]
routes12 = data["S4_10노선_12개월_부담"]
consts = data["S5_핵심상수공식"]

# v2 신규 — α 시나리오 노선 매트릭스
DATA_V2 = Path(__file__).parent.parent / "data" / "v2"
@st.cache_data
def load_v2():
    d = {}
    try:
        d['scen'] = pd.read_excel(DATA_V2 / "greensky_module4_v2_scenarios.xlsx", sheet_name='1_시나리오요약')
        d['matrix'] = pd.read_excel(DATA_V2 / "greensky_module4_v2_scenarios.xlsx", sheet_name='3_현재vs미래')
    except Exception:
        d.update({'scen': None, 'matrix': None})
    return d
v2 = load_v2()

# 헤드라인 (v2 갱신)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("<div class='metric-card'><div class='eyebrow'>학습 데이터</div>"
                "<div class='hero-num'>77<span class='hero-unit'>개월</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>2020.01 ~ 2026.05</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='metric-card'><div class='eyebrow'>최우수 (Val MAE)</div>"
                "<div class='hero-num'>4.22<span class='hero-unit'>★ Naive</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>8 모델 중 1위</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='metric-card'><div class='eyebrow'>SAF 1% 부담 (1.2/L)</div>"
                "<div class='hero-num'>1,323<span class='hero-unit'>원/명</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>시장가 권장</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='metric-card'><div class='eyebrow'>흡수 단계</div>"
                "<div class='hero-num'>0.58<span class='hero-unit'>단계</span></div>"
                "<div style='color:#94a3b8; font-size:0.82rem;'>체감 거의 없음</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6 = st.tabs([
    "📈 MOPS 시계열·예측", "🤖 4 모델 정직 비교", "🛫 노선별 12개월 부담",
    "💰 SAF 흡수성 시각화", "📋 원본 데이터", "🎯 8 모델 + α 시나리오 ★"
])

with t1:
    st.markdown("### MOPS Jet-A1 — 실측 77개월 + 메인 12개월 + 추세 36개월")

    fig = go.Figure()
    # 실측
    fig.add_trace(go.Scatter(
        x=hist['date'], y=hist['MOPS_USD_bbl'],
        mode='lines', name='실측 (2020.01~2026.05)',
        line=dict(color='#cbd5e1', width=1.8),
    ))
    # 12개월 메인
    f12 = fcst36.head(12).copy()
    f12['date'] = pd.to_datetime(f12['date'])
    fig.add_trace(go.Scatter(
        x=list(f12['date']) + list(f12['date'][::-1]),
        y=list(f12['mops_p90']) + list(f12['mops_p10'][::-1]),
        fill='toself', fillcolor='rgba(110,231,183,0.12)',
        line=dict(color='rgba(0,0,0,0)'),
        name='80% 신뢰구간 (P10~P90)', showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=f12['date'], y=f12['mops_p50'],
        mode='lines', name='메인 12개월 (SARIMA P50)',
        line=dict(color=ACCENT, width=2.5),
    ))
    # 36개월 추세
    f36rest = fcst36.iloc[12:].copy()
    f36rest['date'] = pd.to_datetime(f36rest['date'])
    fig.add_trace(go.Scatter(
        x=f36rest['date'], y=f36rest['mops_p50'],
        mode='lines', name='추세선 24개월 (참고)',
        line=dict(color=ACCENT, width=1.5, dash='dash'),
    ))
    # SAF 의무화 라인 — plotly 모든 버전 호환 (직접 shape + annotation)
    fig.add_shape(
        type='line',
        x0='2027-01-01', x1='2027-01-01',
        y0=0, y1=1, yref='paper',
        line=dict(color='#fcd34d', dash='dot', width=1.5),
    )
    fig.add_annotation(
        x='2027-01-01', y=1, yref='paper',
        text='2027.01 SAF 1%', showarrow=False,
        xanchor='left', yanchor='top',
        font=dict(color='#fcd34d', size=11),
    )

    fig.update_layout(
        title=dict(text='MOPS Jet-A1 가격 예측 (메인 12 + 추세 36)', font=dict(size=14)),
        xaxis_title='년월', yaxis_title='MOPS Jet-A1 (USD/BBL)',
        hovermode='x unified',
    )
    apply_layout(fig, height=520)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout'>"
        "<strong>정직 공개</strong> · 2026.03~04 $195~200/BBL 지정학 급등은 어떤 모델도 사전 예측하지 못했습니다. "
        "GreenSky는 신뢰구간과 시나리오 분기로 이 한계를 명시합니다. 학습기간(77월) 대비 36개월 horizon이 60%로 길어 "
        "추세선 신뢰구간이 의도적으로 넓게 표시됩니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t2:
    st.markdown("### 4 모델 정직 비교 — Naive·SARIMA·LSTM 단변량·LSTM 다변량")

    c1, c2 = st.columns(2)
    with c1:
        d = perf[perf['구간']=='검증 (2025)'].copy()
        if d.empty:
            d = perf.iloc[:4]
        fig = px.bar(d, x='model', y='MAE',
                    color='MAE', color_continuous_scale=['#6ee7b7','#fcd34d','#f87171'],
                    title='검증 (2025 평탄 12개월) MAE — 낮을수록 ↑')
        fig.update_traces(text=d['MAE'].round(2), textposition='outside', textfont=dict(color='#cbd5e1'))
        apply_layout(fig, height=380, showlegend=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        d = perf[perf['구간']=='테스트 (2026 급등)'].copy()
        if d.empty:
            d = perf.iloc[4:]
        fig = px.bar(d, x='model', y='MAE',
                    color='MAE', color_continuous_scale=['#6ee7b7','#fcd34d','#f87171'],
                    title='테스트 (2026 급등 5개월) MAE')
        fig.update_traces(text=d['MAE'].round(1), textposition='outside', textfont=dict(color='#cbd5e1'))
        apply_layout(fig, height=380, showlegend=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>학술적 정직성 차별점</strong> · 평탄 구간에서는 <strong>Naive(단순 last value)가 가장 정확</strong>합니다. "
        "AI 만능론을 반박하는 결과를 숨기지 않고 공개합니다. LSTM 다변량이 단변량보다 우수한 점에서 "
        "원유 4종·계절성·SAF 더미의 시그널 유효성은 입증됩니다. 급등 구간은 어떤 모델도 한계 — "
        "신뢰구간과 시나리오의 가치 강조."
        "</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(perf, use_container_width=True, hide_index=True)

with t3:
    st.markdown("### 10 노선 × 12개월 유류할증료 예측 (편도, 원/명)")
    r = routes12.copy()
    if 'date' in r.columns:
        r['date'] = pd.to_datetime(r['date'])
        r_long = r.melt(id_vars=['date'], value_vars=[c for c in r.columns if c.startswith('ICN-')],
                       var_name='route', value_name='fare')
        fig = px.line(r_long, x='date', y='fare', color='route',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(
            title=dict(text='노선별 월간 유류할증료 (P50)', font=dict(size=14)),
            xaxis_title='년월', yaxis_title='편도 단가 (원/명)',
        )
        apply_layout(fig, height=460)
        st.plotly_chart(fig, use_container_width=True)

    # 평균 부담 막대
    routes_cols = [c for c in routes12.columns if c.startswith('ICN-')]
    avg = routes12[routes_cols].mean().sort_values()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=avg.index, x=avg.values, orientation='h',
        marker_color=['#6ee7b7']*5 + ['#7dd3fc']*3 + ['#f472b6']*2,
        text=[f"{int(v):,}원" for v in avg.values], textposition='outside',
        textfont=dict(color='#cbd5e1'),
    ))
    fig.update_layout(
        title=dict(text='노선별 12개월 평균 편도 부담', font=dict(size=14)),
        xaxis_title='원/명/편도',
    )
    apply_layout(fig, height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with t4:
    st.markdown("### SAF 1% 의무화 — 소비자 흡수성 시각화")

    saf_burden = 1756
    stages = np.arange(0, 34)
    short_won = stages * 2275

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stages, y=short_won, mode='lines+markers',
        name='단거리 단계별 단가', line=dict(color=ACCENT, width=2.5),
        marker=dict(size=6),
    ))
    fig.add_hline(y=saf_burden, line=dict(color='#fcd34d', dash='dash', width=2),
                  annotation_text=f"SAF 1% 소비자 부담 = {saf_burden:,}원",
                  annotation_position='top left',
                  annotation_font=dict(color='#fcd34d'))
    fig.add_trace(go.Scatter(
        x=[0.77], y=[saf_burden], mode='markers',
        marker=dict(size=18, color='#fcd34d', symbol='star',
                   line=dict(color='#000', width=1)),
        name='정합점: 단계 0.77',
    ))
    fig.add_trace(go.Scatter(
        x=[23], y=[23*2275], mode='markers',
        marker=dict(size=14, color='#7dd3fc', symbol='circle',
                   line=dict(color='#000', width=1)),
        name='2026.05 현재 (단계 23)',
    ))
    fig.update_layout(
        title=dict(text='SAF 정책 흡수 가능성 — 단계 0.77 인상으로 충분', font=dict(size=14)),
        xaxis_title='유류할증료 단계 (0~33)', yaxis_title='단거리 편도 단가 (원/명)',
    )
    apply_layout(fig, height=480)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='callout-good'>"
        "<strong>★ 핵심 정책 메시지</strong> · 2027 SAF 1% 의무화로 발생하는 항공사 추가 비용을 "
        "전체 소비자에 100% 전가한다고 가정해도, <strong>1인당 1,756원/편도</strong>에 그칩니다. "
        "이는 단거리 유류할증료 단계 1단계의 77%로, 정책 충격이 사실상 단계 1 인상 이내에서 흡수 가능합니다."
        "</div>",
        unsafe_allow_html=True,
    )

with t5:
    st.markdown("### 12개월 메인 예측")
    st.dataframe(fcst12, use_container_width=True, hide_index=True)
    st.markdown("### 36개월 추세 + SAF 시나리오")
    st.dataframe(fcst36, use_container_width=True, hide_index=True, height=400)
    st.markdown("### 핵심 상수·공식")
    st.dataframe(consts, use_container_width=True, hide_index=True)

with t6:
    st.markdown("### 8 모델 종합 비교 ★ v2 신규")
    st.caption("기존 4 모델 + Prophet · Holt-Winters · Transformer (총 7 + Naive = 8)")

    models_df = pd.DataFrame([
        {'Rank': 1, 'Model': 'Naive (last value)', 'Val MAE': 4.22, 'Test MAE': 32.26, 'DM vs Naive': '—', '비고': '★ 가장 강건'},
        {'Rank': 2, 'Model': 'LSTM multi (7 features)', 'Val MAE': 5.61, 'Test MAE': 50.18, 'DM vs Naive': 'p=0.21 비유의', '비고': 'AI 다변량'},
        {'Rank': 3, 'Model': 'Prophet', 'Val MAE': 6.00, 'Test MAE': 63.97, 'DM vs Naive': 'p=0.10 비유의', '비고': 'Meta 산업 표준'},
        {'Rank': 4, 'Model': 'Holt-Winters', 'Val MAE': 6.77, 'Test MAE': 60.87, 'DM vs Naive': 'p=0.052 비유의', '비고': '지수평활'},
        {'Rank': 5, 'Model': 'SARIMA(1,1,1)(1,1,1,12)', 'Val MAE': 7.85, 'Test MAE': 62.02, 'DM vs Naive': 'p=0.020 ★유의', '비고': '통계 베이스'},
        {'Rank': 6, 'Model': 'LSTM uni', 'Val MAE': 8.49, 'Test MAE': 54.12, 'DM vs Naive': 'p=0.031 ★유의', '비고': 'AI 단변량'},
        {'Rank': 7, 'Model': 'Transformer (new)', 'Val MAE': 12.53, 'Test MAE': 45.01, 'DM vs Naive': '—', '비고': '⚠️ AI 최신 = 최악'},
    ])
    st.dataframe(models_df, use_container_width=True, hide_index=True)

    # 막대 차트
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models_df['Model'],
        y=models_df['Val MAE'],
        marker=dict(color=['#6ee7b7','#7dd3fc','#7dd3fc','#94a3b8','#94a3b8','#fcd34d','#f87171']),
        text=models_df['Val MAE'].round(2),
        textposition='outside',
        name='Val 2025 MAE',
    ))
    fig.update_layout(
        title="Val 2025 MAE — 작을수록 우수 (Naive 가장 강건)",
        yaxis_title="MAE (USD/BBL)",
        xaxis_tickangle=-30,
    )
    apply_layout(fig, height=420, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
        <div class='callout-good'>
            ★ <strong>"AI 만능론 반박" 최강 증거</strong>: Transformer(최신 AI)가 8 모델 중 최악 Val MAE 12.53.
            <br>·  <strong>Walk-forward 1-step ahead 비교</strong>: Naive ≈ SARIMA (DM p=0.83) — 통계적 동등
            <br>·  <strong>잔차 진단</strong>: Ljung-Box ✓, ARCH ✓, Jarque-Bera ✗ (왜도 +3.49, 2026 outlier)
            <br>·  GreenSky는 단일 AI 의존 위험 명시 + 4중 안전망 (Naive·SARIMA·LSTM 다변량·시나리오) 제공
        </div>
        """,
        unsafe_allow_html=True
    )

    # α 시나리오 노선 매트릭스
    if v2['matrix'] is not None:
        st.markdown("##### α 시나리오 × 10 노선 부담 매트릭스")
        st.dataframe(v2['matrix'], use_container_width=True, hide_index=True, height=380)

        st.markdown(
            """
            <div class='callout'>
                <strong>핵심 메시지</strong>: 2027 α=1% 시 <strong>모든 노선에서 현재 대비 +2.7%</strong>만 추가.
                2035 α=10% (정부 적극안) 시 +26.8%. 단계적 흡수 충분히 가능.
            </div>
            """,
            unsafe_allow_html=True
        )

    if v2['scen'] is not None:
        st.markdown("##### 5 α 시나리오 요약")
        st.dataframe(v2['scen'], use_container_width=True, hide_index=True)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)
st.caption("Sources: 한국석유공사 페트로넷 · 대한항공 유류할증료 공지 41개월 · §9.2 단계 회귀 R²≈0.99 · §9.1 검증 Δ 0.01")
