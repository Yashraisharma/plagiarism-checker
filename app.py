import streamlit as st
from checker import calculate_similarity, get_reference_files

st.set_page_config(page_title="Plagiarism Shield", layout="wide")

st.title("🛡️ Plagiarism Checker Dashboard")
st.markdown("Upload a document to check its originality against our database.")

# Sidebar for Database Management
st.sidebar.header("Reference Database")
ref_docs = get_reference_files()
st.sidebar.write(f"Files in Database: {len(ref_docs)}")

# Main Content: Upload Section
uploaded_file = st.file_uploader("Upload your document (.txt)", type=["txt"])

if uploaded_file is not None:
    input_text = uploaded_file.read().decode("utf-8")
    st.subheader("Analysis Progress")
    
    results = []
    # Progress Bar
    progress_bar = st.progress(0)
    
    for idx, ref in enumerate(ref_docs):
        score = calculate_similarity(input_text, ref["content"])
        results.append({"Source": ref["name"], "Match Percentage": round(score * 100, 2)})
        progress_bar.progress((idx + 1) / len(ref_docs))

    # Sort results by highest match
    results = sorted(results, key=lambda x: x["Match Percentage"], reverse=True)

    # 📊 Report Dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Highest Match Found", f"{results[0]['Match Percentage']}%")
        st.write("### Comparison Breakdown")
        st.table(results)

    with col2:
        # Visual Warning based on score
        if results[0]['Match Percentage'] > 80:
            st.error("⚠️ HIGH PLAGIARISM DETECTED")
        elif results[0]['Match Percentage'] > 30:
            st.warning("🧐 MODERATE SIMILARITY FOUND")
        else:
            st.success("✅ ORIGINAL CONTENT")

    # Export Report Button
    st.download_button(
        label="Download Plagiarism Report",
        data=str(results),
        file_name="plagiarism_report.txt",
        mime="text/plain"
    )
