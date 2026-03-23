st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.block-container {
    padding-top: 2.1rem;
    padding-bottom: 1.4rem;
    max-width: 1600px;
}

h1, h2, h3 {
    line-height: 1.2 !important;
}

.main-title {
    font-size: 2.7rem;
    font-weight: 800;
    color: #2F3142;
    margin-top: 0.35rem;
    margin-bottom: 0.35rem;
    line-height: 1.2;
    word-break: keep-all;
}

.sub-text {
    font-size: 0.98rem;
    color: #6B7280;
    margin-bottom: 0.8rem;
    line-height: 1.5;
    word-break: keep-all;
}

.panel {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 18px;
    padding: 12px 14px;
    box-shadow: 0 4px 16px rgba(20, 24, 40, 0.04);
    margin-bottom: 10px;
}

.section-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #2F3142;
    margin: 8px 0 10px 0;
    line-height: 1.2;
}

.legend-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.80rem;
    font-weight: 700;
    margin: 0 6px 6px 0;
    border: 1px solid;
}

.metric-chip {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.80rem;
    font-weight: 800;
    margin: 0 8px 8px 0;
    border: 1px solid #D8DEE8;
    background: #ffffff;
    color: #344054;
}

.summary-card {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid #E8EBF2;
    margin-top: 4px;
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
    font-size: 0.92rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.summary-title {
    font-size: 1.22rem;
    font-weight: 800;
    color: #232634;
    line-height: 1.28;
    margin: 0;
    word-break: keep-all;
}

.tag-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 800;
    border: 1px solid #D1D5DB;
    background: #ffffff;
    color: #475467;
    margin-left: 6px;
    vertical-align: middle;
}

.follow-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 800;
    border: 1px solid #D1D5DB;
    background: #F8FAFC;
    color: #344054;
    margin-right: 6px;
    margin-bottom: 6px;
    vertical-align: middle;
}

.info-box {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 16px;
    padding: 11px 13px 10px 13px;
    min-height: 68px;
    margin-bottom: 8px;
}

.info-label {
    font-size: 0.77rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 6px;
    line-height: 1.35;
}

.info-value {
    font-size: 0.96rem;
    font-weight: 600;
    color: #232634;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
}

.memo-box {
    background: #FFFBEA;
    border: 1px solid #F8E3A3;
    border-left: 8px solid #F5C84B;
    border-radius: 16px;
    padding: 12px 16px;
    margin-top: 4px;
}

.memo-title {
    font-size: 0.90rem;
    font-weight: 800;
    color: #7A5A00;
    margin-bottom: 6px;
}

.memo-text {
    font-size: 0.94rem;
    color: #4B5563;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
}

.follow-wrap {
    background: #F7FAFF;
    border: 1px solid #D7E7FF;
    border-left: 8px solid #3B82F6;
    border-radius: 18px;
    padding: 14px 16px;
    margin-top: 8px;
    margin-bottom: 10px;
}

.follow-title {
    font-size: 1rem;
    font-weight: 800;
    color: #1D4ED8;
    margin-bottom: 10px;
}

.follow-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.follow-box {
    border: 1px solid #DDE6F4;
    border-radius: 14px;
    padding: 10px 12px;
    background: #ffffff;
}

.follow-label {
    font-size: 0.75rem;
    font-weight: 800;
    color: #6B7280;
    margin-bottom: 4px;
}

.follow-value {
    font-size: 0.92rem;
    font-weight: 600;
    color: #1F2937;
    line-height: 1.45;
    white-space: pre-wrap;
    word-break: break-word;
}

.small-action button {
    min-height: 34px !important;
    height: 34px !important;
    padding-top: 0.15rem !important;
    padding-bottom: 0.15rem !important;
    font-size: 0.84rem !important;
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
    border-radius: 12px !important;
}

div[data-testid="stForm"] {
    border: 1px solid #ECEEF3;
    border-radius: 18px;
    padding: 16px 16px 10px 16px;
    background: #ffffff;
}

/* ===== 사이드바 버튼 박스 간격: 확실히 축소 ===== */
.menu-btn-wrap {
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    gap: 0px !important;
}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    margin-top: 0px !important;
    margin-bottom: 0px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"],
section[data-testid="stSidebar"] div[data-testid="stDownloadButton"],
section[data-testid="stSidebar"] div[data-testid="stExpander"] {
    margin-top: 0px !important;
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
section[data-testid="stSidebar"] div[data-testid="stDownloadButton"] > button {
    margin-top: 0px !important;
    margin-bottom: 0px !important;
    min-height: 2.85rem !important;
}

/* ===== 일정 박스 간격: 일별/주간/월별 공통으로 확실히 축소 ===== */
div[data-testid="stExpander"] {
    margin-top: 0px !important;
    margin-bottom: 2px !important;
}

div[data-testid="stExpander"] details {
    border-radius: 16px !important;
    border: 1.6px solid #D8DEE8 !important;
    background: #ffffff !important;
    overflow: hidden !important;
    box-shadow: none !important;
}

div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stExpander"]) {
    margin-top: 0px !important;
    margin-bottom: 2px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}

/* 라운드 박스 내부 위아래 여백은 약간 확보 */
.streamlit-expanderHeader {
    font-weight: 800 !important;
    font-size: 0.94rem !important;
    line-height: 1.3 !important;
    text-align: left !important;
}

div[data-testid="stExpander"] summary {
    padding-top: 0.24rem !important;
    padding-bottom: 0.24rem !important;
    padding-left: 0.84rem !important;
    padding-right: 0.84rem !important;
    min-height: auto !important;
}

div[data-testid="stExpander"] summary:hover {
    background: #FAFAFA !important;
}

div[data-testid="stExpanderDetails"] {
    padding-top: 0.12rem !important;
    padding-bottom: 0.12rem !important;
}

/* expander를 담는 상위 블록 gap 제거 */
div[data-testid="stVerticalBlock"] {
    gap: 0px !important;
}

/* 탭과 구역 사이 기본 여백은 유지 */
div[data-testid="stTabs"] {
    margin-bottom: 0px !important;
}

.sidebar-day-item {
    border: 1px solid #ECEEF3;
    border-radius: 12px;
    padding: 8px 10px;
    margin-bottom: 2px !important;
    background: #ffffff;
}

.sidebar-day-time {
    font-size: 0.78rem;
    font-weight: 800;
    color: #475467;
    margin-bottom: 4px;
}

.sidebar-day-title {
    font-size: 0.86rem;
    font-weight: 700;
    color: #1F2937;
    line-height: 1.35;
}

.helper-note {
    font-size: 0.82rem;
    color: #667085;
    line-height: 1.45;
}

.segment-note {
    font-size: 0.84rem;
    color: #667085;
    margin-bottom: 8px;
}

.day-head {
    font-size: 1rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 6px;
}

.day-head.sun {
    color: #C1121F;
}

.day-head.sat {
    color: #1D4ED8;
}

.day-head.dim.sun {
    color: #F1A0A7;
}

.day-head.dim.sat {
    color: #9BB8F5;
}

.day-head.dim {
    color: #B5BBC8;
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

.attend-pill {
    display: inline-block;
    margin-left: 6px;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 800;
    background: #FFF7D6;
    color: #8A6500;
    border: 1px solid #F2D675;
    vertical-align: middle;
}

@media (max-width: 1000px) {
    .block-container {
        padding-top: 1.6rem;
    }
    .main-title {
        font-size: 2.1rem;
    }
    .summary-title {
        font-size: 1.08rem;
    }
    .follow-grid {
        grid-template-columns: 1fr;
    }
    .summary-body {
        padding: 12px 13px 10px 13px;
    }
    .info-box {
        min-height: auto;
    }
    div[data-testid="stExpander"] {
        margin-bottom: 2px !important;
    }
    div[data-testid="stExpander"] summary {
        padding-top: 0.24rem !important;
        padding-bottom: 0.24rem !important;
        padding-left: 0.72rem !important;
        padding-right: 0.72rem !important;
    }
}
</style>
""", unsafe_allow_html=True)
