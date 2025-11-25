import json
import os
from typing import Dict, Any, Optional

class SettingsManager:
    """Manages application settings and user preferences."""

    def __init__(self, settings_file: str = "settings.json"):
        """Initialize settings manager with default values."""
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings."""
        return {
            "currency": {
                "symbol": "$",
                "position": "prefix",  # "prefix" or "suffix"
                "decimal_separator": ".",
                "thousands_separator": ","
            },
            "ui": {
                "window_width": 1000,
                "window_height": 700,
                "theme": "light",
                "default_date_format": "%Y-%m-%d"
            },
            "data": {
                "items_per_page": 50,
                "auto_backup": True,
                "backup_frequency": "daily",  # "daily", "weekly", "monthly"
                "backup_retention_days": 30
            },
            "export": {
                "default_format": "csv",  # "csv" or "xlsx"
                "include_headers": True,
                "date_format": "%Y-%m-%d"
            }
        }

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file, using defaults if file doesn't exist."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all settings exist
                    default_settings = self.get_default_settings()
                    return self._merge_settings(default_settings, loaded_settings)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load settings file: {e}")
                return self.get_default_settings()
        else:
            # Create settings file with defaults
            default_settings = self.get_default_settings()
            self.save_settings(default_settings)
            return default_settings

    def _merge_settings(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge loaded settings with defaults."""
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """Save settings to file."""
        try:
            settings_to_save = settings if settings is not None else self.settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error: Failed to save settings file: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'currency.symbol')."""
        keys = key.split('.')
        value = self.settings
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a setting value using dot notation (e.g., 'currency.symbol')."""
        keys = key.split('.')
        settings = self.settings
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        # Set the value
        settings[keys[-1]] = value
        # Save to file
        self.save_settings()

    def get_currency_settings(self) -> Dict[str, Any]:
        """Get currency-related settings."""
        return self.get('currency', {})

    def set_currency_symbol(self, symbol: str) -> None:
        """Set currency symbol."""
        self.set('currency.symbol', symbol)

    def set_currency_position(self, position: str) -> None:
        """Set currency position ('prefix' or 'suffix')."""
        if position in ['prefix', 'suffix']:
            self.set('currency.position', position)

    def set_decimal_separator(self, separator: str) -> None:
        """Set decimal separator ('.' or ',')."""
        if separator in ['.', ',']:
            self.set('currency.decimal_separator', separator)

    def set_thousands_separator(self, separator: str) -> None:
        """Set thousands separator (',', '.', or space)."""
        if separator in [',', '.', ' ', '']:
            self.set('currency.thousands_separator', separator)

    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI-related settings."""
        return self.get('ui', {})

    def set_window_size(self, width: int, height: int) -> None:
        """Set window dimensions."""
        self.set('ui.window_width', width)
        self.set('ui.window_height', height)

    def get_data_settings(self) -> Dict[str, Any]:
        """Get data-related settings."""
        return self.get('data', {})

    def set_items_per_page(self, count: int) -> None:
        """Set number of items to display per page."""
        if count > 0:
            self.set('data.items_per_page', count)

    def get_export_settings(self) -> Dict[str, Any]:
        """Get export-related settings."""
        return self.get('export', {})

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        self.settings = self.get_default_settings()
        self.save_settings()

    def export_settings(self, file_path: str) -> bool:
        """Export current settings to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def import_settings(self, file_path: str) -> bool:
        """Import settings from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                # Validate and merge with defaults
                self.settings = self._merge_settings(self.get_default_settings(), imported_settings)
                self.save_settings()
            return True
        except (json.JSONDecodeError, IOError):
            return False

    def validate_settings(self) -> bool:
        """Validate current settings for consistency."""
        try:
            # Validate currency settings
            currency_pos = self.get('currency.position')
            if currency_pos not in ['prefix', 'suffix']:
                return False

            decimal_sep = self.get('currency.decimal_separator')
            if decimal_sep not in ['.', ',']:
                return False

            thousands_sep = self.get('currency.thousands_separator')
            if thousands_sep not in [',', '.', ' ', '']:
                return False

            # Validate UI settings
            window_width = self.get('ui.window_width')
            window_height = self.get('ui.window_height')
            if not (isinstance(window_width, int) and window_width > 0):
                return False
            if not (isinstance(window_height, int) and window_height > 0):
                return False

            # Validate data settings
            items_per_page = self.get('data.items_per_page')
            if not (isinstance(items_per_page, int) and items_per_page > 0):
                return False

            return True
        except Exception:
            return False