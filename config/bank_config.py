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
        "color_scheme": {
            "primary": "#7c3aed",
            "secondary": "#6366f1",
            "tertiary": "#8b5cf6"
        },
        "gradient": "135deg, #7c3aed 0%, #6366f1 50%, #8b5cf6 100%",
        "chart_colors": ["#7c3aed", "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd"]
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
        "color_scheme": {
            "primary": "#f59e0b",
            "secondary": "#d97706",
            "tertiary": "#ea580c"
        },
        "gradient": "135deg, #f59e0b 0%, #ea580c 100%",
        "chart_colors": ["#f59e0b", "#d97706", "#ea580c", "#fb923c", "#fdba74"]
    },
    "RBL Bank": {
        "sheet_gid": "1119698657",
        "sheet_name": "Dump",  # RBL MIS has data in "Dump" sheet
        "identifier_column": "QUICK DATA ENTRY: CAMPAIGN SOURCE",  # Actual column name
        "status_column": "DISPOSITION",  # Main disposition column
        "ipa_column": "FINAL OPS STATUS",  # Final OPS Status for IPA tracking
        "ops_status_column": "OPS STATUS TILL 23-OCT-25",  # OPS status for card out tracking
        "card_out_status": ["CARD SETUP"],  # Card setup (181 records)
        "declined_status": [
            "VR REJECTED", "REJECTED BY UW", "CURING REJECTED: CHECKER",
            "FCU REJECT", "RCU DECLINED", "HRP REJECT", "RAMP REJECT"
        ],  # All reject statuses (~59 records)
        "ipa_approved_status": ["CREDIT APPROVED"],  # Credit approved from Final OPS Status (186 records)
        "inprogress_status": [
            "FCU/VERIFICATION PENDING", "RETURN TO UPSELL", "RCU PENDING",
            "EMAIL VERIFICATION PENDING", "CURING PENDING: MAKER", "TAT BREACHED QUEUE",
            "UPSELL", "WIP"
        ],  # In progress statuses
        "color_scheme": {
            "primary": "#06b6d4",
            "secondary": "#3b82f6",
            "tertiary": "#8b5cf6"
        },
        "gradient": "135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%",
        "chart_colors": ["#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b"]
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
        "color_scheme": {
            "primary": "#dc2626",
            "secondary": "#991b1b",
            "tertiary": "#b91c1c"
        },
        "gradient": "135deg, #dc2626 0%, #991b1b 100%",
        "chart_colors": ["#dc2626", "#991b1b", "#b91c1c", "#ef4444", "#f87171"]
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
        "color_scheme": {
            "primary": "#059669",
            "secondary": "#047857",
            "tertiary": "#065f46"
        },
        "gradient": "135deg, #059669 0%, #047857 100%",
        "chart_colors": ["#059669", "#047857", "#065f46", "#10b981", "#34d399"]
    },
    "Scapia": {
        "sheet_gid": "713580679",
        "identifier_column": "FIRST_UTM_CAMPAIGN",  # Campaign identifier (not _screen)
        "status_column": "CARD_ISSUED",  # Use card_issued for card out tracking
        "ipa_column": "CURRENT_STATUS",  # Current status for IPA tracking
        "note_column": "NOTES",  # Notes column for additional info
        "card_out_status": ["ISSUED"],  # Card issued (357 records)
        "declined_status": ["REJECTED"],  # Rejected applications (14,598 records)
        "ipa_approved_status": ["COMPLETED", "IN_PROGRESS"],  # Consider both as IPA approved (2,851 records)
        "inprogress_status": ["IN_PROGRESS"],  # In progress (2,516 records)
        "color_scheme": {
            "primary": "#7c3aed",
            "secondary": "#6d28d9",
            "tertiary": "#5b21b6"
        },
        "gradient": "135deg, #7c3aed 0%, #6d28d9 100%",
        "chart_colors": ["#7c3aed", "#6d28d9", "#5b21b6", "#8b5cf6", "#a78bfa"]
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
