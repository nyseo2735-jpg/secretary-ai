import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (테두리 및 폰트용) ---
COLOR_MAP = {
    "국회": {"color": "#D64545", "bg": "#FFF0F0"},      # 레드
    "정부기관": {"color": "#3D7EA6", "bg": "#F0F7FF"},   # 블루
    "대한수의사회": {"color": "#2D8A3E", "bg": "#F2FBF2"}, # 그린
    "수의과대학": {"color": "#7A379D", "bg": "#F9F0FF"}, # 퍼플
    "언론사": {"color": "#E64A19", "bg": "#FFF7F0"},   # 오렌지
    "기업": {"color": "#455A64", "bg": "#F0F2F5"},      # 네이비/그레이
    "유관단체": {"color": "#0097A7", "bg": "#F0FFFF"},   # 청록
    "기타": {"color": "#757575", "bg": "#F8F9FA"}       # 회색
}

CATEGORIES = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 및 디자인 (CSS) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

# 강한 빨간색 테마를 무력화하고 파스텔톤으로 강제 변경하는 CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * {{ font-family: 'Pretendard', sans-serif; }}
    
    /* 1. 배경색 흰색 고정 */
    .main {{ background-color: #ffffff; }}

    /* 2. 문제의 빨간색 상자 제거 및 커스텀 스타일링 */
    /* Multiselect 태그 내부의 붉은 배경을 흰색/연한 회색으로 강제 변경 */
    div[data-baseweb="tag"] {{
        background-color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 20px !important;
        padding: 2px 8px !important;
    }}
    /* 태그 안의 X 아이콘 색상 변경 */
    div[data-baseweb="tag"] span {{
        color: #666 !important;
    }}
    
    /* 3. 일정 카드: 테두리 선과 폰트 컬러만 고유색 적용 */
    .schedule-container {{
        padding: 25px; 
        border-radius: 20px;
        margin-bottom: 25px; 
        border: 2px solid; /* 테두리 강조 */
        background-color: white; /* 카드 배경은 흰색으로 깔끔하게 */
        box-shadow: 4px 4px 15px rgba(0,0,0,0.03);
    }}
    
    .time-badge {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 5px; display: block; }}
    .subject-title {{ font-size: 1.7rem; font-weight: 800; margin-bottom: 15px; display: block; }}
    
    .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 1rem; color: #333; }}
    
    /* 포스트잇 메모 */
    .memo-section {{
        background-color: #FFFDE7; padding: 15px; border-radius: 12px;
        border: 1px dashed #FFD54F; margin-top: 20px; font-size: 0.95rem;
    }}

    /* 버튼 스타일 조정 */
    .stButton>button {{
        border-radius: 20px; border: 1px solid #eee; background-color: white; color: #888;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로드 및 상태 관리 ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"ID": "1", "Date": datetime.now().strftime("%Y-%m-%d"), "Time": "14:00", "Category": "국회", "Subject": "수의사법 개정안 관련 면담", 
         "Location": "국회 의원회관", "Target": "김의원 (보건복지위)", "Purpose": "법안 통과 협조 요청", 
         "ActionPlan": "정책국장 대동 및 자료 준비", "Status": "확정", 
         "ExtraInfo": "회의장소(세부): 504호 / 보좌관: 박철수 | 등록 차량 번호: 12가 3456",
         "Companion": "부회장, 정책국장", "Staff": "이비서, 박기사", "Memo": "정문 면회실 접수 필요", "Updated": ""}
    ])

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# --- 4. 사이드바 ---
st.sidebar.markdown("# 🏢 KVMA 회장님 일정")
menu = st.sidebar.radio("메뉴 이동", ["📅 회장님 일정 보기", "✍️ 신규 일정 등록"])

# --- 5. [신규 일정 등록] ---
if menu == "✍️ 신규 일정 등록":
    st.header("✍️ 신규 일정 등록")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜 선택")
            time_val = st.time_input("시작 시간")
            category = st.selectbox("카테고리 선택", CATEGORIES)
        with col2:
            subject = st.text_input("핵심 안건 (회의명)")
            location = st.text_input("장소")
            target = st.text_input("만나는 대상 (이름/직함)")

        extra_info = ""
        if category == "국회":
            col_k1, col_k2 = st.columns(2)
            room_info = col_k1.text_input("회의장소(세부), 보좌관/비서 이름, 연락처")
            car_info = col_k2.text_input("등록 차량 번호")
            extra_info = f"세부/연락처: {room_info} | 차량: {car_info}"
        elif category == "정부기관":
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

# --- 6. [📅 회장님 일정 보기] ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    with st.expander("🔍 검색 및 필터 옵션", expanded=False):
        f_col1, f_col2, f_col3 = st.columns([2, 3, 1])
        search_txt = f_col1.text_input("회의명/대상 검색")
        # 필터의 빨간색은 CSS에서 이미 무력화됨
        search_cat = f_col2.multiselect("카테고리 선택", CATEGORIES, default=CATEGORIES)
        filter_date = f_col3.date_input("날짜 이동", value=datetime.now())

    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
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
            c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
            
            if st.session_state.edit_id == row['ID']:
                with st.form(key=f"edit_form_{row['ID']}"):
                    st.markdown(f"#### 🛠️ 정보 수정")
                    e_sub = st.text_input("핵심 안건 (회의명)", row['Subject'])
                    e_time = st.text_input("시간", row['Time'])
                    e_target = st.text_input("만나는 대상", row['Target'])
                    e_loc = st.text_input("장소", row['Location'])
                    e_extra = st.text_input("세부정보 / 차량번호", row['ExtraInfo'])
                    e_purpose = st.text_area("회의 목적", row['Purpose'])
                    e_action = st.text_area("대응 방향", row['ActionPlan'])
                    e_memo = st.text_area("유의사항", row['Memo'])
                    
                    if st.form_submit_button("✅ 수정 완료"):
                        st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], 
                            ['Subject', 'Time', 'Target', 'Location', 'ExtraInfo', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = \
                            [e_sub, e_time, e_target, e_loc, e_extra, e_purpose, e_action, e_memo, datetime.now().strftime("%m/%d %H:%M")]
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                # [일정 카드 디자인: 요청하신 대로 테두리 선과 폰트만 동일 컬러 적용]
                st.markdown(f"""
                <div class="schedule-container" style="border-color: {c['color']}; background-color: {c['bg']};">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span class="time-badge" style="color: {c['color']};">⏰ {row['Time']} | {row['Category']}</span>
                            <span class="subject-title" style="color: {c['color']};">{row['Subject']}</span>
                        </div>
                        <div style="text-align: right;">
                             <span style="font-size: 0.8rem; color: #999;">{f'updated. {row["Updated"]}' if row['Updated'] else ''}</span>
                        </div>
                    </div>
                    <div class="info-grid">
                        <div><b>📍 장소:</b> {row['Location']}</div>
                        <div><b>👤 대상:</b> {row['Target']}</div>
                        <div><b>👥 동행:</b> {row['Companion']}</div>
                        <div><b>👔 수행:</b> {row['Staff']}</div>
                    </div>
                    <div style="margin-top:15px; border-top: 1px solid {c['color']}55; padding-top:12px;">
                        <b>🎯 회의 목적:</b> {row['Purpose']}<br>
                        <b>📋 대응 방향:</b> {row['ActionPlan']}<br>
                        <small style="color:#666; display:block; margin-top:5px;">ℹ️ {row['ExtraInfo']}</small>
                    </div>
                    <div class="memo-section">📌 <b>유의사항(Memo):</b><br>{row['Memo']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 수정 버튼
                col_e1, col_e2 = st.columns([9.4, 0.6])
                if col_e2.button("📝", key=f"edit_btn_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
