#!/usr/bin/env python3
"""
Email Sender Module
Handles automated email distribution of reports with professional formatting.
"""

import smtplib
import ssl
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import get_config

class EmailSender:
    """Handles automated email distribution of business reports."""
    
    def __init__(self, config=None):
        """Initialize the email sender."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        self.smtp_server = None
        
    def send_report_email(self, 
                         report_file: Path,
                         metrics: Dict[str, Any],
                         insights: Dict[str, Any],
                         chart_files: Optional[List[Path]] = None) -> bool:
        """Send comprehensive report email with attachments."""
        try:
            if not self.config.EMAIL_CONFIG['send_reports']:
                self.logger.info("Email sending is disabled in configuration")
                return False
            
            # Prepare email components
            subject = self._generate_subject(metrics)
            html_body = self._generate_html_body(metrics, insights)
            text_body = self._generate_text_body(metrics, insights)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = formataddr(('Business Analytics', self.config.EMAIL_CONFIG['sender_email']))
            message['To'] = ', '.join(self.config.EMAIL_CONFIG['recipients'])
            message['Subject'] = subject
            
            # Attach text and HTML versions
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')
            message.attach(text_part)
            message.attach(html_part)
            
            # Attach PDF report
            self._attach_file(message, report_file, 'Weekly_Business_Report.pdf')
            
            # Attach charts if provided
            if chart_files:
                for chart_file in chart_files[:3]:  # Limit to 3 charts to avoid large emails
                    if chart_file.exists():
                        self._attach_file(message, chart_file, f"Chart_{chart_file.name}")
            
            # Send email
            success = self._send_email(message)
            
            if success:
                self.logger.info(f"Report email sent successfully to {len(self.config.EMAIL_CONFIG['recipients'])} recipients")
            else:
                self.logger.error("Failed to send report email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending report email: {e}")
            return False
    
    def send_alert_email(self, alert_type: str, message: str, metrics: Dict[str, Any]) -> bool:
        """Send alert email for critical business conditions."""
        try:
            if not self.config.EMAIL_CONFIG['send_reports']:
                return False
            
            subject = f"🚨 Business Alert: {alert_type}"
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .alert {{ background-color: #fee; border: 1px solid #fcc; padding: 15px; border-radius: 5px; }}
                    .metrics {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <h2 style="color: {self.config.COLORS['negative']};">Business Alert</h2>
                <div class="alert">
                    <h3>{alert_type}</h3>
                    <p>{message}</p>
                </div>
                
                <div class="metrics">
                    <h4>Current Week Metrics</h4>
                    <ul>
                        <li>Sales: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['current_week']['sales']:,.0f} ({metrics['changes']['sales_change']:+.1f}%)</li>
                        <li>Orders: {metrics['current_week']['orders']:,} ({metrics['changes']['orders_change']:+.1f}%)</li>
                        <li>AOV: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f} ({metrics['aov']['change']:+.1f}%)</li>
                    </ul>
                </div>
                
                <p><em>This is an automated alert from your Business Intelligence System.</em></p>
            </body>
            </html>
            """
            
            text_body = f"""
            BUSINESS ALERT: {alert_type}
            
            {message}
            
            Current Week Metrics:
            - Sales: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['current_week']['sales']:,.0f} ({metrics['changes']['sales_change']:+.1f}%)
            - Orders: {metrics['current_week']['orders']:,} ({metrics['changes']['orders_change']:+.1f}%)
            - AOV: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f} ({metrics['aov']['change']:+.1f}%)
            
            This is an automated alert from your Business Intelligence System.
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr(('Business Analytics Alert', self.config.EMAIL_CONFIG['sender_email']))
            msg['To'] = ', '.join(self.config.EMAIL_CONFIG['recipients'])
            msg['Subject'] = subject
            msg['X-Priority'] = '1'  # High priority
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            return self._send_email(msg)
            
        except Exception as e:
            self.logger.error(f"Error sending alert email: {e}")
            return False
    
    def _generate_subject(self, metrics: Dict[str, Any]) -> str:
        """Generate email subject line."""
        week_range = f"{metrics['current_week']['week_start_formatted']} - {metrics['current_week']['week_end_formatted']}"
        
        # Add performance indicator to subject
        sales_change = metrics['changes']['sales_change']
        if sales_change >= 10:
            indicator = "📈 Strong Growth"
        elif sales_change >= 5:
            indicator = "📊 Good Growth"
        elif sales_change >= 0:
            indicator = "➡️ Stable"
        else:
            indicator = "📉 Declining"
        
        return self.config.EMAIL_CONFIG['subject_template'].format(
            date_range=week_range
        ) + f" - {indicator}"
    
    def _generate_html_body(self, metrics: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate HTML email body."""
        week_range = f"{metrics['current_week']['week_start_formatted']} - {metrics['current_week']['week_end_formatted']}"
        
        # Performance indicators with colors
        sales_color = self.config.COLORS['positive'] if metrics['changes']['sales_change'] >= 0 else self.config.COLORS['negative']
        orders_color = self.config.COLORS['positive'] if metrics['changes']['orders_change'] >= 0 else self.config.COLORS['negative']
        aov_color = self.config.COLORS['positive'] if metrics['aov']['change'] >= 0 else self.config.COLORS['negative']
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    color: {self.config.COLORS['text_dark']};
                    margin: 0;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, {self.config.COLORS['primary']}, {self.config.COLORS['accent1']});
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .metric-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid {self.config.COLORS['primary']};
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 28px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .metric-change {{
                    font-size: 16px;
                    font-weight: bold;
                }}
                .positive {{ color: {self.config.COLORS['positive']}; }}
                .negative {{ color: {self.config.COLORS['negative']}; }}
                .insights {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 30px 0;
                }}
                .insight-item {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 3px solid {self.config.COLORS['accent1']};
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    font-size: 14px;
                    color: {self.config.COLORS['text_light']};
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Weekly Business Report</h1>
                <h2>{week_range}</h2>
                <p>Your comprehensive business performance summary</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div style="color: {self.config.COLORS['primary']}; font-size: 18px; font-weight: bold;">💰 Sales Revenue</div>
                    <div class="metric-value">{self.config.METRICS_CONFIG['currency_symbol']}{metrics['current_week']['sales']:,.0f}</div>
                    <div class="metric-change" style="color: {sales_color}">
                        {metrics['changes']['sales_change']:+.1f}%
                    </div>
                </div>
                
                <div class="metric-card">
                    <div style="color: {self.config.COLORS['primary']}; font-size: 18px; font-weight: bold;">🛒 Total Orders</div>
                    <div class="metric-value">{metrics['current_week']['orders']:,}</div>
                    <div class="metric-change" style="color: {orders_color}">
                        {metrics['changes']['orders_change']:+.1f}%
                    </div>
                </div>
                
                <div class="metric-card">
                    <div style="color: {self.config.COLORS['primary']}; font-size: 18px; font-weight: bold;">📈 Avg Order Value</div>
                    <div class="metric-value">{self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f}</div>
                    <div class="metric-change" style="color: {aov_color}">
                        {metrics['aov']['change']:+.1f}%
                    </div>
                </div>
            </div>
            
            <div class="insights">
                <h3 style="color: {self.config.COLORS['primary']};">🎯 Key Insights</h3>
                <div class="insight-item">
                    <strong>⭐ Top Product:</strong> {metrics['current_week']['top_product']}
                </div>
                <div class="insight-item">
                    <strong>🏆 Top Customer:</strong> {metrics['current_week']['top_customer']}
                </div>
        """
        
        # Add top performance insights
        performance_insights = insights['performance_analysis'][:3]
        for insight in performance_insights:
            html_body += f"""
                <div class="insight-item">
                    <strong>{insight['icon']} {insight['metric']}:</strong> {insight['message']}
                </div>
            """
        
        # Add top recommendations
        if insights['recommendations']:
            html_body += """
                <h4 style="color: """ + self.config.COLORS['primary'] + """; margin-top: 25px;">💡 Top Recommendations</h4>
            """
            for rec in insights['recommendations'][:2]:
                html_body += f"""
                    <div class="insight-item">
                        <strong>{rec['icon']} {rec['title']}:</strong> {rec['description']}
                        <br><em>Timeline: {rec['timeline']} | Impact: {rec['expected_impact']}</em>
                    </div>
                """
        
        html_body += f"""
            </div>
            
            <div class="footer">
                <p><strong>{self.config.PROJECT_NAME}</strong></p>
                <p>Generated on {datetime.now().strftime('%d %B %Y at %H:%M')}</p>
                <p>This report contains confidential business information.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _generate_text_body(self, metrics: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate plain text email body."""
        week_range = f"{metrics['current_week']['week_start_formatted']} - {metrics['current_week']['week_end_formatted']}"
        
        text_body = f"""
WEEKLY BUSINESS REPORT
{week_range}

KEY METRICS:
============
Sales Revenue: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['current_week']['sales']:,.0f} ({metrics['changes']['sales_change']:+.1f}%)
Total Orders: {metrics['current_week']['orders']:,} ({metrics['changes']['orders_change']:+.1f}%)
Avg Order Value: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f} ({metrics['aov']['change']:+.1f}%)

HIGHLIGHTS:
===========
Top Product: {metrics['current_week']['top_product']}
Top Customer: {metrics['current_week']['top_customer']}

PERFORMANCE INSIGHTS:
====================
"""
        
        # Add performance insights
        for insight in insights['performance_analysis'][:3]:
            text_body += f"• {insight['metric']}: {insight['message']}\n"
        
        # Add recommendations
        if insights['recommendations']:
            text_body += "\nTOP RECOMMENDATIONS:\n"
            text_body += "===================\n"
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                text_body += f"{i}. {rec['title']}: {rec['description']}\n   Timeline: {rec['timeline']} | Impact: {rec['expected_impact']}\n\n"
        
        text_body += f"""
Generated by {self.config.PROJECT_NAME}
{datetime.now().strftime('%d %B %Y at %H:%M')}

This report contains confidential business information.
        """
        
        return text_body
    
    def _attach_file(self, message: MIMEMultipart, file_path: Path, filename: str):
        """Attach a file to the email message."""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            message.attach(part)
            
        except Exception as e:
            self.logger.warning(f"Could not attach file {file_path}: {e}")
    
    def _send_email(self, message: MIMEMultipart) -> bool:
        """Send the email message."""
        try:
            # Create SMTP session
            server = smtplib.SMTP(
                self.config.EMAIL_CONFIG['smtp_server'], 
                self.config.EMAIL_CONFIG['smtp_port']
            )
            server.starttls()  # Enable TLS encryption
            server.login(
                self.config.EMAIL_CONFIG['sender_email'],
                self.config.EMAIL_CONFIG['sender_password']
            )
            
            # Send email
            text = message.as_string()
            server.sendmail(
                self.config.EMAIL_CONFIG['sender_email'],
                self.config.EMAIL_CONFIG['recipients'],
                text
            )
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP error: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """Test email server connection and authentication."""
        try:
            if not self.config.EMAIL_CONFIG['sender_email'] or not self.config.EMAIL_CONFIG['sender_password']:
                self.logger.error("Email credentials not configured")
                return False
            
            server = smtplib.SMTP(
                self.config.EMAIL_CONFIG['smtp_server'], 
                self.config.EMAIL_CONFIG['smtp_port']
            )
            server.starttls()
            server.login(
                self.config.EMAIL_CONFIG['sender_email'],
                self.config.EMAIL_CONFIG['sender_password']
            )
            server.quit()
            
            self.logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email to verify email functionality."""
        try:
            if not self.config.EMAIL_CONFIG['send_reports']:
                self.logger.info("Email sending is disabled")
                return False
            
            subject = "Test Email - Business Report System"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: {self.config.COLORS['primary']};">Test Email</h2>
                <p>This is a test email from your Business Report System.</p>
                <p><strong>System Status:</strong> ✅ Email functionality is working correctly</p>
                <p><strong>Sent at:</strong> {datetime.now().strftime('%d %B %Y at %H:%M')}</p>
                <hr>
                <p><em>If you received this email, your report distribution system is properly configured.</em></p>
            </body>
            </html>
            """
            
            text_body = f"""
            TEST EMAIL - Business Report System
            
            This is a test email from your Business Report System.
            
            System Status: Email functionality is working correctly
            Sent at: {datetime.now().strftime('%d %B %Y at %H:%M')}
            
            If you received this email, your report distribution system is properly configured.
            """
            
            message = MIMEMultipart('alternative')
            message['From'] = formataddr(('Business Analytics Test', self.config.EMAIL_CONFIG['sender_email']))
            message['To'] = ', '.join(self.config.EMAIL_CONFIG['recipients'])
            message['Subject'] = subject
            
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            success = self._send_email(message)
            
            if success:
                self.logger.info("Test email sent successfully")
            else:
                self.logger.error("Failed to send test email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            return False