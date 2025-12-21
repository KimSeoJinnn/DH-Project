from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "안녕하세요! AI 헬스케어 앱 서버입니다."}

@app.get("/hello")
def read_hello():
    return {"message": "FastAPI가 정상적으로 작동 중입니다!"}