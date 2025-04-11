import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI-Powered Invoice Risk Analyzer", layout="wide")

st.title("📊 AI-Powered Invoice Risk Analyzer")
st.markdown("Upload your invoice Excel file and get an automated audit risk analysis.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully.")

    # Ensure date columns are properly formatted
    df["Billing Date"] = pd.to_datetime(df["Billing Date"], errors='coerce')
    df["Posting Date"] = pd.to_datetime(df["Posting Date"], errors='coerce')

    # GST rate lookup table
    hsn_gst_rates = {
        "0401": 0, "1001": 5, "2106": 18, "3004": 12,
        "8408": 28, "8708": 18, "3926": 12, "8504": 18,
        "1701": 5, "7308": 18
    }

    df["Risk Score"] = 0
    df["Risk Reason"] = ""

    # Calculate derived columns
    df["Expected GST Rate"] = df["HSN Code"].astype(str).map(hsn_gst_rates)
    df["Actual GST Rate"] = ((df["Input Bed"] / df["Base Amt"]) * 100).round(2)

    # Apply sample rules
    df["Rule_GST_Mismatch"] = (abs(df["Expected GST Rate"] - df["Actual GST Rate"]) > 2).astype(int)
    df.loc[df["Rule_GST_Mismatch"] == 1, "Risk Reason"] += "GST mismatch; "
    df["Risk Score"] += df["Rule_GST_Mismatch"] * 3

    df["Rule_Round_Gross"] = (df["Gross Amt"] % 1000 == 0).astype(int)
    df.loc[df["Rule_Round_Gross"] == 1, "Risk Reason"] += "Round number invoice; "
    df["Risk Score"] += df["Rule_Round_Gross"] * 1

    df["Risk Level"] = pd.cut(df["Risk Score"], bins=[-1, 3, 6, 100], labels=["Low", "Medium", "High"])

    st.subheader("📋 Risk Summary Table")
    st.dataframe(df[["Document Number", "Inv.Vendor Name", "Gross Amt", "Risk Score", "Risk Level", "Risk Reason"]])

    st.download_button("📥 Download Full Risk Report (CSV)", df.to_csv(index=False), file_name="invoice_risk_report.csv")
else:
    st.info("👆 Upload a .xlsx file to begin risk analysis.")
