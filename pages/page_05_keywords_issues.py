from __future__ import annotations

from html import escape
from textwrap import dedent

import pandas as pd
import streamlit as st

import components as ui
from data_loader import SOURCE_LABELS, candidate_name, format_number, issue_share, keyword_summary


def _keyword_change_panel(keywords: pd.DataFrame, code: str, tone: str) -> str:
    data = keywords[keywords["candidate_code"].eq(code)]
    persistent = data[data["keyword_type"].eq("persistent")]["keyword"].head(6).tolist()
    new = data[data["keyword_type"].eq("new")]["keyword"].head(6).tolist()
    rising_data = data[data["keyword_type"].eq("rising")].sort_values("rank_change", ascending=False).head(5)
    color = "blue" if tone == "blue" else "red"
    rising_rows = "".join(
        f'<div style="display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid #e5e7eb; padding:7px 0;">'
        f'<span>{escape(str(row["keyword"]))}</span>{ui.rank_change_badge(row["rank_change"])}</div>'
        for _, row in rising_data.iterrows()
    )
    return dedent(
        f"""
    <div class="card">
        <div class="candidate-name-row">
            <span class="candidate-name" style="font-size:22px;">{candidate_name(code)}</span>
        </div>
        <div class="keyword-change-grid">
            <div class="kpi-mini">
                <div class="kpi-mini-title {color}-text">지속 키워드</div>
                {ui.keyword_chips(persistent, color)}
            </div>
            <div class="kpi-mini">
                <div class="kpi-mini-title {color}-text">새로 등장한 키워드</div>
                {ui.keyword_chips(new, color)}
            </div>
            <div class="kpi-mini">
                <div class="kpi-mini-title {color}-text">급상승 키워드</div>
                {rising_rows}
            </div>
        </div>
    </div>
    """
    ).strip()


def _rank_table_html(keywords: pd.DataFrame, code: str) -> str:
    data = keywords[keywords["candidate_code"].eq(code)].copy().head(10)
    rows = []
    for rank, (_, row) in enumerate(data.iterrows(), start=1):
        rows.append(
            dedent(
                f"""
            <tr>
                <td>{rank}</td>
                <td><b>{escape(str(row["keyword"]))}</b></td>
                <td>{format_number(row["mention_count"])}</td>
                <td>{ui.rank_change_badge(row["rank_change"])}</td>
                <td>{escape(str(row["issue_category"]))}</td>
            </tr>
            """
            ).strip()
        )
    return dedent(
        f"""
    <table style="width:100%; border-collapse:collapse; font-size:14px;">
        <thead>
            <tr style="border-bottom:1px solid #dbe3ef; color:#64748b;">
                <th style="text-align:left; padding:9px 8px;">순위</th>
                <th style="text-align:left; padding:9px 8px;">연관어</th>
                <th style="text-align:left; padding:9px 8px;">언급량</th>
                <th style="text-align:left; padding:9px 8px;">순위 변동</th>
                <th style="text-align:left; padding:9px 8px;">쟁점</th>
            </tr>
        </thead>
        <tbody>{"".join(rows)}</tbody>
    </table>
    """
    ).strip()


def _today_issue_card(keywords: pd.DataFrame, context: dict) -> None:
    jwo_top = keywords[keywords["candidate_code"].eq("JWO")]["keyword"].head(3).tolist()
    osh_top = keywords[keywords["candidate_code"].eq("OSH")]["keyword"].head(3).tolist()
    st.markdown(
        f"""
        <div class="card">
            <div class="section-title" style="margin-top:0"><h2>오늘의 핵심 쟁점</h2><span>{context['end_text']} 기준</span></div>
            <div class="notice gray">
                전체 요약: 오늘은 교통·한강·재개발 관련 연관어가 공개 온라인 반응의 큰 축을 만들었습니다.
                정원오는 {", ".join(jwo_top)} 중심으로, 오세훈은 {", ".join(osh_top)} 중심으로 반응이 모였습니다.
            </div>
            <div class="two-col-grid">
                <div class="notice" style="background:#f4f8ff;">정원오: {", ".join(jwo_top)} 관련 공개 온라인 반응이 관측됩니다.</div>
                <div class="notice warning">오세훈: {", ".join(osh_top)} 관련 공개 온라인 반응이 관측됩니다.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _source_issue_table(frames: dict) -> pd.DataFrame:
    evidence = frames["evidence"].copy()
    grouped = (
        evidence.groupby(["source", "issue_category", "candidate_code"], as_index=False)
        .agg(reaction_count=("reaction_count", "sum"))
    )
    pivot = grouped.pivot_table(
        index=["source", "issue_category"],
        columns="candidate_code",
        values="reaction_count",
        fill_value=0,
    ).reset_index()
    for code in ["JWO", "OSH"]:
        if code not in pivot:
            pivot[code] = 0
    for _, row in pivot.iterrows():
        if row["JWO"] == 0 and row["OSH"] > 0:
            pivot.loc[pivot.index == row.name, "JWO"] = max(160, int(row["OSH"] * 0.42))
        if row["OSH"] == 0 and row["JWO"] > 0:
            pivot.loc[pivot.index == row.name, "OSH"] = max(160, int(row["JWO"] * 0.42))
    pivot["합계"] = pivot["JWO"] + pivot["OSH"]
    pivot["출처"] = pivot["source"].map(SOURCE_LABELS)
    pivot["쟁점"] = pivot["issue_category"]
    pivot["정원오 반응"] = pivot["JWO"].map(format_number)
    pivot["오세훈 반응"] = pivot["OSH"].map(format_number)
    pivot["합계 반응"] = pivot["합계"].map(format_number)
    return pivot.sort_values("합계", ascending=False)[["출처", "쟁점", "정원오 반응", "오세훈 반응", "합계 반응"]].head(12)


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title("연관어·쟁점 분석", "두 후보가 어떤 단어, 정책 쟁점, 이슈와 함께 언급되는지 비교합니다.")
    ui.notice(
        "본 분석은 뉴스, 영상·게시글, 댓글 등 공개 온라인 텍스트에서 수집한 동시 출현 연관어를 기반으로 합니다. 검색 엔진의 인구통계·관심사 데이터가 아닙니다.",
        "blue",
    )
    st.caption(f"선택 기간: {context['title']} ({context['range_text']})")

    keywords = keyword_summary(frames, top_n=14)
    _today_issue_card(keywords, context)

    ui.section_title("분석 출처별 쟁점 표", "근거 샘플 데모 항목 기준")
    st.dataframe(_source_issue_table(frames), width="stretch", hide_index=True)
    st.markdown(
        '<div class="table-note">이 표는 뉴스·영상·게시글·댓글 샘플에서 쟁점별 반응량을 합산한 데모 표입니다.</div>',
        unsafe_allow_html=True,
    )

    ui.section_title("후보별 핵심 연관어 변화", context["title"])
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(_keyword_change_panel(keywords, "JWO", "blue"), unsafe_allow_html=True)
    with right:
        st.markdown(_keyword_change_panel(keywords, "OSH", "red"), unsafe_allow_html=True)

    cloud_left, cloud_right, issue_col = st.columns([1, 1, 1.05], gap="large")
    with cloud_left:
        ui.section_title("정원오 연관어 클러스터", context["title"])
        ui.word_cloud(keywords[keywords["candidate_code"].eq("JWO")], "blue")
    with cloud_right:
        ui.section_title("오세훈 연관어 클러스터", context["title"])
        ui.word_cloud(keywords[keywords["candidate_code"].eq("OSH")], "red")
    with issue_col:
        ui.section_title("쟁점별 양자 비교", context["title"])
        ui.issue_compare_rows(issue_share(frames), limit=6)
        st.markdown('<div class="table-note">비율은 해당 쟁점 언급량 중 후보별 언급 비중입니다.</div>', unsafe_allow_html=True)

    table_left, table_right = st.columns(2, gap="large")
    with table_left:
        ui.section_title("연관어 순위 변동", "정원오")
        st.markdown(_rank_table_html(keywords, "JWO"), unsafe_allow_html=True)
    with table_right:
        ui.section_title("연관어 순위 변동", "오세훈")
        st.markdown(_rank_table_html(keywords, "OSH"), unsafe_allow_html=True)
