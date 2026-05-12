from __future__ import annotations

import runpy
from pathlib import Path

import streamlit as st

import components as ui
from data_loader import DATA_DIR, load_data
from pages import (
    page_01_home,
    page_02_candidate_info,
    page_03_reaction_trend,
    page_04_source_metrics,
    page_08_data_guide,
)


ROOT_DIR = Path(__file__).resolve().parent

ROUTES = {
    "home": page_01_home.render,
    "candidate": page_02_candidate_info.render,
    "trend": page_03_reaction_trend.render,
    "evidence": page_04_source_metrics.render,
    "guide": page_08_data_guide.render,
}

REQUIRED_DATA = [
    "candidates.csv",
    "candidate_channels.csv",
    "reaction_timeseries.csv",
    "issue_summary.csv",
    "issue_detail_timeseries.csv",
    "source_summary.csv",
    "keyword_summary.csv",
    "evidence_samples.csv",
    "collection_status.csv",
]


def ensure_mock_data() -> None:
    if all((DATA_DIR / filename).exists() for filename in REQUIRED_DATA):
        return
    runpy.run_path(str(ROOT_DIR / "scripts" / "generate_mock_data.py"), run_name="__main__")
    if hasattr(load_data, "cache_clear"):
        load_data.cache_clear()


def normalize_page() -> str:
    page = st.query_params.get("page") or st.session_state.get("selected_page", "home")
    if page not in ROUTES:
        page = "home"
    st.session_state.selected_page = page
    return page


def initialize_state() -> None:
    defaults = {
        "selected_period": "7d",
        "selected_issue": "교통",
        "selected_source_for_issue_chart": "전체",
        "selected_metric_for_issue_chart": "반응량",
        "selected_candidate_for_table": "전체",
        "selected_reaction_type_for_evidence": "전체",
        "selected_sort_for_evidence": "최신순",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def main() -> None:
    st.set_page_config(
        page_title="서울시장 선거 여론 모니터 - 공개 온라인 반응으로 보는 두 후보 비교와 주요 쟁점 흐름",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    ensure_mock_data()
    initialize_state()
    ui.inject_css()

    page = normalize_page()
    ui.render_sidebar(page)
    ui.render_header(page)
    period_key, context = ui.render_period_controls()

    data = load_data()
    render = ROUTES[page]
    render(data, period_key, context)


if __name__ == "__main__":
    main()
