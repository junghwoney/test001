import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="강좌 분석", page_icon="📖", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/온라인_수강_데이터.csv', encoding='utf-8-sig')
    courses = pd.read_csv('data/강좌_데이터.csv', encoding='utf-8-sig')
    return df, courses

df, courses = load_data()

st.title("📖 강좌 분석")
st.markdown("---")

# 사이드바 필터
st.sidebar.header("🔍 필터")
categories = ['전체'] + sorted(df['카테고리'].dropna().unique().tolist())
selected_cat = st.sidebar.selectbox("카테고리", categories)
levels = ['전체'] + sorted(df['난이도'].dropna().unique().tolist())
selected_level = st.sidebar.selectbox("난이도", levels)

filtered = df.copy()
if selected_cat != '전체':
    filtered = filtered[filtered['카테고리'] == selected_cat]
if selected_level != '전체':
    filtered = filtered[filtered['난이도'] == selected_level]

tab1, tab2, tab3 = st.tabs(["카테고리 분석", "난이도 분석", "강사 & 인기 강좌"])

with tab1:
    st.subheader("카테고리별 수강 현황")

    cat_stats = filtered.groupby('카테고리').agg(
        수강건수=('수강번호', 'count'),
        완료건수=('상태', lambda x: (x == '완료').sum()),
        평균진행률=('진행률(%)', 'mean'),
        강좌수=('강좌ID', 'nunique')
    ).reset_index()
    cat_stats['완료율(%)'] = (cat_stats['완료건수'] / cat_stats['수강건수'] * 100).round(1)
    cat_stats['평균진행률'] = cat_stats['평균진행률'].round(1)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            cat_stats.sort_values('수강건수', ascending=False),
            x='카테고리', y='수강건수',
            color='카테고리',
            title="카테고리별 수강 건수",
            text='수강건수'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.scatter(
            cat_stats,
            x='수강건수', y='완료율(%)',
            size='강좌수', color='카테고리',
            hover_name='카테고리',
            title="카테고리별 수강건수 vs 완료율",
            text='카테고리'
        )
        fig2.update_traces(textposition='top center')
        fig2.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        cat_stats[['카테고리', '강좌수', '수강건수', '완료건수', '완료율(%)', '평균진행률']],
        use_container_width=True
    )

with tab2:
    st.subheader("난이도별 수강 분석")

    level_order = ['초급', '중급', '고급']
    level_stats = filtered.groupby('난이도').agg(
        수강건수=('수강번호', 'count'),
        완료건수=('상태', lambda x: (x == '완료').sum()),
        평균진행률=('진행률(%)', 'mean'),
        평균시험점수=('시험점수', 'mean'),
        강좌수=('강좌ID', 'nunique')
    ).reset_index()
    level_stats['완료율(%)'] = (level_stats['완료건수'] / level_stats['수강건수'] * 100).round(1)
    level_stats['평균진행률'] = level_stats['평균진행률'].round(1)
    level_stats['평균시험점수'] = level_stats['평균시험점수'].round(1)
    level_stats['난이도'] = pd.Categorical(level_stats['난이도'], categories=level_order, ordered=True)
    level_stats = level_stats.sort_values('난이도')

    col1, col2, col3 = st.columns(3)
    for i, row in level_stats.iterrows():
        col = [col1, col2, col3][level_order.index(row['난이도'])]
        with col:
            st.metric(f"📗 {row['난이도']}", f"{row['수강건수']}건", f"완료율 {row['완료율(%)']}%")

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            level_stats, x='난이도', y='완료율(%)',
            color='난이도',
            title="난이도별 완료율(%)",
            color_discrete_map={'초급': '#2ECC71', '중급': '#F39C12', '고급': '#E74C3C'},
            text='완료율(%)'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            level_stats, x='난이도', y='평균시험점수',
            color='난이도',
            title="난이도별 평균 시험 점수",
            color_discrete_map={'초급': '#2ECC71', '중급': '#F39C12', '고급': '#E74C3C'},
            text='평균시험점수'
        )
        fig2.update_traces(texttemplate='%{text}점', textposition='outside')
        fig2.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("강사별 수강 현황")
        instructor_stats = filtered.groupby('강사명').agg(
            수강건수=('수강번호', 'count'),
            완료건수=('상태', lambda x: (x == '완료').sum()),
            평균점수=('시험점수', 'mean')
        ).reset_index()
        instructor_stats['완료율(%)'] = (instructor_stats['완료건수'] / instructor_stats['수강건수'] * 100).round(1)
        instructor_stats['평균점수'] = instructor_stats['평균점수'].round(1)

        fig = px.bar(
            instructor_stats.sort_values('수강건수', ascending=True),
            x='수강건수', y='강사명', orientation='h',
            color='완료율(%)', color_continuous_scale='Teal',
            text='수강건수', title="강사별 담당 수강 건수"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("인기 강좌 TOP 10")
        course_stats = filtered.groupby(['강좌ID', '강좌명', '카테고리']).agg(
            수강건수=('수강번호', 'count'),
            완료건수=('상태', lambda x: (x == '완료').sum())
        ).reset_index()
        course_stats['완료율(%)'] = (course_stats['완료건수'] / course_stats['수강건수'] * 100).round(1)
        top10 = course_stats.nlargest(10, '수강건수')

        fig2 = px.bar(
            top10.sort_values('수강건수', ascending=True),
            x='수강건수', y='강좌명', orientation='h',
            color='카테고리', text='수강건수',
            title="수강 건수 TOP 10 강좌"
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
