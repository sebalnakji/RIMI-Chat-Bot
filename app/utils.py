import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv


from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 환경 변수
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 호출
client = OpenAI(api_key=api_key)

assistant_id = os.getenv("ASSISTANT_ID")



# 임베딩 모델
embd = OpenAIEmbeddings(model="text-embedding-3-small", disallowed_special=(), openai_api_key=api_key)
# FAISS 인덱스 로드
DB_INDEX = "/home/ubuntu/workspace/fast_api_2/app/RAPTOR"
vectorstore = FAISS.load_local(DB_INDEX, embd, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever()

# def show_json(obj):
#     display(json.loads(obj.model_dump_json()))
    
def is_thread_id(thread_id):
    if thread_id:
        return thread_id
    else:
        thread = client.beta.threads.create()
        return thread.id
    
def add_RAG_to_assistant(instructions):
    assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    instructions=instructions,
    )
    return assistant 

def add_user_text(data_user, thread_id):
    message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=data_user,
    )
    return message

# 실행할 Run 을 생성합니다.
# Thread ID 와 Assistant ID 를 지정합니다.
def create_run(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,  # 생성한 스레드 ID
        assistant_id=assistant_id,  # 적용할 Assistant ID
    )
    
    return run

def wait_on_run(run, thread_id):
    # 주어진 실행(run)이 완료될 때까지 대기합니다.
    # status 가 "queued" 또는 "in_progress" 인 경우에는 계속 polling 하며 대기합니다.
    while run.status == "queued" or run.status == "in_progress":
        # run.status 를 업데이트합니다.
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        # API 요청 사이에 잠깐의 대기 시간을 두어 서버 부하를 줄입니다.
        time.sleep(0.5)
    return run

# 챗봇 함수
def chain_bot(request):
    data_user = request.user
    data_thread_id = request.thread_id
    docs = retriever.get_relevant_documents(data_user)
    # RAG 데이터 생성
    retrieval = [doc.page_content for doc in docs]
    instructions = f"""
    당신의 이름은 RIMI 챗봇입니다.
    당신은 따뜻한 마음을 가진 친절한 정신과 의사 어시스턴트이며, 문서에 포함된 주제에 대해 사용자와 대화하고 있습니다.
    정확한 답변을 제공하기 아래 문서의 정보를 참고하십시오.    

    1. {retrieval[0]}
    2. {retrieval[1]}
    3. {retrieval[2]}
    4. {retrieval[3]}
        
    """
    
    thread_id = is_thread_id(data_thread_id)
    assistant = add_RAG_to_assistant(instructions)
    message = add_user_text(data_user, thread_id)
    run = create_run(thread_id, assistant_id)
    
    # run 객체를 대기 상태로 설정하고, 해당 스레드에서 실행을 완료할 때까지 기다립니다.
    run = wait_on_run(run, thread_id)
    
    messages = client.beta.threads.messages.list(thread_id=thread_id)    
    for res in messages:
        result = res.content[0].text.value
        break
    return result , thread_id

# # 챗봇 함수
# def chain_bot(request) -> str:
#     messages = [
#     {"role": "user", "content": request.user}
#     ]

#     model = "gpt-3.5-turbo"
#     stream = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         stream=True,
#     )

#     result = ""
#     for chunk in stream:
#         if chunk.choices[0].delta.content is not None:
#             result += chunk.choices[0].delta.content

#     return result
    