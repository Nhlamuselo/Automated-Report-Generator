#!/usr/bin/env python3
"""
Chart Generator Module
Creates professional, publication-ready charts and visualizations.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Any

from config import get_config

class ChartGenerator:
    """Generates professional charts and visualizations for business reports."""
    
    def __init__(self, config=None):
        """Initialize the chart generator."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        self.charts_dir = self.config.CHARTS_DIR
        
        # Set up matplotlib and seaborn styling
        self._setup_chart_styling()
        
    def _setup_chart_styling(self):
        """Configure matplotlib and seaborn styling for professional charts."""
        # Set matplotlib parameters
        plt.rcParams.update({
            'figure.figsize': self.config.CHART_CONFIG['figure_size'],
            'figure.dpi': self.config.CHART_CONFIG['dpi'],
            'font.size': self.config.CHART_CONFIG['font_size'],
            'axes.titlesize': self.config.CHART_CONFIG['title_size'],
            'axes.labelsize': self.config.CHART_CONFIG['label_size'],
            'xtick.labelsize': self.config.CHART_CONFIG['font_size'] - 1,
            'ytick.labelsize': self.config.CHART_CONFIG['font_size'] - 1,
            'legend.fontsize': self.config.CHART_CONFIG['font_size'],
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.grid': True,
            'axes.grid.alpha': 0.3,
            'grid.linewidth': 0.5,
            'lines.linewidth': 2.5,
            'lines.markersize': 6
        })
        
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def create_sales_trend_chart(self, chart_data: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Create a professional sales trend line chart."""
        try:
            # Prepare data
            dates = pd.to_datetime(chart_data['dates'])
            sales = chart_data['sales']
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Main line plot
            line = ax.plot(dates, sales, 
                          color=self.config.COLORS['primary'],
                          linewidth=3,
                          marker='o',
                          markersize=8,
                          markerfacecolor='white',
                          markeredgewidth=2,
                          markeredgecolor=self.config.COLORS['primary'],
                          label='Weekly Sales')
            
            # Add trend line
            if len(sales) > 2:
                z = np.polyfit(range(len(sales)), sales, 1)
                p = np.poly1d(z)
                trend_line = ax.plot(dates, p(range(len(sales))),
                                   color=self.config.COLORS['secondary'],
                                   linestyle='--',
                                   alpha=0.7,
                                   linewidth=2,
                                   label=f'Trend Line ({"↗" if z[0] > 0 else "↘"})')
            
            # Highlight current week point
            if len(dates) > 0:
                ax.scatter(dates.iloc[-1], sales[-1],
                          color=self.config.COLORS['positive'],
                          s=150,
                          zorder=10,
                          edgecolor='white',
                          linewidth=2,
                          label='Current Week')
            
            # Formatting
            ax.set_title('Weekly Sales Performance Trend', 
                        fontsize=18, 
                        fontweight='bold',
                        color=self.config.COLORS['text_dark'],
                        pad=20)
            
            ax.set_xlabel('Week', fontsize=14, fontweight='medium')
            ax.set_ylabel(f'Sales ({self.config.METRICS_CONFIG["currency_symbol"]})', 
                         fontsize=14, fontweight='medium')
            
            # Format y-axis with currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{self.config.METRICS_CONFIG["currency_symbol"]}{x:,.0f}'))
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Add grid styling
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # Add performance indicators
            current_sales = metrics['current_week']['sales']
            avg_sales = metrics['historical']['average_weekly_sales']
            
            # Add average line
            ax.axhline(y=avg_sales, 
                      color=self.config.COLORS['warning'],
                      linestyle=':',
                      alpha=0.8,
                      linewidth=2,
                      label=f'Average ({self.config.METRICS_CONFIG["currency_symbol"]}{avg_sales:,.0f})')
            
            # Legend
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # Tight layout
            plt.tight_layout()
            
            # Save chart
            filename = self.charts_dir / 'sales_trend.png'
            plt.savefig(filename, 
                       dpi=self.config.CHART_CONFIG['dpi'],
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none')
            plt.close()
            
            self.logger.info(f"Sales trend chart created: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error creating sales trend chart: {e}")
            raise
    
    def create_orders_trend_chart(self, chart_data: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Create orders trend chart with dual-axis for AOV."""
        try:
            dates = pd.to_datetime(chart_data['dates'])
            orders = chart_data['orders']
            aov = chart_data['aov']
            
            # Create figure with dual y-axis
            fig, ax1 = plt.subplots(figsize=(14, 8))
            ax2 = ax1.twinx()
            
            # Orders line (left axis)
            line1 = ax1.plot(dates, orders,
                            color=self.config.COLORS['positive'],
                            linewidth=3,
                            marker='s',
                            markersize=7,
                            markerfacecolor='white',
                            markeredgewidth=2,
                            markeredgecolor=self.config.COLORS['positive'],
                            label='Orders')
            
            # AOV line (right axis)
            line2 = ax2.plot(dates, aov,
                            color=self.config.COLORS['accent1'],
                            linewidth=3,
                            marker='^',
                            markersize=7,
                            markerfacecolor='white',
                            markeredgewidth=2,
                            markeredgecolor=self.config.COLORS['accent1'],
                            label='Avg Order Value')
            
            # Formatting
            ax1.set_title('Orders Trend & Average Order Value', 
                         fontsize=18, 
                         fontweight='bold',
                         color=self.config.COLORS['text_dark'],
                         pad=20)
            
            # Left axis (Orders)
            ax1.set_xlabel('Week', fontsize=14, fontweight='medium')
            ax1.set_ylabel('Number of Orders', fontsize=14, fontweight='medium', 
                          color=self.config.COLORS['positive'])
            ax1.tick_params(axis='y', labelcolor=self.config.COLORS['positive'])
            
            # Right axis (AOV)
            ax2.set_ylabel(f'Average Order Value ({self.config.METRICS_CONFIG["currency_symbol"]})', 
                          fontsize=14, fontweight='medium',
                          color=self.config.COLORS['accent1'])
            ax2.tick_params(axis='y', labelcolor=self.config.COLORS['accent1'])
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{self.config.METRICS_CONFIG["currency_symbol"]}{x:,.0f}'))
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Grid
            ax1.grid(True, alpha=0.3)
            ax1.set_axisbelow(True)
            
            # Combined legend
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            plt.tight_layout()
            
            filename = self.charts_dir / 'orders_trend.png'
            plt.savefig(filename, 
                       dpi=self.config.CHART_CONFIG['dpi'],
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none')
            plt.close()
            
            self.logger.info(f"Orders trend chart created: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error creating orders trend chart: {e}")
            raise
    
    def create_product_analysis_chart(self, chart_data: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Create product performance analysis chart."""
        try:
            products = chart_data['products']
            product_freq = metrics['products']['product_frequency']
            
            # Create horizontal bar chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Prepare data
            product_names = list(product_freq.keys())
            frequencies = list(product_freq.values())
            
            # Create color palette
            colors = [self.config.COLORS['primary'], 
                     self.config.COLORS['positive'],
                     self.config.COLORS['accent1'],
                     self.config.COLORS['accent2'],
                     self.config.COLORS['warning']]
            bar_colors = colors[:len(product_names)]
            
            # Create bars
            bars = ax.barh(product_names, frequencies, color=bar_colors, alpha=0.8)
            
            # Add value labels on bars
            for i, (bar, freq) in enumerate(zip(bars, frequencies)):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{freq} weeks',
                       ha='left', va='center',
                       fontweight='medium',
                       fontsize=11)
            
            # Formatting
            ax.set_title('Top Products Performance Analysis', 
                        fontsize=18, 
                        fontweight='bold',
                        color=self.config.COLORS['text_dark'],
                        pad=20)
            
            ax.set_xlabel('Weeks as Top Product', fontsize=14, fontweight='medium')
            ax.set_ylabel('Product', fontsize=14, fontweight='medium')
            
            # Grid
            ax.grid(True, alpha=0.3, axis='x')
            ax.set_axisbelow(True)
            
            # Highlight current top product
            current_product = metrics['products']['current_top_product']
            if current_product in product_names:
                idx = product_names.index(current_product)
                bars[idx].set_edgecolor(self.config.COLORS['negative'])
                bars[idx].set_linewidth(3)
                # Add star annotation
                ax.text(frequencies[idx] + 0.5, idx,
                       '⭐ Current',
                       ha='left', va='center',
                       fontweight='bold',
                       fontsize=10,
                       color=self.config.COLORS['negative'])
            
            plt.tight_layout()
            
            filename = self.charts_dir / 'product_analysis.png'
            plt.savefig(filename, 
                       dpi=self.config.CHART_CONFIG['dpi'],
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none')
            plt.close()
            
            self.logger.info(f"Product analysis chart created: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error creating product analysis chart: {e}")
            raise
    
    def create_customer_analysis_chart(self, chart_data: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Create customer analysis donut chart."""
        try:
            customer_freq = metrics['customers']['customer_frequency']
            
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Prepare data
            customers = list(customer_freq.keys())
            frequencies = list(customer_freq.values())
            
            # Create color palette
            colors = plt.cm.Set3(np.linspace(0, 1, len(customers)))
            
            # Create donut chart
            wedges, texts, autotexts = ax.pie(frequencies,
                                             labels=customers,
                                             colors=colors,
                                             autopct='%1.1f%%',
                                             startangle=90,
                                             wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2))
            
            # Beautify text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            
            for text in texts:
                text.set_fontsize(12)
                text.set_fontweight('medium')
            
            # Title
            ax.set_title('Top Customers Distribution', 
                        fontsize=18, 
                        fontweight='bold',
                        color=self.config.COLORS['text_dark'],
                        pad=20)
            
            # Add center text
            current_customer = metrics['customers']['current_top_customer']
            ax.text(0, 0, f'Current Week\n⭐ {current_customer}',
                   ha='center', va='center',
                   fontsize=14,
                   fontweight='bold',
                   color=self.config.COLORS['text_dark'],
                   bbox=dict(boxstyle="round,pad=0.3", 
                            facecolor='white', 
                            edgecolor=self.config.COLORS['primary'],
                            linewidth=2))
            
            plt.axis('equal')
            plt.tight_layout()
            
            filename = self.charts_dir / 'customer_analysis.png'
            plt.savefig(filename, 
                       dpi=self.config.CHART_CONFIG['dpi'],
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none')
            plt.close()
            
            self.logger.info(f"Customer analysis chart created: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error creating customer analysis chart: {e}")
            raise
    
    def create_performance_dashboard(self, chart_data: Dict[str, Any], metrics: Dict[str, Any]) -> Path:
        """Create a comprehensive dashboard with multiple metrics."""
        try:
            fig = plt.figure(figsize=(16, 12))
            
            # Create subplot grid
            gs = fig.add_gridspec(3, 3, height_ratios=[1, 1.5, 1], width_ratios=[1, 1, 1])
            
            # KPI Cards (Top row)
            self._create_kpi_cards(fig, gs, metrics)
            
            # Main charts (Middle row)
            ax_sales = fig.add_subplot(gs[1, :2])
            ax_orders = fig.add_subplot(gs[1, 2])
            
            # Sales trend
            dates = pd.to_datetime(chart_data['dates'])
            sales = chart_data['sales']
            
            ax_sales.plot(dates, sales, 
                         color=self.config.COLORS['primary'],
                         linewidth=3, marker='o', markersize=6)
            ax_sales.set_title('Sales Trend', fontweight='bold')
            ax_sales.grid(True, alpha=0.3)
            
            # Orders bar chart
            ax_orders.bar(range(len(chart_data['orders'])), chart_data['orders'],
                         color=self.config.COLORS['positive'], alpha=0.8)
            ax_orders.set_title('Orders by Week', fontweight='bold')
            ax_orders.grid(True, alpha=0.3)
            
            # Bottom charts
            ax_product = fig.add_subplot(gs[2, :2])
            ax_aov = fig.add_subplot(gs[2, 2])
            
            # Product frequency
            product_freq = metrics['products']['product_frequency']
            if product_freq:
                products = list(product_freq.keys())[:5]  # Top 5
                freqs = list(product_freq.values())[:5]
                ax_product.barh(products, freqs, color=self.config.COLORS['accent1'], alpha=0.8)
                ax_product.set_title('Top Products', fontweight='bold')
            
            # AOV trend
            aov = chart_data['aov']
            ax_aov.plot(range(len(aov)), aov,
                       color=self.config.COLORS['warning'],
                       linewidth=2, marker='s', markersize=5)
            ax_aov.set_title('Avg Order Value', fontweight='bold')
            ax_aov.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filename = self.charts_dir / 'performance_dashboard.png'
            plt.savefig(filename, 
                       dpi=self.config.CHART_CONFIG['dpi'],
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none')
            plt.close()
            
            self.logger.info(f"Performance dashboard created: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error creating performance dashboard: {e}")
            raise
    
    def _create_kpi_cards(self, fig, gs, metrics):
        """Create KPI cards for the dashboard."""
        kpi_data = [
            {
                'title': 'Weekly Sales',
                'value': f"{self.config.METRICS_CONFIG['currency_symbol']}{metrics['current_week']['sales']:,.0f}",
                'change': f"{metrics['changes']['sales_change']:+.1f}%",
                'color': self.config.COLORS['positive'] if metrics['changes']['sales_change'] >= 0 else self.config.COLORS['negative']
            },
            {
                'title': 'Weekly Orders', 
                'value': f"{metrics['current_week']['orders']:,}",
                'change': f"{metrics['changes']['orders_change']:+.1f}%",
                'color': self.config.COLORS['positive'] if metrics['changes']['orders_change'] >= 0 else self.config.COLORS['negative']
            },
            {
                'title': 'Avg Order Value',
                'value': f"{self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f}",
                'change': f"{metrics['aov']['change']:+.1f}%",
                'color': self.config.COLORS['positive'] if metrics['aov']['change'] >= 0 else self.config.COLORS['negative']
            }
        ]
        
        for i, kpi in enumerate(kpi_data):
            ax = fig.add_subplot(gs[0, i])
            ax.text(0.5, 0.7, kpi['title'], ha='center', va='center',
                   fontsize=12, fontweight='medium', transform=ax.transAxes)
            ax.text(0.5, 0.4, kpi['value'], ha='center', va='center',
                   fontsize=18, fontweight='bold', transform=ax.transAxes)
            ax.text(0.5, 0.1, kpi['change'], ha='center', va='center',
                   fontsize=14, fontweight='bold', color=kpi['color'], transform=ax.transAxes)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Add border
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(2)
                spine.set_edgecolor(kpi['color'])
    
    def generate_all_charts(self, chart_data: Dict[str, Any], metrics: Dict[str, Any]) -> List[Path]:
        """Generate all charts and return list of file paths."""
        try:
            self.logger.info("Starting chart generation...")
            
            chart_files = []
            
            # Generate individual charts
            chart_files.append(self.create_sales_trend_chart(chart_data, metrics))
            chart_files.append(self.create_orders_trend_chart(chart_data, metrics))
            chart_files.append(self.create_product_analysis_chart(chart_data, metrics))
            chart_files.append(self.create_customer_analysis_chart(chart_data, metrics))
            chart_files.append(self.create_performance_dashboard(chart_data, metrics))
            
            self.logger.info(f"Generated {len(chart_files)} charts successfully")
            return chart_files
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
            raise
    
    def cleanup_old_charts(self, keep_days: int = 7):
        """Remove old chart files to save space."""
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            removed_count = 0
            for chart_file in self.charts_dir.glob('*.png'):
                if chart_file.stat().st_mtime < cutoff_date.timestamp():
                    chart_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old chart files")
                
        except Exception as e:
            self.logger.warning(f"Error cleaning up old charts: {e}")