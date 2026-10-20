"""Design system: tokens + reusable components. No business logic here."""
import html
import streamlit as st

T = {"text": "#20243A", "muted": "#59607A", "accent": "#6250A4", "hover": "#4F407F",
     "soft": "#F0ECFF", "border": "#E2E5EF"}
KINDS = {"ok": ("#217A52", "#E6F4EC"), "warn": ("#865710", "#FBF1DC"), "err": ("#B42332", "#FBE6E8"),
         "info": ("#315F9B", "#E6EEF8"), "muted": ("#59607A", "#EEF0F5")}


def inject():
    st.markdown(f"""<style>
.block-container{{max-width:1100px;padding-top:2rem}}
section[data-testid="stSidebar"]{{background:#fff;border-right:1px solid {T['border']}}}
.gp-card{{background:#fff;border:1px solid {T['border']};border-radius:12px;padding:16px 18px;margin-bottom:12px}}
.gp-card.empty{{border-style:dashed;background:{T['soft']}}}
.gp-label{{color:{T['muted']};font-size:13px}}
.gp-value{{color:{T['text']};font-size:26px;font-weight:600;line-height:1.2}}
.gp-badge{{display:inline-block;padding:2px 10px;margin:2px 4px 2px 0;border-radius:999px;font-size:12px;font-weight:600}}
div[data-testid="stForm"]{{background:#fff;border:1px solid {T['border']};border-radius:12px}}
button[kind="primary"],button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{{background:{T['accent']};border:0}}
button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{{background:{T['hover']}}}
button[kind="primary"] *,button[kind="primaryFormSubmit"] *,
button[data-testid="stBaseButton-primary"] *,button[data-testid="stBaseButton-primaryFormSubmit"] *{{color:#fff!important}}
button:focus-visible,input:focus-visible,textarea:focus-visible{{outline:3px solid {T['accent']}!important;outline-offset:2px}}
</style>""", unsafe_allow_html=True)


def card(title, body="", kind=""):
    st.markdown(f'<div class="gp-card {kind}"><strong>{html.escape(title)}</strong>'
                f'<div class="gp-label">{html.escape(body)}</div></div>', unsafe_allow_html=True)


def empty(title, body):
    card(title, body, "empty")


def metric(label, value, hint=""):
    st.markdown(f'<div class="gp-card"><div class="gp-label">{html.escape(label)}</div>'
                f'<div class="gp-value">{html.escape(str(value))}</div>'
                f'<div class="gp-label">{html.escape(hint)}</div></div>', unsafe_allow_html=True)


def badge(text, kind="muted"):
    fg, bg = KINDS[kind]
    return f'<span class="gp-badge" style="color:{fg};background:{bg}">{html.escape(text)}</span>'
