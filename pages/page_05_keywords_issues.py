from __future__ import annotations

from pages import page_02_candidate_info


def render(data: dict, period_key: str, context: dict) -> None:
    page_02_candidate_info.render(data, period_key, context)
