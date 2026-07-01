import streamlit as st
import fitz  # PyMuPDF
import re
import os
import tempfile
import zipfile
import io
import pytesseract
from PIL import Image
import sqlite3
import datetime

# --- CONFIGURATION & USERS DATA ---
st.set_page_config(page_title="AuTo Split",
                    page_icon="📄", 
                    layout="centered",
                    menu_items={
                        'About': "Developed by Pranav Vedula | Department of CSE | Aditya University © 2026"
                    },
                    )

# The list of users provided to populate the SQLite database initially
INITIAL_USERS = [
    ("Dr.T.Sudha Rani", "sudharani.tirukoti@adityauniversity.in", "Sudha@123"),
    ("Dr.K.Chandra Sekhar", "chandrasekhark@adityauniversity.in", "sekhar@123"),
    ("Dr.J.Hari", "harij@adityauniversity.in", "hari@123"),
    ("Dr.V Vaitheeshwaran", "vaitheeshwaranv@adityauniversity.in", "vaitheesh@123"),
    ("DR.JALAIAH SAIKAM", "jalaiahs@adityauniversity.in", "saikam@123"),
    ("DR. K NAGARAJU", "nagarajuk@adityauniversity.in", "nagaraju@123"),
    ("Mrs.N.Akhila", "akhila.nalla@adityauniversity.in", "akhila@123"),
    ("Mrs.K.Vydehi", "Kasichainula.Vydehi@adityauniversity.in", "vydehi@123"),
    ("Mr.M. SRINU", "srinu.marni@adityauniversity.in", "srinu@123"),
    ("Mrs.P.Srilatha", "srilatha.p@adityauniversity.in", "srilatha@123"),
    ("Mr.K.Govinda Raju", "govindaraju.kaladi@adityauniversity.in", "govinda@123"),
    ("Mr.G.Uma Mahesh", "umamaheshg@adityauniversity.in", "umamahesh@123"),
    ("Mr.U.V.Ramesh", "veerarameshu@adityauniversity.in", "ramesh@123"),
    ("Mr.G.Appala Raju", "appalarajug@adityauniversity.in", "appala@123"),
    ("Mr.P.Anil Kumar", "anilkumarp@adityauniversity.in", "anil@123"),
    ("Ms.A.Sophia", "sophiaa@adityauniversity.in", "sophia@123"),
    ("Mr.Ch.Bhanu Prakash", "bhanuprakashch@adityauniversity.in", "bhanu@123"),
    ("Mr.K.Ramesh", "rameshk@adityauniversity.in", "kramesh@123"),
    ("Mrs.R PADMA SRI", "padmasrirananki@adityauniversity.in", "padma@123"),
    ("Ms.M SUPRAJA", "suprajam@adityauniversity.in", "supraja@123"),
    ("Bh.Sai Venkata Ganesh", "svganeshb@adityauniversity.in", "ganesh@123"),
    ("Dr. K V SIVA PRASAD REDDY", "kvsivaprasadreddy@adityauniversity.in", "siva@123"),
    ("Pranav Vedula", "24b11cs355@adityauniversity.in", "1234"),
    ("Rohith P", "24b11cs356@adityauniversity.in", "12345"),
    ("P Kaveri", "24b11cs352@adityauniversity.in", "12345"),
    ("Pranav Vedula", "vedulapranav@gmail.com", "1234"),
    ("Dr.P.Subba Rao", "subbaraop@adityauniversity.in", "subbarao@123"),
    ("Ramcharan", "24b11cs371@adityauniversity.in", "1234"),
    ("Mr.M.Kalyan Ram", "kalyanram.mylavarapu@adityauniversity.in", "kalyan@123"),
    ("Mrs. B Hema Nagamani", "hnagamanib@adityauniversity.in", "hema@123"),
    ("PV","pv@gmail.com","pv@123")
]

DB_NAME = "autosplit.db"
WEEKLY_LIMIT = 5

# --- DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    name TEXT,
                    password TEXT
                )''')
    # Create Usage table to track splits
    c.execute('''CREATE TABLE IF NOT EXISTS usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    split_date TIMESTAMP
                )''')
    
    # Populate users if the table is empty
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', INITIAL_USERS)
    
    conn.commit()
    conn.close()

def authenticate(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT name FROM users WHERE email=? AND password=?', (email, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_weekly_usage(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    c.execute('SELECT COUNT(*) FROM usage WHERE email=? AND split_date >= ?', (email, one_week_ago))
    count = c.fetchone()[0]
    conn.close()
    return count

def log_usage(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO usage (email, split_date) VALUES (?, ?)', (email, datetime.datetime.now()))
    conn.commit()
    conn.close()

# Initialize the database on app load
init_db()

# --- HELPER FUNCTIONS ---
def extract_text_from_page(page):
    """Extracts text from a PyMuPDF page, falling back to OCR if text is sparse."""
    text = page.get_text("text", sort=True)
    if len(text.strip()) < 15:
        try:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            text += "\n" + ocr_text
        except Exception as e:
            st.warning(f"OCR failed on a page. Ensure Tesseract is installed. Error: {e}")
    return text

def find_roll_number(text):
    pattern = r'(?i)roll\s*n(?:o|umber)[.\s]*[:\-]?[\s\n]*([A-Za-z0-9]{5,20})'
    match = re.search(pattern, text)
    if match:
        extracted = match.group(1).strip().upper()
        if extracted not in ["BRANCH", "CAMPUS", "STUDENT", "NAME", "DETAILS"]:
            return extracted
    return None

# --- STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""

if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- AUTHENTICATION UI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>Login </h1>", unsafe_allow_html=True)
    st.markdown("""
               <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="https://ik.imagekit.io/syustaging/SYU_PREPROD/LOGO_0H0roO3hk.webp?tr=w-3840" 
                 alt="Aditya University Logo" 
                 style="width: 220px; height: auto;">
        </div>
                """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("User ID", placeholder="e.g., pranavvedula@adityauniversity.in")
        password = st.text_input("Password (your_name@123)", type="password", placeholder="e.g., pranav@123")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            name = authenticate(email, password)
            if name:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.success(f"Welcome, {name}!")
                st.rerun()
            else:
                st.error("Invalid Email or Password. Please try again.")
    st.stop() 

# --- SIDEBAR LOGOUT & USAGE STATS ---
splits_used = get_weekly_usage(st.session_state.user_email)
splits_remaining = max(0, WEEKLY_LIMIT - splits_used)

with st.sidebar:
    st.write(f"👤 **{st.session_state.user_name}**")
    st.write(f"✉️ {st.session_state.user_email}")
    st.divider()
    
    st.metric("Weekly Limits Used", f"{splits_used} / {WEEKLY_LIMIT}")
    if splits_remaining == 0:
        st.error("You have reached your limit for this week.")
    else:
        st.success(f"You have {splits_remaining} splits remaining this week.")
        
    st.divider()
    if st.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.rerun()

# --- MAIN UI (APP LOGIC) ---
st.title("📄 AutoSplit")
st.subheader("Department Of Computer Science Engineering - Aditya University")
st.markdown("""
Upload a bulk PDF containing multiple student records.
*(Max file size: 15MB)*
""")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.last_uploaded_file = uploaded_file.name
        st.session_state.zip_buffer = None
        st.session_state.summary = None

    MAX_SIZE_MB = 15
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > MAX_SIZE_MB:
        st.error(f"File size is {file_size_mb:.2f}MB, which exceeds the 15MB limit. Please upload a smaller file.")
    else:
        st.success(f"File '{uploaded_file.name}' loaded successfully ({file_size_mb:.2f}MB).")
        
        # --- ROLL NUMBER RANGE FILTER UI ---
        st.markdown("### Filter by Roll Number (Optional)")
        st.write("Specify a range to download papers only for specific students. Leave blank to process all.")
        col1, col2 = st.columns(2)
        with col1:
            start_roll = st.text_input("Start Roll Number", placeholder="e.g., 24B11CS001").strip().upper()
        with col2:
            end_roll = st.text_input("End Roll Number", placeholder="e.g., 24B11CS200").strip().upper()
        
        st.divider()

        if st.session_state.zip_buffer is None:
            if st.button("Split Now ✂️", type="secondary"):
                
                # Check limits before processing
                if splits_remaining <= 0:
                    st.error(f"Limit Reached! You have already used all {WEEKLY_LIMIT} allowed splits for the past 7 days.")
                else:
                  
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total_pages = 0
                    created_pdfs = 0
                    skipped_pages = []
                    out_of_range_pages = []
                    duplicates_handled = 0
                    
                    roll_number_counts = {}
                    
                    # Process the PDF using Temporary Files
                    with tempfile.TemporaryDirectory() as temp_dir:
                        try:
                            # Load PDF with PyMuPDF
                            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                            total_pages = len(pdf_document)
                            
                            status_text.info("Extracting pages...")
                            
                            for page_num in range(total_pages):
                                page = pdf_document.load_page(page_num)
                                
                                # 1. Extract Text & Roll Number
                                text = extract_text_from_page(page)
                                roll_number = find_roll_number(text)
                                
                                if roll_number:
                                    # 2. Check if the Roll Number is within the specified range
                                    in_range = True
                                    if start_roll and roll_number < start_roll:
                                        in_range = False
                                    if end_roll and roll_number > end_roll:
                                        in_range = False
                                        
                                    if in_range:
                                        # 3. Handle Duplicates
                                        if roll_number in roll_number_counts:
                                            roll_number_counts[roll_number] += 1
                                            duplicates_handled += 1
                                            final_roll_number = f"{roll_number}_{roll_number_counts[roll_number]}"
                                        else:
                                            roll_number_counts[roll_number] = 0
                                            final_roll_number = roll_number
                                        
                                        # 4. Save as individual PDF
                                        output_filename = f"{final_roll_number}.pdf"
                                        output_filepath = os.path.join(temp_dir, output_filename)
                                        
                                        # Create a new PDF with just this page
                                        new_pdf = fitz.open()
                                        new_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                                        new_pdf.save(output_filepath)
                                        new_pdf.close()
                                        
                                        created_pdfs += 1
                                    else:
                                        out_of_range_pages.append(page_num + 1)
                                else:
                                    skipped_pages.append(page_num + 1)
                                
                                # Update Progress
                                progress = (page_num + 1) / total_pages
                                progress_bar.progress(progress)
                                status_text.text(f"Processed page {page_num + 1} of {total_pages}...")
                            
                            pdf_document.close()
                            
                            # 5. Create ZIP archive in memory
                            status_text.info("Creating ZIP archive...")
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                for root, _, files in os.walk(temp_dir):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        zip_file.write(file_path, arcname=file)
                            
                            # Log usage into DB after successful processing
                            log_usage(st.session_state.user_email)
                            
                            # Store in session state to survive Streamlit widget interactions
                            st.session_state.zip_buffer = zip_buffer.getvalue()
                            st.session_state.summary = {
                                "total": total_pages,
                                "created": created_pdfs,
                                "skipped": skipped_pages,
                                "out_of_range": len(out_of_range_pages),
                                "duplicates": duplicates_handled
                            }
                            
                            status_text.success("Processing complete!")
                            st.rerun() 
                            
                        except Exception as e:
                            st.error(f"An error occurred during processing: {e}")

        # --- DISPLAY RESULTS & DOWNLOAD ---
        if st.session_state.summary is not None:
            summary = st.session_state.summary
            
            st.divider()
            st.subheader("Details")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Pages", summary["total"])
            col2.metric("PDFs Zipped", summary["created"])
            col3.metric("Out of Range", summary["out_of_range"])
            col4.metric("No Roll Found", len(summary["skipped"]))
            col5.metric("Duplicates", summary["duplicates"])
            
            if summary["skipped"]:
                with st.expander("⚠️ View Skipped Pages (No Roll Number Found)"):
                    st.write(f"Pages: {', '.join(map(str, summary['skipped']))}")
            
            if summary["created"] > 0:
                st.divider()
                st.download_button(
                    label="⬇️ Download Selected Papers (ZIP)",
                    data=st.session_state.zip_buffer,
                    file_name="filtered_student_papers.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.warning("No papers matched the given roll number range. Nothing to download.")

# --- FOOTER ---
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        left: 0;
        width: 100%;
        text-align: center;
        color: gray;
        font-size: 19px;
        padding: 10px;
        background-color: transparent;
    }
    </style>

    <div class="footer">
        Developed by Pranav Vedula | Department of CSE | Aditya University © 2026
    </div>
    """,
    unsafe_allow_html=True
)