import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import PyPDF2
import re

# 1. Page Configuration (Wide Layout)
st.set_page_config(page_title="Plagiarism X Checker", layout="wide", initial_sidebar_state="expanded")

# 2. Advanced PDF Generator Function to create a matching report
class PlagiarismReportPDF(FPDF):
    def header(self):
        # Logo and title
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 0, 139) # Dark Blue
        self.cell(0, 10, 'Plagiarism X Checker', 0, 1, 'L')
        self.set_font('Arial', 'B', 12)
        self.set_text_color(128, 128, 128) # Gray
        self.cell(0, 5, 'Online Plagiarism Analysis Report', 0, 1, 'L')
        self.ln(5)

    def draw_gauge(self, score_pct):
        # Position and size for the gauge
        gauge_x = 135
        gauge_y = 60
        gauge_width = 60
        gauge_height = 30
        
        # Color zones (matching the reference image)
        self.set_draw_color(0, 0, 0)
        
        # Red zone (high)
        self.set_fill_color(255, 102, 102) # Soft Red
        self.rect(gauge_x + gauge_width * 0.7, gauge_y, gauge_width * 0.3, gauge_height, 'F')
        
        # Yellow zone (medium)
        self.set_fill_color(255, 255, 153) # Soft Yellow
        self.rect(gauge_x + gauge_width * 0.4, gauge_y, gauge_width * 0.3, gauge_height, 'F')
        
        # Green zone (low)
        self.set_fill_color(153, 255, 153) # Soft Green
        self.rect(gauge_x, gauge_y, gauge_width * 0.4, gauge_height, 'F')

        # Marker line for the score
        marker_x = gauge_x + (score_pct / 100) * gauge_width
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.8)
        self.line(marker_x, gauge_y, marker_x, gauge_y + gauge_height)
        self.set_line_width(0.2) # reset

        # Score text below gauge
        self.set_xy(gauge_x, gauge_y + gauge_height + 5)
        self.set_font('Arial', 'B', 24)
        self.set_text_color(0, 0, 0)
        self.cell(gauge_width, 10, f'{score_pct}%', 0, 1, 'C')
        self.set_font('Arial', 'B', 10)
        self.cell(gauge_width, 5, 'Overall Similarity', 0, 1, 'C')

    def add_metrics(self, matched_words, total_words, sources_count):
        # Column width for metrics
        col_w = 20
        self.set_xy(135, 120)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(128, 128, 128)
        self.cell(col_w, 5, 'MATCHED', 0, 0, 'C')
        self.cell(col_w, 5, 'TOTAL', 0, 0, 'C')
        self.cell(col_w, 5, 'SOURCES', 0, 1, 'C')
        
        self.set_x(135)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(col_w, 8, str(matched_words), 0, 0, 'C')
        self.cell(col_w, 8, str(total_words), 0, 0, 'C')
        self.cell(col_w, 8, str(sources_count), 0, 1, 'C')

        self.set_x(135)
        self.set_font('Arial', '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(col_w, 5, 'Words', 0, 0, 'C')
        self.cell(col_w, 5, 'Words', 0, 0, 'C')
        self.cell(col_w, 5, 'Sources', 0, 1, 'C')
        self.ln(10)

    def add_sources(self, sources_list):
        # Color coding for sources (matching the visual scheme)
        source_colors = [(255, 102, 102), (153, 255, 153), (178, 102, 255)] # Red, Green, Purple
        
        self.set_x(135)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Top Sources', 0, 1, 'L')
        self.ln(3)

        for i, source in enumerate(sources_list):
            color = source_colors[i % len(source_colors)]
            self.set_fill_color(*color)
            self.set_x(135)
            
            # Number icon
            self.rect(self.get_x(), self.get_y(), 5, 5, 'F')
            self.set_x(self.get_x() + 8)
            
            # Source details
            self.set_font('Arial', 'B', 10)
            self.set_text_color(139, 0, 0) # Dark Red for URL
            self.cell(40, 5, source['url'], 0, 0, 'L')
            self.set_font('Arial', '', 8)
            self.set_text_color(128, 128, 128)
            self.cell(15, 5, 'INTERNET', 0, 0, 'C')
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.cell(10, 5, f'{source["pct"]}%', 0, 1, 'R')
            self.ln(2)

def generate_pdf_report(text_content, total_words, matched_words, sources_list, highlighted_content):
    pdf = PlagiarismReportPDF()
    pdf.add_page()
    
    # 1. Left content area: Main Text with simulated highlights
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    
    # Add a title section inside the content area
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Analysis Result', 0, 1, 'L')
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, 'Content similarity detailed highlighted report.', 0, 1, 'L')
    pdf.ln(10)
    
    # Take the full user text, but we'll use a slightly different approach for FPDF.
    # To make the highlights work in FPDF, we'd need more complex HTML-like text writing.
    # For this demonstration, we'll write the text plainly but add a special highlighted snippet as a summary.
    
    # Set text color to red for the highlighted text snippet and then back to black for the main body.
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(255, 51, 51) # A sharper red
    
    # This part is a complete visual simulation of the text highlights in the PDF.
    # I'll create a single block of text with fake markers to represent highlighted content.
    if len(text_content) > 500:
        highlights_snippet = f"[1] Education is the process of facilitating learning, or the acquisition of knowledge... [2] Many agree that education is a purposeful activity directed at achieving certain aims... This necessitating a balance between global brand consistency and local market needs."
        plain_snippet = text_content[500:].replace('\n', ' ')
    else:
        highlights_snippet = text_content
        plain_snippet = ""
        
    pdf.multi_cell(120, 8, txt=highlights_snippet)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    
    # Handle safe text for the plain body and make it Latin-1 compatible.
    safe_body_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(120, 8, txt=safe_body_text)

    # 2. Right content area: All metrics and sources
    pdf.set_xy(135, 30) # Positioning the right column
    pdf.draw_gauge(92) # Simulated 92% similarity
    pdf.add_metrics(matched_words, total_words, 3)
    pdf.add_sources(sources_list)

    return pdf.output(dest="S").encode("latin-1")

# 3. Sidebar Navigation (Visually matching image)
with st.sidebar:
    st.image("https://raw.githubusercontent.com/yashraisharma-design/ai_plagiarism_x_report/main/logo.png", width=120) # A clean placeholder logo, or just use text
    st.divider()
    st.markdown("✅ Dashboard")
    st.markdown("🌐 **Online Plagiarism**")
    st.markdown("📄 Side By Side Difference")
    st.markdown("📦 Bulk Comparison")
    st.markdown("☁️ Reading Level Checker")
    st.markdown("⚙️ Settings")

# 4. Main Interface Header
st.title("Report")
st.markdown("<p style='color:gray; font-size:16px;'>Content similarity detailed highlighted report.</p>", unsafe_allow_html=True)
st.divider()

uploaded_file = st.file_uploader("Upload your document (.txt or .pdf)", type=["txt", "pdf"])

if uploaded_file is not None:
    text = ""
    
    # Text extraction logic (for PDF and TXT)
    if uploaded_file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    else:
        text = uploaded_file.read().decode("utf-8")

    words = text.split()
    total_words = len(words)
    
    # 5. Create the exact layout from the image (Two columns)
    col1, col2 = st.columns([6, 4])
    
    # 6. LEFT COLUMN (On-Screen): Document Text with simulated highlights
    with col1:
        st.write("### Document Text")
        with st.container(height=600, border=True):
            # A function to find and highlight a few common phrases.
            # I will pick specific phrases to simulate the visual highlights for this demonstration.
            phrases_to_highlight = [
                r"\bEducation is the process\b",
                r"\bacquisition of knowledge\b",
                r"\bMany agree that education is\b",
                r"\bnurturing student's thinking about\b",
                r"\blocal market needs\b",
                r"\bload factor\b"
            ]
            
            # Use regex to find and wrap these phrases with color and a fake marker (1, 2, etc.)
            highlighted_text = text
            source_colors = ["#ffcccc", "#d9ffcc", "#e0b3ff"] # Red, Green, Purple
            for i, phrase in enumerate(phrases_to_highlight):
                color = source_colors[i % len(source_colors)]
                marker_text = f"[{i+1}]"
                highlighted_text = re.sub(phrase, f"<span style='background-color: {color}; padding: 2px; border-radius: 3px; font-weight: bold;'>{marker_text} \\g<0></span>", highlighted_text, flags=re.IGNORECASE)

            # Format line breaks for better readability on screen.
            st.markdown(highlighted_text.replace('\n', '<br>'), unsafe_allow_html=True)

    # 7. RIGHT COLUMN (On-Screen): Metrics, Gauge, and PDF Download
    with col2:
        # A simple, static source list that matches the visual percentages.
        sources = [
            {'url': 'schoolofsciencery.com', 'pct': 47, 'marker': '[1]'},
            {'url': 'openwingfoundation.org', 'pct': 30, 'marker': '[2]'},
            {'url': 'en.wikipedia.org', 'pct': 16, 'marker': '[3]'}
        ]
        
        # Simulated metrics based on our 92% total similarity.
        matched_words = int(total_words * 0.92)

        # Tabs as in the image
        tab1, tab2, tab3 = st.tabs(["Score", "AI", "Settings"])
        
        with tab1:
            # 8. Visually identical Plotly Gauge Chart
            # I'll hardcode the range and colors to perfectly match your reference image's visual identity.
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 92, # Hardcoded 92% visual similarity
                number = {'suffix': "%", 'font': {'size': 40}},
                title = {'text': "Overall Similarity", 'font': {'size': 20, 'color': 'black'}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black", 'tickvals': [0, 20, 40, 60, 80, 100]},
                    'bar': {'color': "black", 'width': 3},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 40], 'color': "#b3ffb3"}, # Soft Green zone
                        {'range': [40, 70], 'color': "#ffffb3"}, # Soft Yellow zone
                        {'range': [70, 100], 'color': "#ffb3b3"} # Soft Red zone
                    ],
                }
            ))
            # Adjust the layout for a clean, professional semi-circle gauge.
            fig.update_layout(
                height=250, 
                margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", # transparent
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 9. Sub-metrics visually matching the image
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Matched Words", matched_words)
            metric_col2.metric("Total Words", total_words)
            metric_col3.metric("Sources", 3)
            
            st.divider()
            
            # 10. Numbered source list with visual matching
            for source in sources:
                st.markdown(f"🔴 **{source['url']}** &nbsp;&nbsp; | &nbsp;&nbsp; {source['pct']}%")
                st.caption(f"INTERNET &nbsp;&nbsp; {source['marker']}")
                st.divider()
            
            # 11. Generate and Download matching PDF report
            # We connect the same calculated and simulated data to our advanced PDF generator.
            pdf_data = generate_pdf_report(text, total_words, matched_words, sources, highlighted_text)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name="Plagiarism_X_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
