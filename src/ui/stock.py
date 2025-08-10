"""
Stock management UI for ToluStock.
Provides interface for managing inventory items.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.stock_logic import stock_manager
from logic.supplier_logic import supplier_manager
from logic.user import user_manager
from logic.utils import format_currency, safe_cast_int, safe_cast_float


class StockWindow:
    """Stock management window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.selected_product = None
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the stock management interface."""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with title and actions
        self.create_header(main_frame)
        
        # Search and filter section
        self.create_search_section(main_frame)
        
        # Main content area with product list and details
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create paned window for list and details
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Product list
        self.create_product_list(paned)
        
        # Right side - Product details
        self.create_product_details(paned)
        
        paned.add(self.list_frame, weight=2)
        paned.add(self.details_frame, weight=1)
    
    def create_header(self, parent):
        """Create header section."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Stock Management",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        if user_manager.has_permission('add_stock'):
            ttk.Button(
                button_frame,
                text="Add Product",
                command=self.add_product
            ).pack(side=tk.LEFT, padx=2)
        
        if user_manager.has_permission('edit_stock'):
            ttk.Button(
                button_frame,
                text="Edit Product",
                command=self.edit_product
            ).pack(side=tk.LEFT, padx=2)
            
            ttk.Button(
                button_frame,
                text="Adjust Stock",
                command=self.adjust_stock
            ).pack(side=tk.LEFT, padx=2)
        
        if user_manager.has_permission('delete_stock'):
            ttk.Button(
                button_frame,
                text="Delete Product",
                command=self.delete_product
            ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_data
        ).pack(side=tk.LEFT, padx=2)
    
    def create_search_section(self, parent):
        """Create search and filter section."""
        search_frame = ttk.LabelFrame(parent, text="Search & Filter", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Search entry
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, sticky=tk.W)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Category filter
        ttk.Label(search_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            search_frame,
            textvariable=self.category_var,
            state="readonly",
            width=20
        )
        self.category_combo.grid(row=0, column=3, padx=5, sticky=tk.W)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Stock status filter
        ttk.Label(search_frame, text="Status:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_var,
            values=["All", "In Stock", "Low Stock", "Out of Stock"],
            state="readonly",
            width=15
        )
        self.status_combo.grid(row=0, column=5, padx=5, sticky=tk.W)
        self.status_combo.set("All")
        self.status_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Clear filters button
        ttk.Button(
            search_frame,
            text="Clear",
            command=self.clear_filters
        ).grid(row=0, column=6, padx=10)
    
    def create_product_list(self, parent):
        """Create product list section."""
        self.list_frame = ttk.LabelFrame(parent, text="Products", padding=10)
        
        # Treeview for products
        columns = ("Name", "SKU", "Category", "Quantity", "Price", "Total Value", "Status")
        self.product_tree = ttk.Treeview(
            self.list_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        # Column configurations
        column_widths = {"Name": 200, "SKU": 100, "Category": 120, "Quantity": 80, 
                        "Price": 80, "Total Value": 100, "Status": 100}
        
        for col in columns:
            self.product_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.product_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        h_scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.HORIZONTAL, command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.product_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        self.product_tree.bind('<Double-1>', self.on_product_double_click)
    
    def create_product_details(self, parent):
        """Create product details section."""
        self.details_frame = ttk.LabelFrame(parent, text="Product Details", padding=10)
        
        # Create scrollable frame for details
        details_canvas = tk.Canvas(self.details_frame)
        details_scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=details_canvas.yview)
        scrollable_details = ttk.Frame(details_canvas)
        
        scrollable_details.bind(
            "<Configure>",
            lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all"))
        )
        
        details_canvas.create_window((0, 0), window=scrollable_details, anchor="nw")
        details_canvas.configure(yscrollcommand=details_scrollbar.set)
        
        # Product info fields
        self.detail_vars = {}
        fields = [
            ("Name", "name"),
            ("SKU", "sku"),
            ("Category", "category_name"),
            ("Description", "description"),
            ("Unit Price", "unit_price"),
            ("Quantity", "quantity"),
            ("Min Stock Level", "min_stock_level"),
            ("Supplier", "supplier_name"),
            ("Created", "created_at"),
            ("Updated", "updated_at")
        ]
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(scrollable_details, text=f"{label}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, pady=5
            )
            
            var = tk.StringVar()
            self.detail_vars[key] = var
            
            if key == "description":
                # Text widget for description
                text_widget = tk.Text(scrollable_details, height=3, width=30, font=("Arial", 10))
                text_widget.grid(row=i, column=1, sticky=tk.W, pady=5)
                self.detail_vars[key] = text_widget
            else:
                ttk.Label(scrollable_details, textvariable=var, font=("Arial", 10)).grid(
                    row=i, column=1, sticky=tk.W, pady=5
                )
        
        # Action buttons for selected product
        action_frame = ttk.Frame(scrollable_details)
        action_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        if user_manager.has_permission('edit_stock'):
            ttk.Button(
                action_frame,
                text="Edit",
                command=self.edit_selected_product
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                action_frame,
                text="Adjust Stock",
                command=self.adjust_selected_stock
            ).pack(side=tk.LEFT, padx=5)
        
        if user_manager.has_permission('view_stock'):
            ttk.Button(
                action_frame,
                text="View History",
                command=self.view_stock_history
            ).pack(side=tk.LEFT, padx=5)
        
        details_canvas.pack(side="left", fill="both", expand=True)
        details_scrollbar.pack(side="right", fill="y")
    
    def load_data(self):
        """Load product data."""
        try:
            # Load categories for filter
            categories = stock_manager.get_categories()
            category_names = ["All"] + [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            self.category_combo.set("All")
            
            # Load products
            self.refresh_product_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def refresh_product_list(self):
        """Refresh the product list based on current filters."""
        try:
            # Clear existing items
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
            
            # Get filter values
            search_term = self.search_var.get().strip()
            category_filter = self.category_var.get()
            status_filter = self.status_var.get()
            
            # Get products with filters
            category_id = None
            if category_filter and category_filter != "All":
                categories = stock_manager.get_categories()
                for cat in categories:
                    if cat['name'] == category_filter:
                        category_id = cat['id']
                        break
            
            products = stock_manager.get_all_products(search=search_term, category_id=category_id)
            
            # Apply status filter
            if status_filter == "Low Stock":
                products = [p for p in products if p['quantity'] <= p['min_stock_level']]
            elif status_filter == "Out of Stock":
                products = [p for p in products if p['quantity'] == 0]
            elif status_filter == "In Stock":
                products = [p for p in products if p['quantity'] > p['min_stock_level']]
            
            # Add products to tree
            for product in products:
                # Calculate status
                if product['quantity'] == 0:
                    status = "Out of Stock"
                elif product['quantity'] <= product['min_stock_level']:
                    status = "Low Stock"
                else:
                    status = "In Stock"
                
                # Calculate total value
                total_value = product['quantity'] * product['unit_price']
                
                self.product_tree.insert('', 'end', values=(
                    product['name'],
                    product['sku'] or '',
                    product['category_name'] or '',
                    product['quantity'],
                    format_currency(product['unit_price']),
                    format_currency(total_value),
                    status
                ), tags=(product['id'],))
            
            # Update status
            self.update_summary()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh product list: {str(e)}")
    
    def update_summary(self):
        """Update summary information."""
        # This could show total products, total value, etc.
        pass
    
    def on_search_change(self, event=None):
        """Handle search text change."""
        # Refresh list after short delay to avoid too many updates
        self.parent.after(500, self.refresh_product_list)
    
    def on_filter_change(self, event=None):
        """Handle filter change."""
        self.refresh_product_list()
    
    def clear_filters(self):
        """Clear all filters."""
        self.search_var.set("")
        self.category_var.set("All")
        self.status_var.set("All")
        self.refresh_product_list()
    
    def on_product_select(self, event=None):
        """Handle product selection."""
        selection = self.product_tree.selection()
        if not selection:
            self.clear_product_details()
            return
        
        # Get selected product ID
        item = self.product_tree.item(selection[0])
        product_id = item['tags'][0] if item['tags'] else None
        
        if product_id:
            self.load_product_details(product_id)
    
    def on_product_double_click(self, event=None):
        """Handle product double-click."""
        if user_manager.has_permission('edit_stock'):
            self.edit_selected_product()
    
    def load_product_details(self, product_id):
        """Load details for selected product."""
        try:
            product = stock_manager.get_product_by_id(product_id)
            if not product:
                return
            
            self.selected_product = product
            
            # Update detail fields
            for key, var in self.detail_vars.items():
                value = product.get(key, '')
                
                if key == "description":
                    # Text widget
                    var.delete(1.0, tk.END)
                    var.insert(1.0, value or '')
                    var.config(state=tk.DISABLED)
                elif key in ["unit_price"]:
                    var.set(format_currency(value) if value else '')
                elif key in ["created_at", "updated_at"]:
                    # Format datetime
                    if value:
                        var.set(value[:19] if len(str(value)) > 19 else str(value))
                    else:
                        var.set('')
                else:
                    var.set(str(value) if value is not None else '')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load product details: {str(e)}")
    
    def clear_product_details(self):
        """Clear product details."""
        self.selected_product = None
        for key, var in self.detail_vars.items():
            if key == "description":
                var.delete(1.0, tk.END)
                var.config(state=tk.DISABLED)
            else:
                var.set('')
    
    def sort_by_column(self, col):
        """Sort products by column."""
        # This would implement column sorting
        pass
    
    def add_product(self):
        """Add new product."""
        ProductDialog(self.parent, self.on_product_saved)
    
    def edit_product(self):
        """Edit selected product."""
        self.edit_selected_product()
    
    def edit_selected_product(self):
        """Edit the currently selected product."""
        if not self.selected_product:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return
        
        ProductDialog(self.parent, self.on_product_saved, self.selected_product)
    
    def delete_product(self):
        """Delete selected product."""
        if not self.selected_product:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{self.selected_product['name']}'?\n\n"
            "This action cannot be undone."
        ):
            try:
                if stock_manager.delete_product(self.selected_product['id']):
                    messagebox.showinfo("Success", "Product deleted successfully.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "Failed to delete product.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting product: {str(e)}")
    
    def adjust_stock(self):
        """Adjust stock for selected product."""
        self.adjust_selected_stock()
    
    def adjust_selected_stock(self):
        """Adjust stock for the currently selected product."""
        if not self.selected_product:
            messagebox.showwarning("No Selection", "Please select a product to adjust stock.")
            return
        
        StockAdjustmentDialog(self.parent, self.selected_product, self.on_stock_adjusted)
    
    def view_stock_history(self):
        """View stock movement history for selected product."""
        if not self.selected_product:
            messagebox.showwarning("No Selection", "Please select a product to view history.")
            return
        
        StockHistoryDialog(self.parent, self.selected_product)
    
    def refresh_data(self):
        """Refresh all data."""
        self.load_data()
    
    def on_product_saved(self, product_id):
        """Handle product save."""
        self.refresh_product_list()
        if product_id:
            self.load_product_details(product_id)
    
    def on_stock_adjusted(self):
        """Handle stock adjustment."""
        self.refresh_product_list()
        if self.selected_product:
            self.load_product_details(self.selected_product['id'])


class ProductDialog:
    """Dialog for adding/editing products."""
    
    def __init__(self, parent, callback, product=None):
        self.callback = callback
        self.product = product
        self.is_edit = product is not None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Product" if self.is_edit else "Add Product")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        self.load_data()
        
        if self.is_edit:
            self.populate_fields()
    
    def setup_dialog(self):
        """Setup dialog interface."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        self.form_vars = {}
        
        # Name
        ttk.Label(main_frame, text="Name *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.form_vars['name'] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.form_vars['name'], width=40).grid(
            row=0, column=1, pady=5, sticky=tk.W
        )
        
        # SKU
        ttk.Label(main_frame, text="SKU:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.form_vars['sku'] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.form_vars['sku'], width=40).grid(
            row=1, column=1, pady=5, sticky=tk.W
        )
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.form_vars['category'] = tk.StringVar()
        self.category_combo = ttk.Combobox(
            main_frame, textvariable=self.form_vars['category'], width=37
        )
        self.category_combo.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(main_frame, height=4, width=40)
        self.description_text.grid(row=3, column=1, pady=5, sticky=tk.W)
        
        # Unit Price
        ttk.Label(main_frame, text="Unit Price *:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.form_vars['unit_price'] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.form_vars['unit_price'], width=40).grid(
            row=4, column=1, pady=5, sticky=tk.W
        )
        
        # Quantity
        ttk.Label(main_frame, text="Quantity *:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.form_vars['quantity'] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.form_vars['quantity'], width=40).grid(
            row=5, column=1, pady=5, sticky=tk.W
        )
        
        # Min Stock Level
        ttk.Label(main_frame, text="Min Stock Level:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.form_vars['min_stock_level'] = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.form_vars['min_stock_level'], width=40).grid(
            row=6, column=1, pady=5, sticky=tk.W
        )
        
        # Supplier
        ttk.Label(main_frame, text="Supplier:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.form_vars['supplier'] = tk.StringVar()
        self.supplier_combo = ttk.Combobox(
            main_frame, textvariable=self.form_vars['supplier'], width=37
        )
        self.supplier_combo.grid(row=7, column=1, pady=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self.save_product
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        """Load categories and suppliers."""
        try:
            # Load categories
            categories = stock_manager.get_categories()
            category_names = [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            
            # Load suppliers
            suppliers = supplier_manager.get_all_suppliers()
            supplier_names = [sup['name'] for sup in suppliers]
            self.supplier_combo['values'] = supplier_names
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def populate_fields(self):
        """Populate fields with existing product data."""
        if not self.product:
            return
        
        self.form_vars['name'].set(self.product.get('name', ''))
        self.form_vars['sku'].set(self.product.get('sku', ''))
        self.form_vars['category'].set(self.product.get('category_name', ''))
        
        description = self.product.get('description', '')
        self.description_text.insert(1.0, description)
        
        self.form_vars['unit_price'].set(str(self.product.get('unit_price', '')))
        self.form_vars['quantity'].set(str(self.product.get('quantity', '')))
        self.form_vars['min_stock_level'].set(str(self.product.get('min_stock_level', '')))
        self.form_vars['supplier'].set(self.product.get('supplier_name', ''))
    
    def save_product(self):
        """Save product."""
        try:
            # Validate required fields
            name = self.form_vars['name'].get().strip()
            if not name:
                messagebox.showerror("Validation Error", "Product name is required.")
                return
            
            unit_price = safe_cast_float(self.form_vars['unit_price'].get())
            if unit_price < 0:
                messagebox.showerror("Validation Error", "Unit price must be non-negative.")
                return
            
            quantity = safe_cast_int(self.form_vars['quantity'].get())
            if quantity < 0:
                messagebox.showerror("Validation Error", "Quantity must be non-negative.")
                return
            
            # Get category ID
            category_id = None
            category_name = self.form_vars['category'].get()
            if category_name:
                categories = stock_manager.get_categories()
                for cat in categories:
                    if cat['name'] == category_name:
                        category_id = cat['id']
                        break
            
            # Get supplier ID
            supplier_id = None
            supplier_name = self.form_vars['supplier'].get()
            if supplier_name:
                suppliers = supplier_manager.get_all_suppliers()
                for sup in suppliers:
                    if sup['name'] == supplier_name:
                        supplier_id = sup['id']
                        break
            
            # Get description
            description = self.description_text.get(1.0, tk.END).strip()
            
            # Save product
            if self.is_edit:
                success = stock_manager.update_product(
                    self.product['id'],
                    name=name,
                    category_id=category_id,
                    sku=self.form_vars['sku'].get() or None,
                    description=description or None,
                    unit_price=unit_price,
                    min_stock_level=safe_cast_int(self.form_vars['min_stock_level'].get()),
                    supplier_id=supplier_id
                )
                
                if success:
                    messagebox.showinfo("Success", "Product updated successfully.")
                    product_id = self.product['id']
                else:
                    messagebox.showerror("Error", "Failed to update product.")
                    return
            else:
                product_id = stock_manager.add_product(
                    name=name,
                    category_id=category_id,
                    description=description or None,
                    unit_price=unit_price,
                    quantity=quantity,
                    min_stock_level=safe_cast_int(self.form_vars['min_stock_level'].get()),
                    supplier_id=supplier_id,
                    sku=self.form_vars['sku'].get() or None
                )
                
                if product_id:
                    messagebox.showinfo("Success", "Product added successfully.")
                else:
                    messagebox.showerror("Error", "Failed to add product.")
                    return
            
            # Call callback and close dialog
            if self.callback:
                self.callback(product_id)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving product: {str(e)}")


class StockAdjustmentDialog:
    """Dialog for adjusting stock quantities."""
    
    def __init__(self, parent, product, callback):
        self.product = product
        self.callback = callback
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Adjust Stock - {product['name']}")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup dialog interface."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product info
        ttk.Label(
            main_frame,
            text=f"Product: {self.product['name']}",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))
        
        ttk.Label(
            main_frame,
            text=f"Current Stock: {self.product['quantity']}",
            font=("Arial", 11)
        ).pack(pady=(0, 20))
        
        # New quantity
        ttk.Label(main_frame, text="New Quantity:").pack(anchor=tk.W)
        self.new_quantity_var = tk.StringVar(value=str(self.product['quantity']))
        quantity_entry = ttk.Entry(main_frame, textvariable=self.new_quantity_var, width=20)
        quantity_entry.pack(pady=(5, 10), anchor=tk.W)
        quantity_entry.focus()
        quantity_entry.select_range(0, tk.END)
        
        # Reason
        ttk.Label(main_frame, text="Reason:").pack(anchor=tk.W)
        self.reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(
            main_frame,
            textvariable=self.reason_var,
            values=["Manual Adjustment", "Damaged Goods", "Lost Items", "Found Items", "Correction", "Other"],
            width=30
        )
        reason_combo.pack(pady=(5, 10), anchor=tk.W)
        reason_combo.set("Manual Adjustment")
        
        # Notes
        ttk.Label(main_frame, text="Notes:").pack(anchor=tk.W)
        self.notes_text = tk.Text(main_frame, height=4, width=40)
        self.notes_text.pack(pady=(5, 20), anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(
            button_frame,
            text="Adjust",
            command=self.adjust_stock
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def adjust_stock(self):
        """Perform stock adjustment."""
        try:
            new_quantity = safe_cast_int(self.new_quantity_var.get())
            if new_quantity < 0:
                messagebox.showerror("Error", "Quantity cannot be negative.")
                return
            
            reason = self.reason_var.get()
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            if stock_manager.adjust_stock(self.product['id'], new_quantity, f"{reason}: {notes}"):
                messagebox.showinfo("Success", "Stock adjusted successfully.")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to adjust stock.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error adjusting stock: {str(e)}")


class StockHistoryDialog:
    """Dialog for viewing stock movement history."""
    
    def __init__(self, parent, product):
        self.product = product
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Stock History - {product['name']}")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        
        self.setup_dialog()
        self.load_history()
    
    def setup_dialog(self):
        """Setup dialog interface."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            main_frame,
            text=f"Movement History: {self.product['name']}",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))
        
        # History tree
        columns = ("Date", "Type", "Quantity", "Reference", "Notes", "User")
        self.history_tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(pady=10)
    
    def load_history(self):
        """Load stock movement history."""
        try:
            movements = stock_manager.get_stock_movements(product_id=self.product['id'])
            
            for movement in movements:
                self.history_tree.insert('', 'end', values=(
                    movement.get('created_at', '')[:19],
                    movement.get('movement_type', '').title(),
                    movement.get('quantity', ''),
                    movement.get('reference_id', ''),
                    movement.get('notes', ''),
                    movement.get('username', 'System')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")


if __name__ == "__main__":
    # Test the stock window
    root = tk.Tk()
    root.title("Stock Management Test")
    root.geometry("1200x800")
    
    stock_window = StockWindow(root)
    root.mainloop()