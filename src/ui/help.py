"""
Help and documentation UI for ToluStock.
Provides help content and user guidance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.settings_logic import settings_manager


class HelpWindow:
    """Help and documentation window class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.load_content()
    
    def setup_ui(self):
        """Setup the help interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Help & Documentation", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Content with paned window
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Table of contents
        self.create_toc(paned)
        
        # Right side - Content area
        self.create_content_area(paned)
        
        paned.add(self.toc_frame, weight=1)
        paned.add(self.content_frame, weight=3)
    
    def create_toc(self, parent):
        """Create table of contents."""
        self.toc_frame = ttk.LabelFrame(parent, text="Contents", padding=10)
        
        # Help topics
        topics = [
            ("Getting Started", self.show_getting_started),
            ("User Management", self.show_user_management),
            ("Stock Management", self.show_stock_management),
            ("Customer Management", self.show_customer_management),
            ("Supplier Management", self.show_supplier_management),
            ("Reports", self.show_reports),
            ("Backup & Restore", self.show_backup),
            ("Settings", self.show_settings),
            ("Keyboard Shortcuts", self.show_shortcuts),
            ("Troubleshooting", self.show_troubleshooting),
            ("About", self.show_about),
        ]
        
        for topic, command in topics:
            btn = ttk.Button(self.toc_frame, text=topic, command=command, width=20)
            btn.pack(fill=tk.X, pady=2)
    
    def create_content_area(self, parent):
        """Create content display area."""
        self.content_frame = ttk.LabelFrame(parent, text="Help Content", padding=10)
        
        # Content text widget with scrollbar
        text_frame = ttk.Frame(self.content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            state=tk.DISABLED,
            bg="white"
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_content(self):
        """Load initial content."""
        self.show_getting_started()
    
    def display_content(self, title, content):
        """Display content in the text widget."""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        
        # Add title
        self.content_text.insert(tk.END, f"{title}\n", "title")
        self.content_text.insert(tk.END, "=" * len(title) + "\n\n", "underline")
        
        # Add content
        self.content_text.insert(tk.END, content)
        
        # Configure tags
        self.content_text.tag_config("title", font=("Arial", 16, "bold"))
        self.content_text.tag_config("underline", font=("Arial", 12))
        self.content_text.tag_config("heading", font=("Arial", 12, "bold"))
        self.content_text.tag_config("code", font=("Courier", 10), background="#f0f0f0")
        
        self.content_text.config(state=tk.DISABLED)
        self.content_text.see(1.0)
    
    def show_getting_started(self):
        """Show getting started guide."""
        content = """Welcome to ToluStock - Your Inventory Management Solution!

Getting Started

1. First Login
   - Default username: admin
   - Default password: admin123
   - Change the default password after first login

2. Basic Setup
   - Go to Settings to configure your preferences
   - Set up your currency symbol and date format
   - Configure backup settings

3. Adding Your First Products
   - Navigate to Stock Management
   - Click "Add Product"
   - Fill in product details:
     * Name (required)
     * SKU (auto-generated if left blank)
     * Category
     * Unit price
     * Initial quantity
     * Minimum stock level

4. Managing Customers and Suppliers
   - Use Customer Management to add your customers
   - Use Supplier Management to add your suppliers
   - Link products to suppliers for better tracking

5. Generating Reports
   - Access Reports to view inventory analytics
   - Generate stock reports, low stock alerts
   - Export reports in CSV or JSON format

6. Regular Maintenance
   - Create regular backups from Backup Manager
   - Review low stock alerts on the dashboard
   - Monitor stock movements and trends

Tips:
- Use the search function to quickly find items
- Set minimum stock levels to get automatic alerts
- Regular backups help protect your data
- Check the dashboard for quick overview of your inventory
"""
        self.display_content("Getting Started", content)
    
    def show_user_management(self):
        """Show user management help."""
        content = """User Management (Admin Only)

User Roles:
- Admin: Full access to all features
- Manager: Can manage stock, customers, suppliers, reports
- User: Read-only access to most features

Adding Users:
1. Go to Users > User Management (admin only)
2. Click "Add User"
3. Enter username, password, email
4. Select appropriate role
5. Save the user

Changing Passwords:
- Users can change their own password from Account menu
- Admins can reset any user's password

Permissions:
- View Stock: See inventory items
- Add/Edit/Delete Stock: Manage inventory
- View/Add/Edit/Delete Customers: Manage customers
- View/Add/Edit/Delete Suppliers: Manage suppliers
- View Reports: Access reports and analytics
- Export Data: Export data to files
- Backup Data: Create and restore backups
- Manage Settings: Change application settings
- Manage Users: Add/edit/delete users (admin only)

Security Best Practices:
- Use strong passwords
- Change default admin password
- Regularly review user accounts
- Remove inactive users
- Use appropriate role assignments
"""
        self.display_content("User Management", content)
    
    def show_stock_management(self):
        """Show stock management help."""
        content = """Stock Management

Adding Products:
1. Click "Add Product" button
2. Fill required fields:
   - Name: Product name
   - Unit Price: Cost per unit
   - Quantity: Current stock level
3. Optional fields:
   - SKU: Stock keeping unit code
   - Category: Product category
   - Description: Product description
   - Minimum Stock Level: Alert threshold
   - Supplier: Product supplier

Editing Products:
- Double-click a product or select and click "Edit"
- Modify any field except historical data
- Click "Save" to confirm changes

Stock Adjustments:
- Select a product and click "Adjust Stock"
- Enter new quantity
- Provide reason for adjustment
- Add notes if needed

Search and Filtering:
- Use search box to find products by name, SKU, or description
- Filter by category using dropdown
- Filter by stock status (All, In Stock, Low Stock, Out of Stock)

Stock Status:
- In Stock: Quantity above minimum level
- Low Stock: Quantity at or below minimum level
- Out of Stock: Zero quantity

Categories:
- Organize products into categories
- Add new categories as needed
- Use categories for reporting and filtering

SKU (Stock Keeping Unit):
- Unique identifier for each product
- Auto-generated if not provided
- Format: CAT-PROD-TIMESTAMP
"""
        self.display_content("Stock Management", content)
    
    def show_customer_management(self):
        """Show customer management help."""
        content = """Customer Management

Adding Customers:
1. Click "Add Customer"
2. Enter customer details:
   - Name (required)
   - Email (optional, must be valid)
   - Phone (optional)
   - Address (optional)

Editing Customers:
- Double-click a customer or select and click "Edit"
- Update any information
- Email addresses must be unique

Searching Customers:
- Use search box to find customers
- Searches in name, email, and phone fields
- Results update as you type

Customer Information:
- Name: Customer's full name or business name
- Email: Contact email address
- Phone: Contact phone number
- Address: Customer's address

Data Validation:
- Names cannot be empty
- Email addresses are validated for proper format
- Phone numbers are validated for length and format
- Duplicate email addresses are not allowed

Export/Import:
- Export customer data to CSV or JSON
- Import customers from CSV files
- Batch operations for multiple customers

Best Practices:
- Keep customer information up to date
- Use consistent naming conventions
- Verify email addresses for accuracy
- Regular backup of customer data
"""
        self.display_content("Customer Management", content)
    
    def show_supplier_management(self):
        """Show supplier management help."""
        content = """Supplier Management

Adding Suppliers:
1. Click "Add Supplier"
2. Enter supplier details:
   - Name (required)
   - Email (optional)
   - Phone (optional)
   - Address (optional)

Linking Products:
- Assign suppliers to products in Stock Management
- View supplier's products in supplier details
- Track which supplier provides which products

Supplier Analysis:
- View supplier statistics in Reports
- See total value of products per supplier
- Analyze supplier performance

Managing Suppliers:
- Edit supplier information as needed
- Cannot delete suppliers with linked products
- Search by name, email, or phone

Supplier Information:
- Name: Supplier company or contact name
- Email: Business email address
- Phone: Business phone number
- Address: Supplier's business address

Best Practices:
- Maintain accurate supplier contacts
- Regularly review supplier relationships
- Keep supplier information current
- Use supplier data for procurement planning

Integration with Stock:
- Products can be linked to suppliers
- Supplier information appears in product details
- Useful for reordering and supplier analysis
"""
        self.display_content("Supplier Management", content)
    
    def show_reports(self):
        """Show reports help."""
        content = """Reports & Analytics

Available Reports:

1. Stock Report
   - Comprehensive inventory overview
   - Shows all products with current status
   - Can filter by category and stock level

2. Inventory Valuation
   - Total value of inventory
   - Breakdown by category
   - Most valuable products

3. Low Stock Alert
   - Products below minimum levels
   - Critical (out of stock) items
   - Warning (low stock) items

4. Stock Movement Report
   - History of stock changes
   - Specify time period (days)
   - In/out movement summary

5. Category Analysis
   - Performance by product category
   - Product count and values per category
   - Category comparison

6. Supplier Analysis
   - Supplier performance metrics
   - Products and values per supplier
   - Supplier comparison

Generating Reports:
1. Go to Reports section
2. Select report type from left panel
3. Configure any parameters (if required)
4. View results in tabs (Summary, Details, etc.)

Exporting Reports:
- Click "Export" button after generating report
- Choose CSV or JSON format
- Save to desired location

Report Data:
- All reports show real-time data
- Generated timestamp included
- User who generated report is recorded

Using Report Data:
- Identify trends and patterns
- Make informed inventory decisions
- Track performance over time
- Plan purchasing and stocking
"""
        self.display_content("Reports & Analytics", content)
    
    def show_backup(self):
        """Show backup and restore help."""
        content = """Backup & Restore

Creating Backups:

1. Database Backup
   - Creates complete database copy
   - Includes all data and structure
   - Can be restored to replace current database

2. Data Export
   - Creates JSON export of selected data
   - More portable format
   - Can be imported into other systems

Backup Types:
- Full Database Backup (.db file)
- Data Export (.json file)

Creating Backups:
1. Go to Backup Manager
2. Click "Create Backup" for database backup
3. Click "Create Export" for data export
4. Provide optional backup name
5. Backup is saved to backups folder

Restoring Data:

Database Restore:
- Select a .db backup file
- Click "Restore" (admin only)
- Current database backed up first
- Application restart required after restore

Data Import:
- Select a .json export file
- Click "Import" (admin only)
- Data is merged with existing data
- Duplicates are avoided

Backup Management:
- View all available backups
- Check backup file size and date
- Validate backup integrity
- Delete old backups

Automated Backups:
- Configure in Settings
- Set backup interval in days
- Automatic cleanup of old backups

Best Practices:
- Create regular backups
- Test backup restoration process
- Store backups in safe location
- Clean up old backups periodically
- Verify backup integrity regularly
"""
        self.display_content("Backup & Restore", content)
    
    def show_settings(self):
        """Show settings help."""
        content = """Application Settings

General Settings:
- Application Name: Display name for the application
- Currency Symbol: Symbol used for prices ($, €, ₺, etc.)
- Date Format: How dates are displayed
- Decimal Places: Precision for currency values
- Low Stock Alerts: Enable/disable automatic alerts

Interface Settings:
- Window Width/Height: Default window size
- Theme: Light or dark theme (future feature)
- Language: Interface language

Backup Settings:
- Auto Backup: Enable automatic backups
- Backup Interval: Days between automatic backups

Changing Settings:
1. Go to Settings from menu or toolbar
2. Navigate through tabs (General, Interface, Backup)
3. Modify desired settings
4. Click "Save" to apply changes

Resetting Settings:
- Click "Reset" to restore all defaults
- Confirmation required
- Cannot be undone

Import/Export Settings:
- Export: Save current settings to file
- Import: Load settings from file (admin only)
- Useful for sharing configurations

System Information:
- View application and system details
- Database statistics
- Platform information
- Python version and architecture

Settings Validation:
- Invalid values are rejected
- Warnings shown for potential issues
- Some settings require application restart

Tips:
- Test settings changes in safe environment
- Export settings before major changes
- Some settings affect all users
- Regular settings backup recommended
"""
        self.display_content("Application Settings", content)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts."""
        content = """Keyboard Shortcuts

Global Shortcuts:
Ctrl+N       - Add new product
Ctrl+F       - Open advanced search
Ctrl+Q       - Exit application
F1           - Dashboard
F2           - Stock Management
F3           - Customer Management
F4           - Supplier Management
F5           - Reports

Navigation:
Tab          - Move to next field
Shift+Tab    - Move to previous field
Enter        - Confirm/Select
Escape       - Cancel/Close dialog

List Navigation:
Up/Down      - Navigate items in lists
Page Up/Down - Scroll pages in lists
Home         - Go to first item
End          - Go to last item

Text Editing:
Ctrl+A       - Select all text
Ctrl+C       - Copy
Ctrl+V       - Paste
Ctrl+X       - Cut
Ctrl+Z       - Undo

Window Management:
Alt+F4       - Close window
F11          - Toggle fullscreen (future)

Search and Filtering:
Ctrl+F       - Focus search box
Enter        - Execute search
Escape       - Clear search

Dialog Shortcuts:
Enter        - OK/Save button
Escape       - Cancel button
Tab          - Move between controls

Tips:
- Most dialogs support Enter to save
- Escape key usually cancels operations
- Tab navigation works throughout the application
- Function keys provide quick access to main sections
"""
        self.display_content("Keyboard Shortcuts", content)
    
    def show_troubleshooting(self):
        """Show troubleshooting guide."""
        content = """Troubleshooting

Common Issues:

Login Problems:
- Check username and password
- Default: admin / admin123
- Passwords are case-sensitive
- Contact admin for password reset

Application Won't Start:
- Check Python installation (3.7+ required)
- Verify all dependencies are installed
- Check database file permissions
- Run from command line to see error messages

Database Errors:
- Check database file exists
- Verify file permissions
- Try database validation in Backup Manager
- Restore from recent backup if corrupted

Performance Issues:
- Large datasets may slow operations
- Consider archiving old data
- Increase system memory if possible
- Close other applications

Data Not Saving:
- Check user permissions
- Verify database is not read-only
- Ensure sufficient disk space
- Check for duplicate entries (SKU, email)

Reports Not Generating:
- Check user has report permissions
- Verify data exists for report parameters
- Try different report types
- Check system resources

Import/Export Problems:
- Verify file format (CSV, JSON)
- Check file permissions
- Ensure proper data structure
- Try smaller files for testing

Getting Help:
1. Check this help documentation
2. Verify settings configuration
3. Try creating fresh backup and restore
4. Contact system administrator
5. Check log files for errors

Error Messages:
- Note exact error message text
- Record steps that caused the error
- Check if error is reproducible
- Try restarting the application

Prevention:
- Regular backups prevent data loss
- Keep software updated
- Monitor disk space
- Regular maintenance tasks
"""
        self.display_content("Troubleshooting", content)
    
    def show_about(self):
        """Show about information."""
        app_name = settings_manager.get_setting('app_name', 'ToluStock')
        version = settings_manager.get_setting('version', '1.0.0')
        
        content = f"""{app_name} - Inventory Management System

Version: {version}
Developer: ToluStock Team
License: Apache License 2.0

About ToluStock:
ToluStock is a comprehensive inventory management solution designed to help
businesses of all sizes manage their stock efficiently. Built with Python
and tkinter, it provides a user-friendly interface for tracking inventory,
managing customers and suppliers, and generating insightful reports.

Key Features:
• Complete inventory tracking
• Customer and supplier management
• Comprehensive reporting system
• User management with role-based permissions
• Backup and restore functionality
• Data import/export capabilities
• Advanced search and filtering
• Low stock alerts and notifications

System Requirements:
• Python 3.7 or higher
• tkinter (usually included with Python)
• SQLite support
• 50MB free disk space minimum

Contact Information:
Email: support@tolustock.com
Website: https://tolustock.com
Documentation: https://docs.tolustock.com

Thank you for using ToluStock!

Copyright © 2024 ToluStock Team
All rights reserved.

This software is provided under the Apache License 2.0.
See the LICENSE file for complete license terms.
"""
        self.display_content("About ToluStock", content)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Help Test")
    root.geometry("900x700")
    
    help_window = HelpWindow(root)
    root.mainloop()