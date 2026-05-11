from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "mock"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(20260511)
DATES = pd.date_range("2026-04-12", "2026-05-11", freq="D")

CANDIDATES = [
    {
        "candidate_code": "JWO",
        "candidate_name": "정원오",
        "party": "더불어민주당",
        "role": "서울시장 후보",
        "profile_summary": "생활권 단위 도시정책과 주거 안정 의제를 강조하는 후보",
        "career": "현) 성동구청장 | 전) 성동구 부구청장 | 전) 서울시 정책기획관 | 전) 행정안전부 지역금융과장",
        "education": "연세대학교 행정학 석사 | 서울대학교 행정학 학사",
        "official_channels": "공식 홈페이지|페이스북|유튜브|인스타그램",
    },
    {
        "candidate_code": "OSH",
        "candidate_name": "오세훈",
        "party": "국민의힘",
        "role": "서울시장 후보",
        "profile_summary": "교통 인프라와 도시 경쟁력 의제를 중심으로 반응이 형성되는 후보",
        "career": "현) 서울특별시장 | 전) 제38대 서울특별시장 | 전) 국회의원 | 전) 한나라당 최고위원",
        "education": "고려대학교 법학 석사 | 고려대학교 법학 학사",
        "official_channels": "공식 홈페이지|페이스북|유튜브|인스타그램",
    },
]

KEYWORDS = {
    "JWO": [
        ("재개발", "persistent", "재개발", 1.00),
        ("주거", "persistent", "주거", 0.83),
        ("청년정책", "persistent", "청년정책", 0.74),
        ("모아타운", "rising", "재개발", 0.58),
        ("공공재개발", "new", "재개발", 0.50),
        ("노후", "persistent", "주거", 0.42),
        ("주택공급", "persistent", "주거", 0.40),
        ("지역균형", "persistent", "도시개발", 0.35),
        ("생활SOC", "rising", "청년정책", 0.33),
        ("일자리", "persistent", "청년정책", 0.30),
        ("도시정비", "persistent", "재개발", 0.28),
        ("청년주택", "new", "청년정책", 0.26),
        ("교육", "persistent", "청년정책", 0.22),
        ("골목상권", "rising", "민생", 0.20),
        ("교통체증", "persistent", "교통", 0.24),
        ("공공교통", "new", "교통", 0.18),
        ("한강공원", "persistent", "한강", 0.17),
        ("안전보행", "persistent", "안전", 0.16),
    ],
    "OSH": [
        ("교통", "persistent", "교통", 1.00),
        ("한강", "persistent", "한강", 0.88),
        ("도시개발", "persistent", "도시개발", 0.70),
        ("GTX", "rising", "교통", 0.62),
        ("한강버스", "rising", "한강", 0.55),
        ("지하화", "new", "교통", 0.50),
        ("수상서울", "new", "한강", 0.43),
        ("스마트교통", "new", "교통", 0.39),
        ("엄마아빠택시", "persistent", "민생", 0.34),
        ("대심도터널", "rising", "교통", 0.32),
        ("규제완화", "persistent", "도시개발", 0.30),
        ("민생", "persistent", "민생", 0.27),
        ("안심주택", "rising", "주거", 0.23),
        ("관광", "persistent", "한강", 0.20),
        ("재건축", "persistent", "재개발", 0.31),
        ("주택공급", "persistent", "주거", 0.26),
        ("청년교통", "new", "청년정책", 0.18),
        ("청년주택", "persistent", "청년정책", 0.14),
        ("안전서울", "persistent", "안전", 0.18),
    ],
}

SOURCE_LABELS = {
    "news": "뉴스 기사",
    "video_post": "영상·게시글",
    "comment": "댓글",
}

SOURCE_DETAIL_SPLITS = {
    "news": [
        ("naver_news", "네이버뉴스", 0.56),
        ("daum_news", "다음뉴스", 0.44),
    ],
    "video_post": [
        ("youtube", "유튜브", 0.62),
        ("blog_cafe", "블로그·카페", 0.24),
        ("community", "커뮤니티", 0.14),
    ],
    "comment": [
        ("news_comment", "뉴스 댓글", 0.43),
        ("youtube_comment", "유튜브 댓글", 0.37),
        ("community_comment", "커뮤니티 댓글", 0.20),
    ],
}


def clamp(value: float, low: float, high: float) -> float:
    return float(max(low, min(high, value)))


def day_spike(date: pd.Timestamp, candidate_code: str) -> float:
    if date == pd.Timestamp("2026-05-10") and candidate_code == "OSH":
        return 1.55
    if date == pd.Timestamp("2026-05-10") and candidate_code == "JWO":
        return 1.38
    if date == pd.Timestamp("2026-05-11") and candidate_code == "OSH":
        return 1.20
    if date == pd.Timestamp("2026-05-11") and candidate_code == "JWO":
        return 1.12
    if date == pd.Timestamp("2026-05-08") and candidate_code == "JWO":
        return 1.24
    if date == pd.Timestamp("2026-05-06") and candidate_code == "OSH":
        return 1.18
    return 1.0


def build_daily_metrics() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for candidate_code in ["JWO", "OSH"]:
        previous_reactions = None
        for idx, date in enumerate(DATES):
            trend = idx / (len(DATES) - 1)
            weekly_wave = 1 + 0.08 * np.sin(idx / 2.5)
            noise = RNG.normal(1, 0.06)
            spike = day_spike(date, candidate_code)

            if candidate_code == "JWO":
                base_mentions = 8600 + 1800 * trend
                base_comments = 5600 + 1300 * trend
                base_content = 540 + 110 * trend
            else:
                base_mentions = 9900 + 2100 * trend
                base_comments = 6500 + 1500 * trend
                base_content = 650 + 130 * trend

            mention_count = int(base_mentions * weekly_wave * noise * spike)
            comment_count = int(base_comments * (0.95 + RNG.normal(0, 0.05)) * spike)
            content_count = int(base_content * (0.94 + RNG.normal(0, 0.07)) * spike)
            total_reactions = int(mention_count + comment_count * 1.45 + content_count * 12)

            if previous_reactions:
                growth_rate = round((total_reactions - previous_reactions) / previous_reactions * 100, 1)
            else:
                growth_rate = round(RNG.normal(4, 1), 1)

            rows.append(
                {
                    "metric_date": date.strftime("%Y-%m-%d"),
                    "candidate_code": candidate_code,
                    "total_reactions": total_reactions,
                    "mention_count": mention_count,
                    "content_count": content_count,
                    "comment_count": comment_count,
                    "reaction_score": 0.0,
                    "growth_rate": growth_rate,
                }
            )
            previous_reactions = total_reactions

    df = pd.DataFrame(rows)
    for col in ["mention_count", "comment_count", "content_count", "growth_rate"]:
        min_value = df[col].min()
        max_value = df[col].max()
        df[f"norm_{col}"] = (df[col] - min_value) / (max_value - min_value)

    raw_score = (
        df["norm_mention_count"] * 35
        + df["norm_comment_count"] * 35
        + df["norm_content_count"] * 20
        + df["norm_growth_rate"] * 10
    )
    df["reaction_score"] = (52 + raw_score * 0.45).clip(0, 100).round(1)
    return df[
        [
            "metric_date",
            "candidate_code",
            "total_reactions",
            "mention_count",
            "content_count",
            "comment_count",
            "reaction_score",
            "growth_rate",
        ]
    ]


def build_source_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in daily.iterrows():
        code = row["candidate_code"]
        is_osh = code == "OSH"
        shares = {
            "news": 0.24 if is_osh else 0.23,
            "video_post": 0.53 if is_osh else 0.52,
            "comment": 0.23 if is_osh else 0.25,
        }
        for source, share in shares.items():
            source_reaction_count = int(row["total_reactions"] * share * RNG.normal(1, 0.035))
            if source == "news":
                source_content_count = int(row["content_count"] * 0.28 * RNG.normal(1, 0.06))
                source_comment_count = int(row["comment_count"] * 0.18 * RNG.normal(1, 0.05))
            elif source == "video_post":
                source_content_count = int(row["content_count"] * 0.62 * RNG.normal(1, 0.06))
                source_comment_count = int(row["comment_count"] * 0.60 * RNG.normal(1, 0.05))
            else:
                source_content_count = 0
                source_comment_count = int(row["comment_count"] * 0.42 * RNG.normal(1, 0.05))

            for detail_key, detail_label, detail_share in SOURCE_DETAIL_SPLITS[source]:
                detail_reaction_count = int(source_reaction_count * detail_share * RNG.normal(1, 0.03))
                detail_content_count = int(source_content_count * detail_share * RNG.normal(1, 0.04))
                detail_comment_count = int(source_comment_count * detail_share * RNG.normal(1, 0.04))
                rows.append(
                    {
                        "metric_date": row["metric_date"],
                        "candidate_code": code,
                        "source": source,
                        "source_detail": detail_key,
                        "source_detail_label": detail_label,
                        "content_count": max(0, detail_content_count),
                        "comment_count": max(0, detail_comment_count),
                        "reaction_count": max(0, detail_reaction_count),
                    }
                )
    return pd.DataFrame(rows)


def build_keyword_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, daily_row in daily.iterrows():
        date = pd.Timestamp(daily_row["metric_date"])
        code = daily_row["candidate_code"]
        total_mentions = daily_row["mention_count"]
        spike = day_spike(date, code)

        keyword_counts = []
        for keyword, keyword_type, issue_category, weight in KEYWORDS[code]:
            issue_boost = 1.0
            if date >= pd.Timestamp("2026-05-08") and keyword in {"모아타운", "공공재개발", "청년주택"}:
                issue_boost += 0.38
            if date >= pd.Timestamp("2026-05-09") and keyword in {"교통", "GTX", "한강버스", "지하화", "수상서울"}:
                issue_boost += 0.42
            count = int(total_mentions * weight * 0.28 * issue_boost * spike * RNG.normal(1, 0.08))
            keyword_counts.append((keyword, keyword_type, issue_category, max(80, count)))

        keyword_counts.sort(key=lambda item: item[3], reverse=True)
        for rank, (keyword, keyword_type, issue_category, count) in enumerate(keyword_counts, start=1):
            rank_change = int(RNG.choice([-8, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 7, 8]))
            if keyword_type == "rising":
                rank_change = abs(rank_change) or 3
            rows.append(
                {
                    "metric_date": date.strftime("%Y-%m-%d"),
                    "candidate_code": code,
                    "keyword": keyword,
                    "keyword_type": keyword_type,
                    "mention_count": count,
                    "rank": rank,
                    "rank_change": rank_change,
                    "issue_category": issue_category,
                }
            )
    return pd.DataFrame(rows)


def build_sentiment_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in daily.iterrows():
        date = pd.Timestamp(row["metric_date"])
        code = row["candidate_code"]
        total = max(1, int(row["comment_count"] + row["mention_count"] * 0.28))

        if code == "JWO":
            positive_ratio = clamp(0.43 + RNG.normal(0, 0.025), 0.34, 0.52)
            neutral_ratio = clamp(0.37 + RNG.normal(0, 0.020), 0.30, 0.44)
        else:
            positive_ratio = clamp(0.40 + RNG.normal(0, 0.025), 0.32, 0.50)
            neutral_ratio = clamp(0.36 + RNG.normal(0, 0.020), 0.30, 0.44)

        if date == pd.Timestamp("2026-05-10"):
            if code == "OSH":
                positive_ratio -= 0.03
                neutral_ratio -= 0.02
            else:
                positive_ratio += 0.02

        negative_ratio = clamp(1 - positive_ratio - neutral_ratio, 0.12, 0.34)
        total_ratio = positive_ratio + neutral_ratio + negative_ratio
        positive_ratio /= total_ratio
        neutral_ratio /= total_ratio
        negative_ratio /= total_ratio

        positive_count = int(total * positive_ratio)
        neutral_count = int(total * neutral_ratio)
        negative_count = max(0, total - positive_count - neutral_count)

        rows.append(
            {
                "metric_date": row["metric_date"],
                "candidate_code": code,
                "positive_count": positive_count,
                "neutral_count": neutral_count,
                "negative_count": negative_count,
                "positive_ratio": round(positive_count / total * 100, 1),
                "neutral_ratio": round(neutral_count / total * 100, 1),
                "negative_ratio": round(negative_count / total * 100, 1),
            }
        )
    return pd.DataFrame(rows)


def build_evidence_items() -> pd.DataFrame:
    templates = [
        ("JWO", "news", "재개발", "정원오 “재개발 공공성 강화, 이익 환수로 주거 복지 확대”", "재개발·재건축 과정의 공공성 확보와 청년 주거 지원 확대를 언급한 기사 예시입니다."),
        ("JWO", "news", "청년정책", "정원오 “청년주거 10만 호 공급, 월세 부담 낮추겠다”", "청년 맞춤형 공공임대 확대와 생활권 일자리 지원을 다룬 기사 예시입니다."),
        ("JWO", "video_post", "주거", "모아타운 활성화 방안 발표 영상", "노후 주거지 정비와 생활SOC 확충 계획을 설명한 영상 게시글 예시입니다."),
        ("JWO", "comment", "청년정책", "청년 주거 정책 댓글 샘플", "“월세 부담은 줄었으면 좋겠지만 실제 공급 속도는 더 지켜봐야...”처럼 개인정보와 과격 표현을 마스킹한 댓글 예시입니다."),
        ("OSH", "news", "교통", "오세훈 “GTX D·E 노선 조기 착공 추진, 교통지옥 해소”", "광역 교통망 확충과 도시 교통 수요 관리 방안을 다룬 기사 예시입니다."),
        ("OSH", "news", "한강", "오세훈, 한강 르네상스 2.0 발표", "수변 문화·관광 확대와 한강 접근성 개선을 설명한 기사 예시입니다."),
        ("OSH", "video_post", "교통", "지하철 연장·버스 노선 조정 공약 소개 영상", "교통 혼잡 완화와 출퇴근 시간 단축을 내세운 영상 게시글 예시입니다."),
        ("OSH", "comment", "교통", "교통 공약 댓글 샘플", "“출퇴근이 빨라진다면 좋지만 공사 기간 불편도 걱정...”처럼 일부 표현을 마스킹한 댓글 예시입니다."),
    ]
    outlets = ["연합뉴스", "한겨레", "KBS 뉴스", "SBS 뉴스", "경향신문", "조선일보", "서울경제", "커뮤니티 게시글"]

    rows: list[dict[str, object]] = []
    for i in range(60):
        code, source, issue, title, summary = templates[i % len(templates)]
        date = DATES[-1 - (i % 18)]
        reaction_count = int(RNG.integers(360, 3600) * (1.25 if code == "OSH" else 1.0))
        if source == "comment":
            evidence_type = "댓글 샘플"
            outlet = "공개 댓글"
        elif source == "video_post":
            evidence_type = "영상·게시글"
            outlet = "YouTube·블로그"
        else:
            evidence_type = "뉴스"
            outlet = outlets[i % (len(outlets) - 1)]

        rows.append(
            {
                "published_date": date.strftime("%Y-%m-%d"),
                "candidate_code": code,
                "source": source,
                "issue_category": issue,
                "title": title,
                "summary": summary,
                "reaction_count": reaction_count,
                "url": "#",
                "evidence_type": evidence_type,
                "outlet": outlet,
            }
        )
    return pd.DataFrame(rows).sort_values(["published_date", "reaction_count"], ascending=[False, False])


def build_narrative_summary() -> pd.DataFrame:
    rows = [
        {
            "period_type": "7d",
            "headline_text": "최근 7일 공개 온라인 반응에서는 오세훈 후보 관련 반응이 소폭 높게 관측됩니다.",
            "summary_text": "정원오는 재개발·청년정책 이슈에서, 오세훈은 교통·한강 이슈에서 반응이 집중되었습니다.",
            "competition_text": "두 후보 모두 특정 정책 발표일 이후 댓글과 영상·게시글 반응이 함께 증가했습니다.",
            "issue_text": "핵심 쟁점은 교통, 한강, 재개발, 청년정책입니다.",
            "reliability_text": "본 문장은 데모 데이터 기반 자동 요약 예시이며 실제 지지율이나 선거 결과 예측이 아닙니다.",
        },
        {
            "period_type": "14d",
            "headline_text": "최근 14일 기준으로는 교통과 주거 의제가 번갈아 반응을 만들었습니다.",
            "summary_text": "정원오는 주거 안정·도시정비 언급이 꾸준했고, 오세훈은 교통망과 한강 정책 언급이 늘었습니다.",
            "competition_text": "영상·게시글 출처에서 오세훈, 댓글 반응에서는 양 후보 모두 쟁점별 증가가 관측됩니다.",
            "issue_text": "재개발과 교통 의제가 전체 반응의 큰 비중을 차지합니다.",
            "reliability_text": "공개 온라인 반응 기반 예시이며 여론조사·투표 예측이 아닙니다.",
        },
        {
            "period_type": "30d",
            "headline_text": "최근 1개월 기준으로 두 후보의 온라인 반응은 주요 정책 이벤트에 따라 변동했습니다.",
            "summary_text": "정원오는 생활권 정책 키워드가 지속되고, 오세훈은 대형 인프라 키워드가 강하게 관측됩니다.",
            "competition_text": "온라인 반응량은 출처의 수집 가능성과 게시물 확산 방식에 영향을 받습니다.",
            "issue_text": "장기 흐름에서는 교통, 한강, 재개발, 주거, 청년정책이 반복적으로 등장합니다.",
            "reliability_text": "표시된 수치는 실제 지지율, 득표율, 선거 결과 예측을 의미하지 않습니다.",
        },
    ]
    return pd.DataFrame(rows)


def build_collection_status() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "updated_at": "2026-05-11 10:30",
                "period_type": "7d",
                "collection_status": "정상 수집 중",
                "total_items": 198335,
                "warning_text": "본 서비스는 실제 지지율·득표율이 아닌 공개 온라인 반응 비교 데모입니다.",
            },
            {
                "updated_at": "2026-05-11 10:30",
                "period_type": "14d",
                "collection_status": "정상 수집 중",
                "total_items": 382912,
                "warning_text": "수집 범위와 알고리즘에 따라 수치가 달라질 수 있습니다.",
            },
            {
                "updated_at": "2026-05-11 10:30",
                "period_type": "30d",
                "collection_status": "정상 수집 중",
                "total_items": 781204,
                "warning_text": "이 데이터는 여론조사나 투표 예측이 아닙니다.",
            },
        ]
    )


def main() -> None:
    candidates = pd.DataFrame(CANDIDATES)
    daily = build_daily_metrics()
    source = build_source_metrics(daily)
    keywords = build_keyword_metrics(daily)
    sentiment = build_sentiment_metrics(daily)
    evidence = build_evidence_items()
    narrative = build_narrative_summary()
    status = build_collection_status()

    files = {
        "candidates.csv": candidates,
        "daily_metrics.csv": daily,
        "source_metrics.csv": source,
        "keyword_metrics.csv": keywords,
        "sentiment_metrics.csv": sentiment,
        "evidence_items.csv": evidence,
        "narrative_summary.csv": narrative,
        "collection_status.csv": status,
    }
    for filename, frame in files.items():
        frame.to_csv(DATA_DIR / filename, index=False, encoding="utf-8-sig")

    print(f"Generated {len(files)} mock CSV files in {DATA_DIR}")
    print(f"Period: {DATES.min().date()} ~ {DATES.max().date()}")
    print(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
