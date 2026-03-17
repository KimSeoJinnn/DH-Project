# 🥦 DH-Project: 헬린이 키우기 (AI 식단 코칭 앱)

사용자가 먹은 음식을 입력하면 AI가 영양 성분을 분석하고, 헬스 초보자(헬린이)의 관점에서 **신호등 등급(Green, Yellow, Red)**을 매겨주는 스마트 식단 관리 애플리케이션입니다.

## ✨ 주요 기능
- **AI 식단 분석**: Google Gemini 2.5 Flash 모델을 활용한 실시간 영양 분석.
- **식단 신호등**: 음식의 건강도를 직관적인 색상(초록, 노랑, 빨강)과 네온 효과로 표시.
- **상세 가이드**: 칼로리, 단백질 정보와 함께 헬린이를 위한 AI 코치의 맞춤 조언 제공.
- **사용자 관리**: 로컬 JSON 기반의 데이터 저장 및 회원가입 기능.

## 🛠 기술 스택
- **Frontend**: Flet (Python-based UI Framework)
- **Backend**: FastAPI, Uvicorn
- **AI**: Google Generative AI (Gemini API)
- **Database**: Local JSON File / SQLAlchemy (준비 중)

## 🚀 실행 방법

### 1. 가상환경 세팅 및 패키지 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt