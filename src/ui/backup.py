"""
Backup management UI for ToluStock.
Provides interface for backup and restore operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.backup_logic import backup_manager
from logic.user import user_manager
from logic.utils import format_file_size


class BackupWindow:
    """Backup management window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the backup interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Backup & Restore", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Create Backup", command=self.create_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Create Export", command=self.create_export).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Restore", command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Import", command=self.import_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
        # Backup list
        list_frame = ttk.LabelFrame(main_frame, text="Available Backups", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Filename", "Type", "Size", "Date", "Created By")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.backup_tree.bind('<<TreeviewSelect>>', self.on_backup_select)
        self.backup_tree.bind('<Double-1>', self.on_backup_double_click)
        
        # Action buttons for selected backup
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="Validate", command=self.validate_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Delete", command=self.delete_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Cleanup Old", command=self.cleanup_old_backups).pack(side=tk.LEFT, padx=2)
    
    def load_data(self):
        """Load backup data."""
        self.refresh_backup_list()
    
    def refresh_backup_list(self):
        """Refresh backup list."""
        try:
            # Clear existing items
            for item in self.backup_tree.get_children():
                self.backup_tree.delete(item)
            
            # Get backups
            backups = backup_manager.get_backup_list()
            
            # Add to tree
            for backup in backups:
                metadata = backup.get('metadata', {})
                created_by = metadata.get('created_by', 'Unknown')
                
                self.backup_tree.insert('', 'end', values=(
                    backup['filename'],
                    backup['backup_type'].title(),
                    backup['file_size_formatted'],
                    backup['modified_time'][:19],
                    created_by
                ), tags=(backup['file_path'],))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load backups: {str(e)}")
    
    def on_backup_select(self, event=None):
        """Handle backup selection."""
        pass
    
    def on_backup_double_click(self, event=None):
        """Handle backup double-click."""
        self.validate_backup()
    
    def create_backup(self):
        """Create database backup."""
        try:
            # Ask for backup name
            backup_name = tk.simpledialog.askstring("Backup Name", "Enter backup name (optional):")
            
            backup_file = backup_manager.create_database_backup(backup_name)
            if backup_file:
                messagebox.showinfo("Success", f"Backup created: {os.path.basename(backup_file)}")
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to create backup")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creating backup: {str(e)}")
    
    def create_export(self):
        """Create data export."""
        try:
            # Ask for export name
            export_name = tk.simpledialog.askstring("Export Name", "Enter export name (optional):")
            
            export_file = backup_manager.create_data_export(export_name)
            if export_file:
                messagebox.showinfo("Success", f"Export created: {os.path.basename(export_file)}")
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to create export")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creating export: {str(e)}")
    
    def restore_backup(self):
        """Restore from backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to restore.")
            return
        
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can restore backups.")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_path = item['tags'][0] if item['tags'] else None
        
        if not backup_path:
            messagebox.showerror("Error", "Invalid backup selection.")
            return
        
        if messagebox.askyesno(
            "Confirm Restore",
            "This will replace the current database with the backup.\n"
            "Are you sure you want to continue?\n\n"
            "A backup of the current database will be created first."
        ):
            try:
                if backup_manager.restore_database_backup(backup_path):
                    messagebox.showinfo("Success", "Database restored successfully. Please restart the application.")
                else:
                    messagebox.showerror("Error", "Failed to restore database")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring backup: {str(e)}")
    
    def import_data(self):
        """Import data from file."""
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can import data.")
            return
        
        filename = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                result = backup_manager.import_data_export(filename, overwrite_existing=False)
                
                if result['success']:
                    message = f"Import completed:\n"
                    for table_info in result.get('imported_tables', []):
                        message += f"- {table_info['table']}: {table_info['imported']}/{table_info['total']}\n"
                    
                    if result.get('errors'):
                        message += f"\nErrors: {len(result['errors'])}"
                    
                    messagebox.showinfo("Import Result", message)
                else:
                    messagebox.showerror("Import Failed", result.get('message', 'Unknown error'))
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error importing data: {str(e)}")
    
    def validate_backup(self):
        """Validate selected backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to validate.")
            return
        
        item = self.backup_tree.item(selection[0])
        backup_path = item['tags'][0] if item['tags'] else None
        
        if backup_path:
            try:
                result = backup_manager.validate_backup_integrity(backup_path)
                
                if result['valid']:
                    message = f"Backup is valid.\n\nFile size: {format_file_size(result['file_size'])}"
                    if 'table_count' in result:
                        message += f"\nTables: {result['table_count']}"
                    elif 'tables' in result:
                        message += f"\nTables: {len(result['tables'])}"
                    
                    messagebox.showinfo("Validation Result", message)
                else:
                    messagebox.showerror("Validation Failed", f"Backup is invalid: {result['error']}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error validating backup: {str(e)}")
    
    def delete_backup(self):
        """Delete selected backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to delete.")
            return
        
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can delete backups.")
            return
        
        item = self.backup_tree.item(selection[0])
        filename = item['values'][0] if item['values'] else None
        
        if filename and messagebox.askyesno("Confirm Delete", f"Delete backup '{filename}'?"):
            try:
                if backup_manager.delete_backup(filename):
                    messagebox.showinfo("Success", "Backup deleted successfully.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Error", "Failed to delete backup")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting backup: {str(e)}")
    
    def cleanup_old_backups(self):
        """Cleanup old backups."""
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can cleanup backups.")
            return
        
        days = tk.simpledialog.askinteger("Cleanup Period", "Delete backups older than (days):", initialvalue=30, minvalue=1)
        if days:
            if messagebox.askyesno("Confirm Cleanup", f"Delete all backups older than {days} days?"):
                try:
                    deleted_count = backup_manager.cleanup_old_backups(days)
                    messagebox.showinfo("Cleanup Result", f"Deleted {deleted_count} old backups.")
                    self.refresh_data()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error during cleanup: {str(e)}")
    
    def refresh_data(self):
        """Refresh data."""
        self.load_data()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Backup Management Test")
    root.geometry("800x600")
    
    backup_window = BackupWindow(root)
    root.mainloop()