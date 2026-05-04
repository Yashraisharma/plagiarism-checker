import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF

# 1. Page Configuration (Wide Layout)
st.set_page_config(page_title="Plagiarism Checker Pro", layout="wide", initial_sidebar_state="expanded")

# 2. PDF Generator Function
def generate_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Plagiarism Analysis Report", ln=True, align='L')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Overall Similarity: 2% (98% Original)", ln=True, align='L')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    # Handle encoding for PDF
    safe_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=safe_text)
    return pdf.output(dest="S").encode("latin-1")

# 3. Sidebar Navigation (Visual Only)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Google_Drive_icon_%282020%29.svg/1024px-Google_Drive_icon_%282020%29.svg.png", width=50) # Placeholder logo
    st.title("Plagiarism X")
    st.markdown("✅ Dashboard")
    st.markdown("🌐 **Online Plagiarism**")
    st.markdown("📄 Side By Side Difference")
    st.markdown("⚙️ Settings")

# 4. Main Interface
st.title("Report")
st.markdown("<p style='color:gray;'>Content similarity detailed highlighted report.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your document (.txt)", type=["txt"])

if uploaded_file is not None:
    # Read the file
    text = uploaded_file.read().decode("utf-8")
    words = text.split()
    total_words = len(words)
    
    # Create the two-column layout
    col1, col2 = st.columns([6, 4])
    
    # LEFT COLUMN: Document Text with dummy highlights
    with col1:
        st.write("### Document Text")
        with st.container(height=500, border=True):
            # Highlight the first few words to simulate plagiarism detection
            if total_words > 15:
                highlighted_text = f"<span style='background-color: #ffcccc; padding: 2px; border-radius: 3px;'>{' '.join(words[:15])}</span> {' '.join(words[15:])}"
            else:
                highlighted_text = text
            st.markdown(highlighted_text, unsafe_allow_html=True)

    # RIGHT COLUMN: Metrics, Gauge, and PDF Download
    with col2:
        # Tabs just like the image
        tab1, tab2, tab3 = st.tabs(["Score", "AI", "Settings"])
        
        with tab1:
            # Gauge Chart (Hardcoded to 2% Plagiarism / 98% Original)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 2,
                title = {'text': "Overall Similarity", 'font': {'size': 18}},
                number = {'suffix': "%"},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#ef4444"},
                    'steps': [
                        {'range': [0, 20], 'color': "#22c55e"}, # Green
                        {'range': [20, 50], 'color': "#eab308"}, # Yellow
                        {'range': [50, 100], 'color': "#ef4444"} # Red
                    ]
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            # Sub-metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Matched Words", int(total_words * 0.02))
            metric_col2.metric("Total Words", total_words)
            metric_col3.metric("Sources", 1)
            
            st.divider()
            
            # Dummy Source List
            st.markdown("🔴 **en.wikipedia.org** &nbsp;&nbsp; | &nbsp;&nbsp; 2%")
            st.caption("INTERNET")

            st.divider()
            
            # Generate and Download PDF
            pdf_data = generate_pdf(text)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name="Plagiarism_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
