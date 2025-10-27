"""PDF export functionality for reports."""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from ..models.schemas import CampaignSummary, WeeklyDigest
from ..utils.logger import get_logger
from ..utils.helpers import format_currency, format_percentage

logger = get_logger(__name__)


class PDFExporter:
    """
    Exports reports and visualizations to PDF format.
    
    Features:
    - Professional formatting
    - Tables and charts
    - Multi-page support
    - Custom branding
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize PDF exporter.
        
        Args:
            output_dir: Directory for PDF output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # KPI style
        self.styles.add(ParagraphStyle(
            name='KPIValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#27ae60'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def export_weekly_digest(
        self,
        digest: WeeklyDigest,
        summaries: List[CampaignSummary],
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Export weekly digest to PDF.
        
        Args:
            digest: WeeklyDigest object
            summaries: List of campaign summaries
            output_filename: Custom filename (auto-generated if None)
            
        Returns:
            Path to generated PDF
        """
        if output_filename is None:
            output_filename = f"weekly_digest_{digest.week_start.strftime('%Y%m%d')}.pdf"
        
        output_path = self.output_dir / output_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Title
        title = Paragraph(
            f"Weekly Ads Performance Digest",
            self.styles['CustomTitle']
        )
        story.append(title)
        
        # Date range
        date_range = Paragraph(
            f"{digest.week_start.strftime('%B %d, %Y')} - {digest.week_end.strftime('%B %d, %Y')}",
            self.styles['Heading3']
        )
        story.append(date_range)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        
        summary_data = [
            ['Metric', 'Value', 'WoW Change'],
            ['Total Spend', format_currency(digest.total_spend), 
             format_percentage(digest.wow_spend_change)],
            ['Total Revenue', format_currency(digest.total_revenue), 
             format_percentage(digest.wow_revenue_change)],
            ['Conversions', f'{digest.total_conversions:,}', 'N/A'],
            ['ROAS', f'{digest.overall_roas:.2f}x', 
             format_percentage(digest.wow_roas_change)]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Top Campaigns
        if digest.top_campaigns:
            story.append(Paragraph("Top Performing Campaigns", self.styles['CustomSubtitle']))
            
            campaign_data = [['Campaign', 'Platform', 'Revenue', 'ROAS', 'Conversions']]
            for camp in digest.top_campaigns[:5]:
                campaign_data.append([
                    camp.campaign[:30],  # Truncate long names
                    camp.platform.value.upper(),
                    format_currency(camp.total_revenue),
                    f'{camp.roas:.2f}x',
                    f'{camp.total_conversions:,}'
                ])
            
            campaign_table = Table(campaign_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1*inch, 1*inch])
            campaign_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            story.append(campaign_table)
            story.append(Spacer(1, 20))
        
        # Alerts
        if digest.alerts:
            story.append(PageBreak())
            story.append(Paragraph("Performance Alerts", self.styles['CustomSubtitle']))
            
            for alert in digest.alerts[:10]:  # Limit to top 10 alerts
                severity_color = {
                    'high': '#e74c3c',
                    'medium': '#f39c12',
                    'low': '#3498db'
                }.get(alert.severity, '#95a5a6')
                
                alert_text = f"<font color='{severity_color}'>[{alert.severity.upper()}]</font> {alert.message}"
                story.append(Paragraph(alert_text, self.styles['Normal']))
                story.append(Spacer(1, 8))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Exported weekly digest to {output_path}")
        return output_path
    
    def export_campaign_summary(
        self,
        summaries: List[CampaignSummary],
        start_date,
        end_date,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Export campaign summary report to PDF.
        
        Args:
            summaries: List of campaign summaries
            start_date: Report start date
            end_date: Report end date
            output_filename: Custom filename
            
        Returns:
            Path to generated PDF
        """
        if output_filename is None:
            output_filename = f"campaign_summary_{start_date.strftime('%Y%m%d')}.pdf"
        
        output_path = self.output_dir / output_filename
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("Campaign Performance Summary", self.styles['CustomTitle'])
        story.append(title)
        
        date_range = Paragraph(
            f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            self.styles['Heading3']
        )
        story.append(date_range)
        story.append(Spacer(1, 20))
        
        # Campaigns table
        for summary in summaries:
            story.append(Paragraph(
                f"{summary.campaign} ({summary.platform.value.upper()})",
                self.styles['CustomSubtitle']
            ))
            
            data = [
                ['Metric', 'Value'],
                ['Total Spend', format_currency(summary.total_spend)],
                ['Total Revenue', format_currency(summary.total_revenue)],
                ['ROAS', f'{summary.roas:.2f}x'],
                ['Impressions', f'{summary.total_impressions:,}'],
                ['Clicks', f'{summary.total_clicks:,}'],
                ['Conversions', f'{summary.total_conversions:,}'],
                ['CPC', format_currency(summary.cpc)],
                ['CPM', format_currency(summary.cpm)],
                ['CPP', format_currency(summary.cpp)],
                ['CTR', format_percentage(summary.ctr)],
                ['CVR', format_percentage(summary.cvr)],
            ]
            
            table = Table(data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        doc.build(story)
        
        logger.info(f"Exported campaign summary to {output_path}")
        return output_path
    
    def save_chart_as_image(
        self,
        fig: go.Figure,
        filename: str,
        width: int = 1200,
        height: int = 600
    ) -> Path:
        """
        Save a Plotly figure as an image.
        
        Args:
            fig: Plotly figure
            filename: Output filename
            width: Image width
            height: Image height
            
        Returns:
            Path to saved image
        """
        output_path = self.output_dir / filename
        
        fig.write_image(str(output_path), width=width, height=height)
        
        logger.info(f"Saved chart to {output_path}")
        return output_path




