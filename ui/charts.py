"""
Visualization module for campaign dashboard
Contains all chart and visualization functions
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any


class ChartBuilder:
    """Class for building dashboard visualizations with optimized configuration"""

    def __init__(self, color_scheme: Dict[str, str]):
        """
        Initialize with bank color scheme

        Args:
            color_scheme: Dictionary with primary, secondary, tertiary colors
        """
        self.colors = color_scheme
        self.template = 'plotly_dark'
        # Pre-configure base layout to avoid repetition
        self.base_layout = {
            'template': self.template,
            'paper_bgcolor': 'rgba(30, 41, 59, 0.6)',
            'plot_bgcolor': 'rgba(30, 41, 59, 0.4)',
            'font': dict(color='#e2e8f0', size=13, family='Inter'),
            'title': dict(font=dict(size=16, color='#e2e8f0', family='Inter'))
        }

    def _apply_base_layout(self, fig: go.Figure, **kwargs) -> go.Figure:
        """
        Apply base layout configuration to a figure

        Args:
            fig: Plotly figure object
            **kwargs: Additional layout parameters to override defaults

        Returns:
            Updated figure
        """
        layout_config = {**self.base_layout, **kwargs}
        fig.update_layout(**layout_config)
        return fig

    def create_time_series_chart(self, df: pd.DataFrame, date_col: str = 'Date') -> go.Figure:
        """
        Create time series performance chart

        Args:
            df: DataFrame with time series data
            date_col: Name of date column

        Returns:
            Plotly figure
        """
        df_time = df.groupby(date_col).agg({
            'Applications': 'sum',
            'IPA Approved': 'sum',
            'Card Out': 'sum'
        }).reset_index()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_time[date_col], y=df_time['Applications'],
            mode='lines+markers', name='Applications',
            line=dict(color=self.colors["primary"], width=3),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=df_time[date_col], y=df_time['IPA Approved'],
            mode='lines+markers', name='IPA Approved',
            line=dict(color=self.colors["secondary"], width=3),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=df_time[date_col], y=df_time['Card Out'],
            mode='lines+markers', name='Card Out',
            line=dict(color=self.colors["tertiary"], width=3),
            marker=dict(size=8)
        ))

        # Update trace markers for better visibility
        fig.update_traces(
            marker=dict(size=10),
            line=dict(width=3),
            textfont=dict(size=14, color='#e2e8f0')
        )

        # Use base layout instead of repeating configuration
        return self._apply_base_layout(
            fig,
            title="📈 Performance Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified',
            height=350,
            xaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=12)),
            yaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=12))
        )

    def create_ctr_distribution(self, df: pd.DataFrame) -> go.Figure:
        """
        Create CTR distribution histogram

        Args:
            df: DataFrame with CTR data

        Returns:
            Plotly figure
        """
        fig = px.histogram(
            df, x="CTR (%)", nbins=20,
            title="📊 CTR Distribution Across Campaigns",
            color_discrete_sequence=[self.colors["primary"]]
        )

        fig.update_traces(textfont=dict(size=13))

        return self._apply_base_layout(
            fig,
            xaxis_title="Click-Through Rate (%)",
            yaxis_title="Number of Campaigns",
            height=350,
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12))
        )

    def create_conversion_funnel(self, total_apps: int, total_ipa: int, total_card_out: int) -> go.Figure:
        """
        Create conversion funnel chart

        Args:
            total_apps: Total applications
            total_ipa: Total IPA approved
            total_card_out: Total cards issued

        Returns:
            Plotly figure
        """
        fig = go.Figure(go.Funnel(
            y=["Applications", "IPA Approved", "Card Out"],
            x=[total_apps, total_ipa, total_card_out],
            textposition="inside",
            textinfo="value+percent initial",
            textfont=dict(size=16, color='white', family='Inter', weight='bold'),
            marker={
                "color": [
                    self.colors["primary"],
                    self.colors["secondary"],
                    self.colors["tertiary"]
                ],
                "line": {"width": [2, 2, 2], "color": ["#1e293b", "#1e293b", "#1e293b"]}
            },
            connector={"line": {"color": "#475569", "dash": "dot", "width": 3}}
        ))

        return self._apply_base_layout(
            fig,
            title=dict(text="📊 Conversion Funnel", font=dict(size=16, color='#e2e8f0', family='Inter')),
            height=350
        )

    def create_source_performance_matrix(self, df: pd.DataFrame) -> go.Figure:
        """
        Create source performance scatter chart

        Args:
            df: DataFrame with campaign data

        Returns:
            Plotly figure
        """
        source_perf = df.groupby('Source').agg({
            'Applications': 'sum',
            'Total cost (₹)': 'sum'
        }).reset_index()

        source_perf['Cost per App'] = source_perf['Total cost (₹)'] / source_perf['Applications']

        fig = px.scatter(
            source_perf,
            x='Applications',
            y='Cost per App',
            size='Total cost (₹)',
            color='Source',
            title="💎 Source Performance Matrix",
            hover_data=['Total cost (₹)']
        )

        fig.update_traces(
            textfont=dict(size=13),
            marker=dict(size=15, line=dict(width=1, color='#1e293b'))
        )

        return self._apply_base_layout(
            fig,
            height=350,
            xaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=12)),
            yaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=12))
        )

    def create_channel_performance_bar(self, df: pd.DataFrame) -> go.Figure:
        """
        Create channel performance grouped bar chart

        Args:
            df: DataFrame with campaign data

        Returns:
            Plotly figure
        """
        channel_perf = df.groupby('Channel').agg({
            'Applications': 'sum',
            'IPA Approved': 'sum',
            'Card Out': 'sum'
        }).reset_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=channel_perf['Channel'],
            y=channel_perf['Applications'],
            name='Applications',
            marker_color=self.colors["primary"]
        ))

        fig.add_trace(go.Bar(
            x=channel_perf['Channel'],
            y=channel_perf['IPA Approved'],
            name='IPA Approved',
            marker_color=self.colors["secondary"]
        ))

        fig.add_trace(go.Bar(
            x=channel_perf['Channel'],
            y=channel_perf['Card Out'],
            name='Card Out',
            marker_color=self.colors["tertiary"]
        ))

        fig.update_traces(
            textfont=dict(size=13, color='#e2e8f0'),
            textposition='outside'
        )

        return self._apply_base_layout(
            fig,
            title="📢 Performance by Channel",
            barmode='group',
            height=350,
            xaxis=dict(tickfont=dict(size=12)),
            yaxis=dict(tickfont=dict(size=12))
        )

    def create_cost_distribution_pie(self, df):
        """
        Create cost distribution pie chart

        Args:
            df: DataFrame with campaign data

        Returns:
            Plotly figure
        """
        fig = px.pie(
            df,
            values='Total cost (₹)',
            names='Source',
            title="💸 Cost Distribution by Source",
            hole=0.4
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(size=13, family='Inter'),
            hovertemplate='<b>%{label}</b><br>Cost: ₹%{value:,.2f}<br>Share: %{percent}'
        )

        return self._apply_base_layout(
            fig,
            height=350
        )

    def create_top_campaigns_bar(self, df, top_n=10):
        """
        Create top campaigns horizontal bar chart

        Args:
            df: DataFrame with campaign data
            top_n: Number of top campaigns to show

        Returns:
            Plotly figure
        """
        top_campaigns = df.nlargest(top_n, 'Applications')[
            ['Campaign name', 'Applications', 'Total cost (₹)']
        ]

        fig = px.bar(
            top_campaigns,
            x='Applications',
            y='Campaign name',
            orientation='h',
            title=f"🏆 Top {top_n} Campaigns by Applications",
            color='Applications',
            text='Applications'
        )

        fig.update_traces(
            textposition='outside',
            textfont=dict(size=14, color='#e2e8f0', family='Inter', weight='bold')
        )

        return self._apply_base_layout(
            fig,
            height=450,
            showlegend=False,
            xaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=12)),
            yaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=11))
        )

    def create_cost_efficiency_bar(self, df, top_n=10):
        """
        Create cost efficiency horizontal bar chart

        Args:
            df: DataFrame with campaign data
            top_n: Number of campaigns to show

        Returns:
            Plotly figure
        """
        efficient_campaigns = df.nsmallest(top_n, 'Cost per Application (₹)')

        fig = px.bar(
            efficient_campaigns,
            x='Cost per Application (₹)',
            y='Campaign name',
            orientation='h',
            title=f"💰 Most Cost-Efficient Campaigns (Top {top_n})",
            color='Cost per Application (₹)',
            color_continuous_scale='Teal',
            text='Cost per Application (₹)'
        )

        fig.update_traces(
            texttemplate='₹%{text:.2f}',
            textposition='outside',
            textfont=dict(size=14, color='#e2e8f0', family='Inter', weight='bold')
        )

        return self._apply_base_layout(
            fig,
            height=450,
            showlegend=False,
            xaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=12)),
            yaxis=dict(gridcolor='#475569', color='#e2e8f0', tickfont=dict(size=11))
        )
