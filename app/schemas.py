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

# ★ [확인] 여기가 quest_id가 아니라 difficulty여야 합니다!
class QuestComplete(BaseModel):
    username: str
    difficulty: str

class WorkoutRequest(BaseModel):
    username: str
    exercise: str = "Debug"
    count: str = "1"
    amount: int = 10