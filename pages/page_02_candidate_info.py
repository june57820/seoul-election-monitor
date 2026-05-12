from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    CANDIDATE_ORDER,
    SOURCE_LABELS,
    format_number,
    format_percent,
    get_candidate_channels,
    get_candidate_summary,
    get_evidence_samples,
    get_issue_change_table,
    get_issue_detail_timeseries,
    get_issue_mood_timeseries,
    get_issue_summary,
    get_keyword_summary,
    get_source_summary,
    get_source_timeseries,
    short_date_text,
)


def _issue_line_chart(period_key: str, issue: str, source: str, metric: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, metric)
    fig = go.Figure()

    if metric == "후보 간 격차":
        pivot = detail.pivot_table(index="date", columns="candidate", values="reaction_count", fill_value=0)
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
        if not gap.empty:
            spike = gap.sort_values("gap", ascending=False).iloc[0]
            fig.add_vline(x=spike["date"], line_width=1, line_dash="dash", line_color="#94a3b8")
            fig.add_annotation(
                x=spike["date"],
                y=spike["gap"],
                text=f"격차 최대<br>{short_date_text(spike['date'])}",
                showarrow=True,
                arrowhead=2,
                bgcolor="#ffffff",
                bordercolor="#cbd5e1",
                borderwidth=1,
            )
    else:
        for candidate in CANDIDATE_ORDER:
            data = detail[detail["candidate"].eq(candidate)]
            if data.empty:
                continue
            y_col = "metric_value"
            suffix = "건" if metric == "반응량" else "점" if metric == "반응점수" else "%"
            fig.add_trace(
                go.Scatter(
                    x=data["date"],
                    y=data[y_col],
                    mode="lines+markers+text",
                    name=f"{candidate} ({metric})",
                    line=dict(color=CANDIDATE_COLORS[candidate], width=3),
                    marker=dict(size=8),
                    text=data[y_col].map(lambda value: f"{value:,.0f}" if metric == "반응량" else f"{value:.1f}"),
                    textposition="top center",
                    textfont=dict(size=11, color=CANDIDATE_COLORS[candidate]),
                    customdata=data[["daily_change", "top_keywords", "reaction_score"]],
                    hovertemplate=(
                        "%{x|%Y.%m.%d}<br>%{fullData.name}: %{y:,.1f}"
                        + suffix
                        + "<br>전일 대비 %{customdata[0]:+.1f}%<br>주요 연관 키워드: %{customdata[1]}<extra></extra>"
                    ),
                )
            )
        if not detail.empty:
            spike = detail.sort_values("reaction_count", ascending=False).iloc[0]
            fig.add_vline(x=spike["date"], line_width=1, line_dash="dash", line_color="#94a3b8")
            fig.add_annotation(
                x=spike["date"],
                y=spike["metric_value"],
                text=f"반응 급증일<br>{short_date_text(spike['date'])}",
                showarrow=True,
                arrowhead=2,
                bgcolor="#ffffff",
                bordercolor="#bfdbfe",
                borderwidth=1,
            )

    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=340), width="stretch")


def _mood_stacked_chart(period_key: str, issue: str, source: str) -> None:
    mood = get_issue_mood_timeseries(period_key, issue, source)
    colors = {"우호 표현": "#22c55e", "중립 표현": "#94a3b8", "비판 표현": "#ef3340"}
    fig = go.Figure()
    for label in ["우호 표현", "중립 표현", "비판 표현"]:
        data = mood[mood["reaction_label"].eq(label)]
        fig.add_trace(
            go.Bar(
                x=data["date"],
                y=data["count"],
                name=label,
                marker_color=colors[label],
                hovertemplate="%{x|%Y.%m.%d}<br>" + label + ": %{y:,}건<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.08, x=0))
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=190), width="stretch")


def _surge_card(period_key: str, issue: str, source: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    if detail.empty:
        ui.notice("선택 조건의 반응 급등일을 찾을 수 없습니다.", "warning")
        return
    surge = detail.sort_values("daily_change", ascending=False).head(2)
    rows = []
    for _, row in surge.iterrows():
        tone = "blue" if row["candidate"] == "정원오" else "red"
        rows.append(
            f'<tr><td><span class="badge {tone}">{row["candidate"]}</span></td>'
            f'<td>{short_date_text(row["date"])}</td>'
            f'<td class="num">{format_number(row["reaction_count"])}</td>'
            f'<td class="num {tone}-text">{format_percent(row["daily_change"], signed=True)}</td></tr>'
        )
    html = (
        '<div class="card">'
        '<div class="section-title" style="margin-top:0"><h2>반응 급등일 TOP 1</h2><span>공개 온라인 반응량 기준</span></div>'
        '<table class="html-table">'
        '<thead><tr><th>후보</th><th>급등일</th><th class="num">반응량</th><th class="num">전일 대비</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        '<div class="table-note">월·일 중심으로 표시하며, 실제 지지율 급등이 아닙니다.</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def _ai_summary(period_key: str, issue: str, source: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    if detail.empty:
        return
    totals = detail.groupby("candidate")["reaction_count"].sum()
    leader = totals.sort_values(ascending=False).index[0]
    spike = detail.sort_values("reaction_count", ascending=False).iloc[0]
    keywords = str(spike["top_keywords"])
    other = "오세훈" if leader == "정원오" else "정원오"
    st.markdown(
        f"""
        <div class="card">
            <div class="section-title" style="margin-top:0"><h2>AI 보조 요약</h2><span>선택 쟁점·기간 기준</span></div>
            <div class="insight-title" style="font-size:16px; text-align:left;">
                {issue} 쟁점에서는 {short_date_text(spike['date'])}에 공개 온라인 반응이 크게 증가했습니다.
            </div>
            <div class="insight-body" style="text-align:left;">
                {leader} 후보는 {keywords} 관련 키워드에서 반응이 집중되었고, {other} 후보도 같은 기간 관련 반응이 함께 관측됩니다.
                이 문장은 데모 데이터 기반 보조 요약이며, 실제 지지율·득표율·선거 결과 예측이 아닙니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _source_timeseries_card(period_key: str, issue: str, source: str) -> None:
    source_ts = get_source_timeseries(period_key, issue, source)
    if source_ts.empty:
        ui.notice("선택 조건의 출처별 시계열 데이터가 없습니다.", "warning")
        return
    grouped = source_ts.groupby(["date", "source_label"], as_index=False)["reaction_count"].sum()
    fig = go.Figure()
    palette = {"뉴스": "#2563eb", "영상·게시글": "#ef3340", "댓글": "#22c55e", "커뮤니티/X": "#f97316"}
    for label, data in grouped.groupby("source_label"):
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=data["reaction_count"],
                mode="lines",
                name=label,
                line=dict(color=palette.get(label, "#64748b"), width=2),
                hovertemplate="%{x|%Y.%m.%d}<br>%{fullData.name}: %{y:,}건<extra></extra>",
            )
        )
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=220), width="stretch")


def _mood_distribution(period_key: str, issue: str, source: str) -> None:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    colors = {"우호 표현": "#22c55e", "중립 표현": "#94a3b8", "비판 표현": "#ef3340"}
    cols = st.columns(2, gap="small")
    for col, candidate in zip(cols, CANDIDATE_ORDER):
        data = detail[detail["candidate"].eq(candidate)]
        values = [
            int(data["favorable_count"].sum()),
            int(data["neutral_count"].sum()),
            int(data["critical_count"].sum()),
        ]
        fig = go.Figure(
            go.Pie(
                labels=["우호 표현", "중립 표현", "비판 표현"],
                values=values,
                hole=0.62,
                marker=dict(colors=[colors["우호 표현"], colors["중립 표현"], colors["비판 표현"]]),
                textinfo="percent",
            )
        )
        fig.update_layout(showlegend=False, annotations=[dict(text=candidate, x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=CANDIDATE_COLORS[candidate]))])
        with col:
            st.plotly_chart(ui.styled_plotly(fig, height=210), width="stretch")


def render(data: dict, period_key: str, context: dict) -> None:
    selected_issue = ui.selected_issue_from_query("교통")
    summary = get_candidate_summary(period_key)
    issue_summary = get_issue_summary(period_key)

    left, center, right = st.columns([1.05, 0.95, 1.05], gap="medium")
    with left:
        st.markdown(ui.candidate_card(summary[summary["candidate"].eq("정원오")].iloc[0]), unsafe_allow_html=True)
    with center:
        st.markdown(ui.issue_insight(selected_issue, issue_summary), unsafe_allow_html=True)
    with right:
        st.markdown(ui.candidate_card(summary[summary["candidate"].eq("오세훈")].iloc[0]), unsafe_allow_html=True)

    ui.metric_explainer()

    with st.expander("후보 공식 채널 보기", expanded=False):
        channels = get_candidate_channels()
        c1, c2 = st.columns(2, gap="large")
        with c1:
            ui.section_title("정원오 공식 채널")
            ui.official_channel_buttons(channels, "정원오")
        with c2:
            ui.section_title("오세훈 공식 채널")
            ui.official_channel_buttons(channels, "오세훈")

    top_left, top_right = st.columns([0.86, 1.14], gap="large")
    with top_left:
        ui.section_title("쟁점별 반응 점유율", "지지율이 아닌 공개 온라인 반응 비중")
        ui.issue_selector(issue_summary, selected_issue, page="candidate")
    with top_right:
        keywords = get_keyword_summary(period_key)
        ui.section_title("연관 키워드 클러스터", f"현재 쟁점: {selected_issue}")
        k1, k2 = st.columns(2, gap="small")
        with k1:
            st.markdown('<div class="mini-kpi-title blue-text">정원오 연관 키워드</div>', unsafe_allow_html=True)
            st.markdown(ui.keyword_cloud(keywords, "정원오", selected_issue), unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="mini-kpi-title red-text">오세훈 연관 키워드</div>', unsafe_allow_html=True)
            st.markdown(ui.keyword_cloud(keywords, "오세훈", selected_issue), unsafe_allow_html=True)

    ui.section_title(f"선택 쟁점 시계열 상세 - {selected_issue}", "차트별 필터는 이 영역과 하단 산출물에 함께 적용됩니다.")
    source, metric = ui.filter_row("issue_chart", selected_issue)
    source_label = SOURCE_LABELS.get(source, "전체")

    chart_col, insight_col = st.columns([1.45, 0.8], gap="large")
    with chart_col:
        _issue_line_chart(period_key, selected_issue, source, metric)
        _mood_stacked_chart(period_key, selected_issue, source)
    with insight_col:
        _ai_summary(period_key, selected_issue, source)
        _surge_card(period_key, selected_issue, source)

    ui.section_title(f"기간별 변화 상세표 ({selected_issue})", source_label)
    ui.render_change_table(get_issue_change_table(period_key, selected_issue, source), limit=context["days"])

    source_col, mood_col = st.columns([1.05, 0.95], gap="large")
    with source_col:
        ui.section_title(f"출처별 시계열 비교 ({selected_issue})", source_label)
        _source_timeseries_card(period_key, selected_issue, source)
    with mood_col:
        ui.section_title(f"후보별 반응 분위기 분포", f"{selected_issue}, {context['label']}")
        _mood_distribution(period_key, selected_issue, source)

    ui.section_title("연관어 순위 변동", "상승·하락 화살표와 색상으로 표시")
    rank_left, rank_right = st.columns(2, gap="large")
    issue_keywords = get_keyword_summary(period_key, selected_issue)
    with rank_left:
        st.markdown('<div class="mini-kpi-title blue-text">정원오</div>', unsafe_allow_html=True)
        ui.render_keyword_rank_table(issue_keywords, "정원오")
    with rank_right:
        st.markdown('<div class="mini-kpi-title red-text">오세훈</div>', unsafe_allow_html=True)
        ui.render_keyword_rank_table(issue_keywords, "오세훈")

    ui.section_title("근거 샘플", "현재 선택 쟁점·출처·기간 기준")
    candidate, reaction_type, sort = ui.selected_evidence_filters()
    evidence = get_evidence_samples(
        period_key,
        issue=selected_issue,
        source=source,
        candidate=candidate,
        reaction_type=reaction_type,
        sort=sort,
    )
    ui.render_evidence_table(evidence, limit=8, include_issue=False)
    ui.demo_link_notice_button("candidate_demo_link_notice")
