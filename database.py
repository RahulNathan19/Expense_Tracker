import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class DatabaseHandler:
    """Handles all SQLite database operations for the expense tracker."""

    def __init__(self, db_path: str = "expenses.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self) -> None:
        """Establish connection to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
        except sqlite3.Error as e:
            raise Exception(f"Failed to connect to database: {e}")

    def create_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.connection.cursor()

            # Create expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#cccccc'
                )
            ''')

            # Insert default categories if they don't exist
            default_categories = [
                ('Food & Dining', '#ff6b6b'),
                ('Transportation', '#4ecdc4'),
                ('Utilities', '#45b7d1'),
                ('Entertainment', '#96ceb4'),
                ('Healthcare', '#ffeaa7'),
                ('Shopping', '#dda0dd'),
                ('Education', '#98d8c8'),
                ('Other', '#dfe6e9')
            ]

            for category_name, color in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, color)
                    VALUES (?, ?)
                ''', (category_name, color))

            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)')

            self.connection.commit()
        except sqlite3.Error as e:
            raise Exception(f"Failed to create tables: {e}")

    def add_expense(self, date: str, category: str, amount: float, description: Optional[str] = None) -> int:
        """Add a new expense to the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO expenses (date, category, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (date, category, amount, description))
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Failed to add expense: {e}")

    def get_expenses(self, filters: Optional[Dict[str, Any]] = None,
                    sort_by: str = 'date', sort_order: str = 'DESC',
                    limit: Optional[int] = None) -> List[Dict]:
        """Retrieve expenses from the database with optional filtering and sorting."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM expenses WHERE 1=1"
            params = []

            if filters:
                if 'date_from' in filters and filters['date_from']:
                    query += " AND date >= ?"
                    params.append(filters['date_from'])

                if 'date_to' in filters and filters['date_to']:
                    query += " AND date <= ?"
                    params.append(filters['date_to'])

                if 'category' in filters and filters['category']:
                    query += " AND category = ?"
                    params.append(filters['category'])

                if 'min_amount' in filters and filters['min_amount'] is not None:
                    query += " AND amount >= ?"
                    params.append(filters['min_amount'])

                if 'max_amount' in filters and filters['max_amount'] is not None:
                    query += " AND amount <= ?"
                    params.append(filters['max_amount'])

                if 'search' in filters and filters['search']:
                    query += " AND description LIKE ?"
                    params.append(f"%{filters['search']}%")

            # Add sorting
            valid_sort_columns = ['date', 'amount', 'category', 'created_at']
            if sort_by in valid_sort_columns:
                query += f" ORDER BY {sort_by}"
                if sort_order.upper() in ['ASC', 'DESC']:
                    query += f" {sort_order.upper()}"

            # Add limit if specified
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Failed to retrieve expenses: {e}")

    def get_expense_by_id(self, expense_id: int) -> Optional[Dict]:
        """Retrieve a single expense by its ID."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Failed to retrieve expense: {e}")

    def update_expense(self, expense_id: int, date: str, category: str,
                      amount: float, description: Optional[str] = None) -> bool:
        """Update an existing expense."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE expenses
                SET date = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
            ''', (date, category, amount, description, expense_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Failed to update expense: {e}")

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense from the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Failed to delete expense: {e}")

    def get_categories(self) -> List[Dict]:
        """Retrieve all categories."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Failed to retrieve categories: {e}")

    def get_expense_summary(self, date_from: Optional[str] = None,
                           date_to: Optional[str] = None) -> Dict:
        """Get summary statistics for expenses within a date range."""
        try:
            cursor = self.connection.cursor()

            query = "SELECT COUNT(*) as count, SUM(amount) as total, AVG(amount) as average FROM expenses WHERE 1=1"
            params = []

            if date_from:
                query += " AND date >= ?"
                params.append(date_from)

            if date_to:
                query += " AND date <= ?"
                params.append(date_to)

            cursor.execute(query, params)
            summary = dict(cursor.fetchone())

            # Handle None values
            summary['total'] = summary['total'] or 0.0
            summary['average'] = summary['average'] or 0.0

            return summary
        except sqlite3.Error as e:
            raise Exception(f"Failed to get expense summary: {e}")

    def get_category_breakdown(self, date_from: Optional[str] = None,
                              date_to: Optional[str] = None) -> List[Dict]:
        """Get expense breakdown by category within a date range."""
        try:
            cursor = self.connection.cursor()

            query = '''
                SELECT category, COUNT(*) as count, SUM(amount) as total
                FROM expenses WHERE 1=1
            '''
            params = []

            if date_from:
                query += " AND date >= ?"
                params.append(date_from)

            if date_to:
                query += " AND date <= ?"
                params.append(date_to)

            query += " GROUP BY category ORDER BY total DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Failed to get category breakdown: {e}")

    def backup_database(self, backup_path: str) -> None:
        """Create a backup of the database."""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)

            # Use SQLite backup API
            backup = sqlite3.connect(backup_path)
            self.connection.backup(backup)
            backup.close()
        except Exception as e:
            raise Exception(f"Failed to backup database: {e}")

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()