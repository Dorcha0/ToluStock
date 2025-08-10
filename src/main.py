"""
ToluStock - Inventory Management System
Main entry point for the application.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    # Import main window
    from ui.main_window import MainWindow
    
    def main():
        """Main application entry point."""
        try:
            # Create and run the main application window
            app = MainWindow()
            app.run()
            
        except KeyboardInterrupt:
            print("\nApplication interrupted by user.")
            sys.exit(0)
        except Exception as e:
            # Show error in message box if possible, otherwise print to console
            try:
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                messagebox.showerror(
                    "Application Error",
                    f"An error occurred while running ToluStock:\n\n{str(e)}\n\n"
                    f"Please check the console for more details."
                )
                root.destroy()
            except:
                print(f"Fatal error: {e}")
            
            sys.exit(1)
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required dependencies are installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Startup error: {e}")
    sys.exit(1)