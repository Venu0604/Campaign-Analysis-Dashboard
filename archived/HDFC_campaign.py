"""
HDFC Campaign Analysis Module
Analyze campaign performance across multiple channels
"""

import pandas as pd
import streamlit as st
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


# Campaign costs configuration
CAMPAIGN_COSTS = {
    "SMS": 0.1,
    "RCS": 0.085,
    "Whatsapp Marketing": 0.8,
    "Whatsapp Utility": 0.115,
}

# Final status mapping
FINAL_STATUS_MAP = {
    "IPA APPROVED DROPOFF CASE": "Inprogress",
    "IPA REJECT": "Declined",
    "Decline": "Declined",
    "Approve": "Card Out",
    "Inprocess": "Inprogress",
}


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


def parse_dates_safely(date_series):
    """Parse dates with multiple format handling"""
    parsed_dates = []
    for date_val in date_series:
        if pd.isna(date_val):
            parsed_dates.append(pd.NaT)
            continue
        try:
            parsed = pd.to_datetime(date_val, dayfirst=True, format='mixed')
            parsed_dates.append(parsed)
        except:
            try:
                parsed = pd.to_datetime(date_val, dayfirst=True)
                parsed_dates.append(parsed)
            except:
                parsed_dates.append(pd.NaT)
    return pd.Series(parsed_dates)


def find_date_column(df):
    """Find a date column in the dataframe"""
    date_keywords = ['date', 'created', 'timestamp', 'time', 'dt']
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in date_keywords):
            try:
                test_val = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
                if test_val:
                    pd.to_datetime(test_val, dayfirst=True)
                    return col
            except:
                continue
    return None


def analyze_campaigns(df_identifiers, df_mis, start_date=None, end_date=None, date_col=None):
    """Main analysis function for campaign data"""
    df_identifiers = df_identifiers.copy()
    df_mis = df_mis.copy()
    
    df_identifiers.columns = df_identifiers.columns.str.strip()
    df_mis.columns = df_mis.columns.str.strip().str.lower()

    # Apply date filter
    if date_col and start_date and end_date:
        try:
            if not pd.api.types.is_datetime64_any_dtype(df_identifiers[date_col]):
                df_identifiers[date_col] = parse_dates_safely(df_identifiers[date_col])
            df_identifiers = df_identifiers[df_identifiers[date_col].notna()]
            df_identifiers = df_identifiers[
                (df_identifiers[date_col] >= start_date) & 
                (df_identifiers[date_col] <= end_date)
            ]
        except Exception as e:
            st.warning(f"Date filtering warning: {e}")

    lc_col = find_column(df_identifiers, ['lc code', 'lc_code'])
    lg_col = find_column(df_identifiers, ['lg code', 'lg_code'])
    
    if lc_col:
        df_identifiers[lc_col] = df_identifiers[lc_col].astype(str)
    if lg_col:
        df_identifiers[lg_col] = df_identifiers[lg_col].astype(str)

    output_rows = []

    # Process each campaign
    for _, ident_row in df_identifiers.iterrows():
        channel_col = find_column(df_identifiers, 'channel')
        channel = str(ident_row.get(channel_col, "")).strip() if channel_col else ""
        lc_code = str(ident_row.get(lc_col, "")) if lc_col else ""
        lg_code = str(ident_row.get(lg_col, "")) if lg_col else ""

        # Filter MIS data
        lc_series = df_mis.get("lc1_code", pd.Series([""] * len(df_mis))).astype(str)
        lg_series = df_mis.get("lg_code", pd.Series([""] * len(df_mis))).astype(str)
        mis_filtered = df_mis[
            lc_series.str.contains(lc_code, case=False, na=False) & 
            (lg_series == lg_code)
        ]

        # Build row data
        row = {"Channel": channel, "LC Code": lc_code, "LG Code": lg_code}
        for col in df_identifiers.columns:
            if col not in [lc_col, lg_col, channel_col]:
                row[col] = ident_row[col]

        # Calculate metrics
        row["Applications"] = len(mis_filtered)
        row["IPA Approved"] = int(
            (mis_filtered.get("ipa_status", pd.Series([])).astype(str).str.upper() == "APPROVE").sum()
        )

        if "final_decision" in mis_filtered.columns:
            mis_final = mis_filtered["final_decision"].astype(str).map(FINAL_STATUS_MAP).fillna("Other")
            row["Declined"] = int((mis_final == "Declined").sum())
            row["Inprogress"] = int((mis_final == "Inprogress").sum())
            row["Card Out"] = int((mis_final == "Card Out").sum())
        else:
            row.update({"Declined": 0, "Inprogress": 0, "Card Out": 0})

        # Get delivery metrics
        delivered_col = find_column(df_identifiers, 'delivered')
        read_col = find_column(df_identifiers, 'read')
        clicks_col = find_column(df_identifiers, 'clicks')
        
        delivered = pd.to_numeric(ident_row.get(delivered_col, 0), errors='coerce') if delivered_col else 0
        read_count = pd.to_numeric(ident_row.get(read_col, 0), errors='coerce') if read_col else 0
        clicks = pd.to_numeric(ident_row.get(clicks_col, 0), errors='coerce') if clicks_col else 0

        delivered, read_count, clicks = map(lambda x: 0 if pd.isna(x) else x, [delivered, read_count, clicks])
        row.update({"Delivered": float(delivered), "Read": float(read_count), "Clicks": float(clicks)})

        # Calculate cost and rates
        if channel.lower() == "ivr orbital":
            dialed_col = find_column(df_identifiers, ['dailed', 'dialed'])
            connected_col = find_column(df_identifiers, 'connected')
            dtmf_col = find_column(df_identifiers, 'dtmf')
            sms_trig_col = find_column(df_identifiers, ['sms triggered', 'sms_triggered'])

            dialed = pd.to_numeric(ident_row.get(dialed_col, 0), errors='coerce') if dialed_col else 0
            connected = pd.to_numeric(ident_row.get(connected_col, 0), errors='coerce') if connected_col else 0
            dtmf = pd.to_numeric(ident_row.get(dtmf_col, 0), errors='coerce') if dtmf_col else 0
            sms_triggered = pd.to_numeric(ident_row.get(sms_trig_col, 0), errors='coerce') if sms_trig_col else 0

            dialed, connected, dtmf, sms_triggered = map(
                lambda x: 0 if pd.isna(x) else x,
                [dialed, connected, dtmf, sms_triggered]
            )

            row["Answer Rate (%)"] = round((connected / dialed * 100), 2) if dialed > 0 else 0
            row["Response Rate (%)"] = round((dtmf / connected * 100), 2) if connected > 0 else 0
            row["Cost"] = round((connected * 0.09) + (sms_triggered * 0.1), 2)
        else:
            # Case-insensitive lookup for channel costs
            cost_per_unit = 0
            for key, value in CAMPAIGN_COSTS.items():
                if key.lower() == channel.lower():
                    cost_per_unit = value
                    break
            row["Cost"] = round(delivered * cost_per_unit, 2)
            row["Answer Rate (%)"] = 0
            row["Response Rate (%)"] = 0

        output_rows.append(row)

    df_output = pd.DataFrame(output_rows)

    # Create summary
    summary_rows = []
    all_channels = list(CAMPAIGN_COSTS.keys()) + ["IVR Orbital"]

    for channel in all_channels:
        df_channel = df_output[df_output["Channel"].astype(str).str.lower() == channel.lower()]
        if len(df_channel) == 0:
            continue

        # Case-insensitive lookup for channel costs
        cost_per_unit = 0
        for key, value in CAMPAIGN_COSTS.items():
            if key.lower() == channel.lower():
                cost_per_unit = value
                break

        applications = int(df_channel["Applications"].sum())
        inprogress = int(df_channel["Inprogress"].sum())
        declined = int(df_channel["Declined"].sum())
        ipa_approved = int(df_channel["IPA Approved"].sum())
        card_out = int(df_channel["Card Out"].sum())
        delivered = float(df_channel["Delivered"].sum())
        read = float(df_channel["Read"].sum())
        clicks = float(df_channel["Clicks"].sum())

        # Always use the already calculated cost from detailed data
        total_cost = float(df_channel["Cost"].sum())

        ctr = round((clicks / delivered * 100), 2) if delivered > 0 else 0
        cpc = round((total_cost / clicks), 2) if clicks > 0 else 0
        cost_per_application = round((total_cost / applications), 2) if applications > 0 else 0
        cost_per_ipa = round((total_cost / ipa_approved), 2) if ipa_approved > 0 else 0
        cost_per_card = round((total_cost / card_out), 2) if card_out > 0 else 0
        conversion_rate = round((card_out / applications * 100), 2) if applications > 0 else 0

        summary_rows.append({
            "Channel": channel,
            "Applications": applications,
            "Inprogress": inprogress,
            "Declined": declined,
            "IPA approved": ipa_approved,
            "Card Out": card_out,
            "Delivered": int(delivered),
            "Read": int(read),
            "Clicks": int(clicks),
            "CTR (%)": ctr,
            "CPC (₹)": cpc,
            "Conversion Rate (%)": conversion_rate,
            "Cost per unit (₹)": cost_per_unit,
            "Total cost (₹)": round(total_cost, 2),
            "Cost per Application (₹)": cost_per_application,
            "Cost per IPA (₹)": cost_per_ipa,
            "Cost per Card Out (₹)": cost_per_card,
        })

    df_summary = pd.DataFrame(summary_rows)
    return df_output, df_summary


def render_campaign_analysis_module(df_mis=None, db_engine=None):
    """Main render function for campaign analysis module"""
    st.markdown("## 📈 Campaign Performance Analysis")

    # === Data Source Section ===
    st.markdown("### 📊 Data Sources")

    # Two columns: MIS Data and Campaign Data
    data_col1, data_col2 = st.columns(2)

    # === MIS Data Source ===
    with data_col1:
        st.markdown("#### 📋 MIS Data")

        # Track data source type
        if 'campaign_mis_source' not in st.session_state:
            st.session_state.campaign_mis_source = None

        # Check if MIS data exists from main dashboard
        if df_mis is not None and 'campaign_mis_data' in st.session_state:
            del st.session_state.campaign_mis_data
            st.session_state.campaign_mis_source = None

        if df_mis is None and 'campaign_mis_data' in st.session_state:
            df_mis = st.session_state.campaign_mis_data

        # Display current status with source info
        if df_mis is not None:
            source_text = f" (from {st.session_state.campaign_mis_source})" if st.session_state.campaign_mis_source else ""
            st.success(f"✅ Loaded: {len(df_mis):,} records{source_text}")
        else:
            st.info("ℹ️ No MIS data loaded")

        # MIS data source options
        mis_source_tab1, mis_source_tab2 = st.tabs(["📁 Upload File", "🗄️ Load from DB"])

        with mis_source_tab1:
            uploaded_mis = st.file_uploader(
                "Upload MIS Excel/CSV File",
                type=['xlsx', 'xls', 'csv'],
                key="campaign_mis_file_uploader",
                help="Upload HDFC MIS data file (takes priority over database)"
            )
            if uploaded_mis:
                try:
                    if uploaded_mis.name.endswith('.csv'):
                        df_mis_uploaded = pd.read_csv(uploaded_mis)
                    else:
                        df_mis_uploaded = pd.read_excel(uploaded_mis)

                    df_mis_uploaded.columns = df_mis_uploaded.columns.str.strip()
                    st.session_state.campaign_mis_data = df_mis_uploaded
                    st.session_state.campaign_mis_source = "uploaded file"
                    st.success(f"✅ Uploaded {len(df_mis_uploaded):,} records (file upload takes priority)")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")

        with mis_source_tab2:
            # Disable database load if file is uploaded
            if st.session_state.campaign_mis_source == "uploaded file":
                st.warning("⚠️ File uploaded - database loading disabled. Remove file to use database.")
                st.button("🗄️ Load MIS from Database", key="campaign_load_mis_db", use_container_width=True, disabled=True)
            else:
                if st.button("🗄️ Load MIS from Database", key="campaign_load_mis_db", use_container_width=True):
                    if db_engine:
                        with st.spinner("Loading MIS data from database..."):
                            try:
                                df_mis_loaded = pd.read_sql('SELECT * FROM "HDFC_MIS_Data"', db_engine)
                                df_mis_loaded.columns = df_mis_loaded.columns.str.strip()
                                st.session_state.campaign_mis_data = df_mis_loaded
                                st.session_state.campaign_mis_source = "database"
                                st.success(f"✅ Loaded {len(df_mis_loaded):,} records from DB")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Database error: {str(e)[:100]}")
                    else:
                        st.error("❌ Database not available")

    # === Campaign Identifiers Data Source ===
    with data_col2:
        st.markdown("#### 🎯 Campaign Identifiers")

        # Track data source type
        if 'campaign_identifiers_source' not in st.session_state:
            st.session_state.campaign_identifiers_source = None

        # Display current status with source info
        if 'campaign_identifiers_data' in st.session_state:
            source_text = f" (from {st.session_state.campaign_identifiers_source})" if st.session_state.campaign_identifiers_source else ""
            st.success(f"✅ Loaded: {len(st.session_state.campaign_identifiers_data):,} campaigns{source_text}")
        else:
            st.info("ℹ️ No campaign data loaded")

        # Campaign data source options
        campaign_source_tab1, campaign_source_tab2 = st.tabs(["📁 Upload File", "🔗 Load from Sheets"])

        with campaign_source_tab1:
            uploaded_campaign = st.file_uploader(
                "Upload Campaign Excel/CSV File",
                type=['xlsx', 'xls', 'csv'],
                key="campaign_identifiers_file_uploader",
                help="Upload campaign identifiers file (takes priority over Google Sheets)"
            )
            if uploaded_campaign:
                try:
                    if uploaded_campaign.name.endswith('.csv'):
                        df_campaign_uploaded = pd.read_csv(uploaded_campaign)
                    else:
                        df_campaign_uploaded = pd.read_excel(uploaded_campaign)

                    df_campaign_uploaded.columns = df_campaign_uploaded.columns.str.strip()
                    st.session_state.campaign_identifiers_data = df_campaign_uploaded
                    st.session_state.campaign_identifiers_source = "uploaded file"
                    st.success(f"✅ Uploaded {len(df_campaign_uploaded):,} campaigns (file upload takes priority)")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")

        with campaign_source_tab2:
            # Disable Google Sheets load if file is uploaded
            if st.session_state.campaign_identifiers_source == "uploaded file":
                st.warning("⚠️ File uploaded - Google Sheets loading disabled. Remove file to use Sheets.")
                st.text_input(
                    "Google Sheets URL (CSV export format)",
                    value="https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid=2141873222",
                    key="campaign_sheet_url",
                    disabled=True
                )
                st.button("🔗 Load from Google Sheets", key="campaign_load_sheets", use_container_width=True, disabled=True)
            else:
                sheet_url = st.text_input(
                    "Google Sheets URL (CSV export format)",
                    value="https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid=2141873222",
                    key="campaign_sheet_url"
                )
                if st.button("🔗 Load from Google Sheets", key="campaign_load_sheets", use_container_width=True):
                    try:
                        with st.spinner("Loading from Google Sheets..."):
                            df_campaign_sheets = pd.read_csv(sheet_url)
                            df_campaign_sheets.columns = df_campaign_sheets.columns.str.strip()
                            st.session_state.campaign_identifiers_data = df_campaign_sheets
                            st.session_state.campaign_identifiers_source = "Google Sheets"
                            st.success(f"✅ Loaded {len(df_campaign_sheets):,} campaigns from Sheets")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error loading from Sheets: {str(e)}")

    st.markdown("---")

    # Update df_mis from session state if not from main dashboard
    if df_mis is None and 'campaign_mis_data' in st.session_state:
        df_mis = st.session_state.campaign_mis_data

    # Get campaign identifiers
    df_identifiers = st.session_state.get('campaign_identifiers_data', None)

    if df_mis is not None and df_identifiers is not None:
        try:
            with st.spinner("🔄 Processing campaign data..."):
                df_mis = df_mis.copy()
                
                # Find date column
                date_col = find_date_column(df_identifiers)
                
                if date_col:
                    df_identifiers[date_col] = parse_dates_safely(df_identifiers[date_col])
                    valid_date_mask = df_identifiers[date_col].notna()
                    valid_count = valid_date_mask.sum()
                    df_identifiers = df_identifiers[valid_date_mask].copy()
                    
                    if len(df_identifiers) == 0:
                        st.error("❌ No valid dates found in the data")
                        return
                    
                    min_date = df_identifiers[date_col].min()
                    max_date = df_identifiers[date_col].max()
                    
                    st.success(f"✅ Loaded {len(df_mis):,} MIS records | {valid_count:,} valid campaigns")
                    st.info(f"📅 Date range: {min_date.strftime('%b %d, %Y')} to {max_date.strftime('%b %d, %Y')}")
                    
                    # Date filters
                    st.markdown("### 📅 Date Range Selection")
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        start_date = st.date_input(
                            "Start Date",
                            value=min_date,
                            min_value=min_date,
                            max_value=max_date
                        )
                    
                    with col2:
                        end_date = st.date_input(
                            "End Date",
                            value=max_date,
                            min_value=min_date,
                            max_value=max_date
                        )
                    
                    with col3:
                        quick_filter = st.selectbox(
                            "Quick Filter",
                            ["Custom", "Last 7 days", "Last 30 days", "This Month", "Last Month", "All Time"]
                        )
                        
                        # Apply quick filters
                        if quick_filter == "Last 7 days":
                            end_date = max_date.date()
                            start_date = (max_date - timedelta(days=7)).date()
                        elif quick_filter == "Last 30 days":
                            end_date = max_date.date()
                            start_date = (max_date - timedelta(days=30)).date()
                        elif quick_filter == "This Month":
                            end_date = max_date.date()
                            start_date = max_date.replace(day=1).date()
                        elif quick_filter == "Last Month":
                            end_date = (max_date.replace(day=1) - timedelta(days=1)).date()
                            start_date = end_date.replace(day=1)
                        elif quick_filter == "All Time":
                            start_date = min_date.date()
                            end_date = max_date.date()
                    
                    # Run analysis
                    df_output, df_summary = analyze_campaigns(
                        df_identifiers, df_mis, 
                        pd.Timestamp(start_date), 
                        pd.Timestamp(end_date), 
                        date_col
                    )
                    
                    # Show filtered count
                    filtered_count = len(df_identifiers[
                        (df_identifiers[date_col] >= pd.Timestamp(start_date)) & 
                        (df_identifiers[date_col] <= pd.Timestamp(end_date))
                    ])
                    
                    if filtered_count > 0:
                        st.info(f"📊 Analyzing {filtered_count:,} campaigns from {start_date.strftime('%b %d')} to {end_date.strftime('%b %d, %Y')}")
                    else:
                        st.warning("⚠️ No campaigns found in selected date range")
                        return
                else:
                    st.warning("⚠️ No date column found. Analyzing all campaigns.")
                    df_output, df_summary = analyze_campaigns(df_identifiers, df_mis)
            
            # Display metrics
            st.markdown("### 📈 Key Performance Metrics")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_apps = df_summary["Applications"].sum()
            total_cost = df_summary["Total cost (₹)"].sum()
            total_ipa = df_summary["IPA approved"].sum()
            total_card_out = df_summary["Card Out"].sum()
            avg_cpa = total_cost / total_apps if total_apps > 0 else 0
            
            with col1:
                st.metric("📝 Applications", f"{total_apps:,}")
            with col2:
                st.metric("💰 Total Cost", f"₹{total_cost:,.2f}")
            with col3:
                st.metric("✅ IPA Approved", f"{total_ipa:,}")
            with col4:
                st.metric("💳 Card Out", f"{total_card_out:,}")
            with col5:
                st.metric("📊 Avg Cost/App", f"₹{avg_cpa:.2f}")
            
            st.markdown("---")
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Visualizations", 
                "📑 Summary", 
                "📋 Detailed Data", 
                "📥 Download"
            ])
            
            with tab1:
                st.markdown("### 📊 Performance Visualizations")

                # Global Filters
                st.markdown("#### 🎯 Global Filters (Apply to All Charts)")
                global_filter_col1, global_filter_col2 = st.columns(2)

                with global_filter_col1:
                    global_channel_filter = st.multiselect(
                        "Filter by Channel (Global):",
                        options=df_summary["Channel"].unique().tolist(),
                        default=df_summary["Channel"].unique().tolist(),
                        
                        key="global_channel_filter"
                    )

                with global_filter_col2:
                    global_decision_filter = st.multiselect(
                        "Filter by Final Decision (Global):",
                        options=["Card Out", "Declined", "Inprogress", "IPA Approved"],
                        default=["Card Out", "Declined", "Inprogress", "IPA Approved"],
                        
                        key="global_decision_filter"
                    )

                # Apply global filters to summary data
                df_summary_global = df_summary[df_summary["Channel"].isin(global_channel_filter)].copy()

                # Recalculate totals based on global filters
                global_apps = df_summary_global["Applications"].sum()
                global_cost = df_summary_global["Total cost (₹)"].sum()
                global_ipa = df_summary_global["IPA approved"].sum()
                global_card_out = df_summary_global["Card Out"].sum()
                global_declined = df_summary_global["Declined"].sum()
                global_inprogress = df_summary_global["Inprogress"].sum()

                st.markdown("---")

                # Chart 1: Custom Bar Chart
                st.markdown("#### 📊 Chart 1: Custom Bar Chart")
                with st.expander("⚙️ Customize Bar Chart", expanded=True):
                    bar_col1, bar_col2, bar_col3 = st.columns(3)

                    with bar_col1:
                        numeric_cols = df_summary_global.select_dtypes(include=['number']).columns.tolist()
                        bar_y_col = st.selectbox(
                            "Y-Axis Metric:",
                            options=numeric_cols,
                            index=numeric_cols.index("Applications") if "Applications" in numeric_cols else 0,
                            key="bar_y_col"
                        )

                    with bar_col2:
                        bar_channel_filter = st.multiselect(
                            "Channels for this chart:",
                            options=df_summary_global["Channel"].unique().tolist(),
                            default=df_summary_global["Channel"].unique().tolist(),
                            key="bar_channel_filter"
                        )

                    with bar_col3:
                        bar_sort = st.selectbox(
                            "Sort by:",
                            options=["Default", "Ascending", "Descending"],
                            key="bar_sort"
                        )

                df_bar = df_summary_global[df_summary_global["Channel"].isin(bar_channel_filter)].copy()
                if bar_sort == "Ascending":
                    df_bar = df_bar.sort_values(by=bar_y_col, ascending=True)
                elif bar_sort == "Descending":
                    df_bar = df_bar.sort_values(by=bar_y_col, ascending=False)

                viz_col1, viz_col2 = st.columns(2)

                with viz_col1:
                    # Custom Bar Chart
                    if not df_bar.empty:
                        fig1 = px.bar(
                            df_bar, x="Channel", y=bar_y_col,
                            title=f"{bar_y_col} by Channel",
                            color=bar_y_col,
                            color_continuous_scale="Blues",
                            text=bar_y_col
                        )
                        fig1.update_traces(textposition='outside')
                        fig1.update_layout(showlegend=False, height=400)
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.info("No data available for selected filters")

                    # Chart 3: Cost Efficiency Bar Chart
                    st.markdown("#### 📊 Chart 3: Cost Efficiency")
                    with st.expander("⚙️ Customize Cost Efficiency Chart", expanded=False):
                        cost_col1, cost_col2 = st.columns(2)

                        with cost_col1:
                            cost_metric = st.selectbox(
                                "Cost Metric:",
                                options=["Cost per Application (₹)", "Cost per IPA (₹)", "Cost per Card Out (₹)", "Total cost (₹)"],
                                key="cost_metric"
                            )

                        with cost_col2:
                            cost_channel_filter = st.multiselect(
                                "Channels:",
                                options=df_summary_global["Channel"].unique().tolist(),
                                default=df_summary_global["Channel"].unique().tolist(),
                                key="cost_channel_filter"
                            )

                    df_cost = df_summary_global[df_summary_global["Channel"].isin(cost_channel_filter)].copy()

                    if not df_cost.empty and cost_metric in df_cost.columns:
                        fig3 = px.bar(
                            df_cost, x="Channel", y=cost_metric,
                            title=f"{cost_metric} by Channel",
                            color=cost_metric,
                            color_continuous_scale="Reds",
                            text=cost_metric
                        )
                        fig3.update_traces(texttemplate='₹%{text:.2f}', textposition='outside')
                        fig3.update_layout(showlegend=False, height=400)
                        st.plotly_chart(fig3, use_container_width=True)

                with viz_col2:
                    # Chart 2: Custom Pie Chart
                    st.markdown("#### 📊 Chart 2: Distribution Pie Chart")
                    with st.expander("⚙️ Customize Pie Chart", expanded=True):
                        pie_col1, pie_col2 = st.columns(2)

                        with pie_col1:
                            pie_value_col = st.selectbox(
                                "Value Metric:",
                                options=numeric_cols,
                                index=numeric_cols.index("Total cost (₹)") if "Total cost (₹)" in numeric_cols else 0,
                                key="pie_value_col"
                            )

                        with pie_col2:
                            pie_channel_filter = st.multiselect(
                                "Channels:",
                                options=df_summary_global["Channel"].unique().tolist(),
                                default=df_summary_global["Channel"].unique().tolist(),
                                key="pie_channel_filter"
                            )

                    df_pie = df_summary_global[df_summary_global["Channel"].isin(pie_channel_filter)].copy()

                    if not df_pie.empty:
                        fig2 = px.pie(
                            df_pie, values=pie_value_col, names="Channel",
                            title=f"{pie_value_col} Distribution by Channel",
                            hole=0.4
                        )
                        fig2.update_traces(textposition='inside', textinfo='percent+label+value')
                        fig2.update_layout(height=400)
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.info("No data available for selected filters")

                    # Chart 4: Conversion Funnel
                    st.markdown("#### 📊 Chart 4: Conversion Funnel")
                    with st.expander("⚙️ Customize Funnel", expanded=False):
                        funnel_stages = st.multiselect(
                            "Funnel Stages:",
                            options=["Total Applications", "IPA Approved", "Card Out"],
                            default=["Total Applications", "IPA Approved", "Card Out"],
                            key="funnel_stages"
                        )

                    funnel_data = []
                    funnel_labels = []

                    if "Total Applications" in funnel_stages:
                        funnel_labels.append("Total Applications")
                        funnel_data.append(global_apps)
                    if "IPA Approved" in funnel_stages:
                        funnel_labels.append("IPA Approved")
                        funnel_data.append(global_ipa)
                    if "Card Out" in funnel_stages:
                        funnel_labels.append("Card Out")
                        funnel_data.append(global_card_out)

                    if funnel_data:
                        fig4 = go.Figure(go.Funnel(
                            y=funnel_labels,
                            x=funnel_data,
                            textposition="inside",
                            textinfo="value+percent initial",
                            marker={"color": ["#667eea", "#764ba2", "#f093fb"][:len(funnel_data)]}
                        ))
                        fig4.update_layout(title="Conversion Funnel", height=400)
                        st.plotly_chart(fig4, use_container_width=True)

                # Chart 5: Final Decision Breakdown
                st.markdown("#### 📊 Chart 5: Final Decision Breakdown")
                with st.expander("⚙️ Customize Decision Breakdown", expanded=False):
                    decision_col1, decision_col2 = st.columns(2)

                    with decision_col1:
                        decision_status_filter = st.multiselect(
                            "Statuses to Display:",
                            options=['Card Out', 'Declined', 'Inprogress'],
                            default=['Card Out', 'Declined', 'Inprogress'],
                            key="decision_status_filter"
                        )

                    with decision_col2:
                        decision_chart_type = st.selectbox(
                            "Chart Type:",
                            options=["Bar Chart", "Pie Chart"],
                            key="decision_chart_type"
                        )

                decision_data = {
                    'Status': [],
                    'Count': []
                }

                if "Card Out" in decision_status_filter:
                    decision_data['Status'].append('Card Out')
                    decision_data['Count'].append(global_card_out)
                if "Declined" in decision_status_filter:
                    decision_data['Status'].append('Declined')
                    decision_data['Count'].append(global_declined)
                if "Inprogress" in decision_status_filter:
                    decision_data['Status'].append('Inprogress')
                    decision_data['Count'].append(global_inprogress)

                if decision_data['Count']:
                    df_decision = pd.DataFrame(decision_data)

                    if decision_chart_type == "Bar Chart":
                        fig5 = px.bar(
                            df_decision, x='Status', y='Count',
                            title='Final Decision Status Distribution',
                            color='Status',
                            color_discrete_map={
                                'Card Out': '#10B981',
                                'Declined': '#EF4444',
                                'Inprogress': '#3B82F6'
                            },
                            text='Count'
                        )
                        fig5.update_traces(textposition='outside')
                        fig5.update_layout(showlegend=False, height=400)
                    else:
                        fig5 = px.pie(
                            df_decision, values='Count', names='Status',
                            title='Final Decision Status Distribution',
                            color='Status',
                            color_discrete_map={
                                'Card Out': '#10B981',
                                'Declined': '#EF4444',
                                'Inprogress': '#3B82F6'
                            },
                            hole=0.4
                        )
                        fig5.update_traces(textposition='inside', textinfo='percent+label+value')
                        fig5.update_layout(height=400)

                    st.plotly_chart(fig5, use_container_width=True)
            
            with tab2:
                st.markdown("### 📑 Campaign Summary")
                st.dataframe(
                    df_summary.style.format({
                        "Total cost (₹)": "₹{:.2f}",
                        "Cost per Application (₹)": "₹{:.2f}",
                        "Cost per IPA (₹)": "₹{:.2f}",
                        "Cost per Card Out (₹)": "₹{:.2f}",
                        "CTR (%)": "{:.2f}%",
                        "CPC (₹)": "₹{:.2f}",
                        "Conversion Rate (%)": "{:.2f}%",
                    }),
                    use_container_width=True,
                    height=500
                )
            
            with tab3:
                st.markdown("### 📋 Detailed Campaign Data")
                
                # Filters
                col1, col2 = st.columns(2)
                with col1:
                    channel_filter = st.multiselect(
                        "Filter by Channel:",
                        df_output["Channel"].unique().tolist(),
                        default=df_output["Channel"].unique().tolist()
                    )
                with col2:
                    sort_by = st.selectbox(
                        "Sort by:",
                        ["Applications", "Cost", "IPA Approved", "Card Out"]
                    )
                
                filtered_output = df_output[df_output["Channel"].isin(channel_filter)]
                filtered_output = filtered_output.sort_values(by=sort_by, ascending=False)
                
                st.dataframe(filtered_output, use_container_width=True, height=500)
                st.caption(f"Showing {len(filtered_output):,} of {len(df_output):,} records")
            
            with tab4:
                st.markdown("### 📥 Download Reports")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Excel download
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df_output.to_excel(writer, sheet_name="Detailed Analysis", index=False)
                        df_summary.to_excel(writer, sheet_name="Summary", index=False)
                    output.seek(0)
                    
                    st.download_button(
                        label="📊 Download Excel Report",
                        data=output,
                        file_name=f"Campaign_Analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col2:
                    # Summary CSV
                    csv_summary = df_summary.to_csv(index=False)
                    st.download_button(
                        label="📄 Download Summary CSV",
                        data=csv_summary,
                        file_name=f"Campaign_Summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    # Detailed CSV
                    csv_detailed = df_output.to_csv(index=False)
                    st.download_button(
                        label="📋 Download Detailed CSV",
                        data=csv_detailed,
                        file_name=f"Campaign_Detailed_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"❌ Error processing campaign data: {e}")
            with st.expander("🔍 View Error Details"):
                st.exception(e)

    else:
        st.warning("⚠️ Please load both MIS Data and Campaign Identifiers to begin analysis")


if __name__ == "__main__":
    st.set_page_config(page_title="Campaign Analysis", layout="wide", page_icon="📈")
    render_campaign_analysis_module()