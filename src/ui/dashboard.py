"""
Dashboard UI for ToluStock.
Provides overview of inventory status and quick actions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.stock_logic import stock_manager
from logic.customer_logic import customer_manager
from logic.supplier_logic import supplier_manager
from logic.report_logic import report_manager
from logic.user import user_manager
from logic.utils import format_currency


class DashboardWindow:
    """Dashboard window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the dashboard interface."""
        # Main container with scrollbar
        canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Welcome header
        self.create_header()
        
        # Statistics cards
        self.create_stats_section()
        
        # Recent activity
        self.create_activity_section()
        
        # Quick actions
        self.create_actions_section()
        
        # Alerts and notifications
        self.create_alerts_section()
    
    def create_header(self):
        """Create dashboard header."""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Welcome message
        current_user = user_manager.get_current_user()
        username = current_user.get('username', 'User') if current_user else 'User'
        
        welcome_label = ttk.Label(
            header_frame,
            text=f"Welcome back, {username}!",
            font=("Arial", 18, "bold")
        )
        welcome_label.pack(side=tk.LEFT)
        
        # Current date/time
        current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")
        time_label = ttk.Label(
            header_frame,
            text=current_time,
            font=("Arial", 10),
            foreground="gray"
        )
        time_label.pack(side=tk.RIGHT)
        
        # Refresh button
        refresh_button = ttk.Button(
            header_frame,
            text="Refresh",
            command=self.refresh_dashboard
        )
        refresh_button.pack(side=tk.RIGHT, padx=(0, 20))
    
    def create_stats_section(self):
        """Create statistics cards section."""
        stats_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Overview",
            padding=15
        )
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create grid of stats cards
        self.stats_cards = {}
        
        # Row 1
        self.create_stat_card(stats_frame, "total_products", "Total Products", "0", 0, 0)
        self.create_stat_card(stats_frame, "total_value", "Total Inventory Value", "$0.00", 0, 1)
        self.create_stat_card(stats_frame, "low_stock", "Low Stock Items", "0", 0, 2)
        self.create_stat_card(stats_frame, "out_of_stock", "Out of Stock", "0", 0, 3)
        
        # Row 2
        self.create_stat_card(stats_frame, "customers", "Total Customers", "0", 1, 0)
        self.create_stat_card(stats_frame, "suppliers", "Total Suppliers", "0", 1, 1)
        self.create_stat_card(stats_frame, "recent_movements", "Recent Movements", "0", 1, 2)
        self.create_stat_card(stats_frame, "categories", "Categories", "0", 1, 3)
    
    def create_stat_card(self, parent, key, title, value, row, col):
        """Create a statistics card."""
        card_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Configure column weights
        parent.grid_columnconfigure(col, weight=1)
        
        title_label = ttk.Label(
            card_frame,
            text=title,
            font=("Arial", 10),
            foreground="gray"
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=("Arial", 16, "bold")
        )
        value_label.pack(pady=(0, 10))
        
        # Store reference for updating
        self.stats_cards[key] = value_label
    
    def create_activity_section(self):
        """Create recent activity section."""
        activity_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Recent Activity",
            padding=15
        )
        activity_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Activity list
        columns = ("Time", "Action", "Item", "User")
        self.activity_tree = ttk.Treeview(
            activity_frame,
            columns=columns,
            show="headings",
            height=6
        )
        
        # Column headings
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=150)
        
        # Scrollbar for activity
        activity_scroll = ttk.Scrollbar(
            activity_frame,
            orient=tk.VERTICAL,
            command=self.activity_tree.yview
        )
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_actions_section(self):
        """Create quick actions section."""
        actions_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Quick Actions",
            padding=15
        )
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create action buttons in grid
        buttons = [
            ("Add Product", self.add_product, "add_stock"),
            ("Add Customer", self.add_customer, "add_customers"),
            ("Add Supplier", self.add_supplier, "add_suppliers"),
            ("Stock Report", self.stock_report, "view_reports"),
            ("Low Stock Alert", self.low_stock_alert, "view_stock"),
            ("Backup Database", self.backup_database, "backup_data"),
        ]
        
        for i, (text, command, permission) in enumerate(buttons):
            if user_manager.has_permission(permission):
                btn = ttk.Button(
                    actions_frame,
                    text=text,
                    command=command,
                    width=20
                )
                btn.grid(row=i//3, column=i%3, padx=10, pady=5, sticky="ew")
        
        # Configure column weights
        for i in range(3):
            actions_frame.grid_columnconfigure(i, weight=1)
    
    def create_alerts_section(self):
        """Create alerts and notifications section."""
        alerts_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Alerts & Notifications",
            padding=15
        )
        alerts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Alerts list
        self.alerts_listbox = tk.Listbox(
            alerts_frame,
            height=5,
            font=("Arial", 10)
        )
        self.alerts_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Alert scrollbar
        alert_scroll = ttk.Scrollbar(
            alerts_frame,
            orient=tk.VERTICAL,
            command=self.alerts_listbox.yview
        )
        self.alerts_listbox.configure(yscrollcommand=alert_scroll.set)
        alert_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_data(self):
        """Load dashboard data."""
        try:
            # Get dashboard summary
            summary = report_manager.get_dashboard_summary()
            
            # Update statistics cards
            if 'stock_summary' in summary:
                stock_data = summary['stock_summary']
                self.update_stat_card('total_products', str(stock_data.get('total_products', 0)))
                self.update_stat_card('total_value', format_currency(stock_data.get('total_value', 0)))
                self.update_stat_card('low_stock', str(stock_data.get('low_stock_count', 0)))
                self.update_stat_card('out_of_stock', str(stock_data.get('out_of_stock_count', 0)))
            
            self.update_stat_card('customers', str(summary.get('customer_count', 0)))
            self.update_stat_card('suppliers', str(summary.get('supplier_count', 0)))
            self.update_stat_card('recent_movements', str(summary.get('recent_movements', 0)))
            
            # Load categories count
            categories = stock_manager.get_categories()
            self.update_stat_card('categories', str(len(categories)))
            
            # Load recent activity
            self.load_recent_activity()
            
            # Load alerts
            self.load_alerts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard data: {str(e)}")
    
    def update_stat_card(self, key, value):
        """Update a statistics card value."""
        if key in self.stats_cards:
            self.stats_cards[key].config(text=value)
    
    def load_recent_activity(self):
        """Load recent stock movements."""
        try:
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            # Get recent movements
            movements = stock_manager.get_stock_movements(limit=10)
            
            for movement in movements:
                # Format time
                time_str = movement.get('created_at', '')[:16]  # YYYY-MM-DD HH:MM
                
                # Format action
                action = f"{movement.get('movement_type', '').title()} - {movement.get('quantity', 0)}"
                
                # Product name
                product = movement.get('product_name', 'Unknown')
                
                # User
                user = movement.get('username', 'System')
                
                self.activity_tree.insert('', 'end', values=(time_str, action, product, user))
                
        except Exception as e:
            print(f"Error loading recent activity: {e}")
    
    def load_alerts(self):
        """Load alerts and notifications."""
        try:
            # Clear existing alerts
            self.alerts_listbox.delete(0, tk.END)
            
            alerts = []
            
            # Low stock alerts
            low_stock_products = stock_manager.get_low_stock_products()
            if low_stock_products:
                alerts.append(f"⚠️ {len(low_stock_products)} products are low in stock")
            
            # Out of stock alerts
            out_of_stock = [p for p in low_stock_products if p['quantity'] == 0]
            if out_of_stock:
                alerts.append(f"🚨 {len(out_of_stock)} products are out of stock")
            
            # No alerts message
            if not alerts:
                alerts.append("✅ No alerts at this time")
            
            # Add alerts to listbox
            for alert in alerts:
                self.alerts_listbox.insert(tk.END, alert)
                
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self.alerts_listbox.insert(tk.END, "Error loading alerts")
    
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        self.load_data()
        messagebox.showinfo("Refresh", "Dashboard refreshed successfully!")
    
    # Quick action methods
    def add_product(self):
        """Navigate to add product."""
        messagebox.showinfo("Quick Action", "Navigate to Stock Management → Add Product")
    
    def add_customer(self):
        """Navigate to add customer."""
        messagebox.showinfo("Quick Action", "Navigate to Customer Management → Add Customer")
    
    def add_supplier(self):
        """Navigate to add supplier."""
        messagebox.showinfo("Quick Action", "Navigate to Supplier Management → Add Supplier")
    
    def stock_report(self):
        """Generate stock report."""
        try:
            report = report_manager.generate_stock_report()
            if report:
                messagebox.showinfo("Stock Report", "Stock report generated successfully!")
            else:
                messagebox.showerror("Error", "Failed to generate stock report")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {str(e)}")
    
    def low_stock_alert(self):
        """Show low stock alert."""
        try:
            low_stock_products = stock_manager.get_low_stock_products()
            
            if not low_stock_products:
                messagebox.showinfo("Low Stock Alert", "No products are currently low in stock.")
                return
            
            # Create alert window
            alert_window = tk.Toplevel(self.parent)
            alert_window.title("Low Stock Alert")
            alert_window.geometry("600x400")
            alert_window.transient(self.parent)
            
            # Alert content
            frame = ttk.Frame(alert_window, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                frame,
                text=f"⚠️ {len(low_stock_products)} Products Low in Stock",
                font=("Arial", 14, "bold")
            ).pack(pady=(0, 10))
            
            # Products list
            columns = ("Product", "Current Stock", "Min Level", "Shortage")
            tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for product in low_stock_products:
                shortage = product['min_stock_level'] - product['quantity']
                tree.insert('', 'end', values=(
                    product['name'],
                    product['quantity'],
                    product['min_stock_level'],
                    shortage
                ))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Close button
            ttk.Button(
                frame,
                text="Close",
                command=alert_window.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error showing low stock alert: {str(e)}")
    
    def backup_database(self):
        """Create database backup."""
        messagebox.showinfo("Quick Action", "Navigate to Backup Manager to create backup")


if __name__ == "__main__":
    # Test the dashboard window
    root = tk.Tk()
    root.title("Dashboard Test")
    root.geometry("1000x700")
    
    dashboard = DashboardWindow(root)
    root.mainloop()