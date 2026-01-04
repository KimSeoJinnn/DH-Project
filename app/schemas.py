from pydantic import BaseModel
from typing import Optional

# 유저 관련 스키마
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    level: int
    exp: int

    class Config:
        orm_mode = True

# ★ [추가됨] 운동 퀘스트 관련 스키마
class ExerciseBase(BaseModel):
    name: str
    count: str
    difficulty: str

class ExerciseResponse(ExerciseBase):
    id: int
    
    class Config:
        orm_mode = True

# 운동 기록 요청용
class WorkoutRequest(BaseModel):
    username: str
    exercise: str
    count: str

# 퀘스트 완료 요청용 (나중에 사용)
class QuestComplete(BaseModel):
    username: str
    quest_id: int