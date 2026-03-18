import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (현재 컬러톤 고수) ---
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

# --- 2. 페이지 설정 및 가로 너비 제한 (CSS) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    
    /* 가로 너비를 800px로 제한하여 시선 집중 */
    .block-container { max-width: 800px; padding-top: 2rem; margin: auto; }
    .main { background-color: #ffffff; }

    /* 드롭다운(Expander) 디자인 커스텀 */
    .stExpander {
        border-radius: 12px !important;
        border: 1px solid #eee !important;
        margin-bottom: 10px !important;
        background-color: #fafafa !important;
    }
    
    /* 일정 카드 내부 스타일 */
    .schedule-inner {
        padding: 20px;
        border-radius: 15px;
        border: 2px solid;
        background-color: white;
    }
    
    .subject-title { font-size: 1.4rem; font-weight: 800; margin-bottom: 15px; display: block; }
    .info-item { margin-bottom: 8px; font-size: 1rem; color: #333; line-height: 1.5; }
    .info-label { font-weight: 700; color: #555; margin-right: 10px; min-width: 80px; display: inline-block; }
    
    .strategy-box {
        margin-top: 15px; padding: 15px; border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .memo-section {
        background-color: #FFFDE7; padding: 15px; border-radius: 10px;
        border-left: 5px solid #FFD54F; margin-top: 15px; font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 및 상태 관리 (에러 방지용 초기화) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "ID", "Date", "Time", "Category", "Subject", "Location", "Target", 
        "Purpose", "ActionPlan", "Status", "ExtraInfo", "Companion", "Staff", "Memo", "Updated"
    ])
    # 샘플 데이터 1개 추가
    sample = {
        "ID": "1", "Date": datetime.now().strftime("%Y-%m-%d"), "Time": "14:00", "Category": "국회", 
        "Subject": "수의사법 개정 관련 면담", "Location": "국회 의원회관 504호", "Target": "김의원 (보건복지위)", 
        "Purpose": "법안 통과 중요성 설명", "ActionPlan": "핵심 요약본 전달", "Status": "확정", 
        "ExtraInfo": "보좌관 연락처 포함", "Companion": "부회장", "Staff": "이비서", "Memo": "신분증 지참", "Updated": ""
    }
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([sample])], ignore_index=True)

if 'edit_id' not in st.session_state: st.session_state.edit_id = None
if 'selected_cats' not in st.session_state: st.session_state.selected_cats = CATEGORIES.copy()

# --- 4. 사이드바 ---
st.sidebar.markdown("# 🏢 KVMA 비서실")
menu = st.sidebar.radio("메뉴 이동", ["📅 일정 보기", "✍️ 일정 등록"])

# --- 5. [신규 일정 등록] ---
if menu == "✍️ 일정 등록":
    st.header("✍️ 신규 일정 등록")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜", value=datetime.now())
            time_val = st.time_input("시간")
            category = st.selectbox("카테고리", CATEGORIES)
        with col2:
            subject = st.text_input("회의명")
            location = st.text_input("장소")
            target = st.text_input("만나는 대상")

        extra = st.text_input("상세정보 (세부장소/연락처/차량)")
        companion = st.text_input("회장님 외 동행인")
        staff = st.text_input("사무처 수행직원")
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 (유의사항)")

        if st.form_submit_button("저장하기"):
            new_row = {"ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": category, "Subject": subject, "Location": location, "Target": target, "Purpose": purpose, "ActionPlan": action, "Status": "확정", "ExtraInfo": extra, "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("등록 완료")

# --- 6. [📅 일정 보기] 드롭다운 방식 적용 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    with st.expander("🔍 검색 및 필터", expanded=False):
        f1, f2 = st.columns([3, 1])
        search = f1.text_input("회의명/대상 검색")
        f_date = f2.date_input("날짜 선택", value=datetime.now())
        sel_cats = st.multiselect("카테고리 필터", CATEGORIES, default=st.session_state.selected_cats)
        st.session_state.selected_cats = sel_cats

    df = st.session_state.data.copy()
    # 에러 방지: 데이터가 비어있지 않은지 확인
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        display_df = df[(df['Date'] == f_date) & (df['Category'].isin(st.session_state.selected_cats))]
        if search: 
            display_df = display_df[display_df['Subject'].str.contains(search, na=False) | display_df['Target'].str.contains(search, na=False)]
        display_df = display_df.sort_values(by="Time")
    else:
        display_df = pd.DataFrame()

    st.markdown(f"### 📍 {f_date.strftime('%m월 %d일')} 일정")

    if display_df.empty:
        st.info("해당 조건의 일정이 없습니다.")
    else:
        for idx, row in display_df.iterrows():
            c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
            
            # 드롭다운 제목 (시간 | 회의명)
            expander_title = f"⏰ {row['Time']} | [{row['Category']}] {row['Subject']}"
            
            with st.expander(expander_title):
                if st.session_state.edit_id == row['ID']:
                    # 수정 폼
                    with st.form(key=f"edit_{row['ID']}"):
                        u_sub = st.text_input("회의명", row['Subject'])
                        u_time = st.text_input("시간", row['Time'])
                        u_tar = st.text_input("대상", row['Target'])
                        u_loc = st.text_input("장소", row['Location'])
                        u_pur = st.text_area("목적", row['Purpose'])
                        u_act = st.text_area("대응", row['ActionPlan'])
                        u_mem = st.text_area("메모", row['Memo'])
                        if st.form_submit_button("수정 완료"):
                            st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], ['Subject', 'Time', 'Target', 'Location', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = [u_sub, u_time, u_target, u_loc, u_pur, u_act, u_mem, datetime.now().strftime("%H:%M")]
                            st.session_state.edit_id = None
                            st.rerun()
                else:
                    # [상세 정보 카드]
                    st.markdown(f"""
                    <div class="schedule-inner" style="border-color: {c['border']}; background-color: {c['bg']};">
                        <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
                        <div class="info-item"><span class="info-label">📍 장소</span> {row['Location']}</div>
                        <div class="info-item"><span class="info-label">👤 대상</span> {row['Target']}</div>
                        <div class="info-item"><span class="info-label">👥 동행</span> {row['Companion']}</div>
                        <div class="info-item"><span class="info-label">👔 수행</span> {row['Staff']}</div>
                        
                        <div class="strategy-box">
                            <div class="info-item"><b>🎯 회의 목적</b><br>{row['Purpose']}</div>
                            <div class="info-item" style="margin-top:10px;"><b>📋 사무처 대응</b><br>{row['ActionPlan']}</div>
                        </div>
                        
                        <div class="memo-section">📌 <b>유의사항 (Memo)</b><br>{row['Memo']}<br><small style="color:#777;">ℹ️ {row['ExtraInfo']}</small></div>
                        {f'<div style="text-align:right; font-size:0.7rem; color:#aaa; margin-top:10px;">updated. {row["Updated"]}</div>' if row['Updated'] else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📝 정보 수정", key=f"btn_{row['ID']}"):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
