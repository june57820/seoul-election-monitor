from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "mock"
ASSET_DIR = BASE_DIR / "assets" / "images"

DEMO_WARNING = "이 수치는 실제 지지율·득표율·선거 결과 예측이 아니라 공개 온라인 반응 데모용 수치입니다."
DATA_START = pd.Timestamp("2026-01-01")
DATA_END = pd.Timestamp("2026-05-12")

PERIOD_OPTIONS = {
    "7d": {"label": "7일", "title": "최근 7일", "days": 7},
    "14d": {"label": "14일", "title": "최근 14일", "days": 14},
    "30d": {"label": "1개월", "title": "최근 1개월", "days": 30},
}

CANDIDATE_ORDER = ["정원오", "오세훈"]
CANDIDATE_COLORS = {"정원오": "#2563eb", "오세훈": "#ef3340"}
CANDIDATE_SOFT_COLORS = {"정원오": "#eff6ff", "오세훈": "#fff1f2"}
CANDIDATE_IMAGES = {
    "정원오": ASSET_DIR / "jung_won_oh.jpg",
    "오세훈": ASSET_DIR / "oh_naver_profile.jpg",
}

SOURCE_LABELS = {
    "news": "뉴스",
    "video_post": "영상·게시글",
    "comment": "댓글",
    "community_x": "커뮤니티/X",
}
SOURCE_OPTIONS = {"전체": "전체", **SOURCE_LABELS}

REACTION_TYPES = ["전체", "우호", "중립", "비판"]
ISSUE_ORDER = ["교통", "한강", "GTX", "도시개발", "지하화", "재개발", "주거", "청년정책"]
METRIC_OPTIONS = ["반응량", "반응점수", "반응 분위기", "후보 간 격차"]


def _read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    for column in parse_dates or []:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column])
    return frame


@lru_cache(maxsize=1)
def load_data(data_dir: str | Path | None = None) -> dict[str, pd.DataFrame]:
    path = Path(data_dir) if data_dir else DATA_DIR
    files = {
        "candidates": ("candidates.csv", []),
        "candidate_channels": ("candidate_channels.csv", []),
        "candidate_period_summary": ("candidate_period_summary.csv", ["period_start", "period_end"]),
        "reaction_timeseries": ("reaction_timeseries.csv", ["date"]),
        "issue_summary": ("issue_summary.csv", []),
        "issue_detail_timeseries": ("issue_detail_timeseries.csv", ["date"]),
        "source_summary": ("source_summary.csv", ["date"]),
        "keyword_summary": ("keyword_summary.csv", []),
        "evidence_samples": ("evidence_samples.csv", ["date", "datetime"]),
        "collection_status": ("collection_status.csv", ["latest_date"]),
        "narrative": ("narrative_summary.csv", []),
    }
    return {key: _read_csv(path / filename, dates) for key, (filename, dates) in files.items()}


def clear_data_cache() -> None:
    load_data.cache_clear()


def latest_data_date(data: dict[str, pd.DataFrame] | None = None) -> pd.Timestamp:
    frames = data or load_data()
    return frames["issue_detail_timeseries"]["date"].max()


def make_range_period_key(start: pd.Timestamp | str, end: pd.Timestamp | str) -> str:
    start_date = pd.to_datetime(start).strftime("%Y-%m-%d")
    end_date = pd.to_datetime(end).strftime("%Y-%m-%d")
    return f"range:{start_date}:{end_date}"


def _clamped_date(value: pd.Timestamp | str) -> pd.Timestamp:
    date = pd.to_datetime(value).normalize()
    return min(max(date, DATA_START), DATA_END)


def _parse_range_period(period_key: str) -> tuple[pd.Timestamp, pd.Timestamp] | None:
    if not isinstance(period_key, str) or not period_key.startswith("range:"):
        return None
    parts = period_key.split(":")
    if len(parts) != 3:
        return None
    start_date = _clamped_date(parts[1])
    end_date = _clamped_date(parts[2])
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    return start_date, end_date


def period_context(period_key: str, data: dict[str, pd.DataFrame] | None = None) -> dict[str, Any]:
    frames = data or load_data()
    range_dates = _parse_range_period(period_key)
    if range_dates:
        start_date, end_date = range_dates
        days = int((end_date - start_date).days) + 1
        label = "사용자 지정" if days not in {7, 14, 30} else f"{days}일"
        if days == 30:
            label = "1개월"
        title = "사용자 지정 기간"
    else:
        option = PERIOD_OPTIONS.get(period_key, PERIOD_OPTIONS["7d"])
        end_date = min(latest_data_date(frames), DATA_END)
        start_date = max(end_date - pd.Timedelta(days=option["days"] - 1), DATA_START)
        days = int((end_date - start_date).days) + 1
        label = option["label"]
        title = option["title"]
    return {
        "period_key": period_key,
        "label": label,
        "title": title,
        "days": days,
        "start": start_date,
        "end": end_date,
        "start_text": start_date.strftime("%Y.%m.%d"),
        "end_text": end_date.strftime("%Y.%m.%d"),
        "range_text": f"{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}",
    }


def _period_mask(frame: pd.DataFrame, period_key: str, date_col: str = "date") -> pd.Series:
    ctx = period_context(period_key)
    return frame[date_col].between(ctx["start"], ctx["end"])


def filter_period(data: dict[str, pd.DataFrame], period_key: str) -> dict[str, pd.DataFrame]:
    filtered: dict[str, pd.DataFrame] = {}
    for key, frame in data.items():
        if "date" in frame.columns:
            filtered[key] = frame.loc[_period_mask(frame, period_key, "date")].copy()
        elif "datetime" in frame.columns:
            ctx = period_context(period_key)
            filtered[key] = frame.loc[frame["datetime"].between(ctx["start"], ctx["end"] + pd.Timedelta(days=1))].copy()
        else:
            filtered[key] = frame.copy()
    return filtered


def get_candidate_summary(period_key: str) -> pd.DataFrame:
    frames = load_data()
    daily = frames["reaction_timeseries"].loc[_period_mask(frames["reaction_timeseries"], period_key)].copy()

    summary = (
        daily.groupby("candidate", as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            mention_count=("reaction_count", "sum"),
            content_count=("content_count", "sum"),
            comment_count=("comment_count", "sum"),
            reaction_score=("reaction_score", "mean"),
        )
        .round({"reaction_score": 1})
    )

    changes = []
    for candidate, candidate_daily in daily.sort_values("date").groupby("candidate"):
        first_value = candidate_daily.iloc[0]["reaction_count"]
        last_value = candidate_daily.iloc[-1]["reaction_count"]
        change = ((last_value - first_value) / first_value * 100) if first_value else 0
        changes.append({"candidate": candidate, "period_change": round(change, 1)})
    summary = summary.merge(pd.DataFrame(changes), on="candidate", how="left")
    summary = frames["candidates"].merge(summary, on="candidate", how="left")

    period_summary = frames.get("candidate_period_summary", pd.DataFrame())
    if not period_summary.empty:
        ctx = period_context(period_key, frames)
        period_rows = period_summary[
            period_summary["period_start"].dt.normalize().eq(ctx["start"].normalize())
            & period_summary["period_end"].dt.normalize().eq(ctx["end"].normalize())
        ][["candidate", "reaction_score", "period_change", "mention_count", "basis", "confidence"]]
        if not period_rows.empty:
            summary = summary.drop(columns=["reaction_score", "period_change", "mention_count"], errors="ignore")
            summary = summary.merge(period_rows, on="candidate", how="left")

    keywords = get_keyword_summary(period_key)
    top_keyword_map = (
        keywords.sort_values(["candidate", "mention_count"], ascending=[True, False])
        .groupby("candidate")["keyword"]
        .apply(lambda values: list(values.head(5)))
        .to_dict()
    )
    summary["top_keywords"] = summary["candidate"].map(top_keyword_map).apply(lambda value: value if isinstance(value, list) else [])
    summary["display_order"] = summary["candidate"].map({name: idx for idx, name in enumerate(CANDIDATE_ORDER)})
    return summary.sort_values("display_order").drop(columns=["display_order"])


def get_reaction_timeseries(period_key: str, candidate: str = "전체", source: str = "전체", metric: str = "반응량") -> pd.DataFrame:
    frames = load_data()
    if source == "전체":
        grouped = frames["reaction_timeseries"].loc[_period_mask(frames["reaction_timeseries"], period_key)].copy()
        if candidate != "전체":
            grouped = grouped[grouped["candidate"].eq(candidate)]
        grouped = grouped.sort_values(["candidate", "date"])
        grouped["daily_change"] = grouped.groupby("candidate")["reaction_count"].pct_change().fillna(0).mul(100).round(1)
        grouped["metric_value"] = _metric_value(grouped, metric)
        return grouped

    detail = frames["issue_detail_timeseries"].loc[_period_mask(frames["issue_detail_timeseries"], period_key)].copy()
    if candidate != "전체":
        detail = detail[detail["candidate"].eq(candidate)]
    detail = detail[detail["source"].eq(source)]
    grouped = (
        detail.groupby(["date", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
        )
        .round({"reaction_score": 1})
        .sort_values(["candidate", "date"])
    )
    grouped["daily_change"] = grouped.groupby("candidate")["reaction_count"].pct_change().fillna(0).mul(100).round(1)
    grouped["metric_value"] = _metric_value(grouped, metric)
    return grouped


def get_issue_summary(period_key: str) -> pd.DataFrame:
    frames = load_data()
    detail = frames["issue_detail_timeseries"].loc[_period_mask(frames["issue_detail_timeseries"], period_key)].copy()
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
    pivot = grouped.pivot_table(index="issue", columns="candidate", values="reaction_count", fill_value=0).reset_index()
    for candidate in CANDIDATE_ORDER:
        if candidate not in pivot.columns:
            pivot[candidate] = 0
    pivot["total"] = pivot[CANDIDATE_ORDER].sum(axis=1)
    for candidate in CANDIDATE_ORDER:
        pivot[f"{candidate}_share"] = (pivot[candidate] / pivot["total"] * 100).fillna(0).round(1)
    pivot["issue_order"] = pivot["issue"].map({issue: idx for idx, issue in enumerate(ISSUE_ORDER)})
    return pivot.sort_values(["total", "issue_order"], ascending=[False, True]).drop(columns=["issue_order"])


def _metric_value(frame: pd.DataFrame, metric: str) -> pd.Series:
    if metric == "반응점수":
        return frame["reaction_score"]
    if metric == "후보 간 격차":
        pivot = frame.pivot_table(index="date", columns="candidate", values="reaction_count", fill_value=0)
        gap = (pivot.get("정원오", 0) - pivot.get("오세훈", 0)).abs().rename("metric_value")
        return frame["date"].map(gap)
    if metric == "반응 분위기":
        total = frame[["favorable_count", "neutral_count", "critical_count"]].sum(axis=1)
        return (frame["favorable_count"] / total * 100).fillna(0).round(1)
    return frame["reaction_count"]


def get_issue_detail_timeseries(period_key: str, issue: str, source: str = "전체", metric: str = "반응량") -> pd.DataFrame:
    frames = load_data()
    detail = frames["issue_detail_timeseries"].loc[_period_mask(frames["issue_detail_timeseries"], period_key)].copy()
    detail = detail[detail["issue"].eq(issue)]
    if source != "전체":
        detail = detail[detail["source"].eq(source)]
    grouped = (
        detail.groupby(["date", "issue", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
            top_keywords=("top_keywords", lambda values: ", ".join(sorted(set(", ".join(values).split(", ")))[:4])),
        )
        .round({"reaction_score": 1})
        .sort_values(["candidate", "date"])
    )
    grouped["daily_change"] = grouped.groupby("candidate")["reaction_count"].pct_change().fillna(0).mul(100).round(1)
    grouped["metric_value"] = _metric_value(grouped, metric)
    total = grouped[["favorable_count", "neutral_count", "critical_count"]].sum(axis=1)
    grouped["favorable_ratio"] = (grouped["favorable_count"] / total * 100).fillna(0).round(1)
    grouped["neutral_ratio"] = (grouped["neutral_count"] / total * 100).fillna(0).round(1)
    grouped["critical_ratio"] = (grouped["critical_count"] / total * 100).fillna(0).round(1)
    return grouped


def get_issue_change_table(period_key: str, issue: str, source: str = "전체") -> pd.DataFrame:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    pivot = detail.pivot_table(index="date", columns="candidate", values="reaction_count", fill_value=0).reset_index()
    for candidate in CANDIDATE_ORDER:
        if candidate not in pivot.columns:
            pivot[candidate] = 0
    mood = (
        detail.groupby("date", as_index=False)
        .agg(
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
            top_keywords=("top_keywords", lambda values: ", ".join(sorted(set(", ".join(values).split(", ")))[:5])),
        )
        .sort_values("date")
    )
    total = mood[["favorable_count", "neutral_count", "critical_count"]].sum(axis=1)
    mood["우호 표현 비중"] = (mood["favorable_count"] / total * 100).round(1)
    mood["중립 표현 비중"] = (mood["neutral_count"] / total * 100).round(1)
    mood["비판 표현 비중"] = (mood["critical_count"] / total * 100).round(1)
    table = pivot.merge(mood[["date", "우호 표현 비중", "중립 표현 비중", "비판 표현 비중", "top_keywords"]], on="date", how="left")
    table = table.rename(
        columns={
            "date": "날짜",
            "정원오": "정원오 반응량",
            "오세훈": "오세훈 반응량",
            "top_keywords": "주요 연관 키워드",
        }
    )
    return table.sort_values("날짜")


def get_issue_mood_timeseries(period_key: str, issue: str, source: str = "전체") -> pd.DataFrame:
    detail = get_issue_detail_timeseries(period_key, issue, source, "반응량")
    grouped = (
        detail.groupby("date", as_index=False)
        .agg(
            favorable_count=("favorable_count", "sum"),
            neutral_count=("neutral_count", "sum"),
            critical_count=("critical_count", "sum"),
        )
        .sort_values("date")
    )
    return grouped.melt(
        id_vars="date",
        value_vars=["favorable_count", "neutral_count", "critical_count"],
        var_name="reaction_type",
        value_name="count",
    ).assign(
        reaction_label=lambda frame: frame["reaction_type"].map(
            {
                "favorable_count": "우호 표현",
                "neutral_count": "중립 표현",
                "critical_count": "비판 표현",
            }
        )
    )


def get_source_summary(period_key: str, issue: str | None = None, source: str = "전체") -> pd.DataFrame:
    frames = load_data()
    summary = frames["source_summary"].loc[_period_mask(frames["source_summary"], period_key)].copy()
    if issue:
        summary = summary[summary["issue"].eq(issue)]
    if source != "전체":
        summary = summary[summary["source"].eq(source)]
    grouped = (
        summary.groupby(["source", "source_label", "candidate"], as_index=False)
        .agg(
            reaction_count=("reaction_count", "sum"),
            reaction_score=("reaction_score", "mean"),
            content_count=("content_count", "sum"),
            comment_count=("comment_count", "sum"),
        )
        .round({"reaction_score": 1})
    )
    return grouped


def get_source_timeseries(period_key: str, issue: str | None = None, source: str = "전체") -> pd.DataFrame:
    frames = load_data()
    summary = frames["source_summary"].loc[_period_mask(frames["source_summary"], period_key)].copy()
    if issue:
        summary = summary[summary["issue"].eq(issue)]
    if source != "전체":
        summary = summary[summary["source"].eq(source)]
    return (
        summary.groupby(["date", "source", "source_label", "candidate"], as_index=False)
        .agg(reaction_count=("reaction_count", "sum"), content_count=("content_count", "sum"), comment_count=("comment_count", "sum"))
        .sort_values(["source", "candidate", "date"])
    )


def get_keyword_summary(period_key: str, issue: str | None = None) -> pd.DataFrame:
    frames = load_data()
    ctx = period_context(period_key, frames)
    detail = frames["issue_detail_timeseries"].loc[_period_mask(frames["issue_detail_timeseries"], period_key)].copy()
    issues = [issue] if issue else detail["issue"].drop_duplicates().tolist()
    keywords = frames["keyword_summary"]
    keywords = keywords[keywords["issue"].isin(issues)].copy()
    if not (ctx["start"].date().isoformat() == "2026-05-06" and ctx["end"].date().isoformat() == "2026-05-12"):
        factor = max(0.25, min(5.4, ctx["days"] / 7))
        keywords["mention_count"] = (keywords["mention_count"] * factor).round().astype(int)
    return keywords.sort_values(["candidate", "mention_count"], ascending=[True, False])


def get_keyword_timeseries(period_key: str, keyword: str, issue: str | None = None, source: str = "전체") -> pd.DataFrame:
    query = str(keyword or "").strip()
    if not query:
        return pd.DataFrame()

    query_norm = query.casefold()
    frames = load_data()
    detail = frames["issue_detail_timeseries"].loc[_period_mask(frames["issue_detail_timeseries"], period_key)].copy()
    if issue:
        detail = detail[detail["issue"].eq(issue)]
    if source != "전체":
        detail = detail[detail["source"].eq(source)]
    if detail.empty:
        return pd.DataFrame()

    keyword_summary = get_keyword_summary(period_key, issue)
    keyword_text = keyword_summary["keyword"].astype(str).str.casefold()
    matched_keywords = keyword_summary[
        keyword_text.str.contains(query_norm, regex=False) | keyword_text.map(lambda value: query_norm in value or value in query_norm)
    ].copy()

    rows: list[pd.DataFrame] = []
    for (row_issue, candidate), group in detail.groupby(["issue", "candidate"]):
        group = group.copy()
        direct_mask = group["top_keywords"].astype(str).str.casefold().str.contains(query_norm, regex=False, na=False)
        keyword_rows = matched_keywords[matched_keywords["issue"].eq(row_issue) & matched_keywords["candidate"].eq(candidate)]

        if not keyword_rows.empty:
            eligible = group
            matched_label = ", ".join(keyword_rows["keyword"].astype(str).drop_duplicates().head(4))
            target_mentions = float(keyword_rows["mention_count"].sum())
        elif direct_mask.any():
            eligible = group.loc[direct_mask].copy()
            matched_label = query
            target_mentions = float(eligible["reaction_count"].sum() * 0.32)
        else:
            continue

        total_reactions = float(max(1, eligible["reaction_count"].sum()))
        target_mentions = min(target_mentions, total_reactions * 0.9)
        eligible["keyword"] = query
        eligible["matched_keywords"] = matched_label
        eligible["keyword_mention_count"] = (eligible["reaction_count"] / total_reactions * target_mentions).round().astype(int)
        ratio = (eligible["keyword_mention_count"] / eligible["reaction_count"].replace(0, pd.NA)).fillna(0)
        eligible["keyword_favorable_count"] = (eligible["favorable_count"] * ratio).round().astype(int)
        eligible["keyword_neutral_count"] = (eligible["neutral_count"] * ratio).round().astype(int)
        eligible["keyword_critical_count"] = (
            eligible["keyword_mention_count"] - eligible["keyword_favorable_count"] - eligible["keyword_neutral_count"]
        ).clip(lower=0)
        rows.append(eligible)

    if not rows:
        return pd.DataFrame()

    result = pd.concat(rows, ignore_index=True)
    grouped = (
        result.groupby(["date", "candidate"], as_index=False)
        .agg(
            keyword_mention_count=("keyword_mention_count", "sum"),
            favorable_count=("keyword_favorable_count", "sum"),
            neutral_count=("keyword_neutral_count", "sum"),
            critical_count=("keyword_critical_count", "sum"),
            matched_keywords=("matched_keywords", lambda values: ", ".join(sorted(set(values)))[:80]),
        )
        .sort_values(["candidate", "date"])
    )
    all_dates = sorted(detail["date"].drop_duplicates())
    index = pd.MultiIndex.from_product([all_dates, CANDIDATE_ORDER], names=["date", "candidate"])
    grouped = grouped.set_index(["date", "candidate"]).reindex(index).reset_index()
    fill_columns = ["keyword_mention_count", "favorable_count", "neutral_count", "critical_count"]
    grouped[fill_columns] = grouped[fill_columns].fillna(0).astype(int)
    grouped["matched_keywords"] = grouped["matched_keywords"].fillna("-")
    total = grouped[["favorable_count", "neutral_count", "critical_count"]].sum(axis=1)
    grouped["favorable_ratio"] = (grouped["favorable_count"] / total * 100).fillna(0).round(1)
    grouped["neutral_ratio"] = (grouped["neutral_count"] / total * 100).fillna(0).round(1)
    grouped["critical_ratio"] = (grouped["critical_count"] / total * 100).fillna(0).round(1)
    grouped = grouped.sort_values(["candidate", "date"])
    daily_change = grouped.groupby("candidate")["keyword_mention_count"].pct_change()
    grouped["daily_change"] = daily_change.replace([float("inf"), float("-inf")], 0).fillna(0).mul(100).round(1)
    return grouped


def get_evidence_samples(
    period_key: str,
    issue: str | None = None,
    source: str = "전체",
    candidate: str = "전체",
    reaction_type: str = "전체",
    sort: str = "최신순",
) -> pd.DataFrame:
    frames = load_data()
    evidence = frames["evidence_samples"].loc[_period_mask(frames["evidence_samples"], period_key, "date")].copy()
    if issue:
        evidence = evidence[evidence["issue"].eq(issue)]
    if source != "전체":
        evidence = evidence[evidence["source"].eq(source)]
    if candidate != "전체":
        evidence = evidence[evidence["candidate"].eq(candidate)]
    if reaction_type != "전체":
        evidence = evidence[evidence["reaction_type"].eq(reaction_type)]
    if sort == "반응 많은 순":
        evidence = evidence.sort_values(["count", "datetime"], ascending=[False, False])
    else:
        evidence = evidence.sort_values(["datetime", "count"], ascending=[False, False])
    return evidence


def get_collection_status(period_key: str | None = None) -> dict[str, Any]:
    frames = load_data()
    status = frames["collection_status"]
    if status.empty:
        return {
            "updated_at": "-",
            "collection_status": "상태 확인 필요",
            "total_items": 0,
            "source_scope": "뉴스, 영상·게시글, 댓글, 커뮤니티/X",
            "warning_text": DEMO_WARNING,
        }
    row = status.iloc[0].to_dict()
    if period_key:
        reaction = frames["reaction_timeseries"].loc[_period_mask(frames["reaction_timeseries"], period_key)]
        row["total_items"] = int(reaction["reaction_count"].sum())
    return row


def get_candidate_channels() -> pd.DataFrame:
    return load_data()["candidate_channels"].copy()


def get_candidate_image(candidate: str) -> Path:
    return CANDIDATE_IMAGES[candidate]


def format_number(value: float | int) -> str:
    return f"{int(round(float(value))):,}"


def format_percent(value: float | int, signed: bool = False) -> str:
    number = float(value)
    sign = "+" if signed and number > 0 else ""
    return f"{sign}{number:.1f}%"


def date_text(value: pd.Timestamp) -> str:
    return pd.to_datetime(value).strftime("%Y.%m.%d")


def short_date_text(value: pd.Timestamp) -> str:
    return pd.to_datetime(value).strftime("%m.%d")
