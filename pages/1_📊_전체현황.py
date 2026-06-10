import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="전체 현황", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/온라인_수강_데이터.csv', encoding='utf-8-sig')
    monthly = pd.read_csv('data/월별_통계.csv', encoding='utf-8-sig')
    return df, monthly

df, monthly = load_data()

st.title("📊 전체 현황")
st.markdown("---")

# 사이드바 필터
st.sidebar.header("🔍 필터")
companies = ['전체'] + sorted(df['회사'].dropna().unique().tolist())
selected_company = st.sidebar.selectbox("회사", companies)

statuses = ['전체'] + sorted(df['상태'].dropna().unique().tolist())
selected_status = st.sidebar.selectbox("수강 상태", statuses)

filtered = df.copy()
if selected_company != '전체':
    filtered = filtered[filtered['회사'] == selected_company]
if selected_status != '전체':
    filtered = filtered[filtered['상태'] == selected_status]

# KPI 카드
total_learners = filtered['학습자ID'].nunique()
total_courses = filtered['강좌ID'].nunique()
completion_rate = round(len(filtered[filtered['상태'] == '완료']) / len(filtered) * 100, 1) if len(filtered) > 0 else 0
avg_progress = round(filtered['진행률(%)'].mean(), 1) if len(filtered) > 0 else 0
pass_rate = 0
if filtered['합격여부'].notna().sum() > 0:
    pass_rate = round((filtered['합격여부'] == '합격').sum() / filtered['합격여부'].notna().sum() * 100, 1)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("👤 총 학습자 수", f"{total_learners}명")
col2.metric("📖 수강 강좌 수", f"{total_courses}개")
col3.metric("✅ 수강 완료율", f"{completion_rate}%")
col4.metric("📈 평균 진행률", f"{avg_progress}%")
col5.metric("🏆 합격률", f"{pass_rate}%")

st.markdown("---")

# 차트 행 1
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("수강 상태 분포")
    status_counts = filtered['상태'].value_counts().reset_index()
    status_counts.columns = ['상태', '건수']
    fig_pie = px.pie(
        status_counts, values='건수', names='상태',
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=350, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("부서별 수강 현황")
    dept_counts = filtered.groupby('부서').agg(
        수강건수=('수강번호', 'count'),
        완료건수=('상태', lambda x: (x == '완료').sum())
    ).reset_index()
    dept_counts['완료율(%)'] = (dept_counts['완료건수'] / dept_counts['수강건수'] * 100).round(1)

    fig_bar = px.bar(
        dept_counts, x='부서', y='수강건수',
        color='완료율(%)', color_continuous_scale='Blues',
        text='수강건수'
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(height=350)
    st.plotly_chart(fig_bar, use_container_width=True)

# 월별 트렌드
st.subheader("📅 월별 등록/완료 트렌드")
monthly_sorted = monthly.sort_values('년월')
fig_trend = go.Figure()
fig_trend.add_trace(go.Bar(
    x=monthly_sorted['년월'], y=monthly_sorted['총등록자'],
    name='총 등록자', marker_color='#636EFA', opacity=0.7
))
fig_trend.add_trace(go.Scatter(
    x=monthly_sorted['년월'], y=monthly_sorted['수강완료'],
    name='수강 완료', mode='lines+markers',
    line=dict(color='#EF553B', width=3), marker=dict(size=8)
))
fig_trend.update_layout(
    height=350,
    xaxis_title="년월", yaxis_title="인원",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode='x unified'
)
st.plotly_chart(fig_trend, use_container_width=True)

# 원본 데이터 보기
with st.expander("📋 원본 데이터 보기"):
    st.dataframe(filtered, use_container_width=True, height=300)
    csv = filtered.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("⬇️ CSV 다운로드", csv, "필터된_수강데이터.csv", "text/csv")
