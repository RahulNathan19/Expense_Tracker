#!/usr/bin/env python3
"""
Expense Tracker - A simple and intuitive personal expense tracking application.

This is the main entry point for the Expense Tracker application.
Features include:
- Add and manage expenses
- Filter and search expenses
- View spending analytics and summaries
- Export data to CSV/Excel
- Configurable currency settings (supports USD, INR, EUR, etc.)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from expense_manager import ExpenseManager
from gui.add_expense import AddExpenseForm
from gui.expense_list import ExpenseList
from gui.filter_panel import FilterPanel
from gui.summary_panel import SummaryPanel
from gui.settings_dialog import SettingsDialog

try:
    # Try to import PIL for icon support (optional)
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ExpenseTrackerApp(tk.Tk):
    """Main application window for the Expense Tracker."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Initialize expense manager
        self.expense_manager = ExpenseManager()

        # Set up the main window
        self.setup_window()
        self.create_menu()
        self.create_widgets()
        self.setup_bindings()

        # Load initial data
        self.refresh_all_data()

        # Center window on screen
        self.center_window()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """Set up the main window properties."""
        self.title("Expense Tracker - Personal Finance Manager")

        # Set window size from settings
        width = self.expense_manager.settings.get('ui.window_width', 1000)
        height = self.expense_manager.settings.get('ui.window_height', 700)
        self.geometry(f"{width}x{height}")

        # Set minimum size
        self.minsize(800, 600)

        # Set window icon if PIL is available
        if PIL_AVAILABLE:
            try:
                # Create a simple icon (you can replace this with your own icon file)
                self.create_window_icon()
            except:
                pass

    def create_window_icon(self):
        """Create a simple window icon."""
        # Create a simple 32x32 icon
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))

        # Draw a simple rupee/dollar sign
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((8, 8), "₹", fill=(0, 100, 200, 255))

        icon = ImageTk.PhotoImage(img)
        self.iconphoto(True, icon)

    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to CSV...", command=lambda: self.export_data('csv'))
        file_menu.add_command(label="Export to Excel...", command=lambda: self.export_data('xlsx'))
        file_menu.add_separator()
        file_menu.add_command(label="Create Backup", command=self.create_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings...", command=self.open_settings)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All Filters", command=self.clear_all_filters)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all_data)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)

    def create_widgets(self):
        """Create all application widgets."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.create_expenses_tab()
        self.create_summary_tab()
        self.create_add_expense_tab()

        # Status bar
        self.create_status_bar()

    def create_expenses_tab(self):
        """Create the expenses tab with list and filters."""
        # Main container for expenses tab
        expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(expenses_frame, text="Expenses")

        # Create paned window for resizable layout
        paned = ttk.PanedWindow(expenses_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Filters
        filter_frame = ttk.Frame(paned)
        paned.add(filter_frame, weight=1)

        # Filter panel
        self.filter_panel = FilterPanel(filter_frame, self.expense_manager, self.on_filters_changed)

        # Right panel - Expense list
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=3)

        # Expense list
        self.expense_list = ExpenseList(list_frame, self.expense_manager)

    def create_summary_tab(self):
        """Create the summary/analytics tab."""
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Summary")

        # Summary panel
        self.summary_panel = SummaryPanel(summary_frame, self.expense_manager)

    def create_add_expense_tab(self):
        """Create the add expense tab."""
        add_frame = ttk.Frame(self.notebook)
        self.notebook.add(add_frame, text="Add Expense")

        # Add expense form
        self.add_expense_form = AddExpenseForm(add_frame, self.expense_manager, self.on_expense_added)

        # Center the form
        add_frame.columnconfigure(0, weight=1)
        add_frame.rowconfigure(0, weight=1)

    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.status_bar, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Database info
        self.db_info_var = tk.StringVar()
        self.db_info_label = ttk.Label(self.status_bar, textvariable=self.db_info_var)
        self.db_info_label.pack(side=tk.LEFT, padx=5)

        # Currency info
        self.currency_info_var = tk.StringVar()
        self.currency_info_label = ttk.Label(self.status_bar, textvariable=self.currency_info_var)
        self.currency_info_label.pack(side=tk.RIGHT, padx=5)

        # Update currency info
        self.update_currency_info()

    def setup_bindings(self):
        """Set up keyboard shortcuts and other bindings."""
        # Ctrl+N - Add new expense (switch to add tab)
        self.bind('<Control-n>', lambda e: self.notebook.select(2))

        # Ctrl+L - Focus on expense list
        self.bind('<Control-l>', lambda e: self.notebook.select(0))

        # Ctrl+S - Open settings
        self.bind('<Control-s>', lambda e: self.open_settings())

        # Ctrl+E - Export data
        self.bind('<Control-e>', lambda e: self.export_data('csv'))

        # F5 - Refresh
        self.bind('<F5>', lambda e: self.refresh_all_data())

        # Ctrl+Q - Quit
        self.bind('<Control-q>', lambda e: self.on_closing())

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def on_filters_changed(self, filters):
        """Handle filter changes."""
        self.expense_list.apply_filters(filters)
        self.update_status("Filters applied")

    def on_expense_added(self):
        """Handle expense addition."""
        # Refresh data in all tabs
        self.refresh_all_data()
        # Switch to expenses tab to see the new entry
        self.notebook.select(0)
        self.update_status("Expense added successfully")

    def refresh_all_data(self):
        """Refresh data in all components."""
        try:
            # Refresh expense list
            if hasattr(self, 'expense_list'):
                self.expense_list.refresh_list()

            # Refresh summary panel
            if hasattr(self, 'summary_panel'):
                self.summary_panel.refresh_summary()

            # Update database info
            self.update_database_info()

            self.update_status("Data refreshed")
        except Exception as e:
            self.update_status(f"Error refreshing data: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")

    def clear_all_filters(self):
        """Clear all active filters."""
        if hasattr(self, 'filter_panel'):
            self.filter_panel.clear_filters()
        self.update_status("Filters cleared")

    def export_data(self, format_type):
        """Export expense data."""
        try:
            # Get current filters
            filters = {}
            if hasattr(self, 'filter_panel'):
                filters = self.filter_panel.get_filters()

            success, message = self.expense_manager.export_expenses(
                export_format=format_type,
                filters=filters
            )

            if success:
                self.update_status(f"Exported to {format_type.upper()}: {message}")
                messagebox.showinfo("Export Successful", message)
            else:
                self.update_status(f"Export failed: {message}")
                messagebox.showerror("Export Failed", message)

        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Export Error", error_msg)

    def create_backup(self):
        """Create a database backup."""
        try:
            success, message = self.expense_manager.create_backup()
            if success:
                self.update_status(f"Backup created: {message}")
                messagebox.showinfo("Backup Successful", message)
            else:
                self.update_status(f"Backup failed: {message}")
                messagebox.showerror("Backup Failed", message)
        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Backup Error", error_msg)

    def open_settings(self):
        """Open the settings dialog."""
        try:
            dialog = SettingsDialog(self, self.expense_manager.settings, self.on_settings_changed)
            self.wait_window(dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {str(e)}")

    def on_settings_changed(self):
        """Handle settings changes."""
        try:
            # Update currency display in all components
            if hasattr(self, 'add_expense_form'):
                self.add_expense_form.set_currency_display()

            # Update currency info in status bar
            self.update_currency_info()

            # Refresh data to apply new formatting
            self.refresh_all_data()

            self.update_status("Settings applied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_var.set(message)

    def update_database_info(self):
        """Update database information in status bar."""
        try:
            summary = self.expense_manager.get_expense_summary()
            count = summary['count']
            self.db_info_var.set(f"Total expenses: {count}")
        except:
            self.db_info_var.set("Database info unavailable")

    def update_currency_info(self):
        """Update currency information in status bar."""
        try:
            symbol = self.expense_manager.settings.get('currency.symbol', '$')
            position = self.expense_manager.settings.get('currency.position', 'prefix')
            if position == 'prefix':
                display = f"Currency: {symbol}"
            else:
                display = f"Currency: {symbol} (suffix)"
            self.currency_info_var.set(display)
        except:
            self.currency_info_var.set("Currency: $")

    def show_about(self):
        """Show about dialog."""
        about_text = """Expense Tracker v1.0

A simple and intuitive personal expense tracking application.

Features:
• Track daily expenses with categories
• Filter and search functionality
• Spending analytics and summaries
• Export to CSV and Excel formats
• Configurable currency settings (USD, INR, EUR, etc.)
• Data backup and restore

Built with Python and Tkinter.
Database: SQLite
Export support: CSV, Excel (with openpyxl)

© 2024 - Personal Finance Manager"""

        messagebox.showinfo("About Expense Tracker", about_text)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
Ctrl+N      - Switch to Add Expense tab
Ctrl+E      - Export data to CSV
Ctrl+S      - Open Settings
Ctrl+Q      - Quit application

Navigation:
Ctrl+L      - Switch to Expenses list tab
F5          - Refresh all data

General:
Tab         - Navigate between fields/controls
Enter       - Submit forms or apply actions
Escape      - Cancel dialogs

In Expense List:
Double-click - View expense details
Right-click  - Show context menu"""

        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    def on_closing(self):
        """Handle application closing."""
        try:
            # Save window size to settings
            self.expense_manager.settings.set('ui.window_width', self.winfo_width())
            self.expense_manager.settings.set('ui.window_height', self.winfo_height())

            # Close database connection
            self.expense_manager.close()

            # Destroy the window
            self.destroy()
        except Exception as e:
            # If there's an error, still close the application
            print(f"Error during shutdown: {e}")
            self.destroy()


def main():
    """Main entry point for the application."""
    try:
        # Create and run the application
        app = ExpenseTrackerApp()
        app.mainloop()

    except Exception as e:
        # Handle startup errors
        error_msg = f"Failed to start Expense Tracker: {str(e)}"
        print(error_msg)

        # Try to show a message box if possible
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Startup Error", error_msg)
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()