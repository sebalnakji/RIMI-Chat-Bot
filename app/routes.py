import logging
from .utils import chain_bot
from .models import ChatRequest
from fastapi import APIRouter, HTTPException

# 로깅
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

# 파라미터 설명
description = """
- user: 챗봇에서 사용자가 입력하는 텍스트\n
- assistant: 이전 대화 내용 (개발 예정)\n
- chat_ind: 탭 구분용 변수
"""

# 라우터 설정
@router.post("/medi-mind-chat", description=description)
async def chatbot(request: ChatRequest):
    try:
        response , thread_id= chain_bot(request)
        return response , thread_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   
    