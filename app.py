import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 페이지 설정 및 디자인 (대기업 회장실 스타일) ---
st.set_page_config(page_title="비서실 스케줄 엔그램", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { background-color: #004a99; color: white; border-radius: 5px; }
    .schedule-card {
        background-color: white; padding: 20px; border-radius: 10px;
        border-left: 10px solid #004a99; margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .cat-국회 { border-left-color: #ff4b4b; }
    .cat-정부기관 { border-left-color: #7d3cff; }
    .cat-기업 { border-left-color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사이드바: 관리자 입력 및 내비게이션 ---
st.sidebar.title("🏢 비서실 제어센터")
menu = st.sidebar.radio("메뉴 선택", ["📅 전체 일정 보기", "✍️ 신규 일정 등록", "🔍 상세 검색"])

# 샘플 데이터 (실제로는 구글 시트와 연동 가능)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Date", "Time", "Category", "Subject", "Location", "VIPs", "Purpose", "ActionPlan", "Status"])

# --- 3. [신규 일정 등록] 관리자 페이지 ---
if menu == "✍️ 신규 일정 등록":
    st.header("✍️ 회장님 신규 일정 등록")
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("날짜 선택")
            time = st.text_input("시간 (예: 14:00 - 15:30)")
            category = st.selectbox("카테고리", ["국회", "정부기관", "유관단체", "수의과대학", "언론사", "기업", "기타"])
        with col2:
            subject = st.text_input("핵심 안건")
            location = st.text_input("장소")
            vips = st.text_input("상대방 성함/직함")
        
        purpose = st.text_area("회의 목적 (왜 하는가?)")
        action = st.text_area("사무처 대응 방향 (어떻게 대응할 것인가?)")
        status = st.selectbox("상태", ["확정", "검토", "취소"])
        
        if st.form_submit_button("일정 저장 및 보고"):
            new_data = {"Date": str(date), "Time": time, "Category": category, "Subject": subject, 
                        "Location": location, "VIPs": vips, "Purpose": purpose, "ActionPlan": action, "Status": status}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_data])], ignore_index=True)
            st.success("일정이 등록되었습니다.")

# --- 4. [전체 일정 보기] 메인 대시보드 ---
elif menu == "📅 전체 일정 보기":
    st.header("📅 회장님 주요 일정")
    
    # 상단 드롭다운 필터 (년/월/주차)
    df = st.session_state.data
    col1, col2, col3 = st.columns(3)
    with col1:
        years = sorted(df['Date'].str[:4].unique()) if not df.empty else [2024]
        sel_year = st.selectbox("연도 선택", years)
    with col2:
        sel_month = st.selectbox("월 선택", [f"{i:02d}" for i in range(1, 13)])
    with col3:
        sel_day = st.selectbox("일 선택 (전체는 'All')", ["All"] + [f"{i:02d}" for i in range(1, 32)])

    # 필터링 로직
    filtered_df = df[df['Date'].str.contains(f"{sel_year}-{sel_month}")]
    if sel_day != "All":
        filtered_df = filtered_df[filtered_df['Date'].str.endswith(sel_day)]

    # 일정 출력 (카드 레이아웃)
    if filtered_df.empty:
        st.info("해당 기간에 등록된 일정이 없습니다.")
    else:
        for _, row in filtered_df.iterrows():
            cat_class = f"cat-{row['Category']}" if row['Category'] in ["국회", "정부기관", "기업"] else ""
            st.markdown(f"""
                <div class="schedule-card {cat_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1.2rem; font-weight: bold; color: #004a99;">[{row['Category']}] {row['Subject']}</span>
                        <span style="color: #666;">{row['Date']} | {row['Time']}</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <b>📍 장소:</b> {row['Location']} | <b>👤 대상:</b> {row['VIPs']} | <b>🚩 상태:</b> {row['Status']}
                    </div>
                    <hr>
                    <div style="background: #f0f2f6; padding: 10px; border-radius: 5px;">
                        <b>🎯 회의 목적:</b><br>{row['Purpose']}<br><br>
                        <b>📋 사무처 대응:</b><br>{row['ActionPlan']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- 5. [상세 검색] 기능 ---
elif menu == "🔍 상세 검색":
    st.header("🔍 지능형 일정 검색")
    search_query = st.text_input("회의명, 장소, 또는 VIP 이름을 입력하세요.")
    search_cat = st.multiselect("카테고리 필터", ["국회", "정부기관", "유관단체", "기업"])
    
    if search_query or search_cat:
        results = st.session_state.data
        if search_query:
            results = results[results.apply(lambda row: search_query in str(row.values), axis=1)]
        if search_cat:
            results = results[results['Category'].isin(search_cat)]
        st.write(f"총 {len(results)}건의 결과가 검색되었습니다.")
        st.table(results)
