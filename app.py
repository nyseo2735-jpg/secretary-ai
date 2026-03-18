import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- 1. 고유 파스텔 컬러맵 ---
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

# --- 2. 페이지 설정 ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;700;800&display=swap');

    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #ffffff; }

    /* 검색/필터 영역 */
    .filter-wrap {
        background: #fafafa;
        border: 1px solid #f0f0f0;
        border-radius: 16px;
        padding: 14px 16px 8px 16px;
        margin-bottom: 12px;
    }

    .filter-subtitle {
        font-size: 0.83rem;
        color: #666;
        margin-bottom: 8px;
    }

    /* multiselect 태그 기본 빨간색 느낌 제거 */
    div[data-baseweb="tag"] {
        background-color: #f3f4f6 !important;
        border: 1px solid #e5e7eb !important;
        color: #374151 !important;
        border-radius: 999px !important;
    }

    /* 일정 카드 */
    .schedule-container {
        padding: 15px 20px;
        border-radius: 15px;
        margin-bottom: 12px;
        border: 2px solid;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .time-cat {
        font-size: 0.95rem;
        font-weight: 700;
    }

    .subject-title {
        font-size: 1.25rem;
        font-weight: 800;
        display: block;
        margin-top: -2px;
    }

    .info-row {
        display: grid;
        grid-template-columns: 1.2fr 1fr 1fr;
        gap: 10px;
        font-size: 0.9rem;
        margin-top: 5px;
        color: #444;
    }

    .strategy-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #eee;
        font-size: 0.88rem;
    }

    .memo-slim {
        background-color: #FFFDE7;
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #FFD54F;
        margin-top: 10px;
        font-size: 0.85rem;
        color: #555;
    }

    .updated-text {
        font-size: 0.7rem;
        color: #aaa;
        text-align: right;
        margin-top: 3px;
    }

    /* 선택된 카테고리 컬러 배지 */
    .cat-badge-wrap {
        margin-top: 2px;
        margin-bottom: 4px;
    }

    .cat-badge {
        display: inline-block;
        padding: 4px 10px;
        margin: 2px 6px 2px 0;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid;
    }

    /* 버튼 여백 */
    .stButton > button {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 및 상태 관리 ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {
            "ID": "1",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": "14:00",
            "Category": "국회",
            "Subject": "수의사법 개정안 관련 면담",
            "Location": "국회 의원회관 504호",
            "Target": "김의원 (보건복지위)",
            "Purpose": "법안 통과 협조 요청",
            "ActionPlan": "정책국장 대동 및 자료 준비",
            "Status": "확정",
            "ExtraInfo": "보좌관: 박철수 | 차량: 12가 3456",
            "Companion": "부회장, 정책국장",
            "Staff": "이비서, 박기사",
            "Memo": "정문 면회실 신분증 지참",
            "Updated": ""
        }
    ])

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

if 'selected_cats' not in st.session_state:
    st.session_state.selected_cats = CATEGORIES.copy()

# --- 4. 사이드바 ---
st.sidebar.markdown("# 🏢 KVMA 비서실")
menu = st.sidebar.radio("메뉴", ["📅 일정 보기", "✍️ 일정 등록"])

# --- 5. 일정 등록 ---
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
            new_row = {
                "ID": str(time.time()),
                "Date": str(date),
                "Time": str(time_val)[:5],
                "Category": cat,
                "Subject": sub,
                "Location": loc,
                "Target": tar,
                "Purpose": purp,
                "ActionPlan": act,
                "Status": "확정",
                "ExtraInfo": extra,
                "Companion": comp,
                "Staff": stf,
                "Memo": mem,
                "Updated": ""
            }
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("등록 완료")

# --- 6. 일정 보기 ---
else:
    st.markdown("## 📒 KVMA 회장님 일정")

    with st.container():
        st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="filter-subtitle">검색어 · 카테고리 · 날짜로 빠르게 찾기</div>', unsafe_allow_html=True)

        # 한 줄 검색 바처럼 구성
        f_col1, f_col2, f_col3, f_col4 = st.columns([2.4, 1.8, 1.2, 0.6])

        search = f_col1.text_input(
            "검색",
            placeholder="회의명 / 대상 / 장소 검색",
            label_visibility="collapsed",
            key="search_box"
        )

        selected_cats = f_col2.multiselect(
            "카테고리",
            options=CATEGORIES,
            default=st.session_state.selected_cats,
            placeholder="카테고리 선택",
            label_visibility="collapsed",
            key="category_filter"
        )

        f_date = f_col3.date_input(
            "날짜",
            value=datetime.now(),
            label_visibility="collapsed",
            key="date_filter"
        )

        reset_clicked = f_col4.button("전체", use_container_width=True)

        if reset_clicked:
            st.session_state.selected_cats = CATEGORIES.copy()
            st.session_state.category_filter = CATEGORIES.copy()
            st.rerun()

        if selected_cats:
            st.session_state.selected_cats = selected_cats
        else:
            st.session_state.selected_cats = []

        # 선택된 카테고리 컬러 배지
        badge_html = '<div class="cat-badge-wrap">'
        if st.session_state.selected_cats:
            for cat in st.session_state.selected_cats:
                c = COLOR_MAP.get(cat, COLOR_MAP["기타"])
                badge_html += (
                    f'<span class="cat-badge" '
                    f'style="background:{c["bg"]}; border-color:{c["border"]}; color:{c["text"]};">'
                    f'{cat}</span>'
                )
        else:
            badge_html += '<span style="font-size:0.82rem; color:#999;">선택된 카테고리가 없습니다.</span>'
        badge_html += '</div>'

        st.markdown(badge_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 필터링
    df = st.session_state.data.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    disp = df[df["Date"] == f_date]

    if st.session_state.selected_cats:
        disp = disp[disp["Category"].isin(st.session_state.selected_cats)]
    else:
        disp = disp.iloc[0:0]

    if search:
        search = str(search).strip()
        disp = disp[
            disp["Subject"].fillna("").str.contains(search, case=False, na=False) |
            disp["Target"].fillna("").str.contains(search, case=False, na=False) |
            disp["Location"].fillna("").str.contains(search, case=False, na=False)
        ]

    disp = disp.sort_values(by="Time")

    st.markdown(f"### 📍 {f_date.strftime('%m월 %d일')} 일정")

    if disp.empty:
        st.info("조건에 맞는 일정이 없습니다.")

    for idx, row in disp.iterrows():
        c = COLOR_MAP.get(row["Category"], COLOR_MAP["기타"])

        if st.session_state.edit_id == row["ID"]:
            with st.form(key=f"ed_{row['ID']}"):
                u_sub = st.text_input("회의명", row["Subject"])
                c1, c2, c3 = st.columns(3)
                u_time = c1.text_input("시간", row["Time"])
                u_tar = c2.text_input("대상", row["Target"])
                u_loc = c3.text_input("장소", row["Location"])
                u_purp = st.text_area("목적", row["Purpose"], height=60)
                u_act = st.text_area("대응", row["ActionPlan"], height=60)
                u_mem = st.text_input("메모", row["Memo"])

                if st.form_submit_button("수정 완료"):
                    st.session_state.data.loc[
                        st.session_state.data["ID"] == row["ID"],
                        ["Subject", "Time", "Target", "Location", "Purpose", "ActionPlan", "Memo", "Updated"]
                    ] = [
                        u_sub, u_time, u_tar, u_loc, u_purp, u_act, u_mem,
                        datetime.now().strftime("%H:%M")
                    ]
                    st.session_state.edit_id = None
                    st.rerun()

        else:
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
                {f'<div class="updated-text">updated. {row["Updated"]}</div>' if row["Updated"] else ''}
            </div>
            """, unsafe_allow_html=True)

            _, ed_col = st.columns([19, 1])
            if ed_col.button("📝", key=f"e_{row['ID']}"):
                st.session_state.edit_id = row["ID"]
                st.rerun()
