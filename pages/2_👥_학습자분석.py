import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="학습자 분석", page_icon="👥", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('data/온라인_수강_데이터.csv', encoding='utf-8-sig')

df = load_data()

st.title("👥 학습자 분석")
st.markdown("---")

# 사이드바 필터
st.sidebar.header("🔍 필터")
companies = ['전체'] + sorted(df['회사'].dropna().unique().tolist())
selected_company = st.sidebar.selectbox("회사", companies)
depts = ['전체'] + sorted(df['부서'].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("부서", depts)

filtered = df.copy()
if selected_company != '전체':
    filtered = filtered[filtered['회사'] == selected_company]
if selected_dept != '전체':
    filtered = filtered[filtered['부서'] == selected_dept]

# 탭 구성
tab1, tab2, tab3 = st.tabs(["부서별 분석", "직급별 분석", "학습자 상세"])

with tab1:
    st.subheader("부서별 수강 현황")

    dept_stats = filtered.groupby('부서').agg(
        총수강=('수강번호', 'count'),
        완료=('상태', lambda x: (x == '완료').sum()),
        진행중=('상태', lambda x: (x == '진행중').sum()),
        평균진행률=('진행률(%)', 'mean'),
        학습자수=('학습자ID', 'nunique')
    ).reset_index()
    dept_stats['완료율(%)'] = (dept_stats['완료'] / dept_stats['총수강'] * 100).round(1)
    dept_stats['평균진행률'] = dept_stats['평균진행률'].round(1)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            dept_stats, x='부서', y=['완료', '진행중'],
            title="부서별 완료/진행중 건수",
            barmode='group',
            color_discrete_map={'완료': '#2ECC71', '진행중': '#3498DB'}
        )
        fig.update_layout(height=350, xaxis_title="", yaxis_title="건수")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            dept_stats.sort_values('완료율(%)', ascending=True),
            x='완료율(%)', y='부서', orientation='h',
            title="부서별 완료율(%)",
            color='완료율(%)', color_continuous_scale='Greens',
            text='완료율(%)'
        )
        fig2.update_traces(texttemplate='%{text}%', textposition='outside')
        fig2.update_layout(height=350, xaxis_title="완료율(%)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("부서별 평균 진행률")
    fig3 = px.bar(
        dept_stats.sort_values('평균진행률', ascending=False),
        x='부서', y='평균진행률',
        color='평균진행률', color_continuous_scale='Blues',
        text='평균진행률'
    )
    fig3.update_traces(texttemplate='%{text}%', textposition='outside')
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(
        dept_stats[['부서', '학습자수', '총수강', '완료', '진행중', '완료율(%)', '평균진행률']],
        use_container_width=True
    )

with tab2:
    st.subheader("직급별 학습 현황")

    position_order = ['사원', '주임', '대리', '과장', '부장']
    pos_stats = filtered.groupby('직급').agg(
        총수강=('수강번호', 'count'),
        완료=('상태', lambda x: (x == '완료').sum()),
        평균진행률=('진행률(%)', 'mean'),
        학습자수=('학습자ID', 'nunique')
    ).reset_index()
    pos_stats['완료율(%)'] = (pos_stats['완료'] / pos_stats['총수강'] * 100).round(1)
    pos_stats['평균진행률'] = pos_stats['평균진행률'].round(1)
    pos_stats['직급'] = pd.Categorical(pos_stats['직급'], categories=position_order, ordered=True)
    pos_stats = pos_stats.sort_values('직급')

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            pos_stats, x='직급', y='총수강',
            title="직급별 총 수강 건수",
            color='완료율(%)', color_continuous_scale='RdYlGn',
            text='총수강'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.line(
            pos_stats, x='직급', y='평균진행률',
            title="직급별 평균 진행률",
            markers=True,
            line_shape='spline'
        )
        fig2.update_traces(line_color='#E74C3C', marker_size=10)
        fig2.update_layout(height=350, yaxis_title="평균 진행률(%)")
        st.plotly_chart(fig2, use_container_width=True)

    # 회사별 x 직급별 히트맵
    st.subheader("회사 x 직급별 평균 진행률 히트맵")
    pivot = filtered.groupby(['회사', '직급'])['진행률(%)'].mean().round(1).unstack(fill_value=0)
    fig3 = px.imshow(
        pivot, text_auto=True,
        color_continuous_scale='Blues',
        title="회사별 직급별 평균 진행률(%)"
    )
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("학습자별 수강 현황")

    search = st.text_input("학습자 이름 또는 ID 검색", "")
    learner_df = filtered.copy()
    if search:
        learner_df = learner_df[
            learner_df['이름'].str.contains(search, na=False) |
            learner_df['학습자ID'].str.contains(search, na=False)
        ]

    learner_summary = learner_df.groupby(['학습자ID', '이름', '부서', '직급', '회사']).agg(
        총수강=('수강번호', 'count'),
        완료=('상태', lambda x: (x == '완료').sum()),
        평균진행률=('진행률(%)', 'mean'),
        평균시험점수=('시험점수', 'mean')
    ).reset_index()
    learner_summary['완료율(%)'] = (learner_summary['완료'] / learner_summary['총수강'] * 100).round(1)
    learner_summary['평균진행률'] = learner_summary['평균진행률'].round(1)
    learner_summary['평균시험점수'] = learner_summary['평균시험점수'].round(1)

    st.dataframe(
        learner_summary.sort_values('완료율(%)', ascending=False),
        use_container_width=True, height=400
    )
