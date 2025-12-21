# app/schemas.py
from pydantic import BaseModel

# 회원가입할 때 입력받을 정보
class UserCreate(BaseModel):
    username: str
    password: str   # 여기에 "1234"라고 치면 그대로 들어옵니다.
    height: int
    weight: int

# 회원가입 완료 후 보여줄 정보
class UserResponse(BaseModel):
    id: int
    username: str
    level: int
    xp: int
    
    class Config:
        orm_mode = True

# 운동 정보를 보여줄 때 쓰는 틀
class ExerciseResponse(BaseModel):
    id: int
    name: str
    part: str
    difficulty: str
    video_url: str | None = None # 영상 주소는 없을 수도 있음
    tip: str | None = None

    class Config:
        orm_mode = True


# 1. 사용자가 보낼 데이터: "저 이 퀘스트(이름) 깼어요! (경험치)"
class QuestComplete(BaseModel):
    user_id: int        # 누가 깼는지 (로그인 기능 전이라 임시로 받음)
    quest_name: str     # 깬 퀘스트 이름 (예: 스쿼트)
    earned_xp: int      # 얻을 경험치 (예: 10)

# 2. 서버가 응답할 데이터: "보상 확인하세요"
class QuestResponse(BaseModel):
    message: str        # "경험치 10 획득!" 또는 "레벨업! Lv.2 달성!"
    current_level: int
    current_xp: int
    required_xp: int    # 다음 레벨까지 필요한 경험치



# AI 분석 결과 (프론트엔드에 줄 데이터)
class MealResponse(BaseModel):
    traffic_light: str  # "🟢 GREEN", "🟡 YELLOW", "🔴 RED"
    feedback: str       # "단백질 굿!", "너무 기름져요"
    earned_xp: int      # 획득 경험치