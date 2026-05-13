from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    CANDIDATE_ORDER,
    SOURCE_LABELS,
    SOURCE_OPTIONS,
    format_number,
    get_reaction_timeseries,
    get_source_summary,
    get_source_timeseries,
)


def _trend_filters() -> tuple[str, str, str]:
    st.session_state.setdefault("selected_candidate_for_trend", "전체")
    st.session_state.setdefault("selected_source_for_trend_chart", "전체")
    st.session_state.setdefault("selected_metric_for_trend_chart", "반응량")
    cols = st.columns([0.32, 0.38, 0.30], gap="small")
    with cols[0]:
        st.markdown('<div class="control-label">후보 보기</div>', unsafe_allow_html=True)
        candidate = st.radio(
            "후보 보기",
            ["전체", *CANDIDATE_ORDER],
            horizontal=True,
            key="selected_candidate_for_trend",
            label_visibility="collapsed",
        )
    with cols[1]:
        st.markdown('<div class="control-label">출처</div>', unsafe_allow_html=True)
        source = st.radio(
            "출처",
            list(SOURCE_OPTIONS.keys()),
            format_func=lambda key: SOURCE_OPTIONS[key],
            horizontal=True,
            key="selected_source_for_trend_chart",
            label_visibility="collapsed",
        )
    with cols[2]:
        st.markdown('<div class="control-label">지표</div>', unsafe_allow_html=True)
        metric = st.radio(
            "지표",
            ["반응량", "반응점수", "후보 간 격차"],
            horizontal=True,
            key="selected_metric_for_trend_chart",
            label_visibility="collapsed",
        )
    return candidate, source, metric


def _overall_chart(period_key: str, candidate: str, source: str, metric: str) -> None:
    trend = get_reaction_timeseries(period_key, candidate, source, metric)
    fig = go.Figure()
    if metric == "후보 간 격차":
        pivot = trend.pivot_table(index="date", columns="candidate", values="reaction_count", fill_value=0)
        gap = (pivot.get("정원오", 0) - pivot.get("오세훈", 0)).abs().reset_index(name="gap")
        fig.add_trace(
            go.Scatter(
                x=gap["date"],
                y=gap["gap"],
                mode="lines+markers",
                name="후보 간 격차",
                line=dict(color="#334155", width=3, dash="dot"),
                marker=dict(size=8),
                hovertemplate="%{x|%Y.%m.%d}<br>격차: %{y:,}건<extra></extra>",
            )
        )
    else:
        for candidate_name in CANDIDATE_ORDER:
            data = trend[trend["candidate"].eq(candidate_name)]
            if data.empty:
                continue
            y_col = "metric_value"
            fig.add_trace(
                go.Scatter(
                    x=data["date"],
                    y=data[y_col],
                    mode="lines+markers",
                    name=candidate_name,
                    line=dict(color=CANDIDATE_COLORS[candidate_name], width=3),
                    marker=dict(size=7),
                    customdata=data[["daily_change"]],
                    hovertemplate="%{x|%Y.%m.%d}<br>%{fullData.name}: %{y:,.1f}<br>전일 대비 %{customdata[0]:+.1f}%<extra></extra>",
                )
            )
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=380), width="stretch")


def _source_comparison(period_key: str, source: str) -> None:
    summary = get_source_summary(period_key, source=source)
    if summary.empty:
        ui.notice("선택한 출처 조건의 데이터가 없습니다.", "warning")
        return
    fig = go.Figure()
    for metric, color in [("content_count", "#2563eb"), ("comment_count", "#ef3340")]:
        grouped = summary.groupby("source_label", as_index=False)[metric].sum()
        fig.add_trace(
            go.Bar(
                x=grouped["source_label"],
                y=grouped[metric],
                name="게시물 수" if metric == "content_count" else "댓글 수",
                marker_color=color,
                text=grouped[metric].map(lambda value: f"{value:,}"),
                textposition="outside",
            )
        )
    fig.update_layout(barmode="group")
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=300), width="stretch")


def _source_table(period_key: str, source: str) -> None:
    summary = get_source_summary(period_key, source=source)
    rows = []
    for _, row in summary.sort_values(["source_label", "candidate"]).iterrows():
        tone = "blue" if row["candidate"] == "정원오" else "red"
        rows.append(
            f'<tr><td>{row["source_label"]}</td>'
            f'<td><span class="badge {tone}">{row["candidate"]}</span></td>'
            f'<td class="num">{format_number(row["content_count"])}</td>'
            f'<td class="num">{format_number(row["comment_count"])}</td>'
            f'<td class="num">{format_number(row["reaction_count"])}</td></tr>'
        )
    html = (
        '<table class="html-table">'
        '<thead><tr><th>출처</th><th>후보</th><th class="num">게시물 수</th><th class="num">댓글 수</th><th class="num">반응량</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _source_timeseries(period_key: str, source: str) -> None:
    data = get_source_timeseries(period_key, source=source)
    grouped = data.groupby(["date", "source_label"], as_index=False)["reaction_count"].sum()
    fig = go.Figure()
    palette = {"뉴스": "#2563eb", "영상·게시글": "#ef3340", "댓글": "#22c55e", "커뮤니티/X": "#f97316"}
    for label, frame in grouped.groupby("source_label"):
        fig.add_trace(
            go.Scatter(
                x=frame["date"],
                y=frame["reaction_count"],
                mode="lines+markers",
                name=label,
                line=dict(color=palette.get(label, "#64748b"), width=3),
                marker=dict(size=6),
                hovertemplate="%{x|%Y.%m.%d}<br>%{fullData.name}: %{y:,}건<extra></extra>",
            )
        )
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=320), width="stretch")


def render(data: dict, period_key: str, context: dict) -> None:
    ui.section_title("추이·출처", "전체 공개 온라인 반응 흐름과 출처별 변화")

    candidate, source, metric = _trend_filters()
    ui.metric_explainer(compact=True)
    source_label = SOURCE_LABELS.get(source, "전체")

    left, right = st.columns([1.35, 0.85], gap="large")
    with left:
        ui.section_title("전체 공개 온라인 반응 흐름", f"{context['title']} · {source_label}")
        _overall_chart(period_key, candidate, source, metric)
    with right:
        ui.section_title("출처별 게시물·댓글 수", "출처 필터 기준")
        _source_comparison(period_key, source)

    bottom_left, bottom_right = st.columns([0.95, 1.05], gap="large")
    with bottom_left:
        ui.section_title("출처별 상세표", "빈 셀 없이 숫자로 표시")
        _source_table(period_key, source)
    with bottom_right:
        ui.section_title("출처별 시계열 비교", "전체 기간 변화")
        _source_timeseries(period_key, source)

    st.caption("출처별 수치는 공개 온라인 반응 데모용 seed data 기준입니다.")
