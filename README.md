# Expense Tracker

A simple and intuitive personal expense tracking application built with Python and Tkinter. Track your daily expenses, categorize spending, and monitor your financial habits through an easy-to-use desktop application.

![Expense Tracker](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 📊 Core Functionality
- **Add Expenses**: Quickly add new expenses with date, category, amount, and description
- **View Expenses**: Organized list view with sorting and pagination
- **Search & Filter**: Advanced filtering by date range, category, amount, and text search
- **Delete Expenses**: Remove unwanted expenses with confirmation
- **Data Export**: Export expenses to CSV and Excel formats

### 📈 Analytics & Summary
- **Monthly Summaries**: Track spending patterns month by month
- **Category Breakdown**: Visual breakdown of spending by category
- **Trend Analysis**: Monitor spending trends over time
- **Statistics**: Total expenses, average spending, largest transactions

### 🌍 Currency Support
- **Multiple Currencies**: Built-in support for USD ($), INR (₹), EUR (€), GBP (£), JPY (¥)
- **Custom Currency**: Add your own currency symbols and formatting
- **Flexible Formatting**: Configurable decimal and thousands separators
- **Position Options**: Currency symbol as prefix or suffix

### ⚙️ Configuration & Settings
- **Customizable UI**: Adjustable window size and theme preferences
- **Data Settings**: Configurable items per page and backup options
- **Export Preferences**: Default export format and options
- **Backup & Restore**: Automatic database backups with configurable frequency

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or Download** the repository:
   ```bash
   git clone https://github.com/RahulNathan19/Expence_Tracker.git
   cd Expence_Tracker
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

That's it! The Expense Tracker will launch with a clean, intuitive interface.

## 📖 Usage Guide

### Adding Expenses
1. Click on the "Add Expense" tab or press `Ctrl+N`
2. Fill in the expense details:
   - **Date**: Select date (defaults to today)
   - **Category**: Choose from predefined categories or create custom ones
   - **Amount**: Enter the expense amount
   - **Description**: Add optional notes (max 200 characters)
3. Click "Add Expense" to save

### Viewing and Managing Expenses
1. **Expenses Tab**: View all your expenses in an organized table
2. **Sorting**: Click column headers to sort by date, amount, or category
3. **Pagination**: Navigate through large lists using pagination controls
4. **Quick Actions**: Right-click expenses for context menu options

### Filtering and Searching
1. **Date Range**: Filter expenses by specific time periods
2. **Quick Filters**: Use preset buttons for "Today", "This Week", "This Month", etc.
3. **Category Filter**: Show expenses from specific categories
4. **Amount Range**: Filter by minimum and maximum amounts
5. **Text Search**: Search descriptions for specific keywords

### Analytics and Reports
1. **Summary Tab**: View spending analytics and insights
2. **Time Periods**: Analyze expenses for different time periods
3. **Category Breakdown**: See spending distribution across categories
4. **Trends**: Monitor spending patterns over time

### Exporting Data
1. **Menu → File → Export**: Choose CSV or Excel format
2. **Export Options**: Include all expenses or apply current filters
3. **Custom Exports**: Export specific date ranges or categories

### Currency Configuration
1. **Menu → Edit → Settings**: Open currency settings
2. **Preset Currencies**: Choose from USD, INR, EUR, GBP, or JPY
3. **Custom Settings**: Configure symbol, position, and formatting
4. **Preview**: See formatted amounts before applying changes

## 🎯 Default Categories

The application comes with these predefined categories:
- **Food & Dining** 🍔
- **Transportation** 🚗
- **Utilities** 💡
- **Entertainment** 🎬
- **Healthcare** 🏥
- **Shopping** 🛍️
- **Education** 📚
- **Other** 📝

You can use these as-is or modify them to suit your needs.

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Switch to Add Expense tab |
| `Ctrl+L` | Switch to Expenses list tab |
| `Ctrl+S` | Open Settings dialog |
| `Ctrl+E` | Export data to CSV |
| `Ctrl+Q` | Quit application |
| `F5` | Refresh all data |
| `Tab` | Navigate between fields |
| `Enter` | Submit forms/apply actions |
| `Esc` | Cancel dialogs |

## 💾 Data Storage

- **Database**: SQLite database (`expenses.db`) for local data storage
- **Settings**: JSON configuration file (`settings.json`) for user preferences
- **Backups**: Automatic backups in `backups/` directory
- **Portability**: All data stored locally - no internet connection required

## 🔧 Technical Details

### Architecture
- **Frontend**: Tkinter GUI with ttk widgets
- **Backend**: SQLite database with Python database API
- **Export**: CSV (standard library) and Excel (openpyxl)
- **Configuration**: JSON-based settings management

### File Structure
```
Expence_Tracker/
├── main.py                 # Application entry point
├── expense_manager.py      # Core business logic
├── database.py            # Database operations
├── settings.py            # Configuration management
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── expenses.db            # SQLite database (created automatically)
├── settings.json          # User settings (created automatically)
├── backups/               # Database backups (created automatically)
└── gui/                   # GUI components
    ├── __init__.py
    ├── add_expense.py     # Add expense form
    ├── expense_list.py    # Expense display list
    ├── summary_panel.py   # Analytics and summaries
    ├── filter_panel.py    # Search and filter controls
    └── settings_dialog.py # Settings configuration dialog
```

### Dependencies
- **tkinter**: GUI framework (included with Python)
- **sqlite3**: Database engine (included with Python)
- **openpyxl**: Excel export support
- **json**: Settings storage (included with Python)
- **csv**: CSV export support (included with Python)
- **datetime**: Date handling (included with Python)

## 🌟 Advanced Features

### Currency Support
The application supports multiple currency formats:

**Indian Rupee (INR) Example:**
- Symbol: ₹
- Format: ₹ 1,234.56
- Decimal separator: .
- Thousands separator: ,

**US Dollar (USD) Example:**
- Symbol: $
- Format: $1,234.56
- Decimal separator: .
- Thousands separator: ,

**European Format Example:**
- Symbol: €
- Format: 1.234,56 €
- Decimal separator: ,
- Thousands separator: .

### Data Export Options

**CSV Export:**
- Compatible with Excel, Google Sheets, and spreadsheet applications
- Configurable column headers
- Custom date formats

**Excel Export:**
- Formatted cells with currency styling
- Auto-adjusted column widths
- Professional appearance with headers

### Backup and Recovery
- **Automatic Backups**: Configurable daily, weekly, or monthly backups
- **Manual Backups**: Create instant database backups
- **Settings Export/Import**: Backup and restore application settings

## 🐛 Troubleshooting

### Common Issues

**Application Won't Start:**
```bash
# Check Python version (should be 3.7+)
python --version

# Install missing dependencies
pip install -r requirements.txt

# Run with error output
python main.py
```

**Database Errors:**
- The application automatically creates the database on first run
- Check file permissions in the application directory
- Ensure `expenses.db` is not locked by another process

**Export Issues:**
- For Excel export, ensure `openpyxl` is installed
- Check file permissions for the export location
- Verify disk space availability

**Font/UI Issues:**
- Tkinter uses system fonts - ensure system fonts are available
- On Linux, you may need to install font packages
- UI automatically adapts to system theme

### Performance Tips
- **Large Databases**: Use filters to work with manageable data subsets
- **Regular Backups**: Keep backups to prevent data loss
- **Settings Cleanup**: Reset to defaults if settings become corrupted

## 🤝 Contributing

This is a personal finance tool designed for simplicity and ease of use. While contributions are welcome, the focus is on maintaining a clean, intuitive interface rather than adding complex features.

### Development Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python main.py`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tkinter**: For providing a cross-platform GUI framework
- **SQLite**: For reliable, lightweight database storage
- **openpyxl**: For Excel export functionality
- **Python Community**: For excellent documentation and libraries

## 📞 Support

If you encounter issues or have questions:

1. Check this README for troubleshooting tips
2. Review the keyboard shortcuts and usage guide
3. Make sure Python and dependencies are properly installed
4. Report issues with detailed error messages and system information

---

**Happy Expense Tracking!** 💰📊

Made with ❤️ for personal finance management.
