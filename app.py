st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.main {
    background: #ffffff;
}

.page-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #2F3142;
    margin-bottom: 1rem;
}

.filter-shell {
    background: #ffffff;
    border: 1px solid #ECEEF3;
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 4px 18px rgba(20, 24, 40, 0.04);
    margin-bottom: 22px;
}

.filter-caption {
    font-size: 0.92rem;
    color: #7A7F8C;
    margin-bottom: 10px;
    font-weight: 500;
}

.section-title {
    font-size: 2rem;
    font-weight: 800;
    color: #2F3142;
    margin: 8px 0 18px 0;
}

/* 카드 바깥 프레임 */
.card-wrap {
    border-radius: 24px;
    padding: 0;
    margin-bottom: 18px;
    overflow: hidden;
    border: 1px solid #ECEEF3;
    box-shadow: 0 8px 26px rgba(16, 24, 40, 0.05);
}

/* 카드 내부 */
.card-inner {
    display: flex;
    min-height: 100%;
}

/* 왼쪽 진한 컬러 바 */
.card-accent {
    width: 14px;
    flex-shrink: 0;
}

/* 오른쪽 내용 영역 */
.card-body {
    width: 100%;
    padding: 20px 22px 18px 22px;
}

.meta-row {
    font-size: 0.95rem;
    font-weight: 700;
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
}

.subject-row {
    font-size: 1.7rem;
    font-weight: 800;
    color: #232634;
    margin-bottom: 14px;
    line-height: 1.3;
}

.info-box {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 16px;
    padding: 14px 14px 12px 14px;
    height: 100%;
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
    line-height: 1.45;
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
    line-height: 1.5;
}

.updated-text {
    margin-top: 10px;
    text-align: right;
    font-size: 0.75rem;
    color: #9CA3AF;
}

/* 인풋 둥글게 */
.stTextInput input, .stDateInput input {
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)
