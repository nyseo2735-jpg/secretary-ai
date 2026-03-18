import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# --- 1. 페이지 테마 및 스타일 설정 (파스텔톤 디자인) ---
st.set_page_config(page_title="KVMA 비서실", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .main { background-color: #fcfdfe; }
    
    /* 일정 카드 공통 스타일 */
    .schedule-card {
        padding: 20px; border-radius: 15px; margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05); border-left: 12px solid;
        background-color: white;
    }
    
    /* 카테고리별 파스텔 색상 정의 */
    .cat-국회 { border-left-color: #FFB3BA; color: #D64545; } /* 파스텔 레드 */
    .cat-정부기관 { border-left-color: #BAE1FF; color: #3D7EA6; } /* 파스텔 블루 */
    .cat-대한수의사회 { border-left-color: #BAFFC9; color: #2D8A3E; } /* 파스텔 그린 */
    .cat-기업 { border-left-color: #FFFFBA; color: #8A8A2D; } /* 파스텔 옐로우 */
    
    /* 포스트잇 메모 스타일 */
    .memo-box {
        background-color: #FFF9C4; border-radius: 5px; padding: 10px;
        border-right: 5px solid #FBC02D; font-size: 0.9rem; margin-top: 10px;
    }
    
    .updated-tag { font-size: 0.8rem; color: #999; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 초기화 ---
CATEGORIES = ["국회", "정부기관", "대한수의사회", "유관단체", "수의과대학", "언론사", "기업", "기타"]

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "ID", "Date", "Time", "Category", "Subject", "Location", "VIPs", "Purpose", 
        "ActionPlan", "Status", "ExtraInfo", "Companion", "Staff", "Memo", "Updated"
    ])

# --- 3. 사이드바 (KVMA 회장님 일정) ---
st.sidebar.markdown("# 🏢 KVMA 회장님 일정")
menu = st.sidebar.radio("메뉴 이동", ["📅 전체 일정 보기", "✍️ 신규 일정 등록"])

# --- 4. [신규 일정 등록] 관리자 페이지 ---
if menu == "✍️ 신규 일정 등록":
    st.header("✍️ 신규 일정 등록")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜 선택")
            time = st.time_input("시작 시간")
            category = st.selectbox("카테고리", CATEGORIES)
            status = st.selectbox("상태", ["확정", "검토", "취소"])
        with col2:
            subject = st.text_input("핵심 안건")
            location = st.text_input("장소 (상세 주소)")
            vips = st.text_input("주요 VIP (이름/직함)")

        # 카테고리별 추가 정보
        extra_info = ""
        if category == "국회":
            col_k1, col_k2 = st.columns(2)
            room = col_k1.text_input("의원실(면회실) 번호")
            contact = col_k2.text_input("보좌관/행정관 이름 및 연락처")
            car = st.text_input("국회 등록 차량 번호")
            extra_info = f"의원실: {room} / 연락처: {contact} / 차량: {car}"
        elif category == "정부기관":
            col_g1, col_g2 = st.columns(2)
            g_loc = col_g1.text_input("방문위치 (동/층)")
            g_person = col_g2.text_input("방문부서 및 공무원 이름")
            g_car = st.text_input("청사 등록 차량 번호")
            extra_info = f"위치: {g_loc} / 담당: {g_person} / 차량: {g_car}"

        # 공통 상세 정보
        col_s1, col_s2 = st.columns(2)
        companion = col_s1.text_area("회장님 외 동행인 (이름/소속)")
        staff = col_s2.text_area("사무처 수행직원 정보")
        
        purpose = st.text_area("회의 목적")
        action = st.text_area("사무처 대응 방향")
        memo = st.text_area("📋 포스트잇 (유의사항/메모)")

        if st.form_submit_button("일정 저장"):
            new_id = datetime.now().strftime("%Y%m%d%H%M%S")
            new_row = {
                "ID": new_id, "Date": str(date), "Time": str(time), "Category": category,
                "Subject": subject, "Location": location, "VIPs": vips, "Purpose": purpose,
                "ActionPlan": action, "Status": status, "ExtraInfo": extra_info,
                "Companion": companion, "Staff": staff, "Memo": memo, "Updated": ""
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("일정이 성공적으로 등록되었습니다.")

# --- 5. [전체 일정 보기] 메인 대시보드 ---
elif menu == "📅 전체 일정 보기":
    st.markdown(f"## 📒 KVMA 회장님 일정")
    
    # [상세 검색 섹션]
    with st.expander("🔍 상세 검색 및 필터", expanded=False):
        s_col1, s_col2 = st.columns(2)
        search_txt = s_col1.text_input("회의명 또는 VIP 검색")
        search_cat = s_col2.multiselect("카테고리 필터", CATEGORIES, default=CATEGORIES)

    # [주간/월간 보기 선택]
    view_type = st.radio("조회 방식", ["주간별 보기", "월간별 보기"], horizontal=True)
    
    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Date', 'Time']) # 시간순 정렬

    if view_type == "주간별 보기":
        # 주차 계산을 위한 옵션
        df['Week'] = df['Date'].dt.isocalendar().week
        weeks = df['Date'].dt.strftime('%Y년 %m월 주차').unique() # 단순화된 표시
        sel_week = st.selectbox("주차 선택", sorted(weeks, reverse=True))
        # 필터링 로직 (실제 운영 시에는 시작/종료일 기준으로 정교화 가능)
        display_df = df
        
    else: # 월간별 보기
        months = sorted(df['Date'].dt.strftime('%Y-%m').unique(), reverse=True)
        sel_month = st.selectbox("월 선택", months if months else [datetime.now().strftime('%Y-%m')])
        display_df = df[df['Date'].dt.strftime('%Y-%m') == sel_month]

    # 검색어 필터링 적용
    if search_txt:
        display_df = display_df[display_df['Subject'].str.contains(search_txt) | display_df['VIPs'].str.contains(search_txt)]
    display_df = display_df[display_df['Category'].isin(search_cat)]

    # [일정 출력]
    if display_df.empty:
        st.info("해당하는 일정이 없습니다.")
    else:
        for idx, row in display_df.iterrows():
            cat_color = "#D64545" if row['Category'] == "국회" else "#3D7EA6" if row['Category'] == "정부기관" else "#2D8A3E" if row['Category'] == "대한수의사회" else "#555"
            
            with st.expander(f"⏰ {row['Time'][:5]} | [{row['Category']}] {row['Subject']}"):
                # 수정 기능
                with st.form(key=f"edit_{row['ID']}"):
                    st.markdown(f"<h3 style='color:{cat_color}'>{row['Subject']}</h3>", unsafe_allow_html=True)
                    e_col1, e_col2 = st.columns(2)
                    new_sub = e_col1.text_input("회의명", row['Subject'])
                    new_loc = e_col2.text_input("장소", row['Location'])
                    new_purpose = st.text_area("목적", row['Purpose'])
                    new_action = st.text_area("대응방향", row['ActionPlan'])
                    new_memo = st.text_area("📝 메모 (포스트잇)", row['Memo'])
                    
                    if row['Updated']:
                        st.markdown(f"<span class='updated-tag'>updated. {row['Updated']}</span>", unsafe_allow_html=True)
                    
                    if st.form_submit_button("정보 수정하기"):
                        st.session_state.data.loc[idx, 'Subject'] = new_sub
                        st.session_state.data.loc[idx, 'Location'] = new_loc
                        st.session_state.data.loc[idx, 'Purpose'] = new_purpose
                        st.session_state.data.loc[idx, 'ActionPlan'] = new_action
                        st.session_state.data.loc[idx, 'Memo'] = new_memo
                        st.session_state.data.loc[idx, 'Updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.rerun()

                # 정보 표시
                st.markdown(f"""
                <div class="schedule-card cat-{row['Category']}">
                    <b>👤 VIP:</b> {row['VIPs']} | <b>👥 동행:</b> {row['Companion']} | <b>👔 수행:</b> {row['Staff']}<br>
                    <b>ℹ️ 상세정보:</b> {row['ExtraInfo']}
                    <div class="memo-box">📌 <b>유의사항:</b><br>{row['Memo']}</div>
                </div>
                """, unsafe_allow_html=True)
