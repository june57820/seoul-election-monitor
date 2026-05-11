from __future__ import annotations

from textwrap import dedent

import plotly.graph_objects as go
import streamlit as st

import components as ui
from data_loader import (
    CANDIDATE_COLORS,
    SOURCE_DETAIL_LABELS,
    SOURCE_LABELS,
    format_number,
    source_detail_summary,
    source_summary,
    source_totals,
)


def _source_cards(frames: dict) -> None:
    source = source_summary(frames)
    cards = []
    for source_key, label in SOURCE_LABELS.items():
        data = source[source["source"].eq(source_key)].set_index("candidate_code")
        if source_key == "comment":
            metric_html = f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">
                <div style="background:#f4f8ff; border:1px solid #bfdbfe; border-radius:8px; padding:14px;">
                    <div class="badge blue">정원오</div>
                    <div class="metric-label" style="margin-top:10px;">댓글 수</div>
                    <div class="metric-value blue-text">{format_number(data.loc['JWO','comment_count'])}</div>
                </div>
                <div style="background:#fff7f7; border:1px solid #fecdd3; border-radius:8px; padding:14px;">
                    <div class="badge red">오세훈</div>
                    <div class="metric-label" style="margin-top:10px;">댓글 수</div>
                    <div class="metric-value red-text">{format_number(data.loc['OSH','comment_count'])}</div>
                </div>
            </div>
            """
        else:
            metric_html = f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">
                <div style="background:#f4f8ff; border:1px solid #bfdbfe; border-radius:8px; padding:14px;">
                    <div class="badge blue">정원오</div>
                    <div class="metric-label" style="margin-top:10px;">게시물 수</div>
                    <div class="metric-value blue-text">{format_number(data.loc['JWO','content_count'])}</div>
                    <div class="metric-label">댓글 수</div>
                    <b>{format_number(data.loc['JWO','comment_count'])}</b>
                </div>
                <div style="background:#fff7f7; border:1px solid #fecdd3; border-radius:8px; padding:14px;">
                    <div class="badge red">오세훈</div>
                    <div class="metric-label" style="margin-top:10px;">게시물 수</div>
                    <div class="metric-value red-text">{format_number(data.loc['OSH','content_count'])}</div>
                    <div class="metric-label">댓글 수</div>
                    <b>{format_number(data.loc['OSH','comment_count'])}</b>
                </div>
            </div>
            """
        cards.append(
            dedent(
                f"""
                <div class="card">
                    <div class="section-title" style="margin-top:0"><h2>{label}</h2></div>
                    {metric_html}
                    <div class="table-note">반응량: {format_number(data['reaction_count'].sum())}건</div>
                </div>
                """
            ).strip()
        )
    compact_cards = "".join(card.replace("\n", "") for card in cards)
    st.markdown(f'<div class="kpi-grid">{compact_cards}</div>', unsafe_allow_html=True)


def _detail_options(frames: dict) -> dict[str, str | None]:
    available = source_detail_summary(frames)["source_detail"].drop_duplicates().tolist()
    options: dict[str, str | None] = {"전체": None}
    for key, label in SOURCE_DETAIL_LABELS.items():
        if key in available:
            options[label] = key
    return options


def _filtered_detail(frames: dict, detail_key: str | None):
    detail = source_detail_summary(frames)
    if detail_key:
        detail = detail[detail["source_detail"].eq(detail_key)].copy()
    return detail


def _grouped_bar(frames: dict, detail_key: str | None) -> None:
    detail = _filtered_detail(frames, detail_key)
    fig = go.Figure()
    if detail_key:
        detail = detail.assign(candidate_label=detail["candidate_code"].map({"JWO": "정원오", "OSH": "오세훈"}))
        fig.add_trace(
            go.Bar(
                x=detail["candidate_label"],
                y=detail["reaction_count"],
                marker_color=detail["candidate_code"].map(CANDIDATE_COLORS),
                text=detail["reaction_count"].map(lambda value: f"{value:,}"),
                textposition="outside",
            )
        )
        fig.update_layout(showlegend=False)
    else:
        for code, label in [("JWO", "정원오"), ("OSH", "오세훈")]:
            data = detail[detail["candidate_code"].eq(code)]
            fig.add_trace(
                go.Bar(
                    x=data["source_detail_label"],
                    y=data["reaction_count"],
                    name=label,
                    marker_color=CANDIDATE_COLORS[code],
                    text=data["reaction_count"].map(lambda value: f"{value:,}"),
                    textposition="outside",
                )
            )
        fig.update_layout(barmode="group")
    fig.update_yaxes(tickformat=",")
    st.plotly_chart(ui.styled_plotly(fig, height=380), width="stretch")


def _donut(frames: dict) -> None:
    totals = source_totals(frames)
    fig = go.Figure(
        go.Pie(
            labels=totals["source_label"],
            values=totals["reaction_count"],
            hole=0.58,
            marker=dict(colors=["#2563eb", "#ef3340", "#22c55e"]),
            textinfo="label+percent",
        )
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(ui.styled_plotly(fig, height=330), width="stretch")


def _detail_table(frames: dict, detail_key: str | None) -> None:
    detail = _filtered_detail(frames, detail_key).copy()
    detail["출처"] = detail["source_detail_label"]
    detail["구분"] = detail["source_label"]
    detail["후보"] = detail["candidate_code"].map({"JWO": "정원오", "OSH": "오세훈"})
    detail["게시물 수"] = detail.apply(
        lambda row: "해당 없음" if row["source"] == "comment" else format_number(row["content_count"]),
        axis=1,
    )
    detail["댓글 수"] = detail["comment_count"].map(format_number)
    detail["반응량"] = detail["reaction_count"].map(format_number)
    st.dataframe(detail[["출처", "구분", "후보", "게시물 수", "댓글 수", "반응량"]], width="stretch", hide_index=True)


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title("출처별 핵심지표", f"{context['title']} 기준")
    ui.notice(
        "뉴스, 영상·게시글, 댓글을 네이버뉴스·다음뉴스·유튜브처럼 더 구체적인 공개 출처 단위로 나누어 게시물 수, 댓글 수, 반응량을 비교합니다. 실제 지지율이 아닌 공개 온라인 반응 기반 예시입니다.",
        "gray",
    )

    _source_cards(frames)

    options = _detail_options(frames)
    selected_label = st.radio("출처 필터", list(options.keys()), horizontal=True, key="source_metric_filter")
    selected_source = options[selected_label]

    left, right = st.columns([1.18, 0.82], gap="large")
    with left:
        ui.section_title("출처별 반응량 비교", f"현재 보기: {selected_label}")
        _grouped_bar(frames, selected_source)
    with right:
        ui.section_title("선택 출처 게시물·댓글 수", "필터 기준으로 후보별 지표를 표시")
        _detail_table(frames, selected_source)

    left2, right2 = st.columns([0.85, 1.15], gap="large")
    with left2:
        ui.section_title("출처별 비중", "뉴스·영상·게시글·댓글 기준")
        _donut(frames)
    with right2:
        source = source_summary(frames)
        osh_news = source[(source["source"].eq("news")) & (source["candidate_code"].eq("OSH"))]["reaction_count"].iloc[0]
        jwo_news = source[(source["source"].eq("news")) & (source["candidate_code"].eq("JWO"))]["reaction_count"].iloc[0]
        news_text = "오세훈 관련 보도량이 조금 더 많게 관측됩니다" if osh_news >= jwo_news else "정원오 관련 보도량이 조금 더 많게 관측됩니다"
        ui.notice(
            f"뉴스에서는 {news_text}. 유튜브와 커뮤니티는 짧은 영상·게시글 확산의 영향을 크게 받고, 댓글 출처는 특정 쟁점의 토론량에 따라 변동될 수 있습니다.",
            "blue",
        )
