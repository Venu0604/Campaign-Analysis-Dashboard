"""
Data processing module for campaign analytics
Handles MIS data processing and campaign metric calculations
"""

import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any, Tuple
from utils.helpers import (
    find_column,
    get_channel_cost,
    calculate_metrics,
    normalize_dataframe_columns,
    get_status_counts
)


class CampaignDataProcessor:
    """Main class for processing campaign data"""

    def __init__(self, bank_config):
        """
        Initialize processor with bank configuration

        Args:
            bank_config: Bank-specific configuration dictionary
        """
        self.bank_config = bank_config
        self.df_summary = None
        self.df_matched_mis = None

    def process_campaign_data(self, df_identifiers, df_mis):
        """
        Process campaign data and generate summary

        Args:
            df_identifiers: DataFrame with campaign identifiers
            df_mis: DataFrame with MIS data

        Returns:
            Tuple of (summary_df, matched_mis_df)
        """
        # Normalize MIS columns
        df_mis = normalize_dataframe_columns(df_mis)

        # Find required columns
        identifier_col = find_column(df_mis, self.bank_config["identifier_column"])
        status_col = find_column(df_mis, self.bank_config["status_column"])
        ipa_col = find_column(df_mis, self.bank_config.get("ipa_column", ""))

        # Special handling for RBL (has OPS status column)
        ops_status_col = None
        if "ops_status_column" in self.bank_config:
            ops_status_col = find_column(df_mis, self.bank_config["ops_status_column"])

        if not identifier_col:
            st.error(f"❌ {self.bank_config['identifier_column']} column not found in MIS file")
            return None, None

        output_rows = []
        matched_mis_records = []

        # Process each campaign
        for _, row in df_identifiers.iterrows():
            campaign_data = self._process_single_campaign(
                row, df_mis, identifier_col, status_col, ipa_col, ops_status_col
            )

            if campaign_data:
                output_rows.append(campaign_data['summary'])

                if campaign_data['matched_records'] is not None:
                    matched_mis_records.append(campaign_data['matched_records'])

        # Create summary DataFrame
        self.df_summary = pd.DataFrame(output_rows)
        self.df_summary['Date'] = pd.to_datetime(self.df_summary['Date'], errors='coerce')

        # Combine matched MIS records
        if matched_mis_records:
            self.df_matched_mis = pd.concat(matched_mis_records, ignore_index=True)
            self.df_matched_mis = self._fix_duplicate_columns(self.df_matched_mis)
        else:
            self.df_matched_mis = pd.DataFrame()

        return self.df_summary, self.df_matched_mis

    def _process_single_campaign(self, row, df_mis, identifier_col, status_col, ipa_col, ops_status_col):
        """
        Process a single campaign row
        """
        date = row.get("Date", "")

        # Handle HDFC special case
        if "LC Code" in row.index:
            identifier = str(row.get("LC Code", "")).strip()
        elif "Identifiers" in row.index:
            identifier = str(row.get("Identifiers", "")).strip()
        else:
            identifier = ""

        source = str(row.get("Source", "")).strip()
        channel = str(row.get("Channel", "")).strip()
        delivered = float(row.get("Delivered", 0))
        clicks = float(row.get("Clicks", 0))
        read_count = float(row.get("Read", 0))

        cost_per_unit = get_channel_cost(channel)

        # Filter MIS data
        mask = df_mis[identifier_col].astype(str).str.contains(identifier, case=False, na=False)
        df_filtered_mis = df_mis[mask]

        matched_records = None
        if len(df_filtered_mis) > 0:
            matched_records = df_filtered_mis.copy()
            matched_records['Matched_Identifier'] = identifier
            matched_records['Campaign_Date'] = date
            matched_records['Campaign_Source'] = source
            matched_records['Campaign_Channel'] = channel

        applications = len(df_filtered_mis)

        status_metrics = self._calculate_status_metrics(
            df_filtered_mis, status_col, ipa_col, ops_status_col
        )

        perf_metrics = calculate_metrics(
            delivered, clicks, read_count, cost_per_unit,
            applications, status_metrics['ipa_approved'], status_metrics['card_out']
        )

        summary = {
            "Date": date,
            "Campaign name": identifier,
            "Source": source,
            "Applications": applications,
            "IPA Approved": status_metrics['ipa_approved'],
            "Declined": status_metrics['declined'],
            "In Progress": status_metrics['in_progress'],
            "Card Out": status_metrics['card_out'],
            "Delivered": delivered,
            "Read": read_count,
            "Clicks": clicks,
            "CTR (%)": perf_metrics['ctr'],
            "Read Rate (%)": perf_metrics['read_rate'],
            "CPC (₹)": perf_metrics['cpc'],
            "Cost per unit (₹)": cost_per_unit,
            "Total cost (₹)": float(perf_metrics['total_cost']),
            "Cost per Application (₹)": float(perf_metrics['cost_per_app']),
            "Cost per IPA (₹)": float(perf_metrics['cost_per_ipa']),
            "Cost per Card Out (₹)": float(perf_metrics['cost_per_card']),
            "Channel": channel
        }

        return {
            'summary': summary,
            'matched_records': matched_records
        }

    def _calculate_status_metrics(self, df_filtered, status_col, ipa_col, ops_status_col):
        """
        Calculate status-based metrics (card out, declined, IPA approved)
        """
        applications = len(df_filtered)
        card_out = 0
        declined = 0
        ipa_approved = 0

        # Card Out calculation
        if ops_status_col and ops_status_col in df_filtered.columns:
            card_out = get_status_counts(
                df_filtered, ops_status_col, self.bank_config["card_out_status"]
            )
        elif status_col and status_col in df_filtered.columns:
            card_out = get_status_counts(
                df_filtered, status_col, self.bank_config["card_out_status"]
            )

        # Declined calculation
        if status_col and status_col in df_filtered.columns:
            declined = get_status_counts(
                df_filtered, status_col, self.bank_config["declined_status"]
            )

        # IPA Approved calculation
        if ipa_col and ipa_col in df_filtered.columns:
            ipa_approved = get_status_counts(
                df_filtered, ipa_col, self.bank_config["ipa_approved_status"]
            )
        else:
            ipa_approved = card_out

        in_progress = applications - card_out - declined

        return {
            'card_out': card_out,
            'declined': declined,
            'ipa_approved': ipa_approved,
            'in_progress': in_progress
        }

    def get_summary_statistics(self, df_filtered: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate aggregate statistics for filtered data (optimized)

        Args:
            df_filtered: Filtered DataFrame to analyze

        Returns:
            Dictionary with summary statistics
        """
        if df_filtered is None or len(df_filtered) == 0:
            return self._empty_statistics()

        # Work on a copy to avoid modifying original
        df_work = df_filtered.copy()

        # Step 1: Clean and ensure numeric Total cost (₹) - optimized
        if "Total cost (₹)" in df_work.columns:
            # More efficient: convert directly to numeric, coercing errors
            total_cost_col = df_work["Total cost (₹)"]

            # Only apply string operations if not already numeric
            if total_cost_col.dtype == 'object':
                df_work["Total cost (₹)"] = pd.to_numeric(
                    total_cost_col.astype(str).str.replace(r'[₹,\s]', '', regex=True),
                    errors="coerce"
                ).fillna(0)

        # Step 2: Calculate totals (vectorized operations)
        total_apps = int(df_work["Applications"].sum())
        total_cost = float(df_work["Total cost (₹)"].sum())
        total_ipa_approved = int(df_work["IPA Approved"].sum())
        total_card_out = int(df_work["Card Out"].sum())
        total_declined = int(df_work["Declined"].sum())

        # Step 3: Derived metrics with safe division
        avg_cpa = total_cost / total_apps if total_apps > 0 else 0.0
        avg_ctr = float(df_work["CTR (%)"].mean()) if len(df_work) > 0 else 0.0
        app_to_ipa_rate = (total_ipa_approved / total_apps * 100) if total_apps > 0 else 0.0
        ipa_to_card_rate = (total_card_out / total_ipa_approved * 100) if total_ipa_approved > 0 else 0.0

        # Step 4: Return numeric & formatted cost
        return {
            "total_apps": total_apps,
            "total_cost": total_cost,
            "total_cost_display": f"₹{total_cost:,.2f}",
            "total_ipa_approved": total_ipa_approved,
            "total_card_out": total_card_out,
            "total_declined": total_declined,
            "avg_cpa": avg_cpa,
            "avg_ctr": avg_ctr,
            "app_to_ipa_rate": app_to_ipa_rate,
            "ipa_to_card_rate": ipa_to_card_rate,
            "num_campaigns": len(df_work)
        }

    def _empty_statistics(self):
        """Return empty statistics dictionary"""
        return {
            'total_apps': 0,
            'total_cost': 0,
            'total_ipa_approved': 0,
            'total_card_out': 0,
            'total_declined': 0,
            'avg_cpa': 0,
            'avg_ctr': 0,
            'app_to_ipa_rate': 0,
            'ipa_to_card_rate': 0,
            'num_campaigns': 0
        }

    def _fix_duplicate_columns(self, df):
        """
        Fix duplicate column names in DataFrame
        """
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            indices = cols[cols == dup].index.values.tolist()
            cols[indices] = [f"{dup}_{i}" if i != 0 else dup for i in range(len(indices))]
        df.columns = cols
        return df

    def apply_filters(self, df, date_range=None, source=None, channel=None, campaign=None):
        """
        Apply filters to summary DataFrame
        """
        df_filtered = df.copy()

        # Date filter
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['Date'] >= pd.Timestamp(start_date)) &
                (df_filtered['Date'] <= pd.Timestamp(end_date))
            ]

        # Source filter
        if source and source != "All Sources":
            df_filtered = df_filtered[df_filtered['Source'] == source]

        # Channel filter
        if channel and channel != "All Channels":
            df_filtered = df_filtered[df_filtered['Channel'] == channel]

        # Campaign filter
        if campaign and campaign != "All Campaigns":
            df_filtered = df_filtered[df_filtered['Campaign name'] == campaign]

        return df_filtered
