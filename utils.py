import csv
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


def format_currency(amount: float, settings: Dict[str, Any]) -> str:
    """Format a number as currency according to user settings."""
    if amount is None:
        return ""

    # Get currency settings
    symbol = settings.get('symbol', '$')
    position = settings.get('position', 'prefix')
    decimal_sep = settings.get('decimal_separator', '.')
    thousands_sep = settings.get('thousands_separator', ',')

    # Format the number with proper separators
    if thousands_sep:
        # Format with thousands separator
        formatted = "{:,.2f}".format(abs(amount))
        # Replace default separators with user preferences
        formatted = formatted.replace(',', 'TEMP').replace('.', 'TEMP2')
        formatted = formatted.replace('TEMP', thousands_sep).replace('TEMP2', decimal_sep)
    else:
        # Format without thousands separator
        formatted = "{:.2f}".format(abs(amount))
        formatted = formatted.replace('.', decimal_sep)

    # Add currency symbol and sign
    if amount < 0:
        formatted = "-" + formatted

    if position == 'prefix':
        return f"{symbol}{formatted}"
    else:
        return f"{formatted}{symbol}"


def parse_date(date_string: str, date_format: str = "%Y-%m-%d") -> Optional[date]:
    """Parse a date string and return a date object."""
    try:
        return datetime.strptime(date_string, date_format).date()
    except (ValueError, TypeError):
        return None


def format_date(date_obj: Union[date, datetime], date_format: str = "%Y-%m-%d") -> str:
    """Format a date object as a string."""
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    return date_obj.strftime(date_format)


def get_current_date_string(date_format: str = "%Y-%m-%d") -> str:
    """Get current date as formatted string."""
    return date.today().strftime(date_format)


def validate_amount(amount_str: str) -> Optional[float]:
    """Validate and parse amount string."""
    try:
        # Remove currency symbols and thousands separators
        cleaned = amount_str.strip().replace('$', '').replace(',', '').replace(' ', '')
        amount = float(cleaned)
        if amount >= 0:
            return amount
        return None
    except (ValueError, AttributeError):
        return None


def validate_date(date_str: str, allow_future: bool = False) -> bool:
    """Validate date string and check if it's reasonable."""
    if not date_str:
        return False

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()

        # Check if date is not too far in the past
        min_date = date(1900, 1, 1)
        if parsed_date < min_date:
            return False

        # Check if future dates are allowed
        if not allow_future and parsed_date > today:
            return False

        return True
    except ValueError:
        return False


def validate_description(description: str, max_length: int = 200) -> bool:
    """Validate description text."""
    if description is None:
        return True
    return len(description.strip()) <= max_length


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def generate_export_filename(prefix: str = "expenses",
                           extension: str = "csv",
                           date_format: str = "%Y-%m-%d") -> str:
    """Generate a filename for export files."""
    date_str = datetime.now().strftime(date_format)
    filename = f"{prefix}_{date_str}.{extension}"
    return sanitize_filename(filename)


def export_to_csv(data: List[Dict], file_path: str,
                 include_headers: bool = True,
                 headers: Optional[List[str]] = None) -> bool:
    """Export data to CSV file."""
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            if not data:
                return False

            # Use provided headers or extract from data keys
            if headers is None:
                headers = list(data[0].keys())

            writer = csv.DictWriter(csvfile, fieldnames=headers)

            if include_headers:
                writer.writeheader()

            for row in data:
                # Filter row data to only include header columns
                filtered_row = {key: row.get(key, '') for key in headers}
                writer.writerow(filtered_row)

        return True
    except (IOError, csv.Error):
        return False


def export_to_excel(data: List[Dict], file_path: str,
                   include_headers: bool = True,
                   headers: Optional[List[str]] = None,
                   settings: Optional[Dict[str, Any]] = None) -> bool:
    """Export data to Excel file with formatting."""
    if not OPENPYXL_AVAILABLE:
        return False

    try:
        if not data:
            return False

        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"

        # Use provided headers or extract from data keys
        if headers is None:
            headers = list(data[0].keys())

        # Header styling
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center")

        # Write headers
        if include_headers:
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment

        # Write data
        for row_num, row_data in enumerate(data, 2 if include_headers else 1):
            for col_num, header in enumerate(headers, 1):
                value = row_data.get(header, '')

                # Apply currency formatting for amount column
                if header == 'amount' and isinstance(value, (int, float)):
                    cell = ws.cell(row=row_num, column=col_num, value=float(value))
                    if settings:
                        # Excel uses different format codes
                        decimal_sep = settings.get('decimal_separator', '.')
                        thousands_sep = settings.get('thousands_separator', ',')

                        if decimal_sep == ',' and thousands_sep == '.':
                            cell.number_format = '#.##0,00 €'  # European format
                        else:
                            cell.number_format = '$#,##0.00'  # US format
                else:
                    cell = ws.cell(row=row_num, column=col_num, value=value)

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width

        wb.save(file_path)
        return True
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def ensure_directory_exists(directory: str) -> bool:
    """Ensure a directory exists, create it if necessary."""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length with suffix."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_expense_categories() -> List[str]:
    """Get default expense categories."""
    return [
        "Food & Dining",
        "Transportation",
        "Utilities",
        "Entertainment",
        "Healthcare",
        "Shopping",
        "Education",
        "Other"
    ]


def calculate_monthly_summary(expenses: List[Dict]) -> Dict[str, Any]:
    """Calculate monthly summary statistics from expenses."""
    if not expenses:
        return {
            'total': 0.0,
            'count': 0,
            'average': 0.0,
            'categories': {}
        }

    total = sum(expense['amount'] for expense in expenses)
    count = len(expenses)
    average = total / count if count > 0 else 0.0

    # Category breakdown
    categories = {}
    for expense in expenses:
        category = expense['category']
        if category not in categories:
            categories[category] = {'count': 0, 'total': 0.0}
        categories[category]['count'] += 1
        categories[category]['total'] += expense['amount']

    # Add percentages to categories
    for category_data in categories.values():
        category_data['percentage'] = (category_data['total'] / total * 100) if total > 0 else 0.0

    return {
        'total': total,
        'count': count,
        'average': average,
        'categories': categories
    }


def backup_file(source_path: str, backup_dir: str = "backups") -> Optional[str]:
    """Create a backup of a file."""
    try:
        ensure_directory_exists(backup_dir)

        source_name = os.path.basename(source_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{source_name}"
        backup_path = os.path.join(backup_dir, backup_name)

        # Copy the file
        import shutil
        shutil.copy2(source_path, backup_path)

        return backup_path
    except Exception:
        return None