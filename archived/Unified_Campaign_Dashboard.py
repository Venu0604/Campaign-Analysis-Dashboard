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
    "Email": 0.05,
}

# -------------------------
# Bank Configurations
# -------------------------
BANK_CONFIGS = {
    "Axis Bank": {
        "sheet_gid": "526829508",
        "identifier_column": "CROSSCELLCODE",
        "status_column": "FINAL STATUS",
        "ipa_column": "IPA STATUS",
        "card_out_status": ["APPROVED"],
        "declined_status": ["DECLINED"],
        "ipa_approved_status": ["APPROVED", "IPA APPROVED", "UNDERWRITER APPROVED", "RCU", "UW"],
        "color_scheme": {
            "primary": "#7c3aed",
            "secondary": "#6366f1",
            "tertiary": "#8b5cf6"
        },
        "gradient": "135deg, #7c3aed 0%, #6366f1 50%, #8b5cf6 100%"
    },
    "AU Bank": {
        "sheet_gid": "1138241151",
        "identifier_column": "UTM_CAMPAIGN",
        "status_column": "CURRENT_STATUS",
        "ipa_column": "BRE_OUTPUT",
        "card_out_status": ["DISBURSED"],
        "declined_status": [
            "REJECTED CASE", "BRE DECLINE CASE", "CREDIT REJECT CASE",
            "REJECT FOR CURING", "Gating Criteria Not Met (CIBIL)",
            "PAN AADHAAR CHECK REJECT", "DVU REJECT CASE", "LOGICAL DELETED", "BUREAU DECLINE CASE"
        ],
        "ipa_approved_status": ["APPROVED"],
        "color_scheme": {
            "primary": "#f59e0b",
            "secondary": "#d97706",
            "tertiary": "#ea580c"
        },
        "gradient": "135deg, #f59e0b 0%, #ea580c 100%"
    },
    "RBL Bank": {
        "sheet_gid": "1119698657",
        "identifier_column": "CAMPAIGN SOURCE",
        "status_column": "DISPOSITION",
        "ipa_column": "DISPOSITION",
        "ops_status_column": "OPS STATUS",
        "card_out_status": ["CARD SETUP"],
        "declined_status": ["AIP DECLINE"],
        "ipa_approved_status": ["RECEIVED FOR VKYC", "TOUCH FREE KYC PENDING"],
        "color_scheme": {
            "primary": "#06b6d4",
            "secondary": "#3b82f6",
            "tertiary": "#8b5cf6"
        },
        "gradient": "135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%"
    },
    "HDFC Bank": {
        "sheet_gid": "2141873222",
        "identifier_column": "LC_CODE",
        "status_column": "FINAL_DECISION",
        "ipa_column": "IPA_STATUS",
        "card_out_status": ["APPROVE"],
        "declined_status": ["DECLINE", "IPA REJECT"],
        "ipa_approved_status": ["APPROVE"],
        "color_scheme": {
            "primary": "#dc2626",
            "secondary": "#991b1b",
            "tertiary": "#b91c1c"
        },
        "gradient": "135deg, #dc2626 0%, #991b1b 100%"
    },
    "IDFC Bank": {
        "sheet_gid": "0",
        "identifier_column": "CROSSCELLCODE",
        "status_column": "FINAL STATUS",
        "ipa_column": "IPA STATUS",
        "card_out_status": ["APPROVED"],
        "declined_status": ["DECLINED"],
        "ipa_approved_status": ["APPROVED"],
        "color_scheme": {
            "primary": "#059669",
            "secondary": "#047857",
            "tertiary": "#065f46"
        },
        "gradient": "135deg, #059669 0%, #047857 100%"
    },
    "Scapia": {
        "sheet_gid": "0",
        "identifier_column": "CROSSCELLCODE",
        "status_column": "FINAL STATUS",
        "ipa_column": "IPA STATUS",
        "card_out_status": ["APPROVED"],
        "declined_status": ["DECLINED"],
        "ipa_approved_status": ["APPROVED"],
        "color_scheme": {
            "primary": "#7c3aed",
            "secondary": "#6d28d9",
            "tertiary": "#5b21b6"
        },
        "gradient": "135deg, #7c3aed 0%, #6d28d9 100%"
    }
}

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="Unified Campaign Dashboard", layout="wide", page_icon="🎯")

# -------------------------
# Dynamic CSS Based on Selected Bank
# -------------------------
def get_custom_css(bank_config):
    colors = bank_config["color_scheme"]
    gradient = bank_config["gradient"]

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    .main {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: #e2e8f0;
    }}

    .main-header {{
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient({gradient});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-in-out;
        text-shadow: 0 0 40px rgba({colors['primary']}, 0.2);
    }}

    .sub-header {{
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }}

    [data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {colors['primary']} !important;
        font-weight: 700;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient({gradient});
        color: white !important;
        border: none;
    }}

    .stDownloadButton button {{
        background: linear-gradient({gradient});
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}

    .stDownloadButton button:hover {{
        transform: scale(1.05);
    }}

    @keyframes fadeInDown {{
        from {{
            opacity: 0;
            transform: translateY(-20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    </style>
    """

# -------------------------
# Helper Functions
# -------------------------
def find_column(df, keywords):
    """Find column that contains any of the keywords (case insensitive)"""
    if isinstance(keywords, str):
        keywords = [keywords]
    for col in df.columns:
        col_clean = str(col).strip().replace('*', '').lower()
        for keyword in keywords:
            if keyword.lower() in col_clean:
                return col
    return None

def get_channel_cost(channel, costs_dict):
    """Get cost for a channel (case-insensitive matching)"""
    channel_lower = str(channel).lower()

    if "sms" in channel_lower:
        return costs_dict.get("SMS", 0.10)
    elif "rcs" in channel_lower:
        return costs_dict.get("RCS", 0.085)
    elif "whatsapp" in channel_lower:
        if "utility" in channel_lower:
            return costs_dict.get("Whatsapp Utility", 0.115)
        else:
            return costs_dict.get("Whatsapp Marketing", 0.80)
    elif "email" in channel_lower:
        return costs_dict.get("Email", 0.05)

    return costs_dict.get("SMS", 0.10)

def process_campaign_data(df_identifiers, df_mis, bank_config):
    """Process campaign data for the selected bank"""
    output_rows = []
    matched_mis_records = []

    # Find identifier column in MIS
    identifier_col = find_column(df_mis, bank_config["identifier_column"])
    status_col = find_column(df_mis, bank_config["status_column"])
    ipa_col = find_column(df_mis, bank_config.get("ipa_column", ""))

    # Special handling for RBL (has OPS status column)
    ops_status_col = None
    if "ops_status_column" in bank_config:
        ops_status_col = find_column(df_mis, bank_config["ops_status_column"])

    if not identifier_col:
        st.error(f"❌ {bank_config['identifier_column']} column not found in MIS file")
        return None, None

    for _, row in df_identifiers.iterrows():
        date = row.get("Date", "")
        identifier = str(row.get("Identifiers", "")).strip()
        source = str(row.get("Source", "")).strip()
        channel = str(row.get("Channel", "")).strip()
        delivered = float(row.get("Delivered", 0))
        clicks = float(row.get("Clicks", 0))
        read_count = float(row.get("Read", 0))

        # Get channel-specific cost
        cost_per_unit = get_channel_cost(channel, CAMPAIGN_COSTS)

        # Filter MIS data
        mask = df_mis[identifier_col].astype(str).str.contains(identifier, case=False, na=False)
        df_filtered_mis = df_mis[mask]

        # Add to matched records
        if len(df_filtered_mis) > 0:
            df_matched_copy = df_filtered_mis.copy()
            df_matched_copy['Matched_Identifier'] = identifier
            df_matched_copy['Campaign_Date'] = date
            df_matched_copy['Campaign_Source'] = source
            df_matched_copy['Campaign_Channel'] = channel
            matched_mis_records.append(df_matched_copy)

        applications = len(df_filtered_mis)

        # Status analysis
        card_out = 0
        declined = 0
        ipa_approved = 0

        if status_col:
            status_values = df_filtered_mis[status_col].astype(str).str.strip().str.upper()

            # Card Out
            if ops_status_col:  # RBL special case
                ops_values = df_filtered_mis[ops_status_col].astype(str).str.strip().str.upper()
                card_out = ops_values.isin([s.upper() for s in bank_config["card_out_status"]]).sum()
            else:
                card_out = status_values.isin([s.upper() for s in bank_config["card_out_status"]]).sum()

            # Declined
            declined = status_values.isin([s.upper() for s in bank_config["declined_status"]]).sum()

        # IPA Approved
        if ipa_col:
            ipa_values = df_filtered_mis[ipa_col].astype(str).str.strip().str.upper()
            ipa_approved = ipa_values.isin([s.upper() for s in bank_config["ipa_approved_status"]]).sum()
        else:
            ipa_approved = card_out

        # In Progress
        in_progress = applications - card_out - declined

        # Calculate metrics
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
    df_summary['Date'] = pd.to_datetime(df_summary['Date'], errors='coerce')

    # Combine matched MIS records
    if matched_mis_records:
        df_matched_mis_all = pd.concat(matched_mis_records, ignore_index=True)
    else:
        df_matched_mis_all = pd.DataFrame()

    return df_summary, df_matched_mis_all

# -------------------------
# Main App
# -------------------------

# Sidebar - Bank Selection
with st.sidebar:
    st.markdown("### 🏦 Select Bank")
    selected_bank = st.selectbox(
        "Choose Bank",
        list(BANK_CONFIGS.keys()),
        index=0
    )

    st.markdown("---")
    st.markdown("### 💰 Campaign Economics")
    for channel, cost in CAMPAIGN_COSTS.items():
        st.metric(channel, f"₹{cost:.3f}/unit")

# Get selected bank configuration
bank_config = BANK_CONFIGS[selected_bank]

# Apply dynamic CSS
st.markdown(get_custom_css(bank_config), unsafe_allow_html=True)

# Header
st.markdown(f'<div class="main-header">🎯 {selected_bank} Campaign Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Unified Multi-Bank Performance Dashboard</div>', unsafe_allow_html=True)

# Load Identifiers from Google Sheet
sheet_url = f"https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid={bank_config['sheet_gid']}"

try:
    df_identifiers = pd.read_csv(sheet_url)
    df_identifiers.columns = df_identifiers.columns.str.strip()
    df_identifiers['Date'] = pd.to_datetime(df_identifiers['Date'],format='%d-%m-%Y', errors='coerce')
    st.sidebar.success(f"✅ Loaded {len(df_identifiers)} campaigns")
except Exception as e:
    st.sidebar.error(f"❌ Error loading identifiers: {e}")
    df_identifiers = None

# File Upload
st.markdown("### 📁 Data Upload")
mis_file = st.file_uploader("Upload MIS File (Excel)", type=["xlsx", "xls", "xlsb"], help="Upload your MIS Excel file to begin analysis")

# Main Analysis
if mis_file and df_identifiers is not None:
    try:
        # Read MIS file
        file_extension = mis_file.name.split('.')[-1].lower()
        engine = 'xlrd' if file_extension == 'xls' else ('pyxlsb' if file_extension == 'xlsb' else 'openpyxl')

        df_mis = pd.read_excel(mis_file, sheet_name=0, engine=engine)
        df_mis.columns = df_mis.columns.str.strip()

        # Normalize column names
        df_mis.columns = df_mis.columns.str.lower().str.strip()

        # Process data
        df_summary, df_matched_mis_all = process_campaign_data(df_identifiers, df_mis, bank_config)

        if df_summary is None:
            st.stop()

        st.success(f"✅ Successfully processed {len(df_summary)} campaign records | {len(df_matched_mis_all)} MIS records matched")

        # Interactive Filters
        st.markdown("---")
        st.markdown("### 🔍 Interactive Filters")

        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

        with filter_col1:
            min_date = df_summary['Date'].min()
            max_date = df_summary['Date'].max()

            if pd.notna(min_date) and pd.notna(max_date):
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

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
            sources = ["All Sources"] + sorted(df_summary['Source'].unique().tolist())
            selected_source = st.selectbox("🎯 Source", sources)
            if selected_source != "All Sources":
                df_filtered = df_filtered[df_filtered['Source'] == selected_source]

        with filter_col3:
            channels = ["All Channels"] + sorted(df_summary['Channel'].unique().tolist())
            selected_channel = st.selectbox("📢 Channel", channels)
            if selected_channel != "All Channels":
                df_filtered = df_filtered[df_filtered['Channel'] == selected_channel]

        with filter_col4:
            campaigns = ["All Campaigns"] + sorted(df_summary['Campaign name'].unique().tolist())
            selected_campaign = st.selectbox("🎪 Campaign", campaigns)
            if selected_campaign != "All Campaigns":
                df_filtered = df_filtered[df_filtered['Campaign name'] == selected_campaign]

        # Key Metrics
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

        app_to_ipa_rate = (total_ipa_approved / total_apps * 100) if total_apps > 0 else 0
        ipa_to_card_rate = (total_card_out / total_ipa_approved * 100) if total_ipa_approved > 0 else 0

        with metric_col1:
            st.metric("Total Applications", f"{total_apps:,}", delta=f"{len(df_filtered)} campaigns")

        with metric_col2:
            st.metric("Total Investment", f"₹{total_cost:,.2f}", delta=f"Avg ₹{avg_cpa:.2f}/app")

        with metric_col3:
            st.metric("IPA Approved", f"{total_ipa_approved:,}", delta=f"{app_to_ipa_rate:.1f}% conversion")

        with metric_col4:
            st.metric("Card Out", f"{total_card_out:,}", delta=f"{ipa_to_card_rate:.1f}% from IPA")

        with metric_col5:
            st.metric("Avg CTR", f"{avg_ctr:.2f}%", delta=f"{total_declined:,} declined")

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Performance Analytics", "📊 Campaign Comparison", "📑 Data Table", "🔍 Matched MIS", "📥 Export"])

        with tab1:
            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                # Time Series
                if pd.notna(df_filtered['Date']).any():
                    df_time = df_filtered.groupby('Date').agg({
                        'Applications': 'sum',
                        'IPA Approved': 'sum',
                        'Card Out': 'sum'
                    }).reset_index()

                    fig_time = go.Figure()
                    colors_scheme = bank_config["color_scheme"]

                    fig_time.add_trace(go.Scatter(
                        x=df_time['Date'], y=df_time['Applications'],
                        mode='lines+markers', name='Applications',
                        line=dict(color=colors_scheme["primary"], width=3),
                        marker=dict(size=8)
                    ))
                    fig_time.add_trace(go.Scatter(
                        x=df_time['Date'], y=df_time['IPA Approved'],
                        mode='lines+markers', name='IPA Approved',
                        line=dict(color=colors_scheme["secondary"], width=3),
                        marker=dict(size=8)
                    ))
                    fig_time.add_trace(go.Scatter(
                        x=df_time['Date'], y=df_time['Card Out'],
                        mode='lines+markers', name='Card Out',
                        line=dict(color=colors_scheme["tertiary"], width=3),
                        marker=dict(size=8)
                    ))

                    fig_time.update_layout(
                        title="📈 Performance Trends Over Time",
                        xaxis_title="Date",
                        yaxis_title="Count",
                        hovermode='x unified',
                        height=400,
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig_time, use_container_width=True)

                # CTR Distribution
                fig_ctr = px.histogram(
                    df_filtered, x="CTR (%)", nbins=20,
                    title="📊 CTR Distribution",
                    color_discrete_sequence=[bank_config["color_scheme"]["primary"]]
                )
                fig_ctr.update_layout(height=400, template='plotly_dark')
                st.plotly_chart(fig_ctr, use_container_width=True)

            with viz_col2:
                # Conversion Funnel
                fig_funnel = go.Figure(go.Funnel(
                    y=["Applications", "IPA Approved", "Card Out"],
                    x=[total_apps, total_ipa_approved, total_card_out],
                    textposition="inside",
                    textinfo="value+percent initial",
                    marker={
                        "color": [
                            bank_config["color_scheme"]["primary"],
                            bank_config["color_scheme"]["secondary"],
                            bank_config["color_scheme"]["tertiary"]
                        ]
                    }
                ))
                fig_funnel.update_layout(title="📊 Conversion Funnel", height=400, template='plotly_dark')
                st.plotly_chart(fig_funnel, use_container_width=True)

                # Source Performance
                source_perf = df_filtered.groupby('Source').agg({
                    'Applications': 'sum',
                    'Total cost (₹)': 'sum'
                }).reset_index()
                source_perf['Cost per App'] = source_perf['Total cost (₹)'] / source_perf['Applications']

                fig_source = px.scatter(
                    source_perf, x='Applications', y='Cost per App',
                    size='Total cost (₹)', color='Source',
                    title="💎 Source Performance Matrix"
                )
                fig_source.update_layout(height=400, template='plotly_dark')
                st.plotly_chart(fig_source, use_container_width=True)

        with tab2:
            st.markdown("### 🔄 Campaign Comparison")

            comparison_col1, comparison_col2 = st.columns(2)

            with comparison_col1:
                # Channel Performance
                channel_perf = df_filtered.groupby('Channel').agg({
                    'Applications': 'sum',
                    'IPA Approved': 'sum',
                    'Card Out': 'sum'
                }).reset_index()

                fig_channel = go.Figure()
                colors_scheme = bank_config["color_scheme"]

                fig_channel.add_trace(go.Bar(
                    x=channel_perf['Channel'], y=channel_perf['Applications'],
                    name='Applications', marker_color=colors_scheme["primary"]
                ))
                fig_channel.add_trace(go.Bar(
                    x=channel_perf['Channel'], y=channel_perf['IPA Approved'],
                    name='IPA Approved', marker_color=colors_scheme["secondary"]
                ))
                fig_channel.add_trace(go.Bar(
                    x=channel_perf['Channel'], y=channel_perf['Card Out'],
                    name='Card Out', marker_color=colors_scheme["tertiary"]
                ))

                fig_channel.update_layout(
                    title="📢 Performance by Channel",
                    barmode='group', height=400, template='plotly_dark'
                )
                st.plotly_chart(fig_channel, use_container_width=True)

            with comparison_col2:
                # Cost Distribution
                fig_cost_dist = px.pie(
                    df_filtered, values='Total cost (₹)', names='Source',
                    title="💸 Cost Distribution by Source", hole=0.4
                )
                fig_cost_dist.update_layout(template='plotly_dark')
                st.plotly_chart(fig_cost_dist, use_container_width=True)

        with tab3:
            st.markdown("### 📑 Detailed Campaign Data")

            search_term = st.text_input("🔍 Search campaigns", placeholder="Enter campaign name...")

            display_df = df_filtered.copy()
            if search_term:
                display_df = display_df[
                    display_df['Campaign name'].str.contains(search_term, case=False, na=False)
                ]

            st.dataframe(
                display_df.style.format({
                    "Date": lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '',
                    "Total cost (₹)": "₹{:.2f}",
                    "Cost per Application (₹)": "₹{:.2f}",
                    "Cost per IPA (₹)": "₹{:.2f}",
                    "Cost per Card Out (₹)": "₹{:.2f}",
                    "CTR (%)": "{:.2f}%",
                }),
                use_container_width=True,
                height=600
            )

        with tab4:
            st.markdown("### 🔍 Matched MIS Records")

            if not df_matched_mis_all.empty:
                filtered_identifiers = df_filtered['Campaign name'].unique()
                df_matched_display = df_matched_mis_all[
                    df_matched_mis_all['Matched_Identifier'].isin(filtered_identifiers)
                ]

                st.metric("Total Matched Records", f"{len(df_matched_display):,}")

                st.dataframe(df_matched_display, use_container_width=True, height=600)

                csv_matched = df_matched_display.to_csv(index=False)
                st.download_button(
                    "⬇️ Download Matched MIS (CSV)",
                    data=csv_matched,
                    file_name=f"{selected_bank.replace(' ', '_')}_Matched_MIS_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("📭 No MIS records matched")

        with tab5:
            st.markdown("### 📥 Export Your Reports")

            export_col1, export_col2 = st.columns(2)

            with export_col1:
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df_filtered.to_excel(writer, sheet_name="Campaign Summary", index=False)

                    if not df_matched_mis_all.empty:
                        df_matched_mis_all.to_excel(writer, sheet_name="Matched MIS", index=False)

                output.seek(0)
                st.download_button(
                    "⬇️ Download Excel Report",
                    data=output,
                    file_name=f"{selected_bank.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with export_col2:
                csv_data = df_filtered.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"{selected_bank.replace(' ', '_')}_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
        with st.expander("🔍 View error details"):
            st.exception(e)

else:
    # Welcome Screen
    st.markdown("---")
    col_welcome1, col_welcome2, col_welcome3 = st.columns([1, 2, 1])

    with col_welcome2:
        st.markdown(f"""
            <div style='text-align: center; padding: 3rem;'>
                <h2 style='color: #e2e8f0;'>👋 Welcome to {selected_bank} Campaign Analytics</h2>
                <p style='font-size: 1.1rem; color: #94a3b8; margin-top: 1rem;'>
                    Upload your MIS Excel file to unlock powerful insights and analytics.
                </p>
                <div style='margin-top: 2rem; padding: 2rem;
                     background: linear-gradient({bank_config["gradient"]});
                     border-radius: 15px; color: white;'>
                    <h3>✨ Features</h3>
                    <ul style='list-style: none; padding: 0; text-align: left;'>
                        <li style='padding: 0.5rem 0;'>🏦 Multi-Bank Support</li>
                        <li style='padding: 0.5rem 0;'>📅 Date range filtering</li>
                        <li style='padding: 0.5rem 0;'>📊 Interactive visualizations</li>
                        <li style='padding: 0.5rem 0;'>💰 Channel-specific costing</li>
                        <li style='padding: 0.5rem 0;'>📥 Comprehensive exports</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #94a3b8; padding: 1rem;'>
        <p>Unified Campaign Analytics Dashboard | © 2025</p>
    </div>
""", unsafe_allow_html=True)
