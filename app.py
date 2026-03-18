import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (절대 변하지 않는 고유값) ---
COLOR_MAP = {
    "국회": {"bg": "#FFEBEE", "border": "#FFCDD2", "text": "#C62828"},
    "정부기관": {"bg": "#E3F2FD", "border": "#BBDEFB", "text": "#1565C0"},
    "대한수의사회": {"bg": "#E8F5E9", "border": "#C8E6C9", "text": "#2E7D32"},
    "수의과대학": {"bg": "#F3E5F5", "border": "#E1BEE7", "text": "#6A1B9A"},
    "언론사": {"bg": "#FFF3E0", "border": "#FFE0B2", "text": "#E65100"},
    "기업": {"bg": "#ECEFF1", "border": "#CFD8DC", "text": "#37474F"},
    "유관단체": {"bg": "#E0F7FA", "border": "#B2EBF2", "text": "#00838F"},
    "기타": {"bg": "#F5F5F5", "border": "#E0E0E0", "text": "#616161"}
}
CATEGORIES = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 및 디자인 (강력한 CSS 오버라이드) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    
    /* 가로 길이 최적화 (가로로 너무 길어지지 않게 고정) */
    .block-container { max-width: 900px; padding-top: 2rem; margin: auto; }
    .main { background-color: #ffffff; }

    /* [붉은색 제거] Streamlit 기본 멀티셀렉트 디자인 강제 변경 */
    div[data-baseweb="tag"] {
        background-color: #f0f2f6 !important;
        border: 1px solid #ddd !important;
        color: #333 !important;
    }

    /* 일정 카드: 초기의 세로형 배치 + 파스텔 컬러 */
    .schedule-card {
        padding: 25px; 
        border-radius: 20px;
        margin-bottom: 25px; 
        border: 2px solid;
        background-color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    
    .time-badge { font-size: 1.1rem; font-weight: 700; margin-bottom: 5px; display: block; }
    .subject-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 15px; display: block; line-height: 1.3; }
    
    /* 정보 항목 리스트 */
    .info-item { margin-bottom: 8px; font-size: 1.05rem; color: #333; }
    .info-label { font-weight: 700; color: #555; margin-right: 12px; min-width: 90px; display: inline-block; }
    
    .strategy-box {
        margin-top: 15px; padding: 18px; border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .memo-section {
        background-color: #FFFDE7; padding: 15px; border-radius: 12px;
        border-left: 6px solid #FFD54F; margin-top: 20px; font-size: 1rem;
    }
    
    .updated-tag { font-size: 0.75rem; color: #aaa; text-align: right; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 및 상태 관리 ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "ID", "Date", "Time", "Category", "Subject", "Location", "Target", 
        "Purpose", "ActionPlan", "Status", "ExtraInfo", "Companion", "Staff", "Memo", "Updated"
    ])
    # 기본 샘플 데이터 (초기 로딩 시 보여주기용)
    sample = {
        "ID": "1", "Date": "2026-03-18", "Time": "14:00", "Category": "국회", 
        "Subject": "수의사법 개정 관련 면담", "Location": "국회 의원회관 504호", "Target": "김의원 (보건복지위)", 
        "Purpose": "법안 통과 중요성 피력 및 협조 요청", "ActionPlan": "정책국장 대동 및 핵심 자료 배포", 
        "Status": "확정", "ExtraInfo": "보좌관: 박철수, 차량번호: 12가 3456", "Companion": "부회장, 정책국장", 
        "Staff": "이비서, 박기사", "Memo": "정문 면회실 신분증 지참 필수", "Updated": ""
    }
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([sample])], ignore_index=True)

if 'edit_id' not in st.session_state: st.session_state.edit_id = None
if 'selected_cats' not in st.session_state: st.session_state.selected_cats = CATEGORIES.copy()

# --- 4. 사이드바 (KVMA 회장님 일정) ---
st.sidebar.markdown("# 📒 KVMA 비서실")
menu = st.sidebar.radio("메뉴 이동", ["📅 일정 보기", "✍️ 일정 등록"])

# --- 5. [신규 일정 등록] ---
if menu == "✍️ 일정 등록":
    st.header("✍️ 신규 일정 등록")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜", value=datetime.now())
            time_val = st.time_input("시작 시간")
            category = st.selectbox("카테고리 선택", CATEGORIES)
        with col2:
            subject = st.text_input("회의명")
            location = st.text_input("장소")
            target = st.text_input("만나는 대상")

        extra = st.text_input("상세 정보 (세부장소/연락처/차량번호)")
        companion = st.text_input("동행인 정보")
        staff = st.text_input("수행직원 정보")
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 메모")

        if st.form_submit_button("일정 저장"):
            new_row = {"ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": category, "Subject": subject, "Location": location, "Target": target, "Purpose": purpose, "ActionPlan": action, "Status": "확정", "ExtraInfo": extra, "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("등록되었습니다.")

# --- 6. [📅 일정 보기] 파스텔 카드 나열 방식 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    # [검색 필터 섹션 - 붉은색 제거를 위해 체크박스 배지 방식 채택]
    with st.expander("🔍 검색 및 필터 옵션", expanded=False):
        f1, f2 = st.columns([3, 1])
        search = f1.text_input("회의명/대상 검색")
        f_date = f2.date_input("날짜 선택", value=datetime.now())
        
        st.write("카테고리 선택 (필터링)")
        cols = st.columns(len(CATEGORIES))
        new_selected = []
        for i, cat in enumerate(CATEGORIES):
            c_info = COLOR_MAP[cat]
            is_on = cat in st.session_state.selected_cats
            # 선택 여부에 따른 스타일
            style = f
