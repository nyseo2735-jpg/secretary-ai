import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, time
from zoneinfo import ZoneInfo
import calendar
import html
from io import BytesIO
import math
import gspread
from google.oauth2.service_account import Credentials

# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="KVMA President Schedule",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. 상수
# =========================================================
COLOR_MAP = {
    "국회": {"bg": "#FFF5F6", "soft": "#FDECEF", "line": "#D84C57", "text": "#B4232C", "dot": "🔴"},
    "정부기관": {"bg": "#F4F9FF", "soft": "#EAF4FF", "line": "#3B82F6", "text": "#1D4ED8", "dot": "🔵"},
    "대한수의사회": {"bg": "#F4FBF5", "soft": "#EAF8EC", "line": "#2E9F5B", "text": "#207547", "dot": "🟢"},
    "수의과대학": {"bg": "#FBF6FD", "soft": "#F3EAFB", "line": "#A855F7", "text": "#7E22CE", "dot": "🟣"},
    "언론사": {"bg": "#FFF8F1", "soft": "#FFF0DE", "line": "#F59E0B", "text": "#C56A00", "dot": "🟠"},
    "기업": {"bg": "#F8FAFC", "soft": "#EEF2F6", "line": "#64748B", "text": "#334155", "dot": "⚫"},
    "유관단체": {"bg": "#F2FCFD", "soft": "#E3F7F9", "line": "#14B8A6", "text": "#0F8F82", "dot": "🟦"},
    "시도지부": {"bg": "#F7F5FF", "soft": "#EEE9FF", "line": "#7C3AED", "text": "#5B21B6", "dot": "🟪"},
    "기타": {"bg": "#FAFAFA", "soft": "#F2F2F2", "line": "#9CA3AF", "text": "#4B5563", "dot": "⚪"},
}
CATEGORIES = list(COLOR_MAP.keys())
STATUS_OPTIONS = ["확정", "보류", "완료", "취소"]
PRIORITY_OPTIONS = ["높음", "보통", "낮음"]
FOLLOW_STATUS_OPTIONS = ["미착수", "진행중", "완료", "보류"]

CAT_SLUG = {
    "국회": "assembly", "정부기관": "gov", "대한수의사회": "kvma",
    "수의과대학": "college", "언론사": "media", "기업": "corp",
    "유관단체": "assoc", "시도지부": "branch", "기타": "etc",
}

DATA_COLUMNS = [
    "ID", "Date", "Time", "Category", "Subject", "PresidentAttend",
    "OrgName", "DetailPlace", "TargetDept", "TargetName", "TargetContact",
    "Companion", "Staff", "Purpose", "ActionPlan", "Memo", "Status",
    "Priority", "FollowOwner", "FollowTask", "FollowDue", "SharedNote",
    "FollowStatus", "FollowProgressMemo", "FollowUpdated", "Updated",
    "IsDeleted", "UpdatedBy",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ADMIN_RELOAD_PASSWORD = "2735"

# =========================================================
# 3. 스타일
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*='css'] { font-family: 'Pretendard', sans-serif; }
.block-container { padding-top: 2.5rem; padding-bottom: 1.4rem; max-width: 1600px; }
h1, h2, h3 { line-height: 1.2 !important; }

.main-title {
    font-size: 2.7rem; font-weight: 800; color: #2F3142;
    margin-top: 0.45rem; margin-bottom: 0.35rem; line-height: 1.2; word-break: keep-all;
}
.sub-text {
    font-size: 0.98rem; color: #6B7280; margin-bottom: 0.8rem;
    line-height: 1.5; word-break: keep-all;
}
.panel {
    background: #ffffff; border: 1px solid #ECEEF3; border-radius: 18px;
    padding: 12px 14px; box-shadow: 0 4px 16px rgba(20,24,40,0.04); margin-bottom: 10px;
}
.section-title {
    font-size: 1.7rem; font-weight: 800; color: #2F3142; margin: 8px 0 16px 0; line-height: 1.2;
}
.legend-pill {
    display: inline-block; padding: 6px 12px; border-radius: 999px;
    font-size: 0.80rem; font-weight: 700; margin: 0 6px 6px 0; border: 1px solid;
}
.metric-chip {
    display: inline-block; padding: 6px 12px; border-radius: 999px;
    font-size: 0.80rem; font-weight: 800; margin: 0 8px 8px 0;
    border: 1px solid #D8DEE8; background: #ffffff; color: #344054;
}
.summary-card {
    border-radius: 22px; overflow: hidden; border: 1px solid #E8EBF2; margin-top: 4px; margin-bottom: 10px;
}
.summary-inner { display: flex; }
.summary-accent { width: 10px; flex-shrink: 0; }
.summary-body { width: 100%; padding: 14px 16px 12px 16px; }
.summary-meta { font-size: 0.92rem; font-weight: 800; margin-bottom: 6px; }
.summary-title {
    font-size: 1.22rem; font-weight: 800; color: #232634; line-height: 1.28; margin: 0; word-break: keep-all;
}
.tag-pill {
    display: inline-block; padding: 5px 10px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 800; border: 1px solid #D1D5DB;
    background: #ffffff; color: #475467; margin-left: 6px; vertical-align: middle;
}
.follow-pill {
    display: inline-block; padding: 5px 10px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 800; border: 1px solid #D1D5DB;
    background: #F8FAFC; color: #344054; margin-right: 6px; margin-bottom: 6px; vertical-align: middle;
}
.info-box {
    background: #ffffff; border: 1px solid #ECEEF3; border-radius: 16px;
    padding: 11px 13px 10px 13px; min-height: 68px; margin-bottom: 8px;
}
.info-label { font-size: 0.77rem; font-weight: 800; color: #6B7280; margin-bottom: 6px; line-height: 1.35; }
.info-value { font-size: 0.96rem; font-weight: 600; color: #232634; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
.memo-box {
    background: #FFFBEA; border: 1px solid #F8E3A3; border-left: 8px solid #F5C84B;
    border-radius: 16px; padding: 12px 16px; margin-top: 4px;
}
.memo-title { font-size: 0.90rem; font-weight: 800; color: #7A5A00; margin-bottom: 6px; }
.memo-text { font-size: 0.94rem; color: #4B5563; line-height: 1.55; white-space: pre-wrap; word-break: break-word; }
.follow-wrap {
    background: #F7FAFF; border: 1px solid #D7E7FF; border-left: 8px solid #3B82F6;
    border-radius: 18px; padding: 14px 16px; margin-top: 8px; margin-bottom: 10px;
}
.follow-title { font-size: 1rem; font-weight: 800; color: #1D4ED8; margin-bottom: 10px; }
.follow-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.follow-box { border: 1px solid #DDE6F4; border-radius: 14px; padding: 10px 12px; background: #ffffff; }
.follow-label { font-size: 0.75rem; font-weight: 800; color: #6B7280; margin-bottom: 4px; }
.follow-value { font-size: 0.92rem; font-weight: 600; color: #1F2937; line-height: 1.45; white-space: pre-wrap; word-break: break-word; }

.small-action button {
    min-height: 34px !important; height: 34px !important;
    padding-top: 0.15rem !important; padding-bottom: 0.15rem !important; font-size: 0.84rem !important;
}
div[data-testid='stButton'] > button { border-radius: 12px !important; font-weight: 700 !important; }
div[data-testid='stDownloadButton'] > button { border-radius: 12px !important; font-weight: 700 !important; }
.stTextInput input, .stDateInput input, .stTimeInput input,
.stSelectbox div[data-baseweb='select'] > div, .stTextArea textarea { border-radius: 12px !important; }
div[data-testid='stForm'] {
    border: 1px solid #ECEEF3; border-radius: 18px; padding: 16px 16px 10px 16px; background: #ffffff;
}

/* ──────────────────────────────────────────
   사이드바 미리보기 박스 간격 (강제 적용)
────────────────────────────────────────── */
.sidebar-day-item {
    border: 1px solid #ECEEF3;
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 8px !important;
    margin-top: 0px !important;
    background: #ffffff;
    display: block !important;
}
.sidebar-day-time { font-size: 0.78rem; font-weight: 800; color: #475467; margin-bottom: 4px; }
.sidebar-day-title { font-size: 0.86rem; font-weight: 700; color: #1F2937; line-height: 1.35; }

/* 사이드바 미리보기 컨테이너 내부 p 태그 margin 제거 */
[data-testid='stSidebar'] .sidebar-day-item + .sidebar-day-item { margin-top: 0 !important; }
[data-testid='stSidebar'] .stMarkdown p { margin-bottom: 0 !important; margin-top: 0 !important; }

.helper-note {
    font-size: 0.82rem; color: #667085; line-height: 1.45;
    display: block; margin-top: 8px !important; margin-bottom: 12px !important;
}
.segment-note { font-size: 0.84rem; color: #667085; margin-bottom: 8px; }

.streamlit-expanderHeader { font-weight: 800 !important; font-size: 0.90rem !important; line-height: 1.2 !important; }
div[data-testid='stExpander'] details {
    border-radius: 16px !important; border: 1.6px solid #D8DEE8 !important;
    background: #ffffff !important; overflow: hidden !important; box-shadow: none !important;
}
div[data-testid='stExpander'] summary:hover { background: #FAFAFA !important; }
div[data-testid='stExpander'] summary { padding-top: 0.18rem !important; padding-bottom: 0.18rem !important; }
div[data-testid='stTabs'] { margin-bottom: 0 !important; }

.day-head { font-size: 1rem; font-weight: 800; color: #2F3142; margin-bottom: 4px; }
.day-head.sun { color: #C1121F; }
.day-head.sat { color: #1D4ED8; }
.day-head.dim.sun { color: #F1A0A7; }
.day-head.dim.sat { color: #9BB8F5; }
.day-head.dim { color: #B5BBC8; }

.canceled-title { text-decoration: line-through; opacity: 0.65; }
.cancel-pill {
    display: inline-block; margin-left: 6px; padding: 4px 8px; border-radius: 999px;
    font-size: 0.72rem; font-weight: 800; background: #FEE2E2; color: #B42318;
    border: 1px solid #FECACA; vertical-align: middle;
}
.attend-pill {
    display: inline-block; margin-left: 6px; padding: 4px 8px; border-radius: 999px;
    font-size: 0.72rem; font-weight: 800; background: #FFF7D6; color: #8A6500;
    border: 1px solid #F2D675; vertical-align: middle;
}

/* ──────────────────────────────────────────
   주간/월별 이벤트 detail grid: 한 줄 한 항목
────────────────────────────────────────── */
.wm-detail-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 5px;
    margin-top: 6px;
    margin-bottom: 8px;
}
.wm-detail-cell {
    background: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 8px; padding: 5px 7px;
}
.wm-detail-cell-full {
    background: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 8px; padding: 5px 7px;
}
.wm-detail-label { font-size: 0.66rem; font-weight: 700; color: #9CA3AF; margin-bottom: 2px; }
.wm-detail-value { font-size: 0.78rem; font-weight: 600; color: #1F2937; line-height: 1.35; word-break: break-word; white-space: pre-wrap; }

/* ──────────────────────────────────────────
   주간/월별 컬러 일정 버튼 (HTML 기반)
────────────────────────────────────────── */
.wm-event-btn {
    border-radius: 14px;
    padding: 10px 12px;
    cursor: pointer;
    font-size: 0.82rem;
    font-weight: 700;
    line-height: 1.4;
    text-align: center;
    word-break: keep-all;
    transition: filter 0.12s;
    margin: 0;
    width: 100%;
    box-sizing: border-box;
}
.wm-event-btn:hover { filter: brightness(0.96); }
.wm-event-btn.canceled { text-decoration: line-through; opacity: 0.65; }

/* 주간/월별 일정없음 텍스트 상단 정렬 */
.wm-no-schedule {
    font-size: 0.82rem;
    color: #9CA3AF;
    padding-top: 0px;
    margin-top: 0px;
}

@media (max-width: 1000px) {
    .block-container { padding-top: 2.2rem; }
    .main-title { font-size: 2.1rem; }
    .summary-title { font-size: 1.08rem; }
    .follow-grid { grid-template-columns: 1fr; }
    .summary-body { padding: 12px 13px 10px 13px; }
    .info-box { min-height: auto; }
}

/* ── GAP OVERRIDE ── */
[data-testid='stSidebar'] [data-testid='stVerticalBlock']:has(
    > div > [data-testid='stButton'],
    > div > [data-testid='stDownloadButton'],
    > div > [data-testid='stExpander']
) { gap: 4px !important; row-gap: 4px !important; }

[data-testid='stMain'] [data-testid='stVerticalBlock']:has(
    > div > [data-testid='stExpander']
) { gap: 4px !important; row-gap: 4px !important; }

[data-testid='column'] [data-testid='stVerticalBlock']:has(
    > div > [data-testid='stExpander']
) { gap: 4px !important; row-gap: 4px !important; }

</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. 유틸
# =========================================================
KST = ZoneInfo("Asia/Seoul")

def now_kst(): return datetime.now(KST)
def now_kst_str(): return now_kst().strftime("%Y-%m-%d %H:%M")

def safe_str(v):
    if v is None: return ""
    try:
        if pd.isna(v): return ""
    except Exception: pass
    return str(v).strip()

def normalize_cell(v):
    if v is None: return ""
    try:
        if pd.isna(v): return ""
    except Exception: pass
    if isinstance(v, pd.Timestamp):
        if pd.isna(v): return ""
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, datetime): return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, date): return v.strftime("%Y-%m-%d")
    if isinstance(v, time): return v.strftime("%H:%M")
    if isinstance(v, (list, dict, tuple, set)): return str(v)
    return str(v).strip()

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or not isinstance(df, pd.DataFrame):
        return pd.DataFrame(columns=DATA_COLUMNS)
    df = df.copy()
    for col in DATA_COLUMNS:
        if col not in df.columns: df[col] = ""
    df = df[DATA_COLUMNS].copy()
    for col in DATA_COLUMNS: df[col] = df[col].apply(normalize_cell)
    return df

def empty_df(): return pd.DataFrame(columns=DATA_COLUMNS)
def get_color(cat: str): return COLOR_MAP.get(cat, COLOR_MAP["기타"])
def category_slug(cat: str) -> str: return CAT_SLUG.get(cat, "etc")

def to_date_safe(v):
    text = safe_str(v)
    if not text: return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed): return None
    return parsed.date()

def parse_time_safe(v, default_str="09:00"):
    text = safe_str(v)
    if not text: text = default_str
    for fmt in ["%H:%M", "%H:%M:%S"]:
        try: return datetime.strptime(text, fmt).time()
        except Exception: continue
    return datetime.strptime(default_str, "%H:%M").time()

def esc(v):
    value = safe_str(v)
    return html.escape(value if value else "-")

def is_president_attend(row): return safe_str(row.get("PresidentAttend", "")).upper() == "Y"
def attend_prefix(row): return "👑 " if is_president_attend(row) else ""
def attend_label(row): return "회장 직접 참석" if is_president_attend(row) else "직원 대참/회장 미참석"

def compact_subject_text(row):
    subject = f"{attend_prefix(row)}{safe_str(row.get('Subject'))}"
    if safe_str(row.get("Status")) == "취소": subject = f"{subject} (취소)"
    return subject

def compact_line_text(row):
    time_text = safe_str(row.get("Time")) or "-"
    cat_text  = safe_str(row.get("Category")) or "-"
    return f"{time_text} [{cat_text}] {compact_subject_text(row)}"

def excel_download_bytes(df: pd.DataFrame) -> bytes:
    export_df = get_active_df(df).copy()
    export_df = ensure_columns(export_df)
    export_df = export_df.drop(columns=["IsDeleted"], errors="ignore")
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Schedule")
    output.seek(0)
    return output.getvalue()

def get_secret_value(key: str, default=""):
    if key in st.secrets: return str(st.secrets.get(key, default)).strip()
    if "app_config" in st.secrets and key in st.secrets["app_config"]:
        return str(st.secrets["app_config"].get(key, default)).strip()
    return default

def get_sheet_config():
    return get_secret_value("google_sheet_name", ""), get_secret_value("google_worksheet_name", "")

def has_gsheet_config():
    sheet_name, worksheet_name = get_sheet_config()
    return ("gcp_service_account" in st.secrets) and bool(sheet_name) and bool(worksheet_name)

def column_letter(n: int) -> str:
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

LAST_COL_LETTER = column_letter(len(DATA_COLUMNS))

@st.cache_resource
def get_gspread_client():
    if "gcp_service_account" not in st.secrets: raise KeyError("gcp_service_account")
    creds_info  = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(credentials)

def get_worksheet():
    gc = get_gspread_client()
    sheet_name, worksheet_name = get_sheet_config()
    if not sheet_name: raise ValueError("google_sheet_name 이 설정되지 않았습니다.")
    if not worksheet_name: raise ValueError("google_worksheet_name 이 설정되지 않았습니다.")
    sh = gc.open(sheet_name)
    try:
        ws = sh.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet_name, rows=10000, cols=max(len(DATA_COLUMNS)+8, 40))
        ws.update(range_name=f"A1:{LAST_COL_LETTER}1", values=[DATA_COLUMNS])
    return ws

def ensure_sheet_header(ws):
    values = ws.get_all_values()
    if not values:
        ws.update(range_name=f"A1:{LAST_COL_LETTER}1", values=[DATA_COLUMNS]); return
    first_row = values[0]
    if first_row[:len(first_row)] == DATA_COLUMNS: return
    data_rows        = values[1:] if len(values) > 1 else []
    old_header_index = {col: idx for idx, col in enumerate(first_row)}
    rebuilt_rows = []
    for row in data_rows:
        new_row = []
        for col in DATA_COLUMNS:
            if col in old_header_index and old_header_index[col] < len(row):
                new_row.append(row[old_header_index[col]])
            else: new_row.append("")
        rebuilt_rows.append(new_row)
    new_values = [DATA_COLUMNS] + rebuilt_rows
    ws.clear()
    ws.update(range_name=f"A1:{LAST_COL_LETTER}{len(new_values)}", values=new_values)

def clean_records_df(df: pd.DataFrame) -> pd.DataFrame:
    df = ensure_columns(df)
    if df.empty: return df
    non_id_cols    = [c for c in DATA_COLUMNS if c != "ID"]
    mask_not_empty = df[non_id_cols].apply(lambda row: any(safe_str(v) for v in row), axis=1)
    df = df[mask_not_empty].copy()
    if df.empty: return ensure_columns(df)
    missing_id_mask = df["ID"].apply(lambda x: safe_str(x) == "")
    if missing_id_mask.any():
        for idx in df[missing_id_mask].index: df.at[idx, "ID"] = next_id()
    df["Category"]        = df["Category"].apply(lambda x: x if x in CATEGORIES else "기타")
    df["Status"]          = df["Status"].apply(lambda x: x if x in STATUS_OPTIONS else "확정")
    df["Priority"]        = df["Priority"].apply(lambda x: x if x in PRIORITY_OPTIONS else "보통")
    df["FollowStatus"]    = df["FollowStatus"].apply(lambda x: x if x in FOLLOW_STATUS_OPTIONS else "미착수")
    df["IsDeleted"]       = df["IsDeleted"].apply(lambda x: "Y" if safe_str(x).upper() == "Y" else "")
    df["PresidentAttend"] = df["PresidentAttend"].apply(lambda x: "Y" if safe_str(x).upper() == "Y" else "")
    df["Date"]            = df["Date"].apply(lambda x: to_date_safe(x).strftime("%Y-%m-%d") if to_date_safe(x) else "")
    df["Time"]            = df["Time"].apply(lambda x: parse_time_safe(x).strftime("%H:%M") if safe_str(x) else "")
    df["FollowDue"]       = df["FollowDue"].apply(lambda x: to_date_safe(x).strftime("%Y-%m-%d") if to_date_safe(x) else "")
    for col in ["FollowUpdated", "Updated", "UpdatedBy"]: df[col] = df[col].apply(lambda x: safe_str(x))
    df = df.drop_duplicates(subset=["ID"], keep="last").reset_index(drop=True)
    return ensure_columns(df)

def get_active_df(df: pd.DataFrame) -> pd.DataFrame:
    temp = clean_records_df(df)
    if temp.empty: return temp
    return temp[temp["IsDeleted"] != "Y"].reset_index(drop=True)

def load_data_from_gsheet():
    try:
        if not has_gsheet_config():
            if "gcp_service_account" not in st.secrets: st.info("구글 시트 연결 정보가 아직 설정되지 않았습니다.")
            else: st.info("google_sheet_name 또는 google_worksheet_name 설정이 없습니다.")
            return empty_df()
        ws      = get_worksheet()
        ensure_sheet_header(ws)
        records = ws.get_all_records(default_blank="")
        if not records: return empty_df()
        df = pd.DataFrame(records)
        return clean_records_df(df)
    except Exception as e:
        st.warning(f"구글 시트 데이터를 불러오지 못했습니다: {e}")
        return empty_df()

def find_row_number_by_id(ws, record_id: str):
    id_col_num = DATA_COLUMNS.index("ID") + 1
    id_values  = ws.col_values(id_col_num)
    for row_num in range(2, len(id_values) + 1):
        if safe_str(id_values[row_num - 1]) == safe_str(record_id): return row_num
    return None

def append_record_to_gsheet(record: dict):
    ws = get_worksheet(); ensure_sheet_header(ws)
    ws.append_row([normalize_cell(record.get(col, "")) for col in DATA_COLUMNS], value_input_option="USER_ENTERED")

def update_record_in_gsheet(record: dict):
    ws = get_worksheet(); ensure_sheet_header(ws)
    row_num    = find_row_number_by_id(ws, record["ID"])
    row_values = [normalize_cell(record.get(col, "")) for col in DATA_COLUMNS]
    if row_num is None: ws.append_row(row_values, value_input_option="USER_ENTERED")
    else: ws.update(range_name=f"A{row_num}:{LAST_COL_LETTER}{row_num}", values=[row_values])

def soft_delete_record_in_gsheet(record_id: str):
    ws = get_worksheet(); ensure_sheet_header(ws)
    row_num = find_row_number_by_id(ws, record_id)
    if row_num is None: return
    row_values = ws.row_values(row_num)
    row_values = row_values[:len(DATA_COLUMNS)] + [""] * max(0, len(DATA_COLUMNS) - len(row_values))
    temp = {col: row_values[idx] if idx < len(row_values) else "" for idx, col in enumerate(DATA_COLUMNS)}
    temp["IsDeleted"] = "Y"; temp["Updated"] = now_kst_str()
    ws.update(range_name=f"A{row_num}:{LAST_COL_LETTER}{row_num}",
              values=[[normalize_cell(temp.get(col, "")) for col in DATA_COLUMNS]])

def get_filtered_df(df, selected_cat="카테고리", search_text="", status_filter="일정 현황", follow_status_filter="팔로우업 상태"):
    temp = get_active_df(df).copy()
    temp["DateParsed"] = pd.to_datetime(temp["Date"], errors="coerce").dt.date
    if selected_cat not in ["전체", "카테고리"]: temp = temp[temp["Category"] == selected_cat]
    if status_filter not in ["전체", "일정 현황"]: temp = temp[temp["Status"] == status_filter]
    if follow_status_filter not in ["전체", "팔로우업 상태"]: temp = temp[temp["FollowStatus"] == follow_status_filter]
    if search_text:
        q    = str(search_text).strip()
        mask = (
            temp["Subject"].fillna("").str.contains(q, case=False, na=False)
            | temp["OrgName"].fillna("").str.contains(q, case=False, na=False)
            | temp["DetailPlace"].fillna("").str.contains(q, case=False, na=False)
            | temp["TargetDept"].fillna("").str.contains(q, case=False, na=False)
            | temp["TargetName"].fillna("").str.contains(q, case=False, na=False)
            | temp["TargetContact"].fillna("").str.contains(q, case=False, na=False)
            | temp["FollowOwner"].fillna("").str.contains(q, case=False, na=False)
            | temp["FollowTask"].fillna("").str.contains(q, case=False, na=False)
            | temp["Memo"].fillna("").str.contains(q, case=False, na=False)
            | temp["FollowProgressMemo"].fillna("").str.contains(q, case=False, na=False)
            | temp["UpdatedBy"].fillna("").str.contains(q, case=False, na=False)
            | temp["Staff"].fillna("").str.contains(q, case=False, na=False)
        )
        temp = temp[mask]
    return temp

def week_dates_from_any_day(any_day: date):
    start = any_day - timedelta(days=(any_day.weekday() + 1) % 7)
    return [start + timedelta(days=i) for i in range(7)]

def month_calendar_weeks(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)
    return cal.monthdatescalendar(year, month)

def next_id(): return now_kst().strftime("%Y%m%d%H%M%S%f")

def save_record(record: dict, is_edit=False):
    record = {col: normalize_cell(record.get(col, "")) for col in DATA_COLUMNS}
    record["Updated"]         = now_kst_str()
    record["UpdatedBy"]       = safe_str(record.get("UpdatedBy", ""))
    record["IsDeleted"]       = ""
    record["PresidentAttend"] = "Y" if safe_str(record.get("PresidentAttend", "")).upper() == "Y" else ""
    try:
        if has_gsheet_config():
            if is_edit: update_record_in_gsheet(record)
            else: append_record_to_gsheet(record)
            st.session_state.data = load_data_from_gsheet()
            return True, None
        current = clean_records_df(st.session_state.data)
        if is_edit:
            mask = current["ID"].astype(str) == str(record["ID"])
            if mask.any():
                for col in DATA_COLUMNS: current.loc[mask, col] = record[col]
            else: current = pd.concat([current, pd.DataFrame([record])], ignore_index=True)
        else: current = pd.concat([current, pd.DataFrame([record])], ignore_index=True)
        st.session_state.data = clean_records_df(current)
        return True, None
    except Exception as e: return False, str(e)

def soft_delete_record(record_id: str):
    try:
        if has_gsheet_config():
            soft_delete_record_in_gsheet(record_id)
            st.session_state.data = load_data_from_gsheet()
            return True, None
        current = clean_records_df(st.session_state.data)
        mask = current["ID"].astype(str) == str(record_id)
        if mask.any():
            current.loc[mask, "IsDeleted"] = "Y"
            current.loc[mask, "Updated"]   = now_kst_str()
        st.session_state.data = clean_records_df(current)
        return True, None
    except Exception as e: return False, str(e)

def update_follow_status(record_id: str, new_status: str):
    try:
        current = clean_records_df(st.session_state.data)
        target  = current[current["ID"].astype(str) == str(record_id)]
        if target.empty: return False, "대상 일정을 찾지 못했습니다."
        row = target.iloc[0].to_dict()
        row["FollowStatus"]  = new_status
        row["FollowUpdated"] = now_kst_str()
        row["Updated"]       = now_kst_str()
        if has_gsheet_config():
            update_record_in_gsheet(row)
            st.session_state.data = load_data_from_gsheet()
        else:
            mask = current["ID"].astype(str) == str(record_id)
            for col in DATA_COLUMNS: current.loc[mask, col] = normalize_cell(row.get(col, ""))
            st.session_state.data = clean_records_df(current)
        return True, None
    except Exception as e: return False, str(e)

def contact_text(row):
    parts = []
    if safe_str(row.get("TargetDept")):    parts.append(f"부서: {row['TargetDept']}")
    if safe_str(row.get("TargetName")):    parts.append(f"이름: {row['TargetName']}")
    if safe_str(row.get("TargetContact")): parts.append(f"연락처: {row['TargetContact']}")
    return " / ".join(parts) if parts else "-"

def show_flash():
    if st.session_state.flash_message:
        msg = st.session_state.flash_message
        if "실패" in str(msg): st.warning(msg)
        else: st.success(msg)
        st.session_state.flash_message = None

def render_legend():
    parts = []
    for cat in CATEGORIES:
        c = get_color(cat)
        parts.append(f'<span class="legend-pill" style="background:{c["soft"]};color:{c["text"]};border-color:{c["line"]};">{cat}</span>')
    st.markdown("".join(parts), unsafe_allow_html=True)
    st.markdown('<div class="segment-note">👑 표시가 있으면 회장 직접 참석 일정입니다.</div>', unsafe_allow_html=True)

def render_metric_chips(day_count, confirmed_count, pending_count, cancel_count):
    st.markdown(f"""
    <span class="metric-chip">선택일 {day_count}</span>
    <span class="metric-chip">확정 {confirmed_count}</span>
    <span class="metric-chip">보류 {pending_count}</span>
    <span class="metric-chip">취소 {cancel_count}</span>
    """, unsafe_allow_html=True)

def format_subject_html(row):
    subject      = esc(safe_str(attend_prefix(row)) + safe_str(row["Subject"]))
    attend_badge = '<span class="attend-pill">회장 참석</span>' if is_president_attend(row) else ""
    if safe_str(row["Status"]) == "취소":
        return f'<span class="canceled-title">{subject}</span>{attend_badge}<span class="cancel-pill">취소</span>'
    return f'{subject}{attend_badge}'

def weekday_class_by_index(idx: int):
    if idx == 0: return "sun"
    if idx == 6: return "sat"
    return ""

def weekday_class_by_date(d: date):
    if d.weekday() == 6: return "sun"
    if d.weekday() == 5: return "sat"
    return ""

def day_header_html(day_obj: date, text: str, dim: bool = False):
    cls     = weekday_class_by_date(day_obj)
    classes = "day-head" + (" dim" if dim else "") + (f" {cls}" if cls else "")
    return f"<div class='{classes}'>{text}</div>"

def sort_latest_first(df: pd.DataFrame):
    if df is None or len(df) == 0: return df
    df = df.copy()
    df["DateSort"]    = pd.to_datetime(df["Date"], errors="coerce")
    df["TimeSort"]    = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce")
    df["UpdatedSort"] = pd.to_datetime(df["Updated"], errors="coerce")
    df = df.sort_values(by=["DateSort","TimeSort","UpdatedSort"], ascending=[False,False,False], na_position="last")
    return df.drop(columns=["DateSort","TimeSort","UpdatedSort"], errors="ignore")

def sort_oldest_first(df: pd.DataFrame):
    if df is None or len(df) == 0: return df
    df = df.copy()
    df["DateSort"]    = pd.to_datetime(df["Date"], errors="coerce")
    df["TimeSort"]    = pd.to_datetime(df["Time"], format="%H:%M", errors="coerce")
    df["UpdatedSort"] = pd.to_datetime(df["Updated"], errors="coerce")
    df = df.sort_values(by=["DateSort","TimeSort","UpdatedSort"], ascending=[True,True,False], na_position="last")
    return df.drop(columns=["DateSort","TimeSort","UpdatedSort"], errors="ignore")

def to_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    display_df = ensure_columns(df).copy()
    if display_df.empty: return display_df.drop(columns=["IsDeleted"], errors="ignore")
    for col in display_df.columns: display_df[col] = display_df[col].apply(normalize_cell)
    display_df = display_df.fillna("")
    display_df = display_df.drop(columns=["IsDeleted","DateParsed"], errors="ignore")
    return display_df


# =========================================================
# 5. 상태 초기화
# =========================================================
today = now_kst().date()

if "data" not in st.session_state: st.session_state.data = load_data_from_gsheet()
else: st.session_state.data = clean_records_df(st.session_state.data)

if "app_today" not in st.session_state: st.session_state.app_today = today
if st.session_state.app_today != today:
    st.session_state.app_today    = today
    st.session_state.selected_date = today

for key, val in [
    ("main_menu", "📅 일정 보기"),
    ("selected_date", today),
    ("selected_cat", "카테고리"),
    ("selected_status", "일정 현황"),
    ("selected_follow_status", "팔로우업 상태"),
    ("search_text", ""),
    ("edit_id", None),
    ("flash_message", None),
    ("reload_password_input", ""),
    ("show_reload_password", False),
    ("table_page_num_value", 1),
    ("sidebar_preview_open", False),
    ("wm_expanded", {}),
]:
    if key not in st.session_state: st.session_state[key] = val

# =========================================================
# 5-1. 날짜 선택 콜백
# =========================================================
def _on_date_change():
    st.session_state.selected_date = st.session_state._date_input_main

# =========================================================
# 6. 렌더 함수
# =========================================================
def render_followup_section(row):
    st.markdown(f"""
    <div class="follow-wrap">
        <div class="follow-title">📌 사무처 팔로우업 핵심 영역</div>
        <div style="margin-bottom:8px;">
            <span class="follow-pill">팔로우업 상태: {esc(row["FollowStatus"])}</span>
            <span class="follow-pill">주 담당자: {esc(row["FollowOwner"])}</span>
            <span class="follow-pill">준비기한: {esc(row["FollowDue"])}</span>
        </div>
        <div class="follow-grid">
            <div class="follow-box"><div class="follow-label">회의 목적</div><div class="follow-value">{esc(row["Purpose"])}</div></div>
            <div class="follow-box"><div class="follow-label">대응 방향</div><div class="follow-value">{esc(row["ActionPlan"])}</div></div>
            <div class="follow-box"><div class="follow-label">후속/준비사항</div><div class="follow-value">{esc(row["FollowTask"])}</div></div>
            <div class="follow-box"><div class="follow-label">진행 메모</div><div class="follow-value">{esc(row["FollowProgressMemo"])}</div></div>
            <div class="follow-box"><div class="follow-label">공유 메모</div><div class="follow-value">{esc(row["SharedNote"])}</div></div>
            <div class="follow-box"><div class="follow-label">최종 추적일</div><div class="follow-value">{esc(row["FollowUpdated"])}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_summary_header(row):
    c = get_color(row["Category"])
    attend_badge = '<span class="tag-pill">👑 회장 직접 참석</span>' if is_president_attend(row) else '<span class="tag-pill">대참 가능 일정</span>'
    st.markdown(f"""
    <div class="summary-card" style="background:{c['bg']};">
        <div class="summary-inner">
            <div class="summary-accent" style="background:{c['line']};"></div>
            <div class="summary-body">
                <div class="summary-meta" style="color:{c['text']};">
                    ⏰ {esc(row["Time"])}
                    <span class="tag-pill" style="background:{c['soft']};color:{c['text']};border-color:{c['line']};">{esc(row["Category"])}</span>
                    <span class="tag-pill">{esc(row["Status"])}</span>
                    <span class="tag-pill">우선순위 {esc(row["Priority"])}</span>
                    <span class="tag-pill">팔로우업 {esc(row["FollowStatus"])}</span>
                    {attend_badge}
                </div>
                <div class="summary-title">{format_subject_html(row)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_detail_blocks(row):
    left_items = [
        ("방문기관명", f"🏢 {esc(row['OrgName'])}"),
        ("회의장소(세부)", f"📍 {esc(row['DetailPlace'])}"),
        ("보좌관/비서/담당자 정보", f"👤 {html.escape(contact_text(row))}"),
    ]
    right_items = [
        ("회장님 외 동행인", f"👥 {esc(row['Companion'])}"),
        ("사무처 수행직원", f"🧾 {esc(row['Staff'])}"),
        ("참석 구분 / 최종 수정", f"👑 {esc(attend_label(row))}<br>🕒 {esc(row['Updated'])} / {esc(row['UpdatedBy'])}"),
    ]
    if st.session_state.get("is_mobile_force_stack", False):
        for label, value in left_items + right_items:
            st.markdown(f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value">{value}</div></div>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            for label, value in left_items:
                st.markdown(f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value">{value}</div></div>', unsafe_allow_html=True)
        with c2:
            for label, value in right_items:
                st.markdown(f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value">{value}</div></div>', unsafe_allow_html=True)
    render_followup_section(row)
    st.markdown(f'<div class="memo-box"><div class="memo-title">📌 일반 메모</div><div class="memo-text">{esc(row["Memo"])}</div></div>', unsafe_allow_html=True)

def render_action_buttons_full(row, prefix=""):
    st.markdown('<div class="small-action">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([0.8, 0.9, 0.8, 1.0, 1.0])
    if c1.button("수정", key=f"{prefix}_edit_{row['ID']}", use_container_width=True):
        st.session_state.edit_id = row["ID"]; st.rerun()
    toggle_label = "일정 취소" if row["Status"] != "취소" else "취소 해제"
    toggle_next  = "취소"     if row["Status"] != "취소" else "확정"
    if c2.button(toggle_label, key=f"{prefix}_cancel_{row['ID']}", use_container_width=True):
        current = clean_records_df(st.session_state.data)
        target  = current[current["ID"].astype(str) == str(row["ID"])]
        if not target.empty:
            new_row = target.iloc[0].to_dict()
            new_row["Status"] = toggle_next; new_row["Updated"] = now_kst_str()
            new_row["UpdatedBy"] = safe_str(row["UpdatedBy"])
            ok, err = save_record(new_row, is_edit=True)
            st.session_state.flash_message = "상태가 변경되었습니다." if ok else f"변경 실패: {err}"
            st.rerun()
    if c3.button("삭제", key=f"{prefix}_delete_{row['ID']}", use_container_width=True):
        ok, err = soft_delete_record(row["ID"])
        if st.session_state.edit_id == row["ID"]: st.session_state.edit_id = None
        st.session_state.flash_message = "삭제되었습니다." if ok else f"삭제 실패: {err}"
        st.rerun()
    if c4.button("진행중", key=f"{prefix}_follow_inprogress_{row['ID']}", use_container_width=True):
        ok, err = update_follow_status(row["ID"], "진행중")
        st.session_state.flash_message = "팔로우업: 진행중" if ok else f"실패: {err}"
        st.rerun()
    if c5.button("완료", key=f"{prefix}_follow_done_{row['ID']}", use_container_width=True):
        ok, err = update_follow_status(row["ID"], "완료")
        st.session_state.flash_message = "팔로우업: 완료" if ok else f"실패: {err}"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_action_buttons_compact(row, prefix=""):
    st.markdown('<div class="small-action">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("수정", key=f"{prefix}_edit_{row['ID']}", use_container_width=True):
        st.session_state.edit_id = row["ID"]; st.rerun()
    toggle_label = "취소" if row["Status"] != "취소" else "취소해제"
    toggle_next  = "취소" if row["Status"] != "취소" else "확정"
    if c2.button(toggle_label, key=f"{prefix}_cancel_{row['ID']}", use_container_width=True):
        current = clean_records_df(st.session_state.data)
        target  = current[current["ID"].astype(str) == str(row["ID"])]
        if not target.empty:
            new_row = target.iloc[0].to_dict()
            new_row["Status"] = toggle_next; new_row["Updated"] = now_kst_str()
            ok, err = save_record(new_row, is_edit=True)
            st.session_state.flash_message = "상태가 변경되었습니다." if ok else f"변경 실패: {err}"
            st.rerun()
    if c3.button("삭제", key=f"{prefix}_delete_{row['ID']}", use_container_width=True):
        ok, err = soft_delete_record(row["ID"])
        if st.session_state.edit_id == row["ID"]: st.session_state.edit_id = None
        st.session_state.flash_message = "삭제되었습니다." if ok else f"삭제 실패: {err}"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_compact_event(row, prefix=""):
    label = compact_line_text(row)
    with st.expander(label, expanded=False):
        render_summary_header(row)
        render_detail_blocks(row)
        render_action_buttons_full(row, prefix=prefix)
    st.markdown('<div style="margin-top:-14px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top:-12px;"></div>', unsafe_allow_html=True)


# =========================================================
# render_week_month_event  (완전 재작성)
# - st.button + JavaScript 스타일 주입 방식 제거
# - 순수 HTML 컬러 버튼 + st.session_state 토글
# - 펼침/접힘이 rerun 없이 즉시 반영 (초기 상태 기반)
# - 다른 뷰에 영향 없음
# =========================================================
def render_week_month_event(row, prefix=""):
    c         = get_color(safe_str(row.get("Category", "기타")))
    time_txt  = safe_str(row.get("Time", ""))
    cat_txt   = safe_str(row.get("Category", "기타"))
    subject   = compact_subject_text(row)
    is_cancel = safe_str(row.get("Status")) == "취소"

    row_id     = safe_str(row.get("ID", ""))
    toggle_key = f"wm_toggle_{prefix}_{row_id}"
    is_open    = st.session_state.wm_expanded.get(toggle_key, False)

    if time_txt:
        label = f"{time_txt} [{cat_txt}] {subject}"
    else:
        label = f"[{cat_txt}] {subject}"

    label_style = "text-decoration:line-through;opacity:0.65;" if is_cancel else ""

    btn_js_id = "wmbtn_" + "".join(ch if ch.isalnum() else "_" for ch in toggle_key)

    st.markdown(f"""
<div data-btnid="{btn_js_id}" style="display:none;height:0;margin:0;padding:0;overflow:hidden;"></div>
<script>
(function(){{
  function applyStyle(){{
    var marker = document.querySelector('div[data-btnid="{btn_js_id}"]');
    if(!marker) return;
    var parent = marker.closest('[data-testid="stMarkdown"]') || marker.parentElement;
    var sib = parent;
    var btn = null;
    var limit = 8;
    while(sib && limit > 0){{
      sib = sib.nextElementSibling;
      limit--;
      if(!sib) break;
      var b = sib.querySelector('button');
      if(b){{ btn = b; break; }}
    }}
    if(!btn) return;
    btn.style.setProperty('background', '{c["bg"]}', 'important');
    btn.style.setProperty('border', '1.5px solid {c["line"]}', 'important');
    btn.style.setProperty('color', '{c["text"]}', 'important');
    btn.style.setProperty('border-radius', '14px', 'important');
    btn.style.setProperty('font-weight', '700', 'important');
    btn.style.setProperty('font-size', '0.82rem', 'important');
    btn.style.setProperty('text-align', 'center', 'important');
    btn.style.setProperty('padding', '10px 12px', 'important');
    btn.style.setProperty('white-space', 'normal', 'important');
    btn.style.setProperty('word-break', 'keep-all', 'important');
    btn.style.setProperty('height', 'auto', 'important');
    btn.style.setProperty('min-height', '0', 'important');
    btn.style.setProperty('line-height', '1.4', 'important');
    btn.style.setProperty('margin-top', '0', 'important');
    btn.style.setProperty('margin-bottom', '2px', 'important');
    if('{label_style}'){{
      btn.style.setProperty('text-decoration', 'line-through', 'important');
      btn.style.setProperty('opacity', '0.65', 'important');
    }}
    // 버튼의 부모 stButton wrapper 간격도 제거
    var wrap = btn.closest('[data-testid="stButton"]');
    if(wrap){{
      wrap.style.setProperty('margin-top', '0', 'important');
      wrap.style.setProperty('margin-bottom', '0', 'important');
    }}
  }}
  if(document.readyState === 'loading'){{
    document.addEventListener('DOMContentLoaded', applyStyle);
  }} else {{
    setTimeout(applyStyle, 0);
    setTimeout(applyStyle, 100);
    setTimeout(applyStyle, 300);
  }}
}})();
</script>
""", unsafe_allow_html=True)

    if st.button(label, key=toggle_key, use_container_width=True):
        st.session_state.wm_expanded[toggle_key] = not is_open
        st.rerun()

    if is_open:
        st.markdown(f"""
<div style="border:1px solid {c['line']};border-top:none;background:{c['bg']};
            border-radius:0 0 12px 12px;padding:8px 10px 6px 10px;margin-top:-6px;">
  <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;">
    <span style="background:{c['soft']};color:{c['text']};border:1px solid {c['line']};
                 border-radius:999px;padding:2px 8px;font-size:0.70rem;font-weight:800;">{esc(cat_txt)}</span>
    <span style="background:#F3F4F6;color:#374151;border:1px solid #D1D5DB;
                 border-radius:999px;padding:2px 8px;font-size:0.70rem;font-weight:700;">{esc(row.get('Status',''))}</span>
    <span style="background:#F3F4F6;color:#374151;border:1px solid #D1D5DB;
                 border-radius:999px;padding:2px 8px;font-size:0.70rem;font-weight:700;">우선순위 {esc(row.get('Priority',''))}</span>
    <span style="background:#F3F4F6;color:#374151;border:1px solid #D1D5DB;
                 border-radius:999px;padding:2px 8px;font-size:0.70rem;font-weight:700;">{'👑 회장 직접 참석' if is_president_attend(row) else '대참 가능'}</span>
    <span style="background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;
                 border-radius:999px;padding:2px 8px;font-size:0.70rem;font-weight:700;">팔로우 {esc(row.get('FollowStatus',''))}</span>
  </div>
  <div class="wm-detail-grid">
    <div class="wm-detail-cell"><div class="wm-detail-label">일정 날짜</div><div class="wm-detail-value">{esc(row.get('Date',''))}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">일정 시간</div><div class="wm-detail-value">{esc(row.get('Time',''))}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">카테고리</div><div class="wm-detail-value" style="color:{c['text']};font-weight:700;">{esc(cat_txt)}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">일정 현황</div><div class="wm-detail-value">{esc(row.get('Status',''))}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">우선순위</div><div class="wm-detail-value">{esc(row.get('Priority',''))}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">회장직접참석 여부</div><div class="wm-detail-value">{'👑 직접 참석' if is_president_attend(row) else '대참 가능'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">회의명</div><div class="wm-detail-value" style="font-weight:700;{'text-decoration:line-through;opacity:0.65;' if is_cancel else ''}">{esc(row.get('Subject',''))}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">방문기관명</div><div class="wm-detail-value">{esc(row.get('OrgName','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">회장님 외 동행인</div><div class="wm-detail-value">{esc(row.get('Companion','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">주 담당자</div><div class="wm-detail-value">{esc(row.get('FollowOwner','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">팔로우업 상태</div><div class="wm-detail-value">{esc(row.get('FollowStatus',''))}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">회의 목적</div><div class="wm-detail-value">{esc(row.get('Purpose','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">후속/준비사항</div><div class="wm-detail-value">{esc(row.get('FollowTask','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">진행 메모</div><div class="wm-detail-value">{esc(row.get('FollowProgressMemo','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">공유 메모</div><div class="wm-detail-value">{esc(row.get('SharedNote','')) or '—'}</div></div>
    <div class="wm-detail-cell"><div class="wm-detail-label">일반 메모</div><div class="wm-detail-value">{esc(row.get('Memo','')) or '—'}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)
        render_action_buttons_compact(row, prefix=prefix)



def render_form(mode="new", row_data=None):
    if row_data is None:
        row_data = {
            "ID":"","Date":now_kst().strftime("%Y-%m-%d"),"Time":"09:00",
            "Category":CATEGORIES[0],"Subject":"","PresidentAttend":"Y",
            "OrgName":"","DetailPlace":"","TargetDept":"","TargetName":"",
            "TargetContact":"","Companion":"","Staff":"","Purpose":"",
            "ActionPlan":"","Memo":"","Status":"확정","Priority":"보통",
            "FollowOwner":"","FollowTask":"","FollowDue":"","SharedNote":"",
            "FollowStatus":"미착수","FollowProgressMemo":"","FollowUpdated":"",
            "Updated":"","IsDeleted":"","UpdatedBy":"",
        }
    title = "✍️ 신규 일정 등록" if mode == "new" else "🛠️ 일정 수정"
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

    with st.form(f"form_{mode}", clear_on_submit=False):
        r1c1, r1c2, r1c3 = st.columns(3)
        input_date     = r1c1.date_input("일정 날짜", value=to_date_safe(row_data["Date"]) or now_kst().date())
        input_time     = r1c2.time_input("일정 시간", value=parse_time_safe(row_data["Time"]))
        input_category = r1c3.selectbox("카테고리", CATEGORIES,
                            index=CATEGORIES.index(row_data["Category"]) if row_data["Category"] in CATEGORIES else 0)

        r2c1,r2c2,r2c3,r2c4,r2c5 = st.columns([2.1,1.0,1.0,1.2,1.1])
        input_subject  = r2c1.text_input("회의명", value=safe_str(row_data["Subject"]))
        input_status   = r2c2.selectbox("일정 현황", STATUS_OPTIONS,
                            index=STATUS_OPTIONS.index(row_data["Status"]) if row_data["Status"] in STATUS_OPTIONS else 0)
        input_priority = r2c3.selectbox("우선순위", PRIORITY_OPTIONS,
                            index=PRIORITY_OPTIONS.index(row_data["Priority"]) if row_data["Priority"] in PRIORITY_OPTIONS else 1)
        input_editor_name      = r2c4.text_input("작성자/수정자 이름", value=safe_str(row_data["UpdatedBy"]), placeholder="예: 홍길동")
        input_president_attend = r2c5.checkbox("회장 직접 참석", value=is_president_attend(row_data))

        r3c1,r3c2 = st.columns(2)
        input_org          = r3c1.text_input("방문기관명", value=safe_str(row_data["OrgName"]))
        input_detail_place = r3c2.text_input("회의장소(세부)", value=safe_str(row_data["DetailPlace"]))

        r4c1,r4c2,r4c3 = st.columns(3)
        input_target_dept    = r4c1.text_input("보좌관/비서/담당자 부서", value=safe_str(row_data["TargetDept"]))
        input_target_name    = r4c2.text_input("보좌관/비서/담당자 이름", value=safe_str(row_data["TargetName"]))
        input_target_contact = r4c3.text_input("보좌관/비서/담당자 연락처", value=safe_str(row_data["TargetContact"]))

        r5c1,r5c2 = st.columns(2)
        input_companion = r5c1.text_input("회장님 외 동행인", value=safe_str(row_data["Companion"]))
        input_staff     = r5c2.text_input("사무처 수행직원", value=safe_str(row_data["Staff"]))

        st.markdown("#### 📌 사무처 팔로우업 입력")
        input_purpose = st.text_area("회의 목적", value=safe_str(row_data["Purpose"]), height=90)
        input_action  = st.text_area("대응 방향", value=safe_str(row_data["ActionPlan"]), height=90)

        r6c1,r6c2,r6c3 = st.columns(3)
        input_follow_owner  = r6c1.text_input("주 담당자", value=safe_str(row_data["FollowOwner"]))
        existing_follow_due = to_date_safe(row_data["FollowDue"])
        input_follow_due    = r6c2.date_input("준비 완료기한", value=existing_follow_due or input_date,
                                               key=f"follow_due_date_{mode}_{safe_str(row_data['ID']) or 'new'}")
        input_follow_status = r6c3.selectbox("팔로우업 상태", FOLLOW_STATUS_OPTIONS,
                                  index=FOLLOW_STATUS_OPTIONS.index(row_data["FollowStatus"]) if row_data["FollowStatus"] in FOLLOW_STATUS_OPTIONS else 0)

        input_follow_task     = st.text_area("후속/준비사항",  value=safe_str(row_data["FollowTask"]),         height=100)
        input_follow_progress = st.text_area("진행 메모",      value=safe_str(row_data["FollowProgressMemo"]), height=80)
        input_shared_note     = st.text_area("공유 메모",      value=safe_str(row_data["SharedNote"]),         height=90)
        input_memo            = st.text_area("일반 Memo",      value=safe_str(row_data["Memo"]),               height=80)

        follow_due_value = str(input_follow_due) if input_follow_due else ""

        if mode == "new":
            b1, b2 = st.columns(2)
            submit_view     = b1.form_submit_button("저장 후 일정 보기",  use_container_width=True)
            submit_continue = b2.form_submit_button("저장 후 계속 등록", use_container_width=True)
            if submit_view or submit_continue:
                if not safe_str(input_subject): st.warning("회의명은 입력해 주세요.")
                elif not safe_str(input_editor_name): st.warning("작성자/수정자 이름은 입력해 주세요.")
                else:
                    record = {
                        "ID":next_id(),"Date":str(input_date),"Time":input_time.strftime("%H:%M"),
                        "Category":input_category,"Subject":safe_str(input_subject),
                        "PresidentAttend":"Y" if input_president_attend else "",
                        "OrgName":safe_str(input_org),"DetailPlace":safe_str(input_detail_place),
                        "TargetDept":safe_str(input_target_dept),"TargetName":safe_str(input_target_name),
                        "TargetContact":safe_str(input_target_contact),"Companion":safe_str(input_companion),
                        "Staff":safe_str(input_staff),"Purpose":safe_str(input_purpose),
                        "ActionPlan":safe_str(input_action),"Memo":safe_str(input_memo),
                        "Status":input_status,"Priority":input_priority,
                        "FollowOwner":safe_str(input_follow_owner),"FollowTask":safe_str(input_follow_task),
                        "FollowDue":follow_due_value,"SharedNote":safe_str(input_shared_note),
                        "FollowStatus":input_follow_status,"FollowProgressMemo":safe_str(input_follow_progress),
                        "FollowUpdated":now_kst_str(),"Updated":"","IsDeleted":"",
                        "UpdatedBy":safe_str(input_editor_name),
                    }
                    ok, err = save_record(record, is_edit=False)
                    st.session_state.selected_date = input_date
                    st.session_state.edit_id       = None
                    st.session_state.flash_message = "신규 일정이 저장되었습니다." if ok else f"저장 실패: {err}"
                    st.session_state.main_menu     = "📅 일정 보기" if submit_view else "✍️ 신규 일정 등록"
                    st.rerun()
        else:
            b1, b2 = st.columns(2)
            save_btn   = b1.form_submit_button("수정 저장", use_container_width=True)
            cancel_btn = b2.form_submit_button("수정 취소", use_container_width=True)
            if save_btn:
                if not safe_str(input_subject): st.warning("회의명은 입력해 주세요.")
                elif not safe_str(input_editor_name): st.warning("작성자/수정자 이름은 입력해 주세요.")
                else:
                    record = {
                        "ID":row_data["ID"],"Date":str(input_date),"Time":input_time.strftime("%H:%M"),
                        "Category":input_category,"Subject":safe_str(input_subject),
                        "PresidentAttend":"Y" if input_president_attend else "",
                        "OrgName":safe_str(input_org),"DetailPlace":safe_str(input_detail_place),
                        "TargetDept":safe_str(input_target_dept),"TargetName":safe_str(input_target_name),
                        "TargetContact":safe_str(input_target_contact),"Companion":safe_str(input_companion),
                        "Staff":safe_str(input_staff),"Purpose":safe_str(input_purpose),
                        "ActionPlan":safe_str(input_action),"Memo":safe_str(input_memo),
                        "Status":input_status,"Priority":input_priority,
                        "FollowOwner":safe_str(input_follow_owner),"FollowTask":safe_str(input_follow_task),
                        "FollowDue":follow_due_value,"SharedNote":safe_str(input_shared_note),
                        "FollowStatus":input_follow_status,"FollowProgressMemo":safe_str(input_follow_progress),
                        "FollowUpdated":now_kst_str(),"Updated":"","IsDeleted":"",
                        "UpdatedBy":safe_str(input_editor_name),
                    }
                    ok, err = save_record(record, is_edit=True)
                    st.session_state.edit_id       = None
                    st.session_state.selected_date = input_date
                    st.session_state.flash_message = "일정이 수정되었습니다." if ok else f"수정 실패: {err}"
                    st.rerun()
            if cancel_btn:
                st.session_state.edit_id = None; st.rerun()


# =========================================================
# 7. 사이드바
# =========================================================
st.sidebar.markdown("# 🏢 KVMA Secretary")

selected_day_sidebar = get_active_df(st.session_state.data).copy()
selected_day_sidebar["DateParsed"] = pd.to_datetime(selected_day_sidebar["Date"], errors="coerce").dt.date
selected_day_sidebar = selected_day_sidebar[selected_day_sidebar["DateParsed"] == st.session_state.selected_date]
selected_day_sidebar = sort_oldest_first(selected_day_sidebar)

sidebar_top = st.sidebar.container()

with sidebar_top:
    if st.button("📅 일정 보기", use_container_width=True):
        st.session_state.main_menu     = "📅 일정 보기"
        st.session_state.selected_date = today
        st.session_state.edit_id       = None
        st.rerun()
    st.markdown('<div style="margin-top:-14px;"></div>', unsafe_allow_html=True)

    if st.button("✍️ 신규 일정 등록", use_container_width=True):
        st.session_state.main_menu = "✍️ 신규 일정 등록"; st.rerun()
    st.markdown('<div style="margin-top:-14px;"></div>', unsafe_allow_html=True)

    xlsx_bytes = excel_download_bytes(st.session_state.data)
    st.download_button(
        "📥 일정 엑셀 다운로드", data=xlsx_bytes,
        file_name=f"kvma_schedule_{now_kst().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.markdown('<div style="margin-top:-14px;"></div>', unsafe_allow_html=True)

    preview_open     = st.session_state.sidebar_preview_open
    arrow_icon       = "▲" if preview_open else "▼"
    preview_date_str = str(st.session_state.selected_date)

    if st.button(
        f"📊 선택일 일정 미리보기\n{preview_date_str}  {arrow_icon}",
        use_container_width=True,
        key="sidebar_preview_toggle_btn"
    ):
        st.session_state.sidebar_preview_open = not preview_open
        st.rerun()

    if st.session_state.sidebar_preview_open:
        if selected_day_sidebar.empty:
            st.caption("선택한 날짜의 일정이 없습니다.")
        else:
            # ── 사이드바 미리보기: 모든 박스를 단일 HTML로 묶어 출력 ──
            parts = []
            for i, (_, row) in enumerate(selected_day_sidebar.iterrows()):
                c = get_color(row["Category"])
                mt = "8px" if i > 0 else "0px"
                parts.append(
                    f'<div style="'
                    f'border:1px solid {c["line"]};'
                    f'border-radius:12px;'
                    f'padding:8px 10px;'
                    f'background:{c["bg"]};'
                    f'display:block;'
                    f'margin-top:{mt};'
                    f'">'
                    f'<div style="font-size:0.78rem;font-weight:800;color:{c["text"]};margin-bottom:4px;">'
                    f'{html.escape(safe_str(row["Time"]))} · {html.escape(safe_str(row["Category"]))} · {html.escape(safe_str(row["FollowStatus"]))}'
                    f'</div>'
                    f'<div style="font-size:0.86rem;font-weight:700;color:#1F2937;line-height:1.35;">'
                    f'{html.escape(compact_subject_text(row))}'
                    f'</div>'
                    f'</div>'
                )
            st.markdown("".join(parts), unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="helper-note">구글 시트 다시 불러오기는 맨 아래에서 비밀번호 입력 후 실행할 수 있습니다.</div>', unsafe_allow_html=True)

if st.sidebar.button("🔒 구글 시트 다시 불러오기 열기", use_container_width=True):
    st.session_state.show_reload_password = not st.session_state.show_reload_password

if st.session_state.show_reload_password:
    password_input = st.sidebar.text_input("관리자 비밀번호", type="password", key="reload_password_input")
    if st.sidebar.button("🔄 구글 시트에서 다시 불러오기 실행", use_container_width=True):
        if password_input == ADMIN_RELOAD_PASSWORD:
            st.session_state.data                = load_data_from_gsheet()
            st.session_state.flash_message       = "구글 시트의 최신 내용을 화면으로 다시 불러왔습니다."
            st.session_state.show_reload_password = False
            st.rerun()
        else:
            st.sidebar.error("비밀번호가 올바르지 않습니다.")

# =========================================================
# 8. 상단
# =========================================================
st.markdown('<div class="main-title">📒 KVMA President Schedule</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">회장님 일정 등록 · 조회 · 수정 · 취소 · 삭제와 함께, 직원들이 후속 준비사항을 공유할 수 있는 스케줄러입니다.</div>', unsafe_allow_html=True)

if not has_gsheet_config():
    st.info("현재는 임시 세션 상태입니다. 새로고침 후에도 일정이 계속 유지되려면 구글 시트 연결이 필요합니다.")

show_flash()
st.session_state.is_mobile_force_stack = False

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
    st.markdown("**검색어 · 카테고리 · 일정 현황 · 날짜를 기준으로 일정을 찾을 수 있습니다.**")

    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([2.3, 1.0, 1.0, 1.0, 1.0, 0.8])

    search_text = fc1.text_input("검색", value=st.session_state.search_text,
        placeholder="회의명 / 방문기관명 / 담당자명 / 연락처 / 후속 검색", label_visibility="collapsed")
    st.session_state.search_text = search_text

    selected_cat = fc2.selectbox("", ["카테고리"] + CATEGORIES,
        index=(["카테고리"]+CATEGORIES).index(st.session_state.selected_cat)
        if st.session_state.selected_cat in (["카테고리"]+CATEGORIES) else 0,
        label_visibility="collapsed")
    st.session_state.selected_cat = selected_cat

    selected_status = fc3.selectbox("", ["일정 현황"] + STATUS_OPTIONS,
        index=(["일정 현황"]+STATUS_OPTIONS).index(st.session_state.selected_status)
        if st.session_state.selected_status in (["일정 현황"]+STATUS_OPTIONS) else 0,
        label_visibility="collapsed")
    st.session_state.selected_status = selected_status

    selected_follow_status = fc4.selectbox("", ["팔로우업 상태"] + FOLLOW_STATUS_OPTIONS,
        index=(["팔로우업 상태"]+FOLLOW_STATUS_OPTIONS).index(st.session_state.selected_follow_status)
        if st.session_state.selected_follow_status in (["팔로우업 상태"]+FOLLOW_STATUS_OPTIONS) else 0,
        label_visibility="collapsed")
    st.session_state.selected_follow_status = selected_follow_status

    with fc5:
        st.date_input("", value=st.session_state.selected_date,
                      key="_date_input_main", label_visibility="collapsed",
                      on_change=_on_date_change)
        st.session_state.selected_date = st.session_state._date_input_main

    if fc6.button("오늘", use_container_width=True):
        st.session_state.search_text           = ""
        st.session_state.selected_cat          = "카테고리"
        st.session_state.selected_status       = "일정 현황"
        st.session_state.selected_follow_status = "팔로우업 상태"
        st.session_state.selected_date         = today
        st.session_state.table_page_num_value  = 1
        st.rerun()

    render_legend()
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_df = get_filtered_df(
        st.session_state.data,
        selected_cat=st.session_state.selected_cat,
        search_text=st.session_state.search_text,
        status_filter=st.session_state.selected_status,
        follow_status_filter=st.session_state.selected_follow_status
    )

    day_df = filtered_df[filtered_df["DateParsed"] == st.session_state.selected_date].copy()
    day_df = sort_oldest_first(day_df)

    confirmed_count = 0 if filtered_df.empty else len(filtered_df[filtered_df["Status"] == "확정"])
    pending_count   = 0 if filtered_df.empty else len(filtered_df[filtered_df["Status"] == "보류"])
    cancel_count    = 0 if filtered_df.empty else len(filtered_df[filtered_df["Status"] == "취소"])

    render_metric_chips(len(day_df), confirmed_count, pending_count, cancel_count)

    tabs = st.tabs(["일별 보기", "주간 보기", "월별 보기", "전체 일정표"])

    # ── 일별 ──
    with tabs[0]:
        st.markdown(f'<div class="section-title">📍 {st.session_state.selected_date.strftime("%Y년 %m월 %d일")} 일정</div>', unsafe_allow_html=True)
        if st.session_state.edit_id:
            current     = get_active_df(st.session_state.data)
            edit_target = ensure_columns(current[current["ID"].astype(str) == str(st.session_state.edit_id)])
            if not edit_target.empty: render_form(mode="edit", row_data=edit_target.iloc[0].to_dict())
            else: st.caption("수정할 일정이 존재하지 않습니다.")
        else:
            if day_df.empty: st.caption("선택한 날짜의 일정이 없습니다.")
            else:
                for idx, (_, row) in enumerate(day_df.iterrows()):
                    render_compact_event(row, prefix=f"day_{idx}")

    # ── 주간 ──
    with tabs[1]:
        st.markdown('<div class="section-title">📅 주간 일정</div>', unsafe_allow_html=True)
        wc1, wc2 = st.columns([1.3, 4.7])
        week_anchor = wc1.date_input("", value=st.session_state.selected_date,
                                     key="week_anchor_date", label_visibility="collapsed")
        if wc2.button("이 날짜가 포함된 주 보기", key="apply_week_anchor"):
            st.session_state.selected_date = week_anchor; st.rerun()

        week_days = week_dates_from_any_day(st.session_state.selected_date)
        week_df   = filtered_df[filtered_df["DateParsed"].isin(week_days)].copy()
        day_names = ["일","월","화","수","목","금","토"]
        cols = st.columns(7)

        for idx, day_obj in enumerate(week_days):
            with cols[idx]:
                cls       = weekday_class_by_index(idx)
                label_cls = "day-head" + (f" {cls}" if cls else "")
                st.markdown(f'<div class="{label_cls}">{day_obj.month}/{day_obj.day} ({day_names[idx]})</div>', unsafe_allow_html=True)
                daily = sort_oldest_first(week_df[week_df["DateParsed"] == day_obj].copy())
                if daily.empty:
                    st.markdown('<div class="wm-no-schedule">일정 없음</div>', unsafe_allow_html=True)
                else:
                    for r_idx, (_, row) in enumerate(daily.iterrows()):
                        st.session_state.is_mobile_force_stack = True
                        render_week_month_event(row, prefix=f"week_{idx}_{r_idx}")

        st.session_state.is_mobile_force_stack = False

    # ── 월별 ──
    with tabs[2]:
        st.markdown('<div class="section-title">🗓️ 월별 일정</div>', unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns([1, 1, 2])
        current_year = st.session_state.selected_date.year
        year_options = list(range(min(2025, current_year-3), max(2040, current_year+10)+1))
        month_year       = mc1.selectbox("년도", year_options, index=year_options.index(current_year), key="month_year_select")
        month_month      = mc2.selectbox("월", list(range(1,13)), index=st.session_state.selected_date.month-1, key="month_month_select")
        month_view_mode  = mc3.radio("보기 방식", ["캘린더형","목록형"], horizontal=True, key="month_view_mode")

        month_df = filtered_df[filtered_df["DateParsed"].apply(
            lambda d: d.year == month_year and d.month == month_month if pd.notna(d) else False
        )].copy()

        if month_view_mode == "캘린더형":
            weeks         = month_calendar_weeks(month_year, month_month)
            weekday_names = ["일","월","화","수","목","금","토"]
            head_cols = st.columns(7)
            for i, name in enumerate(weekday_names):
                cls = weekday_class_by_index(i)
                head_cols[i].markdown(f'<div class="day-head{" "+cls if cls else ""}">{name}</div>', unsafe_allow_html=True)
            for week in weeks:
                week_cols = st.columns(7)
                for didx, day_obj in enumerate(week):
                    with week_cols[didx]:
                        if day_obj.month != month_month:
                            st.markdown(day_header_html(day_obj, f"{day_obj.day}일", dim=True), unsafe_allow_html=True)
                            st.markdown('<div class="wm-no-schedule">&nbsp;</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(day_header_html(day_obj, f"{day_obj.day}일", dim=False), unsafe_allow_html=True)
                            daily = sort_oldest_first(month_df[month_df["DateParsed"] == day_obj].copy())
                            if daily.empty:
                                st.markdown('<div class="wm-no-schedule">일정 없음</div>', unsafe_allow_html=True)
                            else:
                                for r_idx, (_, row) in enumerate(daily.iterrows()):
                                    st.session_state.is_mobile_force_stack = True
                                    render_week_month_event(row, prefix=f"month_{didx}_{day_obj}_{r_idx}")
            st.session_state.is_mobile_force_stack = False
        else:
            st.caption("화면 폭이 좁을 때는 목록형이 더 보기 편합니다.")
            month_list  = sort_oldest_first(month_df.copy())
            all_days    = month_calendar_weeks(month_year, month_month)
            flat_days   = [d for week in all_days for d in week if d.month == month_month]
            seen, ordered_days = set(), []
            for d in flat_days:
                if d not in seen: seen.add(d); ordered_days.append(d)
            for d in ordered_days:
                st.markdown(day_header_html(d, f"{d.month}월 {d.day}일", dim=False), unsafe_allow_html=True)
                daily = month_list[month_list["DateParsed"] == d].copy()
                if daily.empty:
                    st.markdown('<div class="wm-no-schedule">일정 없음</div>', unsafe_allow_html=True)
                else:
                    for r_idx, (_, row) in enumerate(daily.iterrows()):
                        render_week_month_event(row, prefix=f"month_list_{d}_{r_idx}")

    # ── 전체 일정표 ──
    with tabs[3]:
        st.markdown('<div class="section-title">📋 전체 일정표</div>', unsafe_allow_html=True)
        tc1,tc2,tc3,tc4 = st.columns([1.25,1.3,1.4,2.8])
        table_sort_mode     = tc1.selectbox("정렬", ["최신 일정 우선","오래된 일정 우선"], index=0, key="table_sort_mode")
        table_page_size     = tc2.selectbox("한 페이지 행 수", [20,50,100,200], index=1, key="table_page_size")
        table_follow_filter = tc3.selectbox("팔로우업 상태", ["전체"]+FOLLOW_STATUS_OPTIONS, index=0, key="table_follow_filter")
        only_open_follow    = tc4.checkbox("미완료 팔로우업만 보기", value=False, key="only_open_follow")
        st.caption("'한 페이지 행 수'는 한 번에 보여줄 일정 데이터 행 개수입니다.")

        table_df = filtered_df.copy()
        if table_follow_filter != "전체": table_df = table_df[table_df["FollowStatus"] == table_follow_filter]
        if only_open_follow: table_df = table_df[table_df["FollowStatus"].isin(["미착수","진행중","보류"])]

        if table_df.empty: st.caption("표시할 일정이 없습니다.")
        else:
            table_df    = sort_latest_first(table_df) if table_sort_mode == "최신 일정 우선" else sort_oldest_first(table_df)
            total_rows  = len(table_df)
            total_pages = max(1, math.ceil(total_rows / table_page_size))
            current_page= min(max(int(st.session_state.get("table_page_num_value",1)),1), total_pages)
            page_num    = st.number_input("페이지", min_value=1, max_value=total_pages,
                                          value=current_page, step=1, key="table_page_num")
            st.session_state.table_page_num_value = int(page_num)
            start_idx = (int(page_num)-1) * table_page_size
            end_idx   = start_idx + table_page_size
            st.caption(f"총 {total_rows}건 중 {start_idx+1} ~ {min(end_idx, total_rows)}건 표시")
            st.dataframe(to_display_dataframe(table_df.iloc[start_idx:end_idx].copy()),
                         use_container_width=True, hide_index=True, height=560)
