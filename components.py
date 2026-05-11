from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import CANDIDATE_COLORS, CANDIDATE_IMAGES, CANDIDATE_NAMES, OFFICIAL_CHANNELS, format_number


FONT_STACK = "'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        :root {{
            --blue: #2563eb;
            --blue-dark: #1d4ed8;
            --blue-soft: #eef5ff;
            --red: #ef3340;
            --red-dark: #dc2626;
            --red-soft: #fff1f2;
            --ink: #111827;
            --muted: #64748b;
            --line: #dbe3ef;
            --surface: #ffffff;
            --soft: #f8fafc;
        }}

        html, body, .stApp, [class^="css"], [class*=" css"] {{
            font-family: {FONT_STACK};
            letter-spacing: 0;
        }}

        .stApp {{
            background:
                linear-gradient(180deg, #ffffff 0%, #f8fafc 42%, #f7faff 100%);
            color: var(--ink);
        }}

        .block-container {{
            max-width: 1540px;
            padding: 1rem 1.5rem 2.5rem;
        }}

        #MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"],
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
            display: none !important;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
            height: 0;
        }}

        h1, h2, h3, h4, p, span, div, button, label {{
            font-family: {FONT_STACK} !important;
            letter-spacing: 0 !important;
        }}

        .top-shell {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 18px;
            border-bottom: 1px solid var(--line);
            padding: 8px 0 18px;
            margin-bottom: 10px;
        }}

        .brand-wrap {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex: 1;
            min-width: 0;
        }}

        .logo-mark {{
            width: 58px;
            height: 58px;
            border-radius: 16px;
            background: linear-gradient(135deg, #eaf2ff, #ffffff);
            border: 1px solid #bfdbfe;
            display: grid;
            place-items: center;
            color: var(--blue);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.11);
        }}

        .logo-mark svg {{
            width: 36px;
            height: 36px;
        }}

        .brand-title {{
            font-size: clamp(22px, 1.75vw, 30px);
            font-weight: 860;
            line-height: 1.2;
            color: #0f172a;
            margin: 0;
            word-break: keep-all;
        }}

        .brand-subtitle {{
            font-size: 15px;
            color: var(--muted);
            margin-top: 8px;
        }}

        .dday-card {{
            border: 1px solid var(--line);
            background: #fff;
            border-radius: 10px;
            padding: 13px 18px;
            font-weight: 760;
            color: #111827;
            white-space: nowrap;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
        }}

        .dday-card b {{
            color: var(--red);
            font-size: 21px;
            margin-left: 6px;
        }}

        div[role="radiogroup"] {{
            gap: 0 !important;
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0;
            overflow: hidden;
            width: fit-content;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
        }}

        div[role="radiogroup"] label {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 42px;
            min-width: 72px;
            padding: 0 16px !important;
            border-right: 1px solid var(--line);
            margin: 0 !important;
            text-align: center !important;
        }}

        div[role="radiogroup"] label p {{
            width: 100%;
            margin: 0 !important;
            text-align: center !important;
            font-weight: 760;
        }}

        div[role="radiogroup"] label:last-child {{
            border-right: 0;
        }}

        div[role="radiogroup"] label > div:first-child {{
            display: none;
        }}

        div[role="radiogroup"] label[data-baseweb="radio"] {{
            background: #fff;
        }}

        div[role="radiogroup"] label:has(input:checked) {{
            background: linear-gradient(135deg, #2f74e8, #1d4ed8);
            color: #fff !important;
        }}

        div.stButton > button {{
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            min-height: 44px;
            border-radius: 8px;
            border: 1px solid var(--line);
            background: #ffffff;
            color: #111827;
            box-shadow: none;
            padding: 0 8px;
            transition: all 0.16s ease;
        }}

        div.stButton > button p {{
            font-size: 14px;
            line-height: 1.15;
            font-weight: 760;
            margin: 0;
            word-break: keep-all;
        }}

        div.stButton > button:hover {{
            border-color: #93c5fd;
            color: var(--blue-dark);
        }}

        div.stButton > button[kind="primary"],
        div.stButton > button[data-testid="stBaseButton-primary"] {{
            background: linear-gradient(135deg, #2f74e8, #1d4ed8) !important;
            border-color: #1d4ed8 !important;
            color: #ffffff !important;
        }}

        div.stButton > button[kind="primary"] p,
        div.stButton > button[data-testid="stBaseButton-primary"] p {{
            color: #ffffff !important;
        }}

        .nav-shell {{
            border-bottom: 1px solid var(--line);
            margin: 4px -1.5rem 18px;
            padding: 0 1.5rem;
            background: rgba(255,255,255,0.72);
            backdrop-filter: blur(12px);
        }}

        .nav-row {{
            display: grid;
            grid-template-columns: repeat(8, minmax(110px, 1fr));
            gap: 4px;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 15px 8px 14px;
            border-bottom: 3px solid transparent;
            color: #1f2937;
            font-size: 15px;
            font-weight: 720;
            white-space: nowrap;
        }}

        .nav-item.active {{
            color: var(--blue-dark);
            border-bottom-color: var(--blue-dark);
            background: linear-gradient(180deg, rgba(37, 99, 235, 0.05), rgba(37, 99, 235, 0));
        }}

        .section-title {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            margin: 8px 0 12px;
        }}

        .section-title h2 {{
            font-size: 25px;
            line-height: 1.2;
            margin: 0;
            font-weight: 850;
        }}

        .section-title span {{
            font-size: 14px;
            color: var(--muted);
        }}

        .card {{
            background: rgba(255,255,255,0.92);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.045);
            text-align: left;
        }}

        .compact-card {{
            padding: 14px;
        }}

        .notice {{
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            background: #f8fbff;
            color: #1e3a8a;
            padding: 14px 18px;
            line-height: 1.65;
            font-weight: 560;
        }}

        .notice.warning {{
            background: #fff7f7;
            border-color: #fecdd3;
            color: #991b1b;
        }}

        .notice.gray {{
            background: #f8fafc;
            border-color: #dbe3ef;
            color: #334155;
        }}

        .candidate-home {{
            display: grid;
            grid-template-columns: 140px 1fr;
            gap: 18px;
            align-items: center;
        }}

        .avatar {{
            width: 140px;
            aspect-ratio: 1 / 1;
            border-radius: 8px;
            border: 1px solid var(--line);
            background: linear-gradient(145deg, #f1f5f9 0%, #ffffff 55%, #e2e8f0 100%);
            display: grid;
            place-items: center;
            position: relative;
            overflow: hidden;
        }}

        .candidate-photo,
        .profile-photo {{
            width: 100% !important;
            height: 100% !important;
            display: block;
            object-fit: cover !important;
            object-position: center top !important;
        }}

        .candidate-photo.photo-OSH,
        .profile-photo.photo-OSH {{
            object-position: center top !important;
        }}

        .avatar:has(img)::before,
        .avatar:has(img)::after,
        .profile-avatar:has(img)::before,
        .profile-avatar:has(img)::after {{
            display: none;
        }}

        .avatar:before {{
            content: "";
            position: absolute;
            width: 64px;
            height: 64px;
            border-radius: 999px;
            top: 25px;
            background: #cbd5e1;
        }}

        .avatar:after {{
            content: "";
            position: absolute;
            width: 104px;
            height: 70px;
            border-radius: 50% 50% 0 0;
            bottom: 0;
            background: #334155;
        }}

        .avatar-initial {{
            position: relative;
            z-index: 3;
            margin-top: -8px;
            font-size: 25px;
            font-weight: 900;
            color: #ffffff;
        }}

        .avatar.red:after {{
            background: #3f1f25;
        }}

        .avatar.blue:after {{
            background: #1e3a5f;
        }}

        .candidate-name-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 45px;
            height: 34px;
            padding: 0 10px;
            border-radius: 8px;
            border: 1px solid;
            font-size: 15px;
            font-weight: 850;
        }}

        .badge.blue {{
            color: var(--blue-dark);
            border-color: #bfdbfe;
            background: #f4f8ff;
        }}

        .badge.red {{
            color: var(--red-dark);
            border-color: #fecdd3;
            background: #fff7f7;
        }}

        .candidate-name {{
            font-size: 27px;
            font-weight: 880;
            color: #0f172a;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            border-top: 1px solid var(--line);
            margin-top: 12px;
        }}

        .metric-cell {{
            padding: 12px 0 0;
        }}

        .metric-cell + .metric-cell {{
            border-left: 1px solid var(--line);
            padding-left: 16px;
        }}

        .metric-label {{
            font-size: 13px;
            color: var(--muted);
            margin-bottom: 4px;
        }}

        .metric-value {{
            font-size: 28px;
            font-weight: 900;
            line-height: 1.08;
        }}

        .blue-text {{
            color: var(--blue-dark);
        }}

        .red-text {{
            color: var(--red-dark);
        }}

        .green-text {{
            color: #15803d;
        }}

        .chip-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
        }}

        .chip {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 7px 12px;
            font-weight: 730;
            font-size: 14px;
            line-height: 1;
            border: 1px solid;
        }}

        .chip.blue {{
            color: #1d4ed8;
            border-color: #d6e6ff;
            background: #edf5ff;
        }}

        .chip.red {{
            color: #b91c1c;
            border-color: #ffe0e0;
            background: #fff0f1;
        }}

        .chip.gray {{
            color: #334155;
            border-color: #e2e8f0;
            background: #f8fafc;
        }}

        .chip.green {{
            color: #15803d;
            border-color: #bbf7d0;
            background: #f0fdf4;
        }}

        .versus-bar-wrap {{
            text-align: center;
        }}

        .versus-title {{
            font-size: 20px;
            font-weight: 850;
            margin-bottom: 4px;
        }}

        .versus-subtitle {{
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 20px;
        }}

        .versus-bar {{
            display: grid;
            grid-template-columns: var(--left) var(--right);
            position: relative;
            overflow: visible;
            height: 68px;
            border-radius: 8px;
            margin: 0 auto;
            max-width: 620px;
            box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.06);
        }}

        .versus-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 25px;
            font-weight: 900;
        }}

        .versus-segment.left {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 8px 0 0 8px;
        }}

        .versus-segment.right {{
            background: linear-gradient(135deg, #fb4856, #dc2626);
            border-radius: 0 8px 8px 0;
        }}

        .vs-bubble {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 68px;
            height: 68px;
            border-radius: 999px;
            background: #fff;
            display: grid;
            place-items: center;
            color: #111827;
            font-weight: 900;
            font-size: 18px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.20);
        }}

        .mini-note {{
            margin-top: 18px;
            color: #475569;
            font-size: 14px;
            line-height: 1.65;
        }}

        .ai-box {{
            display: grid;
            grid-template-columns: 58px 1fr;
            gap: 16px;
            align-items: center;
            border: 1px solid #bfd7ff;
            background: #f8fbff;
            border-radius: 8px;
            padding: 17px 20px;
            margin: 18px 0;
        }}

        .ai-icon {{
            width: 58px;
            height: 58px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: #e8f1ff;
            color: var(--blue-dark);
            font-weight: 900;
        }}

        .ai-title {{
            font-weight: 850;
            margin-bottom: 4px;
        }}

        .ai-text {{
            color: #243041;
            line-height: 1.65;
            font-size: 15px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}

        .two-col-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin-top: 14px;
        }}

        .keyword-change-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }}

        .kpi-mini {{
            border: 1px solid var(--line);
            background: #fff;
            border-radius: 8px;
            padding: 15px;
        }}

        .kpi-mini-title {{
            color: #334155;
            font-weight: 800;
            margin-bottom: 8px;
        }}

        .kpi-mini-value {{
            color: #0f172a;
            font-size: 24px;
            font-weight: 900;
        }}

        .issue-row {{
            display: grid;
            grid-template-columns: 86px 54px 1fr 54px;
            align-items: center;
            gap: 10px;
            margin: 13px 0;
            font-size: 14px;
            font-weight: 730;
        }}

        .issue-track {{
            display: grid;
            grid-template-columns: var(--blueShare) var(--redShare);
            height: 10px;
            border-radius: 999px;
            overflow: hidden;
            background: #e5e7eb;
        }}

        .issue-blue {{
            background: linear-gradient(90deg, #60a5fa, #2563eb);
        }}

        .issue-red {{
            background: linear-gradient(90deg, #fb7185, #ef3340);
        }}

        .word-cloud {{
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            align-content: center;
            flex-wrap: wrap;
            gap: 10px 16px;
            padding: 18px;
            border-radius: 8px;
            border: 1px solid var(--line);
            background: #fff;
            text-align: center;
        }}

        .word {{
            font-weight: 850;
            line-height: 1.1;
            display: inline-block;
        }}

        .word.blue {{
            color: #2563eb;
        }}

        .word.red {{
            color: #dc2626;
        }}

        .reason-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
        }}

        .reason-card {{
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            background: #fff;
        }}

        .reason-title {{
            font-weight: 860;
            margin-bottom: 8px;
            font-size: 16px;
        }}

        .reason-text {{
            color: #334155;
            line-height: 1.65;
            font-size: 14px;
        }}

        .profile-grid {{
            display: grid;
            grid-template-columns: 210px 1fr;
            gap: 20px;
        }}

        .profile-avatar {{
            width: 100%;
            aspect-ratio: 1 / 1.12;
            border-radius: 8px;
            border: 1px solid var(--line);
            background: linear-gradient(145deg, #f1f5f9 0%, #ffffff 52%, #e5e7eb 100%);
            display: grid;
            place-items: center;
            position: relative;
            overflow: hidden;
        }}

        .profile-avatar:before {{
            content: "";
            position: absolute;
            width: 84px;
            height: 84px;
            top: 45px;
            border-radius: 999px;
            background: #cbd5e1;
        }}

        .profile-avatar:after {{
            content: "";
            position: absolute;
            width: 170px;
            height: 110px;
            bottom: 0;
            border-radius: 50% 50% 0 0;
            background: #1e3a5f;
        }}

        .profile-avatar.red:after {{
            background: #3f1f25;
        }}

        .profile-initial {{
            z-index: 2;
            color: #fff;
            font-size: 36px;
            font-weight: 900;
            margin-top: -12px;
        }}

        .button-link {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 9px 12px;
            color: #334155;
            text-decoration: none;
            font-weight: 750;
            font-size: 13px;
            background: #fff;
            margin: 4px 6px 4px 0;
            cursor: pointer;
        }}

        .button-link:hover {{
            border-color: #bfdbfe;
            color: #1d4ed8;
            background: #f8fbff;
        }}

        .button-link.blue {{
            color: var(--blue-dark);
            border-color: #bfdbfe;
            background: #f4f8ff;
        }}

        .button-link.red {{
            color: var(--red-dark);
            border-color: #fecdd3;
            background: #fff7f7;
        }}

        .rank-up {{
            color: #15803d;
            font-weight: 850;
        }}

        .rank-down {{
            color: #dc2626;
            font-weight: 850;
        }}

        .rank-same {{
            color: #64748b;
            font-weight: 760;
        }}

        .table-note {{
            color: var(--muted);
            font-size: 13px;
            margin-top: 8px;
        }}

        @media (max-width: 960px) {{
            .top-shell, .ai-box {{
                grid-template-columns: 1fr;
                display: grid;
            }}
            .top-shell {{
                align-items: start;
            }}
            .nav-row {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .candidate-home, .profile-grid, .reason-grid, .kpi-grid,
            .two-col-grid, .keyword-change-grid {{
                grid-template-columns: 1fr;
            }}
            .brand-wrap {{
                min-width: 0;
            }}
            .versus-bar {{
                height: 54px;
            }}
            .versus-segment {{
                font-size: 19px;
            }}
            .vs-bubble {{
                width: 50px;
                height: 50px;
                font-size: 14px;
            }}
            .word-cloud {{
                min-height: 210px;
                padding: 14px;
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
    mime = "jpeg" if suffix in {"jpg", "jpeg"} else suffix
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def candidate_photo_html(code: str, class_name: str) -> str:
    uri = image_data_uri(CANDIDATE_IMAGES.get(code))
    if not uri:
        name = escape(candidate_name(code))
        return f'<span class="avatar-initial">{name[:1]}</span>'
    return f'<img class="{class_name} photo-{escape(code)}" src="{uri}" alt="{escape(candidate_name(code))} 사진" />'


def action_link(label: str, href: str, tone: str = "gray", full_width: bool = False) -> str:
    width = " width:100%;" if full_width else ""
    return (
        f'<a class="button-link {escape(tone)}" href="{escape(href)}" '
        f'target="_blank" rel="noopener noreferrer" style="{width}">{escape(label)}</a>'
    )


def page_link(label: str, page_key: str, tone: str = "gray", full_width: bool = False) -> str:
    width = " width:100%;" if full_width else ""
    return f'<a class="button-link {escape(tone)}" href="/?page={escape(page_key)}" style="{width}">{escape(label)}</a>'


def navigate_to(page_key: str) -> None:
    st.session_state.selected_page = page_key
    st.query_params["page"] = page_key
    st.rerun()


def nav_button(label: str, key: str, page_key: str = "evidence", width: str = "stretch") -> None:
    if st.button(label, key=key, type="secondary", width=width):
        navigate_to(page_key)


def render_title_header() -> None:
    st.markdown(
        """
        <div class="top-shell">
            <div class="brand-wrap">
                <div class="logo-mark" aria-hidden="true">
                    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7 39H41" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                        <path d="M10 33L20 23L27 29L39 13" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M35 13H40V18" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M10 37V26M20 37V20M30 37V25M40 37V14" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                    </svg>
                </div>
                <div>
                    <h1 class="brand-title">서울시장 선거 여론 모니터 - 공개 온라인 반응으로 보는 두 후보 비교와 주요 쟁점 흐름</h1>
                    <div class="brand-subtitle">데모 데이터 · 실제 지지율·득표율·선거 결과 예측 아님</div>
                </div>
            </div>
            <div class="dday-card">서울시장 선거 <b>D-23</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_nav(selected_page: str, pages: list[tuple[str, str]]) -> None:
    items = []
    for key, label in pages:
        active = " active" if key == selected_page else ""
        items.append(f'<div class="nav-item{active}">{escape(label)}</div>')
    st.markdown(f'<div class="nav-shell"><div class="nav-row">{"".join(items)}</div></div>', unsafe_allow_html=True)


def section_title(title: str, caption: str | None = None) -> None:
    caption_html = f"<span>{escape(caption)}</span>" if caption else ""
    st.markdown(f'<div class="section-title"><h2>{escape(title)}</h2>{caption_html}</div>', unsafe_allow_html=True)


def notice(text: str, tone: str = "blue") -> None:
    cls = "notice"
    if tone in {"warning", "gray"}:
        cls += f" {tone}"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def demo_notice() -> None:
    notice(
        "데모 데이터입니다. 공개 온라인 반응 기반 예시이며, 실제 지지율·득표율·선거 결과 예측이 아닙니다.",
        "warning",
    )


def candidate_home_card(row: pd.Series, keywords: Iterable[str], tone: str) -> str:
    code = str(row["candidate_code"])
    name = escape(str(row["candidate_name"]))
    color_class = "blue" if tone == "blue" else "red"
    score = f"{row['reaction_score']:.1f}"
    growth = f"+{row['period_growth_rate']:.1f}%" if row["period_growth_rate"] >= 0 else f"{row['period_growth_rate']:.1f}%"
    comments = format_number(row["comment_count"])
    chips = "".join(f'<span class="chip {color_class}">{escape(str(keyword))}</span>' for keyword in keywords)
    photo = candidate_photo_html(code, "candidate-photo")
    return f"""
    <div class="card">
        <div class="candidate-home">
            <div class="avatar {color_class}">{photo}</div>
            <div>
                <div class="candidate-name-row">
                    <span class="candidate-name">{name}</span>
                </div>
                <div class="metric-label">온라인 반응 점수</div>
                <div class="metric-value {color_class}-text">{score}</div>
                <div class="table-note">언급량·댓글·게시물 반응을 0~100으로 바꾼 데모 점수입니다.</div>
                <div class="metric-grid">
                    <div class="metric-cell">
                        <div class="metric-label">최근 증가율</div>
                        <div class="metric-value {color_class}-text" style="font-size:21px">{growth}</div>
                    </div>
                    <div class="metric-cell">
                        <div class="metric-label">댓글 반응량</div>
                        <div class="metric-value" style="font-size:21px">{comments}</div>
                    </div>
                </div>
                <div class="metric-label" style="margin-top:14px">대표 연관어 TOP 3</div>
                <div class="chip-row">{chips}</div>
            </div>
        </div>
    </div>
    """


def competition_bar(shares: pd.DataFrame) -> None:
    jwo = shares.loc[shares["candidate_code"].eq("JWO"), "share"].iloc[0]
    osh = shares.loc[shares["candidate_code"].eq("OSH"), "share"].iloc[0]
    st.markdown(
        f"""
        <div class="card versus-bar-wrap">
            <div class="versus-title">온라인 반응 나눠 보기</div>
            <div class="versus-subtitle">선택 기간의 전체 반응량을 두 후보 사이에서 나눈 값입니다.</div>
            <div class="versus-bar" style="--left:{jwo}%; --right:{osh}%;">
                <div class="versus-segment left">{jwo:.1f}%</div>
                <div class="versus-segment right">{osh:.1f}%</div>
                <div class="vs-bubble">VS</div>
            </div>
            <div class="mini-note">
                실제 여론조사나 지지율이 아닙니다.<br/>
                공개 게시물에서 관측된 반응량을 이해하기 쉽게 나눈 데모 수치입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_summary(text: str, page_key: str = "evidence") -> None:
    st.markdown(
        f"""
        <div class="ai-box">
            <div class="ai-icon">AI</div>
            <div>
                <div class="ai-title">AI 요약 한 줄</div>
                <div class="ai-text">{escape(text)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, button_col = st.columns([0.82, 0.18])
    with button_col:
        nav_button("요약 자세히 보기", f"ai_summary_to_{page_key}", page_key)


def kpi_card(title: str, value: str, caption: str = "", tone: str = "gray") -> str:
    value_class = "blue-text" if tone == "blue" else "red-text" if tone == "red" else "green-text" if tone == "green" else ""
    return (
        f'<div class="kpi-mini">'
        f'<div class="kpi-mini-title">{escape(title)}</div>'
        f'<div class="kpi-mini-value {value_class}">{escape(value)}</div>'
        f'<div class="metric-label">{escape(caption)}</div>'
        f"</div>"
    )


def term_glossary_card() -> str:
    return """
    <div class="card">
        <div class="section-title" style="margin-top:0"><h2>용어 쉽게 보기</h2></div>
        <div class="kpi-mini">
            <div class="kpi-mini-title blue-text">온라인 반응 점수</div>
            <div class="reason-text">뉴스·영상·게시글·댓글에서 얼마나 자주 언급되고 반응이 붙었는지를 0~100으로 바꾼 참고 점수입니다. 실제 지지율이 아닙니다.</div>
        </div>
        <div class="kpi-mini" style="margin-top:12px;">
            <div class="kpi-mini-title red-text">온라인 반응 나눠 보기</div>
            <div class="reason-text">선택 기간에 관측된 전체 반응량을 두 후보 사이에서 단순 비교한 값입니다. 득표율이나 당선 가능성이 아닙니다.</div>
        </div>
        <div class="kpi-mini" style="margin-top:12px;">
            <div class="kpi-mini-title">연관어</div>
            <div class="reason-text">후보 이름과 함께 자주 등장한 단어입니다. 검색 로그나 개인 관심사 데이터가 아니라 공개 텍스트에서 나온 단어입니다.</div>
        </div>
    </div>
    """


def keyword_chips(keywords: Iterable[str], tone: str, limit: int | None = None) -> str:
    color_class = "blue" if tone == "blue" else "red" if tone == "red" else "gray"
    values = list(keywords)
    if limit:
        values = values[:limit]
    return '<div class="chip-row">' + "".join(f'<span class="chip {color_class}">{escape(str(item))}</span>' for item in values) + "</div>"


def word_cloud(frame: pd.DataFrame, tone: str, max_words: int = 22) -> None:
    color_class = "blue" if tone == "blue" else "red"
    data = frame.sort_values("mention_count", ascending=False).head(max_words).copy()
    if data.empty:
        st.markdown('<div class="word-cloud">표시할 연관어가 없습니다.</div>', unsafe_allow_html=True)
        return
    min_count = data["mention_count"].min()
    max_count = data["mention_count"].max()
    words = []
    for idx, (_, row) in enumerate(data.iterrows()):
        if max_count == min_count:
            size = 24
            opacity = 0.92
        else:
            importance = (row["mention_count"] - min_count) / (max_count - min_count)
            size = 14 + importance * 34
            opacity = 0.58 + importance * 0.42
        order = 0 if idx < 3 else idx + 1
        words.append(
            f'<span class="word {color_class}" style="font-size:{size:.0f}px; opacity:{opacity:.2f}; order:{order};">'
            f'{escape(str(row["keyword"]))}</span>'
        )
    st.markdown(f'<div class="word-cloud">{"".join(words)}</div>', unsafe_allow_html=True)


def rank_change_badge(value: int | float) -> str:
    number = int(value)
    if number > 0:
        return f'<span class="rank-up">▲ {number}</span>'
    if number < 0:
        return f'<span class="rank-down">▼ {abs(number)}</span>'
    return '<span class="rank-same">변동 없음</span>'


def issue_compare_rows(frame: pd.DataFrame, limit: int = 6) -> None:
    rows = []
    for _, row in frame.head(limit).iterrows():
        issue = escape(str(row["issue_category"]))
        jwo = int(row["JWO_share"])
        osh = int(row["OSH_share"])
        rows.append(
            f"""
            <div class="issue-row">
                <div>{issue}</div>
                <div class="blue-text">{jwo}%</div>
                <div class="issue-track" style="--blueShare:{jwo}%; --redShare:{osh}%;">
                    <div class="issue-blue"></div><div class="issue-red"></div>
                </div>
                <div class="red-text">{osh}%</div>
            </div>
            """
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def reason_cards(items: list[tuple[str, str, list[str] | None]]) -> None:
    cards = []
    for title, text, chips in items:
        chip_html = keyword_chips(chips or [], "blue") if chips else ""
        cards.append(
            f'<div class="reason-card"><div class="reason-title">{escape(title)}</div>'
            f'<div class="reason-text">{escape(text)}</div>{chip_html}</div>'
        )
    st.markdown(f'<div class="reason-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def profile_card(row: pd.Series, tone: str, points: list[tuple[str, str]]) -> None:
    color_class = "blue" if tone == "blue" else "red"
    code = str(row["candidate_code"])
    name = escape(str(row["candidate_name"]))
    party = escape(str(row["party"]))
    role = escape(str(row["role"]))
    career_items = "".join(f"<li>{escape(item.strip())}</li>" for item in str(row["career"]).split("|"))
    education_items = "".join(f"<li>{escape(item.strip())}</li>" for item in str(row["education"]).split("|"))
    channels = "".join(action_link(label, url, color_class) for label, url in OFFICIAL_CHANNELS.get(code, []))
    photo = candidate_photo_html(code, "profile-photo")
    point_cards = "".join(
        f"""
        <div class="kpi-mini">
            <div class="kpi-mini-title {color_class}-text">{escape(title)}</div>
            <div class="reason-text">{escape(caption)}</div>
        </div>
        """
        for title, caption in points
    )

    st.markdown(
        f"""
        <div class="card">
            <div class="profile-grid">
                <div class="profile-avatar {color_class}">{photo}</div>
                <div>
                    <div class="candidate-name-row">
                        <span class="candidate-name">{name}</span>
                    </div>
                    <div class="metric-label" style="font-size:15px">{party}  |  {role}</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px; margin:22px 0; border-top:1px solid var(--line); padding-top:16px;">
                        <div>
                            <div class="{color_class}-text" style="font-weight:850; margin-bottom:8px;">주요 경력</div>
                            <ul style="margin:0; padding-left:18px; line-height:1.8;">{career_items}</ul>
                        </div>
                        <div>
                            <div style="font-weight:850; margin-bottom:8px;">학력 요약</div>
                            <ul style="margin:0; padding-left:18px; line-height:1.8;">{education_items}</ul>
                        </div>
                    </div>
                    <div style="font-weight:850; margin-bottom:8px;">공식 채널</div>
                    <div>{channels}</div>
                    <div class="metric-grid" style="margin-top:18px;">
                        <div class="metric-cell">
                            <div class="metric-label">온라인 반응 점수</div>
                            <div class="metric-value {color_class}-text">{row['reaction_score']:.1f}</div>
                        </div>
                        <div class="metric-cell">
                            <div class="metric-label">최근 증가율</div>
                            <div class="metric-value {color_class}-text">{row['period_growth_rate']:+.1f}%</div>
                        </div>
                    </div>
                </div>
            </div>
            <div style="margin-top:16px;" class="kpi-grid">{point_cards}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_plotly(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=28, b=20),
        font=dict(family=FONT_STACK, size=13, color="#1f2937"),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e5e7eb", tickfont=dict(color="#475569"))
    fig.update_yaxes(gridcolor="#edf2f7", zerolinecolor="#e5e7eb", tickfont=dict(color="#475569"))
    return fig


def dataframe_clean(frame: pd.DataFrame) -> pd.DataFrame:
    display = frame.copy()
    for column in display.columns:
        if pd.api.types.is_datetime64_any_dtype(display[column]):
            display[column] = display[column].dt.strftime("%Y.%m.%d")
    return display


def candidate_color(code: str) -> str:
    return CANDIDATE_COLORS.get(code, "#64748b")


def candidate_name(code: str) -> str:
    return CANDIDATE_NAMES.get(code, code)
