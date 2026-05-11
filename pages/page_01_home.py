from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    SOURCE_LABELS,
    candidate_summary,
    collection_status,
    competition_share,
    format_number,
    issue_share,
    keyword_summary,
    narrative,
    source_totals,
)


def _line_chart(frames: dict) -> None:
    daily = frames["daily"]
    fig = go.Figure()
    for code, name in [("JWO", "정원오"), ("OSH", "오세훈")]:
        candidate_daily = daily[daily["candidate_code"].eq(code)]
        fig.add_trace(
            go.Scatter(
                x=candidate_daily["metric_date"],
                y=candidate_daily["total_reactions"],
                mode="lines+markers",
                name=name,
                line=dict(color=CANDIDATE_COLORS[code], width=3),
                marker=dict(size=8),
            )
        )
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=290), width="stretch")


def _source_cards(frames: dict) -> None:
    totals = source_totals(frames)
    cards = []
    for _, row in totals.iterrows():
        cards.append(
            ui.kpi_card(
                SOURCE_LABELS[row["source"]],
                f"{row['share']:.1f}%",
                f"{format_number(row['reaction_count'])}건",
            )
        )
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="table-note">총 수집 데이터: {format_number(totals["reaction_count"].sum())}건</div>',
        unsafe_allow_html=True,
    )


def _surge_card(frames: dict) -> None:
    daily = frames["daily"].sort_values("growth_rate", ascending=False).iloc[0]
    keywords = keyword_summary(frames, top_n=5)
    top_keywords = keywords[keywords["candidate_code"].eq(daily["candidate_code"])]["keyword"].head(4).tolist()
    color = "blue" if daily["candidate_code"] == "JWO" else "red"
    st.markdown(
        f"""
        <div class="card">
            <div class="section-title" style="margin-top:0"><h2>반응 급등 알림</h2></div>
            <div class="chip {color}">{ui.candidate_name(daily['candidate_code'])}</div>
            <div style="font-size:28px; font-weight:900; margin-top:12px;" class="{color}-text">
                {daily['metric_date'].strftime('%m.%d')} 반응 급등 감지
            </div>
            <div style="font-size:18px; font-weight:850; margin-top:6px;">전일 대비 {daily['growth_rate']:+.1f}%</div>
            <div class="metric-label" style="margin-top:16px">주요 원인으로 추정되는 키워드</div>
            {ui.keyword_chips(top_keywords, color)}
        </div>
        """,
        unsafe_allow_html=True,
    )
    ui.nav_button("관련 근거 샘플 보기", f"home_surge_evidence_{daily['candidate_code']}")


def _data_status(frames: dict, context: dict) -> None:
    status = collection_status(frames)
    st.markdown(
        f"""
        <div class="card">
            <div class="section-title" style="margin-top:0"><h2>데이터 현황</h2></div>
            <div class="notice" style="background:#f0fdf4; border-color:#bbf7d0; color:#166534;">
                수집 상태 <b style="float:right;">{status['collection_status']}</b>
            </div>
            <div style="display:grid; grid-template-columns:1fr auto; gap:8px; margin-top:14px;">
                <div class="metric-label">마지막 업데이트</div><div>{status['updated_at']}</div>
                <div class="metric-label">분석 기간</div><div>{context['range_text']}</div>
                <div class="metric-label">수집 항목</div><div>{format_number(status['total_items'])}건</div>
            </div>
            <div class="notice gray" style="margin-top:14px;">본 서비스는 실제 지지율·득표율이 아닌 공개 온라인 반응 비교 데이터입니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title("양자대결 홈", f"선택 기간: {context['title']} ({context['range_text']})")

    summary = candidate_summary(frames)
    share = competition_share(summary)
    keywords = keyword_summary(frames, top_n=3)

    left, center, right = st.columns([1.05, 1.3, 1.05], gap="large")
    with left:
        row = summary[summary["candidate_code"].eq("JWO")].iloc[0]
        top_keywords = keywords[keywords["candidate_code"].eq("JWO")]["keyword"].head(3).tolist()
        st.markdown(ui.candidate_home_card(row, top_keywords, "blue"), unsafe_allow_html=True)
    with center:
        ui.competition_bar(share)
    with right:
        row = summary[summary["candidate_code"].eq("OSH")].iloc[0]
        top_keywords = keywords[keywords["candidate_code"].eq("OSH")]["keyword"].head(3).tolist()
        st.markdown(ui.candidate_home_card(row, top_keywords, "red"), unsafe_allow_html=True)

    story = narrative(frames, context["period_key"])
    ui.ai_summary(f"{story['headline_text']} {story['summary_text']} 공개 온라인 반응 기준입니다.")

    col1, col2, col3 = st.columns([1.25, 0.8, 1], gap="large")
    with col1:
        ui.section_title(f"{context['title']} 온라인 반응 추이")
        _line_chart(frames)
        totals = summary.set_index("candidate_code")
        st.markdown(
            f"""
            <div class="metric-grid">
                <div class="metric-cell"><div class="metric-label">정원오 총 반응량</div><div class="metric-value blue-text">{format_number(totals.loc['JWO','total_reactions'])}</div></div>
                <div class="metric-cell"><div class="metric-label">오세훈 총 반응량</div><div class="metric-value red-text">{format_number(totals.loc['OSH','total_reactions'])}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        _surge_card(frames)
    with col3:
        ui.section_title("쟁점별 양자 비교", context["title"])
        ui.issue_compare_rows(issue_share(frames), limit=5)

    col4, col5, col6 = st.columns([1, 1.15, 1], gap="large")
    with col4:
        ui.section_title("출처별 반응 비중", context["title"])
        _source_cards(frames)
    with col5:
        st.markdown(ui.term_glossary_card(), unsafe_allow_html=True)
    with col6:
        _data_status(frames, context)
