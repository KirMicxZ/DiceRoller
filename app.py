import streamlit as st
import random
import re
from datetime import datetime
from dice_utils import solve_expression


def _strip_arrows(s: str) -> str:
    """Remove common left/right arrow glyphs from a string for display."""
    if not isinstance(s, str):
        return s
    for ch in ["\u2190", "\u2192", "←", "→", "<-", "->"]:
        s = s.replace(ch, "")
    return s

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Minimalist DnD Roller", page_icon="🎲", layout="centered")

# CSS: เน้นผลลัพธ์ตัวใหญ่ และซ่อน Element ที่ไม่จำเป็น
st.markdown("""
    <style>
    /* Import a pixel-style webfont from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    /* Pixel font with sensible fallbacks (emoji & system fonts) so arrows/emojis display */
    :root { --pixel-font: 'Press Start 2P', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }

    /* Apply pixel font across the entire page (use !important to override Streamlit defaults) */
    html, body, * {
        font-family: var(--pixel-font) !important;
    }

    .result-box { 
        padding: 10px; 
        border-radius: 12px; 
        background-color: #f0f2f6; 
        margin-top: 10px; 
        margin-bottom: 20px; 
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .big-number { 
        font-size: 3.5rem; 
        font-weight: 800; 
        color: #FF4B4B; 
        line-height: 1;
        margin: 10px 0;
    }
    .formula-text { font-size: 0.9rem; color: #555; font-family: var(--pixel-font); }
    .details-text { font-size: 0.8rem; color: #888; font-family: var(--pixel-font); }
    .stTextInput input { font-size: 0.9rem; text-align: center; font-family: var(--pixel-font) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชัน Logic (Dice + Math + Functions) ---
 

# --- 3. จัดการ Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 4. ส่วนแสดงผล UI ---
st.title("🎲 Dice Command Line")

# Input Form เดียว ตรงกลาง
with st.form("main_form"):
    formula_input = st.text_input("Enter a dice expression (e.g. 2d6+3)", value="1d20")
    submit_btn = st.form_submit_button("ROLL", type="primary", use_container_width=True)

if submit_btn:
    res, math_str, details = solve_expression(formula_input)
    
    if res is not None:
        # บันทึกประวัติ
        st.session_state.history.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "formula": formula_input,
            "result": res,
            "details": details,
            "math": math_str
        })
    else:
        st.error(math_str)

# --- 5. แสดงผลลัพธ์ล่าสุด ---
if st.session_state.history:
    latest = st.session_state.history[0]
    
    # sanitize displayed strings to remove arrow glyphs
    latest_formula = _strip_arrows(latest.get('formula', ''))
    latest_details = _strip_arrows(latest.get('details', ''))
    latest_math = _strip_arrows(latest.get('math', ''))

    st.markdown(f"""
        <div class="result-box">
            <div class="formula-text">INPUT: {latest_formula}</div>
            <div class="big-number">{latest['result']}</div>
            <div class="details-text">Rolls: {latest_details} <br> Logic: {latest_math}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # History (compact)

# --- 6. คู่มือการใช้งาน (Instruction Manual) ---
st.divider()
st.markdown("""
### 📖 Quick Cheat Sheet

Type dice expressions in the input box. Examples:

**1. Basic Rolls**
- `d20` : roll one 20-sided die
- `2d6` : roll two 6-sided dice
- `1d8 + 5` : roll 1d8 then add 5

**2. Math & Modifiers**
- `2d6 + 1d4` : combine multiple rolls
- `(1d10 + 5) * 2` : multiply the total (e.g. critical)
- `4d6 / 2` : integer division (the app converts `/` to `//`)

**3. Advanced (Advantage / Disadvantage)**
- `max(d20, d20)` : Advantage (roll twice, take the higher)
- `min(d20, d20)` : Disadvantage (roll twice, take the lower)
- `max(2d6)` : shorthand — roll `2d6` twice and take the higher total
- `max(2d6) + 2` : advantage on `2d6`, then add +2 modifier

**Notes:**
- Use `x` or `*` for multiplication (both supported)
- Division `/` is treated as integer division (`//`) by this app-
""")