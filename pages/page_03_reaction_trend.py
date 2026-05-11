from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    candidate_summary,
    format_number,
    keyword_summary,
    narrative,
)


def _trend_chart(frames: dict) -> None:
    fig = go.Figure()
    for code, label in [("JWO", "정원오"), ("OSH", "오세훈")]:
        daily = frames["daily"][frames["daily"]["candidate_code"].eq(code)]
        fig.add_trace(
            go.Scatter(
                x=daily["metric_date"],
                y=daily["total_reactions"],
                mode="lines+markers",
                name=label,
                line=dict(color=CANDIDATE_COLORS[code], width=3),
                marker=dict(size=8),
            )
        )
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=360), width="stretch")


def _surge_card(frames: dict) -> None:
    daily = frames["daily"].sort_values("growth_rate", ascending=False).iloc[0]
    code = daily["candidate_code"]
    color = "blue" if code == "JWO" else "red"
    keywords = keyword_summary(frames, top_n=5)
    top_keywords = keywords[keywords["candidate_code"].eq(code)]["keyword"].head(4).tolist()
    st.markdown(
        f"""
        <div class="card">
            <div class="section-title" style="margin-top:0"><h2>반응 급등일</h2></div>
            <div style="font-size:30px; font-weight:900;" class="{color}-text">{daily['metric_date'].strftime('%m.%d')}</div>
            <div class="metric-grid">
                <div class="metric-cell"><div class="metric-label">{ui.candidate_name(code)}</div><div class="metric-value {color}-text">{daily['growth_rate']:+.1f}%</div></div>
                <div class="metric-cell"><div class="metric-label">총 반응량</div><div class="metric-value">{format_number(daily['total_reactions'])}</div></div>
            </div>
            <div class="metric-label" style="margin-top:16px">의심 원인 키워드</div>
            {ui.keyword_chips(top_keywords, color)}
            <div class="table-note">평소 기간 평균 대비 반응 증가율을 기준으로 탐지했습니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title("온라인 반응 추이", "최근 기간 동안 후보별 반응량이 어떻게 움직였는지 보여줍니다.")
    ui.notice(
        f"선택 기간: {context['title']} ({context['range_text']})<br/>기간 선택을 변경하면 해당 기간의 온라인 반응 데이터를 기준으로 모든 지표와 차트가 재계산됩니다."
    )

    col1, col2 = st.columns([1.45, 0.85], gap="large")
    with col1:
        ui.section_title(f"{context['title']} 반응 추이")
        _trend_chart(frames)
        summary = candidate_summary(frames).set_index("candidate_code")
        st.markdown(
            f"""
            <div class="metric-grid">
                <div class="metric-cell"><div class="metric-label">정원오 총 반응</div><div class="metric-value blue-text">{format_number(summary.loc['JWO','total_reactions'])}</div></div>
                <div class="metric-cell"><div class="metric-label">오세훈 총 반응</div><div class="metric-value red-text">{format_number(summary.loc['OSH','total_reactions'])}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        _surge_card(frames)

    story = narrative(frames, context["period_key"])
    bottom_left, bottom_right = st.columns([1.35, 0.85], gap="large")
    with bottom_left:
        ui.section_title("왜 이렇게 나왔나요?")
        ui.reason_cards(
            [
                ("교통 이슈 집중 확산", "교통 관련 공약 발표와 보도 증가로 양 후보 모두 관련 반응이 증가했습니다.", ["교통대책", "지하철 연장", "버스노선"]),
                ("영상·게시글 확산 주도", "유튜브, 커뮤니티, SNS에서 짧은 해설형 게시물이 반응을 빠르게 만들었습니다.", ["영상 확산", "커뮤니티", "SNS"]),
                ("댓글 참여 증가", "핵심 쟁점에 대한 공감 및 비판 댓글이 늘며 댓글 수와 공유 수가 함께 증가했습니다.", ["의견 대립", "공감", "참여 확대"]),
            ]
        )
    with bottom_right:
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>요약 한 줄</h2></div>
                <div class="ai-text">{story['headline_text']} {story['competition_text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ui.nav_button("근거 샘플 및 상세 데이터 보기", "trend_summary_to_evidence")
