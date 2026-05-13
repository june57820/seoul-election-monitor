from __future__ import annotations

import streamlit as st

import components as ui
from data_loader import format_number, get_collection_status, load_data


def render(data: dict, period_key: str, context: dict) -> None:
    ui.section_title("데이터 안내", "데이터 출처, 구조, 한계와 향후 DB 전환 지점")

    status = get_collection_status(period_key)
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>수집·분석 범위</h2></div>
                <ul style="margin:0; padding-left:18px; line-height:1.85;">
                    <li>수집 기간: {context['range_text']}</li>
                    <li>수집 출처: {status['source_scope']}</li>
                    <li>수집 상태: {status['collection_status']}</li>
                    <li>수집 규모: {format_number(status['total_items'])}건</li>
                    <li>마지막 업데이트: {status['updated_at']}</li>
                </ul>
                <div class="note-card" style="margin-top:14px;">이 화면은 mock data 구조와 향후 DB 전환 지점을 설명하기 위한 안내 페이지입니다.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>제외 항목</h2></div>
                <ul style="margin:0; padding-left:18px; line-height:1.85;">
                    <li>선거 결과형 지표</li>
                    <li>후보 선호도처럼 보이는 예측성 수치</li>
                    <li>성별·연령대·기기별 클릭 비율</li>
                    <li>지역별 유권자 분포</li>
                    <li>근거가 부족한 이슈 확산 경로 시각화</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    frames = load_data()
    rows = []
    for name, frame in frames.items():
        rows.append(
            f'<tr><td>{name}</td><td class="num">{format_number(len(frame))}</td><td>{", ".join(frame.columns[:8])}</td></tr>'
        )
    ui.section_title("mock CSV 구조", "Streamlit Cloud 배포 환경에서 상대 경로로 로드")
    html = (
        '<table class="html-table">'
        '<thead><tr><th>데이터셋</th><th class="num">행 수</th><th>주요 컬럼</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )
    st.markdown(html, unsafe_allow_html=True)

    ui.section_title("향후 실제 DB 연결 시 교체 함수", "UI는 데이터 로딩 방식에 직접 의존하지 않도록 분리")
    st.markdown(
        """
        <div class="card">
            <div class="summary-grid">
                <div class="mini-kpi"><div class="mini-kpi-title">get_reaction_timeseries()</div><div class="table-note">전체 후보·출처별 일자 흐름 조회</div></div>
                <div class="mini-kpi"><div class="mini-kpi-title">get_issue_summary()</div><div class="table-note">쟁점별 후보 반응 비중 조회</div></div>
                <div class="mini-kpi"><div class="mini-kpi-title">get_issue_detail_timeseries()</div><div class="table-note">선택 쟁점·출처별 시계열 조회</div></div>
                <div class="mini-kpi"><div class="mini-kpi-title">get_source_summary()</div><div class="table-note">출처별 게시물·댓글·반응량 조회</div></div>
                <div class="mini-kpi"><div class="mini-kpi-title">get_evidence_samples()</div><div class="table-note">mock 근거 샘플 또는 실제 근거 테이블 조회</div></div>
                <div class="mini-kpi"><div class="mini-kpi-title">get_candidate_summary()</div><div class="table-note">후보별 기간 요약 지표 조회</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
