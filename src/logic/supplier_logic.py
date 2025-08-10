"""
Supplier management logic for ToluStock.
Handles supplier operations and supplier-related functionality.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .db import db
from .user import user_manager
from .utils import validate_email, validate_phone


class SupplierManager:
    """Manages supplier operations."""
    
    def get_all_suppliers(self, search: str = None) -> List[Dict[str, Any]]:
        """Get all suppliers with optional search filtering."""
        try:
            if not user_manager.has_permission('view_suppliers'):
                return []
            
            query = "SELECT * FROM suppliers WHERE 1=1"
            params = []
            
            if search:
                query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            query += " ORDER BY name"
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Get suppliers error: {e}")
            return []
    
    def get_supplier_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """Get supplier by ID."""
        try:
            if not user_manager.has_permission('view_suppliers'):
                return None
            
            suppliers = db.execute_query(
                "SELECT * FROM suppliers WHERE id = ?",
                (supplier_id,)
            )
            
            return suppliers[0] if suppliers else None
        except Exception as e:
            print(f"Get supplier error: {e}")
            return None
    
    def search_suppliers(self, search_term: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Advanced supplier search."""
        try:
            if not user_manager.has_permission('view_suppliers'):
                return []
            
            if not search_fields:
                search_fields = ['name', 'email', 'phone']
            
            conditions = []
            params = []
            
            for field in search_fields:
                if field in ['name', 'email', 'phone', 'address']:
                    conditions.append(f"{field} LIKE ?")
                    params.append(f"%{search_term}%")
            
            if not conditions:
                return []
            
            query = f"""
                SELECT * FROM suppliers 
                WHERE {' OR '.join(conditions)}
                ORDER BY name
            """
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Supplier search error: {e}")
            return []
    
    def add_supplier(self, name: str, email: str = None, phone: str = None, 
                    address: str = None) -> Optional[int]:
        """Add a new supplier."""
        try:
            if not user_manager.has_permission('add_suppliers'):
                return None
            
            # Validate input
            if not name or not name.strip():
                return None
            
            if email and not validate_email(email):
                return None
            
            if phone and not validate_phone(phone):
                return None
            
            # Check if supplier with same email already exists
            if email:
                existing = db.execute_query(
                    "SELECT id FROM suppliers WHERE email = ?",
                    (email,)
                )
                if existing:
                    return None  # Email already exists
            
            supplier_id = db.execute_insert("""
                INSERT INTO suppliers (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            """, (name.strip(), email, phone, address))
            
            return supplier_id
        except Exception as e:
            print(f"Add supplier error: {e}")
            return None
    
    def update_supplier(self, supplier_id: int, **kwargs) -> bool:
        """Update supplier information."""
        try:
            if not user_manager.has_permission('edit_suppliers'):
                return False
            
            valid_fields = ['name', 'email', 'phone', 'address']
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    # Validate specific fields
                    if field == 'email' and value and not validate_email(value):
                        return False
                    if field == 'phone' and value and not validate_phone(value):
                        return False
                    if field == 'name' and (not value or not value.strip()):
                        return False
                    
                    updates.append(f"{field} = ?")
                    params.append(value.strip() if isinstance(value, str) else value)
            
            if not updates:
                return False
            
            # Check for duplicate email if updating email
            if 'email' in kwargs and kwargs['email']:
                existing = db.execute_query(
                    "SELECT id FROM suppliers WHERE email = ? AND id != ?",
                    (kwargs['email'], supplier_id)
                )
                if existing:
                    return False  # Email already exists for another supplier
            
            params.append(supplier_id)
            query = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = ?"
            
            rows_affected = db.execute_update(query, tuple(params))
            return rows_affected > 0
        except Exception as e:
            print(f"Update supplier error: {e}")
            return False
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete a supplier."""
        try:
            if not user_manager.has_permission('delete_suppliers'):
                return False
            
            # Check if supplier has associated products
            products = db.execute_query(
                "SELECT COUNT(*) as count FROM products WHERE supplier_id = ?",
                (supplier_id,)
            )
            
            if products and products[0]['count'] > 0:
                # Don't delete suppliers with associated products
                return False
            
            rows_affected = db.execute_update(
                "DELETE FROM suppliers WHERE id = ?",
                (supplier_id,)
            )
            
            return rows_affected > 0
        except Exception as e:
            print(f"Delete supplier error: {e}")
            return False
    
    def get_supplier_products(self, supplier_id: int) -> List[Dict[str, Any]]:
        """Get products associated with a supplier."""
        try:
            if not user_manager.has_permission('view_stock'):
                return []
            
            return db.execute_query("""
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.supplier_id = ?
                ORDER BY p.name
            """, (supplier_id,))
        except Exception as e:
            print(f"Get supplier products error: {e}")
            return []
    
    def get_supplier_statistics(self) -> Dict[str, Any]:
        """Get supplier statistics."""
        try:
            stats = {}
            
            # Total suppliers
            total_suppliers = db.execute_query("SELECT COUNT(*) as count FROM suppliers")
            stats['total_suppliers'] = total_suppliers[0]['count'] if total_suppliers else 0
            
            # Suppliers with email
            with_email = db.execute_query(
                "SELECT COUNT(*) as count FROM suppliers WHERE email IS NOT NULL AND email != ''"
            )
            stats['suppliers_with_email'] = with_email[0]['count'] if with_email else 0
            
            # Suppliers with phone
            with_phone = db.execute_query(
                "SELECT COUNT(*) as count FROM suppliers WHERE phone IS NOT NULL AND phone != ''"
            )
            stats['suppliers_with_phone'] = with_phone[0]['count'] if with_phone else 0
            
            # Recent suppliers (last 30 days)
            recent_suppliers = db.execute_query(
                """SELECT COUNT(*) as count FROM suppliers 
                   WHERE created_at >= datetime('now', '-30 days')"""
            )
            stats['recent_suppliers'] = recent_suppliers[0]['count'] if recent_suppliers else 0
            
            # Suppliers with products
            with_products = db.execute_query("""
                SELECT COUNT(DISTINCT s.id) as count
                FROM suppliers s
                JOIN products p ON s.id = p.supplier_id
            """)
            stats['suppliers_with_products'] = with_products[0]['count'] if with_products else 0
            
            # Top suppliers by product count
            top_suppliers = db.execute_query("""
                SELECT s.name, COUNT(p.id) as product_count
                FROM suppliers s
                LEFT JOIN products p ON s.id = p.supplier_id
                GROUP BY s.id, s.name
                ORDER BY product_count DESC
                LIMIT 5
            """)
            stats['top_suppliers'] = top_suppliers
            
            return stats
        except Exception as e:
            print(f"Supplier statistics error: {e}")
            return {}
    
    def export_suppliers(self, file_format: str = 'csv') -> Optional[str]:
        """Export suppliers to file."""
        try:
            if not user_manager.has_permission('export_data'):
                return None
            
            suppliers = self.get_all_suppliers()
            if not suppliers:
                return None
            
            from .utils import export_to_csv, export_to_json, sanitize_filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if file_format.lower() == 'csv':
                filename = f"suppliers_export_{timestamp}.csv"
                if export_to_csv(suppliers, filename):
                    return filename
            elif file_format.lower() == 'json':
                filename = f"suppliers_export_{timestamp}.json"
                if export_to_json(suppliers, filename):
                    return filename
            
            return None
        except Exception as e:
            print(f"Export suppliers error: {e}")
            return None
    
    def import_suppliers(self, filename: str) -> Dict[str, Any]:
        """Import suppliers from file."""
        try:
            if not user_manager.has_permission('add_suppliers'):
                return {'success': False, 'message': 'No permission to import suppliers'}
            
            from .utils import import_from_csv, import_from_json, get_file_extension
            
            file_ext = get_file_extension(filename)
            data = None
            
            if file_ext == 'csv':
                data = import_from_csv(filename)
            elif file_ext == 'json':
                data = import_from_json(filename)
            
            if not data:
                return {'success': False, 'message': 'Failed to read file or empty file'}
            
            imported = 0
            errors = []
            
            for row in data:
                try:
                    supplier_id = self.add_supplier(
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        phone=row.get('phone', ''),
                        address=row.get('address', '')
                    )
                    
                    if supplier_id:
                        imported += 1
                    else:
                        errors.append(f"Failed to import supplier: {row.get('name', 'Unknown')}")
                except Exception as e:
                    errors.append(f"Error importing {row.get('name', 'Unknown')}: {str(e)}")
            
            return {
                'success': True,
                'imported': imported,
                'total': len(data),
                'errors': errors
            }
        except Exception as e:
            print(f"Import suppliers error: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_supplier_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get supplier by email address."""
        try:
            suppliers = db.execute_query(
                "SELECT * FROM suppliers WHERE email = ?",
                (email,)
            )
            
            return suppliers[0] if suppliers else None
        except Exception as e:
            print(f"Get supplier by email error: {e}")
            return None
    
    def get_supplier_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get supplier by phone number."""
        try:
            suppliers = db.execute_query(
                "SELECT * FROM suppliers WHERE phone = ?",
                (phone,)
            )
            
            return suppliers[0] if suppliers else None
        except Exception as e:
            print(f"Get supplier by phone error: {e}")
            return None
    
    def validate_supplier_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate supplier data."""
        errors = []
        
        # Required fields
        if not data.get('name', '').strip():
            errors.append("Supplier name is required")
        
        # Email validation
        email = data.get('email', '')
        if email and not validate_email(email):
            errors.append("Invalid email format")
        
        # Phone validation
        phone = data.get('phone', '')
        if phone and not validate_phone(phone):
            errors.append("Invalid phone number format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }


# Global supplier manager instance
supplier_manager = SupplierManager()