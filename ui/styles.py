"""
UI styling module for campaign dashboard
Contains CSS generation and styling functions
"""


def get_custom_css(bank_config):
    """
    Generate custom CSS based on bank configuration - Circle Health inspired

    Args:
        bank_config: Bank configuration dictionary with color scheme

    Returns:
        CSS string
    """
    # Extract color values from unified color scheme
    colors = {
        "primary": bank_config.get("primary", "#3b82f6"),
        "secondary": bank_config.get("secondary", "#0ea5e9"),
        "tertiary": bank_config.get("tertiary", "#fcc038")
    }
    gradient = bank_config.get("gradient", "135deg, #3b82f6 0%, #0ea5e9 50%, #fcc038 100%")

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800;900&display=swap');

    /* Force light mode globally */
    :root {{
        color-scheme: light !important;
    }}

    html {{
        color-scheme: light !important;
    }}

    body {{
        color-scheme: light !important;
    }}

    /* Global Styles - Circle Health Light Theme */
    .main {{
        font-family: 'Nunito', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #f0f9ff 100%);
        color: #1e293b;
    }}

    .stApp {{
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #f0f9ff 100%) !important;
    }}

    /* Main Header with Gradient */
    .main-header {{
        font-size: 3.5rem;
        font-weight: 800;
        color: #0f172a;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-in-out;
        text-shadow: none;
    }}

    .sub-header {{
        text-align: center;
        color: #1e293b;
        font-size: 1.65rem;
        margin-bottom: 2rem;
        font-weight: 600;
        text-shadow: none;
    }}

    /* Sidebar Styling - Light Theme */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 1px solid #cbd5e1 !important;
    }}

    [data-testid="stSidebar"] * {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] h3 {{
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }}

    [data-testid="stSidebar"] p {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] label {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] div {{
        color: #0f172a !important;
    }}

    [data-testid="stSidebar"] span {{
        color: #0f172a !important;
        font-weight: 700 !important;
    }}

    /* File Uploader in Sidebar - Force Visibility */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
        background-color: white !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] * {{
        color: #0f172a !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] label {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
        background-color: #f8fafc !important;
        border: 2px dashed #3b82f6 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] small {{
        color: #0f172a !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
        background-color: #3b82f6 !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] p {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] div {{
        color: #0f172a !important;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] span {{
        color: #0f172a !important;
        font-weight: 700 !important;
    }}

    /* Expander in Sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {{
        background-color: white !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }}

    /* Fix dark header in expander */
    [data-testid="stSidebar"] [data-testid="stExpander"] > summary {{
        background-color: white !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] > summary > div {{
        background-color: white !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
        background-color: white !important;
    }}

    /* Remove all dark backgrounds from sidebar */
    [data-testid="stSidebar"] div[style*="background"] {{
        background: white !important;
    }}

    [data-testid="stSidebar"] div[class*="st-emotion"] {{
        background-color: transparent !important;
    }}

    /* Target specific emotion cache classes that might have dark backgrounds */
    [data-testid="stSidebar"] .st-emotion-cache-11fa8fd {{
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] .st-emotion-cache-11fa8fd * {{
        color: #0f172a !important;
    }}

    /* Expander text visibility - Force all elements */
    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] * {{
        color: #0f172a !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] p {{
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {{
        color: #0f172a !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {{
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }}

    /* Force expander header text visibility - all states */
    [data-testid="stSidebar"] .streamlit-expanderHeader {{
        background-color: white !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader * {{
        color: #0f172a !important;
        font-weight: 700 !important;
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader p {{
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {{
        background-color: #f1f5f9 !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover * {{
        color: #0f172a !important;
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover p {{
        color: #0f172a !important;
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:active {{
        background-color: #e2e8f0 !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:active * {{
        color: #0f172a !important;
        background-color: transparent !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:focus {{
        background-color: white !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderHeader:focus * {{
        color: #0f172a !important;
        background-color: transparent !important;
    }}

    /* Expander content area */
    [data-testid="stSidebar"] .streamlit-expanderContent {{
        background-color: #f8fafc !important;
    }}

    [data-testid="stSidebar"] .streamlit-expanderContent * {{
        color: #0f172a !important;
    }}

    /* Bank Selection Buttons */
    [data-testid="stSidebar"] button[kind="primary"] {{
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }}

    [data-testid="stSidebar"] button[kind="secondary"] {{
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
    }}

    [data-testid="stSidebar"] button[kind="secondary"]:hover {{
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
        border-color: #3b82f6 !important;
    }}

    /* Filter Section - Light Theme */
    .filter-section {{
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }}

    /* Streamlit Elements Light Mode */
    .stSelectbox, .stDateInput, .stTextInput {{
        background-color: white !important;
    }}

    .stSelectbox > div > div, .stDateInput > div > div, .stTextInput > div > div {{
        background-color: white !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }}

    /* Metric Containers */
    [data-testid="stMetricValue"] {{
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 3.2rem !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}

    [data-testid="stMetricDelta"] {{
        color: #ea580c !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
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

    /* Tabs Styling - Light Theme */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 0 24px;
        font-weight: 600;
        color: #64748b;
        border: 1px solid #e2e8f0;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #3b82f6 !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
    }}

    /* Download Button - Circle Health accent */
    .stDownloadButton button {{
        background-color: #fcc038 !important;
        color: #0f172a !important;
        border: none;
        padding: 0.85rem 1.75rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(252, 192, 56, 0.3);
    }}

    .stDownloadButton button:hover {{
        background-color: #f5b800 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(252, 192, 56, 0.4);
    }}

    /* Info boxes - Light Theme */
    .stAlert {{
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    /* DataFrames - Light Theme */
    .stDataFrame {{
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }}

    .dataframe {{
        background-color: white !important;
        font-size: 1.05rem !important;
    }}

    .dataframe thead th {{
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        border-bottom: 2px solid #cbd5e1 !important;
    }}

    .dataframe tbody td {{
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }}

    .dataframe tbody tr:hover td {{
        background-color: #f8fafc !important;
    }}

    /* Glide DataEditor (Streamlit DataFrame) - Force Light Background */
    .dvn-scroller {{
        background-color: white !important;
        color: #0f172a !important;
    }}

    .dvn-scroll-inner {{
        background-color: white !important;
        color: #0f172a !important;
    }}

    .dvn-underlay {{
        background-color: white !important;
    }}

    .dvn-stack {{
        background-color: white !important;
    }}

    .dvn-stack > div {{
        background-color: white !important;
    }}

    /* All canvas elements in dataframes */
    .stDataFrame canvas {{
        background-color: white !important;
    }}

    /* Glide Data Editor specific */
    div[class*="glide"] {{
        background-color: white !important;
        color: #0f172a !important;
    }}

    .stDataFrameGlideDataEditor {{
        background-color: white !important;
        color: #0f172a !important;
    }}

    /* DataFrame cell text visibility */
    .stDataFrame * {{
        color: #0f172a !important;
    }}

    /* DataFrame wrapper */
    [data-testid="stDataFrame"] > div {{
        background-color: white !important;
    }}

    /* Force all dataframe content to be visible */
    .stDataFrame div {{
        color: #0f172a !important;
    }}

    .stDataFrame span {{
        color: #0f172a !important;
    }}

    .stDataFrame p {{
        color: #0f172a !important;
    }}

    /* Force dataframe to render in light mode */
    [data-testid="stDataFrame"] {{
        color-scheme: light !important;
    }}

    .stDataFrame {{
        color-scheme: light !important;
    }}

    /* Override any dark theme detection */
    @media (prefers-color-scheme: dark) {{
        [data-testid="stDataFrame"] {{
            color-scheme: light !important;
        }}

        .stDataFrame {{
            color-scheme: light !important;
        }}
    }}

    /* Success/Error Messages - Light Theme */
    .stSuccess {{
        background-color: #dcfce7 !important;
        color: #166534 !important;
        border: 1px solid #86efac !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    .stError {{
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border: 1px solid #fca5a5 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    .stWarning {{
        background-color: #fef3c7 !important;
        color: #92400e !important;
        border: 1px solid #fcd34d !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    .stInfo {{
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border: 1px solid #93c5fd !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}

    /* Dividers - Light Theme */
    hr {{
        border-color: #cbd5e1 !important;
    }}

    /* Headers - Light Theme */
    h1, h2, h3, h4, h5, h6 {{
        color: #0f172a !important;
        text-shadow: none;
        font-weight: 700 !important;
    }}

    h3 {{
        font-size: 2rem !important;
    }}

    h2 {{
        font-size: 2.25rem !important;
    }}

    /* Strong text visibility */
    strong, b {{
        color: #0f172a !important;
        font-weight: 700 !important;
    }}

    /* Paragraph text */
    p {{
        color: #1e293b !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }}

    /* Buttons - Circle Health style */
    .stButton>button {{
        background-color: #3b82f6 !important;
        color: white !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.85rem 1.75rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }}

    .stButton>button:hover {{
        background-color: #2563eb !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-1px);
    }}

    /* Chart containers */
    [data-testid="stPlotlyChart"] > div {{
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        background: white !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }}

    /* Plotly Charts Background */
    .js-plotly-plot .plotly .main-svg {{
        background-color: transparent !important;
    }}

    /* Fix any remaining dark backgrounds */
    div[data-testid="stVerticalBlock"] {{
        background-color: transparent !important;
    }}

    div[data-testid="stHorizontalBlock"] {{
        background-color: transparent !important;
    }}

    /* Container backgrounds */
    .element-container {{
        background-color: transparent !important;
    }}

    /* Block containers */
    .block-container {{
        background: transparent !important;
    }}

    /* Ensure all sections are light */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    }}

    /* Fix markdown containers */
    [data-testid="stMarkdownContainer"] {{
        background-color: transparent !important;
    }}

    /* Fix column containers */
    [data-testid="column"] > div {{
        background-color: transparent !important;
    }}

    /* Tabs content area */
    [data-testid="stTabContent"] {{
        background-color: transparent !important;
    }}

    /* Remove any dark overlays */
    .stApp > header {{
        background: transparent !important;
    }}

    /* Ensure streamlit containers are transparent */
    .stMarkdown {{
        background-color: transparent !important;
    }}
    </style>
    """


def get_dashboard_css():
    """
    Generate CSS for the main dashboard (overview mode)
    Consolidated CSS to avoid duplication in app.py
    Circle Health inspired color palette

    Returns:
        CSS string for dashboard styling
    """
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800;900&display=swap');

    /* Force light mode globally */
    :root {
        color-scheme: light !important;
    }

    html {
        color-scheme: light !important;
    }

    body {
        color-scheme: light !important;
    }

    /* Main Container - Circle Health inspired */
    .main {
        font-family: 'Nunito', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #f0f9ff 100%);
        color: #1e293b;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #f0f9ff 100%) !important;
    }

    .main .block-container {
        background: transparent !important;
        padding-top: 1rem !important;
        max-width: 100% !important;
    }

    /* Hide Streamlit header/toolbar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: rgba(0,0,0,0) !important;
    }

    /* Reduce Streamlit top padding */
    .stApp > header {
        background-color: transparent !important;
    }

    /* Header Styling - Circle Health inspired */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: #0f172a;
        text-align: left;
        margin-bottom: 0.3rem;
        margin-top: 0;
        letter-spacing: -0.5px;
        text-shadow: none;
        line-height: 1.1;
    }

    .sub-header {
        text-align: left;
        color: #1e293b;
        font-size: 1.65rem;
        margin-bottom: 0.5rem;
        margin-top: 0;
        font-weight: 600;
        text-shadow: none;
    }

    /* Metric Cards - Circle Health inspired */
    [data-testid="stMetricValue"] {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        text-shadow: none !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetricDelta"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #ea580c !important;
        text-shadow: none !important;
    }

    /* Card Style - Light theme with rounded corners */
    .css-1r6slb0 {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: none;
    }

    /* Section Headers - Light theme */
    h3 {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
        letter-spacing: -0.3px;
        text-shadow: none;
    }

    h2 {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 2.25rem !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
        text-shadow: none;
    }

    h4 {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 1.6rem !important;
        text-shadow: none;
    }

    /* Paragraph text visibility */
    p {
        color: #1e293b !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* Dataframe styling - Light theme */
    .dataframe {
        font-size: 1.05rem !important;
        border: none !important;
        background-color: white !important;
    }

    .dataframe thead th {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        border-bottom: 2px solid #cbd5e1 !important;
        padding: 16px !important;
        text-shadow: none;
    }

    .dataframe tbody td {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        border-bottom: 1px solid #e2e8f0 !important;
        padding: 14px !important;
        background-color: white !important;
    }

    .dataframe tbody tr:hover td {
        background-color: #f8fafc !important;
    }

    [data-testid="stDataFrame"] {
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }

    /* Glide DataEditor (Streamlit DataFrame) - Force Light Background */
    .dvn-scroller {
        background-color: white !important;
        color: #0f172a !important;
    }

    .dvn-scroll-inner {
        background-color: white !important;
        color: #0f172a !important;
    }

    .dvn-underlay {
        background-color: white !important;
    }

    .dvn-stack {
        background-color: white !important;
    }

    .dvn-stack > div {
        background-color: white !important;
    }

    /* All canvas elements in dataframes */
    .stDataFrame canvas {
        background-color: white !important;
    }

    /* Glide Data Editor specific */
    div[class*="glide"] {
        background-color: white !important;
        color: #0f172a !important;
    }

    .stDataFrameGlideDataEditor {
        background-color: white !important;
        color: #0f172a !important;
    }

    /* DataFrame cell text visibility */
    .stDataFrame * {
        color: #0f172a !important;
    }

    /* DataFrame wrapper */
    [data-testid="stDataFrame"] > div {
        background-color: white !important;
    }

    /* Force all dataframe content to be visible */
    .stDataFrame div {
        color: #0f172a !important;
    }

    .stDataFrame span {
        color: #0f172a !important;
    }

    .stDataFrame p {
        color: #0f172a !important;
    }

    /* Force dataframe to render in light mode */
    [data-testid="stDataFrame"] {
        color-scheme: light !important;
    }

    .stDataFrame {
        color-scheme: light !important;
    }

    /* Override any dark theme detection */
    @media (prefers-color-scheme: dark) {
        [data-testid="stDataFrame"] {
            color-scheme: light !important;
        }

        .stDataFrame {
            color-scheme: light !important;
        }
    }

    /* Input elements - Light theme */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div,
    .stDateInput > div > div > input {
        background-color: white !important;
        color: #0f172a !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* Spinner text - Light theme */
    .stSpinner > div {
        color: #1e293b !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }

    /* Buttons - Circle Health inspired */
    .stButton>button {
        background-color: #3b82f6 !important;
        color: white !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.85rem 1.75rem !important;
        transition: all 0.2s ease !important;
        text-shadow: none !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton>button:hover {
        background-color: #2563eb !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Sidebar styling - Light theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 1px solid #cbd5e1 !important;
        padding-top: 1rem !important;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 0.5rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.6rem !important;
        text-shadow: none;
    }

    [data-testid="stSidebar"] p {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] label {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] div {
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] span {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* File Uploader in Sidebar - Force Visibility */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background-color: white !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] * {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] label {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background-color: #f8fafc !important;
        border: 2px dashed #3b82f6 !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] small {
        color: #0f172a !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background-color: #3b82f6 !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] p {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] div {
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] span {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Expander in Sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: white !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }

    /* Fix dark header in expander */
    [data-testid="stSidebar"] [data-testid="stExpander"] > summary {
        background-color: white !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] > summary > div {
        background-color: white !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        background-color: white !important;
    }

    /* Remove all dark backgrounds from sidebar */
    [data-testid="stSidebar"] div[style*="background"] {
        background: white !important;
    }

    [data-testid="stSidebar"] div[class*="st-emotion"] {
        background-color: transparent !important;
    }

    /* Target specific emotion cache classes that might have dark backgrounds */
    [data-testid="stSidebar"] .st-emotion-cache-11fa8fd {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .st-emotion-cache-11fa8fd * {
        color: #0f172a !important;
    }

    /* Expander text visibility - Force all elements */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] * {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] p {
        color: #0f172a !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }

    /* Force expander header text visibility - all states */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: white !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader * {
        color: #0f172a !important;
        font-weight: 700 !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader p {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: #f1f5f9 !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover * {
        color: #0f172a !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover p {
        color: #0f172a !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:active {
        background-color: #e2e8f0 !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:active * {
        color: #0f172a !important;
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:focus {
        background-color: white !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:focus * {
        color: #0f172a !important;
        background-color: transparent !important;
    }

    /* Expander content area */
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: #f8fafc !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderContent * {
        color: #0f172a !important;
    }

    /* Expander styling - Light theme */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
        padding: 0.7rem 1rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: none;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    [data-testid="stExpander"] {
        margin-bottom: 0.5rem !important;
    }

    .streamlit-expanderContent {
        padding: 0.75rem !important;
        background-color: #f8fafc !important;
        border-radius: 0 0 10px 10px;
    }

    /* File uploader styling - Light theme */
    [data-testid="stFileUploader"] {
        background-color: transparent !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stFileUploader"] section {
        background-color: white !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    [data-testid="stFileUploader"] section:hover {
        background-color: #f8fafc !important;
        border-color: #3b82f6 !important;
    }

    [data-testid="stFileUploader"] label {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }

    [data-testid="stFileUploader"] small {
        color: #334155 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploader"] button {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
    }

    [data-testid="stFileUploader"] button:hover {
        background-color: #e2e8f0 !important;
        border-color: #3b82f6 !important;
    }

    [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
        color: #334155 !important;
    }

    /* Alert messages - Light theme */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stSuccess {
        background-color: #dcfce7 !important;
        color: #166534 !important;
        border: 1px solid #86efac !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stInfo {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border: 1px solid #93c5fd !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stError {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border: 1px solid #fca5a5 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Download buttons - Circle Health accent */
    .stDownloadButton>button {
        background-color: #fcc038 !important;
        color: #0f172a !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        padding: 0.85rem 1.75rem !important;
        text-shadow: none !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(252, 192, 56, 0.3) !important;
    }

    .stDownloadButton>button:hover {
        background-color: #f5b800 !important;
        box-shadow: 0 4px 12px rgba(252, 192, 56, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Reduce spacing throughout */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    hr {
        border-color: #334155 !important;
        margin: 0.5rem 0 !important;
    }

    [data-testid="stMetric"] {
        padding: 0.1rem !important;
    }

    [data-testid="column"] {
        padding: 0.1rem !important;
    }

    [data-testid="stMarkdownContainer"] {
        margin-bottom: 0.15rem !important;
    }

    [data-testid="stDataFrame"] {
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stPlotlyChart"] {
        margin-bottom: 0.5rem !important;
    }

    /* Chart Borders and Divisions - Light theme with soft shadows */
    [data-testid="stPlotlyChart"] > div {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        margin-bottom: 1rem !important;
        height: 100% !important;
    }

    /* Section Dividers */
    .chart-section-divider {
        border-top: 1px solid #cbd5e1 !important;
        border-bottom: none !important;
        margin: 1.5rem 0 !important;
        padding: 0.5rem 0 !important;
        box-shadow: none !important;
    }

    /* Horizontal rules between sections */
    hr {
        border-color: #cbd5e1 !important;
        border-width: 1px !important;
        margin: 1.5rem 0 !important;
        box-shadow: none !important;
    }

    /* Column alignment - equal height columns */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        padding: 0.5rem !important;
    }

    /* Ensure equal height for side-by-side elements */
    [data-testid="column"] > div {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Metric card borders - Light theme with soft rounded corners */
    [data-testid="stMetric"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        background: white !important;
        margin-bottom: 0.5rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }

    /* Table borders */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        margin-bottom: 1rem !important;
        background: white !important;
    }

    /* Main content alerts - Light theme */
    .stAlert {
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
    }

    .stSuccess {
        background-color: #dcfce7 !important;
        color: #166534 !important;
        border: 1px solid #86efac !important;
        border-radius: 12px !important;
    }

    .stInfo {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border: 1px solid #93c5fd !important;
        border-radius: 12px !important;
    }

    .stError {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        border: 1px solid #fca5a5 !important;
        border-radius: 12px !important;
    }

    .stWarning {
        background-color: #fef3c7 !important;
        color: #92400e !important;
        border: 1px solid #fcd34d !important;
        border-radius: 12px !important;
    }

    /* Tabs styling - Light theme */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px 10px 0 0 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
    }

    /* Mobile Responsive Styles */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
            text-align: center !important;
        }

        .sub-header {
            font-size: 0.9rem !important;
            text-align: center !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }

        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        [data-testid="column"] {
            padding: 0.25rem !important;
        }

        /* Make tables scrollable on mobile */
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
        }
    }

    /* Tablet responsive */
    @media (max-width: 1024px) and (min-width: 769px) {
        .main-header {
            font-size: 2.2rem !important;
        }

        .sub-header {
            font-size: 1rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
        }
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
