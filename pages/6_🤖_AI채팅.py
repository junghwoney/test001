import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="AI 채팅", page_icon="🤖", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data/온라인_수강_데이터.csv', encoding='utf-8-sig')
    monthly = pd.read_csv('data/월별_통계.csv', encoding='utf-8-sig')
    return df, monthly

def add_status(df):
    def derive(row):
        if pd.notna(row['완료일']):
            return '완료'
        elif pd.notna(row['시작일']):
            return '진행중'
        else:
            return '미시작'
    df = df.copy()
    df['상태'] = df.apply(derive, axis=1)
    return df

def build_data_summary(df, monthly):
    df = add_status(df)
    total = len(df)
    learners = df['학습자ID'].nunique()
    courses = df['강좌ID'].nunique()
    completion_rate = round(len(df[df['상태'] == '완료']) / total * 100, 1)
    avg_progress = round(df['진행률(%)'].mean(), 1)
    pass_rate = 0
    if df['합격여부'].notna().sum() > 0:
        pass_rate = round((df['합격여부'] == '합격').sum() / df['합격여부'].notna().sum() * 100, 1)

    dept_summary = df.groupby('부서').agg(
        수강건수=('수강번호', 'count'),
        완료건수=('상태', lambda x: (x == '완료').sum())
    ).reset_index()
    dept_summary['완료율(%)'] = (dept_summary['완료건수'] / dept_summary['수강건수'] * 100).round(1)

    company_summary = df.groupby('회사').agg(
        수강건수=('수강번호', 'count'),
        완료건수=('상태', lambda x: (x == '완료').sum())
    ).reset_index()
    company_summary['완료율(%)'] = (company_summary['완료건수'] / company_summary['수강건수'] * 100).round(1)

    top_courses = df.groupby('강좌명').agg(
        수강건수=('수강번호', 'count'),
        평균점수=('시험점수', 'mean')
    ).reset_index().sort_values('수강건수', ascending=False).head(5)

    summary = f"""
[HRD 온라인 수강 대시보드 데이터 요약]

■ 전체 현황
- 총 수강 건수: {total:,}건
- 총 학습자 수: {learners:,}명
- 수강 강좌 수: {courses:,}개
- 수강 완료율: {completion_rate}%
- 평균 진행률: {avg_progress}%
- 합격률: {pass_rate}%

■ 수강 상태 분포
{df['상태'].value_counts().to_string()}

■ 부서별 수강 현황
{dept_summary.to_string(index=False)}

■ 회사별 수강 현황
{company_summary.to_string(index=False)}

■ 수강 인기 강좌 Top 5
{top_courses.to_string(index=False)}

■ 월별 통계 (최근 6개월)
{monthly.tail(6).to_string(index=False)}
"""
    return summary


api_key = os.getenv("GEMINI_API_KEY")

st.title("🤖 AI 데이터 채팅")
st.markdown("대시보드 데이터를 기반으로 자유롭게 질문하세요.")
st.markdown("---")

if not api_key or api_key == "여기에_API_키를_입력하세요":
    st.error("⚠️ `.env` 파일에 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

client = genai.Client(api_key=api_key)

df, monthly = load_data()
data_summary = build_data_summary(df, monthly)

SYSTEM_PROMPT = f"""당신은 HRD 온라인 수강 대시보드의 데이터 분석 전문가입니다.
아래 데이터를 기반으로 사용자의 질문에 한국어로 명확하고 친절하게 답변하세요.
수치는 구체적으로 언급하고, 인사이트가 있다면 추가로 제안해주세요.

{data_summary}
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 예시 질문 버튼
if not st.session_state.messages:
    st.markdown("**💡 예시 질문**")
    example_questions = [
        "완료율이 가장 높은 부서는 어디인가요?",
        "합격률이 낮은 이유가 무엇일까요?",
        "인기 강좌 Top 5를 알려주세요.",
        "월별 수강 트렌드를 분석해주세요.",
    ]
    cols = st.columns(2)
    for i, q in enumerate(example_questions):
        if cols[i % 2].button(q, key=f"ex_{i}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

# 사용자 입력
if prompt := st.chat_input("데이터에 대해 질문하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                history = [
                    types.Content(role="user", parts=[types.Part(text=SYSTEM_PROMPT + "\n\n이 데이터를 이해했으면 '네, 이해했습니다.'라고만 답해주세요.")]),
                    types.Content(role="model", parts=[types.Part(text="네, 이해했습니다.")]),
                ]
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
                history.append(types.Content(role="user", parts=[types.Part(text=prompt)]))

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=history,
                )
                answer = response.text

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# 대화 초기화 버튼
if st.session_state.messages:
    st.markdown("---")
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()
