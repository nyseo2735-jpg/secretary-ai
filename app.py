import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (테두리 및 폰트용) ---
# 바탕은 아주 연하게, 테두리와 글자는 선명한 파스텔톤으로 설정
COLOR_MAP = {
    "국회": {"border": "#FFB3BA", "text": "#D64545", "bg": "#FFF9F9"},      # 연분홍/진분홍
    "정부기관": {"border": "#BAE1FF", "text": "#3D7EA6", "bg": "#F4Faff"},   # 연하늘/진파랑
    "대한수의사회": {"border": "#BAFFC9", "text": "#2D8A3E", "bg": "#F7FFF9"}, # 연연두/진초록
    "수의과대학": {"border": "#D1C4E9", "text": "#7A379D", "bg": "#FBF9FF"}, # 연보라/진보라
    "언론사": {"border": "#FFCCBC", "text": "#E64A19", "bg": "#FFFBF9"},   # 연주황/진주황
    "기업": {"border": "#CFD8DC", "text": "#455A64", "bg": "#F8F9FA"},      # 연회청/진회청
    "유관단체": {"border": "#B2EBF2", "text": "#0097A7", "bg": "#F2FDFF"},   # 연청록/진청록
    "기타": {"border": "#EEEEEE", "text": "#757575", "bg": "#FFFFFF"}       # 연회색/진회색
}

CATEGORIES = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 및 디자인 (CSS) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * {{ font-family: 'Pretendard', sans-serif; }}
    
    /* 배경 및 기본 톤 */
    .main {{ background-color: #ffffff; }}
    
    /* 검색 필터(Multiselect)의 붉은 배경 제거 및 아웃라인 스타일링 */
    div[data-baseweb="tag"] {{
        background-color: #f0f2f6 !important;
        border: 1px solid #dfe1e6 !important;
        color: #333333 !important;
        border-radius: 15px !important;
    }}
    div[data-baseweb="tag"] span {{
        color: #333333 !important;
    }}
    
    /* 일정 카드: 라운드 박스 + 아웃라인 스타일 */
    .schedule-container {{
        padding: 25px; 
        border-radius: 18px;
        margin-bottom: 25px; 
        border: 2px solid; /* 테두리 강조 */
        background-color: white;
        transition: all 0.3s ease;
    }}
    .time-badge {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 5px; display: block; }}
    .subject-title {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 15px; display: block; }}
    
    .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 1rem; color: #444; }}
    
    /* 포스트잇 메모 섹션 */
    .memo-section {{
        background-color: #FFFCF0; padding: 15px; border-radius: 10px;
        border: 1px dashed #FFD54F; margin-top: 20px; font-size: 0.95rem;
    }}
    
    /* 수정 버튼 디자인 */
    .stButton>button {{
        border-radius: 20px;
        border: 1px solid #ddd;
        background-color: white;
        color: #666;
        font-size: 0.8rem;
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
                # [일정 카드: 파스텔 아웃라인 디자인]
                st.markdown(f"""
                <div class="schedule-container" style="border-color: {c['border']}; background-color: {c['bg']};">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span class="time-badge" style="color: {c['text']};">⏰ {row['Time']} | {row['Category']}</span>
                            <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
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
                    <div style="margin-top:15px; border-top: 1px solid {c['border']}; padding-top:12px;">
                        <b>🎯 회의 목적:</b> {row['Purpose']}<br>
                        <b>📋 대응 방향:</b> {row['ActionPlan']}<br>
                        <small style="color:#666; display:block; margin-top:5px;">ℹ️ {row['ExtraInfo']}</small>
                    </div>
                    <div class="memo-section">📌 <b>유의사항(Memo):</b><br>{row['Memo']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 수정 버튼을 카드 바로 아래에 배치
                edit_col1, edit_col2 = st.columns([9.3, 0.7])
                if edit_col2.button("📝 수정", key=f"btn_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
