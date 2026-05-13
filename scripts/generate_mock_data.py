from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "mock"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATES = pd.date_range("2026-01-01", "2026-05-12", freq="D")
RECENT_7_START = pd.Timestamp("2026-05-06")
RECENT_7_END = pd.Timestamp("2026-05-12")

DATA_TYPE = "public_online_reaction_demo_seed"
COLLECTION_STATUS = "mock_seed_from_public_clues"
SEED_NOTE = "이 수치는 실제 지지율·득표율·선거 결과 예측이 아니라 공개 온라인 반응 데모용 수치입니다."

CANDIDATES = [
    {
        "candidate": "정원오",
        "party": "더불어민주당",
        "role": "서울시장 후보",
        "image_file": "jung_won_oh.jpg",
        "profile_summary": "생활권 단위 도시정책과 주거 안정 의제를 강조하는 후보",
        "career": "현) 성동구청장|전) 성동구 부구청장|전) 서울시 정책기획관|전) 행정안전부 지역금융과장",
        "education": "연세대학교 행정학 석사|서울대학교 행정학 학사",
        "display_order": 1,
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "candidate": "오세훈",
        "party": "국민의힘",
        "role": "서울시장 후보",
        "image_file": "oh_naver_profile.jpg",
        "profile_summary": "교통 인프라와 도시 경쟁력 의제를 중심으로 반응이 형성되는 후보",
        "career": "현) 서울특별시장|전) 제38대 서울특별시장|전) 국회의원|전) 한나라당 최고위원",
        "education": "고려대학교 법학 석사|고려대학교 법학 학사",
        "display_order": 2,
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
]

CHANNELS = [
    ("정원오", "공식 홈페이지", "https://www.sd.go.kr/mayor/index.do"),
    ("정원오", "페이스북", "https://www.facebook.com/kindchongwono/"),
    ("정원오", "유튜브", "https://www.youtube.com/channel/UC02pT-cLZ1RQcVxmC7fKIMw"),
    ("정원오", "인스타그램", "https://www.instagram.com/chongwonoh/"),
    ("오세훈", "공식 홈페이지", "https://mayor.seoul.go.kr/app/index.do"),
    ("오세훈", "페이스북", "https://www.facebook.com/ohsehoon4u"),
    ("오세훈", "유튜브", "https://www.youtube.com/@ohsehoontv"),
    ("오세훈", "인스타그램", "https://www.instagram.com/ohsehoon4u/"),
]

ISSUES = ["교통", "한강", "GTX", "도시개발", "지하화", "재개발", "주거", "청년정책"]
CANDIDATE_ORDER = ["정원오", "오세훈"]

SOURCES = {
    "news": {"label": "뉴스", "detail_label": "정책 기사", "content_ratio": 0.045},
    "video_post": {"label": "영상·게시글", "detail_label": "보도영상·SNS", "content_ratio": 0.060},
    "comment": {"label": "댓글", "detail_label": "기사·SNS 댓글", "content_ratio": 0.000},
    "community_x": {"label": "커뮤니티/X", "detail_label": "공개 글·인용", "content_ratio": 0.080},
}

SOURCE_WEIGHTS = {
    ("교통", "정원오"): {"news": 35, "video_post": 22, "comment": 23, "community_x": 20},
    ("교통", "오세훈"): {"news": 38, "video_post": 20, "comment": 23, "community_x": 19},
    ("한강", "정원오"): {"news": 30, "video_post": 15, "comment": 35, "community_x": 20},
    ("한강", "오세훈"): {"news": 32, "video_post": 18, "comment": 35, "community_x": 15},
    ("GTX", "정원오"): {"news": 42, "video_post": 12, "comment": 22, "community_x": 24},
    ("GTX", "오세훈"): {"news": 45, "video_post": 10, "comment": 20, "community_x": 25},
    ("도시개발", "정원오"): {"news": 45, "video_post": 12, "comment": 25, "community_x": 18},
    ("도시개발", "오세훈"): {"news": 46, "video_post": 12, "comment": 28, "community_x": 14},
    ("지하화", "정원오"): {"news": 48, "video_post": 10, "comment": 24, "community_x": 18},
    ("지하화", "오세훈"): {"news": 42, "video_post": 10, "comment": 28, "community_x": 20},
    ("재개발", "정원오"): {"news": 43, "video_post": 10, "comment": 32, "community_x": 15},
    ("재개발", "오세훈"): {"news": 44, "video_post": 12, "comment": 30, "community_x": 14},
    ("주거", "정원오"): {"news": 40, "video_post": 8, "comment": 38, "community_x": 14},
    ("주거", "오세훈"): {"news": 42, "video_post": 10, "comment": 33, "community_x": 15},
    ("청년정책", "정원오"): {"news": 28, "video_post": 22, "comment": 25, "community_x": 25},
    ("청년정책", "오세훈"): {"news": 30, "video_post": 18, "comment": 30, "community_x": 22},
}

RECENT_REACTION_ROWS = [
    ("2026-05-06", "정원오", 2000, 61, 720, 900, 380, 150, 1850),
    ("2026-05-07", "정원오", 4200, 70, 1764, 1806, 630, 252, 3948),
    ("2026-05-08", "정원오", 2600, 66, 936, 1170, 494, 195, 2405),
    ("2026-05-09", "정원오", 2300, 64, 828, 1035, 437, 172, 2128),
    ("2026-05-10", "정원오", 2100, 63, 756, 945, 399, 158, 1942),
    ("2026-05-11", "정원오", 3200, 67, 1152, 1440, 608, 240, 2960),
    ("2026-05-12", "정원오", 4500, 71, 1710, 1980, 810, 270, 4230),
    ("2026-05-06", "오세훈", 2100, 58, 609, 903, 588, 158, 1942),
    ("2026-05-07", "오세훈", 4400, 64, 1364, 1892, 1144, 264, 4136),
    ("2026-05-08", "오세훈", 3000, 62, 870, 1290, 840, 225, 2775),
    ("2026-05-09", "오세훈", 2800, 60, 812, 1204, 784, 210, 2590),
    ("2026-05-10", "오세훈", 3600, 61, 1044, 1548, 1008, 270, 3330),
    ("2026-05-11", "오세훈", 3300, 59, 957, 1419, 924, 248, 3052),
    ("2026-05-12", "오세훈", 5200, 55, 1196, 2028, 1976, 312, 4888),
]

CANDIDATE_PERIOD_SUMMARY = [
    {
        "period_key": "7d",
        "period_start": "2026-05-06",
        "period_end": "2026-05-12",
        "candidate": "정원오",
        "reaction_score": 67,
        "period_change": 125.0,
        "mention_count": 20900,
        "basis": "5/7 교통 공약, 5/12 공간대전환·지하화 공약, 3~4월 SNS/X 반응 단서 기반 근거 기반 임시 추정치",
        "confidence": "중간",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "7d",
        "period_start": "2026-05-06",
        "period_end": "2026-05-12",
        "candidate": "오세훈",
        "reaction_score": 60,
        "period_change": 147.6,
        "mention_count": 24400,
        "basis": "5/7 주거·재개발 공약, 5/10 교통 공약, 5/12 광화문 공간 논란 기반 근거 기반 임시 추정치",
        "confidence": "중간",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "14d",
        "period_start": "2026-04-29",
        "period_end": "2026-05-12",
        "candidate": "정원오",
        "reaction_score": 64,
        "period_change": 85.0,
        "mention_count": 37800,
        "basis": "최근 14일 공약 발표와 후보 공방 누적 반응 기준 근거 기반 임시 추정치",
        "confidence": "중간",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "14d",
        "period_start": "2026-04-29",
        "period_end": "2026-05-12",
        "candidate": "오세훈",
        "reaction_score": 61,
        "period_change": 96.0,
        "mention_count": 43600,
        "basis": "최근 14일 주거·교통·도시개발 쟁점 누적 반응 기준 근거 기반 임시 추정치",
        "confidence": "중간",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "30d",
        "period_start": "2026-04-13",
        "period_end": "2026-05-12",
        "candidate": "정원오",
        "reaction_score": 62,
        "period_change": 45.0,
        "mention_count": 71200,
        "basis": "한강버스, SNS 영상, 교통·공간대전환 공약 반응을 포함한 1개월 seed 추정치",
        "confidence": "중간",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "30d",
        "period_start": "2026-04-13",
        "period_end": "2026-05-12",
        "candidate": "오세훈",
        "reaction_score": 59,
        "period_change": 52.0,
        "mention_count": 78400,
        "basis": "한강·주거·교통·광화문 공간 이슈를 포함한 1개월 seed 추정치",
        "confidence": "중간",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "full",
        "period_start": "2026-01-01",
        "period_end": "2026-05-12",
        "candidate": "정원오",
        "reaction_score": 56,
        "period_change": 58.0,
        "mention_count": 112600,
        "basis": "2026-01-01부터 2026-05-12까지 장기 phaseFactor 기반 seed 추정치",
        "confidence": "낮음",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
    {
        "period_key": "full",
        "period_start": "2026-01-01",
        "period_end": "2026-05-12",
        "candidate": "오세훈",
        "reaction_score": 55,
        "period_change": 64.0,
        "mention_count": 139400,
        "basis": "2026-01-01부터 2026-05-12까지 장기 phaseFactor 기반 seed 추정치",
        "confidence": "낮음",
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    },
]

PERIOD_TOTALS = {
    ("2026-01-01", "2026-05-12"): {"정원오": 112600, "오세훈": 139400},
    ("2026-04-13", "2026-05-12"): {"정원오": 71200, "오세훈": 78400},
    ("2026-04-29", "2026-05-12"): {"정원오": 37800, "오세훈": 43600},
    ("2026-05-06", "2026-05-12"): {"정원오": 20900, "오세훈": 24400},
}

ISSUE_TARGETS_7D = {
    ("교통", "정원오"): 6200,
    ("교통", "오세훈"): 5200,
    ("한강", "정원오"): 2000,
    ("한강", "오세훈"): 4200,
    ("GTX", "정원오"): 2200,
    ("GTX", "오세훈"): 1800,
    ("도시개발", "정원오"): 4200,
    ("도시개발", "오세훈"): 5000,
    ("지하화", "정원오"): 2600,
    ("지하화", "오세훈"): 1700,
    ("재개발", "정원오"): 3500,
    ("재개발", "오세훈"): 4800,
    ("주거", "정원오"): 4700,
    ("주거", "오세훈"): 5300,
    ("청년정책", "정원오"): 2500,
    ("청년정책", "오세훈"): 2200,
}

ISSUE_BASIS = {
    "교통": ("정원오 30분 통근·동부선, 오세훈 교통 대동맥 보도 기반", "높음"),
    "한강": ("한강버스·한강 프로젝트 노출, 관련 비판·방어 반응 기반", "중간"),
    "GTX": ("GTX-D 연장, GTX-A 패스·광역철도 언급 기반", "중간"),
    "도시개발": ("공간대전환, 용산, 감사의 정원, 광화문 공간 논란 기반", "높음"),
    "지하화": ("경부선 지하화, 지하도시고속도로 기반", "중간"),
    "재개발": ("착착개발, 쾌속통합, 신통AI기획 기반", "높음"),
    "주거": ("36만호·31만호, 공급 속도전, 전월세 이슈 기반", "높음"),
    "청년정책": ("X/SNS 확산, 청년수당·청년문화 정책 노출 기반", "낮음~중간"),
}

MOOD_RANGES = {
    "교통": (0.39, 0.47, 0.14),
    "한강": (0.27, 0.39, 0.34),
    "GTX": (0.32, 0.52, 0.16),
    "도시개발": (0.30, 0.43, 0.27),
    "지하화": (0.35, 0.49, 0.16),
    "재개발": (0.31, 0.43, 0.26),
    "주거": (0.29, 0.41, 0.30),
    "청년정책": (0.39, 0.45, 0.16),
}

ISSUE_BASE_WEIGHTS = {
    "교통": 0.18,
    "주거": 0.17,
    "도시개발": 0.16,
    "재개발": 0.14,
    "한강": 0.11,
    "청년정책": 0.09,
    "지하화": 0.08,
    "GTX": 0.07,
}

EVENT_MULTIPLIERS = {
    ("2026-03-23", "정원오", "청년정책"): 2.2,
    ("2026-04-13", "정원오", "한강"): 2.5,
    ("2026-04-21", "정원오", "청년정책"): 3.4,
    ("2026-04-27", "오세훈", "도시개발"): 2.0,
    ("2026-05-07", "정원오", "교통"): 3.3,
    ("2026-05-07", "오세훈", "주거"): 3.5,
    ("2026-05-07", "오세훈", "재개발"): 3.5,
    ("2026-05-10", "오세훈", "교통"): 2.3,
    ("2026-05-12", "오세훈", "도시개발"): 3.7,
    ("2026-05-12", "정원오", "지하화"): 2.6,
    ("2026-05-12", "정원오", "도시개발"): 2.6,
}

DETAIL_OVERRIDES = {
    ("2026-05-07", "교통", "정원오", "news"): (1350, 70, 54, 1296, 520, 710, 120, "30분 통근, 동부선, 강북횡단선"),
    ("2026-05-07", "교통", "오세훈", "news"): (520, 61, 22, 498, 150, 320, 50, "교통 대동맥, GTX-A, 도시철도"),
    ("2026-05-12", "도시개발", "오세훈", "comment"): (1900, 52, 0, 1900, 300, 650, 950, "감사의 정원, 받들어총, 207억"),
    ("2026-05-12", "도시개발", "정원오", "comment"): (1200, 64, 0, 1200, 420, 560, 220, "졸속, 선거용, 광화문"),
    ("2026-05-12", "지하화", "정원오", "news"): (840, 71, 60, 780, 260, 470, 110, "경부선 지하화, 대서울 성장축"),
    ("2026-05-12", "지하화", "오세훈", "news"): (420, 59, 31, 389, 110, 250, 60, "지하도시고속도로, 강북횡단"),
}

KEYWORD_SEED = [
    ("교통", "정원오", "30분 통근", 1900, 100, 1, 4),
    ("교통", "정원오", "동부선", 1500, 92, 2, 7),
    ("교통", "정원오", "강북횡단선", 1180, 86, 3, 5),
    ("교통", "정원오", "K-패스 통합", 760, 72, 4, 2),
    ("교통", "오세훈", "교통 대동맥", 1600, 96, 1, 5),
    ("교통", "오세훈", "20조8000억", 1100, 88, 2, 99),
    ("교통", "오세훈", "GTX-A", 980, 82, 3, 4),
    ("교통", "오세훈", "도시철도", 720, 74, 4, 2),
    ("한강", "정원오", "한강버스 중단", 900, 86, 1, 3),
    ("한강", "정원오", "안전점검", 620, 74, 2, 2),
    ("한강", "오세훈", "한강버스", 1200, 90, 1, 2),
    ("한강", "오세훈", "한강 프로젝트", 880, 82, 2, 1),
    ("GTX", "정원오", "GTX-D", 820, 84, 1, 4),
    ("GTX", "정원오", "광역철도", 650, 76, 2, 2),
    ("GTX", "오세훈", "GTX-A 패스", 760, 80, 1, 6),
    ("GTX", "오세훈", "광역교통", 610, 72, 2, 2),
    ("도시개발", "정원오", "공간대전환", 1400, 96, 1, 99),
    ("도시개발", "정원오", "5도심 6광역", 1120, 90, 2, 99),
    ("도시개발", "정원오", "광화문", 920, 82, 3, 4),
    ("도시개발", "오세훈", "감사의 정원", 2100, 100, 1, 99),
    ("도시개발", "오세훈", "용산국제업무", 1050, 84, 2, 3),
    ("도시개발", "오세훈", "207억", 940, 80, 3, 99),
    ("지하화", "정원오", "경부선 지하화", 1050, 94, 1, 99),
    ("지하화", "정원오", "대서울 성장축", 760, 82, 2, 5),
    ("지하화", "오세훈", "지하도시고속도로", 720, 78, 1, 5),
    ("지하화", "오세훈", "강북횡단", 520, 70, 2, 3),
    ("재개발", "정원오", "착착개발", 1100, 91, 1, 2),
    ("재개발", "정원오", "공공재개발", 810, 78, 2, 1),
    ("재개발", "오세훈", "쾌속통합", 1420, 95, 1, 4),
    ("재개발", "오세훈", "신통AI기획", 980, 84, 2, 99),
    ("주거", "정원오", "36만호", 1300, 93, 1, 99),
    ("주거", "정원오", "전월세", 920, 80, 2, 3),
    ("주거", "오세훈", "31만호", 1850, 100, 1, 3),
    ("주거", "오세훈", "쾌속 공급", 1020, 82, 2, 2),
    ("청년정책", "정원오", "X정치", 720, 85, 1, 2),
    ("청년정책", "정원오", "원오위키", 620, 78, 2, 4),
    ("청년정책", "오세훈", "청년수당", 620, 75, 1, 1),
    ("청년정책", "오세훈", "청년문화", 520, 70, 2, 2),
]

EVIDENCE_SEED = [
    ("2026-03-23", "2026-03-23 14:34", "정원오", "청년정책", "community_x", "X 활용 기사", "우호", "X 활용 확산 단서", "X 활용 방식과 팬덤·청년층 접점이 보도됨", 900, "중간"),
    ("2026-04-21", "2026-04-21 14:41", "정원오", "청년정책", "video_post", "인스타그램 영상", "우호", "짧은 영상 반응 급증", "하루 60만 조회, 좋아요 4천 개 이상 보도", 4000, "높음"),
    ("2026-04-13", "2026-04-13 09:55", "정원오", "한강", "news", "라디오 발언 보도", "중립", "한강버스 중단 발언", "한강버스 안전·교통수단 적합성 논쟁 발생", 1100, "중간"),
    ("2026-05-07", "2026-05-07 11:36", "정원오", "교통", "news", "교통 공약 기사", "중립", "동부선·K-패스 통합", "30분 통근도시, 강북권 철도망, K-모두의 기후동행카드 보도", 3100, "높음"),
    ("2026-05-07", "2026-05-07 14:55", "오세훈", "주거", "news", "주거 공약 기사", "중립", "31만호 착공", "2031년까지 31만호, 쾌속통합, 신통AI기획 보도", 3300, "높음"),
    ("2026-05-10", "2026-05-10 10:54", "오세훈", "교통", "news", "교통 공약 기사", "중립", "교통 대동맥", "교통 대동맥, 도시철도, GTX-A 패스 보도", 2400, "중간"),
    ("2026-05-12", "2026-05-12 20:13", "오세훈", "도시개발", "comment", "광화문 공간 댓글", "비판", "감사의 정원 논란", "비용·조형물·공공공간 적합성 관련 비판 표현 증가", 3900, "중간"),
    ("2026-05-12", "2026-05-12 11:10", "정원오", "지하화", "news", "공간대전환 기사", "중립", "경부선 지하화", "5도심·6광역, GTX 연계, 경부선 지하화 보도", 2900, "높음"),
    ("2026-05-12", "2026-05-12 14:14", "오세훈", "도시개발", "news", "준공식 발언 보도", "우호", "감사의 정원 취지 설명", "자유·평화·헌신 기억 공간이라는 설명 보도", 900, "중간"),
]

REFERENCE_URLS = [
    ("선거일 및 일정 기준", "https://news.seoul.go.kr/gov/archives/577805"),
    ("정원오 X/SNS 단서", "https://ichannela.com/news/detail/000000520308.do"),
    ("정원오 교통 공약", "https://www.yna.co.kr/view/AKR20260507082200001"),
    ("오세훈 주거·재개발 공약", "https://www.mt.co.kr/politics/2026/05/07/2026050714463843034"),
    ("오세훈 교통 공약", "https://realty.chosun.com/site/data/html_dir/2026/05/12/2026051201614.html"),
    ("정원오 공간대전환·지하화 공약", "https://www.mk.co.kr/news/politics/12045066"),
    ("한강·광화문 공간 이슈", "https://www.hankyung.com/article/202601213000i"),
    ("청년정책 정책 단서", "https://youth.seoul.go.kr/infoData/plcyInfo/view.do?key=2309150002&plcyBizId=V202600005&sprtInfoId="),
]


def stable_noise(*parts: object, low: float = 0.9, high: float = 1.1) -> float:
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return low + (high - low) * value


def distribute_total(total: int, keys: list[object], weights: list[float]) -> dict[object, int]:
    weight_sum = sum(weights) or 1
    raw = [total * weight / weight_sum for weight in weights]
    values = [int(value) for value in raw]
    remainder = total - sum(values)
    order = sorted(range(len(raw)), key=lambda idx: raw[idx] - values[idx], reverse=True)
    for idx in order[:remainder]:
        values[idx] += 1
    return dict(zip(keys, values))


def split_mood(reaction_count: int, issue: str, candidate: str, date: str) -> tuple[int, int, int]:
    favorable, neutral, critical = MOOD_RANGES[issue]
    if candidate == "오세훈" and issue in {"한강", "도시개발", "주거", "재개발"}:
        favorable -= 0.03
        critical += 0.03
    if candidate == "정원오" and issue in {"교통", "지하화", "청년정책"}:
        favorable += 0.02
        neutral -= 0.01
        critical -= 0.01
    jitter = stable_noise(date, issue, candidate, "mood", low=-0.025, high=0.025)
    favorable = max(0.12, favorable + jitter)
    critical = max(0.08, critical - jitter / 2)
    neutral = max(0.18, 1 - favorable - critical)
    total = favorable + neutral + critical
    favorable_count = int(round(reaction_count * favorable / total))
    neutral_count = int(round(reaction_count * neutral / total))
    critical_count = reaction_count - favorable_count - neutral_count
    return favorable_count, neutral_count, critical_count


def split_content_comments(reaction_count: int, source: str) -> tuple[int, int]:
    ratio = SOURCES[source]["content_ratio"]
    content_count = int(round(reaction_count * ratio))
    if source == "comment":
        content_count = 0
    comment_count = max(0, reaction_count - content_count)
    return content_count, comment_count


def reaction_score(reaction_count: int, issue: str, candidate: str, source: str, date: str) -> int:
    base = 49 + min(18, reaction_count / 145)
    if source == "news":
        base += 3
    if source == "community_x":
        base += 1
    if candidate == "정원오" and issue in {"교통", "지하화", "청년정책"}:
        base += 2
    if candidate == "오세훈" and issue in {"주거", "재개발", "교통"}:
        base += 2
    if issue in {"도시개발", "한강"} and source == "comment":
        base -= 5
    base += stable_noise(date, issue, candidate, source, "score", low=-2.2, high=2.2)
    return int(round(max(35, min(84, base))))


def build_reaction_timeseries() -> pd.DataFrame:
    recent = pd.DataFrame(
        RECENT_REACTION_ROWS,
        columns=[
            "date",
            "candidate",
            "reaction_count",
            "reaction_score",
            "favorable_count",
            "neutral_count",
            "critical_count",
            "content_count",
            "comment_count",
        ],
    )
    rows: list[dict[str, object]] = recent.to_dict("records")

    ranges = [
        ("2026-01-01", "2026-04-12", {"정원오": 41400, "오세훈": 61000}, (48, 58)),
        ("2026-04-13", "2026-04-28", {"정원오": 33400, "오세훈": 34800}, (52, 64)),
        ("2026-04-29", "2026-05-05", {"정원오": 16900, "오세훈": 19200}, (55, 66)),
    ]
    for start, end, totals, score_range in ranges:
        dates = pd.date_range(start, end, freq="D")
        for candidate in CANDIDATE_ORDER:
            weights = [
                stable_noise(date.strftime("%Y-%m-%d"), candidate, "reaction", low=0.82, high=1.18)
                * (1 + idx / max(1, len(dates) - 1) * 0.16)
                for idx, date in enumerate(dates)
            ]
            distributed = distribute_total(totals[candidate], list(dates), weights)
            for idx, date in enumerate(dates):
                date_text = date.strftime("%Y-%m-%d")
                reaction_count = distributed[date]
                if candidate == "정원오":
                    favorable_ratio, neutral_ratio = 0.36, 0.45
                else:
                    favorable_ratio, neutral_ratio = 0.29, 0.43
                favorable_count = int(round(reaction_count * favorable_ratio))
                neutral_count = int(round(reaction_count * neutral_ratio))
                critical_count = reaction_count - favorable_count - neutral_count
                content_count = int(round(reaction_count * 0.072))
                comment_count = reaction_count - content_count
                score = score_range[0] + (score_range[1] - score_range[0]) * idx / max(1, len(dates) - 1)
                score += stable_noise(date_text, candidate, "daily-score", low=-2.0, high=2.0)
                rows.append(
                    {
                        "date": date_text,
                        "candidate": candidate,
                        "reaction_count": reaction_count,
                        "reaction_score": int(round(score)),
                        "favorable_count": favorable_count,
                        "neutral_count": neutral_count,
                        "critical_count": critical_count,
                        "content_count": content_count,
                        "comment_count": comment_count,
                    }
                )
    frame = pd.DataFrame(rows).sort_values(["date", "candidate"])
    return frame


def date_phase(date: pd.Timestamp) -> float:
    if date < pd.Timestamp("2026-03-01"):
        return stable_noise(date.strftime("%Y-%m-%d"), "phase-jan", low=0.35, high=0.50)
    if date < pd.Timestamp("2026-04-01"):
        return stable_noise(date.strftime("%Y-%m-%d"), "phase-mar", low=0.60, high=0.75)
    if date < pd.Timestamp("2026-05-01"):
        return stable_noise(date.strftime("%Y-%m-%d"), "phase-apr", low=0.85, high=1.05)
    return stable_noise(date.strftime("%Y-%m-%d"), "phase-may", low=1.20, high=1.55)


def build_recent_detail_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    recent_dates = list(pd.date_range(RECENT_7_START, RECENT_7_END, freq="D"))
    for issue in ISSUES:
        for candidate in CANDIDATE_ORDER:
            target = ISSUE_TARGETS_7D[(issue, candidate)]
            override_total = sum(
                value[0]
                for key, value in DETAIL_OVERRIDES.items()
                if key[1] == issue and key[2] == candidate and pd.Timestamp(key[0]) in recent_dates
            )
            cells: list[tuple[pd.Timestamp, str]] = []
            weights: list[float] = []
            for date in recent_dates:
                date_text = date.strftime("%Y-%m-%d")
                for source, percent in SOURCE_WEIGHTS[(issue, candidate)].items():
                    if (date_text, issue, candidate, source) in DETAIL_OVERRIDES:
                        continue
                    multiplier = EVENT_MULTIPLIERS.get((date_text, candidate, issue), 1.0)
                    source_weight = percent / 100
                    weights.append(source_weight * multiplier * stable_noise(date_text, issue, candidate, source))
                    cells.append((date, source))
            distributed = distribute_total(max(0, target - override_total), cells, weights)
            for date, source in cells:
                rows.append(detail_row(date, issue, candidate, source, distributed[(date, source)]))
            for key, value in DETAIL_OVERRIDES.items():
                date_text, override_issue, override_candidate, source = key
                if override_issue != issue or override_candidate != candidate:
                    continue
                date = pd.Timestamp(date_text)
                if not (RECENT_7_START <= date <= RECENT_7_END):
                    continue
                count, score, content, comments, fav, neu, crit, keywords = value
                rows.append(
                    detail_row(
                        date,
                        issue,
                        candidate,
                        source,
                        count,
                        score_override=score,
                        content_override=content,
                        comments_override=comments,
                        mood_override=(fav, neu, crit),
                        keywords_override=keywords,
                    )
                )
    return rows


def detail_row(
    date: pd.Timestamp,
    issue: str,
    candidate: str,
    source: str,
    reaction_count: int,
    score_override: int | None = None,
    content_override: int | None = None,
    comments_override: int | None = None,
    mood_override: tuple[int, int, int] | None = None,
    keywords_override: str | None = None,
) -> dict[str, object]:
    date_text = date.strftime("%Y-%m-%d")
    if mood_override:
        favorable_count, neutral_count, critical_count = mood_override
    else:
        favorable_count, neutral_count, critical_count = split_mood(reaction_count, issue, candidate, date_text)
    if content_override is None or comments_override is None:
        content_count, comment_count = split_content_comments(reaction_count, source)
    else:
        content_count, comment_count = content_override, comments_override
    score = score_override if score_override is not None else reaction_score(reaction_count, issue, candidate, source, date_text)
    top_keywords = keywords_override or ", ".join(keywords_for(issue, candidate)[:3])
    return {
        "date": date_text,
        "issue": issue,
        "candidate": candidate,
        "source": source,
        "source_label": SOURCES[source]["label"],
        "reaction_count": int(reaction_count),
        "reaction_score": int(score),
        "content_count": int(content_count),
        "comment_count": int(comment_count),
        "favorable_count": int(favorable_count),
        "neutral_count": int(neutral_count),
        "critical_count": int(critical_count),
        "favorable_ratio": round(favorable_count / reaction_count * 100, 1) if reaction_count else 0,
        "neutral_ratio": round(neutral_count / reaction_count * 100, 1) if reaction_count else 0,
        "critical_ratio": round(critical_count / reaction_count * 100, 1) if reaction_count else 0,
        "top_keywords": top_keywords,
        "basis": ISSUE_BASIS[issue][0],
        "confidence": ISSUE_BASIS[issue][1],
        "data_type": DATA_TYPE,
        "note": SEED_NOTE,
    }


def keywords_for(issue: str, candidate: str) -> list[str]:
    values = [keyword for row_issue, row_candidate, keyword, *_ in KEYWORD_SEED if row_issue == issue and row_candidate == candidate]
    return values or [issue]


def build_historical_detail_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    historical_dates = [date for date in DATES if not (RECENT_7_START <= date <= RECENT_7_END)]
    for date in historical_dates:
        date_text = date.strftime("%Y-%m-%d")
        phase = date_phase(date)
        base_volume = 11500
        for issue in ISSUES:
            for candidate in CANDIDATE_ORDER:
                candidate_modifier = 0.92 if candidate == "정원오" else 1.08
                event_multiplier = EVENT_MULTIPLIERS.get((date_text, candidate, issue), 1.0)
                issue_total = int(
                    base_volume
                    * phase
                    * candidate_modifier
                    * ISSUE_BASE_WEIGHTS[issue]
                    * event_multiplier
                    * stable_noise(date_text, issue, candidate, "issue-total")
                )
                issue_total = max(24, issue_total)
                source_weights = SOURCE_WEIGHTS[(issue, candidate)]
                cells = list(source_weights.keys())
                weights = [source_weights[source] for source in cells]
                distributed = distribute_total(issue_total, cells, weights)
                for source, count in distributed.items():
                    rows.append(detail_row(date, issue, candidate, source, max(1, count)))
    return rows


def build_issue_detail_timeseries() -> pd.DataFrame:
    frame = pd.DataFrame(build_historical_detail_rows() + build_recent_detail_rows())
    return frame.sort_values(["date", "issue", "candidate", "source"])


def build_issue_summary(detail: pd.DataFrame) -> pd.DataFrame:
    recent = detail[pd.to_datetime(detail["date"]).between(RECENT_7_START, RECENT_7_END)].copy()
    grouped = (
        recent.groupby(["issue", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
            basis=("basis", "first"),
            confidence=("confidence", "first"),
        )
        .round({"reaction_score": 1})
    )
    totals = grouped.groupby("issue")["reaction_count"].transform("sum")
    grouped["reaction_share"] = (grouped["reaction_count"] / totals * 100).round(1)
    grouped["summary_period"] = "7d"
    grouped["data_type"] = DATA_TYPE
    grouped["note"] = SEED_NOTE
    return grouped


def build_source_summary(detail: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        detail.groupby(["date", "issue", "source", "source_label", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            content_count=("content_count", "sum"),
            comment_count=("comment_count", "sum"),
            basis=("basis", "first"),
            confidence=("confidence", "first"),
        )
        .round({"reaction_score": 1})
    )
    grouped["data_type"] = DATA_TYPE
    grouped["note"] = SEED_NOTE
    return grouped


def build_keyword_summary() -> pd.DataFrame:
    rows = []
    for issue, candidate, keyword, mentions, importance, rank, rank_change in KEYWORD_SEED:
        basis, confidence = ISSUE_BASIS[issue]
        rows.append(
            {
                "issue": issue,
                "candidate": candidate,
                "keyword": keyword,
                "mention_count": mentions,
                "importance": importance,
                "rank": rank,
                "rank_change": rank_change,
                "basis": basis,
                "confidence": confidence,
                "data_type": DATA_TYPE,
                "note": SEED_NOTE,
            }
        )
    return pd.DataFrame(rows)


def build_evidence_samples(detail: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "date": date,
            "datetime": dt,
            "candidate": candidate,
            "issue": issue,
            "source": source,
            "source_label": source_label,
            "reaction_type": reaction_type,
            "title": title,
            "summary": summary,
            "count": count,
            "confidence": confidence,
            "data_type": DATA_TYPE,
            "note": SEED_NOTE,
        }
        for date, dt, candidate, issue, source, source_label, reaction_type, title, summary, count, confidence in EVIDENCE_SEED
    ]

    existing = {(row["date"], row["candidate"], row["issue"], row["source"]) for row in rows}
    latest_detail = detail[pd.to_datetime(detail["date"]).between(RECENT_7_START, RECENT_7_END)]
    for (date, issue, candidate), group in latest_detail.groupby(["date", "issue", "candidate"]):
        top = group.sort_values("reaction_count", ascending=False).iloc[0]
        key = (date, candidate, issue, top["source"])
        if key in existing:
            continue
        reaction_type = "우호" if top["favorable_count"] >= top["critical_count"] else "비판"
        if abs(int(top["favorable_count"]) - int(top["critical_count"])) < int(top["reaction_count"]) * 0.1:
            reaction_type = "중립"
        keyword_text = str(top["top_keywords"])
        rows.append(
            {
                "date": date,
                "datetime": f"{date} 10:{stable_minute(date, issue, candidate):02d}",
                "candidate": candidate,
                "issue": issue,
                "source": top["source"],
                "source_label": top["source_label"],
                "reaction_type": reaction_type,
                "title": f"{candidate} {issue} 공개 반응 샘플",
                "summary": f"{keyword_text} 키워드를 중심으로 한 공개 온라인 반응 데모용 근거 샘플입니다. 실제 원문 링크는 제공하지 않습니다.",
                "count": max(20, int(top["reaction_count"] * 0.42)),
                "confidence": top["confidence"],
                "data_type": DATA_TYPE,
                "note": SEED_NOTE,
            }
        )
    return pd.DataFrame(rows).sort_values(["datetime", "count"], ascending=[False, False])


def stable_minute(*parts: object) -> int:
    return int(stable_noise(*parts, "minute", low=0, high=58))


def build_collection_status() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "updated_at": "2026-05-13T00:00:00+09:00",
                "latest_date": "2026-05-12",
                "collection_status": COLLECTION_STATUS,
                "total_items": 45300,
                "source_scope": "공개 뉴스, 공개 영상·게시글, 공개 댓글, 공개 커뮤니티/X 검색 흔적. 비공개 계정·비공개 카페·실제 여론조사 제외",
                "period_start": "2026-05-06",
                "period_end": "2026-05-12",
                "election_date": "2026-06-03",
                "d_day": 22,
                "data_type": DATA_TYPE,
                "warning_text": SEED_NOTE,
            }
        ]
    )


def build_reference_urls() -> pd.DataFrame:
    return pd.DataFrame(
        [{"label": label, "url": url, "data_type": DATA_TYPE, "note": SEED_NOTE} for label, url in REFERENCE_URLS]
    )


def build_reaction_mood_metrics(reaction: pd.DataFrame) -> pd.DataFrame:
    frame = reaction.rename(columns={"date": "metric_date"}).copy()
    total = frame[["favorable_count", "neutral_count", "critical_count"]].sum(axis=1)
    frame["favorable_ratio"] = (frame["favorable_count"] / total * 100).round(1)
    frame["neutral_ratio"] = (frame["neutral_count"] / total * 100).round(1)
    frame["critical_ratio"] = (frame["critical_count"] / total * 100).round(1)
    frame["data_type"] = DATA_TYPE
    frame["note"] = SEED_NOTE
    return frame[
        [
            "metric_date",
            "candidate",
            "favorable_count",
            "neutral_count",
            "critical_count",
            "favorable_ratio",
            "neutral_ratio",
            "critical_ratio",
            "data_type",
            "note",
        ]
    ]


def main() -> None:
    reaction = build_reaction_timeseries()
    detail = build_issue_detail_timeseries()
    issue_summary = build_issue_summary(detail)
    source_summary = build_source_summary(detail)
    keyword_summary = build_keyword_summary()
    evidence = build_evidence_samples(detail)
    status = build_collection_status()
    candidate_period_summary = pd.DataFrame(CANDIDATE_PERIOD_SUMMARY)
    reference_urls = build_reference_urls()
    reaction_mood = build_reaction_mood_metrics(reaction)

    files = {
        "candidates.csv": pd.DataFrame(CANDIDATES),
        "candidate_channels.csv": pd.DataFrame(CHANNELS, columns=["candidate", "channel", "url"]),
        "candidate_period_summary.csv": candidate_period_summary,
        "reaction_timeseries.csv": reaction,
        "issue_summary.csv": issue_summary,
        "issue_detail_timeseries.csv": detail,
        "source_summary.csv": source_summary,
        "keyword_summary.csv": keyword_summary,
        "evidence_samples.csv": evidence,
        "collection_status.csv": status,
        "reference_urls.csv": reference_urls,
        "reaction_mood_metrics.csv": reaction_mood,
        "narrative_summary.csv": pd.DataFrame(
            [
                {
                    "period_type": "7d",
                    "headline_text": "공개 온라인 반응 기준으로 교통·주거·도시개발 쟁점이 최근 기간의 핵심 흐름을 만들었습니다.",
                    "summary_text": "선택 쟁점과 출처 필터에 따라 시계열, 반응 분위기, 근거 샘플이 함께 갱신됩니다.",
                    "reliability_text": SEED_NOTE,
                    "data_type": DATA_TYPE,
                }
            ]
        ),
    }
    for filename, frame in files.items():
        frame.to_csv(DATA_DIR / filename, index=False, encoding="utf-8-sig")

    for legacy_filename in [
        "daily_metrics.csv",
        "keyword_metrics.csv",
        "source_metrics.csv",
        "evidence_items.csv",
        "senti" + "ment_metrics.csv",
    ]:
        legacy_path = DATA_DIR / legacy_filename
        if legacy_path.exists():
            legacy_path.unlink()

    print(f"Generated {len(files)} primary mock CSV files in {DATA_DIR}")
    print(f"Period: {DATES.min().date()} ~ {DATES.max().date()}")
    print(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
