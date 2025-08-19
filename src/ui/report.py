"""
Report generation UI for ToluStock.
Provides interface for generating and viewing reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.report_logic import report_manager
from logic.stock_logic import stock_manager
from logic.user import user_manager
from logic.utils import format_currency


class ReportWindow:
    """Report generation window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_report = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the report interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Reports & Analytics", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Content with paned window
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Report types
        self.create_report_types(paned)
        
        # Right side - Report content
        self.create_report_content(paned)
        
        paned.add(self.types_frame, weight=1)
        paned.add(self.content_frame, weight=3)
    
    def create_report_types(self, parent):
        """Create report types section."""
        self.types_frame = ttk.LabelFrame(parent, text="Report Types", padding=10)
        
        reports = [
            ("Stock Report", "Generate comprehensive stock report", self.generate_stock_report),
            ("Inventory Valuation", "Calculate total inventory value", self.generate_valuation_report),
            ("Low Stock Alert", "Show products with low stock", self.generate_low_stock_report),
            ("Stock Movement", "Show stock movement history", self.generate_movement_report),
            ("Category Analysis", "Analyze products by category", self.generate_category_report),
            ("Supplier Analysis", "Analyze suppliers and their products", self.generate_supplier_report),
        ]
        
        for i, (title, description, command) in enumerate(reports):
            frame = ttk.Frame(self.types_frame)
            frame.pack(fill=tk.X, pady=5)
            
            btn = ttk.Button(frame, text=title, command=command, width=20)
            btn.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=description, font=("Arial", 9), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))
    
    def create_report_content(self, parent):
        """Create report content section."""
        self.content_frame = ttk.LabelFrame(parent, text="Report Content", padding=10)
        
        # Report header
        self.header_frame = ttk.Frame(self.content_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.report_title_var = tk.StringVar(value="Select a report type to generate")
        ttk.Label(self.header_frame, textvariable=self.report_title_var, font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Export button
        self.export_button = ttk.Button(
            self.header_frame,
            text="Export",
            command=self.export_report,
            state="disabled"
        )
        self.export_button.pack(side=tk.RIGHT)
        
        # Report content area
        self.report_notebook = ttk.Notebook(self.content_frame)
        self.report_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Default message
        default_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(default_frame, text="Welcome")
        
        ttk.Label(
            default_frame,
            text="Welcome to ToluStock Reports\n\nSelect a report type from the left panel to generate reports.",
            font=("Arial", 12),
            justify=tk.CENTER
        ).pack(expand=True)
    
    def clear_report_content(self):
        """Clear current report content."""
        for tab_id in self.report_notebook.tabs():
            self.report_notebook.forget(tab_id)
        self.current_report = None
        self.export_button.config(state="disabled")
    
    def generate_stock_report(self):
        """Generate stock report."""
        try:
            self.report_title_var.set("Stock Report")
            self.clear_report_content()
            
            # Generate report
            report = report_manager.generate_stock_report()
            if not report:
                messagebox.showerror("Error", "Failed to generate stock report")
                return
            
            self.current_report = report
            
            # Summary tab
            summary_frame = ttk.Frame(self.report_notebook)
            self.report_notebook.add(summary_frame, text="Summary")
            
            summary = report.get('summary', {})
            summary_text = f"""
Stock Report Summary

Total Products: {summary.get('total_products', 0)}
Total Quantity: {summary.get('total_quantity', 0)}
Total Value: {format_currency(summary.get('total_value', 0))}
Low Stock Items: {summary.get('low_stock_count', 0)}
Out of Stock Items: {summary.get('out_of_stock_count', 0)}

Generated: {report.get('generated_at', '')}
By: {report.get('generated_by', '')}
            """
            
            text_widget = tk.Text(summary_frame, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, summary_text.strip())
            text_widget.config(state=tk.DISABLED)
            
            # Products tab
            if 'products' in report:
                self.create_products_tab(report['products'])
            
            self.export_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating stock report: {str(e)}")
    
    def generate_valuation_report(self):
        """Generate inventory valuation report."""
        try:
            self.report_title_var.set("Inventory Valuation Report")
            self.clear_report_content()
            
            report = report_manager.generate_inventory_valuation_report()
            if not report:
                messagebox.showerror("Error", "Failed to generate valuation report")
                return
            
            self.current_report = report
            
            # Summary tab
            summary_frame = ttk.Frame(self.report_notebook)
            self.report_notebook.add(summary_frame, text="Summary")
            
            total_value = report.get('total_value', 0)
            summary_text = f"""
Inventory Valuation Report

Total Inventory Value: {format_currency(total_value)}

Generated: {report.get('generated_at', '')}
By: {report.get('generated_by', '')}
            """
            
            text_widget = tk.Text(summary_frame, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, summary_text.strip())
            text_widget.config(state=tk.DISABLED)
            
            # Category breakdown tab
            if 'category_breakdown' in report:
                self.create_category_breakdown_tab(report['category_breakdown'])
            
            # Products tab
            if 'products' in report:
                self.create_products_tab(report['products'])
            
            self.export_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating valuation report: {str(e)}")
    
    def generate_low_stock_report(self):
        """Generate low stock alert report."""
        try:
            self.report_title_var.set("Low Stock Alert Report")
            self.clear_report_content()
            
            report = report_manager.generate_low_stock_alert_report()
            if not report:
                messagebox.showerror("Error", "Failed to generate low stock report")
                return
            
            self.current_report = report
            
            # Summary tab
            summary_frame = ttk.Frame(self.report_notebook)
            self.report_notebook.add(summary_frame, text="Summary")
            
            summary = report.get('summary', {})
            summary_text = f"""
Low Stock Alert Report

Total Alerts: {summary.get('total_alerts', 0)}
Critical (Out of Stock): {summary.get('critical_alerts', 0)}
Warning (Low Stock): {summary.get('warning_alerts', 0)}

Generated: {report.get('generated_at', '')}
By: {report.get('generated_by', '')}
            """
            
            text_widget = tk.Text(summary_frame, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, summary_text.strip())
            text_widget.config(state=tk.DISABLED)
            
            # Critical items tab
            if 'critical_items' in report and report['critical_items']:
                self.create_products_tab(report['critical_items'], "Critical Items")
            
            # Warning items tab
            if 'warning_items' in report and report['warning_items']:
                self.create_products_tab(report['warning_items'], "Warning Items")
            
            self.export_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating low stock report: {str(e)}")
    
    def generate_movement_report(self):
        """Generate stock movement report."""
        try:
            # Ask for period
            days = tk.simpledialog.askinteger("Period", "Enter number of days:", initialvalue=30, minvalue=1, maxvalue=365)
            if not days:
                return
            
            self.report_title_var.set(f"Stock Movement Report ({days} days)")
            self.clear_report_content()
            
            report = report_manager.generate_stock_movement_report(days=days)
            if not report:
                messagebox.showerror("Error", "Failed to generate movement report")
                return
            
            self.current_report = report
            
            # Summary tab
            summary_frame = ttk.Frame(self.report_notebook)
            self.report_notebook.add(summary_frame, text="Summary")
            
            summary = report.get('summary', {})
            summary_text = f"""
Stock Movement Report ({days} days)

Total Movements: {summary.get('total_movements', 0)}
Movements In: {summary.get('movements_in', 0)} (Qty: {summary.get('total_quantity_in', 0)})
Movements Out: {summary.get('movements_out', 0)} (Qty: {summary.get('total_quantity_out', 0)})
Net Movement: {summary.get('net_movement', 0)}

Period: {report.get('start_date', '')} to {report.get('end_date', '')}
Generated: {report.get('generated_at', '')}
By: {report.get('generated_by', '')}
            """
            
            text_widget = tk.Text(summary_frame, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, summary_text.strip())
            text_widget.config(state=tk.DISABLED)
            
            # Movements tab
            if 'movements' in report:
                self.create_movements_tab(report['movements'])
            
            self.export_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating movement report: {str(e)}")
    
    def generate_category_report(self):
        """Generate category analysis report."""
        try:
            self.report_title_var.set("Category Analysis Report")
            self.clear_report_content()
            
            report = report_manager.generate_category_analysis_report()
            if not report:
                messagebox.showerror("Error", "Failed to generate category report")
                return
            
            self.current_report = report
            
            # Categories tab
            categories_frame = ttk.Frame(self.report_notebook)
            self.report_notebook.add(categories_frame, text="Category Analysis")
            
            columns = ("Category", "Products", "Total Qty", "Total Value", "Avg Price")
            tree = ttk.Treeview(categories_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for category in report.get('categories', []):
                tree.insert('', 'end', values=(
                    category.get('category_name', ''),
                    category.get('product_count', 0),
                    category.get('total_quantity', 0),
                    format_currency(category.get('total_value', 0)),
                    format_currency(category.get('avg_price', 0))
                ))
            
            scrollbar = ttk.Scrollbar(categories_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.export_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating category report: {str(e)}")
    
    def generate_supplier_report(self):
        """Generate supplier analysis report."""
        try:
            self.report_title_var.set("Supplier Analysis Report")
            self.clear_report_content()
            
            report = report_manager.generate_supplier_analysis_report()
            if not report:
                messagebox.showerror("Error", "Failed to generate supplier report")
                return
            
            self.current_report = report
            
            # Suppliers tab
            suppliers_frame = ttk.Frame(self.report_notebook)
            self.report_notebook.add(suppliers_frame, text="Supplier Analysis")
            
            columns = ("Supplier", "Email", "Phone", "Products", "Total Value")
            tree = ttk.Treeview(suppliers_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for supplier in report.get('suppliers', []):
                tree.insert('', 'end', values=(
                    supplier.get('supplier_name', ''),
                    supplier.get('email', ''),
                    supplier.get('phone', ''),
                    supplier.get('product_count', 0),
                    format_currency(supplier.get('total_value', 0))
                ))
            
            scrollbar = ttk.Scrollbar(suppliers_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.export_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating supplier report: {str(e)}")
    
    def create_products_tab(self, products, tab_name="Products"):
        """Create products tab."""
        products_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(products_frame, text=tab_name)
        
        columns = ("Name", "SKU", "Category", "Quantity", "Price", "Value")
        tree = ttk.Treeview(products_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        for product in products:
            total_value = product.get('quantity', 0) * product.get('unit_price', 0)
            tree.insert('', 'end', values=(
                product.get('name', ''),
                product.get('sku', ''),
                product.get('category_name', ''),
                product.get('quantity', 0),
                format_currency(product.get('unit_price', 0)),
                format_currency(total_value)
            ))
        
        scrollbar = ttk.Scrollbar(products_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_category_breakdown_tab(self, breakdown):
        """Create category breakdown tab."""
        breakdown_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(breakdown_frame, text="Category Breakdown")
        
        columns = ("Category", "Products", "Total Qty", "Total Value")
        tree = ttk.Treeview(breakdown_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        for category, data in breakdown.items():
            tree.insert('', 'end', values=(
                category,
                data.get('products', 0),
                data.get('total_quantity', 0),
                format_currency(data.get('total_value', 0))
            ))
        
        scrollbar = ttk.Scrollbar(breakdown_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_movements_tab(self, movements):
        """Create movements tab."""
        movements_frame = ttk.Frame(self.report_notebook)
        self.report_notebook.add(movements_frame, text="Movements")
        
        columns = ("Date", "Product", "Type", "Quantity", "Reference", "User")
        tree = ttk.Treeview(movements_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        for movement in movements:
            tree.insert('', 'end', values=(
                movement.get('created_at', '')[:19],
                movement.get('product_name', ''),
                movement.get('movement_type', '').title(),
                movement.get('quantity', 0),
                movement.get('reference_id', ''),
                movement.get('username', 'System')
            ))
        
        scrollbar = ttk.Scrollbar(movements_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def export_report(self):
        """Export current report."""
        if not self.current_report:
            messagebox.showwarning("No Report", "No report to export.")
            return
        
        try:
            # Ask for file format
            file_format = messagebox.askyesno("Export Format", "Export as CSV? (No for JSON)")
            format_str = "csv" if file_format else "json"
            extension = "csv" if file_format else "json"
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                title="Export Report",
                defaultextension=f".{extension}",
                filetypes=[(f"{extension.upper()} files", f"*.{extension}"), ("All files", "*.*")]
            )
            
            if filename:
                if report_manager.export_report(self.current_report, filename, format_str):
                    messagebox.showinfo("Success", f"Report exported to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting report: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Reports Test")
    root.geometry("1000x700")
    
    report_window = ReportWindow(root)
    root.mainloop()