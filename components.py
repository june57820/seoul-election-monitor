from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import (
    CANDIDATE_COLORS,
    CANDIDATE_ORDER,
    DATA_END,
    DATA_START,
    DEMO_WARNING,
    ISSUE_ORDER,
    METRIC_OPTIONS,
    PERIOD_OPTIONS,
    REACTION_TYPES,
    SOURCE_LABELS,
    SOURCE_OPTIONS,
    format_number,
    format_percent,
    get_candidate_image,
    make_range_period_key,
    period_context,
    short_date_text,
)


FONT_STACK = "'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif"
BRAND_LOGO = Path(__file__).resolve().parent / "assets" / "images" / "seoul_online_issue_radar_logo.svg"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        :root {{
            --navy-950: #071528;
            --navy-900: #0b1d34;
            --navy-800: #102846;
            --ink: #0f172a;
            --muted: #64748b;
            --line: #dbe5f2;
            --surface: #ffffff;
            --surface-soft: #f8fbff;
            --bg: #f3f7fc;
            --blue: #2563eb;
            --blue-dark: #1d4ed8;
            --blue-soft: #eff6ff;
            --red: #ef3340;
            --red-dark: #dc2626;
            --red-soft: #fff1f2;
            --green: #22c55e;
            --green-dark: #15803d;
            --green-soft: #f0fdf4;
            --gray-soft: #f1f5f9;
            --orange: #f97316;
            --radius-lg: 20px;
            --radius-md: 14px;
            --shadow-card: 0 12px 34px rgba(15, 23, 42, 0.07);
            --shadow-soft: 0 8px 22px rgba(15, 23, 42, 0.045);
        }}

        html, body, .stApp, [class^="css"], [class*=" css"] {{
            font-family: {FONT_STACK};
            letter-spacing: 0 !important;
            color: var(--ink);
        }}

        .stApp {{
            background:
                radial-gradient(circle at 84% 8%, rgba(37, 99, 235, 0.06), transparent 28%),
                linear-gradient(180deg, #f8fbff 0%, #f3f7fc 45%, #eef4fb 100%);
        }}

        .block-container {{
            max-width: 1600px;
            padding: 1rem 1.55rem 2.5rem 11.7rem;
        }}

        #MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"],
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
            display: none !important;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
            height: 0;
        }}

        h1, h2, h3, h4, p, div, button, label, input {{
            font-family: {FONT_STACK} !important;
            letter-spacing: 0 !important;
        }}

        button, input, textarea, select {{
            font-variant-numeric: tabular-nums;
        }}

        .app-sidebar {{
            position: fixed;
            z-index: 100;
            top: 0;
            left: 0;
            width: 10.8rem;
            height: 100vh;
            padding: 1.1rem 0.75rem;
            background:
                linear-gradient(180deg, rgba(7, 21, 40, 0.98), rgba(8, 30, 53, 0.98)),
                var(--navy-950);
            color: #e5eefb;
            box-shadow: 8px 0 28px rgba(15, 23, 42, 0.18);
        }}

        .sidebar-brand {{
            height: 150px;
            display: grid;
            align-content: start;
            gap: 10px;
            padding: 0.65rem 0.45rem;
            border-bottom: 1px solid rgba(226, 232, 240, 0.13);
            margin-bottom: 0.85rem;
        }}

        .sidebar-title-card {{
            width: 100%;
            min-height: 116px;
            border-radius: 18px;
            display: grid;
            align-content: center;
            gap: 8px;
            padding: 14px 12px;
            border: 1px solid rgba(147, 197, 253, 0.30);
            background: linear-gradient(145deg, rgba(37, 99, 235, 0.18), rgba(15, 23, 42, 0.12));
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
        }}

        .sidebar-title-main {{
            color: #f8fbff;
            font-size: 19px;
            line-height: 1.28;
            font-weight: 930;
            word-break: keep-all;
        }}

        .sidebar-title-sub {{
            color: rgba(226, 232, 240, 0.74);
            font-size: 10px;
            line-height: 1.3;
            font-weight: 760;
            word-break: keep-all;
        }}

        .sidebar-title {{
            font-weight: 880;
            font-size: 17px;
            line-height: 1.25;
            word-break: keep-all;
        }}

        .sidebar-menu {{
            display: grid;
            gap: 0.35rem;
        }}

        .sidebar-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            height: 46px;
            padding: 0 0.65rem;
            border-radius: 10px;
            color: #cbd5e1 !important;
            text-decoration: none !important;
            font-weight: 730;
            font-size: 14px;
        }}

        .sidebar-item.active {{
            background: linear-gradient(135deg, #2f74e8, #1d4ed8);
            color: #fff !important;
            box-shadow: 0 12px 26px rgba(37, 99, 235, 0.28);
        }}

        .sidebar-item.disabled {{
            color: rgba(203, 213, 225, 0.48) !important;
            cursor: default;
        }}

        .sidebar-footer {{
            position: absolute;
            left: 1rem;
            right: 1rem;
            bottom: 1rem;
            color: rgba(226, 232, 240, 0.72);
            font-size: 12px;
            line-height: 1.55;
        }}

        .top-header {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) 390px 170px;
            gap: 14px;
            align-items: center;
            margin: 2px 0 12px;
        }}

        .title-wrap h1 {{
            font-size: clamp(25px, 2.4vw, 36px);
            line-height: 1.16;
            margin: 0;
            font-weight: 900;
            color: #071528;
            word-break: keep-all;
        }}

        .title-wrap p {{
            margin: 7px 0 0;
            color: var(--muted);
            font-size: 15px;
            font-weight: 620;
        }}

        .header-logo-panel {{
            width: min(100%, 980px);
            height: clamp(184px, 15vw, 270px);
            border-radius: 24px;
            display: grid;
            place-items: center;
            background: transparent;
            border: 0;
            box-shadow: none;
            overflow: hidden;
        }}

        .header-logo-panel img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 0;
            opacity: 1;
            display: block;
        }}

        .header-logo-caption {{
            margin-top: 8px;
            color: var(--muted);
            font-size: 14px;
            font-weight: 680;
        }}

        .top-note, .election-card {{
            min-height: 82px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.84);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-soft);
            padding: 14px 16px;
        }}

        .top-note {{
            display: grid;
            grid-template-columns: 26px 1fr;
            gap: 9px;
            color: #243041;
            font-size: 14px;
            line-height: 1.5;
            font-weight: 650;
        }}

        .note-icon {{
            width: 24px;
            height: 24px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: var(--blue-soft);
            color: var(--blue-dark);
            font-weight: 900;
            border: 1px solid #bfdbfe;
        }}

        .election-card {{
            text-align: center;
            display: grid;
            align-content: center;
            gap: 2px;
        }}

        .election-card .label {{
            color: var(--blue-dark);
            font-size: 13px;
            font-weight: 850;
        }}

        .election-card .dday {{
            color: var(--blue-dark);
            font-size: 18px;
            font-weight: 920;
        }}

        .election-card .date {{
            color: var(--ink);
            font-size: 15px;
            font-weight: 760;
        }}

        .top-tabs {{
            display: grid;
            grid-template-columns: repeat(5, minmax(118px, 1fr));
            gap: 4px;
            max-width: 760px;
            margin: 0 0 10px;
        }}

        .tab-link {{
            display: grid;
            place-items: center;
            height: 42px;
            border-bottom: 3px solid transparent;
            color: #334155 !important;
            text-decoration: none !important;
            font-size: 14px;
            font-weight: 820;
        }}

        .tab-link.active {{
            color: var(--blue-dark) !important;
            border-bottom-color: var(--blue-dark);
        }}

        .control-band {{
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.74);
            box-shadow: var(--shadow-soft);
            border-radius: var(--radius-md);
            padding: 12px 14px 8px;
            margin-bottom: 14px;
        }}

        .control-label {{
            color: #334155;
            font-size: 13px;
            font-weight: 850;
            margin-bottom: 6px;
        }}

        div[role="radiogroup"] {{
            gap: 0 !important;
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0;
            overflow: hidden;
            width: fit-content;
            box-shadow: none;
        }}

        div[role="radiogroup"] label {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 38px;
            min-width: 68px;
            padding: 0 14px !important;
            border-right: 1px solid var(--line);
            margin: 0 !important;
            text-align: center !important;
        }}

        div[role="radiogroup"] label p {{
            width: 100%;
            margin: 0 !important;
            text-align: center !important;
            font-weight: 810;
            font-size: 14px;
        }}

        div[role="radiogroup"] label:last-child {{
            border-right: 0;
        }}

        div[role="radiogroup"] label > div:first-child {{
            display: none;
        }}

        div[role="radiogroup"] label:has(input:checked) {{
            background: linear-gradient(135deg, #2f74e8, #1d4ed8);
            color: #fff !important;
        }}

        div[role="radiogroup"] label:has(input:checked) p {{
            color: #fff !important;
        }}

        .stButton > button {{
            min-height: 40px;
            border-radius: 10px;
            border: 1px solid var(--line);
            background: #fff;
            color: #0f172a;
            font-weight: 820;
            box-shadow: none;
            transition: all 0.15s ease;
        }}

        .stButton > button:hover {{
            border-color: #93c5fd;
            color: var(--blue-dark);
        }}

        .stButton > button[kind="primary"],
        .stButton > button[data-testid="stBaseButton-primary"] {{
            background: linear-gradient(135deg, #2f74e8, #1d4ed8) !important;
            border-color: #1d4ed8 !important;
            color: #fff !important;
        }}

        .section-title {{
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin: 16px 0 10px;
        }}

        .section-title h2 {{
            margin: 0;
            font-size: 21px;
            line-height: 1.22;
            color: #0f172a;
            font-weight: 900;
            word-break: keep-all;
        }}

        .section-title span {{
            color: var(--muted);
            font-size: 13px;
            font-weight: 620;
        }}

        .card {{
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--line);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-card);
            padding: 16px;
            text-align: left;
        }}

        .card.tight {{
            padding: 13px;
        }}

        .hero-card {{
            border-radius: var(--radius-lg);
            box-shadow: 0 16px 42px rgba(15, 23, 42, 0.08);
        }}

        .candidate-card {{
            display: grid;
            grid-template-columns: 112px minmax(0, 1fr);
            gap: 14px;
            min-height: 166px;
            align-items: start;
            overflow: hidden;
        }}

        .candidate-card.blue {{
            background: linear-gradient(135deg, #ffffff 0%, #f6faff 100%);
            border-color: #bfdbfe;
        }}

        .candidate-card.red {{
            background: linear-gradient(135deg, #ffffff 0%, #fff7f7 100%);
            border-color: #fecdd3;
        }}

        .candidate-photo-wrap {{
            width: 112px;
            height: 140px;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid var(--line);
            background: #f8fafc;
            align-self: start;
            justify-self: start;
            flex: 0 0 auto;
        }}

        .candidate-photo-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            object-position: center top;
            display: block;
        }}

        .candidate-name-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}

        .candidate-name {{
            font-size: 26px;
            line-height: 1.12;
            font-weight: 920;
            color: #071528;
        }}

        .candidate-profile-summary {{
            color: #475569;
            font-size: 12px;
            line-height: 1.5;
            font-weight: 700;
            margin: 8px 0 4px;
        }}

        .candidate-profile-grid {{
            grid-column: 1 / -1;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin-top: 12px;
        }}

        .candidate-profile-field {{
            min-width: 0;
            border: 1px solid rgba(203, 213, 225, 0.75);
            border-radius: 12px;
            background: rgba(248, 251, 255, 0.86);
            padding: 10px 11px;
        }}

        .candidate-profile-label {{
            color: var(--muted);
            font-size: 11px;
            font-weight: 900;
            margin-bottom: 6px;
        }}

        .candidate-profile-list {{
            display: grid;
            gap: 4px;
            color: #172033;
            font-size: 12px;
            line-height: 1.42;
            font-weight: 720;
        }}

        .observed-issue-panel {{
            margin-top: 10px;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: rgba(255,255,255,0.86);
            padding: 11px 12px;
        }}

        .observed-issue-title {{
            color: #334155;
            font-size: 12px;
            font-weight: 900;
            margin-bottom: 8px;
        }}

        .observed-issue-grid {{
            display: grid;
            gap: 6px;
        }}

        .observed-issue-item {{
            display: grid;
            grid-template-columns: 74px 1fr auto;
            gap: 8px;
            align-items: center;
            color: #172033;
            font-size: 12px;
            font-weight: 760;
        }}

        .observed-issue-track {{
            height: 8px;
            border-radius: 999px;
            background: #e2e8f0;
            overflow: hidden;
        }}

        .observed-issue-fill {{
            height: 100%;
            border-radius: 999px;
            background: var(--blue);
            width: var(--share);
        }}

        .observed-issue-panel.red .observed-issue-fill {{
            background: var(--red);
        }}

        .ai-briefing {{
            display: grid;
            gap: 12px;
        }}

        .briefing-lead {{
            color: #0f172a;
            font-size: 15px;
            line-height: 1.64;
            font-weight: 780;
        }}

        .briefing-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
        }}

        .briefing-point {{
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #f8fbff;
            padding: 10px 11px;
        }}

        .briefing-point-label {{
            color: var(--muted);
            font-size: 11px;
            font-weight: 900;
            margin-bottom: 5px;
        }}

        .briefing-point-body {{
            color: #172033;
            font-size: 12px;
            line-height: 1.55;
            font-weight: 720;
        }}

        .party-pill, .badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 24px;
            border-radius: 999px;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: 850;
            white-space: nowrap;
        }}

        .party-pill.blue, .badge.blue {{
            color: var(--blue-dark);
            background: #dbeafe;
            border: 1px solid #bfdbfe;
        }}

        .party-pill.red, .badge.red {{
            color: var(--red-dark);
            background: #fee2e2;
            border: 1px solid #fecaca;
        }}

        .badge.green {{
            color: var(--green-dark);
            background: var(--green-soft);
            border: 1px solid #bbf7d0;
        }}

        .badge.gray {{
            color: #475569;
            background: var(--gray-soft);
            border: 1px solid #e2e8f0;
        }}

        .badge.orange {{
            color: #c2410c;
            background: #fff7ed;
            border: 1px solid #fed7aa;
        }}

        .metric-row {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 8px;
            margin-top: 10px;
        }}

        .metric-label {{
            color: var(--muted);
            font-size: 12px;
            font-weight: 720;
            line-height: 1.35;
        }}

        .metric-value {{
            font-size: 19px;
            line-height: 1.1;
            font-weight: 930;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
            word-break: keep-all;
            color: #0f172a;
        }}

        .blue-text {{ color: var(--blue-dark); }}
        .red-text {{ color: var(--red-dark); }}
        .green-text {{ color: var(--green-dark); }}
        .muted-text {{ color: var(--muted); }}

        .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            margin-top: 10px;
        }}

        .chip {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
            line-height: 1;
            font-weight: 820;
            white-space: nowrap;
            border: 1px solid #e2e8f0;
            background: #fff;
            color: #334155;
        }}

        .chip.blue {{
            color: var(--blue-dark);
            background: var(--blue-soft);
            border-color: #bfdbfe;
        }}

        .chip.red {{
            color: var(--red-dark);
            background: var(--red-soft);
            border-color: #fecdd3;
        }}

        .chip.green {{
            color: var(--green-dark);
            background: var(--green-soft);
            border-color: #bbf7d0;
        }}

        .note-card, .warning-card {{
            border-radius: 14px;
            padding: 13px 15px;
            line-height: 1.6;
            font-size: 14px;
            font-weight: 650;
        }}

        .note-card {{
            border: 1px solid #bfdbfe;
            background: #f8fbff;
            color: #1e3a8a;
        }}

        .warning-card {{
            border: 1px solid #fecdd3;
            background: #fff7f7;
            color: #991b1b;
        }}

        .insight-card {{
            min-height: 166px;
            display: grid;
            align-content: center;
            text-align: center;
            border-color: #d7e6fb;
            background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
        }}

        .insight-kicker {{
            display: inline-flex;
            justify-self: center;
            align-items: center;
            gap: 6px;
            padding: 5px 9px;
            border-radius: 999px;
            background: var(--blue-soft);
            color: var(--blue-dark);
            font-size: 12px;
            font-weight: 850;
            margin-bottom: 8px;
        }}

        .insight-title {{
            font-size: 18px;
            font-weight: 900;
            line-height: 1.45;
            word-break: keep-all;
        }}

        .insight-body {{
            color: #475569;
            line-height: 1.55;
            font-size: 13px;
            margin-top: 8px;
        }}

        .issue-list {{
            display: grid;
            gap: 7px;
        }}

        .issue-link {{
            display: grid;
            grid-template-columns: 74px 1fr 54px;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #fff;
            color: #0f172a !important;
            text-decoration: none !important;
        }}

        .issue-link.active {{
            border-color: #93c5fd;
            background: linear-gradient(135deg, #f8fbff, #eff6ff);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.10);
        }}

        .issue-name {{
            font-size: 14px;
            font-weight: 880;
        }}

        .share-track {{
            height: 10px;
            border-radius: 999px;
            display: grid;
            grid-template-columns: var(--jwo) var(--osh);
            overflow: hidden;
            background: #e2e8f0;
        }}

        .share-blue {{
            background: linear-gradient(90deg, #60a5fa, #2563eb);
        }}

        .share-red {{
            background: linear-gradient(90deg, #fb7185, #ef3340);
        }}

        .issue-percent {{
            font-variant-numeric: tabular-nums;
            font-size: 12px;
            text-align: right;
            color: var(--muted);
            font-weight: 780;
        }}

        .keyword-cloud {{
            min-height: 202px;
            display: grid;
            place-items: center;
            position: relative;
            overflow: hidden;
            border-radius: 14px;
            border: 1px solid var(--line);
            background: #fff;
            padding: 16px;
        }}

        .keyword-cloud-inner {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            align-content: center;
            flex-wrap: wrap;
            gap: 10px 14px;
            text-align: center;
        }}

        .cloud-word {{
            display: inline-block;
            font-weight: 900;
            line-height: 1.05;
            border-radius: 999px;
            padding: 3px 5px;
        }}

        .cloud-word.active {{
            background: transparent;
            box-shadow: none;
            text-decoration: none !important;
            border-radius: 999px;
        }}

        .cloud-word.blue-text.active {{
            color: var(--blue-dark) !important;
        }}

        .cloud-word.red-text.active {{
            color: var(--red-dark) !important;
        }}

        .table-note {{
            color: var(--muted);
            font-size: 12px;
            line-height: 1.55;
            margin-top: 8px;
        }}

        .html-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 13px;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #fff;
        }}

        .html-table th {{
            background: #f8fafc;
            color: #475569;
            text-align: left;
            font-size: 12px;
            font-weight: 850;
            padding: 10px 11px;
            border-bottom: 1px solid var(--line);
            white-space: nowrap;
        }}

        .html-table td {{
            padding: 10px 11px;
            border-bottom: 1px solid #edf2f7;
            vertical-align: top;
            color: #172033;
            line-height: 1.45;
        }}

        .html-table tr:last-child td {{
            border-bottom: 0;
        }}

        .html-table tr:hover td {{
            background: #f8fbff;
        }}

        .html-table td:nth-child(2),
        .html-table th:nth-child(2) {{
            white-space: nowrap;
        }}

        .num {{
            text-align: right !important;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }}

        .mini-kpi {{
            border: 1px solid var(--line);
            background: #fff;
            border-radius: 14px;
            padding: 14px;
            box-shadow: var(--shadow-soft);
        }}

        .mini-kpi-title {{
            color: #334155;
            font-size: 13px;
            font-weight: 850;
            margin-bottom: 7px;
        }}

        .mini-kpi-value {{
            font-size: 25px;
            line-height: 1.08;
            font-weight: 930;
            font-variant-numeric: tabular-nums;
        }}

        .data-status-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-top: 12px;
        }}

        .data-status-item {{
            border: 1px solid var(--line);
            background: #f8fbff;
            border-radius: 12px;
            padding: 11px 12px;
            min-width: 0;
        }}

        .data-status-item.wide {{
            grid-column: 1 / -1;
        }}

        .data-status-label {{
            color: var(--muted);
            font-size: 11px;
            font-weight: 850;
            margin-bottom: 4px;
            white-space: nowrap;
        }}

        .data-status-value {{
            color: var(--ink);
            font-size: 15px;
            line-height: 1.45;
            font-weight: 760;
            overflow-wrap: anywhere;
        }}

        .data-status-value.strong {{
            font-size: 20px;
            font-weight: 940;
            font-variant-numeric: tabular-nums;
        }}

        .status-code {{
            display: inline-flex;
            max-width: 100%;
            border-radius: 999px;
            padding: 7px 10px;
            background: #ecfdf3;
            color: #15803d;
            border: 1px solid #bbf7d0;
            font-size: 13px;
            font-weight: 900;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }}

        .official-channel-strip {{
            margin-top: 10px;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: rgba(255,255,255,0.82);
            padding: 10px 12px;
        }}

        .official-channel-title {{
            color: var(--muted);
            font-size: 11px;
            font-weight: 850;
            margin-bottom: 7px;
        }}

        .official-channel-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .official-channel-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 28px;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid #dbe7f5;
            background: #fff;
            color: #334155 !important;
            font-size: 12px;
            font-weight: 820;
            line-height: 1;
            text-decoration: none !important;
            white-space: nowrap;
        }}

        .official-channel-link:hover {{
            border-color: #93c5fd;
            background: #f8fbff;
        }}

        .ethics-footer {{
            margin-top: 24px;
            border: 1px solid #cbdff6;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(248,251,255,0.94));
            box-shadow: var(--shadow-soft);
            padding: 17px 18px;
        }}

        .ethics-footer-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-top: 12px;
        }}

        .ethics-footer-item {{
            border: 1px solid var(--line);
            border-radius: 13px;
            background: #fff;
            padding: 12px;
        }}

        .ethics-footer-item h3 {{
            margin: 0 0 7px;
            color: #1e3a8a;
            font-size: 13px;
            font-weight: 920;
        }}

        .ethics-footer-item p {{
            margin: 0;
            color: #475569;
            font-size: 12px;
            line-height: 1.58;
            font-weight: 670;
        }}

        .stDataFrame {{
            border-radius: 14px;
            overflow: hidden;
        }}

        @media (max-width: 1100px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            .app-sidebar {{
                position: relative;
                width: auto;
                height: auto;
                border-radius: 16px;
                margin-bottom: 12px;
            }}
            .sidebar-brand {{
                height: auto;
            }}
            .sidebar-footer {{
                position: static;
                margin-top: 12px;
            }}
            .sidebar-menu {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .top-header {{
                grid-template-columns: 1fr;
            }}
            .top-tabs {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
                max-width: none;
            }}
            .candidate-card {{
                grid-template-columns: 98px minmax(0, 1fr);
            }}
            .candidate-photo-wrap {{
                width: 98px;
                height: 124px;
            }}
            .metric-row, .summary-grid {{
                grid-template-columns: 1fr;
            }}
            .candidate-profile-grid, .briefing-grid, .ethics-footer-grid {{
                grid-template-columns: 1fr;
            }}
            .issue-link {{
                grid-template-columns: 68px 1fr 48px;
            }}
        }}

        @media (max-width: 640px) {{
            .block-container {{
                padding-top: 0.6rem;
            }}
            .title-wrap h1 {{
                font-size: 28px;
            }}
            .candidate-card {{
                grid-template-columns: 88px minmax(0, 1fr);
            }}
            .candidate-photo-wrap {{
                width: 88px;
                height: 112px;
            }}
            .section-title {{
                display: block;
            }}
            .section-title span {{
                display: block;
                margin-top: 4px;
            }}
            .html-table {{
                font-size: 12px;
            }}
            .html-table th, .html-table td {{
                padding: 8px 7px;
            }}
            .data-status-grid {{
                grid-template-columns: 1fr;
            }}
            .data-status-item.wide {{
                grid-column: auto;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def image_data_uri(path: Path | str | None) -> str:
    if not path:
        return ""
    image_path = Path(path)
    if not image_path.exists():
        return ""
    suffix = image_path.suffix.lower().lstrip(".")
    if suffix in {"jpg", "jpeg"}:
        mime = "jpeg"
    elif suffix == "svg":
        mime = "svg+xml"
    else:
        mime = suffix
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def page_url(page: str, issue: str | None = None) -> str:
    url = f"/?page={quote(page)}"
    if issue:
        url += f"&issue={quote(issue)}"
    return url


def render_sidebar(page: str) -> None:
    st.markdown(
        f"""
        <aside class="app-sidebar">
            <div class="sidebar-brand">
                <div class="sidebar-title-card">
                    <div class="sidebar-title-main">서울시장 선거<br/>여론 모니터</div>
                    <div class="sidebar-title-sub">공개 온라인 반응<br/>대시보드</div>
                </div>
            </div>
            <div class="sidebar-footer">
                서울특별시<br/>여론 모니터링 서비스<br/>Ver. 1.0.0
            </div>
        </aside>
        """,
        unsafe_allow_html=True,
    )


def render_header(page: str) -> None:
    logo_uri = image_data_uri(BRAND_LOGO)
    logo_html = f'<img src="{logo_uri}" alt="Seoul Online Issue Radar logo" />' if logo_uri else '<h1>서울시장 선거 여론 모니터</h1>'
    tabs = [
        ("종합 요약", "home"),
        ("쟁점 상세 분석", "candidate"),
        ("전체 흐름·출처", "trend"),
        ("반응 분위기 추이", "evidence"),
        ("근거·데이터 안내", "evidence_data"),
    ]
    tab_html = "".join(
        f'<a class="tab-link{" active" if page == key else ""}" href="{page_url(key)}" target="_self">{label}</a>' for label, key in tabs
    )
    st.markdown(
        f"""
        <div class="top-header">
            <div class="title-wrap">
                <div class="header-logo-panel">{logo_html}</div>
                <div class="header-logo-caption">공개 온라인 반응으로 보는 두 후보 비교와 주요 쟁점 흐름</div>
            </div>
            <div class="top-note">
                <div class="note-icon">i</div>
                <div>{DEMO_WARNING}</div>
            </div>
            <div class="election-card">
                <div class="label">서울시장 선거</div>
                <div class="dday">D-22</div>
                <div class="date">2026.06.03 (수)</div>
            </div>
        </div>
        <div class="top-tabs">{tab_html}</div>
        """,
        unsafe_allow_html=True,
    )


def render_period_controls() -> tuple[str, dict]:
    if "selected_period" not in st.session_state:
        st.session_state.selected_period = "7d"

    current_key = st.session_state.selected_period
    ctx = period_context(current_key)
    current_range = st.session_state.get("selected_date_range", (ctx["start"].date(), ctx["end"].date()))
    if not isinstance(current_range, tuple) or len(current_range) != 2:
        current_range = (ctx["start"].date(), ctx["end"].date())
    if "period_start_date_input" not in st.session_state:
        st.session_state.period_start_date_input = current_range[0]
    if "period_end_date_input" not in st.session_state:
        st.session_state.period_end_date_input = current_range[1]

    def _clamp_input_date(value) -> object:
        date = pd.to_datetime(value).date()
        return min(max(date, DATA_START.date()), DATA_END.date())

    def _period_key_for_range(start_date, end_date) -> str:
        range_key = make_range_period_key(start_date, end_date)
        for key, option in PERIOD_OPTIONS.items():
            option_end = period_context(key)["end"].date()
            option_start = max(pd.to_datetime(end_date) - pd.Timedelta(days=option["days"] - 1), DATA_START).date()
            if start_date == option_start and end_date == option_end:
                return key
        return range_key

    def _commit_period_range(start_date, end_date) -> None:
        start_date = _clamp_input_date(start_date)
        end_date = _clamp_input_date(end_date)
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        st.session_state.selected_date_range = (start_date, end_date)
        st.session_state.selected_period = _period_key_for_range(start_date, end_date)

    def _sync_manual_period() -> None:
        start_date = _clamp_input_date(st.session_state.period_start_date_input)
        end_date = _clamp_input_date(st.session_state.period_end_date_input)
        if start_date > end_date:
            start_date, end_date = end_date, start_date
            st.session_state.period_start_date_input = start_date
            st.session_state.period_end_date_input = end_date
        _commit_period_range(start_date, end_date)

    def _apply_quick_period(key: str) -> None:
        end_date = _clamp_input_date(st.session_state.get("period_end_date_input", current_range[1]))
        days = PERIOD_OPTIONS[key]["days"]
        start_date = max(pd.to_datetime(end_date) - pd.Timedelta(days=days - 1), DATA_START).date()
        st.session_state.period_start_date_input = start_date
        st.session_state.period_end_date_input = end_date
        _commit_period_range(start_date, end_date)

    _commit_period_range(st.session_state.period_start_date_input, st.session_state.period_end_date_input)
    selected_start, selected_end = st.session_state.selected_date_range
    selected_days = int((pd.to_datetime(selected_end) - pd.to_datetime(selected_start)).days) + 1
    active_quick_key = next(
        (key for key, option in PERIOD_OPTIONS.items() if selected_days == option["days"]),
        None,
    )

    with st.container():
        cols = st.columns([0.43, 0.34, 0.23], gap="small")
        with cols[0]:
            st.markdown('<div class="control-label">분석 기간</div>', unsafe_allow_html=True)
            date_cols = st.columns(2, gap="small")
            with date_cols[0]:
                st.date_input(
                    "시작일",
                    min_value=DATA_START.date(),
                    max_value=DATA_END.date(),
                    format="YYYY.MM.DD",
                    key="period_start_date_input",
                    on_change=_sync_manual_period,
                )
            with date_cols[1]:
                st.date_input(
                    "종료일",
                    min_value=DATA_START.date(),
                    max_value=DATA_END.date(),
                    format="YYYY.MM.DD",
                    key="period_end_date_input",
                    on_change=_sync_manual_period,
                )
            _commit_period_range(st.session_state.period_start_date_input, st.session_state.period_end_date_input)

        with cols[1]:
            st.markdown('<div class="control-label">기간 선택</div>', unsafe_allow_html=True)
            button_cols = st.columns(3, gap="small")
            for button_col, key in zip(button_cols, PERIOD_OPTIONS):
                with button_col:
                    st.button(
                        PERIOD_OPTIONS[key]["label"],
                        key=f"period_quick_{key}",
                        type="primary" if active_quick_key == key else "secondary",
                        width="stretch",
                        on_click=_apply_quick_period,
                        args=(key,),
                    )

        selected = st.session_state.selected_period
        ctx = period_context(selected)
        with cols[2]:
            st.markdown('<div class="control-label">데이터 기준</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="table-note" style="margin-top:9px;">{ctx["range_text"]}<br/>공개 온라인 반응 기준</div>',
                unsafe_allow_html=True,
            )
    return selected, ctx


def section_title(title: str, caption: str | None = None) -> None:
    caption_html = f"<span>{escape(caption)}</span>" if caption else ""
    st.markdown(f'<div class="section-title"><h2>{escape(title)}</h2>{caption_html}</div>', unsafe_allow_html=True)


def notice(text: str, tone: str = "blue") -> None:
    cls = "warning-card" if tone == "warning" else "note-card"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def demo_notice() -> None:
    notice(DEMO_WARNING, "warning")


def metric_explainer(compact: bool = False) -> None:
    body = (
        "반응량은 선택 기간에 관측된 공개 온라인 반응 건수입니다. "
        "기간 변동은 선택 기간 시작일 대비 종료일의 반응량 변화율입니다. "
        "반응점수는 공개 온라인 반응량, 출처 다양성, 이슈 집중도, 최근 급등성을 합성한 데모 지표입니다. "
        "실제 지지율이나 선거 예측 지표가 아닙니다."
    )
    if compact:
        body = (
            "반응량은 공개 온라인 반응 건수이고, 기간 변동은 선택 기간 시작일 대비 종료일의 반응량 변화율입니다. "
            "반응점수는 공개 온라인 반응량, 출처 다양성, 이슈 집중도, 최근 급등성을 합성한 데모 지표입니다. "
            "실제 지지율이나 선거 예측 지표가 아닙니다."
        )
    st.markdown(f'<div class="note-card">{body}</div>', unsafe_allow_html=True)


def chip_list(items: list[str], tone: str = "blue", limit: int | None = None) -> str:
    values = items[:limit] if limit else items
    return '<div class="chip-row">' + "".join(f'<span class="chip {tone}">{escape(str(item))}</span>' for item in values) + "</div>"


def _pipe_items(value: object, limit: int | None = None) -> list[str]:
    if pd.isna(value):
        return []
    items = [item.strip() for item in str(value).split("|") if item.strip()]
    return items[:limit] if limit else items


def _candidate_profile_field(label: str, items: list[str]) -> str:
    if not items:
        return ""
    body = "".join(f"<div>{escape(item)}</div>" for item in items)
    return (
        '<div class="candidate-profile-field">'
        f'<div class="candidate-profile-label">{escape(label)}</div>'
        f'<div class="candidate-profile-list">{body}</div>'
        "</div>"
    )


def candidate_card(row: pd.Series, compact: bool = False) -> str:
    candidate = str(row["candidate"])
    tone = "blue" if candidate == "정원오" else "red"
    image_uri = image_data_uri(get_candidate_image(candidate))
    image_html = f'<img src="{image_uri}" alt="{escape(candidate)} 사진" />' if image_uri else ""
    score = f"{float(row['reaction_score']):.1f}"
    change = format_percent(row["period_change"], signed=True)
    mentions = format_number(row["mention_count"])
    keywords = row.get("top_keywords", [])
    keyword_html = chip_list(list(keywords), tone, 5)
    if compact:
        keyword_html = chip_list(list(keywords), tone, 3)
    profile_html = ""
    if not compact:
        summary = str(row.get("profile_summary", "") or "")
        fields = [
            _candidate_profile_field("학력", _pipe_items(row.get("education"), 2)),
            _candidate_profile_field("경력", _pipe_items(row.get("career"), 3)),
            _candidate_profile_field("주요 공약", _pipe_items(row.get("main_pledges"), 4)),
        ]
        profile_html = (
            f'<div class="candidate-profile-summary">{escape(summary)}</div>'
            f'<div class="candidate-profile-grid">{"".join(field for field in fields if field)}</div>'
        )
    return f"""
    <div class="card hero-card candidate-card {tone}">
        <div class="candidate-photo-wrap">{image_html}</div>
        <div>
            <div class="candidate-name-row">
                <span class="candidate-name">{escape(candidate)}</span>
                <span class="party-pill {tone}">{escape(str(row['party']))}</span>
            </div>
            <div class="metric-row">
                <div>
                    <div class="metric-label">반응점수</div>
                    <div class="metric-value {tone}-text">{score}<span style="font-size:13px; color:#64748b;"> /100</span></div>
                </div>
                <div>
                    <div class="metric-label">기간 변동</div>
                    <div class="metric-value {tone}-text" style="font-size:17px;">{change}</div>
                </div>
                <div>
                    <div class="metric-label">언급량</div>
                    <div class="metric-value" style="font-size:17px;">{mentions}<span style="font-size:11px;"> 건</span></div>
                </div>
            </div>
            <div class="metric-label" style="margin-top:10px;">주요 연관 키워드</div>
            {keyword_html}
        </div>
        {profile_html}
    </div>
    """


def candidate_observed_issue_panel(row: pd.Series, issue_summary: pd.DataFrame) -> str:
    candidate = str(row["candidate"])
    tone = "blue" if candidate == "정원오" else "red"
    issues = _pipe_items(row.get("persistent_issues"), 5)
    if not issues:
        return ""
    indexed = issue_summary.set_index("issue") if not issue_summary.empty else pd.DataFrame()
    rows = []
    for issue in issues:
        if issue in indexed.index:
            share = float(indexed.loc[issue, f"{candidate}_share"])
            count = int(indexed.loc[issue, candidate])
            count_text = f"{format_number(count)}건"
        else:
            share = 0.0
            count_text = "0건"
        rows.append(
            '<div class="observed-issue-item">'
            f"<div>{escape(issue)}</div>"
            f'<div class="observed-issue-track"><div class="observed-issue-fill" style="--share:{share:.1f}%;"></div></div>'
            f"<div>{share:.1f}% · {count_text}</div>"
            "</div>"
        )
    return f"""
    <div class="observed-issue-panel {tone}">
        <div class="observed-issue-title">{escape(candidate)} 지속 관측 이슈</div>
        <div class="observed-issue-grid">{"".join(rows)}</div>
        <div class="table-note">선택 기간 동안 반복적으로 관측되는 공개 온라인 반응 쟁점입니다. 후보 선호도나 선거 예측 지표가 아닙니다.</div>
    </div>
    """


def issue_insight(issue: str, issue_summary: pd.DataFrame) -> str:
    row = issue_summary[issue_summary["issue"].eq(issue)]
    if row.empty:
        return f"""
        <div class="card insight-card">
            <div class="insight-kicker">현재 쟁점: {escape(issue)}</div>
            <div class="insight-title">선택한 쟁점의 공개 온라인 반응을 확인합니다.</div>
        </div>
        """
    data = row.iloc[0]
    jwo = float(data.get("정원오_share", 0))
    osh = float(data.get("오세훈_share", 0))
    if abs(jwo - osh) < 3:
        title = f"{issue} 쟁점에서 두 후보의 공개 온라인 반응 비중이 유사합니다."
        stance = "양측 유사"
    elif jwo > osh:
        title = f"{issue} 쟁점에서 정원오 후보가 공개 온라인 반응량 기준 상대적으로 많이 언급됩니다."
        stance = "정원오 상대 언급 많음"
    else:
        title = f"{issue} 쟁점에서 오세훈 후보가 공개 온라인 반응량 기준 상대적으로 많이 언급됩니다."
        stance = "오세훈 상대 언급 많음"
    return f"""
    <div class="card insight-card">
        <div class="insight-kicker">현재 쟁점: {escape(issue)}</div>
        <div class="insight-title">{escape(title)}</div>
        <div class="chip-row" style="justify-content:center;"><span class="chip blue">정원오 {jwo:.1f}%</span><span class="chip red">오세훈 {osh:.1f}%</span><span class="chip gray">{escape(stance)}</span></div>
    </div>
    """


def issue_selector(issue_summary: pd.DataFrame, selected_issue: str, page: str = "candidate") -> None:
    rows = []
    data = issue_summary.set_index("issue") if not issue_summary.empty else pd.DataFrame()
    for issue in ISSUE_ORDER:
        if issue in data.index:
            jwo = float(data.loc[issue, "정원오_share"])
            osh = float(data.loc[issue, "오세훈_share"])
            total = format_number(data.loc[issue, "total"])
        else:
            jwo, osh, total = 50.0, 50.0, "0"
        active = " active" if issue == selected_issue else ""
        rows.append(
            f'<a class="issue-link{active}" href="{page_url(page, issue)}" target="_self">'
            f'<div class="issue-name">{escape(issue)}</div>'
            f'<div class="share-track" style="--jwo:{jwo}%; --osh:{osh}%;">'
            f'<div class="share-blue"></div><div class="share-red"></div></div>'
            f'<div class="issue-percent">{jwo:.0f}/{osh:.0f}</div></a>'
            f'<div class="table-note" style="margin:-5px 4px 2px;">반응량 {total}건 · 공개 온라인 반응 비중</div>'
        )
    st.markdown(f'<div class="issue-list">{"".join(rows)}</div>', unsafe_allow_html=True)


def keyword_cloud(keywords: pd.DataFrame, candidate: str, issue: str) -> str:
    tone = "blue" if candidate == "정원오" else "red"
    data = keywords[keywords["candidate"].eq(candidate)].copy()
    if data.empty:
        return '<div class="keyword-cloud"><div class="table-note">표시할 연관 키워드가 없습니다.</div></div>'
    max_count = max(1, data["mention_count"].max())
    words = []
    for idx, (_, row) in enumerate(data.sort_values("mention_count", ascending=False).head(12).iterrows()):
        importance = float(row["mention_count"]) / max_count
        size = 13 + importance * 20
        opacity = 0.62 + importance * 0.38
        active = " active" if row["issue"] == issue else ""
        order = 0 if idx < 2 else idx + 1
        words.append(
            f'<span class="cloud-word {tone}-text{active}" style="font-size:{size:.0f}px; opacity:{opacity:.2f}; order:{order};">{escape(str(row["keyword"]))}</span>'
        )
    return f'<div class="keyword-cloud"><div class="keyword-cloud-inner">{"".join(words)}</div></div>'


def filter_row(prefix: str, issue: str | None = None) -> tuple[str, str]:
    source_key = f"selected_source_for_{prefix}"
    metric_key = f"selected_metric_for_{prefix}"
    if source_key not in st.session_state:
        st.session_state[source_key] = "전체"
    if metric_key not in st.session_state:
        st.session_state[metric_key] = "반응량"
    cols = st.columns([0.42, 0.42, 0.16], gap="small")
    with cols[0]:
        st.markdown('<div class="control-label">출처 필터</div>', unsafe_allow_html=True)
        source = st.radio(
            "출처 필터",
            list(SOURCE_OPTIONS.keys()),
            format_func=lambda key: SOURCE_OPTIONS[key],
            horizontal=True,
            key=source_key,
            label_visibility="collapsed",
        )
    with cols[1]:
        st.markdown('<div class="control-label">지표 선택</div>', unsafe_allow_html=True)
        metric = st.radio("지표 선택", METRIC_OPTIONS, horizontal=True, key=metric_key, label_visibility="collapsed")
    with cols[2]:
        st.markdown('<div class="control-label">현재 선택</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="table-note" style="margin-top:8px;">{escape(issue or "전체 쟁점")} 기준<br/>아래 카드·표가 함께 갱신됩니다.</div>',
            unsafe_allow_html=True,
        )
    return source, metric


def styled_plotly(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=38, b=28),
        font=dict(family=FONT_STACK, size=12, color="#334155"),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0", tickfont=dict(color="#475569"))
    fig.update_yaxes(gridcolor="#edf2f7", zerolinecolor="#e2e8f0", tickfont=dict(color="#475569"))
    return fig


def metric_card(title: str, value: str, caption: str = "", tone: str = "") -> str:
    tone_class = f"{tone}-text" if tone else ""
    return (
        '<div class="mini-kpi">'
        f'<div class="mini-kpi-title">{escape(title)}</div>'
        f'<div class="mini-kpi-value {tone_class}">{escape(value)}</div>'
        f'<div class="table-note">{escape(caption)}</div>'
        '</div>'
    )


def collection_status_card(status: dict, context: dict, title: str = "데이터 현황", note: str | None = None) -> str:
    updated_at = pd.to_datetime(status.get("updated_at"), errors="coerce")
    updated_text = updated_at.strftime("%Y.%m.%d %H:%M") if pd.notna(updated_at) else str(status.get("updated_at", "-"))
    source_scope = str(status.get("source_scope", "-")).replace("공개 ", "")
    status_code = str(status.get("collection_status", "-"))
    status_label = {
        "mock_seed_from_public_clues": "근거 기반 임시 seed",
        "public_online_reaction_demo_seed": "공개 온라인 반응 데모 seed",
    }.get(status_code, status_code.replace("_", " "))
    note_text = note or "수집 현황은 mock data 기준이며 선택한 분석 기간에 맞춰 갱신됩니다."
    return f"""
    <div class="card">
        <div class="section-title" style="margin-top:0"><h2>{escape(title)}</h2></div>
        <div class="status-code">{escape(status_label)}</div>
        <div class="data-status-grid">
            <div class="data-status-item">
                <div class="data-status-label">수집 기간</div>
                <div class="data-status-value">{escape(str(context["range_text"]))}</div>
            </div>
            <div class="data-status-item">
                <div class="data-status-label">반응량 합계</div>
                <div class="data-status-value strong">{format_number(status.get("total_items", 0))}건</div>
            </div>
            <div class="data-status-item">
                <div class="data-status-label">마지막 업데이트</div>
                <div class="data-status-value">{escape(updated_text)}</div>
            </div>
            <div class="data-status-item">
                <div class="data-status-label">데이터 기준</div>
                <div class="data-status-value">공개 온라인 반응</div>
            </div>
            <div class="data-status-item wide">
                <div class="data-status-label">수집 출처</div>
                <div class="data-status-value">{escape(source_scope)}</div>
            </div>
        </div>
        <div class="table-note" style="margin-top:10px;">{escape(note_text)}</div>
    </div>
    """


def data_ethics_footer(context: dict) -> None:
    range_text = escape(str(context.get("range_text", "선택 기간")))
    html = f"""
    <div class="ethics-footer">
        <div class="section-title" style="margin-top:0">
            <h2>데이터·윤리 안내</h2>
            <span>{range_text} 기준 · 공개 온라인 반응 데모 화면</span>
        </div>
        <div class="ethics-footer-grid">
            <div class="ethics-footer-item">
                <h3>데이터 성격</h3>
                <p>현재 수치는 실제 수집 DB가 아니라 공개 단서 기반 mock/seed data입니다. 실제 지지율·득표율·선거 결과 예측으로 해석하지 않습니다.</p>
            </div>
            <div class="ethics-footer-item">
                <h3>포함 범위</h3>
                <p>공개 뉴스, 공개 영상·게시글, 공개 댓글, 공개 커뮤니티/X 반응을 가정합니다. 비공개 계정, 비공개 카페, 실제 여론조사는 제외합니다.</p>
            </div>
            <div class="ethics-footer-item">
                <h3>분류 원칙</h3>
                <p>반응 분위기는 공개 텍스트를 우호 표현, 중립 표현, 비판 표현으로 나눈 데모 분류입니다. 풍자, 중의적 표현, 반복 게시물은 오분류 가능성이 있습니다.</p>
            </div>
            <div class="ethics-footer-item">
                <h3>사용자 유의</h3>
                <p>후보 비교는 공개 온라인 반응량과 쟁점 흐름을 설명하기 위한 것입니다. 성별·연령·지역 유권자 분포, 당선 가능성, 득표율 예측은 제공하지 않습니다.</p>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_change_table(frame: pd.DataFrame, limit: int = 7) -> None:
    display = frame.tail(limit).copy()
    rows = []
    for _, row in display.iterrows():
        rows.append(
            f'<tr><td>{short_date_text(row["날짜"])}</td>'
            f'<td class="num blue-text">{format_number(row["정원오 반응량"])}</td>'
            f'<td class="num red-text">{format_number(row["오세훈 반응량"])}</td>'
            f'<td class="num green-text">{row["우호 표현 비중"]:.1f}%</td>'
            f'<td class="num muted-text">{row["중립 표현 비중"]:.1f}%</td>'
            f'<td class="num red-text">{row["비판 표현 비중"]:.1f}%</td>'
            f'<td>{escape(str(row["주요 연관 키워드"]))}</td></tr>'
        )
    html = (
        '<table class="html-table"><thead><tr>'
        '<th>날짜</th><th class="num">정원오 반응량</th><th class="num">오세훈 반응량</th>'
        '<th class="num">우호 표현</th><th class="num">중립 표현</th><th class="num">비판 표현</th>'
        '<th>주요 연관 키워드</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_keyword_timeseries_table(frame: pd.DataFrame, keyword: str, limit: int = 60) -> None:
    if frame.empty:
        notice(f"'{keyword}' 키워드에 해당하는 데모 시계열이 없습니다. 다른 연관 키워드로 다시 확인해 주세요.", "warning")
        return

    display = frame.copy()
    display["candidate_order"] = display["candidate"].map({name: idx for idx, name in enumerate(CANDIDATE_ORDER)}).fillna(99)
    display = display.sort_values(["date", "candidate_order"]).tail(limit)
    rows = []
    for _, row in display.iterrows():
        tone = "blue" if row["candidate"] == "정원오" else "red"
        rows.append(
            f'<tr><td>{short_date_text(row["date"])}</td>'
            f'<td><span class="badge {tone}">{escape(str(row["candidate"]))}</span></td>'
            f'<td class="num {tone}-text">{format_number(row["keyword_mention_count"])}</td>'
            f'<td class="num green-text">{format_number(row["favorable_count"])} / {row["favorable_ratio"]:.1f}%</td>'
            f'<td class="num muted-text">{format_number(row["neutral_count"])} / {row["neutral_ratio"]:.1f}%</td>'
            f'<td class="num red-text">{format_number(row["critical_count"])} / {row["critical_ratio"]:.1f}%</td>'
            f'<td class="num">{format_percent(row["daily_change"], signed=True)}</td>'
            f'<td>{escape(str(row["matched_keywords"]))}</td></tr>'
        )
    html = (
        '<table class="html-table"><thead><tr>'
        '<th>날짜</th><th>후보</th><th class="num">키워드 언급량</th>'
        '<th class="num">우호 표현</th><th class="num">중립 표현</th><th class="num">비판 표현</th>'
        '<th class="num">전일 대비</th><th>매칭 키워드</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
        '<div class="table-note">키워드 언급량과 반응 분위기 수치는 공개 온라인 반응 데모용 seed data에서 추정한 값입니다.</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def reaction_badge(reaction_type: str) -> str:
    tone = {"우호": "green", "중립": "gray", "비판": "orange"}.get(reaction_type, "gray")
    return f'<span class="badge {tone}">{escape(reaction_type)}</span>'


def source_badge(source_label: str) -> str:
    return f'<span class="badge blue">{escape(source_label)}</span>'


def render_evidence_table(frame: pd.DataFrame, limit: int = 8, include_issue: bool = True) -> None:
    display = frame.head(limit).copy()
    if display.empty:
        notice("선택한 조건에 해당하는 데모 근거 샘플이 없습니다. 필터를 넓혀 다시 확인해 주세요.", "warning")
        return
    rows = []
    for _, row in display.iterrows():
        issue_cell = f"<td>{escape(str(row['issue']))}</td>" if include_issue else ""
        rows.append(
            f'<tr><td>{source_badge(str(row["source_label"]))}</td>'
            f'<td>{escape(str(row["candidate"]))}</td>'
            f'<td>{reaction_badge(str(row["reaction_type"]))}</td>'
            f'{issue_cell}'
            f'<td><b>{escape(str(row["title"]))}</b><br/><span class="muted-text">{escape(str(row["summary"]))}</span></td>'
            f'<td class="num">{format_number(row["count"])}</td>'
            f'<td>{pd.to_datetime(row["datetime"]).strftime("%Y.%m.%d %H:%M")}</td></tr>'
        )
    issue_header = "<th>쟁점</th>" if include_issue else ""
    html = (
        '<table class="html-table"><thead><tr>'
        f'<th>출처</th><th>후보</th><th>반응 유형</th>{issue_header}'
        '<th>제목/내용 요약</th><th class="num">반응량</th><th>시간</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )
    st.markdown(html, unsafe_allow_html=True)


def demo_link_notice_button(key: str = "demo_link_notice") -> None:
    if st.button("관련 원문 보기 안내", key=key, width="stretch"):
        st.toast("이 항목은 데모 데이터입니다. 실제 원문 링크는 제공하지 않습니다.")
        st.info("이 항목은 데모 데이터입니다. 실제 원문 링크는 제공하지 않습니다.")


def official_channel_buttons(channels: pd.DataFrame, candidate: str) -> None:
    data = channels[channels["candidate"].eq(candidate)]
    cols = st.columns(max(1, len(data)), gap="small")
    for col, (_, row) in zip(cols, data.iterrows()):
        with col:
            st.link_button(str(row["channel"]), str(row["url"]), width="stretch")


def official_channel_strip(channels: pd.DataFrame, candidate: str) -> str:
    data = channels[channels["candidate"].eq(candidate)]
    if data.empty:
        return ""
    links = "".join(
        f'<a class="official-channel-link" href="{escape(str(row["url"]), quote=True)}" target="_blank" rel="noopener noreferrer">{escape(str(row["channel"]))}</a>'
        for _, row in data.iterrows()
    )
    return f"""
    <div class="official-channel-strip">
        <div class="official-channel-title">{escape(candidate)} 공식 채널</div>
        <div class="official-channel-links">{links}</div>
    </div>
    """


def rank_badge(value: int | float) -> str:
    number = int(value)
    if number > 0:
        return f'<span class="green-text" style="font-weight:850;">▲ {number}</span>'
    if number < 0:
        return f'<span class="red-text" style="font-weight:850;">▼ {abs(number)}</span>'
    return '<span class="muted-text" style="font-weight:760;">-</span>'


def render_keyword_rank_table(keywords: pd.DataFrame, candidate: str, limit: int = 7) -> None:
    data = keywords[keywords["candidate"].eq(candidate)].head(limit)
    rows = []
    for _, row in data.iterrows():
        rows.append(
            f'<tr><td>{int(row["rank"])}</td>'
            f'<td><b>{escape(str(row["keyword"]))}</b></td>'
            f'<td>{escape(str(row["issue"]))}</td>'
            f'<td class="num">{format_number(row["mention_count"])}</td>'
            f'<td class="num">{rank_badge(row["rank_change"])}</td></tr>'
        )
    html = (
        '<table class="html-table">'
        '<thead><tr><th>순위</th><th>연관 키워드</th><th>쟁점</th><th class="num">언급량</th><th class="num">변동</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )
    st.markdown(html, unsafe_allow_html=True)


def selected_issue_from_query(default: str = "교통") -> str:
    issue = st.query_params.get("issue") or st.session_state.get("selected_issue", default)
    if issue not in ISSUE_ORDER:
        issue = default
    st.session_state.selected_issue = issue
    return issue


def source_code(label_or_code: str) -> str:
    if label_or_code == "전체":
        return "전체"
    return label_or_code


def selected_evidence_filters() -> tuple[str, str, str]:
    if "selected_candidate_for_table" not in st.session_state:
        st.session_state.selected_candidate_for_table = "전체"
    if "selected_reaction_type_for_evidence" not in st.session_state:
        st.session_state.selected_reaction_type_for_evidence = "전체"
    if "selected_sort_for_evidence" not in st.session_state:
        st.session_state.selected_sort_for_evidence = "최신순"
    cols = st.columns([0.28, 0.28, 0.28, 0.16], gap="small")
    with cols[0]:
        candidate = st.selectbox("후보", ["전체", *CANDIDATE_ORDER], key="selected_candidate_for_table")
    with cols[1]:
        reaction_type = st.selectbox("반응 유형", REACTION_TYPES, key="selected_reaction_type_for_evidence")
    with cols[2]:
        sort = st.selectbox("정렬", ["최신순", "반응 많은 순"], key="selected_sort_for_evidence")
    with cols[3]:
        st.markdown('<div class="table-note" style="margin-top:28px;">근거 샘플 표만 갱신</div>', unsafe_allow_html=True)
    return candidate, reaction_type, sort
