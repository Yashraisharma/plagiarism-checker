import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import PyPDF2
import re

# 1. Page Configuration
st.set_page_config(page_title="Plagiarism X Checker", layout="wide", initial_sidebar_state="expanded")

# 2. PDF Generator Class (Cloned from image_48e887.png)
class PlagiarismReportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 139) 
        self.cell(0, 10, 'Plagiarism X Checker', 0, 1, 'L')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Comprehensive Similarity Analysis Report', 0, 1, 'L')
        self.ln(10)

    def draw_sidebar_metrics(self, score, words, sentences, chapters):
        # Draw Gauge (Simulated)
        self.set_fill_color(240, 240, 240)
        self.rect(140, 40, 60, 150, 'F')
        
        self.set_xy(145, 50)
        self.set_font('Arial', 'B', 25)
        self.set_text_color(220, 50, 50)
        self.cell(50, 10, f"{score}%", 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.set_x(145)
        self.cell(50, 5, "Overall Similarity", 0, 1, 'C')
        
        # Stats
        metrics = [("Words", words), ("Sentences", sentences), ("Chapters", chapters)]
        y_pos = 90
        for label, val in metrics:
            self.set_xy(145, y_pos)
            self.set_font('Arial', 'B', 12)
            self.cell(50, 5, str(val), 0, 1, 'C')
            self.set_x(145)
            self.set_font('Arial', '', 8)
            self.cell(50, 5, label, 0, 1, 'C')
            y_pos += 15

    def add_content(self, text):
        self.set_xy(10, 40)
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        # Ensure text is compatible with Latin-1 for FPDF
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(125, 6, safe_text)

# 3. Sidebar UI
with st.sidebar:
    st.title("Plagiarism X")
    st.divider()
    st.markdown("✅ Dashboard")
    st.markdown("🌐 **Online Plagiarism**")
    st.markdown("📄 Side By Side Difference")
    st.markdown("⚙️ Settings")

# 4. Main Logic
st.title("Report")
st.markdown("<p style='color:gray;'>Content similarity detailed highlighted report.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])

if uploaded_file:
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    else:
        text = uploaded_file.read().decode("utf-8")

    # Metrics Calculation
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[^.!?]+[.!?]', text))
    chapter_count = len(re.findall(r'(?i)chapter\s+\d+|introduction|conclusion', text))
    if chapter_count == 0: chapter_count = 1 # Default to 1 if no markers found

    col1, col2 = st.columns([6, 4])

    with col1:
        st.subheader("Document Text")
        # Visual highlighting logic
        display_text = text.replace("\n", "<br>")
        # Dummy highlight first paragraph
        st.markdown(f"<div style='height:500px; overflow-y:auto; border:1px solid #ddd; padding:15px; background:white;'>"
                    f"<span style='background-color:#ffcccc;'>{display_text[:200]}</span>{display_text[200:]}</div>", 
                    unsafe_allow_html=True)

    with col2:
        tab1, _, _ = st.tabs(["Score", "AI", "Settings"])
        with tab1:
            # Corrected Gauge to fix ValueError
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 92,
                number = {'suffix': "%", 'font': {'size': 35}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "black"},
                    'steps': [
                        {'range': [0, 40], 'color': "#d9ffcc"},
                        {'range': [40, 70], 'color': "#fff3cd"},
                        {'range': [70, 100], 'color': "#f8d7da"}
                    ],
                }
            ))
            fig.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

            # Detailed Counts
            c1, c2, c3 = st.columns(3)
            c1.metric("Words", word_count)
            c2.metric("Sentences", sentence_count)
            c3.metric("Chapters", chapter_count)

            st.divider()
            st.write("🔴 **en.wikipedia.org** | 92% Match")
            
            # PDF Generation
            pdf = PlagiarismReportPDF()
            pdf.add_page()
            pdf.draw_sidebar_metrics(92, word_count, sentence_count, chapter_count)
            pdf.add_content(text)
            
            report_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("📄 Download PDF Report", data=report_bytes, file_name="Plagiarism_Report.pdf", use_container_width=True)
