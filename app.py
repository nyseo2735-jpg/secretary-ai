else:
    st.markdown('<div class="page-title">📒 KVMA 회장님 일정</div>', unsafe_allow_html=True)

    # 필터 영역
    st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
    st.markdown('<div class="filter-caption">검색어 · 카테고리 · 날짜로 빠르게 찾기</div>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([2.4, 1.3, 1.2, 0.6])

    search = fc1.text_input(
        "검색",
        placeholder="회의명 / 대상 / 장소 검색",
        label_visibility="collapsed"
    )

    category_options = ["전체"] + CATEGORIES
    selected_cat = fc2.selectbox(
        "카테고리",
        options=category_options,
        index=category_options.index(st.session_state.selected_cat) if st.session_state.selected_cat in category_options else 0,
        label_visibility="collapsed"
    )
    st.session_state.selected_cat = selected_cat

    f_date = fc3.date_input(
        "날짜",
        value=datetime.now(),
        label_visibility="collapsed"
    )

    if fc4.button("전체", use_container_width=True):
        st.session_state.selected_cat = "전체"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 필터링
    df = st.session_state.data.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    disp = df[df["Date"] == f_date]

    if st.session_state.selected_cat != "전체":
        disp = disp[disp["Category"] == st.session_state.selected_cat]

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
        c = COLOR_MAP.get(row["Category"], COLOR_MAP["기타"])

        if st.session_state.edit_id == row["ID"]:
            with st.form(key=f"ed_{row['ID']}"):
                u_sub = st.text_input("회의명", row["Subject"])
                c1, c2, c3 = st.columns(3)
                u_time = c1.text_input("시간", row["Time"])
                u_tar = c2.text_input("대상", row["Target"])
                u_loc = c3.text_input("장소", row["Location"])
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
            # 카드 바깥 프레임 시작
            st.markdown(
                f'''
                <div class="card-wrap" style="background:{c["bg"]};">
                    <div class="card-inner">
                        <div class="card-accent" style="background:{c["line"]};"></div>
                        <div class="card-body">
                            <div class="meta-row" style="color:{c["text"]};">
                                ⏰ {row["Time"]}
                                <span class="category-pill"
                                      style="background:{c["soft"]}; color:{c["text"]}; border-color:{c["line"]};">
                                      {row["Category"]}
                                </span>
                            </div>
                            <div class="subject-row">{row["Subject"]}</div>
                ''',
                unsafe_allow_html=True
            )

            info1, info2, info3 = st.columns(3)
            with info1:
                st.markdown(f"""
                <div class="info-box">
                    <div class="info-label">장소</div>
                    <div class="info-value">📍 {row["Location"] if row["Location"] else "-"}</div>
                </div>
                """, unsafe_allow_html=True)

            with info2:
                st.markdown(f"""
                <div class="info-box">
                    <div class="info-label">대상</div>
                    <div class="info-value">👤 {row["Target"] if row["Target"] else "-"}</div>
                </div>
                """, unsafe_allow_html=True)

            with info3:
                st.markdown(f"""
                <div class="info-box">
                    <div class="info-label">동행 / 수행</div>
                    <div class="info-value">👥 {row["Companion"] if row["Companion"] else "-"} / {row["Staff"] if row["Staff"] else "-"}</div>
                </div>
                """, unsafe_allow_html=True)

            plan1, plan2 = st.columns(2)
            with plan1:
                st.markdown(f"""
                <div class="info-box" style="margin-top:12px;">
                    <div class="info-label">🎯 목적</div>
                    <div class="info-value">{row["Purpose"] if row["Purpose"] else "-"}</div>
                </div>
                """, unsafe_allow_html=True)

            with plan2:
                st.markdown(f"""
                <div class="info-box" style="margin-top:12px;">
                    <div class="info-label">📋 대응 방향</div>
                    <div class="info-value">{row["ActionPlan"] if row["ActionPlan"] else "-"}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="memo-note">
                <div class="memo-title">📌 Memo</div>
                <div class="memo-text">{row["Memo"] if row["Memo"] else "-"}</div>
                <div class="memo-text" style="margin-top:6px;">ℹ️ {row["ExtraInfo"] if row["ExtraInfo"] else "-"}</div>
            </div>
            """, unsafe_allow_html=True)

            if row["Updated"]:
                st.markdown(
                    f'<div class="updated-text">updated. {row["Updated"]}</div>',
                    unsafe_allow_html=True
                )

            # 카드 닫기
            st.markdown('</div></div></div>', unsafe_allow_html=True)

            _, btn_col = st.columns([19, 1])
            if btn_col.button("📝", key=f"edit_{row['ID']}"):
                st.session_state.edit_id = row["ID"]
                st.rerun()
