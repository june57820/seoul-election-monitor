# 서울시장 선거 여론 모니터 - 공개 온라인 반응으로 보는 두 후보 비교와 주요 쟁점 흐름

서울시 공공데이터 활용 공모전 창업 파트 제출용 Streamlit 데모 대시보드입니다.

이 프로젝트는 실제 선거 예측 서비스가 아니라, 공개 온라인 반응 데이터에서 관측되는 후보별 반응량, 언급량, 댓글 분위기, 연관어, 출처별 흐름을 시민이 쉽게 비교해볼 수 있게 만든 데모입니다.

## 중요 안내

- 현재 데이터는 `data/mock/` 폴더의 mock CSV입니다.
- 이 데이터는 여론조사나 투표 예측이 아닙니다.
- 표시된 수치는 실제 지지율, 득표율, 선거 결과 예측을 의미하지 않습니다.
- 공개 온라인 반응 지표는 실제 여론조사나 지지율이 아니라 참고용 온라인 반응량 지표입니다.
- 성별·연령대 분석은 현재 데이터에 없으므로 제외했습니다.
- 기기별 클릭 비율, 지역별 유권자 분포, 당선 가능성, 선거 결과 예측도 포함하지 않습니다.

## 실행 방법

```bash
pip install -r requirements.txt
python scripts/generate_mock_data.py
streamlit run app.py
```

Streamlit Community Cloud 배포 시 main file path는 `streamlit_app.py`로 지정하면 됩니다.

## 외부 공유용 임시 공개 링크

계정 없이 바로 외부 공유 링크를 만들려면 Windows PowerShell에서 다음을 실행합니다.

```powershell
.\scripts\start_public_share.ps1
```

실행 후 출력되는 `https://...trycloudflare.com` 주소를 다른 사람에게 공유하면 됩니다. 이 방식은 발표·시연용 임시 터널이며, PC와 Streamlit 서버가 켜져 있는 동안만 접속됩니다.

공유를 중지하려면 다음을 실행합니다.

```powershell
.\scripts\stop_public_share.ps1
```

영구 배포가 필요하면 Streamlit Community Cloud, Render, Railway, Cloud Run 같은 호스팅에 올리고 `data_loader.py`와 mock CSV를 함께 배포하면 됩니다. 자세한 절차는 `DEPLOYMENT.md`를 참고하세요.

## 파일 구조

```text
seoul_election_monitor/
  app.py
  data_loader.py
  components.py
  scripts/
    generate_mock_data.py
  data/
    mock/
  pages/
    page_01_home.py
    page_02_candidate_info.py
    page_03_reaction_trend.py
    page_04_source_metrics.py
    page_05_keywords_issues.py
    page_06_sentiment.py
    page_07_evidence.py
    page_08_data_guide.py
  requirements.txt
  README.md
```

## 실제 DB 연동 계획

현재는 CSV 기반 mock data를 읽습니다. 실제 DB가 들어오면 `data_loader.py`의 로드 함수만 교체하면 페이지와 차트 컴포넌트는 그대로 재사용할 수 있도록 분리했습니다.

## 지표 설명

온라인 반응 점수는 뉴스·영상·게시글·댓글에서 관측된 언급량과 반응량을 0~100 범위로 환산한 참고 점수입니다. 실제 지지율이 아닙니다.

대략적인 계산 방향은 다음과 같습니다.

```text
reaction_score =
  normalized_mention_count * 0.35
  + normalized_comment_count * 0.35
  + normalized_content_count * 0.20
  + normalized_growth_rate * 0.10
```

## mock data

`scripts/generate_mock_data.py`는 최소 30일치 mock CSV를 생성합니다.

- `candidates.csv`
- `daily_metrics.csv`
- `source_metrics.csv`
- `keyword_metrics.csv`
- `sentiment_metrics.csv`
- `evidence_items.csv`
- `narrative_summary.csv`
- `collection_status.csv`
