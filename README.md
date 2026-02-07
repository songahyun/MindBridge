# MindBridge 

# 생성형 AI 기반 아동·청소년 정서 분석 및 상담 지원 챗봇 웹 서비스

본 프로젝트는 **아동·청소년의 정서 상태를 분석하고 상담을 지원하는 AI 기반 웹 서비스**입니다.  
RAG 기반 상담 챗봇, 위험도 평가, 정서분석, 상담사 대시보드 및 상담 관리 기능을 제공합니다.

---

## 아동·청소년 모드

아동은 웹서비스에 로그인하여 챗봇과 상호작용하며 자신의 감정을 자연스럽게 표현할 수 있습니다.

### • 딥봇 상담 (Deep Chatbot)
- RAG 기반 상담 모델로 보다 심층적인 상담 진행  
- 주제별 첫 질문, 후속질문, 발화 횟수 제한, 자동 주제 전환 기능  
- 감정 분석 + 위험도 분석 포함

### • 라이트봇 상담 (Light Chatbot)
- 가벼운 일상 대화 중심의 간단 상담  
- 즉각적이고 부담 없는 대화 방식

### • 나의 상담사
- 위험도가 일정 기준 이상일 경우 상담사 매칭  
- 매칭된 상담사 정보 조회  
- 필요 시 상담사와 1:1 상담 진행 가능

---

## 상담사 모드

상담사는 아동별 분석 결과와 상담 이력을 효율적으로 관리할 수 있습니다.

### • 대시보드
- 6개 주제 기반 위험도 Top 3 아동 자동 추천  
- 태그 기반 분석 결과, 정서 변화 그래프 제공  
- 아동의 장기적 정서 패턴 시각화

### • 상담 내역 관리
- 아동별 보고서, 상담 기록 열람  
- 감정 분석, 태깅, 요약, 위험 점수 확인  
- 자동 저장된 기록 기반으로 아동 변화 추적 가능

---

# ⚙️ 로컬 실행 방법

## 1) 프로젝트 클론
비쥬얼 스튜디오 코드 환경  
git bash 창 열기(ctrl+`로 터미널 열고 +옆 더보기에서 bash선택) 
```bash
git clone <원격저장소 URL>  
```

## 2) 가상환경 생성 및 활성화
cmd 창 열기  
```bash
cd mindbridge_teamproject #중요: 루트에서 진행하기  
python -m venv .venv  # 가상환경 생성  
.\.venv\Scripts\activate # 가상환경 활성화 
```
맨 앞에 (.venv) 뜨면 성공  

  
예시:  
```bash
(.venv) C:\Users\jsw33\mindbridge_teamproject\frontend>  
```  

## 3) 패키지 설치
(가상환경 활성화 상태에서)  
cmd창에서 필요한 모든 패키지 설치:  
```bash
pip install -r requirements.txt   
```
중요: mindbridge_teamproject(루트)에서 진행  
  
## 4) OPENAI KEY 설정하기
mindbridge_teamproject/backend_AI/.env 파일을 열고 본인 OpenAI API Key를 입력  
예시:  
```bash
OPENAI_API_KEY=your-own-openai-api-key-here  
```
  
## 5) 실행 (cmd터미널 2개 필요)
가상환경 활성화 상태 필수. 앞에 (.venv) 있는지 확인.   
  
터미널 #1 — 프론트엔드  
```bash
cd frontend  
npm install (warning 나와도 무시)  
npm start  
```

## 6) 실시간 채팅 사용방법(cme터미널 추가 생성)  
```bash
cd frontend/socket-server
node server
```  

터미널 #2 — 백엔드 (FastAPI)  
```bash
cd backend_AI  
uvicorn app.main:app --reload --port 8001  
```
  
## 챗봇 첫 이용시 DB테이블이 자동 생성.  
DB확장 프로그램 : SQLite3 Editor