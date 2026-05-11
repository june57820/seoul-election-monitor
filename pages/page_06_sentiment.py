from __future__ import annotations

from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st

import components as ui
from data_loader import candidate_name, daily_sentiment_long, format_number, keyword_summary, sentiment_summary


REACTION_COLORS = {
    "우호 표현": "#16a34a",
    "중립 표현": "#94a3b8",
    "비판 표현": "#ef3340",
}


def _ratio_cards(frames: dict) -> None:
    summary = sentiment_summary(frames).set_index("candidate_code")
    cards = []
    for code, tone in [("JWO", "blue"), ("OSH", "red")]:
        row = summary.loc[code]
        cards.append(
            dedent(
                f"""
            <div class="card">
                <div class="candidate-name-row">
                    <span class="candidate-name" style="font-size:22px;">{candidate_name(code)}</span>
                </div>
                <div class="kpi-grid">
                    {ui.kpi_card("우호 표현", f"{row['positive_ratio']:.1f}%", format_number(row["positive_count"]), "green")}
                    {ui.kpi_card("중립 표현", f"{row['neutral_ratio']:.1f}%", format_number(row["neutral_count"]))}
                    {ui.kpi_card("비판 표현", f"{row['negative_ratio']:.1f}%", format_number(row["negative_count"]), "red")}
                </div>
            </div>
            """
            ).strip()
        )
    st.markdown(f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">{"".join(cards)}</div>', unsafe_allow_html=True)


def _stacked_chart(frames: dict) -> None:
    long = daily_sentiment_long(frames)
    long["후보"] = long["candidate_code"].map(candidate_name)
    fig = px.bar(
        long,
        x="metric_date",
        y="count",
        color="reaction_label",
        facet_col="후보",
        barmode="stack",
        color_discrete_map=REACTION_COLORS,
        labels={"metric_date": "날짜", "count": "반응 수", "reaction_label": "분류"},
    )
    fig.update_yaxes(tickformat=",")
    fig.for_each_annotation(lambda annotation: annotation.update(text=annotation.text.split("=")[-1]))
    styled = ui.styled_plotly(fig, height=390)
    styled.update_layout(
        margin=dict(l=20, r=20, t=76, b=76),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0),
    )
    st.plotly_chart(styled, width="stretch")


def _negative_surge(frames: dict) -> None:
    sentiment = frames["sentiment"].copy()
    sentiment["negative_delta"] = sentiment.groupby("candidate_code")["negative_count"].diff().fillna(0)
    row = sentiment.sort_values("negative_delta", ascending=False).iloc[0]
    code = row["candidate_code"]
    tone = "blue" if code == "JWO" else "red"
    st.markdown(
        f"""
        <div class="card">
            <div class="section-title" style="margin-top:0"><h2>비판 반응 급증일</h2></div>
            <div class="badge {tone}">{candidate_name(code)}</div>
            <div style="font-size:28px; font-weight:900; margin-top:12px;" class="{tone}-text">
                {row['metric_date'].strftime('%Y.%m.%d')}
            </div>
            <div class="metric-grid">
                <div class="metric-cell"><div class="metric-label">비판 표현 수</div><div class="metric-value red-text">{format_number(row['negative_count'])}</div></div>
                <div class="metric-cell"><div class="metric-label">전일 대비 증가</div><div class="metric-value red-text">{format_number(row['negative_delta'])}</div></div>
            </div>
            <div class="notice gray" style="margin-top:14px;">해당 날짜의 반응은 특정 쟁점 게시물 확산과 댓글 참여 증가에 영향을 받을 수 있습니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _keyword_table(frames: dict) -> pd.DataFrame:
    keywords = keyword_summary(frames, top_n=12)
    display = keywords.head(18).copy()
    display["후보"] = display["candidate_code"].map(candidate_name)
    display["반응 단어"] = display["keyword"]
    display["분류"] = display["keyword_type"].map({"persistent": "지속", "new": "신규", "rising": "급상승"})
    display["언급량"] = display["mention_count"].map(format_number)
    return display[["후보", "반응 단어", "issue_category", "분류", "언급량"]].rename(columns={"issue_category": "쟁점"})


def _keyword_chip_panel(keywords: pd.DataFrame, code: str, tone: str) -> str:
    data = keywords[keywords["candidate_code"].eq(code)].head(8)
    rows = "".join(
        dedent(
            f"""
        <div style="display:flex; justify-content:space-between; gap:10px; border-bottom:1px solid #e5e7eb; padding:8px 0;">
            <span>{row['keyword']}</span>
            <b>{format_number(row['mention_count'])}</b>
        </div>
        """
        ).strip()
        for _, row in data.iterrows()
    )
    top_chips = ui.keyword_chips(data["keyword"].head(5).tolist(), tone)
    return dedent(
        f"""
    <div class="card">
        <div class="section-title" style="margin-top:0"><h2>{candidate_name(code)} 주요 반응 단어</h2></div>
        <div class="reason-text">반응 분위기와 함께 자주 나타난 단어를 빈도순으로 정리했습니다. 연관어 클러스터 시각화는 연관어·쟁점 분석 페이지에서만 제공합니다.</div>
        {top_chips}
        <div style="margin-top:12px;">{rows}</div>
    </div>
    """
    ).strip().replace("\n", "")


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title("긍/부정 반응 분석", f"{context['title']} 기준")
    ui.notice(
        "본 페이지는 댓글과 공개 텍스트의 우호 표현·중립 표현·비판 표현 분포를 보여줍니다. 실제 여론이나 지지율이 아닙니다.",
        "blue",
    )

    _ratio_cards(frames)

    left, right = st.columns([1.35, 0.8], gap="large")
    with left:
        ui.section_title("일별 반응 분위기 추이")
        _stacked_chart(frames)
    with right:
        _negative_surge(frames)

    keywords = keyword_summary(frames, top_n=14)
    cloud_left, cloud_right, table_col = st.columns([0.85, 0.85, 1.05], gap="large")
    with cloud_left:
        st.markdown(_keyword_chip_panel(keywords, "JWO", "blue"), unsafe_allow_html=True)
    with cloud_right:
        st.markdown(_keyword_chip_panel(keywords, "OSH", "red"), unsafe_allow_html=True)
    with table_col:
        ui.section_title("반응 관련 상위 키워드")
        st.dataframe(_keyword_table(frames), width="stretch", hide_index=True)

    ui.notice(
        "본 분석은 뉴스, 영상·게시글, 댓글의 텍스트를 자동 분류한 결과입니다. 비꼼, 반어, 맥락에 따라 분류 오류가 있을 수 있으므로 근거 샘플과 함께 확인해야 합니다.",
        "warning",
    )
