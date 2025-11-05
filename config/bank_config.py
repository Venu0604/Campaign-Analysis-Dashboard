"""
Bank Configuration Settings
Contains all bank-specific configurations including Google Sheet GIDs,
column mappings, status definitions, and color schemes.
"""

# Campaign costs by channel (shared across all banks)
CAMPAIGN_COSTS = {
    "SMS": 0.10,
    "RCS": 0.085,
    "Whatsapp Marketing": 0.80,
    "Whatsapp Utility": 0.115,
    "Email": 0.05,
}

# Professional color scheme inspired by corporate standards
UNIFIED_COLOR_SCHEME = {
    "primary": "#2367AE",      # Professional blue
    "secondary": "#00A3E0",     # Bright blue accent
    "tertiary": "#FFCD56",      # Gold accent
    "quaternary": "#00C389",    # Teal accent
    "gradient": "135deg, #2367AE 0%, #00A3E0 50%, #FFCD56 100%",
    "chart_colors": ["#2367AE", "#00A3E0", "#FFCD56", "#00C389", "#7B68EE", "#FF6B9D"]
}

# Google Sheets base URL
GOOGLE_SHEETS_BASE_URL = "https://docs.google.com/spreadsheets/d/184yquIAWt0XyQEYhI3yv0djg9f6pUtZS7TZ4Un7NLXI/export?format=csv&gid="

# Bank-specific configurations
BANK_CONFIGS = {
    "Axis Bank": {
        "sheet_gid": "526829508",
        "identifier_column": "CROSSCELLCODE",
        "status_column": "FINAL STATUS",
        "ipa_column": "IPA STATUS",
        "card_out_status": ["APPROVED"],
        "declined_status": ["DECLINED"],
        "ipa_approved_status": ["APPROVED", "IPA APPROVED", "UNDERWRITER APPROVED", "RCU", "UW"],
        **UNIFIED_COLOR_SCHEME
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
            "PAN AADHAAR CHECK REJECT", "DVU REJECT CASE",
            "LOGICAL DELETED", "BUREAU DECLINE CASE"
        ],
        "ipa_approved_status": ["APPROVED"],
        **UNIFIED_COLOR_SCHEME
    },
    "RBL Bank": {
        "sheet_gid": "1119698657",
        "sheet_name": "Dump",  # RBL MIS has data in "Dump" sheet
        "identifier_column": "QUICK DATA ENTRY: CAMPAIGN SOURCE",  # Actual column name
        "status_column": "disposition.1",  # Second Disposition column (column O) - pandas uses dot for duplicates
        "ipa_column": "FINAL OPS STATUS",  # Final OPS Status for IPA tracking
        "ops_status_column": "OPS STATUS TILL",  # OPS status for card out tracking (partial match for date flexibility)
        "card_out_status": ["CARD SETUP"],  # Card setup status
        "declined_status": [
            "AIP DECLINE", "VR REJECTED", "REJECTED BY UW", "CURING REJECTED: CHECKER",
            "FCU REJECT", "RCU DECLINED", "HRP REJECT", "RAMP REJECT"
        ],  # All reject statuses including AIP Decline
        "ipa_approved_status": ["CREDIT APPROVED"],  # Credit approved from Final OPS Status
        "inprogress_status": [
            "FCU/VERIFICATION PENDING", "RETURN TO UPSELL", "RCU PENDING",
            "EMAIL VERIFICATION PENDING", "CURING PENDING: MAKER", "TAT BREACHED QUEUE",
            "UPSELL", "WIP"
        ],  # In progress statuses
        **UNIFIED_COLOR_SCHEME
    },
    "HDFC Bank": {
        "sheet_gid": "2141873222",
        "identifier_column": "LC1_CODE",  # HDFC uses LC1_CODE as primary identifier
        "secondary_identifier": "LG_CODE",  # LG_Code as secondary identifier
        "status_column": "FINAL_DECISION",  # Final decision column for Card Out/Declined
        "ipa_column": "IPA_STATUS",  # IPA_STATUS column (only has APPROVE/DECLINE)
        "card_out_status": ["APPROVE", "Approve"],  # Card issued - from FINAL_DECISION (586+6=592 total)
        "declined_status": ["IPA REJECT", "Decline", "DECLINE"],  # All declined - from FINAL_DECISION (12960+734+12=13706)
        "ipa_approved_status": ["APPROVE"],  # IPA approved - from IPA_STATUS column (6878 total)
        "inprogress_status": ["IPA APPROVED DROPOFF CASE", "Inprocess", "INPROCESS"],  # In progress (4962+577+1=5540)
        **UNIFIED_COLOR_SCHEME
    },
    "IDFC Bank": {
        "sheet_gid": "0",
        "sheet_name": "App Details",  # IDFC MIS has specific sheet name
        "identifier_column": "UTM CAMPAIGN",  # Campaign identifier column
        "status_column": "SUB STAGE",  # Sub Stage column for card out status
        "ipa_column": "SOFT DECISION",  # Soft Decision column for IPA approval
        "card_out_status": ["CARD GENERATION COMPLETED"],  # Card issued (308 records)
        "declined_status": [
            "POSIDEX REJECT", "UNDERWRITING REJECT", "POLICY REJECT",
            "SYSTEM CANCELLED", "SALES CANCELLED", "OPS REJECT", "FI REJECT"
        ],  # All reject/cancelled statuses
        "ipa_approved_status": ["APPROVED"],  # IPA approved in SOFT DECISION (1321 records)
        "inprogress_status": [
            "OFFER GENERATED", "FD QDE PENDING", "DDE PENDING", "QDE PENDING",
            "VKYC INITIATION PENDING", "PAYMENT PENDING", "VKYC INITIATED",
            "UNDERWRITING PENDING", "VERIFICATION PENDING", "EKYC INITIATED",
            "CURING INITIATED"
        ],  # All in-progress statuses
        **UNIFIED_COLOR_SCHEME
    },
    "Scapia": {
        "sheet_gid": "713580679",
        "identifier_column": "FIRST_UTM_CAMPAIGN",  # Campaign identifier (not _screen)
        "status_column": "CURRENT_STATUS",  # Use current_status for declined tracking
        "ops_status_column": "CARD_ISSUED",  # Use card_issued for card out tracking
        "ipa_column": "CURRENT_STATUS",  # Current status for IPA tracking
        "note_column": "NOTES",  # Notes column for additional info
        "card_out_status": ["ISSUED"],  # Card issued (357 records)
        "declined_status": ["REJECTED"],  # Rejected applications from CURRENT_STATUS
        "ipa_approved_status": ["COMPLETED", "IN_PROGRESS"],  # Consider both as IPA approved (2,851 records)
        "inprogress_status": ["IN_PROGRESS"],  # In progress (2,516 records)
        **UNIFIED_COLOR_SCHEME
    }
}

def get_bank_config(bank_name):
    """Get configuration for a specific bank"""
    return BANK_CONFIGS.get(bank_name, BANK_CONFIGS["Axis Bank"])

def get_google_sheet_url(bank_name):
    """Get Google Sheets URL for a specific bank"""
    config = get_bank_config(bank_name)
    return f"{GOOGLE_SHEETS_BASE_URL}{config['sheet_gid']}"

def get_all_bank_names():
    """Get list of all supported banks"""
    return list(BANK_CONFIGS.keys())
