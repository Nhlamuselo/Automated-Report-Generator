#!/usr/bin/env python3
"""
Configuration settings for the Automated Report Generator System
"""

import os
from pathlib import Path
from datetime import datetime

class Config:
    """Main configuration class for the report system."""
    
    # Project Information
    PROJECT_NAME = "Business Intelligence Report Generator"
    VERSION = "1.0.0"
    COMPANY_NAME = "Your Business Analytics"
    
    # Directories
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "reports"
    CHARTS_DIR = BASE_DIR / "charts"
    TEMPLATES_DIR = BASE_DIR / "templates"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Create directories if they don't exist
    for directory in [DATA_DIR, OUTPUT_DIR, CHARTS_DIR, TEMPLATES_DIR, LOGS_DIR]:
        directory.mkdir(exist_ok=True)
    
    # Report Configuration
    REPORT_FORMATS = ['pdf', 'html', 'excel']
    DEFAULT_FORMAT = 'pdf'
    
    # Data Source Configuration
    DATA_SOURCE_TYPE = "csv"  # Options: csv, google_sheets, database, api
    CSV_FILE_PATH = DATA_DIR / "weekly_business_report.csv"
    
    # Google Sheets Configuration (if using Google Sheets)
    GOOGLE_SHEETS_ID = ""
    GOOGLE_SHEETS_RANGE = "Sheet1!A:F"
    GOOGLE_CREDENTIALS_PATH = DATA_DIR / "credentials.json"
    
    # Database Configuration (if using database)
    DATABASE_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'business_reports',
        'username': 'report_user',
        'password': os.getenv('DB_PASSWORD', ''),
        'table_name': 'weekly_sales'
    }
    
    # Email Configuration
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': os.getenv('SENDER_EMAIL', ''),
        'sender_password': os.getenv('EMAIL_PASSWORD', ''),
        'recipients': [
            'manager@company.com',
            'team@company.com'
        ],
        'subject_template': "Weekly Business Report - {date_range}",
        'send_reports': False  # Set to True to enable email sending
    }
    
    # Chart Configuration
    CHART_CONFIG = {
        'figure_size': (12, 8),
        'dpi': 300,
        'style': 'seaborn-v0_8-whitegrid',
        'font_size': 11,
        'title_size': 16,
        'label_size': 12,
        'save_format': 'png'
    }
    
    # Color Palette
    COLORS = {
        'primary': '#0052CC',        # Professional Blue
        'secondary': '#6B7280',      # Neutral Gray
        'positive': '#22C55E',       # Success Green
        'negative': '#DC2626',       # Alert Red
        'warning': '#F59E0B',        # Warning Orange
        'background': '#FFFFFF',     # Clean White
        'accent1': '#8B5CF6',        # Purple
        'accent2': '#06B6D4',        # Cyan
        'text_dark': '#1F2937',      # Dark Gray for text
        'text_light': '#6B7280'      # Light Gray for labels
    }
    
    # PDF Report Configuration
    PDF_CONFIG = {
        'page_size': 'A4',
        'margins': {
            'top': 72,
            'bottom': 72,
            'left': 72,
            'right': 72
        },
        'font_family': 'Helvetica',
        'title_font_size': 24,
        'heading_font_size': 16,
        'normal_font_size': 11,
        'small_font_size': 9
    }
    
    # Metrics Configuration
    METRICS_CONFIG = {
        'currency_symbol': 'R',
        'decimal_places': 2,
        'percentage_decimal_places': 1,
        'large_number_format': '{:,.0f}',  # Format large numbers with commas
        'growth_threshold': {
            'high': 10,  # Above 10% is high growth
            'medium': 5,  # 5-10% is medium growth
            'low': 0     # Below 0% is decline
        }
    }
    
    # Automation Configuration
    AUTOMATION_CONFIG = {
        'schedule_enabled': False,
        'schedule_day': 'monday',  # Day of week to generate reports
        'schedule_time': '09:00',  # Time to generate reports (24-hour format)
        'timezone': 'Africa/Johannesburg',
        'auto_email': False,
        'auto_upload_cloud': False
    }
    
    # Cloud Storage Configuration
    CLOUD_CONFIG = {
        'provider': 'google_drive',  # Options: google_drive, dropbox, aws_s3
        'google_drive': {
            'folder_id': '',
            'credentials_path': DATA_DIR / "drive_credentials.json"
        },
        'dropbox': {
            'access_token': os.getenv('DROPBOX_TOKEN', ''),
            'folder_path': '/Business Reports'
        },
        'aws_s3': {
            'bucket_name': 'business-reports',
            'region': 'us-east-1',
            'access_key': os.getenv('AWS_ACCESS_KEY', ''),
            'secret_key': os.getenv('AWS_SECRET_KEY', '')
        }
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        'level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file_handler': True,
        'console_handler': True,
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # Report Content Configuration
    REPORT_SECTIONS = {
        'cover_page': True,
        'executive_summary': True,
        'key_metrics_table': True,
        'trend_charts': True,
        'product_analysis': True,
        'customer_analysis': True,
        'insights_recommendations': True,
        'appendix': False
    }
    
    # Insights Configuration
    INSIGHTS_CONFIG = {
        'enable_ai_insights': False,  # Future: AI-powered insights
        'minimum_data_points': 2,     # Minimum weeks needed for trend analysis
        'seasonal_analysis': False,   # Enable seasonal pattern detection
        'competitor_comparison': False # Enable if competitor data available
    }

    @classmethod
    def get_current_week_range(cls):
        """Get the current week date range for reports."""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    @classmethod
    def get_report_filename(cls, format_type='pdf', date_suffix=None):
        """Generate standardized report filename."""
        if date_suffix is None:
            date_suffix = datetime.now().strftime('%Y-%m-%d')
        return f"Weekly_Business_Report_{date_suffix}.{format_type}"
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings."""
        errors = []
        
        # Check required directories exist
        for directory in [cls.DATA_DIR, cls.OUTPUT_DIR]:
            if not directory.exists():
                errors.append(f"Directory does not exist: {directory}")
        
        # Check email config if enabled
        if cls.EMAIL_CONFIG['send_reports']:
            if not cls.EMAIL_CONFIG['sender_email']:
                errors.append("Sender email not configured")
            if not cls.EMAIL_CONFIG['recipients']:
                errors.append("No email recipients configured")
        
        # Check data source configuration
        if cls.DATA_SOURCE_TYPE == 'csv' and not cls.CSV_FILE_PATH.exists():
            errors.append(f"CSV file not found: {cls.CSV_FILE_PATH}")
        
        return errors

# Development/Testing Configuration
class DevelopmentConfig(Config):
    """Configuration for development environment."""
    LOGGING_CONFIG = Config.LOGGING_CONFIG.copy()
    LOGGING_CONFIG['level'] = 'DEBUG'
    EMAIL_CONFIG = Config.EMAIL_CONFIG.copy()
    EMAIL_CONFIG['send_reports'] = False
    
# Production Configuration  
class ProductionConfig(Config):
    """Configuration for production environment."""
    LOGGING_CONFIG = Config.LOGGING_CONFIG.copy()
    LOGGING_CONFIG['level'] = 'INFO'
    AUTOMATION_CONFIG = Config.AUTOMATION_CONFIG.copy()
    AUTOMATION_CONFIG['schedule_enabled'] = True

# Get configuration based on environment
def get_config():
    """Return appropriate configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
