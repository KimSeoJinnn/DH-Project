# app/main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models, database, schemas, crud

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



from typing import List # 리스트 형태를 쓰기 위해 필요

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



import random

# AI 식단 분석 API (가짜 AI)
@app.post("/meals/analyze", response_model=schemas.MealResponse)
async def analyze_meal(
    file: UploadFile = File(...),   # 파일 받기
    user_id: int = Form(...),       # 유저 ID 받기
    db: Session = Depends(get_db)
):
    # --- 🤖 가상의 AI 분석 로직 시작 ---
    # 실제로는 여기서 이미지를 YOLO 모델에 넣어야 합니다.
    # 지금은 랜덤으로 결과를 뽑습니다.
    
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