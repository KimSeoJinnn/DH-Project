# 파일 위치: app/ai_model.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 🛡️ 1. .env 파일(비밀 금고) 불러오기
load_dotenv() 

# 🛡️ 2. 금고 안에서 GEMINI_API_KEY 꺼내오기
# (더 이상 이 파일에 진짜 키를 적지 않습니다! 깃허브에 올라가도 안전해요)
API_KEY = os.getenv("GEMINI_API_KEY") 

genai.configure(api_key=API_KEY)

# 👇 이 함수가 서버(main.py)에서 호출할 "핵심 기능"입니다.
def analyze_food_traffic_light(food_input):
    # 속도와 가성비가 좋은 최신 모델 사용
    model = genai.GenerativeModel('gemini-2.5-flash')

    # AI에게 내리는 지시사항 (프롬프트)
    prompt = f"""
    너는 '헬린이 키우기' 앱의 영양 분석 AI야. 
    사용자가 입력한 음식에 대해 헬스 초보자(근성장 및 다이어트 목적) 기준으로 신호등 등급을 매겨줘.

    [입력된 음식]
    {food_input}

    [판단 기준]
    - 🟢 Green (초록불): 고단백, 균형 잡힌 식단, 자연식 위주
    - 🟡 Yellow (노란불): 일반적인 식사, 칼로리가 조금 높거나 단백질이 부족함
    - 🔴 Red (빨간불): 당류 과다, 트랜스지방/포화지방 과다, 술, 정크푸드

    [출력 형식]
    반드시 아래와 같은 JSON 형식으로만 답변해. (마크다운이나 부가 설명 금지)
    {{
        "food_name": "음식 이름",
        "calories": "예상 칼로리 (숫자만, 단위 kcal)",
        "protein": "예상 단백질 (숫자만, 단위 g)",
        "traffic_light": "Green 또는 Yellow 또는 Red",
        "reason": "판단 이유 (헬린이에게 해주는 조언 말투로 1문장)"
    }}
    """

    try:
        # AI에게 질문 던지기
        response = model.generate_content(prompt)
        
        # 텍스트 응답을 JSON 객체로 변환
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(clean_text)
        return result_json

    except Exception as e:
        # 에러가 나면 에러 메시지를 딕셔너리로 반환
        return {"error": str(e)}