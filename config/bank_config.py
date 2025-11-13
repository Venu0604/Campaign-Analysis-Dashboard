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
        "skip_mis_date_filter": True,  # Axis Bank processes ALL MIS records regardless of identifier dates
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
        "skip_mis_date_filter": True,  # AU Bank processes ALL MIS records regardless of identifier dates
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
        "skip_mis_date_filter": True,  # RBL Bank processes ALL MIS records regardless of identifier dates
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
        "skip_mis_date_filter": True,  # HDFC Bank processes ALL MIS records regardless of identifier dates
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
        "skip_mis_date_filter": True,  # IDFC processes ALL MIS records regardless of identifier dates
        **UNIFIED_COLOR_SCHEME
    },
    "Scapia": {
        "sheet_gid": "713580679",
        "identifier_column": "first_utm_campaign",  # Campaign identifier (normalized to lowercase)
        "status_column": "current_status",  # current_status column (normalized to lowercase)
        "ops_status_column": "card_issued",  # card_issued column for IPA logic (normalized to lowercase)
        "card_out_status": ["COMPLETED"],  # Card out = COMPLETED in current_status
        "declined_status": ["REJECTED"],  # Declined = REJECTED in current_status
        "ipa_approved_status": ["IN_PROGRESS"],  # IPA = IN_PROGRESS status (checked with card_issued)
        "ipa_card_issued_status": ["ISSUED"],  # IPA also requires card_issued = ISSUED
        "skip_mis_date_filter": True,  # Scapia processes ALL MIS records regardless of identifier dates
        **UNIFIED_COLOR_SCHEME
    },
    "KIWI Bank": {
        "sheet_gid": "1085917805",
        "identifier_column": "term",  # Campaign identifier in term column (normalized to lowercase)
        "status_column": "current_state",  # current_state column (normalized to lowercase)
        "ipa_column": "current_state",  # Use current_state for IPA tracking as well
        "card_out_status": ["KYC_DONE"],  # Card out = KYC_DONE in current_state
        "declined_status": ["REJECTED"],  # Declined = REJECTED in current_state
        "ipa_approved_status": ["AC_CREATED"],  # IPA = AC_CREATED in current_state
        "inprogress_status": [
            "NOT_STARTED", "VKYC_PENDING", "IN_PROGRESS", "KYC_PENDING", "PAN_AADHAR_NOT_LINKED"
        ],  # In progress statuses
        "skip_mis_date_filter": True,  # KIWI processes ALL MIS records regardless of identifier dates
        **UNIFIED_COLOR_SCHEME
    },
    "IndusInd Bank": {
        "sheet_gid": "421802545",
        "identifier_column": "utm_content",  # Campaign identifier in utm_content column (normalized to lowercase)
        "status_column": "stage",  # Stage column for status tracking (normalized to lowercase)
        "ipa_column": "stage",  # Use stage column for IPA tracking as well
        "card_out_status": ["APPROVED"],  # Card out = Approved in Stage
        "declined_status": ["SYSTEM DECLINE", "CREDIT DECLINE"],  # Declined statuses
        "ipa_approved_status": ["POST-BRE PENDENCY", "PRE-BRE PENDENCY"],  # IPA approved = POST-BRE PENDENCY and PRE-BRE PENDENCY
        "inprogress_status": [
            "VKYC PENDING", "WIP"
        ],  # In progress statuses (other statuses not explicitly card out, declined, or IPA)
        "skip_mis_date_filter": True,  # IndusInd processes ALL MIS records regardless of identifier dates
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
