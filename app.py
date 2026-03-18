import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (필터 및 카드용) ---
COLOR_MAP = {
    "국회": {"bg": "#FFEBEE", "border": "#FFCDD2", "text": "#C62828"},      # 파스텔 레드
    "정부기관": {"bg": "#E3F2FD", "border": "#BBDEFB", "text": "#1565C0"},   # 파스텔 블루
    "대한수의사회": {"bg": "#E8F5E9", "border": "#C8E6C9", "text": "#2E7D32"}, # 파스텔 그린
    "수의과대학": {"bg": "#F3E5F5", "border": "#E1BEE7", "text": "#6A1B9A"}, # 파스텔 퍼플
    "언론사": {"bg": "#FFF3E0", "border": "#FFE0B2", "text": "#E65100"},   # 파스텔 오렌지
    "기업": {"bg": "#ECEFF1", "border": "#CFD8DC", "text": "#37474F"},      # 파스텔 그레이/블루
    "유관단체": {"bg": "#E0F7FA", "border": "#B2EBF2", "text": "#00838F"},   # 파스텔 민트
    "기타": {"bg": "#F5F5F5", "border": "#E0E0E0", "text": "#616161"}       # 파스텔 그레이
}

CATEGORIES = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 및 디자인 (강력한 CSS 오버라이드) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * {{ font-family: 'Pretendard', sans-serif; }}
    
    .main {{ background-color: #ffffff; }}

    /* [중요] 붉은색 상자 강제 박멸 CSS */
    div[data-baseweb="tag"] {{
        background-color: transparent !important; 
        border: 1px solid #ddd !important;
        color: #333 !important;
    }}
    
    /* 필터 버튼 스타일 */
    .filter-btn {{
        display: inline-block; padding: 6px 14px; border-radius: 20px;
        margin-right: 8px; margin-bottom: 8px; font-size: 0.9rem;
        cursor: pointer; border: 1px solid; font-weight: 500;
    }}

    /* 일정 카드: 테두리와 배경 모두 파스텔톤 적용 */
    .schedule-container {{
        padding: 25px; border-radius: 20px; margin-bottom: 25px; 
        border: 2px solid; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }}
    .time-badge {{ font-size: 1.1rem; font-weight: 700; margin-bottom: 5px; display: block; }}
    .subject-title {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 12px; display: block; }}
    .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 1rem; color: #444; }}
    
    .memo-section {{
        background-color: #FFFDE7; padding: 15px; border-radius: 12px;
        border: 1px dashed #FFD54F; margin-top: 20px; font-size: 0.95rem;
    }}
    
    /* 수정 버튼 우측 상단 정렬 */
    .edit-btn-container {{ text-align: right; }}
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

if 'selected_cats' not in st.session_state:
    st.session_state.selected_cats = CATEGORIES.copy()

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
    
    # [검색 필터 섹션 - 붉은색 제거 및 파스텔톤 버튼 적용]
    with st.expander("🔍 검색 및 필터 옵션", expanded=True):
        search_txt = st.text_input("회의명/만나는 대상 검색")
        
        st.write("카테고리 선택 (클릭하여 필터링)")
        cat_cols = st.columns(len(CATEGORIES))
        new_selected_cats = []
        for i, cat in enumerate(CATEGORIES):
            c = COLOR_MAP[cat]
            # 체크박스 형태지만 버튼처럼 보이게 파스텔톤 적용
            is_selected = cat in st.session_state.selected_cats
            if is_selected:
                # 선택된 상태: 파스텔 배경색 적용
                st.markdown(f'<div style="background-color:{c["bg"]}; border:1px solid {c["border"]}; color:{c["text"]}; padding:5px 10px; border-radius:15px; text-align:center; font-size:0.8rem; font-weight:bold;">{cat}</div>', unsafe_allow_html=True)
            else:
                # 해제된 상태: 무색 적용
                st.markdown(f'<div style="background-color:#fff; border:1px solid #eee; color:#ccc; padding:5px 10px; border-radius:15px; text-align:center; font-size:0.8rem;">{cat}</div>', unsafe_allow_html=True)
            
            if cat_cols[i].checkbox("선택", value=is_selected, key=f"cat_{cat}", label_visibility="collapsed"):
                new_selected_cats.append(cat)
        st.session_state.selected_cats = new_selected_cats
        
        filter_date = st.date_input("날짜 이동", value=datetime.now())

    # 데이터 필터링
    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    display_df = df[df['Date'] == filter_date]
    if search_txt:
        display_df = display_df[display_df['Subject'].str.contains(search_txt) | display_df['Target'].str.contains(search_txt)]
    display_df = display_df[display_df['Category'].isin(st.session_state.selected_cats)]
    display_df = display_df.sort_values(by="Time")

    st.markdown(f"### 📍 {filter_date.strftime('%Y년 %m월 %d일')} 일정")

    if display_df.empty:
        st.info("해당 조건의 일정이 없습니다.")
    else:
        for idx, row in display_df.iterrows():
            c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
            
            # [수정 모드]
            if st.session_state.edit_id == row['ID']:
                with st.form(key=f"edit_form_{row['ID']}"):
                    st.markdown(f"#### 🛠️ 일정 정보 수정")
                    # ... (수정 폼 항목 생략 - 이전과 동일)
                    u_sub = st.text_input("핵심 안건 (회의명)", row['Subject'])
                    u_time = st.text_input("시간", row['Time'])
                    u_target = st.text_input("만나는 대상", row['Target'])
                    u_loc = st.text_input("장소", row['Location'])
                    u_extra = st.text_input("세부정보 / 차량번호", row['ExtraInfo'])
                    u_purpose = st.text_area("회의 목적", row['Purpose'])
                    u_action = st.text_area("대응 방향", row['ActionPlan'])
                    u_memo = st.text_area("유의사항", row['Memo'])
                    
                    if st.form_submit_button("✅ 수정 완료"):
                        st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], 
                            ['Subject', 'Time', 'Target', 'Location', 'ExtraInfo', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = \
                            [u_sub, u_time, u_target, u_loc, u_extra, u_purpose, u_action, u_memo, datetime.now().strftime("%m/%d %H:%M")]
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                # [일정 카드: 회장님 요청 파스텔톤 완벽 적용]
                st.markdown(f"""
                <div class="schedule-container" style="border-color: {c['border']}; background-color: {c['bg']};">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span class="time-badge" style="color: {c['text']};">⏰ {row['Time']} | {row['Category']}</span>
                            <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
                        </div>
                        <div class="edit-btn-container">
                             <span style="font-size: 0.75rem; color: #999;">{f'updated. {row["Updated"]}' if row['Updated'] else ''}</span>
                        </div>
                    </div>
                    <div class="info-grid">
                        <div><b>📍 장소:</b> {row['Location']}</div>
                        <div><b>👤 대상:</b> {row['Target']}</div>
                        <div><b>👥 동행:</b> {row['Companion']}</div>
                        <div><b>👔 수행:</b> {row['Staff']}</div>
                    </div>
                    <div style="margin-top:15px; border-top: 1px solid {c['border']}; padding-top:12px; font-size:0.95rem;">
                        <b>🎯 회의 목적:</b> {row['Purpose']}<br>
                        <b>📋 대응 방향:</b> {row['ActionPlan']}<br>
                        <small style="color:#666; display:block; margin-top:5px;">ℹ️ {row['ExtraInfo']}</small>
                    </div>
                    <div class="memo-section">📌 <b>유의사항(Memo):</b><br>{row['Memo']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 수정 버튼을 카드 바로 밑에 아주 작게 배치
                col_e1, col_e2 = st.columns([9.5, 0.5])
                if col_e2.button("📝", key=f"btn_{row['ID']}"):
                    st.session_state.edit_id = row['ID']
                    st.rerun()
