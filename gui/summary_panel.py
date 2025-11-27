import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional, Dict, Any, List


class SummaryPanel(ttk.Frame):
    """Panel for displaying expense summaries and analytics."""

    def __init__(self, parent, expense_manager):
        """Initialize the summary panel."""
        super().__init__(parent)
        self.expense_manager = expense_manager

        self.create_widgets()
        self.refresh_summary()

    def create_widgets(self):
        """Create all summary widgets."""
        # Main container with scrollbar
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create content in scrollable frame
        self.create_period_selector(scrollable_frame)
        self.create_summary_cards(scrollable_frame)
        self.create_category_breakdown(scrollable_frame)
        self.create_trend_analysis(scrollable_frame)

        self.scrollable_frame = scrollable_frame

    def create_period_selector(self, parent):
        """Create period selection controls."""
        period_frame = ttk.LabelFrame(parent, text="Time Period", padding="10")
        period_frame.pack(fill=tk.X, pady=(0, 10))

        # Period selection
        ttk.Label(period_frame, text="Show summary for:").pack(side=tk.LEFT, padx=(0, 10))

        self.period_var = tk.StringVar(value="current_month")
        periods = [
            ("Current Month", "current_month"),
            ("Last Month", "last_month"),
            ("Current Year", "current_year"),
            ("Last 3 Months", "last_3_months"),
            ("Last 6 Months", "last_6_months"),
            ("Custom Range", "custom")
        ]

        for text, value in periods:
            ttk.Radiobutton(period_frame, text=text, variable=self.period_var,
                          value=value, command=self.on_period_change).pack(side=tk.LEFT, padx=5)

        # Custom date range (initially hidden)
        self.custom_frame = ttk.Frame(period_frame)
        self.custom_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(self.custom_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
        self.from_date_var = tk.StringVar()
        self.from_date_entry = ttk.Entry(self.custom_frame, textvariable=self.from_date_var, width=12)
        self.from_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(self.custom_frame, text="To:").pack(side=tk.LEFT, padx=(0, 5))
        self.to_date_var = tk.StringVar()
        self.to_date_entry = ttk.Entry(self.custom_frame, textvariable=self.to_date_var, width=12)
        self.to_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(self.custom_frame, text="Apply", command=self.apply_custom_range).pack(side=tk.LEFT)

    def create_summary_cards(self, parent):
        """Create summary cards showing key metrics."""
        cards_frame = ttk.LabelFrame(parent, text="Summary", padding="10")
        cards_frame.pack(fill=tk.X, pady=(0, 10))

        # Create a grid for summary cards
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)

        # Total expenses card
        self.total_frame = ttk.Frame(cards_frame, relief=tk.RIDGE, borderwidth=2)
        self.total_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.total_frame, text="Total Expenses", font=('Arial', 10, 'bold')).pack(pady=5)
        self.total_label = ttk.Label(self.total_frame, text="Loading...", font=('Arial', 14, 'bold'))
        self.total_label.pack(pady=5)
        self.count_label = ttk.Label(self.total_frame, text="0 transactions")
        self.count_label.pack(pady=(0, 5))

        # Average expense card
        self.avg_frame = ttk.Frame(cards_frame, relief=tk.RIDGE, borderwidth=2)
        self.avg_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.avg_frame, text="Average Expense", font=('Arial', 10, 'bold')).pack(pady=5)
        self.avg_label = ttk.Label(self.avg_frame, text="Loading...", font=('Arial', 14, 'bold'))
        self.avg_label.pack(pady=5)
        self.daily_avg_label = ttk.Label(self.avg_frame, text="Daily: Calculating...")
        self.daily_avg_label.pack(pady=(0, 5))

        # Largest expense card
        self.largest_frame = ttk.Frame(cards_frame, relief=tk.RIDGE, borderwidth=2)
        self.largest_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.largest_frame, text="Largest Expense", font=('Arial', 10, 'bold')).pack(pady=5)
        self.largest_label = ttk.Label(self.largest_frame, text="Loading...", font=('Arial', 14, 'bold'))
        self.largest_label.pack(pady=5)
        self.largest_desc_label = ttk.Label(self.largest_frame, text="N/A", font=('Arial', 9))
        self.largest_desc_label.pack(pady=(0, 5))

    def create_category_breakdown(self, parent):
        """Create category breakdown section."""
        category_frame = ttk.LabelFrame(parent, text="Category Breakdown", padding="10")
        category_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Treeview for category breakdown
        columns = ('category', 'amount', 'count', 'percentage')
        self.category_tree = ttk.Treeview(category_frame, columns=columns, show='headings', height=8)

        # Define column headings
        self.category_tree.heading('category', text='Category')
        self.category_tree.heading('amount', text='Amount')
        self.category_tree.heading('count', text='Count')
        self.category_tree.heading('percentage', text='%')

        # Configure column widths
        self.category_tree.column('category', width=150, minwidth=120)
        self.category_tree.column('amount', width=120, minwidth=100)
        self.category_tree.column('count', width=80, minwidth=60)
        self.category_tree.column('percentage', width=80, minwidth=60)

        # Scrollbar
        cat_scrollbar = ttk.Scrollbar(category_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=cat_scrollbar.set)

        self.category_tree.pack(side="left", fill="both", expand=True)
        cat_scrollbar.pack(side="right", fill="y")

    def create_trend_analysis(self, parent):
        """Create trend analysis section."""
        trend_frame = ttk.LabelFrame(parent, text="Monthly Trend", padding="10")
        trend_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Trend treeview
        columns = ('month', 'total', 'count', 'avg')
        self.trend_tree = ttk.Treeview(trend_frame, columns=columns, show='headings', height=6)

        # Define column headings
        self.trend_tree.heading('month', text='Month')
        self.trend_tree.heading('total', text='Total')
        self.trend_tree.heading('count', text='Count')
        self.trend_tree.heading('avg', text='Average')

        # Configure column widths
        self.trend_tree.column('month', width=100, minwidth=80)
        self.trend_tree.column('total', width=100, minwidth=80)
        self.trend_tree.column('count', width=60, minwidth=50)
        self.trend_tree.column('avg', width=80, minwidth=70)

        # Scrollbar
        trend_scrollbar = ttk.Scrollbar(trend_frame, orient="vertical", command=self.trend_tree.yview)
        self.trend_tree.configure(yscrollcommand=trend_scrollbar.set)

        self.trend_tree.pack(side="left", fill="both", expand=True)
        trend_scrollbar.pack(side="right", fill="y")

        # Refresh button
        refresh_btn = ttk.Button(parent, text="Refresh Summary",
                                command=self.refresh_summary)
        refresh_btn.pack(pady=10)

    def on_period_change(self):
        """Handle period selection change."""
        if self.period_var.get() == "custom":
            self.custom_frame.pack(fill=tk.X, pady=(10, 0))
            # Set default dates for custom range
            today = date.today()
            first_day = date(today.year, today.month, 1)
            self.from_date_var.set(first_day.strftime("%Y-%m-%d"))
            self.to_date_var.set(today.strftime("%Y-%m-%d"))
        else:
            self.custom_frame.pack_forget()
            self.refresh_summary()

    def apply_custom_range(self):
        """Apply custom date range."""
        from_date = self.from_date_var.get().strip()
        to_date = self.to_date_var.get().strip()

        if not from_date or not to_date:
            messagebox.showerror("Error", "Please select both from and to dates")
            return

        try:
            # Validate dates
            from_parsed = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_parsed = datetime.strptime(to_date, "%Y-%m-%d").date()

            if from_parsed > to_parsed:
                messagebox.showerror("Error", "From date cannot be after to date")
                return

            self.refresh_summary()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")

    def get_date_range(self) -> tuple:
        """Get date range based on selected period."""
        today = date.today()

        if self.period_var.get() == "current_month":
            start_date = date(today.year, today.month, 1)
            end_date = today

        elif self.period_var.get() == "last_month":
            if today.month == 1:
                start_date = date(today.year - 1, 12, 1)
                end_date = date(today.year, 1, 1) - timedelta(days=1)
            else:
                start_date = date(today.year, today.month - 1, 1)
                if today.month == 12:
                    end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(today.year, today.month, 1) - timedelta(days=1)

        elif self.period_var.get() == "current_year":
            start_date = date(today.year, 1, 1)
            end_date = today

        elif self.period_var.get() == "last_3_months":
            start_date = today - timedelta(days=90)
            end_date = today

        elif self.period_var.get() == "last_6_months":
            start_date = today - timedelta(days=180)
            end_date = today

        elif self.period_var.get() == "custom":
            start_date = datetime.strptime(self.from_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.strptime(self.to_date_var.get(), "%Y-%m-%d").date()

        else:
            # Default to current month
            start_date = date(today.year, today.month, 1)
            end_date = today

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def refresh_summary(self):
        """Refresh all summary data."""
        try:
            # Get date range
            date_from, date_to = self.get_date_range()

            # Update summary cards
            self.update_summary_cards(date_from, date_to)

            # Update category breakdown
            self.update_category_breakdown(date_from, date_to)

            # Update trend analysis
            self.update_trend_analysis()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh summary: {str(e)}")

    def update_summary_cards(self, date_from: str, date_to: str):
        """Update summary cards with data."""
        # Get summary data
        summary = self.expense_manager.get_expense_summary(date_from, date_to)

        # Update total
        self.total_label.config(text=summary['total_formatted'])
        self.count_label.config(text=f"{summary['count']} transaction{'s' if summary['count'] != 1 else ''}")

        # Update average
        self.avg_label.config(text=summary['average_formatted'])
        if summary['count'] > 0:
            # Calculate daily average
            try:
                from_date_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
                to_date_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
                days = (to_date_obj - from_date_obj).days + 1
                daily_avg = summary['total'] / days
                daily_avg_formatted = self.expense_manager.get_currency_formatted_value(daily_avg)
                self.daily_avg_label.config(text=f"Daily: {daily_avg_formatted}")
            except:
                self.daily_avg_label.config(text="Daily: N/A")
        else:
            self.daily_avg_label.config(text="Daily: N/A")

        # Update largest expense
        if summary['count'] > 0:
            try:
                # Get largest expense
                filters = {'date_from': date_from, 'date_to': date_to}
                expenses = self.expense_manager.db.get_expenses(filters=filters, sort_by='amount', sort_order='DESC', limit=1)
                if expenses:
                    largest = expenses[0]
                    self.largest_label.config(text=self.expense_manager.get_currency_formatted_value(largest['amount']))
                    desc = largest['description'] or "N/A"
                    if len(desc) > 20:
                        desc = desc[:17] + "..."
                    self.largest_desc_label.config(text=desc)
                else:
                    self.largest_label.config(text=self.expense_manager.get_currency_formatted_value(0))
                    self.largest_desc_label.config(text="N/A")
            except:
                self.largest_label.config(text=self.expense_manager.get_currency_formatted_value(0))
                self.largest_desc_label.config(text="N/A")
        else:
            self.largest_label.config(text=self.expense_manager.get_currency_formatted_value(0))
            self.largest_desc_label.config(text="N/A")

    def update_category_breakdown(self, date_from: str, date_to: str):
        """Update category breakdown."""
        # Clear existing items
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        # Get category breakdown
        breakdown = self.expense_manager.get_category_breakdown(date_from, date_to)

        # Add categories to treeview
        for item in breakdown:
            self.category_tree.insert('', tk.END, values=(
                item['category'],
                item.get('total_formatted', 'N/A'),
                item['count'],
                item.get('percentage_formatted', '0.0%')
            ))

    def update_trend_analysis(self):
        """Update monthly trend analysis."""
        # Clear existing items
        for item in self.trend_tree.get_children():
            self.trend_tree.delete(item)

        # Get last 6 months of data
        today = date.today()
        trends = []

        for i in range(6):
            # Calculate month
            month_date = today.replace(day=1)
            if month_date.month - i <= 0:
                year = month_date.year - 1
                month = month_date.month - i + 12
            else:
                year = month_date.year
                month = month_date.month - i

            # Get month summary
            summary = self.expense_manager.get_monthly_summary(year, month)
            trends.append((month, year, summary))

        # Add trends to treeview (in reverse order to show chronological)
        trends.reverse()
        for month, year, summary in trends:
            if summary['count'] > 0:
                self.trend_tree.insert('', tk.END, values=(
                    summary['month_name'],
                    summary['total_formatted'],
                    summary['count'],
                    summary['average_formatted']
                ))
