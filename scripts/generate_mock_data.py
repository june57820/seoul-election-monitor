from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "mock"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(20260512)
DATES = pd.date_range("2026-01-01", "2026-05-12", freq="D")

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

ISSUES = [
    "교통",
    "한강",
    "GTX",
    "도시개발",
    "지하화",
    "재개발",
    "주거",
    "청년정책",
]

SOURCES = {
    "news": {"label": "뉴스", "content_base": 0.18, "comment_base": 0.16},
    "video_post": {"label": "영상·게시글", "content_base": 0.50, "comment_base": 0.42},
    "comment": {"label": "댓글", "content_base": 0.00, "comment_base": 0.34},
    "community_x": {"label": "커뮤니티/X", "content_base": 0.32, "comment_base": 0.08},
}

ISSUE_KEYWORDS = {
    "교통": {
        "정원오": ["버스", "교통약자", "대중교통", "혼잡", "환승"],
        "오세훈": ["도로확장", "교통혼잡", "지하화", "서울역", "주차"],
    },
    "한강": {
        "정원오": ["한강 접근성", "수변공원", "생활체육", "환경", "보행"],
        "오세훈": ["한강버스", "수상교통", "관광", "수변문화", "한강르네상스"],
    },
    "GTX": {
        "정원오": ["환승거점", "교통복지", "통근시간", "역세권", "접근성"],
        "오세훈": ["GTX", "광역교통", "노선확장", "출퇴근", "대심도"],
    },
    "도시개발": {
        "정원오": ["지역균형", "생활SOC", "도시정비", "공공성", "골목상권"],
        "오세훈": ["도시개발", "규제완화", "랜드마크", "도시경쟁력", "복합개발"],
    },
    "지하화": {
        "정원오": ["지상공간", "보행환경", "녹지축", "생활권", "소음저감"],
        "오세훈": ["철도지하화", "도로지하화", "상부공간", "교통체증", "개발효과"],
    },
    "재개발": {
        "정원오": ["재개발", "공공재개발", "모아타운", "노후주거", "주거복지"],
        "오세훈": ["재건축", "신속통합", "정비사업", "주택공급", "규제완화"],
    },
    "주거": {
        "정원오": ["공공임대", "청년주택", "월세부담", "주거안정", "돌봄주거"],
        "오세훈": ["안심주택", "주택공급", "민간임대", "역세권", "주거선택"],
    },
    "청년정책": {
        "정원오": ["청년정책", "청년일자리", "창업지원", "월세지원", "교육"],
        "오세훈": ["청년교통", "창업", "청년공간", "취업지원", "미래산업"],
    },
}

ISSUE_WEIGHTS = {
    "정원오": {
        "교통": 0.92,
        "한강": 0.74,
        "GTX": 0.66,
        "도시개발": 0.83,
        "지하화": 0.70,
        "재개발": 1.18,
        "주거": 1.22,
        "청년정책": 1.16,
    },
    "오세훈": {
        "교통": 1.30,
        "한강": 1.20,
        "GTX": 1.14,
        "도시개발": 1.10,
        "지하화": 1.06,
        "재개발": 0.88,
        "주거": 0.82,
        "청년정책": 0.72,
    },
}

ISSUE_BASE = {
    "교통": 4400,
    "한강": 3600,
    "GTX": 2900,
    "도시개발": 3000,
    "지하화": 2400,
    "재개발": 3300,
    "주거": 3100,
    "청년정책": 2500,
}


def clamp(value: float, low: float, high: float) -> float:
    return float(max(low, min(high, value)))


def issue_event_multiplier(date: pd.Timestamp, issue: str, candidate: str) -> float:
    if date == pd.Timestamp("2026-05-10") and issue in {"교통", "GTX", "지하화"}:
        return 1.86 if candidate == "오세훈" else 1.52
    if date == pd.Timestamp("2026-05-09") and issue in {"한강", "도시개발"}:
        return 1.42 if candidate == "오세훈" else 1.18
    if date == pd.Timestamp("2026-05-08") and issue in {"재개발", "주거", "청년정책"}:
        return 1.48 if candidate == "정원오" else 1.14
    if date == pd.Timestamp("2026-05-06") and issue == "한강":
        return 1.28 if candidate == "오세훈" else 1.08
    return 1.0


def source_multiplier(source: str, candidate: str, issue: str) -> float:
    base = {
        "news": 0.25,
        "video_post": 0.36,
        "comment": 0.24,
        "community_x": 0.15,
    }[source]
    if source == "video_post" and candidate == "오세훈" and issue in {"교통", "한강", "GTX"}:
        base += 0.03
    if source == "comment" and candidate == "정원오" and issue in {"주거", "청년정책", "재개발"}:
        base += 0.025
    return base


def build_issue_detail_timeseries() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for date_idx, date in enumerate(DATES):
        trend = 1 + date_idx / (len(DATES) - 1) * 0.18
        weekly_wave = 1 + 0.08 * np.sin(date_idx / 2.4)
        for issue in ISSUES:
            for candidate in ["정원오", "오세훈"]:
                issue_total_base = (
                    ISSUE_BASE[issue]
                    * ISSUE_WEIGHTS[candidate][issue]
                    * trend
                    * weekly_wave
                    * issue_event_multiplier(date, issue, candidate)
                    * RNG.normal(1, 0.055)
                )
                for source in SOURCES:
                    reaction_count = int(issue_total_base * source_multiplier(source, candidate, issue) * RNG.normal(1, 0.045))
                    reaction_count = max(120, reaction_count)
                    reaction_score = clamp(47 + reaction_count / 310 + RNG.normal(0, 1.6), 35, 95)

                    if candidate == "정원오":
                        favorable_ratio = clamp(0.42 + RNG.normal(0, 0.025), 0.32, 0.55)
                        neutral_ratio = clamp(0.36 + RNG.normal(0, 0.020), 0.28, 0.46)
                    else:
                        favorable_ratio = clamp(0.39 + RNG.normal(0, 0.026), 0.30, 0.53)
                        neutral_ratio = clamp(0.35 + RNG.normal(0, 0.022), 0.27, 0.45)

                    if date == pd.Timestamp("2026-05-10") and issue == "교통":
                        if candidate == "오세훈":
                            favorable_ratio -= 0.02
                            neutral_ratio -= 0.015
                        else:
                            favorable_ratio += 0.015

                    critical_ratio = clamp(1 - favorable_ratio - neutral_ratio, 0.12, 0.36)
                    total_ratio = favorable_ratio + neutral_ratio + critical_ratio
                    favorable_ratio /= total_ratio
                    neutral_ratio /= total_ratio
                    critical_ratio /= total_ratio

                    favorable_count = int(reaction_count * favorable_ratio)
                    neutral_count = int(reaction_count * neutral_ratio)
                    critical_count = max(0, reaction_count - favorable_count - neutral_count)
                    content_count = 0 if source == "comment" else max(1, int(reaction_count * SOURCES[source]["content_base"] / 18))
                    comment_count = max(1, int(reaction_count * SOURCES[source]["comment_base"] / 4.2))
                    rows.append(
                        {
                            "date": date.strftime("%Y-%m-%d"),
                            "issue": issue,
                            "candidate": candidate,
                            "source": source,
                            "source_label": SOURCES[source]["label"],
                            "reaction_count": reaction_count,
                            "reaction_score": round(reaction_score, 1),
                            "content_count": content_count,
                            "comment_count": comment_count,
                            "favorable_count": favorable_count,
                            "neutral_count": neutral_count,
                            "critical_count": critical_count,
                            "favorable_ratio": round(favorable_count / reaction_count * 100, 1),
                            "neutral_ratio": round(neutral_count / reaction_count * 100, 1),
                            "critical_ratio": round(critical_count / reaction_count * 100, 1),
                            "top_keywords": ", ".join(ISSUE_KEYWORDS[issue][candidate][:3]),
                        }
                    )
    return pd.DataFrame(rows)


def build_reaction_timeseries(detail: pd.DataFrame) -> pd.DataFrame:
    daily = (
        detail.groupby(["date", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
            content_count=("content_count", "sum"),
            comment_count=("comment_count", "sum"),
        )
        .round({"reaction_score": 1})
    )
    daily["reaction_score"] = daily["reaction_score"].clip(0, 100)
    return daily


def build_issue_summary(detail: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        detail.groupby(["issue", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
        )
        .round({"reaction_score": 1})
    )
    totals = grouped.groupby("issue")["reaction_count"].transform("sum")
    grouped["reaction_share"] = (grouped["reaction_count"] / totals * 100).round(1)
    grouped["summary_period"] = "30d"
    return grouped


def build_source_summary(detail: pd.DataFrame) -> pd.DataFrame:
    return (
        detail.groupby(["date", "issue", "source", "source_label", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            content_count=("content_count", "sum"),
            comment_count=("comment_count", "sum"),
        )
        .round({"reaction_score": 1})
    )


def build_keyword_summary(detail: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for issue in ISSUES:
        for candidate in ["정원오", "오세훈"]:
            issue_data = detail[(detail["issue"].eq(issue)) & (detail["candidate"].eq(candidate))]
            total = int(issue_data["reaction_count"].sum())
            for rank, keyword in enumerate(ISSUE_KEYWORDS[issue][candidate], start=1):
                weight = 1.0 - (rank - 1) * 0.135
                mention_count = max(80, int(total * 0.045 * weight * RNG.normal(1, 0.04)))
                rank_change = int(RNG.choice([-7, -5, -3, -2, -1, 0, 2, 3, 4, 6, 8]))
                if rank <= 2 and issue in {"교통", "재개발", "주거"}:
                    rank_change = abs(rank_change) or 3
                rows.append(
                    {
                        "issue": issue,
                        "candidate": candidate,
                        "keyword": keyword,
                        "mention_count": mention_count,
                        "importance": round(weight, 2),
                        "rank": rank,
                        "rank_change": rank_change,
                    }
                )
    return pd.DataFrame(rows)


def build_evidence_samples(detail: pd.DataFrame) -> pd.DataFrame:
    reaction_map = [
        ("우호", "정책 방향을 우호적으로 평가하는 공개 반응이 관측되었습니다."),
        ("중립", "정책 내용과 실행 조건을 비교하는 설명형 반응이 관측되었습니다."),
        ("비판", "예산 부담과 추진 가능성을 우려하는 공개 반응이 관측되었습니다."),
    ]
    source_titles = {
        "news": "정책 발표 기사",
        "video_post": "해설 영상·게시글",
        "comment": "공개 댓글 샘플",
        "community_x": "커뮤니티/X 게시글",
    }
    rows: list[dict[str, object]] = []
    top_dates = pd.to_datetime(detail["date"]).drop_duplicates().sort_values(ascending=False).tolist()
    for issue in ISSUES:
        for candidate in ["정원오", "오세훈"]:
            keywords = ISSUE_KEYWORDS[issue][candidate]
            for idx, date in enumerate(top_dates):
                for source_idx, source in enumerate(SOURCES):
                    reaction_type, reaction_sentence = reaction_map[(idx + source_idx + (0 if candidate == "정원오" else 1)) % 3]
                    hour = 9 + ((idx + source_idx * 2) % 10)
                    minute = int(RNG.integers(0, 59))
                    dt = datetime.combine(pd.Timestamp(date).date(), datetime.min.time()) + timedelta(hours=hour, minutes=minute)
                    base_count = detail[
                        detail["date"].eq(pd.Timestamp(date).strftime("%Y-%m-%d"))
                        & detail["issue"].eq(issue)
                        & detail["candidate"].eq(candidate)
                        & detail["source"].eq(source)
                    ]["reaction_count"].sum()
                    title = f"{candidate} {issue} 관련 {source_titles[source]}"
                    summary = (
                        f"{', '.join(keywords[:3])} 키워드를 중심으로 한 데모 근거 샘플입니다. "
                        f"{reaction_sentence} 실제 원문 링크는 제공하지 않습니다."
                    )
                    rows.append(
                        {
                            "date": pd.Timestamp(date).strftime("%Y-%m-%d"),
                            "datetime": dt.strftime("%Y-%m-%d %H:%M"),
                            "candidate": candidate,
                            "issue": issue,
                            "source": source,
                            "source_label": SOURCES[source]["label"],
                            "reaction_type": reaction_type,
                            "title": title,
                            "summary": summary,
                            "count": max(12, int(base_count * RNG.uniform(0.04, 0.17))),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["datetime", "count"], ascending=[False, False])


def build_collection_status(detail: pd.DataFrame) -> pd.DataFrame:
    latest = pd.to_datetime(detail["date"]).max()
    return pd.DataFrame(
        [
            {
                "updated_at": "2026-05-12 10:00",
                "latest_date": latest.strftime("%Y-%m-%d"),
                "collection_status": "정상 수집 중",
                "total_items": int(detail["reaction_count"].sum()),
                "source_scope": "뉴스, 영상·게시글, 댓글, 커뮤니티/X",
                "warning_text": "본 대시보드는 공개 온라인 반응을 수집·분석한 데모 화면이며, 실제 지지율·득표율·선거 결과 예측이 아닙니다.",
            }
        ]
    )


def write_legacy_alias_files(detail: pd.DataFrame, reaction: pd.DataFrame, keywords: pd.DataFrame, evidence: pd.DataFrame) -> None:
    candidate_code = {"정원오": "JWO", "오세훈": "OSH"}
    daily = reaction.rename(columns={"date": "metric_date", "candidate": "candidate_code"}).copy()
    daily["candidate_code"] = daily["candidate_code"].map(candidate_code)
    daily["total_reactions"] = daily["reaction_count"]
    daily["mention_count"] = (daily["reaction_count"] * 0.58).astype(int)
    daily["growth_rate"] = daily.groupby("candidate_code")["total_reactions"].pct_change().fillna(0).mul(100).round(1)
    daily[
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
    ].to_csv(DATA_DIR / "daily_metrics.csv", index=False, encoding="utf-8-sig")

    legacy_keywords = keywords.rename(
        columns={"candidate": "candidate_code", "issue": "issue_category"}
    ).copy()
    legacy_keywords["candidate_code"] = legacy_keywords["candidate_code"].map(candidate_code)
    legacy_keywords["metric_date"] = "2026-05-12"
    legacy_keywords["keyword_type"] = np.where(legacy_keywords["rank_change"] > 0, "rising", "persistent")
    legacy_keywords[
        [
            "metric_date",
            "candidate_code",
            "keyword",
            "keyword_type",
            "mention_count",
            "rank",
            "rank_change",
            "issue_category",
        ]
    ].to_csv(DATA_DIR / "keyword_metrics.csv", index=False, encoding="utf-8-sig")

    legacy_source = detail.rename(columns={"date": "metric_date", "candidate": "candidate_code"}).copy()
    legacy_source["candidate_code"] = legacy_source["candidate_code"].map(candidate_code)
    legacy_source["source_detail"] = legacy_source["source"]
    legacy_source["reaction_count"] = legacy_source["reaction_count"]
    legacy_source[
        [
            "metric_date",
            "candidate_code",
            "source",
            "source_detail",
            "source_label",
            "content_count",
            "comment_count",
            "reaction_count",
        ]
    ].to_csv(DATA_DIR / "source_metrics.csv", index=False, encoding="utf-8-sig")

    legacy_sentiment = reaction.rename(columns={"date": "metric_date", "candidate": "candidate_code"}).copy()
    legacy_sentiment["candidate_code"] = legacy_sentiment["candidate_code"].map(candidate_code)
    legacy_sentiment = legacy_sentiment.rename(
        columns={
            "favorable_count": "positive_count",
            "critical_count": "negative_count",
        }
    )
    total = legacy_sentiment[["positive_count", "neutral_count", "negative_count"]].sum(axis=1)
    legacy_sentiment["positive_ratio"] = (legacy_sentiment["positive_count"] / total * 100).round(1)
    legacy_sentiment["neutral_ratio"] = (legacy_sentiment["neutral_count"] / total * 100).round(1)
    legacy_sentiment["negative_ratio"] = (legacy_sentiment["negative_count"] / total * 100).round(1)
    legacy_sentiment[
        [
            "metric_date",
            "candidate_code",
            "positive_count",
            "neutral_count",
            "negative_count",
            "positive_ratio",
            "neutral_ratio",
            "negative_ratio",
        ]
    ].to_csv(DATA_DIR / "sentiment_metrics.csv", index=False, encoding="utf-8-sig")

    legacy_evidence = evidence.rename(
        columns={
            "date": "published_date",
            "candidate": "candidate_code",
            "issue": "issue_category",
            "count": "reaction_count",
        }
    ).copy()
    legacy_evidence["candidate_code"] = legacy_evidence["candidate_code"].map(candidate_code)
    legacy_evidence["url"] = "#"
    legacy_evidence["outlet"] = legacy_evidence["source_label"]
    legacy_evidence["evidence_type"] = legacy_evidence["source_label"]
    legacy_evidence[
        [
            "published_date",
            "candidate_code",
            "source",
            "issue_category",
            "title",
            "summary",
            "reaction_count",
            "url",
            "evidence_type",
            "outlet",
        ]
    ].to_csv(DATA_DIR / "evidence_items.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    detail = build_issue_detail_timeseries()
    reaction = build_reaction_timeseries(detail)
    issue_summary = build_issue_summary(detail)
    source_summary = build_source_summary(detail)
    keyword_summary = build_keyword_summary(detail)
    evidence = build_evidence_samples(detail)
    status = build_collection_status(detail)

    files = {
        "candidates.csv": pd.DataFrame(CANDIDATES),
        "candidate_channels.csv": pd.DataFrame(CHANNELS, columns=["candidate", "channel", "url"]),
        "reaction_timeseries.csv": reaction,
        "issue_summary.csv": issue_summary,
        "issue_detail_timeseries.csv": detail,
        "source_summary.csv": source_summary,
        "keyword_summary.csv": keyword_summary,
        "evidence_samples.csv": evidence,
        "collection_status.csv": status,
        "narrative_summary.csv": pd.DataFrame(
            [
                {
                    "period_type": "7d",
                    "headline_text": "공개 온라인 반응 기준으로 교통·주거·한강 쟁점이 최근 기간의 핵심 흐름을 만들었습니다.",
                    "summary_text": "선택 쟁점과 출처 필터에 따라 시계열, 반응 분위기, 근거 샘플이 함께 갱신됩니다.",
                    "reliability_text": "실제 지지율·득표율·선거 결과 예측이 아닙니다.",
                }
            ]
        ),
    }
    for filename, frame in files.items():
        frame.to_csv(DATA_DIR / filename, index=False, encoding="utf-8-sig")

    write_legacy_alias_files(detail, reaction, keyword_summary, evidence)

    print(f"Generated {len(files)} primary mock CSV files in {DATA_DIR}")
    print(f"Period: {DATES.min().date()} ~ {DATES.max().date()}")
    print(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
