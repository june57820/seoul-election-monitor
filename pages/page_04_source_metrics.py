from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    CANDIDATE_ORDER,
    ISSUE_ORDER,
    SOURCE_LABELS,
    SOURCE_OPTIONS,
    format_number,
    get_collection_status,
    get_evidence_samples,
    get_issue_detail_timeseries,
    short_date_text,
)


def _context_filters() -> tuple[str, str]:
    st.session_state.setdefault("selected_issue", "교통")
    st.session_state.setdefault("selected_source_for_reaction_page", "전체")
    cols = st.columns([0.34, 0.44, 0.22], gap="small")
    with cols[0]:
        issue = st.selectbox("쟁점", ISSUE_ORDER, key="selected_issue")
    with cols[1]:
        source = st.radio(
            "출처",
            list(SOURCE_OPTIONS.keys()),
            format_func=lambda key: SOURCE_OPTIONS[key],
            horizontal=True,
            key="selected_source_for_reaction_page",
        )
    with cols[2]:
        st.markdown(
            '<div class="table-note" style="margin-top:31px;">반응 분위기와 근거 샘플이 함께 갱신됩니다.</div>',
            unsafe_allow_html=True,
        )
    return issue, source


def _mood_timeseries(period_key: str, issue: str, source: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    grouped = (
        detail.groupby(["date", "candidate"], as_index=False)
        .agg(
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
            reaction_count=("reaction_count", "sum"),
        )
        .sort_values("date")
    )
    mood_total = grouped[["favorable_count", "neutral_count", "critical_count"]].sum(axis=1).replace(0, 1)
    grouped["favorable_ratio"] = grouped["favorable_count"] / mood_total * 100
    grouped["neutral_ratio"] = grouped["neutral_count"] / mood_total * 100
    grouped["critical_ratio"] = grouped["critical_count"] / mood_total * 100
    fig = go.Figure()
    mapping = [
        ("우호 표현", "favorable_ratio", "#22c55e"),
        ("중립 표현", "neutral_ratio", "#94a3b8"),
        ("비판 표현", "critical_ratio", "#ef3340"),
    ]
    chart_cols = st.columns(2, gap="medium")
    for chart_col, candidate in zip(chart_cols, CANDIDATE_ORDER):
        data = grouped[grouped["candidate"].eq(candidate)]
        fig = go.Figure()
        for label, column, color in mapping:
            fig.add_trace(
                go.Scatter(
                    x=data["date"],
                    y=data[column],
                    name=label,
                    mode="lines+markers",
                    line=dict(color=color, width=3),
                    marker=dict(size=7, color=color),
                    hovertemplate="%{x|%Y.%m.%d}<br>" + candidate + " " + label + ": %{y:.1f}%<extra></extra>",
                )
            )
        fig.update_yaxes(tickformat=".0f", ticksuffix="%", title="구성비", range=[0, 100])
        fig.update_xaxes(title=None)
        with chart_col:
            tone = "blue" if candidate == "정원오" else "red"
            st.markdown(f'<div class="mini-kpi-title {tone}-text">{candidate} 우호·중립·비판 표현 추이</div>', unsafe_allow_html=True)
            st.plotly_chart(ui.styled_plotly(fig, height=285), width="stretch")


def _mood_cards(period_key: str, issue: str, source: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    cards = []
    for candidate in CANDIDATE_ORDER:
        data = detail[detail["candidate"].eq(candidate)]
        total = max(1, int(data[["favorable_count", "neutral_count", "critical_count"]].sum().sum()))
        favorable = data["favorable_count"].sum() / total * 100
        neutral = data["neutral_count"].sum() / total * 100
        critical = data["critical_count"].sum() / total * 100
        tone = "blue" if candidate == "정원오" else "red"
        cards.append(
            ui.metric_card(
                candidate,
                f"{favorable:.1f}%",
                f"우호 표현 · 중립 {neutral:.1f}% · 비판 {critical:.1f}%",
                tone,
            )
        )
    st.markdown(f'<div class="summary-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


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
    ui.section_title("반응 분위기·근거", "반응 분위기 분석과 mock 근거 샘플")

    issue, source = _context_filters()
    _evidence_context_label(period_key, issue, source)

    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        ui.section_title("후보별 우호·중립·비판 표현 시계열", f"{issue} · {SOURCE_LABELS.get(source, '전체 출처')} · 후보별 개별 그래프")
        _mood_timeseries(period_key, issue, source)
        _mood_cards(period_key, issue, source)
    with right:
        _data_method_card(period_key, context)

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
    ui.demo_link_notice_button("reaction_page_demo_link_notice")

    with st.expander("분석 방법 안내", expanded=False):
        st.write(
            "본 화면은 공개 온라인 반응 데이터의 흐름을 설명하기 위한 데모입니다. "
            "근거 샘플은 mock data이며 실제 외부 원문 링크를 제공하지 않습니다. "
            "성별, 연령대, 지역별 유권자 분포와 선거 결과형 지표는 포함하지 않습니다."
        )
