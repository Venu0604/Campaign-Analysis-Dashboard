import pandas as pd
import streamlit as st
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -------------------------
# Campaign costs by channel
# -------------------------
CAMPAIGN_COSTS = {
    "SMS": 0.10,
    "RCS": 0.085,
    "Whatsapp Marketing": 0.80,
    "Whatsapp Utility": 0.115,
    "Email": 0.05,
}

# -------------------------
# AU Bank Status Definitions
# -------------------------
CARD_OUT_STATUS = ["DISBURSED"]

DECLINED_STATUS = [
    "REJECTED CASE",
    "BRE DECLINE CASE",
    "CREDIT REJECT CASE",
    "REJECT FOR CURING",
    "Gating Criteria Not Met (CIBIL)",
    "PAN AADHAAR CHECK REJECT",
    "DVU REJECT CASE",
    "LOGICAL DELETED",
    "BUREAU DECLINE CASE"
]

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="AU Bank Campaign Dashboard", layout="wide", page_icon="🏦")

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
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #ea580c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-in-out;
        text-shadow: 0 0 40px rgba(245, 158, 11, 0.2);
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
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.4);
        color: white;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(217, 119, 6, 0.5);
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
        color: #f59e0b !important;
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
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
        color: white !important;
        border: none;
    }

    /* Download Button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }

    .stDownloadButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(234, 88, 12, 0.4);
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

st.markdown('<div class="main-header">🏦 AU Bank Campaign Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time Performance Tracking & Insights</div>', unsafe_allow_html=True)

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown("### 🎯 Dashboard Controls")
    st.info("📊 Upload your MIS file and apply filters to analyze campaign performance in real-time.")

    # Cost Display by Channel
    st.markdown("### 💰 Campaign Economics")
    for channel, cost in CAMPAIGN_COSTS.items():
        st.metric(channel, f"₹{cost:.3f}/unit")

# -------------------------
# Load Identifiers from Google Sheet (AU Bank Sheet)
# -------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid=1138241151"

try:
    df_identifiers = pd.read_csv(sheet_url)
    df_identifiers.columns = df_identifiers.columns.str.strip()

    # Convert Date column to datetime
    df_identifiers['Date'] = pd.to_datetime(df_identifiers['Date'], format='%d-%m-%Y', errors='coerce')

    st.sidebar.success(f"✅ Loaded {len(df_identifiers)} campaigns")
except Exception as e:
    st.sidebar.error(f"❌ Error loading identifiers: {e}")
    df_identifiers = None

# -------------------------
# File Upload
# -------------------------
st.markdown("### 📁 Data Upload")
mis_file = st.file_uploader("Upload MIS File (Excel)", type=["xlsx"], help="Upload your MIS Excel file to begin analysis")

# -------------------------
# Main Analysis Logic
# -------------------------
if mis_file and df_identifiers is not None:
    try:
        df_mis = pd.read_excel(mis_file, sheet_name=0)
        df_mis.columns = df_mis.columns.str.strip()

        # Handle duplicate column names by making them unique
        cols = pd.Series(df_mis.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df_mis.columns = cols

        # Normalize column names for easier access
        column_map = {}
        for col in df_mis.columns:
            normalized = col.lower().strip()
            column_map[col] = normalized

        df_mis.rename(columns=column_map, inplace=True)

        # Find the UTM_CAMPAIGN column (case insensitive)
        utm_col = None
        for col in df_mis.columns:
            if 'utm_campaign' in col.lower() or 'utm campaign' in col.lower():
                utm_col = col
                break

        if utm_col is None:
            st.error("❌ UTM_CAMPAIGN column not found in MIS file. Please check the file structure.")
            st.stop()

        # Find CURRENT_STATUS column
        status_col = None
        for col in df_mis.columns:
            if 'current' in col.lower() and 'status' in col.lower():
                status_col = col
                break

        if status_col is None:
            # Try to find any status column
            for col in df_mis.columns:
                if 'status' in col.lower():
                    status_col = col
                    break

        if status_col is None:
            st.warning("⚠️ CURRENT_STATUS column not found. Status analysis will be limited.")

        # Find BRE_OUTPUT column for IPA status
        bre_output_col = None
        for col in df_mis.columns:
            if 'bre_output' in col.lower() or 'bre output' in col.lower():
                bre_output_col = col
                break

        output_rows = []
        matched_mis_records = []  # Store all matched MIS records

        for _, row in df_identifiers.iterrows():
            date = row.get("Date", "")
            identifier = str(row.get("Identifiers", "")).strip()
            source = str(row.get("Source", "")).strip()
            channel = str(row.get("Channel", "")).strip().lower()
            delivered = float(row.get("Delivered", 0))
            clicks = float(row.get("Clicks", 0))
            read_count = float(row.get("Read", 0))

            # Get channel-specific cost (default to SMS cost if channel not found)
            channel_key = channel.title()
            if "sms" in channel.lower():
                channel_key = "SMS"
            elif "rcs" in channel.lower():
                channel_key = "RCS"
            elif "whatsapp" in channel.lower():
                if "utility" in channel.lower():
                    channel_key = "Whatsapp Utility"
                else:
                    channel_key = "Whatsapp Marketing"
            elif "email" in channel.lower():
                channel_key = "Email"

            cost_per_unit = CAMPAIGN_COSTS.get(channel_key, CAMPAIGN_COSTS["SMS"])

            # Filter MIS data where UTM_CAMPAIGN contains the identifier
            mask = df_mis[utm_col].astype(str).str.contains(identifier, case=False, na=False)
            df_filtered_mis = df_mis[mask]

            # Add identifier metadata to matched records
            if len(df_filtered_mis) > 0:
                df_matched_copy = df_filtered_mis.copy()
                df_matched_copy['Matched_Identifier'] = identifier
                df_matched_copy['Campaign_Date'] = date
                df_matched_copy['Campaign_Source'] = source
                df_matched_copy['Campaign_Channel'] = channel
                matched_mis_records.append(df_matched_copy)

            applications = len(df_filtered_mis)

            # Status analysis based on CURRENT_STATUS column
            # Card Out = "DISBURSED"
            # Declined = List of decline statuses
            # Remaining = In Progress
            if status_col:
                status_values = df_filtered_mis[status_col].astype(str).str.strip()

                # Card Out (Disbursed status)
                card_out = status_values.str.upper().isin([s.upper() for s in CARD_OUT_STATUS]).sum()

                # Declined
                declined = status_values.str.upper().isin([s.upper() for s in DECLINED_STATUS]).sum()

                # In Progress (everything except Card Out and Declined)
                in_progress = applications - card_out - declined
            else:
                card_out = 0
                declined = 0
                in_progress = applications

            # IPA Status analysis based on BRE_OUTPUT column
            # Count where BRE_OUTPUT = "APPROVED"
            if bre_output_col:
                bre_values = df_filtered_mis[bre_output_col].astype(str).str.strip()
                ipa_approved = (bre_values.str.upper() == 'APPROVED').sum()
            else:
                # Fallback if BRE_OUTPUT column not found
                ipa_approved = card_out

            # Metrics with channel-specific cost
            ctr = round((clicks / delivered * 100), 2) if delivered > 0 else 0
            cpc = round((cost_per_unit * delivered / clicks), 2) if clicks > 0 else 0
            read_rate = round((read_count / delivered * 100), 2) if delivered > 0 else 0
            total_cost = round(delivered * cost_per_unit, 2)
            cost_per_app = round(total_cost / applications, 2) if applications > 0 else 0
            cost_per_ipa = round(total_cost / ipa_approved, 2) if ipa_approved > 0 else 0
            cost_per_card = round(total_cost / card_out, 2) if card_out > 0 else 0

            output_rows.append({
                "Date": date,
                "Campaign name": identifier,
                "Source": source,
                "Applications": applications,
                "IPA Approved": ipa_approved,
                "Declined": declined,
                "In Progress": in_progress,
                "Card Out": card_out,
                "Delivered": delivered,
                "Read": read_count,
                "Clicks": clicks,
                "CTR (%)": ctr,
                "Read Rate (%)": read_rate,
                "CPC (₹)": cpc,
                "Cost per unit (₹)": cost_per_unit,
                "Total cost (₹)": total_cost,
                "Cost per Application (₹)": cost_per_app,
                "Cost per IPA (₹)": cost_per_ipa,
                "Cost per Card Out (₹)": cost_per_card,
                "Channel": channel
            })

        df_summary = pd.DataFrame(output_rows)

        # Ensure Date is datetime
        df_summary['Date'] = pd.to_datetime(df_summary['Date'], errors='coerce')

        # Combine all matched MIS records into one DataFrame
        if matched_mis_records:
            df_matched_mis_all = pd.concat(matched_mis_records, ignore_index=True)
        else:
            df_matched_mis_all = pd.DataFrame()  # Empty if no matches

        st.success(f"✅ Successfully processed {len(df_summary)} campaign records | {len(df_matched_mis_all)} MIS records matched")

        # -------------------------
        # Interactive Filters
        # -------------------------
        st.markdown("---")
        st.markdown("### 🔍 Interactive Filters")

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
                    max_value=max_date,
                    help="Select the date range for analysis"
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
            selected_source = st.selectbox("🎯 Source", sources, help="Filter by traffic source")

            if selected_source != "All Sources":
                df_filtered = df_filtered[df_filtered['Source'] == selected_source]

        with filter_col3:
            # Channel Filter
            channels = ["All Channels"] + sorted(df_summary['Channel'].unique().tolist())
            selected_channel = st.selectbox("📢 Channel", channels, help="Filter by marketing channel")

            if selected_channel != "All Channels":
                df_filtered = df_filtered[df_filtered['Channel'] == selected_channel]

        with filter_col4:
            # Campaign Filter
            campaigns = ["All Campaigns"] + sorted(df_summary['Campaign name'].unique().tolist())
            selected_campaign = st.selectbox("🎪 Campaign", campaigns, help="Filter by specific campaign")

            if selected_campaign != "All Campaigns":
                df_filtered = df_filtered[df_filtered['Campaign name'] == selected_campaign]

        # -------------------------
        # Enhanced Key Metrics with Custom Cards
        # -------------------------
        st.markdown("---")
        st.markdown("### 📊 Performance Dashboard")

        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

        total_apps = df_filtered["Applications"].sum()
        total_cost = df_filtered["Total cost (₹)"].sum()
        total_ipa_approved = df_filtered["IPA Approved"].sum()
        total_card_out = df_filtered["Card Out"].sum()
        total_declined = df_filtered["Declined"].sum()
        avg_cpa = total_cost / total_apps if total_apps > 0 else 0
        avg_ctr = df_filtered["CTR (%)"].mean() if len(df_filtered) > 0 else 0

        # Calculate conversion rates
        app_to_ipa_rate = (total_ipa_approved / total_apps * 100) if total_apps > 0 else 0
        ipa_to_card_rate = (total_card_out / total_ipa_approved * 100) if total_ipa_approved > 0 else 0

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
                f"{total_ipa_approved:,}",
                delta=f"{app_to_ipa_rate:.1f}% conversion",
                help="In-Principle Approved applications"
            )

        with metric_col4:
            st.metric(
                "Card Out (Disbursed)",
                f"{total_card_out:,}",
                delta=f"{ipa_to_card_rate:.1f}% from IPA",
                help="Successfully disbursed cards"
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Performance Analytics", "📊 Campaign Comparison", "📑 Data Table", "🔍 Matched MIS", "📥 Export"])

        # --- Tab 1: Performance Analytics ---
        with tab1:
            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                # Time Series Chart
                if pd.notna(df_filtered['Date']).any():
                    df_time = df_filtered.groupby('Date').agg({
                        'Applications': 'sum',
                        'Total cost (₹)': 'sum',
                        'IPA Approved': 'sum',
                        'Card Out': 'sum'
                    }).reset_index()

                    fig_time = go.Figure()
                    fig_time.add_trace(go.Scatter(
                        x=df_time['Date'], y=df_time['Applications'],
                        mode='lines+markers', name='Applications',
                        line=dict(color='#f59e0b', width=3),
                        marker=dict(size=8)
                    ))
                    fig_time.add_trace(go.Scatter(
                        x=df_time['Date'], y=df_time['IPA Approved'],
                        mode='lines+markers', name='IPA Approved',
                        line=dict(color='#d97706', width=3),
                        marker=dict(size=8)
                    ))
                    fig_time.add_trace(go.Scatter(
                        x=df_time['Date'], y=df_time['Card Out'],
                        mode='lines+markers', name='Card Out',
                        line=dict(color='#ea580c', width=3),
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

                # CTR Distribution
                fig_ctr = px.histogram(
                    df_filtered,
                    x="CTR (%)",
                    nbins=20,
                    title="📊 CTR Distribution Across Campaigns",
                    color_discrete_sequence=['#f59e0b']
                )
                fig_ctr.update_layout(
                    title=dict(text="📊 CTR Distribution Across Campaigns", font=dict(size=16, color='#e2e8f0')),
                    xaxis_title="Click-Through Rate (%)",
                    yaxis_title="Number of Campaigns",
                    height=400,
                    template='plotly_dark',
                    paper_bgcolor='rgba(30, 41, 59, 0.6)',
                    plot_bgcolor='rgba(30, 41, 59, 0.4)',
                    font=dict(color='#e2e8f0', size=12),
                    xaxis=dict(gridcolor='#475569', color='#e2e8f0'),
                    yaxis=dict(gridcolor='#475569', color='#e2e8f0')
                )
                st.plotly_chart(fig_ctr, use_container_width=True)

            with viz_col2:
                # Conversion Funnel
                fig_funnel = go.Figure(go.Funnel(
                    y=["Applications", "IPA Approved", "Card Out"],
                    x=[total_apps, total_ipa_approved, total_card_out],
                    textposition="inside",
                    textinfo="value+percent initial",
                    textfont=dict(size=14, color='white', family='Inter'),
                    marker={
                        "color": ["#f59e0b", "#d97706", "#ea580c"],
                        "line": {"width": [2, 2, 2], "color": ["#1e293b", "#1e293b", "#1e293b"]}
                    },
                    connector={"line": {"color": "#475569", "dash": "dot", "width": 3}}
                ))
                fig_funnel.update_layout(
                    title=dict(text="📊 Conversion Funnel", font=dict(size=16, color='#e2e8f0')),
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
                    color_discrete_sequence=['#f59e0b', '#d97706', '#ea580c', '#fb923c', '#fdba74']
                )
                fig_source.update_traces(textfont=dict(size=12, color='white'))
                fig_source.update_layout(
                    title=dict(text="💎 Source Performance Matrix", font=dict(size=16, color='#e2e8f0')),
                    height=400,
                    template='plotly_dark',
                    paper_bgcolor='rgba(30, 41, 59, 0.6)',
                    plot_bgcolor='rgba(30, 41, 59, 0.4)',
                    font=dict(color='#e2e8f0', size=12),
                    xaxis=dict(gridcolor='#475569', color='#e2e8f0'),
                    yaxis=dict(gridcolor='#475569', color='#e2e8f0'),
                    legend=dict(bgcolor='rgba(30, 41, 59, 0.8)', bordercolor='#475569', borderwidth=1)
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
                    color_continuous_scale='Oranges',
                    text='Applications'
                )
                fig_top.update_traces(
                    textposition='outside',
                    textfont=dict(size=13, color='#e2e8f0', family='Inter')
                )
                fig_top.update_layout(
                    title=dict(text="🏆 Top 10 Campaigns by Applications", font=dict(size=16, color='#e2e8f0')),
                    height=500,
                    showlegend=False,
                    template='plotly_dark',
                    paper_bgcolor='rgba(30, 41, 59, 0.6)',
                    plot_bgcolor='rgba(30, 41, 59, 0.4)',
                    font=dict(color='#e2e8f0', size=11),
                    xaxis=dict(gridcolor='#475569', color='#e2e8f0'),
                    yaxis=dict(gridcolor='#475569', color='#e2e8f0')
                )
                st.plotly_chart(fig_top, use_container_width=True)

            with col_full2:
                # Cost Efficiency
                fig_cost = px.bar(
                    df_filtered.nsmallest(10, 'Cost per Application (₹)'),
                    x='Cost per Application (₹)',
                    y='Campaign name',
                    orientation='h',
                    title="💰 Most Cost-Efficient Campaigns",
                    color='Cost per Application (₹)',
                    color_continuous_scale='Teal',
                    text='Cost per Application (₹)'
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
                    'IPA Approved': 'sum',
                    'Card Out': 'sum'
                }).reset_index()

                fig_channel = go.Figure()
                fig_channel.add_trace(go.Bar(
                    x=channel_perf['Channel'],
                    y=channel_perf['Applications'],
                    name='Applications',
                    marker_color='#f59e0b'
                ))
                fig_channel.add_trace(go.Bar(
                    x=channel_perf['Channel'],
                    y=channel_perf['IPA Approved'],
                    name='IPA Approved',
                    marker_color='#d97706'
                ))
                fig_channel.add_trace(go.Bar(
                    x=channel_perf['Channel'],
                    y=channel_perf['Card Out'],
                    name='Card Out',
                    marker_color='#ea580c'
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
                    color_discrete_sequence=['#f59e0b', '#d97706', '#ea580c', '#fb923c', '#fdba74']
                )
                fig_cost_dist.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Cost: ₹%{value:,.2f}<br>Share: %{percent}'
                )
                fig_cost_dist.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(30, 41, 59, 0.6)',
                    font=dict(color='#e2e8f0')
                )
                st.plotly_chart(fig_cost_dist, use_container_width=True)

            # Channel Cost Analysis
            st.markdown("#### 💰 Channel Cost Breakdown")
            channel_cost_analysis = df_filtered.groupby('Channel').agg({
                'Applications': 'sum',
                'Total cost (₹)': 'sum',
                'Cost per Application (₹)': 'mean',
                'Delivered': 'sum'
            }).reset_index()
            channel_cost_analysis['Avg Cost per Unit'] = channel_cost_analysis['Total cost (₹)'] / channel_cost_analysis['Delivered']

            st.dataframe(
                channel_cost_analysis.style.format({
                    'Total cost (₹)': '₹{:.2f}',
                    'Cost per Application (₹)': '₹{:.2f}',
                    'Avg Cost per Unit': '₹{:.3f}',
                    'Delivered': '{:.0f}',
                    'Applications': '{:.0f}'
                }).background_gradient(
                    subset=['Applications'],
                    cmap='YlOrBr'
                ).background_gradient(
                    subset=['Total cost (₹)'],
                    cmap='Oranges'
                ),
                use_container_width=True
            )

            # Detailed Comparison Table
            st.markdown("#### 📋 Detailed Comparison Metrics")
            comparison_metrics = df_filtered.groupby('Source').agg({
                'Applications': 'sum',
                'IPA Approved': 'sum',
                'Card Out': 'sum',
                'Total cost (₹)': 'sum',
                'Cost per Application (₹)': 'mean',
                'CTR (%)': 'mean'
            }).round(2).reset_index()

            comparison_metrics.columns = ['Source', 'Applications', 'IPA Approved',
                                        'Card Out', 'Total Cost (₹)',
                                        'Avg CPA (₹)', 'Avg CTR (%)']

            st.dataframe(
                comparison_metrics.style.background_gradient(
                    subset=['Applications', 'Card Out'],
                    cmap='YlOrBr'
                ).background_gradient(
                    subset=['Total Cost (₹)', 'Avg CPA (₹)'],
                    cmap='Oranges'
                ),
                use_container_width=True,
                height=400
            )

        # --- Tab 3: Data Table ---
        with tab3:
            st.markdown("### 📑 Detailed Campaign Data")

            # Add search functionality
            search_term = st.text_input("🔍 Search campaigns", placeholder="Enter campaign name...")

            display_df = df_filtered.copy()
            if search_term:
                display_df = display_df[
                    display_df['Campaign name'].str.contains(search_term, case=False, na=False)
                ]

            # Format and display
            st.dataframe(
                display_df.style.format({
                    "Date": lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '',
                    "Total cost (₹)": "₹{:.2f}",
                    "Cost per Application (₹)": "₹{:.2f}",
                    "Cost per IPA (₹)": "₹{:.2f}",
                    "Cost per Card Out (₹)": "₹{:.2f}",
                    "Cost per unit (₹)": "₹{:.3f}",
                    "CTR (%)": "{:.2f}%",
                    "Read Rate (%)": "{:.2f}%",
                    "CPC (₹)": "₹{:.2f}",
                }).background_gradient(
                    subset=["Applications", "Total cost (₹)"],
                    cmap="Oranges"
                ),
                use_container_width=True,
                height=600
            )

            # Summary Statistics
            st.markdown("#### 📊 Summary Statistics")
            summary_stats_col1, summary_stats_col2, summary_stats_col3, summary_stats_col4 = st.columns(4)

            with summary_stats_col1:
                st.info(f"**Total Campaigns:** {len(display_df)}")
            with summary_stats_col2:
                st.info(f"**Avg Applications:** {display_df['Applications'].mean():.0f}")
            with summary_stats_col3:
                st.info(f"**Avg Cost:** ₹{display_df['Total cost (₹)'].mean():.2f}")
            with summary_stats_col4:
                st.info(f"**Avg CTR:** {display_df['CTR (%)'].mean():.2f}%")

        # --- Tab 4: Matched MIS ---
        with tab4:
            st.markdown("### 🔍 Matched MIS Records")
            st.write("This tab shows the detailed MIS records that matched each campaign identifier via UTM_CAMPAIGN.")

            if not df_matched_mis_all.empty:
                # Filter matched records based on current filters
                filtered_identifiers = df_filtered['Campaign name'].unique()
                df_matched_display = df_matched_mis_all[
                    df_matched_mis_all['Matched_Identifier'].isin(filtered_identifiers)
                ]

                # Summary metrics
                mis_col1, mis_col2, mis_col3, mis_col4 = st.columns(4)

                with mis_col1:
                    st.metric("Total Matched Records", f"{len(df_matched_display):,}")
                with mis_col2:
                    unique_campaigns = df_matched_display['Matched_Identifier'].nunique()
                    st.metric("Campaigns Matched", f"{unique_campaigns}")
                with mis_col3:
                    if status_col and status_col in df_matched_display.columns:
                        disbursed_count = df_matched_display[status_col].astype(str).str.upper().isin([s.upper() for s in CARD_OUT_STATUS]).sum()
                        st.metric("Disbursed", f"{disbursed_count:,}")
                with mis_col4:
                    if status_col and status_col in df_matched_display.columns:
                        declined_count = df_matched_display[status_col].astype(str).str.upper().isin([s.upper() for s in DECLINED_STATUS]).sum()
                        st.metric("Declined", f"{declined_count:,}")

                st.markdown("---")

                # Campaign filter for matched MIS
                mis_campaign_filter = st.selectbox(
                    "Filter by Campaign Identifier",
                    ["All Campaigns"] + sorted(df_matched_display['Matched_Identifier'].unique().tolist()),
                    key="mis_campaign_filter"
                )

                if mis_campaign_filter != "All Campaigns":
                    df_matched_display = df_matched_display[
                        df_matched_display['Matched_Identifier'] == mis_campaign_filter
                    ]

                # Fix duplicate column names in matched display before showing
                cols_display = pd.Series(df_matched_display.columns)
                for dup in cols_display[cols_display.duplicated()].unique():
                    cols_display[cols_display[cols_display == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols_display == dup))]
                df_matched_display.columns = cols_display

                # Display matched MIS data
                st.dataframe(
                    df_matched_display,
                    use_container_width=True,
                    height=600
                )

                # Download matched MIS as CSV
                st.markdown("---")
                csv_matched = df_matched_display.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Matched MIS (CSV)",
                    data=csv_matched,
                    file_name=f"AU_Bank_Matched_MIS_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("📭 No MIS records matched the campaign identifiers.")

        # --- Tab 5: Export ---
        with tab5:
            st.markdown("### 📥 Export Your Reports")

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                st.markdown("#### 📊 Excel Report")
                st.write("Download complete analysis with all metrics and filtered data.")

                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # Summary Sheet
                    df_filtered.to_excel(writer, sheet_name="Campaign Summary", index=False)

                    # Metrics Sheet
                    metrics_df = pd.DataFrame({
                        'Metric': ['Total Applications', 'Total Cost', 'IPA Approved',
                                  'Card Out', 'Avg CPA', 'Avg CTR'],
                        'Value': [total_apps, f"₹{total_cost:.2f}", total_ipa_approved,
                                 total_card_out, f"₹{avg_cpa:.2f}", f"{avg_ctr:.2f}%"]
                    })
                    metrics_df.to_excel(writer, sheet_name="Key Metrics", index=False)

                    # Source Performance
                    source_perf_export = df_filtered.groupby('Source').agg({
                        'Applications': 'sum',
                        'Total cost (₹)': 'sum',
                        'IPA Approved': 'sum',
                        'Card Out': 'sum'
                    }).reset_index()
                    source_perf_export.to_excel(writer, sheet_name="Source Performance", index=False)

                    # Channel Performance
                    channel_perf_export = df_filtered.groupby('Channel').agg({
                        'Applications': 'sum',
                        'Total cost (₹)': 'sum',
                        'IPA Approved': 'sum',
                        'Card Out': 'sum',
                        'Cost per Application (₹)': 'mean'
                    }).reset_index()
                    channel_perf_export.to_excel(writer, sheet_name="Channel Performance", index=False)

                    # Matched MIS Records Sheet
                    if not df_matched_mis_all.empty:
                        filtered_identifiers = df_filtered['Campaign name'].unique()
                        df_matched_filtered = df_matched_mis_all[
                            df_matched_mis_all['Matched_Identifier'].isin(filtered_identifiers)
                        ]
                        df_matched_filtered.to_excel(writer, sheet_name="Matched MIS", index=False)

                output.seek(0)
                st.download_button(
                    label="⬇️ Download Excel Report",
                    data=output,
                    file_name=f"AU_Bank_Campaign_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            with export_col2:
                st.markdown("#### 📄 CSV Export")
                st.write("Download filtered data in CSV format for further analysis.")

                csv_data = df_filtered.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"AU_Bank_Campaign_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

            st.markdown("---")
            st.info("💡 **Tip:** Export reports regularly to track performance trends over time!")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        with st.expander("🔍 View error details"):
            st.exception(e)

else:
    # Welcome Screen
    st.markdown("---")
    col_welcome1, col_welcome2, col_welcome3 = st.columns([1, 2, 1])

    with col_welcome2:
        st.markdown("""
            <div style='text-align: center; padding: 3rem;'>
                <h2 style='color: #e2e8f0;'>👋 Welcome to AU Bank Campaign Analytics</h2>
                <p style='font-size: 1.1rem; color: #94a3b8; margin-top: 1rem;'>
                    Upload your MIS Excel file to unlock powerful insights and analytics.
                </p>
                <div style='margin-top: 2rem; padding: 2rem;
                     background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
                     border-radius: 15px; color: white; box-shadow: 0 10px 40px rgba(245, 158, 11, 0.3);'>
                    <h3>✨ Features</h3>
                    <ul style='list-style: none; padding: 0; text-align: left;'>
                        <li style='padding: 0.5rem 0;'>📅 Date range filtering</li>
                        <li style='padding: 0.5rem 0;'>🎯 Multi-dimensional analysis</li>
                        <li style='padding: 0.5rem 0;'>📊 Interactive visualizations</li>
                        <li style='padding: 0.5rem 0;'>💡 Real-time insights</li>
                        <li style='padding: 0.5rem 0;'>📥 Comprehensive exports</li>
                        <li style='padding: 0.5rem 0;'>💰 Channel-specific costing</li>
                        <li style='padding: 0.5rem 0;'>🔍 UTM_CAMPAIGN matching</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #94a3b8; padding: 1rem;'>
        <p>Built with ❤️ for AU Bank | © 2025 Campaign Analytics Dashboard</p>
    </div>
""", unsafe_allow_html=True)
