"""
Customer management UI for ToluStock.
Provides interface for managing customer information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.customer_logic import customer_manager
from logic.user import user_manager


class CustomerWindow:
    """Customer management window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.selected_customer = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the customer management interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Customer Management", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        if user_manager.has_permission('add_customers'):
            ttk.Button(button_frame, text="Add Customer", command=self.add_customer).pack(side=tk.LEFT, padx=2)
        if user_manager.has_permission('edit_customers'):
            ttk.Button(button_frame, text="Edit Customer", command=self.edit_customer).pack(side=tk.LEFT, padx=2)
        if user_manager.has_permission('delete_customers'):
            ttk.Button(button_frame, text="Delete Customer", command=self.delete_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Customer list
        list_frame = ttk.LabelFrame(main_frame, text="Customers", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Name", "Email", "Phone", "Address")
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        self.customer_tree.bind('<Double-1>', self.on_customer_double_click)
    
    def load_data(self):
        """Load customer data."""
        self.refresh_customer_list()
    
    def refresh_customer_list(self):
        """Refresh customer list."""
        try:
            # Clear existing items
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            # Get search term
            search_term = self.search_var.get().strip()
            
            # Get customers
            customers = customer_manager.get_all_customers(search=search_term)
            
            # Add to tree
            for customer in customers:
                self.customer_tree.insert('', 'end', values=(
                    customer['name'],
                    customer['email'] or '',
                    customer['phone'] or '',
                    customer['address'] or ''
                ), tags=(customer['id'],))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def on_search_change(self, event=None):
        """Handle search change."""
        self.parent.after(500, self.refresh_customer_list)
    
    def clear_search(self):
        """Clear search."""
        self.search_var.set("")
        self.refresh_customer_list()
    
    def on_customer_select(self, event=None):
        """Handle customer selection."""
        selection = self.customer_tree.selection()
        if selection:
            item = self.customer_tree.item(selection[0])
            customer_id = item['tags'][0] if item['tags'] else None
            if customer_id:
                self.selected_customer = customer_manager.get_customer_by_id(customer_id)
    
    def on_customer_double_click(self, event=None):
        """Handle customer double-click."""
        if user_manager.has_permission('edit_customers'):
            self.edit_customer()
    
    def add_customer(self):
        """Add new customer."""
        CustomerDialog(self.parent, self.on_customer_saved)
    
    def edit_customer(self):
        """Edit selected customer."""
        if not self.selected_customer:
            messagebox.showwarning("No Selection", "Please select a customer to edit.")
            return
        CustomerDialog(self.parent, self.on_customer_saved, self.selected_customer)
    
    def delete_customer(self):
        """Delete selected customer."""
        if not self.selected_customer:
            messagebox.showwarning("No Selection", "Please select a customer to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete customer '{self.selected_customer['name']}'?"):
            try:
                if customer_manager.delete_customer(self.selected_customer['id']):
                    messagebox.showinfo("Success", "Customer deleted successfully.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "Failed to delete customer.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting customer: {str(e)}")
    
    def refresh_data(self):
        """Refresh data."""
        self.load_data()
    
    def on_customer_saved(self, customer_id):
        """Handle customer save."""
        self.refresh_customer_list()
    
    def new_customer(self):
        """Create new customer (called from main window)."""
        self.add_customer()


class CustomerDialog:
    """Dialog for adding/editing customers."""
    
    def __init__(self, parent, callback, customer=None):
        self.callback = callback
        self.customer = customer
        self.is_edit = customer is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Customer" if self.is_edit else "Add Customer")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        if self.is_edit:
            self.populate_fields()
    
    def setup_dialog(self):
        """Setup dialog."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="Name *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=30).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Phone
        ttk.Label(main_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.phone_var, width=30).grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # Address
        ttk.Label(main_frame, text="Address:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.address_text = tk.Text(main_frame, height=4, width=30)
        self.address_text.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def populate_fields(self):
        """Populate fields with customer data."""
        if not self.customer:
            return
        
        self.name_var.set(self.customer.get('name', ''))
        self.email_var.set(self.customer.get('email', ''))
        self.phone_var.set(self.customer.get('phone', ''))
        self.address_text.insert(1.0, self.customer.get('address', ''))
    
    def save_customer(self):
        """Save customer."""
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Validation Error", "Customer name is required.")
                return
            
            email = self.email_var.get().strip() or None
            phone = self.phone_var.get().strip() or None
            address = self.address_text.get(1.0, tk.END).strip() or None
            
            if self.is_edit:
                success = customer_manager.update_customer(
                    self.customer['id'],
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                
                if success:
                    messagebox.showinfo("Success", "Customer updated successfully.")
                    customer_id = self.customer['id']
                else:
                    messagebox.showerror("Error", "Failed to update customer.")
                    return
            else:
                customer_id = customer_manager.add_customer(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                
                if customer_id:
                    messagebox.showinfo("Success", "Customer added successfully.")
                else:
                    messagebox.showerror("Error", "Failed to add customer.")
                    return
            
            if self.callback:
                self.callback(customer_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving customer: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Customer Management Test")
    root.geometry("800x600")
    
    customer_window = CustomerWindow(root)
    root.mainloop()