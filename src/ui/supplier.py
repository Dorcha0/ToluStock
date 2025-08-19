"""
Supplier management UI for ToluStock.
Provides interface for managing supplier information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.supplier_logic import supplier_manager
from logic.user import user_manager


class SupplierWindow:
    """Supplier management window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.selected_supplier = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the supplier management interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Supplier Management", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        if user_manager.has_permission('add_suppliers'):
            ttk.Button(button_frame, text="Add Supplier", command=self.add_supplier).pack(side=tk.LEFT, padx=2)
        if user_manager.has_permission('edit_suppliers'):
            ttk.Button(button_frame, text="Edit Supplier", command=self.edit_supplier).pack(side=tk.LEFT, padx=2)
        if user_manager.has_permission('delete_suppliers'):
            ttk.Button(button_frame, text="Delete Supplier", command=self.delete_supplier).pack(side=tk.LEFT, padx=2)
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
        
        # Content frame with paned window
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Supplier list
        list_frame = ttk.LabelFrame(paned, text="Suppliers", padding=10)
        
        columns = ("Name", "Email", "Phone", "Address")
        self.supplier_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.supplier_tree.heading(col, text=col)
            self.supplier_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.supplier_tree.yview)
        self.supplier_tree.configure(yscrollcommand=scrollbar.set)
        
        self.supplier_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.supplier_tree.bind('<<TreeviewSelect>>', self.on_supplier_select)
        self.supplier_tree.bind('<Double-1>', self.on_supplier_double_click)
        
        # Supplier details
        details_frame = ttk.LabelFrame(paned, text="Supplier Details", padding=10)
        
        # Details content
        self.details_vars = {}
        fields = [("Name", "name"), ("Email", "email"), ("Phone", "phone"), ("Address", "address")]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(details_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, pady=5
            )
            var = tk.StringVar()
            self.details_vars[key] = var
            ttk.Label(details_frame, textvariable=var, font=("Arial", 10)).grid(
                row=i, column=1, sticky=tk.W, pady=5
            )
        
        # Products from supplier
        ttk.Label(details_frame, text="Products:", font=("Arial", 10, "bold")).grid(
            row=len(fields), column=0, sticky=tk.NW, pady=10
        )
        
        self.products_listbox = tk.Listbox(details_frame, height=8, width=40)
        self.products_listbox.grid(row=len(fields), column=1, pady=10, sticky=tk.W)
        
        paned.add(list_frame, weight=2)
        paned.add(details_frame, weight=1)
    
    def load_data(self):
        """Load supplier data."""
        self.refresh_supplier_list()
    
    def refresh_supplier_list(self):
        """Refresh supplier list."""
        try:
            # Clear existing items
            for item in self.supplier_tree.get_children():
                self.supplier_tree.delete(item)
            
            # Get search term
            search_term = self.search_var.get().strip()
            
            # Get suppliers
            suppliers = supplier_manager.get_all_suppliers(search=search_term)
            
            # Add to tree
            for supplier in suppliers:
                self.supplier_tree.insert('', 'end', values=(
                    supplier['name'],
                    supplier['email'] or '',
                    supplier['phone'] or '',
                    supplier['address'] or ''
                ), tags=(supplier['id'],))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")
    
    def on_search_change(self, event=None):
        """Handle search change."""
        self.parent.after(500, self.refresh_supplier_list)
    
    def clear_search(self):
        """Clear search."""
        self.search_var.set("")
        self.refresh_supplier_list()
    
    def on_supplier_select(self, event=None):
        """Handle supplier selection."""
        selection = self.supplier_tree.selection()
        if selection:
            item = self.supplier_tree.item(selection[0])
            supplier_id = item['tags'][0] if item['tags'] else None
            if supplier_id:
                self.load_supplier_details(supplier_id)
        else:
            self.clear_supplier_details()
    
    def load_supplier_details(self, supplier_id):
        """Load supplier details."""
        try:
            supplier = supplier_manager.get_supplier_by_id(supplier_id)
            if supplier:
                self.selected_supplier = supplier
                
                # Update details
                for key, var in self.details_vars.items():
                    var.set(str(supplier.get(key, '')))
                
                # Load products
                products = supplier_manager.get_supplier_products(supplier_id)
                self.products_listbox.delete(0, tk.END)
                for product in products:
                    self.products_listbox.insert(tk.END, product['name'])
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load supplier details: {str(e)}")
    
    def clear_supplier_details(self):
        """Clear supplier details."""
        self.selected_supplier = None
        for var in self.details_vars.values():
            var.set('')
        self.products_listbox.delete(0, tk.END)
    
    def on_supplier_double_click(self, event=None):
        """Handle supplier double-click."""
        if user_manager.has_permission('edit_suppliers'):
            self.edit_supplier()
    
    def add_supplier(self):
        """Add new supplier."""
        SupplierDialog(self.parent, self.on_supplier_saved)
    
    def edit_supplier(self):
        """Edit selected supplier."""
        if not self.selected_supplier:
            messagebox.showwarning("No Selection", "Please select a supplier to edit.")
            return
        SupplierDialog(self.parent, self.on_supplier_saved, self.selected_supplier)
    
    def delete_supplier(self):
        """Delete selected supplier."""
        if not self.selected_supplier:
            messagebox.showwarning("No Selection", "Please select a supplier to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete supplier '{self.selected_supplier['name']}'?"):
            try:
                if supplier_manager.delete_supplier(self.selected_supplier['id']):
                    messagebox.showinfo("Success", "Supplier deleted successfully.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "Failed to delete supplier. May have associated products.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting supplier: {str(e)}")
    
    def refresh_data(self):
        """Refresh data."""
        self.load_data()
    
    def on_supplier_saved(self, supplier_id):
        """Handle supplier save."""
        self.refresh_supplier_list()
    
    def new_supplier(self):
        """Create new supplier (called from main window)."""
        self.add_supplier()


class SupplierDialog:
    """Dialog for adding/editing suppliers."""
    
    def __init__(self, parent, callback, supplier=None):
        self.callback = callback
        self.supplier = supplier
        self.is_edit = supplier is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Supplier" if self.is_edit else "Add Supplier")
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
        
        ttk.Button(button_frame, text="Save", command=self.save_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def populate_fields(self):
        """Populate fields with supplier data."""
        if not self.supplier:
            return
        
        self.name_var.set(self.supplier.get('name', ''))
        self.email_var.set(self.supplier.get('email', ''))
        self.phone_var.set(self.supplier.get('phone', ''))
        self.address_text.insert(1.0, self.supplier.get('address', ''))
    
    def save_supplier(self):
        """Save supplier."""
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Validation Error", "Supplier name is required.")
                return
            
            email = self.email_var.get().strip() or None
            phone = self.phone_var.get().strip() or None
            address = self.address_text.get(1.0, tk.END).strip() or None
            
            if self.is_edit:
                success = supplier_manager.update_supplier(
                    self.supplier['id'],
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                
                if success:
                    messagebox.showinfo("Success", "Supplier updated successfully.")
                    supplier_id = self.supplier['id']
                else:
                    messagebox.showerror("Error", "Failed to update supplier.")
                    return
            else:
                supplier_id = supplier_manager.add_supplier(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address
                )
                
                if supplier_id:
                    messagebox.showinfo("Success", "Supplier added successfully.")
                else:
                    messagebox.showerror("Error", "Failed to add supplier.")
                    return
            
            if self.callback:
                self.callback(supplier_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving supplier: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Supplier Management Test")
    root.geometry("900x700")
    
    supplier_window = SupplierWindow(root)
    root.mainloop()