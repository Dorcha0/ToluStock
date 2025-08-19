"""
Report generation logic for ToluStock.
Handles various types of reports and analytics.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from .db import db
from .user import user_manager
from .utils import export_to_csv, export_to_json, format_currency, format_date


class ReportManager:
    """Manages report generation and analytics."""
    
    def generate_stock_report(self, category_id: int = None, 
                            low_stock_only: bool = False) -> Dict[str, Any]:
        """Generate comprehensive stock report."""
        try:
            if not user_manager.has_permission('view_reports'):
                return {}
            
            query = """
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            """
            params = []
            
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)
            
            if low_stock_only:
                query += " AND p.quantity <= p.min_stock_level"
            
            query += " ORDER BY p.name"
            
            products = db.execute_query(query, tuple(params))
            
            # Calculate summary statistics
            total_products = len(products)
            total_value = sum(p['quantity'] * p['unit_price'] for p in products)
            total_quantity = sum(p['quantity'] for p in products)
            low_stock_count = sum(1 for p in products if p['quantity'] <= p['min_stock_level'])
            out_of_stock_count = sum(1 for p in products if p['quantity'] == 0)
            
            return {
                'report_type': 'Stock Report',
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'filters': {
                    'category_id': category_id,
                    'low_stock_only': low_stock_only
                },
                'summary': {
                    'total_products': total_products,
                    'total_value': total_value,
                    'total_quantity': total_quantity,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count
                },
                'products': products
            }
        except Exception as e:
            print(f"Stock report error: {e}")
            return {}
    
    def generate_inventory_valuation_report(self) -> Dict[str, Any]:
        """Generate inventory valuation report."""
        try:
            if not user_manager.has_permission('view_reports'):
                return {}
            
            # Get products with valuation
            products = db.execute_query("""
                SELECT p.*, c.name as category_name,
                       (p.quantity * p.unit_price) as total_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY total_value DESC
            """)
            
            # Group by category
            category_totals = {}
            for product in products:
                category = product['category_name'] or 'Uncategorized'
                if category not in category_totals:
                    category_totals[category] = {
                        'products': 0,
                        'total_quantity': 0,
                        'total_value': 0.0
                    }
                
                category_totals[category]['products'] += 1
                category_totals[category]['total_quantity'] += product['quantity']
                category_totals[category]['total_value'] += product['total_value']
            
            return {
                'report_type': 'Inventory Valuation Report',
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'total_value': sum(p['total_value'] for p in products),
                'category_breakdown': category_totals,
                'products': products
            }
        except Exception as e:
            print(f"Valuation report error: {e}")
            return {}
    
    def generate_stock_movement_report(self, days: int = 30, 
                                     product_id: int = None) -> Dict[str, Any]:
        """Generate stock movement report for specified period."""
        try:
            if not user_manager.has_permission('view_reports'):
                return {}
            
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT sm.*, p.name as product_name, p.sku, u.username
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                LEFT JOIN users u ON sm.user_id = u.id
                WHERE sm.created_at >= ?
            """
            params = [start_date.isoformat()]
            
            if product_id:
                query += " AND sm.product_id = ?"
                params.append(product_id)
            
            query += " ORDER BY sm.created_at DESC"
            
            movements = db.execute_query(query, tuple(params))
            
            # Calculate summary
            total_movements = len(movements)
            movements_in = [m for m in movements if m['movement_type'] == 'in']
            movements_out = [m for m in movements if m['movement_type'] == 'out']
            
            total_in = sum(m['quantity'] for m in movements_in)
            total_out = sum(m['quantity'] for m in movements_out)
            
            return {
                'report_type': 'Stock Movement Report',
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.now().isoformat(),
                'filters': {
                    'product_id': product_id
                },
                'summary': {
                    'total_movements': total_movements,
                    'movements_in': len(movements_in),
                    'movements_out': len(movements_out),
                    'total_quantity_in': total_in,
                    'total_quantity_out': total_out,
                    'net_movement': total_in - total_out
                },
                'movements': movements
            }
        except Exception as e:
            print(f"Movement report error: {e}")
            return {}
    
    def generate_low_stock_alert_report(self) -> Dict[str, Any]:
        """Generate low stock alert report."""
        try:
            if not user_manager.has_permission('view_reports'):
                return {}
            
            low_stock_products = db.execute_query("""
                SELECT p.*, c.name as category_name, s.name as supplier_name,
                       (p.min_stock_level - p.quantity) as shortage
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.quantity <= p.min_stock_level
                ORDER BY shortage DESC, p.name
            """)
            
            # Categorize alerts
            critical_alerts = [p for p in low_stock_products if p['quantity'] == 0]
            warning_alerts = [p for p in low_stock_products if p['quantity'] > 0]
            
            return {
                'report_type': 'Low Stock Alert Report',
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'summary': {
                    'total_alerts': len(low_stock_products),
                    'critical_alerts': len(critical_alerts),
                    'warning_alerts': len(warning_alerts)
                },
                'critical_items': critical_alerts,
                'warning_items': warning_alerts,
                'all_items': low_stock_products
            }
        except Exception as e:
            print(f"Low stock report error: {e}")
            return {}
    
    def generate_category_analysis_report(self) -> Dict[str, Any]:
        """Generate category analysis report."""
        try:
            if not user_manager.has_permission('view_reports'):
                return {}
            
            category_stats = db.execute_query("""
                SELECT c.name as category_name,
                       COUNT(p.id) as product_count,
                       SUM(p.quantity) as total_quantity,
                       SUM(p.quantity * p.unit_price) as total_value,
                       AVG(p.unit_price) as avg_price,
                       MIN(p.unit_price) as min_price,
                       MAX(p.unit_price) as max_price
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                GROUP BY c.id, c.name
                ORDER BY total_value DESC
            """)
            
            return {
                'report_type': 'Category Analysis Report',
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'categories': category_stats
            }
        except Exception as e:
            print(f"Category analysis error: {e}")
            return {}
    
    def generate_supplier_analysis_report(self) -> Dict[str, Any]:
        """Generate supplier analysis report."""
        try:
            if not user_manager.has_permission('view_reports'):
                return {}
            
            supplier_stats = db.execute_query("""
                SELECT s.name as supplier_name,
                       s.email, s.phone,
                       COUNT(p.id) as product_count,
                       SUM(p.quantity) as total_quantity,
                       SUM(p.quantity * p.unit_price) as total_value,
                       AVG(p.unit_price) as avg_price
                FROM suppliers s
                LEFT JOIN products p ON s.id = p.supplier_id
                GROUP BY s.id, s.name, s.email, s.phone
                ORDER BY total_value DESC
            """)
            
            return {
                'report_type': 'Supplier Analysis Report',
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'suppliers': supplier_stats
            }
        except Exception as e:
            print(f"Supplier analysis error: {e}")
            return {}
    
    def generate_custom_report(self, query: str, title: str = "Custom Report") -> Dict[str, Any]:
        """Generate custom report from SQL query (admin only)."""
        try:
            if not user_manager.is_admin():
                return {}
            
            # Basic SQL injection protection
            forbidden_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create']
            query_lower = query.lower()
            
            for keyword in forbidden_keywords:
                if keyword in query_lower:
                    return {'error': f'Forbidden keyword: {keyword}'}
            
            results = db.execute_query(query)
            
            return {
                'report_type': title,
                'generated_at': datetime.now().isoformat(),
                'generated_by': user_manager.get_current_user().get('username', 'Unknown'),
                'query': query,
                'results': results
            }
        except Exception as e:
            print(f"Custom report error: {e}")
            return {'error': str(e)}
    
    def export_report(self, report_data: Dict[str, Any], filename: str, 
                     file_format: str = 'csv') -> bool:
        """Export report data to file."""
        try:
            if not user_manager.has_permission('export_data'):
                return False
            
            if file_format.lower() == 'csv':
                # Extract tabular data from report
                if 'products' in report_data:
                    data = report_data['products']
                elif 'movements' in report_data:
                    data = report_data['movements']
                elif 'results' in report_data:
                    data = report_data['results']
                elif 'categories' in report_data:
                    data = report_data['categories']
                elif 'suppliers' in report_data:
                    data = report_data['suppliers']
                else:
                    return False
                
                return export_to_csv(data, filename)
            
            elif file_format.lower() == 'json':
                return export_to_json(report_data, filename)
            
            return False
        except Exception as e:
            print(f"Export report error: {e}")
            return False
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary data for dashboard."""
        try:
            # Stock summary
            stock_summary = db.execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(quantity) as total_quantity,
                    SUM(quantity * unit_price) as total_value,
                    COUNT(CASE WHEN quantity <= min_stock_level THEN 1 END) as low_stock_count,
                    COUNT(CASE WHEN quantity = 0 THEN 1 END) as out_of_stock_count
                FROM products
            """)[0]
            
            # Recent movements
            recent_movements = db.execute_query("""
                SELECT COUNT(*) as count
                FROM stock_movements 
                WHERE created_at >= datetime('now', '-7 days')
            """)[0]['count']
            
            # Customer/Supplier counts
            customer_count = db.execute_query("SELECT COUNT(*) as count FROM customers")[0]['count']
            supplier_count = db.execute_query("SELECT COUNT(*) as count FROM suppliers")[0]['count']
            
            # Top products by value
            top_products = db.execute_query("""
                SELECT name, quantity * unit_price as value
                FROM products 
                ORDER BY value DESC 
                LIMIT 5
            """)
            
            return {
                'stock_summary': stock_summary,
                'recent_movements': recent_movements,
                'customer_count': customer_count,
                'supplier_count': supplier_count,
                'top_products': top_products
            }
        except Exception as e:
            print(f"Dashboard summary error: {e}")
            return {}
    
    def schedule_report(self, report_type: str, frequency: str, 
                       recipients: List[str]) -> bool:
        """Schedule automated report generation (placeholder)."""
        # This would be implemented with a task scheduler in a full application
        return True


# Global report manager instance
report_manager = ReportManager()