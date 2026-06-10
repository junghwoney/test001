import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 기존 파일들 로드
df_learners = pd.read_csv('data/학습자_데이터.csv', encoding='utf-8-sig')
df_courses = pd.read_csv('data/강좌_데이터.csv', encoding='utf-8-sig')
df_enrollments = pd.read_csv('data/수강_이력.csv', encoding='utf-8-sig')
df_evaluations = pd.read_csv('data/평가_결과.csv', encoding='utf-8-sig')

# 수강이력과 학습자 정보 병합
df_merged = df_enrollments.merge(df_learners, on='학습자ID', how='left')

# 강좌 정보 병합
df_merged = df_merged.merge(df_courses, on='강좌ID', how='left')

# 평가 결과 병합 (있는 경우만)
df_merged = df_merged.merge(df_evaluations[['수강번호', '시험점수', '과제점수', '참여도', '합격여부']],
                             on='수강번호', how='left')

# 열 순서 정리
columns_order = [
    '수강번호', '학습자ID', '이름', '부서', '직급', '회사',
    '강좌ID', '강좌명', '카테고리', '강사명', '난이도',
    '등록일', '시작일', '완료일', '학습시간_y',
    '진행률(%)', '상태', '시험점수', '과제점수', '참여도', '합격여부'
]

# 실제 존재하는 열만 선택
columns_order = [col for col in columns_order if col in df_merged.columns]
df_merged = df_merged[columns_order]

# 열명 정리 (학습시간_y를 학습시간으로)
df_merged = df_merged.rename(columns={'학습시간_y': '학습시간(시간)'})

# 저장
df_merged.to_csv('data/온라인_수강_데이터.csv', index=False, encoding='utf-8-sig')

print(f"[OK] 통합 데이터 파일 생성 완료!")
print(f"    파일: data/온라인_수강_데이터.csv")
print(f"    행 수: {len(df_merged)}")
print(f"    열 수: {len(df_merged.columns)}")
print(f"\n=== 컬럼 목록 ===")
for i, col in enumerate(df_merged.columns, 1):
    print(f"  {i}. {col}")
