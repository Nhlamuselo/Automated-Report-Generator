#!/usr/bin/env python3
"""
Insights Generator Module
Generates intelligent business insights and recommendations based on data analysis.
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import numpy as np

from config import get_config

class InsightsGenerator:
    """Generates intelligent business insights and actionable recommendations."""
    
    def __init__(self, config=None):
        """Initialize the insights generator."""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
    def generate_comprehensive_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business insights from metrics."""
        try:
            insights = {
                'executive_summary': self._generate_executive_summary(metrics),
                'performance_analysis': self._analyze_performance(metrics),
                'trend_insights': self._analyze_trends(metrics),
                'product_insights': self._analyze_products(metrics),
                'customer_insights': self._analyze_customers(metrics),
                'recommendations': self._generate_recommendations(metrics),
                'risk_alerts': self._identify_risks(metrics),
                'opportunities': self._identify_opportunities(metrics)
            }
            
            self.logger.info("Comprehensive insights generated successfully")
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            raise
    
    def _generate_executive_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate executive summary of business performance."""
        current_week = metrics['current_week']
        changes = metrics['changes']
        
        # Determine overall performance
        sales_trend = "increased" if changes['sales_change'] >= 0 else "decreased"
        orders_trend = "increased" if changes['orders_change'] >= 0 else "decreased"
        
        # Performance qualifier
        sales_qualifier = self._get_performance_qualifier(changes['sales_change'])
        orders_qualifier = self._get_performance_qualifier(changes['orders_change'])
        
        summary = f"""
        Week ending {current_week['week_end_formatted']} Performance Summary:
        
        Sales {sales_trend} {sales_qualifier} by {abs(changes['sales_change']):.1f}% to {self.config.METRICS_CONFIG['currency_symbol']}{current_week['sales']:,.0f}, 
        while orders {orders_trend} {orders_qualifier} by {abs(changes['orders_change']):.1f}% to {current_week['orders']:,} units.
        
        The average order value is currently {self.config.METRICS_CONFIG['currency_symbol']}{metrics['aov']['current']:.0f}, 
        representing a {abs(metrics['aov']['change']):.1f}% {"increase" if metrics['aov']['change'] >= 0 else "decrease"} from the previous week.
        """
        
        return summary.strip()
    
    def _analyze_performance(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze current performance against benchmarks."""
        performance_insights = []
        
        # Sales performance analysis
        sales_change = metrics['changes']['sales_change']
        sales_insight = {
            'metric': 'Sales Performance',
            'status': self._get_status_level(sales_change),
            'message': self._get_sales_performance_message(sales_change, metrics),
            'icon': '📈' if sales_change >= 0 else '📉'
        }
        performance_insights.append(sales_insight)
        
        # Orders performance analysis
        orders_change = metrics['changes']['orders_change']
        orders_insight = {
            'metric': 'Order Volume',
            'status': self._get_status_level(orders_change),
            'message': self._get_orders_performance_message(orders_change, metrics),
            'icon': '🛒' if orders_change >= 0 else '📦'
        }
        performance_insights.append(orders_insight)
        
        # AOV analysis
        aov_change = metrics['aov']['change']
        aov_insight = {
            'metric': 'Average Order Value',
            'status': self._get_status_level(aov_change),
            'message': self._get_aov_performance_message(aov_change, metrics),
            'icon': '💰' if aov_change >= 0 else '💸'
        }
        performance_insights.append(aov_insight)
        
        # Growth rate analysis
        if 'historical' in metrics:
            growth_rate = metrics['historical']['sales_growth_rate']
            growth_insight = {
                'metric': 'Overall Growth Trend',
                'status': self._get_status_level(growth_rate),
                'message': f"Overall growth rate is {growth_rate:.1f}% over the analyzed period, indicating {'strong momentum' if growth_rate > 5 else 'steady progress' if growth_rate > 0 else 'declining performance'}.",
                'icon': '📊'
            }
            performance_insights.append(growth_insight)
        
        return performance_insights
    
    def _analyze_trends(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze trends and patterns in the data."""
        trend_insights = []
        
        if 'trends' in metrics and metrics['trends'].get('status') != 'insufficient_data':
            trends = metrics['trends']
            
            # Sales trend analysis
            sales_trend_direction = trends['sales_trend_direction']
            sales_trend_insight = {
                'type': 'Sales Trend',
                'direction': sales_trend_direction,
                'message': self._get_trend_message('sales', sales_trend_direction, trends),
                'volatility': self._assess_volatility(trends['sales_volatility']),
                'icon': '📈' if sales_trend_direction == 'increasing' else '📉' if sales_trend_direction == 'decreasing' else '➡️'
            }
            trend_insights.append(sales_trend_insight)
            
            # Orders trend analysis
            orders_trend_direction = trends['orders_trend_direction']
            orders_trend_insight = {
                'type': 'Orders Trend',
                'direction': orders_trend_direction,
                'message': self._get_trend_message('orders', orders_trend_direction, trends),
                'volatility': self._assess_volatility(trends['orders_volatility']),
                'icon': '🛒' if orders_trend_direction == 'increasing' else '📦' if orders_trend_direction == 'decreasing' else '➡️'
            }
            trend_insights.append(orders_trend_insight)
            
            # Volatility insights
            if trends['sales_volatility'] > 0.2 or trends['orders_volatility'] > 0.2:
                volatility_insight = {
                    'type': 'Volatility Alert',
                    'direction': 'variable',
                    'message': 'Business metrics show high volatility, indicating inconsistent performance that may require operational review.',
                    'volatility': 'high',
                    'icon': '⚠️'
                }
                trend_insights.append(volatility_insight)
        
        return trend_insights
    
    def _analyze_products(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze product performance and patterns."""
        product_insights = []
        
        if 'products' in metrics:
            products = metrics['products']
            
            # Current top product
            current_product = products['current_top_product']
            most_frequent = products['most_frequent_top_product']
            
            if current_product != most_frequent:
                product_insights.append({
                    'type': 'Product Leadership Change',
                    'message': f"{current_product} is currently the top performer, while {most_frequent} has been the most consistent leader historically.",
                    'action': 'Monitor performance of new top product and analyze factors driving the change.',
                    'icon': '🔄'
                })
            else:
                product_insights.append({
                    'type': 'Product Consistency',
                    'message': f"{current_product} maintains its position as both current and historical top performer.",
                    'action': 'Continue supporting this strong performer while exploring growth opportunities.',
                    'icon': '⭐'
                })
            
            # Product diversity
            unique_products = products['unique_products_count']
            if unique_products < 3:
                product_insights.append({
                    'type': 'Product Concentration Risk',
                    'message': f"Only {unique_products} different products have been top performers, indicating high concentration.",
                    'action': 'Consider diversifying product portfolio or boosting underperforming products.',
                    'icon': '⚠️'
                })
            else:
                product_insights.append({
                    'type': 'Product Diversity',
                    'message': f"Good product diversity with {unique_products} different top performers shows balanced portfolio.",
                    'action': 'Maintain this diversity while identifying patterns in successful products.',
                    'icon': '🎯'
                })
        
        return product_insights
    
    def _analyze_customers(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze customer performance and relationships."""
        customer_insights = []
        
        if 'customers' in metrics:
            customers = metrics['customers']
            
            current_customer = customers['current_top_customer']
            most_frequent = customers['most_frequent_top_customer']
            unique_customers = customers['unique_customers_count']
            
            # Customer loyalty analysis
            if current_customer == most_frequent:
                customer_insights.append({
                    'type': 'Customer Loyalty',
                    'message': f"{current_customer} demonstrates strong loyalty as both current and most frequent top customer.",
                    'action': 'Strengthen relationship with this key customer and understand their success factors.',
                    'icon': '🏆'
                })
            else:
                customer_insights.append({
                    'type': 'Customer Dynamics',
                    'message': f"Customer leadership has shifted from {most_frequent} to {current_customer}.",
                    'action': 'Investigate reasons for customer ranking changes and address any service issues.',
                    'icon': '🔄'
                })
            
            # Customer base diversity
            if unique_customers < 4:
                customer_insights.append({
                    'type': 'Customer Concentration Risk',
                    'message': f"High customer concentration with only {unique_customers} different top customers.",
                    'action': 'Develop strategies to expand customer base and reduce dependency on few key accounts.',
                    'icon': '⚠️'
                })
            else:
                customer_insights.append({
                    'type': 'Customer Base Health',
                    'message': f"Healthy customer diversity with {unique_customers} different top customers.",
                    'action': 'Continue building strong relationships across diverse customer base.',
                    'icon': '👥'
                })
        
        return customer_insights
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable business recommendations."""
        recommendations = []
        
        # Sales-based recommendations
        sales_change = metrics['changes']['sales_change']
        if sales_change < -5:
            recommendations.append({
                'priority': 'High',
                'category': 'Sales Recovery',
                'title': 'Implement Sales Recovery Plan',
                'description': 'Sales have declined significantly. Consider promotional campaigns, customer outreach, or market analysis.',
                'expected_impact': 'High',
                'timeline': '1-2 weeks',
                'icon': '🚨'
            })
        elif sales_change > 10:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Growth Optimization',
                'title': 'Scale Successful Strategies',
                'description': 'Strong sales growth achieved. Identify and replicate successful strategies to sustain momentum.',
                'expected_impact': 'High',
                'timeline': '2-4 weeks',
                'icon': '🚀'
            })
        
        # Order-based recommendations
        orders_change = metrics['changes']['orders_change']
        aov_change = metrics['aov']['change']
        
        if orders_change < 0 and aov_change > 0:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Customer Acquisition',
                'title': 'Focus on Customer Acquisition',
                'description': 'Fewer orders but higher AOV suggests need for broader customer reach while maintaining quality.',
                'expected_impact': 'Medium',
                'timeline': '3-4 weeks',
                'icon': '🎯'
            })
        elif orders_change > 0 and aov_change < 0:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Revenue Optimization',
                'title': 'Implement Upselling Strategies',
                'description': 'More orders but lower AOV. Consider product bundling, premium options, or cross-selling.',
                'expected_impact': 'Medium',
                'timeline': '2-3 weeks',
                'icon': '💰'
            })
        
        # Product recommendations
        if 'products' in metrics:
            unique_products = metrics['products']['unique_products_count']
            if unique_products < 3:
                recommendations.append({
                    'priority': 'Low',
                    'category': 'Product Strategy',
                    'title': 'Diversify Product Portfolio',
                    'description': 'Limited product variety in top performers. Analyze market opportunities for expansion.',
                    'expected_impact': 'Medium',
                    'timeline': '4-8 weeks',
                    'icon': '📦'
                })
        
        # Trend-based recommendations
        if 'trends' in metrics and metrics['trends'].get('status') != 'insufficient_data':
            trends = metrics['trends']
            if trends['sales_volatility'] > 0.2:
                recommendations.append({
                    'priority': 'Medium',
                    'category': 'Business Stability',
                    'title': 'Reduce Business Volatility',
                    'description': 'High sales volatility detected. Review operational processes and market factors.',
                    'expected_impact': 'High',
                    'timeline': '4-6 weeks',
                    'icon': '⚖️'
                })
        
        # Growth recommendations
        if 'historical' in metrics:
            growth_rate = metrics['historical']['sales_growth_rate']
            if 0 < growth_rate < 5:
                recommendations.append({
                    'priority': 'Low',
                    'category': 'Growth Acceleration',
                    'title': 'Accelerate Growth Initiatives',
                    'description': 'Moderate growth rate suggests room for improvement. Consider market expansion or innovation.',
                    'expected_impact': 'Medium',
                    'timeline': '6-12 weeks',
                    'icon': '📈'
                })
        
        return recommendations
    
    def _identify_risks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential business risks from the data."""
        risks = []
        
        # Performance risks
        sales_change = metrics['changes']['sales_change']
        orders_change = metrics['changes']['orders_change']
        
        if sales_change < -10:
            risks.append({
                'level': 'High',
                'category': 'Revenue Risk',
                'description': f'Significant sales decline of {abs(sales_change):.1f}% poses immediate revenue risk.',
                'mitigation': 'Immediate action required: analyze root causes and implement corrective measures.',
                'icon': '🚨'
            })
        
        if orders_change < -15:
            risks.append({
                'level': 'High',
                'category': 'Demand Risk',
                'description': f'Sharp decline in orders ({abs(orders_change):.1f}%) indicates potential demand issues.',
                'mitigation': 'Review market conditions, customer feedback, and competitive landscape.',
                'icon': '⚠️'
            })
        
        # Customer concentration risk
        if 'customers' in metrics:
            unique_customers = metrics['customers']['unique_customers_count']
            if unique_customers < 3:
                risks.append({
                    'level': 'Medium',
                    'category': 'Customer Risk',
                    'description': f'High customer concentration with only {unique_customers} key customers creates dependency risk.',
                    'mitigation': 'Diversify customer base and strengthen relationships with existing customers.',
                    'icon': '👥'
                })
        
        # Product concentration risk
        if 'products' in metrics:
            unique_products = metrics['products']['unique_products_count']
            if unique_products < 3:
                risks.append({
                    'level': 'Medium',
                    'category': 'Product Risk',
                    'description': f'Limited product diversity with only {unique_products} top performers.',
                    'mitigation': 'Expand product portfolio or improve performance of existing products.',
                    'icon': '📦'
                })
        
        # Volatility risk
        if 'trends' in metrics and metrics['trends'].get('status') != 'insufficient_data':
            if metrics['trends']['sales_volatility'] > 0.3:
                risks.append({
                    'level': 'Medium',
                    'category': 'Volatility Risk',
                    'description': 'High business volatility creates unpredictable performance patterns.',
                    'mitigation': 'Implement stabilization measures and improve forecasting capabilities.',
                    'icon': '📊'
                })
        
        return risks
    
    def _identify_opportunities(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify business opportunities from the data."""
        opportunities = []
        
        # Growth opportunities
        sales_change = metrics['changes']['sales_change']
        orders_change = metrics['changes']['orders_change']
        aov_change = metrics['aov']['change']
        
        if sales_change > 5 and orders_change > 5:
            opportunities.append({
                'potential': 'High',
                'category': 'Market Expansion',
                'description': 'Strong performance in both sales and orders suggests market opportunity for expansion.',
                'action': 'Consider scaling operations, expanding territory, or increasing marketing investment.',
                'icon': '🚀'
            })
        
        if aov_change > 10:
            opportunities.append({
                'potential': 'Medium',
                'category': 'Premium Strategy',
                'description': f'AOV increased by {aov_change:.1f}%, indicating customer willingness to pay premium prices.',
                'action': 'Explore premium product lines or value-added services.',
                'icon': '💎'
            })
        
        # Product opportunities
        if 'products' in metrics:
            current_product = metrics['products']['current_top_product']
            opportunities.append({
                'potential': 'Medium',
                'category': 'Product Development',
                'description': f'{current_product} is performing well as current top product.',
                'action': f'Analyze {current_product} success factors and apply to other products or develop complementary offerings.',
                'icon': '⭐'
            })
        
        # Customer opportunities
        if 'customers' in metrics:
            current_customer = metrics['customers']['current_top_customer']
            opportunities.append({
                'potential': 'Medium',
                'category': 'Customer Success',
                'description': f'{current_customer} is the current top customer showing strong engagement.',
                'action': f'Study {current_customer} relationship model and replicate with other customers.',
                'icon': '🏆'
            })
        
        # Trend opportunities
        if 'trends' in metrics and metrics['trends'].get('status') != 'insufficient_data':
            if metrics['trends']['sales_trend_direction'] == 'increasing':
                opportunities.append({
                    'potential': 'High',
                    'category': 'Momentum Capture',
                    'description': 'Positive sales trend provides opportunity to accelerate growth.',
                    'action': 'Increase investment in successful channels and strategies while trend continues.',
                    'icon': '📈'
                })
        
        return opportunities
    
    def _get_performance_qualifier(self, change: float) -> str:
        """Get performance qualifier based on percentage change."""
        if abs(change) >= 20:
            return "dramatically"
        elif abs(change) >= 10:
            return "significantly"
        elif abs(change) >= 5:
            return "moderately"
        else:
            return "slightly"
    
    def _get_status_level(self, change: float) -> str:
        """Get status level based on performance change."""
        if change >= 10:
            return "excellent"
        elif change >= 5:
            return "good" 
        elif change >= 0:
            return "fair"
        elif change >= -5:
            return "concerning"
        else:
            return "critical"
    
    def _get_sales_performance_message(self, change: float, metrics: Dict[str, Any]) -> str:
        """Generate sales performance message."""
        current_sales = metrics['current_week']['sales']
        qualifier = self._get_performance_qualifier(change)
        
        if change >= 0:
            return f"Sales performance is strong with {qualifier} growth of {change:.1f}% to {self.config.METRICS_CONFIG['currency_symbol']}{current_sales:,.0f}."
        else:
            return f"Sales declined {qualifier} by {abs(change):.1f}% to {self.config.METRICS_CONFIG['currency_symbol']}{current_sales:,.0f}, requiring attention."
    
    def _get_orders_performance_message(self, change: float, metrics: Dict[str, Any]) -> str:
        """Generate orders performance message."""
        current_orders = metrics['current_week']['orders']
        qualifier = self._get_performance_qualifier(change)
        
        if change >= 0:
            return f"Order volume shows {qualifier} improvement of {change:.1f}% to {current_orders:,} orders."
        else:
            return f"Order volume decreased {qualifier} by {abs(change):.1f}% to {current_orders:,} orders."
    
    def _get_aov_performance_message(self, change: float, metrics: Dict[str, Any]) -> str:
        """Generate AOV performance message."""
        current_aov = metrics['aov']['current']
        qualifier = self._get_performance_qualifier(change)
        
        if change >= 0:
            return f"Average order value increased {qualifier} by {change:.1f}% to {self.config.METRICS_CONFIG['currency_symbol']}{current_aov:.0f}."
        else:
            return f"Average order value declined {qualifier} by {abs(change):.1f}% to {self.config.METRICS_CONFIG['currency_symbol']}{current_aov:.0f}."
    
    def _get_trend_message(self, metric_type: str, direction: str, trends: Dict[str, Any]) -> str:
        """Generate trend message."""
        if direction == 'increasing':
            return f"{metric_type.title()} shows positive upward trend with consistent growth pattern."
        elif direction == 'decreasing':
            return f"{metric_type.title()} shows concerning downward trend requiring intervention."
        else:
            return f"{metric_type.title()} remains stable with minimal variation over time."
    
    def _assess_volatility(self, volatility: float) -> str:
        """Assess volatility level."""
        if volatility > 0.3:
            return "high"
        elif volatility > 0.15:
            return "moderate"
        else:
            return "low"
    
    def generate_insights_summary(self, insights: Dict[str, Any]) -> str:
        """Generate a concise summary of all insights."""
        summary_parts = []
        
        # Add executive summary
        summary_parts.append("📊 EXECUTIVE SUMMARY")
        summary_parts.append(insights['executive_summary'])
        summary_parts.append("")
        
        # Add key performance highlights
        performance = insights['performance_analysis']
        summary_parts.append("🎯 KEY PERFORMANCE HIGHLIGHTS")
        for perf in performance[:3]:  # Top 3 performance insights
            summary_parts.append(f"{perf['icon']} {perf['metric']}: {perf['message']}")
        summary_parts.append("")
        
        # Add top recommendations
        if insights['recommendations']:
            summary_parts.append("💡 TOP RECOMMENDATIONS")
            high_priority_recs = [r for r in insights['recommendations'] if r['priority'] == 'High']
            for rec in high_priority_recs[:2]:  # Top 2 high priority
                summary_parts.append(f"{rec['icon']} {rec['title']}: {rec['description']}")
            summary_parts.append("")
        
        # Add critical risks
        high_risks = [r for r in insights['risk_alerts'] if r['level'] == 'High']
        if high_risks:
            summary_parts.append("⚠️ CRITICAL RISKS")
            for risk in high_risks[:2]:  # Top 2 critical risks
                summary_parts.append(f"{risk['icon']} {risk['category']}: {risk['description']}")
            summary_parts.append("")
        
        # Add top opportunities
        if insights['opportunities']:
            summary_parts.append("🚀 KEY OPPORTUNITIES")
            high_potential_ops = [o for o in insights['opportunities'] if o['potential'] == 'High']
            for opp in high_potential_ops[:2]:  # Top 2 high potential
                summary_parts.append(f"{opp['icon']} {opp['category']}: {opp['description']}")
        
        return "\n".join(summary_parts)