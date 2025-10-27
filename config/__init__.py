"""Configuration package for Campaign Analysis Dashboard"""

from .bank_config import (
    CAMPAIGN_COSTS,
    BANK_CONFIGS,
    GOOGLE_SHEETS_BASE_URL,
    get_bank_config,
    get_google_sheet_url,
    get_all_bank_names
)

__all__ = [
    'CAMPAIGN_COSTS',
    'BANK_CONFIGS',
    'GOOGLE_SHEETS_BASE_URL',
    'get_bank_config',
    'get_google_sheet_url',
    'get_all_bank_names'
]
