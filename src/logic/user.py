"""
User management logic for ToluStock.
Handles user authentication, authorization, and user-related operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .db import db
from .utils import hash_password, verify_password, validate_email


class UserManager:
    """Manages user operations and authentication."""
    
    def __init__(self):
        self.current_user = None
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            users = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            
            if users and verify_password(password, users[0]['password']):
                user = users[0]
                # Update last login
                db.execute_update(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user['id'],)
                )
                self.current_user = user
                return user
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def logout(self) -> None:
        """Logout current user."""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user."""
        return self.current_user
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return (self.current_user and 
                self.current_user.get('role') == 'admin')
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission."""
        if not self.current_user:
            return False
        
        role = self.current_user.get('role', 'user')
        
        # Admin has all permissions
        if role == 'admin':
            return True
        
        # Define role-based permissions
        user_permissions = {
            'view_stock', 'view_customers', 'view_suppliers',
            'view_reports', 'export_data'
        }
        
        manager_permissions = user_permissions | {
            'add_stock', 'edit_stock', 'delete_stock',
            'add_customers', 'edit_customers', 'delete_customers',
            'add_suppliers', 'edit_suppliers', 'delete_suppliers',
            'backup_data', 'manage_settings'
        }
        
        if role == 'manager':
            return permission in manager_permissions
        elif role == 'user':
            return permission in user_permissions
        
        return False
    
    def create_user(self, username: str, password: str, role: str = 'user', 
                   email: str = None) -> Optional[int]:
        """Create a new user."""
        try:
            # Validate input
            if not username or not password:
                return None
            
            if email and not validate_email(email):
                return None
            
            # Check if username already exists
            existing_users = db.execute_query(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            )
            
            if existing_users:
                return None  # Username already exists
            
            # Hash password and create user
            hashed_password = hash_password(password)
            user_id = db.execute_insert(
                """INSERT INTO users (username, password, role, email)
                   VALUES (?, ?, ?, ?)""",
                (username, hashed_password, role, email)
            )
            
            return user_id
        except Exception as e:
            print(f"User creation error: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information."""
        try:
            if not self.has_permission('manage_users') and user_id != self.current_user.get('id'):
                return False
            
            valid_fields = ['username', 'email', 'role']
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    updates.append(f"{field} = ?")
                    params.append(value)
                elif field == 'password':
                    updates.append("password = ?")
                    params.append(hash_password(value))
            
            if not updates:
                return False
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            
            rows_affected = db.execute_update(query, tuple(params))
            return rows_affected > 0
        except Exception as e:
            print(f"User update error: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            if not self.has_permission('manage_users'):
                return False
            
            # Don't allow deleting current user
            if user_id == self.current_user.get('id'):
                return False
            
            rows_affected = db.execute_update(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )
            return rows_affected > 0
        except Exception as e:
            print(f"User deletion error: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (admin only)."""
        try:
            if not self.has_permission('manage_users'):
                return []
            
            return db.execute_query(
                """SELECT id, username, role, email, created_at, last_login 
                   FROM users ORDER BY username"""
            )
        except Exception as e:
            print(f"Get users error: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            users = db.execute_query(
                "SELECT id, username, role, email, created_at, last_login FROM users WHERE id = ?",
                (user_id,)
            )
            return users[0] if users else None
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # Verify current user can change this password
            if not self.is_admin() and user_id != self.current_user.get('id'):
                return False
            
            # If not admin, verify old password
            if not self.is_admin():
                user = db.execute_query(
                    "SELECT password FROM users WHERE id = ?",
                    (user_id,)
                )
                
                if not user or not verify_password(old_password, user[0]['password']):
                    return False
            
            # Update password
            hashed_password = hash_password(new_password)
            rows_affected = db.execute_update(
                "UPDATE users SET password = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            
            return rows_affected > 0
        except Exception as e:
            print(f"Password change error: {e}")
            return False
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            stats = {}
            
            # Total users
            total_users = db.execute_query("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = total_users[0]['count'] if total_users else 0
            
            # Users by role
            role_stats = db.execute_query(
                "SELECT role, COUNT(*) as count FROM users GROUP BY role"
            )
            stats['users_by_role'] = {row['role']: row['count'] for row in role_stats}
            
            # Recent logins (last 7 days)
            recent_logins = db.execute_query(
                """SELECT COUNT(*) as count FROM users 
                   WHERE last_login >= datetime('now', '-7 days')"""
            )
            stats['recent_logins'] = recent_logins[0]['count'] if recent_logins else 0
            
            return stats
        except Exception as e:
            print(f"User stats error: {e}")
            return {}
    
    def reset_password(self, username: str) -> Optional[str]:
        """Reset user password (admin only)."""
        try:
            if not self.is_admin():
                return None
            
            # Generate temporary password
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Update password
            hashed_password = hash_password(temp_password)
            rows_affected = db.execute_update(
                "UPDATE users SET password = ? WHERE username = ?",
                (hashed_password, username)
            )
            
            if rows_affected > 0:
                return temp_password
            return None
        except Exception as e:
            print(f"Password reset error: {e}")
            return None


# Global user manager instance
user_manager = UserManager()