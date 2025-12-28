# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 1. 사용자 (Users)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    height = Column(Integer)
    weight = Column(Integer)
    
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    last_login = Column(Date, default=datetime.now().date)

    # 관계 설정
    meals = relationship("MealLog", back_populates="owner")
    workouts = relationship("WorkoutLog", back_populates="owner")
    bodies = relationship("BodyLog", back_populates="owner")

# 2. 식단 기록 (MealLogs)
class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    image_url = Column(String)
    traffic_light = Column(String) # GREEN, YELLOW, RED
    feedback = Column(String)
    earned_xp = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    owner = relationship("User", back_populates="meals")

# 3. 운동 퀘스트 기록 (WorkoutLogs)
class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    quest_name = Column(String)
    completed_at = Column(DateTime, default=datetime.now)
    earned_xp = Column(Integer)

    owner = relationship("User", back_populates="workouts")

# 4. 운동 도감 (Exercises)
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    part = Column(String)
    difficulty = Column(String)
    video_url = Column(String)
    tip = Column(String)

    
# 5. 눈바디 기록 (BodyLogs)
class BodyLog(Base):
    __tablename__ = "body_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    image_url = Column(String)
    weight = Column(Integer) # 그 날의 체중
    created_at = Column(Date, default=datetime.now().date)

    owner = relationship("User", back_populates="bodies")
