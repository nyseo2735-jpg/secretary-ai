import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (현재 컬러톤 박제) ---
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

# --- 2. 페이지 설정 및 레이아웃 최적화 (CSS) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    
    /* 화면 배경 및 메인 너비 제한 (가로로 너무 길어지지 않게) */
    .main { background-color: #ffffff; }
    .block-container { max-width: 900px; padding-top: 2rem; }

    /* [붉은색 제거] 필터 태그 스타일 초기화 */
    div[data-baseweb="tag"] { background-color: #f0f2f6 !important; border: 1px solid #ddd !important; color: #333 !important; }

    /* 일정 카드: 초기 버전의 세로형 배치 + 현재의 파스텔 컬러 */
    .schedule-container {
        padding: 25px; 
        border-radius: 20px;
        margin-bottom: 25px; 
        border: 2px solid;
        background-color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    
    .time-badge { font-size: 1.1rem; font-weight: 700; margin-bottom: 5px; display: block; }
    .subject-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 15px; display: block; line-height: 1.3; }
    
    /* 정보 항목 세로 나열 (초기 스타일) */
    .info-item { margin-bottom: 8px; font-size: 1rem; color: #333; }
    .info-label { font-weight: 700; color: #555; margin-right: 8px; }
    
    /* 전략 박스 (목적/대응) */
    .strategy-box {
        margin-top: 15px; padding: 15px; border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .memo-section {
        background-color: #FFFDE7; padding: 15px; border-radius: 12px;
        border-left: 5px solid #FFD54F; margin-top: 20px; font-size: 0.95rem;
    }
    
    .updated-tag { font-size: 0.75rem; color: #aaa; text-align: right; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 및 상태 관리 ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"ID": "1", "Date": datetime.now().strftime("%Y-%m-%d"), "Time": "14:00", "Category": "국회", "Subject": "수의사법 개정안 관련 면담", 
         "Location": "국회 의원회관 504호", "Target": "김의원 (보건복지위)", "Purpose": "법안 통과 중요성 피력 및 협조 요청", 
         "ActionPlan": "정책국장 대동 및 핵심 요약 자료 배포", "Status": "확정", 
         "ExtraInfo": "보좌관: 박철수 | 등록 차량 번호: 12가 3456", "Companion": "부회장, 정책국장", "Staff": "이비서, 박기사", "Memo": "정문 면회실 신분증 지참 필수", "Updated": ""}
    ])
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
            date = st.date_input("날짜")
            time_val = st.time_input("시간")
            category = st.selectbox("카테고리", CATEGORIES)
        with col2:
            subject = st.text_input("회의명")
            location = st.text_input("장소")
            target = st.text_input("만나는 대상")

        extra = st.text_input("상세정보 (회의장소 세부/보좌관 연락처/차량번호)")
        companion = st.text_input("회장님 외 동행인")
        staff = st.text_input("사무처 수행직원")
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 (유의사항)")

        if st.form_submit_button("저장하기"):
            new_row = {"ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": category, "Subject": subject, "Location": location, "Target": target, "Purpose": purpose, "ActionPlan": action, "Status": "확정", "ExtraInfo": extra, "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("등록되었습니다.")

# --- 6. [📅 일정 보기] 초기 레이아웃 복원 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    # [필터 섹션]
    with st.expander("🔍 검색 및 필터", expanded=False):
        f1, f2 = st.columns([3, 1])
        search = f1.text_input("회의명/대상 검색")
        f_date = f2.date_input("날짜 선택", value=datetime.now())
        
        st.write("카테고리 선택")
        cat_cols = st.columns(len(CATEGORIES))
        new_cats = []
        for i, cat in enumerate(CATEGORIES):
            c_info = COLOR_MAP[cat]
            on = cat in st.session_state.selected_cats
            style = f'background:{c_info["bg"]}; border:1px solid {c_info["border"]}; color:{c_info["text"]};' if on else 'background:#fff; border:1px solid #eee; color:#ccc;'
            st.markdown(f'<div style="{style} padding:3px 10px; border-radius:15px; text-align:center; font-size:0.8rem; font-weight:bold;">{cat}</div>', unsafe_allow_html=True)
            if cat_cols[i].checkbox("V", value=on, key=f"filter_{cat}", label_visibility="collapsed"):
                new_cats.append(cat)
        st.session_state.selected_cats = new_cats

    # 필터링 및 정렬
    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    display_df = df[(df['Date'] == f_date) & (df['Category'].isin(st.session_state.selected_cats))]
    if search: display_df = display_df[display_df['Subject'].str.contains(search) | display_df['Target'].str.contains(search)]
    display_df = display_df.sort_values(by="Time")

    st.markdown(f"### 📍 {f_date.strftime('%Y년 %m월 %d일')} 일정")

    for idx, row in display_df.iterrows():
        c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
        
        if st.session_state.edit_id == row['ID']:
            with st.form(key=f"edit_{row['ID']}"):
                st.markdown(f"#### 🛠️ 일정 수정")
                # 수정 폼 생략 (이전 항목과 동일)
                u_sub = st.text_input("회의명", row['Subject'])
                u_time = st.text_input("시간", row['Time'])
                u_target = st.text_input("대상", row['Target'])
                u_loc = st.text_input("장소", row['Location'])
                u_pur = st.text_area("목적", row['Purpose'])
                u_act = st.text_area("대응", row['ActionPlan'])
                u_mem = st.text_area("메모", row['Memo'])
                if st.form_submit_button("완료"):
                    st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], ['Subject', 'Time', 'Target', 'Location', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = [u_sub, u_time, u_target, u_loc, u_pur, u_act, u_mem, datetime.now().strftime("%H:%M")]
                    st.session_state.edit_id = None
                    st.rerun()
        else:
            # [초기 레이아웃 + 현재 컬러]
            st.markdown(f"""
            <div class="schedule-container" style="border-color: {c['border']}; background-color: {c['bg']};">
                <span class="time-badge" style="color: {c['text']};">⏰ {row['Time']} | {row['Category']}</span>
                <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
                
                <div class="info-item"><span class="info-label">📍 장소:</span> {row['Location']}</div>
                <div class="info-item"><span class="info-label">👤 대상:</span> {row['Target']}</div>
                <div class="info-item"><span class="info-label">👥 동행:</span> {row['Companion']}</div>
                <div class="info-item"><span class="info-label">👔 수행:</span> {row['Staff']}</div>
                
                <div class="strategy-box" style="border-color: {c['border']}AA;">
                    <div class="info-item"><b>🎯 회의 목적:</b><br>{row['Purpose']}</div>
                    <div class="info-item" style="margin-top:10px;"><b>📋 사무처 대응:</b><br>{row['ActionPlan']}</div>
                    <small style="color:#666; display:block; margin-top:8px;">ℹ️ {row['ExtraInfo']}</small>
                </div>
                
                <div class="memo-section">📌 <b>유의사항(Memo):</b><br>{row['Memo']}</div>
                {f'<div class="updated-tag">updated. {row["Updated"]}</div>' if row['Updated'] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # 수정 버튼 (우측 하단)
            _, edit_col = st.columns([19, 1])
            if edit_col.button("📝", key=f"btn_{row['ID']}"):
                st.session_state.edit_id = row['ID']
                st.rerun()
