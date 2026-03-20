import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import html
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="KVMA 회장님 일정",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. 상수
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

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# =========================================================
# 3. 스타일
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.block-container {
    padding-top: 2.4rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

h1, h2, h3 {
    line-height: 1.2 !important;
}

.main-title {
    font-size: 2.9rem;
    font-weight: 800;
    color: #2F3142;
    margin-top: 0.5rem;
    margin-bottom: 0.55rem;
    line-height: 1.2;
    word-break: keep-all;
    white-space: normal;
    overflow: visible;
    padding-top: 0.25rem;
}

.sub-text {
    font-size: 1rem;
    color: #6B7280;
    margin-bottom: 1.1rem;
    line-height: 1.5;
    word-break: keep-all;
}

.panel {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 18px;
    padding: 14px 16px;
    box-shadow: 0 4px 16px rgba(20, 24, 40, 0.04);
    margin-bottom: 16px;
}

.section-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #2F3142;
    margin: 10px 0 12px 0;
    line-height: 1.2;
}

.legend-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    margin: 0 8px 8px 0;
    border: 1px solid;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 14px;
    padding: 8px 12px 7px 12px;
    min-height: 62px;
}

.metric-label {
    font-size: 0.76rem;
    color: #6B7280;
    font-weight: 700;
    margin-bottom: 2px;
    line-height: 1.15;
}

.metric-value {
    font-size: 0.95rem;
    font-weight: 800;
    color: #2F3142;
    line-height: 1.05;
}

.summary-card {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid #E8EBF2;
    margin-bottom: 10px;
}

.summary-inner {
    display: flex;
}

.summary-accent {
    width: 10px;
    flex-shrink: 0;
}

.summary-body {
    width: 100%;
    padding: 14px 16px 12px 16px;
}

.summary-meta {
    font-size: 0.95rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.summary-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #232634;
    line-height: 1.28;
    margin: 0;
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
    vertical-align: middle;
}

.info-box {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 16px;
    padding: 12px 14px 10px 14px;
    min-height: 74px;
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
    line-height: 1.45;
    white-space: pre-wrap;
    word-break: break-word;
}

.memo-box {
    background: #FFFBEA;
    border: 1px solid #F8E3A3;
    border-left: 8px solid #F5C84B;
    border-radius: 16px;
    padding: 12px 16px;
    margin-top: 2px;
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

.small-action button {
    min-height: 34px !important;
    height: 34px !important;
    padding-top: 0.15rem !important;
    padding-bottom: 0.15rem !important;
    font-size: 0.84rem !important;
}

div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
}

.stTextInput input,
.stDateInput input,
.stTimeInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea {
    border-radius: 12px !important;
}

div[data-testid="stForm"] {
    border: 1px solid #ECEEF3;
    border-radius: 18px;
    padding: 16px 16px 10px 16px;
    background: #ffffff;
}

.streamlit-expanderHeader {
    font-weight: 800 !important;
    font-size: 1rem !important;
}

.wm-detail {
    margin-bottom: 8px;
    border-radius: 12px;
}

.wm-summary {
    list-style: none;
    cursor: pointer;
    border-radius: 12px;
    padding: 7px 9px;
    font-size: 0.78rem;
    line-height: 1.35;
    border: 1px solid;
    font-weight: 700;
    word-break: break-word;
}

.wm-summary::-webkit-details-marker {
    display: none;
}

.wm-content {
    margin-top: 8px;
    padding: 10px;
    border: 1px solid #ECEEF3;
    border-radius: 14px;
    background: #ffffff;
}

.wm-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
}

.wm-box {
    border: 1px solid #ECEEF3;
    border-radius: 12px;
    padding: 8px 10px;
    background: #ffffff;
}

.wm-label {
    font-size: 0.74rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 4px;
}

.wm-value {
    font-size: 0.88rem;
    font-weight: 600;
    color: #232634;
    line-height: 1.45;
    word-break: break-word;
    white-space: pre-wrap;
}

.day-head {
    font-size: 1rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 8px;
}

.canceled-title {
    text-decoration: line-through;
    opacity: 0.65;
}

.cancel-pill {
    display: inline-block;
    margin-left: 6px;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 800;
    background: #FEE2E2;
    color: #B42318;
    border: 1px solid #FECACA;
    vertical-align: middle;
}

@media (max-width: 1000px) {
    .main-title {
        font-size: 2.1rem;
    }
    .summary-title {
        font-size: 1.15rem;
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
    return df[DATA_COLUMNS].copy().fillna("")

def get_color(cat: str):
    return COLOR_MAP.get(cat, COLOR_MAP["기타"])

def to_date_safe(v):
    if pd.isna(v) or v == "":
        return None
    parsed = pd.to_datetime(v, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()

def safe_str(v):
    if pd.isna(v):
        return ""
    return str(v).strip()

def esc(v):
    return html.escape(safe_str(v) if safe_str(v) else "-")

def csv_download_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def excel_download_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Schedule")
    output.seek(0)
    return output.getvalue()

@st.cache_resource
def get_gspread_client():
    creds_info = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(credentials)

def get_worksheet():
    gc = get_gspread_client()
    sheet_name = st.secrets["google_sheet_name"]
    worksheet_name = st.secrets["google_worksheet_name"]
    sh = gc.open(sheet_name)
    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=len(DATA_COLUMNS) + 5)
        ws.append_row(DATA_COLUMNS)
    return ws

def ensure_sheet_header(ws):
    values = ws.get_all_values()
    if not values:
        ws.append_row(DATA_COLUMNS)
        return
    first_row = values[0]
    if first_row != DATA_COLUMNS:
        ws.clear()
        ws.append_row(DATA_COLUMNS)

def load_data_from_gsheet():
    try:
        ws = get_worksheet()
        ensure_sheet_header(ws)
        records = ws.get_all_records()
        if not records:
            return ensure_columns(pd.DataFrame(columns=DATA_COLUMNS))
        return ensure_columns(pd.DataFrame(records))
    except Exception as e:
        st.error(f"구글 시트 데이터를 불러오지 못했습니다: {e}")
        return ensure_columns(pd.DataFrame(columns=DATA_COLUMNS))

def save_all_to_gsheet(df: pd.DataFrame):
    ws = get_worksheet()
    df = ensure_columns(df)
    values = [DATA_COLUMNS] + df.astype(str).fillna("").values.tolist()
    ws.clear()
    ws.update(values)

def get_filtered_df(df, selected_cat="카테고리", search_text="", status_filter="현황"):
    temp = df.copy()
    temp["Date"] = pd.to_datetime(temp["Date"], errors="coerce").dt.date

    if selected_cat not in ["전체", "카테고리"]:
        temp = temp[temp["Category"] == selected_cat]

    if status_filter not in ["전체", "현황"]:
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

    return temp.sort_values(by=["Date", "Time", "Updated"], ascending=[True, True, False])

def week_dates_from_any_day(any_day: date):
    start = any_day - timedelta(days=(any_day.weekday() + 1) % 7)
    return [start + timedelta(days=i) for i in range(7)]

def month_calendar_weeks(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)
    return cal.monthdatescalendar(year, month)

def next_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

def persist_data():
    save_all_to_gsheet(st.session_state.data)

def save_record(record: dict, is_edit=False):
    record["Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if is_edit:
        mask = st.session_state.data["ID"].astype(str) == str(record["ID"])
        st.session_state.data.loc[mask, DATA_COLUMNS[1:]] = [
            record[col] for col in DATA_COLUMNS[1:]
        ]
    else:
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([record])],
            ignore_index=True
        )

    st.session_state.data = ensure_columns(st.session_state.data)
    persist_data()

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

def render_legend():
    parts = []
    for cat in CATEGORIES:
        c = get_color(cat)
        parts.append(
            f'<span class="legend-pill" style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">{cat}</span>'
        )
    st.markdown("".join(parts), unsafe_allow_html=True)

def format_subject_html(row):
    subject = esc(row["Subject"])
    if safe_str(row["Status"]) == "취소":
        return f'<span class="canceled-title">{subject}</span><span class="cancel-pill">취소</span>'
    return subject

def format_subject_md(row):
    subject = safe_str(row["Subject"])
    if safe_str(row["Status"]) == "취소":
        return f"{safe_str(row['Time'])} · ~~{subject}~~"
    return f"{safe_str(row['Time'])} · {subject}"

# =========================================================
# 5. 상태 초기화
# =========================================================
today = datetime.now().date()

if "data" not in st.session_state:
    st.session_state.data = load_data_from_gsheet()
else:
    st.session_state.data = ensure_columns(st.session_state.data)

if "app_today" not in st.session_state:
    st.session_state.app_today = today

if st.session_state.app_today != today:
    st.session_state.app_today = today
    st.session_state.selected_date = today

if "main_menu" not in st.session_state:
    st.session_state.main_menu = "📅 일정 보기"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = today

if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "카테고리"

if "selected_status" not in st.session_state:
    st.session_state.selected_status = "현황"

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "flash_message" not in st.session_state:
    st.session_state.flash_message = None

# =========================================================
# 6. 렌더 함수
# =========================================================
def render_summary_header(row):
    c = get_color(row["Category"])
    st.markdown(f"""
    <div class="summary-card" style="background:{c['bg']};">
        <div class="summary-inner">
            <div class="summary-accent" style="background:{c['line']};"></div>
            <div class="summary-body">
                <div class="summary-meta" style="color:{c['text']};">
                    ⏰ {esc(row["Time"])}
                    <span class="tag-pill" style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">{esc(row["Category"])}</span>
                    <span class="tag-pill">{esc(row["Status"])}</span>
                    <span class="tag-pill">우선순위 {esc(row["Priority"])}</span>
                </div>
                <div class="summary-title">{format_subject_html(row)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_detail_blocks(row):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">방문기관명</div>
            <div class="info-value">🏢 {esc(row["OrgName"])}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">회의장소(세부)</div>
            <div class="info-value">📍 {esc(row["DetailPlace"])}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">보좌관/비서/담당자 정보</div>
            <div class="info-value">👤 {html.escape(contact_text(row))}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">회장님 외 동행인</div>
            <div class="info-value">👥 {esc(row["Companion"])}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">사무처 수행직원</div>
            <div class="info-value">🧾 {esc(row["Staff"])}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">최종 수정</div>
            <div class="info-value">🕒 {esc(row["Updated"])}</div>
        </div>
        """, unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">회의 목적</div>
            <div class="info-value">{esc(row["Purpose"])}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">주 담당자</div>
            <div class="info-value">{esc(row["FollowOwner"])}</div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">대응 방향</div>
            <div class="info-value">{esc(row["ActionPlan"])}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-label">준비 완료기한</div>
            <div class="info-value">{esc(row["FollowDue"])}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">후속/준비사항</div>
        <div class="info-value">{esc(row["FollowTask"])}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
        <div class="info-label">공유 메모</div>
        <div class="info-value">{esc(row["SharedNote"])}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="memo-box">
        <div class="memo-title">📌 Memo</div>
        <div class="memo-text">{esc(row["Memo"])}</div>
    </div>
    """, unsafe_allow_html=True)

def render_action_buttons(row, prefix=""):
    st.markdown('<div class="small-action">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([0.8, 0.9, 0.8, 6.5])

    if c1.button("수정", key=f"{prefix}_edit_{row['ID']}", use_container_width=True):
        st.session_state.edit_id = row["ID"]
        st.rerun()

    toggle_label = "일정 취소" if row["Status"] != "취소" else "취소 해제"
    toggle_next = "취소" if row["Status"] != "취소" else "확정"
    if c2.button(toggle_label, key=f"{prefix}_cancel_{row['ID']}", use_container_width=True):
        mask = st.session_state.data["ID"].astype(str) == str(row["ID"])
        st.session_state.data.loc[
            mask, ["Status", "Updated"]
        ] = [toggle_next, datetime.now().strftime("%Y-%m-%d %H:%M")]
        persist_data()
        st.session_state.flash_message = "상태가 변경되었습니다."
        st.rerun()

    if c3.button("삭제", key=f"{prefix}_delete_{row['ID']}", use_container_width=True):
        st.session_state.data = st.session_state.data[
            st.session_state.data["ID"].astype(str) != str(row["ID"])
        ].reset_index(drop=True)
        if st.session_state.edit_id == row["ID"]:
            st.session_state.edit_id = None
        persist_data()
        st.session_state.flash_message = "일정이 삭제되었습니다."
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_day_expander(row, prefix="", expanded=False):
    label = format_subject_md(row)
    with st.expander(label, expanded=expanded):
        render_summary_header(row)
        render_detail_blocks(row)
        render_action_buttons(row, prefix=prefix)

def render_week_month_details_html(row):
    c = get_color(row["Category"])
    summary_text = f'{html.escape(safe_str(row["Time"]))} [{html.escape(safe_str(row["Category"]))}] {html.escape(safe_str(row["Subject"]))}'
    if safe_str(row["Status"]) == "취소":
        summary_text = f'{html.escape(safe_str(row["Time"]))} [{html.escape(safe_str(row["Category"]))}] <span class="canceled-title">{html.escape(safe_str(row["Subject"]))}</span><span class="cancel-pill">취소</span>'

    return f"""
    <details class="wm-detail">
        <summary class="wm-summary" style="color:{c["text"]}; border-color:{c["line"]}; background:{c["soft"]};">
            {summary_text}
        </summary>
        <div class="wm-content">
            <div class="wm-grid">
                <div class="wm-box"><div class="wm-label">방문기관명</div><div class="wm-value">{esc(row["OrgName"])}</div></div>
                <div class="wm-box"><div class="wm-label">회의장소(세부)</div><div class="wm-value">{esc(row["DetailPlace"])}</div></div>
                <div class="wm-box"><div class="wm-label">보좌관/비서/담당자 정보</div><div class="wm-value">{html.escape(contact_text(row))}</div></div>
                <div class="wm-box"><div class="wm-label">회장님 외 동행인</div><div class="wm-value">{esc(row["Companion"])}</div></div>
                <div class="wm-box"><div class="wm-label">사무처 수행직원</div><div class="wm-value">{esc(row["Staff"])}</div></div>
                <div class="wm-box"><div class="wm-label">회의 목적</div><div class="wm-value">{esc(row["Purpose"])}</div></div>
                <div class="wm-box"><div class="wm-label">대응 방향</div><div class="wm-value">{esc(row["ActionPlan"])}</div></div>
                <div class="wm-box"><div class="wm-label">주 담당자</div><div class="wm-value">{esc(row["FollowOwner"])}</div></div>
                <div class="wm-box"><div class="wm-label">준비 완료기한</div><div class="wm-value">{esc(row["FollowDue"])}</div></div>
                <div class="wm-box"><div class="wm-label">후속/준비사항</div><div class="wm-value">{esc(row["FollowTask"])}</div></div>
                <div class="wm-box"><div class="wm-label">공유 메모</div><div class="wm-value">{esc(row["SharedNote"])}</div></div>
                <div class="wm-box"><div class="wm-label">Memo</div><div class="wm-value">{esc(row["Memo"])}</div></div>
                <div class="wm-box"><div class="wm-label">최종 수정</div><div class="wm-value">{esc(row["Updated"])}</div></div>
            </div>
        </div>
    </details>
    """

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

        try:
            default_time = datetime.strptime(safe_str(row_data["Time"]) or "09:00", "%H:%M").time()
        except Exception:
            default_time = datetime.strptime("09:00", "%H:%M").time()

        input_time = r1c2.time_input("일정 시간", value=default_time)
        input_category = r1c3.selectbox(
            "카테고리",
            CATEGORIES,
            index=CATEGORIES.index(row_data["Category"]) if row_data["Category"] in CATEGORIES else 0
        )

        r2c1, r2c2, r2c3 = st.columns([2, 1, 1])
        input_subject = r2c1.text_input("회의명", value=safe_str(row_data["Subject"]))
        input_status = r2c2.selectbox(
            "현황",
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
                if not safe_str(input_subject):
                    st.warning("회의명은 입력해 주세요.")
                else:
                    record = {
                        "ID": next_id(),
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
            b1, b2 = st.columns([1, 1])
            save_btn = b1.form_submit_button("수정 저장", use_container_width=True)
            cancel_btn = b2.form_submit_button("수정 취소", use_container_width=True)

            if save_btn:
                if not safe_str(input_subject):
                    st.warning("회의명은 입력해 주세요.")
                else:
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
                    st.session_state.selected_date = input_date
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
xlsx_bytes = excel_download_bytes(st.session_state.data)

st.sidebar.download_button(
    "📥 일정 CSV 다운로드",
    data=csv_bytes,
    file_name=f"kvma_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
    use_container_width=True
)

st.sidebar.download_button(
    "📥 일정 엑셀 다운로드",
    data=xlsx_bytes,
    file_name=f"kvma_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

if st.sidebar.button("🔄 구글 시트에서 다시 불러오기", use_container_width=True):
    st.session_state.data = load_data_from_gsheet()
    st.session_state.flash_message = "구글 시트에서 최신 데이터를 다시 불러왔습니다."
    st.rerun()

with st.sidebar.expander("📊 저장된 일정표 미리보기", expanded=False):
    preview_df = st.session_state.data.copy()
    if not preview_df.empty:
        st.dataframe(
            preview_df.sort_values(by=["Date", "Time", "Updated"], ascending=[True, True, False]),
            use_container_width=True,
            hide_index=True,
            height=320
        )
    else:
        st.caption("저장된 일정이 없습니다.")

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
# 9. 신규 등록
# =========================================================
if st.session_state.main_menu == "✍️ 신규 일정 등록":
    render_form(mode="new")

# =========================================================
# 10. 일정 보기
# =========================================================
else:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("**검색어 · 카테고리 · 현황 · 날짜를 기준으로 일정을 찾을 수 있습니다.**")

    fc1, fc2, fc3, fc4, fc5 = st.columns([2.7, 1.2, 1.2, 1.25, 0.8])

    search_text = fc1.text_input(
        "검색",
        placeholder="회의명 / 방문기관명 / 담당자명 / 연락처 / 후속업무 검색",
        label_visibility="collapsed"
    )

    selected_cat = fc2.selectbox(
        "",
        ["카테고리"] + CATEGORIES,
        index=(["카테고리"] + CATEGORIES).index(st.session_state.selected_cat)
        if st.session_state.selected_cat in (["카테고리"] + CATEGORIES) else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_cat = selected_cat

    selected_status = fc3.selectbox(
        "",
        ["현황"] + STATUS_OPTIONS,
        index=(["현황"] + STATUS_OPTIONS).index(st.session_state.selected_status)
        if st.session_state.selected_status in (["현황"] + STATUS_OPTIONS) else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_status = selected_status

    selected_date = fc4.date_input(
        "",
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

    day_df = filtered_df.copy()
    day_df["Date"] = pd.to_datetime(day_df["Date"], errors="coerce").dt.date
    day_df = day_df[day_df["Date"] == st.session_state.selected_date].sort_values(by="Time")

    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.8])
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">선택일 일정 수</div><div class="metric-value">{len(day_df)}</div></div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">확정 일정</div><div class="metric-value">{len(filtered_df[filtered_df["Status"]=="확정"])}</div></div>',
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">보류 일정</div><div class="metric-value">{len(filtered_df[filtered_df["Status"]=="보류"])}</div></div>',
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">취소 일정</div><div class="metric-value">{len(filtered_df[filtered_df["Status"]=="취소"])}</div></div>',
            unsafe_allow_html=True
        )
    with m5:
        st.empty()

    tabs = st.tabs(["일별 보기", "주간 보기", "월별 보기", "전체 일정표"])

    with tabs[0]:
        st.markdown(
            f'<div class="section-title">📍 {st.session_state.selected_date.strftime("%Y년 %m월 %d일")} 일정</div>',
            unsafe_allow_html=True
        )

        if st.session_state.edit_id:
            edit_target = st.session_state.data[
                st.session_state.data["ID"].astype(str) == str(st.session_state.edit_id)
            ]
            if not edit_target.empty:
                render_form(mode="edit", row_data=edit_target.iloc[0].to_dict())
        else:
            if not day_df.empty:
                for idx, (_, row) in enumerate(day_df.iterrows()):
                    render_day_expander(row, prefix=f"day_{idx}", expanded=False)

    with tabs[1]:
        st.markdown('<div class="section-title">📅 주간 일정</div>', unsafe_allow_html=True)

        wc1, wc2 = st.columns([1.3, 4.7])
        week_anchor = wc1.date_input(
            "",
            value=st.session_state.selected_date,
            key="week_anchor_date",
            label_visibility="collapsed"
        )
        if wc2.button("이 날짜가 포함된 주 보기", key="apply_week_anchor"):
            st.session_state.selected_date = week_anchor
            st.rerun()

        week_days = week_dates_from_any_day(st.session_state.selected_date)
        week_df = filtered_df.copy()
        week_df["Date"] = pd.to_datetime(week_df["Date"], errors="coerce").dt.date
        week_df = week_df[week_df["Date"].isin(week_days)]

        day_names = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7)

        for idx, day_obj in enumerate(week_days):
            with cols[idx]:
                st.markdown(
                    f'<div class="day-head">{day_obj.month}/{day_obj.day} ({day_names[idx]})</div>',
                    unsafe_allow_html=True
                )

                daily = week_df[week_df["Date"] == day_obj].sort_values(by="Time")
                if daily.empty:
                    st.caption("일정 없음")
                else:
                    for _, row in daily.iterrows():
                        st.markdown(render_week_month_details_html(row), unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="section-title">🗓️ 월별 일정</div>', unsafe_allow_html=True)

        mc1, mc2 = st.columns([1, 1])
        year_options = list(range(datetime.now().year - 2, datetime.now().year + 4))

        month_year = mc1.selectbox(
            "년도",
            year_options,
            index=year_options.index(st.session_state.selected_date.year),
            key="month_year_select"
        )
        month_month = mc2.selectbox(
            "월",
            list(range(1, 13)),
            index=st.session_state.selected_date.month - 1,
            key="month_month_select"
        )

        month_df = filtered_df.copy()
        month_df["Date"] = pd.to_datetime(month_df["Date"], errors="coerce").dt.date
        month_df = month_df[
            month_df["Date"].apply(
                lambda d: d.year == month_year and d.month == month_month if pd.notna(d) else False
            )
        ]

        weeks = month_calendar_weeks(month_year, month_month)
        weekday_names = ["일", "월", "화", "수", "목", "금", "토"]

        head_cols = st.columns(7)
        for i, name in enumerate(weekday_names):
            head_cols[i].markdown(f"**{name}**")

        for week in weeks:
            week_cols = st.columns(7)
            for didx, day_obj in enumerate(week):
                with week_cols[didx]:
                    if day_obj.month != month_month:
                        st.markdown(
                            f"<div class='day-head' style='color:#B5BBC8;'>{day_obj.day}일</div>",
                            unsafe_allow_html=True
                        )
                        st.caption(" ")
                    else:
                        st.markdown(
                            f"<div class='day-head'>{day_obj.day}일</div>",
                            unsafe_allow_html=True
                        )
                        daily = month_df[month_df["Date"] == day_obj].sort_values(by="Time")

                        if daily.empty:
                            st.caption("일정 없음")
                        else:
                            for _, row in daily.iterrows():
                                st.markdown(render_week_month_details_html(row), unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('<div class="section-title">📋 전체 일정표</div>', unsafe_allow_html=True)

        table_df = filtered_df.copy()
        if table_df.empty:
            st.caption("표시할 일정이 없습니다.")
        else:
            st.dataframe(
                table_df.sort_values(by=["Date", "Time", "Updated"], ascending=[True, True, False]),
                use_container_width=True,
                hide_index=True,
                height=500
            )
