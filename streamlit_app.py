import streamlit as st
import requests
import os
import random

# API 엔드포인트 (App Engine 또는 Cloud Run에 배포된 주소)
API_URL = os.environ.get("API_URL")
# 암호
ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD")

st.set_page_config(
    page_title="KCMF문서 Q&A 챗봇",
    page_icon="📚",
    layout="wide"
)

st.title("KCMF문서 Q&A 챗봇")

# 로그인 여부 확인
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    # 엔터키 처리를 위해 form 사용
    with st.form(key='password_form'):
        password = st.text_input("암호를 입력하세요:", type="password", key="password_input")
        submit_button = st.form_submit_button("확인")
        if submit_button:
            if password == ACCESS_PASSWORD:
                st.session_state.authenticated = True
                st.success("인증 성공!")
                st.rerun() # 화면을 다시 렌더링하여 암호 입력창을 제거
            else:
                st.warning("잘못된 암호입니다.")
                # st.error("잘못된 암호입니다.")
    
if not st.session_state.authenticated:
    st.stop()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 질문 예시
example_questions = [
    "독일의 미디어교육 현황은?",
    "미디어리 최근호 이슈 리포트 내용을 설명해줘",
    "보호자가 아이에게 스마트폰을 주는 이유?",
    "사실에 대한 학습 없이 팩트체크 학습이 가능한가?",
    "교육 자료 제작 시 유의할 점은?",
    "외국인도 정회원이 될 수 있나?",
    "OOO 강사 전화, 이메일, 소득 구분",
    "이메일 ID가 oooo 인 사람은 누구?",
    "강사 교통비 지급 기준은?",
    "강사 평가를 위해 직원이 해야 하는 일?",
    "상설교육은 개강 며칠전까지 계획보고를 해야 하나?",
    "라이브 커머스 사업을 하는 센터는?",
    "울산센터, 부산센터의 마을미디어교육 예산을 비교해줘",
    "부산센터 위기 상황 OOO 직원의 역할은?",
    "부산센터 위기 상황 현장대응반 구성원은?",
    "재단의 CCTV 갯수는?",
    "개인 역량 평가, 개인 업적 평가의 점수 계산 방식은?",
    "재단에서 제공하는 복리후생 혜택 목록",
    "6급 직원 경력 10년일 때 급여 수준은?",
    "스페인에 출장 다녀온 사람은?",
    "각 국가별 출장자 명단을 알려줘",
    "무리하고 불합리한 민원을 반복 제기하는 민원인 상대 요령?",
    "보고서의 기본 구성과 필수 항목을 알려줘",
    "사업배경, 사업목적, 사업내용, 기대효과의 차이점?",
    "공문서 작성 시 1,2,3 앞에 띄어쓰기는 몇 칸?",
    "기록물 보존 기간별 대상 기록물은?",
    "행사 의전시 차상위자 위치는 최상위자의 오른편인가 왼편인가?",
]
selected_questions = random.sample(example_questions, 6)

# 사이드바
with st.sidebar:
    st.header("질문 예시")
    for question in selected_questions:
        st.write(f"- {question}")
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    st.write("## 주의: \n- 질문이 조금만 바뀌어도 검색 결과가 달라지며, 검색결과 일부를 사용해 답변하므로 누락되는 정보가 있습니다. 100% 신뢰하지 마시고, 질문을 다양하게 해보세요.")
    
# 기존 대화 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
# question = st.text_input("질문:")
question = st.chat_input("질문:")

if question:
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(question)
    
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": question})

    # 로딩 표시
    with st.chat_message("assistant"):
        with st.spinner("답변 찾는 중..."):
            try:
                 # API 호출
                response = requests.post(
                    API_URL,
                    json={"question": question}
                )
                response.raise_for_status() # 오류 발생 시 예외 처리

                # 응답 표시 및 저장
                answer = response.json().get("answer", "응답을 받지 못했습니다.")
                st.write("#### 답변")
                st.write(answer)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer
                })

            except requests.RequestException as e:
                st.error(f"API 요청 오류: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.json()
                        st.error(f"세부 오류: {error_detail.get('detail', '알 수 없는 오류')}")
                    except:
                        st.error(f"상태 코드: {e.response.status_code}")
