"""
ui/styles/theme.py
──────────────────
CSS injection for light / dark themes.
Call inject_css(dark=True/False) once per page render.
"""

import streamlit as st


def inject_css(dark: bool) -> None:
    """Inject a full light or dark theme via st.markdown unsafe HTML."""

    if dark:
        bg          = "#0f1117"
        surface     = "#1a1d27"
        surface2    = "#22263a"
        border      = "#2e3354"
        text_pri    = "#e8eaf6"
        text_sec    = "#9098c0"
        accent      = "#5c6bc0"
        accent_glow = "rgba(92,107,192,0.18)"
        success_bg  = "rgba(46,125,50,0.15)"
        success_br  = "#2e7d32"
        warn_bg     = "rgba(230,162,0,0.12)"
        warn_br     = "#e6a200"
        err_bg      = "rgba(183,28,28,0.14)"
        err_br      = "#b71c1c"
        metric_bg   = "#1e2235"
        divider     = "#2e3354"
        sidebar_bg  = "#13151f"
        badge_bg    = "rgba(92,107,192,0.18)"
        badge_text  = "#a0aad4"
    else:
        bg          = "#f4f6fb"
        surface     = "#ffffff"
        surface2    = "#eef0f8"
        border      = "#d0d5e8"
        text_pri    = "#1a1d2e"
        text_sec    = "#555c80"
        accent      = "#3d52a0"
        accent_glow = "rgba(61,82,160,0.10)"
        success_bg  = "rgba(46,125,50,0.08)"
        success_br  = "#2e7d32"
        warn_bg     = "rgba(230,162,0,0.10)"
        warn_br     = "#b87800"
        err_bg      = "rgba(183,28,28,0.08)"
        err_br      = "#b71c1c"
        metric_bg   = "#eef0f8"
        divider     = "#d0d5e8"
        sidebar_bg  = "#eaedf5"
        badge_bg    = "rgba(61,82,160,0.10)"
        badge_text  = "#3d52a0"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

        /* ── Base ── */
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {{
            background-color: {bg} !important;
            color: {text_pri} !important;
            font-family: 'DM Sans', sans-serif !important;
        }}
        .block-container {{
            padding-top: 1.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 1160px !important;
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div:first-child {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border} !important;
        }}
        [data-testid="stSidebar"] .stMarkdown p {{
            color: {text_sec} !important;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: {border} !important;
        }}

        /* ── Sidebar status badge ── */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            font-weight: 500;
            padding: 4px 10px;
            border-radius: 99px;
            background: {badge_bg};
            color: {badge_text};
            border: 1px solid {border};
            margin-top: 4px;
        }}
        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
        }}
        .status-dot.online  {{ background: #4caf50; box-shadow: 0 0 4px #4caf5088; }}
        .status-dot.offline {{ background: #ef5350; box-shadow: 0 0 4px #ef535088; }}

        /* ── Sidebar info card ── */
        .sidebar-card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 12px;
            font-size: 0.82rem;
            color: {text_sec};
            line-height: 1.6;
        }}
        .sidebar-card strong {{
            color: {text_pri} !important;
            font-weight: 600;
        }}

        /* ── Typography ── */
        h1, h2, h3, h4 {{
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            color: {text_pri} !important;
            letter-spacing: -0.3px;
        }}
        p, li, label, span, div {{
            color: {text_pri} !important;
        }}
        .stMarkdown p {{
            color: {text_sec} !important;
            font-size: 0.92rem !important;
            line-height: 1.65 !important;
        }}
        caption, small, [data-testid="stCaptionContainer"] p {{
            color: {text_sec} !important;
            font-size: 0.8rem !important;
        }}

        /* ── Inputs ── */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] select {{
            background-color: {surface2} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
            color: {text_pri} !important;
            font-family: 'DM Sans', sans-serif !important;
            transition: border-color 0.2s;
        }}
        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 3px {accent_glow} !important;
        }}

        /* ── Buttons ── */
        .stButton > button {{
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }}
        .stButton > button[kind="primary"] {{
            background: {accent} !important;
            border: none !important;
            color: #ffffff !important;
            padding: 0.5rem 1.4rem !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            opacity: 0.88 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px {accent_glow} !important;
        }}
        .stButton > button:not([kind="primary"]) {{
            background: {surface2} !important;
            border: 1px solid {border} !important;
            color: {text_pri} !important;
        }}

        /* ── Metrics ── */
        [data-testid="stMetric"] {{
            background: {metric_bg} !important;
            border: 1px solid {border} !important;
            border-radius: 12px !important;
            padding: 1rem 1.2rem !important;
        }}
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricLabel"] span {{
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            color: {text_sec} !important;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'Space Mono', monospace !important;
            font-size: 1.5rem !important;
            color: {text_pri} !important;
        }}

        /* ── Alerts ── */
        [data-testid="stSuccess"] {{
            background: {success_bg} !important;
            border: 1px solid {success_br} !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.1rem !important;
        }}
        [data-testid="stWarning"] {{
            background: {warn_bg} !important;
            border: 1px solid {warn_br} !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.1rem !important;
        }}
        [data-testid="stError"] {{
            background: {err_bg} !important;
            border: 1px solid {err_br} !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.1rem !important;
        }}

        /* ── Tabs ── */
        [data-testid="stTabs"] [role="tablist"] {{
            background: {surface} !important;
            border: 1px solid {border} !important;
            border-radius: 12px !important;
            padding: 4px !important;
            gap: 2px !important;
        }}
        [data-testid="stTabs"] [role="tab"] {{
            border-radius: 9px !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            padding: 0.45rem 1rem !important;
            color: {text_sec} !important;
            transition: all 0.2s !important;
        }}
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
            background: {accent} !important;
            color: #ffffff !important;
        }}

        /* ── Tables ── */
        [data-testid="stTable"] table,
        .stDataFrame table {{
            background: {surface} !important;
            border-radius: 10px !important;
            border: 1px solid {border} !important;
            overflow: hidden !important;
            font-size: 0.87rem !important;
        }}
        [data-testid="stTable"] thead tr th,
        .stDataFrame thead tr th {{
            background: {surface2} !important;
            color: {text_sec} !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            padding: 0.65rem 1rem !important;
            border-bottom: 1px solid {border} !important;
        }}
        [data-testid="stTable"] tbody tr td,
        .stDataFrame tbody tr td {{
            color: {text_pri} !important;
            padding: 0.6rem 1rem !important;
            border-bottom: 1px solid {border} !important;
        }}

        /* ── Divider ── */
        hr {{
            border-color: {divider} !important;
            margin: 1.5rem 0 !important;
        }}

        /* ── File uploader ── */
        [data-testid="stFileUploader"] {{
            border: 2px dashed {border} !important;
            border-radius: 12px !important;
            background: {surface} !important;
            padding: 1rem !important;
        }}
        [data-testid="stFileUploader"]:hover {{
            border-color: {accent} !important;
        }}

        /* ── Charts ── */
        [data-testid="stArrowVegaLiteChart"] > div,
        [data-testid="stVegaLiteChart"] > div {{
            background: {surface} !important;
            border: 1px solid {border} !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }}

        /* ── Form container ── */
        [data-testid="stForm"] {{
            background: {surface} !important;
            border: 1px solid {border} !important;
            border-radius: 14px !important;
            padding: 1.5rem !important;
        }}

        /* ── Info box ── */
        [data-testid="stInfo"] {{
            background: {surface2} !important;
            border: 1px solid {border} !important;
            border-radius: 10px !important;
        }}
    </style>
    """, unsafe_allow_html=True)