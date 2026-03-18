import streamlit as st
import pandas as pd
from datetime import datetime
import time
import html

# --- 1. 카테고리 컬러맵 ---
COLOR_MAP = {
    "국회": {"bg": "#FFF5F6", "soft": "#FDECEF", "line": "#D84C57", "text": "#B4232C"},
    "정부기관": {"bg": "#F4F9FF", "soft": "#EAF4FF", "line": "#3B82F6", "text": "#1D4ED8"},
    "대한수의사회": {"bg": "#F4FBF5", "soft": "#EAF8EC", "line": "#2E9F5B", "text": "#207547"},
    "수의과대학": {"bg": "#FBF6FD", "soft": "#F3EAFB", "line": "#A855F7", "text": "#7E22CE"},
    "언론사": {"bg": "#FFF8F1", "soft": "#FFF0DE", "line": "#F59E0B", "text": "#C56A00"},
    "기업": {"bg": "#F8FAFC", "soft": "#EEF2F6", "line": "#64748B", "text": "#334155"},
    "유관단체": {"bg": "#F2FCFD", "soft": "#E3F7F9", "line": "#14B8A6", "text": "#0F8F82"},
    "기타": {"bg": "#FAFAFA", "soft": "#F2F2F2", "line": "#9CA3AF", "text": "#4B5563"}
}
CATEGORIES = list(COLOR_MAP.keys())

# --- 2. 페이지 설정 ---
st.set_page_config(page_title="KVMA 회장님 일정", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.main {
    background: #ffffff;
}

/* 상단 제목 */
.page-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 1rem;
}

/* 필터 박스 */
.filter-shell {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 16px 16px 10px 16px;
    box-shadow: 0 4px 18px rgba(20, 24, 40, 0.04);
    margin-bottom: 18px;
}

.filter-caption {
    font-size: 0.92rem;
    color: #7A7F8C;
    margin: 0 0 10px 2px;
    font-weight: 500;
}

/* 멀티셀렉트 내부의 빨간 태그 제거 */
div[data-baseweb="tag"] {
    display: none !important;
}

/* 멀티셀렉트 입력창 여백 */
div[data-baseweb="select"] > div {
    min-height: 54px !important;
    border-radius: 14px !important;
}

/* 일반 인풋도 둥글게 */
.stTextInput input, .stDateInput input {
    border-radius: 14px !important;
}

/* 선택된 카테고리 컬러 칩 */
.cat-chip-wrap {
    margin-top: 10px;
    margin-left: 2px;
}
.cat-chip {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    border: 1px solid;
    margin: 0 8px 8px 0;
}

/* 섹션 제목 */
.section-title {
    font-size: 2rem;
    font-weight: 800;
    color: #2F3142;
    margin: 10px 0 18px 0;
}

/* 일정 카드 */
.schedule-card {
    position: relative;
    border-radius: 24px;
    padding: 22px 24px 18px 26px;
    margin-bottom: 18px;
    border: 1px solid #ECEEF3;
    box-shadow: 0 8px 26px rgba(16, 24, 40, 0.05);
    overflow: hidden;
}

.schedule-card::before {
    content: "";
    position: absolute;
    left: 0;
    top: 18px;
    bottom: 18px;
    width: 12px;
    border-radius: 0 10px 10px 0;
    background: var(--line-color);
}

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
}

.left-block {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.meta-row {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-color);
}

.category-pill {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    border: 1px solid var(--line-color);
    background: var(--soft-color);
    color: var(--text-color);
    margin-left: 8px;
    vertical-align: middle;
}

.subject-row {
    font-size: 1.65rem;
    font-weight: 800;
    color: #232634;
    line-height: 1.28;
    margin-top: 2px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 18px;
}

.info-box {
    background: rgba(255,255,255,0.70);
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 16px;
    padding: 14px 14px 12px 14px;
}

.info-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

.info-value {
    font-size: 1rem;
    font-weight: 600;
    color: #232634;
    line-height: 1.45;
}

.plan-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 12px;
}

.plan-box {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 16px;
    padding: 14px 16px;
}

.plan-title {
    font-size: 0.82rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 6px;
}

.plan-value {
    font-size: 1rem;
    font-weight: 600;
    color: #232634;
    line-height: 1.55;
}

.memo-note {
    margin-top: 14px;
    background: #FFFBEA;
    border: 1px solid #F8E3A3;
    border-left: 8px solid #F5C84B;
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
}

.memo-title {
    font-size: 0.95rem;
    font-weight: 800;
    color: #7A5A00;
    margin-bottom: 4px;
}

.memo-text {
    font-size: 0.95rem;
    color: #4B5563;
    line-height: 1.5;
}

.updated-text {
    margin-top: 10px;
    text-align: right;
    font-size: 0.75rem;
    color: #9CA3AF;
}

/* 수정 버튼 쪽 */
.edit-btn-wrap {
    margin-top: -6px;
    margin-bottom: 10px;
}

/* 모바일 대응 */
@media (max-width: 1100px) {
    .info-grid {
        grid-template-columns: 1fr;
    }
    .plan-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# --- 3. 상태 관리 ---
if "data" not in st.session_state:
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

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "selected_cats" not in st.session_state:
    st.session_state.selected_cats = CATEGORIES.copy()

# --- 4. 사이드바 ---
st.sidebar.markdown("# 🏢 KVMA 비서실")
menu = st.sidebar.radio("메뉴", ["📅 일정 보기", "✍️ 일정 등록"])

# --- 5. 등록 화면 ---
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
    st.markdown('<div class="page-title">📒 KVMA 회장님 일정</div>', unsafe_allow_html=True)

    st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
    st.markdown('<div class="filter-caption">검색어 · 카테고리 · 날짜로 빠르게 찾기</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2.3, 1.8, 1.1, 0.5])

    search = c1.text_input(
        "검색",
        placeholder="회의명 / 대상 / 장소 검색",
        label_visibility="collapsed",
        key="search_box"
    )

    selected_cats = c2.multiselect(
        "카테고리 선택",
        options=CATEGORIES,
        default=st.session_state.selected_cats,
        placeholder="카테고리 선택",
        label_visibility="collapsed",
        key="category_filter",
        width="stretch"
    )

    f_date = c3.date_input(
        "날짜 선택",
        value=datetime.now(),
        label_visibility="collapsed",
        key="date_filter"
    )

    reset_clicked = c4.button("전체", use_container_width=True)

    if reset_clicked:
        st.session_state.selected_cats = CATEGORIES.copy()
        st.session_state.category_filter = CATEGORIES.copy()
        st.rerun()

    st.session_state.selected_cats = selected_cats if selected_cats else []

    chip_html = '<div class="cat-chip-wrap">'
    if st.session_state.selected_cats:
        for cat in st.session_state.selected_cats:
            ci = COLOR_MAP.get(cat, COLOR_MAP["기타"])
            chip_html += (
                f'<span class="cat-chip" '
                f'style="background:{ci["soft"]}; border-color:{ci["line"]}; color:{ci["text"]};">'
                f'{html.escape(cat)}</span>'
            )
    else:
        chip_html += '<span style="font-size:0.85rem;color:#9AA0AC;">선택된 카테고리가 없습니다.</span>'
    chip_html += '</div>'

    st.markdown(chip_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 필터
    df = st.session_state.data.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    disp = df[df["Date"] == f_date]

    if st.session_state.selected_cats:
        disp = disp[disp["Category"].isin(st.session_state.selected_cats)]
    else:
        disp = disp.iloc[0:0]

    if search:
        q = str(search).strip()
        disp = disp[
            disp["Subject"].fillna("").str.contains(q, case=False, na=False)
            | disp["Target"].fillna("").str.contains(q, case=False, na=False)
            | disp["Location"].fillna("").str.contains(q, case=False, na=False)
        ]

    disp = disp.sort_values(by="Time")

    st.markdown(
        f'<div class="section-title">📍 {f_date.strftime("%m월 %d일")} 일정</div>',
        unsafe_allow_html=True
    )

    if disp.empty:
        st.info("조건에 맞는 일정이 없습니다.")

    for _, row in disp.iterrows():
        ci = COLOR_MAP.get(row["Category"], COLOR_MAP["기타"])

        if st.session_state.edit_id == row["ID"]:
            with st.form(key=f"ed_{row['ID']}"):
                u_sub = st.text_input("회의명", row["Subject"])
                cc1, cc2, cc3 = st.columns(3)
                u_time = cc1.text_input("시간", row["Time"])
                u_tar = cc2.text_input("대상", row["Target"])
                u_loc = cc3.text_input("장소", row["Location"])
                u_purp = st.text_area("목적", row["Purpose"], height=80)
                u_act = st.text_area("대응", row["ActionPlan"], height=80)
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
            subject = html.escape(str(row.get("Subject", "")))
            time_txt = html.escape(str(row.get("Time", "")))
            category = html.escape(str(row.get("Category", "")))
            location = html.escape(str(row.get("Location", "")))
            target = html.escape(str(row.get("Target", "")))
            companion = html.escape(str(row.get("Companion", "")))
            staff = html.escape(str(row.get("Staff", "")))
            purpose = html.escape(str(row.get("Purpose", "")))
            action_plan = html.escape(str(row.get("ActionPlan", "")))
            memo = html.escape(str(row.get("Memo", "")))
            extra = html.escape(str(row.get("ExtraInfo", "")))
            updated = html.escape(str(row.get("Updated", "")))

            st.markdown(f"""
            <div class="schedule-card"
                 style="background:{ci['bg']};
                        --line-color:{ci['line']};
                        --text-color:{ci['text']};
                        --soft-color:{ci['soft']};">
                <div class="card-top">
                    <div class="left-block">
                        <div class="meta-row">
                            ⏰ {time_txt}
                            <span class="category-pill">{category}</span>
                        </div>
                        <div class="subject-row">{subject}</div>
                    </div>
                </div>

                <div class="info-grid">
                    <div class="info-box">
                        <div class="info-label">장소</div>
                        <div class="info-value">📍 {location if location else "-"}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">대상</div>
                        <div class="info-value">👤 {target if target else "-"}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">동행 / 수행</div>
                        <div class="info-value">👥 {companion if companion else "-"} / {staff if staff else "-"}</div>
                    </div>
                </div>

                <div class="plan-grid">
                    <div class="plan-box">
                        <div class="plan-title">🎯 목적</div>
                        <div class="plan-value">{purpose if purpose else "-"}</div>
                    </div>
                    <div class="plan-box">
                        <div class="plan-title">📋 대응 방향</div>
                        <div class="plan-value">{action_plan if action_plan else "-"}</div>
                    </div>
                </div>

                <div class="memo-note">
                    <div class="memo-title">📌 Memo</div>
                    <div class="memo-text">{memo if memo else "-"}</div>
                    <div class="memo-text" style="margin-top:6px;">ℹ️ {extra if extra else "-"}</div>
                </div>

                {f'<div class="updated-text">updated. {updated}</div>' if updated else ''}
            </div>
            """, unsafe_allow_html=True)

            _, btn_col = st.columns([19, 1])
            with btn_col:
                if st.button("📝", key=f"edit_{row['ID']}"):
                    st.session_state.edit_id = row["ID"]
                    st.rerun()
