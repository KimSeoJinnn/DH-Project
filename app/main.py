from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models, database, schemas, crud
from typing import List
from pydantic import BaseModel
import random

# 1. 서버 시작 시 테이블 생성 시도
try:
    models.Base.metadata.create_all(bind=database.engine)
except:
    pass

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
    return {"message": "헬린이 키우기 서버 (정상 가동 중) 🚀"}

# 회원가입 API
@app.post("/users/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 있는 아이디입니다.")
    return crud.create_user(db=db, user=user)

# ★ [수정됨] 관리자용: 기초 운동 데이터 생성 API (초강력 버전)
@app.post("/exercises/init")
def init_data(db: Session = Depends(get_db)):
    try:
        # 1. 테이블이 없으면 지금 당장 만듭니다 (확인사살)
        models.Base.metadata.create_all(bind=database.engine)
        
        # 2. 데이터 채워넣기
        result = crud.initialize_exercises(db)
        
        if result:
            return {"message": result}
        return {"message": "이미 데이터가 있습니다."}
        
    except Exception as e:
        # 에러가 나도 500으로 죽지 말고, 에러 내용을 보여줘라! (디버깅용)
        return {"message": f"에러발생: {str(e)}"}

# 오늘의 운동 퀘스트 받기 API
@app.get("/quests", response_model=List[schemas.ExerciseResponse])
def get_today_quests(db: Session = Depends(get_db)):
    # 혹시라도 테이블 없으면 여기서도 생성 시도
    try:
        return crud.get_random_quests(db, limit=3)
    except:
        models.Base.metadata.create_all(bind=database.engine)
        return crud.get_random_quests(db, limit=3)

# 퀘스트 완료 API
@app.post("/quests/complete")
def complete_quest_api(quest: schemas.QuestComplete, db: Session = Depends(get_db)):
    # 아직 기능 구현 전이므로 임시 응답
    return {"message": "퀘스트 완료 기능 준비 중"}

# AI 식단 분석 API
@app.post("/meals/analyze")
async def analyze_meal(file: UploadFile = File(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    ai_results = [
        {"color": "🟢 GREEN", "msg": "완벽해요! 단백질이 풍부하네요.", "xp": 5},
        {"color": "🟡 YELLOW", "msg": "나쁘지 않아요.", "xp": 2},
        {"color": "🔴 RED", "msg": "기름진 음식은 줄여보세요.", "xp": 1},
    ]
    result = random.choice(ai_results)
    crud.create_meal_log(db=db, user_id=user_id, traffic_light=result["color"], feedback=result["msg"], xp=result["xp"])
    return {"traffic_light": result["color"], "feedback": result["msg"], "earned_xp": result["xp"]}

# 로그인 API
@app.post("/users/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="아이디가 없습니다.")
    if not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="비밀번호가 틀렸습니다.")
    return {
        "message": "로그인 성공! 💪",
        "user_id": db_user.id,
        "username": db_user.username,
        "level": db_user.level,
        "exp": db_user.exp
    }

class WorkoutRequest(BaseModel):
    username: str
    exercise: str
    count: str

# 운동 기록 API
@app.post("/users/workout")
def record_workout(request: WorkoutRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    gain_xp = 10 
    user.exp += gain_xp
    message = f"운동 완료! 경험치 +{gain_xp} 획득!"
    
    if user.exp >= 100:
        user.level += 1
        user.exp = 0 
        message = f"🎉 축하합니다! 레벨업! (Lv.{user.level})"
        
    db.commit()
    return {"message": message, "new_level": user.level, "current_xp": user.exp}

# 랭킹 조회 API
@app.get("/users/ranking")
def get_ranking(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.level.desc(), models.User.exp.desc()).limit(10).all()