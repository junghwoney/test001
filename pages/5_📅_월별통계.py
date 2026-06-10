import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="월별 통계", page_icon="📅", layout="wide")

@st.cache_data
def load_data():
    monthly = pd.read_csv('data/월별_통계.csv', encoding='utf-8-sig')
    df = pd.read_csv('data/온라인_수강_데이터.csv', encoding='utf-8-sig')
    return monthly, df

monthly, df = load_data()

st.title("📅 월별 통계")
st.markdown("---")

monthly_sorted = monthly.sort_values('년월').reset_index(drop=True)

# KPI
col1, col2, col3, col4 = st.columns(4)
latest = monthly_sorted.iloc[-1]
prev = monthly_sorted.iloc[-2]

col1.metric("최근 월 총 등록자", f"{latest['총등록자']}명",
            delta=f"{latest['총등록자'] - prev['총등록자']:+d}명 (전월 대비)")
col2.metric("최근 월 수강 완료", f"{latest['수강완료']}명",
            delta=f"{latest['수강완료'] - prev['수강완료']:+d}명")
col3.metric("최근 월 평균 만족도", f"{latest['평균만족도']:.2f}점",
            delta=f"{latest['평균만족도'] - prev['평균만족도']:+.2f}점")
col4.metric("최근 월 활성 학습자", f"{latest['활성학습자']}명",
            delta=f"{latest['활성학습자'] - prev['활성학습자']:+d}명")

st.markdown("---")

# 등록/완료/활성 트렌드
st.subheader("📈 월별 등록 · 완료 · 활성 학습자 추이")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly_sorted['년월'], y=monthly_sorted['총등록자'],
    name='총 등록자', marker_color='#AED6F1', opacity=0.8
))
fig.add_trace(go.Bar(
    x=monthly_sorted['년월'], y=monthly_sorted['수강완료'],
    name='수강 완료', marker_color='#2ECC71', opacity=0.8
))
fig.add_trace(go.Scatter(
    x=monthly_sorted['년월'], y=monthly_sorted['활성학습자'],
    name='활성 학습자', mode='lines+markers',
    line=dict(color='#E74C3C', width=3, dash='dot'),
    marker=dict(size=8)
))
fig.update_layout(
    barmode='group', height=380,
    xaxis_title="년월", yaxis_title="인원",
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 월별 평균 진행률 추이")
    fig2 = px.area(
        monthly_sorted, x='년월', y='평균진행률(%)',
        title="월별 평균 진행률(%)",
        color_discrete_sequence=['#3498DB'],
        markers=True
    )
    fig2.update_traces(
        fill='tozeroy', fillcolor='rgba(52,152,219,0.2)',
        line_color='#3498DB', marker_size=8
    )
    fig2.update_layout(height=350, yaxis_title="평균 진행률(%)")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("⭐ 월별 평균 만족도 추이")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=monthly_sorted['년월'], y=monthly_sorted['평균만족도'],
        mode='lines+markers+text',
        text=monthly_sorted['평균만족도'].round(2),
        textposition='top center',
        line=dict(color='#F39C12', width=3),
        marker=dict(size=10, color='#F39C12'),
        fill='tozeroy', fillcolor='rgba(243,156,18,0.15)'
    ))
    fig3.update_layout(
        height=350,
        yaxis=dict(range=[0, 5], title="만족도 (5점 만점)"),
        xaxis_title="년월"
    )
    st.plotly_chart(fig3, use_container_width=True)

# 월별 완료율
st.subheader("📉 월별 수강 완료율")
monthly_sorted['완료율(%)'] = (monthly_sorted['수강완료'] / monthly_sorted['총등록자'] * 100).round(1)
fig4 = px.bar(
    monthly_sorted, x='년월', y='완료율(%)',
    color='완료율(%)', color_continuous_scale='RdYlGn',
    text='완료율(%)'
)
fig4.update_traces(texttemplate='%{text}%', textposition='outside')
fig4.update_layout(height=320)
st.plotly_chart(fig4, use_container_width=True)

# 원본 통계 테이블
with st.expander("📋 월별 통계 원본 데이터"):
    st.dataframe(monthly_sorted, use_container_width=True)
    csv = monthly_sorted.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("⬇️ CSV 다운로드", csv, "월별_통계.csv", "text/csv")
