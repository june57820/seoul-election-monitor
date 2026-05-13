from __future__ import annotations

import streamlit as st

import components as ui
from data_loader import (
    ISSUE_ORDER,
    SOURCE_LABELS,
    SOURCE_OPTIONS,
    get_collection_status,
    get_evidence_samples,
    get_issue_detail_timeseries,
    short_date_text,
)


def _context_filters() -> tuple[str, str]:
    st.session_state.setdefault("selected_issue", "교통")
    st.session_state.setdefault("selected_source_for_evidence_data_page", "전체")
    cols = st.columns([0.34, 0.44, 0.22], gap="small")
    with cols[0]:
        issue = st.selectbox("쟁점", ISSUE_ORDER, key="selected_issue")
    with cols[1]:
        source = st.radio(
            "출처",
            list(SOURCE_OPTIONS.keys()),
            format_func=lambda key: SOURCE_OPTIONS[key],
            horizontal=True,
            key="selected_source_for_evidence_data_page",
        )
    with cols[2]:
        st.markdown(
            '<div class="table-note" style="margin-top:31px;">데이터 안내와 근거 샘플 표가 함께 갱신됩니다.</div>',
            unsafe_allow_html=True,
        )
    return issue, source


def _data_method_card(period_key: str, context: dict) -> None:
    status = get_collection_status(period_key)
    st.markdown(
        ui.collection_status_card(
            status,
            context,
            title="데이터 안내",
            note="반응 분위기 분석은 공개 텍스트를 우호 표현, 중립 표현, 비판 표현으로 분류한 데모 결과입니다. 공개 온라인 반응 데모용 seed data 기준입니다.",
        ),
        unsafe_allow_html=True,
    )


def _evidence_context_label(period_key: str, issue: str, source: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    if detail.empty:
        label = f"현재 근거 샘플: {issue} 쟁점"
    else:
        date = detail.sort_values("reaction_count", ascending=False).iloc[0]["date"]
        label = f"현재 근거 샘플: {issue} 쟁점 · {short_date_text(date)} 반응 집중일 기준"
    st.markdown(f'<div class="note-card">{label}<br/>근거 샘플은 mock data이며 실제 원문 링크를 제공하지 않습니다.</div>', unsafe_allow_html=True)


def render(data: dict, period_key: str, context: dict) -> None:
    ui.section_title("근거·데이터 안내", "mock 근거 샘플과 데이터 수집 기준")

    issue, source = _context_filters()
    _evidence_context_label(period_key, issue, source)

    left, right = st.columns([1.35, 0.75], gap="large")
    with left:
        ui.section_title("근거 샘플", "현재 선택된 쟁점·출처·후보·반응 유형 기준")
        candidate, reaction_type, sort = ui.selected_evidence_filters()
        evidence = get_evidence_samples(
            period_key,
            issue=issue,
            source=source,
            candidate=candidate,
            reaction_type=reaction_type,
            sort=sort,
        )
        ui.render_evidence_table(evidence, limit=12, include_issue=False)
        ui.demo_link_notice_button("evidence_data_page_demo_link_notice")
    with right:
        _data_method_card(period_key, context)

    with st.expander("분석 방법 안내", expanded=False):
        st.write(
            "본 화면은 공개 온라인 반응 데이터의 흐름을 설명하기 위한 데모입니다. "
            "근거 샘플은 mock data이며 실제 외부 원문 링크를 제공하지 않습니다. "
            "성별, 연령대, 지역별 유권자 분포와 선거 결과형 지표는 포함하지 않습니다."
        )
