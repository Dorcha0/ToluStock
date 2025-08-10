"""
Advanced search UI for ToluStock.
Provides comprehensive search functionality across all data.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.stock_logic import stock_manager
from logic.customer_logic import customer_manager
from logic.supplier_logic import supplier_manager
from logic.user import user_manager
from logic.utils import format_currency


class AdvancedSearchWindow:
    """Advanced search window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.search_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the advanced search interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Advanced Search", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Clear results button
        ttk.Button(header_frame, text="Clear Results", command=self.clear_results).pack(side=tk.RIGHT)
        
        # Search configuration
        self.create_search_config(main_frame)
        
        # Results area
        self.create_results_area(main_frame)
    
    def create_search_config(self, parent):
        """Create search configuration section."""
        config_frame = ttk.LabelFrame(parent, text="Search Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Search term
        term_frame = ttk.Frame(config_frame)
        term_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(term_frame, text="Search Term:").pack(side=tk.LEFT)
        self.search_term_var = tk.StringVar()
        self.search_entry = ttk.Entry(term_frame, textvariable=self.search_term_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', self.perform_search)
        
        ttk.Button(term_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT, padx=5)
        
        # Search options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        # Search in checkboxes
        ttk.Label(options_frame, text="Search in:").pack(side=tk.LEFT)
        
        self.search_products = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Products", variable=self.search_products).pack(side=tk.LEFT, padx=5)
        
        if user_manager.has_permission('view_customers'):
            self.search_customers = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Customers", variable=self.search_customers).pack(side=tk.LEFT, padx=5)
        else:
            self.search_customers = tk.BooleanVar(value=False)
        
        if user_manager.has_permission('view_suppliers'):
            self.search_suppliers = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Suppliers", variable=self.search_suppliers).pack(side=tk.LEFT, padx=5)
        else:
            self.search_suppliers = tk.BooleanVar(value=False)
        
        # Case sensitive option
        self.case_sensitive = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Case Sensitive", variable=self.case_sensitive).pack(side=tk.LEFT, padx=20)
        
        # Product-specific filters
        if user_manager.has_permission('view_stock'):
            self.create_product_filters(config_frame)
    
    def create_product_filters(self, parent):
        """Create product-specific filters."""
        filters_frame = ttk.LabelFrame(parent, text="Product Filters", padding=5)
        filters_frame.pack(fill=tk.X, pady=5)
        
        # Category filter
        cat_frame = ttk.Frame(filters_frame)
        cat_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(cat_frame, text="Category:").pack()
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, state="readonly", width=15)
        self.category_combo.pack()
        
        # Stock status filter
        status_frame = ttk.Frame(filters_frame)
        status_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(status_frame, text="Stock Status:").pack()
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["All", "In Stock", "Low Stock", "Out of Stock"],
            state="readonly",
            width=15
        )
        self.status_combo.pack()
        self.status_combo.set("All")
        
        # Price range
        price_frame = ttk.Frame(filters_frame)
        price_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(price_frame, text="Price Range:").pack()
        price_input_frame = ttk.Frame(price_frame)
        price_input_frame.pack()
        
        self.min_price_var = tk.StringVar()
        ttk.Entry(price_input_frame, textvariable=self.min_price_var, width=8).pack(side=tk.LEFT)
        ttk.Label(price_input_frame, text=" - ").pack(side=tk.LEFT)
        self.max_price_var = tk.StringVar()
        ttk.Entry(price_input_frame, textvariable=self.max_price_var, width=8).pack(side=tk.LEFT)
        
        # Load categories
        self.load_categories()
    
    def load_categories(self):
        """Load product categories."""
        try:
            categories = stock_manager.get_categories()
            category_names = ["All"] + [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            self.category_combo.set("All")
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def create_results_area(self, parent):
        """Create search results area."""
        results_frame = ttk.LabelFrame(parent, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results notebook for different types
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each search type
        self.create_products_tab()
        self.create_customers_tab()
        self.create_suppliers_tab()
        
        # Summary label
        self.summary_var = tk.StringVar(value="Enter search term and click Search")
        ttk.Label(results_frame, textvariable=self.summary_var, font=("Arial", 10)).pack(pady=5)
    
    def create_products_tab(self):
        """Create products results tab."""
        self.products_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.products_frame, text="Products")
        
        # Products tree
        columns = ("Name", "SKU", "Category", "Quantity", "Price", "Status")
        self.products_tree = ttk.Treeview(self.products_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)
        
        # Scrollbar
        products_scroll = ttk.Scrollbar(self.products_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scroll.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        products_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-click to view details
        self.products_tree.bind('<Double-1>', self.show_product_details)
    
    def create_customers_tab(self):
        """Create customers results tab."""
        self.customers_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.customers_frame, text="Customers")
        
        # Customers tree
        columns = ("Name", "Email", "Phone", "Address")
        self.customers_tree = ttk.Treeview(self.customers_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=150)
        
        # Scrollbar
        customers_scroll = ttk.Scrollbar(self.customers_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=customers_scroll.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        customers_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.customers_tree.bind('<Double-1>', self.show_customer_details)
    
    def create_suppliers_tab(self):
        """Create suppliers results tab."""
        self.suppliers_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.suppliers_frame, text="Suppliers")
        
        # Suppliers tree
        columns = ("Name", "Email", "Phone", "Address")
        self.suppliers_tree = ttk.Treeview(self.suppliers_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=150)
        
        # Scrollbar
        suppliers_scroll = ttk.Scrollbar(self.suppliers_frame, orient=tk.VERTICAL, command=self.suppliers_tree.yview)
        self.suppliers_tree.configure(yscrollcommand=suppliers_scroll.set)
        
        self.suppliers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suppliers_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.suppliers_tree.bind('<Double-1>', self.show_supplier_details)
    
    def perform_search(self, event=None):
        """Perform the search."""
        search_term = self.search_term_var.get().strip()
        
        if not search_term:
            messagebox.showwarning("Search Term Required", "Please enter a search term.")
            return
        
        try:
            self.clear_results()
            
            total_results = 0
            
            # Search products
            if self.search_products.get() and user_manager.has_permission('view_stock'):
                products = self.search_products_data(search_term)
                self.display_products_results(products)
                total_results += len(products)
            
            # Search customers
            if self.search_customers.get() and user_manager.has_permission('view_customers'):
                customers = self.search_customers_data(search_term)
                self.display_customers_results(customers)
                total_results += len(customers)
            
            # Search suppliers
            if self.search_suppliers.get() and user_manager.has_permission('view_suppliers'):
                suppliers = self.search_suppliers_data(search_term)
                self.display_suppliers_results(suppliers)
                total_results += len(suppliers)
            
            # Update summary
            self.summary_var.set(f"Found {total_results} results for '{search_term}'")
            
            if total_results == 0:
                messagebox.showinfo("No Results", "No items found matching your search criteria.")
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Error performing search: {str(e)}")
    
    def search_products_data(self, search_term):
        """Search in products."""
        try:
            # Apply filters
            category_filter = self.category_var.get()
            category_id = None
            
            if category_filter and category_filter != "All":
                categories = stock_manager.get_categories()
                for cat in categories:
                    if cat['name'] == category_filter:
                        category_id = cat['id']
                        break
            
            # Get products with basic filter
            products = stock_manager.get_all_products(search=search_term, category_id=category_id)
            
            # Apply additional filters
            filtered_products = []
            
            for product in products:
                # Stock status filter
                status_filter = self.status_var.get()
                if status_filter != "All":
                    quantity = product['quantity']
                    min_level = product['min_stock_level']
                    
                    if status_filter == "In Stock" and quantity <= min_level:
                        continue
                    elif status_filter == "Low Stock" and (quantity == 0 or quantity > min_level):
                        continue
                    elif status_filter == "Out of Stock" and quantity != 0:
                        continue
                
                # Price range filter
                min_price = self.min_price_var.get().strip()
                max_price = self.max_price_var.get().strip()
                
                if min_price:
                    try:
                        min_val = float(min_price)
                        if product['unit_price'] < min_val:
                            continue
                    except ValueError:
                        pass
                
                if max_price:
                    try:
                        max_val = float(max_price)
                        if product['unit_price'] > max_val:
                            continue
                    except ValueError:
                        pass
                
                filtered_products.append(product)
            
            return filtered_products
            
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def search_customers_data(self, search_term):
        """Search in customers."""
        try:
            search_fields = ['name', 'email', 'phone']
            if hasattr(self, 'case_sensitive') and not self.case_sensitive.get():
                # Use the customer manager's search function
                return customer_manager.search_customers(search_term, search_fields)
            else:
                # Get all and filter manually for case-sensitive search
                customers = customer_manager.get_all_customers()
                results = []
                
                for customer in customers:
                    for field in search_fields:
                        value = customer.get(field, '') or ''
                        if search_term in value:
                            results.append(customer)
                            break
                
                return results
                
        except Exception as e:
            print(f"Error searching customers: {e}")
            return []
    
    def search_suppliers_data(self, search_term):
        """Search in suppliers."""
        try:
            search_fields = ['name', 'email', 'phone']
            if hasattr(self, 'case_sensitive') and not self.case_sensitive.get():
                # Use the supplier manager's search function
                return supplier_manager.search_suppliers(search_term, search_fields)
            else:
                # Get all and filter manually for case-sensitive search
                suppliers = supplier_manager.get_all_suppliers()
                results = []
                
                for supplier in suppliers:
                    for field in search_fields:
                        value = supplier.get(field, '') or ''
                        if search_term in value:
                            results.append(supplier)
                            break
                
                return results
                
        except Exception as e:
            print(f"Error searching suppliers: {e}")
            return []
    
    def display_products_results(self, products):
        """Display products search results."""
        for product in products:
            # Calculate status
            if product['quantity'] == 0:
                status = "Out of Stock"
            elif product['quantity'] <= product['min_stock_level']:
                status = "Low Stock"
            else:
                status = "In Stock"
            
            self.products_tree.insert('', 'end', values=(
                product['name'],
                product['sku'] or '',
                product['category_name'] or '',
                product['quantity'],
                format_currency(product['unit_price']),
                status
            ), tags=(product['id'],))
    
    def display_customers_results(self, customers):
        """Display customers search results."""
        for customer in customers:
            self.customers_tree.insert('', 'end', values=(
                customer['name'],
                customer['email'] or '',
                customer['phone'] or '',
                customer['address'] or ''
            ), tags=(customer['id'],))
    
    def display_suppliers_results(self, suppliers):
        """Display suppliers search results."""
        for supplier in suppliers:
            self.suppliers_tree.insert('', 'end', values=(
                supplier['name'],
                supplier['email'] or '',
                supplier['phone'] or '',
                supplier['address'] or ''
            ), tags=(supplier['id'],))
    
    def clear_results(self):
        """Clear all search results."""
        # Clear trees
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        # Reset summary
        self.summary_var.set("Enter search term and click Search")
    
    def show_product_details(self, event=None):
        """Show product details."""
        selection = self.products_tree.selection()
        if selection:
            item = self.products_tree.item(selection[0])
            product_id = item['tags'][0] if item['tags'] else None
            if product_id:
                self.show_details_dialog("Product", stock_manager.get_product_by_id(product_id))
    
    def show_customer_details(self, event=None):
        """Show customer details."""
        selection = self.customers_tree.selection()
        if selection:
            item = self.customers_tree.item(selection[0])
            customer_id = item['tags'][0] if item['tags'] else None
            if customer_id:
                self.show_details_dialog("Customer", customer_manager.get_customer_by_id(customer_id))
    
    def show_supplier_details(self, event=None):
        """Show supplier details."""
        selection = self.suppliers_tree.selection()
        if selection:
            item = self.suppliers_tree.item(selection[0])
            supplier_id = item['tags'][0] if item['tags'] else None
            if supplier_id:
                self.show_details_dialog("Supplier", supplier_manager.get_supplier_by_id(supplier_id))
    
    def show_details_dialog(self, item_type, item_data):
        """Show item details in a dialog."""
        if not item_data:
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"{item_type} Details")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Content frame
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(content_frame, text=f"{item_type}: {item_data.get('name', 'Unknown')}", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Details text
        details_text = tk.Text(content_frame, wrap=tk.WORD, font=("Arial", 10), height=15)
        details_text.pack(fill=tk.BOTH, expand=True)
        
        # Format details
        details = ""
        for key, value in item_data.items():
            if key not in ['id']:  # Skip ID field
                formatted_key = key.replace('_', ' ').title()
                if value is not None:
                    if key == 'unit_price':
                        value = format_currency(value)
                    details += f"{formatted_key}: {value}\n"
        
        details_text.insert(1.0, details)
        details_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(content_frame, text="Close", command=dialog.destroy).pack(pady=10)
    
    def set_search_term(self, term):
        """Set search term (called from main window)."""
        self.search_term_var.set(term)
        self.perform_search()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Advanced Search Test")
    root.geometry("1000x700")
    
    search_window = AdvancedSearchWindow(root)
    root.mainloop()