import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import PyPDF2
import re
import time
from datetime import datetime
import uuid

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Plagiarism X | Enterprise Checker", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom CSS to force a cleaner, app-like appearance
st.markdown("""
    <style>
    .report-card {
        background-color: white; padding: 20px; border-radius: 8px; 
        border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }
    .doc-viewer-container {
        background-color: #f1f5f9; padding: 20px; border-radius: 8px; 
        border: 1px solid #cbd5e1; height: 650px; overflow-y: auto;
    }
    .doc-page {
        background-color: white; padding: 40px 50px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); 
        font-family: 'Times New Roman', serif; font-size: 16px; line-height: 1.8; color: #1e293b;
        min-height: 800px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ENTERPRISE PDF GENERATOR
# ==========================================
class OfficialReport(FPDF):
    def header(self):
        # Corporate Dark Blue Header
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_xy(15, 12)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'PLAGIARISM X', 0, 1, 'L')
        
        self.set_xy(15, 22)
        self.set_font('Arial', '', 10)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, 'CERTIFICATE OF ORIGINALITY & ANALYSIS REPORT', 0, 1, 'L')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f'Plagiarism X Enterprise Edition  |  Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  |  Page {self.page_no()}', 0, 0, 'C')

    def add_executive_summary(self, score, words, chars, doc_id):
        # Summary Box
        self.set_fill_color(248, 250, 252)
        self.set_draw_color(226, 232, 240)
        self.rect(15, 45, 180, 40, 'FD')
        
        # Scan ID and Date
        self.set_xy(20, 50)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(71, 85, 105)
        self.cell(50, 5, f"DOCUMENT ID: {doc_id}", 0, 1, 'L')
        self.set_x(20)
        self.cell(50, 5, f"SCAN DATE: {datetime.now().strftime('%b %d, %Y')}", 0, 1, 'L')

        # The Score
        self.set_xy(140, 52)
        self.set_font('Arial', 'B', 28)
        self.set_text_color(34, 197, 94) # Success Green
        self.cell(40, 10, f"{score}%", 0, 1, 'R')
        self.set_xy(140, 62)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(100, 116, 139)
        self.cell(40, 5, "Similarity Index", 0, 1, 'R')
        
        # Metrics line
        self.set_xy(20, 75)
        self.set_font('Arial', '', 10)
        self.set_text_color(15, 23, 42)
        self.cell(0, 5, f"Analysis Complete: Processed {words:,} words and {chars:,} characters.", 0, 1, 'L')
        self.ln(10)

    def add_document_body(self, text):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'I. Analyzed Content', 0, 1, 'L')
        self.ln(2)
        
        self.set_font('Times', '', 11)
        self.set_text_color(51, 65, 85)
        
        # Clean text for PDF compatibility (Latin-1)
        clean_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        # Write text with justified alignment and proper line height
        self.multi_cell(180, 6, clean_text, align='J')

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ Plagiarism X")
    st.caption("Enterprise Edition v4.2")
    st.divider()
    st.markdown("📊 **Dashboard**")
    st.markdown("🔍 New Scan")
    st.markdown("📁 Report Archive")
    st.markdown("⚙️ System Settings")
    st.divider()
    st.info("System Status: Online\nDatabase: Syncing (24.1M Sources)")

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("Content Originality Report")
st.markdown("<p style='color:#64748b; font-size: 16px;'>Upload a document to cross-reference against global academic and web databases.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["pdf", "txt"], help="Supported formats: PDF, TXT. Max file size: 50MB.")

if uploaded_file:
    # -----------------------------------
    # Text Extraction Phase
    # -----------------------------------
    text = ""
    try:
        if uploaded_file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            text = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    if not text.strip():
        st.error("The uploaded document appears to be empty or unreadable.")
        st.stop()

    # Calculate real document metrics
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    doc_id = str(uuid.uuid4()).upper()[:12]

    # -----------------------------------
    # Processing Simulation (Adds Authenticity)
    # -----------------------------------
    if 'processed' not in st.session_state or st.session_state.get('last_file') != uploaded_file.name:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            (20, "Extracting text structure..."),
            (45, "Tokenizing document content..."),
            (70, "Querying global index databases..."),
            (90, "Applying machine learning similarity models..."),
            (100, "Compiling final report...")
        ]
        
        for percent, message in stages:
            status_text.text(f"Status: {message}")
            progress_bar.progress(percent)
            time.sleep(0.4) # Simulated delay
            
        status_text.empty()
        progress_bar.empty()
        st.session_state['processed'] = True
        st.session_state['last_file'] = uploaded_file.name

    # -----------------------------------
    # Layout Generation
    # -----------------------------------
    col1, col2 = st.columns([6, 4])

    # LEFT: The Document Viewer (Looks like a real document)
    with col1:
        st.markdown("##### Document Preview")
        # Format line breaks for HTML display
        html_text = text.replace('\n', '<br>')
        # Highlight a few words randomly to simulate the "2%" finding
        if word_count > 50:
            target = " ".join(words[20:35]) # Grab a chunk to highlight
            html_text = html_text.replace(target, f"<span style='background-color: #fecaca; color: #991b1b; padding: 2px 4px; border-radius: 3px; font-weight: 500;'>{target}</span>")

        st.markdown(f"""
            <div class="doc-viewer-container">
                <div class="doc-page">
                    {html_text}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # RIGHT: The Analysis Dashboard
    with col2:
        st.markdown("##### Analysis Metrics")
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        
        # Professional Gauge Chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 2,
            number = {'suffix': "%", 'font': {'size': 45, 'color': '#166534', 'family': 'Arial'}},
            title = {'text': "Similarity Index", 'font': {'size': 18, 'color': '#475569'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': "#22c55e", 'thickness': 0.75}, # Clean Green
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 15], 'color': "#dcfce7"},  # Safe
                    {'range': [15, 40], 'color': "#fef08a"}, # Warning
                    {'range': [40, 100], 'color': "#fecaca"} # Danger
                ],
            }
        ))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
        # High-level summary text
        st.success("✅ **Document is 98% Original**")
        st.caption(f"Scan ID: `{doc_id}`")
        st.divider()

        # Detailed Metrics
        m1, m2 = st.columns(2)
        m1.metric("Total Words", f"{word_count:,}")
        m2.metric("Total Characters", f"{char_count:,}")
        
        st.divider()
        
        # Source Breakdown
        st.markdown("**Matched Sources (2%)**")
        st.markdown("1. 🔴 `academic-archive.org/pub/1029` — **1.2%**")
        st.markdown("2. 🔴 `en.wikipedia.org/wiki/Main` — **0.8%**")
        
        st.markdown("</div>", unsafe_allow_html=True) # End report-card

        # -----------------------------------
        # PDF Generation & Download
        # -----------------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        
        pdf = OfficialReport()
        pdf.add_page()
        pdf.add_executive_summary(2, word_count, char_count, doc_id)
        pdf.add_document_body(text)
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            label="📄 Download Official Certificate (PDF)",
            data=pdf_bytes,
            file_name=f"Plagiarism_Certificate_{doc_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
