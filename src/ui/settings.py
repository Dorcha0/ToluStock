"""
Settings UI for ToluStock.
Provides interface for managing application settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.settings_logic import settings_manager
from logic.user import user_manager


class SettingsWindow:
    """Settings management window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.settings_vars = {}
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Application Settings", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset", command=self.reset_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export", command=self.export_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Import", command=self.import_settings).pack(side=tk.LEFT, padx=2)
        
        # Notebook for different setting categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # General settings tab
        self.create_general_tab()
        
        # UI settings tab
        self.create_ui_tab()
        
        # Backup settings tab
        self.create_backup_tab()
        
        # System info tab
        self.create_system_tab()
    
    def create_general_tab(self):
        """Create general settings tab."""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Scrollable frame
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Application name
        self.create_setting_field(scrollable_frame, 0, "Application Name", "app_name", "string")
        
        # Currency symbol
        self.create_setting_field(scrollable_frame, 1, "Currency Symbol", "currency_symbol", "string")
        
        # Date format
        self.create_setting_field(scrollable_frame, 2, "Date Format", "date_format", "choice", 
                                ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"])
        
        # Decimal places
        self.create_setting_field(scrollable_frame, 3, "Decimal Places", "decimal_places", "integer")
        
        # Low stock alert
        self.create_setting_field(scrollable_frame, 4, "Low Stock Alerts", "low_stock_alert", "boolean")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_ui_tab(self):
        """Create UI settings tab."""
        ui_frame = ttk.Frame(self.notebook)
        self.notebook.add(ui_frame, text="Interface")
        
        # Scrollable frame
        canvas = tk.Canvas(ui_frame)
        scrollbar = ttk.Scrollbar(ui_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Window dimensions
        self.create_setting_field(scrollable_frame, 0, "Window Width", "window_width", "integer")
        self.create_setting_field(scrollable_frame, 1, "Window Height", "window_height", "integer")
        
        # Theme
        self.create_setting_field(scrollable_frame, 2, "Theme", "theme", "choice", ["light", "dark"])
        
        # Language
        self.create_setting_field(scrollable_frame, 3, "Language", "language", "choice", ["en", "tr"])
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_backup_tab(self):
        """Create backup settings tab."""
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="Backup")
        
        # Scrollable frame
        canvas = tk.Canvas(backup_frame)
        scrollbar = ttk.Scrollbar(backup_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Auto backup
        self.create_setting_field(scrollable_frame, 0, "Auto Backup", "auto_backup", "boolean")
        
        # Backup interval
        self.create_setting_field(scrollable_frame, 1, "Backup Interval (days)", "backup_interval_days", "integer")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_system_tab(self):
        """Create system information tab."""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="System Info")
        
        # System info text
        self.system_text = tk.Text(system_frame, wrap=tk.WORD, font=("Arial", 10), state=tk.DISABLED)
        self.system_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(system_frame, text="Refresh", command=self.load_system_info).pack(pady=5)
    
    def create_setting_field(self, parent, row, label, key, field_type, choices=None):
        """Create a setting field."""
        ttk.Label(parent, text=f"{label}:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, padx=10, pady=5
        )
        
        if field_type == "boolean":
            var = tk.BooleanVar()
            widget = ttk.Checkbutton(parent, variable=var)
        elif field_type == "choice" and choices:
            var = tk.StringVar()
            widget = ttk.Combobox(parent, textvariable=var, values=choices, state="readonly", width=20)
        elif field_type == "integer":
            var = tk.StringVar()
            widget = ttk.Entry(parent, textvariable=var, width=20)
        else:  # string
            var = tk.StringVar()
            widget = ttk.Entry(parent, textvariable=var, width=30)
        
        widget.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        self.settings_vars[key] = var
        
        # Add description if available
        definition = settings_manager.get_setting_definition(key)
        description = definition.get('description', '')
        if description:
            ttk.Label(parent, text=description, font=("Arial", 9), foreground="gray").grid(
                row=row, column=2, sticky=tk.W, padx=10, pady=5
            )
    
    def load_settings(self):
        """Load current settings."""
        try:
            app_settings = settings_manager.get_application_settings()
            
            for key, var in self.settings_vars.items():
                value = app_settings.get(key, '')
                
                if isinstance(var, tk.BooleanVar):
                    var.set(bool(value))
                else:
                    var.set(str(value))
            
            self.load_system_info()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")
    
    def load_system_info(self):
        """Load system information."""
        try:
            system_info = settings_manager.get_system_info()
            
            info_text = "System Information\n" + "="*50 + "\n\n"
            
            # Application info
            app_info = system_info.get('application', {})
            info_text += f"Application: {app_info.get('name', 'Unknown')}\n"
            info_text += f"Version: {app_info.get('version', 'Unknown')}\n"
            info_text += f"Database: {app_info.get('database_file', 'Unknown')}\n\n"
            
            # System info
            sys_info = system_info.get('system', {})
            info_text += f"Platform: {sys_info.get('platform', 'Unknown')}\n"
            info_text += f"Python: {sys_info.get('python_version', 'Unknown')}\n"
            info_text += f"Architecture: {sys_info.get('architecture', 'Unknown')}\n\n"
            
            # Database stats
            db_info = system_info.get('database', {})
            info_text += "Database Statistics:\n"
            info_text += f"  Products: {db_info.get('product_count', 0)}\n"
            info_text += f"  Customers: {db_info.get('customer_count', 0)}\n"
            info_text += f"  Suppliers: {db_info.get('supplier_count', 0)}\n"
            info_text += f"  Users: {db_info.get('user_count', 0)}\n"
            info_text += f"  Stock Movements: {db_info.get('movement_count', 0)}\n\n"
            
            info_text += f"Settings Count: {system_info.get('settings_count', 0)}\n"
            
            self.system_text.config(state=tk.NORMAL)
            self.system_text.delete(1.0, tk.END)
            self.system_text.insert(1.0, info_text)
            self.system_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error loading system info: {e}")
    
    def save_settings(self):
        """Save settings."""
        try:
            updates = {}
            
            for key, var in self.settings_vars.items():
                if isinstance(var, tk.BooleanVar):
                    updates[key] = var.get()
                else:
                    value = var.get().strip()
                    
                    # Validate based on type
                    definition = settings_manager.get_setting_definition(key)
                    field_type = definition.get('type', 'string')
                    
                    if field_type == 'integer':
                        try:
                            value = int(value)
                        except ValueError:
                            messagebox.showerror("Validation Error", f"Invalid integer value for {key}")
                            return
                    
                    updates[key] = value
            
            # Validate settings
            validation = settings_manager.validate_settings()
            if not validation['valid']:
                errors = '\n'.join(validation['errors'])
                messagebox.showerror("Validation Error", f"Settings validation failed:\n{errors}")
                return
            
            # Update settings
            results = settings_manager.update_settings(updates)
            
            success_count = sum(1 for success in results.values() if success)
            
            if success_count == len(updates):
                messagebox.showinfo("Success", "All settings saved successfully.")
            else:
                failed = [key for key, success in results.items() if not success]
                messagebox.showwarning("Partial Success", f"Some settings failed to save: {', '.join(failed)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Confirm Reset", "Reset all settings to default values?"):
            try:
                if settings_manager.reset_all_settings():
                    messagebox.showinfo("Success", "Settings reset to defaults.")
                    self.load_settings()
                else:
                    messagebox.showerror("Error", "Failed to reset settings.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error resetting settings: {str(e)}")
    
    def export_settings(self):
        """Export settings."""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Settings",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                export_file = settings_manager.export_settings(filename)
                if export_file:
                    messagebox.showinfo("Success", f"Settings exported to {export_file}")
                else:
                    messagebox.showerror("Error", "Failed to export settings")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting settings: {str(e)}")
    
    def import_settings(self):
        """Import settings."""
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can import settings.")
            return
        
        try:
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                result = settings_manager.import_settings(filename, overwrite_existing=True)
                
                if result['success']:
                    message = f"Import completed:\nImported: {result['imported']}/{result['total']}"
                    if result.get('errors'):
                        message += f"\nErrors: {len(result['errors'])}"
                    
                    messagebox.showinfo("Import Result", message)
                    self.load_settings()
                else:
                    messagebox.showerror("Import Failed", result.get('message', 'Unknown error'))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error importing settings: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Settings Test")
    root.geometry("700x600")
    
    settings_window = SettingsWindow(root)
    root.mainloop()