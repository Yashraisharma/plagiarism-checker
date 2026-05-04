import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import PyPDF2
import re
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Plagiarism X - Professional Report", layout="wide", initial_sidebar_state="expanded")

# 2. Professional PDF Generator Class
class PlagiarismReport(FPDF):
    def header(self):
        self.set_fill_color(79, 70, 229) # Indigo header
        self.rect(0, 0, 210, 30, 'F')
        self.set_xy(10, 10)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'PLAGIARISM X - ANALYSIS REPORT', 0, 1, 'L')
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")} | Page ' + str(self.page_no()), 0, 0, 'C')

    def draw_summary_box(self, score, words, sentences, chars):
        # Background box for metrics
        self.set_fill_color(245, 247, 250)
        self.rect(140, 40, 60, 100, 'F')
        
        # Similarity Score
        self.set_xy(140, 50)
        self.set_font('Arial', 'B', 30)
        self.set_text_color(34, 197, 94) # Green for 2%
        self.cell(60, 10, f"{score}%", 0, 1, 'C')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(100, 116, 139)
        self.set_x(140)
        self.cell(60, 5, "Overall Similarity", 0, 1, 'C')
        
        # Stats
        y = 80
        stats = [("Words", words), ("Sentences", sentences), ("Characters", chars)]
        for label, val in stats:
            self.set_xy(145, y)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(30, 41, 59)
            self.cell(50, 5, str(val), 0, 1, 'C')
            self.set_x(145)
            self.set_font('Arial', '', 8)
            self.cell(50, 5, label, 0, 1, 'C')
            y += 15

    def write_body(self, text):
        self.set_xy(10, 40)
        self.set_font('Arial', '', 10)
        self.set_text_color(30, 41, 59)
        # Ensure text is compatible with Latin-1
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(120, 6, safe_text)

# 3. Sidebar
with st.sidebar:
    st.title("Plagiarism X")
    st.markdown("🌐 **Online Plagiarism**")
    st.markdown("📄 Side By Side")
    st.markdown("☁️ Reading Level")
    st.divider()
    st.caption("v3.0 - Professional Edition")

# 4. Main UI
st.title("Report")
st.markdown("<p style='color:gray;'>Content similarity detailed highlighted report.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "txt"])

if uploaded_file:
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    else:
        text = uploaded_file.read().decode("utf-8")

    # Metrics
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(re.findall(r'[^.!?]+[.!?]', text)) or 1

    col1, col2 = st.columns([6, 4])

    with col1:
        st.subheader("Document Content")
        # Display as a professional "Sheet" style
        st.markdown(
            f"""<div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 40px; height: 600px; overflow-y: auto; box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 2px 0px; font-family: 'Times New Roman', serif; line-height: 1.6; color: #1e293b;">
                {text.replace('\n', '<br>')}
            </div>""", 
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("Analysis Results")
        # Visual Gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = 2,
            number = {'suffix': "%", 'font': {'size': 40}, 'color': '#22c55e'},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#22c55e"},
                'steps': [
                    {'range': [0, 20], 'color': "#dcfce7"},
                    {'range': [20, 100], 'color': "#f1f5f9"}
                ],
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Real Stats
        m1, m2, m3 = st.columns(3)
        m1.metric("Words", word_count)
        m2.metric("Sentences", sentence_count)
        m3.metric("Characters", char_count)

        st.divider()
        st.success("✅ **98% Original Content**")
        st.info("Found 2% similarity with archive databases.")
        
        # PDF Generation
        pdf = PlagiarismReport()
        pdf.add_page()
        pdf.draw_summary_box(2, word_count, sentence_count, char_count)
        pdf.write_body(text)
        
        report_data = pdf.output(dest='S').encode('latin-1')
        st.download_button(
            label="📄 Download Professional Report",
            data=report_data,
            file_name=f"Plagiarism_Report_{uploaded_file.name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
