import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (회장님이 승인하신 컬러톤) ---
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
    
    .block-container { max-width: 850px; padding-top: 2rem; margin: auto; }
    .main { background-color: #ffffff; }

    /* [붉은색 상자 완전 제거] Multiselect 태그 디자인 강제 변경 */
    div[data-baseweb="tag"] {
        background-color: #f0f2f6 !important;
        border: 1px solid #ddd !important;
        color: #333 !important;
        border-radius: 20px !important;
    }
    div[data-baseweb="tag"] span { color: #333 !important; }

    /* Expander(드롭다운) 디자인 */
    .stExpander {
        border-radius: 12px !important;
        border: 1px solid #eee !important;
        margin-bottom: 12px !important;
        background-color: #ffffff !important;
    }
    .stExpander > div:first-child:hover { background-color: #f9f9f9 !important; }

    /* 일정 카드 내부: 파스텔 테두리와 배경 */
    .schedule-inner {
        padding: 25px;
        border-radius: 18px;
        border: 2px solid;
        background-color: white;
    }
    
    .subject-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 15px; display: block; line-height: 1.3; }
    .info-item { margin-bottom: 10px; font-size: 1.05rem; color: #333; }
    .info-label { font-weight: 700; color: #555; margin-right: 12px; min-width: 90px; display: inline-block; }
    
    /* 전략적 중요 박스 */
    .strategy-box {
        margin-top: 15px; padding: 18px; border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(0, 0, 0, 0.06);
    }
    
    .memo-section {
        background-color: #FFFDE7; padding: 15px; border-radius: 12px;
        border-left: 6px solid #FFD54F; margin-top: 18px; font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 및 상태 관리 ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "ID", "Date", "Time", "Category", "Subject", "Location", "Target", 
        "Purpose", "ActionPlan", "Status", "ExtraInfo", "Companion", "Staff", "Memo", "Updated"
    ])
    # 기본 샘플 데이터 (파스텔 테스트용)
    sample = {
        "ID": "1", "Date": "2026-03-18", "Time": "14:00", "Category": "국회", 
        "Subject": "수의사법 개정 관련 면담", "Location": "국회 의원회관 504호", "Target": "김의원 (보건복지위)", 
        "Purpose": "법안 통과 중요성 피력 및 협조 요청", "ActionPlan": "정책국장 대동 및 핵심 자료 배포", 
        "Status": "확정", "ExtraInfo": "보좌관: 박철수, 등록차량: 12가 3456", "Companion": "부회장, 정책국장", 
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
            subject = st.text_input("핵심 안건 (회의명)")
            location = st.text_input("장소")
            target = st.text_input("만나는 대상")

        extra = st.text_input("상세 정보 (세부 장소/연락처/차량번호)")
        companion = st.text_input("회장님 외 동행인")
        staff = st.text_input("사무처 수행직원")
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 (유의사항)")

        if st.form_submit_button("저장하기"):
            new_row = {"ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": category, "Subject": subject, "Location": location, "Target": target, "Purpose": purpose, "ActionPlan": action, "Status": "확정", "ExtraInfo": extra, "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("일정이 등록되었습니다.")

# --- 6. [📅 일정 보기] 드롭다운 및 파스텔 디자인 복구 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    with st.expander("🔍 검색 및 필터 옵션", expanded=False):
        f1, f2 = st.columns([3, 1])
        search = f1.text_input("회의명/대상 검색")
        f_date = f2.date_input("날짜 선택", value=datetime.now())
        
        # 카테고리별 개별 파스텔 배지 (체크박스 스타일)
        st.write("카테고리 선택")
        new_cats = []
        cols = st.columns(len(CATEGORIES))
        for i, cat in enumerate(CATEGORIES):
            c_info = COLOR_MAP[cat]
            on = cat in st.session_state.selected_cats
            style = f'background:{c_info["bg"]}; border:1px solid {c_info["border"]}; color:{c_info["text"]};' if on else 'background:#fff; border:1px solid #eee; color:#ccc;'
            st.markdown(f'<div style="{style} padding:4px 10px; border-radius:15px; text-align:center; font-size:0.8rem; font-weight:bold;">{cat}</div>', unsafe_allow_html=True)
            if cols[i].checkbox("V", value=on, key=f"f_{cat}", label_visibility="collapsed"):
                new_cats.append(cat)
        st.session_state.selected_cats = new_cats

    df = st.session_state.data.copy()
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        disp = df[(df['Date'] == f_date) & (df['Category'].isin(st.session_state.selected_cats))]
        if search: disp = disp[disp['Subject'].str.contains(search, na=False) | disp['Target'].str.contains(search, na=False)]
        disp = disp.sort_values(by="Time")
    else: disp = pd.DataFrame()

    st.markdown(f"### 📍 {f_date.strftime('%Y년 %m월 %d일')} 일정")

    if disp.empty: st.info("일정이 없습니다.")
    else:
        for idx, row in disp.iterrows():
            c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
            
            # 드롭다운 제목
            title = f"⏰ {row['Time']} | [{row['Category']}] {row['Subject']}"
            
            with st.expander(title):
                if st.session_state.edit_id == row['ID']:
                    with st.form(key=f"edit_{row['ID']}"):
                        # 수정 폼
                        u_sub = st.text_input("회의명", row['Subject'])
                        u_time = st.text_input("시간", row['Time'])
                        u_tar = st.text_input("대상", row['Target'])
                        u_loc = st.text_input("장소", row['Location'])
                        u_pur = st.text_area("목적", row['Purpose'])
                        u_act = st.text_area("대응", row['ActionPlan'])
                        u_mem = st.text_area("메모", row['Memo'])
                        if st.form_submit_button("완료"):
                            st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], ['Subject', 'Time', 'Target', 'Location', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = [u_sub, u_time, u_tar, u_loc, u_pur, u_act, u_mem, datetime.now().strftime("%H:%M")]
                            st.session_state.edit_id = None
                            st.rerun()
                else:
                    # [상세 정보 카드: 파스텔 테두리와 배경]
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
                        
                        <div class="memo-section">📌 <b>유의사항(Memo)</b><br>{row['Memo']}<br><small style="color:#777;">ℹ️ {row['ExtraInfo']}</small></div>
                        {f'<div style="text-align:right; font-size:0.75rem; color:#aaa; margin-top:10px;">updated. {row["Updated"]}</div>' if row['Updated'] else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📝 수정하기", key=f"btn_{row['ID']}"):
                        st.session_state.edit_id = row['ID']
                        st.rerun()
