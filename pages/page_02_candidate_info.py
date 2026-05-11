from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import CANDIDATE_COLORS, candidate_summary, format_number


JWO_POINTS = [
    ("균형발전·생활권 혁신", "권역별 균형발전 및 생활 인프라 확충"),
    ("주거안정·모두의 주거", "공공임대 확대와 주거비 부담 완화"),
    ("교육·청년 기회 확대", "교육환경 개선 및 청년 일자리 지원"),
]

OSH_POINTS = [
    ("교통 혁신·도시 인프라", "GTX 확충 및 교통망 고도화"),
    ("도시개발·매력도시 서울", "재개발·재건축 활성화 및 규제 완화"),
    ("창업·일자리 활성화", "창업 생태계 조성과 일자리 창출"),
]


def _mini_chart(frames: dict) -> None:
    fig = go.Figure()
    for code, label in [("JWO", "정원오"), ("OSH", "오세훈")]:
        daily = frames["daily"][frames["daily"]["candidate_code"].eq(code)]
        fig.add_trace(
            go.Scatter(
                x=daily["metric_date"],
                y=daily["reaction_score"],
                mode="lines+markers",
                name=label,
                line=dict(color=CANDIDATE_COLORS[code], width=3),
                marker=dict(size=8),
            )
        )
    fig.update_yaxes(range=[0, 100])
    st.plotly_chart(ui.styled_plotly(fig, height=300), width="stretch")


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title(
        "후보 기본정보 비교",
        "후보의 주요 이력과 정책, 경력, 공식 채널, 최근 온라인 반응 점수를 같은 기준으로 비교합니다.",
    )
    ui.notice("본 화면의 정보는 공개 자료를 바탕으로 정리한 데모 예시입니다. 수치는 실제 지지율이 아닙니다.", "gray")

    summary = candidate_summary(frames)
    left, right = st.columns(2, gap="large")
    with left:
        ui.profile_card(summary[summary["candidate_code"].eq("JWO")].iloc[0], "blue", JWO_POINTS)
    with right:
        ui.profile_card(summary[summary["candidate_code"].eq("OSH")].iloc[0], "red", OSH_POINTS)

    left2, right2 = st.columns([1, 1], gap="large")
    with left2:
        st.markdown(
            """
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>기본정보 기반 비교 요약</h2></div>
                <div class="ai-text">
                    본 페이지는 후보의 주요 이력, 학력, 공식 채널, 핵심 포인트와 더불어
                    선택 기간의 온라인 반응 점수 및 증가율을 함께 확인할 수 있는 비교 화면입니다.
                    후보의 배경 정보와 최근 공개 온라인 반응 흐름을 종합적으로 비교해 보세요.
                </div>
                <div class="notice gray" style="margin-top:18px;">
                    모든 정보는 공표된 자료와 공식 채널을 기반으로 하며, 실시간 반영 주기에 따라 업데이트됩니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        totals = summary.set_index("candidate_code")
        st.markdown(
            f"""
            <div class="card" style="margin-top:16px;">
                <div class="kpi-grid">
                    {ui.kpi_card("정원오 총 반응량", format_number(totals.loc["JWO", "total_reactions"]), context["title"], "blue")}
                    {ui.kpi_card("오세훈 총 반응량", format_number(totals.loc["OSH", "total_reactions"]), context["title"], "red")}
                    {ui.kpi_card("분석 기준", context["range_text"], "선택 기간")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right2:
        ui.section_title(f"{context['title']} 반응 비교")
        _mini_chart(frames)
