import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Callable, Optional, Dict, Any


class AddExpenseForm(ttk.Frame):
    """Form for adding new expenses."""

    def __init__(self, parent, expense_manager, on_expense_added: Optional[Callable] = None):
        """Initialize the add expense form."""
        super().__init__(parent)
        self.expense_manager = expense_manager
        self.on_expense_added = on_expense_added

        self.create_widgets()
        self.load_categories()
        self.set_default_values()

    def create_widgets(self):
        """Create all form widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)

        # Title
        title_label = ttk.Label(main_frame, text="Add New Expense", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Date field
        ttk.Label(main_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(main_frame, textvariable=self.date_var)
        self.date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Date format hint
        date_format = self.expense_manager.settings.get('ui.default_date_format', '%Y-%m-%d')
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=('Arial', 9, 'italic')).grid(
            row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5
        )

        # Category field
        ttk.Label(main_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Amount field with currency symbol
        ttk.Label(main_frame, text="Amount:").grid(row=3, column=0, sticky=tk.W, pady=5)

        # Currency frame for amount
        amount_frame = ttk.Frame(main_frame)
        amount_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Currency symbol label
        self.currency_label = ttk.Label(amount_frame, text=self.get_currency_symbol())
        self.currency_label.pack(side=tk.LEFT)

        # Amount entry
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var)
        self.amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Description field
        ttk.Label(main_frame, text="Description:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        self.description_var = tk.StringVar()
        self.description_text = tk.Text(main_frame, height=3, width=40, wrap=tk.WORD)
        self.description_text.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Character counter
        self.char_count_label = ttk.Label(main_frame, text="0/200", font=('Arial', 8))
        self.char_count_label.grid(row=5, column=1, sticky=tk.E, pady=(0, 5))

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=20)

        # Add button
        self.add_button = ttk.Button(buttons_frame, text="Add Expense", command=self.add_expense)
        self.add_button.pack(side=tk.LEFT, padx=(0, 10))

        # Clear button
        self.clear_button = ttk.Button(buttons_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT)

        # Bind events
        self.description_text.bind('<KeyRelease>', self.update_char_count)
        self.amount_entry.bind('<Return>', lambda e: self.add_expense())
        self.category_combo.bind('<Return>', lambda e: self.amount_entry.focus_set())
        self.date_entry.bind('<Return>', lambda e: self.category_combo.focus_set())

        # Set focus to date field
        self.date_entry.focus_set()

    def get_currency_symbol(self) -> str:
        """Get the current currency symbol."""
        symbol = self.expense_manager.settings.get('currency.symbol', '$')
        position = self.expense_manager.settings.get('currency.position', 'prefix')

        if position == 'prefix':
            return symbol + " "
        else:
            return ""

    def load_categories(self):
        """Load expense categories from the database."""
        try:
            categories = self.expense_manager.get_categories()
            category_names = [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
            if category_names:
                self.category_combo.set(category_names[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")
            # Fallback to default categories
            default_categories = [
                "Food & Dining", "Transportation", "Utilities",
                "Entertainment", "Healthcare", "Shopping", "Education", "Other"
            ]
            self.category_combo['values'] = default_categories
            if default_categories:
                self.category_combo.set("Other")

    def set_default_values(self):
        """Set default values for the form."""
        # Set today's date
        today_str = self.expense_manager.get_current_date_formatted()
        self.date_var.set(today_str)

        # Set default character count
        self.update_char_count()

    def update_char_count(self, event=None):
        """Update the character count for description."""
        text = self.description_text.get(1.0, tk.END).strip()
        count = len(text)
        self.char_count_label.config(text=f"{count}/200")

        # Change color if approaching limit
        if count > 180:
            self.char_count_label.config(foreground="red")
        elif count > 150:
            self.char_count_label.config(foreground="orange")
        else:
            self.char_count_label.config(foreground="black")

    def validate_form(self) -> Optional[str]:
        """Validate form inputs."""
        # Check date
        date_str = self.date_var.get().strip()
        if not date_str:
            return "Date is required"

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if parsed_date > date.today():
                return "Date cannot be in the future"
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD"

        # Check category
        if not self.category_var.get().strip():
            return "Category is required"

        # Check amount
        amount_str = self.amount_var.get().strip()
        if not amount_str:
            return "Amount is required"

        try:
            amount = float(amount_str.replace(',', ''))
            if amount <= 0:
                return "Amount must be positive"
            if amount > 999999999:
                return "Amount is too large"
        except ValueError:
            return "Invalid amount format"

        # Check description length
        description_text = self.description_text.get(1.0, tk.END).strip()
        if len(description_text) > 200:
            return "Description is too long (maximum 200 characters)"

        return None  # No errors

    def add_expense(self):
        """Add the expense to the database."""
        # Validate form
        error_message = self.validate_form()
        if error_message:
            messagebox.showerror("Validation Error", error_message)
            return

        # Get form data
        date_str = self.date_var.get().strip()
        category = self.category_var.get().strip()
        amount_str = self.amount_var.get().strip()
        description = self.description_text.get(1.0, tk.END).strip() or None

        # Add expense
        success, message = self.expense_manager.add_expense(date_str, category, amount_str, description)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            # Call callback if provided
            if self.on_expense_added:
                self.on_expense_added()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        """Clear all form fields."""
        self.date_var.set(self.expense_manager.get_current_date_formatted())
        self.category_combo.set(self.category_combo['values'][0] if self.category_combo['values'] else "")
        self.amount_var.set("")
        self.description_text.delete(1.0, tk.END)
        self.update_char_count()
        self.date_entry.focus_set()

    def set_currency_display(self):
        """Update currency display based on settings."""
        self.currency_label.config(text=self.get_currency_symbol())

    def get_form_data(self) -> Dict[str, Any]:
        """Get current form data as dictionary."""
        return {
            'date': self.date_var.get().strip(),
            'category': self.category_var.get().strip(),
            'amount': self.amount_var.get().strip(),
            'description': self.description_text.get(1.0, tk.END).strip() or None
        }

    def set_form_data(self, data: Dict[str, Any]):
        """Set form data from dictionary."""
        if 'date' in data:
            self.date_var.set(data['date'])
        if 'category' in data:
            self.category_var.set(data['category'])
        if 'amount' in data:
            self.amount_var.set(data['amount'])
        if 'description' in data:
            self.description_text.delete(1.0, tk.END)
            if data['description']:
                self.description_text.insert(1.0, data['description'])

        self.update_char_count()