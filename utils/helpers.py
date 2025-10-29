"""
Helper utility functions for campaign dashboard
Contains reusable functions for data manipulation and calculations
"""

import pandas as pd
import streamlit as st
from config.bank_config import CAMPAIGN_COSTS
from typing import Optional, Union, List, Dict, Any


def find_column(df, keywords):
    """
    Find column that contains any of the keywords (case insensitive)
    First tries exact match, then partial match

    Args:
        df: DataFrame to search
        keywords: String or list of keywords to match

    Returns:
        Column name if found, None otherwise
    """
    if isinstance(keywords, str):
        keywords = [keywords]

    # First pass: Try exact match (case-insensitive)
    for col in df.columns:
        col_clean = str(col).strip().replace('*', '').lower()
        for keyword in keywords:
            keyword_clean = keyword.lower()
            if col_clean == keyword_clean:
                return col

    # Second pass: Try partial match (contains)
    for col in df.columns:
        col_clean = str(col).strip().replace('*', '').lower()
        for keyword in keywords:
            keyword_clean = keyword.lower()
            if keyword_clean in col_clean:
                return col

    return None


@st.cache_data
def get_channel_cost(channel: str, costs_dict: Optional[Dict[str, float]] = None) -> float:
    """
    Get cost for a channel with case-insensitive matching and caching

    Args:
        channel: Channel name
        costs_dict: Dictionary of channel costs (defaults to CAMPAIGN_COSTS)

    Returns:
        Cost per unit for the channel
    """
    if costs_dict is None:
        costs_dict = CAMPAIGN_COSTS

    channel_lower = str(channel).lower()

    # Optimized lookup with early return
    if "sms" in channel_lower:
        return costs_dict.get("SMS", 0.10)
    if "rcs" in channel_lower:
        return costs_dict.get("RCS", 0.085)
    if "whatsapp" in channel_lower:
        return costs_dict.get("Whatsapp Utility", 0.115) if "utility" in channel_lower else costs_dict.get("Whatsapp Marketing", 0.80)
    if "email" in channel_lower:
        return costs_dict.get("Email", 0.05)

    return costs_dict.get("SMS", 0.10)


def calculate_metrics(delivered, clicks, read_count, cost_per_unit, applications,
                      ipa_approved, card_out):
    """
    Calculate campaign performance metrics

    Args:
        delivered: Number of messages delivered
        clicks: Number of clicks
        read_count: Number of reads
        cost_per_unit: Cost per message
        applications: Number of applications
        ipa_approved: IPA approved count
        card_out: Card out count

    Returns:
        Dictionary of calculated metrics
    """
    metrics = {}

    # CTR and Read Rate
    metrics['ctr'] = round((clicks / delivered * 100), 2) if delivered > 0 else 0
    metrics['read_rate'] = round((read_count / delivered * 100), 2) if delivered > 0 else 0

    # Cost metrics
    metrics['total_cost'] = round(delivered * cost_per_unit, 2)
    metrics['cpc'] = round((metrics['total_cost'] / clicks), 2) if clicks > 0 else 0
    metrics['cost_per_app'] = round((metrics['total_cost'] / applications), 2) if applications > 0 else 0
    metrics['cost_per_ipa'] = round((metrics['total_cost'] / ipa_approved), 2) if ipa_approved > 0 else 0
    metrics['cost_per_card'] = round((metrics['total_cost'] / card_out), 2) if card_out > 0 else 0

    # Conversion rates
    metrics['app_to_ipa_rate'] = round((ipa_approved / applications * 100), 2) if applications > 0 else 0
    metrics['ipa_to_card_rate'] = round((card_out / ipa_approved * 100), 2) if ipa_approved > 0 else 0
    metrics['app_to_card_rate'] = round((card_out / applications * 100), 2) if applications > 0 else 0

    return metrics


def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column names (optimized to avoid extra copy)

    Args:
        df: DataFrame to normalize

    Returns:
        DataFrame with normalized columns
    """
    # Strip whitespace and convert to lowercase in one pass
    df.columns = df.columns.str.strip().str.lower()

    # Handle duplicate columns efficiently
    cols = pd.Series(df.columns)
    duplicates = cols[cols.duplicated()].unique()

    if len(duplicates) > 0:
        for dup in duplicates:
            indices = cols[cols == dup].index.values.tolist()
            cols[indices] = [f"{dup}_{i}" if i != 0 else dup for i in range(len(indices))]
        df.columns = cols

    return df


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_google_sheet(url: str) -> Optional[pd.DataFrame]:
    """
    Load data from Google Sheets CSV export URL with caching

    Args:
        url: Google Sheets CSV export URL

    Returns:
        DataFrame or None if error
    """
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error loading Google Sheet: {e}")
        return None


def load_excel_file(file, sheet_name=0):
    """
    Load Excel file with automatic engine detection

    Args:
        file: File object
        sheet_name: Sheet name or index

    Returns:
        DataFrame or None if error
    """
    try:
        file_extension = file.name.split('.')[-1].lower()

        if file_extension == 'xls':
            engine = 'xlrd'
        elif file_extension == 'xlsb':
            engine = 'pyxlsb'
        else:
            engine = 'openpyxl'

        df = pd.read_excel(file, sheet_name=sheet_name, engine=engine)
        return df
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return None


def format_currency(value):
    """Format value as Indian Rupee currency"""
    return f"₹{value:,.2f}"


def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.2f}%"


def format_number(value):
    """Format number with thousand separators"""
    return f"{value:,}"


def safe_division(numerator, denominator, default=0, decimals=2):
    """
    Safely divide two numbers with error handling

    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Default value if division fails
        decimals: Number of decimal places

    Returns:
        Result of division or default
    """
    try:
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        return round(numerator / denominator, decimals)
    except:
        return default


def create_date_filters(df, date_column, date_format=None):
    """
    Create date range filters for dashboard

    Args:
        df: DataFrame with date column
        date_column: Name of date column
        date_format: Optional date format string (e.g., '%d/%m/%Y')

    Returns:
        Dictionary with min_date, max_date, and filter options
    """
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Could not infer format")

        if date_format:
            df[date_column] = pd.to_datetime(df[date_column], format=date_format, errors='coerce')
        else:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

    min_date = df[date_column].min()
    max_date = df[date_column].max()

    filters = {
        'min_date': min_date,
        'max_date': max_date,
        'options': {
            'Last 7 days': (max_date - pd.Timedelta(days=7), max_date),
            'Last 30 days': (max_date - pd.Timedelta(days=30), max_date),
            'This Month': (max_date.replace(day=1), max_date),
            'All Time': (min_date, max_date)
        }
    }

    return filters


def get_status_counts(df, status_column, status_list):
    """
    Count occurrences of specific statuses

    Args:
        df: DataFrame
        status_column: Column containing status
        status_list: List of statuses to count

    Returns:
        Count of matching statuses
    """
    if status_column not in df.columns:
        return 0

    status_values = df[status_column].astype(str).str.strip().str.upper()
    status_list_upper = [s.upper() for s in status_list]

    return status_values.isin(status_list_upper).sum()
