import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional


class SettingsDialog(tk.Toplevel):
    """Settings dialog for configuring application preferences."""

    def __init__(self, parent, settings_manager, on_settings_changed: Optional[Callable] = None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.on_settings_changed = on_settings_changed

        self.title("Settings")
        self.geometry("500x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_current_settings()

        # Center the dialog
        self.center_window()

    def center_window(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"500x600+{x}+{y}")

    def create_widgets(self):
        """Create all settings widgets."""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_currency_tab()
        self.create_ui_tab()
        self.create_data_tab()
        self.create_export_tab()

        # Create button frame
        self.create_button_frame()

    def create_currency_tab(self):
        """Create currency settings tab."""
        currency_frame = ttk.Frame(self.notebook)
        self.notebook.add(currency_frame, text="Currency")

        # Currency symbol settings
        symbol_frame = ttk.LabelFrame(currency_frame, text="Currency Symbol", padding="10")
        symbol_frame.pack(fill=tk.X, padx=10, pady=10)

        # Predefined currency options
        ttk.Label(symbol_frame, text="Preset Currencies:").pack(anchor=tk.W, pady=(0, 5))

        currency_frame_row1 = ttk.Frame(symbol_frame)
        currency_frame_row1.pack(fill=tk.X, pady=2)

        currencies = [
            ("USD ($)", "$", "prefix", ".", ","),
            ("INR (₹)", "₹", "prefix", ".", ","),
            ("EUR (€)", "€", "suffix", ".", ","),
            ("GBP (£)", "£", "prefix", ".", ","),
            ("JPY (¥)", "¥", "prefix", ".", ","),
        ]

        for i, (name, symbol, position, decimal_sep, thousands_sep) in enumerate(currencies):
            row = currency_frame_row1 if i < 3 else ttk.Frame(symbol_frame)
            if i >= 3:
                row.pack(fill=tk.X, pady=2)

            btn = ttk.Button(row, text=name, command=lambda s=symbol, p=position, d=decimal_sep, t=thousands_sep: self.set_currency_preset(s, p, d, t))
            btn.pack(side=tk.LEFT, padx=(0, 10))

        # Separator
        ttk.Separator(symbol_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Custom currency settings
        ttk.Label(symbol_frame, text="Custom Settings:").pack(anchor=tk.W, pady=(0, 5))

        # Currency symbol
        symbol_row = ttk.Frame(symbol_frame)
        symbol_row.pack(fill=tk.X, pady=2)
        ttk.Label(symbol_row, text="Symbol:").pack(side=tk.LEFT, padx=(0, 10))
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(symbol_row, textvariable=self.symbol_var, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Symbol position
        ttk.Label(symbol_row, text="Position:").pack(side=tk.LEFT, padx=(0, 5))
        self.position_var = tk.StringVar()
        position_combo = ttk.Combobox(symbol_row, textvariable=self.position_var,
                                     values=["prefix", "suffix"], state="readonly", width=10)
        position_combo.pack(side=tk.LEFT)

        # Format settings
        format_frame = ttk.LabelFrame(currency_frame, text="Number Formatting", padding="10")
        format_frame.pack(fill=tk.X, padx=10, pady=10)

        # Decimal separator
        decimal_row = ttk.Frame(format_frame)
        decimal_row.pack(fill=tk.X, pady=2)
        ttk.Label(decimal_row, text="Decimal Separator:").pack(side=tk.LEFT, padx=(0, 10))
        self.decimal_var = tk.StringVar()
        decimal_combo = ttk.Combobox(decimal_row, textvariable=self.decimal_var,
                                    values=[".", ","], state="readonly", width=5)
        decimal_combo.pack(side=tk.LEFT)

        # Thousands separator
        thousands_row = ttk.Frame(format_frame)
        thousands_row.pack(fill=tk.X, pady=2)
        ttk.Label(thousands_row, text="Thousands Separator:").pack(side=tk.LEFT, padx=(0, 10))
        self.thousands_var = tk.StringVar()
        thousands_combo = ttk.Combobox(thousands_row, textvariable=self.thousands_var,
                                      values=[",", ".", " ", "None"], state="readonly", width=10)
        thousands_combo.pack(side=tk.LEFT)
        thousands_combo.bind('<<ComboboxSelected>>', self.on_thousands_changed)

        # Preview
        preview_frame = ttk.LabelFrame(currency_frame, text="Preview", padding="10")
        preview_frame.pack(fill=tk.X, padx=10, pady=10)

        self.preview_label = ttk.Label(preview_frame, text="1234.56", font=('Arial', 16, 'bold'))
        self.preview_label.pack()

    def create_ui_tab(self):
        """Create UI settings tab."""
        ui_frame = ttk.Frame(self.notebook)
        self.notebook.add(ui_frame, text="Interface")

        # Window settings
        window_frame = ttk.LabelFrame(ui_frame, text="Window", padding="10")
        window_frame.pack(fill=tk.X, padx=10, pady=10)

        # Window size
        size_row = ttk.Frame(window_frame)
        size_row.pack(fill=tk.X, pady=2)
        ttk.Label(size_row, text="Window Width:").pack(side=tk.LEFT, padx=(0, 10))
        self.width_var = tk.IntVar()
        width_spin = ttk.Spinbox(size_row, from_=800, to=1920, textvariable=self.width_var, width=10)
        width_spin.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(size_row, text="Window Height:").pack(side=tk.LEFT, padx=(0, 10))
        self.height_var = tk.IntVar()
        height_spin = ttk.Spinbox(size_row, from_=600, to=1080, textvariable=self.height_var, width=10)
        height_spin.pack(side=tk.LEFT)

        # Date format
        date_frame = ttk.LabelFrame(ui_frame, text="Date Format", padding="10")
        date_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(date_frame, text="Default Date Format:").pack(anchor=tk.W, pady=(0, 5))
        self.date_format_var = tk.StringVar()
        date_combo = ttk.Combobox(date_frame, textvariable=self.date_format_var,
                                 values=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"],
                                 state="readonly", width=15)
        date_combo.pack(anchor=tk.W)

        # Data display settings
        data_frame = ttk.LabelFrame(ui_frame, text="Data Display", padding="10")
        data_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(data_frame, text="Items per page:").pack(anchor=tk.W, pady=(0, 5))
        self.items_per_page_var = tk.IntVar()
        items_spin = ttk.Spinbox(data_frame, from_=10, to=200, textvariable=self.items_per_page_var, width=10)
        items_spin.pack(anchor=tk.W)

    def create_data_tab(self):
        """Create data settings tab."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data")

        # Backup settings
        backup_frame = ttk.LabelFrame(data_frame, text="Backup Settings", padding="10")
        backup_frame.pack(fill=tk.X, padx=10, pady=10)

        self.auto_backup_var = tk.BooleanVar()
        ttk.Checkbutton(backup_frame, text="Enable automatic backups",
                       variable=self.auto_backup_var).pack(anchor=tk.W, pady=(0, 10))

        freq_row = ttk.Frame(backup_frame)
        freq_row.pack(fill=tk.X, pady=2)
        ttk.Label(freq_row, text="Backup Frequency:").pack(side=tk.LEFT, padx=(0, 10))
        self.backup_freq_var = tk.StringVar()
        freq_combo = ttk.Combobox(freq_row, textvariable=self.backup_freq_var,
                                 values=["daily", "weekly", "monthly"], state="readonly")
        freq_combo.pack(side=tk.LEFT)

        # Database management
        db_frame = ttk.LabelFrame(data_frame, text="Database Management", padding="10")
        db_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(db_frame, text="Create Backup",
                  command=self.create_backup).pack(fill=tk.X, pady=2)
        ttk.Button(db_frame, text="Import Settings",
                  command=self.import_settings).pack(fill=tk.X, pady=2)
        ttk.Button(db_frame, text="Export Settings",
                  command=self.export_settings).pack(fill=tk.X, pady=2)

        # Reset button
        reset_frame = ttk.Frame(data_frame)
        reset_frame.pack(fill=tk.X, padx=10, pady=20)

        ttk.Button(reset_frame, text="Reset to Default Settings",
                  command=self.reset_to_defaults).pack(fill=tk.X)

    def create_export_tab(self):
        """Create export settings tab."""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="Export")

        # Export format
        format_frame = ttk.LabelFrame(export_frame, text="Default Format", padding="10")
        format_frame.pack(fill=tk.X, padx=10, pady=10)

        self.export_format_var = tk.StringVar()
        ttk.Radiobutton(format_frame, text="CSV (Comma Separated Values)",
                       variable=self.export_format_var, value="csv").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(format_frame, text="Excel (.xlsx)",
                       variable=self.export_format_var, value="xlsx").pack(anchor=tk.W, pady=2)

        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Export Options", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        self.include_headers_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Include column headers",
                       variable=self.include_headers_var).pack(anchor=tk.W, pady=2)

        # Export date format
        date_row = ttk.Frame(options_frame)
        date_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(date_row, text="Date Format in Exports:").pack(side=tk.LEFT, padx=(0, 10))
        self.export_date_format_var = tk.StringVar()
        export_date_combo = ttk.Combobox(date_row, textvariable=self.export_date_format_var,
                                        values=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"],
                                        state="readonly", width=15)
        export_date_combo.pack(side=tk.LEFT)

    def create_button_frame(self):
        """Create dialog button frame."""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def load_current_settings(self):
        """Load current settings into the dialog."""
        # Currency settings
        self.symbol_var.set(self.settings_manager.get('currency.symbol', '$'))
        self.position_var.set(self.settings_manager.get('currency.position', 'prefix'))
        self.decimal_var.set(self.settings_manager.get('currency.decimal_separator', '.'))
        thousands_sep = self.settings_manager.get('currency.thousands_separator', ',')
        self.thousands_var.set(thousands_sep if thousands_sep else "None")

        # UI settings
        self.width_var.set(self.settings_manager.get('ui.window_width', 1000))
        self.height_var.set(self.settings_manager.get('ui.window_height', 700))
        self.date_format_var.set(self.settings_manager.get('ui.default_date_format', '%Y-%m-%d'))

        # Data settings
        self.auto_backup_var.set(self.settings_manager.get('data.auto_backup', True))
        self.backup_freq_var.set(self.settings_manager.get('data.backup_frequency', 'daily'))
        self.items_per_page_var.set(self.settings_manager.get('data.items_per_page', 50))

        # Export settings
        self.export_format_var.set(self.settings_manager.get('export.default_format', 'csv'))
        self.include_headers_var.set(self.settings_manager.get('export.include_headers', True))
        self.export_date_format_var.set(self.settings_manager.get('export.date_format', '%Y-%m-%d'))

        # Update preview
        self.update_preview()

    def set_currency_preset(self, symbol: str, position: str, decimal_sep: str, thousands_sep: str):
        """Set currency preset values."""
        self.symbol_var.set(symbol)
        self.position_var.set(position)
        self.decimal_var.set(decimal_sep)
        self.thousands_var.set(thousands_sep if thousands_sep else "None")
        self.update_preview()

    def on_thousands_changed(self, event=None):
        """Handle thousands separator change."""
        if self.thousands_var.get() == "None":
            self.thousands_var.set("")
        self.update_preview()

    def update_preview(self):
        """Update the currency preview."""
        symbol = self.symbol_var.get()
        position = self.position_var.get()
        decimal_sep = self.decimal_var.get()
        thousands_sep = self.thousands_var.get() if self.thousands_var.get() != "None" else ""

        # Format sample number
        sample = "1234.56"
        if thousands_sep:
            # Add thousands separator to sample
            sample = sample.replace(",", thousands_sep)

        # Replace decimal separator
        sample = sample.replace(".", decimal_sep)

        # Add currency symbol
        if position == "prefix":
            formatted = f"{symbol} {sample}"
        else:
            formatted = f"{sample} {symbol}"

        self.preview_label.config(text=formatted)

    def apply_settings(self):
        """Apply the settings and close dialog."""
        try:
            # Validate settings
            if not self.validate_settings():
                return

            # Apply currency settings
            self.settings_manager.set('currency.symbol', self.symbol_var.get())
            self.settings_manager.set('currency.position', self.position_var.get())
            self.settings_manager.set('currency.decimal_separator', self.decimal_var.get())
            thousands_sep = self.thousands_var.get() if self.thousands_var.get() != "None" else ""
            self.settings_manager.set('currency.thousands_separator', thousands_sep)

            # Apply UI settings
            self.settings_manager.set('ui.window_width', self.width_var.get())
            self.settings_manager.set('ui.window_height', self.height_var.get())
            self.settings_manager.set('ui.default_date_format', self.date_format_var.get())

            # Apply data settings
            self.settings_manager.set('data.auto_backup', self.auto_backup_var.get())
            self.settings_manager.set('data.backup_frequency', self.backup_freq_var.get())
            self.settings_manager.set('data.items_per_page', self.items_per_page_var.get())

            # Apply export settings
            self.settings_manager.set('export.default_format', self.export_format_var.get())
            self.settings_manager.set('export.include_headers', self.include_headers_var.get())
            self.settings_manager.set('export.date_format', self.export_date_format_var.get())

            # Save settings
            if not self.settings_manager.save_settings():
                messagebox.showerror("Error", "Failed to save settings")
                return

            # Call callback if provided
            if self.on_settings_changed:
                self.on_settings_changed()

            messagebox.showinfo("Success", "Settings applied successfully")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    def validate_settings(self) -> bool:
        """Validate all settings."""
        try:
            # Validate window dimensions
            if not (800 <= self.width_var.get() <= 1920):
                messagebox.showerror("Invalid Setting", "Window width must be between 800 and 1920")
                return False

            if not (600 <= self.height_var.get() <= 1080):
                messagebox.showerror("Invalid Setting", "Window height must be between 600 and 1080")
                return False

            # Validate items per page
            if not (10 <= self.items_per_page_var.get() <= 200):
                messagebox.showerror("Invalid Setting", "Items per page must be between 10 and 200")
                return False

            # Validate currency symbol
            if not self.symbol_var.get().strip():
                messagebox.showerror("Invalid Setting", "Currency symbol cannot be empty")
                return False

            return True

        except Exception as e:
            messagebox.showerror("Validation Error", f"Invalid setting: {str(e)}")
            return False

    def create_backup(self):
        """Create a backup of the database."""
        try:
            from .. import expense_manager  # Import here to avoid circular imports
            # This would need to be implemented in the main application
            messagebox.showinfo("Info", "Backup functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")

    def import_settings(self):
        """Import settings from file."""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.settings_manager.import_settings(filename):
                messagebox.showinfo("Success", "Settings imported successfully")
                self.load_current_settings()
            else:
                messagebox.showerror("Error", "Failed to import settings")

    def export_settings(self):
        """Export settings to file."""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.settings_manager.export_settings(filename):
                messagebox.showinfo("Success", "Settings exported successfully")
            else:
                messagebox.showerror("Error", "Failed to export settings")

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Confirm Reset",
                              "Are you sure you want to reset all settings to their default values?"):
            self.settings_manager.reset_to_defaults()
            self.load_current_settings()
            messagebox.showinfo("Success", "Settings reset to defaults")