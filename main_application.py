#!/usr/bin/env python3
"""
Main Application - Business Intelligence Report Generator
Orchestrates the complete report generation workflow.
"""

import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import our custom modules
from config import get_config
from data_processor import DataProcessor
from chart_generator import ChartGenerator
from insights_generator import InsightsGenerator
from pdf_report_generator import PDFReportGenerator
from email_sender import EmailSender

class BusinessReportGenerator:
    """Main application class that orchestrates the report generation process."""
    
    def __init__(self, config=None):
        """Initialize the report generator with all components."""
        self.config = config or get_config()
        self._setup_logging()
        
        # Initialize all components
        self.data_processor = DataProcessor(self.config)
        self.chart_generator = ChartGenerator(self.config)
        self.insights_generator = InsightsGenerator(self.config)
        self.pdf_generator = PDFReportGenerator(self.config)
        self.email_sender = EmailSender(self.config)
        
        self.logger = logging.getLogger(__name__)
        
    def _setup_logging(self):
        """Configure logging for the application."""
        log_level = getattr(logging, self.config.LOGGING_CONFIG['level'])
        log_format = self.config.LOGGING_CONFIG['format']
        
        # Create logs directory
        self.config.LOGS_DIR.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(
                    self.config.LOGS_DIR / f'report_generator_{datetime.now().strftime("%Y%m%d")}.log'
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def generate_complete_report(self, 
                               use_sample_data: bool = True,
                               data_file: Optional[Path] = None,
                               send_email: bool = False,
                               create_summary: bool = False) -> Dict[str, Any]:
        """Generate a complete business report with all components."""
        
        self.logger.info("="*60)
        self.logger.info("STARTING BUSINESS REPORT GENERATION")
        self.logger.info("="*60)
        
        try:
            # Step 1: Load and process data
            self.logger.info("Step 1: Loading and processing data...")
            if use_sample_data:
                self.data_processor.load_sample_data()
            else:
                self.data_processor.load_data_from_csv(data_file)
            
            cleaned_data = self.data_processor.clean_data()
            self.logger.info(f"Processed {len(cleaned_data)} weeks of data")
            
            # Step 2: Calculate metrics
            self.logger.info("Step 2: Calculating business metrics...")
            metrics = self.data_processor.calculate_metrics()
            chart_data = self.data_processor.get_data_for_charts()
            
            # Step 3: Generate insights
            self.logger.info("Step 3: Generating business insights...")
            insights = self.insights_generator.generate_comprehensive_insights(metrics)
            
            # Step 4: Create visualizations
            self.logger.info("Step 4: Creating charts and visualizations...")
            chart_files = self.chart_generator.generate_all_charts(chart_data, metrics)
            self.logger.info(f"Generated {len(chart_files)} charts")
            
            # Step 5: Generate PDF reports
            self.logger.info("Step 5: Creating PDF reports...")
            main_report = self.pdf_generator.create_comprehensive_report(metrics, insights, chart_files)
            
            reports_created = [main_report]
            
            if create_summary:
                summary_report = self.pdf_generator.create_summary_report(metrics, insights)
                reports_created.append(summary_report)
                self.logger.info("Summary report created")
            
            # Step 6: Send email if requested
            email_sent = False
            if send_email and self.config.EMAIL_CONFIG['send_reports']:
                self.logger.info("Step 6: Sending email report...")
                email_sent = self.email_sender.send_report_email(
                    main_report, metrics, insights, chart_files[:3]
                )
                if email_sent:
                    self.logger.info("Email sent successfully")
                else:
                    self.logger.warning("Email sending failed")
            
            # Step 7: Check for alerts
            self._check_and_send_alerts(metrics, insights)
            
            # Cleanup old files
            self.chart_generator.cleanup_old_charts(keep_days=7)
            
            # Generate results summary
            results = {
                'success': True,
                'reports_created': reports_created,
                'charts_created': chart_files,
                'email_sent': email_sent,
                'metrics': metrics,
                'insights': insights,
                'data_summary': self.data_processor.get_data_summary(),
                'generation_time': datetime.now().isoformat()
            }
            
            self.logger.info("="*60)
            self.logger.info("REPORT GENERATION COMPLETED SUCCESSFULLY")
            self.logger.info("="*60)
            
            # Print summary to console
            self._print_generation_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in report generation: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'generation_time': datetime.now().isoformat()
            }
    
    def _check_and_send_alerts(self, metrics: Dict[str, Any], insights: Dict[str, Any]):
        """Check for critical conditions and send alert emails if necessary."""
        try:
            alerts_sent = []
            
            # Check for significant sales decline
            sales_change = metrics['changes']['sales_change']
            if sales_change < -15:  # More than 15% decline
                alert_message = f"Sales have declined significantly by {abs(sales_change):.1f}% this week. Immediate attention required."
                if self.email_sender.send_alert_email("Significant Sales Decline", alert_message, metrics):
                    alerts_sent.append("Sales Decline Alert")
            
            # Check for high-risk alerts from insights
            high_risks = [r for r in insights['risk_alerts'] if r['level'] == 'High']
            if high_risks:
                for risk in high_risks:
                    alert_message = f"{risk['description']} {risk['mitigation']}"
                    if self.email_sender.send_alert_email(risk['category'], alert_message, metrics):
                        alerts_sent.append(f"{risk['category']} Alert")
            
            if alerts_sent:
                self.logger.info(f"Sent {len(alerts_sent)} alert emails: {', '.join(alerts_sent)}")
                
        except Exception as e:
            self.logger.warning(f"Error checking/sending alerts: {e}")
    
    def _print_generation_summary(self, results: Dict[str, Any]):
        """Print a summary of the generation process to console."""
        print("\n" + "="*80)
        print("📊 BUSINESS REPORT GENERATION SUMMARY")
        print("="*80)
        
        metrics = results.get('metrics', {})
        if 'current_week' in metrics:
            current_week = metrics['current_week']
            changes = metrics['changes']
            
            print(f"📅 Report Period: {current_week['week_start_formatted']} - {current_week['week_end_formatted']}")
            print(f"💰 Sales: {self.config.METRICS_CONFIG['currency_symbol']}{current_week['sales']:,.0f} ({changes['sales_change']:+.1f}%)")
            print(f"🛒 Orders: {current_week['orders']:,} ({changes['orders_change']:+.1f}%)")
            print(f"📈 AOV: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f} ({metrics['aov']['change']:+.1f}%)")
            print(f"⭐ Top Product: {current_week['top_product']}")
            print(f"🏆 Top Customer: {current_week['top_customer']}")
        
        print(f"\n📁 Files Created:")
        for report in results.get('reports_created', []):
            print(f"   📄 {report.name}")
        
        charts_created = results.get('charts_created', [])
        if charts_created:
            print(f"   📊 {len(charts_created)} charts created")
        
        if results.get('email_sent'):
            print(f"✅ Email sent to {len(self.config.EMAIL_CONFIG['recipients'])} recipients")
        
        print(f"\n⏰ Generated at: {datetime.now().strftime('%d %B %Y at %H:%M')}")
        print("="*80)
        
        # Print key insights summary
        insights = results.get('insights', {})
        if 'performance_analysis' in insights:
            print("\n🎯 KEY INSIGHTS:")
            for perf in insights['performance_analysis'][:3]:
                status_emoji = "✅" if perf['status'] in ['excellent', 'good'] else "⚠️" if perf['status'] == 'fair' else "🚨"
                print(f"   {status_emoji} {perf['metric']}: {perf['message']}")
        
        if 'recommendations' in insights and insights['recommendations']:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for rec in insights['recommendations'][:2]:
                print(f"   {rec['icon']} {rec['title']}: {rec['description']}")
        
        print("\n")
    
    def test_system(self) -> Dict[str, Any]:
        """Test all system components and return status report."""
        self.logger.info("Running system tests...")
        
        test_results = {
            'data_processing': False,
            'chart_generation': False,
            'pdf_generation': False,
            'email_connection': False,
            'config_validation': False,
            'overall_status': 'failed'
        }
        
        try:
            # Test 1: Configuration validation
            config_errors = self.config.validate_config()
            test_results['config_validation'] = len(config_errors) == 0
            if config_errors:
                self.logger.warning(f"Configuration issues: {config_errors}")
            
            # Test 2: Data processing
            try:
                self.data_processor.load_sample_data()
                self.data_processor.clean_data()
                test_results['data_processing'] = True
                self.logger.info("✅ Data processing test passed")
            except Exception as e:
                self.logger.error(f"❌ Data processing test failed: {e}")
            
            # Test 3: Chart generation
            try:
                if test_results['data_processing']:
                    metrics = self.data_processor.calculate_metrics()
                    chart_data = self.data_processor.get_data_for_charts()
                    charts = self.chart_generator.generate_all_charts(chart_data, metrics)
                    test_results['chart_generation'] = len(charts) > 0
                    self.logger.info("✅ Chart generation test passed")
            except Exception as e:
                self.logger.error(f"❌ Chart generation test failed: {e}")
            
            # Test 4: PDF generation
            try:
                if test_results['data_processing']:
                    insights = self.insights_generator.generate_comprehensive_insights(metrics)
                    pdf_file = self.pdf_generator.create_summary_report(metrics, insights)
                    test_results['pdf_generation'] = pdf_file.exists()
                    self.logger.info("✅ PDF generation test passed")
            except Exception as e:
                self.logger.error(f"❌ PDF generation test failed: {e}")
            
            # Test 5: Email connection
            if self.config.EMAIL_CONFIG['send_reports']:
                test_results['email_connection'] = self.email_sender.test_email_connection()
                if test_results['email_connection']:
                    self.logger.info("✅ Email connection test passed")
                else:
                    self.logger.warning("❌ Email connection test failed")
            else:
                test_results['email_connection'] = True  # Not applicable
                self.logger.info("📧 Email sending disabled - skipping test")
            
            # Overall status
            passed_tests = sum(test_results.values())
            total_tests = len(test_results) - 1  # Exclude overall_status
            
            if passed_tests == total_tests:
                test_results['overall_status'] = 'passed'
                self.logger.info(f"🎉 All system tests passed ({passed_tests}/{total_tests})")
            else:
                test_results['overall_status'] = 'partial'
                self.logger.warning(f"⚠️ Some tests failed ({passed_tests}/{total_tests})")
            
        except Exception as e:
            self.logger.error(f"System test error: {e}")
            test_results['overall_status'] = 'failed'
        
        return test_results

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Business Intelligence Report Generator')
    parser.add_argument('--data-file', type=Path, help='Path to CSV data file')
    parser.add_argument('--no-sample-data', action='store_true', help='Use actual data instead of sample')
    parser.add_argument('--send-email', action='store_true', help='Send report via email')
    parser.add_argument('--create-summary', action='store_true', help='Create summary report')
    parser.add_argument('--test-system', action='store_true', help='Run system tests')
    parser.add_argument('--test-email', action='store_true', help='Send test email')
    
    args = parser.parse_args()
    
    # Initialize the report generator
    generator = BusinessReportGenerator()
    
    if args.test_system:
        print("🔧 Running system tests...")
        test_results = generator.test_system()
        print(f"\nTest Results: {test_results['overall_status'].upper()}")
        return 0 if test_results['overall_status'] == 'passed' else 1
    
    if args.test_email:
        print("📧 Sending test email...")
        success = generator.email_sender.send_test_email()
        print("✅ Test email sent successfully" if success else "❌ Test email failed")
        return 0 if success else 1
    
    # Generate the report
    results = generator.generate_complete_report(
        use_sample_data=not args.no_sample_data,
        data_file=args.data_file,
        send_email=args.send_email,
        create_summary=args.create_summary
    )
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    sys.exit(main())