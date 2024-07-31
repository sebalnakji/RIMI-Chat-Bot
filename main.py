import os
import uvicorn
from fastapi import FastAPI
from app.routes import router
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 인스턴스 생성
app = FastAPI()

# 환경 변수
load_dotenv()
server_endpoint = os.getenv("SERVER_ENDPOINT")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[server_endpoint],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 라우터 추가
app.include_router(router)

# uvicorn 설정
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001)


# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Medi-Mind Chat API!"}
