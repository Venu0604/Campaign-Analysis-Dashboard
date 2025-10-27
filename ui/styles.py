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
    colors = bank_config["color_scheme"]
    gradient = bank_config["gradient"]

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
        color: #e2e8f0 !important;
    }}

    /* Plotly Charts Background */
    .js-plotly-plot .plotly .main-svg {{
        background-color: transparent !important;
    }}
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
    gradient = bank_config["gradient"]

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
