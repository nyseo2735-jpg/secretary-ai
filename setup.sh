#!/bin/bash

STREAMLIT_HTML=$(python3 -c "import streamlit, os; print(os.path.join(os.path.dirname(streamlit.__file__), 'static', 'index.html'))")

if [ -f "$STREAMLIT_HTML" ]; then
    if ! grep -q "kvma-gap-fix" "$STREAMLIT_HTML"; then
        sed -i "s|</head>|<style id='kvma-gap-fix'>.main [data-testid='stVerticalBlock'],section.main [data-testid='stVerticalBlock'],[data-testid='stMain'] [data-testid='stVerticalBlock']{gap:4px!important;row-gap:4px!important;}[data-testid='stSidebar'] [data-testid='stVerticalBlock']{gap:2px!important;row-gap:2px!important;}</style></head>|" "$STREAMLIT_HTML"
        echo "kvma-gap-fix 주입 완료"
    else
        echo "이미 적용됨 – 스킵"
    fi
else
    echo "index.html 경로를 찾을 수 없음: $STREAMLIT_HTML"
fi
