import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="성과 분석", page_icon="🏆", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/온라인_수강_데이터.csv', encoding='utf-8-sig')
    evals = pd.read_csv('data/평가_결과.csv', encoding='utf-8-sig')
    return df, evals

df, evals = load_data()

st.title("🏆 성과 분석")
st.markdown("---")

# 사이드바 필터
st.sidebar.header("🔍 필터")
depts = ['전체'] + sorted(df['부서'].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("부서", depts)
categories = ['전체'] + sorted(df['카테고리'].dropna().unique().tolist())
selected_cat = st.sidebar.selectbox("카테고리", categories)

eval_df = df[df['합격여부'].notna()].copy()
if selected_dept != '전체':
    eval_df = eval_df[eval_df['부서'] == selected_dept]
if selected_cat != '전체':
    eval_df = eval_df[eval_df['카테고리'] == selected_cat]

# KPI
col1, col2, col3, col4 = st.columns(4)
avg_exam = eval_df['시험점수'].mean()
avg_assign = eval_df['과제점수'].mean()
pass_rate = (eval_df['합격여부'] == '합격').mean() * 100
total_eval = len(eval_df)

col1.metric("📝 평균 시험 점수", f"{avg_exam:.1f}점")
col2.metric("📋 평균 과제 점수", f"{avg_assign:.1f}점")
col3.metric("✅ 합격률", f"{pass_rate:.1f}%")
col4.metric("🔢 평가 대상 수", f"{total_eval}건")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["점수 분포", "합격 분석", "참여도 분석"])

with tab1:
    st.subheader("시험 & 과제 점수 분포")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            eval_df, x='시험점수', nbins=20,
            title="시험 점수 분포",
            color_discrete_sequence=['#3498DB'],
            marginal='box'
        )
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(
            eval_df, x='과제점수', nbins=20,
            title="과제 점수 분포",
            color_discrete_sequence=['#E67E22'],
            marginal='box'
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("시험 점수 vs 과제 점수 산점도")
    fig3 = px.scatter(
        eval_df, x='시험점수', y='과제점수',
        color='합격여부',
        symbol='참여도',
        hover_data=['부서', '강좌명', '난이도'],
        color_discrete_map={'합격': '#2ECC71', '불합격': '#E74C3C'},
        title="시험 점수 vs 과제 점수 (합격여부·참여도별)"
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("합격/불합격 분석")
    col1, col2 = st.columns(2)

    with col1:
        pass_counts = eval_df['합격여부'].value_counts().reset_index()
        pass_counts.columns = ['합격여부', '건수']
        fig = px.pie(
            pass_counts, values='건수', names='합격여부',
            title="전체 합격/불합격 비율",
            color='합격여부',
            color_discrete_map={'합격': '#2ECC71', '불합격': '#E74C3C'},
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dept_pass = eval_df.groupby('부서').agg(
            합격=('합격여부', lambda x: (x == '합격').sum()),
            불합격=('합격여부', lambda x: (x == '불합격').sum()),
            total=('합격여부', 'count')
        ).reset_index()
        dept_pass['합격률(%)'] = (dept_pass['합격'] / dept_pass['total'] * 100).round(1)

        fig2 = px.bar(
            dept_pass.sort_values('합격률(%)', ascending=True),
            x='합격률(%)', y='부서', orientation='h',
            title="부서별 합격률(%)",
            color='합격률(%)', color_continuous_scale='RdYlGn',
            text='합격률(%)'
        )
        fig2.update_traces(texttemplate='%{text}%', textposition='outside')
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("카테고리별 합격률")
    cat_pass = eval_df.groupby('카테고리').agg(
        합격=('합격여부', lambda x: (x == '합격').sum()),
        total=('합격여부', 'count')
    ).reset_index()
    cat_pass['합격률(%)'] = (cat_pass['합격'] / cat_pass['total'] * 100).round(1)
    fig4 = px.bar(
        cat_pass.sort_values('합격률(%)', ascending=False),
        x='카테고리', y='합격률(%)',
        color='합격률(%)', color_continuous_scale='RdYlGn',
        text='합격률(%)'
    )
    fig4.update_traces(texttemplate='%{text}%', textposition='outside')
    fig4.update_layout(height=320)
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("참여도별 성과 비교")
    participation_order = ['높음', '보통', '낮음']

    part_stats = eval_df.groupby('참여도').agg(
        건수=('수강번호', 'count'),
        평균시험점수=('시험점수', 'mean'),
        평균과제점수=('과제점수', 'mean'),
        합격수=('합격여부', lambda x: (x == '합격').sum())
    ).reset_index()
    part_stats['합격률(%)'] = (part_stats['합격수'] / part_stats['건수'] * 100).round(1)
    part_stats['평균시험점수'] = part_stats['평균시험점수'].round(1)
    part_stats['평균과제점수'] = part_stats['평균과제점수'].round(1)
    part_stats['참여도'] = pd.Categorical(part_stats['참여도'], categories=participation_order, ordered=True)
    part_stats = part_stats.sort_values('참여도')

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=part_stats['참여도'], y=part_stats['평균시험점수'],
            name='평균 시험 점수', marker_color='#3498DB'
        ))
        fig.add_trace(go.Bar(
            x=part_stats['참여도'], y=part_stats['평균과제점수'],
            name='평균 과제 점수', marker_color='#E67E22'
        ))
        fig.update_layout(
            title="참여도별 평균 점수 비교",
            barmode='group', height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            part_stats, x='참여도', y='합격률(%)',
            color='참여도',
            color_discrete_map={'높음': '#2ECC71', '보통': '#F39C12', '낮음': '#E74C3C'},
            title="참여도별 합격률(%)",
            text='합격률(%)'
        )
        fig2.update_traces(texttemplate='%{text}%', textposition='outside')
        fig2.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
