import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# 데이터 저장 디렉토리
os.makedirs('data', exist_ok=True)

np.random.seed(42)

# 1. 학습자 데이터 생성
learners = []
departments = ['인사팀', '영업팀', '개발팀', '마케팅팀', '재무팀', '기획팀']
positions = ['사원', '주임', '대리', '과장', '부장']

for i in range(200):
    learners.append({
        '학습자ID': f'L{i+1:04d}',
        '이름': f'직원{i+1}',
        '부서': np.random.choice(departments),
        '직급': np.random.choice(positions),
        '가입일': (datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d'),
        '회사': f'회사{np.random.randint(1, 4)}'
    })

df_learners = pd.DataFrame(learners)
df_learners.to_csv('data/학습자_데이터.csv', index=False, encoding='utf-8-sig')
print(f"[OK] 학습자 데이터 생성: {len(df_learners)}명")

# 2. 강좌 데이터 생성
courses = []
categories = ['직무 스킬', '리더십', '직장 예절', '기술', '언어', '기본소양']
instructors = ['김강사', '이강사', '박강사', '최강사', '정강사', '한강사']

for i in range(50):
    courses.append({
        '강좌ID': f'C{i+1:03d}',
        '강좌명': f'{np.random.choice(categories)} 강좌 {i+1}',
        '카테고리': np.random.choice(categories),
        '강사명': np.random.choice(instructors),
        '학습시간': np.random.choice([2, 4, 6, 8, 10, 12]),
        '난이도': np.random.choice(['초급', '중급', '고급']),
        '오픈일': (datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d'),
        '상태': np.random.choice(['진행중', '종료', '준비중'])
    })

df_courses = pd.DataFrame(courses)
df_courses.to_csv('data/강좌_데이터.csv', index=False, encoding='utf-8-sig')
print(f"[OK] 강좌 데이터 생성: {len(df_courses)}개")

# 3. 수강 이력 데이터 생성
enrollments = []
statuses = ['완료', '진행중', '미시작', '중단']

for i in range(1000):
    learner = df_learners.sample(1).iloc[0]
    course = df_courses.sample(1).iloc[0]

    start_date = datetime.now() - timedelta(days=np.random.randint(0, 365))
    enrollment_date = start_date
    completion_date = start_date + timedelta(days=np.random.randint(0, 60))
    status = np.random.choice(statuses, p=[0.5, 0.3, 0.1, 0.1])

    if status == '미시작':
        completion_date = None
        progress = 0
    elif status == '중단':
        progress = np.random.randint(10, 90)
        completion_date = None
    elif status == '진행중':
        progress = np.random.randint(10, 99)
        completion_date = None
    else:  # 완료
        progress = 100

    enrollments.append({
        '수강번호': f'E{i+1:05d}',
        '학습자ID': learner['학습자ID'],
        '강좌ID': course['강좌ID'],
        '등록일': enrollment_date.strftime('%Y-%m-%d'),
        '시작일': start_date.strftime('%Y-%m-%d') if status != '미시작' else None,
        '완료일': completion_date.strftime('%Y-%m-%d') if completion_date else None,
        '진행률(%)': progress,
        '상태': status,
        '학습시간': np.random.randint(0, int(course['학습시간'])*60)
    })

df_enrollments = pd.DataFrame(enrollments)
df_enrollments.to_csv('data/수강_이력.csv', index=False, encoding='utf-8-sig')
print(f"[OK] 수강 이력 데이터 생성: {len(df_enrollments)}건")

# 4. 평가 데이터 생성
evaluations = []

for enrollment in enrollments:
    if enrollment['상태'] == '완료':
        evaluations.append({
            '수강번호': enrollment['수강번호'],
            '학습자ID': enrollment['학습자ID'],
            '강좌ID': enrollment['강좌ID'],
            '시험점수': np.random.randint(60, 100),
            '과제점수': np.random.randint(70, 100),
            '참여도': np.random.choice(['높음', '보통', '낮음']),
            '합격여부': np.random.choice(['합격', '불합격'], p=[0.9, 0.1]),
            '평가일': enrollment['완료일']
        })

df_evaluations = pd.DataFrame(evaluations)
df_evaluations.to_csv('data/평가_결과.csv', index=False, encoding='utf-8-sig')
print(f"[OK] 평가 결과 데이터 생성: {len(df_evaluations)}건")

# 5. 월별 통계 데이터 생성
monthly_stats = []

for month in range(12):
    month_date = datetime.now() - timedelta(days=30*month)
    year_month = month_date.strftime('%Y-%m')

    monthly_stats.append({
        '년월': year_month,
        '총등록자': np.random.randint(100, 300),
        '수강완료': np.random.randint(30, 150),
        '평균진행률(%)': np.random.randint(40, 90),
        '평균만족도': round(np.random.uniform(3.5, 4.8), 2),
        '활성학습자': np.random.randint(80, 250)
    })

df_monthly = pd.DataFrame(monthly_stats)
df_monthly.to_csv('data/월별_통계.csv', index=False, encoding='utf-8-sig')
print(f"[OK] 월별 통계 데이터 생성: {len(df_monthly)}건")

print("\n=== 모든 데이터 파일이 'data' 폴더에 생성되었습니다! ===")
print(f"  - 학습자_데이터.csv")
print(f"  - 강좌_데이터.csv")
print(f"  - 수강_이력.csv")
print(f"  - 평가_결과.csv")
print(f"  - 월별_통계.csv")
