"""
Image Handler Module
Handles loading and encoding images for dashboard display
"""

import base64
from pathlib import Path
from typing import Optional, Dict
import streamlit as st

# Base path for assets
ASSETS_PATH = Path(__file__).parent.parent / "assets"
IMAGES_PATH = ASSETS_PATH / "images"
LOGOS_PATH = ASSETS_PATH / "logos"

# Bank logo mapping
BANK_LOGO_MAP = {
    "Axis Bank": "axis_cc_logo.jpeg",
    "AU Bank": "AU_cc_logo.jpeg",
    "RBL Bank": "rbl_cc_logo.jpeg",
    "HDFC Bank": "hdfc_cc_logo.jpeg",
    "IDFC Bank": "idfc_cc_logo.jpeg",
    "Scapia": "scapia_cc_logo.jpeg"
}

@st.cache_data
def get_base64_image(image_path: str) -> Optional[str]:
    """
    Convert image to base64 string for HTML embedding (with caching)

    Args:
        image_path: Path to image file

    Returns:
        Base64 encoded string or None on error
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


@st.cache_data
def get_extrape_logo() -> Optional[str]:
    """
    Get extrape advisor logo as base64 (cached)

    Returns:
        Base64 encoded logo string
    """
    logo_path = IMAGES_PATH / "Extrape-advisor-arc-logo-.webp"
    return get_base64_image(str(logo_path))


@st.cache_data
def get_bank_logo(bank_name: str) -> Optional[str]:
    """
    Get bank logo as base64 (cached)

    Args:
        bank_name: Name of the bank

    Returns:
        Base64 encoded logo string or None
    """
    if bank_name not in BANK_LOGO_MAP:
        return None

    logo_filename = BANK_LOGO_MAP[bank_name]
    logo_path = LOGOS_PATH / logo_filename
    return get_base64_image(str(logo_path))


@st.cache_data
def get_all_bank_logos(bank_names: tuple) -> Dict[str, str]:
    """
    Get logos for multiple banks (cached - requires tuple for hashability)

    Args:
        bank_names: Tuple of bank names

    Returns:
        Dictionary with bank names as keys and base64 logos as values
    """
    logos = {}
    for bank_name in bank_names:
        logo = get_bank_logo(bank_name)
        if logo:
            logos[bank_name] = logo
    return logos
