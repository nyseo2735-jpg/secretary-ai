import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 카테고리별 고유 키 컬러 설정 (회장님 전용 컬러맵) ---
COLOR_MAP = {
    "국회": {"bg": "#FFF0F0", "border": "#FF4B4B", "text": "#D64545"},      # 레드
    "정부기관": {"bg": "#F0F7FF", "border": "#007AFF", "text": "#0056B3"},   # 블루
    "대한수의사회": {"bg": "#F2FBF2", "border": "#28A745", "text": "#1E7E34"}, # 그린
    "수의과대학": {"bg": "#F9F0FF", "border": "#AF52DE", "text": "#7A379D"}, # 퍼플
    "언론사": {"bg": "#FFF7F0", "border": "#FF9500", "text": "#CC7600"},   # 오렌지
    "기업": {"bg": "#F0F2F5", "border": "#34495E", "text": "#2C3E50"},      # 네이비
    "유관단체": {"bg": "#F0FFFF", "border": "#00A3BF", "text": "#007B8F"},   # 청록
    "기타": {"bg": "#F8F9FA", "border": "#8E8E93", "text": "#636366"}       # 그레이
}

CATEGORIES = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

# CSS 주입: 카드 디자인 및 폰트
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * {{ font-family: 'Pretendard', sans-serif; }}
    .main {{ background-color: #f8f9fa; }}
    
    /* 일정 카드 스타일 */
    .schedule-container {{
        background-color: white; padding: 25px; border-radius: 15px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        position: relative; border-left: 10px solid;
    }}
    .time-badge {{
        font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; display: block;
    }}
    .subject-title {{
        font-size: 1.5rem; font-weight: 800; margin-bottom: 15px; display: block;
    }}
    .info-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.95rem;
    }}
    .memo-section {{
        background-color: #FFF9C4; padding: 12px; border-radius: 8px;
        border-right: 4px solid #FBC02D; margin-top: 15px; font-size: 0.9rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로드 및 상태 관리 ---
if 'data' not in st.session_state:
    # 샘플 데이터 1개 포함 (오늘 날짜)
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.session_state.data = pd.DataFrame([
        {"ID": "1", "Date": today_str, "Time": "14:00", "Category": "국회", "Subject": "수의사법 개정안 공청회", 
         "Location": "국회 본관 316호", "VIPs": "김의원 (보건복지위)", "Purpose": "법안 중요성 피력", 
         "ActionPlan": "사무처 정무팀 대동", "Status": "확정", "ExtraInfo": "의원실: 504호 / 차량등록 완료",
         "Companion": "부회장 외 1명", "Staff": "이비서, 박기사", "Memo": "신분증 지참 필수", "Updated": ""}
    ])

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- 4. 사이드바 (KVMA 회장님 일정) ---
st.sidebar.markdown("# 🏢 KVMA 회장님 일정")
menu = st.sidebar.radio("메뉴 이동", ["📅 회장님 일정 보기", "✍️ 신규 일정 등록"])

# --- 5. [신규 일정 등록] 관리자 페이지 ---
if menu == "✍️ 신규 일정 등록":
    st.header("✍️ 신규 일정 등록")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜 선택")
            time_val = st.time_input("시작 시간")
            category = st.selectbox("카테고리", CATEGORIES)
        with col2:
            subject = st.text_input("핵심 안건")
            location = st.text_input("장소")
            vips = st.text_input("주요 VIP")

        extra_info = ""
        if category == "국회":
            room = st.text_input("의원실 번호 / 보좌관 연락처")
            car = st.text_input("국회 등록 차량 번호")
            extra_info = f"의원실/연락처: {room} | 차량: {car}"
        elif category == "정부기관":
            g_loc = st.text_input("방문위치 (동/층) / 담당 공무원")
            g_car = st.text_input("청사 등록 차량 번호")
            extra_info = f"위치/담당: {g_loc} | 차량: {g_car}"

        col_s1, col_s2 = st.columns(2)
        companion = col_s1.text_area("회장님 외 동행인")
        staff = col_s2.text_area("사무처 수행직원")
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 (유의사항)")

        if st.form_submit_button("일정 저장 및 보고"):
            new_row = {
                "ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": category,
                "Subject": subject, "Location": location, "VIPs": vips, "Purpose": purpose,
                "ActionPlan": action, "Status": "확정", "ExtraInfo": extra_info,
                "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("저장되었습니다.")

# --- 6. [📅 회장님 일정 보기] 메인 대시보드 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    # [상단 필터 섹션]
    with st.expander("🔍 검색 및 필터 옵션", expanded=False):
        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        search_txt = f_col1.text_input("회의명/VIP 검색")
        # 카테고리 필터 (고유 색상 적용 표시)
        search_cat = f_col2.multiselect("카테고리 선택", CATEGORIES, default=CATEGORIES)
        filter_date = f_col3.date_input("날짜 이동", value=datetime.now())

    # 데이터 정리
    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    today = filter_date
    
    # 필터링 적용
    display_df = df[df['Date'] == today]
    if search_txt:
        display_df = display_df[display_df['Subject'].str.contains(search_txt) | display_df['VIPs'].str.contains(search_txt)]
    display_df = display_df[display_df['Category'].isin(search_cat)]
    display_df = display_df.sort_values(by="Time")

    st.markdown(f"### 📍 {today.strftime('%Y년 %m월 %d일')} 일정 요약")

    if display_df.empty:
        st.info("오늘 등록된 일정이 없습니다.")
    else:
        for idx, row in display_df.iterrows():
            c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
            
            # [수정 모드 확인]
            if st.session_state.edit_id == row['ID']:
                with st.container():
                    st.markdown(f"#### 🛠️ 일정 수정 중: {row['Subject']}")
                    with st.form(key=f"form_{row['ID']}"):
                        u_sub = st.text_input("회의명", row['Subject'])
                        u_time = st.text_input("시간", row['Time'])
                        u_loc = st.text_input("장소", row['Location'])
                        u_vips = st.text_input("대상", row['VIPs'])
                        u_purpose = st.text_area("목적", row['Purpose'])
                        u_action = st.text_area("대응", row['ActionPlan'])
                        u_memo = st.text_area("메모", row['Memo'])
                        
                        col_btn1, col_btn2 = st.columns(2)
                        if col_btn1.form_submit_button("✅ 수정 완료"):
                            st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], 
                                ['Subject', 'Time', 'Location', 'VIPs', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = \
                                [u_sub, u_time, u_loc, u_vips, u_purpose, u_action, u_memo, datetime.now().strftime("%m/%d %H:%M")]
                            st.session_state.edit_id = None
                            st.rerun()
                        if col_btn2.form_submit_button("❌ 취소"):
                            st.session_state.edit_id = None
                            st.rerun()
            else:
                # [일정 카드 보기 모드]
                st.markdown(f"""
                <div class="schedule-container" style="border-left-color: {c['border']}; background-color: {c['bg']};">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span class="time-badge" style="color: {c['text']};">⏰ {row['Time']} | {row['Category']}</span>
                            <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
                        </div>
                    </div>
                    <div class="info-grid">
                        <div><b>📍 장소:</b> {row['Location']}</div>
                        <div><b>👤 대상:</b> {row['VIPs']}</div>
                        <div><b>👥 동행:</b> {row['Companion']}</div>
                        <div><b>👔 수행:</b> {row['Staff']}</div>
                    </div>
                    <div style="margin-top:15px; border-top: 1px solid #ddd; padding-top:10px;">
                        <b>🎯 회의 목적:</b> {row['Purpose']}<br>
                        <b>📋 대응 방향:</b> {row['ActionPlan']}<br>
                        <small style="color:#777;">{row['ExtraInfo']}</small>
                    </div>
                    <div class="memo-section">📌 <b>유의사항:</b><br>{row['Memo']}</div>
                    {f'<div class="updated-tag" style="text-align:right; font-size:0.7rem; color:#aaa; margin-top:5px;">updated. {row["Updated"]}</div>' if row['Updated'] else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # 수정 버튼을 우측 상단에 배치하기 위한 버튼 열
                btn_col1, btn_col2 = st.columns([9, 1])
                if btn_col2.button("📝 수정", key=f"btn_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
