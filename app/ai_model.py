# 파일 위치: app/ai_model.py

import google.generativeai as genai
import json

# ⚠️ 여기에 발급받은 실제 API 키를 넣어주세요.
API_KEY = "AIzaSyBETh6czjW0YDY95oxs4Q43iJwt10W5Sgw" 

genai.configure(api_key=API_KEY)

# 👇 이 함수가 서버(main.py)에서 호출할 "핵심 기능"입니다.
def analyze_food_traffic_light(food_input):
    # 속도와 가성비가 좋은 Gemini 2.5 Flash 모델 사용
    model = genai.GenerativeModel('gemini-pro')

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