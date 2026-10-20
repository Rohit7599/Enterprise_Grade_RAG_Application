import os
import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import uuid
import logfire
from dotenv import load_dotenv


# Load environment variables explicitly from the root directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)


# Initialize Logfire
try:
    token = os.getenv("LOGFIRE_TOKEN")
    if not token:
        print("ERROR: LOGFIRE_TOKEN is empty or None!")
    logfire.configure(token=token)
    # logfire.instrument_requests() # Disabled due to OpenTelemetry bug on Windows: MeterProvider.get_meter() got multiple values for argument 'version'
    LOGFIRE_STATUS = "Connected & Tracing"
except Exception as e:
    print(f"Logfire Init Error in UI: {e}")
    LOGFIRE_STATUS = f"Standby (Error: {e})"
    


# --- BRANDING (change these two lines to rename your website) ---
BRAND_NAME = "KubeMind"
BRAND_TAGLINE = "psst... your Kubernetes docs, but chatty 🐙"

TIPS = [
    "Pods are mortal. Wrap them in a Deployment and Kubernetes will bring them back for you. 🧟",
    "Pod stuck on Pending? Run kubectl describe pod and read the Events at the bottom. 🕵️",
    "Always set resource requests and limits. Your future self will say thanks. 🙏",
    "Labels and selectors are how a Service finds its Pods. Match them carefully. 🏷️",
    "Namespaces keep teams and environments tidy. Use them early. 🗂️",
    "A readiness probe stops traffic from reaching a pod that is not ready yet. 🚦",
]


def brand_logo(size=46):
    """Hand-made looking sticker logo: a little container cube on a mustard tile."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-label="{BRAND_NAME} logo"><rect x="6" y="6" width="56" height="56" rx="16" fill="#1f1b16"/><rect x="2" y="2" width="56" height="56" rx="16" fill="#f2b83d" stroke="#1f1b16" stroke-width="3"/><polygon points="30,13 45,21.5 45,38.5 30,47 15,38.5 15,21.5" fill="#fffaf0" stroke="#1f1b16" stroke-width="3" stroke-linejoin="round"/><polygon points="30,13 45,21.5 30,30 15,21.5" fill="#e8553d" stroke="#1f1b16" stroke-width="3" stroke-linejoin="round"/><path d="M30 30V47" stroke="#1f1b16" stroke-width="3" stroke-linecap="round"/><circle cx="48" cy="12" r="3.2" fill="#fffaf0" stroke="#1f1b16" stroke-width="2"/></svg>"""


# --- PAGE CONFIG ---
st.set_page_config(
    page_title=f"{BRAND_NAME} | Kubernetes Docs Assistant",
    page_icon="🐙",
    layout="wide",
)

# --- AVATARS ---
AI_AVATAR = "🐙"
USER_AVATAR = "🧑‍💻"


# --- THEME (UI ONLY) ---
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --paper: #f6efe1;
    --paper-2: #fffaf0;
    --ink: #1f1b16;
    --ink-soft: #5b5246;
    --tomato: #e8553d;
    --mustard: #f2b83d;
    --butter: #ffe08a;
    --mint: #a8dcc3;
    --sky: #b9d3ff;
    --blush: #f8bdd0;
    --ocean: #2b59c3;
}

::selection { background: var(--butter); color: var(--ink); }

html, body, .stApp,
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stSidebar"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink) !important;
}

/* ---------- Paper background ---------- */
.stApp {
    background-color: var(--paper);
    background-image: radial-gradient(rgba(31, 27, 22, 0.11) 1.2px, transparent 1.2px);
    background-size: 24px 24px;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.4rem; padding-bottom: 6rem; max-width: 1040px; }

/* default text colour inside markdown (zero specificity so classes below win) */
[data-testid="stMarkdownContainer"] :where(p, li, strong, em, h1, h2, h3, h4, td, th) { color: var(--ink); }

/* hide the invisible haptics component */
[data-testid="stElementContainer"]:has(iframe[height="0"]),
.element-container:has(iframe[height="0"]) {
    position: absolute; height: 0; width: 0; overflow: hidden; margin: 0; padding: 0;
}

/* ---------- Masthead ---------- */
.mast {
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; flex-wrap: wrap;
    padding: 14px 22px; margin-bottom: 30px;
    background: var(--paper-2);
    border: 2px solid var(--ink); border-radius: 18px;
    box-shadow: 5px 5px 0 var(--ink);
}
.mast-left { display: flex; align-items: center; gap: 14px; }
.mast-logo { display: flex; transform: rotate(-5deg); transition: transform .3s ease; }
.mast-logo:hover { transform: rotate(7deg) scale(1.08); }
.mast-name {
    font-family: 'Fraunces', serif; font-weight: 800; font-size: 1.95rem;
    line-height: 1; letter-spacing: -.02em; color: var(--ink);
}
.mast-name em { font-style: normal; color: var(--tomato); }
.mast-tag { font-family: 'Caveat', cursive; font-size: 1.3rem; color: var(--ink-soft); margin-top: 3px; }
.mast-right { display: flex; gap: 10px; flex-wrap: wrap; }
.sticker {
    font-size: .82rem; font-weight: 700; color: var(--ink);
    padding: 7px 14px; border: 2px solid var(--ink); border-radius: 999px;
    box-shadow: 2px 2px 0 var(--ink);
}
.s1 { background: var(--mint); transform: rotate(-2deg); }
.s2 { background: var(--sky); transform: rotate(1.5deg); }
.s3 { background: var(--blush); transform: rotate(-1deg); }
.dot {
    display: inline-block; width: 9px; height: 9px; margin-right: 7px;
    border-radius: 50%; background: #1faa59; border: 1.5px solid var(--ink);
    animation: blink 1.6s ease-in-out infinite;
}
@keyframes blink { 50% { opacity: .35; } }

/* ---------- Hero poster ---------- */
.hero {
    position: relative;
    padding: 40px 38px 36px; margin-bottom: 34px;
    background: var(--paper-2);
    border: 2px solid var(--ink); border-radius: 24px;
    box-shadow: 8px 8px 0 var(--ink);
}
.hero-kicker {
    display: inline-block; font-family: 'Caveat', cursive; font-size: 1.7rem;
    font-weight: 700; color: var(--tomato); transform: rotate(-2deg); margin-bottom: 6px;
}
.hero h1 {
    font-family: 'Fraunces', serif; font-weight: 800;
    font-size: clamp(2rem, 5.2vw, 3.3rem); line-height: 1.1; letter-spacing: -.025em;
    margin: 0 0 18px 0; padding: 0; max-width: 700px; color: var(--ink);
}
.hl { background: linear-gradient(transparent 60%, var(--butter) 60%); padding: 0 6px; }
.squig { position: relative; display: inline-block; }
.squig svg { position: absolute; left: 0; bottom: -13px; width: 100%; height: 12px; }
.hero p { font-size: 1.1rem; line-height: 1.7; color: var(--ink-soft) !important; max-width: 600px; margin: 0; }
.badge-stamp {
    position: absolute; top: -20px; right: 28px;
    width: 108px; height: 108px; border-radius: 50%;
    display: grid; place-items: center; text-align: center; padding: 10px;
    background: var(--tomato); color: #fff;
    border: 2px solid var(--ink); box-shadow: 4px 4px 0 var(--ink);
    font-family: 'Caveat', cursive; font-weight: 700; font-size: 1.3rem; line-height: 1.05;
    transform: rotate(12deg);
}
.float { position: absolute; font-size: 2.1rem; animation: bob 4s ease-in-out infinite; }
.f1 { right: 170px; bottom: 34px; }
.f2 { right: 70px; bottom: 80px; animation-delay: .9s; }
.f3 { right: 250px; bottom: 90px; animation-delay: 1.7s; font-size: 1.6rem; }
@keyframes bob { 50% { transform: translateY(-10px) rotate(6deg); } }

/* ---------- Section labels ---------- */
.sec {
    display: inline-block; font-family: 'Caveat', cursive; font-size: 1.9rem; font-weight: 700;
    color: var(--ink); margin: 4px 4px 16px 4px; transform: rotate(-1deg);
}

/* ---------- Sticky notes ---------- */
.notes { display: grid; grid-template-columns: repeat(2, 1fr); gap: 26px 22px; margin-bottom: 36px; padding: 6px 4px; }
.note {
    position: relative; padding: 24px 22px 18px;
    border: 2px solid var(--ink); border-radius: 6px 6px 16px 6px;
    box-shadow: 5px 5px 0 var(--ink);
    transition: transform .25s ease, box-shadow .25s ease;
}
.note:hover { transform: rotate(0deg) translateY(-6px); box-shadow: 8px 11px 0 var(--ink); }
.n1 { background: var(--butter); transform: rotate(-1.2deg); }
.n2 { background: var(--sky);    transform: rotate(.9deg); }
.n3 { background: var(--blush);  transform: rotate(.7deg); }
.n4 { background: var(--mint);   transform: rotate(-.8deg); }
.pin { position: absolute; top: -17px; left: 50%; margin-left: -12px; font-size: 1.6rem; filter: drop-shadow(1px 2px 0 rgba(0,0,0,.25)); }
.note-emoji { font-size: 2rem; margin-bottom: 6px; }
.note-q { font-family: 'Fraunces', serif; font-weight: 700; font-size: 1.14rem; line-height: 1.3; color: var(--ink); }
.note-hint { font-family: 'Caveat', cursive; font-size: 1.25rem; color: var(--ink-soft); margin-top: 8px; }

/* ---------- Steps ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 12px; }
.step {
    display: flex; gap: 14px; align-items: flex-start; padding: 16px;
    background: var(--paper-2); border: 2px dashed var(--ink); border-radius: 14px;
}
.step-n {
    flex-shrink: 0; width: 40px; height: 40px; border-radius: 50%;
    display: grid; place-items: center;
    background: var(--tomato); color: #fff; border: 2px solid var(--ink); box-shadow: 2px 2px 0 var(--ink);
    font-family: 'Fraunces', serif; font-weight: 800;
}
.step-t { font-family: 'Fraunces', serif; font-weight: 700; color: var(--ink); margin-bottom: 3px; }
.step-d { font-size: .9rem; line-height: 1.5; color: var(--ink-soft); }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--paper-2); border-right: 2px solid var(--ink); }
[data-testid="stSidebar"] hr { border-color: var(--ink); border-top-width: 2px; opacity: .9; }
[data-testid="stSidebar"] h1 { font-family: 'Fraunces', serif; font-size: 1.15rem; font-weight: 700; color: var(--ink); }
.side-brand { display: flex; align-items: center; gap: 12px; margin: 2px 0 10px 0; }
.side-name { font-family: 'Fraunces', serif; font-weight: 800; font-size: 1.6rem; line-height: 1; color: var(--ink); }
.side-name em { font-style: normal; color: var(--tomato); }
.side-sub { font-family: 'Caveat', cursive; font-size: 1.15rem; color: var(--ink-soft); }
.side-sec { font-family: 'Caveat', cursive; font-size: 1.55rem; font-weight: 700; color: var(--ink); margin: 20px 0 8px 0; }
.tip {
    background: var(--butter); border: 2px solid var(--ink); border-radius: 6px 6px 14px 6px;
    box-shadow: 4px 4px 0 var(--ink); padding: 14px 16px; transform: rotate(-1deg);
    font-size: .92rem; line-height: 1.55; color: var(--ink);
}
.cheat {
    background: #ffffff; border: 2px solid var(--ink); border-radius: 12px;
    box-shadow: 3px 3px 0 var(--ink); padding: 10px 12px;
    font-family: 'JetBrains Mono', monospace; font-size: .74rem; line-height: 1.95; color: var(--ink);
}
.cheat div { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cheat span { color: var(--tomato); font-weight: 500; }
.side-foot { margin-top: 22px; text-align: center; font-family: 'Caveat', cursive; font-size: 1.2rem; color: var(--ink-soft); line-height: 1.3; }

[data-testid="stAlert"] {
    background: #ffffff !important; border: 2px solid var(--ink) !important;
    border-radius: 12px; box-shadow: 3px 3px 0 var(--ink);
}
[data-testid="stAlert"] * { color: var(--ink) !important; }

/* ---------- Buttons (with a real "press" feel) ---------- */
.stButton > button {
    background: #ffffff; color: var(--ink);
    border: 2px solid var(--ink); border-radius: 12px;
    font-weight: 700; padding: .65rem 1rem;
    box-shadow: 3px 3px 0 var(--ink);
    transition: transform .12s ease, box-shadow .12s ease;
}
.stButton > button:hover { transform: translate(-1px, -1px); box-shadow: 5px 5px 0 var(--ink); border-color: var(--ink); color: var(--ink); }
.stButton > button:active { transform: translate(3px, 3px); box-shadow: 0 0 0 var(--ink); }
.stButton > button[kind="primary"] { background: var(--tomato); color: #ffffff; }
.stButton > button[kind="primary"]:hover { color: #ffffff; }
.stButton > button p { color: inherit !important; font-weight: 700; }
.km-pop { animation: pop .24s ease; }
@keyframes pop { 0% { transform: scale(1); } 40% { transform: scale(.94); } 100% { transform: scale(1); } }

/* ---------- Chat messages ---------- */
[data-testid="stChatMessage"] {
    position: relative;
    background: #fffdf7; border: 2px solid var(--ink); border-radius: 16px;
    box-shadow: 5px 5px 0 var(--ink);
    padding: 18px 20px; margin-bottom: 24px;
    animation: rise .4s ease both;
}
@keyframes rise {
    from { opacity: 0; transform: translateY(12px) rotate(-.4deg); }
    to   { opacity: 1; transform: none; }
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: var(--butter); }
/* tape strip on assistant answers */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"])::before {
    content: ""; position: absolute; top: -12px; left: 30px; width: 84px; height: 22px;
    background: rgba(232, 85, 61, .55); border: 1px solid rgba(31, 27, 22, .25);
    transform: rotate(-3deg);
}
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
    background: #ffffff !important; border: 2px solid var(--ink); border-radius: 50%;
    box-shadow: 2px 2px 0 var(--ink);
}

/* ---------- Answer typography ---------- */
[data-testid="stChatMessage"] :where(p, li, td, th, h1, h2, h3, h4, strong, em) { color: var(--ink) !important; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { font-size: 1.05rem; line-height: 1.75; }
[data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3, [data-testid="stChatMessage"] h4 {
    font-family: 'Fraunces', serif; font-weight: 700; margin-top: 1rem; padding-top: 0;
}
[data-testid="stChatMessage"] h3 { color: var(--ocean) !important; font-size: 1.25rem; }
[data-testid="stChatMessage"] a {
    color: var(--ocean) !important; text-decoration: none; font-weight: 600;
    background: linear-gradient(transparent 62%, var(--butter) 62%);
}
[data-testid="stChatMessage"] ul, [data-testid="stChatMessage"] ol { padding-left: 1.4rem; }
[data-testid="stChatMessage"] li::marker { color: var(--tomato); font-weight: 700; }
[data-testid="stChatMessage"] :not(pre) > code {
    background: #fff0b8; color: var(--ink) !important;
    border: 1.5px solid var(--ink); padding: 1px 7px; border-radius: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: .88em;
}
[data-testid="stChatMessage"] pre, [data-testid="stCode"] pre {
    background: #fff7dc !important;
    border: 2px solid var(--ink); border-radius: 12px; box-shadow: 3px 3px 0 var(--ink);
}
[data-testid="stChatMessage"] pre code {
    font-family: 'JetBrains Mono', monospace; font-size: .9rem; line-height: 1.65;
}
[data-testid="stChatMessage"] table { border-collapse: separate; border-spacing: 0; width: 100%; border: 2px solid var(--ink); border-radius: 12px; overflow: hidden; }
[data-testid="stChatMessage"] th { background: var(--butter); padding: 10px 14px; text-align: left; }
[data-testid="stChatMessage"] td { padding: 10px 14px; border-top: 2px solid var(--ink); background: #ffffff; }
[data-testid="stChatMessage"] blockquote {
    border-left: 4px solid var(--tomato); background: #fff3c4;
    padding: 8px 16px; border-radius: 0 10px 10px 0;
}

/* ---------- Thinking box + sources ---------- */
[data-testid="stStatus"] details, [data-testid="stExpander"] details {
    background: #ffffff !important; border: 2px dashed var(--ink) !important; border-radius: 14px !important;
}
[data-testid="stStatus"] summary, [data-testid="stExpander"] summary { font-weight: 700; color: var(--ink); }
[data-testid="stStatus"] summary:hover, [data-testid="stExpander"] summary:hover { color: var(--tomato); }
[data-testid="stStatus"] p { color: var(--ink-soft) !important; font-size: .94rem; }
[data-testid="stExpander"] [data-testid="stAlert"] { background: var(--paper-2) !important; box-shadow: none; }

/* ---------- Answer stamps ---------- */
.meta-bar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.meta-bar span {
    font-family: 'JetBrains Mono', monospace; font-size: .74rem; font-weight: 500; color: var(--ink);
    padding: 5px 10px; background: var(--butter);
    border: 2px dashed var(--ink); border-radius: 8px; transform: rotate(-1deg);
}
.meta-bar span:nth-child(2) { background: var(--sky);  transform: rotate(1deg); }
.meta-bar span:nth-child(3) { background: var(--mint); transform: rotate(-.6deg); }

/* ---------- Chat input ---------- */
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: var(--paper) !important; }
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 2px solid var(--ink) !important; border-radius: 16px !important;
    box-shadow: 5px 5px 0 var(--ink);
    transition: box-shadow .2s ease;
}
[data-testid="stChatInput"] > div { background: transparent !important; border: none !important; }
[data-testid="stChatInput"]:focus-within { box-shadow: 7px 7px 0 var(--tomato); }
[data-testid="stChatInput"] textarea { color: var(--ink) !important; font-size: 1.03rem; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--ink-soft); opacity: 1; }
[data-testid="stChatInputSubmitButton"] { background: var(--tomato) !important; color: #ffffff !important; border-radius: 10px; }

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: var(--ink); border-radius: 8px; border: 2px solid var(--paper); }

/* ---------- Small screens ---------- */
@media (max-width: 800px) {
    .notes, .steps { grid-template-columns: 1fr; }
    .float, .badge-stamp { display: none; }
    .hero { padding: 28px 22px 28px; }
    .mast { padding: 12px 16px; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- HAPTIC FEEDBACK (UI ONLY) ---
# Vibrates on taps, on sending a message and when an answer arrives.
# Works on phones/browsers that support the Vibration API (mostly Android).
# Everywhere else you still get the visual "press" animation on buttons.
HAPTIC_JS = """
<script>
(function () {
  try {
    var P = window.parent, doc = P.document;
    if (doc.__kmCleanup) { try { doc.__kmCleanup(); } catch (e) {} }
    var last = 0;
    var buzz = function (pattern, gap) {
      var now = Date.now();
      if (now - last < (gap || 120)) return;
      last = now;
      try { if (P.navigator && P.navigator.vibrate) P.navigator.vibrate(pattern); } catch (e) {}
    };
    var onDown = function (e) {
      var el = e.target && e.target.closest
        ? e.target.closest('button, [role="button"], summary, [data-testid="stChatInputSubmitButton"]')
        : null;
      if (!el) return;
      buzz(14);
      el.classList.remove('km-pop'); void el.offsetWidth; el.classList.add('km-pop');
      setTimeout(function () { el.classList.remove('km-pop'); }, 260);
    };
    var onKey = function (e) {
      var t = e.target;
      if (t && t.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey) buzz([16, 30, 16]);
    };
    var obs = new P.MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var added = muts[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          var n = added[j];
          if (n.nodeType !== 1) continue;
          var hit = (n.classList && n.classList.contains('meta-bar')) || (n.querySelector && n.querySelector('.meta-bar'));
          if (hit) { buzz([18, 40, 18, 40, 36], 600); return; }
        }
      }
    });
    doc.addEventListener('pointerdown', onDown, true);
    doc.addEventListener('keydown', onKey, true);
    obs.observe(doc.body, { childList: true, subtree: true });
    doc.__kmCleanup = function () {
      doc.removeEventListener('pointerdown', onDown, true);
      doc.removeEventListener('keydown', onKey, true);
      obs.disconnect();
    };
  } catch (e) {}
})();
</script>
"""
components.html(HAPTIC_JS, height=0)


def meta_bar(meta):
    """Small stamps shown under each answer."""
    return (
        '<div class="meta-bar">'
        f'<span>⏱ answered in {meta["time"]}s</span>'
        f'<span>📄 {meta["sources"]} sources</span>'
        f'<span>🧠 {meta["steps"]} reasoning steps</span>'
        "</div>"
    )


# --- SESSION MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logfire.info(f"✨ New User Session Created: {st.session_state.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = []


# --- SIDEBAR ---
with st.sidebar:
    st.markdown(
        f'<div class="side-brand">{brand_logo(46)}'
        f'<div><div class="side-name">{BRAND_NAME}<em>.</em></div>'
        '<div class="side-sub">your k8s docs buddy 🐙</div></div></div>',
        unsafe_allow_html=True,
    )
    st.title("🧠 Agent OS")
    st.markdown("---")
    st.success(f"Logfire: {LOGFIRE_STATUS}")
    st.info(f"Memory ID: {st.session_state.session_id[:8]}")
    
    if st.button("🗑️ Clear History & Memory", width="stretch", type="primary"):
        logfire.warn(f"🗑️ Memory Wipe Triggered for session: {st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    tip = TIPS[int(st.session_state.session_id[:4], 16) % len(TIPS)]
    st.markdown(
        '<div class="side-sec">💡 Tip of the moment</div>'
        f'<div class="tip">{tip}</div>'
        '<div class="side-sec">🧰 kubectl pocket cheatsheet</div>'
        '<div class="cheat">'
        "<div><span>$</span> kubectl get pods</div>"
        "<div><span>$</span> kubectl describe pod &lt;name&gt;</div>"
        "<div><span>$</span> kubectl logs &lt;pod&gt; -f</div>"
        "<div><span>$</span> kubectl apply -f file.yaml</div>"
        "<div><span>$</span> kubectl rollout undo deploy/&lt;name&gt;</div>"
        "</div>"
        '<div class="side-foot">made with ☕ and way too many pods<br>📳 haptics on supported phones</div>',
        unsafe_allow_html=True,
    )

# --- MAIN CHAT ---
# Masthead with logo and website name
st.markdown(
    '<div class="mast">'
    f'<div class="mast-left"><div class="mast-logo">{brand_logo(56)}</div>'
    f'<div><div class="mast-name">{BRAND_NAME}<em>.</em></div>'
    f'<div class="mast-tag">{BRAND_TAGLINE}</div></div></div>'
    '<div class="mast-right">'
    '<span class="sticker s1"><span class="dot"></span>online</span>'
    '<span class="sticker s2">📘 k8s docs</span>'
    '<span class="sticker s3">🔒 private</span>'
    "</div></div>",
    unsafe_allow_html=True,
)

# Welcome / empty state (disappears as soon as a question is asked)
empty_slot = st.empty()
if not st.session_state.messages:
    empty_slot.markdown(
        '<div class="hero">'
        '<div class="badge-stamp">docs<br>backed<br>answers ✅</div>'
        '<span class="float f1">🚢</span><span class="float f2">📦</span><span class="float f3">⚙️</span>'
        '<div class="hero-kicker">hey there, cluster wrangler! 👋</div>'
        '<h1>Got a <span class="hl">Kubernetes</span> question? '
        '<span class="squig">Just ask.'
        '<svg viewBox="0 0 200 12" preserveAspectRatio="none"><path d="M2 8 Q 14 0 26 8 T 50 8 T 74 8 T 98 8 T 122 8 T 146 8 T 170 8 T 198 8" fill="none" stroke="#e8553d" stroke-width="4" stroke-linecap="round"/></svg>'
        "</span></h1>"
        "<p>From Pods and Deployments to networking and security, I dig through the Kubernetes docs, "
        "think out loud so you can follow along, and show you exactly where each answer came from. 🔍</p>"
        "</div>"
        '<div class="sec">📝 Not sure where to start? Try one of these</div>'
        '<div class="notes">'
        '<div class="note n1"><span class="pin">📌</span><div class="note-emoji">🧩</div>'
        '<div class="note-q">What is the difference between a Pod and a Deployment?</div>'
        '<div class="note-hint">a classic, ask away ↓</div></div>'
        '<div class="note n2"><span class="pin">📌</span><div class="note-emoji">🌐</div>'
        '<div class="note-q">How do I expose an app using a Service or Ingress?</div>'
        '<div class="note-hint">get traffic in ↓</div></div>'
        '<div class="note n3"><span class="pin">📌</span><div class="note-emoji">🔐</div>'
        '<div class="note-q">How do ConfigMaps and Secrets work?</div>'
        '<div class="note-hint">keep configs tidy ↓</div></div>'
        '<div class="note n4"><span class="pin">📌</span><div class="note-emoji">🔄</div>'
        '<div class="note-q">Explain how rolling updates and rollbacks work</div>'
        '<div class="note-hint">ship without fear ↓</div></div>'
        "</div>"
        '<div class="sec">🛠️ How it works</div>'
        '<div class="steps">'
        '<div class="step"><div class="step-n">1</div><div><div class="step-t">You ask ✍️</div>'
        '<div class="step-d">Type your question in plain language below.</div></div></div>'
        '<div class="step"><div class="step-n">2</div><div><div class="step-t">I dig 🔎</div>'
        '<div class="step-d">The agent searches the docs and picks the best chunks.</div></div></div>'
        '<div class="step"><div class="step-n">3</div><div><div class="step-t">You verify ✅</div>'
        '<div class="step-d">Open the sources to see where each answer came from.</div></div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


# Display history
for message in st.session_state.messages:
    avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message.get("meta"):
            st.markdown(meta_bar(message["meta"]), unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Ask anything about Kubernetes... 🚀"):
    empty_slot.empty()
    # START TRACE: User Interaction
    with logfire.span("💬 User Chat Interaction", user_query=prompt, session_id=st.session_state.session_id):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # Assistant Response
        with st.chat_message("assistant", avatar=AI_AVATAR):
            with st.status("🔍 Agent is thinking...", expanded=True) as status:
                try:
                    # DISTRIBUTED TRACE: Calling Backend
                    with logfire.span("📡 Calling RAG Backend"):
                        # Get backend URL from env, or default to local if not set
                        base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                        url = f"{base_url}/query"
                        payload = {"q": prompt, "thread_id": st.session_state.session_id}
                        t_start = time.time()
                        response = requests.post(url, json=payload, timeout=60)
                        data = response.json()
                    
                    # Show Reasoning Steps from Backend
                    steps = data.get("thought_process", [])
                    for step in steps:
                        st.write(f"⚙️ {step}")
                    
                    status.update(label="✅ Answer Synthesized", state="complete", expanded=False)
                    
                    # --- SHOW SOURCES (NESTED EXPANDABLES) ---
                    sources = data.get("sources", [])
                    if sources:
                        with st.expander("📄 View Retrieved Context (Sources)"):
                            for i, source in enumerate(sources):
                                # Create a preview title for each chunk
                                preview = source[:100].replace("\n", " ") + "..."
                                with st.expander(f"Chunk {i+1}: {preview}"):
                                    st.info(source)
                except Exception as e:
                    logfire.error(f"❌ UI-Backend Connection Failed: {e}")
                    status.update(label="❌ Connection Failed", state="error")
                    st.error("Backend Offline.")
                    st.stop()

            # Final Answer Streaming
            answer_placeholder = st.empty()
            full_answer = data.get("answer", "No response.")
            
            curr_text = ""
            for char in full_answer:
                curr_text += char
                answer_placeholder.markdown(curr_text + "▌")
                time.sleep(0.005)
            
            answer_placeholder.markdown(full_answer)
            meta = {"time": round(time.time() - t_start, 1), "sources": len(sources), "steps": len(steps)}
            st.markdown(meta_bar(meta), unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_answer, "meta": meta})
            logfire.info("✅ Chat cycle completed successfully.")