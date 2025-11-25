import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any, List
import calendar


class ExpenseList(ttk.Frame):
    """Widget for displaying and managing expenses list."""

    def __init__(self, parent, expense_manager, on_selection_change: Optional[Callable] = None):
        """Initialize the expense list."""
        super().__init__(parent)
        self.expense_manager = expense_manager
        self.on_selection_change = on_selection_change
        self.current_page = 1
        self.total_pages = 1
        self.current_filters = {}
        self.current_sort_by = 'date'
        self.current_sort_order = 'DESC'
        self.selected_expense_id = None

        self.create_widgets()
        self.load_expenses()

    def create_widgets(self):
        """Create all list widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control panel
        self.create_control_panel(main_frame)

        # Treeview for expenses
        self.create_treeview(main_frame)

        # Pagination controls
        self.create_pagination(main_frame)

        # Context menu
        self.create_context_menu()

    def create_control_panel(self, parent):
        """Create control panel with sort and refresh options."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Sort controls
        sort_frame = ttk.Frame(control_frame)
        sort_frame.pack(side=tk.LEFT)

        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=(0, 5))

        self.sort_by_var = tk.StringVar(value='date')
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_by_var,
                                 values=['date', 'amount', 'category', 'created_at'],
                                 state='readonly', width=15)
        sort_combo.pack(side=tk.LEFT, padx=(0, 5))
        sort_combo.bind('<<ComboboxSelected>>', self.on_sort_change)

        self.sort_order_var = tk.StringVar(value='DESC')
        order_combo = ttk.Combobox(sort_frame, textvariable=self.sort_order_var,
                                  values=['ASC', 'DESC'], state='readonly', width=10)
        order_combo.pack(side=tk.LEFT, padx=(0, 10))
        order_combo.bind('<<ComboboxSelected>>', self.on_sort_change)

        # Refresh button
        refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.refresh_list)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        self.delete_btn = ttk.Button(control_frame, text="Delete Selected",
                                   command=self.delete_selected_expense, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT)

        # Export buttons
        export_frame = ttk.Frame(control_frame)
        export_frame.pack(side=tk.RIGHT)

        ttk.Button(export_frame, text="Export CSV",
                  command=lambda: self.export_expenses('csv')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="Export Excel",
                  command=lambda: self.export_expenses('xlsx')).pack(side=tk.LEFT)

    def create_treeview(self, parent):
        """Create the treeview for displaying expenses."""
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        columns = ('date', 'category', 'description', 'amount')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Define column headings and widths
        self.tree.heading('date', text='Date', command=lambda: self.sort_by_column('date'))
        self.tree.heading('category', text='Category', command=lambda: self.sort_by_column('category'))
        self.tree.heading('description', text='Description', command=lambda: self.sort_by_column('description'))
        self.tree.heading('amount', text='Amount', command=lambda: self.sort_by_column('amount'))

        # Set column widths
        self.tree.column('date', width=100, minwidth=80)
        self.tree.column('category', width=120, minwidth=100)
        self.tree.column('description', width=300, minwidth=150)
        self.tree.column('amount', width=100, minwidth=80)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_changed)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

    def create_pagination(self, parent):
        """Create pagination controls."""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill=tk.X, pady=(10, 0))

        # Page info
        self.page_info_var = tk.StringVar()
        self.page_info_label = ttk.Label(pagination_frame, textvariable=self.page_info_var)
        self.page_info_label.pack(side=tk.LEFT)

        # Navigation buttons
        nav_frame = ttk.Frame(pagination_frame)
        nav_frame.pack(side=tk.RIGHT)

        self.first_btn = ttk.Button(nav_frame, text="<<", command=self.first_page, width=3)
        self.first_btn.pack(side=tk.LEFT, padx=(0, 2))

        self.prev_btn = ttk.Button(nav_frame, text="<", command=self.prev_page, width=3)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.page_entry = ttk.Entry(nav_frame, width=8)
        self.page_entry.pack(side=tk.LEFT, padx=(0, 2))
        self.page_entry.bind('<Return>', self.go_to_page)

        self.next_btn = ttk.Button(nav_frame, text=">", command=self.next_page, width=3)
        self.next_btn.pack(side=tk.LEFT, padx=(2, 0))

        self.last_btn = ttk.Button(nav_frame, text=">>", command=self.last_page, width=3)
        self.last_btn.pack(side=tk.LEFT, padx=(2, 0))

    def create_context_menu(self):
        """Create context menu for right-click operations."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected_expense)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_expense)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Amount", command=self.copy_amount)
        self.context_menu.add_command(label="Copy Description", command=self.copy_description)

    def load_expenses(self, page: int = 1):
        """Load expenses into the list."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Get expenses
            result = self.expense_manager.get_expenses(
                filters=self.current_filters,
                sort_by=self.current_sort_by,
                sort_order=self.current_sort_order,
                page=page
            )

            if 'error' in result:
                messagebox.showerror("Error", f"Failed to load expenses: {result['error']}")
                return

            expenses = result['expenses']
            self.total_pages = result['total_pages']
            self.current_page = page

            # Add expenses to treeview
            for expense in expenses:
                # Prepare values for display
                values = (
                    expense['date_formatted'],
                    expense['category'],
                    expense['description'] or '',
                    expense['amount_formatted']
                )

                # Insert item with expense_id as tag
                item = self.tree.insert('', tk.END, values=values)
                self.tree.set(item, 'expense_id', expense['id'])

                # Set tag for row coloring based on category
                self.tree.item(item, tags=(expense['category'],))

            # Configure tag colors for categories
            self.configure_category_tags()

            # Update pagination
            self.update_pagination(result)

            # Update status
            total_count = result['total_count']
            status_text = f"Showing {len(expenses)} of {total_count} expenses"
            if self.current_filters:
                status_text += " (filtered)"
            self.page_info_var.set(status_text)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {str(e)}")

    def configure_category_tags(self):
        """Configure colors for different categories."""
        try:
            categories = self.expense_manager.get_categories()
            for cat in categories:
                color = cat.get('color', '#cccccc')
                self.tree.tag_configure(cat['name'], background=color)
        except Exception:
            # Use default colors if categories fail to load
            pass

    def update_pagination(self, result: Dict[str, Any]):
        """Update pagination controls."""
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page))

        # Update button states
        self.first_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.prev_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if result['has_next'] else tk.DISABLED)
        self.last_btn.config(state=tk.NORMAL if result['has_next'] else tk.DISABLED)

    def sort_by_column(self, column: str):
        """Sort by specific column."""
        # Toggle sort order if same column
        if self.current_sort_by == column:
            self.current_sort_order = 'ASC' if self.current_sort_order == 'DESC' else 'DESC'
        else:
            self.current_sort_by = column
            self.current_sort_order = 'ASC'  # Default to ASC for new column

        # Update sort controls
        self.sort_by_var.set(self.current_sort_by)
        self.sort_order_var.set(self.current_sort_order)

        # Reload data
        self.load_expenses(1)

    def on_sort_change(self, event=None):
        """Handle sort control changes."""
        self.current_sort_by = self.sort_by_var.get()
        self.current_sort_order = self.sort_order_var.get()
        self.load_expenses(1)

    def on_selection_changed(self, event=None):
        """Handle treeview selection changes."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Get expense_id from item data
            expense_id = self.tree.item(item, 'values')[0]  # First value is typically ID or date
            # Actually, we need to store expense_id separately
            try:
                expense_id = int(self.tree.set(item, 'expense_id'))
                self.selected_expense_id = expense_id
                self.delete_btn.config(state=tk.NORMAL)
            except (ValueError, tk.TclError):
                self.selected_expense_id = None
                self.delete_btn.config(state=tk.DISABLED)
        else:
            self.selected_expense_id = None
            self.delete_btn.config(state=tk.DISABLED)

        # Call callback if provided
        if self.on_selection_change:
            self.on_selection_change(self.selected_expense_id)

    def on_double_click(self, event=None):
        """Handle double-click on expense."""
        if self.selected_expense_id:
            self.edit_selected_expense()

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.on_selection_changed()
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_expense(self):
        """Delete the selected expense."""
        if not self.selected_expense_id:
            return

        # Confirm deletion
        if messagebox.askyesno("Confirm Delete",
                              "Are you sure you want to delete this expense?"):
            success, message = self.expense_manager.delete_expense(self.selected_expense_id)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_list()
            else:
                messagebox.showerror("Error", message)

    def edit_selected_expense(self):
        """Edit the selected expense."""
        if not self.selected_expense_id:
            return

        # This would open an edit dialog
        # For now, just show the expense details
        expense = self.expense_manager.get_expense_by_id(self.selected_expense_id)
        if expense:
            details = f"Date: {expense['date_formatted']}\n"
            details += f"Category: {expense['category']}\n"
            details += f"Amount: {expense['amount_formatted']}\n"
            details += f"Description: {expense['description'] or 'N/A'}"
            messagebox.showinfo("Expense Details", details)

    def copy_amount(self):
        """Copy selected expense amount to clipboard."""
        if self.selected_expense_id:
            expense = self.expense_manager.get_expense_by_id(self.selected_expense_id)
            if expense:
                self.clipboard_clear()
                self.clipboard_append(str(expense['amount']))

    def copy_description(self):
        """Copy selected expense description to clipboard."""
        if self.selected_expense_id:
            expense = self.expense_manager.get_expense_by_id(self.selected_expense_id)
            if expense and expense['description']:
                self.clipboard_clear()
                self.clipboard_append(expense['description'])

    def refresh_list(self):
        """Refresh the expense list."""
        self.load_expenses(self.current_page)

    def apply_filters(self, filters: Dict[str, Any]):
        """Apply filters and reload data."""
        self.current_filters = filters
        self.current_page = 1
        self.load_expenses(1)

    def clear_filters(self):
        """Clear all filters and reload data."""
        self.current_filters = {}
        self.current_page = 1
        self.load_expenses(1)

    # Pagination methods
    def first_page(self):
        """Go to first page."""
        if self.current_page > 1:
            self.load_expenses(1)

    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.load_expenses(self.current_page - 1)

    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.load_expenses(self.current_page + 1)

    def last_page(self):
        """Go to last page."""
        if self.current_page < self.total_pages:
            self.load_expenses(self.total_pages)

    def go_to_page(self, event=None):
        """Go to specific page number."""
        try:
            page_num = int(self.page_entry.get())
            if 1 <= page_num <= self.total_pages:
                self.load_expenses(page_num)
            else:
                messagebox.showerror("Invalid Page",
                                  f"Please enter a page number between 1 and {self.total_pages}")
        except ValueError:
            messagebox.showerror("Invalid Page", "Please enter a valid page number")

    def export_expenses(self, format_type: str):
        """Export expenses to file."""
        try:
            success, message = self.expense_manager.export_expenses(
                export_format=format_type,
                filters=self.current_filters
            )
            if success:
                messagebox.showinfo("Export Successful", message)
            else:
                messagebox.showerror("Export Failed", message)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")