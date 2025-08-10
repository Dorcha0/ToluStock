"""
Login UI for ToluStock.
Provides user authentication interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add src to path to import logic modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.user import user_manager


class LoginWindow:
    """Login window class."""
    
    def __init__(self, parent, on_success_callback=None):
        self.parent = parent
        self.on_success_callback = on_success_callback
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login interface."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Center the login form
        login_frame = ttk.Frame(main_frame)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Logo/Title
        title_label = ttk.Label(
            login_frame,
            text="ToluStock",
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle_label = ttk.Label(
            login_frame,
            text="Inventory Management System",
            font=("Arial", 12)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Username field
        ttk.Label(login_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            login_frame,
            textvariable=self.username_var,
            width=25,
            font=("Arial", 11)
        )
        self.username_entry.grid(row=2, column=1, padx=(10, 0), pady=5)
        
        # Password field
        ttk.Label(login_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            login_frame,
            textvariable=self.password_var,
            show="*",
            width=25,
            font=("Arial", 11)
        )
        self.password_entry.grid(row=3, column=1, padx=(10, 0), pady=5)
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(
            login_frame,
            text="Remember me",
            variable=self.remember_var
        )
        remember_check.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Login button
        self.login_button = ttk.Button(
            button_frame,
            text="Login",
            command=self.login,
            width=12
        )
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_form,
            width=12
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            login_frame,
            textvariable=self.status_var,
            foreground="red",
            font=("Arial", 10)
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Default credentials info
        info_frame = ttk.LabelFrame(login_frame, text="Default Login", padding=10)
        info_frame.grid(row=7, column=0, columnspan=2, pady=20, sticky=tk.EW)
        
        ttk.Label(
            info_frame,
            text="Username: admin",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        ttk.Label(
            info_frame,
            text="Password: admin123",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        # Version info
        version_label = ttk.Label(
            login_frame,
            text="Version 1.0.0",
            font=("Arial", 8),
            foreground="gray"
        )
        version_label.grid(row=8, column=0, columnspan=2, pady=(20, 0))
        
        # Setup key bindings
        self.setup_key_bindings()
        
        # Focus on username field
        self.username_entry.focus()
    
    def setup_key_bindings(self):
        """Setup keyboard shortcuts."""
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        self.parent.bind('<Escape>', lambda e: self.clear_form())
    
    def clear_form(self):
        """Clear the login form."""
        self.username_var.set("")
        self.password_var.set("")
        self.status_var.set("")
        self.username_entry.focus()
    
    def set_status(self, message, color="red"):
        """Set status message."""
        self.status_var.set(message)
        self.status_label.config(foreground=color)
    
    def login(self):
        """Attempt to login."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        # Validate input
        if not username:
            self.set_status("Please enter username")
            self.username_entry.focus()
            return
        
        if not password:
            self.set_status("Please enter password")
            self.password_entry.focus()
            return
        
        # Disable login button during authentication
        self.login_button.config(state="disabled")
        self.set_status("Authenticating...", "blue")
        
        # Update UI
        self.parent.update()
        
        try:
            # Attempt authentication
            user = user_manager.authenticate(username, password)
            
            if user:
                self.set_status("Login successful!", "green")
                
                # Remember user if checkbox is checked
                if self.remember_var.get():
                    # In a real application, you might save credentials securely
                    pass
                
                # Call success callback
                if self.on_success_callback:
                    self.parent.after(500, self.on_success_callback)  # Small delay to show success message
                
            else:
                self.set_status("Invalid username or password")
                self.password_var.set("")  # Clear password field
                self.password_entry.focus()
        
        except Exception as e:
            self.set_status(f"Login error: {str(e)}")
        
        finally:
            # Re-enable login button
            self.login_button.config(state="normal")
    
    def show_forgot_password(self):
        """Show forgot password dialog."""
        # This would typically send a password reset email or show security questions
        messagebox.showinfo(
            "Forgot Password",
            "Please contact your administrator to reset your password.\n\n"
            "Default admin credentials:\n"
            "Username: admin\n"
            "Password: admin123"
        )
    
    def show_registration(self):
        """Show user registration dialog."""
        # In a real application, this might allow self-registration
        # For now, show info about admin registration
        messagebox.showinfo(
            "User Registration",
            "New users must be created by an administrator.\n\n"
            "Please contact your system administrator to create an account."
        )


class LoginDialog:
    """Standalone login dialog for use in other windows."""
    
    def __init__(self, parent=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Login Required")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        if parent:
            self.dialog.geometry("+%d+%d" % (
                parent.winfo_rootx() + 50,
                parent.winfo_rooty() + 50
            ))
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the dialog interface."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="Authentication Required",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=30)
        self.username_entry.pack(pady=(5, 10), fill=tk.X)
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.pack(pady=(5, 20), fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Login",
            command=self.login
        ).pack(side=tk.RIGHT)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground="red"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Bindings
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        self.username_entry.focus()
    
    def login(self):
        """Attempt login."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.status_var.set("Please enter both username and password")
            return
        
        user = user_manager.authenticate(username, password)
        if user:
            self.result = user
            self.dialog.destroy()
        else:
            self.status_var.set("Invalid credentials")
            self.password_var.set("")
            self.password_entry.focus()
    
    def cancel(self):
        """Cancel login."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


if __name__ == "__main__":
    # Test the login window
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    login_window = LoginWindow(root)
    root.mainloop()