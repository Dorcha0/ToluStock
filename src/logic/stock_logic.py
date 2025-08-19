"""
Stock management logic for ToluStock.
Handles inventory operations, stock movements, and stock tracking.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from .db import db
from .user import user_manager
from .utils import generate_sku, safe_cast_int, safe_cast_float


class StockManager:
    """Manages stock/inventory operations."""
    
    def get_all_products(self, search: str = None, category_id: int = None) -> List[Dict[str, Any]]:
        """Get all products with optional filtering."""
        try:
            query = """
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (p.name LIKE ? OR p.sku LIKE ? OR p.description LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)
            
            query += " ORDER BY p.name"
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Get products error: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        try:
            products = db.execute_query("""
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.id = ?
            """, (product_id,))
            
            return products[0] if products else None
        except Exception as e:
            print(f"Get product error: {e}")
            return None
    
    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU."""
        try:
            products = db.execute_query("""
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.sku = ?
            """, (sku,))
            
            return products[0] if products else None
        except Exception as e:
            print(f"Get product by SKU error: {e}")
            return None
    
    def add_product(self, name: str, category_id: int = None, description: str = None,
                   unit_price: float = 0.0, quantity: int = 0, min_stock_level: int = 0,
                   supplier_id: int = None, sku: str = None) -> Optional[int]:
        """Add a new product to inventory."""
        try:
            if not user_manager.has_permission('add_stock'):
                return None
            
            # Generate SKU if not provided
            if not sku:
                category_name = ""
                if category_id:
                    categories = db.execute_query(
                        "SELECT name FROM categories WHERE id = ?", (category_id,)
                    )
                    if categories:
                        category_name = categories[0]['name']
                sku = generate_sku(name, category_name)
            
            # Check if SKU already exists
            existing = self.get_product_by_sku(sku)
            if existing:
                return None
            
            product_id = db.execute_insert("""
                INSERT INTO products 
                (name, category_id, sku, description, unit_price, quantity, 
                 min_stock_level, supplier_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, category_id, sku, description, unit_price, quantity, 
                  min_stock_level, supplier_id))
            
            # Record initial stock movement if quantity > 0
            if quantity > 0:
                self.record_stock_movement(
                    product_id, 'in', quantity, 'Initial stock', 'Initial inventory'
                )
            
            return product_id
        except Exception as e:
            print(f"Add product error: {e}")
            return None
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """Update product information."""
        try:
            if not user_manager.has_permission('edit_stock'):
                return False
            
            valid_fields = [
                'name', 'category_id', 'sku', 'description', 'unit_price',
                'min_stock_level', 'supplier_id'
            ]
            
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                return False
            
            # Add updated_at timestamp
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(product_id)
            
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
            rows_affected = db.execute_update(query, tuple(params))
            
            return rows_affected > 0
        except Exception as e:
            print(f"Update product error: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product."""
        try:
            if not user_manager.has_permission('delete_stock'):
                return False
            
            # Check if product has stock movements
            movements = db.execute_query(
                "SELECT COUNT(*) as count FROM stock_movements WHERE product_id = ?",
                (product_id,)
            )
            
            if movements and movements[0]['count'] > 0:
                # Don't delete products with movement history
                return False
            
            rows_affected = db.execute_update(
                "DELETE FROM products WHERE id = ?",
                (product_id,)
            )
            
            return rows_affected > 0
        except Exception as e:
            print(f"Delete product error: {e}")
            return False
    
    def adjust_stock(self, product_id: int, new_quantity: int, reason: str = None) -> bool:
        """Adjust stock quantity for a product."""
        try:
            if not user_manager.has_permission('edit_stock'):
                return False
            
            # Get current quantity
            product = self.get_product_by_id(product_id)
            if not product:
                return False
            
            current_quantity = product['quantity']
            difference = new_quantity - current_quantity
            
            if difference == 0:
                return True
            
            # Update product quantity
            rows_affected = db.execute_update(
                "UPDATE products SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_quantity, product_id)
            )
            
            if rows_affected > 0:
                # Record stock movement
                movement_type = 'in' if difference > 0 else 'out'
                self.record_stock_movement(
                    product_id, movement_type, abs(difference), 
                    'adjustment', reason or 'Stock adjustment'
                )
                return True
            
            return False
        except Exception as e:
            print(f"Stock adjustment error: {e}")
            return False
    
    def record_stock_movement(self, product_id: int, movement_type: str, 
                            quantity: int, reference_id: str = None, 
                            notes: str = None) -> Optional[int]:
        """Record a stock movement."""
        try:
            user_id = user_manager.get_current_user()
            user_id = user_id['id'] if user_id else None
            
            movement_id = db.execute_insert("""
                INSERT INTO stock_movements 
                (product_id, movement_type, quantity, reference_id, notes, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product_id, movement_type, quantity, reference_id, notes, user_id))
            
            return movement_id
        except Exception as e:
            print(f"Record movement error: {e}")
            return None
    
    def get_stock_movements(self, product_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get stock movements with optional product filter."""
        try:
            query = """
                SELECT sm.*, p.name as product_name, p.sku, u.username
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                LEFT JOIN users u ON sm.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if product_id:
                query += " AND sm.product_id = ?"
                params.append(product_id)
            
            query += " ORDER BY sm.created_at DESC LIMIT ?"
            params.append(limit)
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Get movements error: {e}")
            return []
    
    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Get products with low stock levels."""
        try:
            return db.execute_query("""
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.quantity <= p.min_stock_level
                ORDER BY (p.quantity - p.min_stock_level) ASC, p.name
            """)
        except Exception as e:
            print(f"Get low stock error: {e}")
            return []
    
    def get_stock_statistics(self) -> Dict[str, Any]:
        """Get stock statistics."""
        try:
            stats = {}
            
            # Total products
            total_products = db.execute_query("SELECT COUNT(*) as count FROM products")
            stats['total_products'] = total_products[0]['count'] if total_products else 0
            
            # Total stock value
            stock_value = db.execute_query(
                "SELECT SUM(quantity * unit_price) as total_value FROM products"
            )
            stats['total_stock_value'] = stock_value[0]['total_value'] or 0.0
            
            # Low stock count
            low_stock = db.execute_query(
                "SELECT COUNT(*) as count FROM products WHERE quantity <= min_stock_level"
            )
            stats['low_stock_count'] = low_stock[0]['count'] if low_stock else 0
            
            # Out of stock count
            out_of_stock = db.execute_query(
                "SELECT COUNT(*) as count FROM products WHERE quantity = 0"
            )
            stats['out_of_stock_count'] = out_of_stock[0]['count'] if out_of_stock else 0
            
            # Categories with products
            categories = db.execute_query("""
                SELECT c.name, COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                GROUP BY c.id, c.name
                ORDER BY product_count DESC
            """)
            stats['categories'] = categories
            
            return stats
        except Exception as e:
            print(f"Stock statistics error: {e}")
            return {}
    
    def search_products(self, search_term: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Advanced product search."""
        try:
            if not search_fields:
                search_fields = ['name', 'sku', 'description']
            
            conditions = []
            params = []
            
            for field in search_fields:
                if field in ['name', 'sku', 'description']:
                    conditions.append(f"p.{field} LIKE ?")
                    params.append(f"%{search_term}%")
                elif field == 'category':
                    conditions.append("c.name LIKE ?")
                    params.append(f"%{search_term}%")
                elif field == 'supplier':
                    conditions.append("s.name LIKE ?")
                    params.append(f"%{search_term}%")
            
            if not conditions:
                return []
            
            query = f"""
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE {' OR '.join(conditions)}
                ORDER BY p.name
            """
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Product search error: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        try:
            return db.execute_query("SELECT * FROM categories ORDER BY name")
        except Exception as e:
            print(f"Get categories error: {e}")
            return []
    
    def add_category(self, name: str, description: str = None) -> Optional[int]:
        """Add a new category."""
        try:
            if not user_manager.has_permission('edit_stock'):
                return None
            
            category_id = db.execute_insert(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
            return category_id
        except Exception as e:
            print(f"Add category error: {e}")
            return None


# Global stock manager instance
stock_manager = StockManager()