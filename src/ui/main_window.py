"""
Main window UI for ToluStock.
Provides the main application window with menu, toolbar, and content area.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.user import user_manager
from logic.settings_logic import settings_manager


class MainWindow:
    """Main application window class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_frame = None
        self.setup_window()
        self.create_menu()
        self.create_toolbar()
        self.create_content_area()
        self.setup_status_bar()
        
        # Check if user is logged in
        if not user_manager.is_authenticated():
            self.show_login()
        else:
            self.show_dashboard()
    
    def setup_window(self):
        """Setup main window properties."""
        self.root.title(settings_manager.get_setting('app_name', 'ToluStock'))
        
        # Get window dimensions from settings
        width = settings_manager.get_setting('window_width', 1200)
        height = settings_manager.get_setting('window_height', 800)
        
        # Center window on screen
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # Set window icon (if logo exists)
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'logo.png')
            if os.path.exists(logo_path):
                self.root.iconphoto(True, tk.PhotoImage(file=logo_path))
        except:
            pass
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """Create application menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Product", command=self.new_product, accelerator="Ctrl+N")
        file_menu.add_command(label="New Customer", command=self.new_customer)
        file_menu.add_command(label="New Supplier", command=self.new_supplier)
        file_menu.add_separator()
        file_menu.add_command(label="Import Data...", command=self.import_data)
        file_menu.add_command(label="Export Data...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database...", command=self.backup_database)
        file_menu.add_command(label="Restore Database...", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Dashboard", command=self.show_dashboard, accelerator="F1")
        view_menu.add_command(label="Stock Management", command=self.show_stock, accelerator="F2")
        view_menu.add_command(label="Customers", command=self.show_customers, accelerator="F3")
        view_menu.add_command(label="Suppliers", command=self.show_suppliers, accelerator="F4")
        view_menu.add_command(label="Reports", command=self.show_reports, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="Advanced Search", command=self.show_advanced_search, accelerator="Ctrl+F")
        
        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        tools_menu.add_command(label="Backup Manager", command=self.show_backup)
        
        # User menu (show only if admin)
        if user_manager.is_admin():
            user_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Users", menu=user_menu)
            user_menu.add_command(label="User Management", command=self.show_user_management)
            user_menu.add_command(label="User Statistics", command=self.show_user_stats)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help & Documentation", command=self.show_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About ToluStock", command=self.show_about)
        
        # Account menu
        account_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Account", menu=account_menu)
        if user_manager.is_authenticated():
            current_user = user_manager.get_current_user()
            account_menu.add_command(
                label=f"Logged in as: {current_user.get('username', 'Unknown')}", 
                state="disabled"
            )
            account_menu.add_separator()
            account_menu.add_command(label="Change Password", command=self.change_password)
            account_menu.add_command(label="Logout", command=self.logout)
        else:
            account_menu.add_command(label="Login", command=self.show_login)
    
    def create_toolbar(self):
        """Create application toolbar."""
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Quick action buttons
        ttk.Button(
            self.toolbar_frame, 
            text="Dashboard", 
            command=self.show_dashboard
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            self.toolbar_frame, 
            text="Stock", 
            command=self.show_stock
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            self.toolbar_frame, 
            text="Customers", 
            command=self.show_customers
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            self.toolbar_frame, 
            text="Suppliers", 
            command=self.show_suppliers
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            self.toolbar_frame, 
            text="Reports", 
            command=self.show_reports
        ).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Search box
        ttk.Label(self.toolbar_frame, text="Quick Search:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.toolbar_frame, 
            textvariable=self.search_var,
            width=20
        )
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind('<Return>', self.quick_search)
        
        ttk.Button(
            self.toolbar_frame, 
            text="Search", 
            command=self.quick_search
        ).pack(side=tk.LEFT, padx=2)
    
    def create_content_area(self):
        """Create main content area."""
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_status_bar(self):
        """Setup status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # User info
        if user_manager.is_authenticated():
            current_user = user_manager.get_current_user()
            user_info = f"User: {current_user.get('username', 'Unknown')} ({current_user.get('role', 'user')})"
            ttk.Label(
                self.status_frame, 
                text=user_info,
                relief=tk.SUNKEN
            ).pack(side=tk.RIGHT, padx=2, pady=2)
    
    def clear_content(self):
        """Clear the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_frame = None
    
    def set_status(self, message: str):
        """Set status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_login(self):
        """Show login window."""
        from .login import LoginWindow
        self.clear_content()
        self.current_frame = LoginWindow(self.content_frame, self.on_login_success)
    
    def on_login_success(self):
        """Handle successful login."""
        self.create_menu()  # Recreate menu with user permissions
        self.setup_status_bar()  # Update status bar with user info
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show dashboard."""
        if not user_manager.is_authenticated():
            self.show_login()
            return
        
        from .dashboard import DashboardWindow
        self.clear_content()
        self.current_frame = DashboardWindow(self.content_frame)
        self.set_status("Dashboard loaded")
    
    def show_stock(self):
        """Show stock management."""
        if not user_manager.has_permission('view_stock'):
            messagebox.showerror("Access Denied", "You don't have permission to view stock.")
            return
        
        from .stock import StockWindow
        self.clear_content()
        self.current_frame = StockWindow(self.content_frame)
        self.set_status("Stock management loaded")
    
    def show_customers(self):
        """Show customer management."""
        if not user_manager.has_permission('view_customers'):
            messagebox.showerror("Access Denied", "You don't have permission to view customers.")
            return
        
        from .customer import CustomerWindow
        self.clear_content()
        self.current_frame = CustomerWindow(self.content_frame)
        self.set_status("Customer management loaded")
    
    def show_suppliers(self):
        """Show supplier management."""
        if not user_manager.has_permission('view_suppliers'):
            messagebox.showerror("Access Denied", "You don't have permission to view suppliers.")
            return
        
        from .supplier import SupplierWindow
        self.clear_content()
        self.current_frame = SupplierWindow(self.content_frame)
        self.set_status("Supplier management loaded")
    
    def show_reports(self):
        """Show reports."""
        if not user_manager.has_permission('view_reports'):
            messagebox.showerror("Access Denied", "You don't have permission to view reports.")
            return
        
        from .report import ReportWindow
        self.clear_content()
        self.current_frame = ReportWindow(self.content_frame)
        self.set_status("Reports loaded")
    
    def show_settings(self):
        """Show settings."""
        if not user_manager.has_permission('manage_settings'):
            messagebox.showerror("Access Denied", "You don't have permission to access settings.")
            return
        
        from .settings import SettingsWindow
        self.clear_content()
        self.current_frame = SettingsWindow(self.content_frame)
        self.set_status("Settings loaded")
    
    def show_backup(self):
        """Show backup manager."""
        if not user_manager.has_permission('backup_data'):
            messagebox.showerror("Access Denied", "You don't have permission to access backup.")
            return
        
        from .backup import BackupWindow
        self.clear_content()
        self.current_frame = BackupWindow(self.content_frame)
        self.set_status("Backup manager loaded")
    
    def show_user_management(self):
        """Show user management."""
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can manage users.")
            return
        
        from .user_management import UserManagementWindow
        self.clear_content()
        self.current_frame = UserManagementWindow(self.content_frame)
        self.set_status("User management loaded")
    
    def show_advanced_search(self):
        """Show advanced search."""
        from .advanced_search import AdvancedSearchWindow
        self.clear_content()
        self.current_frame = AdvancedSearchWindow(self.content_frame)
        self.set_status("Advanced search loaded")
    
    def show_help(self):
        """Show help."""
        from .help import HelpWindow
        self.clear_content()
        self.current_frame = HelpWindow(self.content_frame)
        self.set_status("Help loaded")
    
    def quick_search(self, event=None):
        """Perform quick search."""
        search_term = self.search_var.get().strip()
        if search_term:
            self.show_advanced_search()
            if hasattr(self.current_frame, 'set_search_term'):
                self.current_frame.set_search_term(search_term)
    
    def new_product(self):
        """Create new product."""
        if user_manager.has_permission('add_stock'):
            self.show_stock()
            if hasattr(self.current_frame, 'new_product'):
                self.current_frame.new_product()
    
    def new_customer(self):
        """Create new customer."""
        if user_manager.has_permission('add_customers'):
            self.show_customers()
            if hasattr(self.current_frame, 'new_customer'):
                self.current_frame.new_customer()
    
    def new_supplier(self):
        """Create new supplier."""
        if user_manager.has_permission('add_suppliers'):
            self.show_suppliers()
            if hasattr(self.current_frame, 'new_supplier'):
                self.current_frame.new_supplier()
    
    def import_data(self):
        """Import data."""
        filename = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            # Import logic would go here
            messagebox.showinfo("Import", f"Import from {filename} not yet implemented.")
    
    def export_data(self):
        """Export data."""
        filename = filedialog.asksaveasfilename(
            title="Export Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            # Export logic would go here
            messagebox.showinfo("Export", f"Export to {filename} not yet implemented.")
    
    def backup_database(self):
        """Backup database."""
        self.show_backup()
        if hasattr(self.current_frame, 'create_backup'):
            self.current_frame.create_backup()
    
    def restore_database(self):
        """Restore database."""
        self.show_backup()
        if hasattr(self.current_frame, 'restore_backup'):
            self.current_frame.restore_backup()
    
    def change_password(self):
        """Change password."""
        # This would open a password change dialog
        messagebox.showinfo("Change Password", "Password change dialog not yet implemented.")
    
    def logout(self):
        """Logout user."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            user_manager.logout()
            self.create_menu()  # Recreate menu without user permissions
            self.setup_status_bar()  # Update status bar
            self.show_login()
    
    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts = """
        Keyboard Shortcuts:
        
        Ctrl+N    - New Product
        Ctrl+F    - Advanced Search
        Ctrl+Q    - Exit
        
        F1        - Dashboard
        F2        - Stock Management
        F3        - Customers
        F4        - Suppliers
        F5        - Reports
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        {settings_manager.get_setting('app_name', 'ToluStock')}
        Version {settings_manager.get_setting('version', '1.0.0')}
        
        A comprehensive inventory management system.
        
        © 2024 ToluStock Team
        """
        messagebox.showinfo("About ToluStock", about_text)
    
    def show_user_stats(self):
        """Show user statistics."""
        messagebox.showinfo("User Statistics", "User statistics dialog not yet implemented.")
    
    def setup_key_bindings(self):
        """Setup keyboard shortcuts."""
        self.root.bind('<Control-n>', lambda e: self.new_product())
        self.root.bind('<Control-f>', lambda e: self.show_advanced_search())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F1>', lambda e: self.show_dashboard())
        self.root.bind('<F2>', lambda e: self.show_stock())
        self.root.bind('<F3>', lambda e: self.show_customers())
        self.root.bind('<F4>', lambda e: self.show_suppliers())
        self.root.bind('<F5>', lambda e: self.show_reports())
    
    def on_closing(self):
        """Handle application closing."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit ToluStock?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.setup_key_bindings()
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()