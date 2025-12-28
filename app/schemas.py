# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date           # 날짜 처리를 위해 가져옴

# 1. 기본 유저 형태
class UserBase(BaseModel):
    username: str

# 2. 회원가입할 때 받는 정보 (아이디, 비번)
class UserCreate(UserBase):
    password: str

# 3. 운동 데이터 형태
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str

class ExerciseResponse(ExerciseBase):
    id: int
    class Config:
        from_attributes = True  # (구버전 orm_mode = True)

# 4. 퀘스트 데이터 형태
class QuestBase(BaseModel):
    exercise_id: int
    target_count: str

class QuestResponse(QuestBase):
    id: int
    is_completed: bool
    user_id: int
    exercise: ExerciseResponse
    
    class Config:
        from_attributes = True

class QuestComplete(BaseModel):
    username: str
    quest_id: int

# 5. 식단 분석 결과 형태
class MealResponse(BaseModel):
    traffic_light: str
    feedback: str
    earned_xp: int

# 6. 로그인할 때 받는 정보
class UserLogin(BaseModel):
    username: str
    password: str

# ★ 7. 서버가 응답할 유저 정보 (여기에 exp가 꼭 있어야 함!)
class UserResponse(UserBase):
    id: int
    level: int
    exp: int  # ★ [추가] 이게 없어서 에러가 난 겁니다!
    items: List[str] = [] 

    class Config:
        from_attributes = True
