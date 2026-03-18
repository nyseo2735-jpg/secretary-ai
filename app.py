import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 (압축형 디자인용) ---
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

# --- 2. 페이지 설정 및 고압축 디자인 (CSS) ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #ffffff; }

    /* [붉은색 제거] Multiselect 기본 스타일 초기화 */
    div[data-baseweb="tag"] { background-color: #eee !important; border: 1px solid #ddd !important; color: #333 !important; }

    /* 일정 카드 압축형 스타일 */
    .schedule-container {
        padding: 15px 20px; /* 패딩 대폭 축소 */
        border-radius: 15px; 
        margin-bottom: 12px; /* 간격 축소 */
        border: 2px solid;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .time-cat { font-size: 0.95rem; font-weight: 700; }
    .subject-title { font-size: 1.25rem; font-weight: 800; display: block; margin-top: -2px; }
    
    /* 정보를 가로로 배치하여 길이 단축 */
    .info-row { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 10px; font-size: 0.9rem; margin-top: 5px; color: #444; }
    
    /* 목적 및 대응 방향 압축 */
    .strategy-row { 
        display: grid; grid-template-columns: 1fr 1fr; gap: 15px; 
        margin-top: 10px; padding-top: 8px; border-top: 1px solid #eee; font-size: 0.88rem;
    }
    
    /* 메모 섹션 슬림화 */
    .memo-slim {
        background-color: #FFFDE7; padding: 8px 12px; border-radius: 8px;
        border-left: 4px solid #FFD54F; margin-top: 10px; font-size: 0.85rem; color: #555;
    }
    
    .updated-text { font-size: 0.7rem; color: #aaa; text-align: right; margin-top: 3px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 및 상태 관리 ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"ID": "1", "Date": datetime.now().strftime("%Y-%m-%d"), "Time": "14:00", "Category": "국회", "Subject": "수의사법 개정안 관련 면담", 
         "Location": "국회 의원회관 504호", "Target": "김의원 (보건복지위)", "Purpose": "법안 통과 협조 요청", 
         "ActionPlan": "정책국장 대동 및 자료 준비", "Status": "확정", 
         "ExtraInfo": "보좌관: 박철수 | 차량: 12가 3456", "Companion": "부회장, 정책국장", "Staff": "이비서, 박기사", "Memo": "정문 면회실 신분증 지참", "Updated": ""}
    ])
if 'edit_id' not in st.session_state: st.session_state.edit_id = None
if 'selected_cats' not in st.session_state: st.session_state.selected_cats = CATEGORIES.copy()

# --- 4. 사이드바 ---
st.sidebar.markdown("# 🏢 KVMA 비서실")
menu = st.sidebar.radio("메뉴", ["📅 일정 보기", "✍️ 일정 등록"])

# --- 5. [신규 등록] (화면 생략 - 이전과 동일하게 유지) ---
if menu == "✍️ 일정 등록":
    st.header("✍️ 일정 등록")
    with st.form("reg_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        date = c1.date_input("날짜")
        time_val = c1.time_input("시간")
        cat = c1.selectbox("카테고리", CATEGORIES)
        sub = c2.text_input("회의명")
        loc = c2.text_input("장소")
        tar = c2.text_input("만나는 대상")
        
        extra = st.text_input("상세정보(방문지/보좌관/차량번호 등)")
        comp = st.text_input("회장님 외 동행인")
        stf = st.text_input("사무처 수행직원")
        purp = st.text_area("회의 목적", height=70)
        act = st.text_area("대응 방향", height=70)
        mem = st.text_input("유의사항(Memo)")

        if st.form_submit_button("저장"):
            new_row = {"ID": str(time.time()), "Date": str(date), "Time": str(time_val)[:5], "Category": cat, "Subject": sub, "Location": loc, "Target": tar, "Purpose": purp, "ActionPlan": act, "Status": "확정", "ExtraInfo": extra, "Companion": comp, "Staff": stf, "Memo": mem, "Updated": ""}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("등록 완료")

# --- 6. [📅 일정 보기] 압축 레이아웃 적용 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")
    
    with st.expander("🔍 필터 및 검색", expanded=False):
        f_col1, f_col2 = st.columns([3, 1])
        search = f_col1.text_input("회의명/대상 검색")
        f_date = f_col2.date_input("날짜 선택", value=datetime.now())
        
        # 카테고리 필터 (압축형 배지)
        st.write("카테고리 선택")
        cat_cols = st.columns(len(CATEGORIES))
        new_cats = []
        for i, cat in enumerate(CATEGORIES):
            c_info = COLOR_MAP[cat]
            is_on = cat in st.session_state.selected_cats
            style = f'background:{c_info["bg"]}; border:1px solid {c_info["border"]}; color:{c_info["text"]};' if is_on else 'background:#fff; border:1px solid #eee; color:#ccc;'
            st.markdown(f'<div style="{style} padding:2px 8px; border-radius:12px; text-align:center; font-size:0.75rem;">{cat}</div>', unsafe_allow_html=True)
            if cat_cols[i].checkbox("V", value=is_on, key=f"c_{cat}", label_visibility="collapsed"):
                new_cats.append(cat)
        st.session_state.selected_cats = new_cats

    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    disp = df[(df['Date'] == f_date) & (df['Category'].isin(st.session_state.selected_cats))]
    if search: disp = disp[disp['Subject'].str.contains(search) | disp['Target'].str.contains(search)]
    disp = disp.sort_values(by="Time")

    st.markdown(f"### 📍 {f_date.strftime('%m월 %d일')} 일정")

    for idx, row in disp.iterrows():
        c = COLOR_MAP.get(row['Category'], COLOR_MAP["기타"])
        
        if st.session_state.edit_id == row['ID']:
            with st.form(key=f"ed_{row['ID']}"):
                # 수정 폼은 그대로 유지하되 콤팩트하게 배치
                u_sub = st.text_input("회의명", row['Subject'])
                c1, c2, c3 = st.columns(3)
                u_time = c1.text_input("시간", row['Time'])
                u_tar = c2.text_input("대상", row['Target'])
                u_loc = c3.text_input("장소", row['Location'])
                u_purp = st.text_area("목적", row['Purpose'], height=60)
                u_act = st.text_area("대응", row['ActionPlan'], height=60)
                u_mem = st.text_input("메모", row['Memo'])
                if st.form_submit_button("수정 완료"):
                    st.session_state.data.loc[st.session_state.data['ID'] == row['ID'], ['Subject', 'Time', 'Target', 'Location', 'Purpose', 'ActionPlan', 'Memo', 'Updated']] = [u_sub, u_time, u_tar, u_loc, u_purp, u_act, u_mem, datetime.now().strftime("%H:%M")]
                    st.session_state.edit_id = None
                    st.rerun()
        else:
            # [고압축 카드 레이아웃]
            st.markdown(f"""
            <div class="schedule-container" style="border-color: {c['border']}; background-color: {c['bg']};">
                <div class="card-header">
                    <div>
                        <span class="time-cat" style="color: {c['text']};">⏰ {row['Time']} | {row['Category']}</span>
                        <span class="subject-title" style="color: {c['text']};">{row['Subject']}</span>
                    </div>
                </div>
                <div class="info-row">
                    <div><b>📍 장소:</b> {row['Location']}</div>
                    <div><b>👤 대상:</b> {row['Target']}</div>
                    <div><b>👥 동행/수행:</b> {row['Companion']} / {row['Staff']}</div>
                </div>
                <div class="strategy-row">
                    <div><b>🎯 목적:</b> {row['Purpose']}</div>
                    <div><b>📋 대응:</b> {row['ActionPlan']}</div>
                </div>
                <div class="memo-slim">📌 <b>Memo:</b> {row['Memo']} <br> <small>ℹ️ {row['ExtraInfo']}</small></div>
                {f'<div class="updated-text">updated. {row["Updated"]}</div>' if row['Updated'] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # 수정 버튼 우측 하단 배치
            _, ed_col = st.columns([19, 1])
            if ed_col.button("📝", key=f"e_{row['ID']}"):
                st.session_state.edit_id = row['ID']
                st.rerun()
