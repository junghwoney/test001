import streamlit as st

st.set_page_config(
    page_title="HRD 온라인 수강 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📚 HRD 온라인 수강 대시보드")
st.markdown("---")

st.markdown("""
### 👋 환영합니다!

사이드바에서 분석 페이지를 선택하세요.

| 페이지 | 설명 |
|---|---|
| 📊 전체 현황 | KPI 카드, 월별 트렌드, 수강 상태 분포 |
| 👥 학습자 분석 | 부서·직급·회사별 수강 현황 |
| 📖 강좌 분석 | 카테고리·난이도·강사별 강좌 성과 |
| 🏆 성과 분석 | 점수 분포, 합격률, 참여도 분석 |
| 📅 월별 통계 | 월별 등록/완료 트렌드, 만족도 추이 |
""")
