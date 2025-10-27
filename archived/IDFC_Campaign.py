import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="IDFC Campaign Intelligence Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Dark Mode CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background - Dark */
    .main {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Headers */
    h1 {
        color: #f1f5f9 !important;
        font-weight: 700;
        font-size: 2.5rem !important;
    }
    
    h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 600;
    }
    
    p, span, label {
        color: #cbd5e1 !important;
    }
    
    /* Metric Cards - Dark with colored accent */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 24px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 1px solid #334155;
        transition: all 0.3s;
        min-height: 120px;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        border-color: #10b981;
    }
    
    div[data-testid="stMetricValue"] {
        color: #10b981 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px !important;
        white-space: normal !important;
    }
    
    div[data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-weight: 600 !important;
    }
    
    /* Insight Boxes - Dark cards with bright text */
    .insight-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 28px;
        border-radius: 16px;
        margin: 12px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 2px solid #10b981;
        transition: all 0.3s;
    }
    
    .insight-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.3);
        border-color: #34d399;
    }
    
    .insight-box strong {
        color: #94a3b8 !important;
        font-size: 12px;
        font-weight: 600;
        display: block;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .insight-box h2 {
        color: #10b981 !important;
        margin: 8px 0 !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        white-space: normal !important;
        overflow: visible !important;
        word-break: break-word !important;
    }
    
    .insight-box small {
        color: #cbd5e1 !important;
        font-size: 13px;
    }
    
    /* Tabs - Dark style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0f172a;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 14px 28px;
        color: #94a3b8 !important;
        font-weight: 600;
        border: 1px solid #334155;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #334155;
        border-color: #10b981;
        color: #e2e8f0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #10b981 !important;
        color: #0f172a !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid #334155;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #0f172a !important;
        border: none;
        padding: 12px 32px;
        border-radius: 10px;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 28px rgba(16, 185, 129, 0.5);
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
    }
    
    /* Download buttons */
    .stDownloadButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white !important;
        border: none;
        padding: 12px 32px;
        border-radius: 10px;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
        transition: all 0.3s;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 28px rgba(59, 130, 246, 0.5);
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #1e293b;
        padding: 24px;
        border-radius: 12px;
        border: 2px dashed #334155;
    }
    
    .stFileUploader:hover {
        border-color: #10b981;
    }
    
    /* Divider */
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
    }
    
    /* Welcome Screen */
    .welcome-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 80px 60px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
        margin: 60px auto;
        max-width: 900px;
        border: 2px solid #334155;
    }
    
    .welcome-box h2 {
        color: #10b981 !important;
        font-size: 42px;
        margin-bottom: 24px;
        font-weight: 700;
    }
    
    .welcome-box p {
        color: #cbd5e1 !important;
        font-size: 18px;
        margin: 16px 0;
    }
    
    .welcome-icon {
        font-size: 72px;
        margin-bottom: 28px;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 20px 28px;
        border-radius: 12px;
        margin: 24px 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .section-header h2, .section-header h3 {
        margin: 0 !important;
        color: #f1f5f9 !important;
    }
    
    /* Data tables */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* Success/Info messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        border-radius: 12px;
        padding: 16px;
        border: none;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white !important;
        border-radius: 12px;
        padding: 16px;
        border: none;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white !important;
        border-radius: 12px;
        padding: 16px;
        border: none;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #10b981 !important;
    }
    
    /* Checkbox */
    .stCheckbox {
        color: #cbd5e1 !important;
    }
    
    /* Selectbox */
    .stSelectbox label {
        color: #cbd5e1 !important;
    }
    
    /* All text elements */
    div, span, p, label {
        color: #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🎯 IDFC Campaign Intelligence Hub")
st.markdown("<p style='color: #94a3b8; font-size: 16px; font-weight: 500;'>Advanced analytics and insights for marketing campaign performance</p>", unsafe_allow_html=True)
st.divider()

# --- Google Sheet Configuration ---
identifiers_sheet_url = "https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/edit?gid=0#gid=0"
identifiers_csv_url = identifiers_sheet_url.replace("/edit?gid=", "/export?format=csv&gid=")
output_sheet_id = "1LNzJzk2EA54sg_VvAt9ee9GEsJtGKEA7ZPw5pmtTprk"

# --- Campaign Costs ---
campaign_costs = {
    "SMS": 0.1,
    "RCS": 0.085,
    "Whatsapp Marketing": 0.80,
    "Whatsapp Utility": 0.115
}

# --- Google API Authentication ---
@st.cache_resource
def get_gsheet_client():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

client = get_gsheet_client()
sheet = client.open_by_key(output_sheet_id)

# --- Function to Update Google Sheet ---
def update_sheet(sheet_obj, sheet_name, df):
    try:
        worksheet = sheet_obj.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet_obj.add_worksheet(title=sheet_name, rows=str(len(df)+10), cols=str(len(df.columns)+10))
    
    worksheet.clear()
    data = [df.columns.tolist()] + df.astype(str).values.tolist()
    worksheet.update('A1', data, value_input_option='USER_ENTERED')

# --- Session State ---
if "mis_uploaded" not in st.session_state:
    st.session_state.mis_uploaded = None
if "df_output" not in st.session_state:
    st.session_state.df_output = None
if "df_summary" not in st.session_state:
    st.session_state.df_summary = None

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📂 Data Upload")
    mis_file = st.file_uploader("Upload MIS Excel File", type=["xlsx"], help="Upload your campaign MIS data")
    
    st.divider()
    st.markdown("### ⚙️ Settings")
    
    show_detailed = st.checkbox("Show Detailed Analysis", value=True)
    show_charts = st.checkbox("Show Interactive Charts", value=True)
    
    st.divider()
    st.markdown("### 💡 Quick Stats")
    if st.session_state.df_summary is not None:
        total_apps = st.session_state.df_summary["Applications"].sum()
        total_cost = st.session_state.df_summary["Total cost"].sum()
        st.metric("Total Applications", f"{total_apps:,}")
        st.metric("Total Investment", f"₹{total_cost:,.2f}")

# --- Main Processing ---
if mis_file:
    if st.session_state.mis_uploaded != mis_file.name:
        st.session_state.mis_uploaded = mis_file.name
        
        with st.spinner("🔄 Processing data with advanced analytics..."):
            # Load identifiers
            df_identifiers = pd.read_csv(identifiers_csv_url)
            df_identifiers.columns = df_identifiers.columns.str.strip()
            
            # Remove duplicate columns if they exist
            df_identifiers = df_identifiers.loc[:, ~df_identifiers.columns.duplicated()].copy()
            
            df_identifiers["Identifiers"] = df_identifiers["Identifiers"].astype(str)
            
            # Load MIS
            df_mis = pd.read_excel(mis_file, sheet_name="App Details")
            df_mis.columns = df_mis.columns.str.strip()
            df_mis["UTM Campaign"] = df_mis["UTM Campaign"].astype(str)
            df_mis["Sub Stage"] = df_mis["Sub Stage"].astype(str)
            df_mis["Soft Decision"] = df_mis["Soft Decision"].astype(str)
            
            # Define substages
            substage_list = [
                "EKYC Initiated","Address Check","Card Generation Completed","Card Generation Pending",
                "Curing Initiated","DDE Pending","FD QDE Pending","FI Reject","INC C2C Doc Check",
                "Manual Doc Upload","Offer Expired","Offer Generated","OPS Reject","Payment Pending",
                "Policy Reject","Posidex Reject","Pre FICO Check","QDE Pending","Sales Cancelled",
                "System Cancelled","T&C Pending","Underwriting Pending","Underwriting Reject",
                "Verification Pending","VKYC Initiated","VKYC Initiation Pending"
            ]
            decline_substages = [
                "FI Reject","Offer Expired","OPS Reject","Policy Reject",
                "Posidex Reject","Sales Cancelled","System Cancelled","Underwriting Reject"
            ]
            
            # Build detailed output
            output_rows = []
            for _, ident_row in df_identifiers.iterrows():
                ident = ident_row["Identifiers"]
                mis_filtered = df_mis[df_mis["UTM Campaign"].str.contains(ident, case=False, na=False)]
                
                row = ident_row.to_dict()
                row["Applications"] = len(mis_filtered)
                
                for substage in substage_list:
                    row[substage] = (mis_filtered["Sub Stage"] == substage).sum()
                
                row["IPA Approved"] = (mis_filtered["Soft Decision"].str.lower() == "approved").sum()
                row["Decline"] = mis_filtered["Sub Stage"].isin(decline_substages).sum()
                row["Card Out"] = (mis_filtered["Sub Stage"] == "Card Generation Completed").sum()
                row["Delivered"] = ident_row.get("Delivered", 0)
                row["Read"] = ident_row.get("Read", 0)
                row["Clicks"] = ident_row.get("Clicks", 0)
                
                output_rows.append(row)
            
            df_output = pd.DataFrame(output_rows)
            
            # Remove duplicate columns if they exist
            df_output = df_output.loc[:, ~df_output.columns.duplicated()].copy()
            
            # Build summary
            summary_rows = []
            for channel, cost_per_unit in campaign_costs.items():
                df_channel = df_output[df_output.get("Channel", "").str.lower() == channel.lower()]
                applications = df_channel["Applications"].sum()
                inprogress = applications - df_channel["Decline"].sum() - df_channel["IPA Approved"].sum() - df_channel["Card Out"].sum()
                declined = df_channel["Decline"].sum()
                ipa_approved = df_channel["IPA Approved"].sum()
                card_out = df_channel["Card Out"].sum()
                delivered = df_channel["Delivered"].sum()
                read = df_channel["Read"].sum()
                clicks = df_channel["Clicks"].sum()
                
                ctr = clicks / delivered if delivered else 0
                cpc = delivered * cost_per_unit / clicks if clicks else 0
                total_cost = delivered * cost_per_unit
                cost_per_application = total_cost / applications if applications else 0
                cost_per_ipa = total_cost / ipa_approved if ipa_approved else 0
                cost_per_card = total_cost / card_out if card_out else 0
                
                summary_rows.append({
                    "Channel": channel,
                    "Applications": applications,
                    "Inprogress": inprogress,
                    "Declined": declined,
                    "IPA approved": ipa_approved,
                    "Card Out": card_out,
                    "Delivered": delivered,
                    "Read": read,
                    "Clicks": clicks,
                    "CTR": round(ctr * 100, 2),
                    "CPC": round(cpc, 2),
                    "Cost per unit": cost_per_unit,
                    "Total cost": round(total_cost, 2),
                    "Cost Per Application": round(cost_per_application, 2),
                    "Cost per IPA approved": round(cost_per_ipa, 2),
                    "Cost per Card Out": round(cost_per_card, 2)
                })
            
            df_summary = pd.DataFrame(summary_rows)
            
            # Remove duplicate columns if they exist
            df_summary = df_summary.loc[:, ~df_summary.columns.duplicated()].copy()
            
            # Store in session state
            st.session_state.df_output = df_output
            st.session_state.df_summary = df_summary
            
            # Update Google Sheets
            update_sheet(sheet, "Analysis", df_output)
            update_sheet(sheet, "Summary", df_summary)
            
            st.success("✅ Data processed and synced to Google Sheets successfully!")

# --- Display Dashboard ---
if st.session_state.df_summary is not None:
    df_summary = st.session_state.df_summary
    df_output = st.session_state.df_output
    
    # --- KPI Overview ---
    st.markdown("<div class='section-header'><h2>📊 Key Performance Indicators</h2></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_apps = df_summary["Applications"].sum()
        st.metric("Total Applications", f"{total_apps:,}")
    
    with col2:
        total_ipa = df_summary["IPA approved"].sum()
        ipa_rate = (total_ipa / total_apps * 100) if total_apps > 0 else 0
        st.metric("IPA Approved", f"{total_ipa:,}", delta=f"{ipa_rate:.1f}%")
    
    with col3:
        total_cards = df_summary["Card Out"].sum()
        card_rate = (total_cards / total_apps * 100) if total_apps > 0 else 0
        st.metric("Cards Issued", f"{total_cards:,}", delta=f"{card_rate:.1f}%")
    
    with col4:
        total_cost = df_summary["Total cost"].sum()
        st.metric("Total Investment", f"₹{total_cost:,.2f}")
    
    with col5:
        avg_cpa = df_summary["Cost Per Application"].mean()
        st.metric("Avg Cost/App", f"₹{avg_cpa:.2f}")
    
    st.divider()
    
    # --- Tabs for Different Views ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Performance Overview", "🔍 Channel Analysis", "💰 Cost Efficiency", "🏆 Top Identifiers", "📋 Detailed Data"])
    
    with tab1:
        st.markdown("<div class='section-header'><h3>Campaign Performance Funnel</h3></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Funnel Chart
            funnel_data = pd.DataFrame({
                'Stage': ['Delivered', 'Clicks', 'Applications', 'IPA Approved', 'Card Out'],
                'Count': [
                    df_summary['Delivered'].sum(),
                    df_summary['Clicks'].sum(),
                    df_summary['Applications'].sum(),
                    df_summary['IPA approved'].sum(),
                    df_summary['Card Out'].sum()
                ]
            })
            
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                textposition="inside",
                textinfo="value+percent initial",
                textfont=dict(size=15, color='#0f172a', family='Inter', weight=600),
                marker=dict(
                    color=['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'],
                    line=dict(width=0)
                )
            ))
            
            fig_funnel.update_layout(
                height=450,
                paper_bgcolor='#0f172a',
                plot_bgcolor='#0f172a',
                font=dict(color='#e2e8f0', size=12, family='Inter'),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Key Insights")
            
            click_rate = (df_summary['Clicks'].sum() / df_summary['Delivered'].sum() * 100) if df_summary['Delivered'].sum() > 0 else 0
            app_rate = (df_summary['Applications'].sum() / df_summary['Clicks'].sum() * 100) if df_summary['Clicks'].sum() > 0 else 0
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Click Through Rate</strong>
                <h2>{click_rate:.2f}%</h2>
                <small>From delivered messages</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>Application Rate</strong>
                <h2>{app_rate:.2f}%</h2>
                <small>From clicks to applications</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Channel Comparison
        st.markdown("<div class='section-header'><h3>Channel Performance Comparison</h3></div>", unsafe_allow_html=True)
        
        fig_channel = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Applications by Channel", "Success Rate by Channel"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        fig_channel.add_trace(
            go.Bar(
                x=df_summary['Channel'], 
                y=df_summary['Applications'],
                marker_color='#10b981',
                marker_line=dict(width=0),
                name='Applications',
                text=df_summary['Applications'],
                textposition='outside',
                textfont=dict(size=14, color='#e2e8f0', weight=700),
                texttemplate='%{text}'
            ),
            row=1, col=1
        )
        
        success_rate = (df_summary['Card Out'] / df_summary['Applications'] * 100).fillna(0)
        fig_channel.add_trace(
            go.Bar(
                x=df_summary['Channel'], 
                y=success_rate,
                marker_color='#3b82f6',
                marker_line=dict(width=0),
                name='Success Rate %',
                text=[f"{x:.1f}%" for x in success_rate],
                textposition='outside',
                textfont=dict(size=14, color='#e2e8f0', weight=700),
                texttemplate='%{text}'
            ),
            row=1, col=2
        )
        
        fig_channel.update_layout(
            height=450,
            showlegend=False,
            paper_bgcolor='#0f172a',
            plot_bgcolor='#0f172a',
            font=dict(color='#e2e8f0', size=12, family='Inter'),
            margin=dict(t=50, b=40, l=40, r=40)
        )
        
        fig_channel.update_xaxes(showgrid=False, tickfont=dict(color='#e2e8f0'))
        fig_channel.update_yaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#e2e8f0'))
        
        # Prevent clipping of text labels
        fig_channel.update_yaxes(range=[0, df_summary['Applications'].max() * 1.15], row=1, col=1)
        fig_channel.update_yaxes(range=[0, success_rate.max() * 1.15], row=1, col=2)
        
        st.plotly_chart(fig_channel, use_container_width=True)
    
    with tab2:
        st.markdown("<div class='section-header'><h3>In-Depth Channel Analysis</h3></div>", unsafe_allow_html=True)
        
        # Channel selector
        selected_channel = st.selectbox("Select Channel for Deep Dive", df_summary['Channel'].tolist())
        
        channel_data = df_summary[df_summary['Channel'] == selected_channel].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Applications", f"{int(channel_data['Applications']):,}")
            st.metric("In Progress", f"{int(channel_data['Inprogress']):,}")
        
        with col2:
            st.metric("IPA Approved", f"{int(channel_data['IPA approved']):,}")
            st.metric("Declined", f"{int(channel_data['Declined']):,}")
        
        with col3:
            st.metric("Card Out", f"{int(channel_data['Card Out']):,}")
            st.metric("CTR", f"{channel_data['CTR']:.2f}%")
        
        # Status Distribution Pie Chart
        st.markdown(f"<div class='section-header'><h3>{selected_channel} - Status Distribution</h3></div>", unsafe_allow_html=True)
        
        status_values = [
            channel_data['Inprogress'],
            channel_data['IPA approved'],
            channel_data['Card Out'],
            channel_data['Declined']
        ]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['In Progress', 'IPA Approved', 'Card Out', 'Declined'],
            values=status_values,
            hole=0.5,
            marker_colors=['#f59e0b', '#10b981', '#3b82f6', '#ef4444'],
            textfont=dict(size=14, color='#0f172a', family='Inter', weight=600),
            textposition='inside'
        )])
        
        fig_pie.update_layout(
            height=450,
            paper_bgcolor='#0f172a',
            plot_bgcolor='#0f172a',
            font=dict(color='#e2e8f0', size=12, family='Inter'),
            legend=dict(font=dict(color='#e2e8f0', size=12)),
            margin=dict(t=40, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        st.markdown("<div class='section-header'><h3>Cost Efficiency Analysis</h3></div>", unsafe_allow_html=True)
        
        # Cost Metrics
        col1, col2 = st.columns(2)
        
        with col1:
            fig_cost = px.bar(
                df_summary,
                x='Channel',
                y=['Cost Per Application', 'Cost per IPA approved', 'Cost per Card Out'],
                barmode='group',
                color_discrete_sequence=['#10b981', '#3b82f6', '#8b5cf6'],
                text_auto='.2f'
            )
            fig_cost.update_traces(
                textposition='outside',
                textfont=dict(size=13, color='#e2e8f0', weight=700)
            )
            fig_cost.update_layout(
                paper_bgcolor='#0f172a',
                plot_bgcolor='#0f172a',
                legend_title_text='Cost Metrics',
                font=dict(color='#e2e8f0', size=12, family='Inter'),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#e2e8f0')),
                margin=dict(t=50, b=40, l=40, r=40),
                height=450
            )
            fig_cost.update_xaxes(showgrid=False, tickfont=dict(color='#e2e8f0'))
            fig_cost.update_yaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#e2e8f0'))
            
            # Add space for text labels on top
            max_cost = df_summary[['Cost Per Application', 'Cost per IPA approved', 'Cost per Card Out']].max().max()
            fig_cost.update_yaxes(range=[0, max_cost * 1.15])
            st.plotly_chart(fig_cost, use_container_width=True)
        
        with col2:
            # ROI Analysis
            fig_roi = px.scatter(
                df_summary,
                x='Total cost',
                y='Card Out',
                size='Applications',
                color='Channel',
                color_discrete_sequence=['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                hover_data=['Applications', 'CTR']
            )
            fig_roi.update_layout(
                paper_bgcolor='#0f172a',
                plot_bgcolor='#0f172a',
                font=dict(color='#e2e8f0', size=12, family='Inter'),
                legend=dict(font=dict(color='#e2e8f0')),
                margin=dict(t=40, b=40, l=40, r=40),
                height=450
            )
            fig_roi.update_xaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#e2e8f0'))
            fig_roi.update_yaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#e2e8f0'))
            st.plotly_chart(fig_roi, use_container_width=True)
        
        # Cost Efficiency Table
        st.markdown("<div class='section-header'><h3>Cost Efficiency Scorecard</h3></div>", unsafe_allow_html=True)
        
        efficiency_df = df_summary[['Channel', 'Total cost', 'Cost Per Application', 
                                     'Cost per IPA approved', 'Cost per Card Out', 'CTR']].copy()
        
        st.dataframe(
            efficiency_df.style.format({
                'Total cost': '₹{:.2f}',
                'Cost Per Application': '₹{:.2f}',
                'Cost per IPA approved': '₹{:.2f}',
                'Cost per Card Out': '₹{:.2f}',
                'CTR': '{:.2f}%'
            }),
            use_container_width=True,
            height=250
        )
    
    with tab4:
        st.markdown("<div class='section-header'><h3>🏆 Top Performing Sources</h3></div>", unsafe_allow_html=True)
        
        # Try to find Source column with different variations
        source_col = None
        possible_names = ['Source', 'source', 'Sources', 'sources', 'SOURCE']
        
        for col_name in possible_names:
            if col_name in df_output.columns:
                source_col = col_name
                break
        
        if source_col is None:
            st.error("⚠️ 'Source' column not found. Please ensure your identifiers sheet has a 'Source' column.")
        else:
            # Aggregate data by Source
            df_by_source = df_output.groupby(source_col, as_index=False).agg({
                'Channel': 'first',
                'Applications': 'sum',
                'IPA Approved': 'sum',
                'Card Out': 'sum',
                'Decline': 'sum',
                'Delivered': 'sum',
                'Read': 'sum',
                'Clicks': 'sum'
            })
            
            df_by_source = df_by_source.rename(columns={source_col: 'Source'})
            df_by_source['CTR'] = (df_by_source['Clicks'] / df_by_source['Delivered'] * 100).fillna(0).round(2)
            
            # Compact filter controls in one row
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                metric_options = {
                    "Applications": "Applications",
                    "IPA Approved": "IPA Approved",
                    "Card Out": "Card Out",
                    "CTR (Click Rate)": "CTR",
                    "Delivered": "Delivered",
                    "Clicks": "Clicks",
                    "Read": "Read"
                }
                selected_metric = st.selectbox("📊 Performance Metric", list(metric_options.keys()))
                metric_column = metric_options[selected_metric]
            
            with col2:
                top_n = st.slider("🔢 Top N", min_value=5, max_value=50, value=10, step=5)
            
            with col3:
                channel_filter_options = ["All Channels"] + df_summary['Channel'].tolist()
                selected_channel_filter = st.selectbox("📱 Channel", channel_filter_options)
            
            with col4:
                # Quick stats in compact format
                if selected_channel_filter != "All Channels":
                    df_filtered = df_by_source[df_by_source['Channel'].str.lower() == selected_channel_filter.lower()].copy()
                else:
                    df_filtered = df_by_source.copy()
                
                st.metric("Sources", len(df_filtered), delta=None)
            
            df_top = df_filtered.nlargest(top_n, metric_column).copy()
            
            # Main visualization in two columns
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                st.markdown(f"**Top {top_n} Sources by {selected_metric}**")
                
                df_top_sorted = df_top.sort_values(by=metric_column, ascending=True)
                
                fig_sources = go.Figure()
                fig_sources.add_trace(go.Bar(
                    y=df_top_sorted['Source'],
                    x=df_top_sorted[metric_column],
                    orientation='h',
                    marker=dict(
                        color=df_top_sorted[metric_column],
                        colorscale='Viridis',
                        showscale=False
                    ),
                    text=df_top_sorted[metric_column],
                    textposition='outside',
                    textfont=dict(size=11, color='#e2e8f0', weight=700),
                    texttemplate='%{text:.2f}' if metric_column == 'CTR' else '%{text}',
                    hovertemplate='<b>%{y}</b><br>' + selected_metric + ': %{x}<extra></extra>'
                ))
                
                fig_sources.update_layout(
                    height=max(350, top_n * 28),
                    paper_bgcolor='#0f172a',
                    plot_bgcolor='#0f172a',
                    font=dict(color='#e2e8f0', size=10, family='Inter'),
                    margin=dict(l=180, r=60, t=10, b=30),
                    showlegend=False
                )
                
                fig_sources.update_xaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#e2e8f0', size=9))
                fig_sources.update_yaxes(showgrid=False, tickfont=dict(color='#e2e8f0', size=9))
                
                st.plotly_chart(fig_sources, use_container_width=True)
            
            with col_right:
                st.markdown("**Performance Insights**")
                
                # Compact stats
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Avg", f"{df_filtered[metric_column].mean():.1f}", delta=None)
                    st.metric("Max", f"{df_filtered[metric_column].max():.1f}", delta=None)
                with col_b:
                    st.metric("Min", f"{df_filtered[metric_column].min():.1f}", delta=None)
                    st.metric("Median", f"{df_filtered[metric_column].median():.1f}", delta=None)
                
                # Performance tiers - compact version
                q3 = df_filtered[metric_column].quantile(0.75)
                q1 = df_filtered[metric_column].quantile(0.25)
                
                tier_top = df_filtered[df_filtered[metric_column] >= q3]
                tier_low = df_filtered[df_filtered[metric_column] < q1]
                
                st.markdown("---")
                st.markdown("**🥇 Top Tier** (75th+ percentile)")
                if len(tier_top) > 0:
                    for idx, row in tier_top.nlargest(3, metric_column).iterrows():
                        st.write(f"• {row['Source']}: **{row[metric_column]:.1f}**")
                
                st.markdown("**📊 Needs Improvement** (<25th)")
                if len(tier_low) > 0:
                    for idx, row in tier_low.head(3).iterrows():
                        st.write(f"• {row['Source']}: {row[metric_column]:.1f}")
            
            # Comparison and detailed data in tabs for better space
            subtab1, subtab2 = st.tabs(["📊 Comparison", "📋 Detailed Data"])
            
            with subtab1:
                top_10 = df_filtered.nlargest(10, metric_column)[['Source', metric_column]].copy()
                bottom_10 = df_filtered.nsmallest(10, metric_column)[['Source', metric_column]].copy()
                
                fig_comparison = go.Figure()
                
                fig_comparison.add_trace(go.Bar(
                    name='Top 10',
                    x=top_10['Source'],
                    y=top_10[metric_column],
                    marker_color='#10b981',
                    text=top_10[metric_column],
                    textposition='outside',
                    textfont=dict(size=10, color='#e2e8f0', weight=700),
                    texttemplate='%{text:.1f}' if metric_column == 'CTR' else '%{text}'
                ))
                
                fig_comparison.add_trace(go.Bar(
                    name='Bottom 10',
                    x=bottom_10['Source'],
                    y=bottom_10[metric_column],
                    marker_color='#ef4444',
                    text=bottom_10[metric_column],
                    textposition='outside',
                    textfont=dict(size=10, color='#e2e8f0', weight=700),
                    texttemplate='%{text:.1f}' if metric_column == 'CTR' else '%{text}'
                ))
                
                fig_comparison.update_layout(
                    height=380,
                    paper_bgcolor='#0f172a',
                    plot_bgcolor='#0f172a',
                    font=dict(color='#e2e8f0', size=9, family='Inter'),
                    margin=dict(l=30, r=30, t=30, b=100),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#e2e8f0')),
                    barmode='group'
                )
                
                fig_comparison.update_xaxes(showgrid=False, tickfont=dict(color='#e2e8f0', size=8), tickangle=-45)
                fig_comparison.update_yaxes(showgrid=True, gridcolor='#334155', tickfont=dict(color='#e2e8f0'))
                
                st.plotly_chart(fig_comparison, use_container_width=True)
            
            with subtab2:
                display_columns = ['Source', 'Channel', 'Applications', 'IPA Approved', 'Card Out', 'Delivered', 'Clicks', 'CTR']
                
                st.dataframe(
                    df_top[display_columns].style.format({
                        'Applications': '{:.0f}',
                        'IPA Approved': '{:.0f}',
                        'Card Out': '{:.0f}',
                        'Delivered': '{:.0f}',
                        'Clicks': '{:.0f}',
                        'CTR': '{:.2f}%'
                    }),
                    use_container_width=True,
                    height=350
                )
                
                csv_top = df_top[display_columns].to_csv(index=False).encode('utf-8')
                st.download_button(
                    f"📥 Download Top {top_n} Sources",
                    csv_top,
                    f"top_{top_n}_sources.csv",
                    "text/csv",
                    key='download-top-performers'
                )
    
    with tab5:
        st.markdown("<div class='section-header'><h3>Comprehensive Data Export</h3></div>", unsafe_allow_html=True)
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_summary = df_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Summary CSV",
                csv_summary,
                "campaign_summary.csv",
                "text/csv",
                key='download-summary'
            )
        
        with col2:
            csv_detailed = df_output.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Detailed CSV",
                csv_detailed,
                "campaign_detailed.csv",
                "text/csv",
                key='download-detailed'
            )
        
        with col3:
            # Combined Excel file with both sheets
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                df_output.to_excel(writer, sheet_name='Detailed Analysis', index=False)
            
            excel_data = buffer.getvalue()
            st.download_button(
                "📥 Download Combined Excel",
                excel_data,
                "campaign_complete_report.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download-combined'
            )
        
        # Summary Table
        st.markdown("#### Summary Overview")
        st.dataframe(df_summary, use_container_width=True, height=300)
        
        if show_detailed:
            st.markdown("#### Detailed Campaign Data")
            st.dataframe(df_output, use_container_width=True, height=400)

else:
    # Welcome Screen
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-icon">📊</div>
        <h2>Welcome to Campaign Intelligence Hub</h2>
        <p>Upload your MIS file to unlock powerful insights and analytics</p>
        <p style="font-size: 16px;">✨ Advanced Analytics • 💡 Actionable Insights • 📈 Real-time Tracking</p>
    </div>
    """, unsafe_allow_html=True)