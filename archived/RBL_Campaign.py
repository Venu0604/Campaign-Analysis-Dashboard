import pandas as pd
import streamlit as st
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


# -------------------------
# Campaign costs by channel
# -------------------------
CAMPAIGN_COSTS = {
   "SMS": 0.10,
   "RCS": 0.085,
   "Whatsapp Marketing": 0.80,
   "Whatsapp Utility": 0.115,
}


# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="RBL Bank Campaign Dashboard", layout="wide", page_icon="🏦")


# -------------------------
# Enhanced Custom CSS - Dark Theme
# -------------------------
st.markdown("""
   <style>
   /* Import Google Fonts */
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
  
   /* Global Styles */
   .main {
       font-family: 'Inter', sans-serif;
       background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
       color: #e2e8f0;
   }
  
   /* Main Header with Gradient */
   .main-header {
       font-size: 3.5rem;
       font-weight: 800;
       background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
       -webkit-background-clip: text;
       -webkit-text-fill-color: transparent;
       text-align: center;
       margin-bottom: 0.5rem;
       animation: fadeInDown 0.8s ease-in-out;
       text-shadow: 0 0 40px rgba(59, 130, 246, 0.3);
   }
  
   .sub-header {
       text-align: center;
       color: #94a3b8;
       font-size: 1.1rem;
       margin-bottom: 2rem;
       font-weight: 300;
   }
  
   /* Metric Cards */
   .metric-card {
       background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
       padding: 1.5rem;
       border-radius: 15px;
       box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
       color: white;
       text-align: center;
       transition: transform 0.3s ease, box-shadow 0.3s ease;
   }
  
   .metric-card:hover {
       transform: translateY(-5px);
       box-shadow: 0 15px 40px rgba(139, 92, 246, 0.5);
   }
  
   .metric-value {
       font-size: 2.5rem;
       font-weight: 700;
       margin: 0.5rem 0;
   }
  
   .metric-label {
       font-size: 0.9rem;
       opacity: 0.9;
       text-transform: uppercase;
       letter-spacing: 1px;
   }
  
   /* Sidebar Styling */
   [data-testid="stSidebar"] {
       background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
       border-right: 1px solid #334155;
   }
  
   [data-testid="stSidebar"] * {
       color: #e2e8f0 !important;
   }
  
   /* Filter Section */
   .filter-section {
       background: rgba(30, 41, 59, 0.6);
       padding: 1.5rem;
       border-radius: 10px;
       box-shadow: 0 2px 10px rgba(0,0,0,0.3);
       margin-bottom: 1rem;
       border: 1px solid #334155;
   }
  
   /* Streamlit Elements Dark Mode */
   .stSelectbox, .stDateInput, .stTextInput {
       background-color: #1e293b !important;
   }
  
   .stSelectbox > div > div, .stDateInput > div > div, .stTextInput > div > div {
       background-color: #334155 !important;
       color: #e2e8f0 !important;
       border: 1px solid #475569 !important;
   }
  
   /* Metric Containers */
   [data-testid="stMetricValue"] {
       color: #06b6d4 !important;
       font-weight: 700;
   }
  
   [data-testid="stMetricDelta"] {
       color: #94a3b8 !important;
   }
  
   /* Animation */
   @keyframes fadeInDown {
       from {
           opacity: 0;
           transform: translateY(-20px);
       }
       to {
           opacity: 1;
           transform: translateY(0);
       }
   }
  
   /* Tabs Styling */
   .stTabs [data-baseweb="tab-list"] {
       gap: 8px;
       background-color: transparent;
   }
  
   .stTabs [data-baseweb="tab"] {
       height: 50px;
       background: rgba(30, 41, 59, 0.6);
       border-radius: 10px 10px 0 0;
       padding: 0 24px;
       font-weight: 600;
       color: #94a3b8;
       border: 1px solid #334155;
   }
  
   .stTabs [aria-selected="true"] {
       background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
       color: white !important;
       border: none;
   }
  
   /* Download Button */
   .stDownloadButton button {
       background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
       color: white;
       border: none;
       padding: 0.75rem 2rem;
       border-radius: 10px;
       font-weight: 600;
       transition: all 0.3s ease;
       box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
   }
  
   .stDownloadButton button:hover {
       transform: scale(1.05);
       box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6);
   }
  
   /* Info boxes */
   .stAlert {
       background-color: rgba(30, 41, 59, 0.8) !important;
       color: #e2e8f0 !important;
       border: 1px solid #334155 !important;
   }
  
   /* DataFrames */
   .stDataFrame {
       background-color: #1e293b !important;
   }
  
   /* Success/Error Messages */
   .stSuccess {
       background-color: rgba(16, 185, 129, 0.1) !important;
       color: #10b981 !important;
       border: 1px solid #10b981 !important;
   }
  
   .stError {
       background-color: rgba(239, 68, 68, 0.1) !important;
       color: #ef4444 !important;
       border: 1px solid #ef4444 !important;
   }
  
   /* Dividers */
   hr {
       border-color: #334155 !important;
   }
  
   /* Headers */
   h1, h2, h3, h4, h5, h6 {
       color: #e2e8f0 !important;
   }
  
   /* Plotly Charts Background */
   .js-plotly-plot .plotly .main-svg {
       background-color: transparent !important;
   }
   </style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-header">🏦 RBL Bank Campaign Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Performance Tracking & Insights</div>', unsafe_allow_html=True)


# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
   st.markdown("### 💰 Campaign Economics")
   for channel, cost in CAMPAIGN_COSTS.items():
       st.metric(channel, f"₹{cost:.3f}/unit")


# -------------------------
# Load Identifiers
# -------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid=1119698657"


try:
   df_identifiers = pd.read_csv(sheet_url)
   df_identifiers.columns = df_identifiers.columns.str.strip()
  
   # Convert Date column to datetime
   df_identifiers['Date'] = pd.to_datetime(df_identifiers['Date'], errors='coerce')
  
   st.sidebar.success(f"✅ Loaded {len(df_identifiers)} campaigns")
except Exception as e:
   st.sidebar.error(f"❌ Error loading identifiers: {e}")
   df_identifiers = None


# -------------------------
# File Upload
# -------------------------
mis_file = st.file_uploader("📁 Upload MIS File", type=["xlsx", "xls", "xlsb"])


# -------------------------
# Main Analysis Logic
# -------------------------
if mis_file and df_identifiers is not None:
   try:
       # Detect file type and use appropriate engine
       file_name = mis_file.name
       file_extension = file_name.split('.')[-1].lower()
      
       # Determine the engine based on file extension
       if file_extension == 'xls':
           engine = 'xlrd'
       elif file_extension == 'xlsb':
           engine = 'pyxlsb'
       else:
           engine = 'openpyxl'
      
       # First, try to get all sheet names
       try:
           excel_file = pd.ExcelFile(mis_file, engine=engine)
       except Exception as e:
           st.error(f"❌ Error reading Excel file: {e}")
           if file_extension == 'xls':
               st.error("💡 Install xlrd: `pip install xlrd`")
           st.stop()
      
       sheet_names = excel_file.sheet_names
      
       if len(sheet_names) == 0:
           st.error("❌ No worksheets found in the file.")
           st.stop()
      
       # Let user select sheet if multiple sheets exist
       if len(sheet_names) > 1:
           selected_sheet = st.selectbox("Select MIS Data Sheet", sheet_names, index=0)
       else:
           selected_sheet = sheet_names[0]
      
       # Read the selected sheet
       df_mis = pd.read_excel(mis_file, sheet_name=selected_sheet, engine=engine)
       df_mis.columns = df_mis.columns.str.strip()


       # Identify the Campaign source column (column K in the original sheet)
       campaign_source_col = None
       disposition_col = None
       ops_status_col = None
      
       # Try to find Campaign source column (flexible matching)
       for col in df_mis.columns:
           if "campaign source" in col.lower():
               campaign_source_col = col
               break
      
       # Try to find Disposition column
       for col in df_mis.columns:
           if col.strip().lower() == "disposition":
               disposition_col = col
               break
      
       # Find the OPS Status column (it contains "OPS Status till")
       for col in df_mis.columns:
           if "ops status till" in col.lower():
               ops_status_col = col
               break
      
 
       # Validate required columns
       if campaign_source_col is None:
           st.error("❌ 'Campaign source' column not found")
           with st.expander("Available columns"):
               st.write(list(df_mis.columns))
           st.stop()
      
       if disposition_col is None:
           st.error("❌ 'Disposition' column not found")
           with st.expander("Available columns"):
               st.write(list(df_mis.columns))
           st.stop()
          
       if ops_status_col is None:
           st.warning("⚠️ OPS Status column not found. Card Out will be 0.")
      
       # Display found columns for confirmation
       st.success(f"✅ Loaded {len(df_mis):,} rows from '{selected_sheet}'")


       # ----------------------------------------------------------------------
       # 🛑 MOVED DEBUGGING SECTION - This runs ONCE after file load 🛑
       # ----------------------------------------------------------------------
       st.markdown("---")
       with st.expander("🔍 DEBUG: Unique OPS Statuses (Click to view)") as debug_expander:

           if ops_status_col and not df_mis.empty:
               st.info(f"Checking unique values in column: **{ops_status_col}**")
               
               # Get all unique, lowercased, and stripped non-empty statuses
               unique_statuses = (
                   df_mis[ops_status_col]
                   .astype(str)
                   .str.strip()
                   .str.lower()
                   .loc[lambda x: x != 'nan'] # Filter out NaN placeholder strings
                   .unique()
               )
               
               if unique_statuses.size > 0:
                   st.write("---")
                   st.error("🚨 Found the Statuses. **Copy the EXACT status** for 'Card Out' below:")
                   st.code(unique_statuses.tolist(), language='text') 
               else:
                   st.warning("No unique, non-empty statuses found in the OPS column.")
           else:
               st.warning("OPS Status column was not found or the MIS data is empty.")
       st.markdown("---")
       # ----------------------------------------------------------------------


       output_rows = []


       for _, row in df_identifiers.iterrows():
           date = row.get("Date", "")
           identifier = str(row.get("Identifiers", "")).strip()
           source = str(row.get("Source", "")).strip()
           channel = str(row.get("Channel", "")).strip()
           delivered = float(row.get("Delivered", 0))
           clicks = float(row.get("Clicks", 0))


           # Get channel-specific cost
           cost_per_unit = CAMPAIGN_COSTS.get(channel, CAMPAIGN_COSTS["SMS"])


           # Filter MIS data where campaign source contains the identifier
           mask = df_mis[campaign_source_col].astype(str).str.contains(identifier, case=False, na=False)
           df_filtered = df_mis[mask]


           # Count applications
           applications = len(df_filtered)
          
           # Count disposition values (case-insensitive and whitespace-tolerant)
           aip_decline = len(df_filtered[df_filtered[disposition_col].astype(str).str.strip().str.lower() == "aip decline"])
           received_vkyc = len(df_filtered[df_filtered[disposition_col].astype(str).str.strip().str.lower() == "received for vkyc"])
           touch_free_kyc = len(df_filtered[df_filtered[disposition_col].astype(str).str.strip().str.lower() == "touch free kyc pending"])
           received_biometric = len(df_filtered[df_filtered[disposition_col].astype(str).str.strip().str.lower() == "received for biometric"])
          
           # Calculate declined and approved
           declined = aip_decline
           approved = received_vkyc + touch_free_kyc
          
  
           # Count Card Out (where OPS Status = "Card Setup") - 🚨 CORRECTED CODE HERE 🚨
           card_out = 0
           if ops_status_col:
               # We use str.contains for robustness against extra text (e.g., dates)
               CARD_OUT_KEYWORD = "Card Setup" 
              
               card_out = len(
                   df_filtered[
                       df_filtered[ops_status_col]
                       .astype(str)
                       .str.strip()
                       .str.lower()
                       # This line is the most robust way to find "Card Setup"
                       .str.contains(CARD_OUT_KEYWORD, na=False, regex=False) 
                   ]
               )


           # Calculate in progress (applications - declined - card_out)
           in_progress = applications - declined - card_out


           # Metrics with channel-specific cost
           ctr = round((clicks / delivered * 100), 2) if delivered > 0 else 0
           cpc = round((cost_per_unit * delivered / clicks), 2) if clicks > 0 else 0
           total_cost = round(delivered * cost_per_unit, 2)
           cost_per_app = round(total_cost / applications, 2) if applications > 0 else 0
           cost_per_ipa = round(total_cost / approved, 2) if approved > 0 else 0
           cost_per_card = round(total_cost / card_out, 2) if card_out > 0 else 0


           output_rows.append({
               "Date": date,
               "Campaign name": identifier,
               "Applications": applications,
               "AIP Decline": aip_decline,
               "Received For VKYC": received_vkyc,
               "Touch Free KYC Pending": touch_free_kyc,
               "Received For Biometric": received_biometric,
               "Declined": declined,
               "Approved": approved,
               "Card Out": card_out,
               "In Progress": in_progress,
               "Delivered": delivered,
               "Clicks": clicks,
               "CTR (%)": ctr,
               "CPC (₹)": cpc,
               "Cost per unit (₹)": cost_per_unit,
               "Total cost (₹)": total_cost,
               "Cost Per Application (₹)": cost_per_app,
               "Cost per IPA approved (₹)": cost_per_ipa,
               "Cost per Card Out (₹)": cost_per_card,
               "Source": source,
               "Channel": channel
           })


       df_summary = pd.DataFrame(output_rows)
      
       # Ensure Date is datetime
       df_summary['Date'] = pd.to_datetime(df_summary['Date'], errors='coerce')
      
       st.success(f"✅ Processed {len(df_summary)} campaigns | {df_summary['Applications'].sum():,} applications | ₹{df_summary['Total cost (₹)'].sum():,.0f} total cost")


       # -------------------------
       # Interactive Filters
       # -------------------------
       st.markdown("---")
       st.markdown("### 🔍 Filters")
      
       filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
      
       with filter_col1:
           # Date Range Filter
           min_date = df_summary['Date'].min()
           max_date = df_summary['Date'].max()
          
           if pd.notna(min_date) and pd.notna(max_date):
               date_range = st.date_input(
                   "📅 Date Range",
                   value=(min_date, max_date),
                   min_value=min_date,
                   max_value=max_date
               )
              
               # Apply date filter
               if len(date_range) == 2:
                   start_date, end_date = date_range
                   df_filtered = df_summary[
                       (df_summary['Date'] >= pd.Timestamp(start_date)) &
                       (df_summary['Date'] <= pd.Timestamp(end_date))
                   ]
               else:
                   df_filtered = df_summary
           else:
               st.warning("⚠️ Date data not available")
               df_filtered = df_summary
      
       with filter_col2:
           # Source Filter
           sources = ["All Sources"] + sorted(df_summary['Source'].unique().tolist())
           selected_source = st.selectbox("🎯 Source", sources)
          
           if selected_source != "All Sources":
               df_filtered = df_filtered[df_filtered['Source'] == selected_source]
      
       with filter_col3:
           # Channel Filter
           channels = ["All Channels"] + sorted(df_summary['Channel'].unique().tolist())
           selected_channel = st.selectbox("📢 Channel", channels)
          
           if selected_channel != "All Channels":
               df_filtered = df_filtered[df_filtered['Channel'] == selected_channel]
      
       with filter_col4:
           # Campaign Filter
           campaigns = ["All Campaigns"] + sorted(df_summary['Campaign name'].unique().tolist())
           selected_campaign = st.selectbox("🎪 Campaign", campaigns)
          
           if selected_campaign != "All Campaigns":
               df_filtered = df_filtered[df_filtered['Campaign name'] == selected_campaign]


       # -------------------------
       # Enhanced Key Metrics
       # -------------------------
       st.markdown("---")
       st.markdown("### 📊 Key Metrics")
      
       metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)


       total_apps = df_filtered["Applications"].sum()
       total_cost = df_filtered["Total cost (₹)"].sum()
       total_declined = df_filtered["Declined"].sum()
       total_approved = df_filtered["Approved"].sum()
       total_card_out = df_filtered["Card Out"].sum()
       avg_cpa = total_cost / total_apps if total_apps > 0 else 0
       avg_ctr = df_filtered["CTR (%)"].mean() if len(df_filtered) > 0 else 0
      
       # Calculate conversion rates
       app_to_approved_rate = (total_approved / total_apps * 100) if total_apps > 0 else 0
       approved_to_card_rate = (total_card_out / total_approved * 100) if total_approved > 0 else 0


       with metric_col1:
           st.metric(
               "Total Applications",
               f"{total_apps:,}",
               delta=f"{len(df_filtered)} campaigns",
               help="Total number of applications received"
           )
      
       with metric_col2:
           st.metric(
               "Total Investment",
               f"₹{total_cost:,.2f}",
               delta=f"Avg ₹{avg_cpa:.2f}/app",
               help="Total campaign spend"
           )
      
       with metric_col3:
           st.metric(
               "IPA Approved",
               f"{total_approved:,}",
               delta=f"{app_to_approved_rate:.1f}% conversion",
               help="In-Principle Approved applications"
           )
      
       with metric_col4:
           st.metric(
               "Cards Issued",
               f"{total_card_out:,}",
               delta=f"{approved_to_card_rate:.1f}% from IPA",
               help="Successfully issued cards"
           )
      
       with metric_col5:
           st.metric(
               "Avg CTR",
               f"{avg_ctr:.2f}%",
               delta=f"{total_declined:,} declined",
               help="Average click-through rate"
           )


       st.markdown("---")


       # -------------------------
       # Enhanced Tabs
       # -------------------------
       tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Performance Analytics", "📊 Campaign Comparison", "📋 Summary Reports", "📑 Data Table", "📥 Export"])


       # --- Tab 1: Performance Analytics ---
       with tab1:
           viz_col1, viz_col2 = st.columns(2)
      
           with viz_col1:
               # Time Series Chart
               if pd.notna(df_filtered['Date']).any():
                   df_time = df_filtered.groupby('Date').agg({
                       'Applications': 'sum',
                       'Total cost (₹)': 'sum',
                       'Approved': 'sum',
                       'Card Out': 'sum'
                   }).reset_index()
          
                   fig_time = go.Figure()
                   fig_time.add_trace(go.Scatter(
                       x=df_time['Date'], y=df_time['Applications'],
                       mode='lines+markers', name='Applications',
                       line=dict(color='#06b6d4', width=3),
                       marker=dict(size=8)
                   ))
                   fig_time.add_trace(go.Scatter(
                       x=df_time['Date'], y=df_time['Approved'],
                       mode='lines+markers', name='Approved',
                       line=dict(color='#3b82f6', width=3),
                       marker=dict(size=8)
                   ))
                   fig_time.add_trace(go.Scatter(
                       x=df_time['Date'], y=df_time['Card Out'],
                       mode='lines+markers', name='Cards Issued',
                       line=dict(color='#8b5cf6', width=3),
                       marker=dict(size=8)
                   ))
                   fig_time.update_layout(
                       title=dict(text="📈 Performance Trends Over Time", font=dict(size=16, color='#e2e8f0')),
                       xaxis_title="Date",
                       yaxis_title="Count",
                       hovermode='x unified',
                       height=400,
                       template='plotly_dark',
                       paper_bgcolor='rgba(30, 41, 59, 0.6)',
                       plot_bgcolor='rgba(30, 41, 59, 0.4)',
                       font=dict(color='#e2e8f0', size=12),
                       xaxis=dict(gridcolor='#475569', color='#e2e8f0'),
                       yaxis=dict(gridcolor='#475569', color='#e2e8f0'),
                       legend=dict(bgcolor='rgba(30, 41, 59, 0.8)', bordercolor='#475569', borderwidth=1)
                   )
                   st.plotly_chart(fig_time, use_container_width=True)


                   # Disposition Breakdown
                   disposition_data = {
                       'Status': ['AIP Decline', 'Received For VKYC', 'Touch Free KYC Pending', 'Received For Biometric'],
                       'Count': [
                           df_filtered['AIP Decline'].sum(),
                           df_filtered['Received For VKYC'].sum(),
                           df_filtered['Touch Free KYC Pending'].sum(),
                           df_filtered['Received For Biometric'].sum()
                       ]
                   }
                   fig_disposition = px.bar(
                       disposition_data,
                       x='Status',
                       y='Count',
                       title="📊 Disposition Status Breakdown",
                       color='Count',
                       color_continuous_scale='Blues'
                   )
                   fig_disposition.update_layout(
                       height=400,
                       template='plotly_dark',
                       paper_bgcolor='rgba(30, 41, 59, 0.6)',
                       plot_bgcolor='rgba(30, 41, 59, 0.4)',
                       font=dict(color='#e2e8f0')
                   )
                   st.plotly_chart(fig_disposition, use_container_width=True)


           with viz_col2:
               # Conversion Funnel
               fig_funnel = go.Figure(go.Funnel(
                   y=["Applications", "Approved", "Cards Issued"],
                   x=[total_apps, total_approved, total_card_out],
                   textposition="inside",
                   textinfo="value+percent initial",
                   textfont=dict(size=14, color='white', family='Inter'),
                   marker={
                       "color": ["#06b6d4", "#3b82f6", "#8b5cf6"],
                       "line": {"width": [2, 2, 2], "color": ["#1e293b", "#1e293b", "#1e293b"]}
                   },
                   connector={"line": {"color": "#475569", "dash": "dot", "width": 3}}
               ))
               fig_funnel.update_layout(
                   title=dict(text="🎯 Conversion Funnel", font=dict(size=16, color='#e2e8f0')),
                   height=400,
                   template='plotly_dark',
                   paper_bgcolor='rgba(30, 41, 59, 0.6)',
                   plot_bgcolor='rgba(30, 41, 59, 0.4)',
                   font=dict(color='#e2e8f0', size=12)
               )
               st.plotly_chart(fig_funnel, use_container_width=True)


               # Source Performance
               source_perf = df_filtered.groupby('Source').agg({
                   'Applications': 'sum',
                   'Total cost (₹)': 'sum'
               }).reset_index()
               source_perf['Cost per App'] = source_perf['Total cost (₹)'] / source_perf['Applications']
               fig_source = px.scatter(
                   source_perf,
                   x='Applications',
                   y='Cost per App',
                   size='Total cost (₹)',
                   color='Source',
                   title="💎 Source Performance Matrix",
                   hover_data=['Total cost (₹)'],
                   color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b']
               )
               fig_source.update_layout(
                   height=400,
                   template='plotly_dark',
                   paper_bgcolor='rgba(30, 41, 59, 0.6)',
                   plot_bgcolor='rgba(30, 41, 59, 0.4)',
                   font=dict(color='#e2e8f0')
               )
               st.plotly_chart(fig_source, use_container_width=True)


           # Full Width Charts
           col_full1, col_full2 = st.columns(2)
           with col_full1:
               # Top Performing Campaigns
               top_campaigns = df_filtered.nlargest(10, 'Applications')[['Campaign name', 'Applications', 'Total cost (₹)']]
               fig_top = px.bar(
                   top_campaigns,
                   x='Applications',
                   y='Campaign name',
                   orientation='h',
                   title="🏆 Top 10 Campaigns by Applications",
                   color='Applications',
                   color_continuous_scale='Turbo',
                   text='Applications'
               )
               fig_top.update_traces(textposition='outside')
               fig_top.update_layout(
                   height=500,
                   showlegend=False,
                   template='plotly_dark',
                   paper_bgcolor='rgba(30, 41, 59, 0.6)',
                   plot_bgcolor='rgba(30, 41, 59, 0.4)',
                   font=dict(color='#e2e8f0')
               )
               st.plotly_chart(fig_top, use_container_width=True)
           with col_full2:
               # Cost Efficiency
               fig_cost = px.bar(
                   df_filtered.nsmallest(10, 'Cost Per Application (₹)'),
                   x='Cost Per Application (₹)',
                   y='Campaign name',
                   orientation='h',
                   title="💰 Most Cost-Efficient Campaigns",
                   color='Cost Per Application (₹)',
                   color_continuous_scale='Tealgrn',
                   text='Cost Per Application (₹)'
               )
               fig_cost.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
               fig_cost.update_layout(
                   height=500,
                   showlegend=False,
                   template='plotly_dark',
                   paper_bgcolor='rgba(30, 41, 59, 0.6)',
                   plot_bgcolor='rgba(30, 41, 59, 0.4)',
                   font=dict(color='#e2e8f0')
               )
               st.plotly_chart(fig_cost, use_container_width=True)


       # --- Tab 2: Campaign Comparison ---
       with tab2:
           st.markdown("### 🔄 Campaign Comparison")
           comparison_col1, comparison_col2 = st.columns(2)
           with comparison_col1:
               # Channel Performance
               channel_perf = df_filtered.groupby('Channel').agg({
                   'Applications': 'sum',
                   'Total cost (₹)': 'sum',
                   'Approved': 'sum',
                   'Card Out': 'sum'
               }).reset_index()
               fig_channel = go.Figure()
               fig_channel.add_trace(go.Bar(
                   x=channel_perf['Channel'],
                   y=channel_perf['Applications'],
                   name='Applications',
                   marker_color='#06b6d4'
               ))
               fig_channel.add_trace(go.Bar(
                   x=channel_perf['Channel'],
                   y=channel_perf['Approved'],
                   name='Approved',
                   marker_color='#3b82f6'
               ))
               fig_channel.add_trace(go.Bar(
                   x=channel_perf['Channel'],
                   y=channel_perf['Card Out'],
                   name='Cards Issued',
                   marker_color='#8b5cf6'
               ))
               fig_channel.update_layout(
                   title="📢 Performance by Channel",
                   barmode='group',
                   height=400,
                   template='plotly_dark',
                   paper_bgcolor='rgba(30, 41, 59, 0.6)',
                   plot_bgcolor='rgba(30, 41, 59, 0.4)',
                   font=dict(color='#e2e8f0')
               )
               st.plotly_chart(fig_channel, use_container_width=True)


           with comparison_col2:
               # Cost Distribution
               fig_cost_dist = px.pie(
                   df_filtered,
                   values='Total cost (₹)',
                   names='Source',
                   title="💸 Cost Distribution by Source",
                   hole=0.4,
                   color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b']
               )
               fig_cost_dist.update_traces(
                   textposition='inside',
                   textinfo='percent+label'
               )
               fig_cost_dist.update_layout(
                   template='plotly_dark',
                   paper_bgcolor='rgba(30, 41, 59, 0.6)',
                   font=dict(color='#e2e8f0')
               )
               st.plotly_chart(fig_cost_dist, use_container_width=True)


       # --- Tab 3: Summary Reports ---
       with tab3:
           st.markdown("### 📋 Summary Reports")
           # ... add summary report logic here ...


       # --- Tab 4: Data Table ---
       with tab4:
           st.markdown("### 📑 Data Table")
           st.dataframe(df_filtered)


       # --- Tab 5: Export ---
       with tab5:
           st.markdown("### 📥 Export Data")
           export_col1, export_col2, export_col3 = st.columns(3)


           with export_col1:
               # CSV export - Filtered Summary
               csv_data = df_filtered.to_csv(index=False).encode('utf-8')
               st.download_button(
                   "📄 Download Filtered Summary CSV",
                   data=csv_data,
                   file_name=f"RBL_Campaign_Summary_{datetime.now().strftime('%Y%m%d')}.csv",
                   mime="text/csv",
                   use_container_width=True
               )


           with export_col2:
               # Excel export - Filtered Summary
               output = BytesIO()
               with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                   df_filtered.to_excel(writer, sheet_name='Campaign Summary', index=False)
               st.download_button(
                   "📊 Download Filtered Summary Excel",
                   data=output.getvalue(),
                   file_name=f"RBL_Campaign_Summary_{datetime.now().strftime('%Y%m%d')}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   use_container_width=True
               )


   except Exception as e:
       st.error("An error occurred during processing.")
       with st.expander("View Error Details"):
           st.exception(e)


else:
   # Welcome Screen
   st.markdown("---")
   col_welcome1, col_welcome2, col_welcome3 = st.columns([1, 2, 1])
  
   with col_welcome2:
       st.markdown("""
           <div style='text-align: center; padding: 3rem;'>
               <h2 style='color: #e2e8f0;'>👋 Welcome to RBL Bank Campaign Analytics</h2>
               <p style='font-size: 1.1rem; color: #94a3b8; margin-top: 1rem;'>
                   Upload your MIS Excel file to begin
               </p>
               <div style='margin-top: 2rem; padding: 2rem;
                    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
                    border-radius: 15px; color: white; box-shadow: 0 10px 40px rgba(59, 130, 246, 0.4);'>
                   <h3>✨ Key Features</h3>
                   <ul style='list-style: none; padding: 0; text-align: left;'>
                       <li style='padding: 0.5rem 0;'>📊 Real-time analytics</li>
                       <li style='padding: 0.5rem 0;'>📋 Channel & identifier summaries</li>
                       <li style='padding: 0.5rem 0;'>🎯 UTM_CAMPAIGN matching</li>
                       <li style='padding: 0.5rem 0;'>💰 Cost-per-acquisition metrics</li>
                   </ul>
               </div>
           </div>
       """, unsafe_allow_html=True)