import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 카테고리별 고유 키 컬러 및 아이콘 설정 ---
COLOR_MAP = {
    "🔴 국회": {"bg": "#FFF0F0", "border": "#FF4B4B", "text": "#D64545", "raw": "국회"},
    "🔵 정부기관": {"bg": "#F0F7FF", "border": "#007AFF", "text": "#0056B3", "raw": "정부기관"},
    "🟢 대한수의사회": {"bg": "#F2FBF2", "border": "#28A745", "text": "#1E7E34", "raw": "대한수의사회"},
    "🟣 수의과대학": {"bg": "#F9F0FF", "border": "#AF52DE", "text": "#7A379D", "raw": "수의과대학"},
    "🟠 언론사": {"bg": "#FFF7F0", "border": "#FF9500", "text": "#CC7600", "raw": "언론사"},
    "🌑 기업": {"bg": "#F0F2F5", "border": "#34495E", "text": "#2C3E50", "raw": "기업"},
    "💎 유관단체": {"bg": "#F0FFFF", "border": "#00A3BF", "text": "#007B8F", "raw": "유관단체"},
    "⚪ 기타": {"bg": "#F8F9FA", "border": "#8E8E93", "text": "#636366", "raw": "기타"}
}

# 필터용 카테고리 리스트 (이모지 포함)
CATEGORIES_WITH_EMOJI = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * {{ font-family: 'Pretendard', sans-serif; }}
    .main {{ background-color: #f8f9fa; }}
    
    .schedule-container {{
        background-color: white; padding: 25px; border-radius: 15px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative; border-left: 12px solid;
    }}
    .time-badge {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; display: block; }}
    .subject-title {{ font-size: 1.5rem; font-weight: 800; margin-bottom: 12px; display: block; }}
    .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.95rem; }}
    .memo-section {{
        background-color: #FFF9C4; padding: 12px; border-radius: 8px;
        border-right: 5px solid #FBC02D; margin-top: 15px; font-size: 0.9rem;
    }}
    /* 필터 내 텍스트 색상 커스텀은 제한적이나 이모지로 구분감 제공 */
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로드 및 상태 관리 ---
if 'data' not in st.session_state:
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.session_state.data = pd.DataFrame([
        {"ID": "1", "Date": today_str, "Time": "14:00", "Category": "🔴 국회", "Subject": "수의사법 개정안 관련 면담", 
         "Location": "국회 의원회관", "Target": "김의원 (보건복지위)", "Purpose": "법안 통과 협조 요청", 
         "ActionPlan": "정책국장 대동 및 자료 준비", "Status": "확정", 
         "ExtraInfo": "회의장소(세부): 504호 / 보좌관: 박철수, 연락처: 010-1234-5678 | 등록 차량 번호: 12가 3456",
         "Companion": "부회장, 정책국장", "Staff": "이비서, 박기사", "Memo": "정문 면회실 접수 필요", "Updated": ""}
    ])

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- 4. 사이드바 ---
st.sidebar.markdown("# 🏢 KVMA 회장님 일정")
menu = st.sidebar.radio("메뉴 이동", ["📅 회장님 일정 보기", "✍️ 신규 일정 등록"])

# --- 5. [신규 일정 등록] (항목 명칭 통일) ---
if menu == "✍️ 신규 일정 등록":
    st.header("✍️ 신규 일정 등록")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜 선택")
            time_val = st.time_input("시작 시간")
            category = st.selectbox("카테고리 선택", CATEGORIES_WITH_EMOJI)
        with col2:
            subject = st.text_input("핵심 안건 (회의명)")
            location = st.text_input("장소")
            target = st.text_input("만나는 대상 (이름/직함)")

        extra_info = ""
        if "국회" in category:
            col_k1, col_k2 = st.columns(2)
            room_info = col_k1.text_input("회의장소(세부), 보좌관/비서 이름, 연락처")
            car_info = col_k2.text_input("등록 차량 번호")
            extra_info = f"세부/연락처: {room_info} | 차량: {car_info}"
        elif "정부기관" in category:
            col_g1, col_g2 = st.columns(2)
            g_loc = col_g1.text_input("방문위치 (동/층) / 담당 공무원")
            g_car = col_g2.text_input("등록 차량 번호")
            extra_info = f"위치/담당: {g_loc} | 차량: {g_car}"

        col_s1, col_s2 = st.columns(2)
        companion = col_s1.text_area("회장님 외 동행인 (이름/소속)")
        staff = col_s2.text_area("사무처 수행직원")
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 (유의사항)")

        if st.form_submit_button("일정 저장 및 보고"):
            new_row = {
                "ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": category,
                "Subject": subject, "Location": location, "Target": target, "Purpose": purpose,
                "ActionPlan": action, "Status": "확정", "ExtraInfo": extra_info,
                "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("새 일정이 등록되었습니다.")

# --- 6. [📅 회장님 일정 보기] (수정 항목 및 필터 반영) ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    # [상단 필터 섹션 - 명칭 수정 및 컬러 이모지 반영]
    with st.expander("🔍 검색 및 필터 옵션", expanded=False):
        f_col1, f_col2, f_col3 = st.columns([2, 3, 1])
        search_txt = f_col1.text_input("회의명/대상 검색")
        search_cat = f_col2.multiselect("카테고리 선택 (고유 컬러)", CATEGORIES_WITH_EMOJI, default=CATEGORIES_WITH_EMOJI)
        filter_date = f_col3.date_input("날짜 이동", value=datetime.now())

    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    # 필터링 적용
    display_df = df[df['Date'] == filter_date]
    if search_txt:
        display_df = display_df[display_df['Subject'].str.contains(search_txt) | display_df['Target'].str.contains(search_txt)]
    display_df = display_df[display_df['Category'].isin(search_cat)]
    display_df = display_df.sort_values(by="Time")

    st.markdown(f"### 📍 {filter_date.strftime('%Y년 %m월 %d일')} 일정")

    if display_df.empty:
        st.info("해당 조건의 일정이 없습니다.")
    else:
        for idx, row in display_df.iterrows():
            c = COLOR_MAP.get(row['Category'], COLOR_MAP["⚪ 기타"])
            
            # [수정 모드 - 명칭 통일]
            if st.session_state.edit_id == row['ID']:
                with st.form(key=f"edit_form_{row['ID']}"):
                    st.markdown(f"#### 🛠️ 일정 정보 수정")
                    u_sub = st.text_input("핵심 안건 (회의명)", row['Subject'])
                    u_time = st.text_input("시간", row['Time'])
                    u_loc = st.text_input("장소", row['Location'])
                    u_target = st.text_input("만나는 대상 (이름/직함)", row['Target'])
                    
                    if "국회" in row['Category']:
                        u_extra = st.text_input("회의장소(세부), 보좌관/비서 이름, 연락처 / 등록 차량 번호", row['ExtraInfo'])
                    else:
                        u_extra = st.text_input("추가 정보", row['ExtraInfo'])
                        
                    u_companion = st.text_area("회장님 외 동행인", row['Companion'])
                    u_staff = st.text_area("사무처 수행직원", row['Staff'])
                    u_purpose = st.text_area("회의 목적", row['Purpose'])
                    u_action = st.text_area("사무처 대응 방향", row['ActionPlan'])
                    u_memo = st.text_area("📋 포스트잇 (유의사항)", row['Memo'])
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("✅ 수정 완료"):
                        st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], 
                            ['Subject', 'Time', 'Location', 'Target', 'ExtraInfo', 'Companion', 'Staff', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = \
                            [u_sub, u_time, u_loc, u_target, u_extra, u_companion, u_staff, u_purpose, u_action, u_memo, datetime.now().strftime("%m/%d %H:%M")]
                        st.session_state.edit_id = None
                        st.rerun()
                    if c2.form_submit_button("❌ 취소"):
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                # [일정 카드 모드 - 명칭 통일]
                st.markdown(f"""
                <div class="schedule-container" style="border-left-color: {c['border']}; background-color: {c['bg']};">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span class="time-badge" style="color: {c['text']};">⏰ {row['Time']} | {row['Category']}</span>
                            <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
                        </div>
                    </div>
                    <div class="info-grid">
                        <div><b>📍 장소:</b> {row['Location']}</div>
                        <div><b>👤 대상:</b> {row['Target']}</div>
                        <div><b>👥 동행:</b> {row['Companion']}</div>
                        <div><b>👔 수행:</b> {row['Staff']}</div>
                    </div>
                    <div style="margin-top:12px; border-top: 1px solid #ddd; padding-top:10px; font-size:0.95rem;">
                        <b>🎯 회의 목적:</b> {row['Purpose']}<br>
                        <b>📋 대응 방향:</b> {row['ActionPlan']}<br>
                        <small style="color:#666; display:block; margin-top:5px;">ℹ️ {row['ExtraInfo']}</small>
                    </div>
                    <div class="memo-section">📌 <b>유의사항:</b><br>{row['Memo']}</div>
                    {f'<div style="text-align:right; font-size:0.75rem; color:#999; margin-top:8px;">updated. {row["Updated"]}</div>' if row['Updated'] else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # 수정 버튼 (우측 상단 배치 느낌)
                b1, b2 = st.columns([9.2, 0.8])
                if b2.button("📝 수정", key=f"edit_btn_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
