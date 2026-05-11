from __future__ import annotations

import streamlit as st

import components as ui
from data_loader import collection_status, format_number


def render(data: dict, frames: dict, context: dict) -> None:
    status = collection_status(frames)
    ui.section_title("데이터 안내", "데이터 출처, 수집 상태, 지표 정의와 한계를 시민에게 공개합니다.")

    st.markdown(
        """
        <div class="notice warning">
            이 데이터는 여론조사나 투표 예측이 아닙니다.<br/>
            본 서비스는 공개 온라인 출처에서 수집 가능한 반응량과 텍스트 흐름을 보여주는 참고용 대시보드입니다.<br/>
            표시된 수치는 실제 지지율, 득표율, 선거 결과 예측을 의미하지 않습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(
            """
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>데이터 출처 설명</h2></div>
                <div class="kpi-grid">
                    <div class="kpi-mini">
                        <div class="kpi-mini-title blue-text">뉴스</div>
                        <div class="reason-text">주요 언론 기사 제목, 본문, 공개 댓글을 수집 대상으로 가정합니다.</div>
                    </div>
                    <div class="kpi-mini">
                        <div class="kpi-mini-title red-text">영상·게시글</div>
                        <div class="reason-text">유튜브 영상, 블로그, 카페, 커뮤니티 게시글의 공개 텍스트를 대상으로 합니다.</div>
                    </div>
                    <div class="kpi-mini">
                        <div class="kpi-mini-title" style="color:#16a34a;">댓글</div>
                        <div class="reason-text">뉴스, 영상, 게시글에 달린 공개 댓글 중 수집 가능한 댓글을 대상으로 합니다.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="margin-top:16px;">
                <div class="section-title" style="margin-top:0"><h2>수집 상태</h2></div>
                <div style="display:grid; grid-template-columns:1fr auto; gap:12px; font-size:15px;">
                    <div class="metric-label">마지막 업데이트 시간</div><b>{status['updated_at']}</b>
                    <div class="metric-label">수집 상태</div><b style="color:#15803d;">{status['collection_status']}</b>
                    <div class="metric-label">분석 기간</div><b>{context['range_text']}</b>
                    <div class="metric-label">총 수집 항목</div><b>{format_number(status['total_items'])}건</b>
                </div>
                <div class="notice gray" style="margin-top:16px;">{status['warning_text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="card">
                <div class="section-title" style="margin-top:0"><h2>데이터 한계</h2></div>
                <div class="reason-text">
                    공개 온라인 데이터는 전체 시민 의견을 대표하지 않습니다.<br/>
                    특정 플랫폼 이용자, 게시물 확산 방식, 언론 보도량, 중복 댓글의 영향을 받을 수 있습니다.<br/>
                    자동 텍스트 분류는 비꼼, 반어, 맥락을 완벽히 해석하지 못할 수 있습니다.<br/>
                    성별·연령대·기기별 클릭·지역별 유권자 분포는 현재 데이터에 없으므로 분석에서 제외했습니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="card" style="margin-top:16px;">
                <div class="section-title" style="margin-top:0"><h2>지표 설명</h2></div>
                <div class="kpi-mini">
                    <div class="kpi-mini-title blue-text">온라인 반응 점수</div>
                    <div class="reason-text">
                        온라인 반응 점수는 뉴스·영상·게시글·댓글에서 관측된 언급량과 반응량을
                        0~100 범위로 바꾼 참고 점수입니다. 실제 지지율이 아닙니다.
                    </div>
                </div>
                <div class="kpi-mini" style="margin-top:12px;">
                    <div class="kpi-mini-title blue-text">연관어·쟁점</div>
                    <div class="reason-text">
                        후보명과 함께 등장한 단어를 집계해 쟁점별로 묶은 값입니다.
                        실제 검색 로그나 개인 관심사 데이터가 아닙니다.
                    </div>
                </div>
                <div class="kpi-mini" style="margin-top:12px;">
                    <div class="kpi-mini-title blue-text">반응 분위기 분석</div>
                    <div class="reason-text">
                        공개 텍스트를 우호 표현, 중립 표현, 비판 표현으로 자동 분류한 값입니다.
                        근거 샘플과 함께 확인해야 합니다.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="card" style="margin-top:16px;">
            <div class="section-title" style="margin-top:0"><h2>실제 DB 연동 계획</h2></div>
            <div class="reason-text">
                현재 버전은 <b>mock CSV 데이터</b>를 사용합니다.
                실제 DB가 연결되면 <b>data_loader.py</b>의 로드 함수만 교체하고,
                페이지와 차트 컴포넌트는 그대로 재사용할 수 있도록 분리했습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
