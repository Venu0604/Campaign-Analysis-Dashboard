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

        # Filter MIS data by date range from identifiers (unless bank config skips this)
        if not self.bank_config.get("skip_mis_date_filter", False):
            df_mis = self._filter_mis_by_date_range(df_identifiers, df_mis)

            if df_mis is None or len(df_mis) == 0:
                st.warning("⚠️ No MIS data found within the identifiers date range")
                return None, None

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
        self.df_summary['Date'] = pd.to_datetime(self.df_summary['Date'], format='%d-%m-%Y',errors='coerce')

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
        # For Scapia, always use status_column even if ops_status_column exists
        if "ipa_card_issued_status" in self.bank_config:
            # Scapia: Card Out from status_column
            if status_col and status_col in df_filtered.columns:
                card_out = get_status_counts(
                    df_filtered, status_col, self.bank_config["card_out_status"]
                )
        elif ops_status_col and ops_status_col in df_filtered.columns:
            # Other banks: Try ops_status_column first
            card_out = get_status_counts(
                df_filtered, ops_status_col, self.bank_config["card_out_status"]
            )
        elif status_col and status_col in df_filtered.columns:
            # Fallback to status_column
            card_out = get_status_counts(
                df_filtered, status_col, self.bank_config["card_out_status"]
            )

        # Declined calculation
        if status_col and status_col in df_filtered.columns:
            declined = get_status_counts(
                df_filtered, status_col, self.bank_config["declined_status"]
            )

        # IPA Approved calculation - Special logic for Scapia
        # Scapia: IPA = card_issued = "ISSUED" AND current_status = "IN_PROGRESS"
        if "ipa_card_issued_status" in self.bank_config and ops_status_col:
            # This is Scapia - use special logic
            # IPA = card_issued = "ISSUED" AND current_status = "IN_PROGRESS"
            if status_col and status_col in df_filtered.columns and ops_status_col and ops_status_col in df_filtered.columns:
                ipa_approved = len(df_filtered[
                    (df_filtered[ops_status_col].astype(str).str.upper() == "ISSUED") &
                    (df_filtered[status_col].astype(str).str.upper() == "IN_PROGRESS")
                ])
            else:
                ipa_approved = 0
        else:
            # Standard IPA calculation for other banks
            if ipa_col and ipa_col in df_filtered.columns:
                ipa_approved = get_status_counts(
                    df_filtered, ipa_col, self.bank_config["ipa_approved_status"]
                )
            else:
                # FIX: If IPA column not found, set to 0 instead of card_out
                # This prevents showing same numbers for Applications and Card Out
                ipa_approved = 0
                # Optionally log this for debugging
                if len(df_filtered) > 0:
                    st.warning(f"⚠️ IPA column '{self.bank_config.get('ipa_column', 'N/A')}' not found in MIS data. IPA Approved will be set to 0.")

        # CRITICAL FIX: In Progress calculation
        # Applications = Total count of MIS records
        # IPA Approved = Records that got IPA approval
        # Card Out = Records that got final card (subset of IPA in most cases)
        # Declined = Records that were rejected
        # In Progress = Records not yet declined and not card_out
        #
        # The correct hierarchy is:
        # Applications = Card Out + Declined + In Progress
        # (IPA Approved overlaps with Card Out and In Progress, it's not a separate bucket)
        in_progress = applications - card_out - declined

        # Ensure in_progress doesn't go negative (data quality issue)
        if in_progress < 0:
            in_progress = 0

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

    def _filter_mis_by_date_range(self, df_identifiers, df_mis):
        """
        Filter MIS data based on the date range present in identifiers sheet

        Args:
            df_identifiers: DataFrame with campaign identifiers and dates
            df_mis: DataFrame with MIS data

        Returns:
            Filtered MIS DataFrame
        """
        try:
            # Ensure identifiers Date column is datetime
            if 'Date' not in df_identifiers.columns:
                st.warning("⚠️ No Date column found in identifiers, skipping date filtering")
                return df_mis

            # Get date range from identifiers
            identifier_dates = pd.to_datetime(df_identifiers['Date'], errors='coerce')
            identifier_dates = identifier_dates.dropna()

            if len(identifier_dates) == 0:
                st.warning("⚠️ No valid dates found in identifiers, skipping date filtering")
                return df_mis

            min_date = identifier_dates.min()
            max_date = identifier_dates.max()

            st.info(f"📅 Filtering MIS data from {min_date.strftime('%d-%m-%Y')} to {max_date.strftime('%d-%m-%Y')}")

            # Find date column in MIS data
            # Common date column names in MIS files
            date_column_patterns = [
                'date', 'application_date', 'app_date', 'created_date',
                'submission_date', 'lead_date', 'application date',
                'created date', 'app date', 'lead date', 'timestamp',
                'created_at', 'application_timestamp', 'login date'
            ]

            mis_date_col = None
            for col in df_mis.columns:
                col_lower = str(col).lower().strip()
                for pattern in date_column_patterns:
                    if pattern in col_lower:
                        mis_date_col = col
                        break
                if mis_date_col:
                    break

            if mis_date_col is None:
                st.warning("⚠️ No date column found in MIS data, skipping date filtering. Processing all MIS records.")
                return df_mis

            # Convert MIS date column to datetime with multiple format attempts
            df_mis_copy = df_mis.copy()

            # Try multiple date parsing strategies
            date_parsed = False

            # Strategy 1: Try inferring format automatically
            df_mis_copy[mis_date_col] = pd.to_datetime(df_mis_copy[mis_date_col], errors='coerce')
            valid_dates = df_mis_copy[mis_date_col].notna().sum()

            # Strategy 2: If most dates are invalid, try common formats
            if valid_dates < len(df_mis_copy) * 0.5:  # Less than 50% parsed successfully
                # Try DD-MM-YYYY format
                df_mis_copy[mis_date_col] = pd.to_datetime(df_mis_copy[mis_date_col], format='%d-%m-%Y', errors='coerce')
                valid_dates = df_mis_copy[mis_date_col].notna().sum()

                if valid_dates < len(df_mis_copy) * 0.5:
                    # Try DD/MM/YYYY format
                    df_mis_copy[mis_date_col] = pd.to_datetime(df_mis_copy[mis_date_col], format='%d/%m/%Y', errors='coerce')
                    valid_dates = df_mis_copy[mis_date_col].notna().sum()

            # Check if we have any valid dates
            if valid_dates == 0:
                st.warning(f"⚠️ Could not parse dates in column '{mis_date_col}'. Processing all MIS records.")
                return df_mis

            # Filter MIS data by date range (only consider rows with valid dates)
            original_count = len(df_mis_copy)
            df_filtered = df_mis_copy[
                (df_mis_copy[mis_date_col].notna()) &
                (df_mis_copy[mis_date_col] >= min_date) &
                (df_mis_copy[mis_date_col] <= max_date)
            ]
            filtered_count = len(df_filtered)

            # If we filtered out too many records (>95%), warn and use all data
            if filtered_count < original_count * 0.05 and filtered_count < 100:
                st.warning(f"⚠️ Date filtering removed {original_count - filtered_count:,} records. This may indicate a date format mismatch. Processing all MIS records.")
                st.info(f"📊 Date range in identifiers: {min_date.strftime('%d-%m-%Y')} to {max_date.strftime('%d-%m-%Y')}")
                st.info(f"📊 Sample dates from MIS: {df_mis_copy[mis_date_col].dropna().head(3).dt.strftime('%d-%m-%Y').tolist()}")
                return df_mis

            st.success(f"✅ Filtered {filtered_count:,} records out of {original_count:,} from MIS data based on identifier dates")

            return df_filtered

        except Exception as e:
            st.warning(f"⚠️ Error during date filtering: {str(e)}. Processing all MIS records.")
            return df_mis

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
