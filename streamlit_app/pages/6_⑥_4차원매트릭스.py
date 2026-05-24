"""
페이지 ⑥ — 4차원 정책 매트릭스
================================
노선 × α × 가격 × 감축률 = 450 조합 시뮬레이션
정책 의사결정자가 즉시 탐색
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import apply_global_style, hero_metric, apply_layout

apply_global_style()

# ============================================================
# 데이터 로드
# ============================================================
@st.cache_data
def load_matrix():
    DATA = Path(__file__).parent.parent / "data" / "v2"
    df = pd.read_excel(DATA / "greensky_module2_v9_matrix.xlsx", sheet_name='1_마스터_매트릭스')
    return df

df = load_matrix()

# ============================================================
# 헤더
# ============================================================
st.markdown("<span class='eyebrow'>Module 6 · Four-Dimensional Policy Matrix</span>", unsafe_allow_html=True)
st.markdown("# ⑥ 4차원 정책 매트릭스")
st.markdown(
    "<p style='color:#94a3b8; font-size:1.05rem;'>"
    "노선 × α × 가격 × 감축률 = <strong>450 조합</strong> 즉시 시뮬레이션. "
    "정부 16만 t 목표 달성 가능 조합 <span class='serif-accent'>39/45 (87%)</span>."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("<hr class='divider-thin'>", unsafe_allow_html=True)

# ============================================================
# 컨트롤 — 4 슬라이더
# ============================================================
st.markdown("### 🎛 시뮬레이션 컨트롤")

c1, c2, c3 = st.columns(3)
with c1:
    alpha_sel = st.select_slider(
        "α (의무비율)",
        options=sorted(df['alpha'].unique()),
        value=0.01,
        format_func=lambda x: f"{x*100:.0f}%",
    )
with c2:
    price_sel = st.select_slider(
        "SAF 시장가 (USD/L)",
        options=sorted(df['price_USD'].unique()),
        value=1.2,
        format_func=lambda x: f"${x}/L",
    )
with c3:
    rate_sel = st.selectbox(
        "감축률 시나리오",
        sorted(df['reduce_rate_name'].unique()),
        index=0,  # CORSIA Default가 알파벳 순 첫 번째일 수 있음
    )
    # CORSIA Default 우선 선택
    if 'CORSIA Default (84.4%)' in df['reduce_rate_name'].unique():
        default_idx = list(sorted(df['reduce_rate_name'].unique())).index('CORSIA Default (84.4%)')
        rate_sel = st.session_state.get('rate_sel_v', 'CORSIA Default (84.4%)')

# 필터
filt = df[(df['alpha'] == alpha_sel) & (df['price_USD'] == price_sel) &
          (df['reduce_rate_name'] == rate_sel)]

if len(filt) == 0:
    st.warning("선택된 조합에 데이터가 없습니다.")
    st.stop()

total_co2 = filt['co2_kt'].sum()
total_cost = filt['cost_oku'].sum()
avg_burden = filt['burden_per_pax'].mean()
saf_total_kL = (filt['saf_L'].sum()) / 1000

# 정부 16만 t × 30% = 48 kt 도달 여부
gov_target = 48.0
hits_target = total_co2 >= gov_target

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 헤드라인 메트릭
# ============================================================
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(hero_metric("총 CO2 감축", f"{total_co2:.1f} kt/yr",
                             f"{'정부 48kt ✓' if hits_target else f'목표 -{gov_target-total_co2:.1f}kt'}"),
                unsafe_allow_html=True)
with m2:
    st.markdown(hero_metric("총 비용", f"{total_cost:.0f} 억/yr",
                             f"tCO2당 {total_cost*100/total_co2:.1f}만원"),
                unsafe_allow_html=True)
with m3:
    st.markdown(hero_metric("평균 부담", f"{avg_burden:,.0f} 원/명",
                             "10 노선 평균"),
                unsafe_allow_html=True)
with m4:
    st.markdown(hero_metric("SAF 총량", f"{saf_total_kL:,.0f} kL",
                             f"α {alpha_sel*100:.0f}%"),
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 탭 — 시각화
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺 노선별 매트릭스", "📊 시나리오 히트맵", "🎯 정부 목표 달성 조합", "📋 마스터 테이블"
])

with tab1:
    st.markdown("##### 선택된 조합의 노선별 SAF 영향")

    show_df = filt[['iata', 'region', 'dist_km', 'co2_kt', 'cost_oku',
                     'burden_per_pax', 'stage_equiv']].copy()
    show_df.columns = ['노선', '지역', '거리(km)', 'CO2 감축 (kt)',
                        '비용 (억)', '1편 부담 (원)', '단계 환산']
    show_df['CO2 감축 (kt)'] = show_df['CO2 감축 (kt)'].round(2)
    show_df['비용 (억)'] = show_df['비용 (억)'].round(1)
    show_df['1편 부담 (원)'] = show_df['1편 부담 (원)'].astype(int)
    show_df['단계 환산'] = show_df['단계 환산'].round(2)
    show_df = show_df.sort_values('CO2 감축 (kt)', ascending=False)

    st.dataframe(show_df, use_container_width=True, hide_index=True)

    # 노선별 CO2 감축 막대 차트
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=show_df['노선'],
        y=show_df['CO2 감축 (kt)'],
        marker=dict(color='#6ee7b7'),
        name='CO2 감축',
        text=show_df['CO2 감축 (kt)'].round(2),
        textposition='outside',
    ))
    fig.update_layout(title="노선별 CO2 감축량", yaxis_title="kt/yr")
    apply_layout(fig, height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("##### α × 가격 매트릭스 (현재 감축률 시나리오 적용)")

    sub = df[df['reduce_rate_name'] == rate_sel].groupby(
        ['alpha', 'price_USD']
    ).agg(co2_kt=('co2_kt', 'sum'), cost_oku=('cost_oku', 'sum')).reset_index()

    pivot_co2 = sub.pivot(index='alpha', columns='price_USD', values='co2_kt')
    pivot_cost = sub.pivot(index='alpha', columns='price_USD', values='cost_oku')

    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**CO2 감축 (kt)**")
        fig1 = go.Figure(data=go.Heatmap(
            z=pivot_co2.values,
            x=[f"${p}/L" for p in pivot_co2.columns],
            y=[f"α {a*100:.0f}%" for a in pivot_co2.index],
            colorscale=[[0, '#0a0e1a'], [0.5, '#6ee7b7'], [1, '#fcd34d']],
            text=pivot_co2.round(1).values,
            texttemplate='%{text}',
            showscale=True,
            colorbar=dict(title=dict(text='kt', font=dict(color='#cbd5e1'))),
        ))
        apply_layout(fig1, height=340, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with cc2:
        st.markdown("**총 비용 (억)**")
        fig2 = go.Figure(data=go.Heatmap(
            z=pivot_cost.values,
            x=[f"${p}/L" for p in pivot_cost.columns],
            y=[f"α {a*100:.0f}%" for a in pivot_cost.index],
            colorscale=[[0, '#0a0e1a'], [0.5, '#7dd3fc'], [1, '#f87171']],
            text=pivot_cost.round(0).values,
            texttemplate='%{text}',
            showscale=True,
            colorbar=dict(title=dict(text='억', font=dict(color='#cbd5e1'))),
        ))
        apply_layout(fig2, height=340, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("##### 정부 16만 t × 30% = 48 kt 목표 달성 가능 조합")
    st.caption("총 45 시나리오 (5α × 3가격 × 3감축률) 중 87% 달성")

    agg = df.groupby(['alpha', 'price_USD', 'reduce_rate_name']).agg(
        total_co2=('co2_kt', 'sum'),
        total_cost=('cost_oku', 'sum'),
    ).reset_index()
    agg['hits'] = agg['total_co2'] >= gov_target
    hits = agg[agg['hits']].sort_values('total_cost')

    show = hits[['alpha', 'price_USD', 'reduce_rate_name', 'total_co2', 'total_cost']].copy()
    show['alpha'] = (show['alpha'] * 100).round(0).astype(str) + '%'
    show.columns = ['α', '가격 (USD/L)', '감축률', 'CO2 (kt)', '비용 (억)']
    show['CO2 (kt)'] = show['CO2 (kt)'].round(1)
    show['비용 (억)'] = show['비용 (억)'].round(0)
    st.dataframe(show.head(20), use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div class='callout-good'>
            ✓ <strong>최저 비용 정책</strong>: {hits.iloc[0]['alpha']*100:.0f}% × ${hits.iloc[0]['price_USD']}/L × {hits.iloc[0]['reduce_rate_name']}
            → 비용 {hits.iloc[0]['total_cost']:.0f}억, 감축 {hits.iloc[0]['total_co2']:.1f}kt
        </div>
        """,
        unsafe_allow_html=True
    )

with tab4:
    st.markdown("##### 마스터 매트릭스 — 450 조합 전체")
    show_master = df[['iata','region','alpha_label','price_USD','reduce_rate_name',
                       'co2_kt','cost_oku','burden_per_pax']].copy()
    show_master.columns = ['노선','지역','α','가격','감축률','CO2(kt)','비용(억)','부담(원)']
    st.dataframe(show_master, use_container_width=True, hide_index=True, height=420)

    # 다운로드
    csv = show_master.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 마스터 매트릭스 CSV 다운로드",
        csv,
        "greensky_4d_matrix.csv",
        "text/csv",
    )

st.markdown("<hr class='divider-thin' style='margin-top:3rem;'>", unsafe_allow_html=True)
st.caption("GreenSky v2.0 · 4차원 매트릭스 · 카탈로그 §34")
