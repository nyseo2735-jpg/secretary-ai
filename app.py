import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="KVMA 회장님 일정",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. 기본 상수
# =========================================================
COLOR_MAP = {
    "국회": {"bg": "#FFF5F6", "soft": "#FDECEF", "line": "#D84C57", "text": "#B4232C"},
    "정부기관": {"bg": "#F4F9FF", "soft": "#EAF4FF", "line": "#3B82F6", "text": "#1D4ED8"},
    "대한수의사회": {"bg": "#F4FBF5", "soft": "#EAF8EC", "line": "#2E9F5B", "text": "#207547"},
    "수의과대학": {"bg": "#FBF6FD", "soft": "#F3EAFB", "line": "#A855F7", "text": "#7E22CE"},
    "언론사": {"bg": "#FFF8F1", "soft": "#FFF0DE", "line": "#F59E0B", "text": "#C56A00"},
    "기업": {"bg": "#F8FAFC", "soft": "#EEF2F6", "line": "#64748B", "text": "#334155"},
    "유관단체": {"bg": "#F2FCFD", "soft": "#E3F7F9", "line": "#14B8A6", "text": "#0F8F82"},
    "기타": {"bg": "#FAFAFA", "soft": "#F2F2F2", "line": "#9CA3AF", "text": "#4B5563"},
}
CATEGORIES = list(COLOR_MAP.keys())

STATUS_OPTIONS = ["확정", "보류", "완료", "취소"]
PRIORITY_OPTIONS = ["높음", "보통", "낮음"]

DATA_COLUMNS = [
    "ID",
    "Date",
    "Time",
    "Category",
    "Subject",
    "OrgName",
    "DetailPlace",
    "TargetDept",
    "TargetName",
    "TargetContact",
    "Companion",
    "Staff",
    "Purpose",
    "ActionPlan",
    "Memo",
    "Status",
    "Priority",
    "FollowOwner",
    "FollowTask",
    "FollowDue",
    "SharedNote",
    "Updated",
]

# =========================================================
# 3. CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2.8rem;
}

.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 0.25rem;
}

.sub-text {
    font-size: 0.98rem;
    color: #6B7280;
    margin-bottom: 1.1rem;
}

.panel {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 4px 18px rgba(20, 24, 40, 0.04);
    margin-bottom: 18px;
}

.section-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #2F3142;
    margin: 10px 0 14px 0;
}

.small-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #2F3142;
    margin: 6px 0 10px 0;
}

.helper-box {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 12px 14px;
    color: #475467;
    font-size: 0.92rem;
    margin-top: 10px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 18px;
    padding: 12px 14px;
}

.metric-label {
    font-size: 0.82rem;
    color: #6B7280;
    font-weight: 700;
}

.metric-value {
    font-size: 1.35rem;
    font-weight: 800;
    color: #2F3142;
}

.legend-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    margin: 0 8px 8px 0;
    border: 1px solid;
}

.day-card {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid #ECEEF3;
    box-shadow: 0 8px 24px rgba(16, 24, 40, 0.05);
    margin-bottom: 14px;
}

.day-card-inner {
    display: flex;
}

.day-card-accent {
    width: 12px;
    flex-shrink: 0;
}

.day-card-body {
    width: 100%;
    padding: 18px 20px 18px 20px;
}

.meta-row {
    font-size: 0.95rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.subject-row {
    font-size: 1.55rem;
    font-weight: 800;
    color: #232634;
    margin-bottom: 14px;
    line-height: 1.3;
}

.info-box {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 16px;
    padding: 13px 14px 11px 14px;
    min-height: 88px;
    margin-bottom: 10px;
}

.info-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 6px;
}

.info-value {
    font-size: 0.98rem;
    font-weight: 600;
    color: #232634;
    line-height: 1.48;
    white-space: pre-wrap;
}

.memo-box {
    background: #FFFBEA;
    border: 1px solid #F8E3A3;
    border-left: 8px solid #F5C84B;
    border-radius: 16px;
    padding: 14px 16px;
    margin-top: 4px;
}

.memo-title {
    font-size: 0.92rem;
    font-weight: 800;
    color: #7A5A00;
    margin-bottom: 6px;
}

.memo-text {
    font-size: 0.95rem;
    color: #4B5563;
    line-height: 1.55;
    white-space: pre-wrap;
}

.tag-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 800;
    border: 1px solid #D1D5DB;
    background: #ffffff;
    color: #475467;
    margin-left: 6px;
}

.month-day-box {
    border: 1px solid #E7EAF0;
    border-radius: 18px;
    background: #ffffff;
    padding: 10px;
    min-height: 180px;
    margin-bottom: 10px;
}

.month-day-head {
    font-size: 1.05rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 8px;
}

.month-event {
    border-radius: 12px;
    padding: 7px 8px;
    margin-bottom: 6px;
    font-size: 0.78rem;
    line-height: 1.35;
    border: 1px solid;
    background: #ffffff;
}

.week-day-box {
    border: 1px solid #E7EAF0;
    border-radius: 18px;
    background: #ffffff;
    padding: 10px;
    min-height: 320px;
}

.week-day-head {
    font-size: 1rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 8px;
}

div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stTextInput input,
.stDateInput input,
.stTimeInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea {
    border-radius: 14px !important;
}

div[data-testid="stForm"] {
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 18px 18px 10px 18px;
    background: #ffffff;
}

@media (max-width: 1100px) {
    .subject-row {
        font-size: 1.3rem;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4. 유틸
# =========================================================
def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATA_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[DATA_COLUMNS].copy()

def get_color(cat: str):
    return COLOR_MAP.get(cat, COLOR_MAP["기타"])

def to_date_safe(v):
    if pd.isna(v) or v == "":
        return None
    return pd.to_datetime(v, errors="coerce").date()

def safe_str(v):
    if pd.isna(v):
        return ""
    return str(v).strip()

def csv_download_bytes(df: pd.DataFrame) -> bytes:
    export_df = df.copy()
    return export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def init_sample_data():
    sample = pd.DataFrame([
        {
            "ID": "1",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": "14:00",
            "Category": "국회",
            "Subject": "수의사법 개정안 관련 면담",
            "OrgName": "국회 의원회관",
            "DetailPlace": "504호",
            "TargetDept": "보건복지위원회",
            "TargetName": "김의원",
            "TargetContact": "010-1234-5678",
            "Companion": "부회장, 정책국장",
            "Staff": "이비서, 박기사",
            "Purpose": "법안 통과 협조 요청",
            "ActionPlan": "정책국장 대동 및 자료 준비",
            "Memo": "정문 면회실 신분증 지참",
            "Status": "확정",
            "Priority": "높음",
            "FollowOwner": "정책국장",
            "FollowTask": "면담자료 최종본 준비, 참석자별 역할 정리",
            "FollowDue": datetime.now().strftime("%Y-%m-%d"),
            "SharedNote": "면담 후 결과 요약을 사무처 단톡방에 공유",
            "Updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    ])
    return ensure_columns(sample)

def get_filtered_df(df, selected_cat="전체", search_text="", status_filter="전체"):
    temp = df.copy()
    temp["Date"] = pd.to_datetime(temp["Date"], errors="coerce").dt.date

    if selected_cat != "전체":
        temp = temp[temp["Category"] == selected_cat]

    if status_filter != "전체":
        temp = temp[temp["Status"] == status_filter]

    if search_text:
        q = str(search_text).strip()
        mask = (
            temp["Subject"].fillna("").str.contains(q, case=False, na=False)
            | temp["OrgName"].fillna("").str.contains(q, case=False, na=False)
            | temp["DetailPlace"].fillna("").str.contains(q, case=False, na=False)
            | temp["TargetDept"].fillna("").str.contains(q, case=False, na=False)
            | temp["TargetName"].fillna("").str.contains(q, case=False, na=False)
            | temp["TargetContact"].fillna("").str.contains(q, case=False, na=False)
            | temp["FollowOwner"].fillna("").str.contains(q, case=False, na=False)
            | temp["FollowTask"].fillna("").str.contains(q, case=False, na=False)
        )
        temp = temp[mask]

    temp = temp.sort_values(by=["Date", "Time"])
    return temp

def week_dates_from_any_day(any_day: date):
    start = any_day - timedelta(days=(any_day.weekday() + 1) % 7)  # 일요일 시작
    return [start + timedelta(days=i) for i in range(7)]

def month_calendar_weeks(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    return cal.monthdatescalendar(year, month)

def save_record(record: dict, is_edit=False):
    record["Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if is_edit:
        st.session_state.data.loc[
            st.session_state.data["ID"] == record["ID"], DATA_COLUMNS[1:]
        ] = [record[col] for col in DATA_COLUMNS[1:]]
    else:
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([record])],
            ignore_index=True
        )
    st.session_state.data = ensure_columns(st.session_state.data)

def contact_text(row):
    parts = []
    if safe_str(row.get("TargetDept")):
        parts.append(f"부서: {row['TargetDept']}")
    if safe_str(row.get("TargetName")):
        parts.append(f"이름: {row['TargetName']}")
    if safe_str(row.get("TargetContact")):
        parts.append(f"연락처: {row['TargetContact']}")
    return " / ".join(parts) if parts else "-"

def show_flash():
    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = None

def category_color_text_html(text: str, cat: str):
    c = get_color(cat)
    return f"""
    <div class="month-event" style="color:{c['text']}; border-color:{c['line']}; background:{c['soft']};">
        {text}
    </div>
    """

def render_legend():
    html_parts = []
    for cat in CATEGORIES:
        c = get_color(cat)
        html_parts.append(
            f'<span class="legend-pill" style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">{cat}</span>'
        )
    st.markdown("".join(html_parts), unsafe_allow_html=True)

# =========================================================
# 5. 상태 초기화
# =========================================================
if "data" not in st.session_state:
    st.session_state.data = init_sample_data()
else:
    st.session_state.data = ensure_columns(st.session_state.data)

if "main_menu" not in st.session_state:
    st.session_state.main_menu = "📅 일정 보기"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "전체"

if "selected_status" not in st.session_state:
    st.session_state.selected_status = "전체"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "selected_event_id" not in st.session_state:
    st.session_state.selected_event_id = None

if "flash_message" not in st.session_state:
    st.session_state.flash_message = None

# =========================================================
# 6. 공통 렌더 함수
# =========================================================
def render_event_card(row):
    c = get_color(row["Category"])
    status_text = safe_str(row["Status"]) or "-"
    priority_text = safe_str(row["Priority"]) or "-"

    card_html = f"""
    <div class="day-card" style="background:{c["bg"]};">
        <div class="day-card-inner">
            <div class="day-card-accent" style="background:{c["line"]};"></div>
            <div class="day-card-body">
                <div class="meta-row" style="color:{c["text"]};">
                    ⏰ {safe_str(row["Time"])}
                    <span class="tag-pill" style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">{safe_str(row["Category"])}</span>
                    <span class="tag-pill">{status_text}</span>
                    <span class="tag-pill">우선순위 {priority_text}</span>
                </div>
                <div class="subject-row">{safe_str(row["Subject"])}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    info1, info2, info3 = st.columns(3)
    with info1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">방문기관명</div>
            <div class="info-value">🏢 {safe_str(row["OrgName"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">회의장소(세부)</div>
            <div class="info-value">📍 {safe_str(row["DetailPlace"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)

    with info2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">보좌관/비서/담당자 정보</div>
            <div class="info-value">👤 {contact_text(row)}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">회장님 외 동행인</div>
            <div class="info-value">👥 {safe_str(row["Companion"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)

    with info3:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">사무처 수행직원</div>
            <div class="info-value">🧾 {safe_str(row["Staff"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">최종 수정</div>
            <div class="info-value">🕒 {safe_str(row["Updated"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)

    plan1, plan2 = st.columns(2)
    with plan1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">회의 목적</div>
            <div class="info-value">{safe_str(row["Purpose"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">주 담당자</div>
            <div class="info-value">{safe_str(row["FollowOwner"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)

    with plan2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">대응 방향</div>
            <div class="info-value">{safe_str(row["ActionPlan"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">준비 완료기한</div>
            <div class="info-value">{safe_str(row["FollowDue"]) or "-"}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">후속/준비사항</div>
        <div class="info-value">{safe_str(row["FollowTask"]) or "-"}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">공유 메모</div>
        <div class="info-value">{safe_str(row["SharedNote"]) or "-"}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="memo-box">
        <div class="memo-title">📌 Memo</div>
        <div class="memo-text">{safe_str(row["Memo"]) or "-"}</div>
    </div>
    """, unsafe_allow_html=True)

def render_action_buttons(row):
    c1, c2, c3, c4 = st.columns([1, 1, 1, 6])

    if c1.button("수정", key=f"edit_{row['ID']}", use_container_width=True):
        st.session_state.edit_id = row["ID"]
        st.rerun()

    toggle_label = "일정 취소" if row["Status"] != "취소" else "취소 해제"
    toggle_next = "취소" if row["Status"] != "취소" else "확정"
    if c2.button(toggle_label, key=f"cancel_{row['ID']}", use_container_width=True):
        st.session_state.data.loc[
            st.session_state.data["ID"] == row["ID"], ["Status", "Updated"]
        ] = [toggle_next, datetime.now().strftime("%Y-%m-%d %H:%M")]
        st.session_state.flash_message = "상태가 변경되었습니다."
        st.rerun()

    if c3.button("삭제", key=f"delete_{row['ID']}", use_container_width=True):
        st.session_state.data = st.session_state.data[st.session_state.data["ID"] != row["ID"]].reset_index(drop=True)
        if st.session_state.selected_event_id == row["ID"]:
            st.session_state.selected_event_id = None
        if st.session_state.edit_id == row["ID"]:
            st.session_state.edit_id = None
        st.session_state.flash_message = "일정이 삭제되었습니다."
        st.rerun()

def render_form(mode="new", row_data=None):
    if row_data is None:
        row_data = {
            "ID": "",
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": "09:00",
            "Category": CATEGORIES[0],
            "Subject": "",
            "OrgName": "",
            "DetailPlace": "",
            "TargetDept": "",
            "TargetName": "",
            "TargetContact": "",
            "Companion": "",
            "Staff": "",
            "Purpose": "",
            "ActionPlan": "",
            "Memo": "",
            "Status": "확정",
            "Priority": "보통",
            "FollowOwner": "",
            "FollowTask": "",
            "FollowDue": "",
            "SharedNote": "",
            "Updated": "",
        }

    title = "✍️ 신규 일정 등록" if mode == "new" else "🛠️ 일정 수정"
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

    with st.form(f"form_{mode}", clear_on_submit=False):
        r1c1, r1c2, r1c3 = st.columns(3)
        input_date = r1c1.date_input("일정 날짜", value=to_date_safe(row_data["Date"]) or datetime.now().date())
        default_time = datetime.strptime(safe_str(row_data["Time"]) or "09:00", "%H:%M").time()
        input_time = r1c2.time_input("일정 시간", value=default_time)
        input_category = r1c3.selectbox(
            "카테고리",
            CATEGORIES,
            index=CATEGORIES.index(row_data["Category"]) if row_data["Category"] in CATEGORIES else 0
        )

        r2c1, r2c2, r2c3 = st.columns([2, 1, 1])
        input_subject = r2c1.text_input("회의명", value=safe_str(row_data["Subject"]))
        input_status = r2c2.selectbox(
            "상태",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(row_data["Status"]) if row_data["Status"] in STATUS_OPTIONS else 0
        )
        input_priority = r2c3.selectbox(
            "우선순위",
            PRIORITY_OPTIONS,
            index=PRIORITY_OPTIONS.index(row_data["Priority"]) if row_data["Priority"] in PRIORITY_OPTIONS else 1
        )

        r3c1, r3c2 = st.columns(2)
        input_org = r3c1.text_input("방문기관명", value=safe_str(row_data["OrgName"]))
        input_detail_place = r3c2.text_input("회의장소(세부)", value=safe_str(row_data["DetailPlace"]))

        r4c1, r4c2, r4c3 = st.columns(3)
        input_target_dept = r4c1.text_input("보좌관/비서/담당자 부서", value=safe_str(row_data["TargetDept"]))
        input_target_name = r4c2.text_input("보좌관/비서/담당자 이름", value=safe_str(row_data["TargetName"]))
        input_target_contact = r4c3.text_input("보좌관/비서/담당자 연락처", value=safe_str(row_data["TargetContact"]))

        r5c1, r5c2 = st.columns(2)
        input_companion = r5c1.text_input("회장님 외 동행인", value=safe_str(row_data["Companion"]))
        input_staff = r5c2.text_input("사무처 수행직원", value=safe_str(row_data["Staff"]))

        input_purpose = st.text_area("회의 목적", value=safe_str(row_data["Purpose"]), height=90)
        input_action = st.text_area("대응 방향", value=safe_str(row_data["ActionPlan"]), height=90)

        r6c1, r6c2 = st.columns(2)
        input_follow_owner = r6c1.text_input("주 담당자", value=safe_str(row_data["FollowOwner"]))
        input_follow_due = r6c2.date_input(
            "준비 완료기한",
            value=to_date_safe(row_data["FollowDue"]) or input_date
        )

        input_follow_task = st.text_area("후속/준비사항", value=safe_str(row_data["FollowTask"]), height=100)
        input_shared_note = st.text_area("공유 메모", value=safe_str(row_data["SharedNote"]), height=90)
        input_memo = st.text_area("Memo", value=safe_str(row_data["Memo"]), height=80)

        if mode == "new":
            submit = st.form_submit_button("저장 후 일정 보기로 이동", use_container_width=True)
            if submit:
                record = {
                    "ID": str(datetime.now().timestamp()),
                    "Date": str(input_date),
                    "Time": str(input_time)[:5],
                    "Category": input_category,
                    "Subject": input_subject,
                    "OrgName": input_org,
                    "DetailPlace": input_detail_place,
                    "TargetDept": input_target_dept,
                    "TargetName": input_target_name,
                    "TargetContact": input_target_contact,
                    "Companion": input_companion,
                    "Staff": input_staff,
                    "Purpose": input_purpose,
                    "ActionPlan": input_action,
                    "Memo": input_memo,
                    "Status": input_status,
                    "Priority": input_priority,
                    "FollowOwner": input_follow_owner,
                    "FollowTask": input_follow_task,
                    "FollowDue": str(input_follow_due),
                    "SharedNote": input_shared_note,
                    "Updated": "",
                }
                save_record(record, is_edit=False)
                st.session_state.main_menu = "📅 일정 보기"
                st.session_state.selected_date = input_date
                st.session_state.edit_id = None
                st.session_state.flash_message = "신규 일정이 저장되었습니다."
                st.rerun()
        else:
            b1, b2 = st.columns(2)
            save_btn = b1.form_submit_button("수정 저장", use_container_width=True)
            cancel_btn = b2.form_submit_button("수정 취소", use_container_width=True)

            if save_btn:
                record = {
                    "ID": row_data["ID"],
                    "Date": str(input_date),
                    "Time": str(input_time)[:5],
                    "Category": input_category,
                    "Subject": input_subject,
                    "OrgName": input_org,
                    "DetailPlace": input_detail_place,
                    "TargetDept": input_target_dept,
                    "TargetName": input_target_name,
                    "TargetContact": input_target_contact,
                    "Companion": input_companion,
                    "Staff": input_staff,
                    "Purpose": input_purpose,
                    "ActionPlan": input_action,
                    "Memo": input_memo,
                    "Status": input_status,
                    "Priority": input_priority,
                    "FollowOwner": input_follow_owner,
                    "FollowTask": input_follow_task,
                    "FollowDue": str(input_follow_due),
                    "SharedNote": input_shared_note,
                    "Updated": "",
                }
                save_record(record, is_edit=True)
                st.session_state.edit_id = None
                st.session_state.flash_message = "일정이 수정되었습니다."
                st.rerun()

            if cancel_btn:
                st.session_state.edit_id = None
                st.rerun()

# =========================================================
# 7. 사이드바
# =========================================================
st.sidebar.markdown("# 🏢 KVMA 비서실")

menu = st.sidebar.radio(
    "메뉴",
    ["📅 일정 보기", "✍️ 신규 일정 등록"],
    index=["📅 일정 보기", "✍️ 신규 일정 등록"].index(st.session_state.main_menu)
)
st.session_state.main_menu = menu

csv_bytes = csv_download_bytes(st.session_state.data)
st.sidebar.download_button(
    "📥 일정 CSV 다운로드",
    data=csv_bytes,
    file_name=f"kvma_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 운영 팁")
st.sidebar.markdown("""
- **주 담당자 / 후속사항 / 준비기한**을 같이 적으면 직원 간 협업이 쉬워집니다.
- 월간/주간은 **전체 흐름 확인용**,
- 일별 보기는 **실행/브리핑용**으로 쓰기 좋습니다.
""")

# =========================================================
# 8. 상단
# =========================================================
st.markdown('<div class="main-title">📒 KVMA 회장님 일정</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">회장님 일정 등록 · 조회 · 수정 · 취소 · 삭제와 함께, 직원들이 후속 준비사항을 공유할 수 있는 스케줄러입니다.</div>',
    unsafe_allow_html=True
)
show_flash()

# =========================================================
# 9. 신규 등록 화면
# =========================================================
if st.session_state.main_menu == "✍️ 신규 일정 등록":
    render_form(mode="new")

# =========================================================
# 10. 일정 보기 화면
# =========================================================
else:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**검색어 · 카테고리 · 상태 · 날짜를 기준으로 일정을 찾을 수 있습니다.**")

    fc1, fc2, fc3, fc4, fc5 = st.columns([2.4, 1.1, 1.1, 1.1, 0.8])
    search_text = fc1.text_input(
        "검색",
        placeholder="회의명 / 방문기관명 / 담당자명 / 연락처 / 후속업무 검색",
        label_visibility="collapsed"
    )
    selected_cat = fc2.selectbox(
        "카테고리",
        ["전체"] + CATEGORIES,
        index=(["전체"] + CATEGORIES).index(st.session_state.selected_cat)
        if st.session_state.selected_cat in (["전체"] + CATEGORIES) else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_cat = selected_cat

    selected_status = fc3.selectbox(
        "상태",
        ["전체"] + STATUS_OPTIONS,
        index=(["전체"] + STATUS_OPTIONS).index(st.session_state.selected_status)
        if st.session_state.selected_status in (["전체"] + STATUS_OPTIONS) else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_status = selected_status

    selected_date = fc4.date_input(
        "날짜",
        value=st.session_state.selected_date,
        label_visibility="collapsed"
    )
    st.session_state.selected_date = selected_date

    if fc5.button("오늘", use_container_width=True):
        st.session_state.selected_date = datetime.now().date()
        st.rerun()

    render_legend()
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_df = get_filtered_df(
        st.session_state.data,
        selected_cat=st.session_state.selected_cat,
        search_text=search_text,
        status_filter=st.session_state.selected_status
    )

    # 요약 지표
    daily_df = filtered_df[filtered_df["Date"].apply(lambda x: to_date_safe(x)) == st.session_state.selected_date]
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">선택일 일정 수</div><div class="metric-value">{len(daily_df)}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">확정 일정</div><div class="metric-value">{len(filtered_df[filtered_df["Status"]=="확정"])}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">보류 일정</div><div class="metric-value">{len(filtered_df[filtered_df["Status"]=="보류"])}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">취소 일정</div><div class="metric-value">{len(filtered_df[filtered_df["Status"]=="취소"])}</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["일별 보기", "주간 보기", "월별 보기"])

    # -----------------------------------------------------
    # 10-1. 일별 보기
    # -----------------------------------------------------
    with tabs[0]:
        st.markdown(
            f'<div class="section-title">📍 {st.session_state.selected_date.strftime("%Y년 %m월 %d일")} 일정</div>',
            unsafe_allow_html=True
        )

        if st.session_state.edit_id:
            target_df = st.session_state.data[st.session_state.data["ID"] == st.session_state.edit_id]
            if not target_df.empty:
                render_form(mode="edit", row_data=target_df.iloc[0].to_dict())

        day_df = filtered_df.copy()
        day_df["Date"] = pd.to_datetime(day_df["Date"], errors="coerce").dt.date
        day_df = day_df[day_df["Date"] == st.session_state.selected_date].sort_values(by="Time")

        if day_df.empty:
            st.info("조건에 맞는 일정이 없습니다.")

        for _, row in day_df.iterrows():
            if st.session_state.edit_id == row["ID"]:
                continue
            render_event_card(row)
            render_action_buttons(row)

    # -----------------------------------------------------
    # 10-2. 주간 보기
    # -----------------------------------------------------
    with tabs[1]:
        st.markdown('<div class="section-title">📅 주간 일정</div>', unsafe_allow_html=True)

        wc1, wc2 = st.columns([1.3, 4.7])
        week_anchor = wc1.date_input("기준 날짜", value=st.session_state.selected_date, key="week_anchor")
        if wc2.button("이 날짜가 포함된 주 보기", use_container_width=False):
            st.session_state.selected_date = week_anchor

        week_days = week_dates_from_any_day(st.session_state.selected_date)
        week_df = filtered_df.copy()
        week_df["Date"] = pd.to_datetime(week_df["Date"], errors="coerce").dt.date
        week_df = week_df[week_df["Date"].isin(week_days)]

        day_names = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7)

        for idx, day_obj in enumerate(week_days):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"**{day_obj.month}/{day_obj.day} ({day_names[idx]})**")
                    daily = week_df[week_df["Date"] == day_obj].sort_values(by="Time")

                    if daily.empty:
                        st.caption("일정 없음")
                    else:
                        show_rows = daily.head(6)
                        for _, row in show_rows.iterrows():
                            c = get_color(row["Category"])
                            line = f"{safe_str(row['Time'])} [{safe_str(row['Category'])}] {safe_str(row['Subject'])}"
                            st.markdown(
                                category_color_text_html(line, row["Category"]),
                                unsafe_allow_html=True
                            )
                            open_cols = st.columns([5, 1])
                            if open_cols[1].button("↗", key=f"week_open_{row['ID']}", use_container_width=True):
                                st.session_state.selected_event_id = row["ID"]
                                st.rerun()

                        if len(daily) > 6:
                            st.caption(f"+ {len(daily) - 6}개 더")

        if st.session_state.selected_event_id:
            selected_df = st.session_state.data[st.session_state.data["ID"] == st.session_state.selected_event_id]
            if not selected_df.empty:
                st.markdown('<div class="small-title">선택한 일정 상세정보</div>', unsafe_allow_html=True)
                render_event_card(selected_df.iloc[0])
                render_action_buttons(selected_df.iloc[0])

    # -----------------------------------------------------
    # 10-3. 월별 보기
    # -----------------------------------------------------
    with tabs[2]:
        st.markdown('<div class="section-title">🗓️ 월별 일정</div>', unsafe_allow_html=True)

        mc1, mc2 = st.columns([1, 1])
        year_options = list(range(datetime.now().year - 2, datetime.now().year + 4))
        month_year = mc1.selectbox("년도", year_options, index=year_options.index(st.session_state.selected_date.year))
        month_month = mc2.selectbox("월", list(range(1, 13)), index=st.session_state.selected_date.month - 1)

        month_df = filtered_df.copy()
        month_df["Date"] = pd.to_datetime(month_df["Date"], errors="coerce").dt.date
        month_df = month_df[month_df["Date"].apply(lambda d: d.year == month_year and d.month == month_month if pd.notna(d) else False)]

        weeks = month_calendar_weeks(month_year, month_month)
        weekday_names = ["일", "월", "화", "수", "목", "금", "토"]

        head_cols = st.columns(7)
        for i, name in enumerate(weekday_names):
            head_cols[i].markdown(f"**{name}**")

        for week_idx, week in enumerate(weeks):
            week_cols = st.columns(7)
            for day_idx, day_obj in enumerate(week):
                with week_cols[day_idx]:
                    with st.container(border=True):
                        if day_obj.month != month_month:
                            st.markdown(f"<div class='month-day-head' style='color:#B5BBC8;'>{day_obj.day}일</div>", unsafe_allow_html=True)
                            st.caption(" ")
                        else:
                            st.markdown(f"<div class='month-day-head'>{day_obj.day}일</div>", unsafe_allow_html=True)
                            daily = month_df[month_df["Date"] == day_obj].sort_values(by="Time")

                            if daily.empty:
                                st.caption("일정 없음")
                            else:
                                show_rows = daily.head(4)
                                for _, row in show_rows.iterrows():
                                    line = f"{safe_str(row['Time'])} [{safe_str(row['Category'])}] {safe_str(row['Subject'])}"
                                    st.markdown(
                                        category_color_text_html(line, row["Category"]),
                                        unsafe_allow_html=True
                                    )
                                    btn_cols = st.columns([5, 1])
                                    if btn_cols[1].button("↗", key=f"month_open_{row['ID']}", use_container_width=True):
                                        st.session_state.selected_event_id = row["ID"]
                                        st.rerun()

                                if len(daily) > 4:
                                    st.caption(f"+ {len(daily) - 4}개 더")

        if st.session_state.selected_event_id:
            selected_df = st.session_state.data[st.session_state.data["ID"] == st.session_state.selected_event_id]
            if not selected_df.empty:
                st.markdown('<div class="small-title">선택한 일정 상세정보</div>', unsafe_allow_html=True)
                render_event_card(selected_df.iloc[0])
                render_action_buttons(selected_df.iloc[0])

    st.markdown("""
    <div class="helper-box">
    현재 버전에는 실무용으로 바로 쓰기 좋은 필드를 넣었습니다.
    특히 <b>주 담당자 · 후속/준비사항 · 준비 완료기한 · 공유 메모</b>를 활용하면,
    회장 일정이 단순 보기용이 아니라 사무처 협업용 보드로도 작동합니다.
    </div>
    """, unsafe_allow_html=True)
