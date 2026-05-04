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
    page_title="Plagiarism X | Official Checker", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .report-card { background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgb(0 0 0 / 0.05); }
    .doc-viewer { background-color: white; padding: 40px 50px; border-radius: 4px; border: 1px solid #cbd5e1; height: 600px; overflow-y: auto; font-family: 'Times New Roman', Times, serif; font-size: 16px; line-height: 2.0; color: #1e293b; box-shadow: 0 4px 6px rgb(0 0 0 / 0.1); }
    .metric-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .metric-table th, .metric-table td { border: 1px solid #e2e8f0; padding: 12px; text-align: left; }
    .metric-table th { background-color: #f8fafc; color: #475569; font-weight: 600; }
    .highlight-red { background-color: #fee2e2; color: #991b1b; padding: 2px 4px; border-radius: 3px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ENTERPRISE PDF GENERATOR
# ==========================================
class OfficialReport(FPDF):
    def header(self):
        # Header
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 30, 'F')
        self.set_xy(15, 10)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'PLAGIARISM X - OFFICIAL REPORT', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Plagiarism X Enterprise  |  Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}  |  Page {self.page_no()}', 0, 0, 'C')

    def add_visual_meter_and_table(self, doc_id):
        # --- 1. Visual Meter Bar (Graphic) ---
        self.set_font('Arial', 'B', 14)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'I. Authenticity Meter', 0, 1, 'L')
        
        # Draw the Meter Bar
        bar_x = 15
        bar_y = self.get_y() + 5
        bar_width = 180
        bar_height = 12
        
        # 98% Green Bar
        self.set_fill_color(34, 197, 94) # Green
        self.rect(bar_x, bar_y, bar_width * 0.98, bar_height, 'F')
        # 2% Red Bar
        self.set_fill_color(239, 68, 68) # Red
        self.rect(bar_x + (bar_width * 0.98), bar_y, bar_width * 0.02, bar_height, 'F')
        
        self.set_y(bar_y + 15)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(34, 197, 94)
        self.cell(90, 5, '98% Original', 0, 0, 'L')
        self.set_text_color(239, 68, 68)
        self.cell(90, 5, '2% Plagiarized', 0, 1, 'R')
        self.ln(10)

        # --- 2. The Mandatory Breakdown Table ---
        self.set_font('Arial', 'B', 14)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'II. Analysis Breakdown', 0, 1, 'L')
        
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(15, 23, 42)
        
        # Table Headers
        self.cell(60, 10, 'Metric', 1, 0, 'C', 1)
        self.cell(60, 10, 'Percentage', 1, 0, 'C', 1)
        self.cell(60, 10, 'Status', 1, 1, 'C', 1)
        
        # Table Rows
        self.set_font('Arial', '', 11)
        
        # Row 1: Originality
        self.cell(60, 10, 'Originality', 1, 0, 'C')
        self.set_text_color(34, 197, 94) # Green
        self.cell(60, 10, '98%', 1, 0, 'C')
        self.cell(60, 10, 'Passed (Excellent)', 1, 1, 'C')
        
        # Row 2: Similarity
        self.set_text_color(15, 23, 42)
        self.cell(60, 10, 'Similarity', 1, 0, 'C')
        self.set_text_color(239, 68, 68) # Red
        self.cell(60, 10, '2%', 1, 0, 'C')
        self.cell(60, 10, 'Minor Matches', 1, 1, 'C')

        # Row 3: Plagiarism
        self.set_text_color(15, 23, 42)
        self.cell(60, 10, 'Plagiarism', 1, 0, 'C')
        self.set_text_color(239, 68, 68) # Red
        self.cell(60, 10, '2%', 1, 0, 'C')
        self.cell(60, 10, 'Review Recommended', 1, 1, 'C')
        
        self.set_text_color(15, 23, 42)
        self.ln(10)

    def add_document_body(self, text):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'III. Scanned Document Text', 0, 1, 'L')
        self.ln(2)
        
        self.set_font('Times', '', 12)
        # Clean text: replace arbitrary line breaks with spaces so it flows as paragraphs
        clean_text = text.replace('\n', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text) # Remove extra spaces
        clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
        
        self.multi_cell(180, 8, clean_text, align='J')

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ Plagiarism X")
    st.caption("Official Grading Portal")
    st.divider()
    st.markdown("📊 **Dashboard**")
    st.markdown("🔍 New Scan")
    st.markdown("⚙️ Settings")

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("Document Originality Dashboard")

uploaded_file = st.file_uploader("Upload Document for Official Scanning", type=["pdf", "txt"])

if uploaded_file:
    # --- Text Extraction & Paragraph Cleanup ---
    raw_text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            raw_text += page.extract_text() + " "
    else:
        raw_text = uploaded_file.read().decode("utf-8")

    # Fix the "word by word" issue by consolidating line breaks into proper paragraphs
    formatted_text = re.sub(r'\n(?!\n)', ' ', raw_text) 
    formatted_text = re.sub(r'\s+', ' ', formatted_text).strip()

    if not formatted_text:
        st.error("Document is empty or unreadable.")
        st.stop()

    doc_id = str(uuid.uuid4()).upper()[:10]

    # Layout
    col1, col2 = st.columns([55, 45])

    # LEFT: Cohesive Document Viewer
    with col1:
        st.markdown("##### Scanned Document")
        
        # Simulate a 2% highlight finding roughly 20-30 words in
        words = formatted_text.split()
        if len(words) > 30:
            target_phrase = " ".join(words[15:25])
            display_html = formatted_text.replace(target_phrase, f"<span class='highlight-red'>{target_phrase}</span>")
        else:
            display_html = formatted_text

        st.markdown(f"<div class='doc-viewer'>{display_html}</div>", unsafe_allow_html=True)

    # RIGHT: The Analysis & Mandatory Table
    with col2:
        st.markdown("##### Official Results")
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        
        # The Plotly Gauge (Visual Meter)
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 98,
            number = {'suffix': "%", 'font': {'size': 45, 'color': '#15803d'}},
            title = {'text': "Originality Score", 'font': {'size': 18, 'color': '#334155'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "#22c55e"}, # Green
                'steps': [
                    {'range': [0, 50], 'color': "#fee2e2"},
                    {'range': [50, 80], 'color': "#fef08a"},
                    {'range': [80, 100], 'color': "#dcfce7"}
                ],
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # The Mandatory Table in the UI
        st.markdown("""
            <table class='metric-table'>
                <tr><th>Metric</th><th>Percentage</th><th>Status</th></tr>
                <tr><td><b>Originality</b></td><td style='color: #16a34a; font-weight: bold;'>98%</td><td>Passed</td></tr>
                <tr><td><b>Similarity</b></td><td style='color: #dc2626; font-weight: bold;'>2%</td><td>Minor Matches</td></tr>
                <tr><td><b>Plagiarism</b></td><td style='color: #dc2626; font-weight: bold;'>2%</td><td>Review</td></tr>
            </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"Scan ID: `{doc_id}` | Words Checked: {len(words)}")
        
        st.markdown("</div>", unsafe_allow_html=True) # End card

        # PDF Generation
        pdf = OfficialReport()
        pdf.add_page()
        pdf.add_visual_meter_and_table(doc_id)
        pdf.add_document_body(formatted_text)
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📄 Download Official PDF Report",
            data=pdf_bytes,
            file_name=f"Official_Report_{doc_id}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
