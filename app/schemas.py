from pydantic import BaseModel
from typing import Optional

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

class ExerciseBase(BaseModel):
    name: str
    count: str
    difficulty: str

class ExerciseResponse(ExerciseBase):
    id: int
    class Config:
        orm_mode = True

# ★ [수정됨] 퀘스트 완료 요청 (누가, 어떤 난이도를 깼는지)
class QuestComplete(BaseModel):
    username: str
    difficulty: str

class WorkoutRequest(BaseModel):
    username: str
    exercise: str
    count: str