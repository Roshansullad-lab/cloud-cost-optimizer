import streamlit as st
import requests
import pandas as pd

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FinOps Cost Optimizer",
    page_icon="💰",
    layout="wide"
)

st.title("💰 FinOps Cloud Cost Optimizer & Remediation Engine")
st.markdown("Ingest cloud exports, identify orphaned infrastructure, and generate cleanup scripts instantly.")

# Create tabs for the 3 main lifecycle stages
tab1, tab2, tab3 = st.tabs(["📥 1. Ingest Inventory", "📊 2. Optimization Dashboard", "📜 3. Remediation Scripts"])

# --- TAB 1: INGESTION ---
with tab1:
    st.header("Upload Cloud Inventory / Billing Export")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        provider = st.selectbox("Cloud Provider", ["AWS", "Azure"])
        uploaded_file = st.file_uploader("Choose a CSV or JSON file", type=["csv", "json"])
        
    with col2:
        st.markdown("""
        **Expected Schema Format:**
        Your export file should contain at least these columns:
        * `resource_id`: Unique identifier (e.g., `vol-0abc123...` or asset URI)
        * `resource_type`: Type classification (`volume` or `vm`)
        * `region`: Cloud deployment zone (e.g., `us-east-1`)
        * `status`: Lifecycle state (`available`, `Unattached`, `idle`, `stopped`)
        * `monthly_cost`: Associated waste run-rate dollar value
        """)

    if uploaded_file is not None:
        if st.button("🚀 Process & Run Optimization Rules"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            params = {"cloud_provider": provider}
            
            with st.spinner("Analyzing infrastructure for waste..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/import/inventory/", params=params, files=files)
                    if response.status_code == 200:
                        res_data = response.json()
                        st.success(f"Successfully digested data! {res_data.get('orphaned_resources_detected')} new orphaned resources flagged.")
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Could not connect to FastAPI Backend: {e}")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.header("Detected Waste Analytics")
    
    if st.button("🔄 Refresh Analysis"):
        try:
            response = requests.get(f"{BACKEND_URL}/optimize/")
            if response.status_code == 200:
                data = response.json()
                
                # Metric Callouts
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Potential Monthly Savings", f"${data['total_potential_monthly_savings_usd']:.2f}")
                m_col2.metric("Orphaned Resources Count", data['resource_count'])
                
                # Raw Details Table
                if data['resource_count'] > 0:
                    st.subheader("Flagged Infrastructure Details")
                    df_resources = pd.DataFrame(data['resources'])
                    # Drop DB interior keys for user cleanliness
                    df_clean = df_resources.drop(columns=['id'], errors='ignore')
                    st.dataframe(df_clean, use_container_width=True)
                else:
                    st.info("No orphaned resources detected in the environment. Your cloud is lean!")
            else:
                st.error("Failed to fetch optimization metrics.")
        except Exception as e:
            st.error(f"Could not connect to FastAPI Backend: {e}")

# --- TAB 3: REMEDIATION ---
with tab3:
    st.header("Generate Actionable Remediation Code")
    st.caption("Engineered to output specific, deterministic CLI scripts to eliminate the waste permanently.")
    
    script_provider = st.radio("Target Ecosystem", ["AWS", "Azure"], horizontal=True)
    
    if st.button("🛠️ Generate Cleanup Script"):
        try:
            response = requests.get(f"{BACKEND_URL}/optimize/remediation-script/", params={"cloud_provider": script_provider})
            if response.status_code == 200:
                script_data = response.json()
                
                st.markdown(f"**Target Resource Count Found:** `{script_data.get('target_resources_count', 0)}`")
                
                # Code Block wrapper with copy-to-clipboard functionality
                st.code(script_data.get("script"), language="bash")
                
                st.info("💡 **Next Steps:** Review the shell commands above, ensure your local CLI execution environment is properly authenticated to the target cloud provider, and run the script safely in a sandbox terminal.")
            else:
                st.error("Failed to generate remediation commands.")
        except Exception as e:
            st.error(f"Could not connect to FastAPI Backend: {e}")