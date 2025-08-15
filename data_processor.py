#!/usr/bin/env python3
"""
Data Processor Module
Handles data loading, cleaning, and processing for the report generator.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json

from config import get_config

class DataProcessor:
    """Handles all data processing operations for the report system."""
    
    def __init__(self, config=None):
        """Initialize the data processor."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        self.data = None
        self.processed_data = None
        
    def load_data_from_csv(self, file_path: Optional[Path] = None, csv_content: Optional[str] = None) -> pd.DataFrame:
        """Load data from CSV file or string content."""
        try:
            if csv_content:
                # Load from string content (for demo/testing)
                from io import StringIO
                self.data = pd.read_csv(StringIO(csv_content))
                self.logger.info("Data loaded from string content")
            elif file_path:
                self.data = pd.read_csv(file_path)
                self.logger.info(f"Data loaded from {file_path}")
            else:
                # Use default CSV path
                default_path = self.config.CSV_FILE_PATH
                if default_path.exists():
                    self.data = pd.read_csv(default_path)
                    self.logger.info(f"Data loaded from default path: {default_path}")
                else:
                    raise FileNotFoundError(f"CSV file not found: {default_path}")
            
            return self.data
            
        except Exception as e:
            self.logger.error(f"Error loading CSV data: {e}")
            raise
    
    def load_sample_data(self) -> pd.DataFrame:
        """Load the sample business data for demonstration."""
        sample_data = """Week_Start,Week_End,Total_Sales,Total_Orders,Top_Product,Top_Customer
2025-01-06,2025-01-12,12500,45,Laptop,Alpha Corp
2025-01-13,2025-01-19,15800,52,Smartphone,Beta Ltd
2025-01-20,2025-01-26,14200,48,Tablet,Gamma LLC
2025-01-27,2025-02-02,16950,55,Monitor,Delta Inc
2025-02-03,2025-02-09,18100,60,Printer,Epsilon Co
2025-02-10,2025-02-16,17500,57,Keyboard,Zeta Enterprises
2025-02-17,2025-02-23,19000,62,Mouse,Eta Traders
2025-02-24,2025-03-02,20050,65,Headphones,Theta Solutions"""
        
        return self.load_data_from_csv(csv_content=sample_data)
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and prepare the data for analysis."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data_from_csv() first.")
        
        try:
            # Create a copy for processing
            cleaned_data = self.data.copy()
            
            # Convert date columns to datetime
            cleaned_data['Week_Start'] = pd.to_datetime(cleaned_data['Week_Start'])
            cleaned_data['Week_End'] = pd.to_datetime(cleaned_data['Week_End'])
            
            # Sort by week start date
            cleaned_data = cleaned_data.sort_values('Week_Start')
            
            # Handle missing values
            numeric_columns = ['Total_Sales', 'Total_Orders']
            for col in numeric_columns:
                if cleaned_data[col].isnull().any():
                    # Fill missing numeric values with interpolation
                    cleaned_data[col] = cleaned_data[col].interpolate()
                    self.logger.warning(f"Missing values in {col} filled using interpolation")
            
            # Fill missing categorical values
            categorical_columns = ['Top_Product', 'Top_Customer']
            for col in categorical_columns:
                if cleaned_data[col].isnull().any():
                    cleaned_data[col] = cleaned_data[col].fillna('Unknown')
                    self.logger.warning(f"Missing values in {col} filled with 'Unknown'")
            
            # Remove duplicates
            initial_count = len(cleaned_data)
            cleaned_data = cleaned_data.drop_duplicates(subset=['Week_Start'])
            if len(cleaned_data) < initial_count:
                self.logger.warning(f"Removed {initial_count - len(cleaned_data)} duplicate records")
            
            # Validate data integrity
            self._validate_data_integrity(cleaned_data)
            
            self.processed_data = cleaned_data
            self.logger.info(f"Data cleaned successfully. {len(cleaned_data)} records processed.")
            
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {e}")
            raise
    
    def _validate_data_integrity(self, data: pd.DataFrame):
        """Validate the integrity of the cleaned data."""
        # Check for negative values
        if (data['Total_Sales'] < 0).any() or (data['Total_Orders'] < 0).any():
            raise ValueError("Data contains negative values for sales or orders")
        
        # Check for unrealistic values
        max_reasonable_sales = data['Total_Sales'].median() * 10  # 10x median as threshold
        if (data['Total_Sales'] > max_reasonable_sales).any():
            self.logger.warning("Data contains unusually high sales values")
        
        # Check date consistency
        date_issues = data[data['Week_End'] <= data['Week_Start']]
        if not date_issues.empty:
            raise ValueError("Data contains weeks where end date is before start date")
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive business metrics."""
        if self.processed_data is None:
            raise ValueError("No processed data available. Call clean_data() first.")
        
        try:
            data = self.processed_data
            metrics = {}
            
            # Current period (latest week) metrics
            latest_week = data.iloc[-1]
            previous_week = data.iloc[-2] if len(data) > 1 else latest_week
            
            # Basic metrics
            metrics['current_week'] = {
                'sales': float(latest_week['Total_Sales']),
                'orders': int(latest_week['Total_Orders']),
                'top_product': str(latest_week['Top_Product']),
                'top_customer': str(latest_week['Top_Customer']),
                'week_start': latest_week['Week_Start'].strftime('%Y-%m-%d'),
                'week_end': latest_week['Week_End'].strftime('%Y-%m-%d'),
                'week_start_formatted': latest_week['Week_Start'].strftime('%d %b %Y'),
                'week_end_formatted': latest_week['Week_End'].strftime('%d %b %Y')
            }
            
            metrics['previous_week'] = {
                'sales': float(previous_week['Total_Sales']),
                'orders': int(previous_week['Total_Orders'])
            }
            
            # Calculate changes and growth rates
            current_sales = metrics['current_week']['sales']
            previous_sales = metrics['previous_week']['sales']
            current_orders = metrics['current_week']['orders']
            previous_orders = metrics['previous_week']['orders']
            
            metrics['changes'] = {
                'sales_change': self._calculate_percentage_change(current_sales, previous_sales),
                'orders_change': self._calculate_percentage_change(current_orders, previous_orders),
                'sales_absolute_change': current_sales - previous_sales,
                'orders_absolute_change': current_orders - previous_orders
            }
            
            # Average Order Value (AOV)
            current_aov = current_sales / current_orders if current_orders > 0 else 0
            previous_aov = previous_sales / previous_orders if previous_orders > 0 else 0
            
            metrics['aov'] = {
                'current': current_aov,
                'previous': previous_aov,
                'change': self._calculate_percentage_change(current_aov, previous_aov)
            }
            
            # Historical analysis
            metrics['historical'] = self._calculate_historical_metrics(data)
            
            # Product and customer analysis
            metrics['products'] = self._analyze_products(data)
            metrics['customers'] = self._analyze_customers(data)
            
            # Trend analysis
            metrics['trends'] = self._calculate_trends(data)
            
            self.logger.info("Metrics calculated successfully")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            raise
    
    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between two values."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
    
    def _calculate_historical_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate historical metrics and aggregations."""
        return {
            'total_sales': float(data['Total_Sales'].sum()),
            'total_orders': int(data['Total_Orders'].sum()),
            'average_weekly_sales': float(data['Total_Sales'].mean()),
            'average_weekly_orders': float(data['Total_Orders'].mean()),
            'max_weekly_sales': float(data['Total_Sales'].max()),
            'min_weekly_sales': float(data['Total_Sales'].min()),
            'sales_std_dev': float(data['Total_Sales'].std()),
            'weeks_count': len(data),
            'sales_growth_rate': self._calculate_growth_rate(data, 'Total_Sales'),
            'orders_growth_rate': self._calculate_growth_rate(data, 'Total_Orders')
        }
    
    def _calculate_growth_rate(self, data: pd.DataFrame, column: str) -> float:
        """Calculate compound average growth rate."""
        if len(data) < 2:
            return 0.0
        
        first_value = data[column].iloc[0]
        last_value = data[column].iloc[-1]
        periods = len(data) - 1
        
        if first_value <= 0:
            return 0.0
        
        growth_rate = ((last_value / first_value) ** (1 / periods) - 1) * 100
        return float(growth_rate)
    
    def _analyze_products(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze product performance."""
        product_counts = data['Top_Product'].value_counts()
        
        return {
            'most_frequent_top_product': str(product_counts.index[0]) if not product_counts.empty else 'None',
            'product_frequency': product_counts.to_dict(),
            'unique_products_count': len(product_counts),
            'current_top_product': str(data.iloc[-1]['Top_Product'])
        }
    
    def _analyze_customers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze customer performance."""
        customer_counts = data['Top_Customer'].value_counts()
        
        return {
            'most_frequent_top_customer': str(customer_counts.index[0]) if not customer_counts.empty else 'None',
            'customer_frequency': customer_counts.to_dict(),
            'unique_customers_count': len(customer_counts),
            'current_top_customer': str(data.iloc[-1]['Top_Customer'])
        }
    
    def _calculate_trends(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend indicators."""
        if len(data) < 3:
            return {'status': 'insufficient_data'}
        
        # Calculate moving averages
        data_copy = data.copy()
        data_copy['sales_ma3'] = data_copy['Total_Sales'].rolling(window=3).mean()
        data_copy['orders_ma3'] = data_copy['Total_Orders'].rolling(window=3).mean()
        
        # Trend direction (simple linear trend)
        sales_trend = np.polyfit(range(len(data)), data['Total_Sales'], 1)[0]
        orders_trend = np.polyfit(range(len(data)), data['Total_Orders'], 1)[0]
        
        # Volatility (coefficient of variation)
        sales_cv = data['Total_Sales'].std() / data['Total_Sales'].mean()
        orders_cv = data['Total_Orders'].std() / data['Total_Orders'].mean()
        
        return {
            'sales_trend_slope': float(sales_trend),
            'orders_trend_slope': float(orders_trend),
            'sales_trend_direction': 'increasing' if sales_trend > 0 else 'decreasing' if sales_trend < 0 else 'stable',
            'orders_trend_direction': 'increasing' if orders_trend > 0 else 'decreasing' if orders_trend < 0 else 'stable',
            'sales_volatility': float(sales_cv),
            'orders_volatility': float(orders_cv),
            'latest_ma3_sales': float(data_copy['sales_ma3'].iloc[-1]) if not pd.isna(data_copy['sales_ma3'].iloc[-1]) else 0,
            'latest_ma3_orders': float(data_copy['orders_ma3'].iloc[-1]) if not pd.isna(data_copy['orders_ma3'].iloc[-1]) else 0
        }
    
    def get_data_for_charts(self) -> Dict[str, Any]:
        """Prepare data specifically formatted for chart generation."""
        if self.processed_data is None:
            raise ValueError("No processed data available.")
        
        data = self.processed_data
        
        return {
            'dates': data['Week_Start'].dt.strftime('%Y-%m-%d').tolist(),
            'formatted_dates': data['Week_Start'].dt.strftime('%d %b').tolist(),
            'sales': data['Total_Sales'].tolist(),
            'orders': data['Total_Orders'].tolist(),
            'products': data['Top_Product'].tolist(),
            'customers': data['Top_Customer'].tolist(),
            'aov': (data['Total_Sales'] / data['Total_Orders']).tolist()
        }
    
    def export_processed_data(self, file_path: Optional[Path] = None) -> Path:
        """Export processed data to CSV for backup or further analysis."""
        if self.processed_data is None:
            raise ValueError("No processed data to export.")
        
        if file_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.config.DATA_DIR / f"processed_data_{timestamp}.csv"
        
        self.processed_data.to_csv(file_path, index=False)
        self.logger.info(f"Processed data exported to {file_path}")
        
        return file_path
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded data."""
        if self.processed_data is None:
            return {'status': 'no_data'}
        
        data = self.processed_data
        
        return {
            'total_records': len(data),
            'date_range': {
                'start': data['Week_Start'].min().strftime('%Y-%m-%d'),
                'end': data['Week_End'].max().strftime('%Y-%m-%d')
            },
            'columns': data.columns.tolist(),
            'data_types': data.dtypes.to_dict(),
            'missing_values': data.isnull().sum().to_dict(),
            'sales_range': {
                'min': float(data['Total_Sales'].min()),
                'max': float(data['Total_Sales'].max()),
                'mean': float(data['Total_Sales'].mean())
            },
            'orders_range': {
                'min': int(data['Total_Orders'].min()),
                'max': int(data['Total_Orders'].max()),
                'mean': float(data['Total_Orders'].mean())
            }
        }
