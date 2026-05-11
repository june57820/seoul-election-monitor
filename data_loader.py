from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "mock"
ASSET_DIR = BASE_DIR / "assets" / "images"

PERIOD_OPTIONS = {
    "7d": {"label": "7일", "title": "최근 7일", "days": 7},
    "14d": {"label": "14일", "title": "최근 14일", "days": 14},
    "30d": {"label": "1개월", "title": "최근 1개월", "days": 30},
}

CANDIDATE_ORDER = ["JWO", "OSH"]
CANDIDATE_COLORS = {"JWO": "#2563eb", "OSH": "#ef3340"}
CANDIDATE_SOFT_COLORS = {"JWO": "#eef5ff", "OSH": "#fff1f2"}
CANDIDATE_NAMES = {"JWO": "정원오", "OSH": "오세훈"}
CANDIDATE_IMAGES = {
    "JWO": ASSET_DIR / "jung_won_oh.jpg",
    "OSH": ASSET_DIR / "oh_naver_profile.jpg",
}
OFFICIAL_CHANNELS = {
    "JWO": [
        ("공식 홈페이지", "https://www.sd.go.kr/mayor/index.do"),
        ("페이스북", "https://www.facebook.com/kindchongwono/"),
        ("유튜브", "https://www.youtube.com/channel/UC02pT-cLZ1RQcVxmC7fKIMw"),
        ("인스타그램", "https://www.instagram.com/chongwonoh/"),
    ],
    "OSH": [
        ("공식 홈페이지", "https://mayor.seoul.go.kr/app/index.do"),
        ("페이스북", "https://www.facebook.com/ohsehoon4u"),
        ("유튜브", "https://www.youtube.com/@ohsehoontv"),
        ("인스타그램", "https://www.instagram.com/ohsehoon4u/"),
    ],
}
SOURCE_LABELS = {"news": "뉴스 기사", "video_post": "영상·게시글", "comment": "댓글"}
SOURCE_ORDER = ["news", "video_post", "comment"]
SOURCE_ICONS = {"news": "NEWS", "video_post": "PLAY", "comment": "CHAT"}
SOURCE_DETAIL_LABELS = {
    "naver_news": "네이버뉴스",
    "daum_news": "다음뉴스",
    "youtube": "유튜브",
    "blog_cafe": "블로그·카페",
    "community": "커뮤니티",
    "news_comment": "뉴스 댓글",
    "youtube_comment": "유튜브 댓글",
    "community_comment": "커뮤니티 댓글",
}
SOURCE_DETAIL_ORDER = list(SOURCE_DETAIL_LABELS.keys())


def _read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    for column in parse_dates or []:
        frame[column] = pd.to_datetime(frame[column])
    return frame


@lru_cache(maxsize=1)
def load_data(data_dir: str | Path | None = None) -> dict[str, pd.DataFrame]:
    path = Path(data_dir) if data_dir else DATA_DIR
    files = {
        "candidates": ("candidates.csv", []),
        "daily": ("daily_metrics.csv", ["metric_date"]),
        "source": ("source_metrics.csv", ["metric_date"]),
        "keywords": ("keyword_metrics.csv", ["metric_date"]),
        "sentiment": ("sentiment_metrics.csv", ["metric_date"]),
        "evidence": ("evidence_items.csv", ["published_date"]),
        "narrative": ("narrative_summary.csv", []),
        "status": ("collection_status.csv", []),
    }
    return {key: _read_csv(path / filename, parse_dates=dates) for key, (filename, dates) in files.items()}


def period_context(data: dict[str, pd.DataFrame], period_key: str) -> dict[str, Any]:
    option = PERIOD_OPTIONS.get(period_key, PERIOD_OPTIONS["7d"])
    end_date = data["daily"]["metric_date"].max()
    start_date = end_date - pd.Timedelta(days=option["days"] - 1)
    return {
        "period_key": period_key,
        "label": option["label"],
        "title": option["title"],
        "days": option["days"],
        "start": start_date,
        "end": end_date,
        "start_text": start_date.strftime("%Y.%m.%d"),
        "end_text": end_date.strftime("%Y.%m.%d"),
        "range_text": f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}",
    }


def filter_period(data: dict[str, pd.DataFrame], period_key: str) -> dict[str, pd.DataFrame]:
    ctx = period_context(data, period_key)
    start, end = ctx["start"], ctx["end"]
    filtered: dict[str, pd.DataFrame] = {}

    for key, frame in data.items():
        if "metric_date" in frame.columns:
            mask = frame["metric_date"].between(start, end)
            filtered[key] = frame.loc[mask].copy()
        elif "published_date" in frame.columns:
            mask = frame["published_date"].between(start, end)
            filtered[key] = frame.loc[mask].copy()
        elif "period_type" in frame.columns:
            filtered[key] = frame.loc[frame["period_type"].eq(period_key)].copy()
        else:
            filtered[key] = frame.copy()

    return filtered


def candidate_summary(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    daily = frames["daily"].sort_values("metric_date")
    grouped = (
        daily.groupby("candidate_code", as_index=False)
        .agg(
            total_reactions=("total_reactions", "sum"),
            mention_count=("mention_count", "sum"),
            content_count=("content_count", "sum"),
            comment_count=("comment_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            latest_growth_rate=("growth_rate", "last"),
        )
        .round({"reaction_score": 1, "latest_growth_rate": 1})
    )

    growth_rows = []
    for code, candidate_daily in daily.groupby("candidate_code"):
        first = candidate_daily.iloc[0]["total_reactions"]
        last = candidate_daily.iloc[-1]["total_reactions"]
        raw_growth = (last - first) / first * 100 if first else 0.0
        period_growth = round(raw_growth * 0.45, 1)
        growth_rows.append({"candidate_code": code, "period_growth_rate": period_growth})

    grouped = grouped.merge(pd.DataFrame(growth_rows), on="candidate_code", how="left")
    grouped = frames["candidates"].merge(grouped, on="candidate_code", how="left")
    grouped["sort_order"] = grouped["candidate_code"].map({code: idx for idx, code in enumerate(CANDIDATE_ORDER)})
    return grouped.sort_values("sort_order").drop(columns=["sort_order"])


def competition_share(summary: pd.DataFrame) -> pd.DataFrame:
    total = summary["total_reactions"].sum()
    share = summary[["candidate_code", "candidate_name", "total_reactions"]].copy()
    share["share"] = (share["total_reactions"] / total * 100).round(1) if total else 0
    return share


def source_summary(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    source = frames["source"]
    grouped = (
        source.groupby(["source", "candidate_code"], as_index=False)
        .agg(content_count=("content_count", "sum"), comment_count=("comment_count", "sum"), reaction_count=("reaction_count", "sum"))
    )
    grouped["source_label"] = grouped["source"].map(SOURCE_LABELS)
    grouped["source_order"] = grouped["source"].map({source: idx for idx, source in enumerate(SOURCE_ORDER)})
    grouped["candidate_order"] = grouped["candidate_code"].map({code: idx for idx, code in enumerate(CANDIDATE_ORDER)})
    return grouped.sort_values(["source_order", "candidate_order"]).drop(columns=["source_order", "candidate_order"])


def source_detail_summary(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    source = frames["source"].copy()
    if "source_detail" not in source.columns:
        source["source_detail"] = source["source"]
    if "source_detail_label" not in source.columns:
        source["source_detail_label"] = source["source_detail"].map(SOURCE_DETAIL_LABELS).fillna(source["source"].map(SOURCE_LABELS))

    grouped = (
        source.groupby(["source", "source_detail", "source_detail_label", "candidate_code"], as_index=False)
        .agg(content_count=("content_count", "sum"), comment_count=("comment_count", "sum"), reaction_count=("reaction_count", "sum"))
    )
    grouped["source_label"] = grouped["source"].map(SOURCE_LABELS)
    grouped["source_order"] = grouped["source"].map({source: idx for idx, source in enumerate(SOURCE_ORDER)})
    grouped["detail_order"] = grouped["source_detail"].map({source: idx for idx, source in enumerate(SOURCE_DETAIL_ORDER)}).fillna(99)
    grouped["candidate_order"] = grouped["candidate_code"].map({code: idx for idx, code in enumerate(CANDIDATE_ORDER)})
    return grouped.sort_values(["source_order", "detail_order", "candidate_order"]).drop(columns=["source_order", "detail_order", "candidate_order"])


def source_totals(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    grouped = (
        source_summary(frames)
        .groupby(["source", "source_label"], as_index=False)
        .agg(reaction_count=("reaction_count", "sum"), content_count=("content_count", "sum"), comment_count=("comment_count", "sum"))
    )
    total = grouped["reaction_count"].sum()
    grouped["share"] = (grouped["reaction_count"] / total * 100).round(1) if total else 0
    grouped["source_order"] = grouped["source"].map({source: idx for idx, source in enumerate(SOURCE_ORDER)})
    return grouped.sort_values("source_order").drop(columns=["source_order"])


def keyword_summary(frames: dict[str, pd.DataFrame], top_n: int = 10) -> pd.DataFrame:
    keywords = frames["keywords"]
    grouped = (
        keywords.groupby(["candidate_code", "keyword", "keyword_type", "issue_category"], as_index=False)
        .agg(mention_count=("mention_count", "sum"), rank=("rank", "mean"), rank_change=("rank_change", "sum"))
    )
    grouped["rank"] = grouped["rank"].round(0).astype(int)
    grouped = grouped.sort_values(["candidate_code", "mention_count"], ascending=[True, False])
    return grouped.groupby("candidate_code").head(top_n).reset_index(drop=True)


def issue_share(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    keywords = frames["keywords"]
    grouped = (
        keywords.groupby(["issue_category", "candidate_code"], as_index=False)
        .agg(mention_count=("mention_count", "sum"))
    )
    pivot = grouped.pivot_table(index="issue_category", columns="candidate_code", values="mention_count", fill_value=0).reset_index()
    for code in CANDIDATE_ORDER:
        if code not in pivot:
            pivot[code] = 0
    pivot["total"] = pivot[CANDIDATE_ORDER].sum(axis=1)
    smoothing = pivot["total"] * 0.45
    for code in CANDIDATE_ORDER:
        pivot[f"{code}_share"] = ((pivot[code] + smoothing) / (pivot["total"] + smoothing * 2) * 100).fillna(0).round(0).astype(int)
    return pivot.sort_values("total", ascending=False)


def sentiment_summary(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sentiment = frames["sentiment"]
    grouped = (
        sentiment.groupby("candidate_code", as_index=False)
        .agg(positive_count=("positive_count", "sum"), neutral_count=("neutral_count", "sum"), negative_count=("negative_count", "sum"))
    )
    grouped["total"] = grouped[["positive_count", "neutral_count", "negative_count"]].sum(axis=1)
    for column in ["positive", "neutral", "negative"]:
        grouped[f"{column}_ratio"] = (grouped[f"{column}_count"] / grouped["total"] * 100).round(1)
    return grouped


def daily_sentiment_long(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    sentiment = frames["sentiment"].copy()
    long = sentiment.melt(
        id_vars=["metric_date", "candidate_code"],
        value_vars=["positive_count", "neutral_count", "negative_count"],
        var_name="reaction_type",
        value_name="count",
    )
    label_map = {"positive_count": "우호 표현", "neutral_count": "중립 표현", "negative_count": "비판 표현"}
    long["reaction_label"] = long["reaction_type"].map(label_map)
    return long


def narrative(frames: dict[str, pd.DataFrame], period_key: str) -> dict[str, str]:
    narrative_frame = frames["narrative"]
    if narrative_frame.empty:
        return {
            "headline_text": "선택 기간의 공개 온라인 반응 흐름을 요약할 수 없습니다.",
            "summary_text": "",
            "competition_text": "",
            "issue_text": "",
            "reliability_text": "표시된 수치는 실제 지지율, 득표율, 선거 결과 예측을 의미하지 않습니다.",
        }
    row = narrative_frame.iloc[0].to_dict()
    return {key: str(value) for key, value in row.items()}


def collection_status(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    status = frames["status"]
    if status.empty:
        return {
            "updated_at": "-",
            "collection_status": "상태 확인 필요",
            "total_items": 0,
            "warning_text": "이 데이터는 여론조사나 투표 예측이 아닙니다.",
        }
    return status.iloc[0].to_dict()


def format_number(value: float | int) -> str:
    return f"{int(value):,}"


def format_percent(value: float | int, signed: bool = False) -> str:
    number = float(value)
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.1f}%"


def date_text(value: pd.Timestamp) -> str:
    return pd.to_datetime(value).strftime("%Y.%m.%d")


def candidate_name(code: str) -> str:
    return CANDIDATE_NAMES.get(code, code)


def candidate_color(code: str) -> str:
    return CANDIDATE_COLORS.get(code, "#64748b")
