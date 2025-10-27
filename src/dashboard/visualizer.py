"""Interactive dashboard with Plotly and Dash."""

from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from ..models.schemas import CampaignSummary
from ..analytics.kpi_calculator import KPICalculator
from ..analytics.aggregator import DataAggregator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DashboardVisualizer:
    """
    Creates interactive visualizations and dashboard for ad performance.
    
    Includes:
    - Time series charts
    - Campaign comparison
    - Platform breakdown
    - KPI cards
    - Interactive filters
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8050,
        debug: bool = False
    ):
        """
        Initialize dashboard visualizer.
        
        Args:
            host: Host address
            port: Port number
            debug: Debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.app = None
        self.df = None
        self.kpi_calculator = KPICalculator()
        self.aggregator = DataAggregator()
    
    def create_revenue_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create revenue vs spend time series chart.
        
        Args:
            df: Aggregated DataFrame with date, revenue, spend
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['revenue'],
            name='Revenue',
            line=dict(color='#2ecc71', width=3),
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['spend'],
            name='Spend',
            line=dict(color='#e74c3c', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Revenue vs Spend Over Time',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_roas_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create ROAS trend chart.
        
        Args:
            df: DataFrame with date, spend, revenue
            
        Returns:
            Plotly figure
        """
        # Calculate ROAS for each period
        df = df.copy()
        df['roas'] = df.apply(
            lambda row: self.kpi_calculator._calculate_roas(row['spend'], row['revenue']),
            axis=1
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['roas'],
            name='ROAS',
            line=dict(color='#3498db', width=3),
            mode='lines+markers',
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)'
        ))
        
        # Add target line
        fig.add_hline(
            y=3.0,
            line_dash="dash",
            line_color="green",
            annotation_text="Target ROAS"
        )
        
        fig.update_layout(
            title='Return on Ad Spend (ROAS) Trend',
            xaxis_title='Date',
            yaxis_title='ROAS',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_platform_breakdown(self, df: pd.DataFrame) -> go.Figure:
        """
        Create platform performance breakdown.
        
        Args:
            df: DataFrame with platform, spend, revenue
            
        Returns:
            Plotly figure
        """
        # Aggregate by platform
        platform_data = df.groupby('platform').agg({
            'spend': 'sum',
            'revenue': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Spend by Platform', 'Revenue by Platform', 'Conversions by Platform'),
            specs=[[{'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}]]
        )
        
        colors = ['#3498db', '#e74c3c', '#f39c12']
        
        fig.add_trace(
            go.Pie(labels=platform_data['platform'], values=platform_data['spend'], 
                   marker=dict(colors=colors), name='Spend'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(labels=platform_data['platform'], values=platform_data['revenue'],
                   marker=dict(colors=colors), name='Revenue'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Pie(labels=platform_data['platform'], values=platform_data['conversions'],
                   marker=dict(colors=colors), name='Conversions'),
            row=1, col=3
        )
        
        fig.update_layout(
            title_text='Platform Performance Breakdown',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_campaign_comparison(
        self,
        summaries: List[CampaignSummary],
        top_n: int = 10
    ) -> go.Figure:
        """
        Create top campaigns comparison chart.
        
        Args:
            summaries: List of campaign summaries
            top_n: Number of top campaigns to show
            
        Returns:
            Plotly figure
        """
        # Sort by revenue and take top N
        sorted_summaries = sorted(summaries, key=lambda x: x.total_revenue, reverse=True)[:top_n]
        
        campaigns = [s.campaign for s in sorted_summaries]
        revenues = [s.total_revenue for s in sorted_summaries]
        spends = [s.total_spend for s in sorted_summaries]
        roas_values = [s.roas for s in sorted_summaries]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Revenue & Spend by Campaign', 'ROAS by Campaign'),
            vertical_spacing=0.15,
            specs=[[{'type': 'bar'}], [{'type': 'bar'}]]
        )
        
        # Revenue and Spend bars
        fig.add_trace(
            go.Bar(name='Revenue', x=campaigns, y=revenues, marker_color='#2ecc71'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(name='Spend', x=campaigns, y=spends, marker_color='#e74c3c'),
            row=1, col=1
        )
        
        # ROAS bars with color scale
        colors = ['#2ecc71' if r >= 3.0 else '#f39c12' if r >= 2.0 else '#e74c3c' 
                  for r in roas_values]
        
        fig.add_trace(
            go.Bar(name='ROAS', x=campaigns, y=roas_values, marker_color=colors),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Campaign", row=2, col=1)
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="ROAS", row=2, col=1)
        
        fig.update_layout(
            title_text=f'Top {len(campaigns)} Campaigns Performance',
            height=700,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def create_conversion_funnel(self, df: pd.DataFrame) -> go.Figure:
        """
        Create conversion funnel visualization.
        
        Args:
            df: DataFrame with impressions, clicks, conversions
            
        Returns:
            Plotly figure
        """
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
            title='Conversion Funnel',
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    def create_kpi_cards(self, df: pd.DataFrame) -> List[Dict]:
        """
        Create KPI summary cards data.
        
        Args:
            df: Aggregated DataFrame
            
        Returns:
            List of KPI card dictionaries
        """
        total_spend = df['spend'].sum()
        total_revenue = df['revenue'].sum()
        total_conversions = df['conversions'].sum()
        total_clicks = df['clicks'].sum()
        total_impressions = df['impressions'].sum()
        
        roas = self.kpi_calculator._calculate_roas(total_spend, total_revenue)
        cpc = self.kpi_calculator._calculate_cpc(total_spend, total_clicks)
        cpp = self.kpi_calculator._calculate_cpp(total_spend, total_conversions)
        ctr = self.kpi_calculator._calculate_ctr(total_impressions, total_clicks)
        cvr = self.kpi_calculator._calculate_cvr(total_clicks, total_conversions)
        
        cards = [
            {
                'title': 'Total Spend',
                'value': f'${total_spend:,.2f}',
                'color': '#e74c3c',
                'icon': '💰'
            },
            {
                'title': 'Total Revenue',
                'value': f'${total_revenue:,.2f}',
                'color': '#2ecc71',
                'icon': '💵'
            },
            {
                'title': 'ROAS',
                'value': f'{roas:.2f}x',
                'color': '#3498db',
                'icon': '📈'
            },
            {
                'title': 'Conversions',
                'value': f'{total_conversions:,}',
                'color': '#f39c12',
                'icon': '🎯'
            },
            {
                'title': 'CPC',
                'value': f'${cpc:.2f}',
                'color': '#9b59b6',
                'icon': '🖱️'
            },
            {
                'title': 'CPP',
                'value': f'${cpp:.2f}',
                'color': '#1abc9c',
                'icon': '🛒'
            },
            {
                'title': 'CTR',
                'value': f'{ctr*100:.2f}%',
                'color': '#34495e',
                'icon': '👆'
            },
            {
                'title': 'CVR',
                'value': f'{cvr*100:.2f}%',
                'color': '#16a085',
                'icon': '✅'
            }
        ]
        
        return cards
    
    def create_dashboard(self, df: pd.DataFrame, summaries: List[CampaignSummary]):
        """
        Create interactive Dash dashboard.
        
        Args:
            df: Normalized DataFrame
            summaries: Campaign summaries
        """
        self.df = df
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        # Aggregate data by day
        from ..models.enums import ReportPeriod
        daily_df = self.aggregator.aggregate_by_period(df, ReportPeriod.DAILY)
        
        # Create KPI cards
        kpi_cards = self.create_kpi_cards(df)
        
        # Build layout
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("📊 Ads Performance Dashboard", className="text-center mb-4"), width=12)
            ]),
            
            # KPI Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(card['icon'] + ' ' + card['title'], className="card-title"),
                            html.H2(card['value'], className="card-text", style={'color': card['color']})
                        ])
                    ], className="mb-3")
                ], width=3) for card in kpi_cards
            ]),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=self.create_revenue_chart(daily_df))
                ], width=6),
                dbc.Col([
                    dcc.Graph(figure=self.create_roas_chart(daily_df))
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=self.create_platform_breakdown(df))
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=self.create_conversion_funnel(df))
                ], width=6),
                dbc.Col([
                    dcc.Graph(figure=self.create_campaign_comparison(summaries))
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.Footer(
                        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        className="text-center text-muted mt-4"
                    )
                ], width=12)
            ])
        ], fluid=True)
        
        logger.info("Dashboard created successfully")
    
    def run(self):
        """Run the dashboard server."""
        if self.app is None:
            raise RuntimeError("Dashboard not created. Call create_dashboard() first.")
        
        logger.info(f"Starting dashboard on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=self.debug)

