from __future__ import annotations

import runpy
from pathlib import Path

import streamlit as st

import components as ui
from data_loader import DATA_DIR, PERIOD_OPTIONS, filter_period, load_data, period_context
from pages import (
    page_01_home,
    page_02_candidate_info,
    page_03_reaction_trend,
    page_04_source_metrics,
    page_05_keywords_issues,
    page_06_sentiment,
    page_07_evidence,
    page_08_data_guide,
)


ROOT_DIR = Path(__file__).resolve().parent

PAGES = [
    ("home", "양자대결 홈", page_01_home.render),
    ("candidate", "후보 기본정보 비교", page_02_candidate_info.render),
    ("trend", "온라인 반응 추이", page_03_reaction_trend.render),
    ("source", "출처별 핵심지표", page_04_source_metrics.render),
    ("keywords", "연관어·쟁점 분석", page_05_keywords_issues.render),
    ("sentiment", "긍/부정 반응 분석", page_06_sentiment.render),
    ("evidence", "근거 샘플", page_07_evidence.render),
    ("guide", "데이터 안내", page_08_data_guide.render),
]


def ensure_mock_data() -> None:
    required = [
        "candidates.csv",
        "daily_metrics.csv",
        "source_metrics.csv",
        "keyword_metrics.csv",
        "sentiment_metrics.csv",
        "evidence_items.csv",
        "narrative_summary.csv",
        "collection_status.csv",
    ]
    if all((DATA_DIR / filename).exists() for filename in required):
        return
    runpy.run_path(str(ROOT_DIR / "scripts" / "generate_mock_data.py"), run_name="__main__")


def render_period_selector() -> str:
    if "period_key" not in st.session_state:
        st.session_state.period_key = "7d"

    labels = {key: value["label"] for key, value in PERIOD_OPTIONS.items()}
    selected = st.radio(
        "기간 선택",
        options=list(PERIOD_OPTIONS.keys()),
        format_func=lambda key: labels[key],
        horizontal=True,
        key="period_key",
    )
    return selected


def render_page_selector() -> str:
    page_keys = [key for key, _, _ in PAGES]
    query_page = st.query_params.get("page")
    if query_page in page_keys:
        st.session_state.selected_page = query_page
    elif "selected_page" not in st.session_state:
        st.session_state.selected_page = "home"

    if st.session_state.selected_page not in page_keys:
        st.session_state.selected_page = "home"

    columns = st.columns(len(PAGES), gap="small")
    for column, (key, label, _) in zip(columns, PAGES):
        button_type = "primary" if st.session_state.selected_page == key else "secondary"
        if column.button(label, key=f"nav_{key}", type=button_type, width="stretch"):
            st.session_state.selected_page = key
            st.query_params["page"] = key
            st.rerun()
    return st.session_state.selected_page


def main() -> None:
    st.set_page_config(
        page_title="서울시장 선거 여론 모니터 - 공개 온라인 반응으로 보는 두 후보 비교와 주요 쟁점 흐름",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    ensure_mock_data()
    ui.inject_css()

    ui.render_title_header()
    _, period_col = st.columns([0.76, 0.24])
    with period_col:
        period_key = render_period_selector()

    selected_page = render_page_selector()
    ui.demo_notice()

    data = load_data()
    frames = filter_period(data, period_key)
    context = period_context(data, period_key)

    for key, _, render in PAGES:
        if key == selected_page:
            render(data, frames, context)
            break

    st.markdown(
        """
        <div class="table-note" style="margin-top:24px;">
            모든 수치는 선택 기간 내 공개 온라인 텍스트와 반응량을 바탕으로 만든 데모 데이터입니다.
            실제 지지율·득표율·선거 결과 예측이 아닙니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
