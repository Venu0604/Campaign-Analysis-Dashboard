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
               type=["xlsx", "xls", "xlsb"],
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
                                       df_identifiers['Date'] = pd.to_datetime(df_identifiers['Date'], format='%d/%m/%Y', errors='coerce')

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
   """Detect Streamlit theme (dark/light) and return corresponding Plotly settings"""
   theme = st.get_option("theme.base") or "dark"


   if theme == "light":
       return {
           "template": "plotly_white",
           "bg_color": "rgba(255,255,255,1)",
           "font_color": "#0F172A",  # dark navy text
           "grid_color": "#E2E8F0"
       }
   else:
       return {
           "template": "plotly_dark",
           "bg_color": "rgba(15,23,42,0)",
           "font_color": "#E2E8F0",  # light text
           "grid_color": "#334155"
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


    # Show loaded banks count
    if st.session_state.bank_data:
        st.markdown(f"""
            <div style='background: #1E293B; padding: 0.5rem 0.75rem; border-radius: 6px; margin: 0.25rem 0; border: 1px solid #475569;'>
                <p style='color: #CBD5E1; font-size: 0.85rem; margin: 0; text-align: center; font-weight: 600;'>
                    📊 Analyzing {len(st.session_state.bank_data)} Bank{'s' if len(st.session_state.bank_data) > 1 else ''}: {', '.join(st.session_state.bank_data.keys())}
                </p>
            </div>
        """, unsafe_allow_html=True)


    if not st.session_state.bank_data:
        # Clean minimalist welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Welcome message
            st.markdown("""
                <div style='text-align: center; padding: 1rem 0 0.5rem 0;'>
                    <h2 style='color: #FFFFFF; font-weight: 800;
    font-size: 2rem; margin-bottom: 0.5rem; text-shadow: 0 2px 6px rgba(0,0,0,0.4);'>
                        Welcome to Campaign Analytics
                    </h2>
                    <p style='color: #E2E8F0;
    font-size: 1.05rem; line-height: 1.5; font-weight: 500;'>
                        Upload MIS files in the sidebar to begin analysis
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Features section - using Streamlit native components
            st.markdown("""
                <div style='background: #1E293B; border-radius: 8px; padding: 1.25rem; border: 1px solid #475569; margin-top: 0.75rem;'>
                    <p style='color: #FFFFFF; font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem; text-align: center; text-shadow: 0 1px 3px rgba(0,0,0,0.3);'>
                        Key Capabilities
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Feature list with minimal styling
            features = [
                "Multi-Bank Consolidated View",
                "Real-Time Performance Metrics",
                "Interactive Visual Analytics",
                "Individual Bank Deep Dive",
                "Comprehensive Export Options"
            ]

            for feature in features:
                st.markdown(f"""
                    <div style='padding: 0.4rem 0;
    color: #F1F5F9;'>
                        <span style='color: #22D3EE;
    margin-right: 0.5rem; font-weight: 700;'>●</span>
                        <span style='font-size: 1rem; font-weight: 500;'>{feature}</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        # Aggregate data from all banks
        all_summaries = []
        bank_wise_stats = []

        for bank, data in st.session_state.bank_data.items():
            df = data['summary'].copy()
            df['Bank'] = bank
            all_summaries.append(df)

            # Calculate bank-wise stats
            stats = data['processor'].get_summary_statistics(df)
            stats['Bank'] = bank
            bank_wise_stats.append(stats)

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
        st.dataframe(
            bank_comparison.style.format({
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
            .background_gradient(subset=['Total Cost (₹)'], cmap='Reds'),
            width='stretch',
            height=250
        )

        # -------------------------
        # Visual Analytics
        # -------------------------
        st.markdown("### 📈 Visual Analytics")
        st.markdown("<br>", unsafe_allow_html=True)

        # First Row - Card Out by Source and Cost Distribution
        viz_row1_col1, viz_row1_col2 = st.columns([1, 1], gap="medium")

        with viz_row1_col1:
            # Card Out by Source & Bank (REPLACEMENT for Applications vs Card Out)
            # Get source-wise card out data from all banks
            source_cardout_data = []
            for bank, data in st.session_state.bank_data.items():
                df = data['summary']
                # Check if Source column exists in the summary
                if 'Source' in df.columns:
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

                # Define colors for different banks
                available_colors = ['#2367AE', '#00C389', '#FFCD56', '#00A3E0', '#7B68EE', '#FF6B9D']
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
                        textposition='inside',
                        textfont=dict(size=11, color='#FFFFFF', family='Poppins'),
                        hovertemplate='<b>%{x}</b><br>Bank: ' + bank + '<br>Card Out: %{y:,}<extra></extra>'
                    ))

                # Calculate max value
                source_totals = df_source_cardout.groupby('Source')['Card Out'].sum()
                cardout_y_max = source_totals.max() * 1.15

                fig_cardout_combined.update_layout(
                    title=dict(text="<b>Card Out by Source (Bank Breakdown)</b>", font=dict(size=14, color='#FFFFFF')),
                    height=380,
                    template=theme_cfg['template'],
                    paper_bgcolor=theme_cfg['bg_color'],
                    plot_bgcolor=theme_cfg['bg_color'],
                    barmode='stack',
                    xaxis=dict(
                        title='Source',
                        gridcolor=theme_cfg['grid_color'],
                        tickfont=dict(size=9, color='#FFFFFF'),
                        tickangle=-45
                    ),
                    yaxis=dict(
                        title='Card Out',
                        gridcolor=theme_cfg['grid_color'],
                        tickfont=dict(size=10, color='#FFFFFF'),
                        range=[0, cardout_y_max]
                    ),
                    font=dict(color='#FFFFFF'),
                    margin=dict(t=50, b=80, l=50, r=20),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=10, color='#FFFFFF'),
                        title=dict(text="Bank", font=dict(size=10, color='#FFFFFF'))
                    )
                )
                st.plotly_chart(fig_cardout_combined, use_container_width=True)
            else:
                st.warning("Source column not found in campaign data. Please ensure the Source field is included in the identifiers sheet.")

        with viz_row1_col2:
            # --- Cost Distribution by Bank (ORIGINAL - RESTORED) ---
            fig_cost = px.pie(
                bank_comparison.sort_values('Total Cost (₹)', ascending=False),
                values='Total Cost (₹)',
                names='Bank',
                title="<b>Cost Distribution by Bank</b>",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_cost.update_traces(
                textposition='outside',
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Cost: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>',
                textfont=dict(size=14, family='Poppins', color=theme_cfg['font_color']),
                marker=dict(line=dict(color=theme_cfg['bg_color'], width=2))
            )
            fig_cost.update_layout(
                height=380,
                template=theme_cfg['template'],
                title=dict(text="<b>Cost Distribution</b>", font=dict(size=14, color='#FFFFFF')),
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
                    font=dict(size=10, color='#FFFFFF')
                ),
                margin=dict(t=50, b=30, l=30, r=120)
            )
            fig_cost.update_traces(
                textfont=dict(size=16, family='Poppins', color='#FFFFFF')
            )
            st.plotly_chart(fig_cost, use_container_width=True)

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
                color_discrete_sequence=['#2367AE', '#00A3E0', '#FFCD56']
            )
            fig_funnel.update_traces(
                texttemplate='<b>%{text:,}</b>',
                textposition='outside',
                textfont=dict(size=18, color='#FFFFFF', family='Poppins')
            )
            # Calculate max value for funnel and add padding
            funnel_max = funnel_data['Count'].max()
            funnel_y_max = funnel_max * 1.25

            fig_funnel.update_layout(
                height=380,
                template=theme_cfg['template'],
                font=dict(family='Poppins', color='#FFFFFF', size=10),
                title=dict(text="<b>Conversion Funnel</b>", font=dict(size=14, color='#FFFFFF')),
                paper_bgcolor=theme_cfg['bg_color'],
                plot_bgcolor=theme_cfg['bg_color'],
                xaxis=dict(
                    title='Bank',
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=10, color='#FFFFFF')
                ),
                yaxis=dict(
                    title='Count',
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=10, color='#FFFFFF'),
                    range=[0, funnel_y_max]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=10, color='#FFFFFF')
                ),
                margin=dict(t=50, b=30, l=50, r=20)
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

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
                marker_color='#7B68EE',
                text=[f"<b>{v:.1f}%</b>" for v in bank_comparison['App→Card %']],
                textposition='outside',
                textfont=dict(size=18, color='#FFFFFF', family='Poppins')
            ))
            # Add padding for conversion rate numbers
            conv_max = bank_comparison['App→Card %'].max()
            conv_y_max = conv_max * 1.25

            fig_conversion.update_layout(
                title=dict(text="<b>Conversion Rate</b>", font=dict(size=14, color='#FFFFFF')),
                height=380,
                template=theme_cfg['template'],
                paper_bgcolor=theme_cfg['bg_color'],
                plot_bgcolor=theme_cfg['bg_color'],
                xaxis=dict(gridcolor=theme_cfg['grid_color'], tickfont=dict(size=10, color='#FFFFFF')),
                yaxis=dict(
                    gridcolor=theme_cfg['grid_color'],
                    tickfont=dict(size=10, color='#FFFFFF'),
                    range=[0, conv_y_max]
                ),
                showlegend=False,
                font=dict(color='#FFFFFF'),
                margin=dict(t=50, b=30, l=50, r=20)
            )
            st.plotly_chart(fig_conversion, use_container_width=True)

        # -------------------------
        # Export Section
        # -------------------------
        st.markdown("### 📥 Export Reports")
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                bank_comparison.to_excel(writer, sheet_name="Bank Comparison", index=False)
                for bank, data in st.session_state.bank_data.items():
                    sheet_name = bank.replace(' ', '_')[:31]
                    data['summary'].to_excel(writer, sheet_name=sheet_name, index=False)
            output.seek(0)
            st.download_button(
                "📊 Download Excel Report",
                data=output,
                file_name=f"Multi_Bank_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )
        with export_col2:
            csv_data = bank_comparison.to_csv(index=False)
            st.download_button(
                "📄 Download CSV",
                data=csv_data,
                file_name=f"Multi_Bank_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
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

        # Get statistics
        stats = processor.get_summary_statistics(df_summary)

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
        st.dataframe(
            channel_analysis.style.format({
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
            .background_gradient(subset=['Total cost (₹)'], cmap='Reds', high=0.8) # Adjusted high value for better color range
            .background_gradient(subset=['CTR (%)'], cmap='PiYG', low=0.2, high=0.8), # Added gradient for CTR
            width='stretch'
        )

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
            color_discrete_sequence=['#2367AE', '#00A3E0', '#FFCD56'] # Professional colors
        )

        # Calculate max for channel funnel and add padding
        channel_funnel_max = funnel_data['Count'].max()
        channel_y_max = channel_funnel_max * 1.25

        fig_channel_funnel.update_traces(
            texttemplate='<b>%{text:,}</b>',
            textposition='outside',
            textfont=dict(size=16, color='#FFFFFF', family='Poppins')
        )
        fig_channel_funnel.update_layout(
            height=300,
            template='plotly_dark',
            paper_bgcolor='rgba(30, 41, 59, 0.6)',
            plot_bgcolor='rgba(30, 41, 59, 0.4)',
            font=dict(color='#FFFFFF', family='Poppins'),
            title=dict(font=dict(size=14, color='#FFFFFF')),
            xaxis=dict(tickfont=dict(size=10, color='#FFFFFF'), gridcolor='#475569'),
            yaxis=dict(
                tickfont=dict(size=10, color='#FFFFFF'),
                gridcolor='#475569',
                range=[0, channel_y_max]
            ),
            legend=dict(font=dict(size=10, color='#FFFFFF')),
            margin=dict(t=40, b=30, l=40, r=15)
        )
        st.plotly_chart(fig_channel_funnel, use_container_width=True)

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
        st.dataframe(
            df_display.style.format({
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
            }),
            width='stretch',
            height=400
        )

        # Export options for detail view
        st.markdown("### 📥 Export Campaign Data")
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            # Excel export
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_summary.to_excel(writer, sheet_name="Campaign Summary", index=False)
                df_matched_mis.to_excel(writer, sheet_name="Matched MIS Data", index=False)
            output.seek(0)
            st.download_button(
                "📊 Download Excel Report",
                data=output,
                file_name=f"{selected_bank.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )

        with export_col2:
            # CSV export - Summary
            csv_data = df_summary.to_csv(index=False)
            st.download_button(
                "📄 Download Campaign Summary CSV",
                data=csv_data,
                file_name=f"{selected_bank.replace(' ', '_')}_Campaigns_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
            )


        with export_col3:
            # CSV export - Matched MIS
            if len(df_matched_mis) > 0:
                mis_csv_data = df_matched_mis.to_csv(index=False)
                st.download_button(
                    "📄 Download Matched MIS CSV",
                    data=mis_csv_data,
                    file_name=f"{selected_bank.replace(' ', '_')}_MIS_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    width='stretch'
                )
            else:
                st.info("No matched MIS records")


    else:
        st.error(f"No data available for {selected_bank}")


# Footer
st.markdown("""
    <div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-top: 1px solid #475569; margin-top: 1.5rem;'>
        <p style='color: #94A3B8; font-size: 0.75rem; font-weight: 500; margin: 0;'>
            Powered by extrape advisor | Data last updated: {timestamp}
        </p>
    </div>
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)