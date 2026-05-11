from __future__ import annotations

import pandas as pd
import streamlit as st

import components as ui
from data_loader import SOURCE_LABELS, candidate_name, collection_status, format_number


def _prepare_evidence(frame: pd.DataFrame) -> pd.DataFrame:
    display = frame.copy()
    display["날짜"] = display["published_date"].dt.strftime("%Y.%m.%d")
    display["후보"] = display["candidate_code"].map(lambda code: candidate_name(code))
    display["출처"] = display["source"].map(SOURCE_LABELS)
    display["제목 / 요약"] = display["title"] + "\n" + display["summary"]
    display["반응 수"] = display["reaction_count"].map(format_number)
    display["자료 상태"] = "데모 데이터"
    return display[["날짜", "후보", "outlet", "issue_category", "제목 / 요약", "반응 수", "자료 상태"]].rename(
        columns={"outlet": "매체", "issue_category": "쟁점"}
    )


def _filter_evidence(evidence: pd.DataFrame, candidate: str, source: str, issue: str) -> pd.DataFrame:
    filtered = evidence.copy()
    if candidate != "전체 후보":
        filtered = filtered[filtered["candidate_code"].eq(candidate)]
    if source != "전체 출처":
        filtered = filtered[filtered["source"].eq(source)]
    if issue != "전체 쟁점":
        filtered = filtered[filtered["issue_category"].eq(issue)]
    return filtered.sort_values(["published_date", "reaction_count"], ascending=[False, False])


def _evidence_table(frame: pd.DataFrame) -> None:
    if frame.empty:
        st.info("선택한 조건에 해당하는 근거 샘플이 없습니다.")
        return
    st.dataframe(
        _prepare_evidence(frame).head(20),
        width="stretch",
        hide_index=True,
    )
    st.caption("데모 데이터이므로 외부 링크는 연결하지 않았습니다.")


def render(data: dict, frames: dict, context: dict) -> None:
    ui.section_title("근거 샘플", "수치와 해석의 근거가 되는 기사, 영상·게시글, 댓글 샘플 형식의 데모 데이터입니다.")

    ui.section_title("왜 이렇게 나왔나요?")
    ui.reason_cards(
        [
            ("오세훈 반응 증가", "GTX 노선 발표, 한강 관리 계획 등 교통·도시 개발 관련 뉴스와 영상 확산이 반응 증가를 이끌었습니다.", ["교통", "한강", "도시개발"]),
            ("정원오 반응 증가", "재개발·청년주거 정책 발표와 청년 정책 관련 게시글·댓글 확산이 우호 표현 증가에 기여했습니다.", ["재개발", "청년정책", "주거"]),
            ("쟁점 이슈 집중", "교통 혼잡 완화, 한강 개발 방향, 재개발 속도와 공공성 논점이 양 진영에서 높은 관심과 토론을 만들었습니다.", ["교통", "한강", "재개발"]),
        ]
    )

    evidence = frames["evidence"]
    left, right = st.columns([1.45, 0.75], gap="large")
    with left:
        ui.section_title("근거 샘플 보기")
        filter_cols = st.columns(3)
        candidate = filter_cols[0].selectbox("후보", ["전체 후보", "JWO", "OSH"], format_func=lambda value: value if value == "전체 후보" else candidate_name(value))
        source = filter_cols[1].selectbox("출처", ["전체 출처", "news", "video_post", "comment"], format_func=lambda value: value if value == "전체 출처" else SOURCE_LABELS[value])
        issues = ["전체 쟁점"] + sorted(evidence["issue_category"].dropna().unique().tolist())
        issue = filter_cols[2].selectbox("쟁점", issues)

        filtered = _filter_evidence(evidence, candidate, source, issue)
        news_tab, video_tab, comment_tab = st.tabs(["뉴스", "영상·게시글", "댓글 샘플"])
        with news_tab:
            _evidence_table(filtered[filtered["source"].eq("news")])
        with video_tab:
            _evidence_table(filtered[filtered["source"].eq("video_post")])
        with comment_tab:
            st.caption("댓글 샘플은 개인정보와 과격 표현을 일부 마스킹한 예시입니다.")
            _evidence_table(filtered[filtered["source"].eq("comment")])

        st.markdown(
            """
            <div class="card" style="margin-top:16px;">
                <div class="section-title" style="margin-top:0"><h2>지표 설명</h2></div>
                <div class="kpi-grid">
                    <div class="kpi-mini"><div class="kpi-mini-title blue-text">온라인 반응 점수</div><div class="reason-text">뉴스·영상·게시글·댓글의 양과 참여도를 종합해 0~100 범위로 환산한 참고 점수입니다. 실제 지지율이 아닙니다.</div></div>
                    <div class="kpi-mini"><div class="kpi-mini-title blue-text">연관어</div><div class="reason-text">후보와 함께 자주 언급되는 단어를 빈도 기준으로 추출하여 표시합니다.</div></div>
                    <div class="kpi-mini"><div class="kpi-mini-title blue-text">반응 분위기</div><div class="reason-text">텍스트 분류를 통해 우호·중립·비판 표현 비율을 기간별로 보여줍니다.</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        status = collection_status(frames)
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>데이터 안내</h2></div>
                <div class="kpi-mini">
                    <div class="kpi-mini-title">데이터 출처</div>
                    <div class="reason-text">뉴스: 주요 언론 기사 본문 및 제목<br/>영상·게시글: YouTube, 블로그, 카페 등<br/>댓글: 공개 댓글</div>
                </div>
                <div style="display:grid; grid-template-columns:1fr auto; gap:8px; margin-top:14px;">
                    <div class="metric-label">마지막 업데이트</div><div>{status['updated_at']}</div>
                    <div class="metric-label">수집 현황</div><div>{status['collection_status']}</div>
                    <div class="metric-label">수집 기간</div><div>{context['range_text']}</div>
                    <div class="metric-label">총 항목</div><div>{format_number(status['total_items'])}건</div>
                </div>
                <div class="notice gray" style="margin-top:14px;">
                    온라인 공개 데이터를 기반으로 하며, 전체 여론을 대표하지 않습니다.
                    봇·중복 게시글·스팸 등은 필터링하나 일부 잔존 가능성이 있습니다.
                </div>
            </div>
            <div class="notice warning" style="margin-top:16px;">
                이 데이터는 여론조사나 투표 예측이 아닙니다.<br/>
                실제 지지율·득표율·선거 결과 예측을 의미하지 않습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
