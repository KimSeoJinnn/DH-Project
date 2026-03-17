# 파일 위치: app/test_api.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# 🛡️ 1. .env 파일(비밀 금고) 불러오기
load_dotenv() 

# 🛡️ 2. 금고 안에서 GEMINI_API_KEY 꺼내오기
API_KEY = os.getenv("GEMINI_API_KEY") 

genai.configure(api_key=API_KEY)

print("🔍 사용 가능한 모델을 조회합니다...")

try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- 발견됨: {m.name}")
            available_models.append(m.name)

    if not available_models:
        print("❌ 사용 가능한 모델이 하나도 없습니다. API 키가 올바른지 확인해주세요.")
    else:
        print("\n✅ 위 목록에 있는 이름 중 하나를 골라 app/ai_model.py에 넣으면 됩니다.")

except Exception as e:
    print(f"❌ 에러 발생: {e}")