# 🎯 Unified Campaign Analytics Dashboard

A professional, modular multi-bank campaign performance analysis and reporting tool built with Streamlit.

## 🏦 Supported Banks

- **Axis Bank**
- **AU Bank**
- **RBL Bank**
- **HDFC Bank**
- **IDFC Bank**
- **Scapia**

## ✨ Features

- 🏦 **Multi-Bank Support** - Single dashboard for all banks with bank-specific configurations
- 📊 **Interactive Analytics** - Real-time performance tracking with dynamic visualizations
- 🎨 **Dynamic Theming** - Each bank has its unique color scheme and branding
- 📅 **Advanced Filtering** - Filter by date range, source, channel, and campaign
- 💰 **Channel-Specific Costing** - Accurate cost calculations per communication channel
- 🔍 **MIS Record Matching** - Automatic matching of MIS records with campaign identifiers
- 📥 **Comprehensive Exports** - Excel and CSV export capabilities
- 📈 **Rich Visualizations** - Time series, funnels, distributions, and comparison charts

## 📁 Project Structure

```
Campaign Analysis/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore configuration
│
├── config/                     # Configuration modules
│   ├── __init__.py
│   └── bank_config.py         # Bank-specific configurations
│
├── core/                       # Core processing modules
│   ├── __init__.py
│   └── data_processor.py      # Campaign data processing logic
│
├── ui/                         # UI components
│   ├── __init__.py
│   ├── charts.py              # Chart building functions
│   └── styles.py              # CSS styling functions
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── helpers.py             # Helper utilities
│
├── data/                       # MIS data files
│   └── [Excel/XLSB files]     # Bank MIS files
│
├── credentials/                # Authentication credentials
│   └── service_account.json   # Google Sheets API credentials
│
└── archived/                   # Legacy files
    └── [old individual dashboards]
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### Using the Dashboard

1. **Select Bank** - Choose the bank from the sidebar dropdown
2. **Upload MIS File** - Upload your Excel MIS file (.xlsx, .xls, or .xlsb)
3. **Apply Filters** - Use date range, source, channel, and campaign filters
4. **Analyze** - View interactive charts and metrics
5. **Export** - Download reports in Excel or CSV format

## 📊 Dashboard Tabs

### 1. Performance Analytics
- Time series performance trends
- CTR distribution analysis
- Conversion funnel visualization
- Source performance matrix
- Top performing campaigns
- Cost efficiency analysis

### 2. Campaign Comparison
- Channel performance comparison
- Cost distribution by source
- Channel cost breakdown

### 3. Data Table
- Searchable campaign data
- Formatted metrics display
- Summary statistics

### 4. Matched MIS
- View matched MIS records
- Filter by campaign identifier
- Export matched records

### 5. Export
- Download Excel reports with multiple sheets
- Export filtered data as CSV
- Comprehensive data exports

## 🎨 Channel Costs

Default costs per communication channel:

- **SMS**: ₹0.10 per unit
- **RCS**: ₹0.085 per unit
- **WhatsApp Marketing**: ₹0.80 per unit
- **WhatsApp Utility**: ₹0.115 per unit
- **Email**: ₹0.05 per unit

## 🔧 Configuration

### Adding a New Bank

Edit `config/bank_config.py` and add a new entry to the `BANK_CONFIGS` dictionary:

```python
"New Bank": {
    "sheet_gid": "your_google_sheet_gid",
    "identifier_column": "COLUMN_NAME",
    "status_column": "STATUS_COLUMN",
    "ipa_column": "IPA_COLUMN",
    "card_out_status": ["APPROVED"],
    "declined_status": ["DECLINED"],
    "ipa_approved_status": ["APPROVED"],
    "color_scheme": {
        "primary": "#hex_color",
        "secondary": "#hex_color",
        "tertiary": "#hex_color"
    },
    "gradient": "135deg, #color1 0%, #color2 100%",
    "chart_colors": ["#color1", "#color2", "#color3"]
}
```

## 📈 Calculated Metrics

The dashboard automatically calculates:

- **CTR (Click-Through Rate)**: (Clicks / Delivered) × 100
- **Read Rate**: (Read / Delivered) × 100
- **CPC (Cost Per Click)**: Total Cost / Clicks
- **Cost per Application**: Total Cost / Applications
- **Cost per IPA**: Total Cost / IPA Approved
- **Cost per Card Out**: Total Cost / Card Out
- **Conversion Rates**: Application to IPA, IPA to Card Out

## 🛠️ Technology Stack

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive visualizations
- **OpenPyXL** - Excel file handling

## 📝 Data Requirements

### Campaign Identifiers (Google Sheets)
Required columns:
- Date
- Identifiers
- Source
- Channel
- Delivered
- Clicks
- Read

### MIS File (Excel)
Required columns vary by bank - see `config/bank_config.py` for bank-specific requirements.

## 🔒 Data Privacy

- All data processing happens locally
- No data is stored permanently
- Google Sheets integration is read-only

## 🤝 Contributing

To contribute:
1. Add new features in appropriate modules
2. Update configurations in `config/bank_config.py`
3. Add utility functions to `utils/helpers.py`
4. Update this README with changes

## 📄 License

© 2025 Campaign Analytics Dashboard - All Rights Reserved

## 🆘 Support

For issues or questions:
1. Check the error details in the expander
2. Verify your MIS file structure matches bank configuration
3. Ensure all required columns are present in uploaded files

## 🎯 Best Practices

1. **Regular Exports** - Export reports regularly to track trends
2. **Date Filtering** - Use date filters for period-specific analysis
3. **Campaign Naming** - Use consistent naming conventions for campaigns
4. **Data Quality** - Ensure MIS files have clean, consistent data

---

**Built with ❤️ for Campaign Performance Analytics**
