#!/usr/bin/env python3
"""
Setup and Installation Script for Business Intelligence Report Generator
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def create_directory_structure():
    """Create the required directory structure."""
    directories = [
        'data',
        'reports', 
        'charts',
        'templates',
        'logs',
        'config',
        'tests'
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    print()

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing dependencies...")
    
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
    except subprocess.CalledProcessError:
        print("❌ pip is not installed. Please install pip first.")
        return False
    
    # Install packages from requirements.txt
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_sample_data():
    """Create sample data file."""
    print("📊 Creating sample data file...")
    
    sample_data = """Week_Start,Week_End,Total_Sales,Total_Orders,Top_Product,Top_Customer
2025-01-06,2025-01-12,12500,45,Laptop,Alpha Corp
2025-01-13,2025-01-19,15800,52,Smartphone,Beta Ltd
2025-01-20,2025-01-26,14200,48,Tablet,Gamma LLC
2025-01-27,2025-02-02,16950,55,Monitor,Delta Inc
2025-02-03,2025-02-09,18100,60,Printer,Epsilon Co
2025-02-10,2025-02-16,17500,57,Keyboard,Zeta Enterprises
2025-02-17,2025-02-23,19000,62,Mouse,Eta Traders
2025-02-24,2025-03-02,20050,65,Headphones,Theta Solutions"""
    
    data_file = Path('data/weekly_business_report.csv')
    data_file.write_text(sample_data)
    print(f"   ✅ Sample data created: {data_file}")
    print()

def create_env_template():
    """Create environment template file."""
    print("🔧 Creating environment template...")
    
    env_template = """# Business Report Generator Configuration
# Copy this file to .env and update with your settings

# Email Configuration
SENDER_EMAIL=your-email@company.com
EMAIL_PASSWORD=your-app-password
DB_PASSWORD=your-database-password

# Google Sheets (if using)
GOOGLE_SHEETS_ID=your-sheet-id

# Cloud Storage Tokens (if using)
DROPBOX_TOKEN=your-dropbox-token
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key

# Environment
FLASK_ENV=development
"""
    
    env_file = Path('.env.template')
    env_file.write_text(env_template)
    print(f"   ✅ Environment template created: {env_file}")
    print("   📝 Copy .env.template to .env and update with your settings")
    print()

def create_run_scripts():
    """Create convenient run scripts."""
    print("🚀 Creating run scripts...")
    
    # Windows batch script
    windows_script = """@echo off
echo Starting Business Report Generator...
python main.py %*
pause
"""
    
    Path('run_report.bat').write_text(windows_script)
    print("   ✅ Created: run_report.bat (Windows)")
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting Business Report Generator..."
python3 main.py "$@"
"""
    
    unix_file = Path('run_report.sh')
    unix_file.write_text(unix_script)
    unix_file.chmod(0o755)  # Make executable
    print("   ✅ Created: run_report.sh (Linux/Mac)")
    print()

def create_readme():
    """Create README file with usage instructions."""
    print("📖 Creating README file...")
    
    readme_content = """# Business Intelligence Report Generator

An automated system for generating professional business reports with charts, insights, and email distribution.

## Features

- 📊 Automated data processing and analysis
- 📈 Professional chart generation
- 📄 Beautiful PDF report creation
- 🧠 AI-powered business insights
- 📧 Automated email distribution
- ⚠️ Risk alerts and recommendations
- 🎨 Customizable branding and styling

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Test System**
   ```bash
   python main.py --test-system
   ```

4. **Generate Report**
   ```bash
   python main.py --send-email --create-summary
   ```

## Usage Examples

### Generate Basic Report
```bash
python main.py
```

### Use Custom Data File
```bash
python main.py --data-file path/to/your/data.csv --no-sample-data
```

### Send Email Report
```bash
python main.py --send-email
```

### Create Summary Report
```bash
python main.py --create-summary
```

### Test Email Configuration
```bash
python main.py --test-email
```

## Configuration

Edit `config.py` to customize:
- Color schemes and branding
- Report sections and content
- Email settings
- Chart styles
- Metrics and KPIs

## Data Format

Your CSV data should include columns:
- Week_Start: Start date (YYYY-MM-DD)
- Week_End: End date (YYYY-MM-DD)
- Total_Sales: Revenue amount
- Total_Orders: Number of orders
- Top_Product: Best performing product
- Top_Customer: Highest value customer

## File Structure

```
├── main.py                 # Main application
├── config.py              # Configuration settings
├── data_processor.py      # Data handling
├── chart_generator.py     # Chart creation
├── insights_generator.py  # Business insights
├── pdf_report_generator.py # PDF creation
├── email_sender.py        # Email distribution
├── requirements.txt       # Dependencies
├── data/                  # Data files
├── reports/              # Generated reports
├── charts/               # Generated charts
└── logs/                 # Application logs
```

## Customization

### Adding New Metrics
Edit `data_processor.py` to add new calculations in the `calculate_metrics()` method.

### Custom Charts
Add new chart types in `chart_generator.py` following the existing patterns.

### Email Templates
Modify email templates in `email_sender.py` for custom styling.

### Report Sections
Customize report sections in `pdf_report_generator.py`.

## Scheduling

### Linux/Mac (cron)
```bash
# Run every Monday at 9 AM
0 9 * * 1 /path/to/python /path/to/main.py --send-email
```

### Windows (Task Scheduler)
Create a scheduled task to run `run_report.bat` weekly.

## Troubleshooting

### Common Issues

1. **Email not sending**: Check SMTP settings and app passwords
2. **Charts not generating**: Ensure matplotlib backend is properly configured
3. **PDF creation fails**: Check reportlab installation and permissions
4. **Data processing errors**: Verify CSV format and column names

### Getting Help

1. Run system tests: `python main.py --test-system`
2. Check logs in the `logs/` directory
3. Verify configuration with `config.validate_config()`

## Support

For issues and questions:
- Check the logs directory for detailed error messages
- Verify your configuration settings
- Test individual components using the test functions

## License

This project is licensed under the MIT License.
"""
    
    Path('README.md').write_text(readme_content)
    print("   ✅ Created: README.md")
    print()

def run_initial_test():
    """Run initial system test."""
    print("🧪 Running initial system test...")
    
    try:
        # Import and test the main module
        import main
        generator = main.BusinessReportGenerator()
        
        # Run basic tests
        test_results = generator.test_system()
        
        if test_results['overall_status'] == 'passed':
            print("   ✅ System test passed - Ready to use!")
        elif test_results['overall_status'] == 'partial':
            print("   ⚠️ Some tests failed - Check configuration")
        else:
            print("   ❌ System test failed - Check installation")
            
        return test_results['overall_status'] != 'failed'
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Business Intelligence Report Generator Setup")
    print("="*50)
    print()
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    print()
    
    # Setup steps
    steps = [
        ("Creating directory structure", create_directory_structure),
        ("Installing dependencies", install_dependencies),
        ("Creating sample data", create_sample_data),
        ("Creating environment template", create_env_template),
        ("Creating run scripts", create_run_scripts),
        ("Creating documentation", create_readme),
    ]
    
    success_count = 0
    for step_name, step_function in steps:
        try:
            result = step_function()
            if result is False:  # Some functions return False on failure
                print(f"❌ {step_name} failed")
            else:
                success_count += 1
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    print("="*50)
    
    if success_count == len(steps):
        print("🎉 Setup completed successfully!")
        print()
        
        # Run initial test
        if run_initial_test():
            print()
            print("🚀 NEXT STEPS:")
            print("1. Copy .env.template to .env and configure your settings")
            print("2. Run: python main.py --test-system")
            print("3. Generate your first report: python main.py")
            print()
            print("📚 Read README.md for detailed usage instructions")
        else:
            print()
            print("⚠️ Setup completed but system tests failed.")
            print("Please check the configuration and try again.")
    else:
        print(f"⚠️ Setup completed with {len(steps) - success_count} errors")
        print("Please resolve the issues and run setup again.")
    
    print()

if __name__ == "__main__":
    main()
        