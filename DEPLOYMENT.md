# 정규 주소 배포 안내

이 프로젝트는 Streamlit 앱이므로 임시 터널 없이 고정 공유 주소를 만들려면 호스팅 서비스에 배포해야 합니다.

## 가장 빠른 방법: Streamlit Community Cloud

예상 결과 주소 예시:

```text
https://seoul-election-monitor.streamlit.app
```

필요한 것:

- GitHub 계정
- 이 프로젝트가 올라간 GitHub 저장소
- Streamlit Community Cloud 계정

배포 설정:

```text
Repository: GitHub에 올린 저장소
Branch: main
Main file path: app.py
Python version: 3.11 또는 3.12
App URL: seoul-election-monitor 등 사용 가능한 이름
```

현재 프로젝트는 배포에 필요한 `requirements.txt`, `.streamlit/config.toml`, `app.py`, mock CSV 데이터를 포함합니다.

## 자체 도메인을 쓰는 방법

`monitor.example.com` 같은 주소를 쓰려면 도메인을 소유해야 합니다. 이 경우 선택지는 두 가지입니다.

1. Streamlit Cloud 또는 Render 같은 호스팅에 먼저 배포한 뒤 도메인을 연결합니다.
2. Cloudflare Named Tunnel을 만들고 도메인의 DNS를 터널에 연결합니다.

두 번째 방식은 주소는 고정되지만, 로컬 PC에서 계속 실행하면 PC가 꺼질 때 접속이 끊깁니다. 공모전 제출용으로는 클라우드 호스팅 방식이 더 안정적입니다.

## 임시 터널과의 차이

`trycloudflare.com` 빠른 터널은 시연용 임시 주소입니다. 프로세스가 종료되면 기존 URL이 사라질 수 있습니다.

정규 배포 주소는 앱이 클라우드 서버에서 실행되므로, 사용자가 링크를 열 때마다 내 PC에 의존하지 않습니다.
