"""
Beautiful Streamlit Dashboard for Ads Auto-Reporting System.

Modern, interactive UI with:
- Real-time KPI cards
- Interactive charts
- Date range filters
- Campaign comparisons
- Platform breakdowns
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from ..analytics.kpi_calculator import KPICalculator
from ..analytics.aggregator import DataAggregator
from ..analytics.creator_analytics import CreatorAnalytics
from ..models.enums import ReportPeriod, AdPlatform
from ..utils.helpers import format_currency, format_percentage

# Page config
st.set_page_config(
    page_title="Ads Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


class StreamlitDashboard:
    """Streamlit-based dashboard for ads performance visualization."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize dashboard with data.
        
        Args:
            df: Normalized DataFrame with ad performance data
        """
        self.df = df
        self.kpi_calculator = KPICalculator()
        self.aggregator = DataAggregator()
        self.creator_analytics = CreatorAnalytics()
        
    def run(self):
        """Run the Streamlit dashboard."""
        
        # Header
        st.markdown('<h1 class="main-header">📊 Ads Performance Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar filters
        self._render_sidebar()
        
        # Apply filters
        filtered_df = self._apply_filters()
        
        if filtered_df.empty:
            st.warning("No data available for the selected filters.")
            return
        
        # Get comparison data if enabled
        comparison_df = None
        if st.session_state.get('enable_comparison', False):
            comparison_df = self._get_previous_period_data(filtered_df)
        
        # Check if creator/video data is available
        has_creator_data = self.creator_analytics.has_creator_data(filtered_df)
        has_video_data = self.creator_analytics.has_video_data(filtered_df)
        
        # Main content with tabs (add Creators tab if data available)
        if has_creator_data or has_video_data:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview", 
                "📈 Performance", 
                "🎯 Campaigns",
                "👤 Creators",
                "📋 Detailed Analysis"
            ])
        else:
            tab1, tab2, tab3, tab5 = st.tabs([
                "📊 Overview", 
                "📈 Performance", 
                "🎯 Campaigns", 
                "📋 Detailed Analysis"
            ])
            tab4 = None
        
        with tab1:
            self._render_overview_tab(filtered_df, comparison_df)
        
        with tab2:
            self._render_performance_tab(filtered_df)
        
        with tab3:
            self._render_campaigns_tab(filtered_df)
        
        if tab4 is not None:
            with tab4:
                self._render_creators_tab(filtered_df)
        
        with tab5:
            self._render_detailed_tab(filtered_df)
        
    def _render_sidebar(self):
        """Render sidebar with filters and presets."""
        st.sidebar.header("🎛️ Filters & Controls")
        
        # Date range with presets
        with st.sidebar.expander("📅 Date Range", expanded=True):
            # Convert pandas timestamps to date objects
            min_date = pd.Timestamp(self.df['date'].min()).date()
            max_date = pd.Timestamp(self.df['date'].max()).date()
            
            # Preset date ranges
            st.caption("Quick Presets:")
            col1, col2, col3 = st.columns(3)
            
            if col1.button("Last 7d", use_container_width=True):
                # Ensure dates are within data range
                preset_start = max(max_date - timedelta(days=7), min_date)
                st.session_state['start_date'] = preset_start
                st.session_state['end_date'] = max_date
                st.rerun()
            if col2.button("Last 30d", use_container_width=True):
                preset_start = max(max_date - timedelta(days=30), min_date)
                st.session_state['start_date'] = preset_start
                st.session_state['end_date'] = max_date
                st.rerun()
            if col3.button("Last 90d", use_container_width=True):
                preset_start = max(max_date - timedelta(days=90), min_date)
                st.session_state['start_date'] = preset_start
                st.session_state['end_date'] = max_date
                st.rerun()
            
            # Custom date picker - ensure defaults are within range
            default_start = st.session_state.get('start_date', min_date)
            default_end = st.session_state.get('end_date', max_date)
            
            # Clamp defaults to valid range
            if isinstance(default_start, pd.Timestamp):
                default_start = default_start.date()
            if isinstance(default_end, pd.Timestamp):
                default_end = default_end.date()
            
            default_start = max(min_date, min(default_start, max_date))
            default_end = max(min_date, min(default_end, max_date))
            
            date_range = st.date_input(
                "Custom Range",
                value=(default_start, default_end),
                min_value=min_date,
                max_value=max_date,
                help="Select a custom date range for analysis"
            )
            
            if len(date_range) == 2:
                st.session_state['start_date'] = date_range[0]
                st.session_state['end_date'] = date_range[1]
        
        # Platform filter
        with st.sidebar.expander("🌐 Platform", expanded=True):
            platforms = ['All'] + sorted(self.df['platform'].unique().tolist())
            selected_platform = st.selectbox(
                "Select Platform",
                platforms,
                key='platform_select',
                help="Filter data by advertising platform"
            )
            st.session_state['platform'] = selected_platform
        
        # Campaign filter
        with st.sidebar.expander("🎯 Campaign", expanded=False):
            campaigns = ['All'] + sorted(self.df['campaign'].unique().tolist())
            selected_campaign = st.selectbox(
                "Select Campaign",
                campaigns,
                key='campaign_select',
                help="Filter data by specific campaign"
            )
            st.session_state['campaign'] = selected_campaign
        
        # View settings
        with st.sidebar.expander("📊 View Settings", expanded=True):
            period = st.radio(
                "Aggregation Period",
                ['Daily', 'Weekly', 'Monthly'],
                help="Choose how to aggregate time-series data"
            )
            st.session_state['period'] = period
            
            # Comparison toggle
            enable_comparison = st.checkbox(
                "Compare with Previous Period",
                value=False,
                help="Show period-over-period comparison"
            )
            st.session_state['enable_comparison'] = enable_comparison
        
        # Quick stats
        st.sidebar.markdown("---")
        with st.sidebar.expander("📈 Quick Stats", expanded=True):
            st.metric("📊 Total Records", f"{len(self.df):,}", help="Total data points loaded")
            st.metric("🎯 Campaigns", self.df['campaign'].nunique(), help="Unique campaigns")
            st.metric("📅 Days", f"{(max_date - min_date).days + 1}", help="Date range span")
        
    def _apply_filters(self) -> pd.DataFrame:
        """Apply filters to dataframe."""
        df = self.df.copy()
        
        # Date filter
        if 'start_date' in st.session_state and 'end_date' in st.session_state:
            df = self.aggregator.filter_date_range(
                df,
                st.session_state['start_date'],
                st.session_state['end_date']
            )
        
        # Platform filter
        if st.session_state.get('platform', 'All') != 'All':
            df = df[df['platform'] == st.session_state['platform']]
        
        # Campaign filter
        if st.session_state.get('campaign', 'All') != 'All':
            df = df[df['campaign'] == st.session_state['campaign']]
        
        return df
    
    def _render_kpi_cards(self, df: pd.DataFrame):
        """Render KPI metric cards."""
        st.subheader("📊 Key Performance Indicators")
        
        # Calculate metrics
        total_spend = df['spend'].sum()
        total_revenue = df['revenue'].sum()
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_conversions = df['conversions'].sum()
        
        roas = self.kpi_calculator._calculate_roas(total_spend, total_revenue)
        cpc = self.kpi_calculator._calculate_cpc(total_spend, total_clicks)
        cpm = self.kpi_calculator._calculate_cpm(total_spend, total_impressions)
        cpp = self.kpi_calculator._calculate_cpp(total_spend, total_conversions)
        ctr = self.kpi_calculator._calculate_ctr(total_impressions, total_clicks)
        cvr = self.kpi_calculator._calculate_cvr(total_clicks, total_conversions)
        
        # Display in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Spend", format_currency(total_spend))
            st.metric("💵 Total Revenue", format_currency(total_revenue))
        
        with col2:
            delta_color = "normal" if roas >= 3.0 else "inverse"
            st.metric("📈 ROAS", f"{roas:.2f}x", delta=f"{'✅' if roas >= 3.0 else '⚠️'}")
            st.metric("🎯 Conversions", f"{total_conversions:,}")
        
        with col3:
            st.metric("🖱️ CPC", format_currency(cpc))
            st.metric("📺 CPM", format_currency(cpm))
        
        with col4:
            st.metric("🛒 CPP", format_currency(cpp))
            st.metric("👆 CTR", format_percentage(ctr))
        
    def _render_revenue_chart(self, df: pd.DataFrame):
        """Render revenue vs spend chart."""
        
        # Aggregate by period
        period_map = {'Daily': ReportPeriod.DAILY, 'Weekly': ReportPeriod.WEEKLY, 'Monthly': ReportPeriod.MONTHLY}
        period = period_map.get(st.session_state.get('period', 'Daily'), ReportPeriod.DAILY)
        
        daily_df = self.aggregator.aggregate_by_period(df, period)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['revenue'],
            name='Revenue',
            line=dict(color='#2ecc71', width=3),
            fill='tonexty',
            fillcolor='rgba(46, 204, 113, 0.2)'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['spend'],
            name='Spend',
            line=dict(color='#e74c3c', width=3),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)'
        ))
        
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_roas_chart(self, df: pd.DataFrame):
        """Render ROAS trend chart."""
        
        # Aggregate by period
        period_map = {'Daily': ReportPeriod.DAILY, 'Weekly': ReportPeriod.WEEKLY, 'Monthly': ReportPeriod.MONTHLY}
        period = period_map.get(st.session_state.get('period', 'Daily'), ReportPeriod.DAILY)
        
        daily_df = self.aggregator.aggregate_by_period(df, period)
        daily_df['roas'] = daily_df.apply(
            lambda row: self.kpi_calculator._calculate_roas(row['spend'], row['revenue']),
            axis=1
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['roas'],
            name='ROAS',
            line=dict(color='#3498db', width=3),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.3)'
        ))
        
        # Target line
        fig.add_hline(
            y=3.0,
            line_dash="dash",
            line_color="green",
            annotation_text="Target: 3.0x",
            annotation_position="right"
        )
        
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=400,
            yaxis_title="ROAS",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_platform_breakdown(self, df: pd.DataFrame):
        """Render platform performance breakdown."""
        
        platform_data = df.groupby('platform').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Create tabs for different metrics
        tab1, tab2, tab3 = st.tabs(["Spend", "Revenue", "Conversions"])
        
        with tab1:
            fig = px.pie(
                platform_data,
                values='spend',
                names='platform',
                color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig = px.pie(
                platform_data,
                values='revenue',
                names='platform',
                color_discrete_sequence=['#2ecc71', '#9b59b6', '#1abc9c']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            fig = px.pie(
                platform_data,
                values='conversions',
                names='platform',
                color_discrete_sequence=['#f39c12', '#34495e', '#16a085']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_conversion_funnel(self, df: pd.DataFrame):
        """Render conversion funnel."""
        
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_conversions = df['conversions'].sum()
        
        fig = go.Figure(go.Funnel(
            y=['Impressions', 'Clicks', 'Conversions'],
            x=[total_impressions, total_clicks, total_conversions],
            textinfo="value+percent initial",
            marker=dict(color=['#3498db', '#f39c12', '#2ecc71'])
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_top_campaigns(self, df: pd.DataFrame):
        """Render top campaigns chart."""
        
        summaries = self.kpi_calculator.calculate_multiple_campaigns(df)
        top_10 = sorted(summaries, key=lambda x: x.total_revenue, reverse=True)[:10]
        
        campaigns = [s.campaign for s in top_10]
        revenues = [s.total_revenue for s in top_10]
        roas_values = [s.roas for s in top_10]
        
        fig = go.Figure()
        
        # Bar chart for revenue
        fig.add_trace(go.Bar(
            x=campaigns,
            y=revenues,
            name='Revenue',
            marker_color='#2ecc71',
            text=[format_currency(r) for r in revenues],
            textposition='outside'
        ))
        
        fig.update_layout(
            xaxis_tickangle=-45,
            template='plotly_white',
            height=500,
            showlegend=False,
            yaxis_title="Revenue ($)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show ROAS comparison
        st.subheader("📊 ROAS Comparison")
        roas_df = pd.DataFrame({
            'Campaign': campaigns,
            'ROAS': roas_values
        })
        
        # Color code by performance
        roas_df['Performance'] = roas_df['ROAS'].apply(
            lambda x: '🟢 Excellent' if x >= 5 else '🟡 Good' if x >= 3 else '🔴 Needs Improvement'
        )
        
        st.dataframe(
            roas_df,
            use_container_width=True,
            hide_index=True
        )
    
    def _render_campaign_table(self, df: pd.DataFrame):
        """Render detailed campaign table."""
        
        summaries = self.kpi_calculator.calculate_multiple_campaigns(df)
        
        # Create dataframe
        table_data = []
        for s in summaries:
            table_data.append({
                'Campaign': s.campaign,
                'Platform': s.platform.value.upper(),
                'Spend': format_currency(s.total_spend),
                'Revenue': format_currency(s.total_revenue),
                'ROAS': f"{s.roas:.2f}x",
                'Conversions': s.total_conversions,
                'CPC': format_currency(s.cpc),
                'CPP': format_currency(s.cpp),
                'CTR': format_percentage(s.ctr),
                'CVR': format_percentage(s.cvr)
            })
        
        table_df = pd.DataFrame(table_data)
        
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = table_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Campaign Data (CSV)",
            data=csv,
            file_name=f"campaign_data_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


    def _get_previous_period_data(self, current_df: pd.DataFrame) -> pd.DataFrame:
        """Get data from the previous period for comparison."""
        if current_df.empty:
            return pd.DataFrame()
        
        # Calculate period length - ensure we're working with Timestamps
        start = pd.Timestamp(current_df['date'].min())
        end = pd.Timestamp(current_df['date'].max())
        period_days = (end - start).days + 1
        
        # Get previous period as Timestamps
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_days - 1)
        
        # Filter to previous period (comparing Timestamp to Timestamp)
        prev_df = self.df[
            (pd.to_datetime(self.df['date']) >= prev_start) & 
            (pd.to_datetime(self.df['date']) <= prev_end)
        ].copy()
        
        return prev_df
    
    def _render_overview_tab(self, df: pd.DataFrame, comparison_df: Optional[pd.DataFrame]):
        """Render overview tab with KPIs and high-level metrics."""
        st.subheader("📊 Key Performance Indicators")
        
        # Calculate current metrics
        current_metrics = self._calculate_metrics(df)
        
        # Calculate comparison if available
        if comparison_df is not None and not comparison_df.empty:
            prev_metrics = self._calculate_metrics(comparison_df)
            st.caption("📆 Comparing with previous period")
        else:
            prev_metrics = None
        
        # Render KPI cards with comparisons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_metric_card(
                "💰 Total Spend", 
                current_metrics['spend'],
                prev_metrics['spend'] if prev_metrics else None,
                format_type='currency'
            )
            self._render_metric_card(
                "🖱️ CPC", 
                current_metrics['cpc'],
                prev_metrics['cpc'] if prev_metrics else None,
                format_type='currency',
                help_text="Cost Per Click - lower is better"
            )
        
        with col2:
            self._render_metric_card(
                "💵 Total Revenue", 
                current_metrics['revenue'],
                prev_metrics['revenue'] if prev_metrics else None,
                format_type='currency'
            )
            self._render_metric_card(
                "📺 CPM", 
                current_metrics['cpm'],
                prev_metrics['cpm'] if prev_metrics else None,
                format_type='currency',
                help_text="Cost Per 1000 Impressions"
            )
        
        with col3:
            self._render_metric_card(
                "📈 ROAS", 
                current_metrics['roas'],
                prev_metrics['roas'] if prev_metrics else None,
                format_type='multiplier',
                help_text="Return on Ad Spend - target: 3.0x"
            )
            self._render_metric_card(
                "🛒 CPP", 
                current_metrics['cpp'],
                prev_metrics['cpp'] if prev_metrics else None,
                format_type='currency',
                help_text="Cost Per Purchase/Conversion"
            )
        
        with col4:
            self._render_metric_card(
                "🎯 Conversions", 
                current_metrics['conversions'],
                prev_metrics['conversions'] if prev_metrics else None,
                format_type='number'
            )
            self._render_metric_card(
                "👆 CTR", 
                current_metrics['ctr'],
                prev_metrics['ctr'] if prev_metrics else None,
                format_type='percentage',
                help_text="Click Through Rate"
            )
        
        st.markdown("---")
        
        # Revenue & Spend Chart
        st.subheader("💹 Revenue vs Spend Trend")
        self._render_revenue_chart(df)
        
        # Export button
        st.download_button(
            label="📥 Export Overview Data (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"overview_data_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def _render_performance_tab(self, df: pd.DataFrame):
        """Render performance tab with detailed charts."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 ROAS Trend")
            self._render_roas_chart(df)
        
        with col2:
            st.subheader("🎯 Conversion Funnel")
            self._render_conversion_funnel(df)
        
        st.markdown("---")
        
        st.subheader("🌐 Platform Performance Comparison")
        self._render_platform_stacked_bars(df)
        
        # Export button
        col1, col2 = st.columns([3, 1])
        with col2:
            platform_summary = df.groupby('platform').agg({
                'spend': 'sum',
                'revenue': 'sum',
                'conversions': 'sum'
            }).reset_index()
            st.download_button(
                label="📥 Export Platform Data",
                data=platform_summary.to_csv(index=False).encode('utf-8'),
                file_name=f"platform_performance_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    def _render_campaigns_tab(self, df: pd.DataFrame):
        """Render campaigns tab with top performers."""
        st.subheader("🏆 Top Performing Campaigns")
        
        summaries = self.kpi_calculator.calculate_multiple_campaigns(df)
        top_10 = sorted(summaries, key=lambda x: x.total_revenue, reverse=True)[:10]
        
        # Stacked bar chart for top campaigns
        campaigns = [s.campaign[:30] for s in top_10]  # Truncate long names
        revenues = [s.total_revenue for s in top_10]
        spends = [s.total_spend for s in top_10]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Revenue',
            y=campaigns,
            x=revenues,
            orientation='h',
            marker_color='#2ecc71',
            text=[format_currency(r) for r in revenues],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Spend',
            y=campaigns,
            x=spends,
            orientation='h',
            marker_color='#e74c3c',
            text=[format_currency(s) for s in spends],
            textposition='auto'
        ))
        
        fig.update_layout(
            barmode='group',
            template='plotly_white',
            height=500,
            xaxis_title="Amount ($)",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ROAS Performance Table
        st.subheader("📊 Campaign ROAS Analysis")
        roas_data = []
        for s in top_10:
            roas_data.append({
                'Campaign': s.campaign,
                'Platform': s.platform.value.upper(),
                'ROAS': f"{s.roas:.2f}x",
                'Performance': '🟢 Excellent' if s.roas >= 5 else '🟡 Good' if s.roas >= 3 else '🔴 Needs Work',
                'Revenue': format_currency(s.total_revenue),
                'Spend': format_currency(s.total_spend)
            })
        
        roas_df = pd.DataFrame(roas_data)
        st.dataframe(roas_df, use_container_width=True, hide_index=True)
        
        # Export button
        st.download_button(
            label="📥 Export Campaign Summary (CSV)",
            data=roas_df.to_csv(index=False).encode('utf-8'),
            file_name=f"campaign_summary_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def _render_creators_tab(self, df: pd.DataFrame):
        """Render creators/video performance tab."""
        st.subheader("👤 Creator & Video Performance")
        
        has_creator = self.creator_analytics.has_creator_data(df)
        has_video = self.creator_analytics.has_video_data(df)
        
        if not has_creator and not has_video:
            st.info("📝 **No creator or video data available.**\n\nTo track creator performance, add a `creator_name` column to your CSV.\n\nTo track video performance, add `video_id` or `video_name` columns.")
            return
        
        # Creator Performance Section
        if has_creator:
            st.markdown("### 🏆 Top Creators Leaderboard")
            
            # Metric selector
            col1, col2 = st.columns([3, 1])
            with col2:
                sort_metric = st.selectbox(
                    "Sort by",
                    ['roas', 'total_revenue', 'total_conversions', 'ctr', 'cvr'],
                    format_func=lambda x: {
                        'roas': 'ROAS',
                        'total_revenue': 'Revenue',
                        'total_conversions': 'Conversions',
                        'ctr': 'CTR',
                        'cvr': 'CVR'
                    }[x]
                )
            
            # Get top creators
            top_creators = self.creator_analytics.get_creator_leaderboard(
                df, 
                metric=sort_metric,
                top_n=10
            )
            
            if top_creators:
                # Create leaderboard chart
                creators = [c.creator_name[:30] for c in top_creators]
                revenues = [c.total_revenue for c in top_creators]
                spends = [c.total_spend for c in top_creators]
                roas_values = [c.roas for c in top_creators]
                
                fig = go.Figure()
                
                # Revenue bars
                fig.add_trace(go.Bar(
                    name='Revenue',
                    y=creators,
                    x=revenues,
                    orientation='h',
                    marker_color='#2ecc71',
                    text=[format_currency(r) for r in revenues],
                    textposition='auto'
                ))
                
                # Spend bars
                fig.add_trace(go.Bar(
                    name='Spend',
                    y=creators,
                    x=spends,
                    orientation='h',
                    marker_color='#e74c3c',
                    text=[format_currency(s) for s in spends],
                    textposition='auto'
                ))
                
                fig.update_layout(
                    barmode='group',
                    template='plotly_white',
                    height=500,
                    xaxis_title="Amount ($)",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Creator performance table
                st.markdown("### 📊 Creator Performance Details")
                creator_data = []
                for c in top_creators:
                    perf_indicator = '🟢 Excellent' if c.roas >= 5 else '🟡 Good' if c.roas >= 3 else '🔴 Needs Work'
                    creator_data.append({
                        'Creator': c.creator_name,
                        'Videos': c.total_videos,
                        'ROAS': f"{c.roas:.2f}x",
                        'Performance': perf_indicator,
                        'Revenue': format_currency(c.total_revenue),
                        'Spend': format_currency(c.total_spend),
                        'CTR': format_percentage(c.ctr),
                        'Platforms': ', '.join([p.upper() for p in c.platforms]),
                        'Best Video': c.best_video[:40] if c.best_video else 'N/A'
                    })
                
                creator_df = pd.DataFrame(creator_data)
                st.dataframe(creator_df, use_container_width=True, hide_index=True)
                
                # Export button
                st.download_button(
                    label="📥 Export Creator Performance (CSV)",
                    data=creator_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"creator_performance_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No creator data found in the filtered dataset.")
        
        st.markdown("---")
        
        # Video Performance Section
        if has_video:
            st.markdown("### 🎬 Top Performing Videos")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                # Creator filter for videos
                if has_creator:
                    creators = ['All'] + sorted(df['creator_name'].dropna().unique().tolist())
                    selected_creator = st.selectbox(
                        "Filter by Creator",
                        creators,
                        key='video_creator_filter'
                    )
                    creator_filter = None if selected_creator == 'All' else selected_creator
                else:
                    creator_filter = None
            
            with col2:
                video_sort_metric = st.selectbox(
                    "Sort by",
                    ['roas', 'total_revenue', 'total_conversions'],
                    format_func=lambda x: {
                        'roas': 'ROAS',
                        'total_revenue': 'Revenue',
                        'total_conversions': 'Conversions'
                    }[x],
                    key='video_sort'
                )
            
            with col3:
                video_count = st.number_input(
                    "Show top",
                    min_value=5,
                    max_value=50,
                    value=20,
                    step=5
                )
            
            # Get top videos
            top_videos = self.creator_analytics.get_video_leaderboard(
                df,
                metric=video_sort_metric,
                top_n=video_count,
                creator=creator_filter
            )
            
            if top_videos:
                # Video performance table
                video_data = []
                for v in top_videos:
                    video_data.append({
                        'Video': v.video_name[:50],
                        'Creator': v.creator_name,
                        'Platform': v.platform.upper(),
                        'ROAS': f"{v.roas:.2f}x",
                        'Revenue': format_currency(v.total_revenue),
                        'Spend': format_currency(v.total_spend),
                        'Conversions': f"{v.total_conversions:,}",
                        'CTR': format_percentage(v.ctr),
                        'Days Active': v.days_active
                    })
                
                video_df = pd.DataFrame(video_data)
                st.dataframe(video_df, use_container_width=True, hide_index=True)
                
                # Export button
                st.download_button(
                    label="📥 Export Video Performance (CSV)",
                    data=video_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"video_performance_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No video data found for the selected filters.")
    
    def _render_detailed_tab(self, df: pd.DataFrame):
        """Render detailed analysis tab with full campaign table."""
        st.subheader("📋 Complete Campaign Analysis")
        
        self._render_campaign_table(df)
    
    def _calculate_metrics(self, df: pd.DataFrame) -> dict:
        """Calculate all metrics for a dataframe."""
        total_spend = df['spend'].sum()
        total_revenue = df['revenue'].sum()
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_conversions = df['conversions'].sum()
        
        return {
            'spend': total_spend,
            'revenue': total_revenue,
            'impressions': total_impressions,
            'clicks': total_clicks,
            'conversions': total_conversions,
            'roas': self.kpi_calculator._calculate_roas(total_spend, total_revenue),
            'cpc': self.kpi_calculator._calculate_cpc(total_spend, total_clicks),
            'cpm': self.kpi_calculator._calculate_cpm(total_spend, total_impressions),
            'cpp': self.kpi_calculator._calculate_cpp(total_spend, total_conversions),
            'ctr': self.kpi_calculator._calculate_ctr(total_impressions, total_clicks),
            'cvr': self.kpi_calculator._calculate_cvr(total_clicks, total_conversions)
        }
    
    def _render_metric_card(self, label: str, value: float, prev_value: Optional[float] = None, 
                           format_type: str = 'number', help_text: Optional[str] = None):
        """Render a metric card with optional comparison."""
        if format_type == 'currency':
            formatted_value = format_currency(value)
        elif format_type == 'percentage':
            formatted_value = format_percentage(value)
        elif format_type == 'multiplier':
            formatted_value = f"{value:.2f}x"
        else:
            formatted_value = f"{value:,.0f}"
        
        # Calculate delta if comparison available
        delta = None
        delta_color = "off"
        if prev_value is not None and prev_value != 0:
            pct_change = ((value - prev_value) / prev_value) * 100
            delta = f"{pct_change:+.1f}%"
            delta_color = "normal" if pct_change >= 0 else "inverse"
        
        st.metric(
            label=label,
            value=formatted_value,
            delta=delta,
            delta_color=delta_color,
            help=help_text
        )
    
    def _render_platform_stacked_bars(self, df: pd.DataFrame):
        """Render platform performance as stacked bars."""
        platform_data = df.groupby('platform').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Spend',
            x=platform_data['platform'],
            y=platform_data['spend'],
            marker_color='#e74c3c',
            text=[format_currency(s) for s in platform_data['spend']],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Revenue',
            x=platform_data['platform'],
            y=platform_data['revenue'],
            marker_color='#2ecc71',
            text=[format_currency(r) for r in platform_data['revenue']],
            textposition='auto'
        ))
        
        fig.update_layout(
            barmode='group',
            template='plotly_white',
            height=400,
            yaxis_title="Amount ($)",
            xaxis_title="Platform",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)


def run_streamlit_dashboard(df: pd.DataFrame):
    """
    Run the Streamlit dashboard.
    
    Args:
        df: Normalized DataFrame with ad performance data
    """
    dashboard = StreamlitDashboard(df)
    dashboard.run()

