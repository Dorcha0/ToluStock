"""
Utility functions for ToluStock application.
Contains common helper functions used across the application.
"""

import hashlib
import re
import csv
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed_password


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it has 10-15 digits
    return 10 <= len(digits_only) <= 15


def format_currency(amount: Union[float, Decimal]) -> str:
    """Format amount as currency."""
    return f"${amount:.2f}"


def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime object to string."""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except ValueError:
            return date_obj
    return date_obj.strftime(format_str)


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None


def generate_sku(product_name: str, category: str = "") -> str:
    """Generate SKU for a product."""
    # Take first 3 characters of category and product name
    category_prefix = category[:3].upper() if category else "GEN"
    product_prefix = ''.join(c for c in product_name[:4] if c.isalnum()).upper()
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%m%d%H%M")
    
    return f"{category_prefix}-{product_prefix}-{timestamp}"


def export_to_csv(data: List[Dict[str, Any]], filename: str, headers: Optional[List[str]] = None) -> bool:
    """Export data to CSV file."""
    try:
        if not data:
            return False
        
        if headers is None:
            headers = list(data[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        
        return True
    except Exception as e:
        print(f"CSV export failed: {e}")
        return False


def import_from_csv(filename: str) -> Optional[List[Dict[str, Any]]]:
    """Import data from CSV file."""
    try:
        data = []
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(dict(row))
        return data
    except Exception as e:
        print(f"CSV import failed: {e}")
        return None


def export_to_json(data: Any, filename: str) -> bool:
    """Export data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, default=str)
        return True
    except Exception as e:
        print(f"JSON export failed: {e}")
        return False


def import_from_json(filename: str) -> Optional[Any]:
    """Import data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            return json.load(jsonfile)
    except Exception as e:
        print(f"JSON import failed: {e}")
        return None


def calculate_stock_value(products: List[Dict[str, Any]]) -> float:
    """Calculate total stock value."""
    total_value = 0.0
    for product in products:
        quantity = product.get('quantity', 0)
        unit_price = product.get('unit_price', 0.0)
        total_value += quantity * unit_price
    return total_value


def get_low_stock_items(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get products with low stock levels."""
    low_stock_items = []
    for product in products:
        quantity = product.get('quantity', 0)
        min_stock_level = product.get('min_stock_level', 0)
        if quantity <= min_stock_level:
            low_stock_items.append(product)
    return low_stock_items


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    # Remove invalid characters for filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_string(text: str) -> str:
    """Normalize string for searching (lowercase, strip whitespace)."""
    return text.lower().strip()


def search_in_text(search_term: str, text: str) -> bool:
    """Check if search term exists in text (case-insensitive)."""
    return normalize_string(search_term) in normalize_string(text)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return filename.split('.')[-1].lower() if '.' in filename else ""


def is_valid_number(value: str) -> bool:
    """Check if string represents a valid number."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def safe_cast_int(value: Any, default: int = 0) -> int:
    """Safely cast value to integer with default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_cast_float(value: Any, default: float = 0.0) -> float:
    """Safely cast value to float with default fallback."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_current_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().isoformat()


def days_between_dates(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date2 - date1).days)


class ConfigManager:
    """Simple configuration manager for application settings."""
    
    def __init__(self):
        self.config = {
            'app_name': 'ToluStock',
            'version': '1.0.0',
            'window_width': 1200,
            'window_height': 800,
            'theme': 'light',
            'language': 'en',
            'auto_backup': True,
            'backup_interval_days': 7,
            'low_stock_alert': True,
            'currency_symbol': '$',
            'date_format': '%Y-%m-%d',
            'decimal_places': 2
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(updates)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config.copy()


# Global configuration instance
config = ConfigManager()