import streamlit as st
import os
import pandas as pd
from app import process_pdf

st.set_page_config(page_title="Credit Card Parser", page_icon="💳", layout="wide")

st.title("💳 Credit Card Statement Parser")
st.write("Upload one or more PDF statements from HDFC, ICICI, Amex, Chase, Union, or Wells Fargo.")

uploaded_files = st.file_uploader(
    "Choose PDF files", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    all_transactions = []
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    with st.status("Processing statements...", expanded=True) as status:
        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.write(f"Parsing `{uploaded_file.name}`...")
            try:
                result = process_pdf(temp_path)
                if result.get("status") == "success":
                    issuer = result.get("issuer", "unknown").upper()
                    for tx in result.get("transactions", []):
                        tx['bank'] = issuer
                        all_transactions.append(tx)
                else:
                    st.error(f"Error in {uploaded_file.name}: {result.get('message')}")
            except Exception as e:
                st.error(f"Failed to process {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        status.update(label="Processing complete!", state="complete", expanded=False)

    if all_transactions:
        df = pd.DataFrame(all_transactions)
        
        st.subheader(f"Combined Transactions ({len(all_transactions)})")
        
        # Define clean column order
        cols = ['bank', 'date', 'description', 'amount', 'type', 'ref_no']
        display_df = df[[c for c in cols if c in df.columns]]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Download
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download All Transactions as CSV",
            data=csv,
            file_name="combined_transactions.csv",
            mime='text/csv',
        )
    else:
        st.warning("No transactions found in the uploaded files.")
else:
    st.info("Please upload one or more credit card statements.")
