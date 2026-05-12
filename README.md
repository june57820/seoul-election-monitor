# 서울시장 선거 여론 모니터

공개 온라인 반응으로 보는 두 후보 비교와 주요 쟁점 흐름을 보여주는 Python + Streamlit 기반 데모 대시보드입니다.

본 대시보드는 공개 온라인 반응을 수집·분석한 데모 화면이며, 실제 지지율·득표율·선거 결과 예측이 아닙니다.

## 실행 방법

```powershell
pip install -r requirements.txt
python scripts/generate_mock_data.py
streamlit run streamlit_app.py
```

Streamlit Community Cloud의 main file path는 `streamlit_app.py`입니다.

## 화면 구조

- 개요: 후보 요약, 전체 공개 온라인 반응 흐름, 핵심 쟁점 스냅샷
- 후보·쟁점: 쟁점 클릭, 선택 쟁점 시계열, 반응 분위기, 출처 비교, 근거 샘플
- 추이·출처: 전체 기간 흐름과 출처별 게시물·댓글 수 비교
- 반응·근거: 우호·중립·비판 표현 분포와 mock 근거 샘플
- 데이터 안내: mock CSV 구조, 제외 항목, 향후 DB 전환 지점

## 데이터 구조

주요 mock CSV는 `data/mock/`에 있습니다.

- `candidates.csv`
- `candidate_channels.csv`
- `reaction_timeseries.csv`
- `issue_summary.csv`
- `issue_detail_timeseries.csv`
- `source_summary.csv`
- `keyword_summary.csv`
- `evidence_samples.csv`
- `collection_status.csv`

기존 페이지 호환을 위해 `daily_metrics.csv`, `source_metrics.csv`, `keyword_metrics.csv`, `sentiment_metrics.csv`, `evidence_items.csv`도 함께 생성됩니다.

## 향후 DB 연결 지점

`data_loader.py`의 아래 함수들을 DB 쿼리 기반으로 교체하면 UI 코드는 대부분 유지할 수 있습니다.

- `get_reaction_timeseries()`
- `get_issue_summary()`
- `get_issue_detail_timeseries()`
- `get_source_summary()`
- `get_evidence_samples()`
- `get_candidate_summary()`

## 제외 항목

이 데모에는 실제 지지율, 득표율 예측, 당선 가능성, 선거 결과 예측, 성별·연령대·기기별 클릭 비율, 지역별 유권자 분포, 이슈 확산 경로 시각화가 포함되지 않습니다.
