import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
from typing import Callable, Optional, Dict, Any


class FilterPanel(ttk.LabelFrame):
    """Panel for filtering expenses."""

    def __init__(self, parent, expense_manager, on_filters_changed: Optional[Callable] = None):
        """Initialize the filter panel."""
        super().__init__(parent, text="Filters", padding="10")
        self.expense_manager = expense_manager
        self.on_filters_changed = on_filters_changed

        self.create_widgets()
        self.load_categories()

    def create_widgets(self):
        """Create all filter widgets."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid
        for i in range(6):
            main_frame.rowconfigure(i, weight=0)
        main_frame.columnconfigure(1, weight=1)

        # Date range filters
        self.create_date_filters(main_frame)

        # Category filter
        self.create_category_filter(main_frame)

        # Amount range filters
        self.create_amount_filters(main_frame)

        # Text search filter
        self.create_search_filter(main_frame)

        # Quick filter buttons
        self.create_quick_filters(main_frame)

        # Action buttons
        self.create_action_buttons(main_frame)

    def create_date_filters(self, parent):
        """Create date range filter widgets."""
        # Date from
        ttk.Label(parent, text="From Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_from_var = tk.StringVar()
        self.date_from_entry = ttk.Entry(parent, textvariable=self.date_from_var, width=15)
        self.date_from_entry.grid(row=0, column=1, sticky=tk.W, pady=2)

        # Calendar button for from date
        self.from_calendar_btn = ttk.Button(parent, text="📅", width=3,
                                          command=lambda: self.show_calendar('from'))
        self.from_calendar_btn.grid(row=0, column=2, padx=(5, 0), pady=2)

        # Date to
        ttk.Label(parent, text="To Date:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.date_to_var = tk.StringVar()
        self.date_to_entry = ttk.Entry(parent, textvariable=self.date_to_var, width=15)
        self.date_to_entry.grid(row=1, column=1, sticky=tk.W, pady=2)

        # Calendar button for to date
        self.to_calendar_btn = ttk.Button(parent, text="📅", width=3,
                                        command=lambda: self.show_calendar('to'))
        self.to_calendar_btn.grid(row=1, column=2, padx=(5, 0), pady=2)

    def create_category_filter(self, parent):
        """Create category filter widget."""
        ttk.Label(parent, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(parent, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        self.category_combo['values'] = ['All Categories']

        # All Categories option
        self.category_combo.set('All Categories')

    def create_amount_filters(self, parent):
        """Create amount range filter widgets."""
        # Minimum amount
        ttk.Label(parent, text="Min Amount:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.min_amount_var = tk.StringVar()
        self.min_amount_entry = ttk.Entry(parent, textvariable=self.min_amount_var, width=15)
        self.min_amount_entry.grid(row=3, column=1, sticky=tk.W, pady=2)

        # Maximum amount
        ttk.Label(parent, text="Max Amount:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.max_amount_var = tk.StringVar()
        self.max_amount_entry = ttk.Entry(parent, textvariable=self.max_amount_var, width=15)
        self.max_amount_entry.grid(row=4, column=1, sticky=tk.W, pady=2)

    def create_search_filter(self, parent):
        """Create text search filter widget."""
        ttk.Label(parent, text="Search:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(parent, textvariable=self.search_var)
        self.search_entry.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)

        # Bind Enter key to apply filters
        self.search_entry.bind('<Return>', lambda e: self.apply_filters())

    def create_quick_filters(self, parent):
        """Create quick filter buttons."""
        quick_frame = ttk.LabelFrame(parent, text="Quick Filters", padding="5")
        quick_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Quick filter buttons
        ttk.Button(quick_frame, text="Today",
                  command=self.filter_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="This Week",
                  command=self.filter_this_week).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="This Month",
                  command=self.filter_this_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="Last Month",
                  command=self.filter_last_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="This Year",
                  command=self.filter_this_year).pack(side=tk.LEFT, padx=2)

    def create_action_buttons(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(10, 0))

        ttk.Button(button_frame, text="Apply Filters",
                  command=self.apply_filters).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Filters",
                  command=self.clear_filters).pack(side=tk.LEFT)

    def load_categories(self):
        """Load categories from the database."""
        try:
            categories = self.expense_manager.get_categories()
            category_names = ['All Categories'] + [cat['name'] for cat in categories]
            self.category_combo['values'] = category_names
        except Exception:
            # Fallback to default categories
            default_categories = ['All Categories', 'Food & Dining', 'Transportation',
                                'Utilities', 'Entertainment', 'Healthcare', 'Shopping',
                                'Education', 'Other']
            self.category_combo['values'] = default_categories

    def show_calendar(self, date_type: str):
        """Show calendar popup for date selection."""
        # Create calendar popup
        popup = tk.Toplevel(self)
        popup.title("Select Date")
        popup.geometry("250x200")
        popup.resizable(False, False)

        # Center the popup
        popup.transient(self)
        popup.grab_set()

        # Calendar widget (simple implementation)
        today = date.today()
        selected_date = tk.StringVar(value=today.strftime("%Y-%m-%d"))

        # Year and month selection
        year_frame = ttk.Frame(popup)
        year_frame.pack(pady=5)

        # Year spinner
        ttk.Label(year_frame, text="Year:").pack(side=tk.LEFT, padx=(0, 5))
        year_var = tk.IntVar(value=today.year)
        year_spin = ttk.Spinbox(year_frame, from_=2000, to=2100, textvariable=year_var, width=8)
        year_spin.pack(side=tk.LEFT)

        # Month combo
        ttk.Label(year_frame, text="Month:").pack(side=tk.LEFT, padx=(10, 5))
        month_var = tk.IntVar(value=today.month)
        month_combo = ttk.Combobox(year_frame, textvariable=month_var,
                                  values=list(range(1, 13)), state="readonly", width=8)
        month_combo.pack(side=tk.LEFT)

        # Day selection (simplified calendar grid)
        day_frame = ttk.Frame(popup)
        day_frame.pack(pady=10)

        ttk.Label(day_frame, text="Day:").pack(side=tk.LEFT, padx=(0, 5))
        day_var = tk.IntVar(value=today.day)
        day_spin = ttk.Spinbox(day_frame, from_=1, to=31, textvariable=day_var, width=8)
        day_spin.pack(side=tk.LEFT)

        # Buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)

        def select_date():
            try:
                selected = date(year_var.get(), month_var.get(), day_var.get())
                selected_date.set(selected.strftime("%Y-%m-%d"))
                if date_type == 'from':
                    self.date_from_var.set(selected_date.get())
                else:
                    self.date_to_var.set(selected_date.get())
                popup.destroy()
            except ValueError:
                pass  # Invalid date, ignore

        ttk.Button(button_frame, text="Select", command=select_date).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=2)

    def get_filters(self) -> Dict[str, Any]:
        """Get current filter values."""
        filters = {}

        # Date filters
        if self.date_from_var.get().strip():
            filters['date_from'] = self.date_from_var.get().strip()
        if self.date_to_var.get().strip():
            filters['date_to'] = self.date_to_var.get().strip()

        # Category filter
        if self.category_var.get() != 'All Categories':
            filters['category'] = self.category_var.get()

        # Amount filters
        if self.min_amount_var.get().strip():
            try:
                filters['min_amount'] = float(self.min_amount_var.get())
            except ValueError:
                pass
        if self.max_amount_var.get().strip():
            try:
                filters['max_amount'] = float(self.max_amount_var.get())
            except ValueError:
                pass

        # Search filter
        if self.search_var.get().strip():
            filters['search'] = self.search_var.get().strip()

        return filters

    def set_filters(self, filters: Dict[str, Any]):
        """Set filter values."""
        # Date filters
        if 'date_from' in filters:
            self.date_from_var.set(filters['date_from'])
        if 'date_to' in filters:
            self.date_to_var.set(filters['date_to'])

        # Category filter
        if 'category' in filters:
            self.category_var.set(filters['category'])

        # Amount filters
        if 'min_amount' in filters:
            self.min_amount_var.set(str(filters['min_amount']))
        if 'max_amount' in filters:
            self.max_amount_var.set(str(filters['max_amount']))

        # Search filter
        if 'search' in filters:
            self.search_var.set(filters['search'])

    def apply_filters(self):
        """Apply filters and notify callback."""
        # Validate filters
        filters = self.get_filters()
        is_valid, error_message = self.expense_manager.validate_filters(filters)

        if not is_valid:
            tk.messagebox.showerror("Filter Error", error_message)
            return

        # Notify callback
        if self.on_filters_changed:
            self.on_filters_changed(filters)

    def clear_filters(self):
        """Clear all filters."""
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.category_var.set("All Categories")
        self.min_amount_var.set("")
        self.max_amount_var.set("")
        self.search_var.set("")

        # Apply cleared filters
        if self.on_filters_changed:
            self.on_filters_changed({})

    def has_active_filters(self) -> bool:
        """Check if any filters are active."""
        return bool(self.get_filters())

    # Quick filter methods
    def filter_today(self):
        """Filter expenses for today."""
        today = date.today()
        self.date_from_var.set(today.strftime("%Y-%m-%d"))
        self.date_to_var.set(today.strftime("%Y-%m-%d"))
        self.apply_filters()

    def filter_this_week(self):
        """Filter expenses for this week."""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        self.date_from_var.set(start_of_week.strftime("%Y-%m-%d"))
        self.date_to_var.set(today.strftime("%Y-%m-%d"))
        self.apply_filters()

    def filter_this_month(self):
        """Filter expenses for this month."""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        self.date_from_var.set(start_of_month.strftime("%Y-%m-%d"))
        self.date_to_var.set(today.strftime("%Y-%m-%d"))
        self.apply_filters()

    def filter_last_month(self):
        """Filter expenses for last month."""
        today = date.today()
        if today.month == 1:
            last_month = date(today.year - 1, 12, 1)
        else:
            last_month = date(today.year, today.month - 1, 1)

        # Calculate last day of last month
        if last_month.month == 12:
            next_month = date(last_month.year + 1, 1, 1)
        else:
            next_month = date(last_month.year, last_month.month + 1, 1)
        last_day = next_month - timedelta(days=1)

        self.date_from_var.set(last_month.strftime("%Y-%m-%d"))
        self.date_to_var.set(last_day.strftime("%Y-%m-%d"))
        self.apply_filters()

    def filter_this_year(self):
        """Filter expenses for this year."""
        today = date.today()
        start_of_year = date(today.year, 1, 1)
        self.date_from_var.set(start_of_year.strftime("%Y-%m-%d"))
        self.date_to_var.set(today.strftime("%Y-%m-%d"))
        self.apply_filters()