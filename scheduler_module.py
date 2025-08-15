#!/usr/bin/env python3
"""
Scheduler Module
Handles automated scheduling and execution of report generation.
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import signal
import sys

from config import get_config
from main import BusinessReportGenerator

class ReportScheduler:
    """Handles automated scheduling of report generation."""
    
    def __init__(self, config=None):
        """Initialize the scheduler."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        self.generator = BusinessReportGenerator(self.config)
        self.running = False
        self.scheduler_thread = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def setup_schedule(self):
        """Setup the report generation schedule."""
        if not self.config.AUTOMATION_CONFIG['schedule_enabled']:
            self.logger.info("Scheduling is disabled in configuration")
            return
        
        schedule_day = self.config.AUTOMATION_CONFIG['schedule_day']
        schedule_time = self.config.AUTOMATION_CONFIG['schedule_time']
        
        self.logger.info(f"Setting up schedule: {schedule_day} at {schedule_time}")
        
        # Map day names to schedule methods
        day_mapping = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday,
            'daily': schedule.every().day
        }
        
        if schedule_day.lower() in day_mapping:
            scheduled_job = day_mapping[schedule_day.lower()].at(schedule_time)
            scheduled_job.do(self._run_scheduled_report)
            self.logger.info(f"Scheduled weekly report for {schedule_day} at {schedule_time}")
        else:
            self.logger.error(f"Invalid schedule day: {schedule_day}")
            return
        
        # Add additional schedules if needed
        self._setup_additional_schedules()
        
    def _setup_additional_schedules(self):
        """Setup additional scheduled tasks."""
        # Monthly summary report (first Monday of each month)
        schedule.every().monday.at("10:00").do(self._run_monthly_report)
        
        # Daily health check (if enabled)
        if self.config.AUTOMATION_CONFIG.get('daily_health_check', False):
            schedule.every().day.at("08:00").do(self._run_health_check)
        
        # Weekly cleanup (every Sunday)
        schedule.every().sunday.at("23:00").do(self._run_cleanup)
        
    def _run_scheduled_report(self):
        """Execute the scheduled report generation."""
        self.logger.info("🕐 Running scheduled report generation...")
        
        try:
            results = self.generator.generate_complete_report(
                use_sample_data=False,  # Use real data for scheduled reports
                send_email=self.config.AUTOMATION_CONFIG.get('auto_email', True),
                create_summary=True
            )
            
            if results['success']:
                self.logger.info("✅ Scheduled report generated successfully")
                
                # Log key metrics
                if 'metrics' in results:
                    metrics = results['metrics']
                    self.logger.info(
                        f"📊 Report metrics - Sales: {self.config.METRICS_CONFIG['currency_symbol']}{metrics['current_week']['sales']:,.0f} "
                        f"({metrics['changes']['sales_change']:+.1f}%), "
                        f"Orders: {metrics['current_week']['orders']:,} "
                        f"({metrics['changes']['orders_change']:+.1f}%)"
                    )
            else:
                self.logger.error(f"❌ Scheduled report failed: {results.get('error', 'Unknown error')}")
                
                # Send error notification
                self._send_error_notification(results.get('error', 'Unknown error'))
                
        except Exception as e:
            self.logger.error(f"Exception in scheduled report: {e}", exc_info=True)
            self._send_error_notification(str(e))
            
    def _run_monthly_report(self):
        """Generate monthly summary report (first Monday of month)."""
        today = datetime.now()
        
        # Check if this is the first Monday of the month
        first_monday = self._get_first_monday_of_month(today.year, today.month)
        
        if today.date() == first_monday:
            self.logger.info("📅 Generating monthly summary report...")
            
            try:
                # Could extend this to generate a monthly report
                # For now, generate regular report with monthly flag
                results = self.generator.generate_complete_report(
                    use_sample_data=False,
                    send_email=True,
                    create_summary=True
                )
                
                if results['success']:
                    self.logger.info("✅ Monthly report generated successfully")
                    
            except Exception as e:
                self.logger.error(f"❌ Monthly report failed: {e}")
                
    def _run_health_check(self):
        """Run daily system health check."""
        self.logger.info("🏥 Running daily health check...")
        
        try:
            test_results = self.generator.test_system()
            
            if test_results['overall_status'] != 'passed':
                self.logger.warning("⚠️ System health check revealed issues")
                
                # Send health alert if configured
                if self.config.EMAIL_CONFIG.get('send_health_alerts', False):
                    self._send_health_alert(test_results)
            else:
                self.logger.info("✅ System health check passed")
                
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            
    def _run_cleanup(self):
        """Run weekly cleanup tasks."""
        self.logger.info("🧹 Running weekly cleanup...")
        
        try:
            # Cleanup old charts
            self.generator.chart_generator.cleanup_old_charts(keep_days=30)
            
            # Cleanup old reports (keep last 12 weeks = ~3 months)
            self._cleanup_old_reports(keep_weeks=12)
            
            # Cleanup old logs (keep last 4 weeks)
            self._cleanup_old_logs(keep_weeks=4)
            
            self.logger.info("✅ Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
            
    def _cleanup_old_reports(self, keep_weeks: int = 12):
        """Clean up old report files."""
        cutoff_date = datetime.now() - timedelta(weeks=keep_weeks)
        reports_dir = self.config.OUTPUT_DIR
        
        removed_count = 0
        for report_file in reports_dir.glob('*.pdf'):
            if report_file.stat().st_mtime < cutoff_date.timestamp():
                report_file.unlink()
                removed_count += 1
                
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} old report files")
            
    def _cleanup_old_logs(self, keep_weeks: int = 4):
        """Clean up old log files."""
        cutoff_date = datetime.now() - timedelta(weeks=keep_weeks)
        logs_dir = self.config.LOGS_DIR
        
        removed_count = 0
        for log_file in logs_dir.glob('*.log'):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                removed_count += 1
                
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} old log files")
            
    def _get_first_monday_of_month(self, year: int, month: int) -> datetime.date:
        """Get the first Monday of a given month."""
        first_day = datetime(year, month, 1)
        
        # Find the first Monday
        days_ahead = 0 - first_day.weekday()  # Monday is 0
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
            
        return (first_day + timedelta(days=days_ahead)).date()
        
    def _send_error_notification(self, error_message: str):
        """Send error notification email."""
        if self.config.EMAIL_CONFIG.get('send_error_alerts', True):
            try:
                alert_message = f"The scheduled report generation failed with the following error: {error_message}"
                self.generator.email_sender.send_alert_email(
                    "Report Generation Failed",
                    alert_message,
                    {}  # Empty metrics since generation failed
                )
            except Exception as e:
                self.logger.error(f"Failed to send error notification: {e}")
                
    def _send_health_alert(self, test_results: Dict[str, Any]):
        """Send system health alert."""
        try:
            failed_tests = [test for test, passed in test_results.items() 
                          if not passed and test != 'overall_status']
            
            alert_message = f"System health check found issues with: {', '.join(failed_tests)}"
            self.generator.email_sender.send_alert_email(
                "System Health Alert",
                alert_message,
                {}
            )
        except Exception as e:
            self.logger.error(f"Failed to send health alert: {e}")
            
    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
            
        self.setup_schedule()
        self.running = True
        
        def run_scheduler():
            self.logger.info("🚀 Report scheduler started")
            
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Scheduler error: {e}")
                    time.sleep(300)  # Wait 5 minutes before retrying
                    
            self.logger.info("⏹️ Report scheduler stopped")
            
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Print next scheduled run
        self._print_schedule_info()
        
    def stop_scheduler(self):
        """Stop the scheduler."""
        if not self.running:
            return
            
        self.logger.info("🛑 Stopping scheduler...")
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
            
        schedule.clear()
        self.logger.info("✅ Scheduler stopped")
        
    def _print_schedule_info(self):
        """Print information about scheduled jobs."""
        jobs = schedule.get_jobs()
        
        if jobs:
            print("\n📅 SCHEDULED JOBS:")
            print("="*50)
            
            for job in jobs:
                next_run = job.next_run
                if next_run:
                    time_until = next_run - datetime.now()
                    days = time_until.days
                    hours, remainder = divmod(time_until.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    
                    print(f"📊 {job.job_func.__name__}")
                    print(f"   Next run: {next_run.strftime('%A, %B %d at %H:%M')}")
                    print(f"   Time until: {days}d {hours}h {minutes}m")
                    print()
        else:
            print("No scheduled jobs configured")
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop_scheduler()
        sys.exit(0)
        
    def run_once_now(self):
        """Run report generation once immediately."""
        self.logger.info("🏃 Running report generation immediately...")
        self._run_scheduled_report()
        
    def get_schedule_status(self) -> Dict[str, Any]:
        """Get current schedule status and information."""
        jobs = schedule.get_jobs()
        
        status = {
            'running': self.running,
            'jobs_count': len(jobs),
            'jobs': [],
            'next_run': None
        }
        
        if jobs:
            next_job = min(jobs, key=lambda j: j.next_run if j.next_run else datetime.max)
            status['next_run'] = next_job.next_run.isoformat() if next_job.next_run else None
            
            for job in jobs:
                job_info = {
                    'function': job.job_func.__name__,
                    'next_run': job.next_run.isoformat() if job.next_run else None,
                    'interval': str(job.interval) if hasattr(job, 'interval') else 'unknown'
                }
                status['jobs'].append(job_info)
                
        return status

def main():
    """Main function for running the scheduler standalone."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Business Report Scheduler')
    parser.add_argument('--run-once', action='store_true', help='Run report generation once and exit')
    parser.add_argument('--status', action='store_true', help='Show schedule status and exit')
    parser.add_argument('--test', action='store_true', help='Test scheduler setup')
    
    args = parser.parse_args()
    
    scheduler = ReportScheduler()
    
    if args.status:
        status = scheduler.get_schedule_status()
        print(f"Scheduler Status: {'Running' if status['running'] else 'Stopped'}")
        print(f"Scheduled Jobs: {status['jobs_count']}")
        if status['next_run']:
            print(f"Next Run: {status['next_run']}")
        return
        
    if args.test:
        print("🧪 Testing scheduler setup...")
        scheduler.setup_schedule()
        scheduler._print_schedule_info()
        return
        
    if args.run_once:
        scheduler.run_once_now()
        return
        
    # Start the scheduler
    try:
        scheduler.start_scheduler()
        
        print("🚀 Business Report Scheduler is running...")
        print("Press Ctrl+C to stop")
        
        # Keep the main thread alive
        while scheduler.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
    finally:
        scheduler.stop_scheduler()

if __name__ == "__main__":
    main()