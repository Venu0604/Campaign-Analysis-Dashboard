"""
UI styling module for campaign dashboard
Contains CSS generation and styling functions
"""


def get_custom_css(bank_config):
    """
    Generate custom CSS based on bank configuration

    Args:
        bank_config: Bank configuration dictionary with color scheme

    Returns:
        CSS string
    """
    # Extract color values from unified color scheme
    colors = {
        "primary": bank_config.get("primary", "#06B6D4"),
        "secondary": bank_config.get("secondary", "#10B981"),
        "tertiary": bank_config.get("tertiary", "#F59E0B")
    }
    gradient = bank_config.get("gradient", "135deg, #06B6D4 0%, #10B981 50%, #F59E0B 100%")

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    /* Global Styles */
    .main {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: #e2e8f0;
    }}

    /* Main Header with Gradient */
    .main-header {{
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient({gradient});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-in-out;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5)) drop-shadow(0 0 20px rgba(6, 182, 212, 0.3));
    }}

    .sub-header {{
        text-align: center;
        color: #F1F5F9;
        font-size: 1.25rem;
        margin-bottom: 2rem;
        font-weight: 600;
        text-shadow: 0 1px 4px rgba(0,0,0,0.4);
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }}

    [data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}

    /* Bank Selection Buttons */
    [data-testid="stSidebar"] button[kind="primary"] {{
        background: linear-gradient({gradient}) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba({colors['primary']}, 0.4) !important;
    }}

    [data-testid="stSidebar"] button[kind="secondary"] {{
        background: rgba(30, 41, 59, 0.6) !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        font-weight: 500 !important;
    }}

    [data-testid="stSidebar"] button[kind="secondary"]:hover {{
        background: rgba(51, 65, 85, 0.8) !important;
        color: #e2e8f0 !important;
        border-color: #475569 !important;
    }}

    /* Filter Section */
    .filter-section {{
        background: rgba(30, 41, 59, 0.6);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }}

    /* Streamlit Elements Dark Mode */
    .stSelectbox, .stDateInput, .stTextInput {{
        background-color: #1e293b !important;
    }}

    .stSelectbox > div > div, .stDateInput > div > div, .stTextInput > div > div {{
        background-color: #334155 !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
    }}

    /* Metric Containers */
    [data-testid="stMetricValue"] {{
        color: {colors['primary']} !important;
        font-weight: 700;
    }}

    [data-testid="stMetricDelta"] {{
        color: #94a3b8 !important;
    }}

    /* Animation */
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

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 10px 10px 0 0;
        padding: 0 24px;
        font-weight: 600;
        color: #94a3b8;
        border: 1px solid #334155;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient({gradient});
        color: white !important;
        border: none;
    }}

    /* Download Button */
    .stDownloadButton button {{
        background: linear-gradient({gradient});
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba({colors['primary']}, 0.3);
    }}

    .stDownloadButton button:hover {{
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba({colors['secondary']}, 0.4);
    }}

    /* Info boxes */
    .stAlert {{
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
    }}

    /* DataFrames */
    .stDataFrame {{
        background-color: #1e293b !important;
    }}

    /* Success/Error Messages */
    .stSuccess {{
        background-color: rgba(16, 185, 129, 0.1) !important;
        color: #10b981 !important;
        border: 1px solid #10b981 !important;
    }}

    .stError {{
        background-color: rgba(239, 68, 68, 0.1) !important;
        color: #ef4444 !important;
        border: 1px solid #ef4444 !important;
    }}

    /* Dividers */
    hr {{
        border-color: #334155 !important;
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: #FFFFFF !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}

    /* Strong text visibility */
    strong, b {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}

    /* Plotly Charts Background */
    .js-plotly-plot .plotly .main-svg {{
        background-color: transparent !important;
    }}
    </style>
    """


def get_dashboard_css():
    """
    Generate CSS for the main dashboard (overview mode)
    Consolidated CSS to avoid duplication in app.py

    Returns:
        CSS string for dashboard styling
    """
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* Main Container - Dark theme */
    .main {
        font-family: 'Poppins', sans-serif;
        background: #0F172A;
        color: #E2E8F0;
    }

    .stApp {
        background: #0F172A !important;
    }

    .main .block-container {
        background: #0F172A !important;
    }

    /* Header Styling - Dark theme with bright accent */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        text-align: left;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5), 0 0 20px rgba(6, 182, 212, 0.3);
        line-height: 1.2;
    }

    .sub-header {
        text-align: left;
        color: #F1F5F9;
        font-size: 1.15rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-shadow: 0 1px 4px rgba(0,0,0,0.4);
    }

    /* Metric Cards - Dark theme */
    [data-testid="stMetricValue"] {
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #CBD5E1 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    [data-testid="stMetricDelta"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #22D3EE !important;
    }

    /* Card Style - Dark theme */
    .css-1r6slb0 {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #334155;
    }

    /* Section Headers - Dark theme */
    h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.35rem !important;
        letter-spacing: -0.3px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    h2 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.35rem !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.3);
    }

    /* Paragraph text visibility */
    p {
        color: #E2E8F0 !important;
    }

    /* Dataframe styling - Dark theme */
    .dataframe {
        font-size: 1rem !important;
        border: none !important;
        background-color: #1E293B !important;
    }

    .dataframe thead th {
        background-color: #334155 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border-bottom: 2px solid #475569 !important;
        padding: 14px !important;
    }

    .dataframe tbody td {
        color: #F1F5F9 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        border-bottom: 1px solid #334155 !important;
        padding: 12px !important;
        background-color: #1E293B !important;
    }

    .dataframe tbody tr:hover td {
        background-color: #334155 !important;
    }

    [data-testid="stDataFrame"] {
        background-color: #1E293B !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }

    /* Input elements - Dark theme */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div,
    .stDateInput > div > div > input {
        background-color: #334155 !important;
        color: #F1F5F9 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        border: 1px solid #475569 !important;
    }

    /* Spinner text - Dark theme */
    .stSpinner > div {
        color: #E2E8F0 !important;
    }

    /* Buttons - Bright accent for dark theme */
    .stButton>button {
        background-color: #0EA5E9 !important;
        color: white !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.6rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background-color: #0284C7 !important;
        box-shadow: 0 4px 12px rgba(14,165,233,0.4) !important;
    }

    /* Sidebar styling - Dark theme */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 2px solid #475569 !important;
        padding-top: 1rem !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 0.5rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.1rem !important;
    }

    /* Expander styling - Dark theme */
    .streamlit-expanderHeader {
        background-color: #334155 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        padding: 0.6rem 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stExpander"] {
        margin-bottom: 0.5rem !important;
    }

    .streamlit-expanderContent {
        padding: 0.75rem !important;
    }

    /* File uploader styling - Dark theme */
    [data-testid="stFileUploader"] {
        background-color: transparent !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: #334155 !important;
        border: 2px dashed #64748B !important;
        border-radius: 8px !important;
        padding: 1.25rem !important;
    }

    [data-testid="stFileUploader"] section:hover {
        background-color: #475569 !important;
        border-color: #0EA5E9 !important;
    }

    [data-testid="stFileUploader"] label {
        color: #F1F5F9 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }

    [data-testid="stFileUploader"] small {
        color: #CBD5E1 !important;
        font-size: 0.95rem !important;
    }

    [data-testid="stFileUploader"] button {
        background-color: #475569 !important;
        color: #E2E8F0 !important;
        border: 1px solid #64748B !important;
        font-weight: 500 !important;
    }

    [data-testid="stFileUploader"] button:hover {
        background-color: #334155 !important;
        border-color: #0EA5E9 !important;
    }

    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
        color: #94A3B8 !important;
    }

    /* Alert messages */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #334155 !important;
        color: #E2E8F0 !important;
        border: 1px solid #475569 !important;
    }

    [data-testid="stSidebar"] .stSuccess {
        background-color: #134E4A !important;
        color: #6EE7B7 !important;
        border: 1px solid #10B981 !important;
    }

    [data-testid="stSidebar"] .stInfo {
        background-color: #0C4A6E !important;
        color: #7DD3FC !important;
        border: 1px solid #0EA5E9 !important;
    }

    [data-testid="stSidebar"] .stError {
        background-color: #7F1D1D !important;
        color: #FCA5A5 !important;
        border: 1px solid #EF4444 !important;
    }

    /* Download buttons - Dark theme */
    .stDownloadButton>button {
        background-color: #0EA5E9 !important;
        color: white !important;
    }

    /* Reduce spacing throughout */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    hr {
        border-color: #E2E8F0 !important;
        margin: 0.75rem 0 !important;
    }

    [data-testid="stMetric"] {
        padding: 0.25rem !important;
    }

    [data-testid="column"] {
        padding: 0.15rem !important;
    }

    [data-testid="stMarkdownContainer"] {
        margin-bottom: 0.25rem !important;
    }

    [data-testid="stDataFrame"] {
        margin-bottom: 0.75rem !important;
    }

    [data-testid="stPlotlyChart"] {
        margin-bottom: 0.75rem !important;
    }

    /* Main content alerts - Dark theme */
    .stAlert {
        background-color: #334155 !important;
        color: #E2E8F0 !important;
        border: 1px solid #475569 !important;
    }

    .stSuccess {
        background-color: #134E4A !important;
        color: #6EE7B7 !important;
        border: 1px solid #10B981 !important;
    }

    .stInfo {
        background-color: #0C4A6E !important;
        color: #7DD3FC !important;
        border: 1px solid #0EA5E9 !important;
    }

    .stError {
        background-color: #7F1D1D !important;
        color: #FCA5A5 !important;
        border: 1px solid #EF4444 !important;
    }

    .stWarning {
        background-color: #78350F !important;
        color: #FCD34D !important;
        border: 1px solid #F59E0B !important;
    }

    /* Tabs styling - Dark theme */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #334155 !important;
        color: #94A3B8 !important;
        border: 1px solid #475569 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0EA5E9 !important;
        color: white !important;
        border: 1px solid #0EA5E9 !important;
    }
    </style>
    """


def get_welcome_message(bank_name, bank_config):
    """
    Generate welcome screen HTML

    Args:
        bank_name: Name of the bank
        bank_config: Bank configuration dictionary

    Returns:
        HTML string
    """
    gradient = bank_config.get("gradient", "135deg, #06B6D4 0%, #10B981 50%, #F59E0B 100%")

    return f"""
        <div style='text-align: center; padding: 3rem;'>
            <h2 style='color: #e2e8f0;'>👋 Welcome to {bank_name} Campaign Analytics</h2>
            <p style='font-size: 1.1rem; color: #94a3b8; margin-top: 1rem;'>
                Upload your MIS Excel file to unlock powerful insights and analytics.
            </p>
            <div style='margin-top: 2rem; padding: 2rem;
                 background: linear-gradient({gradient});
                 border-radius: 15px; color: white; box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);'>
                <h3>✨ Features</h3>
                <ul style='list-style: none; padding: 0; text-align: left;'>
                    <li style='padding: 0.5rem 0;'>🏦 Multi-Bank Support</li>
                    <li style='padding: 0.5rem 0;'>📅 Date range filtering</li>
                    <li style='padding: 0.5rem 0;'>🎯 Multi-dimensional analysis</li>
                    <li style='padding: 0.5rem 0;'>📊 Interactive visualizations</li>
                    <li style='padding: 0.5rem 0;'>💰 Channel-specific costing</li>
                    <li style='padding: 0.5rem 0;'>📥 Comprehensive exports</li>
                    <li style='padding: 0.5rem 0;'>🔍 MIS record matching</li>
                </ul>
            </div>
        </div>
    """
