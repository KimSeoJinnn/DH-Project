# 🥦 DH-Project: 헬린이 키우기 (AI Diet & Fitness RPG)

평범한 식단 관리는 지루하니까 음식을 분석하고 운동 퀘스트를 수행하며 자신의 캐릭터를 성장시키는 RPG형 식단 관리 애플리케이션입니다.

## ✨ 주요 기능

### 1. 🎮 게임 시스템 (Gamification)
- **레벨 및 경험치**: 식단 분석과 퀘스트 완료를 통해 경험치를 획득하고 레벨업하세요.
- **데일리 퀘스트**: 매일 주어지는 식단 미션을 달성하고 보상을 받습니다.
- **실시간 랭킹**: 다른 사용자들과 레벨을 비교하며 동기부여를 얻는 랭킹 시스템을 제공합니다.

### 2. 🚦 AI 식단 신호등 (AI Analysis)
- **실시간 분석**: Google Gemini 2.5 Flash 모델이 음식의 영양 성분을 즉시 분석합니다.
- **직관적 UI**: 분석 결과에 따라 **Green(추천), Yellow(보통), Red(주의)** 신호등 불빛이 들어옵니다.
- **맞춤형 조언**: 단순히 칼로리만 보여주는 게 아니라, 헬스 초보자에게 꼭 필요한 피드백을 제공합니다.

### 3. 💾 데이터 관리
- **로컬 캐시 시스템**: `quest_data.json`을 통해 사용자의 진행 상황과 퀘스트 상태를 안전하게 저장합니다.
- **회원가입/로그인**: 개별 사용자 프로필 관리가 가능합니다.

## 🛠 기술 스택
- **Frontend**: Flet (Python-based UI)
- **Backend**: FastAPI, Uvicorn
- **AI**: Google Generative AI (Gemini API)
- **Environment**: Python 3.10+

## 🚀 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt