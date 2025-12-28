# app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models, database, schemas, crud
from typing import List # 리스트 형태를 쓰기 위해 필요
from pydantic import BaseModel
import random

# DB 테이블 생성 (sql_app.db 파일이 없으면 자동 생성)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# DB 세션 가져오기
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "헬린이 키우기 서버 (보안 해제 모드) 🚀"}

# 회원가입 API
@app.post("/users/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 이미 있는 아이디인지 검사
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 있는 아이디입니다.")
    
    # 없으면 저장
    return crud.create_user(db=db, user=user)

# 1. 관리자용: 기초 운동 데이터 생성 API
@app.post("/exercises/init")
def init_data(db: Session = Depends(get_db)):
    result = crud.initialize_exercises(db)
    if result:
        return {"message": result}
    return {"message": "이미 데이터가 있습니다."}

# 2. 헬린이용: 오늘의 운동 퀘스트 받기 API
@app.get("/quests", response_model=List[schemas.ExerciseResponse])
def get_today_quests(db: Session = Depends(get_db)):
    return crud.get_random_quests(db, limit=3)

# 퀘스트 완료 API
@app.post("/quests/complete", response_model=schemas.QuestResponse)
def complete_quest_api(quest: schemas.QuestComplete, db: Session = Depends(get_db)):
    result = crud.complete_quest(db, quest)
    if not result:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return result

# AI 식단 분석 API (가짜 AI)
@app.post("/meals/analyze", response_model=schemas.MealResponse)
async def analyze_meal(
    file: UploadFile = File(...),   # 파일 받기
    user_id: int = Form(...),       # 유저 ID 받기
    db: Session = Depends(get_db)
):
    # --- 🤖 가상의 AI 분석 로직 시작 ---
    ai_results = [
        {"color": "🟢 GREEN", "msg": "완벽해요! 단백질이 풍부하네요.", "xp": 5},
        {"color": "🟡 YELLOW", "msg": "나쁘지 않아요. 국물은 남기세요.", "xp": 2},
        {"color": "🔴 RED", "msg": "위험해요! 튀김 옷은 벗기고 드세요.", "xp": 0},
    ]
    
    result = random.choice(ai_results) # 랜덤 뽑기
    # --- 🤖 가상의 AI 분석 로직 끝 ---

    # DB에 저장
    crud.create_meal_log(
        db=db, 
        user_id=user_id, 
        traffic_light=result["color"], 
        feedback=result["msg"], 
        xp=result["xp"]
    )

    # 결과 반환
    return {
        "traffic_light": result["color"],
        "feedback": result["msg"],
        "earned_xp": result["xp"]
    }

# 로그인 API
@app.post("/users/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. 아이디 찾기
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="아이디가 없습니다.")
    
    # 2. 비밀번호 맞는지 검사 (crud에 만든 함수 사용)
    if not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="비밀번호가 틀렸습니다.")
    
    # 3. 성공 시 유저 정보 반환
    return {
        "message": "로그인 성공! 💪",
        "user_id": db_user.id,
        "username": db_user.username,
        "level": db_user.level
    }

# ★ [수정] BaseModel이 이제 정의되어서 에러가 안 납니다.
class WorkoutRequest(BaseModel):
    username: str
    exercise: str
    count: str

# 2. 운동 기록 및 레벨업 처리

# [수정 후 (새로운 코드) - 이렇게 되어야 함!]
@app.post("/users/workout")
def record_workout(request: WorkoutRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    # ★ 여기가 핵심! 레벨이 아니라 경험치를 줍니다.
    gain_xp = 10 
    user.exp += gain_xp
    
    message = f"운동 완료! 경험치 +{gain_xp} 획득!"
    
    # 경험치 100 넘으면 레벨업
    if user.exp >= 100:
        user.level += 1
        user.exp = 0 
        message = f"🎉 축하합니다! 레벨업! (Lv.{user.level})"
        
    db.commit()
    
    return {
        "message": message, 
        "new_level": user.level,
        "current_xp": user.exp 
    }


# 랭킹 조회 API (레벨 높은 순, 경험치 높은 순으로 정렬)
@app.get("/users/ranking")
def get_ranking(db: Session = Depends(get_db)):
    # 레벨 내림차순(desc), 경험치 내림차순(desc)으로 상위 10명 가져오기
    top_users = db.query(models.User).order_by(
        models.User.level.desc(), 
        models.User.exp.desc()
    ).limit(10).all()
    
    return top_users
