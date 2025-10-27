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

from ..analytics.kpi_calculator import KPICalculator
from ..analytics.aggregator import DataAggregator
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
        
        # Main content
        st.markdown("---")
        
        # KPI Cards
        self._render_kpi_cards(filtered_df)
        
        st.markdown("---")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        with col1:
            self._render_revenue_chart(filtered_df)
        with col2:
            self._render_roas_chart(filtered_df)
        
        st.markdown("---")
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        with col1:
            self._render_platform_breakdown(filtered_df)
        with col2:
            self._render_conversion_funnel(filtered_df)
        
        st.markdown("---")
        
        # Top Campaigns
        self._render_top_campaigns(filtered_df)
        
        st.markdown("---")
        
        # Campaign Details Table
        self._render_campaign_table(filtered_df)
        
    def _render_sidebar(self):
        """Render sidebar with filters."""
        st.sidebar.header("🎛️ Filters")
        
        # Date range
        st.sidebar.subheader("📅 Date Range")
        min_date = self.df['date'].min()
        max_date = self.df['date'].max()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            st.session_state['start_date'] = date_range[0]
            st.session_state['end_date'] = date_range[1]
        
        # Platform filter
        st.sidebar.subheader("🌐 Platform")
        platforms = ['All'] + sorted(self.df['platform'].unique().tolist())
        selected_platform = st.sidebar.selectbox(
            "Select Platform",
            platforms
        )
        st.session_state['platform'] = selected_platform
        
        # Campaign filter
        st.sidebar.subheader("🎯 Campaign")
        campaigns = ['All'] + sorted(self.df['campaign'].unique().tolist())
        selected_campaign = st.sidebar.selectbox(
            "Select Campaign",
            campaigns
        )
        st.session_state['campaign'] = selected_campaign
        
        # Aggregation period
        st.sidebar.subheader("📊 View")
        period = st.sidebar.radio(
            "Aggregation Period",
            ['Daily', 'Weekly', 'Monthly']
        )
        st.session_state['period'] = period
        
        # Quick stats
        st.sidebar.markdown("---")
        st.sidebar.subheader("📈 Quick Stats")
        st.sidebar.metric("Total Records", f"{len(self.df):,}")
        st.sidebar.metric("Total Campaigns", self.df['campaign'].nunique())
        st.sidebar.metric("Date Range", f"{(max_date - min_date).days + 1} days")
        
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
        st.subheader("💹 Revenue vs Spend Over Time")
        
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
        st.subheader("📊 ROAS Trend")
        
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
        st.subheader("🌐 Platform Performance")
        
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
        st.subheader("🎯 Conversion Funnel")
        
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
        st.subheader("🏆 Top 10 Campaigns by Revenue")
        
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
        st.subheader("📋 Campaign Details")
        
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


def run_streamlit_dashboard(df: pd.DataFrame):
    """
    Run the Streamlit dashboard.
    
    Args:
        df: Normalized DataFrame with ad performance data
    """
    dashboard = StreamlitDashboard(df)
    dashboard.run()

