"""
Customer management logic for ToluStock.
Handles customer operations and customer-related functionality.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .db import db
from .user import user_manager
from .utils import validate_email, validate_phone


class CustomerManager:
    """Manages customer operations."""
    
    def get_all_customers(self, search: str = None) -> List[Dict[str, Any]]:
        """Get all customers with optional search filtering."""
        try:
            if not user_manager.has_permission('view_customers'):
                return []
            
            query = "SELECT * FROM customers WHERE 1=1"
            params = []
            
            if search:
                query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            query += " ORDER BY name"
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Get customers error: {e}")
            return []
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        try:
            if not user_manager.has_permission('view_customers'):
                return None
            
            customers = db.execute_query(
                "SELECT * FROM customers WHERE id = ?",
                (customer_id,)
            )
            
            return customers[0] if customers else None
        except Exception as e:
            print(f"Get customer error: {e}")
            return None
    
    def search_customers(self, search_term: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Advanced customer search."""
        try:
            if not user_manager.has_permission('view_customers'):
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
                SELECT * FROM customers 
                WHERE {' OR '.join(conditions)}
                ORDER BY name
            """
            
            return db.execute_query(query, tuple(params))
        except Exception as e:
            print(f"Customer search error: {e}")
            return []
    
    def add_customer(self, name: str, email: str = None, phone: str = None, 
                    address: str = None) -> Optional[int]:
        """Add a new customer."""
        try:
            if not user_manager.has_permission('add_customers'):
                return None
            
            # Validate input
            if not name or not name.strip():
                return None
            
            if email and not validate_email(email):
                return None
            
            if phone and not validate_phone(phone):
                return None
            
            # Check if customer with same email already exists
            if email:
                existing = db.execute_query(
                    "SELECT id FROM customers WHERE email = ?",
                    (email,)
                )
                if existing:
                    return None  # Email already exists
            
            customer_id = db.execute_insert("""
                INSERT INTO customers (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            """, (name.strip(), email, phone, address))
            
            return customer_id
        except Exception as e:
            print(f"Add customer error: {e}")
            return None
    
    def update_customer(self, customer_id: int, **kwargs) -> bool:
        """Update customer information."""
        try:
            if not user_manager.has_permission('edit_customers'):
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
                    "SELECT id FROM customers WHERE email = ? AND id != ?",
                    (kwargs['email'], customer_id)
                )
                if existing:
                    return False  # Email already exists for another customer
            
            params.append(customer_id)
            query = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"
            
            rows_affected = db.execute_update(query, tuple(params))
            return rows_affected > 0
        except Exception as e:
            print(f"Update customer error: {e}")
            return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer."""
        try:
            if not user_manager.has_permission('delete_customers'):
                return False
            
            # TODO: Check if customer has associated orders/transactions
            # For now, we'll allow deletion
            
            rows_affected = db.execute_update(
                "DELETE FROM customers WHERE id = ?",
                (customer_id,)
            )
            
            return rows_affected > 0
        except Exception as e:
            print(f"Delete customer error: {e}")
            return False
    
    def get_customer_statistics(self) -> Dict[str, Any]:
        """Get customer statistics."""
        try:
            stats = {}
            
            # Total customers
            total_customers = db.execute_query("SELECT COUNT(*) as count FROM customers")
            stats['total_customers'] = total_customers[0]['count'] if total_customers else 0
            
            # Customers with email
            with_email = db.execute_query(
                "SELECT COUNT(*) as count FROM customers WHERE email IS NOT NULL AND email != ''"
            )
            stats['customers_with_email'] = with_email[0]['count'] if with_email else 0
            
            # Customers with phone
            with_phone = db.execute_query(
                "SELECT COUNT(*) as count FROM customers WHERE phone IS NOT NULL AND phone != ''"
            )
            stats['customers_with_phone'] = with_phone[0]['count'] if with_phone else 0
            
            # Recent customers (last 30 days)
            recent_customers = db.execute_query(
                """SELECT COUNT(*) as count FROM customers 
                   WHERE created_at >= datetime('now', '-30 days')"""
            )
            stats['recent_customers'] = recent_customers[0]['count'] if recent_customers else 0
            
            return stats
        except Exception as e:
            print(f"Customer statistics error: {e}")
            return {}
    
    def export_customers(self, file_format: str = 'csv') -> Optional[str]:
        """Export customers to file."""
        try:
            if not user_manager.has_permission('export_data'):
                return None
            
            customers = self.get_all_customers()
            if not customers:
                return None
            
            from .utils import export_to_csv, export_to_json, sanitize_filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if file_format.lower() == 'csv':
                filename = f"customers_export_{timestamp}.csv"
                if export_to_csv(customers, filename):
                    return filename
            elif file_format.lower() == 'json':
                filename = f"customers_export_{timestamp}.json"
                if export_to_json(customers, filename):
                    return filename
            
            return None
        except Exception as e:
            print(f"Export customers error: {e}")
            return None
    
    def import_customers(self, filename: str) -> Dict[str, Any]:
        """Import customers from file."""
        try:
            if not user_manager.has_permission('add_customers'):
                return {'success': False, 'message': 'No permission to import customers'}
            
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
                    customer_id = self.add_customer(
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        phone=row.get('phone', ''),
                        address=row.get('address', '')
                    )
                    
                    if customer_id:
                        imported += 1
                    else:
                        errors.append(f"Failed to import customer: {row.get('name', 'Unknown')}")
                except Exception as e:
                    errors.append(f"Error importing {row.get('name', 'Unknown')}: {str(e)}")
            
            return {
                'success': True,
                'imported': imported,
                'total': len(data),
                'errors': errors
            }
        except Exception as e:
            print(f"Import customers error: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email address."""
        try:
            customers = db.execute_query(
                "SELECT * FROM customers WHERE email = ?",
                (email,)
            )
            
            return customers[0] if customers else None
        except Exception as e:
            print(f"Get customer by email error: {e}")
            return None
    
    def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get customer by phone number."""
        try:
            customers = db.execute_query(
                "SELECT * FROM customers WHERE phone = ?",
                (phone,)
            )
            
            return customers[0] if customers else None
        except Exception as e:
            print(f"Get customer by phone error: {e}")
            return None
    
    def validate_customer_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate customer data."""
        errors = []
        
        # Required fields
        if not data.get('name', '').strip():
            errors.append("Customer name is required")
        
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


# Global customer manager instance
customer_manager = CustomerManager()