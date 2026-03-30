# models/light_prompt.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from collections import deque
from threading import Lock
from typing import List, Dict, Union, Optional

# 🔹 .env 파일 로드 (있으면)
load_dotenv()

# 🔹 환경변수에서 OPENAI_API_KEY 읽기
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 또는 시스템 환경변수를 확인하세요.")

# 🔹 OpenAI 클라이언트 생성
client = OpenAI(api_key=API_KEY)


# =============================
# 세션 관리 (간단한 in-memory 저장소)
# =============================
class SessionManager:
    """
    간단한 in-memory session 저장소.
    - session_id -> deque([{"role":..., "content":...}, ...])
    - thread-safe (간단한 Lock 사용)
    """
    def __init__(self, max_messages_per_session: int = 60):
        self._store: Dict[str, deque] = {}
        self._max = max_messages_per_session
        self._lock = Lock()

    def create_session(self, session_id: str, system_prompt: Optional[str] = None):
        with self._lock:
            self._store[session_id] = deque(maxlen=self._max)
            if system_prompt is not None:
                self._store[session_id].append({"role": "system", "content": system_prompt})

    def add_user_message(self, session_id: str, content: str):
        with self._lock:
            self._ensure_session_exists(session_id)
            self._store[session_id].append({"role": "user", "content": content})

    def add_assistant_message(self, session_id: str, content: str):
        with self._lock:
            self._ensure_session_exists(session_id)
            self._store[session_id].append({"role": "assistant", "content": content})

    def get_messages(self, session_id: str) -> List[Dict]:
        with self._lock:
            self._ensure_session_exists(session_id)
            # 반환은 리스트(복사)로
            return list(self._store[session_id])

    def clear_session(self, session_id: str):
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]

    def _ensure_session_exists(self, session_id: str):
        if session_id not in self._store:
            self._store[session_id] = deque(maxlen=self._max)


# 전역 세션 매니저 인스턴스 (다른 모듈에서 import해서 사용 가능)
session_mgr = SessionManager(max_messages_per_session=60)


# =============================
# 라이트 챗봇 프롬프트 정의
# =============================
def get_light_prompt(username: str, prev_summary: str = "") -> str:
    prev_section = ""
    if prev_summary:
        prev_section = (
            "\n\n(참고: 아래 이전 상담 기록 요약을 참고하되, 대화를 자연스럽게 이어가라.)\n\n"
            "이전 상담 기록 요약:\n" + prev_summary + "\n"
        )

    return f"""
너는 아동·청소년과 따뜻하게 대화하는 전문 상담사야.
아동의 이름은 "{username}"이야. 상담 대화에서 아동을 {username}이라고 불러.
너의 가장 중요한 역할은 **아동의 현재 심리 상태와 그 원인을 파악**하고, **아이가 충분히 말할 수 있도록 끝까지 들어주는 것**이야.
대화는 성의껏 경청하고 이어간다.
대화를 중간에 끊거나, 대화를 끝내도 된다는 신호를 주지 마.
{prev_section}
대화 방식 지침:
1. 대화 시작 시, **아이의 상태를 확인하는 짧은 질문**을 먼저 해. ("오늘 하루 어땠어?", "지금 기분은 어때?")
2. 아동이 감정을 표현하면,
   - **즉시 공감하거나 조언하지 말고**, 우선 **그 상황을 이해하는 반응**을 보여줘. ("그랬구나.", "그런 일이 있었구나.")
   - 필요할 때만 부드럽게 이유를 묻거나 상황을 더 듣고 싶어해. ("어떤 일이 있었는지 조금 더 말해줄래?" 정도로 간단히.)
   - 아동이 오늘 느낀 감정(우울, 행복, 슬픔 등)에 대해 **충분히 말하고 싶어 하는 부분을 끝까지 들어준다.**
3. 공감을 깊게 하기 위해 **비슷한 경험을 지어내서 짧게 공유**해.
   - 아동이 "친구가 무시했어"라고 하면 "나도 전에 친구가 무시하는 말을 해서 속상했던 적 있어"처럼,
     **상대방 감정에 맞춘 짧은 경험담을 1문장 정도** 덧붙여줘.
4. 아동이 충분히 말한 뒤에야,
   - **따뜻한 공감**을 표현해. ("그랬구나, 속상했겠다.")
   - **짧은 위로·안정 문장**을 덧붙여. (예: "잠깐 쉬어도 괜찮아.", "그럴 수도 있지.", "괜찮아", "조금씩 나아질 거야.", "너무 부담 갖지 않아도 돼.", "잘 될 거야!")
5. 질문은 매번 하지 않고, **아이가 스스로 더 말할 수 있게 기다리고 반응**해.
   - 질문이 필요하면 짧게, 자연스럽게 던져라. (ex. "그 뒤에 어떻게 됐어?" 정도)
7. **훈계하거나 비난하지 말고, 따뜻하고 안전한 어조를 유지**해.
8. 목표는 아이가 "끝까지 들어준다", "내 이야기를 이해해준다"고 느끼도록 하는 거야.
9. 답변은 **짧고 간결하게(1~3문장)** 해. 반말을 사용해.
10. 이미 언급한 내용이나 사용자가 이미 말한 내용은 다시 묻지마.
"""

# =============================
# session-style (딥 스타일) 응답 생성 함수
# =============================
def get_light_response_session_style(session_id: str, username: str = "아이", prev_summary: str = "", user_input: Optional[str] = None) -> str:
    """
    세션 보장 및 user 추가 -> conversation_history를 하나의 블록으로 묶어 모델에 전달.
    """
    # 1) 세션 존재 보장 및 user 발화 추가
    session_mgr._ensure_session_exists(session_id)
    if user_input is not None:
        session_mgr.add_user_message(session_id, user_input)

    # 2) build conversation_history (최근 메시지 전체)
    msgs = session_mgr.get_messages(session_id)
    history_lines = []
    for m in msgs:
        role = m.get("role", "")
        content = m.get("content", "")
        history_lines.append(f"{role}: {content}")
    conversation_history = "\n".join(history_lines) if history_lines else "(빈 대화 기록)"

    # 3) system + human 메시지 구성
    system_text = get_light_prompt(username, prev_summary)
    human_content = f"""
- 이번 세션 대화 기록:
{conversation_history}

위의 모든 맥락을 참고해서, 아동의 마지막 발화에 대해 이어서 공감하고 자연스럽게 질문하거나 반응해줘.
"""
    messages = [
        {"role": "system", "content": system_text},
        {"role": "user", "content": human_content}
    ]

    # 4) API 호출 
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.3,
            messages=messages
        )
        choice = response.choices[0]
        content = None
        if hasattr(choice, "message") and getattr(choice.message, "content", None):
            content = choice.message.content
        elif isinstance(choice, dict):
            content = choice.get("message", {}).get("content") or choice.get("text")
        assistant_text = (content or "").strip()

        # 5) 세션에 assistant 저장 (원본 시퀀스 형식 유지)
        session_mgr.add_assistant_message(session_id, assistant_text)

        return assistant_text
    except Exception as e:
        return f"[ERROR] {e}"


# =============================
# get_light_response 
# =============================
def get_light_response(conversation: Union[List[Dict], str], user_input: Optional[str] = None, username: str = "아이", prev_summary: str = "") -> str:
    """
    - conversation:
        * list of dict (기존 방식: [{"role":"system","content":"..."}, ...])
        * OR session_id (str) -> 이 경우 session-style로 호출(메시지들을 하나의 history 블록으로 묶어 전달)
    - user_input: 현재 요청에서 들어온 사용자의 최신 발화(옵션).
    - username: 시스템 프롬프트에서 사용할 아동 이름(기본 "아이")
    - prev_summary: 이전 deep 세션 요약(옵션)
    """
    if isinstance(conversation, str):
        # session-style로 처리
        return get_light_response_session_style(conversation, username=username, prev_summary=prev_summary, user_input=user_input)

    # 기존 리스트 방식 호환: user_input이 있으면 해당 호출에서만 메시지에 추가(세션 저장은 하지 않음)
    messages = conversation
    if user_input is not None:
        messages = messages + [{"role": "user", "content": user_input}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=messages
        )
        choice = response.choices[0]
        content = None
        if hasattr(choice, "message") and getattr(choice.message, "content", None):
            content = choice.message.content
        elif isinstance(choice, dict):
            content = choice.get("message", {}).get("content") or choice.get("text")
        assistant_text = (content or "").strip()
        return assistant_text
    except Exception as e:
        return f"[ERROR] get_light_response 실패: {e}"
