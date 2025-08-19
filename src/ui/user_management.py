"""
User management UI for ToluStock.
Provides interface for managing users (admin only).
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.user import user_manager
from logic.utils import validate_email


class UserManagementWindow:
    """User management window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.selected_user = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the user management interface."""
        if not user_manager.is_admin():
            # Show access denied message
            ttk.Label(
                self.parent,
                text="Access Denied: Administrator privileges required",
                font=("Arial", 14, "bold"),
                foreground="red"
            ).pack(expand=True)
            return
        
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="User Management", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Change Password", command=self.change_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset Password", command=self.reset_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # Content with paned window
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - User list
        self.create_user_list(paned)
        
        # Right side - User details and statistics
        self.create_user_details(paned)
        
        paned.add(self.list_frame, weight=2)
        paned.add(self.details_frame, weight=1)
    
    def create_user_list(self, parent):
        """Create user list section."""
        self.list_frame = ttk.LabelFrame(parent, text="Users", padding=10)
        
        # Users tree
        columns = ("Username", "Role", "Email", "Created", "Last Login")
        self.user_tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        self.user_tree.bind('<Double-1>', self.on_user_double_click)
    
    def create_user_details(self, parent):
        """Create user details section."""
        self.details_frame = ttk.Frame(parent)
        
        # User details
        details_section = ttk.LabelFrame(self.details_frame, text="User Details", padding=10)
        details_section.pack(fill=tk.X, pady=(0, 10))
        
        self.detail_vars = {}
        fields = [("Username", "username"), ("Role", "role"), ("Email", "email"), 
                 ("Created", "created_at"), ("Last Login", "last_login")]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(details_section, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, pady=2
            )
            var = tk.StringVar()
            self.detail_vars[key] = var
            ttk.Label(details_section, textvariable=var, font=("Arial", 10)).grid(
                row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0)
            )
        
        # User statistics
        stats_section = ttk.LabelFrame(self.details_frame, text="User Statistics", padding=10)
        stats_section.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_section, height=10, width=40, font=("Arial", 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Load user stats
        self.load_user_statistics()
        
        # Actions for selected user
        actions_section = ttk.LabelFrame(self.details_frame, text="Actions", padding=10)
        actions_section.pack(fill=tk.X)
        
        ttk.Button(actions_section, text="Edit", command=self.edit_selected_user, width=15).pack(pady=2, fill=tk.X)
        ttk.Button(actions_section, text="Change Password", command=self.change_user_password, width=15).pack(pady=2, fill=tk.X)
        ttk.Button(actions_section, text="Reset Password", command=self.reset_user_password, width=15).pack(pady=2, fill=tk.X)
        ttk.Button(actions_section, text="Delete", command=self.delete_selected_user, width=15).pack(pady=2, fill=tk.X)
    
    def load_data(self):
        """Load user data."""
        if not user_manager.is_admin():
            return
        self.refresh_user_list()
    
    def refresh_user_list(self):
        """Refresh user list."""
        try:
            # Clear existing items
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            
            # Get users
            users = user_manager.get_all_users()
            
            # Add to tree
            for user in users:
                created_at = user.get('created_at', '')[:19] if user.get('created_at') else ''
                last_login = user.get('last_login', '')[:19] if user.get('last_login') else 'Never'
                
                self.user_tree.insert('', 'end', values=(
                    user['username'],
                    user['role'].title(),
                    user['email'] or '',
                    created_at,
                    last_login
                ), tags=(user['id'],))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
    
    def load_user_statistics(self):
        """Load user statistics."""
        try:
            stats = user_manager.get_user_stats()
            
            stats_text = "User Statistics\n" + "="*30 + "\n\n"
            stats_text += f"Total Users: {stats.get('total_users', 0)}\n\n"
            
            # Users by role
            users_by_role = stats.get('users_by_role', {})
            stats_text += "Users by Role:\n"
            for role, count in users_by_role.items():
                stats_text += f"  {role.title()}: {count}\n"
            
            stats_text += f"\nRecent Logins (7 days): {stats.get('recent_logins', 0)}\n"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error loading user statistics: {e}")
    
    def on_user_select(self, event=None):
        """Handle user selection."""
        selection = self.user_tree.selection()
        if selection:
            item = self.user_tree.item(selection[0])
            user_id = item['tags'][0] if item['tags'] else None
            if user_id:
                self.load_user_details(user_id)
        else:
            self.clear_user_details()
    
    def load_user_details(self, user_id):
        """Load user details."""
        try:
            user = user_manager.get_user_by_id(user_id)
            if user:
                self.selected_user = user
                
                # Update details
                for key, var in self.detail_vars.items():
                    value = user.get(key, '')
                    if key in ['created_at', 'last_login'] and value:
                        value = value[:19] if len(str(value)) > 19 else str(value)
                    var.set(str(value) if value else 'N/A')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user details: {str(e)}")
    
    def clear_user_details(self):
        """Clear user details."""
        self.selected_user = None
        for var in self.detail_vars.values():
            var.set('')
    
    def on_user_double_click(self, event=None):
        """Handle user double-click."""
        self.edit_selected_user()
    
    def add_user(self):
        """Add new user."""
        UserDialog(self.parent, self.on_user_saved)
    
    def edit_user(self):
        """Edit selected user."""
        self.edit_selected_user()
    
    def edit_selected_user(self):
        """Edit the currently selected user."""
        if not self.selected_user:
            messagebox.showwarning("No Selection", "Please select a user to edit.")
            return
        UserDialog(self.parent, self.on_user_saved, self.selected_user)
    
    def change_password(self):
        """Change password for selected user."""
        self.change_user_password()
    
    def change_user_password(self):
        """Change password for the currently selected user."""
        if not self.selected_user:
            messagebox.showwarning("No Selection", "Please select a user to change password.")
            return
        
        PasswordChangeDialog(self.parent, self.selected_user, self.on_password_changed)
    
    def reset_password(self):
        """Reset password for selected user."""
        self.reset_user_password()
    
    def reset_user_password(self):
        """Reset password for the currently selected user."""
        if not self.selected_user:
            messagebox.showwarning("No Selection", "Please select a user to reset password.")
            return
        
        if messagebox.askyesno(
            "Confirm Reset",
            f"Reset password for user '{self.selected_user['username']}'?\n\n"
            "A temporary password will be generated."
        ):
            try:
                temp_password = user_manager.reset_password(self.selected_user['username'])
                if temp_password:
                    messagebox.showinfo(
                        "Password Reset",
                        f"Password reset successfully.\n\nTemporary password: {temp_password}\n\n"
                        "Please give this password to the user and ask them to change it."
                    )
                else:
                    messagebox.showerror("Error", "Failed to reset password.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error resetting password: {str(e)}")
    
    def delete_user(self):
        """Delete selected user."""
        self.delete_selected_user()
    
    def delete_selected_user(self):
        """Delete the currently selected user."""
        if not self.selected_user:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return
        
        current_user = user_manager.get_current_user()
        if self.selected_user['id'] == current_user['id']:
            messagebox.showerror("Error", "Cannot delete your own account.")
            return
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user '{self.selected_user['username']}'?\n\n"
            "This action cannot be undone."
        ):
            try:
                if user_manager.delete_user(self.selected_user['id']):
                    messagebox.showinfo("Success", "User deleted successfully.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "Failed to delete user.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting user: {str(e)}")
    
    def refresh_data(self):
        """Refresh all data."""
        self.load_data()
        self.load_user_statistics()
    
    def on_user_saved(self, user_id):
        """Handle user save."""
        self.refresh_user_list()
        self.load_user_statistics()
        if user_id:
            self.load_user_details(user_id)
    
    def on_password_changed(self):
        """Handle password change."""
        messagebox.showinfo("Success", "Password changed successfully.")


class UserDialog:
    """Dialog for adding/editing users."""
    
    def __init__(self, parent, callback, user=None):
        self.callback = callback
        self.user = user
        self.is_edit = user is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit User" if self.is_edit else "Add User")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        if self.is_edit:
            self.populate_fields()
    
    def setup_dialog(self):
        """Setup dialog."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Password (only for new users)
        if not self.is_edit:
            ttk.Label(main_frame, text="Password *:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.password_var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=25).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Role
        row = 2 if not self.is_edit else 1
        ttk.Label(main_frame, text="Role *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(
            main_frame,
            textvariable=self.role_var,
            values=["user", "manager", "admin"],
            state="readonly",
            width=22
        )
        self.role_combo.grid(row=row, column=1, pady=5, sticky=tk.W)
        
        # Email
        row += 1
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=25).grid(row=row, column=1, pady=5, sticky=tk.W)
        
        # Buttons
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus username field
        self.username_entry.focus()
    
    def populate_fields(self):
        """Populate fields with user data."""
        if not self.user:
            return
        
        self.username_var.set(self.user.get('username', ''))
        self.role_var.set(self.user.get('role', 'user'))
        self.email_var.set(self.user.get('email', ''))
        
        # Disable username for editing
        self.username_entry.config(state='readonly')
    
    def save_user(self):
        """Save user."""
        try:
            username = self.username_var.get().strip()
            if not username:
                messagebox.showerror("Validation Error", "Username is required.")
                return
            
            role = self.role_var.get()
            if not role:
                messagebox.showerror("Validation Error", "Role is required.")
                return
            
            email = self.email_var.get().strip() or None
            if email and not validate_email(email):
                messagebox.showerror("Validation Error", "Invalid email format.")
                return
            
            if self.is_edit:
                success = user_manager.update_user(
                    self.user['id'],
                    username=username,
                    role=role,
                    email=email
                )
                
                if success:
                    messagebox.showinfo("Success", "User updated successfully.")
                    user_id = self.user['id']
                else:
                    messagebox.showerror("Error", "Failed to update user.")
                    return
            else:
                password = self.password_var.get()
                if not password:
                    messagebox.showerror("Validation Error", "Password is required.")
                    return
                
                if len(password) < 6:
                    messagebox.showerror("Validation Error", "Password must be at least 6 characters.")
                    return
                
                user_id = user_manager.create_user(
                    username=username,
                    password=password,
                    role=role,
                    email=email
                )
                
                if user_id:
                    messagebox.showinfo("Success", "User created successfully.")
                else:
                    messagebox.showerror("Error", "Failed to create user. Username may already exist.")
                    return
            
            if self.callback:
                self.callback(user_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving user: {str(e)}")


class PasswordChangeDialog:
    """Dialog for changing user password."""
    
    def __init__(self, parent, user, callback):
        self.user = user
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Change Password - {user['username']}")
        self.dialog.geometry("350x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup dialog."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text=f"Change password for: {self.user['username']}",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 15))
        
        # Current password (for non-admin users changing their own password)
        current_user = user_manager.get_current_user()
        if current_user['id'] == self.user['id'] and not user_manager.is_admin():
            ttk.Label(main_frame, text="Current Password:").pack(anchor=tk.W)
            self.current_password_var = tk.StringVar()
            ttk.Entry(main_frame, textvariable=self.current_password_var, show="*", width=30).pack(pady=(5, 10))
        else:
            self.current_password_var = None
        
        # New password
        ttk.Label(main_frame, text="New Password:").pack(anchor=tk.W)
        self.new_password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.new_password_var, show="*", width=30).pack(pady=(5, 10))
        
        # Confirm password
        ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W)
        self.confirm_password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.confirm_password_var, show="*", width=30).pack(pady=(5, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Change", command=self.change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def change_password(self):
        """Change the password."""
        try:
            new_password = self.new_password_var.get()
            confirm_password = self.confirm_password_var.get()
            
            if not new_password:
                messagebox.showerror("Validation Error", "New password is required.")
                return
            
            if len(new_password) < 6:
                messagebox.showerror("Validation Error", "Password must be at least 6 characters.")
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Validation Error", "Passwords do not match.")
                return
            
            old_password = ""
            if self.current_password_var:
                old_password = self.current_password_var.get()
                if not old_password:
                    messagebox.showerror("Validation Error", "Current password is required.")
                    return
            
            if user_manager.change_password(self.user['id'], old_password, new_password):
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to change password. Check current password.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error changing password: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("User Management Test")
    root.geometry("900x700")
    
    user_mgmt_window = UserManagementWindow(root)
    root.mainloop()