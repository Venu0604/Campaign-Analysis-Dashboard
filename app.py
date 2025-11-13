"""
Unified Campaign Analytics Dashboard
Multi-bank campaign performance analysis and reporting tool
"""


import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO


import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px


# Import custom modules
from config import get_bank_config, get_google_sheet_url, get_all_bank_names
from core import CampaignDataProcessor
from ui import get_custom_css, get_dashboard_css
from utils import load_google_sheet, load_excel_file, get_extrape_logo


# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(
   page_title="Campaign Analytics | extrape advisor",
   layout="wide",
   page_icon="📊",
   initial_sidebar_state="expanded"
)

# Force Streamlit to use light theme for dataframes
import os
os.environ['STREAMLIT_THEME_BASE'] = 'light'


# -------------------------
# Initialize Session State
# -------------------------
if 'bank_data' not in st.session_state:
   st.session_state.bank_data = {}


if 'view_mode' not in st.session_state:
   st.session_state.view_mode = 'overview'  # 'overview' or 'bank_detail'


if 'selected_bank_detail' not in st.session_state:
   st.session_state.selected_bank_detail = None


if 'clear_triggered' not in st.session_state:
   st.session_state.clear_triggered = False


# -------------------------
# Sidebar - MIS Upload for Each Bank
# -------------------------
with st.sidebar:
   st.markdown("### 📁 Upload MIS Files")
   st.markdown("Upload MIS files for each bank to see overall analysis")

   st.markdown("---")


   for bank in get_all_bank_names():
       bank_key = bank.replace(' ', '_').lower()


       with st.expander(f"🏦 {bank}", expanded=False):
           uploaded_file = st.file_uploader(
               f"Upload {bank} MIS",
               type=["xlsx", "xls", "xlsb", "csv"],
               key=f"upload_{bank_key}",
               label_visibility="collapsed"
           )


           if uploaded_file:
               # Skip processing if clear was just triggered
               if st.session_state.get('clear_triggered', False):
                   st.info("⚠️ Data cleared - Click 'Dismiss' below and re-upload if needed")
               elif bank not in st.session_state.bank_data or \
                       st.session_state.bank_data.get(bank, {}).get('file_name') != uploaded_file.name:

                   with st.spinner(f"Processing {bank}..."):
                       try:
                           # Get bank config first to check for specific sheet name
                           bank_config = get_bank_config(bank)

                           # Load MIS file with bank-specific sheet name if specified
                           sheet_name = bank_config.get('sheet_name', 0)  # Default to first sheet
                           df_mis = load_excel_file(uploaded_file, sheet_name=sheet_name)

                           if df_mis is not None:
                               # Load identifiers
                               sheet_url = get_google_sheet_url(bank)
                               df_identifiers = load_google_sheet(sheet_url)

                               if df_identifiers is not None:
                                   import warnings
                                   with warnings.catch_warnings():
                                       warnings.filterwarnings("ignore", message="Could not infer format")
                                       df_identifiers['Date'] = pd.to_datetime(df_identifiers['Date'], format='%d-%m-%Y', errors='coerce')

                                   # Process data
                                   processor = CampaignDataProcessor(bank_config)
                                   df_summary, df_matched_mis = processor.process_campaign_data(
                                       df_identifiers, df_mis
                                   )


                                   if df_summary is not None:
                                       st.session_state.bank_data[bank] = {
                                           'file_name': uploaded_file.name,
                                           'summary': df_summary,
                                           'matched_mis': df_matched_mis,
                                           'processor': processor,
                                           'config': bank_config
                                       }
                                       st.success(f"✅ {len(df_summary)} campaigns")

                                       # Show View Details button immediately after processing
                                       if st.button(f"View {bank} Details", key=f"view_{bank_key}_new", use_container_width=True):
                                           st.session_state.view_mode = 'bank_detail'
                                           st.session_state.selected_bank_detail = bank
                                           st.rerun()
                                   else:
                                       st.error("❌ Processing failed")
                               else:
                                   st.error("❌ Failed to load identifiers")
                           else:
                               st.error("❌ Failed to load MIS")
                       except Exception as e:
                           st.error(f"❌ Error: {str(e)[:50]}")
               else:
                   st.success(f"✅ {uploaded_file.name}")

                   # View detail button
                   if st.button(f"View {bank} Details", key=f"view_{bank_key}", use_container_width=True):
                       st.session_state.view_mode = 'bank_detail'
                       st.session_state.selected_bank_detail = bank
                       st.rerun()
           else:
               # Only remove if file was removed (not on initial load)
               if bank in st.session_state.bank_data:
                   del st.session_state.bank_data[bank]
                   st.session_state.view_mode = 'overview'
                   st.session_state.selected_bank_detail = None
               st.info("No file uploaded")


   st.markdown("---")

   # Clear all data button - Always show if data exists
   if len(st.session_state.bank_data) > 0:
       st.markdown("### 🗑️ Clear Data")
       if st.button("Clear All Data", key='clear_all_button', type='secondary', use_container_width=True):
           # Store keys to delete
           keys_to_delete = list(st.session_state.bank_data.keys())

           # Clear all bank data
           for key in keys_to_delete:
               if key in st.session_state.bank_data:
                   del st.session_state.bank_data[key]

           # Clear all file uploader widgets
           for bank in get_all_bank_names():
               bank_key = bank.replace(' ', '_').lower()
               upload_key = f"upload_{bank_key}"
               if upload_key in st.session_state:
                   del st.session_state[upload_key]

           # Reset other session state variables
           st.session_state.view_mode = 'overview'
           st.session_state.selected_bank_detail = None
           st.session_state.clear_triggered = True

           # Force rerun
           st.rerun()

   # Show warning if clear was triggered
   if st.session_state.get('clear_triggered', False) and len(st.session_state.bank_data) == 0:
       st.info("✅ All data has been cleared successfully!")
       if st.button("Dismiss", key='dismiss_button', use_container_width=True):
           st.session_state.clear_triggered = False
           st.rerun()


# --- THEME DETECTION HELPER ---
def get_plotly_theme():
   """Circle Health inspired Plotly theme with light colors"""
   # Always use light theme for Circle Health style
   return {
       "template": "plotly_white",
       "bg_color": "rgba(255,255,255,1)",
       "font_color": "#0f172a",  # dark navy text
       "grid_color": "#e2e8f0",  # light grid
       "primary_color": "#3b82f6",  # soft blue
       "secondary_color": "#0ea5e9",  # lighter blue
       "accent_color": "#fcc038",  # yellow/orange accent
       "success_color": "#10b981",  # green
       "chart_colors": ["#3b82f6", "#0ea5e9", "#fcc038", "#8b5cf6", "#ec4899", "#10b981"]
   }


# --- Initialize global theme configuration ---
theme_cfg = get_plotly_theme()


# --- Improve Plotly visibility across the app ---
# FIX: Use square bracket notation [] instead of .get() on pio.templates
base_template = pio.templates[theme_cfg.get("template", "plotly_dark")].layout


# FIX: Use square bracket notation [] instead of .get() on pio.templates
pio.templates["extrape_high_contrast"] = pio.templates[theme_cfg.get("template", "plotly_dark")].update({})
pio.templates["extrape_high_contrast"].layout.font = dict(
    color=theme_cfg["font_color"],
    family="Poppins",
    size=13
)
pio.templates["extrape_high_contrast"].layout.title = dict(
    font=dict(color=theme_cfg["font_color"], size=16, family="Poppins")
)
pio.templates["extrape_high_contrast"].layout.xaxis = dict(tickfont=dict(color=theme_cfg["font_color"], size=11))
pio.templates["extrape_high_contrast"].layout.yaxis = dict(tickfont=dict(color=theme_cfg["font_color"], size=11))
pio.templates["extrape_high_contrast"].layout.legend = dict(font=dict(color=theme_cfg["font_color"], size=11))
pio.templates["extrape_high_contrast"].layout.paper_bgcolor = theme_cfg["bg_color"]
pio.templates["extrape_high_contrast"].layout.plot_bgcolor = theme_cfg["bg_color"]


pio.templates.default = "extrape_high_contrast"


def enhance_fig_visibility(fig, text_font_size=13, text_color=None):
    if text_color is None:
        text_color = theme_cfg["font_color"]
    try:
        for trace in fig.data:
            if hasattr(trace, "textfont"):
                trace.textfont = dict(size=text_font_size, color=text_color, family="Poppins")
            if hasattr(trace, "marker") and isinstance(trace.marker, dict):
                trace.marker.setdefault("line", {})
                trace.marker["line"].update({"color": theme_cfg["bg_color"], "width": 1.5})
    except Exception:
        pass
    fig.update_layout(
        font=dict(color=theme_cfg["font_color"], family="Poppins"),
        title_font=dict(color=theme_cfg["font_color"]),
        legend=dict(font=dict(color=theme_cfg["font_color"]))
    )
    return fig


# -------------------------
# Main Content Area
# -------------------------


# Navigation
if st.session_state.view_mode == 'bank_detail':
   # Back button with enhanced visibility
   col1, col2, col3 = st.columns([1, 2, 1])

   with col1:
       if st.button("← Back to Overview", key='back_to_overview', type='primary', use_container_width=True):
           st.session_state.view_mode = 'overview'
           st.session_state.selected_bank_detail = None
           st.rerun()

   # Bank selector - only if multiple banks loaded
   if len(st.session_state.bank_data) > 1:
       with col2:
           bank_list = list(st.session_state.bank_data.keys())

           # Get current index
           if st.session_state.selected_bank_detail in bank_list:
               current_index = bank_list.index(st.session_state.selected_bank_detail)
           else:
               current_index = 0

           # Show selectbox
           selected_bank = st.selectbox(
               "Switch to Bank:",
               options=bank_list,
               index=current_index,
               key='bank_switch_selector'
           )

           # Update if changed
           if selected_bank != st.session_state.selected_bank_detail:
               st.session_state.selected_bank_detail = selected_bank
               st.rerun()

   st.markdown("---")


# -------------------------
# Overview Mode - Multi-Bank Analysis
# -------------------------
if st.session_state.view_mode == 'overview':
    # Apply consolidated dashboard styling
    st.markdown(get_dashboard_css(), unsafe_allow_html=True)


    # Header with branding
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown('<div class="main-header">Campaign Analytics Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Multi-Bank Performance Intelligence</div>', unsafe_allow_html=True)


    with header_col2:
        # Display extrape advisor logo
        extrape_logo = get_extrape_logo()
        if extrape_logo:
            st.markdown(f"""
                <div style='text-align: right; padding-top: 0.25rem;'>
                    <img src='data:image/webp;base64,{extrape_logo}' style='height: 35px; width: auto;'/>
                </div>
            """, unsafe_allow_html=True)


    # Show loaded banks count and filters
    if st.session_state.bank_data:
        st.markdown(f"""
            <div style='background: white; padding: 0.85rem 1.25rem; border-radius: 12px; margin: 0.5rem 0; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                <p style='color: #1e293b; font-size: 1.1rem; margin: 0; text-align: center; font-weight: 700; font-family: Nunito;'>
                    📊 Analyzing {len(st.session_state.bank_data)} Bank{'s' if len(st.session_state.bank_data) > 1 else ''}: {', '.join(st.session_state.bank_data.keys())}
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Add Date Filter Section
        st.markdown("### 🔍 Filter by Date Range")

        # Get min and max dates across all banks
        all_dates = []
        for bank, data in st.session_state.bank_data.items():
            df = data['summary']
            if 'Date' in df.columns:
                all_dates.extend(df['Date'].dropna().tolist())

        if all_dates:
            min_date = pd.to_datetime(min(all_dates)).date()
            max_date = pd.to_datetime(max(all_dates)).date()

            filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 3])

            with filter_col1:
                start_date = st.date_input(
                    "Start Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key='overview_start_date'
                )

            with filter_col2:
                end_date = st.date_input(
                    "End Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key='overview_end_date'
                )

            with filter_col3:
                if start_date > end_date:
                    st.error("⚠️ Start date must be before or equal to end date")
                else:
                    total_days = (end_date - start_date).days + 1
                    st.info(f"📅 Analyzing {total_days} days of data ({start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')})")

        st.markdown("---")


    if not st.session_state.bank_data:
        # Clean minimalist welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Welcome message
            st.markdown("""
                <div style='text-align: center; padding: 2rem 0 1rem 0;'>
                    <h2 style='color: #0f172a; font-weight: 700; font-family: Nunito;
    font-size: 2.8rem; margin-bottom: 0.75rem;'>
                        Welcome to Campaign Analytics
                    </h2>
                    <p style='color: #1e293b; font-family: Nunito;
    font-size: 1.25rem; line-height: 1.5; font-weight: 600;'>
                        Upload MIS files in the sidebar to begin analysis
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Features section - Circle Health style
            st.markdown("""
                <div style='background: white; border-radius: 16px; padding: 1.5rem; border: 1px solid #cbd5e1; margin-top: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
                    <p style='color: #0f172a; font-weight: 700; font-size: 1.35rem; margin-bottom: 1rem; text-align: center; font-family: Nunito;'>
                        Key Capabilities
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Feature list with Circle Health styling
            features = [
                "Multi-Bank Consolidated View",
                "Real-Time Performance Metrics",
                "Interactive Visual Analytics",
                "Individual Bank Deep Dive",
                "Comprehensive Export Options"
            ]

            for feature in features:
                st.markdown(f"""
                    <div style='padding: 0.5rem 0; color: #0f172a;'>
                        <span style='color: #3b82f6; margin-right: 0.5rem; font-weight: 700; font-size: 1.3rem;'>●</span>
                        <span style='font-size: 1.1rem; font-weight: 600; font-family: Nunito;'>{feature}</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        # Aggregate data from all banks
        all_summaries = []
        bank_wise_stats = []

        # Apply date filter if dates are selected
        date_filter_active = False
        if all_dates:
            date_filter_active = True
            filter_start = pd.Timestamp(start_date)
            filter_end = pd.Timestamp(end_date)

        for bank, data in st.session_state.bank_data.items():
            df = data['summary'].copy()

            # Apply date filter
            if date_filter_active and 'Date' in df.columns:
                df = df[(df['Date'] >= filter_start) & (df['Date'] <= filter_end)]

            df['Bank'] = bank
            all_summaries.append(df)

            # Calculate bank-wise stats
            stats = data['processor'].get_summary_statistics(df)
            stats['Bank'] = bank
            bank_wise_stats.append(stats)

        # Show filter summary
        if date_filter_active:
            total_campaigns = sum([len(df) for df in all_summaries])
            st.success(f"✅ Showing {total_campaigns} campaigns within the selected date range")

        # Combine all data
        df_combined = pd.concat(all_summaries, ignore_index=True)

        # Calculate overall metrics
        total_applications = df_combined['Applications'].sum()
        total_ipa_approved = df_combined['IPA Approved'].sum()
        total_card_out = df_combined['Card Out'].sum()
        total_declined = df_combined['Declined'].sum()
        total_in_progress = df_combined['In Progress'].sum()
        total_cost = df_combined['Total cost (₹)'].sum()

        # Conversion rates
        app_to_ipa = (total_ipa_approved / total_applications * 100) if total_applications > 0 else 0
        ipa_to_card = (total_card_out / total_ipa_approved * 100) if total_ipa_approved > 0 else 0
        app_to_card = (total_card_out / total_applications * 100) if total_applications > 0 else 0

        # -------------------------
        # Overall Metrics Dashboard
        # -------------------------
        st.markdown("### 📊 Performance Overview")

        # Create and normalize the bank_comparison DataFrame
        bank_comparison = pd.DataFrame(bank_wise_stats)
        bank_comparison = bank_comparison[[
            'Bank', 'total_apps', 'total_ipa_approved', 'total_card_out',
            'total_declined', 'total_cost', 'avg_cpa', 'app_to_ipa_rate', 'ipa_to_card_rate'
        ]]

        # --- Clean & force numeric cost before renaming ---
        bank_comparison['total_cost'] = (
            bank_comparison['total_cost']
            .astype(str)
            .str.replace('₹', '', regex=False)
            .str.replace(',', '', regex=False)
            .str.strip()
        )
        bank_comparison['total_cost'] = pd.to_numeric(bank_comparison['total_cost'], errors='coerce').fillna(0)


        bank_comparison.columns = [
            'Bank', 'Applications', 'IPA Approved', 'Card Out',
            'Declined', 'Total Cost (₹)', 'Avg CPA (₹)', 'App→IPA %', 'IPA→Card %'
        ]

        # 🧮 Ensure numeric Total Cost (remove ₹ symbols/commas)
        if bank_comparison['Total Cost (₹)'].dtype == object:
            bank_comparison['Total Cost (₹)'] = (
                bank_comparison['Total Cost (₹)']
                .astype(str)
                .str.replace(r'[^\d.-]', '', regex=True)
                .replace('', '0')
                .astype(float)
            )

        # Compute total cost percentage share per bank
        total_cost = bank_comparison['Total Cost (₹)'].sum()
        bank_comparison['Cost %'] = (
            (bank_comparison['Total Cost (₹)'] / total_cost * 100).round(1)
        )

        # Compute aggregate totals
        total_applications = bank_comparison['Applications'].sum()
        total_ipa_approved = bank_comparison['IPA Approved'].sum()
        total_card_out = bank_comparison['Card Out'].sum()
        total_declined = bank_comparison['Declined'].sum()
        total_in_progress = 0  # optional if not tracked

        # Conversion metrics
        app_to_ipa = (total_ipa_approved / total_applications * 100) if total_applications > 0 else 0
        app_to_card = (total_card_out / total_applications * 100) if total_applications > 0 else 0

        # --- KPI Cards ---
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

        with metric_col1:
            st.metric(
                "Total Applications",
                f"{total_applications:,}",
                delta=f"{len(st.session_state.bank_data)} banks",
                help="Total applications across all banks"
            )

        with metric_col2:
            st.metric(
                "IPA Approved",
                f"{total_ipa_approved:,}",
                delta=f"{app_to_ipa:.1f}% of apps",
                help="In-Principle Approved applications"
            )

        with metric_col3:
            st.metric(
                "Card Out",
                f"{total_card_out:,}",
                delta=f"{app_to_card:.1f}% conversion",
                help="Successfully issued cards"
            )

        with metric_col4:
            st.metric(
                "Declined",
                f"{total_declined:,}",
                delta=f"{(total_declined / total_applications * 100):.1f}% of apps" if total_applications > 0 else "0%",
                delta_color="inverse",
                help="Declined applications"
            )

        with metric_col5:
            st.metric(
                "Total Cost (₹)",
                f"₹{total_cost:,.0f}",
                help="Total campaign spend"
            )

        # -------------------------
        # Bank-Wise Comparison Table
        # -------------------------
        st.markdown("### 🏦 Bank Performance Comparison")

        # Format the styled dataframe and convert to HTML
        styled_df = (bank_comparison.style.format({
            'Applications': '{:,.0f}',
            'IPA Approved': '{:,.0f}',
            'Card Out': '{:,.0f}',
            'Declined': '{:,.0f}',
            'Total Cost (₹)': '₹{:,.2f}',
            'Avg CPA (₹)': '₹{:.2f}',
            'App→IPA %': '{:.1f}%',
            'IPA→Card %': '{:.1f}%',
            'Cost %': '{:.1f}%'
        }).background_gradient(subset=['Applications'], cmap='Blues')
          .background_gradient(subset=['Card Out'], cmap='Greens')
          .background_gradient(subset=['Total Cost (₹)'], cmap='Reds')
          .set_properties(**{
            'color': '#0f172a',
            'background-color': 'white',
            'font-weight': '600',
            'font-size': '1.05rem',
            'font-family': 'Nunito',
            'text-align': 'center'
          }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f1f5f9'), ('color', '#0f172a'), ('font-weight', '700'), ('font-size', '1.15rem'), ('border-bottom', '2px solid #cbd5e1'), ('text-align', 'center')]},
            {'selector': 'td', 'props': [('color', '#0f172a'), ('border-bottom', '1px solid #e2e8f0'), ('text-align', 'center')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f8fafc')]},
            {'selector': '', 'props': [('border', '1px solid #e2e8f0'), ('border-radius', '12px'), ('margin', '0 auto')]}
          ]))

        st.markdown(styled_df.to_html(), unsafe_allow_html=True)

        # -------------------------
        # Visual Analytics
        # -------------------------
        st.markdown("### 📈 Visual Analytics")
        st.markdown("<br>", unsafe_allow_html=True)

        # First Row - Card Out by Source and Cost Distribution
        viz_row1_col1, viz_row1_col2 = st.columns([1, 1], gap="medium")

        with viz_row1_col1:
            # Card Out by Source & Bank (REPLACEMENT for Applications vs Card Out)
            # Get source-wise card out data from all banks (USE FILTERED DATA FROM all_summaries)
            source_cardout_data = []
            for df in all_summaries:
                if len(df) > 0 and 'Source' in df.columns and 'Bank' in df.columns:
                    bank = df['Bank'].iloc[0]
                    source_stats = df.groupby('Source').agg({'Card Out': 'sum'}).reset_index()
                    source_stats['Bank'] = bank
                    source_cardout_data.append(source_stats)

            # Get top sources by card out and by bank
            if source_cardout_data:
                df_source_cardout = pd.concat(source_cardout_data, ignore_index=True)

                # Get unique banks and sources
                banks = df_source_cardout['Bank'].unique()
                sources = df_source_cardout.groupby('Source')['Card Out'].sum().sort_values(ascending=False).index

                # Create stacked bar chart showing Source breakdown by Bank
                fig_cardout_combined = go.Figure()

                # Define colors for different banks - Circle Health palette
                available_colors = ['#3b82f6', '#0ea5e9', '#fcc038', '#8b5cf6', '#ec4899', '#10b981']
                bank_colors = {bank: available_colors[i % len(available_colors)] for i, bank in enumerate(banks)}

                # Add a trace for each bank
                for bank in banks:
                    bank_data = df_source_cardout[df_source_cardout['Bank'] == bank]
                    bank_source_data = bank_data.set_index('Source').reindex(sources, fill_value=0)

                    fig_cardout_combined.add_trace(go.Bar(
                        name=bank,
                        x=sources,
                        y=bank_source_data['Card Out'],
                        marker_color=bank_colors.get(bank, '#2367AE'),
                        text=[f"<b>{int(v):,}</b>" if v > 0 else "" for v in bank_source_data['Card Out']],
                        textposition='outside',
                        textfont=dict(size=14, color='#0f172a', family='Nunito', weight='bold'),
                        hovertemplate='<b>%{x}</b><br>Bank: ' + bank + '<br>Card Out: %{y:,}<extra></extra>'
                    ))

                # Calculate max value with extra padding for outside text labels
                source_totals = df_source_cardout.groupby('Source')['Card Out'].sum()
                cardout_y_max = source_totals.max() * 1.35

                fig_cardout_combined.update_layout(
                    title=dict(text="<b>Card Out by Source (Bank Breakdown)</b>", font=dict(size=16, color='#0f172a', family='Nunito')),
                    height=380,
                    template=theme_cfg['template'],
                    paper_bgcolor=theme_cfg['bg_color'],
                    plot_bgcolor=theme_cfg['bg_color'],
                    barmode='stack',
                    xaxis=dict(
                        title=dict(text='Source', font=dict(size=13, color='#0f172a', family='Nunito')),
                        gridcolor=theme_cfg['grid_color'],
                        tickfont=dict(size=11, color='#1e293b', family='Nunito'),
                        tickangle=-45
                    ),
                    yaxis=dict(
                        title=dict(text='Card Out', font=dict(size=13, color='#0f172a', family='Nunito')),
                        gridcolor=theme_cfg['grid_color'],
                        tickfont=dict(size=11, color='#1e293b', family='Nunito'),
                        range=[0, cardout_y_max]
                    ),
                    font=dict(color='#0f172a', family='Nunito', size=12),
                    margin=dict(t=50, b=80, l=50, r=20),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=11, color='#0f172a', family='Nunito'),
                        title=dict(text="Bank", font=dict(size=12, color='#0f172a', family='Nunito'))
                    )
                )
                st.plotly_chart(fig_cardout_combined, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})
            else:
                st.warning("Source column not found in campaign data. Please ensure the Source field is included in the identifiers sheet.")

        with viz_row1_col2:
            # --- Cost Distribution by Bank - Circle Health colors ---
            fig_cost = px.pie(
                bank_comparison.sort_values('Total Cost (₹)', ascending=False),
                values='Total Cost (₹)',
                names='Bank',
                title="<b>Cost Distribution by Bank</b>",
                hole=0.4,
                color_discrete_sequence=theme_cfg['chart_colors']
            )
            fig_cost.update_traces(
                textposition='outside',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Cost: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>',
                textfont=dict(size=14, family='Nunito', color='#0f172a'),
                marker=dict(line=dict(color='white', width=2))
            )
            fig_cost.update_layout(
                height=380,
                template=theme_cfg['template'],
                title=dict(text="<b>Cost Distribution</b>", font=dict(size=16, color='#0f172a', family='Nunito')),
                paper_bgcolor=theme_cfg['bg_color'],
                plot_bgcolor=theme_cfg['bg_color'],
                xaxis=dict(gridcolor=theme_cfg['grid_color']),
                yaxis=dict(gridcolor=theme_cfg['grid_color']),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=11, color='#0f172a', family='Nunito')
                ),
                margin=dict(t=50, b=30, l=30, r=120)
            )
            st.plotly_chart(fig_cost, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

        # Second Row - Conversion Funnel and Conversion Rate
        st.markdown("<br>", unsafe_allow_html=True)
        viz_row2_col1, viz_row2_col2 = st.columns([1, 1], gap="medium")

        with viz_row2_col1:
            # --- Conversion Funnel (ORIGINAL - RESTORED) ---
            funnel_data = bank_comparison.melt(
                id_vars='Bank',
                value_vars=['Applications', 'IPA Approved', 'Card Out'],
                var_name='Stage',
                value_name='Count'
            )
            funnel_data['Stage'] = pd.Categorical(
                funnel_data['Stage'],
                categories=['Applications', 'IPA Approved', 'Card Out'],
                ordered=True
            )
            fig_funnel = px.bar(
                funnel_data,
                x='Bank',
                y='Count',
                color='Stage',
                barmode='group',
                text='Count',
                title="<b>Conversion Funnel by Bank</b>",
                color_discrete_sequence=['#3b82f6', '#0ea5e9', '#fcc038']
            )
            fig_funnel.update_traces(
                texttemplate='<b>%{text:,}</b>',
                textposition='outside',
                textfont=dict(size=16, color='#0f172a', family='Nunito', weight='bold')
            )
            # Calculate max value for funnel and add extra padding for outside text labels
            funnel_max = funnel_data['Count'].max()
            funnel_y_max = funnel_max * 1.35

            fig_funnel.update_layout(
                height=380,
                template=theme_cfg['template'],
                font=dict(family='Nunito', color='#0f172a', size=12),
                title=dict(text="<b>Conversion Funnel</b>", font=dict(size=16, color='#0f172a', family='Nunito')),
                paper_bgcolor=theme_cfg['bg_color'],
                plot_bgcolor=theme_cfg['bg_color'],
                xaxis=dict(
                    title=dict(text='Bank', font=dict(size=13, color='#0f172a', family='Nunito')),
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=11, color='#1e293b', family='Nunito')
                ),
                yaxis=dict(
                    title=dict(text='Count', font=dict(size=13, color='#0f172a', family='Nunito')),
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=11, color='#1e293b', family='Nunito'),
                    range=[0, funnel_y_max]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11, color='#0f172a', family='Nunito')
                ),
                margin=dict(t=50, b=30, l=50, r=20)
            )
            st.plotly_chart(fig_funnel, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

        with viz_row2_col2:
            # Conversion Rate Comparison
            bank_comparison['App→Card %'] = (
                (bank_comparison['Card Out'] / bank_comparison['Applications'] * 100)
                .fillna(0)
                .round(1)
            )
            fig_conversion = go.Figure()
            fig_conversion.add_trace(go.Bar(
                x=bank_comparison['Bank'],
                y=bank_comparison['App→Card %'],
                name='App → Card Out %',
                marker_color='#8b5cf6',
                text=[f"<b>{v:.1f}%</b>" for v in bank_comparison['App→Card %']],
                textposition='outside',
                textfont=dict(size=16, color='#0f172a', family='Nunito', weight='bold')
            ))
            # Add extra padding for conversion rate numbers and outside text labels
            conv_max = bank_comparison['App→Card %'].max()
            conv_y_max = conv_max * 1.35

            fig_conversion.update_layout(
                title=dict(text="<b>Conversion Rate</b>", font=dict(size=16, color='#0f172a', family='Nunito')),
                height=380,
                template=theme_cfg['template'],
                paper_bgcolor=theme_cfg['bg_color'],
                plot_bgcolor=theme_cfg['bg_color'],
                xaxis=dict(
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=11, color='#1e293b', family='Nunito')
                ),
                yaxis=dict(
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=11, color='#1e293b', family='Nunito'),
                    range=[0, conv_y_max]
                ),
                showlegend=False,
                font=dict(color='#0f172a', family='Nunito', size=12),
                margin=dict(t=50, b=30, l=50, r=20)
            )
            st.plotly_chart(fig_conversion, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

        # -------------------------
        # Export Section
        # -------------------------
        st.markdown("### 📥 Export Reports")

        # Add date range info to export if filter is active
        export_filename_suffix = datetime.now().strftime('%Y%m%d')
        if date_filter_active:
            export_filename_suffix = f"{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}"

        export_col1, export_col2 = st.columns(2)
        with export_col1:
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                # Export filtered bank comparison
                bank_comparison.to_excel(writer, sheet_name="Bank Comparison", index=False)

                # ====== SOURCE-WISE ANALYSIS ======
                # Create comprehensive source-wise analysis
                source_analysis_data = []

                for bank, data in st.session_state.bank_data.items():
                    df = data['summary'].copy()

                    # Apply date filter
                    if date_filter_active and 'Date' in df.columns:
                        df = df[(df['Date'] >= filter_start) & (df['Date'] <= filter_end)]

                    # Group by source for this bank
                    if 'Source' in df.columns:
                        source_stats = df.groupby('Source').agg({
                            'Applications': 'sum',
                            'IPA Approved': 'sum',
                            'Card Out': 'sum',
                            'Declined': 'sum',
                            'Total cost (₹)': 'sum',
                            'Delivered': 'sum',
                            'Clicks': 'sum'
                        }).reset_index()

                        # Calculate efficiency metrics per source
                        source_stats['Bank'] = bank
                        source_stats['CTR (%)'] = (source_stats['Clicks'] / source_stats['Delivered'] * 100).round(2).fillna(0)
                        source_stats['CPA (₹)'] = (source_stats['Total cost (₹)'] / source_stats['Applications']).round(2).fillna(0)
                        source_stats['Cost per Card Out (₹)'] = (source_stats['Total cost (₹)'] / source_stats['Card Out']).round(2).fillna(0)
                        source_stats['App→IPA (%)'] = (source_stats['IPA Approved'] / source_stats['Applications'] * 100).round(1).fillna(0)
                        source_stats['IPA→Card (%)'] = (source_stats['Card Out'] / source_stats['IPA Approved'] * 100).round(1).fillna(0)
                        source_stats['App→Card (%)'] = (source_stats['Card Out'] / source_stats['Applications'] * 100).round(1).fillna(0)

                        source_analysis_data.append(source_stats)

                # Combine all source analysis data
                if source_analysis_data:
                    df_source_analysis = pd.concat(source_analysis_data, ignore_index=True)

                    # Reorder columns for better readability
                    column_order = [
                        'Bank', 'Source', 'Applications', 'IPA Approved', 'Card Out', 'Declined',
                        'Total cost (₹)', 'CPA (₹)', 'Cost per Card Out (₹)',
                        'CTR (%)', 'App→IPA (%)', 'IPA→Card (%)', 'App→Card (%)',
                        'Delivered', 'Clicks'
                    ]
                    df_source_analysis = df_source_analysis[column_order]

                    # Sort by Bank and then by Card Out descending
                    df_source_analysis = df_source_analysis.sort_values(['Bank', 'Card Out'], ascending=[True, False])

                    # Export source analysis
                    df_source_analysis.to_excel(writer, sheet_name="Source Analysis", index=False)

                    # Create a pivot summary: Sources as rows, Banks as columns, Card Out as values
                    df_source_pivot = df_source_analysis.pivot_table(
                        index='Source',
                        columns='Bank',
                        values='Card Out',
                        aggfunc='sum',
                        fill_value=0
                    ).reset_index()

                    # Add total column
                    df_source_pivot['Total Card Out'] = df_source_pivot.select_dtypes(include='number').sum(axis=1)

                    # Sort by total descending
                    df_source_pivot = df_source_pivot.sort_values('Total Card Out', ascending=False)

                    # NOTE: Source Card Out Matrix and Source Cost Efficiency sheets removed as per user request
                    # The Source Analysis sheet already contains all this information

                # Export filtered data for each bank
                for bank, data in st.session_state.bank_data.items():
                    df = data['summary'].copy()

                    # Apply date filter
                    if date_filter_active and 'Date' in df.columns:
                        df = df[(df['Date'] >= filter_start) & (df['Date'] <= filter_end)]

                    if len(df) > 0:
                        sheet_name = bank.replace(' ', '_')[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            output.seek(0)
            st.download_button(
                "📊 Download Excel Report (Filtered)",
                data=output,
                file_name=f"Multi_Bank_Report_{export_filename_suffix}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Downloads data for the selected date range"
            )
        with export_col2:
            csv_data = bank_comparison.to_csv(index=False)
            st.download_button(
                "📄 Download CSV (Filtered)",
                data=csv_data,
                file_name=f"Multi_Bank_Data_{export_filename_suffix}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Downloads comparison data for the selected date range"
            )

# -------------------------
# Bank Detail Mode
# -------------------------
elif st.session_state.view_mode == 'bank_detail':
    selected_bank = st.session_state.selected_bank_detail
    if selected_bank in st.session_state.bank_data:
        bank_data = st.session_state.bank_data[selected_bank]
        bank_config = bank_data['config']
        # Apply bank-specific styling
        st.markdown(get_custom_css(bank_config), unsafe_allow_html=True)

        # Header
        st.markdown(
            f'<div class="main-header">🏦 {selected_bank} Campaign Analytics</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="sub-header">Detailed Bank Performance Analysis</div>',
            unsafe_allow_html=True
        )

        df_summary = bank_data['summary']
        df_matched_mis = bank_data['matched_mis']
        processor = bank_data['processor']

        # Add Filters Section
        st.markdown("### 🔍 Data Filters")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

        with filter_col1:
            # Date range filter
            if 'Date' in df_summary.columns and len(df_summary) > 0:
                min_date = df_summary['Date'].min().date()
                max_date = df_summary['Date'].max().date()

                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key=f'date_filter_{selected_bank}'
                )
            else:
                date_range = None

        with filter_col2:
            # Source filter
            sources = ['All Sources'] + sorted(df_summary['Source'].unique().tolist())
            selected_source = st.selectbox(
                "Source",
                options=sources,
                key=f'source_filter_{selected_bank}'
            )

        with filter_col3:
            # Channel filter
            channels = ['All Channels'] + sorted(df_summary['Channel'].unique().tolist())
            selected_channel = st.selectbox(
                "Channel",
                options=channels,
                key=f'channel_filter_{selected_bank}'
            )

        with filter_col4:
            # Campaign filter
            campaigns = ['All Campaigns'] + sorted(df_summary['Campaign name'].unique().tolist())
            selected_campaign = st.selectbox(
                "Campaign",
                options=campaigns,
                key=f'campaign_filter_{selected_bank}'
            )

        # Apply filters
        df_filtered = processor.apply_filters(
            df_summary,
            date_range=date_range if date_range and len(date_range) == 2 else None,
            source=selected_source if selected_source != 'All Sources' else None,
            channel=selected_channel if selected_channel != 'All Channels' else None,
            campaign=selected_campaign if selected_campaign != 'All Campaigns' else None
        )

        # Filter matched MIS data based on filtered campaigns
        if len(df_matched_mis) > 0 and 'Matched_Identifier' in df_matched_mis.columns:
            # Get list of campaign identifiers that passed the filter
            filtered_identifiers = df_filtered['Campaign name'].unique().tolist()
            # Filter matched MIS to only include records from filtered campaigns
            df_matched_mis = df_matched_mis[df_matched_mis['Matched_Identifier'].isin(filtered_identifiers)]

        # Show filter info
        if len(df_filtered) < len(df_summary):
            st.info(f"📊 Showing {len(df_filtered)} out of {len(df_summary)} campaigns based on filters | {len(df_matched_mis):,} MIS records")

        st.markdown("---")

        # -------------------------
        # Campaign Comparison Tool
        # -------------------------
        st.markdown("### 🔄 Campaign Comparison Tool")
        st.markdown("Select 2-5 campaigns to compare their performance side-by-side")

        # Campaign selection
        available_campaigns = df_filtered['Campaign name'].unique().tolist()

        if len(available_campaigns) >= 2:
            col_select, col_action = st.columns([3, 1])

            with col_select:
                selected_campaigns = st.multiselect(
                    "Select Campaigns to Compare (2-5)",
                    options=available_campaigns,
                    max_selections=5,
                    key=f'campaign_compare_{selected_bank}',
                    help="Choose between 2 and 5 campaigns for comparison"
                )

            with col_action:
                if selected_campaigns and len(selected_campaigns) >= 2:
                    st.markdown(f"<div style='padding: 0.5rem; background: #d1fae5; border-radius: 8px; text-align: center; margin-top: 1.7rem;'>"
                               f"<span style='color: #065f46; font-weight: 700; font-size: 1.1rem;'>"
                               f"✓ {len(selected_campaigns)} campaigns selected</span></div>",
                               unsafe_allow_html=True)
                elif selected_campaigns and len(selected_campaigns) == 1:
                    st.warning("⚠️ Select at least one more")

            # Show comparison if valid selection
            if selected_campaigns and len(selected_campaigns) >= 2:
                st.markdown("---")

                # Filter data for selected campaigns
                df_comparison = df_filtered[df_filtered['Campaign name'].isin(selected_campaigns)].copy()

                # -------------------------
                # Comparison Metrics Table
                # -------------------------
                st.markdown("#### 📊 Performance Comparison")

                # Select key columns for comparison
                comparison_cols = [
                    'Campaign name', 'Source', 'Channel', 'Applications',
                    'IPA Approved', 'Card Out', 'Declined',
                    'Total cost (₹)', 'Cost per App (₹)',
                    'CTR (%)', 'App→IPA (%)', 'IPA→Card (%)'
                ]

                # Create comparison dataframe
                df_comp_display = df_comparison[comparison_cols].copy()

                # Add performance indicators
                df_comp_display['Card Out Rank'] = df_comp_display['Card Out'].rank(ascending=False).astype(int)
                df_comp_display['CPA Rank'] = df_comp_display['Cost per App (₹)'].rank(ascending=True).astype(int)

                # Calculate efficiency score (normalized)
                max_cardout = df_comp_display['Card Out'].max()
                min_cpa = df_comp_display['Cost per App (₹)'].min()

                if max_cardout > 0 and min_cpa > 0:
                    df_comp_display['Efficiency Score'] = (
                        (df_comp_display['Card Out'] / max_cardout * 50) +
                        (min_cpa / df_comp_display['Cost per App (₹)'] * 50)
                    ).round(1)
                else:
                    df_comp_display['Efficiency Score'] = 0

                # Style the comparison table
                def highlight_best_worst(s):
                    if s.name in ['Card Out', 'Applications', 'IPA Approved', 'CTR (%)', 'App→IPA (%)', 'IPA→Card (%)', 'Efficiency Score']:
                        is_max = s == s.max()
                        return ['background-color: #d1fae5; font-weight: 700;' if v else '' for v in is_max]
                    elif s.name in ['Cost per App (₹)', 'Total cost (₹)', 'Declined']:
                        is_min = s == s.min()
                        return ['background-color: #dbeafe; font-weight: 700;' if v else '' for v in is_min]
                    return ['' for _ in s]

                styled_comparison = (df_comp_display.style
                    .apply(highlight_best_worst, subset=['Card Out', 'Applications', 'IPA Approved',
                                                         'Total cost (₹)', 'Cost per App (₹)',
                                                         'CTR (%)', 'App→IPA (%)', 'IPA→Card (%)',
                                                         'Declined', 'Efficiency Score'])
                    .format({
                        'Applications': '{:,.0f}',
                        'IPA Approved': '{:,.0f}',
                        'Card Out': '{:,.0f}',
                        'Declined': '{:,.0f}',
                        'Total cost (₹)': '₹{:,.2f}',
                        'Cost per App (₹)': '₹{:.2f}',
                        'CTR (%)': '{:.2f}%',
                        'App→IPA (%)': '{:.1f}%',
                        'IPA→Card (%)': '{:.1f}%',
                        'Efficiency Score': '{:.1f}'
                    })
                    .set_properties(**{
                        'color': '#0f172a',
                        'background-color': 'white',
                        'font-weight': '600',
                        'font-size': '0.95rem',
                        'font-family': 'Nunito',
                        'text-align': 'center'
                    })
                    .set_table_styles([
                        {'selector': 'th', 'props': [
                            ('background-color', '#f1f5f9'),
                            ('color', '#0f172a'),
                            ('font-weight', '700'),
                            ('font-size', '1rem'),
                            ('border-bottom', '2px solid #cbd5e1'),
                            ('text-align', 'center'),
                            ('padding', '8px')
                        ]},
                        {'selector': 'td', 'props': [
                            ('color', '#0f172a'),
                            ('border-bottom', '1px solid #e2e8f0'),
                            ('text-align', 'center'),
                            ('padding', '8px')
                        ]},
                        {'selector': 'tr:hover', 'props': [('background-color', '#f8fafc')]},
                        {'selector': '', 'props': [
                            ('border', '1px solid #e2e8f0'),
                            ('border-radius', '12px'),
                            ('overflow', 'hidden')
                        ]}
                    ])
                )

                st.markdown(styled_comparison.to_html(), unsafe_allow_html=True)

                # Legend for highlighting
                st.markdown("""
                    <div style='display: flex; gap: 1.5rem; justify-content: center; margin: 1rem 0; padding: 0.75rem; background: #f8fafc; border-radius: 8px;'>
                        <span style='color: #0f172a; font-weight: 600;'>
                            <span style='background: #d1fae5; padding: 0.25rem 0.5rem; border-radius: 4px;'>Green</span> = Best Performance
                        </span>
                        <span style='color: #0f172a; font-weight: 600;'>
                            <span style='background: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 4px;'>Blue</span> = Best Value (Lowest Cost)
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                # -------------------------
                # Comparison Visualizations
                # -------------------------
                st.markdown("#### 📈 Visual Comparison")

                viz_col1, viz_col2 = st.columns(2)

                with viz_col1:
                    # Bar chart comparison - Key Metrics
                    metrics_data = df_comparison[['Campaign name', 'Applications', 'IPA Approved', 'Card Out']].copy()
                    metrics_melted = metrics_data.melt(
                        id_vars='Campaign name',
                        var_name='Metric',
                        value_name='Count'
                    )

                    fig_bar = px.bar(
                        metrics_melted,
                        x='Campaign name',
                        y='Count',
                        color='Metric',
                        barmode='group',
                        title="<b>Applications vs Card Out Comparison</b>",
                        color_discrete_sequence=['#3b82f6', '#0ea5e9', '#fcc038']
                    )

                    fig_bar.update_traces(
                        texttemplate='%{y:,.0f}',
                        textposition='outside',
                        textfont=dict(size=12, color='#0f172a', family='Nunito', weight='bold')
                    )

                    # Calculate max for proper spacing
                    bar_max = metrics_melted['Count'].max()
                    bar_y_max = bar_max * 1.25

                    fig_bar.update_layout(
                        height=400,
                        template=theme_cfg['template'],
                        paper_bgcolor=theme_cfg['bg_color'],
                        plot_bgcolor=theme_cfg['bg_color'],
                        font=dict(color='#0f172a', family='Nunito', size=11),
                        title=dict(font=dict(size=14, color='#0f172a', family='Nunito')),
                        xaxis=dict(
                            tickangle=-45,
                            tickfont=dict(size=10, color='#1e293b', family='Nunito')
                        ),
                        yaxis=dict(
                            tickfont=dict(size=10, color='#1e293b', family='Nunito'),
                            range=[0, bar_y_max]
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            font=dict(size=10, color='#0f172a', family='Nunito')
                        ),
                        margin=dict(t=60, b=100, l=50, r=20)
                    )

                    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

                with viz_col2:
                    # Efficiency Comparison - Cost vs Performance
                    fig_scatter = go.Figure()

                    fig_scatter.add_trace(go.Scatter(
                        x=df_comparison['Cost per App (₹)'],
                        y=df_comparison['Card Out'],
                        mode='markers+text',
                        marker=dict(
                            size=df_comparison['Applications'] / df_comparison['Applications'].max() * 50 + 20,
                            color=df_comparison['CTR (%)'],
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="CTR %", titlefont=dict(size=10)),
                            line=dict(width=2, color='white')
                        ),
                        text=df_comparison['Campaign name'].str[:15],
                        textposition='top center',
                        textfont=dict(size=10, color='#0f172a', family='Nunito', weight='bold'),
                        hovertemplate='<b>%{text}</b><br>CPA: ₹%{x:.2f}<br>Card Out: %{y:,.0f}<extra></extra>'
                    ))

                    fig_scatter.update_layout(
                        title=dict(
                            text="<b>Cost Efficiency Analysis</b><br><sub>Bubble size = Applications | Color = CTR%</sub>",
                            font=dict(size=14, color='#0f172a', family='Nunito')
                        ),
                        height=400,
                        template=theme_cfg['template'],
                        paper_bgcolor=theme_cfg['bg_color'],
                        plot_bgcolor=theme_cfg['bg_color'],
                        xaxis=dict(
                            title=dict(text='Cost per App (₹)', font=dict(size=11, color='#0f172a')),
                            gridcolor='#e2e8f0',
                            tickfont=dict(size=10, color='#1e293b')
                        ),
                        yaxis=dict(
                            title=dict(text='Card Out', font=dict(size=11, color='#0f172a')),
                            gridcolor='#e2e8f0',
                            tickfont=dict(size=10, color='#1e293b')
                        ),
                        font=dict(color='#0f172a', family='Nunito'),
                        margin=dict(t=80, b=50, l=60, r=20)
                    )

                    st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

                # -------------------------
                # Radar Chart - Multi-dimensional Comparison
                # -------------------------
                st.markdown("#### 🎯 Multi-Dimensional Performance Radar")

                # Prepare data for radar chart (normalize to 0-100 scale)
                radar_metrics = ['Applications', 'Card Out', 'CTR (%)', 'App→IPA (%)', 'IPA→Card (%)']

                fig_radar = go.Figure()

                # Color palette for campaigns
                campaign_colors = ['#3b82f6', '#0ea5e9', '#fcc038', '#8b5cf6', '#ec4899']

                for idx, campaign in enumerate(selected_campaigns):
                    campaign_data = df_comparison[df_comparison['Campaign name'] == campaign].iloc[0]

                    # Normalize values to 0-100 scale for better visualization
                    normalized_values = []
                    for metric in radar_metrics:
                        max_val = df_comparison[metric].max()
                        if max_val > 0:
                            normalized_values.append((campaign_data[metric] / max_val) * 100)
                        else:
                            normalized_values.append(0)

                    # Add campaign name to close the radar
                    normalized_values.append(normalized_values[0])

                    fig_radar.add_trace(go.Scatterpolar(
                        r=normalized_values,
                        theta=radar_metrics + [radar_metrics[0]],
                        fill='toself',
                        name=campaign[:25],
                        line=dict(color=campaign_colors[idx % len(campaign_colors)], width=2),
                        fillcolor=campaign_colors[idx % len(campaign_colors)],
                        opacity=0.3,
                        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>'
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            tickfont=dict(size=10, color='#1e293b'),
                            gridcolor='#e2e8f0'
                        ),
                        angularaxis=dict(
                            tickfont=dict(size=11, color='#0f172a', family='Nunito', weight='bold'),
                            gridcolor='#e2e8f0'
                        ),
                        bgcolor=theme_cfg['bg_color']
                    ),
                    height=450,
                    template=theme_cfg['template'],
                    paper_bgcolor=theme_cfg['bg_color'],
                    font=dict(color='#0f172a', family='Nunito'),
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.1,
                        font=dict(size=10, color='#0f172a', family='Nunito')
                    ),
                    margin=dict(t=20, b=20, l=80, r=150)
                )

                st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

                # -------------------------
                # Key Insights
                # -------------------------
                st.markdown("#### 💡 Key Insights")

                insight_col1, insight_col2, insight_col3 = st.columns(3)

                with insight_col1:
                    best_cardout = df_comparison.loc[df_comparison['Card Out'].idxmax()]
                    st.markdown(f"""
                        <div style='background: #d1fae5; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;'>
                            <p style='color: #065f46; font-weight: 700; font-size: 1rem; margin: 0;'>🏆 Best Card Out</p>
                            <p style='color: #047857; font-size: 0.9rem; margin: 0.5rem 0 0 0; font-weight: 600;'>
                                {best_cardout['Campaign name'][:30]}<br>
                                <span style='font-size: 1.2rem;'>{int(best_cardout['Card Out']):,}</span> cards
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                with insight_col2:
                    best_cpa = df_comparison.loc[df_comparison['Cost per App (₹)'].idxmin()]
                    st.markdown(f"""
                        <div style='background: #dbeafe; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;'>
                            <p style='color: #1e40af; font-weight: 700; font-size: 1rem; margin: 0;'>💰 Best CPA</p>
                            <p style='color: #1e3a8a; font-size: 0.9rem; margin: 0.5rem 0 0 0; font-weight: 600;'>
                                {best_cpa['Campaign name'][:30]}<br>
                                <span style='font-size: 1.2rem;'>₹{best_cpa['Cost per App (₹)']:.2f}</span> per app
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                with insight_col3:
                    best_conversion = df_comparison.loc[df_comparison['App→IPA (%)'].idxmax()]
                    st.markdown(f"""
                        <div style='background: #fef3c7; padding: 1rem; border-radius: 8px; border-left: 4px solid #fcc038;'>
                            <p style='color: #92400e; font-weight: 700; font-size: 1rem; margin: 0;'>🎯 Best Conversion</p>
                            <p style='color: #78350f; font-size: 0.9rem; margin: 0.5rem 0 0 0; font-weight: 600;'>
                                {best_conversion['Campaign name'][:30]}<br>
                                <span style='font-size: 1.2rem;'>{best_conversion['App→IPA (%)']:.1f}%</span> App→IPA
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

        else:
            st.info("ℹ️ Not enough campaigns to compare. Apply different filters to see more campaigns.")

        st.markdown("---")

        # Get statistics from filtered data
        stats = processor.get_summary_statistics(df_filtered)

        # Use filtered data for all displays
        df_summary = df_filtered

        # Key Metrics
        st.markdown("### 📊 Overall Performance Summary")
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
        with metric_col1:
            st.metric(
                "Total Applications",
                f"{stats['total_apps']:,}",
                help="Total number of applications received"
            )
        with metric_col2:
            st.metric(
                "IPA Approved",
                f"{stats['total_ipa_approved']:,}",
                delta=f"{stats['app_to_ipa_rate']:.1f}% of apps",
                help="In-Principle Approved applications"
            )
        with metric_col3:
            st.metric(
                "Card Out",
                f"{stats['total_card_out']:,}",
                delta=f"{stats['ipa_to_card_rate']:.1f}% of IPA",
                help="Successfully issued cards"
            )
        with metric_col4:
            st.metric(
                "Declined",
                f"{stats['total_declined']:,}",
                delta=f"{(stats['total_declined']/stats['total_apps']*100):.1f}% of apps" if stats['total_apps'] > 0 else "0%",
                delta_color="inverse",
                help="Declined applications"
            )
        with metric_col5:
            st.metric(
                "Total Investment",
                f"₹{stats['total_cost']:,.0f}",
                help="Total campaign cost"
            )

        # Additional Metrics Row
        st.markdown("---")
        metric_col6, metric_col7, metric_col8, metric_col9, metric_col10 = st.columns(5)
        with metric_col6:
            st.metric(
                "Avg Cost per App",
                f"₹{stats['avg_cpa']:.2f}",
                help="Average cost per application"
            )
        with metric_col7:
            st.metric(
                "Avg CTR",
                f"{stats['avg_ctr']:.2f}%",
                help="Average click-through rate"
            )
        with metric_col8:
            st.metric(
                "App → IPA Rate",
                f"{stats['app_to_ipa_rate']:.1f}%",
                help="Application to IPA approval rate"
            )
        with metric_col9:
            st.metric(
                "IPA → Card Rate",
                f"{stats['ipa_to_card_rate']:.1f}%",
                help="IPA approval to card issuance rate"
            )
        with metric_col10:
            st.metric(
                "Total Campaigns",
                f"{stats['num_campaigns']:,}",
                help="Number of campaigns analyzed"
            )

        # Channel Performance Analysis
        st.markdown("### 📡 Channel-Wise Performance")
        # Group by channel
        channel_analysis = df_summary.groupby('Channel').agg({
            'Applications': 'sum',
            'IPA Approved': 'sum',
            'Card Out': 'sum',
            'Declined': 'sum',
            'Total cost (₹)': 'sum',
            'Delivered': 'sum',
            'Clicks': 'sum'
        }).reset_index()

        # Calculate channel metrics
        channel_analysis['CTR (%)'] = (channel_analysis['Clicks'] / channel_analysis['Delivered'] * 100).round(2)
        channel_analysis['Cost per App (₹)'] = (channel_analysis['Total cost (₹)'] / channel_analysis['Applications']).round(2)
        channel_analysis['App→IPA (%)'] = (channel_analysis['IPA Approved'] / channel_analysis['Applications'] * 100).round(1)
        channel_analysis['IPA→Card (%)'] = (channel_analysis['Card Out'] / channel_analysis['IPA Approved'] * 100).round(1)

        # Display channel table
        styled_channel = (channel_analysis.style.format({
            'Applications': '{:,.0f}',
            'IPA Approved': '{:,.0f}',
            'Card Out': '{:,.0f}',
            'Declined': '{:,.0f}',
            'Total cost (₹)': '₹{:,.2f}',
            'Delivered': '{:,.0f}',
            'Clicks': '{:,.0f}',
            'CTR (%)': '{:.2f}%',
            'Cost per App (₹)': '₹{:.2f}',
            'App→IPA (%)': '{:.1f}%',
            'IPA→Card (%)': '{:.1f}%'
        }).background_gradient(subset=['Applications'], cmap='Blues')
          .background_gradient(subset=['Card Out'], cmap='Greens')
          .background_gradient(subset=['Total cost (₹)'], cmap='Reds', high=0.8)
          .background_gradient(subset=['CTR (%)'], cmap='PiYG', low=0.2, high=0.8)
          .set_properties(**{
            'color': '#0f172a',
            'background-color': 'white',
            'font-weight': '600',
            'font-size': '1.05rem',
            'font-family': 'Nunito'
          }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f1f5f9'), ('color', '#0f172a'), ('font-weight', '700'), ('font-size', '1.15rem'), ('border-bottom', '2px solid #cbd5e1')]},
            {'selector': 'td', 'props': [('color', '#0f172a'), ('border-bottom', '1px solid #e2e8f0')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f8fafc')]},
            {'selector': '', 'props': [('border', '1px solid #e2e8f0'), ('border-radius', '12px')]}
          ]))

        st.markdown(styled_channel.to_html(), unsafe_allow_html=True)

        # Visual Analytics - Channel Funnel
        st.markdown("### 📈 Channel-Wise Conversion Funnel")
        funnel_data = channel_analysis.melt(
            id_vars='Channel',
            value_vars=['Applications', 'IPA Approved', 'Card Out'],
            var_name='Stage',
            value_name='Count'
        )
        funnel_data['Stage'] = pd.Categorical(
            funnel_data['Stage'],
            categories=['Applications', 'IPA Approved', 'Card Out'],
            ordered=True
        )

        fig_channel_funnel = px.bar(
            funnel_data,
            x='Channel',
            y='Count',
            color='Stage',
            barmode='group',
            text='Count',
            title=f"<b>{selected_bank} Conversion Funnel by Channel</b>",
            color_discrete_sequence=['#3b82f6', '#0ea5e9', '#fcc038']
        )

        # Calculate max for channel funnel and add extra padding for outside text labels
        channel_funnel_max = funnel_data['Count'].max()
        channel_y_max = channel_funnel_max * 1.35

        fig_channel_funnel.update_traces(
            texttemplate='<b>%{text:,}</b>',
            textposition='outside',
            textfont=dict(size=16, color='#0f172a', family='Nunito', weight='bold')
        )
        fig_channel_funnel.update_layout(
            height=300,
            template='plotly_white',
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#0f172a', family='Nunito', size=12),
            title=dict(font=dict(size=16, color='#0f172a', family='Nunito')),
            xaxis=dict(
                tickfont=dict(size=11, color='#1e293b', family='Nunito'),
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                tickfont=dict(size=11, color='#1e293b', family='Nunito'),
                gridcolor='#e2e8f0',
                range=[0, channel_y_max]
            ),
            legend=dict(font=dict(size=11, color='#0f172a', family='Nunito')),
            margin=dict(t=40, b=30, l=40, r=15)
        )
        st.plotly_chart(fig_channel_funnel, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

        # Campaign List Table
        st.markdown("### 📑 All Campaigns")
        df_display = df_summary.copy()
        
        # Format columns for display
        df_display = df_display.rename(columns={
            'Total cost (₹)': 'Cost (₹)',
            'Cost per App (₹)': 'CPA (₹)',
            'App→IPA (%)': 'App→IPA %',
            'IPA→Card (%)': 'IPA→Card %'
        })
        
        # Sort by Applications descending by default
        df_display = df_display.sort_values(by='Applications', ascending=False)
        
        # Display the table
        styled_campaigns = df_display.style.format({
            'Applications': '{:,.0f}',
            'IPA Approved': '{:,.0f}',
            'Card Out': '{:,.0f}',
            'Declined': '{:,.0f}',
            'Cost (₹)': '₹{:,.2f}',
            'Delivered': '{:,.0f}',
            'Clicks': '{:,.0f}',
            'CTR (%)': '{:.2f}%',
            'CPA (₹)': '₹{:.2f}',
            'App→IPA %': '{:.1f}%',
            'IPA→Card %': '{:.1f}%'
        }).set_properties(**{
            'color': '#0f172a',
            'background-color': 'white',
            'font-weight': '600',
            'font-size': '1.05rem',
            'font-family': 'Nunito'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f1f5f9'), ('color', '#0f172a'), ('font-weight', '700'), ('font-size', '1.15rem'), ('border-bottom', '2px solid #cbd5e1')]},
            {'selector': 'td', 'props': [('color', '#0f172a'), ('border-bottom', '1px solid #e2e8f0')]},
            {'selector': 'tr:hover', 'props': [('background-color', '#f8fafc')]},
            {'selector': '', 'props': [('border', '1px solid #e2e8f0'), ('border-radius', '12px'), ('max-height', '400px'), ('overflow-y', 'auto')]}
        ])

        st.markdown(f'<div style="max-height: 400px; overflow-y: auto;">{styled_campaigns.to_html()}</div>', unsafe_allow_html=True)

        # Export options for detail view
        st.markdown("### 📥 Export Campaign Data")

        # Determine if filters are active and build filter description
        filter_descriptions = []
        filters_active = False

        if date_range and len(date_range) == 2:
            start_d, end_d = date_range
            if start_d != bank_data['summary']['Date'].min().date() or end_d != bank_data['summary']['Date'].max().date():
                filter_descriptions.append(f"Date: {start_d.strftime('%d-%m-%Y')} to {end_d.strftime('%d-%m-%Y')}")
                filters_active = True

        if selected_source != 'All Sources':
            filter_descriptions.append(f"Source: {selected_source}")
            filters_active = True

        if selected_channel != 'All Channels':
            filter_descriptions.append(f"Channel: {selected_channel}")
            filters_active = True

        if selected_campaign != 'All Campaigns':
            filter_descriptions.append(f"Campaign: {selected_campaign}")
            filters_active = True

        # Show filter info in export section
        if filters_active:
            st.info(f"📋 Active Filters: {' | '.join(filter_descriptions)}")

        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            # Excel export - with filtered data
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_summary.to_excel(writer, sheet_name="Campaign Summary", index=False)
                df_matched_mis.to_excel(writer, sheet_name="Matched MIS Data", index=False)

                # ====== SOURCE-WISE ANALYSIS FOR INDIVIDUAL BANK ======
                if 'Source' in df_summary.columns and len(df_summary) > 0:
                    # Group by source
                    source_stats = df_summary.groupby('Source').agg({
                        'Applications': 'sum',
                        'IPA Approved': 'sum',
                        'Card Out': 'sum',
                        'Declined': 'sum',
                        'Total cost (₹)': 'sum',
                        'Delivered': 'sum',
                        'Clicks': 'sum'
                    }).reset_index()

                    # Calculate efficiency metrics per source
                    source_stats['CTR (%)'] = (source_stats['Clicks'] / source_stats['Delivered'] * 100).round(2).fillna(0)
                    source_stats['CPA (₹)'] = (source_stats['Total cost (₹)'] / source_stats['Applications']).round(2).fillna(0)
                    source_stats['Cost per Card Out (₹)'] = (source_stats['Total cost (₹)'] / source_stats['Card Out']).round(2).fillna(0)
                    source_stats['App→IPA (%)'] = (source_stats['IPA Approved'] / source_stats['Applications'] * 100).round(1).fillna(0)
                    source_stats['IPA→Card (%)'] = (source_stats['Card Out'] / source_stats['IPA Approved'] * 100).round(1).fillna(0)
                    source_stats['App→Card (%)'] = (source_stats['Card Out'] / source_stats['Applications'] * 100).round(1).fillna(0)

                    # Calculate cost share
                    total_cost = source_stats['Total cost (₹)'].sum()
                    source_stats['Cost Share (%)'] = (source_stats['Total cost (₹)'] / total_cost * 100).round(2) if total_cost > 0 else 0

                    # Sort by Card Out descending
                    source_stats = source_stats.sort_values('Card Out', ascending=False)

                    # Export source analysis
                    source_stats.to_excel(writer, sheet_name="Source Analysis", index=False)

            output.seek(0)

            # Create filename with filter indication
            file_suffix = "Filtered" if filters_active else datetime.now().strftime('%Y%m%d')

            st.download_button(
                "📊 Download Excel Report (Filtered)" if filters_active else "📊 Download Excel Report",
                data=output,
                file_name=f"{selected_bank.replace(' ', '_')}_Report_{file_suffix}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help=f"Downloads {len(df_summary)} campaigns and {len(df_matched_mis)} MIS records based on current filters"
            )

        with export_col2:
            # CSV export - Summary (filtered)
            csv_data = df_summary.to_csv(index=False)
            st.download_button(
                "📄 Download Campaign Summary (Filtered)" if filters_active else "📄 Download Campaign Summary",
                data=csv_data,
                file_name=f"{selected_bank.replace(' ', '_')}_Campaigns_{'Filtered' if filters_active else datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                help=f"Downloads {len(df_summary)} filtered campaigns"
            )


        with export_col3:
            # CSV export - Matched MIS (filtered)
            if len(df_matched_mis) > 0:
                mis_csv_data = df_matched_mis.to_csv(index=False)
                st.download_button(
                    "📄 Download Matched MIS (Filtered)" if filters_active else "📄 Download Matched MIS",
                    data=mis_csv_data,
                    file_name=f"{selected_bank.replace(' ', '_')}_MIS_{'Filtered' if filters_active else datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help=f"Downloads {len(df_matched_mis)} filtered MIS records"
                )
            else:
                st.info("No matched MIS records")


    else:
        st.error(f"No data available for {selected_bank}")


# Footer - Circle Health inspired
st.markdown("""
    <div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); border-top: 1px solid #cbd5e1; margin-top: 1.5rem;'>
        <p style='color: #334155; font-size: 1rem; font-weight: 600; margin: 0; font-family: Nunito;'>
            Powered by extrape advisor | Data last updated: {timestamp}
        </p>
    </div>
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)