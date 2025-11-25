from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from database import DatabaseHandler
from settings import SettingsManager
from utils import (
    validate_amount, validate_date, validate_description,
    format_currency, parse_date, format_date, get_current_date_string,
    export_to_csv, export_to_excel, generate_export_filename,
    calculate_monthly_summary, backup_file
)


class ExpenseManager:
    """Core business logic for expense management."""

    def __init__(self, db_path: str = "expenses.db", settings_file: str = "settings.json"):
        """Initialize expense manager with database and settings."""
        self.db = DatabaseHandler(db_path)
        self.settings = SettingsManager(settings_file)

    def add_expense(self, date_str: str, category: str, amount_str: str,
                   description: Optional[str] = None) -> Tuple[bool, str]:
        """Add a new expense with validation."""
        # Validate date
        if not validate_date(date_str):
            return False, "Invalid date. Please use YYYY-MM-DD format and avoid future dates."

        # Validate amount
        amount = validate_amount(amount_str)
        if amount is None:
            return False, "Invalid amount. Please enter a positive number."

        # Validate description
        if not validate_description(description or ""):
            return False, "Description is too long (maximum 200 characters)."

        # Validate category
        if not category or not category.strip():
            category = "Other"

        try:
            # Add to database
            expense_id = self.db.add_expense(date_str, category.strip(), amount, description.strip() if description else None)
            return True, f"Expense added successfully (ID: {expense_id})"
        except Exception as e:
            return False, f"Failed to add expense: {str(e)}"

    def get_expenses(self, filters: Optional[Dict[str, Any]] = None,
                    sort_by: str = 'date', sort_order: str = 'DESC',
                    page: int = 1, per_page: Optional[int] = None) -> Dict[str, Any]:
        """Retrieve expenses with pagination, filtering, and sorting."""
        try:
            # Get settings for pagination
            if per_page is None:
                per_page = self.settings.get('data.items_per_page', 50)

            # Calculate offset for pagination
            offset = (page - 1) * per_page if page > 1 else 0

            # Get total count for pagination
            all_expenses = self.db.get_expenses(filters=filters, sort_by=sort_by, sort_order=sort_order)
            total_count = len(all_expenses)

            # Get paginated results
            expenses = self.db.get_expenses(
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=per_page
            )

            # If not first page, we need to get the correct slice
            if page > 1:
                # For simplicity, get all and slice
                all_expenses = self.db.get_expenses(filters=filters, sort_by=sort_by, sort_order=sort_order)
                expenses = all_expenses[offset:offset + per_page]

            # Format expenses for display
            formatted_expenses = []
            currency_settings = self.settings.get_currency_settings()

            for expense in expenses:
                formatted_expense = expense.copy()
                formatted_expense['amount_formatted'] = format_currency(expense['amount'], currency_settings)
                formatted_expense['date_formatted'] = format_date(parse_date(expense['date']))
                formatted_expenses.append(formatted_expense)

            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page if per_page > 0 else 1

            return {
                'expenses': formatted_expenses,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        except Exception as e:
            return {
                'expenses': [],
                'total_count': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False,
                'error': str(e)
            }

    def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a single expense by ID."""
        try:
            expense = self.db.get_expense_by_id(expense_id)
            if expense:
                currency_settings = self.settings.get_currency_settings()
                expense['amount_formatted'] = format_currency(expense['amount'], currency_settings)
                expense['date_formatted'] = format_date(parse_date(expense['date']))
            return expense
        except Exception:
            return None

    def update_expense(self, expense_id: int, date_str: str, category: str,
                      amount_str: str, description: Optional[str] = None) -> Tuple[bool, str]:
        """Update an existing expense."""
        # Validate date
        if not validate_date(date_str):
            return False, "Invalid date. Please use YYYY-MM-DD format and avoid future dates."

        # Validate amount
        amount = validate_amount(amount_str)
        if amount is None:
            return False, "Invalid amount. Please enter a positive number."

        # Validate description
        if not validate_description(description or ""):
            return False, "Description is too long (maximum 200 characters)."

        # Validate category
        if not category or not category.strip():
            category = "Other"

        try:
            success = self.db.update_expense(expense_id, date_str, category.strip(),
                                          amount, description.strip() if description else None)
            if success:
                return True, "Expense updated successfully"
            else:
                return False, "Expense not found"
        except Exception as e:
            return False, f"Failed to update expense: {str(e)}"

    def delete_expense(self, expense_id: int) -> Tuple[bool, str]:
        """Delete an expense."""
        try:
            success = self.db.delete_expense(expense_id)
            if success:
                return True, "Expense deleted successfully"
            else:
                return False, "Expense not found"
        except Exception as e:
            return False, f"Failed to delete expense: {str(e)}"

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all available categories."""
        try:
            return self.db.get_categories()
        except Exception:
            return []

    def get_expense_summary(self, date_from: Optional[str] = None,
                           date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get expense summary with formatted values."""
        try:
            summary = self.db.get_expense_summary(date_from, date_to)
            currency_settings = self.settings.get_currency_settings()

            # Format monetary values
            summary['total_formatted'] = format_currency(summary['total'], currency_settings)
            summary['average_formatted'] = format_currency(summary['average'], currency_settings)

            return summary
        except Exception as e:
            return {
                'count': 0,
                'total': 0.0,
                'total_formatted': format_currency(0.0, self.settings.get_currency_settings()),
                'average': 0.0,
                'average_formatted': format_currency(0.0, self.settings.get_currency_settings()),
                'error': str(e)
            }

    def get_category_breakdown(self, date_from: Optional[str] = None,
                              date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get category breakdown with percentages and formatted values."""
        try:
            breakdown = self.db.get_category_breakdown(date_from, date_to)
            currency_settings = self.settings.get_currency_settings()

            # Calculate total for percentage calculation
            total = sum(item['total'] for item in breakdown)

            # Format monetary values and calculate percentages
            for item in breakdown:
                item['total_formatted'] = format_currency(item['total'], currency_settings)
                item['percentage'] = (item['total'] / total * 100) if total > 0 else 0.0
                item['percentage_formatted'] = f"{item['percentage']:.1f}%"

            return breakdown
        except Exception as e:
            return [{'error': str(e)}]

    def get_monthly_summary(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        """Get monthly summary for a specific year/month or current month."""
        try:
            if year is None or month is None:
                today = date.today()
                year = today.year
                month = today.month

            # Create date range for the month
            date_from = f"{year:04d}-{month:02d}-01"

            # Get last day of the month
            if month == 12:
                date_to = f"{year + 1:04d}-01-01"
            else:
                date_to = f"{year:04d}-{month + 1:02d}-01"

            # Get expenses for the month
            expenses = self.db.get_expenses(filters={'date_from': date_from, 'date_to': date_to})

            # Calculate summary using utility function
            summary = calculate_monthly_summary(expenses)
            currency_settings = self.settings.get_currency_settings()

            # Format monetary values
            summary['total_formatted'] = format_currency(summary['total'], currency_settings)
            summary['average_formatted'] = format_currency(summary['average'], currency_settings)

            # Format category breakdown
            for category, data in summary['categories'].items():
                data['total_formatted'] = format_currency(data['total'], currency_settings)

            result = {
                'year': year,
                'month': month,
                'month_name': datetime(year, month, 1).strftime('%B %Y'),
            }
            result.update(summary)
            return result
        except Exception as e:
            return {
                'year': year or datetime.now().year,
                'month': month or datetime.now().month,
                'month_name': datetime.now().strftime('%B %Y'),
                'total': 0.0,
                'total_formatted': format_currency(0.0, self.settings.get_currency_settings()),
                'count': 0,
                'average': 0.0,
                'average_formatted': format_currency(0.0, self.settings.get_currency_settings()),
                'categories': {},
                'error': str(e)
            }

    def export_expenses(self, export_format: str = "csv",
                       filters: Optional[Dict[str, Any]] = None,
                       file_path: Optional[str] = None) -> Tuple[bool, str]:
        """Export expenses to CSV or Excel file."""
        try:
            # Get expenses data
            expenses = self.db.get_expenses(filters=filters)

            if not expenses:
                return False, "No expenses to export"

            # Generate filename if not provided
            if file_path is None:
                extension = export_format.lower()
                filename = generate_export_filename("expenses", extension)
                file_path = filename

            # Prepare headers
            headers = ['date', 'category', 'description', 'amount', 'created_at']
            export_data = []

            for expense in expenses:
                export_data.append({key: expense.get(key, '') for key in headers})

            # Export based on format
            if export_format.lower() == "csv":
                success = export_to_csv(export_data, file_path,
                                      include_headers=self.settings.get('export.include_headers', True),
                                      headers=headers)
            elif export_format.lower() == "xlsx":
                success = export_to_excel(export_data, file_path,
                                        include_headers=self.settings.get('export.include_headers', True),
                                        headers=headers,
                                        settings=self.settings.get_currency_settings())
            else:
                return False, f"Unsupported export format: {export_format}"

            if success:
                return True, f"Expenses exported successfully to {file_path}"
            else:
                return False, "Export failed"

        except Exception as e:
            return False, f"Export error: {str(e)}"

    def create_backup(self) -> Tuple[bool, str]:
        """Create a backup of the database."""
        try:
            backup_path = backup_file(self.db.db_path)
            if backup_path:
                return True, f"Database backup created: {backup_path}"
            else:
                return False, "Failed to create backup"
        except Exception as e:
            return False, f"Backup error: {str(e)}"

    def validate_filters(self, filters: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate filter parameters."""
        if not isinstance(filters, dict):
            return False, "Filters must be a dictionary"

        # Validate date range
        if 'date_from' in filters and filters['date_from']:
            if not validate_date(filters['date_from']):
                return False, "Invalid 'from' date"

        if 'date_to' in filters and filters['date_to']:
            if not validate_date(filters['date_to']):
                return False, "Invalid 'to' date"

        # Validate amount range
        if 'min_amount' in filters and filters['min_amount'] is not None:
            try:
                amount = float(filters['min_amount'])
                if amount < 0:
                    return False, "Minimum amount cannot be negative"
            except (ValueError, TypeError):
                return False, "Invalid minimum amount"

        if 'max_amount' in filters and filters['max_amount'] is not None:
            try:
                amount = float(filters['max_amount'])
                if amount < 0:
                    return False, "Maximum amount cannot be negative"
            except (ValueError, TypeError):
                return False, "Invalid maximum amount"

        # Check if min > max
        if ('min_amount' in filters and 'max_amount' in filters and
            filters['min_amount'] is not None and filters['max_amount'] is not None):
            if float(filters['min_amount']) > float(filters['max_amount']):
                return False, "Minimum amount cannot be greater than maximum amount"

        return True, "Filters are valid"

    def get_currency_formatted_value(self, amount: float) -> str:
        """Format a monetary amount according to user settings."""
        return format_currency(amount, self.settings.get_currency_settings())

    def get_current_date_formatted(self) -> str:
        """Get current date formatted according to user settings."""
        date_format = self.settings.get('ui.default_date_format', '%Y-%m-%d')
        return get_current_date_string(date_format)

    def close(self) -> None:
        """Close database connection."""
        self.db.close()