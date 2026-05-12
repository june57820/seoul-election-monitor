from __future__ import annotations

from pages import page_04_source_metrics


def render(data: dict, period_key: str, context: dict) -> None:
    page_04_source_metrics.render(data, period_key, context)
