from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import models, database, schemas, crud
from typing import List

try: models.Base.metadata.create_all(bind=database.engine)
except: pass

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/")
def read_root(): return {"message": "헬린이 키우기 서버 가동 중 🚀"}

@app.post("/users/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user: raise HTTPException(status_code=400, detail="이미 있는 아이디입니다.")
    return crud.create_user(db=db, user=user)

@app.post("/users/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호가 틀렸습니다.")
    return {"message": "로그인 성공!", "username": db_user.username, "level": db_user.level, "exp": db_user.exp}

@app.post("/exercises/init")
def init_data(db: Session = Depends(get_db)):
    try:
        models.Base.metadata.create_all(bind=database.engine)
        result = crud.initialize_exercises(db)
        if result: return {"message": result}
        return {"message": "이미 데이터가 있습니다."}
    except Exception as e: return {"message": f"에러: {str(e)}"}

@app.get("/quests", response_model=List[schemas.ExerciseResponse])
def get_today_quests(db: Session = Depends(get_db)):
    try: return crud.get_random_quests(db, limit=3)
    except: 
        models.Base.metadata.create_all(bind=database.engine)
        return crud.get_random_quests(db, limit=3)

# ★ [확인] 이 부분이 있어야 합니다.
@app.post("/quests/complete")
def complete_quest_api(request: schemas.QuestComplete, db: Session = Depends(get_db)):
    result = crud.complete_quest(db, request)
    if not result: raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return result

@app.post("/users/workout")
def record_workout(request: schemas.WorkoutRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user: raise HTTPException(status_code=404, detail="유저 없음")
    gain_xp = 10
    user.exp += gain_xp
    msg = f"기록 완료! (+{gain_xp} XP)"
    if user.exp >= 100:
        user.level += 1
        user.exp -= 100
        msg = f"🎉 레벨업! (Lv.{user.level})"
    db.commit()
    return {"message": msg, "new_level": user.level, "current_xp": user.exp}

@app.get("/users/ranking")
def get_ranking(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.level.desc(), models.User.exp.desc()).limit(10).all()