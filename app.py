import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import time
import html
from io import BytesIO

# =========================================================
# 1. 기본 설정
# =========================================================
st.set_page_config(
    page_title="KVMA 회장님 일정",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. 카테고리 컬러맵
# =========================================================
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
STATUS_OPTIONS = ["확정", "보류", "취소", "완료"]

# =========================================================
# 3. CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.main {
    background: #ffffff;
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

.page-title {
    font-size: 2.35rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 0.35rem;
}

.page-sub {
    font-size: 0.95rem;
    color: #7A7F8C;
    margin-bottom: 1rem;
}

.filter-shell {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 4px 18px rgba(20, 24, 40, 0.04);
    margin-bottom: 18px;
}

.filter-caption {
    font-size: 0.92rem;
    color: #7A7F8C;
    margin-bottom: 10px;
    font-weight: 600;
}

.section-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: #2F3142;
    margin: 10px 0 14px 0;
}

.small-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #2F3142;
    margin: 8px 0 10px 0;
}

.legend-wrap {
    margin: 8px 0 6px 0;
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

.card-wrap {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid #ECEEF3;
    box-shadow: 0 8px 26px rgba(16, 24, 40, 0.05);
    margin-bottom: 12px;
}

.card-inner {
    display: flex;
}

.card-accent {
    width: 14px;
    flex-shrink: 0;
}

.card-body {
    width: 100%;
    padding: 20px 22px 18px 22px;
}

.meta-row {
    font-size: 0.96rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.category-pill {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 800;
    border: 1px solid;
    margin-left: 8px;
    vertical-align: middle;
}

.status-pill {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 800;
    border: 1px solid #D1D5DB;
    margin-left: 8px;
    vertical-align: middle;
    background: #F8FAFC;
    color: #475467;
}

.subject-row {
    font-size: 1.7rem;
    font-weight: 800;
    color: #232634;
    margin-bottom: 14px;
    line-height: 1.3;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 4px;
}

.plan-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 12px;
}

.info-box {
    background: rgba(255,255,255,0.80);
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 16px;
    padding: 14px 14px 12px 14px;
    min-height: 90px;
}

.info-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 6px;
}

.info-value {
    font-size: 1rem;
    font-weight: 600;
    color: #232634;
    line-height: 1.5;
    white-space: pre-wrap;
}

.memo-note {
    margin-top: 14px;
    background: #FFFBEA;
    border: 1px solid #F8E3A3;
    border-left: 8px solid #F5C84B;
    border-radius: 16px;
    padding: 14px 16px;
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
    line-height: 1.55;
    white-space: pre-wrap;
}

.updated-text {
    margin-top: 10px;
    text-align: right;
    font-size: 0.75rem;
    color: #9CA3AF;
}

.month-day-box {
    border: 1px solid #E9ECF2;
    border-radius: 16px;
    min-height: 170px;
    padding: 10px;
    background: #ffffff;
    margin-bottom: 10px;
}

.month-day-head {
    font-size: 0.95rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 8px;
}

.empty-day-box {
    border: 1px dashed #EEF1F5;
    border-radius: 16px;
    min-height: 170px;
    padding: 10px;
    background: #FAFBFC;
    margin-bottom: 10px;
}

.week-col-box {
    border: 1px solid #E9ECF2;
    border-radius: 16px;
    background: #ffffff;
    padding: 12px;
    min-height: 280px;
}

.week-day-head {
    font-size: 1rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 10px;
}

.helper-box {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 12px 14px;
    color: #475467;
    font-size: 0.92rem;
}

div[data-testid="stForm"] {
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 18px 18px 10px 18px;
    background: #ffffff;
}

div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 14px !important;
}

@media (max-width: 1100px) {
    .info-grid, .plan-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4. 컬럼 정의
# =========================================================
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
    "Updated"
]

# =========================================================
# 5. 유틸 함수
# =========================================================
def ensure_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATA_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[DATA_COLUMNS].copy()

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
            "Updated": ""
        }
    ])
    return ensure_dataframe_columns(sample)

def get_color(cat: str):
    return COLOR_MAP.get(cat, COLOR_MAP["기타"])

def to_date_safe(value):
    if pd.isna(value) or value == "":
        return None
    return pd.to_datetime(value, errors="coerce").date()

def escape(v):
    if v is None:
        return "-"
    s = str(v).strip()
    return html.escape(s) if s else "-"

def build_contact_block(row):
    parts = []
    if str(row.get("TargetDept", "")).strip():
        parts.append(f"부서: {row['TargetDept']}")
    if str(row.get("TargetName", "")).strip():
        parts.append(f"이름: {row['TargetName']}")
    if str(row.get("TargetContact", "")).strip():
        parts.append(f"연락처: {row['TargetContact']}")
    return " / ".join(parts) if parts else "-"

def build_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df = df.copy()
        export_df.to_excel(writer, index=False, sheet_name="schedule")
    return output.getvalue()

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
    st.session_state.data = ensure_dataframe_columns(st.session_state.data)

def get_filtered_df(base_df: pd.DataFrame, selected_date=None, selected_cat="전체", search_text=""):
    df = base_df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    if selected_date is not None:
        df = df[df["Date"] == selected_date]

    if selected_cat != "전체":
        df = df[df["Category"] == selected_cat]

    if search_text:
        q = str(search_text).strip()
        mask = (
            df["Subject"].fillna("").str.contains(q, case=False, na=False) |
            df["OrgName"].fillna("").str.contains(q, case=False, na=False) |
            df["DetailPlace"].fillna("").str.contains(q, case=False, na=False) |
            df["TargetDept"].fillna("").str.contains(q, case=False, na=False) |
            df["TargetName"].fillna("").str.contains(q, case=False, na=False) |
            df["TargetContact"].fillna("").str.contains(q, case=False, na=False)
        )
        df = df[mask]

    df = df.sort_values(by=["Date", "Time"])
    return df

def get_month_weeks(year: int, month: int):
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    weeks = cal.monthdatescalendar(year, month)
    return weeks

def render_category_legend():
    html_parts = ['<div class="legend-wrap">']
    for cat in CATEGORIES:
        c = get_color(cat)
        html_parts.append(
            f'<span class="legend-pill" style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">{cat}</span>'
        )
    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)

def render_event_card(row):
    c = get_color(row["Category"])
    contact_block = build_contact_block(row)

    card_html = f"""
    <div class="card-wrap" style="background:{c["bg"]};">
        <div class="card-inner">
            <div class="card-accent" style="background:{c["line"]};"></div>
            <div class="card-body">
                <div class="meta-row" style="color:{c["text"]};">
                    ⏰ {escape(row["Time"])}
                    <span class="category-pill" style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">
                        {escape(row["Category"])}
                    </span>
                    <span class="status-pill">{escape(row["Status"])}</span>
                </div>

                <div class="subject-row">{escape(row["Subject"])}</div>

                <div class="info-grid">
                    <div class="info-box">
                        <div class="info-label">방문기관명</div>
                        <div class="info-value">🏢 {escape(row["OrgName"])}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">회의장소(세부)</div>
                        <div class="info-value">📍 {escape(row["DetailPlace"])}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">보좌관/비서/담당자 정보</div>
                        <div class="info-value">👤 {escape(contact_block)}</div>
                    </div>
                </div>

                <div class="info-grid" style="margin-top:12px;">
                    <div class="info-box">
                        <div class="info-label">회장님 외 동행인</div>
                        <div class="info-value">👥 {escape(row["Companion"])}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">사무처 수행직원</div>
                        <div class="info-value">🧾 {escape(row["Staff"])}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">최종 수정</div>
                        <div class="info-value">🕒 {escape(row["Updated"])}</div>
                    </div>
                </div>

                <div class="plan-grid">
                    <div class="info-box">
                        <div class="info-label">회의 목적</div>
                        <div class="info-value">{escape(row["Purpose"])}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">대응 방향</div>
                        <div class="info-value">{escape(row["ActionPlan"])}</div>
                    </div>
                </div>

                <div class="memo-note">
                    <div class="memo-title">📌 Memo</div>
                    <div class="memo-text">{escape(row["Memo"])}</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def event_action_buttons(row):
    b1, b2, b3, b4 = st.columns([1, 1, 1, 6])
    if b1.button("수정", key=f"edit_{row['ID']}", use_container_width=True):
        st.session_state.edit_id = row["ID"]
        st.session_state.main_menu = "📅 일정 보기"
        st.rerun()

    next_status = "취소" if row["Status"] != "취소" else "확정"
    next_label = "일정 취소" if row["Status"] != "취소" else "취소 해제"
    if b2.button(next_label, key=f"cancel_{row['ID']}", use_container_width=True):
        st.session_state.data.loc[
            st.session_state.data["ID"] == row["ID"], ["Status", "Updated"]
        ] = [next_status, datetime.now().strftime("%Y-%m-%d %H:%M")]
        st.rerun()

    if b3.button("삭제", key=f"delete_{row['ID']}", use_container_width=True):
        st.session_state.data = st.session_state.data[st.session_state.data["ID"] != row["ID"]].reset_index(drop=True)
        if st.session_state.selected_event_id == row["ID"]:
            st.session_state.selected_event_id = None
        st.rerun()

def render_event_form(mode="new", row_data=None):
    if row_data is None:
        row_data = {
            "ID": str(time.time()),
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
            "Updated": ""
        }

    form_title = "✍️ 신규 일정 등록" if mode == "new" else "🛠️ 일정 수정"
    st.markdown(f'<div class="section-title">{form_title}</div>', unsafe_allow_html=True)

    with st.form(f"schedule_form_{mode}", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)
        input_date = c1.date_input("일정 날짜", value=to_date_safe(row_data["Date"]) or datetime.now().date())
        input_time = c2.time_input("일정 시간", value=datetime.strptime(str(row_data["Time"]), "%H:%M").time() if str(row_data["Time"]) else datetime.strptime("09:00", "%H:%M").time())
        input_category = c3.selectbox("카테고리", CATEGORIES, index=CATEGORIES.index(row_data["Category"]) if row_data["Category"] in CATEGORIES else 0)

        s1, s2 = st.columns([2, 1])
        input_subject = s1.text_input("회의명", value=str(row_data["Subject"]))
        input_status = s2.selectbox("상태", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row_data["Status"]) if row_data["Status"] in STATUS_OPTIONS else 0)

        a1, a2 = st.columns(2)
        input_org = a1.text_input("방문기관명", value=str(row_data["OrgName"]))
        input_detail_place = a2.text_input("회의장소(세부)", value=str(row_data["DetailPlace"]))

        b1, b2, b3 = st.columns(3)
        input_target_dept = b1.text_input("보좌관/비서/담당자 부서", value=str(row_data["TargetDept"]))
        input_target_name = b2.text_input("보좌관/비서/담당자 이름", value=str(row_data["TargetName"]))
        input_target_contact = b3.text_input("보좌관/비서/담당자 연락처", value=str(row_data["TargetContact"]))

        d1, d2 = st.columns(2)
        input_companion = d1.text_input("회장님 외 동행인", value=str(row_data["Companion"]))
        input_staff = d2.text_input("사무처 수행직원", value=str(row_data["Staff"]))

        input_purpose = st.text_area("회의 목적", value=str(row_data["Purpose"]), height=110)
        input_action = st.text_area("대응 방향", value=str(row_data["ActionPlan"]), height=110)
        input_memo = st.text_area("Memo", value=str(row_data["Memo"]), height=90)

        if mode == "new":
            submit = st.form_submit_button("저장 후 일정 보기로 이동", use_container_width=True)
            if submit:
                new_record = {
                    "ID": str(time.time()),
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
                    "Updated": ""
                }
                save_record(new_record, is_edit=False)
                st.session_state.main_menu = "📅 일정 보기"
                st.session_state.selected_date = input_date
                st.session_state.current_view = "일별 보기"
                st.session_state.edit_id = None
                st.session_state.flash_message = "신규 일정이 저장되었습니다."
                st.rerun()
        else:
            f1, f2, f3 = st.columns([1, 1, 1])
            save_btn = f1.form_submit_button("수정 저장", use_container_width=True)
            cancel_btn = f2.form_submit_button("수정 취소", use_container_width=True)
            delete_btn = f3.form_submit_button("삭제", use_container_width=True)

            if save_btn:
                updated_record = {
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
                    "Updated": ""
                }
                save_record(updated_record, is_edit=True)
                st.session_state.edit_id = None
                st.session_state.flash_message = "일정이 수정되었습니다."
                st.rerun()

            if cancel_btn:
                st.session_state.edit_id = None
                st.rerun()

            if delete_btn:
                st.session_state.data = st.session_state.data[st.session_state.data["ID"] != row_data["ID"]].reset_index(drop=True)
                st.session_state.edit_id = None
                st.session_state.flash_message = "일정이 삭제되었습니다."
                st.rerun()

def show_flash():
    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = None

# =========================================================
# 6. 상태 초기화
# =========================================================
if "data" not in st.session_state:
    st.session_state.data = init_sample_data()
else:
    st.session_state.data = ensure_dataframe_columns(st.session_state.data)

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "main_menu" not in st.session_state:
    st.session_state.main_menu = "📅 일정 보기"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = "전체"

if "selected_event_id" not in st.session_state:
    st.session_state.selected_event_id = None

if "current_view" not in st.session_state:
    st.session_state.current_view = "일별 보기"

if "flash_message" not in st.session_state:
    st.session_state.flash_message = None

# =========================================================
# 7. 사이드바
# =========================================================
st.sidebar.markdown("# 🏢 KVMA 비서실")

main_menu = st.sidebar.radio(
    "메뉴",
    ["📅 일정 보기", "✍️ 신규 일정 등록"],
    index=["📅 일정 보기", "✍️ 신규 일정 등록"].index(st.session_state.main_menu),
    key="main_menu_radio"
)
st.session_state.main_menu = main_menu

excel_bytes = build_excel_bytes(st.session_state.data)
st.sidebar.download_button(
    label="📥 엑셀 다운로드",
    data=excel_bytes,
    file_name=f"kvma_schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 상태값 안내")
st.sidebar.markdown("""
- **확정**: 일정 확정
- **보류**: 조정 중
- **취소**: 취소된 일정
- **완료**: 종료된 일정
""")

# =========================================================
# 8. 메인 화면
# =========================================================
st.markdown('<div class="page-title">📒 KVMA 회장님 일정</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">회장 일정 등록 · 조회 · 수정 · 취소 · 삭제를 한 화면 흐름 안에서 관리할 수 있는 스케줄러입니다.</div>', unsafe_allow_html=True)
show_flash()

# =========================================================
# 9. 신규 일정 등록
# =========================================================
if st.session_state.main_menu == "✍️ 신규 일정 등록":
    render_event_form(mode="new")

# =========================================================
# 10. 일정 보기
# =========================================================
else:
    st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
    st.markdown('<div class="filter-caption">검색어 · 카테고리 · 날짜를 기준으로 일정을 찾을 수 있습니다.</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([2.4, 1.2, 1.2, 0.8])
    search_text = f1.text_input(
        "검색",
        placeholder="회의명 / 방문기관명 / 담당자명 / 연락처 검색",
        label_visibility="collapsed"
    )

    cat_options = ["전체"] + CATEGORIES
    selected_cat = f2.selectbox(
        "카테고리",
        options=cat_options,
        index=cat_options.index(st.session_state.selected_cat) if st.session_state.selected_cat in cat_options else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_cat = selected_cat

    selected_date = f3.date_input(
        "날짜",
        value=st.session_state.selected_date,
        label_visibility="collapsed"
    )
    st.session_state.selected_date = selected_date

    if f4.button("오늘", use_container_width=True):
        st.session_state.selected_date = datetime.now().date()
        st.rerun()

    render_category_legend()
    st.markdown('</div>', unsafe_allow_html=True)

    view_tabs = st.tabs(["일별 보기", "월간 보기", "주간 보기"])

    # -----------------------------------------------------
    # 10-1. 일별 보기
    # -----------------------------------------------------
    with view_tabs[0]:
        st.session_state.current_view = "일별 보기"

        day_df = get_filtered_df(
            st.session_state.data,
            selected_date=st.session_state.selected_date,
            selected_cat=st.session_state.selected_cat,
            search_text=search_text
        )

        st.markdown(
            f'<div class="section-title">📍 {st.session_state.selected_date.strftime("%Y년 %m월 %d일")} 일정</div>',
            unsafe_allow_html=True
        )

        if st.session_state.edit_id:
            edit_df = st.session_state.data[st.session_state.data["ID"] == st.session_state.edit_id]
            if not edit_df.empty:
                render_event_form(mode="edit", row_data=edit_df.iloc[0].to_dict())

        if day_df.empty:
            st.info("조건에 맞는 일정이 없습니다.")

        for _, row in day_df.iterrows():
            if st.session_state.edit_id == row["ID"]:
                continue
            render_event_card(row)
            event_action_buttons(row)

    # -----------------------------------------------------
    # 10-2. 월간 보기
    # -----------------------------------------------------
    with view_tabs[1]:
        st.markdown('<div class="section-title">🗓️ 월간 일정</div>', unsafe_allow_html=True)

        month_ctrl1, month_ctrl2, month_ctrl3 = st.columns([1, 1, 5])

        month_year = month_ctrl1.selectbox(
            "년도 선택",
            options=list(range(datetime.now().year - 2, datetime.now().year + 4)),
            index=2,
            key="month_year"
        )
        month_month = month_ctrl2.selectbox(
            "월 선택",
            options=list(range(1, 13)),
            index=st.session_state.selected_date.month - 1,
            key="month_month"
        )

        month_df = st.session_state.data.copy()
        month_df["Date"] = pd.to_datetime(month_df["Date"], errors="coerce").dt.date
        if st.session_state.selected_cat != "전체":
            month_df = month_df[month_df["Category"] == st.session_state.selected_cat]
        if search_text:
            q = str(search_text).strip()
            month_df = month_df[
                month_df["Subject"].fillna("").str.contains(q, case=False, na=False) |
                month_df["OrgName"].fillna("").str.contains(q, case=False, na=False) |
                month_df["TargetName"].fillna("").str.contains(q, case=False, na=False)
            ]

        weeks = get_month_weeks(month_year, month_month)
        weekday_names = ["일", "월", "화", "수", "목", "금", "토"]
        head_cols = st.columns(7)
        for i, wname in enumerate(weekday_names):
            head_cols[i].markdown(f"**{wname}**")

        for w_idx, week in enumerate(weeks):
            cols = st.columns(7)
            for d_idx, day_obj in enumerate(week):
                with cols[d_idx]:
                    if day_obj.month != month_month:
                        st.markdown('<div class="empty-day-box"></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div class="month-day-box"><div class="month-day-head">{day_obj.day}일</div></div>',
                            unsafe_allow_html=True
                        )
                        day_events = month_df[month_df["Date"] == day_obj].sort_values(by="Time")
                        if day_events.empty:
                            st.caption("일정 없음")
                        else:
                            for _, row in day_events.iterrows():
                                label = f"{row['Time']} | {row['Subject'][:16]}"
                                if st.button(label, key=f"month_btn_{row['ID']}", use_container_width=True):
                                    st.session_state.selected_event_id = row["ID"]
                                    st.session_state.selected_date = day_obj
                                    st.rerun()

        if st.session_state.selected_event_id:
            selected_df = st.session_state.data[st.session_state.data["ID"] == st.session_state.selected_event_id]
            if not selected_df.empty:
                st.markdown('<div class="small-title">선택한 일정 상세정보</div>', unsafe_allow_html=True)
                render_event_card(selected_df.iloc[0])
                event_action_buttons(selected_df.iloc[0])

    # -----------------------------------------------------
    # 10-3. 주간 보기
    # -----------------------------------------------------
    with view_tabs[2]:
        st.markdown('<div class="section-title">📅 주간 일정</div>', unsafe_allow_html=True)

        w1, w2, w3, w4 = st.columns([1, 1, 1, 4])

        week_year = w1.selectbox(
            "년도",
            options=list(range(datetime.now().year - 2, datetime.now().year + 4)),
            index=2,
            key="week_year"
        )
        week_month = w2.selectbox(
            "월",
            options=list(range(1, 13)),
            index=st.session_state.selected_date.month - 1,
            key="week_month"
        )

        month_weeks = get_month_weeks(week_year, week_month)
        week_labels = [f"{week_month}월 {idx+1}주차" for idx in range(len(month_weeks))]
        week_idx = w3.selectbox(
            "주차",
            options=list(range(len(month_weeks))),
            format_func=lambda x: week_labels[x],
            key="week_idx"
        )

        selected_week = month_weeks[week_idx]

        week_df = st.session_state.data.copy()
        week_df["Date"] = pd.to_datetime(week_df["Date"], errors="coerce").dt.date
        week_dates = [d for d in selected_week if d.month == week_month]
        week_df = week_df[week_df["Date"].isin(week_dates)]

        if st.session_state.selected_cat != "전체":
            week_df = week_df[week_df["Category"] == st.session_state.selected_cat]

        if search_text:
            q = str(search_text).strip()
            week_df = week_df[
                week_df["Subject"].fillna("").str.contains(q, case=False, na=False) |
                week_df["OrgName"].fillna("").str.contains(q, case=False, na=False) |
                week_df["TargetName"].fillna("").str.contains(q, case=False, na=False)
            ]

        day_names = ["일", "월", "화", "수", "목", "금", "토"]
        week_cols = st.columns(7)

        for idx, day_obj in enumerate(selected_week):
            with week_cols[idx]:
                if day_obj.month != week_month:
                    st.markdown('<div class="week-col-box"><div class="week-day-head" style="color:#9CA3AF;">해당 월 아님</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        f'<div class="week-col-box"><div class="week-day-head">{day_obj.month}/{day_obj.day} ({day_names[idx]})</div></div>',
                        unsafe_allow_html=True
                    )
                    daily = week_df[week_df["Date"] == day_obj].sort_values(by="Time")
                    if daily.empty:
                        st.caption("일정 없음")
                    else:
                        for _, row in daily.iterrows():
                            label = f"{row['Time']} | {row['Subject'][:14]}"
                            if st.button(label, key=f"week_btn_{row['ID']}", use_container_width=True):
                                st.session_state.selected_event_id = row["ID"]
                                st.session_state.selected_date = day_obj
                                st.rerun()

        if st.session_state.selected_event_id:
            selected_df = st.session_state.data[st.session_state.data["ID"] == st.session_state.selected_event_id]
            if not selected_df.empty:
                st.markdown('<div class="small-title">선택한 일정 상세정보</div>', unsafe_allow_html=True)
                render_event_card(selected_df.iloc[0])
                event_action_buttons(selected_df.iloc[0])

    # -----------------------------------------------------
    # 10-4. 추가 기능 안내
    # -----------------------------------------------------
    st.markdown('<div class="small-title">추가로 넣어두면 좋은 기능</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="helper-box">
현재 코드에는 기본 스케줄러 기능을 넣어두었습니다. 다음 단계에서 붙이기 좋은 기능은
1) 엑셀 자동 저장 파일 업로드/동기화,
2) 슬랙 공유 버튼,
3) 일정별 중요도/우선순위,
4) 회장님 브리핑용 일일 요약,
5) 반복 일정,
6) 일정 완료 체크 후 히스토리 보관
입니다.
</div>
""", unsafe_allow_html=True)
