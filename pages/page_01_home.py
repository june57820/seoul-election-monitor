from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    CANDIDATE_ORDER,
    format_number,
    get_candidate_summary,
    get_collection_status,
    get_evidence_samples,
    get_issue_summary,
    get_reaction_timeseries,
    get_source_summary,
)


def _overall_trend(period_key: str) -> None:
    trend = get_reaction_timeseries(period_key)
    fig = go.Figure()
    for candidate in CANDIDATE_ORDER:
        data = trend[trend["candidate"].eq(candidate)]
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=data["reaction_count"],
                mode="lines+markers",
                name=candidate,
                line=dict(color=CANDIDATE_COLORS[candidate], width=3),
                marker=dict(size=7),
                customdata=data[["daily_change"]],
                hovertemplate="%{x|%Y.%m.%d}<br>%{fullData.name}: %{y:,}건<br>전일 대비 %{customdata[0]:+.1f}%<extra></extra>",
            )
        )
    fig.update_yaxes(tickformat=",", title="공개 온라인 반응량")
    st.plotly_chart(ui.styled_plotly(fig, height=300), width="stretch")


def _issue_overview(period_key: str) -> None:
    issue = get_issue_summary(period_key)
    rows = []
    for _, row in issue.head(6).iterrows():
        rows.append(
            ui.metric_card(
                str(row["issue"]),
                format_number(row["total"]),
                f"정원오 {row['정원오_share']:.1f}% · 오세훈 {row['오세훈_share']:.1f}%",
                "blue" if row["정원오_share"] >= row["오세훈_share"] else "red",
            )
        )
    st.markdown(f'<div class="summary-grid">{"".join(rows)}</div>', unsafe_allow_html=True)


def _source_snapshot(period_key: str) -> None:
    source = get_source_summary(period_key)
    totals = source.groupby(["source", "source_label"], as_index=False)["reaction_count"].sum().sort_values("reaction_count", ascending=False)
    cards = []
    for _, row in totals.iterrows():
        cards.append(ui.metric_card(str(row["source_label"]), format_number(row["reaction_count"]), "공개 온라인 반응량"))
    st.markdown(f'<div class="summary-grid">{"".join(cards[:4])}</div>', unsafe_allow_html=True)


def render(data: dict, period_key: str, context: dict) -> None:
    summary = get_candidate_summary(period_key)
    left, center, right = st.columns([1.05, 0.92, 1.05], gap="medium")
    with left:
        st.markdown(ui.candidate_card(summary[summary["candidate"].eq("정원오")].iloc[0], compact=True), unsafe_allow_html=True)
    with center:
        issue = get_issue_summary(period_key)
        selected = st.session_state.get("selected_issue", "교통")
        st.markdown(ui.issue_insight(selected, issue), unsafe_allow_html=True)
    with right:
        st.markdown(ui.candidate_card(summary[summary["candidate"].eq("오세훈")].iloc[0], compact=True), unsafe_allow_html=True)

    ui.metric_explainer(compact=True)

    ui.section_title("전체 공개 온라인 반응 흐름", f"{context['title']} · 후보별 전체 반응량")
    chart_col, side_col = st.columns([1.6, 0.8], gap="large")
    with chart_col:
        _overall_trend(period_key)
    with side_col:
        status = get_collection_status(period_key)
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>데이터 현황</h2></div>
                <div class="mini-kpi">
                    <div class="mini-kpi-title">수집 상태</div>
                    <div class="mini-kpi-value green-text" style="font-size:20px;">{status['collection_status']}</div>
                </div>
                <div style="display:grid; grid-template-columns:1fr auto; gap:8px; margin-top:12px;">
                    <div class="metric-label">수집 기간</div><div>{context['range_text']}</div>
                    <div class="metric-label">마지막 업데이트</div><div>{status['updated_at']}</div>
                    <div class="metric-label">수집 출처</div><div>{status['source_scope']}</div>
                    <div class="metric-label">반응량 합계</div><div>{format_number(status['total_items'])}건</div>
                </div>
                <div class="table-note">수집 현황은 mock data 기준이며 선택한 분석 기간에 맞춰 갱신됩니다.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    lower_left, lower_right = st.columns([1.05, 0.95], gap="large")
    with lower_left:
        ui.section_title("핵심 쟁점 요약", "쟁점별 공개 온라인 반응 비중")
        _issue_overview(period_key)
    with lower_right:
        ui.section_title("출처별 반응 스냅샷", "뉴스·영상·댓글·커뮤니티/X")
        _source_snapshot(period_key)

    evidence = get_evidence_samples(period_key, issue=st.session_state.get("selected_issue", "교통"))
    ui.section_title("최근 근거 샘플", "현재 선택 쟁점 기준 · 실제 원문 링크 미제공")
    ui.render_evidence_table(evidence, limit=5, include_issue=False)
    ui.demo_link_notice_button("home_demo_link_notice")
